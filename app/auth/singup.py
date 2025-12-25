import flet as ft
import hashlib
import time
from auth.db import insert_user, get_user_by_email

# --- Bouton Personnalisé 2025 ---
class MyButton(ft.ElevatedButton):
    def __init__(self, text, on_click):
        super().__init__()
        self.bgcolor = "#3FEB82"
        self.color = "#121417"
        self.text = text
        self.on_click = on_click  
        self.width = 300
        self.height = 50
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        )

def hash_password(password: str) -> str:
    """Hashage SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def signup_view(page: ft.Page):
    # --- Champs de saisie stylisés ---
    username = ft.TextField(
        label="Nom d'utilisateur", 
        width=300, 
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12
    )
    email = ft.TextField(
        label="Email", 
        width=300, 
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12
    )
    password = ft.TextField(
        label="Mot de passe", 
        password=True, 
        can_reveal_password=True, 
        width=300,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=12
    )

    message = ft.Text(value="", size=12, text_align=ft.TextAlign.CENTER)

    def handle_signup(e):
        # Reset message
        message.value = ""
        page.update()

        # Validation
        if not username.value or not email.value or not password.value:
            message.value = "Veuillez remplir tous les champs."
            message.color = ft.Colors.RED_400
            page.update()
            return

        # Vérification unicité email
        if get_user_by_email(email.value):
            message.value = "Cet email est déjà utilisé."
            message.color = ft.Colors.RED_400
            page.update()
            return

        try:
            # Hash et Insertion
            hashed_pwd = hash_password(password.value)
            insert_user(username.value, email.value, hashed_pwd)

            # Succès
            message.value = "Compte créé avec succès ! Redirection..."
            message.color = "#3FEB82"
            page.update()
            
            # Petite pause pour laisser lire le message avant redirection
            time.sleep(1.5)
            page.go("/login")
            
        except Exception as ex:
            message.value = f"Erreur lors de l'inscription : {ex}"
            message.color = ft.Colors.RED_400
            page.update()

    return ft.View(
        "/signup",
        bgcolor="#121417",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.AppBar(
                title=ft.Text("Créer un compte", weight="bold"),
                bgcolor=ft.Colors.TRANSPARENT,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/login"))
            ),
            
            # Logo ou Icone principale
            ft.Container(
                content=ft.Icon(name=ft.Icons.PERSON_ADD_ROUNDED, size=80, color="#3FEB82"),
                margin=ft.margin.only(bottom=20)
            ),
            
            ft.Column([
                username,
                email,
                password,
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            
            ft.Container(height=10),
            
            MyButton("S’inscrire", on_click=handle_signup),
            
            ft.Container(content=message, padding=ft.padding.only(top=10, left=40, right=40)),
            
            ft.TextButton(
                "Déjà un compte ? Connectez-vous", 
                on_click=lambda _: page.go("/login"),
                style=ft.ButtonStyle(color=ft.Colors.SECONDARY)
            )
        ],
    )
