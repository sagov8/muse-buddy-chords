from core.graph_engine import ChordGraph


class AppState:
    def __init__(self):
        self.progression = []
        self.graph_data = {"nodes": [], "edges": []}
        self.mode = "major"
        self.graph_engine = ChordGraph()