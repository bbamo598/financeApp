import flet as ft
import hashlib
from auth.db import insert_user, get_user_by_email

class MyButton(ft.CupertinoFilledButton):
    def __init__(self, text, on_click):
        super().__init__()
        self.bgcolor = "#3FEB82"
        self.text = text
        self.on_click = on_click  
        self.width = 500  

def hash_password(password: str) -> str:
    """Hashage simple SHA256 (à remplacer par bcrypt/argon2 en prod)."""
    return hashlib.sha256(password.encode()).hexdigest()

def signup_view(page: ft.Page):
    username = ft.TextField(label="Nom d'utilisateur", width=300)
    email = ft.TextField(label="Email", width=300)
    password = ft.TextField(label="Mot de passe", password=True, can_reveal_password=True, width=300)

    message = ft.Text(value="", color="red")

    def handle_signup(e):
        # Vérif champs vides
        if not username.value or not email.value or not password.value:
            message.value = "Veuillez remplir tous les champs."
            message.color = "red"
            page.update()
            return

        # Vérification unicité email
        if get_user_by_email(email.value):
            message.value = "Cet email est déjà utilisé."
            message.color = "red"
            message.update()
            return

        # Hash du mot de passe avant stockage
        hashed_pwd = hash_password(password.value)

        # Sauvegarde en BD
        insert_user(username.value, email.value, hashed_pwd)

        # Message de succès
        message.value = "Inscription réussie \nVeuillez confirmer votre email pour activer le compte."
        message.color = "green"
        page.update()

        # (Optionnel) Redirection auto après quelques secondes
        #page.go("/login")

    return ft.View(
        "/signup",
        [
            ft.AppBar(
                title=ft.Text("Inscription"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/login"))
            ),
            ft.Icon(name=ft.Icons.ACCOUNT_CIRCLE, size=150, color="#3FEB82"),
            ft.Text("Inscription", size=24, weight="bold"),
            username,
            email,
            password,
            MyButton("S’inscrire", on_click=handle_signup),
            message,
        ],
    )
