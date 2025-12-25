import flet as ft
from auth.db import init_db

# Importation de vos vues (Assurez-vous que ces fichiers existent)
from login import login_view
from menu import menu_view
from dettes.dettes import dettes_view
from dashboard.dash import dashboard_view
from budget.budget import budget_view
from epargne.epargne import epargne_view
from auth.singup import signup_view
from depenses.depense import depense_view
from analyses.analyses import analyses_view
from settings.settings import settings_view
from notifications.notifications import notifications_view


def main(page: ft.Page):
    # --- CONFIGURATION DE LA PAGE ---
    page.title = "FinanceApp | 2025"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Palette de couleurs "Légèrement sombre & Moderne"
    page.theme = ft.Theme(
        color_scheme_seed="#3FEB82",
        color_scheme=ft.ColorScheme(
            primary="#3FEB82",          # Vert accent
            surface="#1E2023",          # Gris foncé (Cartes/Menus)
            background="#121417",       # Fond sombre profond (pas noir pur)
            on_surface="#E3E2E6",       # Texte clair
            secondary="#ADB5BD",        # Texte secondaire
        ),
        use_material3=True,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # Configuration fenêtre pour le test Desktop
    page.window_width = 420
    page.window_height = 850
    
    init_db()

    def route_change(e):
        page.views.clear()

        # --- ROUTE ACCUEIL (Style Premium) ---
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Container(
                            expand=True,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_center,
                                end=ft.alignment.bottom_center,
                                colors=["#1E2023", "#121417"],
                            ),
                            content=ft.Column(
                                [
                                    # ft.Spacer(flex=1) remplacé par un Container expansible
                                    ft.Container(expand=True), 
                                    
                                    # Logo avec effet de lueur
                                    ft.Container(
                                        content=ft.Icon(
                                            name=ft.Icons.ANALYTICS_ROUNDED, 
                                            color="#3FEB82", 
                                            size=150
                                        ),
                                        shadow=ft.BoxShadow(blur_radius=100, color="#1A3FEB82"),
                                    ),
                                    ft.Text(
                                        "FinanceApp", 
                                        size=48, 
                                        weight=ft.FontWeight.BOLD, 
                                        color="#FDFDFD",
                                        #letter_spacing=1.5
                                    ),
                                    ft.Text(
                                        "Maîtrisez votre avenir financier", 
                                        size=16, 
                                        color="#ADB5BD",
                                        text_align=ft.TextAlign.CENTER
                                    ),

                                    # ft.Spacer(flex=1) remplacé par un Container expansible
                                    ft.Container(expand=True), 
                                    
                                    # Bouton d'action principal
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Row(
                                                [
                                                    ft.Text("Démarrer l'expérience", size=16, weight="bold"),
                                                    ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=20)
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            bgcolor="#3FEB82",
                                            color="#121417",
                                            on_click=lambda _: page.go("/login"),
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=15),
                                            ),
                                            height=60,
                                        ),
                                        padding=ft.padding.only(left=40, right=40, bottom=50)
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        )
                    ],
                    padding=0
                )
            )

        # --- GESTION DES AUTRES ROUTES ---
        elif page.route == "/login":
            page.views.append(login_view(page))
        elif page.route == "/signup":
            page.views.append(signup_view(page))
        elif page.route == "/menu":
            page.views.append(menu_view(page))
        elif page.route == "/bord":
            page.views.append(dashboard_view(page))
        elif page.route == "/budget":
            page.views.append(budget_view(page))
        elif page.route == "/depenses":
            page.views.append(depense_view(page))
        elif page.route == "/dettes":
            page.views.append(dettes_view(page))
        elif page.route == "/epargne":
            page.views.append(epargne_view(page))
        elif page.route == "/analyses":
            page.views.append(analyses_view(page))
        elif page.route == "/settings":
            page.views.append(settings_view(page))
        elif page.route == "/notifications":
            page.views.append(notifications_view(page))

    
        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            page.window_destroy()

    # --- INITIALISATION ET ÉCOUTEURS ---
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Lancement sur la route actuelle ou accueil
    if page.route == "/":
        page.go("/")
    else:
        page.go(page.route)



# Exécution de l'application
if __name__ == "__main__":
    # Assurez-vous que le dossier 'assets' existe si vous utilisez des images
    ft.app(target=main, assets_dir="assets")
