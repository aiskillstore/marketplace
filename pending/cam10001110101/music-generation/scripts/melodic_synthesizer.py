"""
Real-time melodic synthesis for electronic music.

Synthesizes bass, pads, and leads with ADSR envelopes, filters,
and modulation. All parameters tunable for different genres.
"""
import numpy as np
from scipy import signal


def apply_adsr_envelope(
    audio: np.ndarray,
    attack=0.01,
    decay=0.1,
    sustain=0.7,
    release=0.2,
    sample_rate=44100
) -> np.ndarray:
    """
    Apply ADSR envelope to audio signal.

    Args:
        audio: Input audio array
        attack: Attack time in seconds
        decay: Decay time in seconds
        sustain: Sustain level (0-1)
        release: Release time in seconds
        sample_rate: Audio sample rate

    Returns:
        Audio with ADSR envelope applied
    """
    total_samples = len(audio)
    duration = total_samples / sample_rate

    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)

    total_adsr_samples = attack_samples + decay_samples + release_samples

    if total_adsr_samples > total_samples:
        scale_factor = total_samples / total_adsr_samples
        attack_samples = int(attack_samples * scale_factor)
        decay_samples = int(decay_samples * scale_factor)
        release_samples = int(release_samples * scale_factor)

    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    sustain_samples = max(sustain_samples, 0)

    envelope = np.zeros(total_samples)

    attack_end = min(attack_samples, total_samples)
    if attack_end > 0:
        envelope[:attack_end] = np.linspace(0, 1, attack_end)

    decay_start = attack_end
    decay_end = min(decay_start + decay_samples, total_samples)
    if decay_end > decay_start:
        envelope[decay_start:decay_end] = np.linspace(1, sustain, decay_end - decay_start)

    sustain_start = decay_end
    sustain_end = min(sustain_start + sustain_samples, total_samples)
    if sustain_end > sustain_start:
        envelope[sustain_start:sustain_end] = sustain

    release_start = sustain_end
    remaining_samples = total_samples - release_start
    if remaining_samples > 0:
        envelope[release_start:] = np.linspace(sustain, 0, remaining_samples)

    return audio * envelope


def apply_lowpass_filter(
    audio: np.ndarray,
    cutoff_hz=1000,
    resonance=0.5,
    sample_rate=44100
) -> np.ndarray:
    """
    Apply low-pass filter with resonance.

    Args:
        audio: Input audio array
        cutoff_hz: Cutoff frequency in Hz
        resonance: Filter resonance (0-1)
        sample_rate: Audio sample rate

    Returns:
        Filtered audio
    """
    nyquist = sample_rate / 2
    normalized_cutoff = cutoff_hz / nyquist

    normalized_cutoff = np.clip(normalized_cutoff, 0.01, 0.99)

    order = 2 + int(resonance * 2)

    b, a = signal.butter(order, normalized_cutoff, btype='low')

    filtered = signal.filtfilt(b, a, audio)

    return filtered


def apply_highpass_filter(
    audio: np.ndarray,
    cutoff_hz=200,
    sample_rate=44100
) -> np.ndarray:
    """
    Apply high-pass filter to remove low frequencies.

    Args:
        audio: Input audio array
        cutoff_hz: Cutoff frequency in Hz
        sample_rate: Audio sample rate

    Returns:
        Filtered audio
    """
    nyquist = sample_rate / 2
    normalized_cutoff = cutoff_hz / nyquist

    normalized_cutoff = np.clip(normalized_cutoff, 0.01, 0.99)

    b, a = signal.butter(2, normalized_cutoff, btype='high')

    filtered = signal.filtfilt(b, a, audio)

    return filtered


