GraphData = dict


def add_chord(
    data: GraphData,
    chord: str,
    incoming: list[tuple[str, float]] | None = None,
    outgoing: list[tuple[str, float]] | None = None,
) -> GraphData:
    nodes = data["nodes"] + [chord] if chord not in data["nodes"] else list(data["nodes"])
    new_edges = (
        [(src, chord, w) for src, w in (incoming or [])] +
        [(chord, dst, w) for dst, w in (outgoing or [])]
    )
    return {"nodes": nodes, "edges": list(data["edges"]) + new_edges}


def remove_chord(data: GraphData, chord: str) -> GraphData:
    return {
        "nodes": [n for n in data["nodes"] if n != chord],
        "edges": [(s, d, w) for s, d, w in data["edges"] if s != chord and d != chord],
    }


def set_edge_weight(
    data: GraphData, src: str, dst: str, weight: float
) -> GraphData:
    """Ajusta el peso de una transición específica."""
    return {
        "nodes": data["nodes"],
        "edges": [
            (s, d, weight if s == src and d == dst else w)
            for s, d, w in data["edges"]
        ],
    }