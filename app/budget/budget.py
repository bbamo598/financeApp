import flet as ft
import sqlite3
from datetime import datetime
import calendar

# ===================== BD SQLITE CONFIG ===================== #
# Utilisation d'une fonction pour obtenir la connexion de manière thread-safe si nécessaire
def get_db_connection():
    return sqlite3.connect("databases/budget.db", check_same_thread=False)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        percentage REAL NOT NULL,
        amount REAL DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Initialisation de la BD au démarrage du module
init_db()

# ===================== Fonctions auxiliaires ===================== #
def get_total_gains_mois():
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.today()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day).strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(amount) FROM gains WHERE date BETWEEN ? AND ?", (start_date, end_date))
    result = cursor.fetchone()[0] or 0
    conn.close()
    return result

def update_category_amounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    gain = get_total_gains_mois()
    cursor.execute("SELECT id, percentage FROM categories")
    for cat_id, pct in cursor.fetchall():
        montant = gain * pct
        cursor.execute("UPDATE categories SET amount=? WHERE id=?", (montant, cat_id))
    conn.commit()
    conn.close()

# ===================== UI & LOGIQUE PRINCIPALE ===================== #
def budget_view(page: ft.Page) -> ft.View:
    # Initialisation des variables
    gain = get_total_gains_mois()
    budget_summary_text = ft.Text(f"Total : {gain:,.0f} FCFA", size=25, weight="bold")
    
    # --- Composants dynamiques ---
    categories_grid = ft.Column(spacing=15)
    historique_list = ft.Column(spacing=10)

    # --- Fonctions de mise à jour UI ---
    def update_budget_summary():
        nonlocal gain
        gain = get_total_gains_mois()
        budget_summary_text.value = f"Total : {gain:,.0f} FCFA"
        page.update()

    def update_categories():
        update_category_amounts()
        categories_grid.controls.clear()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, amount, percentage FROM categories")
        rows = cursor.fetchall()
        conn.close()
        
        for cat_id, cat_name, montant, pct in rows:
            # Design 2025 : Carte avec barre de progression intégrée
            categories_grid.controls.append(
                ft.Container(
                    bgcolor="#1E2023",
                    padding=15,
                    border_radius=15,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{cat_name} ({pct*100:.0f}%)", size=16, weight="bold"),
                            ft.Text(f"{montant:,.0f} FCFA", size=16, weight="bold", color=page.theme.color_scheme.primary)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(
                            value=(montant / gain) if gain > 0 else 0,
                            color=page.theme.color_scheme.primary,
                            bgcolor=ft.Colors.with_opacity(0.1, page.theme.color_scheme.primary),
                        ),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT_ROUNDED, tooltip="Modifier", on_click=lambda e, cid=cat_id: edit_category(cid), icon_size=18),
                            ft.IconButton(ft.Icons.DELETE_FOREVER_ROUNDED, tooltip="Supprimer", on_click=lambda e, cid=cat_id: delete_category(cid), icon_size=18)
                        ], alignment=ft.MainAxisAlignment.END, spacing=0)
                    ], spacing=10)
                )
            )
        page.update()

    def update_historique():
        historique_list.controls.clear()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, date FROM gains ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            historique_list.controls.append(ft.Text("Aucun gain enregistré", size=14, color=ft.Colors.SECONDARY))
        else:
            for gid, amount, date in rows:
                historique_list.controls.append(
                    ft.Container(
                        padding=10, border_radius=10, bgcolor="#1E2023",
                        content=ft.Row([
                            ft.Text(f"{amount:,.0f} FCFA  •  {date}", expand=True),
                            ft.IconButton(ft.Icons.EDIT_ROUNDED, on_click=lambda e, gid=gid: edit_gain(gid), icon_size=16),
                            ft.IconButton(ft.Icons.DELETE_FOREVER_ROUNDED, on_click=lambda e, gid=gid: delete_gain(gid), icon_size=16)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
                )
        page.update()

    # === Fonctions BD (CRUD Gains) === #
    def add_gain(e):
        try:
            valeur = float(new_gain_field.value) # Utilisation d'un nouveau nom de champ pour éviter conflit
            today_str = datetime.today().strftime("%Y-%m-%d")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO gains (amount, date) VALUES (?, ?)", (valeur, today_str))
            conn.commit()
            conn.close()
            new_gain_field.value = ""
            update_category_amounts()
            update_budget_summary()
            update_categories()
            update_historique()
            page.snack_bar = ft.SnackBar(ft.Text("Gain ajouté avec succès!"), bgcolor="#3FEB82")
            page.snack_bar.open = True
        except ValueError:
            new_gain_field.error_text = "Veuillez entrer un nombre valide"
        page.update()

    def edit_gain(gid):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM gains WHERE id=?", (gid,))
        row = cursor.fetchone()
        conn.close()
        if not row: return
        champ = ft.TextField(label="Nouveau montant (FCFA)", value=str(row[0]), width=300)

        def save_edit(e):
            try:
                nv = float(champ.value)
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE gains SET amount=? WHERE id=?", (nv, gid))
                conn.commit()
                conn.close()
                update_category_amounts()
                update_historique()
                update_budget_summary()
                dialog.open = False
                page.update()
            except ValueError:
                champ.error_text = "Valeur invalide"
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Modifier le gain"), content=champ,
            actions=[ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, "open", False)), ft.ElevatedButton("Enregistrer", on_click=save_edit)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def delete_gain(gid):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gains WHERE id=?", (gid,))
        conn.commit()
        conn.close()
        update_category_amounts()
        update_historique()
        update_budget_summary()
        page.snack_bar = ft.SnackBar(ft.Text("Gain supprimé."))
        page.snack_bar.open = True
        page.update()
    
    # === Fonctions BD (CRUD Catégories) === #
    cat_name = ft.TextField(label="Nom de la catégorie", expand=True)
    cat_pct = ft.TextField(label="Pourcentage (ex: 0.3)", width=150)

    # Initialisation des catégories par défaut si vide
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        defaults = [("Obligations", 0.5), ("Loisirs", 0.3), ("Epargne", 0.2)]
        for name, pct in defaults:
            cursor.execute("INSERT INTO categories (name, percentage, amount) VALUES (?, ?, ?)", (name, pct, 0))
        conn.commit()
    conn.close()
    
    def add_category(e):
        try:
            name = cat_name.value.strip()
            pct = float(cat_pct.value.strip())
            if not (0 < pct <= 1):
                cat_pct.error_text = "Le pourcentage doit être entre 0 et 1"
            elif name:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name, percentage, amount) VALUES (?, ?, ?)", (name, pct, 0))
                conn.commit()
                conn.close()
                update_category_amounts()
                cat_name.value, cat_pct.value = "", ""
                update_categories()
                page.snack_bar = ft.SnackBar(ft.Text("Catégorie ajoutée!"), bgcolor="#3FEB82")
                page.snack_bar.open = True
            else:
                cat_name.error_text = "Nom requis"
        except ValueError:
            cat_pct.error_text = "Veuillez entrer un nombre valide"
        page.update()

    def edit_category(cat_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, percentage FROM categories WHERE id=?", (cat_id,))
        row = cursor.fetchone()
        conn.close()
        if not row: return
        name_field = ft.TextField(label="Nom", value=row[0], expand=True)
        pct_field = ft.TextField(label="Pourcentage (0.0 - 1.0)", value=str(row[1]), width=150)

        def save_edit(e):
            try:
                nv_pct = float(pct_field.value)
                if not (0 < nv_pct <= 1):
                    pct_field.error_text = "Entre 0 et 1"
                    page.update()
                    return
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE categories SET name=?, percentage=? WHERE id=?", (name_field.value, nv_pct, cat_id))
                conn.commit()
                conn.close()
                update_category_amounts()
                update_categories()
                dialog.open = False
                page.update()
            except ValueError:
                pct_field.error_text = "Valeur invalide"
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Modifier la catégorie"), content=ft.Column([ft.Row([name_field, pct_field])]),
            actions=[ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, "open", False)), ft.ElevatedButton("Enregistrer", on_click=save_edit)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def delete_category(cat_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit()
        conn.close()
        update_category_amounts()
        update_categories()
        update_budget_summary()
        page.snack_bar = ft.SnackBar(ft.Text("Catégorie supprimée."))
        page.snack_bar.open = True
        page.update()

    # --- Initialisation de l'affichage ---
    update_categories()
    update_historique()
    
    new_gain_field = ft.TextField(label="Montant du gain (FCFA)", expand=True) # Champ pour l'ajout de gain
    
    # === Vue principale === #
    return ft.View(
        "/budget",
        controls=[
            ft.AppBar(
                title=ft.Text("Gestion du Budget", weight="bold"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.ListView(
                expand=True,
                spacing=25,
                padding=20,
                controls=[
                    # Résumé du budget total (Carte moderne)
                    ft.Container(
                        gradient=ft.LinearGradient(colors=["#25BBFF", "#0C96FF"]),
                        padding=20, border_radius=20,
                        content=ft.Column([
                            ft.Text("Revenus Mensuels Estimés", color="#121417", size=14, weight="w500"),
                            budget_summary_text,
                            ft.Text(f"Calculé sur les gains réels du mois en cours", color="#121417", size=12, opacity=0.8)
                        ]),
                    ),
                    
                    # Section Ajout Gain (Inline)
                    ft.Text("Enregistrer un gain :", size=18, weight="bold"),
                    ft.Row([
                        new_gain_field, 
                        ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_gain, mini=True, bgcolor=page.theme.color_scheme.primary),
                    ]),

                    ft.Divider(height=10, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),

                    # Section Catégories
                    ft.Text("Répartition par catégories :", size=18, weight="bold"),
                    categories_grid,

                    ft.Divider(height=10, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),

                    # Section Ajout Catégorie (Déplacement pour meilleure UX)
                    ft.Text("Ajouter une nouvelle catégorie :", size=16, weight="bold"),
                    ft.Row([
                        cat_name, cat_pct,
                        ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_category, mini=True, bgcolor=page.theme.color_scheme.surface)
                    ], vertical_alignment=ft.CrossAxisAlignment.END),

                    ft.Divider(height=10, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    
                    # Historique des gains
                    ft.Text("Historique des gains :", size=18, weight="bold"),
                    ft.Container(content=historique_list, padding=10, bgcolor="#1E2023", border_radius=15)
                ]
            )
        ],
        bgcolor="#121417",
    )
