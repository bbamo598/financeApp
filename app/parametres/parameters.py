import flet as ft
import base64
import os

def load_image_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

class MyButton(ft.CupertinoFilledButton):
    def __init__(self, text, on_click):
        super().__init__()
        self.bgcolor = ft.Colors.GREEN_700
       # self.color = ft.Colors.LIME_800
        self.text = text
        self.on_click = on_click  
        self.width = 500   



def parameters_view(page: ft.Page) -> ft.View:
    return ft.View(
        "/parameters",
        [
            ft.AppBar(
                title=ft.Text("Paramètres"),
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/menu")),
            ),
            ft.Icon(name=ft.Icons.SETTINGS, color="#3FEB82", size=200),
            ft.Text("Paramètres", size=35, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    [
                        ft.TextButton(text="Sécurité", icon=ft.Icons.SECURITY, style=ft.ButtonStyle(text_style=ft.TextStyle(size=30, weight=ft.FontWeight.BOLD)), on_click=lambda _: page.go("/menu")),
                        ft.TextButton(text="Notification", icon=ft.Icons.CIRCLE_NOTIFICATIONS, style=ft.ButtonStyle(text_style=ft.TextStyle(size=30, weight=ft.FontWeight.BOLD)), on_click=lambda _: page.go("/menu")),
                        ft.TextButton(text="Thèmes", icon=ft.Icons.DARK_MODE_OUTLINED, style=ft.ButtonStyle(text_style=ft.TextStyle(size=30, weight=ft.FontWeight.BOLD)), on_click=lambda _: page.go("/menu")),
                        ft.TextButton(text="Stockage", icon=ft.Icons.STORAGE, style=ft.ButtonStyle(text_style=ft.TextStyle(size=30, weight=ft.FontWeight.BOLD)), on_click=lambda _: page.go("/menu")),
                        ft.TextButton(text="A propos", icon=ft.Icons.MORE_HORIZ, style=ft.ButtonStyle(text_style=ft.TextStyle(size=30, weight=ft.FontWeight.BOLD)), on_click=lambda _: page.go("/menu")),  
                    ]
                    ),
                alignment=ft.alignment.center_left
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
