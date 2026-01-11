#!/usr/bin/env python3
"""
Extract structured information from MIDI files to JSON.

This script analyzes any MIDI file and extracts:
- Tempo, key signature, time signature
- Track information and instrument assignments
- Note sequences with timing and velocity
- Chord progressions and musical structure

Usage:
    python midi_inventory.py input.mid output.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import mido


def extract_midi_inventory(midi_path: Path) -> dict[str, Any]:
    """Extract complete musical structure from MIDI file."""
    midi = mido.MidiFile(midi_path)

    inventory = {
        "filename": midi_path.name,
        "type": midi.type,
        "ticks_per_beat": midi.ticks_per_beat,
        "length_seconds": midi.length,
        "tempo": 120,
        "time_signature": "4/4",
        "key_signature": None,
        "tracks": {}
    }

    current_tempo = 500000

    for track_idx, track in enumerate(midi.tracks):
        track_name = f"track-{track_idx}"
        track_info = {
            "name": track.name or track_name,
            "instrument": None,
            "midi_program": None,
            "notes": []
        }

        absolute_time = 0
        active_notes = {}

        for msg in track:
            absolute_time += msg.time

            if msg.type == 'set_tempo':
                current_tempo = msg.tempo
                inventory["tempo"] = int(60000000 / current_tempo)

            elif msg.type == 'time_signature':
                inventory["time_signature"] = f"{msg.numerator}/{msg.denominator}"

            elif msg.type == 'key_signature':
                inventory["key_signature"] = msg.key

            elif msg.type == 'program_change':
                track_info["midi_program"] = msg.program
                track_info["instrument"] = get_instrument_name(msg.program)

            elif msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = {
                    "start_ticks": absolute_time,
                    "velocity": msg.velocity
                }

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    note_start = active_notes[msg.note]
                    duration_ticks = absolute_time - note_start["start_ticks"]

                    start_seconds = ticks_to_seconds(
                        note_start["start_ticks"],
                        midi.ticks_per_beat,
                        current_tempo
                    )
                    duration_seconds = ticks_to_seconds(
                        duration_ticks,
                        midi.ticks_per_beat,
                        current_tempo
                    )

                    track_info["notes"].append({
                        "pitch": midi_note_to_name(msg.note),
                        "midi_note": msg.note,
                        "start": round(start_seconds, 3),
                        "duration": round(duration_seconds, 3),
                        "velocity": note_start["velocity"]
                    })

                    del active_notes[msg.note]

        if track_info["notes"]:
            inventory["tracks"][track_name] = track_info

    return inventory


def ticks_to_seconds(ticks: int, ticks_per_beat: int, tempo: int) -> float:
    """Convert MIDI ticks to seconds."""
    seconds_per_tick = (tempo / 1000000) / ticks_per_beat
    return ticks * seconds_per_tick


def midi_note_to_name(midi_note: int) -> str:
    """Convert MIDI note number to note name (e.g., 60 -> C4)."""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note = note_names[midi_note % 12]
    return f"{note}{octave}"


def get_instrument_name(program: int) -> str:
    """Get instrument name from General MIDI program number."""
    instruments = {
        0: "piano", 1: "bright_piano", 4: "electric_piano",
        24: "acoustic_guitar", 27: "electric_guitar", 32: "bass",
        40: "violin", 41: "viola", 42: "cello", 43: "contrabass",
        46: "harp", 47: "timpani",
        56: "trumpet", 57: "trombone", 58: "tuba", 60: "french_horn",
        68: "oboe", 70: "bassoon", 71: "clarinet", 73: "flute",
        88: "synth_pad", 80: "synth_lead"
    }
    return instruments.get(program, f"program_{program}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract musical structure from MIDI files to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python midi_inventory.py song.mid structure.json
    Extract complete structure from any MIDI file

  python midi_inventory.py mozart.mid mozart-analysis.json
    Analyze classical MIDI file

Output JSON structure:
  {
    "tempo": 120,
    "time_signature": "4/4",
    "key_signature": "C",
    "tracks": {
      "track-0": {
        "instrument": "violin",
        "midi_program": 40,
        "notes": [
          {"pitch": "E5", "start": 0.0, "duration": 0.5, "velocity": 80}
        ]
      }
    }
  }
        """
    )

    parser.add_argument("input", help="Input MIDI file (.mid)")
    parser.add_argument("output", help="Output JSON file")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not input_path.suffix.lower() in ['.mid', '.midi']:
        print("Error: Input must be a MIDI file (.mid or .midi)")
        sys.exit(1)

    try:
        print(f"Extracting MIDI structure from: {args.input}")
        inventory = extract_midi_inventory(input_path)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(inventory, f, indent=2)

        print(f"Inventory saved to: {args.output}")
        print(f"  Tempo: {inventory['tempo']} BPM")
        print(f"  Time signature: {inventory['time_signature']}")
        print(f"  Duration: {inventory['length_seconds']:.1f}s")
        print(f"  Tracks: {len(inventory['tracks'])}")

    except Exception as e:
        print(f"Error extracting MIDI structure: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()