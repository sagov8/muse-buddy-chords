import flet as ft


def build_lyrics_panel(controller):
    lyrics_input = ft.TextField(
        label="Pega aquí la letra",
        multiline=True,
        min_lines=8,
        max_lines=12,
        expand=True,
    )

    lyrics_output = ft.TextField(
        label="Letra con acordes",
        multiline=True,
        min_lines=8,
        max_lines=12,
        read_only=True,
        expand=True,
    )

    controller.lyrics_input = lyrics_input
    controller.lyrics_output = lyrics_output

    return ft.Container(
        bgcolor="#141521",
        border_radius=16,
        padding=20,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Aplicar progresión a letra",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#EEF2F6",
                ),
                ft.Row(
                    controls=[
                        lyrics_input,
                        ft.IconButton(
                            icon=ft.Icons.LYRICS,
                            icon_color="#EEF2F6",
                            bgcolor="#3F51B5",
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