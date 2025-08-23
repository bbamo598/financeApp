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
gain = 0
depense = 0

# Pourcentages pour les catégories
categories_percent = {
    "Obligations": 0.4,
    "Loisirs": 0.2,
    "Urgence": 0.1,
    "Investisement": 0.1
}

def budget_view(page: ft.Page) -> ft.View:

    # --- Carte Budget résumé ---
    budget_summary = ft.Card()
    
    def update_budget_summary():
        budget_summary.content = ft.Container(
            content=ft.Column([
                ft.Text("Budget du mois", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Total : {gain} FCFA | Reste : {gain*0.1} FCFA", size=35),
                ft.ProgressBar(width=300, value=depense / gain if gain else 0)
            ]),
            padding=20
        )
        page.update()
    
    update_budget_summary()

    # --- Catégories calculées dynamiquement ---
    categories_grid = ft.GridView(
        expand=True,
        runs_count=1,
        child_aspect_ratio=2.0,
        spacing=10,
        run_spacing=10,
    )

    def update_categories():
        categories_grid.controls.clear()
        for cat_name, pct in categories_percent.items():
            montant = int(gain * pct)
            categories_grid.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Text(f"{cat_name} :\n {montant} FCFA", size= 30),
                        padding=10
                    )
                )
            )
        page.update()
    
    update_categories()

    # --- Ajout d’un budget dynamique ---
    budget_list = ft.Column()
    new_budget = ft.TextField(label="Entrez un budget (FCFA)", width=300)

    def add_clicked(e):
        global gain
        if new_budget.value.strip():
            try:
                nouvelle_valeur = int(new_budget.value)
                gain = nouvelle_valeur
                depense = gain*0.1
                update_budget_summary()
                update_categories()  # mise à jour des montants des catégories
                ##budget_list.controls.append(
                #    ft.Text(f"Budget ajouté : {gain} FCFA", size=16, weight=ft.FontWeight.BOLD)
               # )
                new_budget.value = ""
                page.update()
            except ValueError:
                new_budget.error_text = "Veuillez entrer un nombre valide"
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
                    ft.Icon(name=ft.Icons.WALLET, size=150, color="#3FEB82"),
                    budget_summary,
                    new_budget,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_clicked),
                    budget_list,
                    categories_grid,

                ]
            )
        ]
    )
