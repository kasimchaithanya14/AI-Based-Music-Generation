
import sys
import threading
import subprocess
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

MIDI_DIR = OUTPUT_DIR / "midi"
TEST_MIDI_DIR = OUTPUT_DIR / "test_midi"
TEST_AUDIO_DIR = OUTPUT_DIR / "test_audio"

GENERATOR = BASE_DIR / "src" / "ai_music_generator.py"

app = Flask(__name__)
generation_lock = threading.Lock()

generation_status = {
    "running": False,
    "message": "Ready to create music.",
    "error": None,
    "midi": None,
    "audio": None,
    "midi_folder": None,
    "duration": None,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}

    genre = data.get("genre", "classical")
    emotion = data.get("emotion", "happy")
    prompt = str(data.get("prompt", "")).strip()

    if genre not in {"classical", "jazz", "electronic"}:
        return jsonify(error="Invalid genre."), 400

    if emotion not in {"happy", "sad", "tense"}:
        return jsonify(error="Invalid emotion."), 400

    if len(prompt) > 1000:
        return jsonify(error="Keep your prompt under 1000 characters."), 400

    try:
        duration = int(data.get("duration", 30))
    except (ValueError, TypeError):
        return jsonify(error="Duration must be a whole number."), 400

    if not 10 <= duration <= 180:
        return jsonify(
            error="Duration must be between 10 and 180 seconds."
        ), 400

    # Interpret selected genre and emotion using prompt keywords.
    # MIDI-GPT is not directly conditioned on the prompt text.
    text = prompt.lower()

    genre_keywords = {
        "classical": [
            "classical", "piano", "orchestra", "orchestral",
            "symphony", "violin", "cinematic",
        ],
        "jazz": [
            "jazz", "saxophone", "sax", "swing", "blues",
        ],
        "electronic": [
            "electronic", "synth", "synthesizer", "edm",
            "techno", "dance", "digital",
        ],
    }

    emotion_keywords = {
        "happy": [
            "happy", "joyful", "cheerful", "positive",
            "uplifting", "celebration",
        ],
        "sad": [
            "sad", "melancholy", "heartbreak", "lonely",
            "sorrowful", "emotional",
        ],
        "tense": [
            "tense", "dark", "suspense", "suspenseful",
            "intense", "dramatic", "thriller",
        ],
    }

    for candidate, keywords in genre_keywords.items():
        if any(word in text for word in keywords):
            genre = candidate
            break

    for candidate, keywords in emotion_keywords.items():
        if any(word in text for word in keywords):
            emotion = candidate
            break

    if not GENERATOR.is_file():
        return jsonify(error=f"Generator script not found: {GENERATOR}"), 500

    if not generation_lock.acquire(blocking=False):
        return jsonify(
            error="A generation is already running. Please wait."
        ), 409

    def run_generation():
        try:
            # IMPORTANT:
            # The generator saves durations below 180 seconds to test_midi.
            # A duration of exactly 180 seconds is saved to outputs/midi.
            if duration < 180:
                midi_dir = TEST_MIDI_DIR
                midi_folder = "test_midi"
            else:
                midi_dir = MIDI_DIR
                midi_folder = "midi"

            midi_dir.mkdir(parents=True, exist_ok=True)
            TEST_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

            midi_path = midi_dir / f"{genre}_{emotion}.mid"
            audio_path = TEST_AUDIO_DIR / f"{genre}_{emotion}.wav"

            # Remove previous files so an old 30-second result
            # cannot accidentally be reported as the new result.
            for old_file in (midi_path, audio_path):
                if old_file.exists():
                    old_file.unlink()

            generation_status.update(
                running=True,
                message=f"Generating {duration}-second {genre} / {emotion} music...",
                error=None,
                midi=None,
                audio=None,
                midi_folder=None,
                duration=duration,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--genre", genre,
                    "--emotion", emotion,
                    "--duration", str(duration),
                ],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=1800,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    result.stderr[-3000:]
                    or result.stdout[-3000:]
                    or "Music generation failed."
                )

            if not midi_path.is_file():
                raise RuntimeError(
                    f"Generator finished, but the expected MIDI file "
                    f"was not found: {midi_path}\n"
                    f"Generator output:\n{result.stdout[-2000:]}"
                )

            generation_status["message"] = (
                f"Checking the generated MIDI ({duration} seconds)..."
            )

            # Confirm the actual MIDI duration before rendering audio.
            check_code = """
import sys
import pretty_midi

midi = pretty_midi.PrettyMIDI(sys.argv[1])
print(midi.get_end_time())
"""

            checked = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    check_code,
                    str(midi_path),
                ],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=60,
            )

            if checked.returncode != 0:
                raise RuntimeError(
                    checked.stderr[-3000:]
                    or "Could not validate MIDI duration."
                )

            try:
                actual_duration = float(checked.stdout.strip().splitlines()[-1])
            except (ValueError, IndexError):
                raise RuntimeError("Could not read the generated MIDI duration.")

            # Allow a small difference caused by MIDI note timing.
            tolerance = max(3.0, duration * 0.02)

            if actual_duration < duration - tolerance:
                raise RuntimeError(
                    f"Duration mismatch: requested {duration} seconds, "
                    f"but the MIDI is only {actual_duration:.2f} seconds. "
                    f"Check the duration handling in ai_music_generator.py."
                )

            generation_status["message"] = (
                f"MIDI verified ({actual_duration:.1f} seconds). Rendering WAV..."
            )

            render_code = """
import sys
import numpy as np
import pretty_midi
from scipy.io import wavfile

midi_path, wav_path = sys.argv[1], sys.argv[2]
sample_rate = 44100

midi = pretty_midi.PrettyMIDI(midi_path)
audio = np.asarray(midi.synthesize(fs=sample_rate), dtype=np.float32)

if audio.size == 0:
    raise RuntimeError("No audio was produced.")

peak = np.max(np.abs(audio))
if peak > 0:
    audio = audio / peak * 0.9

wavfile.write(wav_path, sample_rate, audio)

print(f"Rendered duration: {len(audio) / sample_rate:.2f} seconds")
"""

            rendered = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    render_code,
                    str(midi_path),
                    str(audio_path),
                ],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=600,
            )

            if rendered.returncode != 0:
                raise RuntimeError(
                    rendered.stderr[-3000:]
                    or rendered.stdout[-3000:]
                    or "Audio rendering failed."
                )

            if not audio_path.is_file() or audio_path.stat().st_size == 0:
                raise RuntimeError("The WAV file was not created correctly.")

            generation_status.update(
                running=False,
                message=(
                    f"Complete! Generated {genre} / {emotion}. "
                    f"MIDI duration: {actual_duration:.1f} seconds."
                ),
                midi=midi_path.name,
                audio=audio_path.name,
                midi_folder=midi_folder,
                duration=duration,
                error=None,
            )

        except Exception as exc:
            generation_status.update(
                running=False,
                message="Generation failed.",
                error=str(exc),
                midi=None,
                audio=None,
                midi_folder=None,
            )

        finally:
            generation_lock.release()

    threading.Thread(
        target=run_generation,
        daemon=True,
    ).start()

    return jsonify(
        message="Generation started.",
        interpreted_genre=genre,
        interpreted_emotion=emotion,
        requested_duration=duration,
    ), 202


@app.route("/status")
def status():
    return jsonify(generation_status)


@app.route("/files/<kind>/<path:filename>")
def download_file(kind, filename):
    # Keep compatibility with existing frontend links.
    if kind == "midi":
        current_folder = generation_status.get("midi_folder")

        if current_folder == "midi":
            folders = [MIDI_DIR, TEST_MIDI_DIR]
        else:
            folders = [TEST_MIDI_DIR, MIDI_DIR]

    elif kind == "audio":
        folders = [TEST_AUDIO_DIR]

    else:
        return jsonify(error="Invalid file type."), 400

    for folder in folders:
        candidate = folder / filename

        if candidate.is_file():
            return send_from_directory(
                folder,
                filename,
                as_attachment=True,
            )

    return jsonify(error="Requested file was not found."), 404


@app.route("/audio/<path:filename>")
def play_audio(filename):
    return send_from_directory(
        TEST_AUDIO_DIR,
        filename,
        mimetype="audio/wav",
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
