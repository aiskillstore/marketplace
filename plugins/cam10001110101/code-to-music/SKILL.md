---
name: code-to-music
description: Tools, patterns, and utilities for creating music with code. Output as a .mp3 file with realistic instrument sounds. Write custom compositions to bring creativity to life through music. This skill should be used whenever the user asks for music to be created. Never use this skill for replicating songs, beats, riffs, or other sensitive works. The skill is not suitable for vocal/lyrical music, audio mixing/mastering (reverb, EQ, compression), real-time MIDI playback, or professional studio recording quality.
---

This skill provides **tools and patterns** for music composition, not pre-baked solutions. The intelligence and music21 library should be used to compose dynamically based on user requests.

**Core Principle**: Write custom code that composes music algorithmically rather than calling functions with hardcoded melodies.

## Installation & Setup

### Quick Installation

Run the automated installer for complete setup: `install.sh`. This installs all system dependencies, Python packages, and verifies the installation.

**Note:** The install script may display "error: externally-managed-environment" messages at the end. These are expected and can be safely ignored - the dependencies are already installed. If such messages appear, the installation was successful.

### Available SoundFonts

**Traditional Pipeline (Orchestral/Acoustic):**
- **`/usr/share/sounds/sf2/FluidR3_GM.sf2`** (141MB, General MIDI soundfont - use for high-quality orchestral/acoustic samples)
- `/usr/share/sounds/sf2/default.sf2` (symlink to best available)
- ⚠️ **DO NOT use TimGM6mb.sf2** - inferior quality, guitars sound electronic/piano-like

**Electronic Pipeline:**
- Uses the same FluidR3_GM.sf2 soundfont as traditional music
- The difference is which GM programs you choose (synth programs 38-39, 80-95 instead of orchestral)

### Key Concepts

- **Always create downloadable MP3 files** (not HTML players)
- **music21.instrument classes can be used** for convenience: `instrument.Violin()`, `instrument.Violoncello()`, `instrument.Piano()`, `instrument.Trumpet()`, etc.
- **CRITICAL: ALWAYS use mido to set MIDI program numbers after export** - music21's instrument classes do NOT reliably export program_change messages. See the mido workflow below.
- **Generate notes programmatically** - avoid hardcoded sequences

## Choosing Your Music Generation Pipeline

This skill supports TWO rendering pipelines optimized for different musical styles. Read the user's request carefully and choose the correct pipeline by reading the correct next file.

### Decision Process

Identify from the user's request:
- Genre keywords (house, techno, classical, orchestral, reggae)
- Instrument references (synthesizers vs acoustic instruments)
- Musical style descriptions (electronic/DJ vs traditional/acoustic)
- Artist mentions (DJs vs classical composers)

### Electronic Pipeline

**Use `electronic-music-pipeline.md` when request includes:**

- **Genres**: House, techno, trance, EDM, electronic dance music, ambient electronic, acid house, deep house, club music, DJ sets
- **Instruments**: Synthesizers, synth bass/pads/leads, 808 drums, electronic drums, supersaw leads, sub-bass
- **Context**: References to DJs (Keinemusik, Black Coffee, Avicii, Swedish House Mafia), BPM 120-140, "for a club", "for dancing"
- **Sound descriptions**: "Fat synth sound", "buzzy leads", "electronic", "synth-heavy"

**How it works:**
- Uses real-time synthesis (no soundfonts)
- Synthesizes drums, bass, pads, leads on-the-fly with DSP
- Genre presets optimize synthesis parameters (deep_house, techno, trance, ambient, acid_house)
- Frequency-aware mixing automatically balances low/mid/high frequencies
- Best for: Authentic electronic sounds, modern EDM production

**→ See `electronic-music-pipeline.md` for detailed instructions**

---

### Traditional Pipeline

**Use `traditional-music-pipeline.md` when request includes:**

- **Genres**: Classical, orchestral, jazz, blues, rock, country, folk, reggae, ska, symphonic, chamber music
- **Instruments**: Violin, cello, trumpet, flute, piano, acoustic guitar, acoustic bass, brass ensembles, string quartets, organ (reggae/gospel)
- **Context**: References to composers (Mozart, Beethoven, Bach), classical periods (Baroque, Romantic), "unplugged", "acoustic version"
- **Sound descriptions**: "Traditional", "acoustic", "orchestral"

**How it works:**
- Uses pre-recorded orchestral samples (soundfonts)
- FluidR3_GM.sf2 soundfont with 128 General MIDI instruments
- Good for realistic orchestral/acoustic instruments
- Best for: Classical, jazz, reggae, rock, traditional music

**→ See `traditional-music-pipeline.md` for detailed instructions**

---

### If Unclear

- **Default to TRADITIONAL** for mixed requests or ambiguous genres
- **Ask user for clarification** if request could go either way

### Why This Matters

- **Using wrong pipeline** = poor audio quality (technically works, sounds bad)
- Electronic pipeline: Real-time synthesis for authentic electronic sounds
- Traditional pipeline: Pre-recorded samples for realistic orchestral/acoustic

