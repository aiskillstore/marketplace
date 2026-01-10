#!/usr/bin/env python3
"""
Transform MIDI structure JSON with various operations.

This script applies generic transformations to JSON music structures:
- Transpose (shift all pitches)
- Tempo scaling (speed up/slow down)
- Duration extension (loop/repeat)
- Instrument swapping
- Section looping
- Reversal

Usage:
    python midi_transform.py input.json output.json --transpose 2 --tempo-scale 1.5
"""

import argparse
import copy
import json
import sys
from pathlib import Path


def transpose_notes(notes: list[dict], semitones: int) -> list[dict]:
    """Transpose all notes by semitones."""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    transposed = []
    for note in notes:
        pitch = note['pitch']

        note_part = ''.join(c for c in pitch if c.isalpha() or c == '#')
        octave = int(''.join(c for c in pitch if c.isdigit()))

        if note_part in note_names:
            current_index = note_names.index(note_part)
            total_semitones = (octave * 12) + current_index + semitones

            new_octave = total_semitones // 12
            new_note_index = total_semitones % 12
            new_pitch = f"{note_names[new_note_index]}{new_octave}"

            new_note = copy.deepcopy(note)
            new_note['pitch'] = new_pitch
            new_note['midi_note'] = total_semitones + 12
            transposed.append(new_note)

    return transposed


def scale_tempo(structure: dict, tempo_scale: float) -> dict:
    """Scale tempo by multiplying BPM."""
    if 'tempo' in structure:
        structure['tempo'] = int(structure['tempo'] * tempo_scale)
    return structure


def extend_duration(structure: dict, target_seconds: float) -> dict:
    """Extend composition to target duration by repeating patterns."""
    current_duration = structure.get('length_seconds', 0)

    if current_duration >= target_seconds:
        return structure

    repetitions_needed = int((target_seconds / current_duration) + 1) if current_duration > 0 else 1

    for track_id, track in structure.get('tracks', {}).items():
        original_notes = track['notes']
        extended_notes = []

        for rep in range(repetitions_needed):
            time_offset = rep * current_duration
            for note in original_notes:
                new_note = copy.deepcopy(note)
                new_note['start'] = note['start'] + time_offset
                extended_notes.append(new_note)

        track['notes'] = extended_notes

    structure['length_seconds'] = target_seconds
    return structure


def swap_instrument(structure: dict, from_inst: str, to_inst: str) -> dict:
    """Swap instrument in all tracks."""
    instrument_map = {
        "piano": 0, "bright_piano": 1, "electric_piano": 4,
        "acoustic_guitar": 24, "electric_guitar": 27, "bass": 32,
        "violin": 40, "viola": 41, "cello": 42, "contrabass": 43,
        "harp": 46, "timpani": 47,
        "trumpet": 56, "trombone": 57, "tuba": 58, "french_horn": 60,
        "oboe": 68, "bassoon": 70, "clarinet": 71, "flute": 73,
    }

    for track_id, track in structure.get('tracks', {}).items():
        if track.get('instrument') == from_inst:
            track['instrument'] = to_inst
            if to_inst in instrument_map:
                track['midi_program'] = instrument_map[to_inst]

    return structure


def loop_section(structure: dict, start_time: float, end_time: float, repetitions: int) -> dict:
    """Loop a time section multiple times."""
    for track_id, track in structure.get('tracks', {}).items():
        section_notes = [n for n in track['notes'] if start_time <= n['start'] < end_time]
        section_duration = end_time - start_time

        looped_notes = []
        for rep in range(repetitions):
            time_offset = end_time + (rep * section_duration)
            for note in section_notes:
                new_note = copy.deepcopy(note)
                new_note['start'] = (note['start'] - start_time) + time_offset
                looped_notes.append(new_note)

        track['notes'].extend(looped_notes)
        track['notes'].sort(key=lambda n: n['start'])

    if 'length_seconds' in structure:
        structure['length_seconds'] += section_duration * repetitions

    return structure


def reverse_composition(structure: dict) -> dict:
    """Reverse the entire composition."""
    total_duration = structure.get('length_seconds', 0)

    for track_id, track in structure.get('tracks', {}).items():
        for note in track['notes']:
            note['start'] = total_duration - note['start'] - note['duration']

        track['notes'].sort(key=lambda n: n['start'])

    return structure


def main():
    parser = argparse.ArgumentParser(
        description="Transform MIDI structure JSON with various operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python midi_transform.py input.json output.json --transpose 2
    Transpose all notes up by 2 semitones (whole step)

  python midi_transform.py input.json output.json --tempo-scale 1.5
    Speed up by 50% (120 BPM → 180 BPM)

  python midi_transform.py input.json output.json --extend-to 90
    Extend composition to 90 seconds by repeating patterns

  python midi_transform.py input.json output.json --swap-instrument violin cello
    Change all violin tracks to cello

  python midi_transform.py input.json output.json --transpose 2 --tempo-scale 1.2
    Combine multiple transformations

  python midi_transform.py input.json output.json --loop-section 10 20 3
    Loop the section from 10s-20s three times

  python midi_transform.py input.json output.json --reverse
    Reverse the entire composition
        """
    )

    parser.add_argument("input", help="Input JSON structure file")
    parser.add_argument("output", help="Output JSON structure file")
    parser.add_argument("--transpose", type=int, help="Transpose by N semitones")
    parser.add_argument("--tempo-scale", type=float, help="Multiply tempo by factor")
    parser.add_argument("--extend-to", type=float, help="Extend to N seconds")
    parser.add_argument("--swap-instrument", nargs=2, metavar=('FROM', 'TO'),
                        help="Swap instrument (e.g., violin cello)")
    parser.add_argument("--loop-section", nargs=3, type=float,
                        metavar=('START', 'END', 'TIMES'),
                        help="Loop section from START to END for TIMES repetitions")
    parser.add_argument("--reverse", action='store_true', help="Reverse composition")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    try:
        print(f"Loading structure from: {args.input}")
        with open(input_path, 'r') as f:
            structure = json.load(f)

        if args.transpose:
            print(f"Transposing by {args.transpose} semitones...")
            for track_id, track in structure.get('tracks', {}).items():
                track['notes'] = transpose_notes(track['notes'], args.transpose)

        if args.tempo_scale:
            print(f"Scaling tempo by {args.tempo_scale}x...")
            structure = scale_tempo(structure, args.tempo_scale)

        if args.extend_to:
            print(f"Extending to {args.extend_to} seconds...")
            structure = extend_duration(structure, args.extend_to)

        if args.swap_instrument:
            from_inst, to_inst = args.swap_instrument
            print(f"Swapping {from_inst} → {to_inst}...")
            structure = swap_instrument(structure, from_inst, to_inst)

        if args.loop_section:
            start, end, times = args.loop_section
            print(f"Looping section {start}s-{end}s {int(times)} times...")
            structure = loop_section(structure, start, end, int(times))

        if args.reverse:
            print("Reversing composition...")
            structure = reverse_composition(structure)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(structure, f, indent=2)

        print(f"\nTransformation complete!")
        print(f"Output: {args.output}")

    except Exception as e:
        print(f"Error transforming structure: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()