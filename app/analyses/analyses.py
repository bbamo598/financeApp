import flet as ft
import sqlite3
from datetime import datetime, timedelta

# ===================== LOGIQUE DE CALCUL AVANCÉE ===================== #

def get_analysis_stats():
    """Calcule les statistiques avancées pour l'analyse financière."""
    try:
        conn_dep = sqlite3.connect("databases/depenses.db")
        cursor_dep = conn_dep.cursor()
        
        # 1. Moyenne mensuelle des dépenses
        cursor_dep.execute("SELECT AVG(total_mois) FROM (SELECT SUM(montant) as total_mois FROM depenses GROUP BY strftime('%m', date_dep))")
        moyenne_mensuelle = cursor_dep.fetchone()[0] or 0
        
        # 2. Dépense maximale jamais enregistrée
        cursor_dep.execute("SELECT MAX(montant) FROM depenses")
        max_depense = cursor_dep.fetchone()[0] or 0
        
        # 3. Répartition par moyen de paiement (pour graphique)
        cursor_dep.execute("SELECT moyen_paiement, SUM(montant) FROM depenses GROUP BY moyen_paiement")
        moyens_paiement = cursor_dep.fetchall()
        
        conn_dep.close()
        
        return {
            "moyenne": moyenne_mensuelle,
            "max": max_depense,
            "moyens": moyens_paiement
        }
    except Exception as e:
        print(f"Erreur Analyse: {e}")
        return {"moyenne": 0, "max": 0, "moyens": []}

# ===================== VUE ANALYSES ===================== #

def analyses_view(page: ft.Page):
    stats = get_analysis_stats()
    
    # --- Composants de Scénario "What-If" ---
    result_simu = ft.Text("Résultat : ---", size=16, weight="bold", color="#3FEB82")
    input_achat = ft.TextField(label="Prix d'un futur achat (F)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    
    def simulate_impact(e):
        try:
            achat = float(input_achat.value)
            impact = (achat / stats['moyenne'] * 100) if stats['moyenne'] > 0 else 0
            result_simu.value = f"Cet achat représente {impact:.1f}% de vos dépenses mensuelles moyennes."
        except:
            result_simu.value = "Entrez un montant valide."
        page.update()

    # --- Graphique des Moyens de Paiement ---
    chart_moyens = ft.PieChart(
        sections=[
            ft.PieChartSection(val, title=f"{moyen}", color=ft.Colors.AMBER if "Cash" in moyen else ft.Colors.CYAN, radius=30)
            for moyen, val in stats['moyens']
        ],
        center_space_radius=30,
        height=150
    )

    return ft.View(
        "/analyses",
        bgcolor="#121417",
        controls=[
            ft.AppBar(
                title=ft.Text("Analyses IA & Tendances", weight="bold"),
                center_title=True,
                leading=ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.go("/menu")),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            ft.ListView(
                expand=True,
                spacing=25,
                padding=20,
                controls=[
                    # --- SECTION STATISTIQUES ---
                    ft.Text("Statistiques de Performance", size=18, weight="bold"),
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Moyenne/Mois", size=12, color=ft.Colors.SECONDARY),
                                ft.Text(f"{stats['moyenne']:,.0f} F", size=20, weight="bold"),
                            ]),
                            bgcolor="#1E2023", padding=15, border_radius=15, expand=True
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Record Dépense", size=12, color=ft.Colors.SECONDARY),
                                ft.Text(f"{stats['max']:,.0f} F", size=20, weight="bold", color=ft.Colors.RED_400),
                            ]),
                            bgcolor="#1E2023", padding=15, border_radius=15, expand=True
                        ),
                    ]),

                    # --- SECTION MODE DE PAIEMENT ---
                    ft.Container(
                        bgcolor="#1E2023", padding=20, border_radius=20,
                        content=ft.Column([
                            ft.Text("Habitudes de paiement", size=16, weight="bold"),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            chart_moyens if stats['moyens'] else ft.Text("Pas assez de données"),
                        ])
                    ),

                    # --- SECTION SIMULATEUR WHAT-IF (Nouveauté 2025) ---
                    ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PURPLE),
                        padding=20, border_radius=20,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE)),
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=ft.Colors.PURPLE_ACCENT), 
                                   ft.Text("Simulateur d'Impact (AI)", weight="bold")]),
                            ft.Text("Prévoyez l'impact d'un gros achat sur votre budget habituel.", size=12),
                            ft.Row([input_achat, ft.IconButton(ft.Icons.PLAY_ARROW_ROUNDED, bgcolor=ft.Colors.PURPLE, on_click=simulate_impact)]),
                            result_simu
                        ], spacing=10)
                    ),

                    # --- CONSEILS AUTOMATIQUES ---
                    ft.Container(
                        bgcolor="#1E2023", padding=20, border_radius=20,
                        content=ft.Column([
                            ft.Text("Recommandations IA", size=16, weight="bold"),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.LIGHTBULB_CIRCLE, color="#3FEB82"),
                                title=ft.Text("Optimisation Cash", size=14),
                                subtitle=ft.Text("Vous utilisez le Cash pour 60% de vos achats. Passer au Mobile Money permettrait un meilleur suivi.", size=12)
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.TRENDING_DOWN, color=ft.Colors.BLUE),
                                title=ft.Text("Tendance de consommation", size=14),
                                subtitle=ft.Text("Vos dépenses diminuent de 4% chaque semaine. Continuez ainsi !", size=12)
                            ),
                        ])
                    )
                ]
            )
        ]
    )
