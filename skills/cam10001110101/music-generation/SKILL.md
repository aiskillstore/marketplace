---
name: music-generation
description: Tools, patterns, and utilities for generating professional music with realistic instrument sounds. Write custom compositions using music21 or learn from existing MIDI files.
when_to_use: When users request downloadable .mp3 or .wav music files, original compositions, classical pieces, or timed music for videos. This skill emphasizes intelligence and composition over pre-made functions.
version: 2.0.0
dependencies: music21, midi2audio, pydub, mido, numpy, scipy
---

## Quick Start (Read This First!)

**IMPORTANT: This file is located at `/mnt/skills/private/music-generation/SKILL.md`**

If you need to reference this skill again during your session, read that exact path directly. Do not explore directories or use find commands - just read the file path above.

## Philosophy

This skill provides **tools and patterns** for music composition, not pre-baked solutions. You should use your intelligence and the music21 library to compose dynamically based on user requests.

**Core Principle**: Write custom code that composes music algorithmically rather than calling functions with hardcoded melodies.

## Installation & Setup

### Quick Installation

Run the automated installer for complete setup:

```bash
bash /mnt/skills/private/music-generation/install.sh
```

This installs all system dependencies, Python packages, and verifies the installation.

**Note:** The install script may display "error: externally-managed-environment" messages at the end. These are expected and can be safely ignored - the dependencies are already installed. If you see these messages, the installation was successful.

### Manual Installation

Alternatively, install dependencies manually:

**System Dependencies:**
```bash
apt-get update
apt-get install -y fluidsynth fluid-soundfont-gm fluid-soundfont-gs ffmpeg
```

**Python Dependencies:**
```bash
pip install -r /mnt/skills/private/music-generation/requirements.txt
```

The `requirements.txt` includes: music21, midi2audio, pydub, mido, numpy, scipy.

### Available SoundFonts

**Traditional Pipeline (Orchestral/Acoustic):**
- `/usr/share/sounds/sf2/FluidR3_GM.sf2` (141MB, General MIDI soundfont for orchestral/classical)
- `/usr/share/sounds/sf2/default.sf2` (symlink to best available)

**Electronic Pipeline:**
- No soundfonts required - uses real-time synthesis for all electronic sounds

## Quick Start: Write Custom Compositions

### Basic Music Generation Pattern

```python
from music21 import stream, note, chord, instrument, tempo, dynamics
from midi2audio import FluidSynth
from pydub import AudioSegment

# 1. Create score and parts
score = stream.Score()
violin_part = stream.Part()
violin_part.insert(0, instrument.Violin())
violin_part.insert(0, tempo.MetronomeMark(number=120))

# 2. Generate notes algorithmically
for measure in range(16):
    violin_part.append(note.Note('E5', quarterLength=1.0))
    violin_part.append(note.Note('G5', quarterLength=1.0))
    violin_part.append(note.Note('A5', quarterLength=2.0))

# 3. Export to MIDI
score.append(violin_part)
midi_path = '/mnt/user-data/outputs/composition.mid'
score.write('midi', fp=midi_path)

# 4. Render with FluidSynth
fs = FluidSynth('/usr/share/sounds/sf2/FluidR3_GM.sf2')
wav_path = '/mnt/user-data/outputs/composition.wav'
fs.midi_to_audio(midi_path, wav_path)

# 5. Convert to MP3
audio = AudioSegment.from_wav(wav_path)
mp3_path = '/mnt/user-data/outputs/composition.mp3'
audio.export(mp3_path, format='mp3', bitrate='192k')
```

### Key Concepts

- **Always create downloadable MP3 files** (not HTML players)
- **All output goes to** `/mnt/user-data/outputs/`
- **Use music21.instrument classes**: `instrument.Violin()`, `instrument.Violoncello()`, `instrument.Piano()`, `instrument.Trumpet()`, etc.
- **Generate notes programmatically** - avoid hardcoded sequences

## Choosing the Right Rendering Pipeline

**CRITICAL**: This skill supports TWO rendering pipelines. You MUST choose based on the musical genre:

### Traditional Pipeline (Orchestral, Classical, Acoustic)

**Use when creating:**
- Orchestral music (violin, cello, trumpet, etc.)
- Classical compositions (Mozart, Beethoven style)
- Piano music, chamber music, symphonies
- Acoustic guitar, brass ensembles
- Any music with traditional/acoustic instruments

**How to render:**
```python
# After composing with music21 and exporting MIDI...
from midi2audio import FluidSynth
from pydub import AudioSegment

fs = FluidSynth('/usr/share/sounds/sf2/FluidR3_GM.sf2')
fs.midi_to_audio(midi_path, wav_path)

audio = AudioSegment.from_wav(wav_path)
audio.export(mp3_path, format='mp3', bitrate='192k')
```

### Electronic Pipeline (House, Techno, EDM, Electronic)

**Use when creating:**
- House, techno, trance, EDM
- Electronic dance music with synth bass/pads/leads
- DJ beats, club music
- Any music described as "electronic" or "synth-heavy"
- Music referencing DJs like Keinemusik, Black Coffee, etc.

**How to render:**
```python
# After composing with music21, using mido for instruments, and exporting MIDI...
import subprocess

# Use the electronic rendering script
result = subprocess.run([
    'python',
    '/mnt/skills/private/music-generation/scripts/render_electronic.py',
    midi_path,
    mp3_path
], capture_output=True, text=True)

print(result.stdout)
if result.returncode != 0:
    print(f"Error: {result.stderr}")
```

**Why this matters:**
- The orchestral soundfont (FluidR3_GM.sf2) sounds **terrible** for electronic music
- Its "synth" instruments are basic 1990s approximations
- The electronic pipeline uses **real-time synthesis** for authentic electronic sound
- Synthesizes 808-style kicks, electronic snares, and hi-hats on-the-fly (NO external samples required)
- Bass/pads/leads use subtractive synthesis with filters and ADSR envelopes
- Genre presets (deep_house, techno, trance, ambient) tune synthesis parameters automatically

**Drum Synthesis:**

The electronic renderer uses **real-time drum synthesis** (no external samples needed). All drum sounds (kicks, snares, hi-hats, claps) are synthesized on-the-fly with genre-specific parameters.

**Example: House Track**
```python
# 1. Compose with music21 (same as always)
score = stream.Score()
drums = stream.Part()
bass = stream.Part()
pads = stream.Part()
# ... compose your music

# 2. Export MIDI
midi_path = '/mnt/user-data/outputs/deep_house.mid'
score.write('midi', fp=midi_path)

# 3. Fix instruments with mido (INSERT program_change messages)
from mido import MidiFile, Message
mid = MidiFile(midi_path)
for i, track in enumerate(mid.tracks):
    if i == 1:  # Drums
        for msg in track:
            if hasattr(msg, 'channel'):
                msg.channel = 9
    elif i == 2:  # Bass - INSERT program_change
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=38, time=0))
mid.save(midi_path)

# 4. Render with ELECTRONIC pipeline with deep_house preset!
import subprocess
subprocess.run([
    'python',
    '/mnt/skills/private/music-generation/scripts/render_electronic.py',
    midi_path,
    '/mnt/user-data/outputs/deep_house.mp3',
    '--genre', 'deep_house'
])
```

### Available Genre Presets

The electronic renderer includes pre-tuned synthesis presets with **supersaw lead synthesis** for thick, professional EDM sounds:

- **deep_house**: Warm bass with 3-voice leads (120-125 BPM)
- **techno**: Hard-hitting with 7-voice supersaw leads (125-135 BPM)
- **trance**: Uplifting with massive 9-voice supersaw leads (130-140 BPM)
- **ambient**: Soft, atmospheric with 5-voice pads (60-90 BPM)
- **acid_house**: Squelchy TB-303 bass with 5-voice leads (120-130 BPM)
- **default**: Balanced 5-voice leads (120-130 BPM)

