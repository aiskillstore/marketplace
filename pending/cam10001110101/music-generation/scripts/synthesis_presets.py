"""
Genre-specific synthesis presets for electronic music.

Provides pre-tuned parameters for drums, bass, pads, and leads
optimized for different electronic music genres.
"""

PRESETS = {
    "deep_house": {
        "description": "Warm, groovy deep house with subby bass and lush pads",
        "bpm_range": (120, 125),
        "volume_balance": {
            "drums": 0.0,
            "bass": -5.0,
            "pad": -4.0,
            "lead": -1.0,
            "velocity_curve": "exponential",
        },
        "drums": {
            "kick": {
                "pitch": 56.0,
                "decay": 0.5,
                "punch": 0.85,
                "click_level": 0.25,
            },
            "snare": {
                "tone_mix": 0.3,
                "pitch": 200.0,
                "snap": 0.6,
                "decay": 0.25,
            },
            "hat_closed": {
                "brightness": 0.65,
                "decay": 0.12,
                "metallic": 0.5,
            },
            "hat_open": {
                "brightness": 0.7,
                "decay": 0.4,
                "metallic": 0.55,
            },
            "clap": {
                "room_size": 0.4,
                "density": 0.7,
                "brightness": 0.6,
            },
        },
        "bass": {
            "waveform": "sawtooth",
            "cutoff": 180,
            "resonance": 0.5,
            "attack": 0.01,
            "decay": 0.15,
            "sustain": 0.85,
            "release": 0.2,
        },
        "pad": {
            "attack": 0.4,
            "release": 0.6,
            "brightness": 0.5,
            "detune": 0.02,
        },
        "lead": {
            "brightness": 0.5,
            "attack": 0.01,
            "decay": 0.1,
            "sustain": 0.6,
            "release": 0.15,
            "portamento": 0.0,
            "unison_voices": 3,
            "unison_detune": 0.08,
        },
    },
    "techno": {
        "description": "Hard-hitting techno with punchy drums and aggressive bass",
        "bpm_range": (125, 135),
        "volume_balance": {
            "drums": 1.0,
            "bass": 0.0,
            "pad": -3.0,
            "lead": 0.0,
            "velocity_curve": "linear",
        },
        "drums": {
            "kick": {
                "pitch": 60.0,
                "decay": 0.3,
                "punch": 1.0,
                "click_level": 0.4,
            },
            "snare": {
                "tone_mix": 0.2,
                "pitch": 220.0,
                "snap": 0.8,
                "decay": 0.2,
            },
            "hat_closed": {
                "brightness": 0.8,
                "decay": 0.08,
                "metallic": 0.6,
            },
            "hat_open": {
                "brightness": 0.85,
                "decay": 0.3,
                "metallic": 0.7,
            },
            "clap": {
                "room_size": 0.2,
                "density": 0.8,
                "brightness": 0.7,
            },
        },
        "bass": {
            "waveform": "square",
            "cutoff": 300,
            "resonance": 0.8,
            "attack": 0.005,
            "decay": 0.1,
            "sustain": 0.6,
            "release": 0.1,
        },
        "pad": {
            "attack": 0.5,
            "release": 0.8,
            "brightness": 0.5,
            "detune": 0.02,
        },
        "lead": {
            "brightness": 0.85,
            "attack": 0.005,
            "decay": 0.08,
            "sustain": 0.5,
            "release": 0.1,
            "portamento": 0.0,
            "unison_voices": 7,
            "unison_detune": 0.12,
        },
    },
    "trance": {
        "description": "Uplifting trance with soaring leads and driving bass",
        "bpm_range": (130, 140),
        "volume_balance": {
            "drums": 0.0,
            "bass": -1.0,
            "pad": -1.0,
            "lead": 1.0,
            "velocity_curve": "exponential",
        },
        "drums": {
            "kick": {
                "pitch": 58.0,
                "decay": 0.4,
                "punch": 0.9,
                "click_level": 0.35,
            },
            "snare": {
                "tone_mix": 0.25,
                "pitch": 210.0,
                "snap": 0.7,
                "decay": 0.23,
            },
            "hat_closed": {
                "brightness": 0.75,
                "decay": 0.10,
                "metallic": 0.55,
            },
            "hat_open": {
                "brightness": 0.8,
                "decay": 0.35,
                "metallic": 0.6,
            },
            "clap": {
                "room_size": 0.3,
                "density": 0.75,
                "brightness": 0.65,
            },
        },
        "bass": {
            "waveform": "sawtooth",
            "cutoff": 250,
            "resonance": 0.7,
            "attack": 0.008,
            "decay": 0.12,
            "sustain": 0.65,
            "release": 0.15,
        },
        "pad": {
            "attack": 1.2,
            "release": 1.5,
            "brightness": 0.6,
            "detune": 0.04,
        },
        "lead": {
            "brightness": 0.9,
            "attack": 0.005,
            "decay": 0.15,
            "sustain": 0.7,
            "release": 0.2,
            "portamento": 0.05,
            "unison_voices": 9,
            "unison_detune": 0.15,
        },
    },
    "ambient": {
        "description": "Atmospheric ambient with soft pads and subtle percussion",
        "bpm_range": (60, 90),
        "volume_balance": {
            "drums": -6.0,
            "bass": -4.0,
            "pad": 0.0,
            "lead": -2.0,
            "velocity_curve": "logarithmic",
        },
        "drums": {
            "kick": {
                "pitch": 50.0,
                "decay": 0.8,
                "punch": 0.4,
                "click_level": 0.1,
            },
            "snare": {
                "tone_mix": 0.4,
                "pitch": 180.0,
                "snap": 0.3,
                "decay": 0.4,
            },
            "hat_closed": {
                "brightness": 0.5,
                "decay": 0.15,
                "metallic": 0.3,
            },
            "hat_open": {
                "brightness": 0.55,
                "decay": 0.6,
                "metallic": 0.4,
            },
            "clap": {
                "room_size": 0.8,
                "density": 0.5,
                "brightness": 0.4,
            },
        },
        "bass": {
            "waveform": "sine",
            "cutoff": 120,
            "resonance": 0.3,
            "attack": 0.05,
            "decay": 0.3,
            "sustain": 0.8,
            "release": 0.5,
        },
        "pad": {
            "attack": 1.0,
            "release": 1.2,
            "brightness": 0.4,
            "detune": 0.03,
        },
        "lead": {
            "brightness": 0.5,
            "attack": 0.02,
            "decay": 0.2,
            "sustain": 0.75,
            "release": 0.4,
            "portamento": 0.1,
            "unison_voices": 5,
            "unison_detune": 0.10,
        },
    },
    "deep_house_warm": {
        "description": "Extra warm deep house with darker, more analog sound",
        "bpm_range": (118, 122),
        "volume_balance": {
            "drums": 0.0,
            "bass": -6.0,
            "pad": -5.0,
            "lead": -2.0,
            "velocity_curve": "exponential",
        },
        "drums": {
            "kick": {
                "pitch": 54.0,
                "decay": 0.55,
                "punch": 0.9,
                "click_level": 0.2,
            },
            "snare": {
                "tone_mix": 0.35,
                "pitch": 190.0,
                "snap": 0.55,
                "decay": 0.28,
            },
            "hat_closed": {
                "brightness": 0.6,
                "decay": 0.13,
                "metallic": 0.45,
            },
            "hat_open": {
                "brightness": 0.65,
                "decay": 0.45,
                "metallic": 0.5,
            },
            "clap": {
                "room_size": 0.5,
                "density": 0.65,
                "brightness": 0.55,
            },
        },
        "bass": {
            "waveform": "sawtooth",
            "cutoff": 160,
            "resonance": 0.5,
            "attack": 0.015,
            "decay": 0.18,
            "sustain": 0.9,
            "release": 0.25,
        },
        "pad": {
            "attack": 0.5,
            "release": 0.7,
            "brightness": 0.4,
            "detune": 0.02,
        },
        "lead": {
            "brightness": 0.45,
            "attack": 0.015,
            "decay": 0.12,
            "sustain": 0.65,
            "release": 0.18,
            "portamento": 0.0,
            "unison_voices": 3,
            "unison_detune": 0.06,
        },
    },
    "acid_house": {
        "description": "Classic acid house with squelchy TB-303 style bass",
        "bpm_range": (120, 130),
        "volume_balance": {
            "drums": 0.0,
            "bass": 1.0,
            "pad": -3.0,
            "lead": -1.0,
            "velocity_curve": "linear",
        },
        "drums": {
            "kick": {
                "pitch": 56.0,
                "decay": 0.45,
                "punch": 0.9,
                "click_level": 0.3,
            },
            "snare": {
                "tone_mix": 0.15,
                "pitch": 240.0,
                "snap": 0.7,
                "decay": 0.2,
            },
            "hat_closed": {
                "brightness": 0.7,
                "decay": 0.10,
                "metallic": 0.6,
            },
            "hat_open": {
                "brightness": 0.75,
                "decay": 0.35,
                "metallic": 0.65,
            },
            "clap": {
                "room_size": 0.25,
                "density": 0.75,
                "brightness": 0.65,
            },
        },
        "bass": {
            "waveform": "square",
            "cutoff": 400,
            "resonance": 0.9,
            "attack": 0.005,
            "decay": 0.08,
            "sustain": 0.5,
            "release": 0.08,
        },
        "pad": {
            "attack": 0.6,
            "release": 0.9,
            "brightness": 0.45,
            "detune": 0.02,
        },
        "lead": {
            "brightness": 0.75,
            "attack": 0.005,
            "decay": 0.09,
            "sustain": 0.55,
            "release": 0.1,
            "portamento": 0.02,
            "unison_voices": 5,
            "unison_detune": 0.12,
        },
    },
    "default": {
        "description": "Balanced general-purpose electronic music preset",
        "bpm_range": (120, 130),
        "volume_balance": {
            "drums": 0.0,
            "bass": 0.0,
            "pad": 0.0,
            "lead": 0.0,
            "velocity_curve": "linear",
        },
        "drums": {
            "kick": {
                "pitch": 56.0,
                "decay": 0.5,
                "punch": 0.8,
                "click_level": 0.3,
            },
            "snare": {
                "tone_mix": 0.3,
                "pitch": 200.0,
                "snap": 0.7,
                "decay": 0.25,
            },
            "hat_closed": {
                "brightness": 0.7,
                "decay": 0.12,
                "metallic": 0.5,
            },
            "hat_open": {
                "brightness": 0.75,
                "decay": 0.4,
                "metallic": 0.55,
            },
            "clap": {
                "room_size": 0.5,
                "density": 0.7,
                "brightness": 0.6,
            },
            "rim": {
                "pitch": 800.0,
                "decay": 0.08,
                "click_mix": 0.7,
            },
        },
        "bass": {
            "waveform": "sawtooth",
            "cutoff": 200,
            "resonance": 0.6,
            "attack": 0.01,
            "decay": 0.15,
            "sustain": 0.7,
            "release": 0.2,
        },
        "pad": {
            "attack": 0.8,
            "release": 1.0,
            "brightness": 0.4,
            "detune": 0.03,
        },
        "lead": {
            "brightness": 0.75,
            "attack": 0.01,
            "decay": 0.1,
            "sustain": 0.6,
            "release": 0.15,
            "portamento": 0.0,
            "unison_voices": 5,
            "unison_detune": 0.10,
        },
    },
}


def get_preset(genre: str = "default") -> dict:
    """
    Get synthesis preset for a specific genre.

    Args:
        genre: Genre name (e.g., "deep_house", "techno", "ambient")

    Returns:
        Preset dictionary with drum, bass, pad, and lead parameters
    """
    genre_lower = genre.lower().replace(" ", "_").replace("-", "_")

    if genre_lower in PRESETS:
        return PRESETS[genre_lower]

    return PRESETS["default"]


def list_genres() -> list[str]:
    """Get list of available genre presets."""
    return list(PRESETS.keys())


def describe_preset(genre: str) -> str:
    """Get description of a genre preset."""
    preset = get_preset(genre)
    return preset.get("description", "No description available")