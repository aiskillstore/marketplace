import os

from mido import Message, MetaMessage, MidiFile, MidiTrack


def get_midi_bpm(midi_path: str) -> int:
    """Extract BPM from MIDI file, default to 120 if not found."""
    mid = MidiFile(midi_path)

    for track in mid.tracks:
        for msg in track:
            if msg.type == "set_tempo":
                return int(60_000_000 / msg.tempo)

    return 120


def get_midi_duration_ms(midi_path: str) -> int:
    """Calculate total duration of MIDI file in milliseconds."""
    mid = MidiFile(midi_path)

    total_ticks = 0
    for track in mid.tracks:
        track_ticks = sum(msg.time for msg in track)
        total_ticks = max(total_ticks, track_ticks)

    bpm = get_midi_bpm(midi_path)
    seconds_per_tick = 60 / (bpm * mid.ticks_per_beat)
    total_seconds = total_ticks * seconds_per_tick

    return int(total_seconds * 1000)


def extract_drum_events(midi_path: str) -> list[dict]:
    """
    Extract all drum events (channel 9/10) from MIDI file.
    Returns list of dicts with: time_ms, note, velocity
    """
    mid = MidiFile(midi_path)
    bpm = get_midi_bpm(midi_path)
    seconds_per_tick = 60 / (bpm * mid.ticks_per_beat)

    events = []

    for track in mid.tracks:
        current_time_ticks = 0

        for msg in track:
            current_time_ticks += msg.time

            if msg.type == "note_on" and msg.channel == 9 and msg.velocity > 0:
                time_ms = int(current_time_ticks * seconds_per_tick * 1000)
                events.append(
                    {"time_ms": time_ms, "note": msg.note, "velocity": msg.velocity}
                )

    return events


def strip_channel(midi_path: str, channel: int, output_path: str = None) -> str:
    """
    Remove all events from a specific MIDI channel.
    Returns path to new MIDI file without that channel.
    """
    if output_path is None:
        base, ext = os.path.splitext(midi_path)
        output_path = f"{base}_no_ch{channel}{ext}"

    mid = MidiFile(midi_path)
    new_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)

    for track in mid.tracks:
        new_track = MidiTrack()

        for msg in track:
            if not hasattr(msg, "channel") or msg.channel != channel:
                new_track.append(msg.copy())

        if len(new_track) > 0:
            new_mid.tracks.append(new_track)

    new_mid.save(output_path)
    return output_path


def extract_drum_channel(midi_path: str, output_path: str = None) -> str:
    """
    Extract ONLY drum channel (9) from MIDI file.
    Returns path to drums-only MIDI file.
    """
    if output_path is None:
        base, ext = os.path.splitext(midi_path)
        output_path = f"{base}_drums_only{ext}"

    mid = MidiFile(midi_path)
    new_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)

    tempo_track = MidiTrack()
    for track in mid.tracks:
        for msg in track:
            if msg.type == "set_tempo":
                tempo_track.append(msg.copy())

    if len(tempo_track) > 0:
        new_mid.tracks.append(tempo_track)

    for track in mid.tracks:
        new_track = MidiTrack()

        for msg in track:
            if hasattr(msg, "channel") and msg.channel == 9:
                new_track.append(msg.copy())
            elif msg.type in ["track_name", "end_of_track"]:
                new_track.append(msg.copy())

        if any(msg.type == "note_on" for msg in new_track):
            new_mid.tracks.append(new_track)

    new_mid.save(output_path)
    return output_path