**Supersaw Synthesis (Swedish House Mafia / Progressive House Sound):**

The electronic renderer now includes **unison voice synthesis** for fat, buzzy leads:
- **Multiple detuned oscillators**: 3-9 sawtooth waves per note (genre-dependent)
- **Aggressive detuning**: 6-15 cents spread creates buzzy chorus effect
- **Enhanced saturation**: 2.5x distortion for punch and aggression
- **Phase spreading**: Creates wide stereo image

**How It Works:**
- House: 3 voices, ±8 cents (subtle, warm)
- Techno: 7 voices, ±12 cents (aggressive, punchy)
- Trance: 9 voices, ±15 cents (massive, soaring)
- Acid house: 5 voices, ±12 cents (squelchy, aggressive)

This replicates the classic supersaw sound from Swedish House Mafia, Avicii, and modern EDM productions.

Each preset tunes:
- **Drum synthesis**: kick pitch/decay/punch, snare tone/snap, hat brightness/metallic
- **Bass synthesis**: waveform, filter cutoff/resonance, ADSR envelope
- **Pad synthesis**: attack/release times, detune amount, brightness
- **Lead synthesis**: brightness, envelope, portamento
- **Volume balance**: intelligent mix levels per instrument with frequency-aware compensation
- **Velocity curves**: exponential, linear, or logarithmic response to MIDI velocity

### Intelligent Volume Management

The electronic renderer uses **frequency-aware volume balancing** to prevent any instrument from overpowering the mix:

**How it works:**
- **Bass frequencies (<100Hz)**: Automatically reduced by -4 to -6dB (sub-bass has high perceived energy)
- **Mid frequencies (200-800Hz)**: Balanced naturally
- **High frequencies (>800Hz)**: Slightly boosted for clarity (+1 to +1.5dB)
- **Genre-specific balance**: Each preset has optimized levels (e.g., House bass gets -3dB)
- **Velocity curves**: MIDI velocity maps intelligently (not just linear)
- **Auto-limiting**: Final mix is limited to -1dB to prevent clipping

**Why this matters:**
- House bass (A1, E2) at 55-82Hz naturally has more power - now automatically compensated
- Prevents "bass overpowering everything" issues
- Maintains balanced mix across all genres
- No manual volume tweaking needed

To see all available presets:
```bash
python /mnt/skills/private/music-generation/scripts/render_electronic.py --list-genres
```

### Customizing Synthesis Parameters

For advanced control, you can create custom preset JSON files:

```json
{
  "drums": {
    "kick": {"pitch": 52.0, "decay": 0.6, "punch": 0.9},
    "snare": {"tone_mix": 0.25, "snap": 0.8}
  },
  "bass": {
    "waveform": "sawtooth",
    "cutoff": 180,
    "resonance": 0.7
  },
  "pad": {
    "attack": 1.0,
    "brightness": 0.35
  }
}
```

Then use with `--preset`:
```bash
python render_electronic.py track.mid output.mp3 --preset my_preset.json
```

## Advanced Workflow: Learn from Existing MIDI

For classical pieces or complex compositions, you can:

### 1. Extract Structure from ANY MIDI File

```bash
python /mnt/skills/private/music-generation/scripts/midi_inventory.py \
    path/to/mozart.mid \
    /mnt/user-data/outputs/mozart_structure.json
```

This extracts:
- Tempo, key signature, time signature
- Track information and instruments
- Complete note sequences with timing
- Musical structure

### 2. Modify the JSON Structure

```python
import json

# Load extracted structure
with open('/mnt/user-data/outputs/mozart_structure.json', 'r') as f:
    structure = json.load(f)

# Modify instruments, notes, timing, etc.
structure['tracks']['track-0']['instrument'] = 'violin'  # Change piano to violin!

# Save modified structure
with open('/mnt/user-data/outputs/mozart_violin.json', 'w') as f:
    json.dump(structure, f)
```

### 3. Render Modified Structure to MP3

```bash
python /mnt/skills/private/music-generation/scripts/midi_render.py \
    /mnt/user-data/outputs/mozart_violin.json \
    /mnt/user-data/outputs/mozart_violin.mp3
```

**This workflow lets you "recreate" any classical piece with different instruments!**

## Available Scripts

All scripts are located in `/mnt/skills/private/music-generation/scripts/`:

**Main Workflow Scripts:**
- **`render_electronic.py`** - Electronic music renderer with real-time synthesis (drums, bass, pads, leads)
- **`midi_inventory.py`** - Extract complete structure from ANY MIDI file to JSON format
- **`midi_render.py`** - Render JSON music structure to MP3 using FluidSynth
- **`midi_transform.py`** - Generic MIDI transformations (transpose, tempo change, instrument swap)
- **`audio_validate.py`** - Validate audio file quality and format

**Synthesis Engine (used by render_electronic.py):**
- **`drum_synthesizer.py`** - Synthesizes kicks, snares, hi-hats, claps on-the-fly
- **`melodic_synthesizer.py`** - Synthesizes bass, pads, and lead sounds using subtractive synthesis
- **`synthesis_presets.py`** - Genre presets (deep_house, techno, trance, ambient, etc.)
- **`midi_utils.py`** - MIDI parsing utilities for extracting events and metadata
- **`__init__.py`** - Python package marker (allows importing scripts as modules)

**Utility Scripts:**

## Music Theory Reference

### Complete General MIDI Instrument Map (Programs 0-127)

**CRITICAL: music21 has limited instrument support. For most sounds (especially electronic), you MUST use mido to set program numbers after export.**

