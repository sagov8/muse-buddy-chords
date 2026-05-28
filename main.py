import flet as ft

from app.state import AppState
from ui.layout import build_layout
from controller.chord_controller import ChordController


def configure_page(page: ft.Page):
    page.title = "Chord Generator"
    page.window_width = 1250
    page.window_height = 820
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0C10"
    page.padding = 15
    page.spacing = 15

    page.fonts = {
        "Outfit": "https://github.com/google/fonts/raw/main/ofl/outfit/Outfit%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Outfit")


def main(page: ft.Page):
    configure_page(page)

    state = AppState()
    controller = ChordController(page, state)

    layout = build_layout(controller)

    page.add(layout)

    controller.load_initial_graph()


ft.app(target=main)