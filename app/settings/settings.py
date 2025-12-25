import flet as ft
import sqlite3

# ===================== LOGIQUE DE DONNÉES ===================== #

def get_user_profile():
    """Récupère les informations de l'utilisateur (Simulé ou via auth.db)."""
    # Ici vous pouvez connecter votre base auth.db si nécessaire
    return {
        "nom": "Utilisateur Finance",
        "email": "contact@financeapp.2025",
        "devise": "FCFA (XAF)",
        "version": "v2.1.0 - 2025 Edition"
    }

# ===================== VUE PARAMÈTRES ===================== #

def settings_view(page: ft.Page):
    user = get_user_profile()

    # --- Éléments de Profil ---
    nom_field = ft.Text(user["nom"], size=20, weight="bold")
    email_field = ft.Text(user["email"], size=14, color=ft.Colors.SECONDARY)

    # --- Switchs de Configuration ---
    switch_biometrie = ft.Switch(value=True, active_color="#3FEB82")
    switch_notifs = ft.Switch(value=True, active_color="#3FEB82")
    switch_dark_mode = ft.Switch(value=True, active_color="#3FEB82", disabled=True) # Toujours activé pour le design 2025

    def on_logout(e):
        page.go("/login")

    def show_info(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="#3FEB82")
        page.snack_bar.open = True
        page.update()

    return ft.View(
        "/settings",
        bgcolor="#121417",
        controls=[
            ft.AppBar(
                title=ft.Text("Paramètres", weight="bold"),
                center_title=True,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.ListView(
                expand=True,
                spacing=20,
                padding=20,
                controls=[
                    # --- SECTION PROFIL ---
                    ft.Container(
                        bgcolor="#1E2023", padding=20, border_radius=20,
                        content=ft.Row([
                            ft.CircleAvatar(
                                content=ft.Icon(ft.Icons.PERSON_ROUNDED, size=30),
                                radius=30, bgcolor="#3FEB82", color="#121417"
                            ),
                            ft.VerticalDivider(),
                            ft.Column([nom_field, email_field], spacing=2)
                        ])
                    ),

                    # --- SECTION PRÉFÉRENCES ---
                    ft.Text("Préférences App", size=16, weight="bold", color=ft.Colors.SECONDARY),
                    ft.Container(
                        bgcolor="#1E2023", border_radius=20,
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.MONETIZATION_ON_ROUNDED, color="#3FEB82"),
                                title=ft.Text("Devise principale"),
                                subtitle=ft.Text(user["devise"]),
                                on_click=lambda _: show_info("Changement de devise bientôt disponible")
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.NOTIFICATIONS_ROUNDED, color="#3FEB82"),
                                title=ft.Text("Notifications push"),
                                trailing=switch_notifs
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.DARK_MODE_ROUNDED, color="#3FEB82"),
                                title=ft.Text("Mode Sombre (2025 Focus)"),
                                trailing=switch_dark_mode
                            ),
                        ], spacing=0)
                    ),

                    # --- SECTION SÉCURITÉ ---
                    ft.Text("Sécurité", size=16, weight="bold", color=ft.Colors.SECONDARY),
                    ft.Container(
                        bgcolor="#1E2023", border_radius=20,
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.FINGERPRINT_ROUNDED, color=ft.Colors.BLUE),
                                title=ft.Text("Authentification Biométrique"),
                                subtitle=ft.Text("FaceID / Empreinte"),
                                trailing=switch_biometrie
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.LOCK_ROUNDED, color=ft.Colors.BLUE),
                                title=ft.Text("Changer le mot de passe"),
                                on_click=lambda _: page.go("/signup") # Redirection vers signup pour reset
                            ),
                        ], spacing=0)
                    ),

                    # --- SECTION SUPPORT & INFOS ---
                    ft.Container(
                        bgcolor="#1E2023", border_radius=20,
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=ft.Colors.AMBER),
                                title=ft.Text("Version de l'application"),
                                subtitle=ft.Text(user["version"])
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.HELP_OUTLINE_ROUNDED, color=ft.Colors.AMBER),
                                title=ft.Text("Aide & Support"),
                                on_click=lambda _: show_info("Support : support@financeapp.com")
                            ),
                        ], spacing=0)
                    ),

                    # --- DÉCONNEXION ---
                    ft.ElevatedButton(
                        "Se déconnecter",
                        icon=ft.Icons.LOGOUT_ROUNDED,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED_400),
                        color=ft.Colors.RED_400,
                        height=50,
                        on_click=on_logout,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
                    ),
                    
                    ft.Text("© 2025 FinanceApp Team. Tous droits réservés.", 
                            size=10, text_align=ft.TextAlign.CENTER, color=ft.Colors.SECONDARY)
                ]
            )
        ]
    )