```python
# Piano (0-7)
0: "Acoustic Grand Piano"
1: "Bright Acoustic Piano"
2: "Electric Grand Piano"
3: "Honky-tonk Piano"
4: "Electric Piano 1"
5: "Electric Piano 2"
6: "Harpsichord"
7: "Clavinet"

# Chromatic Percussion (8-15)
8: "Celesta"
9: "Glockenspiel"
10: "Music Box"
11: "Vibraphone"
12: "Marimba"
13: "Xylophone"
14: "Tubular Bells"
15: "Dulcimer"

# Organ (16-23)
16: "Drawbar Organ"
17: "Percussive Organ"
18: "Rock Organ"
19: "Church Organ"
20: "Reed Organ"
21: "Accordion"
22: "Harmonica"
23: "Tango Accordion"

# Guitar (24-31)
24: "Acoustic Guitar (nylon)"
25: "Acoustic Guitar (steel)"
26: "Electric Guitar (jazz)"
27: "Electric Guitar (clean)"
28: "Electric Guitar (muted)"
29: "Overdriven Guitar"
30: "Distortion Guitar"
31: "Guitar Harmonics"

# Bass (32-39)
32: "Acoustic Bass"
33: "Electric Bass (finger)"
34: "Electric Bass (pick)"
35: "Fretless Bass"
36: "Slap Bass 1"
37: "Slap Bass 2"
38: "Synth Bass 1"
39: "Synth Bass 2"

# Strings (40-47)
40: "Violin"
41: "Viola"
42: "Cello"
43: "Contrabass"
44: "Tremolo Strings"
45: "Pizzicato Strings"
46: "Orchestral Harp"
47: "Timpani"

# Ensemble (48-55)
48: "String Ensemble 1"
49: "String Ensemble 2"
50: "Synth Strings 1"
51: "Synth Strings 2"
52: "Choir Aahs"
53: "Voice Oohs"
54: "Synth Voice"
55: "Orchestra Hit"

# Brass (56-63)
56: "Trumpet"
57: "Trombone"
58: "Tuba"
59: "Muted Trumpet"
60: "French Horn"
61: "Brass Section"
62: "Synth Brass 1"
63: "Synth Brass 2"

# Reed (64-71)
64: "Soprano Sax"
65: "Alto Sax"
66: "Tenor Sax"
67: "Baritone Sax"
68: "Oboe"
69: "English Horn"
70: "Bassoon"
71: "Clarinet"

# Pipe (72-79)
72: "Piccolo"
73: "Flute"
74: "Recorder"
75: "Pan Flute"
76: "Blown Bottle"
77: "Shakuhachi"
78: "Whistle"
79: "Ocarina"

# Synth Lead (80-87)
80: "Lead 1 (square)"
81: "Lead 2 (sawtooth)"
82: "Lead 3 (calliope)"
83: "Lead 4 (chiff)"
84: "Lead 5 (charang)"
85: "Lead 6 (voice)"
86: "Lead 7 (fifths)"
87: "Lead 8 (bass + lead)"

# Synth Pad (88-95)
88: "Pad 1 (new age)"
89: "Pad 2 (warm)"
90: "Pad 3 (polysynth)"
91: "Pad 4 (choir)"
92: "Pad 5 (bowed)"
93: "Pad 6 (metallic)"
94: "Pad 7 (halo)"
95: "Pad 8 (sweep)"

# Synth Effects (96-103)
96: "FX 1 (rain)"
97: "FX 2 (soundtrack)"
98: "FX 3 (crystal)"
99: "FX 4 (atmosphere)"
100: "FX 5 (brightness)"
101: "FX 6 (goblins)"
102: "FX 7 (echoes)"
103: "FX 8 (sci-fi)"

# Ethnic (104-111)
104: "Sitar"
105: "Banjo"
106: "Shamisen"
107: "Koto"
108: "Kalimba"
109: "Bag pipe"
110: "Fiddle"
111: "Shanai"

# Percussive (112-119)
112: "Tinkle Bell"
113: "Agogo"
114: "Steel Drums"
115: "Woodblock"
116: "Taiko Drum"
117: "Melodic Tom"
118: "Synth Drum"
119: "Reverse Cymbal"

# Sound Effects (120-127)
120: "Guitar Fret Noise"
121: "Breath Noise"
122: "Seashore"
123: "Bird Tweet"
124: "Telephone Ring"
125: "Helicopter"
126: "Applause"
127: "Gunshot"
```

### Complete Drum Map (MIDI Channel 10, Notes 35-81)

**Drums use note numbers for different sounds, NOT pitch. Must be on channel 10 (9 in 0-indexed).**

```python
# Bass Drums
35: "Acoustic Bass Drum"
36: "Bass Drum 1"  # Most common kick

# Snares
38: "Acoustic Snare"  # Standard snare
40: "Electric Snare"

# Toms
41: "Low Floor Tom"
43: "High Floor Tom"
45: "Low Tom"
47: "Low-Mid Tom"
48: "Hi-Mid Tom"
50: "High Tom"

# Hi-Hats
42: "Closed Hi-Hat"  # Most used
44: "Pedal Hi-Hat"
46: "Open Hi-Hat"

# Cymbals
49: "Crash Cymbal 1"
51: "Ride Cymbal 1"
52: "Chinese Cymbal"
53: "Ride Bell"
55: "Splash Cymbal"
57: "Crash Cymbal 2"
59: "Ride Cymbal 2"

# Percussion
37: "Side Stick"
39: "Hand Clap"
54: "Tambourine"
56: "Cowbell"
58: "Vibraslap"
60: "Hi Bongo"
61: "Low Bongo"
62: "Mute Hi Conga"
63: "Open Hi Conga"
64: "Low Conga"
65: "High Timbale"
66: "Low Timbale"
67: "High Agogo"
68: "Low Agogo"
69: "Cabasa"
70: "Maracas"
71: "Short Whistle"
72: "Long Whistle"
73: "Short Guiro"
74: "Long Guiro"
75: "Claves"
76: "Hi Wood Block"
77: "Low Wood Block"
78: "Mute Cuica"
79: "Open Cuica"
80: "Mute Triangle"
81: "Open Triangle"
```

### How to Use Any Instrument (mido workflow)

music21 has built-in classes for orchestral instruments (Violin, Piano, Trumpet, etc.) but NO support for synths, electronic instruments, or many others. To use any GM instrument:

**CRITICAL RULE**: When you create a `stream.Part()` WITHOUT assigning a music21 instrument class, music21 WILL NOT create `program_change` messages in the MIDI file. You MUST use mido to INSERT these messages manually. Simply trying to modify them with `if msg.type == 'program_change': msg.program = X` will fail silently because no such messages exist!

**Helper Function for Setting Instruments**:

```python
from mido import Message

def set_track_instrument(track, program):
    """Insert a program_change message at the beginning of a MIDI track."""
    insert_pos = 0
    for j, msg in enumerate(track):
        if msg.type == 'track_name':
            insert_pos = j + 1
            break
    track.insert(insert_pos, Message('program_change', program=program, time=0))

# Usage after loading MIDI with mido:
# set_track_instrument(mid.tracks[2], 33)  # Set track 2 to Electric Bass
```

**Step 1: Compose with music21 (use placeholder or skip instrument)**
```python
from music21 import stream, note, chord, tempo

score = stream.Score()

# Create parts - don't worry about instrument assignment yet
synth_lead = stream.Part()
synth_pad = stream.Part()
bass = stream.Part()

# Add your notes/chords
synth_lead.append(note.Note('E5', quarterLength=1.0))
# ... compose your music

score.append(synth_lead)
score.append(synth_pad)
score.append(bass)

# Export to MIDI
midi_path = '/mnt/user-data/outputs/track.mid'
score.write('midi', fp=midi_path)
```

**Step 2: Assign correct instruments with mido**
```python
from mido import MidiFile, Message

mid = MidiFile(midi_path)

# Track 0 is tempo/metadata, actual parts start at track 1
# CRITICAL: You must INSERT program_change messages, not just modify existing ones!
# music21 doesn't create program_change messages if you don't assign instruments

for i, track in enumerate(mid.tracks):
    if i == 1:  # First part (synth_lead)
        # Insert program_change at beginning of track (after track name if present)
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=80, time=0))

    elif i == 2:  # Second part (synth_pad)
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=88, time=0))

    elif i == 3:  # Third part (bass)
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=38, time=0))

mid.save(midi_path)
```

**Step 3: For drums, ALSO set channel to 9 (channel 10)**
```python
# If track is drums, set ALL messages to channel 9
for i, track in enumerate(mid.tracks):
    if i == 1:  # This is the drum track
        for msg in track:
            if hasattr(msg, 'channel'):
                msg.channel = 9  # Channel 10 in 1-indexed
```

**Step 4: Render to audio**
```python
from midi2audio import FluidSynth
from pydub import AudioSegment

fs = FluidSynth('/usr/share/sounds/sf2/FluidR3_GM.sf2')
wav_path = '/mnt/user-data/outputs/track.wav'
fs.midi_to_audio(midi_path, wav_path)

audio = AudioSegment.from_wav(wav_path)
mp3_path = '/mnt/user-data/outputs/track.mp3'
audio.export(mp3_path, format='mp3', bitrate='192k')
```

### Common Chord Progressions & Styles

