from __future__ import annotations
from typing import TypedDict

class GraphData(TypedDict):
    nodes: list[str]
    edges: list[tuple[str, str, float]]


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
    # 1. Identify predecessors and successors of chord
    preds = [(s, w) for s, d, w in data["edges"] if d == chord]
    succs = [(d, w) for s, d, w in data["edges"] if s == chord]
    
    # 2. Filter out the chord from nodes and edges
    remaining_nodes = [n for n in data["nodes"] if n != chord]
    remaining_edges = [(s, d, w) for s, d, w in data["edges"] if s != chord and d != chord]
    
    # 3. Create bypass edges
    # Map of existing edges to their weights for fast lookup/update
    edge_map = {(s, d): w for s, d, w in remaining_edges}
    
    for s, w_s in preds:
        if s == chord:
            continue
        for d, w_d in succs:
            if d == chord or s == d:
                continue
            bypass_w = round(w_s * w_d, 2)
            # If already exists, take max weight
            if (s, d) in edge_map:
                edge_map[(s, d)] = max(edge_map[(s, d)], bypass_w)
            else:
                edge_map[(s, d)] = bypass_w
                
    # 4. Check for any remaining orphan nodes in the resulting graph
    # A node is an orphan if it has no incoming edges or no outgoing edges.
    # We want to heal them by connecting them to/from the fallback node.
    in_degrees = {n: 0 for n in remaining_nodes}
    out_degrees = {n: 0 for n in remaining_nodes}
    for s, d in edge_map.keys():
        if s in out_degrees:
            out_degrees[s] += 1
        if d in in_degrees:
            in_degrees[d] += 1
            
    if remaining_nodes:
        # Fallback node: we try to find a tonic (e.g. C, Cmaj7, Am, etc.) or just the first node.
        fallback_node = remaining_nodes[0]
        
        for node in remaining_nodes:
            # If a node has no outgoing edges, connect it to the fallback_node
            if out_degrees[node] == 0 and len(remaining_nodes) > 1:
                target = fallback_node if node != fallback_node else remaining_nodes[1]
                edge_map[(node, target)] = 0.5
                out_degrees[node] += 1
                in_degrees[target] += 1
                
            # If a node has no incoming edges, connect it from the fallback_node
            if in_degrees[node] == 0 and len(remaining_nodes) > 1:
                source = fallback_node if node != fallback_node else remaining_nodes[1]
                edge_map[(source, node)] = 0.5
                in_degrees[node] += 1
                out_degrees[source] += 1
                
    # Convert edge_map back to edge list
    new_edges = [(s, d, w) for (s, d), w in edge_map.items()]
    
    return {
        "nodes": remaining_nodes,
        "edges": new_edges
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


def get_auto_connections(
    chord: str,
    existing_nodes: list[str],
    key: str,
    mode: str,
    genre: str
) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    from util.style_connections import STYLE_CONNECTIONS
    from core.chord_theory import chord_to_roman, get_canonical_base, resolve_roman, HARMONIC_RULES
    
    # 1. Determine Roman numeral and canonical base of the new chord
    new_roman = chord_to_roman(chord, key, mode)
    new_canon = get_canonical_base(new_roman)
    
    outgoing_map = {}
    incoming_map = {}
    
    # A. First, check style-specific connections (if they exist)
    style_map = STYLE_CONNECTIONS.get(genre, {})
    
    # Outgoing style transitions
    style_targets = []
    if new_roman in style_map:
        style_targets = style_map[new_roman]
    elif new_canon in style_map:
        style_targets = style_map[new_canon]
        
    for target_roman, weight in style_targets:
        try:
            target_chord = resolve_roman(target_roman, key, mode)
            if target_chord in existing_nodes:
                outgoing_map[target_chord] = weight
        except Exception:
            pass
            
    # Incoming style transitions
    for src_roman, targets in style_map.items():
        for dst_roman, weight in targets:
            dst_canon = get_canonical_base(dst_roman)
            if dst_roman == new_roman or dst_canon == new_canon:
                try:
                    src_chord = resolve_roman(src_roman, key, mode)
                    if src_chord in existing_nodes:
                        incoming_map[src_chord] = weight
                except Exception:
                    pass
                    
    # B. Enrich with general HARMONIC_RULES
    canon_rules = HARMONIC_RULES.get(new_canon, {})
    
    if canon_rules:
        # Outgoing general transitions:
        for target_canon, weight in canon_rules.get("outgoing", []):
            for node in existing_nodes:
                try:
                    node_roman = chord_to_roman(node, key, mode)
                    node_canon = get_canonical_base(node_roman)
                    if node_canon == target_canon:
                        if node not in outgoing_map:
                            outgoing_map[node] = weight
                except Exception:
                    pass
                        
        # Incoming general transitions:
        for source_canon, weight in canon_rules.get("incoming", []):
            for node in existing_nodes:
                try:
                    node_roman = chord_to_roman(node, key, mode)
                    node_canon = get_canonical_base(node_roman)
                    if node_canon == source_canon:
                        if node not in incoming_map:
                            incoming_map[node] = weight
                except Exception:
                    pass
                        
    # C. Special check: If the new chord still has 0 incoming or 0 outgoing edges (and there are other nodes),
    # guarantee at least one connection to avoid orphaned nodes.
    if existing_nodes:
        tonics = []
        for node in existing_nodes:
            try:
                node_roman = chord_to_roman(node, key, mode)
                node_canon = get_canonical_base(node_roman)
                if node_canon in ("I", "i"):
                    tonics.append(node)
            except Exception:
                pass
                
        default_fallback = tonics[0] if tonics else existing_nodes[0]
        
        if not incoming_map:
            incoming_map[default_fallback] = 0.5
            
        if not outgoing_map:
            outgoing_map[default_fallback] = 0.5
            
    return list(incoming_map.items()), list(outgoing_map.items())