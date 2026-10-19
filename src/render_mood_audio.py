
import os
import pretty_midi
import numpy as np
from scipy.io.wavfile import write

os.makedirs("outputs/audio", exist_ok=True)

for mood in ["happy", "sad", "tense"]:
    midi_path = f"outputs/midi/mood_{mood}.mid"
    wav_path = f"outputs/audio/mood_{mood}.wav"

    print(f"\nRendering {mood}...")

    midi = pretty_midi.PrettyMIDI(midi_path)
    audio = midi.synthesize(fs=22050)

    peak = np.max(np.abs(audio)) if len(audio) else 0

    if peak > 0:
        audio = audio / peak * 0.9

    write(wav_path, 22050, (audio * 32767).astype(np.int16))

    print("Saved:", wav_path)
    print(f"Duration: {len(audio) / 22050:.2f} seconds")

print("\nAll mood audio files are ready.")