def synthesize_bass_note(
    frequency=55.0,
    duration=1.0,
    waveform='sawtooth',
    cutoff=200,
    resonance=0.6,
    attack=0.01,
    decay=0.15,
    sustain=0.7,
    release=0.2,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize a synth bass note.

    Args:
        frequency: Note frequency in Hz (A1 = 55Hz)
        duration: Note duration in seconds
        waveform: 'sawtooth', 'square', or 'sine'
        cutoff: Low-pass filter cutoff in Hz
        resonance: Filter resonance (0-1)
        attack: ADSR attack time
        decay: ADSR decay time
        sustain: ADSR sustain level (0-1)
        release: ADSR release time
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))

    if waveform == 'sawtooth':
        oscillator = signal.sawtooth(2 * np.pi * frequency * t)
    elif waveform == 'square':
        oscillator = signal.square(2 * np.pi * frequency * t)
    elif waveform == 'sine':
        oscillator = np.sin(2 * np.pi * frequency * t)
    else:
        oscillator = signal.sawtooth(2 * np.pi * frequency * t)

    if frequency < 60:
        sub_bass_mix = 0.0
    elif frequency < 100:
        sub_bass_mix = 0.05
    elif frequency < 150:
        sub_bass_mix = 0.1
    else:
        sub_bass_mix = 0.15

    if sub_bass_mix > 0:
        sub_bass = np.sin(2 * np.pi * (frequency / 2) * t)
        bass_signal = oscillator * (1.0 - sub_bass_mix) + sub_bass * sub_bass_mix
    else:
        bass_signal = oscillator

    bass = apply_lowpass_filter(bass_signal, cutoff, resonance, sample_rate)

    bass = apply_adsr_envelope(bass, attack, decay, sustain, release, sample_rate)

    bass = np.tanh(bass * 1.2) / 1.2

    bass = bass / np.max(np.abs(bass)) * 0.5

    return (bass * 32767).astype(np.int16)


def synthesize_pad_chord(
    frequencies: list[float],
    duration=4.0,
    attack=0.8,
    release=1.0,
    brightness=0.4,
    detune=0.03,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize an atmospheric pad chord.

    Args:
        frequencies: List of note frequencies in Hz (e.g., [220, 261.63, 329.63] for Am)
        duration: Chord duration in seconds
        attack: Slow attack time for pad character
        release: Release time
        brightness: Filter brightness (0=dark, 1=bright)
        detune: Detuning amount for chorus effect (0-0.1)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))

    pad = np.zeros(len(t))

    detune_amounts = [-0.02, 0, 0.02]
    phase_offsets = [0, 0, 0.3]

    for freq in frequencies:
        for detune_amt, phase_offset in zip(detune_amounts, phase_offsets):
            phase = 2 * np.pi * freq * (1 + detune_amt * detune) * t + phase_offset
            osc = np.sin(phase)
            pad += osc

    pad = pad / (len(frequencies) * len(detune_amounts))

    pad = apply_highpass_filter(pad, cutoff_hz=200, sample_rate=sample_rate)

    cutoff = 400 + brightness * 1000
    pad = apply_lowpass_filter(pad, cutoff, resonance=0.2, sample_rate=sample_rate)

    sustain = 0.7
    pad = apply_adsr_envelope(pad, attack, 0.1, sustain, release, sample_rate)

    pad = np.tanh(pad * 1.0) / 1.0

    pad = pad / np.max(np.abs(pad)) * 0.35

    return (pad * 32767).astype(np.int16)


