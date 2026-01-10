"""
Real-time drum synthesis for electronic music.

Synthesizes 808-style kicks, snares, hi-hats, and other percussion
on-the-fly without requiring external samples. All parameters are tunable
for different genres and styles.
"""
import numpy as np
from scipy import signal
from scipy.io import wavfile


def synthesize_kick(
    pitch=56.0,
    decay=0.5,
    punch=0.8,
    click_level=0.3,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize an 808-style kick drum.

    Args:
        pitch: Fundamental frequency in Hz (808 default: 56Hz)
        decay: Decay time in seconds (shorter = tighter)
        punch: Amount of pitch sweep (0-1, higher = more punch)
        click_level: Attack click amount (0-1)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    duration = max(decay * 2, 0.5)
    t = np.linspace(0, duration, int(sample_rate * duration))

    freq_start = pitch * (1 + punch * 3)
    freq_end = pitch
    freq = np.linspace(freq_start, freq_end, len(t))

    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    body = np.sin(phase)

    envelope_body = np.exp(-8 * t / decay)
    body = body * envelope_body

    click_freq = 2000
    click = np.sin(2 * np.pi * click_freq * t)
    envelope_click = np.exp(-100 * t)
    click = click * envelope_click * click_level

    kick = body + click

    kick = kick / np.max(np.abs(kick)) * 0.85

    return (kick * 32767).astype(np.int16)


def synthesize_snare(
    tone_mix=0.3,
    pitch=200.0,
    snap=0.7,
    decay=0.25,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize an electronic snare drum.

    Args:
        tone_mix: Balance between tone and noise (0=pure noise, 1=pure tone)
        pitch: Fundamental frequency of tone in Hz
        snap: Brightness/sharpness of attack (0-1)
        decay: Decay time in seconds
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    duration = max(decay * 2, 0.3)
    t = np.linspace(0, duration, int(sample_rate * duration))

    pink_noise = np.random.randn(len(t))
    b, a = signal.butter(1, 0.5, btype='high')
    noise = signal.filtfilt(b, a, pink_noise)

    tone1 = np.sin(2 * np.pi * pitch * t)
    tone2 = np.sin(2 * np.pi * (pitch * 1.3) * t)
    tone = (tone1 + tone2 * 0.7) / 1.7

    snare = noise * (1 - tone_mix) + tone * tone_mix

    envelope = np.exp(-10 * t / decay)
    snare = snare * envelope

    if snap > 0:
        attack = np.exp(-80 * t) * snap
        snare = snare + attack * np.random.randn(len(t)) * 0.5

    snare = snare / np.max(np.abs(snare)) * 0.7

    return (snare * 32767).astype(np.int16)


def synthesize_hat_closed(
    brightness=0.7,
    decay=0.12,
    metallic=0.5,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize a closed hi-hat.

    Args:
        brightness: Frequency content (0=dark, 1=bright)
        decay: Decay time in seconds
        metallic: Amount of metallic overtones (0-1)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    duration = max(decay * 2, 0.15)
    t = np.linspace(0, duration, int(sample_rate * duration))

    noise = np.random.randn(len(t))

    cutoff_low = 0.2 + brightness * 0.3
    cutoff_high = 0.5 + brightness * 0.4
    b, a = signal.butter(2, [cutoff_low, cutoff_high], btype='band')
    hat = signal.filtfilt(b, a, noise)

    if metallic > 0:
        freqs = [8000, 10500, 13000, 15500]
        for freq in freqs:
            metallic_tone = np.sin(2 * np.pi * freq * t)
            hat = hat + metallic_tone * metallic * 0.1

    envelope = np.exp(-50 * t / decay)
    hat = hat * envelope

    hat = hat / np.max(np.abs(hat)) * 0.45

    return (hat * 32767).astype(np.int16)


def synthesize_hat_open(
    brightness=0.8,
    decay=0.4,
    metallic=0.6,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize an open hi-hat.

    Args:
        brightness: Frequency content (0=dark, 1=bright)
        decay: Decay time in seconds (longer than closed)
        metallic: Amount of metallic overtones (0-1)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    duration = max(decay * 1.5, 0.4)
    t = np.linspace(0, duration, int(sample_rate * duration))

    noise = np.random.randn(len(t))

    cutoff_low = 0.25 + brightness * 0.25
    cutoff_high = 0.6 + brightness * 0.3
    b, a = signal.butter(2, [cutoff_low, cutoff_high], btype='band')
    hat = signal.filtfilt(b, a, noise)

    if metallic > 0:
        freqs = [7500, 9000, 11000, 13500]
        for freq in freqs:
            metallic_tone = np.sin(2 * np.pi * freq * t)
            hat = hat + metallic_tone * metallic * 0.12

    envelope = np.exp(-8 * t / decay)
    hat = hat * envelope

    hat = hat / np.max(np.abs(hat)) * 0.4

    return (hat * 32767).astype(np.int16)


def synthesize_clap(
    room_size=0.5,
    density=0.7,
    brightness=0.6,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize a hand clap.

    Args:
        room_size: Simulated room size (0=tight, 1=large)
        density: Number of clap layers (0=sparse, 1=dense)
        brightness: Frequency content (0=dark, 1=bright)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    duration = 0.2 + room_size * 0.3
    t = np.linspace(0, duration, int(sample_rate * duration))

    noise = np.random.randn(len(t))

    cutoff_low = 0.1 + brightness * 0.15
    cutoff_high = 0.3 + brightness * 0.3
    b, a = signal.butter(2, [cutoff_low, cutoff_high], btype='band')
    clap = signal.filtfilt(b, a, noise)

    burst_count = int(3 + density * 3)
    burst_times = [0.0]
    for i in range(1, burst_count):
        burst_times.append(0.005 + i * 0.008 * (1 - density * 0.5))

    envelope = np.zeros_like(t)
    for bt in burst_times:
        burst_env = np.exp(-100 * (t - bt))
        burst_env[t < bt] = 0
        envelope += burst_env

    clap = clap * envelope

    if room_size > 0:
        tail = np.exp(-15 * t) * room_size * 0.3
        clap = clap + tail * np.random.randn(len(t))

    clap = clap / np.max(np.abs(clap)) * 0.6

    return (clap * 32767).astype(np.int16)


def synthesize_rim(
    pitch=800.0,
    decay=0.08,
    click_mix=0.7,
    sample_rate=44100
) -> np.ndarray:
    """
    Synthesize a rim shot / side stick.

    Args:
        pitch: Resonant frequency in Hz
        decay: Decay time in seconds
        click_mix: Balance between click and tone (0=pure tone, 1=pure click)
        sample_rate: Audio sample rate

    Returns:
        16-bit mono audio array
    """
    duration = max(decay * 2, 0.1)
    t = np.linspace(0, duration, int(sample_rate * duration))

    tone = np.sin(2 * np.pi * pitch * t)
    envelope_tone = np.exp(-40 * t / decay)
    tone = tone * envelope_tone

    click = np.random.randn(len(t))
    b, a = signal.butter(1, 0.6, btype='high')
    click = signal.filtfilt(b, a, click)
    envelope_click = np.exp(-100 * t)
    click = click * envelope_click

    rim = tone * (1 - click_mix) + click * click_mix

    rim = rim / np.max(np.abs(rim)) * 0.5

    return (rim * 32767).astype(np.int16)


def save_drum_sample(audio_array: np.ndarray, filepath: str, sample_rate=44100):
    """Save synthesized drum audio to WAV file."""
    wavfile.write(filepath, sample_rate, audio_array)