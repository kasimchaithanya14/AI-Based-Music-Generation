
from midigpt import Score, Track, Bar
from midigpt.inference import (
    InferenceEngine,
    GenerationRequest,
    InferenceConfig,
    TrackPrompt,
)

print("Loading pretrained MIDI-GPT model...")
engine = InferenceEngine.from_pretrained("yellow_medium")

score = Score(
    tracks=[
        Track(
            bars=[Bar() for _ in range(4)],
            instrument=0,
            track_type="melodic",
        )
    ]
)

request = GenerationRequest(
    tracks=[
        TrackPrompt(
            id=0,
            bars=[0, 1, 2, 3],
        )
    ],
    config=InferenceConfig(
        temperature=1.0,
        top_p=0.95,
        model_dim=4,
        mask_mode="attention",
    ),
)

print("Generating music...")
result = engine.session(score, request).run()

total_notes = sum(
    len(bar.notes)
    for track in result.tracks
    for bar in track.bars
)

if total_notes == 0:
    raise RuntimeError("The model returned a MIDI with no notes.")

output_path = "outputs/midi/ai_test.mid"
result.to_midi(output_path)

print("Generated notes:", total_notes)
print("AI-generated MIDI saved to:", output_path)
