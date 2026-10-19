
import os
import pretty_midi
import numpy as np
from scipy.io import wavfile

INPUT_DIR = "outputs/test_midi"
OUTPUT_DIR = "outputs/test_audio"
SAMPLE_RATE = 44100

os.makedirs(OUTPUT_DIR, exist_ok=True)

midi_files = sorted(
    filename
    for filename in os.listdir(INPUT_DIR)
    if filename.lower().endswith(".mid")
)

if not midi_files:
    print("No MIDI files found.")
    raise SystemExit(1)

for filename in midi_files:
    midi_path = os.path.join(INPUT_DIR, filename)
    wav_path = os.path.join(
        OUTPUT_DIR,
        os.path.splitext(filename)[0] + ".wav",
    )

    print(f"\nRendering: {filename}")

    try:
        midi = pretty_midi.PrettyMIDI(midi_path)
        audio = midi.synthesize(fs=SAMPLE_RATE)

        audio = np.asarray(audio, dtype=np.float32)

        if audio.size == 0:
            print("Skipped: no audio was generated.")
            continue

        # Normalize volume to prevent clipping.
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio / peak * 0.9

        wavfile.write(wav_path, SAMPLE_RATE, audio)

        print("Saved:", wav_path)
        print(f"MIDI duration: {midi.get_end_time():.2f} seconds")
        print(f"WAV duration: {len(audio) / SAMPLE_RATE:.2f} seconds")

    except Exception as error:
        print(f"Failed: {filename}: {error}")

print("\nTest audio rendering completed.")

