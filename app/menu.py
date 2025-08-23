import flet as ft

def menu_view(page: ft.Page) -> ft.View:
    def menu_item(icon, label, color, route):
        return ft.Column(
            [
                ft.IconButton(
                    icon=icon,
                    icon_size=120,
                    icon_color=color,
                    tooltip=label,
                    on_click=lambda _: page.go(route)
                ),
                ft.Text(label, size=18, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    return ft.View(
        "/menu",
        [
            ft.AppBar(
                title=ft.Text("Menu"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/login")),
            ),
            ft.Text("Menu", size=35, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),

            ft.GridView(
                expand=True,
                max_extent=200,  # largeur max de chaque case
                spacing=30,
                run_spacing=30,
                child_aspect_ratio=0.9,  # ajuste hauteur/largeur
                controls=[
                    menu_item(ft.Icons.DASHBOARD, "Tableau de bord", "#3FEB82", "/bord"),
                    menu_item(ft.Icons.SAVINGS, "Épargne", "#FF6A13", "/epargne"),
                    menu_item(ft.Icons.LIST_ALT, "Dépenses", "#0C96FF", "/depenses"),
                    menu_item(ft.Icons.CENTER_FOCUS_STRONG, "Objectifs", "#FF1915", "/objectifs"),
                    menu_item(ft.Icons.WALLET, "Budget", "#25BBFF", "/budget"),
                    menu_item(ft.Icons.BAR_CHART, "Analyse", "#1712FF", "/analyse"),
                    menu_item(ft.Icons.SETTINGS, "Paramètres", "#7E7E7E", "/parameters"),
                ],
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
