import flet as ft

def dashboard_view(page: ft.Page, gain: int, objectifs: list) -> ft.View:
    # Calcul de la progression globale
    total_montant = sum(obj["montant"] for obj in objectifs) if objectifs else 0
    total_encaissé = sum(obj.get("encaissé", 0) for obj in objectifs) if objectifs else 0
    progression = (total_encaissé / total_montant * 100) if total_montant else 0

    # Affichage des indicateurs principaux
    indicateurs = ft.Row(
        controls=[
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Gain actuel", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{gain} FCFA", size=22, weight=ft.FontWeight.BOLD, color="green"),
                    ], alignment="center"),
                    padding=20,
                ),
                width=200, height=120
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Progression globale", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{progression:.2f} %", size=22, weight=ft.FontWeight.BOLD, color="blue"),
                        ft.ProgressBar(value=progression/100 if total_montant else 0, width=150),
                    ], alignment="center"),
                    padding=20,
                ),
                width=220, height=120
            ),
        ],
        alignment="center",
        spacing=20
    )

    # Liste rapide des 3 derniers objectifs
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

    # Boutons d’actions rapides
    actions = ft.Row(
        controls=[
            ft.ElevatedButton("Ajouter Dépense", icon=ft.Icons.REMOVE, on_click=lambda _: page.go("/depenses")),
            ft.ElevatedButton("Ajouter Recette", icon=ft.Icons.ADD, on_click=lambda _: page.go("/recettes")),
            ft.ElevatedButton("Voir Objectifs", icon=ft.Icons.FLAG, on_click=lambda _: page.go("/objectifs")),
        ],
        alignment="center",
        spacing=15
    )

    return ft.View(
        "/bord",
        controls=[
            ft.AppBar(
                title=ft.Text("Paramètres"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.Column(
                controls=[
                    ft.Text("Résumé financier", size=22, weight=ft.FontWeight.BOLD),
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
