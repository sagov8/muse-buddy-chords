import flet as ft
from ui.styles import PANEL_BORDER

from app.constants import KEYS, GENRES


def build_control_panel(controller):
    genre = ft.Dropdown(
        label="Género",
        width=180,
        value="pop",
        options=[ft.dropdown.Option(g) for g in GENRES],
    )

    key = ft.Dropdown(
        label="Tonalidad",
        width=130,
        value="C",
        options=[ft.dropdown.Option(k) for k in KEYS],
    )

    length_slider = ft.Slider(
        min=4,
        max=16,
        divisions=12,
        value=4,
    )

    edit_field = ft.TextField(
        label="Editar progresión",
        expand=True,
    )

    result_container = ft.Column()

    add_chord_dropdown = ft.Dropdown(
        label="Acorde sugerido",
        width=220,
    )

    remove_chord_dropdown = ft.Dropdown(
        label="Acorde a eliminar",
        width=220,
    )

    genre.on_change = controller.load_genre_graph
    key.on_change = controller.load_genre_graph

    controller.bind_controls(
        genre_dropdown=genre,
        key_dropdown=key,
        length_slider=length_slider,
        edit_field=edit_field,
        result_container=result_container,
        add_chord_dropdown=add_chord_dropdown,
        remove_chord_dropdown=remove_chord_dropdown,
        visualizer=controller.visualizer,
    )

    return ft.Container(
        width=400,
        bgcolor="#141521",
        border_radius=16,
        padding=20,
        border=PANEL_BORDER,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            controls=[
                ft.Text(
                    "Generador de Progresiones",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color="#EEF2F6",
                ),

                ft.Text(
                    "Configuración",
                    size=14,
                    color="#94A3B8",
                    weight=ft.FontWeight.W_500,
                ),

                ft.Row([genre, key], spacing=10),

                ft.Text(
                    "Longitud de la progresión",
                    size=13,
                    color="#94A3B8",
                ),

                length_slider,

                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Generar Progresión",
                            on_click=controller.regenerate_progression,
                            icon=ft.icons.Icons.AUTO_AWESOME,
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#4F46E5",
                                padding=15,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),

                        ft.TextButton(
                            "Restablecer Grafo",
                            icon=ft.icons.Icons.RESTORE,
                            icon_color="#94A3B8",
                            on_click=controller.load_genre_graph,
                            style=ft.ButtonStyle(color="#94A3B8"),
                        ),
                    ],
                    spacing=10,
                ),

                ft.Divider(color="#25283D"),

                ft.Text(
                    "Modificar Grafo Nativamente",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color="#EEF2F6",
                ),

                ft.Row(
                    [
                        add_chord_dropdown,
                        ft.IconButton(
                            icon=ft.icons.Icons.ADD,
                            icon_color="#34D399",
                            icon_size=32,
                            tooltip="Añadir acorde al grafo",
                            on_click=controller.add_chord,
                        ),
                    ],
                    spacing=10,
                ),

                ft.Row(
                    [
                        remove_chord_dropdown,
                        ft.IconButton(
                            icon=ft.icons.Icons.REMOVE,
                            icon_color="#F87171",
                            icon_size=32,
                            tooltip="Eliminar acorde del grafo",
                            on_click=controller.remove_chord,
                        ),
                    ],
                    spacing=10,
                ),

                ft.Divider(color="#25283D"),

                ft.Text(
                    "Progreso y Edición",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color="#EEF2F6",
                ),

                edit_field,

                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Guardar edición",
                            on_click=controller.save_edit,
                            icon=ft.icons.Icons.SAVE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                        ),

                        ft.ElevatedButton(
                            "Escuchar",
                            on_click=controller.play,
                            icon=ft.icons.Icons.PLAY_ARROW,
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#10B981",
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ],
                    spacing=10,
                ),

                ft.Text(
                    "Progresión Generada:",
                    size=13,
                    color="#94A3B8",
                ),

                result_container,
            ],
        ),
    )