def synthesize_lead_note(
    frequency=440.0,
    duration=0.5,
    brightness=0.8,
    attack=0.005,
    decay=0.1,
    sustain=0.6,
    release=0.1,
    portamento=0.0,
    unison_voices=7,
    unison_detune=0.12,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize a synth lead note with supersaw (multiple detuned oscillators).

    Args:
        frequency: Note frequency in Hz (A4 = 440Hz)
        duration: Note duration in seconds
        brightness: Filter brightness (0=dark, 1=bright)
        attack: Fast attack for plucky character
        decay: Decay time
        sustain: Sustain level (0-1)
        release: Release time
        portamento: Pitch glide time (0=none)
        unison_voices: Number of detuned voices (1=single osc, 7=supersaw)
        unison_detune: Detune amount in semitones (0.12 = ±12 cents)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))

    if unison_voices == 1:
        if portamento > 0:
            freq_start = frequency * 0.9
            portamento_samples = int(portamento * sample_rate)
            freq_curve = np.ones(len(t)) * frequency
            freq_curve[:portamento_samples] = np.linspace(
                freq_start, frequency, portamento_samples
            )
            phase = 2 * np.pi * np.cumsum(freq_curve) / sample_rate
            oscillator = signal.sawtooth(phase)
        else:
            oscillator = signal.sawtooth(2 * np.pi * frequency * t)
    else:
        supersaw = np.zeros(len(t))

        detune_range = unison_detune
        detune_step = (2 * detune_range) / max(1, unison_voices - 1)

        for voice_idx in range(unison_voices):
            detune_semitones = -detune_range + (voice_idx * detune_step)
            detune_ratio = 2 ** (detune_semitones / 12)
            detuned_freq = frequency * detune_ratio

            phase_offset = (voice_idx * 0.15) % (2 * np.pi)

            if portamento > 0:
                freq_start = detuned_freq * 0.9
                portamento_samples = int(portamento * sample_rate)
                freq_curve = np.ones(len(t)) * detuned_freq
                freq_curve[:portamento_samples] = np.linspace(
                    freq_start, detuned_freq, portamento_samples
                )
                phase = 2 * np.pi * np.cumsum(freq_curve) / sample_rate + phase_offset
                voice = signal.sawtooth(phase)
            else:
                voice = signal.sawtooth(2 * np.pi * detuned_freq * t + phase_offset)

            supersaw += voice

        oscillator = supersaw / unison_voices

    cutoff = 300 + brightness * 1200
    lead = apply_lowpass_filter(oscillator, cutoff, resonance=0.4, sample_rate=sample_rate)

    lead = apply_adsr_envelope(lead, attack, decay, sustain, release, sample_rate)

    if unison_voices > 1:
        lead = np.tanh(lead * 2.5) / 2.0
    else:
        lead = np.tanh(lead * 1.5) / 1.5

    lead = lead / np.max(np.abs(lead)) * 0.65

    return (lead * 32767).astype(np.int16)


def midi_note_to_frequency(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def frequency_to_note_name(frequency: float) -> str:
    """Convert frequency to nearest note name for debugging."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    midi_note = int(69 + 12 * np.log2(frequency / 440.0))
    octave = (midi_note // 12) - 1
    note = notes[midi_note % 12]
    return f"{note}{octave}"


def get_frequency_compensation_db(frequency: float, instrument_type: str = "bass") -> float:
    """
    Calculate frequency-aware volume compensation in dB.

    Lower frequencies naturally have more perceived energy and should be reduced.
    Higher frequencies can be boosted for clarity.

    Args:
        frequency: Frequency in Hz
        instrument_type: Type of instrument ('bass', 'pad', 'lead')

    Returns:
        Compensation in dB (negative for reduction, positive for boost)
    """
    if instrument_type == "bass":
        if frequency < 40:
            return -9.0
        elif frequency < 60:
            return -7.0
        elif frequency < 100:
            return -5.0
        elif frequency < 150:
            return -3.0
        elif frequency < 250:
            return -1.5
        else:
            return 0.0

    elif instrument_type == "pad":
        if frequency < 120:
            return -4.0
        elif frequency < 200:
            return -3.0
        elif frequency < 300:
            return -2.0
        elif frequency < 500:
            return -1.0
        elif frequency > 1000:
            return 1.0
        else:
            return 0.0

    elif instrument_type == "lead":
        if frequency < 200:
            return -1.0
        elif frequency > 800:
            return 1.5
        elif frequency > 500:
            return 0.5
        else:
            return 0.0

    return 0.0


def velocity_to_db(velocity: int, curve: str = "linear") -> float:
    """
    Convert MIDI velocity (0-127) to dB adjustment with proper curve.

    Args:
        velocity: MIDI velocity (0-127)
        curve: Response curve ('linear', 'exponential', 'logarithmic')

    Returns:
        Volume adjustment in dB
    """
    normalized = velocity / 127.0

    if curve == "exponential":
        response = normalized ** 2
        return (response - 0.5) * 12

    elif curve == "logarithmic":
        response = np.log1p(normalized * 2) / np.log1p(2)
        return (response - 0.5) * 10

    else:
        return (velocity - 90) * 0.15