## Available Scripts

All scripts are located in `./scripts`:

**Traditional Rendering:**
- **`midi_inventory.py`** - Extract complete structure from ANY MIDI file to JSON format
- **`midi_render.py`** - Render JSON music structure to MP3 using FluidSynth with dynamic range compression
- **`midi_utils.py`** - MIDI utility functions (extract drums, get BPM, etc.)

**Utilities:**
- **`audio_validate.py`** - Validate audio file quality and format

**Note**: Both electronic and traditional music use the same rendering pipeline (FluidSynth + FluidR3_GM.sf2). The difference is which GM programs you choose.

## Music Theory Reference

### Complete General MIDI Instrument Map (Programs 0-127)

**CRITICAL: music21 does NOT reliably export program_change messages. You MUST ALWAYS use mido to set program numbers after export, even for traditional instruments like saxophone, guitar, or bass. Without this step, tracks will default to piano (program 0).**

**INSTRUMENT CATEGORIZATION FOR SYNTHESIS:**
When composing electronic music, classify instruments by their sonic characteristics for proper synthesis:
- **Guitar (24-31)**: Plucky attack, bright tone, medium sustain - needs distinct synthesis from pads
- **Bass (32-39)**: Low-frequency fundamentals, sub-bass energy, short attack
- **Strings (40-47)**: Sustained bowing, rich harmonics, smooth legato
- **Brass (56-63)**: Bright attack, sustained tone, powerful projection
- **Reed/Woodwinds (64-79)**: Breathy attack, organic timbre, expressive dynamics
- **Synth Lead (80-87)**: Bright, cutting, aggressive - designed for melody
- **Synth Pad (88-95)**: Soft attack, long sustain, atmospheric - designed for background
- **Ethnic/Percussive (104-119)**: Plucky or struck sounds with unique timbres

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

**CRITICAL RULE**: music21 does NOT reliably export `program_change` messages, even when using instrument classes like `instrument.TenorSaxophone()` or `instrument.AcousticGuitar()`. mido MUST ALWAYS be used to INSERT program_change messages manually after exporting to MIDI. Without this step, all tracks will sound like piano (program 0).

**Common mistake**: Assuming that `sax_part.insert(0, instrument.TenorSaxophone())` will automatically make the track sound like a saxophone. It won't! mido must still be used to set the program number.

**Helper Function for Setting Instruments**:

```python
from mido import Message

def set_track_instrument(track, program):
    """Insert a program_change message at the beginning of a MIDI track."""
    # Find position after all meta messages (track_name, etc.)
    insert_pos = 0
    for j, msg in enumerate(track):
        if not msg.is_meta:  # Insert before first non-meta message
            insert_pos = j
            break
    else:
        # If all messages are meta, insert at end
        insert_pos = len(track)
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

# Add your notes/chords using .insert() with explicit timing
# CRITICAL: Always use .insert(offset, note) not .append(note)
offset = 0.0
synth_lead.insert(offset, note.Note('E5', quarterLength=1.0))
offset += 1.0
synth_lead.insert(offset, note.Note('G5', quarterLength=1.0))
# ... compose your music with .insert()

score.append(synth_lead)
score.append(synth_pad)
score.append(bass)

# Export to MIDI
midi_path = # define a output path
score.write('midi', fp=midi_path)
```

