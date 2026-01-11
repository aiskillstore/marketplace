#!/usr/bin/env python3
"""
Electronic Music Renderer with Real-Time Synthesis

Renders MIDI files using pure synthesis - no external samples or soundfonts needed.
Synthesizes drums, bass, pads, and leads on-the-fly for authentic electronic sound.

Usage:
    python render_electronic.py input.mid output.mp3
    python render_electronic.py input.mid output.mp3 --genre deep_house
    python render_electronic.py input.mid output.mp3 --preset custom_params.json
"""
import sys
import os
import argparse
import json
from pathlib import Path
from pydub import AudioSegment
import numpy as np

from midi_utils import (
    extract_drum_events,
    get_midi_duration_ms,
    get_midi_bpm
)
from drum_synthesizer import (
    synthesize_kick,
    synthesize_snare,
    synthesize_hat_closed,
    synthesize_hat_open,
    synthesize_clap,
    synthesize_rim
)
from melodic_synthesizer import (
    synthesize_bass_note,
    synthesize_pad_chord,
    synthesize_lead_note,
    midi_note_to_frequency,
    get_frequency_compensation_db,
    velocity_to_db
)
from synthesis_presets import get_preset, list_genres


DRUM_SYNTH_MAP = {
    35: 'kick',
    36: 'kick',
    37: 'rim',
    38: 'snare',
    39: 'clap',
    40: 'snare',
    42: 'hat_closed',
    44: 'hat_closed',
    46: 'hat_open',
}


def synthesize_drum_sample(drum_type: str, params: dict, sample_rate=44100) -> np.ndarray:
    """
    Synthesize a drum sample based on type and parameters.

    Args:
        drum_type: Type of drum ('kick', 'snare', 'hat_closed', etc.)
        params: Synthesis parameters from preset
        sample_rate: Audio sample rate

    Returns:
        Audio array (16-bit PCM)
    """
    if drum_type == 'kick':
        return synthesize_kick(**params, sample_rate=sample_rate)
    elif drum_type == 'snare':
        return synthesize_snare(**params, sample_rate=sample_rate)
    elif drum_type == 'hat_closed':
        return synthesize_hat_closed(**params, sample_rate=sample_rate)
    elif drum_type == 'hat_open':
        return synthesize_hat_open(**params, sample_rate=sample_rate)
    elif drum_type == 'clap':
        return synthesize_clap(**params, sample_rate=sample_rate)
    elif drum_type == 'rim':
        return synthesize_rim(**params, sample_rate=sample_rate)
    else:
        return synthesize_kick(sample_rate=sample_rate)


def render_drums_synthesized(
    drum_events: list[dict],
    total_duration_ms: int,
    preset: dict,
    sample_rate=44100
) -> AudioSegment:
    """
    Render drum track using real-time synthesis.

    Args:
        drum_events: List of drum events from MIDI
        total_duration_ms: Total duration in milliseconds
        preset: Genre preset with drum parameters
        sample_rate: Audio sample rate

    Returns:
        Mixed drum audio
    """
    drum_audio = AudioSegment.silent(duration=total_duration_ms)

    drum_params = preset.get('drums', {})
    volume_balance = preset.get('volume_balance', {})
    base_drum_level = volume_balance.get('drums', 0.0)
    velocity_curve = volume_balance.get('velocity_curve', 'linear')

    for event in drum_events:
        drum_type = DRUM_SYNTH_MAP.get(event['note'])
        if drum_type is None:
            continue

        params = drum_params.get(drum_type, {})

        try:
            sample_array = synthesize_drum_sample(drum_type, params, sample_rate)

            sample = AudioSegment(
                sample_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )

            velocity = event['velocity']
            velocity_db = velocity_to_db(velocity, velocity_curve)
            total_volume_db = base_drum_level + velocity_db
            sample = sample + total_volume_db

            position_ms = event['time_ms']
            drum_audio = drum_audio.overlay(sample, position=position_ms)

        except Exception as e:
            print(f"Warning: Could not synthesize {drum_type} at {event['time_ms']}ms: {e}")

    return drum_audio


