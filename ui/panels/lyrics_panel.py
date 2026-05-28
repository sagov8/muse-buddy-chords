import flet as ft
from ui.styles import theme_colors


def build_lyrics_panel(controller):
    current_input = ""
    current_output = ""
    if getattr(controller, 'lyrics_input', None) and controller.lyrics_input.value:
        current_input = controller.lyrics_input.value
    elif controller.state and hasattr(controller.state, 'lyrics') and controller.state.lyrics:
        current_input = controller.state.lyrics
        
    if getattr(controller, 'lyrics_output', None) and controller.lyrics_output.value:
        current_output = controller.lyrics_output.value
    elif controller.state and hasattr(controller.state, 'lyrics_with_chords') and controller.state.lyrics_with_chords:
        current_output = controller.state.lyrics_with_chords

    lyrics_input = ft.TextField(
        label="Pega aquí la letra",
        multiline=True,
        min_lines=8,
        max_lines=12,
        expand=True,
        value=current_input,
    )

    lyrics_output = ft.TextField(
        label="Letra con acordes",
        multiline=True,
        min_lines=8,
        max_lines=12,
        read_only=True,
        expand=True,
        value=current_output,
    )

    controller.lyrics_input = lyrics_input
    controller.lyrics_output = lyrics_output

    return ft.Container(
        bgcolor=theme_colors.panel_bg,
        border_radius=16,
        padding=20,
        border=theme_colors.panel_border,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Aplicar progresión a letra",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=theme_colors.text_title,
                ),
                ft.Row(
                    controls=[
                        lyrics_input,
                        ft.IconButton(
                            icon=ft.Icons.LYRICS,
                            icon_color=theme_colors.panel_bg,
                            bgcolor=theme_colors.edge_bidirectional,
                            on_click=controller.apply_progression_to_lyrics,
                            tooltip="Aplicar acordes a letra",
                            width=50,
                            height=50,
                        ),
                        lyrics_output,
                    ],
                    expand=True,
                    spacing=12,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
        ),
    )