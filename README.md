# AI-Based Music Generation

## Project Overview

This project is an AI-based music generation prototype that uses a pretrained MIDI-GPT model to generate musical sequences. It supports three genres—Classical, Jazz, and Electronic—and three configurable emotion presets—Happy, Sad, and Tense.

The generated MIDI files can be converted into WAV audio for playback and evaluation. A Flask-based web interface allows users to enter a prompt, select musical settings, choose a duration, generate music, listen to the output, and download files.

## Features

- AI-based MIDI music generation using a pretrained model
- Three supported genres: Classical, Jazz, and Electronic
- Three emotion presets: Happy, Sad, and Tense
- Configurable music duration, including three-minute generation
- MIDI-to-WAV audio rendering
- Flask web interface for music generation
- Audio playback and file downloads
- CSV-based evaluation of basic musical properties

## Technologies Used

- Python 3.11
- MIDI-GPT
- PyTorch
- pretty_midi
- NumPy and SciPy
- Flask
- HTML, CSS, and JavaScript

## Project Structure

```text
ai-music-generator/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── ai_music_generator.py
│   ├── evaluate_music.py
│   ├── render_final_samples.py
│   ├── render_test_samples.py
│   └── evaluate_test_music.py
├── templates/
│   └── index.html
├── static/
├── outputs/
│   ├── midi/
│   ├── audio/
│   ├── test_midi/
│   ├── test_audio/
│   ├── temp_sections/
│   ├── evaluation_results.csv
│   └── test_evaluation_results.csv
└── .venv311/
```

## Installation

Install Python 3.11 and open a terminal in the project directory.

Create a virtual environment if one does not already exist:

```bash
python -m venv .venv311
```

Activate it on Windows CMD:

```cmd
.venv311\Scripts\activate
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

The pretrained model may need to download its checkpoint the first time it is used.

## Run the Web Application

Start Flask from the project directory:

```bash
python app.py
```

Open this address in your browser:

http://127.0.0.1:5000

Keep the terminal open while using the application.

## Generate Music from CMD

Example: generate a three-minute classical piece with a happy preset.

```bash
python src/ai_music_generator.py --genre classical --emotion happy --duration 180
```

Supported genre values:

- `classical`
- `jazz`
- `electronic`

Supported emotion values:

- `happy`
- `sad`
- `tense`

The generator saves output files according to its configured duration-based output directories.

## Evaluation

The project includes evaluation scripts that inspect properties such as:

- MIDI duration
- Instrument count
- Note count
- Average pitch
- Average note duration
- Notes per second
- Whether the MIDI contains notes

The evaluation CSV files provide quantitative summaries of the generated music. These measurements do not independently establish perceived emotional quality; listener evaluation can be added in future work.

## Current Limitations

- The system uses a pretrained model rather than a model trained from scratch for this project.
- Prompt interpretation uses keyword-based genre and emotion selection.
- The model does not directly understand every natural-language instruction.
- Musical quality and emotional perception require additional listening-based evaluation.
- Audio rendering quality depends on the synthesis method and available sound-generation tools.

## Future Enhancements

- Improve natural-language prompt interpretation.
- Explore more controllable musical structures and transitions.
- Improve audio synthesis and instrument sound quality.
- Conduct listener surveys to evaluate perceived genre and emotion.
- Expand the range of musical styles and controls.

## Academic Project

**Project:** AI-Based Music Generation  
**Student:** Kasim Sri Chaithanya Hanu  
**Department:** Computer Science and Engineering  
**Institution:** Dhanekula Institute of Engineering and Technology  
**Academic Year:** 2026–2027
