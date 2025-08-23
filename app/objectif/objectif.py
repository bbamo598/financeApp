import flet as ft

# Liste globale des objectifs
objectifs = []  # Exemple : {"nom": "Vacances", "montant": 100000, "pourcentage": 20, "encaissé": 0}

def objectifs_view(page: ft.Page, gain: int) -> ft.View:

    # Colonne pour afficher les objectifs
    objectifs_list = ft.Column()

    # Champ de saisie pour un nouvel objectif
    nom_field = ft.TextField(label="Nom de l'objectif", width=300)
    montant_field = ft.TextField(label="Montant (FCFA)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    pourcentage_field = ft.TextField(label="Pourcentage du budget (%)", width=200, keyboard_type=ft.KeyboardType.NUMBER)

    # Label pour résumé global
    total_label = ft.Text("Total objectif : 0 FCFA | Total encaissé : 0 FCFA | Progression globale : 0%", size=18, weight=ft.FontWeight.BOLD)

    # Fonction pour rafraîchir les cartes objectifs
    def update_objectifs():
        objectifs_list.controls.clear()
        total_montant = 0
        total_encaissé = 0
        for obj in objectifs:
            total_montant += obj["montant"]
            total_encaissé += obj.get("encaissé", 0)
            objectifs_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"{obj['nom']}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Montant à atteindre : {obj['montant']} FCFA"),
                            ft.Text(f"Montant déjà encaissé : {obj.get('encaissé', 0)} FCFA"),
                            ft.ProgressBar(
                                value=obj.get("encaissé",0)/obj["montant"] if obj["montant"] else 0,
                                width=300
                            )
                        ]),
                        padding=10
                    )
                )
            )
        # Mise à jour du résumé global
        progression = (total_encaissé / total_montant * 100) if total_montant else 0
        total_label.value = f"Total objectif : {total_montant} FCFA | Total encaissé : {total_encaissé} FCFA | Progression globale : {progression:.2f}%"
        page.update()

    # Fonction pour ajouter un nouvel objectif
    def add_objectif(e):
        try:
            nom = nom_field.value.strip()
            montant = int(montant_field.value)
            epargne = 500000
            pourcentage = int(pourcentage_field.value)
            if nom and montant > 0 and 0 < pourcentage <= 100:
                encaissé = epargne * pourcentage // 100
                objectifs.append({"nom": nom, "montant": montant, "pourcentage": pourcentage, "encaissé": encaissé})
                nom_field.value = ""
                montant_field.value = ""
                pourcentage_field.value = ""
                update_objectifs()
        except ValueError:
            pass  # Ignorer si montant ou pourcentage non valides

    return ft.View(
        "/objectifs",
        controls=[
            ft.AppBar(
                title=ft.Text("Objectifs"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.Icon(name=ft.Icons.CENTER_FOCUS_STRONG, color="#3FEB82", size=200),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    ft.Text("Ajouter un objectif", size=20, weight=ft.FontWeight.BOLD),
                    nom_field,
                    montant_field,
                    pourcentage_field,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_objectif),
                    #total_label,
                    objectifs_list
                ]
            )
        ]
    )
