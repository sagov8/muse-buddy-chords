import flet as ft

from ui.graph_visualizer import GraphVisualizer
from ui.panels.control_panel import build_control_panel
from ui.panels.visualizer_panel import build_visualizer_panel
from ui.panels.lyrics_panel import build_lyrics_panel


def build_layout(controller):
    visualizer = GraphVisualizer(width=620, height=340)
    controller.visualizer = visualizer

    control_panel = build_control_panel(controller)
    visualizer_panel = build_visualizer_panel(visualizer)
    lyrics_panel = build_lyrics_panel(controller)

    return ft.Row(
        controls=[
            control_panel,
            ft.Column(
                expand=True,
                spacing=15,
                controls=[
                    ft.Container(
                        content=visualizer_panel,
                        height=520,
                    ),
                    ft.Container(
                        content=lyrics_panel,
                        expand=True,
                    ),
                ],
            ),
        ],
        expand=True,
        spacing=15,
    )