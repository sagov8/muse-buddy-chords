# audio/player.py

import io
import os
import math
import struct
import wave
import platform
from music21 import harmony


SAMPLE_RATE = 44100
HARMONICS = ((1, 1.0), (2, 0.5), (3, 0.75), (4, 0.4))
HARMONIC_GAIN = 1.85
ATTACK_FRAMES = 800
FADE_OUT_FRAMES = 400


def _chord_frequencies(symbol):
    # Convert flat symbols in roots (e.g. Bb -> B-, Bb/Db -> B-/D-) for music21 compatibility
    def translate_flat(s):
        if len(s) >= 2 and s[1] == "b":
            return s[0] + "-" + s[2:]
        return s

    if "/" in symbol:
        parts = symbol.split("/")
        symbol = "/".join(translate_flat(part) for part in parts)
    else:
        symbol = translate_flat(symbol)

    cs = harmony.ChordSymbol(symbol)
    freqs = []

    for pitch in cs.pitches:
        octave = pitch.octave if pitch.octave is not None else 4

        # Llevar acordes demasiado graves a una zona audible.
        while octave < 3:
            octave += 1

        pitch.octave = octave
        freqs.append(pitch.frequency)

    return freqs


def _additive_tone(freq, t):
    tone = 0.0
    for multiplier, amplitude in HARMONICS:
        tone += amplitude * math.sin(2 * math.pi * (multiplier * freq) * t)
    return tone / HARMONIC_GAIN


def _envelope(frame_index, total_frames):
    attack = min(ATTACK_FRAMES, total_frames)

    if frame_index < attack and attack > 0:
        envelope = frame_index / attack
    else:
        decay_frames = max(total_frames - attack, 1)
        progress = (frame_index - attack) / decay_frames
        envelope = math.exp(-3.5 * progress)

    fade_out = min(FADE_OUT_FRAMES, total_frames)
    frames_left = total_frames - frame_index
    if frames_left < fade_out and fade_out > 0:
        envelope *= frames_left / fade_out

    return envelope


def progression_to_wav_bytes(
    progression,
    bpm=90,
    beats_per_chord=2,
    volume=0.95,
):
    seconds_per_chord = 60 / bpm * beats_per_chord
    frames_per_chord = int(seconds_per_chord * SAMPLE_RATE)

    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        for symbol in progression:
            freqs = _chord_frequencies(symbol)

            if not freqs:
                continue

            for i in range(frames_per_chord):
                t = i / SAMPLE_RATE

                chord_value = 0.0
                for freq in freqs:
                    chord_value += _additive_tone(freq, t)

                # Promedio del acorde para que no sature al sonar varias notas
                chord_value /= len(freqs)

                envelope = _envelope(i, frames_per_chord)

                # Aplicamos el volumen general y la envolvente
                sample = int(chord_value * volume * envelope * 32767)
                wav.writeframes(struct.pack("<h", sample))

    return buffer.getvalue()


def play_progression(progression, bpm=90, beats_per_chord=2):
    if not progression:
        return 0.0

    os.makedirs("generated", exist_ok=True)

    wav_path = os.path.abspath("generated/output.wav")

    wav_bytes = progression_to_wav_bytes(progression, bpm=bpm, beats_per_chord=beats_per_chord)

    with open(wav_path, "wb") as f:
        f.write(wav_bytes)

    duration = len(progression) * (60.0 / bpm * beats_per_chord)

    if platform.system() == "Windows":
        import winsound

        # Detiene cualquier reproducción anterior
        winsound.PlaySound(None, winsound.SND_PURGE)

        # Reproduce sin bloquear la app
        winsound.PlaySound(
            wav_path,
            winsound.SND_FILENAME | winsound.SND_ASYNC,
        )
        return duration
    else:
        raise RuntimeError(
            "Esta versión usa winsound, disponible solo en Windows."
        )

def stop_progression():
    if platform.system() == "Windows":
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)

chord_progression_to_wav_bytes = progression_to_wav_bytes