def extract_melodic_events(midi_path: str) -> dict:
    """
    Extract melodic events (bass, pads, leads) from MIDI file.

    Returns:
        Dictionary with 'bass', 'pad', 'lead' keys, each containing note events
    """
    from mido import MidiFile

    mid = MidiFile(midi_path)
    bpm = get_midi_bpm(midi_path)
    seconds_per_tick = 60 / (bpm * mid.ticks_per_beat)

    melodic_events = {
        'bass': [],
        'pad': [],
        'lead': []
    }

    for i, track in enumerate(mid.tracks):
        if i == 0:
            continue

        current_time_ticks = 0
        track_program = 0
        track_channel = 0
        active_notes = {}

        for msg in track:
            current_time_ticks += msg.time

            if msg.type == 'program_change':
                track_program = msg.program
                track_channel = msg.channel

            elif msg.type == 'note_on' and msg.channel != 9:
                time_ms = int(current_time_ticks * seconds_per_tick * 1000)

                if msg.velocity > 0:
                    note_key = msg.note
                    active_notes[note_key] = {
                        'start_ms': time_ms,
                        'velocity': msg.velocity,
                        'program': track_program
                    }
                else:
                    note_key = msg.note
                    if note_key in active_notes:
                        note_info = active_notes.pop(note_key)
                        duration_ms = time_ms - note_info['start_ms']

                        if duration_ms < 50:
                            duration_ms = 2000

                        if 32 <= note_info['program'] <= 39:
                            instrument_type = 'bass'
                        elif 80 <= note_info['program'] <= 87:
                            instrument_type = 'lead'
                        elif 88 <= note_info['program'] <= 95:
                            instrument_type = 'pad'
                        elif 0 <= note_info['program'] <= 7:
                            instrument_type = 'lead'
                        else:
                            instrument_type = 'pad'

                        melodic_events[instrument_type].append({
                            'time_ms': note_info['start_ms'],
                            'note': note_key,
                            'velocity': note_info['velocity'],
                            'duration_ms': duration_ms
                        })

            elif msg.type == 'note_off' and msg.channel != 9:
                time_ms = int(current_time_ticks * seconds_per_tick * 1000)
                note_key = msg.note

                if note_key in active_notes:
                    note_info = active_notes.pop(note_key)
                    duration_ms = time_ms - note_info['start_ms']

                    if duration_ms < 50:
                        duration_ms = 2000

                    if 32 <= note_info['program'] <= 39:
                        instrument_type = 'bass'
                    elif 80 <= note_info['program'] <= 87:
                        instrument_type = 'lead'
                    elif 88 <= note_info['program'] <= 95:
                        instrument_type = 'pad'
                    elif 0 <= note_info['program'] <= 7:
                        instrument_type = 'lead'
                    else:
                        instrument_type = 'pad'

                    melodic_events[instrument_type].append({
                        'time_ms': note_info['start_ms'],
                        'note': note_key,
                        'velocity': note_info['velocity'],
                        'duration_ms': duration_ms
                    })

        for note_key, note_info in active_notes.items():
            duration_ms = 2000

            if 32 <= note_info['program'] <= 39:
                instrument_type = 'bass'
            elif 80 <= note_info['program'] <= 87:
                instrument_type = 'lead'
            elif 88 <= note_info['program'] <= 95:
                instrument_type = 'pad'
            elif 0 <= note_info['program'] <= 7:
                instrument_type = 'lead'
            else:
                instrument_type = 'pad'

            melodic_events[instrument_type].append({
                'time_ms': note_info['start_ms'],
                'note': note_key,
                'velocity': note_info['velocity'],
                'duration_ms': duration_ms
            })

    return melodic_events


def render_melodic_synthesized(
    melodic_events: dict,
    total_duration_ms: int,
    preset: dict,
    sample_rate=44100
) -> AudioSegment:
    """
    Render melodic parts (bass, pads, leads) using synthesis.

    Args:
        melodic_events: Dictionary of melodic note events
        total_duration_ms: Total duration in milliseconds
        preset: Genre preset with melodic parameters
        sample_rate: Audio sample rate

    Returns:
        Mixed melodic audio
    """
    melodic_audio = AudioSegment.silent(duration=total_duration_ms)

    volume_balance = preset.get('volume_balance', {})
    base_bass_level = volume_balance.get('bass', 0.0)
    base_lead_level = volume_balance.get('lead', 0.0)
    base_pad_level = volume_balance.get('pad', 0.0)
    velocity_curve = volume_balance.get('velocity_curve', 'linear')

    bass_params = preset.get('bass', {})
    for event in melodic_events.get('bass', []):
        try:
            frequency = midi_note_to_frequency(event['note'])
            duration = event['duration_ms'] / 1000.0

            bass_array = synthesize_bass_note(
                frequency=frequency,
                duration=duration,
                **bass_params,
                sample_rate=sample_rate
            )

            bass_segment = AudioSegment(
                bass_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )

            velocity = event['velocity']
            velocity_db = velocity_to_db(velocity, velocity_curve)
            frequency_comp = get_frequency_compensation_db(frequency, "bass")
            total_volume_db = base_bass_level + velocity_db + frequency_comp
            bass_segment = bass_segment + total_volume_db

            position_ms = event['time_ms']
            melodic_audio = melodic_audio.overlay(bass_segment, position=position_ms)

        except Exception as e:
            print(f"Warning: Could not synthesize bass note at {event['time_ms']}ms: {e}")

    lead_params = preset.get('lead', {})
    for event in melodic_events.get('lead', []):
        try:
            frequency = midi_note_to_frequency(event['note'])
            duration = event['duration_ms'] / 1000.0

            lead_array = synthesize_lead_note(
                frequency=frequency,
                duration=duration,
                **lead_params,
                sample_rate=sample_rate
            )

            lead_segment = AudioSegment(
                lead_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )

            velocity = event['velocity']
            velocity_db = velocity_to_db(velocity, velocity_curve)
            frequency_comp = get_frequency_compensation_db(frequency, "lead")
            total_volume_db = base_lead_level + velocity_db + frequency_comp
            lead_segment = lead_segment + total_volume_db

            position_ms = event['time_ms']
            melodic_audio = melodic_audio.overlay(lead_segment, position=position_ms)

        except Exception as e:
            print(f"Warning: Could not synthesize lead note at {event['time_ms']}ms: {e}")

    pad_params = preset.get('pad', {})
    for event in melodic_events.get('pad', []):
        try:
            frequency = midi_note_to_frequency(event['note'])
            duration = event['duration_ms'] / 1000.0

            pad_array = synthesize_pad_chord(
                frequencies=[frequency],
                duration=duration,
                **pad_params,
                sample_rate=sample_rate
            )

            pad_segment = AudioSegment(
                pad_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )

            velocity = event['velocity']
            velocity_db = velocity_to_db(velocity, velocity_curve)
            frequency_comp = get_frequency_compensation_db(frequency, "pad")
            total_volume_db = base_pad_level + velocity_db + frequency_comp
            pad_segment = pad_segment + total_volume_db

            position_ms = event['time_ms']
            melodic_audio = melodic_audio.overlay(pad_segment, position=position_ms)

        except Exception as e:
            print(f"Warning: Could not synthesize pad note at {event['time_ms']}ms: {e}")

    return melodic_audio


