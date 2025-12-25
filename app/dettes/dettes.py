import flet as ft
import sqlite3
from datetime import datetime
import calendar

# ===================== CONFIGURATION BD ===================== #
def get_dettes_conn():
    return sqlite3.connect("databases/dettes.db", check_same_thread=False)

def init_db():
    conn = get_dettes_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dettes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        montant REAL NOT NULL,
        motif TEXT,
        date_echeance TEXT NOT NULL,
        interet REAL,
        fournisseur TEXT,
        duree INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ===================== VUE GESTION DETTES ===================== #
def dettes_view(page: ft.Page):
    
    dettes_list = ft.Column(spacing=15)
    titre_field = ft.TextField(label="Titre / Créancier", hint_text="Ex: Prêt Banque", expand=True)
    montant_field = ft.TextField(label="Montant (F)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    motif_field = ft.TextField(label="Motif", expand=True)
    duree_field = ft.TextField(label="Durée (mois)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    interet_field = ft.TextField(label="Intérêt (%)", width=100, value="0")
    total_label = ft.Text("Total: 0 F", size=22, weight="bold", color="#F44336")

    # --- DatePicker 2025 (CORRECTION) ---
    selected_date_text = ft.Text("Échéance non définie", size=14, color=ft.Colors.SECONDARY)
    
    def on_date_change(e):
        if date_picker.value:
            selected_date_text.value = date_picker.value.strftime("%d/%m/%Y")
            page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(2024, 1, 1),
        last_date=datetime(2040, 1, 1)
    )
    
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)

    def load_dettes():
        dettes_list.controls.clear()
        conn = get_dettes_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dettes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        total_global = 0
        for row in rows:
            det_id, titre, montant, motif, date_ech, interet, fourn, duree = row
            # Calcul du montant final avec intérêt simple
            total_avec_interet = montant + (montant * (interet / 100))
            total_global += total_avec_interet
            
            dettes_list.controls.append(
                ft.Container(
                    bgcolor="#1E2023",
                    padding=15,
                    border_radius=15,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.MONEY_OFF_ROUNDED, color="#F44336", size=22),
                                bgcolor=ft.Colors.with_opacity(0.1, "#F44336"),
                                padding=10, border_radius=10
                            ),
                            ft.Column([
                                ft.Text(titre, weight="bold", size=16),
                                ft.Text(f"Échéance : {date_ech}", size=12, color=ft.Colors.SECONDARY),
                            ], expand=True, spacing=2),
                            ft.Column([
                                ft.Text(f"{total_avec_interet:,.0f} F", weight="bold", size=17, color="#F44336"),
                                ft.Text(f"Dont {interet}% int.", size=10, color=ft.Colors.SECONDARY)
                            ], horizontal_alignment=ft.CrossAxisAlignment.END)
                        ]),
                        ft.Divider(height=10, color=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
                        ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=ft.Colors.SECONDARY),
                            ft.Text(f"{motif if motif else 'Pas de motif'} • {duree if duree else 'N/A'} mois", size=12, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                icon_size=20,
                                on_click=lambda e, di=det_id: delete_dette(di)
                            )
                        ])
                    ], spacing=10)
                )
            )
        total_label.value = f"Total Dettes : {total_global:,.0f} FCFA"
        page.update()

    def add_dette(e):
        if not titre_field.value or not montant_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("Veuillez remplir le titre et le montant"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = get_dettes_conn()
            cursor = conn.cursor()
            
            date_ech = selected_date_text.value
            if "non définie" in date_ech:
                duree = int(duree_field.value) if duree_field.value else 0
                today = datetime.today()
                month = today.month - 1 + duree
                year = today.year + month // 12
                month = month % 12 + 1
                date_ech = datetime(year, month, today.day).strftime("%d/%m/%Y")

            cursor.execute("""
                INSERT INTO dettes (titre, montant, motif, date_echeance, interet, fournisseur, duree)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (titre_field.value, float(montant_field.value), motif_field.value, 
                  date_ech, float(interet_field.value), titre_field.value, duree_field.value))
            
            conn.commit()
            conn.close()
            
            titre_field.value = montant_field.value = motif_field.value = duree_field.value = ""
            interet_field.value = "0"
            selected_date_text.value = "Échéance non définie"
            load_dettes()
            page.snack_bar = ft.SnackBar(ft.Text("Dette enregistrée !"), bgcolor="#F44336")
            page.snack_bar.open = True
        except Exception as ex:
            print(f"Erreur ajout dette: {ex}")
        page.update()

    def delete_dette(det_id):
        conn = get_dettes_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dettes WHERE id=?", (det_id,))
        conn.commit()
        conn.close()
        load_dettes()

    load_dettes()

    return ft.View(
        "/dettes",
        bgcolor="#121417",
        controls=[
            ft.AppBar(
                title=ft.Text("Dettes & Crédits", weight="bold"),
                center_title=True,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    ft.Container(
                        bgcolor="#1E2023",
                        padding=20,
                        border_radius=20,
                        content=ft.Column([
                            ft.Text("Nouveau Prêt / Dette", size=18, weight="bold"),
                            ft.Row([titre_field, montant_field], spacing=10),
                            ft.Row([motif_field, interet_field], spacing=10),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Date d'échéance", size=12, color=ft.Colors.SECONDARY),
                                    selected_date_text,
                                ], expand=True),
                                # CORRECTION ICI : Utilisation de date_picker.open = True
                                ft.IconButton(
                                    ft.Icons.CALENDAR_MONTH_ROUNDED, 
                                    on_click=lambda _: (setattr(date_picker, "open", True), page.update())
                                ),
                                duree_field,
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.ElevatedButton(
                                "Ajouter la dette",
                                icon=ft.Icons.ADD_CARD_ROUNDED,
                                bgcolor="#F44336",
                                color=ft.Colors.WHITE,
                                height=50,
                                expand=True,
                                on_click=add_dette,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                            )
                        ], spacing=15)
                    ),
                    ft.Row([
                        ft.Text("Dettes en cours", size=18, weight="bold", expand=True),
                        
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    total_label,
                    dettes_list
                ]
            )
        ]
    )
