
import os
import pretty_midi

from midigpt import Score, Track, Bar
from midigpt.inference import (
    InferenceEngine,
    GenerationRequest,
    InferenceConfig,
    TrackPrompt,
)

BAR_COUNT = 32
SECTION_COUNT = 4
OUTPUT_PATH = "outputs/midi/ai_long_test.mid"
SEGMENT_DIR = "outputs/midi/segments"

os.makedirs(SEGMENT_DIR, exist_ok=True)
os.makedirs("outputs/midi", exist_ok=True)

print("Loading pretrained MIDI-GPT model...")
engine = InferenceEngine.from_pretrained("yellow_medium")

combined = pretty_midi.PrettyMIDI()
offset = 0.0

for section in range(SECTION_COUNT):
    print(f"\nGenerating section {section + 1}/{SECTION_COUNT}...")

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
            )
        ],
        config=InferenceConfig(
            temperature=1.0,
            seed=100 + section,
            top_p=0.95,
            model_dim=4,
            mask_mode="attention",
            bars_per_step=1,
            max_attempts=5,
            temperature_escalation=1.2,
        ),
    )

    result = engine.session(score, request).run()

    segment_path = os.path.join(
        SEGMENT_DIR, f"section_{section + 1:02d}.mid"
    )
    result.to_midi(segment_path)

    segment = pretty_midi.PrettyMIDI(segment_path)
    note_count = sum(len(inst.notes) for inst in segment.instruments)
    duration = segment.get_end_time()

    if note_count == 0 or duration <= 0:
        raise RuntimeError(
            f"Section {section + 1} contains no usable music."
        )

    print(f"Notes: {note_count}")
    print(f"Duration: {duration:.2f} seconds")

    for instrument in segment.instruments:
        shifted = pretty_midi.Instrument(
            program=instrument.program,
            is_drum=instrument.is_drum,
            name=f"Section {section + 1}",
        )

        for note in instrument.notes:
            shifted.notes.append(
                pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.start + offset,
                    end=note.end + offset,
                )
            )

        combined.instruments.append(shifted)

    offset += duration

combined.write(OUTPUT_PATH)

total_notes = sum(
    len(inst.notes) for inst in combined.instruments
)

print("\nAll sections combined successfully.")
print("Total sections:", SECTION_COUNT)
print("Total notes:", total_notes)
print(f"Combined MIDI duration: {combined.get_end_time():.2f} seconds")
print("Saved:", OUTPUT_PATH)
