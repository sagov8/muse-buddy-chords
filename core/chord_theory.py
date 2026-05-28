from __future__ import annotations
from typing import TypedDict
from copy import deepcopy

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ENHARMONICS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

_ROMAN_IDX = {"i": 0, "ii": 1, "iii": 2, "iv": 3, "v": 4, "vi": 5, "vii": 6}

# Tipado explícito para el grafo de datos
class GraphData(TypedDict):
    nodes: list[str]
    edges: list[tuple[str, str, float]]


def parse_chord(chord: str) -> tuple[str, str]:
    """'Dm7' → ('D', 'm7'),  'C#maj7' → ('C#', 'maj7')"""
    if len(chord) >= 2 and chord[1] in ("#", "b"):
        root, quality = chord[:2], chord[2:]
    else:
        root, quality = chord[0], chord[1:]
    return ENHARMONICS.get(root, root), quality


def transpose_chord(chord: str, semitones: int) -> str:
    root, quality = parse_chord(chord)
    new_root = NOTES[(NOTES.index(root) + semitones) % 12]
    return new_root + quality


def semitones_from_key(target_key: str, base_key: str = "C") -> int:
    """Calcula cuántos semitonos hay entre base_key y target_key."""
    base = ENHARMONICS.get(base_key, base_key)
    target = ENHARMONICS.get(target_key, target_key)
    return (NOTES.index(target) - NOTES.index(base)) % 12

def _parse_roman(numeral: str) -> tuple[int, bool, str, int]:
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

    roman, suffix = s[:i], s[i:]
    is_upper = roman == roman.upper()
    degree = _ROMAN_IDX[roman.lower()]

    return degree, is_upper, ("dim" + suffix if is_dim else suffix), accidental


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