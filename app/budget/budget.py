import flet as ft
import sqlite3
from menu import menu_view

# ===================== BD SQLITE ===================== #
conn = sqlite3.connect("budget.db", check_same_thread=False)
cursor = conn.cursor()

# Table des catégories (ajout colonne amount)
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
    amount REAL NOT NULL
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
                ft.Text(f"Total : {gain} FCFA | Reste : {gain*0.1} FCFA", size=25),
                ft.ProgressBar(width=300, value=0.1 if gain else 0)
            ]),
            padding=20
        )
        page.update()

    update_budget_summary()

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
                cursor.execute("INSERT INTO gains (amount) VALUES (?)", (gain,))
                conn.commit()

                # 🔄 Mettre à jour les montants des catégories déjà existantes
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

    def add_category(e):
        try:
            name = cat_name.value.strip()
            pct = float(cat_pct.value.strip())
            if not (0 < pct <= 1):
                cat_pct.error_text = "Le pourcentage doit être entre 0 et 1"
            elif name:
                montant = gain * pct  # 🔄 Calcul du montant selon le budget actuel
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
                    ft.Text("Définir un budget :", size=18, weight=ft.FontWeight.BOLD),
                    new_budget,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_budget),
                    ft.Divider(),
                    ft.Text("Ajouter une catégorie :", size=18, weight=ft.FontWeight.BOLD),

                    # 📌 En colonne
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
