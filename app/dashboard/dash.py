# dash.py

import flet as ft
import sqlite3
from datetime import datetime, timedelta
import calendar

# ---- Fonctions pour récupérer les données ----
def get_totaux_objectifs():
    conn = sqlite3.connect("objectifs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(montant), SUM(encaisse) FROM objectifs")
    result = cursor.fetchone()
    conn.close()
    montant_prevu = result[0] if result and result[0] else 0
    montant_encaisse = result[1] if result and result[1] else 0
    return montant_prevu, montant_encaisse

# Total des gains du mois courant
def get_gains_du_mois():
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()
    today = datetime.today()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day).strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(amount) FROM gains WHERE date(date) BETWEEN ? AND ?", (start_date, end_date))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0

def get_totaux_depense_mois():
    conn = sqlite3.connect("depenses.db")
    cursor = conn.cursor()
    today = datetime.today()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day).strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(montant) FROM depenses WHERE date_dep BETWEEN ? AND ?", (start_date, end_date))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0

def get_depenses_by_period(start_date, end_date):
    conn = sqlite3.connect("depenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(montant) FROM depenses WHERE date_dep BETWEEN ? AND ?",
        (start_date, end_date)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0

# ---- Fonction utilitaire pour PieChart ----
def build_piechart(sections_data, normal_radius=50, hover_radius=60):
    normal_title_style = ft.TextStyle(
        size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
    )
    hover_title_style = ft.TextStyle(
        size=22,
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD,
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK54),
    )

    def on_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(chart.sections):
            if idx == e.section_index:
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.radius = normal_radius
                section.title_style = normal_title_style
        chart.update()

    chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                value,
                title=f"{percent}%",
                color=color,
                radius=normal_radius,
                title_style=normal_title_style,
            )
            for value, percent, color in sections_data
        ],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_chart_event,
        expand=True,
    )
    return chart