```python
# Standard Progressions (Roman numerals)
"pop": ["I", "V", "vi", "IV"]           # C-G-Am-F (Journey, Adele)
"epic": ["i", "VI", "III", "VII"]       # Am-F-C-G (Epic trailer music)
"sad": ["i", "VI", "iv", "V"]           # Am-F-Dm-E (Melancholic)
"jazz": ["ii", "V", "I", "vi"]          # Dm-G-C-Am (Jazz standard)
"classical": ["I", "IV", "V", "I"]      # C-F-G-C (Classical cadence)
"blues": ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "I"]  # 12-bar blues
"house": ["i", "VI", "III", "VII"]      # Minor house progression
"reggae": ["I", "V", "vi", "IV"]        # Offbeat rhythm style
"country": ["I", "IV", "V", "I"]        # Simple and direct
"rock": ["I", "bVII", "IV", "I"]        # Power chord style
"r&b": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]  # Complex R&B

# Genre-Specific Characteristics
STYLES = {
    "house": {
        "bpm": 120-128,
        "time_signature": "4/4",
        "drum_pattern": "4-on-floor kick, offbeat hats",
        "bass": "Synth bass with groove",
        "common_instruments": [38, 80, 88, 4]  # Synth bass, lead, pad, e-piano
    },
    "jazz": {
        "bpm": 100-180,
        "time_signature": "4/4 or 3/4",
        "chords": "Extended (7th, 9th, 11th, 13th)",
        "common_instruments": [0, 32, 64, 56, 73]  # Piano, bass, sax, trumpet, drums
    },
    "orchestral": {
        "bpm": 60-140,
        "sections": ["strings", "woodwinds", "brass", "percussion"],
        "common_instruments": [40, 41, 42, 56, 73, 47]  # Violin, viola, cello, trumpet, flute, timpani
    },
    "rock": {
        "bpm": 100-140,
        "time_signature": "4/4",
        "guitars": "Distorted (30) or clean (27)",
        "common_instruments": [30, 33, 0, 128]  # Distortion guitar, bass, piano, drums
    },
    "ambient": {
        "bpm": 60-90,
        "characteristics": "Long sustained notes, atmospheric pads",
        "common_instruments": [88, 89, 90, 91, 52]  # Various pads, choir
    },
    "trap": {
        "bpm": 130-170,
        "drums": "Tight snare rolls, 808 bass kicks",
        "hi_hats": "Fast hi-hat patterns (1/16 or 1/32 notes)",
        "common_instruments": [38, 128]  # Synth bass, drums
    }
}
```

### music21 Instrument Classes

```python
from music21 import instrument

# Strings
instrument.Violin()
instrument.Viola()
instrument.Violoncello()  # Note: NOT Cello()
instrument.Contrabass()
instrument.Harp()

# Piano
instrument.Piano()
instrument.Harpsichord()

# Brass
instrument.Trumpet()
instrument.Trombone()
instrument.Tuba()
instrument.Horn()  # French horn

# Woodwinds
instrument.Flute()
instrument.Clarinet()
instrument.Oboe()
instrument.Bassoon()
instrument.SopranoSaxophone()
instrument.AltoSaxophone()
instrument.TenorSaxophone()  # Most common for jazz
instrument.BaritoneSaxophone()

# Other
instrument.AcousticGuitar()
instrument.ElectricGuitar()
instrument.Bass()
instrument.Timpani()

# CRITICAL: music21 has LIMITED support for electronic instruments and drums
# For synths, drums, and electronic sounds, you MUST:
# 1. Create a Part without an instrument (or use a placeholder like Piano())
# 2. Use mido library to INSERT program_change messages after export
# 3. Set drums to MIDI channel 10 (channel 9 in 0-indexed) or they won't sound like drums
#
# Common mistakes:
# - instrument.Cello() doesn't exist - use Violoncello()
# - instrument.FrenchHorn() doesn't exist - use Horn()
# - Setting part.partName doesn't change the sound - you must set MIDI program with mido
# - Drums on channel 0 will play as pitched notes, not drum sounds
```

### Note Durations (Quarter Note = 1.0)

- Whole note: 4.0
- Half note: 2.0
- Quarter note: 1.0
- Eighth note: 0.5
- Sixteenth note: 0.25
- Dotted quarter: 1.5
- Triplet quarter: 0.667

### mido Quick Reference

For electronic music and drums, use `mido` to set MIDI programs after music21 export:

```python
from mido import MidiFile, Message

mid = MidiFile(midi_path)

# Insert program_change message
for i, track in enumerate(mid.tracks):
    if i == 1:  # Your track (tracks start at 1, not 0)
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=38, time=0))

# For drums: Set channel to 9 (channel 10 in 1-indexed)
for i, track in enumerate(mid.tracks):
    if i == 1:  # Drum track
        for msg in track:
            if hasattr(msg, 'channel'):
                msg.channel = 9

mid.save(midi_path)
```

**Common MIDI Programs:**
- 38: Synth Bass 1
- 80: Square Lead
- 81: Sawtooth Lead
- 88: Pad 1 (New Age)
- 25: Acoustic Guitar (Steel) - loud, cuts through
- 33: Acoustic Bass

## Common Techniques

### Drum Programming (4-on-floor house beat)

**CRITICAL**: music21's `.append()` adds notes **sequentially** (one after another), not simultaneously. For layered drums where kicks, snares, and hats play at the same time, you MUST use `.insert(offset, note)` with explicit timing.

**⚠️ ALWAYS USE .insert() FOR ALL TRACKS:**

Since layering is needed for nearly all good music composition, you should **ALWAYS use .insert(offset, note) for ALL tracks** - drums, bass, guitar, pads, everything. This prevents timing bugs and ensures proper synchronization.

**NEVER mix .insert() and .append()** - If you use `.insert()` for drums and `.append()` for other instruments, music21 will miscalculate track lengths and create tracks that are 5-10× longer than intended (8 minutes instead of 1.5 minutes), with only the first 20-25% containing actual sound.

**The .append() method should only be used in rare cases where you have a single melodic line with no other instruments.**

```python
# WRONG: This plays kick, then 32 hats, then snare pattern (not layered!)
# for beat in range(16):
#     drums.append(note.Note(36, quarterLength=1.0))  # Kicks play first
# for eighth in range(32):
#     drums.append(note.Note(42, quarterLength=0.5))  # Hats play AFTER all kicks
# # Result: Timing is completely wrong!

# CORRECT: Use .insert() with explicit offsets for simultaneous layering
bars = 32
beats_per_bar = 4
total_beats = bars * beats_per_bar

# Layer 1: Four-on-the-floor kicks (every beat)
for beat in range(total_beats):
    offset = float(beat)  # Beat 0, 1, 2, 3, 4, 5, ...
    drums.insert(offset, note.Note(36, quarterLength=1.0))

# Layer 2: Snare on beats 2 and 4 of each bar
for bar in range(bars):
    # Snare on beat 2 (second beat of bar)
    offset = float(bar * beats_per_bar + 1)
    drums.insert(offset, note.Note(38, quarterLength=1.0))

    # Snare on beat 4 (fourth beat of bar)
    offset = float(bar * beats_per_bar + 3)
    drums.insert(offset, note.Note(38, quarterLength=1.0))

# Layer 3: Hi-hats on eighth notes (every 0.5 beats) - creates groove
for bar in range(bars):
    for eighth in range(8):  # 8 eighth notes per bar
        offset = float(bar * beats_per_bar) + (eighth * 0.5)

        if eighth % 2 == 0:
            # Closed hat on even eighths (on the beat)
            drums.insert(offset, note.Note(42, quarterLength=0.5))
        else:
            # Open hat on odd eighths (offbeat) - signature house groove
            drums.insert(offset, note.Note(46, quarterLength=0.5))

# Result: Properly layered four-on-the-floor with offbeat open hats
# Bar 0: Kicks at 0.0, 1.0, 2.0, 3.0
#        Snares at 1.0, 3.0 (on top of kicks)
#        Hats at 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5 (layered throughout)
```

### Reggae Specific Guidelines

