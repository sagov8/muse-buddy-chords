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


MAJOR_INTERVALS = {
    0: (0, 0),   # I
    1: (1, -1),  # bII
    2: (1, 0),   # II
    3: (2, -1),  # bIII
    4: (2, 0),   # III
    5: (3, 0),   # IV
    6: (3, 1),   # #IV
    7: (4, 0),   # V
    8: (5, -1),  # bVI
    9: (5, 0),   # VI
    10: (6, -1), # bVII
    11: (6, 0)   # VII
}

MINOR_INTERVALS = {
    0: (0, 0),   # i
    1: (1, -1),  # bII
    2: (1, 0),   # ii
    3: (2, 0),   # bIII
    4: (2, 1),   # III
    5: (3, 0),   # iv
    6: (4, -1),  # bV
    7: (4, 0),   # v
    8: (5, 0),   # bVI
    9: (5, 1),   # VI
    10: (6, 0),  # bVII
    11: (6, 1)   # VII
}

HARMONIC_RULES = {
    # TONIC
    "I": {
        "outgoing": [("V", 0.9), ("vi", 0.7), ("IV", 0.7), ("ii", 0.6), ("iii", 0.4), ("bVII", 0.5)],
        "incoming": [("V", 0.9), ("IV", 0.8), ("ii", 0.5), ("vii", 0.7), ("bVII", 0.6)]
    },
    "i": {
        "outgoing": [("v", 0.7), ("V", 0.8), ("bVI", 0.7), ("iv", 0.6), ("bIII", 0.5), ("bVII", 0.6)],
        "incoming": [("v", 0.8), ("V", 0.9), ("iv", 0.7), ("bVII", 0.7), ("bVI", 0.6)]
    },
    # SUBDOMINANT / PREDOMINANT
    "ii": {
        "outgoing": [("V", 0.9), ("I", 0.5), ("vii", 0.4)],
        "incoming": [("I", 0.6), ("vi", 0.8), ("IV", 0.5)]
    },
    "II": {
        "outgoing": [("V", 0.9), ("I", 0.5)],
        "incoming": [("I", 0.6), ("vi", 0.6)]
    },
    # MEDIANT (TONIC/DOMINANT-FACING)
    "iii": {
        "outgoing": [("vi", 0.8), ("IV", 0.6)],
        "incoming": [("I", 0.5), ("IV", 0.4)]
    },
    "III": {
        "outgoing": [("vi", 0.9)],
        "incoming": [("I", 0.6)]
    },
    # SUBDOMINANT
    "IV": {
        "outgoing": [("V", 0.8), ("I", 0.7), ("ii", 0.6), ("vi", 0.5)],
        "incoming": [("I", 0.7), ("vi", 0.7), ("iii", 0.5)]
    },
    "iv": {
        "outgoing": [("I", 0.8), ("v", 0.7), ("V", 0.8)],
        "incoming": [("i", 0.7), ("bVI", 0.6)]
    },
    # DOMINANT
    "V": {
        "outgoing": [("I", 0.9), ("vi", 0.7), ("IV", 0.4)],
        "incoming": [("I", 0.6), ("ii", 0.9), ("IV", 0.8), ("VI", 0.7), ("bVI", 0.6)]
    },
    "v": {
        "outgoing": [("i", 0.8), ("bVI", 0.7)],
        "incoming": [("i", 0.6), ("iv", 0.7)]
    },
    # SUBMEDIANT / TONIC
    "vi": {
        "outgoing": [("ii", 0.8), ("IV", 0.8), ("V", 0.6), ("I", 0.5)],
        "incoming": [("I", 0.7), ("V", 0.7), ("iii", 0.8)]
    },
    "VI": {
        "outgoing": [("ii", 0.9)],
        "incoming": [("I", 0.6), ("iii", 0.6)]
    },
    # LEADING TONE / SUBTONIC
    "vii": {
        "outgoing": [("I", 0.8), ("iii", 0.4)],
        "incoming": [("I", 0.4), ("IV", 0.5), ("ii", 0.5)]
    },
    # BORROWED CHORDS
    "bIII": {
        "outgoing": [("IV", 0.7), ("bVII", 0.6), ("bVI", 0.6), ("I", 0.5)],
        "incoming": [("I", 0.5), ("bVI", 0.6)]
    },
    "bVI": {
        "outgoing": [("bVII", 0.8), ("V", 0.6), ("bIII", 0.5), ("I", 0.5)],
        "incoming": [("I", 0.6), ("bIII", 0.6)]
    },
    "bVII": {
        "outgoing": [("IV", 0.8), ("I", 0.9), ("bIII", 0.5)],
        "incoming": [("I", 0.5), ("bVI", 0.7), ("bIII", 0.6)]
    }
}


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
    is_half_dim = "ø" in numeral
    s = numeral.replace("°", "").replace("ø", "")

    i = 0
    while i < len(s) and s[i] in "IiVv":
        i += 1

    roman, suffix = s[:i], s[i:]
    is_upper = roman == roman.upper()
    degree = _ROMAN_IDX[roman.lower()]

    final_suffix = suffix
    if is_dim:
        final_suffix = "dim" + suffix
    elif is_half_dim:
        if suffix.startswith("7"):
            final_suffix = "m7b5" + suffix[1:]
        else:
            final_suffix = "m7b5" + suffix

    return degree, is_upper, final_suffix, accidental


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


def get_canonical_base(numeral: str) -> str:
    try:
        degree, is_upper, suffix, accidental = _parse_roman(numeral)
        acc = "b" if accidental < 0 else ("#" if accidental > 0 else "")
        deg_str = ["I", "II", "III", "IV", "V", "VI", "VII"][degree]
        if not is_upper:
            deg_str = deg_str.lower()
        return f"{acc}{deg_str}"
    except Exception:
        return numeral


def chord_to_roman(chord: str, key: str, mode: str = "major") -> str:
    root, quality = parse_chord(chord)
    semitones = semitones_from_key(root, key)
    
    intervals = MAJOR_INTERVALS if mode == "major" else MINOR_INTERVALS
    if semitones not in intervals:
        return chord
        
    degree, accidental = intervals[semitones]
    
    is_minor = False
    if quality.startswith("m") and not quality.startswith("maj"):
        is_minor = True
    elif quality.startswith(("dim", "°", "ø", "m7b5")):
        is_minor = True
        
    roman_base = ["I", "II", "III", "IV", "V", "VI", "VII"][degree]
    if is_minor:
        roman_base = roman_base.lower()
        
    acc = "b" if accidental < 0 else ("#" if accidental > 0 else "")
    
    suffix = quality
    if is_minor:
        if suffix.startswith("m"):
            suffix = suffix[1:]
            
    return f"{acc}{roman_base}{suffix}"


def chord_suggestions_for_key(key: str, genre: str, mode: str = "major") -> list[tuple[str, str]]:
    if genre == "jazz":
        diatonic = [
            "Imaj7",
            "ii7",
            "iii7",
            "IVmaj7",
            "V7",
            "vi7",
            "viiø7",
        ]
        borrowed = [
            "bIIImaj7",
            "iv7",
            "bVImaj7",
            "bVII7",
        ]
        secondary = [
            "II7",
            "III7",
            "VI7",
        ]
    else:
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