def render_electronic(
    midi_path: str,
    output_path: str,
    genre: str = "default",
    custom_preset: dict = None
) -> str:
    """
    Render MIDI file using electronic music synthesis pipeline.

    Args:
        midi_path: Path to input MIDI file
        output_path: Path for output MP3 file
        genre: Genre preset name (e.g., "deep_house", "techno")
        custom_preset: Optional custom preset dictionary

    Returns:
        Path to rendered MP3 file
    """
    midi_path = str(Path(midi_path).resolve())
    output_path = str(Path(output_path).resolve())

    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    if custom_preset:
        preset = custom_preset
        print(f"Using custom preset")
    else:
        preset = get_preset(genre)
        print(f"Using '{genre}' preset")

    print(f"Rendering electronic music: {os.path.basename(midi_path)}")

    bpm = get_midi_bpm(midi_path)
    total_duration_ms = get_midi_duration_ms(midi_path)

    print(f"  BPM: {bpm}")
    print(f"  Duration: {total_duration_ms / 1000:.1f}s")

    print("  Step 1/3: Synthesizing drums...")
    drum_events = extract_drum_events(midi_path)
    print(f"    Found {len(drum_events)} drum hits")
    drum_audio = render_drums_synthesized(drum_events, total_duration_ms, preset)

    print("  Step 2/3: Synthesizing melodic parts (bass, pads, leads)...")
    melodic_events = extract_melodic_events(midi_path)
    total_melodic = sum(len(events) for events in melodic_events.values())
    print(f"    Found {total_melodic} melodic notes")
    melodic_audio = render_melodic_synthesized(melodic_events, total_duration_ms, preset)

    print("  Step 3/3: Mixing and exporting...")
    final_audio = drum_audio.overlay(melodic_audio)

    max_db = final_audio.max_dBFS
    if max_db > -1.0:
        headroom_db = -1.0 - max_db
        print(f"    Applying limiter: reducing {-headroom_db:.1f} dB to prevent clipping")
        final_audio = final_audio + headroom_db

    final_audio.export(output_path, format='mp3', bitrate='192k')

    print(f"✓ Electronic music rendering complete!")
    print(f"  Output: {output_path}")

    return output_path


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Render MIDI files with real-time electronic music synthesis'
    )
    parser.add_argument(
        'input',
        help='Input MIDI file path'
    )
    parser.add_argument(
        'output',
        help='Output MP3 file path'
    )
    parser.add_argument(
        '--genre',
        default='default',
        choices=list_genres(),
        help='Genre preset to use (default: default)'
    )
    parser.add_argument(
        '--preset',
        help='Path to custom preset JSON file'
    )
    parser.add_argument(
        '--list-genres',
        action='store_true',
        help='List available genre presets and exit'
    )

    args = parser.parse_args()

    if args.list_genres:
        print("Available genre presets:")
        for genre in list_genres():
            preset = get_preset(genre)
            desc = preset.get('description', '')
            print(f"  {genre}: {desc}")
        return 0

    try:
        custom_preset = None
        if args.preset:
            with open(args.preset, 'r') as f:
                custom_preset = json.load(f)

        render_electronic(args.input, args.output, args.genre, custom_preset)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())