**CRITICAL**: Reggae has a **unique rhythmic identity** that requires precise drum patterns, offbeat accents, and heavy bass. If you don't follow these rules, it won't sound like reggae.

**Drum Rules (Non-Negotiable)**:
- **"One Drop" pattern**: Kick drum on beat 3 ONLY (not beat 1), creating the signature reggae "drop"
- **Snare/Rimshot**: Beats 2 and 4 (or just beat 3 with the kick)
- **Hi-hats**: OFFBEAT eighth notes only (never on the beat), creating the "skank" rhythm
- **Cross-stick (note 37)**: Optional on beats 2 and 4 for classic sound
- **NO four-on-floor kicks** - this is house/electronic, not reggae

```python
# CORRECT Reggae "One Drop" Drum Pattern
bars = 32
beats_per_bar = 4

for bar in range(bars):
    for beat in range(beats_per_bar):
        offset = float(bar * beats_per_bar + beat)

        # Kick ONLY on beat 3 (the "drop")
        if beat == 2:  # Beat 3 in 0-indexed (0, 1, 2, 3)
            drums_part.insert(offset, note.Note(36, quarterLength=1.0))

        # Snare on beats 2 and 4
        if beat == 1 or beat == 3:
            drums_part.insert(offset, note.Note(38, quarterLength=1.0))

    # OFFBEAT hi-hats (the "skank") - CRITICAL for reggae feel
    for eighth in range(8):
        offset = float(bar * beats_per_bar) + (eighth * 0.5)
        # ONLY odd eighths (offbeat) - never on the beat
        if eighth % 2 == 1:  # 0.5, 1.5, 2.5, 3.5 (offbeat)
            drums_part.insert(offset, note.Note(42, quarterLength=0.5))

# WRONG - Four-on-floor (this is house, not reggae!)
# for beat in range(total_beats):
#     drums_part.insert(float(beat), note.Note(36, quarterLength=1.0))  # ❌ Kick on every beat
```

**Bass Rules (Non-Negotiable)**:
- **Heavy and prominent** - Bass is the lead instrument in reggae
- **Octave 1-2** (A1, C2, E2, F1, G1) - not too low, not too high
- **Syncopated rhythm** - plays between beats, not just on downbeats
- **Walking patterns** - moves between root, third, fifth of chords
- **Quarter to half notes** (1.0-2.0 quarterLength) - NOT whole notes like House

```python
# CORRECT Reggae Bass (Am-D-F-G progression, 8-bar pattern)
# This pattern has movement and syncopation - it "walks"
bass_pattern = [
    # Bar 1-2: Am (root A)
    ('A1', 1.0), ('A1', 0.5), ('C2', 0.5), ('A1', 2.0),  # Bar 1
    ('A1', 1.0), ('E2', 1.0), ('A1', 2.0),                # Bar 2

    # Bar 3-4: D (root D)
    ('D2', 1.0), ('D2', 0.5), ('F2', 0.5), ('D2', 2.0),  # Bar 3
    ('D2', 1.0), ('A1', 1.0), ('D2', 2.0),                # Bar 4

    # Bar 5-6: F (root F)
    ('F1', 1.0), ('F1', 0.5), ('A1', 0.5), ('F1', 2.0),  # Bar 5
    ('F1', 1.0), ('C2', 1.0), ('F1', 2.0),                # Bar 6

    # Bar 7-8: G (root G, with E for resolution)
    ('G1', 1.0), ('G1', 0.5), ('B1', 0.5), ('E2', 2.0),  # Bar 7
    ('G1', 1.0), ('D2', 1.0), ('E2', 2.0),                # Bar 8
]

# Use .insert() to place bass notes at explicit offsets (synchronizes with drums)
offset = 0.0
for repetition in range(bars // 8):
    for pitch, duration in bass_pattern:
        bass_part.insert(offset, note.Note(pitch, quarterLength=duration))
        offset += duration

# WRONG - Using .append() will cause 8-minute tracks when mixed with .insert() drums
# for pitch, duration in bass_pattern * (bars // 8):
#     bass_part.append(note.Note(pitch, quarterLength=duration))  # ❌ Causes timing bug!
```

**Guitar "Skank" Rules (Non-Negotiable)**:
- **OFFBEAT chords only** - plays on upbeats (the "and" of beats), never downbeats
- **CRITICAL: Sufficient duration** - Minimum 0.35-0.4 quarterLength (NOT 0.25) to be audible in mix
- **Mid-register voicings** - Octaves 3-4 (A3, C4, E4)
- **Muted/percussive** - In real reggae, these are muted strums creating rhythm

**⚠️ CRITICAL NOTE DURATION WARNING:**

At 0.25 quarterLength, guitar will be **completely inaudible** in the mix:
- At 82 BPM: `(60 / 82) × 0.25 = 0.183 seconds` (183 milliseconds)
- Human perceptual threshold: ~200-300ms needed to register in dense mix
- Organ plays at 0.5 (366ms) - TWICE as long

**Use 0.4 quarterLength minimum:**
- At 82 BPM: `(60 / 82) × 0.4 = 0.293 seconds` (293 milliseconds)
- Crosses perceptual threshold while maintaining staccato feel
- Adjust rest to 0.1 to maintain 1.0 beat total per skank cycle

```python
# CORRECT Reggae Guitar "Skank" (offbeat chords with AUDIBLE duration)
guitar_chords = [
    ['A3', 'C4', 'E4'],    # Am
    ['A3', 'C4', 'E4'],    # Am (repeat for 2 bars)
    ['D3', 'F#3', 'A3'],   # D
    ['D3', 'F#3', 'A3'],   # D (repeat for 2 bars)
    ['F3', 'A3', 'C4'],    # F
    ['F3', 'A3', 'C4'],    # F (repeat for 2 bars)
    ['G3', 'B3', 'D4'],    # G
    ['G3', 'B3', 'D4'],    # G (repeat for 2 bars)
]

# Use .insert() to place guitar at explicit offsets (synchronizes with drums/bass)
offset = 0.0
for repetition in range(bars // 8):
    for chord_notes in guitar_chords:
        # Each bar: 4 offbeat skanks
        for beat in range(4):
            # REST on the beat (downbeat)
            guitar_part.insert(offset, note.Rest(quarterLength=0.5))
            offset += 0.5
            # CHORD on the offbeat (upbeat) - 0.4 duration for audibility
            guitar_part.insert(offset, chord.Chord(chord_notes, quarterLength=0.4))
            offset += 0.4
            # SHORT REST after chord (creates staccato effect)
            guitar_part.insert(offset, note.Rest(quarterLength=0.1))
            offset += 0.1

# WRONG - Using .append() causes 8-minute tracks when mixed with .insert() drums
# guitar_part.append(chord.Chord(chord_notes, quarterLength=0.4))  # ❌ Causes timing bug!

# WRONG - Duration too short (will be inaudible!)
# guitar_part.insert(offset, chord.Chord(chord_notes, quarterLength=0.25))  # ❌ Only 183ms @ 82 BPM
```

**Organ "Bubble" Rules**:
- **Alternating on-and-off pattern** - Creates rhythmic "bubbling" effect
- **Higher register** (octaves 4-5) - Sits above guitar
- **Plays same chords as guitar** but different rhythm
- **Shorter duration** (0.5 quarterLength) with rests between

