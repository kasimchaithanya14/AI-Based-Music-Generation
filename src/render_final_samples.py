import os
import numpy as np
import pretty_midi
from scipy.io.wavfile import write

INPUT_FOLDER = "outputs/midi"
OUTPUT_FOLDER = "outputs/audio"

FILES = [
    "classical_happy.mid",
    "classical_sad.mid",
    "classical_tense.mid",
    "jazz_happy.mid",
    "electronic_tense.mid",
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in FILES:
    midi_path = os.path.join(INPUT_FOLDER, filename)

    if not os.path.exists(midi_path):
        print("Skipping missing file:", filename)
        continue

    print("\nRendering:", filename)

    midi = pretty_midi.PrettyMIDI(midi_path)
    audio = midi.synthesize(fs=22050)

    peak = np.max(np.abs(audio))

    if peak > 0:
        audio = audio / peak * 0.9

    audio_int16 = (audio * 32767).astype(np.int16)

    wav_name = os.path.splitext(filename)[0] + ".wav"
    wav_path = os.path.join(OUTPUT_FOLDER, wav_name)

    write(wav_path, 22050, audio_int16)

    print("Saved:", wav_path)
    print("Duration:", round(len(audio) / 22050, 2), "seconds")

print("\nAudio rendering completed.")