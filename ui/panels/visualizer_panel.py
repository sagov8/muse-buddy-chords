import flet as ft
from ui.styles import PANEL_BORDER


def build_visualizer_panel(visualizer):
    return ft.Container(
        bgcolor="#141521",
        border_radius=16,
        padding=20,
        border=PANEL_BORDER,
        content=ft.Column(
            spacing=10,
            expand=True,
            controls=[
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.MUSIC_NOTE, color="#6366F1", size=24),
                        ft.Text(
                            "Visualizador del Grafo de Acordes",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#EEF2F6",
                        ),
                    ]
                ),
                ft.Text(
                    "Haz clic y arrastra los acordes para reposicionarlos.",
                    size=13,
                    color="#94A3B8",
                ),
                ft.Container(
                    content=visualizer,
                    alignment=ft.alignment.Alignment.CENTER,
                    expand=True,
                ),
            ],
        ),
    )