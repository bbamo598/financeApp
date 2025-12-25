import flet as ft
import sqlite3
from datetime import datetime, timedelta # Ajout de timedelta ici
import calendar

# ===================== FONCTIONS DE DONNÉES ===================== #

def fetch_finance_data(period="Mois"):
    """Récupère les données réelles selon la période sélectionnée"""
    try:
        today = datetime.today()
        # Définition des dates
        if period == "Semaine":
            # Correction : Utilisation de timedelta (sans ft.)
            start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        elif period == "Année":
            start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        else: # Mois par défaut
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
        
        end_date = today.strftime("%Y-%m-%d")

        # 1. Revenus (Base budget.db)
        conn = sqlite3.connect("databases/budget.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM gains WHERE date(date) BETWEEN ? AND ?", (start_date, end_date))
        result_gains = cursor.fetchone()
        gains = result_gains[0] if result_gains and result_gains[0] else 0
        conn.close()

        # 2. Dépenses (Base depenses.db)
        conn = sqlite3.connect("databases/depenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(montant) FROM depenses WHERE date_dep BETWEEN ? AND ?", (start_date, end_date))
        result_depenses = cursor.fetchone()
        depenses = result_depenses[0] if result_depenses and result_depenses[0] else 0
        
        # Récupération pour le graphique (Top 3 catégories)
        cursor.execute("SELECT categorie, SUM(montant) FROM depenses GROUP BY categorie ORDER BY SUM(montant) DESC LIMIT 3")
        categories_data = cursor.fetchall()
        conn.close()

        return {
            "gains": gains,
            "depenses": depenses,
            "solde": gains - depenses,
            "categories": categories_data if categories_data else [("N/A", 1)]
        }
    except Exception as e:
        print(f"Erreur DB Dashboard: {e}")
        return {"gains": 0, "depenses": 0, "solde": 0, "categories": [("N/A", 1)]}

# ===================== VUE DASHBOARD ===================== #

def dashboard_view(page: ft.Page) -> ft.View:
    
    # --- États des widgets ---
    txt_solde = ft.Text("0 FCFA", color="#121417", size=32, weight="bold")
    txt_revenus = ft.Text("0 F", size=20, weight="bold")
    txt_depenses = ft.Text("0 F", size=20, weight="bold")
    pie_chart = ft.PieChart(sections=[], sections_space=2, center_space_radius=30)
    
    def update_ui(period="Mois"):
        data = fetch_finance_data(period)
        txt_solde.value = f"{data['solde']:,.0f} F"
        txt_revenus.value = f"{data['gains']:,.0f} F"
        txt_depenses.value = f"{data['depenses']:,.0f} F"
        
        # Mise à jour graphique
        colors = [ft.Colors.BLUE, "#3FEB82", ft.Colors.ORANGE]
        pie_chart.sections = [
            ft.PieChartSection(val, title=str(cat), color=colors[i % 3], radius=30 + (i*5))
            for i, (cat, val) in enumerate(data['categories'])
        ]
        page.update()

    def stat_card(title, control, color, icon):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=color, size=20), ft.Text(title, size=12, color=ft.Colors.SECONDARY)]),
                control,
            ], spacing=5),
            bgcolor="#1E2023", padding=12, border_radius=15, expand=True,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        )

    # --- Actions des boutons ---
    def handle_export(e):
        page.snack_bar = ft.SnackBar(ft.Text(f"Exportation lancée..."), bgcolor="#3FEB82")
        page.snack_bar.open = True
        page.update()

    def on_filter_change(e):
        # On récupère le texte du label du Chip sélectionné
        update_ui(e.control.label.value)

    # --- Initialisation UI ---
    update_ui()

    return ft.View(
        "/bord",
        [
            ft.AppBar(
                title=ft.Text("Tableau de Bord", weight="bold"),
                center_title=True, bgcolor=ft.Colors.TRANSPARENT,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                actions=[
                    ft.IconButton(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, icon_color="#3FEB82", on_click=lambda _: page.go("/notifications")),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(icon=ft.Icons.PICTURE_AS_PDF, text="Export PDF", on_click=handle_export),
                            ft.PopupMenuItem(icon=ft.Icons.TABLE_CHART, text="Export Excel", on_click=handle_export),
                        ]
                    ),
                ]
            ),

            ft.Column([
                # Filtrage fonctionnel
                ft.Row([
                    ft.Chip(label=ft.Text("Mois"), on_select=on_filter_change, selected=True),
                    ft.Chip(label=ft.Text("Semaine"), on_select=on_filter_change),
                    ft.Chip(label=ft.Text("Année"), on_select=on_filter_change),
                ], scroll=ft.ScrollMode.AUTO),

                # Hero Card
                ft.Container(
                    gradient=ft.LinearGradient(colors=["#3FEB82", "#1E7E46"]),
                    padding=20, border_radius=20,
                    content=ft.Column([
                        ft.Text("Solde Disponible", color="#121417", size=14),
                        txt_solde,
                        ft.Row([ft.Icon(ft.Icons.TRENDING_UP, color="#121417", size=16), ft.Text("Données synchronisées", color="#121417", size=12)])
                    ]),
                ),

                # Synthèse
                ft.Row([
                    stat_card("Revenus", txt_revenus, "#3FEB82", ft.Icons.ARROW_UPWARD),
                    stat_card("Dépenses", txt_depenses, ft.Colors.RED_400, ft.Icons.ARROW_DOWNWARD),
                ]),

                # Graphique
                ft.Text("Répartition des dépenses", size=16, weight="bold"),
                ft.Container(content=pie_chart, bgcolor="#1E2023", padding=15, border_radius=20, height=180),

                # AI Notification
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.05, "#3FEB82"),
                    padding=15, border_radius=15,
                    content=ft.Row([
                        ft.Icon(ft.Icons.LIGHTBULB_CIRCLE, color="#3FEB82"),
                        ft.Text("IA : Vos dépenses sont stables par rapport à la période précédente.", size=12, expand=True)
                    ])
                ),

                # Histogramme
                ft.BarChart(
                    bar_groups=[
                        ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(from_y=0, to_y=10, color="#3FEB82", width=15)]),
                        ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(from_y=0, to_y=15, color="#3FEB82", width=15)]),
                        ft.BarChartGroup(x=2, bar_rods=[ft.BarChartRod(from_y=0, to_y=8, color="#3FEB82", width=15)]),
                    ],
                    height=120,
                )
            ], spacing=20, scroll=ft.ScrollMode.HIDDEN, expand=True)
        ],
        bgcolor="#121417", padding=20
    )