**Step 2: Inspect MIDI structure and assign instruments with mido**
```python
from mido import MidiFile, Message

mid = MidiFile(midi_path)

# CRITICAL: DO NOT assume track numbers! Inspect the MIDI file first.
# Print track structure to see what tracks exist
print(f"Total tracks: {len(mid.tracks)}")
for i, track in enumerate(mid.tracks):
    note_count = sum(1 for msg in track if msg.type == 'note_on' and msg.velocity > 0)
    print(f"Track {i}: {note_count} notes")

# Helper function to set instruments
def set_track_instrument(track, program):
    """Insert a program_change message at the beginning of a MIDI track."""
    insert_pos = 0
    for j, msg in enumerate(track):
        if not msg.is_meta:
            insert_pos = j
            break
    else:
        insert_pos = len(track)
    track.insert(insert_pos, Message('program_change', program=program, time=0))

# Based on inspection, assign instruments to the correct tracks
# Example: if [drums, bass, guitar] were appended and inspection shows tracks 1, 2, 3 have notes:
set_track_instrument(mid.tracks[1], 80)  # First part - Square Lead
set_track_instrument(mid.tracks[2], 88)  # Second part - Pad
set_track_instrument(mid.tracks[3], 38)  # Third part - Bass

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
wav_path = # define a path here
fs.midi_to_audio(midi_path, wav_path)

audio = AudioSegment.from_wav(wav_path)
mp3_path = # define a path here
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
# For synths, drums, and electronic sounds, the following steps must be taken:
# 1. Create a Part without an instrument (or use a placeholder like Piano())
# 2. Use mido library to INSERT program_change messages after export
# 3. Set drums to MIDI channel 10 (channel 9 in 0-indexed) or they won't sound like drums
#
# Common mistakes:
# - instrument.Cello() doesn't exist - use Violoncello()
# - instrument.FrenchHorn() doesn't exist - use Horn()
# - Setting part.partName doesn't change the sound - MIDI program must be set with mido
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

# Define helper function
def set_track_instrument(track, program):
    """Insert a program_change message at the beginning of a MIDI track."""
    insert_pos = 0
    for j, msg in enumerate(track):
        if not msg.is_meta:
            insert_pos = j
            break
    else:
        insert_pos = len(track)
    track.insert(insert_pos, Message('program_change', program=program, time=0))

# Insert program_change messages
for i, track in enumerate(mid.tracks):
    if i == 1:  # Your track (tracks start at 1, not 0)
        set_track_instrument(track, 38)  # Synth Bass 1

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

**CRITICAL**: music21's `.append()` adds notes **sequentially** (one after another), not simultaneously. For layered drums where kicks, snares, and hats play at the same time, `.insert(offset, note)` MUST be used with explicit timing.

**ALWAYS USE .insert() FOR ADDING NOTES TO PARTS:**

Since layering is needed for nearly all good music composition, **part.insert(offset, note) MUST ALWAYS be used for ALL tracks** - drums, bass, guitar, pads, everything. This prevents timing bugs and ensures proper synchronization.

**NEVER mix .insert() and .append() when adding notes to parts** - If `.insert()` is used for drums and `.append()` for other instruments, music21 will miscalculate track lengths and create tracks that are 5-10× longer than intended (8 minutes instead of 1.5 minutes), with only the first 20-25% containing actual sound.

**Note**: Using `score.append(part)` to add Parts to the Score is fine - the issue is specifically about adding **notes/chords to Parts**, not adding Parts to Scores.

**Correct Pattern:**
```python
# RIGHT: Use .insert() for notes, .append() for parts
drum_part = stream.Part()
bass_part = stream.Part()

offset = 0.0
for beat in range(16):
    # Kick and hi-hat on same beat (layered)
    drum_part.insert(offset, note.Note(36, quarterLength=0.5))  # Kick
    drum_part.insert(offset, note.Note(42, quarterLength=0.5))  # Hi-hat

    # Bass note
    bass_part.insert(offset, note.Note('A2', quarterLength=0.5))

    offset += 0.5  # Advance time

# Add parts to score (this .append() is fine)
score.append(drum_part)
score.append(bass_part)
```

### Ensuring Complete Bar Coverage

**CRITICAL**: When composing with loops, ensure your notes completely fill each bar without gaps. A common mistake is placing notes that don't span the full bar duration, leaving silent gaps.

**Problem Pattern** (creates gaps):
```python
bar_length = 1.5  # 6/8 time signature
offset = 0.0

for bar in range(8):
    # Only fills first 1.0 quarter lengths, leaving 0.5 silent!
    guitar_part.insert(offset, note.Note('D3', quarterLength=0.5))
    guitar_part.insert(offset + 0.5, chord.Chord(['D3', 'F#3', 'A3'], quarterLength=0.5))
    # Missing: offset + 1.0 to offset + 1.5

    offset += bar_length  # Advances to next bar, but gap remains

# Result: Guitar plays for 10 seconds, then silence for remaining duration
```

**Solution Pattern** (complete coverage):
```python
bar_length = 1.5  # 6/8 time signature
offset = 0.0

for bar in range(8):
    # Fill the ENTIRE bar with notes
    guitar_part.insert(offset, note.Note('D3', quarterLength=0.5))           # 0.0 to 0.5
    guitar_part.insert(offset + 0.5, chord.Chord(['D3', 'F#3', 'A3'], quarterLength=0.5))  # 0.5 to 1.0
    guitar_part.insert(offset + 1.0, note.Note('D3', quarterLength=0.5))     # 1.0 to 1.5 ✓ Complete!

    offset += bar_length

# Result: Guitar plays continuously throughout the entire piece
```

**Best Practice**: Before advancing `offset += bar_length`, verify that your last note ends exactly at `offset + bar_length`. For example:
- If `bar_length = 1.5`, your last note should start at `offset + 1.0` with `quarterLength=0.5` to reach `offset + 1.5`
- If `bar_length = 2.0`, your last note should start at `offset + 1.5` with `quarterLength=0.5` to reach `offset + 2.0`

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
- **Limiting**: Applied via `audio.compress_dynamic_range()` to prevent clipping
- **Timing precision**: Use quarterLength values carefully
- **Cleanup**: Remove temporary MIDI/WAV files after MP3 conversion

### Common Pitfalls
- **CRITICAL: NEVER assume track numbers** - DO NOT blindly use `if i == 3` for guitar. ALWAYS inspect the MIDI file first with note counts to verify which track is which
- **CRITICAL: Always use part.insert(offset, note) for adding notes to parts** - Never use `part.append(note)` or mix `.insert()` and `.append()`. This causes timing bugs where tracks are 5-10x longer than intended with only 20-25% containing sound. See "Drum Programming" section for details
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