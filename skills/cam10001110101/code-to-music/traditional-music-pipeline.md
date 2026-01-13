# Traditional Music Generation Pipeline

**Prerequisites**: Before using this pipeline, the generic music21 and MIDI content in SKILL.md should have been read, including:
- Basic music21 composition patterns
- Complete GM Instrument Map (programs 0-127)
- Complete Drum Map (notes 35-81)
- mido workflow for setting instruments and velocities
- Generic music theory (chord progressions, scales, timing)

## How the Traditional Pipeline Works

The traditional pipeline uses pre-recorded samples from soundfonts to render acoustic instruments:

```python
# After composing with music21 and exporting MIDI...
from midi2audio import FluidSynth
from pydub import AudioSegment

fs = FluidSynth('/usr/share/sounds/sf2/FluidR3_GM.sf2')
fs.midi_to_audio(midi_path, wav_path)

audio = AudioSegment.from_wav(wav_path)
# Note: You should make sure dynamic range compression is applied to prevent clipping
audio.export(mp3_path, format='mp3', bitrate='192k')
```

### Available Soundfonts

- `/usr/share/sounds/sf2/FluidR3_GM.sf2` (141MB, General MIDI soundfont for orchestral/classical)
- `/usr/share/sounds/sf2/default.sf2` (symlink to best available)

## Rendering Traditional Music

The traditional pipeline uses pre-recorded samples from soundfonts:

**Conceptual workflow:**
1. Compose with music21 (create parts, add notes/chords)
2. Export to MIDI
3. **CRITICAL: ALWAYS use mido to set instruments and velocities** - even if music21 instrument classes like `instrument.TenorSaxophone()` or `instrument.AcousticGuitar()` were used, mido MUST still be used to set program numbers. Without this step, all tracks will default to piano.
4. Render MIDI to WAV using FluidSynth
5. Convert WAV to MP3 with pydub

## Advanced Workflow: Learning from Existing MIDI

For classical pieces or complex compositions, the following approach can be used:

### 1. Extract Structure from ANY MIDI File

```bash
python ./scripts/midi_inventory.py \
    path/to/mozart.mid \
    path/to/output_structure.json  # Output path for extracted structure
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
with open('path/to/output_structure.json', 'r') as f:
    structure = json.load(f)

# Modify instruments, notes, timing, etc.
structure['tracks']['track-0']['instrument'] = 'violin'  # Change piano to violin!

# Save modified structure
with open('path/to/modified_structure.json', 'w') as f:
    json.dump(structure, f)
```

### 3. Render Modified Structure to MP3

```bash
python ./scripts/midi_render.py \
    path/to/modified_structure.json \
    path/to/output.mp3  # Final MP3 output path
```

**This workflow allows "recreating" any classical piece with different instruments!**

### Additional Scripts

- **`midi_transform.py`** - Generic MIDI transformations (transpose, tempo change, instrument swap)
- **`audio_validate.py`** - Validate audio file quality and format

## music21 Instrument Classes

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
```

### Common mistakes:
- **CRITICAL**: Using music21 instrument classes (like `instrument.TenorSaxophone()` or `instrument.AcousticGuitar()`) but forgetting to ALSO set programs with mido afterwards - the track will sound like piano (program 0) instead of your intended instrument
- instrument.Cello() doesn't exist - use Violoncello()
- instrument.FrenchHorn() doesn't exist - use Horn()
- Setting part.partName doesn't change the sound - MIDI program must be set with mido
- Drums on channel 0 will play as pitched notes, not drum sounds

## Traditional-Specific Mixing and Balance

**CRITICAL**: Setting MIDI program numbers alone is not enough. Without explicit velocity control, some instruments will be **completely inaudible**.

### Setting Velocities

music21 uses default velocity 64 for all notes, which causes poor mixing. Use mido to set velocities after MIDI export:

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
- Lead at velocity 90-105
- Background at velocity 50-65
- Bass at velocity 75-85
- Check for quiet instruments (programs 24, 27, 73) and use alternatives
- Minimum 0.4 quarterLength for rhythm instruments

## Best Practices for Traditional Music

- **ALWAYS use mido to set program numbers for ALL tracks** (even if music21 instrument classes were used)
- You can optionally use music21 instrument classes for documentation (Violin, Piano, etc.) but they don't set the MIDI program
- Respect instrument ranges (Violin G3-E7, Cello C2-C6, Trumpet E3-C6)
- Watch for soundfont level issues (program 27 too quiet, use 25 instead)
- Use 0.4+ quarterLength for rhythm instruments (below this is inaudible)
- Set velocities explicitly with mido: lead 90-105, rhythm 85-100, background 50-65
- **CRITICAL: For acoustic guitar (programs 24-31), use individual `note.Note()` calls, NOT `chord.Chord()`**. The FluidR3_GM soundfont renders guitar chords with a keyboard/piano-like timbre. Use arpeggiated notes instead for authentic guitar sound.
- **For fingerpicked acoustic guitar, use the proper register: bass notes D3-A3, treble notes G3-D5**. Notes below D3 sound muddy and keyboard-like in the FluidR3_GM soundfont. Standard guitar range is E2-E5, but fingerpicking sounds best in the mid-to-high register.