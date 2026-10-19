
import argparse
import os
import pretty_midi

from midigpt import Score, Track, Bar
from midigpt.inference import (
    InferenceEngine,
    GenerationRequest,
    InferenceConfig,
    TrackPrompt,
)

MOODS = {
    "happy": {
        "scale": "major",
        "root": 0,
        "min_pitch": 60,
        "max_pitch": 84,
        "min_note_duration": 1,
        "max_note_duration": 3,
    },
    "sad": {
        "scale": "natural_minor",
        "root": 9,
        "min_pitch": 48,
        "max_pitch": 72,
        "min_note_duration": 2,
        "max_note_duration": 4,
    },
    "tense": {
        "scale": "phrygian",
        "root": 0,
        "min_pitch": 48,
        "max_pitch": 84,
        "min_note_duration": 0,
        "max_note_duration": 2,
    },
}

GENRES = {
    "classical": {"program": 0, "tempo": 100},
    "jazz": {"program": 4, "tempo": 120},
    "electronic": {"program": 80, "tempo": 125},
}


def main():
    parser = argparse.ArgumentParser(
        description="AI music generator using pretrained MIDI-GPT"
    )

    parser.add_argument(
        "--genre",
        choices=GENRES.keys(),
        default="classical",
    )

    parser.add_argument(
        "--emotion",
        choices=MOODS.keys(),
        default="happy",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=180,
        help="Target duration in seconds",
    )

    args = parser.parse_args()

    if args.duration < 10:
        parser.error("Duration must be at least 10 seconds.")

    mood = MOODS[args.emotion]
    genre = GENRES[args.genre]

    # Keep short test generations separate from final outputs.
    if args.duration < 180:
        output_folder = "outputs/test_midi"
    else:
        output_folder = "outputs/midi"

    os.makedirs(output_folder, exist_ok=True)

    # Temporary section files are stored separately.
    temp_folder = "outputs/temp_sections"
    os.makedirs(temp_folder, exist_ok=True)

    output_path = os.path.join(
        output_folder,
        f"{args.genre}_{args.emotion}.mid",
    )

    bars_per_section = 8
    max_sections = max(20, args.duration // 4 + 10)

    print("Loading pretrained MIDI-GPT model...")
    engine = InferenceEngine.from_pretrained("yellow_medium")

    combined = pretty_midi.PrettyMIDI(
        initial_tempo=genre["tempo"]
    )

    offset = 0.0
    section_index = 0

    while offset < args.duration and section_index < max_sections:
        section_index += 1

        print(
            f"\nGenerating section {section_index} "
            f"(current duration: {offset:.1f}s)..."
        )

        score = Score(
            tracks=[
                Track(
                    bars=[Bar() for _ in range(bars_per_section)],
                    instrument=genre["program"],
                    track_type="melodic",
                )
            ]
        )

        request = GenerationRequest(
            tracks=[
                TrackPrompt(
                    id=0,
                    bars=list(range(bars_per_section)),
                    autoregressive=True,
                    controls={
                        "pitch_mask": {
                            "scale": mood["scale"],
                            "root": mood["root"],
                            "shape": {
                                "type": "uniform",
                                "min": mood["min_pitch"],
                                "max": mood["max_pitch"],
                            },
                        }
                    },
                    attributes={
                        "min_note_duration": mood["min_note_duration"],
                        "max_note_duration": mood["max_note_duration"],
                        "min_polyphony": 0,
                        "max_polyphony": 3,
                    },
                )
            ],
            config=InferenceConfig(
                temperature=1.0,
                seed=100 + section_index,
                top_p=0.95,
                model_dim=4,
                mask_mode="attention",
                bars_per_step=1,
                max_attempts=5,
                temperature_escalation=1.2,
            ),
        )

        result = engine.session(score, request).run()

        temporary_path = os.path.join(
            temp_folder,
            f"_section_{section_index:03d}.mid",
        )

        result.to_midi(temporary_path)
        segment = pretty_midi.PrettyMIDI(temporary_path)

        notes = [
            note
            for inst in segment.instruments
            for note in inst.notes
        ]

        # Remove the temporary MIDI after reading it.
        os.remove(temporary_path)

        if not notes:
            print("Warning: empty section; skipping.")
            continue

        section_duration = segment.get_end_time()

        if section_duration <= 0:
            print("Warning: zero-duration section; skipping.")
            continue

        instrument = pretty_midi.Instrument(
            program=genre["program"],
            name=f"{args.genre.title()} section {section_index}",
        )

        for note in notes:
            start = note.start + offset
            end = note.end + offset

            if start >= args.duration:
                continue

            instrument.notes.append(
                pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=start,
                    end=min(end, float(args.duration)),
                )
            )

        if instrument.notes:
            combined.instruments.append(instrument)

        offset += section_duration

        print(
            f"Generated section length: {section_duration:.1f}s"
        )

    if offset < args.duration:
        print(
            "\nWarning: generation reached its section limit "
            "before the target duration."
        )

    # Trim notes to the requested duration.
    for instrument in combined.instruments:
        instrument.notes = [
            note
            for note in instrument.notes
            if note.start < args.duration
            and note.end > note.start
        ]

        for note in instrument.notes:
            note.end = min(note.end, float(args.duration))

    combined.write(output_path)

    total_notes = sum(
        len(inst.notes) for inst in combined.instruments
    )

    final_duration = combined.get_end_time()

    print("\nMusic generation finished.")
    print("Genre:", args.genre)
    print("Mood:", args.emotion)
    print("Notes:", total_notes)
    print(f"Target duration: {args.duration} seconds")
    print(f"Actual MIDI duration: {final_duration:.2f} seconds")
    print("Saved:", output_path)

    if final_duration < args.duration - 1:
        print(
            "Warning: the MIDI contains less music than requested. "
            "Check the generated sections."
        )

    print(
        "\nGenre presets are heuristic settings, not a model "
        "trained specifically to follow genre labels."
    )


if __name__ == "__main__":
    main()

