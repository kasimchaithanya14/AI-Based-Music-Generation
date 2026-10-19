
import os
import pretty_midi

from midigpt import Score, Track, Bar
from midigpt.inference import (
    InferenceEngine,
    GenerationRequest,
    InferenceConfig,
    TrackPrompt,
)

os.makedirs("outputs/midi", exist_ok=True)

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

BAR_COUNT = 16

print("Loading MIDI-GPT...")
engine = InferenceEngine.from_pretrained("yellow_medium")

for index, (mood, settings) in enumerate(MOODS.items()):
    print(f"\nGenerating mood: {mood}")

    score = Score(
        tracks=[
            Track(
                bars=[Bar() for _ in range(BAR_COUNT)],
                instrument=0,
                track_type="melodic",
            )
        ]
    )

    request = GenerationRequest(
        tracks=[
            TrackPrompt(
                id=0,
                bars=list(range(BAR_COUNT)),
                autoregressive=True,
                controls={
                    "pitch_mask": {
                        "scale": settings["scale"],
                        "root": settings["root"],
                        "shape": {
                            "type": "uniform",
                            "min": settings["min_pitch"],
                            "max": settings["max_pitch"],
                        },
                    }
                },
                attributes={
                    "min_note_duration": settings["min_note_duration"],
                    "max_note_duration": settings["max_note_duration"],
                    "min_polyphony": 0,
                    "max_polyphony": 3,
                },
            )
        ],
        config=InferenceConfig(
            temperature=1.0,
            seed=100 + index,
            top_p=0.95,
            model_dim=4,
            mask_mode="attention",
            bars_per_step=1,
            max_attempts=5,
            temperature_escalation=1.2,
        ),
    )

    result = engine.session(score, request).run()

    path = f"outputs/midi/mood_{mood}.mid"
    result.to_midi(path)

    midi = pretty_midi.PrettyMIDI(path)
    notes = [note for inst in midi.instruments for note in inst.notes]

    if not notes:
        print("WARNING: No notes generated.")
        continue

    print("Saved:", path)
    print("Notes:", len(notes))
    print(f"Duration: {midi.get_end_time():.2f} seconds")
    print(f"Average pitch: {sum(n.pitch for n in notes) / len(notes):.1f}")
    print(
        "Average note length:",
        f"{sum(n.end - n.start for n in notes) / len(notes):.2f} seconds",
    )

print("\nMood-control test finished.")