# ---- Vue principale ----
def dashboard_view(page: ft.Page) -> ft.View:
    # Données depuis la BD
    montant_global = get_gains_du_mois()  # <-- Total des gains du mois en cours
    montant_depenses = get_totaux_depense_mois()  # <-- Dépenses du mois en cours
    solde = montant_global - montant_depenses
    depenses_prevues, depenses_effectuees = get_totaux_objectifs()

    # --- Calculs ---
    depenses_per = int((depenses_effectuees * 100) / depenses_prevues) if depenses_prevues > 0 else 0
    reste_per = 100 - depenses_per if depenses_prevues > 0 else 0
    depense_percent = int((montant_depenses * 100) / montant_global) if montant_global > 0 else 0
    solde_percent = 100 - depense_percent if montant_global > 0 else 0

    # --- Graphiques ---
    chart_objectifs = build_piechart([
        (depenses_effectuees, depenses_per, ft.Colors.BLUE),
        (depenses_prevues - depenses_effectuees, reste_per, ft.Colors.PURPLE),
    ])

    chart_solde = build_piechart([
        (montant_depenses, depense_percent, "#3FEB82"),
        (solde, solde_percent, ft.Colors.RED),
    ])

    # --- Cartes existantes ---
    solde_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Dépenses globales", size=25, weight="bold"),
                ft.Text(f"Total des Dépenses : {montant_depenses} FCFA", size=20, color="#3FEB82"),
                ft.Text(f"Solde global : {solde} FCFA", size=20, color=ft.Colors.RED),
                chart_solde,
            ]),
            padding=20,
        )
    )

    depenses_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Objectifs financiers", size=25, weight="bold"),
                ft.Text(f"Montant total prévu: {depenses_prevues} FCFA", size=20),
                ft.Text(f"Montant encaissé: {depenses_effectuees} FCFA", size=20, color=ft.Colors.BLUE),
                ft.Text(f"Reste: {depenses_prevues - depenses_effectuees} FCFA", size=20, color=ft.Colors.PURPLE),
                chart_objectifs,
            ]),
            padding=20,
        )
    )

    # --- NOUVELLE CARTE: Résumé des dépenses ---
    period_options = ["Hebdomadaire", "Mensuel", "Trimestriel", "Semestriel", "Annuel"]
    period_dropdown = ft.Dropdown(
        width=200,
        options=[ft.dropdown.Option(p) for p in period_options],
        value="Hebdomadaire"
    )
    start_date_picker = ft.DatePicker(field_label_text="Date de début")
    end_date_picker = ft.DatePicker(field_label_text="Date de fin")
    total_dep_label = ft.Text("", size=20, weight="bold")
    chart_depenses_container = ft.Container()

    def update_depenses_summary(e=None):
        today = datetime.today()
        period = period_dropdown.value

        if start_date_picker.value and end_date_picker.value:
            start_date = start_date_picker.value.strftime("%Y-%m-%d")
            end_date = end_date_picker.value.strftime("%Y-%m-%d")
        else:
            if period == "Hebdomadaire":
                start = today - timedelta(days=today.weekday())
                end = start + timedelta(days=6)
            elif period == "Mensuel":
                start = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end = today.replace(day=last_day)
            elif period == "Trimestriel":
                month = (today.month - 1) // 3 * 3 + 1
                start = today.replace(month=month, day=1)
                end_month = month + 2
                last_day = calendar.monthrange(today.year, end_month)[1]
                end = today.replace(month=end_month, day=last_day)
            elif period == "Semestriel":
                month = 1 if today.month <= 6 else 7
                start = today.replace(month=month, day=1)
                end_month = month + 5
                last_day = calendar.monthrange(today.year, end_month)[1]
                end = today.replace(month=end_month, day=last_day)
            elif period == "Annuel":
                start = today.replace(month=1, day=1)
                end = today.replace(month=12, day=31)
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")

        total_dep = get_depenses_by_period(start_date, end_date)
        total_dep_label.value = f"Total des dépenses ({period}): {total_dep} FCFA"

        depense_percent = int((total_dep * 100) / depenses_prevues) if depenses_prevues > 0 else 0
        reste_percent = 100 - depense_percent if depenses_prevues > 0 else 0
        chart_depenses_container.content = build_piechart([
            (total_dep, depense_percent, ft.Colors.BLUE),
            (depenses_prevues - total_dep, reste_percent, ft.Colors.PURPLE)
        ])
        page.update()

    period_dropdown.on_change = update_depenses_summary
    start_date_picker.on_change = update_depenses_summary
    end_date_picker.on_change = update_depenses_summary
    update_depenses_summary()

    depenses_summary_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Résumé des dépenses", size=25, weight="bold"),
                period_dropdown,
                ft.Row([
                    ft.Column([ft.Text("Date de début"), start_date_picker]),
                    ft.Column([ft.Text("Date de fin"), end_date_picker])
                ], spacing=10),
                total_dep_label,
                chart_depenses_container
            ]),
            padding=20
        )
    )

    # --- Carte Notification ---
    notifications = []
    today = datetime.today()
    day_of_month = today.day

    # Notification si dépenses > 50% avant le 15 du mois
    if day_of_month <= 15 and montant_depenses > 0.5 * montant_global:
        notifications.append(("⚠️ Dépenses > 50% du budget avant le 15 du mois", ft.Colors.ORANGE))

    # Notification si dépenses > 80% du budget
    if montant_depenses > 0.8 * montant_global:
        notifications.append(("⚠️ Vous avez consommé plus de 80% du budget mensuel", ft.Colors.RED))

    # Notification si dépenses > budget global
    if montant_depenses > montant_global:
        notifications.append(("🚨 Les dépenses dépassent le budget du mois", ft.Colors.RED))

    notification_controls = []
    if notifications:
        for msg, color in notifications:
            notification_controls.append(ft.Text(msg, size=18, color=color))
    else:
        notification_controls.append(ft.Text("Aucune notification", size=18, color=ft.Colors.GREEN))

    notification_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [ft.Text("Notifications", size=25, weight="bold")] + notification_controls
            ),
            padding=20
        )
    )

    # --- Vue globale ---
    return ft.View(
        "/bord",
        controls=[
            ft.AppBar(
                title=ft.Text("Tableau de Bord"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    ft.Icon(name=ft.Icons.DASHBOARD, size=150, color="#3FEB82"),
                    solde_card,
                    depenses_card,
                    depenses_summary_card,
                    notification_card,  # Carte Notification ajoutée
                ]
            )
        ]
    )
