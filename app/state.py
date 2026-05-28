from core.graph_engine import ChordGraph

class AppState:
    def __init__(self):
        self.progression = []
        self.graph_data = {"nodes": [], "edges": []}
        self.mode = "major"
        self.graph_engine = ChordGraph()

        self.current_genre = None
        self.current_key = None