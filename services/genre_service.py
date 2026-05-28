from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def get_genre_mode(genre: str) -> str:
    try:
        path = DATA_DIR / f"{genre}.json"

        with path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        return raw.get("mode", "major")

    except FileNotFoundError:
        return "major"