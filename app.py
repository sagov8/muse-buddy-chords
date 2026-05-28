import os
import flet as ft
import webbrowser
import random

from core.genre_loader import load_genre
from core.graph_transforms import add_chord, remove_chord
from core.graph_engine import ChordGraph
from core.progression_generator import generate
from audio.player import play_progression
from ui.components import progression_row
from util.style_connections import STYLE_CONNECTIONS


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
}


def _parse_roman(numeral: str):
    accidental = 0

    if numeral.startswith("b"):
        accidental = -1
        numeral = numeral[1:]
    elif numeral.startswith("#"):
        accidental = 1
        numeral = numeral[1:]

    is_dim = "°" in numeral
    s = numeral.replace("°", "")

    i = 0
    while i < len(s) and s[i] in "IiVv":
        i += 1

    roman = s[:i]
    suffix = s[i:]
    degree = _ROMAN_IDX[roman.lower()]
    is_upper = roman == roman.upper()

    if is_dim:
        suffix = "dim" + suffix

    return degree, is_upper, suffix, accidental


def resolve_roman(numeral: str, root: str, mode: str = "major") -> str:
    scale = MAJOR_SCALE if mode == "major" else MINOR_SCALE
    degree, is_upper, suffix, accidental = _parse_roman(numeral)

    root = ENHARMONICS.get(root, root)
    chord_root = NOTES[
        (NOTES.index(root) + scale[degree] + accidental) % 12
    ]

    if is_upper:
        return chord_root + suffix

    if suffix.startswith(("m", "dim")):
        return chord_root + suffix

    return chord_root + "m" + suffix


def chord_suggestions_for_key(key: str, mode: str = "major") -> list[tuple[str, str]]:
    diatonic = [
        "I",
        "ii",
        "iii",
        "IV",
        "V",
        "vi",
        "vii°",
    ]

    borrowed = [
        "bIII",
        "iv",
        "bVI",
        "bVII",
    ]

    secondary = [
        "II",
        "III",
        "VI",
    ]

    romans = diatonic + borrowed + secondary

    result = []
    seen = set()

    for roman in romans:
        chord = resolve_roman(roman, key, mode)
        if chord not in seen:
            result.append((roman, chord))
            seen.add(chord)

    return result


def main(page: ft.Page):
    page.title = "Chord Generator"

    result_container = ft.Column()

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

    def snack(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def update_chord_dropdowns():
        suggestions = chord_suggestions_for_key(key.value, "major")

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

    def refresh_graph(data: dict):
        _state["graph_data"] = data
        graph_engine.build(data)
        graph_engine.render()

        path = os.path.abspath("generated/graph.html")
        webbrowser.open(f"file://{path}")

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
        suggestions = chord_suggestions_for_key(key.value, "major")
        chord_to_roman = {chord_name: roman for roman, chord_name in suggestions}

        roman = chord_to_roman.get(chord)
        style_map = STYLE_CONNECTIONS.get(genre.value, {})

        if roman not in style_map:
            return [], []

        outgoing_romans = style_map[roman]

        outgoing = []
        for target_roman, weight in outgoing_romans:
            target_chord = resolve_roman(target_roman, key.value, "major")

            if target_chord in _state["graph_data"]["nodes"]:
                outgoing.append((target_chord, weight))

        incoming = []
        for source_roman, targets in style_map.items():
            for target_roman, weight in targets:
                if target_roman == roman:
                    source_chord = resolve_roman(source_roman, key.value, "major")

                    if source_chord in _state["graph_data"]["nodes"]:
                        incoming.append((source_chord, weight))

        return incoming, outgoing

    async def generar(e):
        data = load_genre(genre.value, key=key.value)
        refresh_graph(data)
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
        _state["progression"] = []
        _state["graph_data"] = {"nodes": [], "edges": []}
        result_container.controls.clear()
        edit_field.value = ""
        update_chord_dropdowns()
        page.update()

    genre.on_change = on_key_or_genre_change
    key.on_change = on_key_or_genre_change

    update_chord_dropdowns()

    page.add(
        ft.Text(
            "Generador de Progresiones",
            size=28,
            weight=ft.FontWeight.BOLD,
        ),

        ft.Row([genre, key]),

        ft.Text("Longitud"),
        length_slider,

        ft.ElevatedButton(
            "Generar",
            on_click=generar,
        ),

        ft.Divider(),

        ft.Text("Modificar grafo", size=16),

        ft.Row([
            add_chord_dropdown,
            ft.ElevatedButton(
                "+ Añadir",
                on_click=on_add_chord,
            ),
        ]),

        ft.Row([
            remove_chord_dropdown,
            ft.ElevatedButton(
                "− Eliminar",
                on_click=on_remove_chord,
            ),
        ]),

        ft.Divider(),

        edit_field,

        ft.Row([
            ft.ElevatedButton(
                "Guardar edición",
                on_click=guardar_edicion,
            ),
            ft.ElevatedButton(
                "▶ Escuchar",
                on_click=reproducir,
            ),
        ]),

        result_container,
    )


ft.app(target=main)