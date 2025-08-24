import flet as ft
import hashlib
from auth.db import get_user_by_email

class MyButton(ft.CupertinoFilledButton):
    def __init__(self, text, on_click):
        super().__init__()
        self.bgcolor = "#3FEB82"
        self.text = text
        self.on_click = on_click  
        self.width = 500  

def login_view(page: ft.Page) -> ft.View:
    # Champs Email et Mot de passe
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(label="Mot de passe", password=True, width=300)
    message = ft.Text(value="", color="red")
    
    # Fonction pour vérifier les informations de connexion
    def login_action(e):
        user = get_user_by_email(email_field.value)
        if user:
            # Hash du mot de passe saisi
            password_hash = hashlib.sha256(password_field.value.encode()).hexdigest()
            if user[3] == password_hash:  # index 3 = password hashé dans la table users
                # Connexion réussie, redirection vers le menu
                page.go("/menu")
                return
        
        # Si email ou mot de passe incorrect
        message.value = "Email ou mot de passe incorrect"
        page.update()
    
    return ft.View(
        "/login",
        controls=[
            ft.AppBar(
                title=ft.Text("Connexion"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/"))
            ),
            ft.Column(
                [
                    ft.Icon(name=ft.Icons.ACCOUNT_CIRCLE, size=150, color="#3FEB82"),
                    email_field,
                    password_field,
                    MyButton("Se connecter", on_click=login_action),
                    message,
                    MyButton("Créer un compte", on_click=lambda _: page.go("/signup")),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
