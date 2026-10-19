
import os
import csv
import pretty_midi
import numpy as np

INPUT_DIR = "outputs/test_midi"
OUTPUT_CSV = "outputs/test_evaluation_results.csv"

results = []

for filename in sorted(os.listdir(INPUT_DIR)):
    if not filename.lower().endswith(".mid"):
        continue

    path = os.path.join(INPUT_DIR, filename)
    midi = pretty_midi.PrettyMIDI(path)

    notes = [
        note
        for instrument in midi.instruments
        for note in instrument.notes
    ]

    duration = midi.get_end_time()
    pitches = [note.pitch for note in notes]
    note_durations = [
        note.end - note.start for note in notes
    ]

    result = {
        "file": filename,
        "duration_seconds": round(duration, 2),
        "instrument_count": len(midi.instruments),
        "note_count": len(notes),
        "average_pitch": round(float(np.mean(pitches)), 2) if pitches else 0,
        "average_note_duration": round(float(np.mean(note_durations)), 3) if note_durations else 0,
        "notes_per_second": round(len(notes) / duration, 2) if duration > 0 else 0,
        "contains_notes": bool(notes),
    }

    results.append(result)

    print(f"\nFile: {filename}")
    for key, value in result.items():
        if key != "file":
            print(f"{key}: {value}")

os.makedirs("outputs", exist_ok=True)

if results:
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

print(f"\nEvaluation complete: {len(results)} files")
print("CSV saved:", OUTPUT_CSV)
