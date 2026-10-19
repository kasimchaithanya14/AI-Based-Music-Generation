
import csv
import glob
import os
import pretty_midi

INPUT_FOLDER = "outputs/midi"
OUTPUT_FOLDER = "outputs"
CSV_PATH = os.path.join(OUTPUT_FOLDER, "evaluation_results.csv")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

midi_files = sorted(
    path
    for path in glob.glob(os.path.join(INPUT_FOLDER, "*.mid"))
    if not os.path.basename(path).startswith("_")
)

if not midi_files:
    print("No MIDI files found in", INPUT_FOLDER)
    raise SystemExit(1)

results = []

for path in midi_files:
    try:
        midi = pretty_midi.PrettyMIDI(path)

        notes = [
            note
            for instrument in midi.instruments
            for note in instrument.notes
        ]

        duration = midi.get_end_time()
        pitches = [note.pitch for note in notes]
        note_lengths = [
            note.end - note.start
            for note in notes
            if note.end > note.start
        ]

        row = {
            "file": os.path.basename(path),
            "duration_seconds": round(duration, 2),
            "target_seconds": 180,
            "duration_difference_seconds": round(duration - 180, 2),
            "note_count": len(notes),
            "instrument_count": len(midi.instruments),
            "average_pitch": (
                round(sum(pitches) / len(pitches), 2)
                if pitches else ""
            ),
            "minimum_pitch": min(pitches) if pitches else "",
            "maximum_pitch": max(pitches) if pitches else "",
            "average_note_duration_seconds": (
                round(sum(note_lengths) / len(note_lengths), 3)
                if note_lengths else ""
            ),
            "notes_per_second": (
                round(len(notes) / duration, 2)
                if duration > 0 else ""
            ),
            "has_notes": bool(notes),
        }

        results.append(row)

        print("\nFile:", row["file"])
        print("Duration:", row["duration_seconds"], "seconds")
        print("Notes:", row["note_count"])
        print("Instruments:", row["instrument_count"])
        print("Average pitch:", row["average_pitch"])
        print(
            "Average note duration:",
            row["average_note_duration_seconds"],
            "seconds",
        )
        print("Notes per second:", row["notes_per_second"])
        print("Contains notes:", row["has_notes"])

    except Exception as error:
        print("\nCould not evaluate:", path)
        print("Reason:", error)

if not results:
    print("No files could be evaluated.")
    raise SystemExit(1)

with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("\nEvaluation finished.")
print("Files evaluated:", len(results))
print("CSV report saved to:", CSV_PATH)
