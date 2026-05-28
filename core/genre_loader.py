import json
import os
from typing import Callable
from functools import reduce
from core.chord_theory import resolve_roman

GraphData = dict  # {"nodes": [...], "edges": [...]}
Transform = Callable[[GraphData], GraphData]


def load_genre(name: str, key: str = "C") -> GraphData:
    path = os.path.join("data", f"{name}.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    mode = raw.get("mode", "major")
    resolve = lambda symbol: resolve_roman(symbol, key, mode)

    return {
        "nodes": [resolve(n) for n in raw["nodes"]],
        "edges": [
            (resolve(src), resolve(dst), w)
            for src, dst, w in raw["edges"]
        ],
    }


def pipe(*transforms: Transform) -> Transform:
    return lambda data: reduce(lambda acc, fn: fn(acc), transforms, data)