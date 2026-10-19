
import argparse
import os
import random
import pretty_midi


def generate_music(genre, emotion, duration):
    random.seed()

    # Choose tempo based on genre and emotion
    genre_tempos = {
        "classical": 100,
        "jazz": 115,
        "electronic": 125,
    }

    emotion_adjustments = {
        "happy": 15,
        "sad": -25,
        "tense": 20,
    }

    tempo = max(
        50,
        min(180, genre_tempos[genre] + emotion_adjustments[emotion])
    )

    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    # Select instrument
    programs = {
        "classical": 0,   # Acoustic piano
        "jazz": 4,        # Electric piano
        "electronic": 80, # Synth lead
    }

    instrument = pretty_midi.Instrument(
        program=programs[genre]
    )

    # Basic scale selection
    scales = {
        "happy": [60, 62, 64, 65, 67, 69, 71, 72],
        "sad": [57, 59, 60, 62, 64, 65, 67, 69],
        "tense": [60, 61, 63, 66, 67, 69, 70, 72],
    }

    scale = scales[emotion]

    # Create a continuous melody for the requested duration
    beat = 60.0 / tempo
    note_duration = beat * 0.8
    step = beat

    start = 0.0

    while start + note_duration <= duration:
        pitch = random.choice(scale)

        # Genre-specific note variation
        if genre == "jazz" and random.random() < 0.25:
            pitch += 12

        if genre == "electronic" and random.random() < 0.30:
            pitch = scale[0] + (pitch - scale[0]) % 12

        velocity = 90 if emotion == "happy" else 65
        if emotion == "tense":
            velocity = 105

        note = pretty_midi.Note(
            velocity=velocity,
            pitch=max(0, min(127, pitch)),
            start=start,
            end=min(start + note_duration, duration),
        )

        instrument.notes.append(note)
        start += step

    midi.instruments.append(instrument)

    os.makedirs("outputs/midi", exist_ok=True)

    output_path = (
        f"outputs/midi/{genre}_{emotion}.mid"
    )

    midi.write(output_path)

    print("Composition created!")
    print(f"Genre: {genre}")
    print(f"Emotion: {emotion}")
    print(f"Tempo: {tempo} BPM")
    print(f"Target duration: {duration} seconds")
    print(f"Notes: {len(instrument.notes)}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--genre",
        choices=["classical", "jazz", "electronic"],
        default="classical",
    )

    parser.add_argument(
        "--emotion",
        choices=["happy", "sad", "tense"],
        default="happy",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=180,
    )

    args = parser.parse_args()

    generate_music(
        args.genre,
        args.emotion,
        args.duration,
    )
