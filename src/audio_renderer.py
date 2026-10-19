
import argparse
import os

import numpy as np
import pretty_midi
from scipy.io.wavfile import write


def render_audio(genre, emotion):
    midi_path = f"outputs/midi/{genre}_{emotion}.mid"
    audio_path = f"outputs/audio/{genre}_{emotion}.wav"

    if not os.path.exists(midi_path):
        print(f"Error: MIDI file not found: {midi_path}")
        print("Generate the MIDI file first.")
        return

    print("Loading MIDI composition...")
    midi = pretty_midi.PrettyMIDI(midi_path)

    sample_rate = 22050

    print("Synthesizing audio...")
    audio = midi.synthesize(fs=sample_rate)

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak

    audio_int16 = (audio * 32767).astype(np.int16)

    os.makedirs("outputs/audio", exist_ok=True)
    write(audio_path, sample_rate, audio_int16)

    print("Audio generated successfully!")
    print(f"Saved: {audio_path}")
    print(f"Duration: {len(audio) / sample_rate:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genre", required=True,
                        choices=["classical", "jazz", "electronic"])
    parser.add_argument("--emotion", required=True,
                        choices=["happy", "sad", "tense"])

    args = parser.parse_args()
    render_audio(args.genre, args.emotion)
