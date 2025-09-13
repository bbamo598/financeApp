import flet as ft
import sqlite3
from datetime import datetime, timedelta
import calendar
from menu import menu_view

# ===================== BD SQLITE ===================== #
conn = sqlite3.connect("budget.db", check_same_thread=False)
cursor = conn.cursor()

# Table des catégories
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    percentage REAL NOT NULL,
    amount REAL DEFAULT 0
)
""")

# Table des gains
cursor.execute("""
CREATE TABLE IF NOT EXISTS gains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)
""")

conn.commit()

# ===================== UI ===================== #
def budget_view(page: ft.Page) -> ft.View:
    # --- Carte Budget résumé ---
    budget_summary = ft.Card()

    # Récupérer le dernier gain
    cursor.execute("SELECT amount FROM gains ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    gain = row[0] if row else 0

    def update_budget_summary():
        budget_summary.content = ft.Container(
            content=ft.Column([
                ft.Text("Budget du mois", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Total : {gain} FCFA | Reste : {gain*0.1:.0f} FCFA", size=25),
                ft.ProgressBar(width=300, value=0.1 if gain else 0)
            ]),
            padding=20
        )
        page.update()

    update_budget_summary()

    # --- Carte Total gains du mois ---
    def gains_du_mois_card():
        today = datetime.today()
        current_month_start = today.replace(day=1).strftime("%Y-%m-%d")
        current_month_end = today.strftime("%Y-%m-%d")

        if today.month == 1:
            prev_month_start = today.replace(year=today.year-1, month=12, day=1).strftime("%Y-%m-%d")
            prev_month_end = today.replace(year=today.year-1, month=12, day=31).strftime("%Y-%m-%d")
        else:
            prev_month_start = today.replace(month=today.month-1, day=1).strftime("%Y-%m-%d")
            last_day_prev_month = calendar.monthrange(today.year, today.month-1)[1]
            prev_month_end = today.replace(month=today.month-1, day=last_day_prev_month).strftime("%Y-%m-%d")

        cursor.execute("SELECT SUM(amount) FROM gains WHERE date BETWEEN ? AND ?", (current_month_start, current_month_end))
        current_total = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM gains WHERE date BETWEEN ? AND ?", (prev_month_start, prev_month_end))
        prev_total = cursor.fetchone()[0] or 0

        if prev_total > 0:
            variation = ((current_total - prev_total) / prev_total) * 100
        else:
            variation = 0

        if variation > 0:
            arrow = "🡅"
            color = ft.Colors.GREEN
        elif variation < 0:
            arrow = "🡇"
            color = ft.Colors.RED
        else:
            arrow = "-"
            color = ft.Colors.BLACK

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Total des gains du mois", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{current_total:.0f} FCFA", size=25),
                    ft.Text(f"{arrow} {abs(variation):.1f}%", size=20, color=color)
                ]),
                padding=20
            )
        )

    # --- Catégories calculées dynamiquement ---
    categories_grid = ft.GridView(
        expand=True,
        runs_count=1,
        child_aspect_ratio=2.0,
        spacing=10,
        run_spacing=10,
    )

    def update_categories():
        categories_grid.controls.clear()
        cursor.execute("SELECT name, amount FROM categories")
        for cat_name, montant in cursor.fetchall():
            categories_grid.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Text(f"{cat_name} :\n {montant:.0f} FCFA", size=25),
                        padding=10
                    )
                )
            )
        page.update()

    update_categories()

    # --- Ajout d’un gain (budget total) ---
    new_budget = ft.TextField(label="Entrez un budget (FCFA)", width=300)

    def add_budget(e):
        nonlocal gain
        if new_budget.value.strip():
            try:
                nouvelle_valeur = int(new_budget.value)
                gain = nouvelle_valeur
                today_str = datetime.today().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO gains (amount, date) VALUES (?, ?)", (gain, today_str))
                conn.commit()

                # 🔄 Mettre à jour les montants des catégories existantes
                cursor.execute("SELECT id, percentage FROM categories")
                for cat_id, pct in cursor.fetchall():
                    montant = gain * pct
                    cursor.execute("UPDATE categories SET amount=? WHERE id=?", (montant, cat_id))
                conn.commit()

                new_budget.value = ""
                update_budget_summary()
                update_categories()
            except ValueError:
                new_budget.error_text = "Veuillez entrer un nombre valide"
            page.update()

    # --- Ajout d’une nouvelle catégorie ---
    cat_name = ft.TextField(label="Nom de la catégorie", width=300)
    cat_pct = ft.TextField(label="Pourcentage (0.0 - 1.0)", width=300)

    # Initialiser les catégories par défaut si la table est vide
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        defaults = [("Obligations", 0.5), ("Loisirs", 0.3), ("Epargne", 0.2)]
        for name, pct in defaults:
            cursor.execute("INSERT INTO categories (name, percentage, amount) VALUES (?, ?, ?)", (name, pct, 0))
        conn.commit()

    def add_category(e):
        try:
            name = cat_name.value.strip()
            pct = float(cat_pct.value.strip())
            if not (0 < pct <= 1):
                cat_pct.error_text = "Le pourcentage doit être entre 0 et 1"
            elif name:
                # 🔄 Déduire le pourcentage du plus grand
                cursor.execute("SELECT id, percentage FROM categories ORDER BY percentage DESC LIMIT 1")
                largest_id, largest_pct = cursor.fetchone()
                new_largest_pct = largest_pct - pct
                if new_largest_pct < 0:
                    cat_pct.error_text = "Pourcentage trop élevé"
                    page.update()
                    return
                cursor.execute("UPDATE categories SET percentage=? WHERE id=?", (new_largest_pct, largest_id))

                # Calcul du montant pour chaque catégorie
                montant = gain * pct
                cursor.execute("INSERT INTO categories (name, percentage, amount) VALUES (?, ?, ?)", (name, pct, montant))
                conn.commit()
                cat_name.value, cat_pct.value = "", ""
                update_categories()
            else:
                cat_name.error_text = "Nom requis"
        except ValueError:
            cat_pct.error_text = "Veuillez entrer un nombre valide"
        page.update()

    # --- Vue principale ---
    return ft.View(
        "/budget",
        controls=[
            ft.AppBar(
                title=ft.Text("Budget"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    ft.Icon(name=ft.Icons.WALLET, size=100, color="#3FEB82"),
                    budget_summary,
                    gains_du_mois_card(),  # Nouvelle carte gains du mois
                    ft.Text("Définir un budget :", size=18, weight=ft.FontWeight.BOLD),
                    new_budget,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_budget),
                    ft.Divider(),
                    ft.Text("Ajouter une catégorie :", size=18, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        cat_name,
                        cat_pct,
                        ft.ElevatedButton("Ajouter", icon=ft.Icons.ADD, on_click=add_category)
                    ], spacing=10, width=300),
                    categories_grid
                ]
            )
        ]
    )
