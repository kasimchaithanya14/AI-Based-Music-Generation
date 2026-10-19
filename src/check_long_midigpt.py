import os
import pretty_midi

midi_path = "outputs/midi/ai_long_test.mid"
audio_path = "outputs/audio/ai_long_test.wav"

midi = pretty_midi.PrettyMIDI(midi_path)

duration = midi.get_end_time()
note_count = sum(len(track.notes) for track in midi.instruments)

print(f"MIDI duration: {duration:.2f} seconds")
print(f"MIDI duration: {duration / 60:.2f} minutes")
print(f"Total notes: {note_count}")
print(f"Tracks: {len(midi.instruments)}")

if note_count == 0:
    raise RuntimeError("The MIDI contains no notes.")

print("Rendering audio...")
audio = midi.synthesize(fs=22050)

if len(audio) == 0:
    raise RuntimeError("Audio rendering produced no samples.")

peak = max(abs(audio))

if peak > 0:
    audio = audio / peak * 0.9

os.makedirs("outputs/audio", exist_ok=True)
midi.fluidsynth = None

from scipy.io.wavfile import write
write(audio_path, 22050, (audio * 32767).astype("int16"))

print("Audio saved to:", audio_path)
print("Audio duration:", f"{len(audio) / 22050:.2f} seconds")