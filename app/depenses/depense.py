import flet as ft
import sqlite3
from datetime import datetime

# ===================== CONFIGURATION BD ===================== #
def get_depense_conn():
    return sqlite3.connect("databases/depenses.db", check_same_thread=False)

def init_db():
    conn = get_depense_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        montant INTEGER NOT NULL,
        categorie TEXT NOT NULL,
        date_dep DATE NOT NULL,
        moyen_paiement TEXT NOT NULL,
        notes TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def load_categories():
    """Récupère les catégories depuis la base budget de manière sécurisée."""
    try:
        conn_budget = sqlite3.connect("databases/budget.db")
        cursor_budget = conn_budget.cursor()
        cursor_budget.execute("SELECT name FROM categories ORDER BY name")
        rows = cursor_budget.fetchall()
        conn_budget.close()
        # On extrait la chaîne du tuple : row[0]
        return [row[0] for row in rows] if rows else ["Général"]
    except Exception:
        return ["Général"]

# ===================== VUE DES DÉPENSES ===================== #
def depense_view(page: ft.Page):
    
    # --- États et Champs ---
    depenses_list = ft.Column(spacing=15)
    nom_field = ft.TextField(label="Libellé", hint_text="Ex: Courses", expand=True)
    montant_field = ft.TextField(label="Montant (F)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    
    cat_list = load_categories()
    categorie_dropdown = ft.Dropdown(
        label="Catégorie",
        options=[ft.dropdown.Option(c) for c in cat_list],
        value=cat_list[0] if cat_list else "Général",
        expand=True
    )

    moyen_paiement_dropdown = ft.Dropdown(
        label="Paiement",
        options=[ft.dropdown.Option("Cash"), ft.dropdown.Option("Mobile Money"), ft.dropdown.Option("Carte")],
        value="Cash",
        width=150
    )

    notes_field = ft.TextField(label="Notes (Optionnel)", multiline=True, min_lines=1, max_lines=2)
    total_label = ft.Text("Total: 0 F", size=20, weight="bold", color="#3FEB82")

    # --- DatePicker 2025 ---
    selected_date_text = ft.Text(datetime.today().strftime("%Y-%m-%d"), size=16, weight="bold")
    
    def on_date_change(e):
        selected_date_text.value = date_picker.value.strftime("%Y-%m-%d")
        page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31)
    )
    # Important : On ajoute le picker à l'overlay de la page
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)

    # --- Logique d'affichage ---
    def get_category_icon(cat_name):
        cat = str(cat_name).lower()
        if "loyer" in cat or "maison" in cat: return ft.Icons.HOME_ROUNDED
        if "food" in cat or "alimentation" in cat or "courses" in cat: return ft.Icons.RESTAURANT_ROUNDED
        if "transport" in cat: return ft.Icons.DIRECTIONS_CAR_ROUNDED
        if "santé" in cat or "hopital" in cat: return ft.Icons.LOCAL_HOSPITAL_ROUNDED
        if "loisirs" in cat: return ft.Icons.GAMES_ROUNDED # Correction ici
        if "épargne" in cat: return ft.Icons.SAVINGS_ROUNDED
        return ft.Icons.SHOPPING_BAG_ROUNDED

    def load_depenses():
        depenses_list.controls.clear()
        conn = get_depense_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, montant, categorie, date_dep, moyen_paiement, notes FROM depenses ORDER BY date_dep DESC, id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        total = 0
        for row in rows:
            dep_id, nom, montant, cat, date, moyen, notes = row
            total += montant
            
            depenses_list.controls.append(
                ft.Container(
                    bgcolor="#1E2023",
                    padding=15,
                    border_radius=15,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(get_category_icon(cat), color="#3FEB82", size=24),
                            bgcolor=ft.Colors.with_opacity(0.1, "#3FEB82"),
                            padding=10, border_radius=10
                        ),
                        ft.Column([
                            ft.Text(nom, weight="bold", size=16),
                            ft.Text(f"{cat} • {date}", size=12, color=ft.Colors.SECONDARY),
                        ], expand=True, spacing=2),
                        ft.Column([
                            ft.Text(f"- {montant:,.0f} F", weight="bold", size=16, color=ft.Colors.RED_400),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                icon_size=18,
                                on_click=lambda e, di=dep_id: delete_depense(di)
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0)
                    ])
                )
            )
        total_label.value = f"Total : {total:,.0f} FCFA"
        page.update()

    def add_depense(e):
        if not nom_field.value or not montant_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("Nom et montant requis !"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = get_depense_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO depenses (nom, montant, categorie, date_dep, moyen_paiement, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (nom_field.value, int(montant_field.value), categorie_dropdown.value, selected_date_text.value, moyen_paiement_dropdown.value, notes_field.value)
            )
            conn.commit()
            conn.close()
            
            # Reset des champs
            nom_field.value = ""
            montant_field.value = ""
            notes_field.value = ""
            load_depenses()
            page.snack_bar = ft.SnackBar(ft.Text("Dépense ajoutée !"), bgcolor="#3FEB82")
            page.snack_bar.open = True
        except Exception as ex:
            print(f"Erreur : {ex}")
        page.update()

    def delete_depense(dep_id):
        conn = get_depense_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM depenses WHERE id=?", (dep_id,))
        conn.commit()
        conn.close()
        load_depenses()

    # --- Initialisation ---
    load_depenses()

    return ft.View(
        "/depenses",
        bgcolor="#121417",
        controls=[
            ft.AppBar(
                title=ft.Text("Mes Dépenses", weight="bold"),
                center_title=True,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    # Bloc Formulaire
                    ft.Container(
                        bgcolor="#1E2023",
                        padding=20,
                        border_radius=20,
                        content=ft.Column([
                            ft.Text("Ajouter une transaction", size=18, weight="bold"),
                            ft.Row([nom_field, montant_field], spacing=10),
                            ft.Row([categorie_dropdown, moyen_paiement_dropdown], spacing=10),
                            ft.Row([
                                ft.Icon(ft.Icons.EVENT_ROUNDED, color=ft.Colors.SECONDARY, size=20),
                                selected_date_text,
                                ft.TextButton("Modifier la date", on_click=lambda _: date_picker.pick_date())
                            ]),
                            notes_field,
                            ft.ElevatedButton(
                                "Enregistrer",
                                icon=ft.Icons.ADD_ROUNDED,
                                bgcolor="#3FEB82",
                                color="#121417",
                                height=50,
                                expand=True,
                                on_click=add_depense,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                            )
                        ], spacing=15)
                    ),
                    
                    ft.Row([
                        ft.Text("Historique", size=18, weight="bold", expand=True),
                        total_label
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    
                    depenses_list
                ]
            )
        ]
    )
