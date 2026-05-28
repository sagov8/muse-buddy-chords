import random
import flet as ft

from core.genre_loader import load_genre
from core.graph_transforms import add_chord, remove_chord, get_auto_connections
from core.progression_generator import generate
from core.chord_theory import chord_suggestions_for_key
from audio.player import play_progression
from ui.components import progression_row
from services.genre_service import get_genre_mode
from services.lyric_chord_mapper import apply_chords_to_lyrics

class ChordController:
    def __init__(self, page: ft.Page, state):
        self.page = page
        self.state = state

        self.genre_dropdown = None
        self.key_dropdown = None
        self.length_slider = None
        self.edit_field = None
        self.result_container = None
        self.add_chord_dropdown = None
        self.remove_chord_dropdown = None
        self.visualizer = None
        self.lyrics_input = None
        self.lyrics_output = None

    def bind_controls(
        self,
        genre_dropdown,
        key_dropdown,
        length_slider,
        edit_field,
        result_container,
        add_chord_dropdown,
        remove_chord_dropdown,
        visualizer,
    ):
        self.genre_dropdown = genre_dropdown
        self.key_dropdown = key_dropdown
        self.length_slider = length_slider
        self.edit_field = edit_field
        self.result_container = result_container
        self.add_chord_dropdown = add_chord_dropdown
        self.remove_chord_dropdown = remove_chord_dropdown
        self.visualizer = visualizer

    def snack(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    def load_initial_graph(self):
        self.load_genre_graph(None)

    def load_genre_graph(self, e=None):
        genre = self.genre_dropdown.value
        key = self.key_dropdown.value

        self.state.mode = get_genre_mode(genre)

        data = load_genre(genre, key=key)
        self.refresh_graph(data, reset_layout=True)

        self.state.current_genre = genre
        self.state.current_key = key

        self.regenerate_progression()

    def refresh_graph(self, data: dict, reset_layout: bool = False):
        self.state.graph_data = data
        self.state.graph_engine.build(data)

        self.visualizer.set_graph_data(data, reset_layout=reset_layout)
        self.update_chord_dropdowns()

    def refresh_ui(self):
        self.edit_field.value = ", ".join(self.state.progression)

        self.result_container.controls = [
            progression_row(self.state.progression, on_reorder=self.reorder_progression)
        ]

        self.page.update()

    def reorder_progression(self, src_idx: int, dest_idx: int):
        if src_idx == dest_idx:
            return

        # Perform the reordering in state
        chord = self.state.progression.pop(src_idx)
        self.state.progression.insert(dest_idx, chord)

        # Refresh the UI to reflect new order
        self.refresh_ui()

        # Automatically update lyrics mapping if lyrics are loaded
        if getattr(self, 'lyrics_input', None) and self.lyrics_input.value and self.lyrics_input.value.strip():
            self.apply_progression_to_lyrics()

    def regenerate_progression(self, e=None):
        self.ensure_current_graph()

        nodes = self.state.graph_data["nodes"]

        if not nodes:
            return

        start = random.choice(nodes)

        self.state.progression = generate(
            self.state.graph_engine.graph,
            start=start,
            length=int(self.length_slider.value),
        )

        self.refresh_ui()

    def play(self, e):
        if not self.state.progression:
            self.snack("Primero genera una progresión.")
            return

        play_progression(self.state.progression)

    def save_edit(self, e):
        self.state.progression = [
            chord.strip()
            for chord in self.edit_field.value.split(",")
            if chord.strip()
        ]

        self.refresh_ui()

    def update_chord_dropdowns(self):
        suggestions = chord_suggestions_for_key(
            self.key_dropdown.value,
            self.genre_dropdown.value,
            self.state.mode,
        )

        current_nodes = set(self.state.graph_data["nodes"])

        self.add_chord_dropdown.options = [
            ft.dropdown.Option(
                key=chord,
                text=f"{roman}  →  {chord}",
            )
            for roman, chord in suggestions
            if chord not in current_nodes
        ]

        self.remove_chord_dropdown.options = [
            ft.dropdown.Option(chord)
            for chord in self.state.graph_data["nodes"]
        ]

        self.add_chord_dropdown.value = None
        self.remove_chord_dropdown.value = None

    def auto_connections_for_new_chord(self, chord: str):
        return get_auto_connections(
            chord,
            self.state.graph_data["nodes"],
            self.key_dropdown.value,
            self.state.mode,
            self.genre_dropdown.value,
        )

    def add_chord(self, e):
        chord = self.add_chord_dropdown.value

        if not chord:
            self.snack("Selecciona un acorde para agregar.")
            return

        if not self.state.graph_data["nodes"]:
            self.snack("Genera una progresión primero.")
            return

        incoming, outgoing = self.auto_connections_for_new_chord(chord)

        new_data = add_chord(
            self.state.graph_data,
            chord,
            incoming=incoming,
            outgoing=outgoing,
        )

        self.refresh_graph(new_data)
        self.regenerate_progression()
        self.snack(f"'{chord}' añadido al grafo.")

    def remove_chord(self, e):
        chord = self.remove_chord_dropdown.value

        if not chord:
            self.snack("Selecciona un acorde para eliminar.")
            return

        if chord not in self.state.graph_data["nodes"]:
            self.snack(f"'{chord}' no está en el grafo.")
            return

        new_data = remove_chord(
            self.state.graph_data,
            chord,
        )

        self.refresh_graph(new_data)
        self.regenerate_progression()
        self.snack(f"'{chord}' eliminado del grafo.")

    def change_base_graph(self, e=None):
        genre = self.genre_dropdown.value
        key = self.key_dropdown.value

        self.state.mode = get_genre_mode(genre)

        data = load_genre(genre, key=key)
        self.refresh_graph(data, reset_layout=True)
        self.regenerate_progression()

    def ensure_current_graph(self):
        genre = self.genre_dropdown.value
        key = self.key_dropdown.value

        graph_changed = (
                genre != self.state.current_genre
                or key != self.state.current_key
        )

        if graph_changed:
            self.state.mode = get_genre_mode(genre)

            data = load_genre(genre, key=key)
            self.refresh_graph(data, reset_layout=True)

            self.state.current_genre = genre
            self.state.current_key = key

    def apply_progression_to_lyrics(self, e=None):
        lyrics = self.lyrics_input.value or ""

        if not lyrics.strip():
            self.snack("Pega una letra primero.")
            return

        if not self.state.progression:
            self.snack("Genera una progresión primero.")
            return

        result = apply_chords_to_lyrics(
            lyrics=lyrics,
            progression=self.state.progression,
        )

        self.state.lyrics = lyrics
        self.state.lyrics_with_chords = result

        self.lyrics_output.value = result
        self.page.update()

    def toggle_theme(self, e=None):
        from ui.styles import theme_colors
        from ui.layout import build_layout

        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        new_is_dark = not is_dark
        self.page.theme_mode = ft.ThemeMode.DARK if new_is_dark else ft.ThemeMode.LIGHT
        theme_colors.update_theme(new_is_dark)
        self.page.bgcolor = theme_colors.page_bg

        # Recreate the layout and update the page
        new_layout = build_layout(self)
        self.page.controls[0] = new_layout

        # Refresh graph to apply new colors
        if self.state.graph_data:
            self.refresh_graph(self.state.graph_data, reset_layout=False)

        # Refresh generated progression display
        if self.state.progression:
            self.refresh_ui()

        self.page.update()