def apply_chords_to_lyrics(lyrics: str, progression: list[str]) -> str:
    if not lyrics.strip():
        return ""

    if not progression:
        return lyrics

    lines = lyrics.splitlines()
    result = []
    chord_index = 0

    for line in lines:
        if not line.strip():
            result.append("")
            continue

        chord = progression[chord_index % len(progression)]
        result.append(f"[{chord}] {line}")

        chord_index += 1

    return "\n".join(result)