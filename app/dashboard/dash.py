import flet as ft
import sqlite3

# ---- Fonction pour récupérer les données de la BD objectifs ----
def get_totaux_objectifs():
    # Connexion à SQLite (base existante)
    conn = sqlite3.connect("objectifs.db")
    cursor = conn.cursor()

    # On additionne tous les montants prévus et encaissés
    cursor.execute("SELECT SUM(montant), SUM(encaisse) FROM objectifs")
    result = cursor.fetchone()
    conn.close()

    # Sécurité si pas de données
    montant_prevu = result[0] if result[0] else 0
    montant_encaisse = result[1] if result[1] else 0
    return montant_prevu, montant_encaisse

# ---- Fonction pour récupérer les données de la BD gains ----
def get_totaux_gain():
    # Connexion à SQLite (base existante)
    conn = sqlite3.connect("budget.db")
    cursor = conn.cursor()

    # On additionne tous les montants prévus et encaissés
    cursor.execute("SELECT amount FROM gains")
    result = cursor.fetchone()
    conn.close()

    # Sécurité si pas de données
    montant = result[0] if result[0] else 0
    return montant

def get_totaux_depense():
    # Connexion à SQLite (base existante)
    conn = sqlite3.connect("depenses.db")
    cursor = conn.cursor()

    # On additionne tous les montants prévus et encaissés
    cursor.execute("SELECT SUM(montant) FROM depenses")
    result = cursor.fetchone()
    conn.close()

    # Sécurité si pas de données
    montant_depenses = result[0] if result[0] else 0
    return montant_depenses


# ---- Vue principale ----
def dashboard_view(page: ft.Page) -> ft.View:
    # Récupération des données depuis la BD
    montant_global = get_totaux_gain()
    montant_depenses = get_totaux_depense()
    Solde = montant_global - montant_depenses
    depenses_prevues, depenses_effectuees = get_totaux_objectifs()

    # Calculs pour le PieChart
    depenses_per = 0
    if depenses_prevues > 0:
        depenses_per = int((depenses_effectuees * 100) / depenses_prevues)
    reste_per = 100 - depenses_per

    # Styles PieChart
    normal_radius = 50
    hover_radius = 60
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

    # Graphique circulaire (prévu vs encaissé)
    chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                depenses_per,
                title=f"{depenses_per}%",
                color=ft.Colors.BLUE,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                reste_per,
                title=f"{reste_per}%",
                color=ft.Colors.PURPLE,
                radius=normal_radius,
            )],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_chart_event,
        expand=True,
    )



    def on_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(charte.sections):
            if idx == e.section_index:
                section.radius = hover_radius
                section.title_style = hover_title_style
            else:
                section.radius = normal_radius
                section.title_style = normal_title_style
        chart.update()



    # Graphique circulaire (Montant global vs Solde)
    charte = ft.PieChart(
        sections=[
            ft.PieChartSection(
                montant_depenses,
                title=f"{int((montant_depenses * 100)/montant_global)}%",
                color=ft.Colors.GREEN_700,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                Solde,
                title=f"{int(100 - ((montant_depenses * 100)/montant_global))}%",
                color=ft.Colors.RED,
                radius=normal_radius,
            )],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_chart_event,
        expand=True,
    )




    # Solde global
    solde_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Budget global", size=25, weight="bold"),
                ft.Text(f"Montant total : {montant_global} FCFA", size=20, color=ft.Colors.GREEN_700),
                ft.Text(f"Solde : {montant_global - montant_depenses} FCFA", size=20, color=ft.Colors.RED,),
                charte,
            ]),
            padding=20,
        )
    )

    # Carte Dépenses
    depenses_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Objectifs financiers", size=25, weight="bold"),
                ft.Text(f"Montant total prévu: {depenses_prevues} FCFA", size=20),
                ft.Text(f"Montant encaissé: {depenses_effectuees} FCFA", size=20, color=ft.Colors.BLUE),
                ft.Text(f"Reste: {depenses_prevues - depenses_effectuees} FCFA", size=20, color=ft.Colors.PURPLE),
                chart,
            ]),
            padding=20,
        )
    )

    # Vue globale
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
                ]
            )
        ]
    )
