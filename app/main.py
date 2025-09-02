import flet as ft
import base64
import os
from auth.db import init_db
from login import login_view
from menu import menu_view
from parametres.parameters import parameters_view
from dashboard.dash import dashboard_view
from budget.budget import budget_view
from objectif.objectif import objectifs_view
#from budget.budget import gain
#from objectif.objectif import objectifs
from auth.singup import signup_view
from depenses.depense import depense_view



def load_image_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def main(page: ft.Page):
    page.title = "Finance App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    init_db()

    def route_change(e):
        page.views.clear()

        if page.route == "/":
            # Page d’accueil

            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Icon(name=ft.Icons.ANALYTICS, color="#3FEB82", size=250),
                        ft.Text("FinanceApp", size=55, weight=ft.FontWeight.BOLD),
                        ft.Text("Master the management of your money !", size=15),
                        ft.TextButton("Let's go!", on_click=lambda _: page.go("/login")),
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        elif page.route == "/login":
            # Appel de la page importée
            page.views.append(login_view(page))
        elif page.route == "/menu":
            page.views.append(menu_view(page))
        elif page.route == "/parameters":
            page.views.append(parameters_view(page))
        elif page.route == "/bord":
            page.views.append(dashboard_view(page))
        elif page.route == "/budget":
            page.views.append(budget_view(page))
        elif page.route == "/objectifs":
            page.views.append(objectifs_view(page))
        elif page.route == "/signup":
            page.views.append(signup_view(page))
        elif page.route == "/depenses":
            page.views.append(depense_view(page))
    
        page.update()


    def view_pop(view):
        # Supprime la vue actuelle
        page.views.pop()
        if page.views:
            # Va à la vue précédente
            page.go(page.views[-1].route)
        else:
            # Quitter l'app si plus de vues
            page.window_destroy()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)




    #page.on_route_change = route_change
    page.go("/")



ft.app(target=main)
