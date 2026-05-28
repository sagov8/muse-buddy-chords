import os
import json
import flet as ft
import webbrowser
import random

from core.genre_loader import load_genre
from core.graph_transforms import add_chord, remove_chord, get_auto_connections
from core.graph_engine import ChordGraph
from core.progression_generator import generate
from audio.player import play_progression
from ui.components import progression_row
from ui.graph_visualizer import GraphVisualizer
from util.style_connections import STYLE_CONNECTIONS
from core.chord_theory import chord_suggestions_for_key


KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTES = KEYS
ENHARMONICS = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

_ROMAN_IDX = {
    "i": 0,
    "ii": 1,
    "iii": 2,
    "iv": 3,
    "v": 4,
    "vi": 5,
    "vii": 6,
}

graph_engine = ChordGraph()

_state = {
    "progression": [],
    "graph_data": {"nodes": [], "edges": []},
    "mode": "major",
}


def main(page: ft.Page):
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

    visualizer = GraphVisualizer(width=720, height=540)
    result_container = ft.Column()

    # --- DEFINICIÓN DE FUNCIONES AUXILIARES Y MANEJADORES DE EVENTOS ---

    def snack(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def update_chord_dropdowns():
        suggestions = chord_suggestions_for_key(
            key.value,
            genre.value,
            _state.get("mode", "major")
        )

        current_nodes = set(_state["graph_data"]["nodes"])

        add_chord_dropdown.options = [
            ft.dropdown.Option(
                key=chord,
                text=f"{roman}  →  {chord}",
            )
            for roman, chord in suggestions
            if chord not in current_nodes
        ]

        remove_chord_dropdown.options = [
            ft.dropdown.Option(chord)
            for chord in _state["graph_data"]["nodes"]
        ]

        add_chord_dropdown.value = None
        remove_chord_dropdown.value = None

    def refresh_graph(data: dict, reset_layout: bool = False):
        _state["graph_data"] = data
        graph_engine.build(data)
        
        # Renderizar en el visualizador integrado
        visualizer.set_graph_data(data, reset_layout=reset_layout)

        update_chord_dropdowns()

    def refresh_ui():
        edit_field.value = ", ".join(_state["progression"])
        result_container.controls = [
            progression_row(_state["progression"])
        ]
        page.update()

    def regenerate_progression():
        if not _state["graph_data"]["nodes"]:
            return

        start = random.choice(_state["graph_data"]["nodes"])

        _state["progression"] = generate(
            graph_engine.graph,
            start=start,
            length=int(length_slider.value),
        )

        refresh_ui()

    def auto_connections_for_new_chord(chord: str):
        return get_auto_connections(
            chord,
            _state["graph_data"]["nodes"],
            key.value,
            _state.get("mode", "major"),
            genre.value
        )

    def generar(e):
        try:
            path = os.path.join("data", f"{genre.value}.json")
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            mode_val = raw.get("mode", "major")
        except Exception:
            mode_val = "major"
            
        _state["mode"] = mode_val
        data = load_genre(genre.value, key=key.value)
        refresh_graph(data, reset_layout=True)
        regenerate_progression()

    def reproducir(e):
        if not _state["progression"]:
            snack("Primero genera una progresión.")
            return

        play_progression(_state["progression"])

    def guardar_edicion(e):
        _state["progression"] = [
            x.strip()
            for x in edit_field.value.split(",")
            if x.strip()
        ]

        result_container.controls = [
            progression_row(_state["progression"])
        ]

        page.update()

    def on_add_chord(e):
        chord = add_chord_dropdown.value

        if not chord:
            snack("Selecciona un acorde para agregar.")
            return

        if not _state["graph_data"]["nodes"]:
            snack("Genera una progresión primero.")
            return

        incoming, outgoing = auto_connections_for_new_chord(chord)

        new_data = add_chord(
            _state["graph_data"],
            chord,
            incoming=incoming,
            outgoing=outgoing,
        )

        refresh_graph(new_data)
        regenerate_progression()
        snack(f"'{chord}' añadido al grafo.")

    def on_remove_chord(e):
        chord = remove_chord_dropdown.value

        if not chord:
            snack("Selecciona un acorde para eliminar.")
            return

        if chord not in _state["graph_data"]["nodes"]:
            snack(f"'{chord}' no está en el grafo.")
            return

        new_data = remove_chord(
            _state["graph_data"],
            chord,
        )

        refresh_graph(new_data)
        regenerate_progression()
        snack(f"'{chord}' eliminado del grafo.")

    def on_key_or_genre_change(e):
        generar(None)

    # --- DEFINICIÓN DE CONTROLES DE LA INTERFAZ ---

    genre = ft.Dropdown(
        label="Género",
        width=180,
        value="pop",
        options=[
            ft.dropdown.Option("pop"),
            ft.dropdown.Option("rock"),
            ft.dropdown.Option("jazz"),
        ],
    )

    key = ft.Dropdown(
        label="Tonalidad",
        width=130,
        value="C",
        options=[ft.dropdown.Option(k) for k in KEYS],
    )

    genre.on_change = on_key_or_genre_change
    key.on_change = on_key_or_genre_change

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

    add_chord_dropdown = ft.Dropdown(
        label="Acorde sugerido",
        width=220,
    )

    remove_chord_dropdown = ft.Dropdown(
        label="Acorde a eliminar",
        width=220,
    )

    # Inicializar opciones del dropdown
    update_chord_dropdowns()

    # Panel de controles (Columna Izquierda)
    control_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Generador de Progresiones",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color="#EEF2F6"
                ),
                ft.Text("Configuración", size=14, color="#94A3B8", weight=ft.FontWeight.W_500),
                ft.Row([genre, key], spacing=10),
                ft.Text("Longitud de la progresión", size=13, color="#94A3B8"),
                length_slider,
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Generar Progresión",
                                on_click=lambda e: regenerate_progression(),
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
                                on_click=generar,
                                style=ft.ButtonStyle(
                                    color="#94A3B8",
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10,
                    ),
                    margin=ft.margin.Margin(top=5, bottom=10)
                ),
                ft.Divider(color="#25283D"),
                
                ft.Text("Modificar Grafo Nativamente", size=15, weight=ft.FontWeight.BOLD, color="#EEF2F6"),
                ft.Row([
                    add_chord_dropdown,
                    ft.IconButton(
                        icon=ft.icons.Icons.ADD,
                        icon_color="#34D399",
                        icon_size=32,
                        tooltip="Añadir acorde al grafo",
                        on_click=on_add_chord,
                    ),
                ], spacing=10),
                ft.Row([
                    remove_chord_dropdown,
                    ft.IconButton(
                        icon=ft.icons.Icons.REMOVE,
                        icon_color="#F87171",
                        icon_size=32,
                        tooltip="Eliminar acorde del grafo",
                        on_click=on_remove_chord,
                    ),
                ], spacing=10),
                ft.Divider(color="#25283D"),
                
                ft.Text("Progreso y Edición", size=15, weight=ft.FontWeight.BOLD, color="#EEF2F6"),
                edit_field,
                ft.Row([
                    ft.ElevatedButton(
                        "Guardar edición",
                        on_click=guardar_edicion,
                        icon=ft.icons.Icons.SAVE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                    ft.ElevatedButton(
                        "Escuchar",
                        on_click=reproducir,
                        icon=ft.icons.Icons.PLAY_ARROW,
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="#10B981",
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    ),
                ], spacing=10),
                ft.Text("Progresión Generada:", size=13, color="#94A3B8"),
                result_container,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        ),
        width=400,
        bgcolor="#141521",
        border_radius=16,
        border=ft.Border(
            top=ft.BorderSide(1, "#25283D"),
            right=ft.BorderSide(1, "#25283D"),
            bottom=ft.BorderSide(1, "#25283D"),
            left=ft.BorderSide(1, "#25283D")
        ),
        padding=20,
    )

    # Panel del visualizador (Columna Derecha)
    visualizer_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Icon(ft.icons.Icons.MUSIC_NOTE, color="#6366F1", size=24),
                    ft.Text("Visualizador del Grafo de Acordes", size=22, weight=ft.FontWeight.BOLD, color="#EEF2F6"),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Text(
                    "Haz clic y arrastra los acordes para reposicionarlos. Los cambios y conexiones se recalculan dinámicamente.",
                    size=13,
                    color="#94A3B8"
                ),
                ft.Container(
                    content=visualizer,
                    alignment=ft.alignment.Alignment.CENTER,
                    expand=True,
                )
            ],
            spacing=10,
            expand=True,
        ),
        expand=True,
        bgcolor="#141521",
        border_radius=16,
        border=ft.Border(
            top=ft.BorderSide(1, "#25283D"),
            right=ft.BorderSide(1, "#25283D"),
            bottom=ft.BorderSide(1, "#25283D"),
            left=ft.BorderSide(1, "#25283D")
        ),
        padding=20,
    )

    page.add(
        ft.Row([
            control_panel,
            visualizer_panel
        ], expand=True)
    )

    # Cargar grafo y progresión por defecto al inicio
    generar(None)


ft.app(target=main)