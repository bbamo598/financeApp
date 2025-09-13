import flet as ft
import sqlite3
from datetime import date

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

# Fonction pour charger les catégories depuis la BD budget
def load_categories():
    conn_budget = sqlite3.connect("budget.db")
    cursor_budget = conn_budget.cursor()
    cursor_budget.execute("SELECT name FROM categories ORDER BY name")
    cats = [row[0] for row in cursor_budget.fetchall()]
    conn_budget.close()
    return cats if cats else ["Autre"]

def depense_view(page: ft.Page):

    # Colonne pour afficher les dépenses
    depenses_list = ft.Column()

    # Champs de saisie
    nom_field = ft.TextField(label="Nom de la dépense", width=300)
    montant_field = ft.TextField(label="Montant (FCFA)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    
    # Dropdown catégories
    categorie_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in load_categories()],
        value=load_categories()[0]  # valeur par défaut
    )
    
    # DatePicker facultatif (vide par défaut)
    date_field = ft.TextField(label="Date de la dépense (AAAA-MM-JJ)", width=200)
    
    
    # Dropdown pour méthode de paiement
    moyen_paiement_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("Cash"),
            ft.dropdown.Option("Mobile Money"),
            ft.dropdown.Option("Carte Bancaire")
        ],
        value="Cash"  # valeur par défaut
    )
    
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
            categorie = categorie_dropdown.value
            # Si aucune date sélectionnée, prendre la date du jour
            date_dep = date_field.value.strip()
            moyen_paiement = moyen_paiement_dropdown.value
            notes = notes_field.value.strip()

            if not (nom and montant and categorie and moyen_paiement):
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
            categorie_dropdown.options = [ft.dropdown.Option(c) for c in load_categories()]
            categorie_dropdown.value = load_categories()[0]
            date_field.value = None  # réinitialiser à vide
            moyen_paiement_dropdown.value = "Cash"
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
                    ft.Column([ft.Text("Catégorie"), categorie_dropdown], spacing=5),
                    ft.Column([ft.Text("Date de la dépense (facultatif)"), date_field], spacing=5),
                    ft.Column([ft.Text("Moyen de paiement"), moyen_paiement_dropdown], spacing=5),
                    notes_field,
                    ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_depense),
                    depenses_list,
                    total_label,
                ]
            )
        ]
    )
