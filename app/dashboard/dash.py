import flet as ft

def dashboard_view(page: ft.Page) -> ft.View:

    # Données
    depenses_prevues = 1500
    depenses_effectuees = 1250
    depenses_per = (depenses_effectuees * 100)/depenses_prevues
    depenses_per= int(depenses_per)
    reste_per=100 - depenses_per
    epargne = 400

    # Vue dépenses

    depenses_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Dépenses", size=25, weight="bold"),
                ft.Text(f"Prévu: {depenses_prevues} FCFA", size=20),
                ft.Text(f"Effectué: {depenses_effectuees} FCFA", size=20, color=ft.Colors.BLUE),
                ft.Text(f"Reste: {depenses_prevues - depenses_effectuees} FCFA", size=20, color=ft.Colors.PURPLE),
            ]),
            padding=20,
        )
    )

    #PieChart

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


    chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                depenses_per,
                title=f"{depenses_per}%",
                #title_style=normal_title_style,
                color=ft.Colors.BLUE,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                reste_per,
                title=f"{reste_per}%",
                #title_style=normal_title_style,
                color=ft.Colors.PURPLE,
                radius=normal_radius,
            )],
        sections_space=0,
        center_space_radius=40,
        on_chart_event=on_chart_event,
        expand=True,
    )














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
                    depenses_card,
                    chart,
                ]
            )
        ]
    )