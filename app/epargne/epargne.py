import flet as ft
import sqlite3
from datetime import datetime
import calendar

# ===================== CONFIGURATION BD ===================== #
def get_epargne_conn():
    return sqlite3.connect("databases/objectifs.db", check_same_thread=False)

def get_budget_conn():
    return sqlite3.connect("databases/budget.db", check_same_thread=False)

def init_db():
    conn = get_epargne_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS objectifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        montant INTEGER NOT NULL,
        duree INTEGER NOT NULL,
        pourcentage INTEGER NOT NULL,
        date_echeance TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

def get_epargne_budget():
    """Récupère le montant (float) de la catégorie 'Epargne'."""
    try:
        conn = get_budget_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM categories WHERE LOWER(name) = 'epargne'")
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row and row[0] else 0.0
    except Exception:
        return 0.0

# ===================== VUE ÉPARGNE ===================== #
def epargne_view(page: ft.Page):
    
    objectifs_list = ft.Column(spacing=15)
    nom_field = ft.TextField(label="Objectif (ex: Vacances)", expand=True)
    montant_field = ft.TextField(label="Cible (F)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    pourcentage_field = ft.TextField(label="%", width=80, keyboard_type=ft.KeyboardType.NUMBER, value="10")
    total_label = ft.Text("Total Objectifs : 0 F", size=16, weight="bold")

    # --- DatePicker (Correction AttributeError) ---
    selected_date_text = ft.Text(datetime.today().strftime("%d/%m/%Y"), size=14, weight="bold")
    
    def on_date_change(e):
        if date_picker.value:
            selected_date_text.value = date_picker.value.strftime("%d/%m/%Y")
            page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime.today(),
    )
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)

    # --- Fonctions ---
    def load_objectifs():
        objectifs_list.controls.clear()
        epargne_disponible = get_epargne_budget()
        
        conn = get_epargne_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, montant, pourcentage, date_echeance FROM objectifs")
        rows = cursor.fetchall()
        conn.close()

        total_cible = 0
        for obj_id, nom, montant, pct, date_ech in rows:
            total_cible += montant
            # Calcul de la progression (Simulé par le budget actuel * pourcentage alloué)
            encaisse = (epargne_disponible * pct) / 100
            progression = min(encaisse / montant, 1.0) if montant > 0 else 0

            objectifs_list.controls.append(
                ft.Container(
                    bgcolor="#1E2023", padding=15, border_radius=15,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(nom, weight="bold", size=16, expand=True),
                            ft.Text(f"{int(progression*100)}%", color=ft.Colors.BLUE_ACCENT, weight="bold")
                        ]),
                        ft.ProgressBar(value=progression, color=ft.Colors.BLUE_ACCENT, bgcolor="#333333"),
                        ft.Row([
                            ft.Text(f"{encaisse:,.0f} / {montant:,.0f} F", size=12, color=ft.Colors.SECONDARY),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=ft.Colors.RED_400, 
                                          icon_size=18, on_click=lambda e, oid=obj_id: delete_objectif(oid))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=8)
                )
            )
        total_label.value = f"Total Cible : {total_cible:,.0f} FCFA"
        page.update()

    def add_objectif(e):
        if not nom_field.value or not montant_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("Veuillez remplir les champs requis"))
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            conn = get_epargne_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO objectifs (nom, montant, duree, pourcentage, date_echeance) VALUES (?, ?, ?, ?, ?)",
                (nom_field.value, int(montant_field.value), 0, int(pourcentage_field.value), selected_date_text.value)
            )
            conn.commit()
            conn.close()
            
            nom_field.value = ""
            montant_field.value = ""
            load_objectifs()
            page.snack_bar = ft.SnackBar(ft.Text("Objectif ajouté !"), bgcolor=ft.Colors.BLUE_ACCENT_1)
            page.snack_bar.open = True
        except Exception as ex:
            print(f"Erreur ajout epargne: {ex}")
        page.update()

    def delete_objectif(oid):
        conn = get_epargne_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM objectifs WHERE id=?", (oid,))
        conn.commit()
        conn.close()
        load_objectifs()

    load_objectifs()

    return ft.View(
        "/epargne",
        bgcolor="#121417",
        controls=[
            ft.AppBar(
                title=ft.Text("Épargne & Objectifs", weight="bold"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.ListView(
                expand=True, spacing=20, padding=20,
                controls=[
                    ft.Container(
                        bgcolor="#1E2023", padding=20, border_radius=20,
                        content=ft.Column([
                            ft.Text("Nouvel Objectif", size=18, weight="bold"),
                            ft.Row([nom_field, montant_field], spacing=10),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Échéance", size=12, color=ft.Colors.SECONDARY),
                                    selected_date_text,
                                ], expand=True),
                                # CORRECTION ICI : date_picker.open = True
                                ft.IconButton(ft.Icons.CALENDAR_MONTH_ROUNDED, 
                                              on_click=lambda _: (setattr(date_picker, "open", True), page.update())),
                                pourcentage_field
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.ElevatedButton(
                                "Enregistrer l'objectif",
                                icon=ft.Icons.SAVINGS_ROUNDED,
                                bgcolor=ft.Colors.BLUE_ACCENT,
                                color="#121417",
                                height=50, expand=True,
                                on_click=add_objectif,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                            )
                        ], spacing=15)
                    ),
                    ft.Row([ft.Text("Mes Projets", size=18, weight="bold", expand=True), total_label]),
                    objectifs_list
                ]
            )
        ]
    )
