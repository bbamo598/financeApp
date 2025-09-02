import flet as ft
import sqlite3

# Connexion SQLite
conn = sqlite3.connect("objectifs.db", check_same_thread=False)
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS objectifs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    montant INTEGER NOT NULL,
    pourcentage INTEGER NOT NULL,
    encaisse INTEGER NOT NULL
)
""")
conn.commit()


def objectifs_view(page: ft.Page):

    # Colonne pour afficher les objectifs
    objectifs_list = ft.Column()

    # Champs de saisie
    nom_field = ft.TextField(label="Nom de l'objectif", width=300)
    montant_field = ft.TextField(label="Montant (FCFA)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    pourcentage_field = ft.TextField(label="Pourcentage du budget (%)", width=200, keyboard_type=ft.KeyboardType.NUMBER)

    # Label résumé global
    total_label = ft.Text("Chargement...", size=18, weight=ft.FontWeight.BOLD)

    # Fonction pour charger les objectifs depuis la BD
    def load_objectifs():
        objectifs_list.controls.clear()
        cursor.execute("SELECT nom, montant, pourcentage, encaisse FROM objectifs")
        rows = cursor.fetchall()

        total_montant = 0
        total_encaisse = 0

        for nom, montant, pourcentage, encaisse in rows:
            total_montant += montant
            total_encaisse += encaisse
            objectifs_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(nom, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Montant à atteindre : {montant} FCFA"),
                            ft.Text(f"Montant déjà encaissé : {encaisse} FCFA"),
                            ft.ProgressBar(
                                value=encaisse/montant if montant else 0,
                                width=300
                            )
                        ]),
                        padding=10
                    )
                )
            )

        progression = (total_encaisse / total_montant * 100) if total_montant else 0
        total_label.value = f"Total objectif : {total_montant} FCFA | Total encaissé : {total_encaisse} FCFA | Progression globale : {progression:.2f}%"
        page.update()

    # Fonction pour ajouter un objectif
    def add_objectif(e):
        try:
            nom = nom_field.value.strip()
            montant = int(montant_field.value)
            pourcentage = int(pourcentage_field.value)
            epargne = 500000  # Exemple fixe
            if nom and montant > 0 and 0 < pourcentage <= 100:
                encaisse = epargne * pourcentage // 100

                # Insertion BD
                cursor.execute(
                    "INSERT INTO objectifs (nom, montant, pourcentage, encaisse) VALUES (?, ?, ?, ?)",
                    (nom, montant, pourcentage, encaisse)
                )
                conn.commit()

                # Réinitialiser champs
                nom_field.value = ""
                montant_field.value = ""
                pourcentage_field.value = ""

                # Rafraîchir affichage
                load_objectifs()
        except ValueError:
            pass

    # Charger les objectifs existants
    load_objectifs()

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