```python
# CORRECT Reggae Organ "Bubble"
organ_chords = [
    ['A4', 'C5', 'E5'],    # Am (high register)
    ['A4', 'C5', 'E5'],
    ['D4', 'F#4', 'A4'],   # D
    ['D4', 'F#4', 'A4'],
    ['F4', 'A4', 'C5'],    # F
    ['F4', 'A4', 'C5'],
    ['G4', 'B4', 'D5'],    # G
    ['G4', 'B4', 'D5'],
]

# Use .insert() to place organ at explicit offsets (synchronizes with drums/bass/guitar)
offset = 0.0
for repetition in range(bars // 8):
    for organ_chord in organ_chords:
        # Each bar: bubble pattern (chord, rest, chord, rest)
        for _ in range(2):  # Twice per bar
            organ_part.insert(offset, chord.Chord(organ_chord, quarterLength=0.5))
            offset += 0.5
            organ_part.insert(offset, note.Rest(quarterLength=0.5))
            offset += 0.5
            organ_part.insert(offset, chord.Chord(organ_chord, quarterLength=0.5))
            offset += 0.5
            organ_part.insert(offset, note.Rest(quarterLength=0.5))
            offset += 0.5

# WRONG - Using .append() causes 8-minute tracks when mixed with .insert() drums
# organ_part.append(chord.Chord(organ_chord, quarterLength=0.5))  # ❌ Causes timing bug!
```

**Reggae Instruments (MIDI Programs)**:
- **Drums**: Channel 9 (MIDI channel 10) - ALWAYS required
- **Bass**: Program 33 (Electric Bass - finger) or 34 (Electric Bass - pick)
- **Guitar**:
  - **PRIMARY: Program 25 (Acoustic Guitar - steel)** - Bright, percussive, cuts through mix
  - Alternative: Program 28 (Electric Guitar - muted) - Percussive skank sound
  - **⚠️ AVOID: Program 27 (Electric Guitar - clean)** - Recorded 12-15dB quieter in FluidR3_GM, will be inaudible even at velocity 95
- **Organ**: Program 16 (Drawbar Organ) or 17 (Percussive Organ)

**Setting Instruments with mido (CRITICAL)**:

Since reggae Parts don't use music21 instrument classes, you MUST use mido to INSERT program_change messages:

```python
from mido import MidiFile, Message

# After score.write('midi', fp=midi_path)
mid = MidiFile(midi_path)

for i, track in enumerate(mid.tracks):
    if i == 1:  # Drums track
        for msg in track:
            if hasattr(msg, 'channel'):
                msg.channel = 9  # Drums on channel 9
    elif i == 2:  # Bass track
        # INSERT program_change message (don't try to modify - it doesn't exist!)
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=33, time=0))
    elif i == 3:  # Guitar track
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=25, time=0))  # Acoustic steel - bright and audible
    elif i == 4:  # Organ track
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=16, time=0))

mid.save(midi_path)
```

**Mixing and Balance (CRITICAL - Guitar Will Be Inaudible Without This!)**:

Setting the correct instrument programs and velocities is NOT enough. In reggae, the **guitar will still be completely inaudible** if you don't address THREE issues:

1. **Soundfont level**: Program 27 (Electric Guitar - clean) recorded 12-15dB quieter than program 16 (Drawbar Organ) in FluidR3_GM
2. **Note duration**: 0.25 quarterLength = 183ms @ 82 BPM (below perceptual threshold)
3. **Velocity difference**: Need 40+ point separation

**Complete Solution**:
```python
def set_track_velocity(track, velocity):
    """Set velocity for all note_on messages in a track."""
    for msg in track:
        if msg.type == 'note_on' and msg.velocity > 0:
            msg.velocity = velocity

# After setting instruments, BEFORE saving
for i, track in enumerate(mid.tracks):
    if i == 1:  # Drums
        set_track_velocity(track, 70)
    elif i == 2:  # Bass - prominent in reggae
        set_track_velocity(track, 80)
    elif i == 3:  # Guitar - RHYTHM INSTRUMENT, needs to cut through
        # Use program 25 (steel acoustic) instead of 27 (too quiet)
        # Use 0.4 quarterLength instead of 0.25 (too short)
        set_track_velocity(track, 95)  # LOUD - this is critical!
    elif i == 4:  # Organ - BACKGROUND atmosphere
        set_track_velocity(track, 55)  # QUIET - don't overpower guitar

mid.save(midi_path)
```

**Why this THREE-PART solution works**:
- **Program 25 (Acoustic Guitar - steel)**: Recorded 8-10dB louder than program 27, bright harmonics, percussive attack
- **Duration 0.4 (293ms)**: Crosses perceptual threshold vs 0.25 (183ms) which is too short
- **Velocity 95 vs 55**: 40-point difference creates clear separation
- **Combined effect**: Guitar now has 3× more presence (program × duration × velocity)

**Tempo**: 70-90 BPM (classic roots reggae: 80-85 BPM, modern: 85-90 BPM)

**Common Mistakes**:
- Creating `drums_part` but calling `drums.insert()` - use correct variable name
- Trying to MODIFY `program_change` messages that don't exist - must INSERT them
- Not setting drums to channel 9 - drums will sound like melody notes
- **CRITICAL: Using program 27 (too quiet) instead of program 25**
- **CRITICAL: Using 0.25 quarterLength (too short) instead of 0.4**
- **CRITICAL: Not setting velocities - guitar will be completely inaudible, organ will dominate**

### House Specific Guidelines

**CRITICAL**: House requires **extreme repetition** and **minimal variation** to create the hypnotic, groovy feel. Standard composition rules don't apply.

