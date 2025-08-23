import flet as ft
from menu import menu_view

# Bouton personnalisé
class MyButton(ft.CupertinoFilledButton):
    def __init__(self, text, on_click):
        super().__init__()
        self.bgcolor = "#3FEB82"
        self.text = text
        self.on_click = on_click  
        self.width = 500   

# Variables globales
gain = 5000
depense = 4200

categories = [
    {"nom": "Alimentation", "montant": 1200},
    {"nom": "Transport", "montant": 800},
    {"nom": "Loisirs", "montant": 500},
    {"nom": "Santé", "montant": 700},
]

def budget_view(page: ft.Page) -> ft.View:
    # --- Carte Budget résumé ---
    budget_summary = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Budget du mois", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Prévu : {gain} FCFA | Dépensé : {depense} FCFA", size=18),
                ft.ProgressBar(width=300, value=depense / gain if gain else 0)
            ]),
            padding=20
        ),
        elevation=3
    )

    # --- Catégories ---
    categories_grid = ft.GridView(
        expand=True,
        runs_count=2,
        child_aspect_ratio=2.5,
        spacing=15,
        run_spacing=15,
    )

    for cat in categories:
        categories_grid.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Text(f"{cat['nom']} : {cat['montant']} FCFA"),
                    padding=10
                )
            )
        )

    # --- Ajout d’un budget (dynamique) ---
    budget_list = ft.Column()
    new_budget = ft.TextField(label="Entrez un budget (FCFA)", width=300)

    def add_clicked(e):
        if new_budget.value.strip():
            budget_list.controls.append(
                ft.Text(f"Budget ajouté : {new_budget.value} FCFA", size=16, weight=ft.FontWeight.BOLD)
            )
            new_budget.value = ""
            page.update()

    # --- Vue principale ---
    return ft.View(
        "/budget",
        controls=[
            ft.AppBar(
                title=ft.Text("Budget"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    ft.Icon(name=ft.Icons.ACCOUNT_CIRCLE, size=150),
                    budget_summary,
                    categories_grid,
                    new_budget,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_clicked),
                    budget_list,
                ]
            )
        ]
    )
