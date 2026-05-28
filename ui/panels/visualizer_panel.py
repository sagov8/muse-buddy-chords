import flet as ft
from ui.styles import theme_colors


def build_visualizer_panel(visualizer):
    return ft.Container(
        bgcolor=theme_colors.panel_bg,
        border_radius=16,
        padding=20,
        border=theme_colors.panel_border,
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
                            color=theme_colors.text_title,
                        ),
                    ]
                ),
                ft.Text(
                    "Haz clic y arrastra los acordes para reposicionarlos.",
                    size=13,
                    color=theme_colors.text_sub,
                ),
                ft.Container(
                    content=visualizer,
                    alignment=ft.alignment.Alignment.CENTER,
                    expand=True,
                ),
            ],
        ),
    )