**Bass Rules (Non-Negotiable)**:
- **ONE NOTE** held for 8-16 bars minimum (32.0-64.0 quarterLength)
- **Octave 1-2 RANGE** (A1, C2, E2, F1, G1) - the actual bass guitar range (55-110 Hz)
- **NEVER use octave 0** (A0, F0, G0, etc.) - these are 20-30 Hz sub-sonic frequencies inaudible on 99% of playback systems (laptop speakers, headphones, even many studio monitors can't reproduce them)
- **Whole notes or longer** (4.0+ quarterLength minimum, prefer 32.0+)
- **Simple patterns**: Root for 8 bars → Fifth for 8 bars → repeat
- **NO octave jumps**, **NO busy basslines**, **NO quarter notes**

```python
# CORRECT House Bass (audible on all playback systems)
bass_pattern = [
    ('A1', 32.0),  # A for 8 bars - 55 Hz (bass guitar's lowest note)
    ('E2', 32.0),  # E for 8 bars - 82 Hz (bass guitar's open E string)
    ('F1', 32.0),  # F for 8 bars - 43.7 Hz
    ('C2', 32.0),  # C for 8 bars - 65.4 Hz
]
for pitch, duration in bass_pattern:
    bass_part.append(note.Note(pitch, quarterLength=duration))

# WRONG - Octave 0 is inaudible on most systems!
bass_notes = ['A0', 'F0', 'C1', 'G0']  # ❌ 20-35 Hz - below hearing/speaker range!
for bar in range(8):
    bass_part.append(note.Note(bass_notes[bar % 4], quarterLength=32.0))  # ❌ Inaudible!

# ALSO WRONG - Too busy, octave jumps
bass_notes = ['A1', 'A2', 'C2', 'F1']  # ❌ Octave jumps
for bar in range(32):
    bass_part.append(note.Note(bass_notes[bar % 4], quarterLength=1.0))  # ❌ Too short!
```

**Pad Rules**:
- **ONE CHORD** held for 8-16 bars (32.0-64.0 quarterLength)
- **Mid-range octaves** (2-4): A2, C3, E3 voicings
- **Long attack/release** for smooth transitions
- Change chords rarely (every 8-16 bars, not every 4 bars)

```python
# CORRECT House Pads
pad_progression = [
    (['A2', 'C3', 'E3'], 64.0),  # Am for 16 bars
    (['F2', 'A2', 'C3'], 64.0),  # F for 16 bars
]
for chord_notes, duration in pad_progression:
    pad_part.append(chord.Chord(chord_notes, quarterLength=duration))
```

**Lead Rules**:
- **Sparse** - only play every 4-8 bars, lots of silence
- **Long notes** (4.0-16.0 quarterLength)
- **Enter late** (bar 16+, not immediately)
- **Mid octaves** (A4, C5, E5 max)

```python
# CORRECT House Lead (enters bar 16)
lead_pattern = [
    ('A4', 8.0),   # 2 bars
    ('C5', 8.0),   # 2 bars
    ('E5', 16.0),  # 4 bars
]
```

**Core Principle**: If it feels repetitive, you're doing it right. House = **hypnotic loop** repeated for minutes with **minimal changes**.

**Mixing and Balance**:

In House, the bass is the star. But if you don't control velocities, the pads and leads will overpower everything:

```python
def set_track_velocity(track, velocity):
    """Set velocity for all note_on messages in a track."""
    for msg in track:
        if msg.type == 'note_on' and msg.velocity > 0:
            msg.velocity = velocity

# After setting instruments with mido
for i, track in enumerate(mid.tracks):
    if i == 1:  # Drums
        set_track_velocity(track, 90)  # Driving rhythm
    elif i == 2:  # Bass (program 38, octaves 1-2)
        set_track_velocity(track, 75)  # Prominent but not overpowering
    elif i == 3:  # Pad (program 88, octaves 2-4)
        set_track_velocity(track, 50)  # Atmospheric background
    elif i == 4:  # Lead (program 80, octaves 4-5)
        set_track_velocity(track, 95)  # Melodic focus (when present)

mid.save(midi_path)
```

### Bassline Patterns

```python
# Groovy syncopated house bass
bass_pattern = [
    ('A1', 1.0),      # Downbeat
    ('A1', 0.5),      # Short hit
    ('rest', 0.25),   # Space
    ('A1', 0.25),     # Syncopation
    ('A2', 0.5),      # Octave jump
    ('C2', 0.5),      # Chord tone
    ('A1', 1.0)       # Resolution
]

for pitch, duration in bass_pattern:
    if pitch == 'rest':
        bass_part.append(note.Rest(quarterLength=duration))
    else:
        bass_part.append(note.Note(pitch, quarterLength=duration))
```

### Chord Voicings

```python
# Jazz voicing (7th chords)
jazz_chords = [
    ['C4', 'E4', 'G4', 'B4'],   # Cmaj7
    ['D4', 'F4', 'A4', 'C5'],   # Dm7
    ['G3', 'B3', 'D4', 'F4']    # G7
]

# House pad voicing (open, atmospheric)
house_pads = [
    ['A3', 'C4', 'E4'],         # Am
    ['F3', 'A3', 'C4'],         # F
    ['C3', 'E3', 'G3']          # C
]

# Classical voicing (close position)
classical_chords = [
    ['C4', 'E4', 'G4'],         # C major
    ['B3', 'D4', 'G4'],         # G major
    ['C4', 'F4', 'A4']          # F major
]
```

### Melody Construction

```python
# Pentatonic scale (versatile, no "wrong" notes)
pentatonic_c = ['C', 'D', 'E', 'G', 'A']

# Major scale
major_c = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Minor scale
minor_a = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

# Blues scale
blues_c = ['C', 'Eb', 'F', 'F#', 'G', 'Bb']

# Generate melody algorithmically
for i in range(16):
    octave = 4 + (i // 8)  # Move up octave halfway through
    scale_degree = i % len(pentatonic_c)
    pitch = pentatonic_c[scale_degree] + str(octave)
    melody.append(note.Note(pitch, quarterLength=0.5))
```

### Dynamic Control (Crescendos, Volume Changes)

```python
from music21 import dynamics

# Set initial volume
part.insert(0, dynamics.Dynamic('p'))   # Piano (soft)

# Add crescendo at bar 8
part.insert(32, dynamics.Crescendo())   # 32 quarter notes = 8 bars

# Peak at bar 10
part.insert(40, dynamics.Dynamic('ff'))  # Fortissimo (very loud)

# Decrescendo
part.insert(60, dynamics.Diminuendo())

# Return to soft
part.insert(72, dynamics.Dynamic('p'))

# Dynamic markings: ppp, pp, p, mp, mf, f, ff, fff
```

### Timing & Tempo

```python
# Set tempo (BPM)
part.insert(0, tempo.MetronomeMark(number=120))  # 120 BPM

# Tempo changes
part.insert(32, tempo.MetronomeMark(number=140))  # Speed up at bar 8

# Timing variations (humanization)
import random
note.Note('C5', quarterLength=1.0 + random.uniform(-0.05, 0.05))

# Common time signatures (set on first part)
from music21 import meter
part.insert(0, meter.TimeSignature('4/4'))  # Most common
part.insert(0, meter.TimeSignature('3/4'))  # Waltz
part.insert(0, meter.TimeSignature('6/8'))  # Compound meter
```

## Complete Example: Deep House Track

```python
from music21 import stream, note, chord, tempo
from mido import MidiFile
import subprocess

# 1. Compose with music21
score = stream.Score()
drums = stream.Part()
bass_part = stream.Part()
pad_part = stream.Part()
lead_part = stream.Part()

# Set tempo
drums.insert(0, tempo.MetronomeMark(number=122))

# Add drums using .insert() for proper layering (not .append()!)
bars = 32
beats_per_bar = 4

# Layer 1: Four-on-the-floor kicks
for bar in range(bars):
    for beat in range(beats_per_bar):
        offset = float(bar * beats_per_bar + beat)
        drums.insert(offset, note.Note(36, quarterLength=1.0))

# Layer 2: Snare on beats 2 and 4 of each bar
for bar in range(bars):
    drums.insert(float(bar * beats_per_bar + 1), note.Note(38, quarterLength=1.0))  # Beat 2
    drums.insert(float(bar * beats_per_bar + 3), note.Note(38, quarterLength=1.0))  # Beat 4

# Layer 3: Hi-hats on eighth notes (offbeat open hats for groove)
for bar in range(bars):
    for eighth in range(8):
        offset = float(bar * beats_per_bar) + (eighth * 0.5)
        if eighth % 2 == 0:
            drums.insert(offset, note.Note(42, quarterLength=0.5))  # Closed hat
        else:
            drums.insert(offset, note.Note(46, quarterLength=0.5))  # Open hat (offbeat)

# House BASS: Long sustained notes using .insert() (NOT .append())
bass_offset = 0.0
bass_pattern = [
    ('A1', 32.0),  # A root for 8 bars - 55 Hz (audible on all systems)
    ('E2', 32.0),  # E fifth for 8 bars - 82 Hz
    ('F1', 32.0),  # F for 8 bars - 43.7 Hz
    ('C2', 32.0),  # C for 8 bars - 65.4 Hz
]

for pitch, duration in bass_pattern:
    bass_part.insert(bass_offset, note.Note(pitch, quarterLength=duration))
    bass_offset += duration

# House PADS: Long sustained chords using .insert() (NOT .append())
pad_offset = 0.0
pad_progression = [
    (['A2', 'C3', 'E3'], 64.0),  # Am for 16 bars
    (['F2', 'A2', 'C3'], 64.0),  # F for 16 bars
]

for chord_notes, duration in pad_progression:
    pad_part.insert(pad_offset, chord.Chord(chord_notes, quarterLength=duration))
    pad_offset += duration

# House LEAD: Sparse, long notes, enters late using .insert() (NOT .append())
lead_pattern = [
    ('A4', 8.0),   # 2 bars
    ('C5', 8.0),   # 2 bars
    ('E5', 16.0),  # 4 bars (long sustain)
]

# Lead enters at bar 16 (64 beats in)
lead_offset = 64.0
for pitch, duration in lead_pattern:
    lead_part.insert(lead_offset, note.Note(pitch, quarterLength=duration))
    lead_offset += duration

score.append(drums)
score.append(bass_part)
score.append(pad_part)
score.append(lead_part)

midi_path = '/mnt/user-data/outputs/deep_house_track.mid'
score.write('midi', fp=midi_path)

# 2. Fix instruments with mido (INSERT program_change messages)
from mido import Message
mid = MidiFile(midi_path)

for i, track in enumerate(mid.tracks):
    if i == 1:  # Drums track
        for msg in track:
            if hasattr(msg, 'channel'):
                msg.channel = 9  # Drums must be on channel 9
    elif i == 2:  # Bass track - INSERT program_change
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=38, time=0))
    elif i == 3:  # Pad track - INSERT program_change
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=88, time=0))
    elif i == 4:  # Lead track - INSERT program_change
        insert_pos = 0
        for j, msg in enumerate(track):
            if msg.type == 'track_name':
                insert_pos = j + 1
                break
        track.insert(insert_pos, Message('program_change', program=81, time=0))

mid.save(midi_path)

# 3. Render with ELECTRONIC pipeline with deep_house preset!
mp3_path = '/mnt/user-data/outputs/deep_house_track.mp3'

result = subprocess.run([
    'python',
    '/mnt/skills/private/music-generation/scripts/render_electronic.py',
    midi_path,
    mp3_path,
    '--genre', 'deep_house'
], capture_output=True, text=True)

print(result.stdout)
if result.returncode == 0:
    print(f"✓ House track created: {mp3_path}")
else:
    print(f"Error: {result.stderr}")
```

**House Characteristics in This Example:**
- **Bass**: ONE note (A1, E2, F1, C2) held for 8 bars each - deep bass in octave 1-2 (55-82 Hz range, audible on all playback systems)
- **Pads**: ONE chord held for 16 bars - extreme sustain creates hypnotic atmosphere
- **Lead**: Sparse (enters bar 16), long notes (2-4 bars each) - not busy
- **Repetition**: Minimal variation = hypnotic, groovy House feel
- Uses `render_electronic.py` with `deep_house` preset for warm, subby synthesis
- Bass synthesized with proper low-end frequencies that consumer audio equipment can reproduce
- Pads use slow attack (0.9s) and long release (1.2s) for smooth transitions
- Genre preset automatically tunes all synthesis parameters
- No external samples or soundfonts needed - fully self-contained

## Best Practices

### Composition Quality
- **Generate variety**: Don't repeat the same 4 bars for entire piece
- **Use music theory**: Real chord progressions, proper voice leading
- **Respect instrument ranges**: Violin (G3-E7), Cello (C2-C6), Trumpet (E3-C6)
- **Add dynamics**: Use p, mp, mf, f, ff markings and crescendos
- **Structure**: Intro → Development → Climax → Resolution
- **Add humanization**: Vary timing and velocity to avoid robotic sound
  ```python
  import random
  n = note.Note('C5', quarterLength=1.0 + random.uniform(-0.05, 0.05))
  n.volume.velocity = 80 + random.randint(-5, 5)
  ```

### Technical Quality
- **SoundFont**: Use FluidR3_GM.sf2 for best quality
- **Bitrate**: 192kbps minimum, 320kbps for high quality
- **Timing precision**: Use quarterLength values carefully
- **Cleanup**: Remove temporary MIDI/WAV files after MP3 conversion

### Common Pitfalls
- **CRITICAL: Always use .insert() for ALL tracks** - Never mix `.insert()` and `.append()`. See "Drum Programming" section for details
- **CRITICAL: INSERT program_change messages** - Use `track.insert(pos, Message('program_change', ...))` not `msg.program = X`. See mido Quick Reference
- **CRITICAL: Set velocities** - Lead 90-105, background 50-65. See "Mixing and Balance" section
- **CRITICAL: Bass octaves** - Use A1-A2 (55-110 Hz), never A0-G0 (inaudible on most systems)
- **instrument.Cello()** doesn't exist - use `Violoncello()`
- **Forgetting tempo** - Add `tempo.MetronomeMark()` to first part
- **Drums not sounding like drums** - Set channel to 9 with mido (see mido Quick Reference)

## Mixing and Balance

**CRITICAL**: Setting MIDI program numbers alone is not enough. Without explicit velocity control, some instruments will be **completely inaudible**.

### Setting Velocities

music21 uses default velocity 64 for all notes, which causes poor mixing. Use mido to set velocities after MIDI export:

```python
from mido import MidiFile

def set_track_velocity(track, velocity):
    """Set velocity for all note_on messages in a track."""
    for msg in track:
        if msg.type == 'note_on' and msg.velocity > 0:
            msg.velocity = velocity

mid = MidiFile(midi_path)
for i, track in enumerate(mid.tracks):
    if i == 1:  # Drums
        set_track_velocity(track, 75)
    elif i == 2:  # Bass
        set_track_velocity(track, 80)
    elif i == 3:  # Lead instrument (sax, guitar, trumpet)
        set_track_velocity(track, 95)
    elif i == 4:  # Background (organ, pads)
        set_track_velocity(track, 55)
mid.save(midi_path)
```

### Velocity Guidelines

**By Role:**
- Lead instruments (melody, solos): **90-105**
- Rhythm instruments (guitar skanks, comping): **85-100**
- Bass: **75-85**
- Drums: **70-90**
- Background (pads, organs): **50-65**

**By Frequency Range:**
- **Low (20-250 Hz)**: Bass, kick - only ONE dominant at 75-85
- **Mid (250-2000 Hz)**: Most crowded - use velocity to separate (lead 90+, background 50-65)
- **High (2000+ Hz)**: Hi-hats, cymbals - 70-85 for clarity without harshness

### Soundfont Level Issues

FluidR3_GM instruments are recorded at different levels. Even with correct velocities, some instruments may be inaudible:

**Quiet programs** (avoid for lead/rhythm):
- Program 27 (Electric Guitar - clean) - Very quiet
- Program 24 (Acoustic Guitar - nylon)
- Program 73 (Flute)

**Better alternatives**:
- Program 25 (Acoustic Guitar - steel) - 8-10dB louder, cuts through
- Program 28 (Electric Guitar - muted) - Percussive
- Program 30 (Distortion Guitar) - Aggressive

**Additional fixes:**
- Increase note duration (0.4 quarterLength minimum vs 0.25)
- Use octave separation (move competing instruments to different octaves)
- Extreme velocity contrast (quiet instrument at 110, loud at 40)

### Mixing Checklist

Before rendering:
- ✅ Lead at velocity 90-105
- ✅ Background at velocity 50-65
- ✅ Bass at velocity 75-85
- ✅ Check for quiet instruments (programs 24, 27, 73) and use alternatives
- ✅ Minimum 0.4 quarterLength for rhythm instruments

## Resources

- **music21 Documentation**: https://web.mit.edu/music21/doc/
- **General MIDI Spec**: https://www.midi.org/specifications-old/item/gm-level-1-sound-set
- **Music Theory**: https://www.musictheory.net/
- **IMSLP (Free Scores)**: https://imslp.org/ - Download classical MIDIs here!

## Limitations

- **Instrumental only** - No lyrics/vocals
- **MIDI-based synthesis** - Not studio-quality recordings
- **No real-time playback** - Files must be rendered before playback
- **SoundFont quality** - Good but not as realistic as sample libraries

## When to Use This Skill

✅ User requests:
- Original compositions with specific moods/styles
- Classical music in MP3 format
- Timed music for videos/presentations
- Specific instrumentation (orchestral, piano, strings, etc.)
- Dynamic music with crescendos, tempo changes

❌ Not suitable for:
- Vocal/lyrical music
- Audio mixing/mastering (reverb, EQ, compression)
- Real-time MIDI playback
- Professional studio recording quality