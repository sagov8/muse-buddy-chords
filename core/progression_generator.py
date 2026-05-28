import random


def generate(graph, start=None, length=4):
    if len(graph.nodes) == 0:
        return []

    if start is None or start not in graph.nodes:
        start = random.choice(list(graph.nodes))

    progression = [start]

    for _ in range(length - 1):
        current = progression[-1]

        neighbors = list(graph.successors(current))

        # Si no hay sucesores:
        if not neighbors:

            # Reiniciar desde otro nodo aleatorio
            current = random.choice(list(graph.nodes))
            progression.append(current)
            continue

        weights = [
            graph[current][n]["weight"]
            for n in neighbors
        ]

        nxt = random.choices(
            neighbors,
            weights=weights,
        )[0]

        progression.append(nxt)

    return progression