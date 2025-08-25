import flet as ft

def dashboard_view(page: ft.Page, gain: int, objectifs: list, depenses: list = None, epargne: int = 0) -> ft.View:
    depenses = depenses or []

    # Calcul de la progression globale des objectifs
    total_montant = sum(obj["montant"] for obj in objectifs) if objectifs else 0
    total_encaissé = sum(obj.get("encaissé", 0) for obj in objectifs) if objectifs else 0
    progression = (total_encaissé / total_montant * 100) if total_montant else 0

    # Calcul du solde global (gain - total dépenses - épargne)
    total_depenses = sum(dep["montant"] for dep in depenses) if depenses else 0
    solde_global = gain - total_depenses - epargne

    # Carte solde
    solde_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Solde global", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"{solde_global} FCFA", size=20, weight=ft.FontWeight.BOLD, color="green")
            ], alignment="center"),
            padding=20
        ),
        width=250, height=120
    )

    # Carte indicateurs clés
    indicateurs = ft.Row(
        controls=[
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Gain actuel", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{gain} FCFA", size=18, weight=ft.FontWeight.BOLD, color="green")
                    ], alignment="center"),
                    padding=20
                ),
                width=200, height=120
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Progression Objectifs", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{progression:.2f} %", size=18, weight=ft.FontWeight.BOLD, color="blue"),
                        ft.ProgressBar(value=progression/100 if total_montant else 0, width=150)
                    ], alignment="center"),
                    padding=20
                ),
                width=220, height=120
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Dépenses totales", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{total_depenses} FCFA", size=18, weight=ft.FontWeight.BOLD, color="red")
                    ], alignment="center"),
                    padding=20
                ),
                width=200, height=120
            )
        ],
        alignment="center",
        spacing=20
    )

    # Derniers objectifs
    derniers_objectifs = ft.Column(
        controls=[
            ft.Text("Derniers objectifs", size=18, weight=ft.FontWeight.BOLD)
        ] + [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.FLAG, color="blue"),
                title=ft.Text(obj["nom"]),
                subtitle=ft.Text(f"{obj.get('encaissé', 0)}/{obj['montant']} FCFA"),
                trailing=ft.ProgressBar(
                    value=(obj.get("encaissé", 0)/obj["montant"]) if obj["montant"] else 0,
                    width=100
                )
            ) for obj in objectifs[-3:]
        ]
    )

    # Actions rapides
    actions = ft.Row(
        controls=[
            ft.ElevatedButton("Ajouter Dépense", icon=ft.Icons.REMOVE, on_click=lambda _: page.go("/depenses")),
            ft.ElevatedButton("Ajouter Recette", icon=ft.Icons.ADD, on_click=lambda _: page.go("/recettes")),
            ft.ElevatedButton("Voir Objectifs", icon=ft.Icons.FLAG, on_click=lambda _: page.go("/objectifs")),
            ft.ElevatedButton("Budget & Épargne", icon=ft.Icons.SAVINGS, on_click=lambda _: page.go("/budget")),
            ft.ElevatedButton("Générer Rapport", icon=ft.Icons.PIE_CHART, on_click=lambda _: generate_report(page)),
        ],
        alignment="center",
        spacing=15
    )

    return ft.View(
        "/dashboard",
        controls=[
            ft.AppBar(
                title=ft.Text("Tableau de bord"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu"))
            ),
            ft.Column(
                controls=[
                    solde_card,
                    ft.Divider(),
                    indicateurs,
                    ft.Divider(),
                    derniers_objectifs,
                    ft.Divider(),
                    actions
                ],
                expand=True,
                horizontal_alignment="center",
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )

# Fonction de génération de rapport (placeholder)
def generate_report(page: ft.Page):
    page.dialog = ft.AlertDialog(
        title=ft.Text("Rapport financier"),
        content=ft.Text("Le rapport est généré automatiquement avec vos données."),
        actions=[ft.ElevatedButton("Fermer", on_click=lambda e: close_dialog(page))]
    )
    page.dialog.open = True
    page.update()

def close_dialog(page: ft.Page):
    page.dialog.open = False
    page.update()
