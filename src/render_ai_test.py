
import os
import numpy as np
import pretty_midi
from scipy.io.wavfile import write

midi_path = "outputs/midi/ai_test.mid"
audio_path = "outputs/audio/ai_test.wav"

if not os.path.exists(midi_path):
    raise FileNotFoundError(f"MIDI file not found: {midi_path}")

midi = pretty_midi.PrettyMIDI(midi_path)

note_count = sum(len(track.notes) for track in midi.instruments)
print("MIDI notes:", note_count)
print("MIDI duration:", round(midi.get_end_time(), 2), "seconds")

if note_count == 0:
    raise ValueError("The MIDI contains no notes.")

sample_rate = 22050
audio = midi.synthesize(fs=sample_rate)

peak = np.max(np.abs(audio))
if peak > 0:
    audio = audio / peak

audio_int16 = (audio * 32767).astype(np.int16)

os.makedirs("outputs/audio", exist_ok=True)
write(audio_path, sample_rate, audio_int16)

print("Audio saved to:", audio_path)
print("Audio duration:", round(len(audio) / sample_rate, 2), "seconds")
