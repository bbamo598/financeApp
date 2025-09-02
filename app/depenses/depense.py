import flet as ft
import sqlite3

# Connexion SQLite
conn = sqlite3.connect("depenses.db", check_same_thread=False)
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    montant INTEGER NOT NULL,
    categorie TEXT NOT NULL,
    date_dep DATE NOT NULL,
    moyen_paiement TEXT NOT NULL,
    notes TEXT
)
""")
conn.commit()


def depense_view(page: ft.Page):

    # Colonne pour afficher les dépenses
    depenses_list = ft.Column()

    # Champs de saisie
    nom_field = ft.TextField(label="Nom de la dépense", width=300)
    montant_field = ft.TextField(label="Montant (FCFA)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    categorie_field = ft.TextField(label="Catégorie", width=200)
    date_field = ft.TextField(label="Date de la dépense (AAAA-MM-JJ)", width=200)
    moyen_paiement_field = ft.TextField(label="Moyen de paiement", width=200)
    notes_field = ft.TextField(label="Notes (facultatif)", width=300)

    # Label résumé global
    total_label = ft.Text("Chargement...", size=35, weight=ft.FontWeight.BOLD)

    # Fonction pour charger les dépenses existantes
    def load_depenses():
        depenses_list.controls.clear()
        cursor.execute("SELECT nom, montant, categorie, date_dep, moyen_paiement, notes FROM depenses ORDER BY id DESC")
        rows = cursor.fetchall()
        total = 0
        for row in rows:
            nom, montant, categorie, date_dep, moyen_paiement, notes = row
            total += montant
            depenses_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text(f"{nom} - {montant} FCFA", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Catégorie: {categorie}"),
                            ft.Text(f"Date: {date_dep}"),
                            ft.Text(f"Moyen: {moyen_paiement}"),
                            ft.Text(f"Notes: {notes if notes else '---'}"),
                        ])
                    )
                )
            )
        total_label.value = f"Total des dépenses: {total} FCFA"
        page.update()

    # Fonction pour ajouter une dépense
    def add_depense(e):
        try:
            nom = nom_field.value.strip()
            montant = int(montant_field.value)
            categorie = categorie_field.value.strip()
            date_dep = date_field.value.strip()
            moyen_paiement = moyen_paiement_field.value.strip()
            notes = notes_field.value.strip()

            if not (nom and montant and categorie and date_dep and moyen_paiement):
                return  # Champs requis manquants

            # Insertion BD
            cursor.execute(
                "INSERT INTO depenses (nom, montant, categorie, date_dep, moyen_paiement, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (nom, montant, categorie, date_dep, moyen_paiement, notes)
            )
            conn.commit()

            # Réinitialiser champs
            nom_field.value = ""
            montant_field.value = ""
            categorie_field.value = ""
            date_field.value = ""
            moyen_paiement_field.value = ""
            notes_field.value = ""

            # Rafraîchir affichage
            load_depenses()
        except ValueError:
            pass

    # Charger les dépenses existantes
    load_depenses()

    return ft.View(
        "/depenses",
        controls=[
            ft.AppBar(
                title=ft.Text("Dépenses"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.Icon(name=ft.Icons.MONEY_OFF, color="#E53935", size=100),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    ft.Text("Ajouter une dépense", size=20, weight=ft.FontWeight.BOLD),
                    nom_field,
                    montant_field,
                    categorie_field,
                    date_field,
                    moyen_paiement_field,
                    notes_field,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_depense),
                    depenses_list,
                    total_label,
                ]
            )
        ]
    )
