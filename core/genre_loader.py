import json
from pathlib import Path
from typing import Callable
from functools import reduce

from core.chord_theory import resolve_roman


GraphData = dict
Transform = Callable[[GraphData], GraphData]

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_genre(name: str, key: str = "C") -> GraphData:
    path = DATA_DIR / f"{name}.json"

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    mode = raw.get("mode", "major")

    def resolve(symbol: str) -> str:
        return resolve_roman(symbol, key, mode)

    return {
        "nodes": [resolve(n) for n in raw["nodes"]],
        "edges": [
            (resolve(src), resolve(dst), w)
            for src, dst, w in raw["edges"]
        ],
    }


def pipe(*transforms: Transform) -> Transform:
    return lambda data: reduce(lambda acc, fn: fn(acc), transforms, data)