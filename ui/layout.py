import flet as ft

from ui.graph_visualizer import GraphVisualizer
from ui.panels.control_panel import build_control_panel
from ui.panels.visualizer_panel import build_visualizer_panel


def build_layout(controller):
    visualizer = GraphVisualizer(width=720, height=540)
    controller.visualizer = visualizer

    control_panel = build_control_panel(controller)
    visualizer_panel = build_visualizer_panel(visualizer)

    return ft.Row(
        controls=[
            control_panel,
            visualizer_panel,
        ],
        expand=True,
    )