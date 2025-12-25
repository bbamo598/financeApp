import flet as ft
from datetime import datetime

# ===================== LOGIQUE DE SIMULATION ===================== #

def get_notifications():
    """
    Récupère les notifications. En production, cela viendrait d'une table 'notifications' 
    alimentée par des déclencheurs (triggers) dans vos autres bases.
    """
    return [
        {
            "id": 1,
            "titre": "Alerte Budget",
            "msg": "Vous avez atteint 90% de votre budget 'Loisirs'.",
            "type": "warning",
            "date": "Aujourd'hui, 10:30",
            "icon": ft.Icons.WARNING_ROUNDED,
            "color": ft.Colors.AMBER
        },
        {
            "id": 2,
            "titre": "Rappel Échéance",
            "msg": "Le remboursement de 'Prêt Scolaire' est prévu dans 2 jours.",
            "type": "info",
            "date": "Hier, 18:15",
            "icon": ft.Icons.SCHEDULE_ROUNDED,
            "color": ft.Colors.BLUE
        },
        {
            "id": 3,
            "titre": "Objectif Atteint !",
            "msg": "Félicitations ! Vous avez complété votre objectif 'Épargne Vacances'.",
            "type": "success",
            "date": "23/12/2025",
            "icon": ft.Icons.STAR_ROUNDED,
            "color": "#3FEB82"
        },
        {
            "id": 4,
            "titre": "Conseil IA",
            "msg": "Nous avons détecté une baisse de vos dépenses en transport. Vous pourriez épargner 5000 F de plus.",
            "type": "ai",
            "date": "22/12/2025",
            "icon": ft.Icons.AUTO_AWESOME_ROUNDED,
            "color": ft.Colors.PURPLE_ACCENT
        }
    ]

# ===================== VUE NOTIFICATIONS ===================== #

def notifications_view(page: ft.Page):
    notifs = get_notifications()

    def delete_notif(e, container):
        # Simulation de suppression visuelle
        container.visible = False
        page.update()

    def clear_all(e):
        notifs_col.controls.clear()
        notifs_col.controls.append(
            ft.Container(
                content=ft.Text("Aucune nouvelle notification", color=ft.Colors.SECONDARY),
                padding=50, alignment=ft.alignment.center
            )
        )
        page.update()

    notifs_col = ft.Column(spacing=15, scroll=ft.ScrollMode.HIDDEN)

    # Construction de la liste des notifications
    for n in notifs:
        notif_item = ft.Container(
            bgcolor="#1E2023",
            padding=15,
            border_radius=15,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(n["icon"], color=n["color"], size=24),
                    bgcolor=ft.Colors.with_opacity(0.1, n["color"]),
                    padding=10, border_radius=10
                ),
                ft.Column([
                    ft.Text(n["titre"], weight="bold", size=16),
                    ft.Text(n["msg"], size=13, color=ft.Colors.ON_SURFACE_VARIANT, expand=True),
                    ft.Text(n["date"], size=11, color=ft.Colors.SECONDARY),
                ], expand=True, spacing=2),
                ft.IconButton(
                    icon=ft.Icons.CLOSE_ROUNDED, 
                    icon_size=16, 
                    icon_color=ft.Colors.SECONDARY,
                    on_click=lambda e, c=None: delete_notif(e, e.control.parent.parent.parent) # Récupère le container parent
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START)
        )
        notifs_col.controls.append(notif_item)

    return ft.View(
        "/notifications",
        bgcolor="#121417",
        controls=[
            ft.AppBar(
                title=ft.Text("Centre de Notifications", weight="bold"),
                center_title=True,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
                actions=[
                    ft.TextButton("Tout effacer", on_click=clear_all)
                ]
            ),
            ft.ListView(
                expand=True,
                padding=20,
                controls=[
                    ft.Text("Récentes", size=18, weight="bold", color=ft.Colors.SECONDARY),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    notifs_col
                ]
            )
        ]
    )
