import flet as ft

def menu_view(page: ft.Page) -> ft.View:
    def menu_item(icon, label, color, route):
        # Création d'une carte stylisée pour chaque option
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        name=icon,
                        size=50, # Taille plus équilibrée pour 2025
                        color=color,
                    ),
                    ft.Text(
                        label, 
                        size=14, 
                        weight=ft.FontWeight.W_600, 
                        color=ft.Colors.ON_SURFACE,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.Colors.with_opacity(0.05, color), # Fond très léger assorti à l'icône
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
            border_radius=20,
            padding=20,
            on_click=lambda _: page.go(route),
            # Effet de survol (uniquement desktop) et animation
            animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            ink=True, # Effet d'onde au clic
        )

    return ft.View(
        "/menu",
        [
            # AppBar Modernisée
            ft.AppBar(
                title=ft.Text("FinanceApp", weight="bold"),
                center_title=True,
                bgcolor=ft.Colors.TRANSPARENT,
                leading=ft.IconButton(
                    ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, 
                    icon_size=20,
                    on_click=lambda _: page.go("/login")
                ),
                actions=[
                    ft.IconButton(ft.Icons.PERSON_ROUNDED, on_click=lambda _: page.go("/profil"))
                ]
            ),

            ft.Container(
                padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                content=ft.Column(
                    [
                        ft.Text("Bonjour,", size=16, color=ft.Colors.SECONDARY),
                        ft.Text("Que voulez-vous faire ?", size=24, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=0,
                )
            ),

            # Grille de navigation
            ft.Container(
                expand=True,
                padding=20,
                content=ft.GridView(
                    expand=True,
                    max_extent=180,
                    spacing=20,
                    run_spacing=20,
                    child_aspect_ratio=1.0, # Carré parfait pour un look propre
                    controls=[
                        # Utilisation d'icônes ROUNDED pour un look plus premium
                        menu_item(ft.Icons.DASHBOARD_CUSTOMIZE_ROUNDED, "Tableau de bord", "#3FEB82", "/bord"),
                        menu_item(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, "Mon Budget", "#25BBFF", "/budget"),
                        menu_item(ft.Icons.RECEIPT_LONG_ROUNDED, "Dépenses", "#FFC107", "/depenses"),
                        menu_item(ft.Icons.SAVINGS_ROUNDED, "Épargne", "#FF6A13", "/epargne"),
                        menu_item(ft.Icons.PAYMENTS_ROUNDED, "Dettes", "#F44336", "/dettes"),
                        menu_item(ft.Icons.INSIGHTS_ROUNDED, "Analyses", "#9C27B0", "/analyses"),
                        menu_item(ft.Icons.SETTINGS_SUGGEST_ROUNDED, "Paramètres", "#ADB5BD", "/settings"),
                    ],
                ),
            )
        ],
        bgcolor="#121417", # Rappel du fond légèrement sombre du main.py
    )
