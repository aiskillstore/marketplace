#!/usr/bin/env python3
"""
Render JSON music structure to MP3 audio file.

This script takes a JSON structure (from midi_inventory.py or custom)
and renders it to MP3 using FluidSynth and the existing rendering pipeline.

Usage:
    python midi_render.py structure.json output.mp3
"""

import argparse
import json
import os
import sys
from pathlib import Path

from music21 import stream, note, instrument, tempo, key, meter
from midi2audio import FluidSynth
from pydub import AudioSegment


# Standard system paths for soundfont files
# These are installed by the skill's install.sh script via: apt-get install fluid-soundfont-gm
SOUNDFONT_PATHS = [
    '/usr/share/sounds/sf2/FluidR3_GM.sf2',
    '/usr/share/sounds/sf2/default.sf2',
    '/usr/share/soundfonts/default.sf2',
]


def get_soundfont_path():
    """Find the best available SoundFont."""
    for path in SOUNDFONT_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("No SoundFont file found. Install with: apt-get install fluid-soundfont-gm")


INSTRUMENTS = {
    "piano": (instrument.Piano(), 0),
    "bright_piano": (instrument.Piano(), 1),
    "electric_piano": (instrument.Piano(), 4),
    "acoustic_guitar": (instrument.AcousticGuitar(), 24),
    "electric_guitar": (instrument.ElectricGuitar(), 27),
    "bass": (instrument.Bass(), 32),
    "violin": (instrument.Violin(), 40),
    "viola": (instrument.Viola(), 41),
    "cello": (instrument.Violoncello(), 42),
    "contrabass": (instrument.Contrabass(), 43),
    "harp": (instrument.Harp(), 46),
    "timpani": (instrument.Timpani(), 47),
    "trumpet": (instrument.Trumpet(), 56),
    "trombone": (instrument.Trombone(), 57),
    "tuba": (instrument.Tuba(), 58),
    "french_horn": (instrument.Horn(), 60),
    "oboe": (instrument.Oboe(), 68),
    "bassoon": (instrument.Bassoon(), 70),
    "clarinet": (instrument.Clarinet(), 71),
    "flute": (instrument.Flute(), 73),
    "synth_pad": (instrument.Piano(), 88),
}


def render_json_to_mp3(json_structure: dict, output_mp3: Path) -> str:
    """Render JSON music structure to MP3 file."""
    score = stream.Score()

    if "tempo" in json_structure:
        score.insert(0, tempo.MetronomeMark(number=json_structure["tempo"]))

    if "key_signature" in json_structure and json_structure["key_signature"]:
        score.insert(0, key.Key(json_structure["key_signature"]))

    if "time_signature" in json_structure:
        score.insert(0, meter.TimeSignature(json_structure["time_signature"]))

    for track_id, track_data in json_structure.get("tracks", {}).items():
        part = stream.Part()

        inst_name = track_data.get("instrument", "piano")
        if inst_name in INSTRUMENTS:
            inst_obj, midi_num = INSTRUMENTS[inst_name]
            part.insert(0, inst_obj)
        else:
            part.insert(0, instrument.Piano())

        if "tempo" in json_structure:
            part.insert(0, tempo.MetronomeMark(number=json_structure["tempo"]))

        for note_data in track_data.get("notes", []):
            pitch = note_data.get("pitch")
            duration = note_data.get("duration", 0.5)
            start_time = note_data.get("start", 0.0)

            tempo_bpm = json_structure.get("tempo", 120)
            quarter_length = duration * (tempo_bpm / 60)

            n = note.Note(pitch, quarterLength=quarter_length)
            part.insert(start_time, n)

        score.append(part)

    title = output_mp3.stem
    midi_path = output_mp3.parent / f"{title}.mid"
    wav_path = output_mp3.parent / f"{title}.wav"

    score.write('midi', fp=str(midi_path))
    print(f"MIDI created: {midi_path}")

    sf_path = get_soundfont_path()
    fs = FluidSynth(sf_path)
    fs.midi_to_audio(str(midi_path), str(wav_path))
    print(f"WAV rendered: {wav_path}")

    audio = AudioSegment.from_wav(str(wav_path))

    # Apply gentle limiter to prevent clipping (threshold=-10dB, ratio=2.5:1, attack=5ms)
    audio = audio.compress_dynamic_range(threshold=-10.0, ratio=2.5, attack=5.0)

    if json_structure.get("length_seconds"):
        target_ms = int(json_structure["length_seconds"] * 1000)
        if len(audio) > target_ms:
            audio = audio[:target_ms]

    audio = audio.fade_out(2000)

    audio.export(str(output_mp3), format='mp3', bitrate='192k')
    print(f"MP3 exported: {output_mp3}")

    try:
        os.remove(midi_path)
        os.remove(wav_path)
    except:
        pass

    return str(output_mp3)


def main():
    parser = argparse.ArgumentParser(
        description="Render JSON music structure to MP3 audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python midi_render.py structure.json output.mp3
    Render JSON structure to MP3

  python midi_render.py modified-song.json new-version.mp3
    Render modified structure

JSON structure format:
  {
    "tempo": 120,
    "key_signature": "C",
    "time_signature": "4/4",
    "tracks": {
      "track-0": {
        "instrument": "violin",
        "notes": [
          {"pitch": "E5", "start": 0.0, "duration": 0.5}
        ]
      }
    }
  }
        """
    )

    parser.add_argument("input", help="Input JSON structure file")
    parser.add_argument("output", help="Output MP3 file")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not input_path.suffix.lower() == '.json':
        print("Error: Input must be a JSON file")
        sys.exit(1)

    try:
        print(f"Loading JSON structure from: {args.input}")
        with open(input_path, 'r') as f:
            structure = json.load(f)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not output_path.suffix.lower() == '.mp3':
            output_path = output_path.with_suffix('.mp3')

        result = render_json_to_mp3(structure, output_path)
        print(f"\nRendering complete!")
        print(f"Output: {result}")

    except Exception as e:
        print(f"Error rendering audio: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()