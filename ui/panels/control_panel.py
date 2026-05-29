import flet as ft
from ui.styles import theme_colors

from app.constants import KEYS, GENRES


def build_control_panel(controller):
    current_genre = "pop"
    current_key = "C"
    current_length = 4
    current_edit = ""
    
    if getattr(controller, 'genre_dropdown', None) and controller.genre_dropdown.value:
        current_genre = controller.genre_dropdown.value
    elif controller.state and controller.state.current_genre:
        current_genre = controller.state.current_genre
        
    if getattr(controller, 'key_dropdown', None) and controller.key_dropdown.value:
        current_key = controller.key_dropdown.value
    elif controller.state and controller.state.current_key:
        current_key = controller.state.current_key
        
    if getattr(controller, 'length_slider', None) and controller.length_slider.value is not None:
        current_length = controller.length_slider.value
        
    if getattr(controller, 'edit_field', None) and controller.edit_field.value is not None:
        current_edit = controller.edit_field.value
    elif controller.state and controller.state.progression:
        current_edit = ", ".join(controller.state.progression)

    genre = ft.Dropdown(
        label="Género",
        width=180,
        value=current_genre,
        options=[ft.dropdown.Option(g) for g in GENRES],
    )

    key = ft.Dropdown(
        label="Tonalidad",
        width=130,
        value=current_key,
        options=[ft.dropdown.Option(k) for k in KEYS],
    )

    length_label = ft.Text(
        f"Longitud de la progresión: {int(current_length)} acordes",
        size=13,
        color=theme_colors.text_sub,
    )

    def on_slider_change(e):
        length_label.value = f"Longitud de la progresión: {int(e.control.value)} acordes"
        length_label.update()

    length_slider = ft.Slider(
        min=4,
        max=16,
        divisions=12,
        value=current_length,
        label="{value}",
        on_change=on_slider_change,
    )

    edit_field = ft.TextField(
        label="Editar progresión",
        expand=True,
        value=current_edit,
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

    play_button = ft.ElevatedButton(
        "Escuchar",
        on_click=controller.play,
        icon=ft.icons.Icons.PLAY_ARROW,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="#10B981",
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    genre.on_change = controller.change_base_graph
    key.on_change = controller.change_base_graph

    controller.bind_controls(
        genre_dropdown=genre,
        key_dropdown=key,
        length_slider=length_slider,
        edit_field=edit_field,
        result_container=result_container,
        add_chord_dropdown=add_chord_dropdown,
        remove_chord_dropdown=remove_chord_dropdown,
        visualizer=controller.visualizer,
        play_button=play_button,
    )

    return ft.Container(
        width=400,
        bgcolor=theme_colors.panel_bg,
        border_radius=16,
        padding=20,
        border=theme_colors.panel_border,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            controls=[
                ft.Row(
                    [
                        ft.Text(
                            "Generador",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=theme_colors.text_title,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.icons.Icons.SUNNY if theme_colors.is_dark else ft.icons.Icons.DARK_MODE,
                            icon_color=theme_colors.text_title,
                            on_click=controller.toggle_theme,
                            tooltip="Cambiar tema (claro/oscuro)",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),

                ft.Text(
                    "Configuración",
                    size=14,
                    color=theme_colors.text_sub,
                    weight=ft.FontWeight.W_500,
                ),

                ft.Row([genre, key], spacing=10),

                length_label,

                length_slider,

                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Generar",
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
                            "Reiniciar",
                            icon=ft.icons.Icons.RESTORE,
                            icon_color=theme_colors.text_sub,
                            on_click=controller.load_genre_graph,
                            style=ft.ButtonStyle(color=theme_colors.text_sub),
                        ),
                    ],
                    spacing=10,
                ),

                ft.Divider(color=theme_colors.divider),

                ft.Text(
                    "Modificar Acordes",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=theme_colors.text_title,
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

                ft.Divider(color=theme_colors.divider),

                ft.Text(
                    "Progreso y Edición",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=theme_colors.text_title,
                ),

                edit_field,

                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Guardar",
                            on_click=controller.save_edit,
                            icon=ft.icons.Icons.SAVE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                        ),

                        play_button,
                    ],
                    spacing=10,
                ),

                ft.Text(
                    "Progresión Generada:",
                    size=13,
                    color=theme_colors.text_sub,
                ),

                result_container,
            ],
        ),
    )