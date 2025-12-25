import flet as ft
import hashlib
from auth.db import get_user_by_email

# --- Bouton Stylisé 2025 ---
class MyButton(ft.ElevatedButton):
    def __init__(self, text, on_click, is_primary=True):
        super().__init__()
        # Vert pour l'action principale, Gris transparent pour l'action secondaire
        self.bgcolor = "#3FEB82" if is_primary else ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        self.color = "#121417" if is_primary else ft.Colors.WHITE
        self.text = text
        self.on_click = on_click  
        self.width = 300
        self.height = 50
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        )

def login_view(page: ft.Page) -> ft.View:
    # --- Champs de saisie avec icônes ---
    email_field = ft.TextField(
        label="Email", 
        width=300, 
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=12
    )
    password_field = ft.TextField(
        label="Mot de passe", 
        password=True, 
        can_reveal_password=True,
        width=300, 
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=12
    )
    message = ft.Text(value="", color=ft.Colors.RED_400, size=12)
    
    def login_action(e):
        if not email_field.value or not password_field.value:
            message.value = "Veuillez remplir tous les champs"
            page.update()
            return

        user = get_user_by_email(email_field.value)
        if user:
            # Hashage pour comparaison
            password_hash = hashlib.sha256(password_field.value.encode()).hexdigest()
            # user[3] correspond au mot de passe dans votre structure de table
            if user[3] == password_hash:
                # Stockage de la session (Optionnel mais recommandé pour 2025)
                page.session.set("user_id", user[0])
                page.session.set("username", user[1])
                
                page.go("/menu")
                return
        
        message.value = "Email ou mot de passe incorrect"
        page.update()
    
    return ft.View(
        "/login",
        bgcolor="#121417",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.AppBar(
                title=ft.Text("Bienvenue", weight="bold"),
                bgcolor=ft.Colors.TRANSPARENT,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/"))
            ),
            
            # Espace visuel / Logo
            ft.Container(
                content=ft.Icon(name=ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=100, color="#3FEB82"),
                margin=ft.margin.only(bottom=20)
            ),
            
            ft.Column(
                [
                    email_field,
                    password_field,
                    ft.Container(content=message, padding=ft.padding.only(bottom=10)),
                    MyButton("Se connecter", on_click=login_action),
                    ft.Text("ou", color=ft.Colors.SECONDARY, size=12),
                    MyButton("Créer un compte", on_click=lambda _: page.go("/signup"), is_primary=False),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            
            # Option mot de passe oublié (esthétique)
            ft.TextButton(
                "Mot de passe oublié ?", 
                on_click=lambda _: print("Reset..."),
                style=ft.ButtonStyle(color=ft.Colors.SECONDARY)
            )
        ]
    )
