# Electronic Music Generation Pipeline

**Prerequisites**: Before using this pipeline, the generic music21 and MIDI content in SKILL.md should have been read, including:
- Basic music21 composition patterns
- Complete GM Instrument Map (programs 0-127)
- Complete Drum Map (notes 35-81)
- mido workflow for setting instruments
- Generic music theory (chord progressions, scales, timing)

## How the Electronic Pipeline Works

**Key principle**: Electronic music uses the SAME FluidR3_GM soundfont and rendering pipeline as traditional music. The difference is in **which GM instruments are chosen**.

**Why it works:**
- FluidR3_GM includes dedicated synth programs (38-39 for bass, 80-87 for leads, 88-95 for pads)
- Channel 10 drums include 808-style electronic drum sounds
- The soundfont was designed with both traditional AND electronic music in mind

**The "terrible electronic sound" myth**: The soundfont only sounds bad if wrong programs are used (like Violin for a synth lead). Programs 38-39, 80-95 should be used for authentic electronic sound.

## Rendering Electronic Music

Electronic music uses the SAME rendering pipeline as traditional music:

```python
from music21 import stream, note, tempo
from mido import MidiFile, Message
from midi2audio import FluidSynth
from pydub import AudioSegment

# 1. Compose with music21
score = stream.Score()
# ... compose your parts

# 2. Export MIDI
midi_path = "/path/to/output.mid"
score.write('midi', fp=midi_path)

# 3. Set instruments with mido (CRITICAL!)
def set_track_instrument(track, program):
    insert_pos = 0
    for j, msg in enumerate(track):
        if not msg.is_meta:
            insert_pos = j
            break
    else:
        insert_pos = len(track)
    track.insert(insert_pos, Message('program_change', program=program, time=0))

mid = MidiFile(midi_path)
# Inspect and set programs for each track
# ...

mid.save(midi_path)

# 4. Render with FluidSynth (same as traditional)
wav_path = "/path/to/output.wav"
mp3_path = "/path/to/output.mp3"

fs = FluidSynth('/usr/share/sounds/sf2/FluidR3_GM.sf2')
fs.midi_to_audio(midi_path, wav_path)

audio = AudioSegment.from_wav(wav_path)
# Note: Dynamic range compression is automatically applied to prevent clipping
audio.export(mp3_path, format='mp3', bitrate='192k')
```

## Choosing Electronic Instruments

**CRITICAL**: The key to electronic music is choosing the right GM programs. FluidR3_GM includes authentic electronic sounds.

### Core Electronic Programs

**Bass (use these for electronic bass):**
- **38: Synth Bass 1** (fat, warm - best for house/techno)
- **39: Synth Bass 2** (bright, aggressive - good for trance/acid)
- 32-37: Acoustic/electric bass (for more organic styles)

**Lead (use these for melodic lines):**
- **80: Square Lead** (classic chip-tune/retro style)
- **81: Sawtooth Lead** (bright, buzzy - most versatile for EDM)
- 82: Calliope Lead (circus-like, bright)
- 83: Chiff Lead (breathy attack)
- 84: Charang Lead (aggressive, distorted)
- 85-87: Other synth leads

**Pad (use these for atmospheric backgrounds):**
- **88: Pad 1 (New Age)** (soft, warm - best for house)
- **89: Pad 2 (Warm)** (rich, full background)
- **90: Pad 3 (Polysynth)** (bright, present - good for trance)
- 91: Pad 4 (Choir) (vocal-like)
- 92-95: Other atmospheric pads

**Additional Electronic Sounds:**
- 50-51: Synth Strings (electronic string sounds)
- 62-63: Synth Brass (electronic brass sounds)
- 96-103: FX sounds (rain, soundtrack, crystal, atmosphere, etc.)

### Using Non-Synth Programs in Electronic Music

**IMPORTANT**: You can (and should) use traditional instrument programs when appropriate. The key is matching the program to your musical intent:

**Guitars (24-31) work great for:**
- Rhythm guitar parts in electronic-rock fusion
- Plucky melodic riffs
- Strummed chord progressions
- **Programs 24-31 are fully supported** - don't avoid them

**Strings/Brass/Woodwinds (40-79) work for:**
- Orchestral stabs and hits
- Melodic counterpoint
- Adding organic texture to electronic beats
- Buildups and transitions

**Ethnic instruments (104-111) work for:**
- World music fusion (sitar, koto, shamisen)
- Unique plucky textures

### Instrument Selection Guidelines

1. **Match program to sonic role**:
   - Plucky rhythm → Guitar (25), Synth Lead (80-81)
   - Smooth background → Pad (88-90), Strings (48-49)
   - Melodic lead → Synth Lead (80-87), Brass (56-60), Sax (64-67)
   - Sub-bass → Synth Bass (38-39)

2. **Don't limit yourself to programs 38-39, 80-95**:
   - House music with acoustic guitar (25) = authentic
   - Trance with strings (48) = classic sound
   - Techno with brass stabs (61) = proper

3. **ALL GM instruments are available**:
   - Guitar programs 24-31 are fully supported
   - Strings 40-47 work perfectly
   - Brass 56-63, woodwinds 64-79 all render correctly

## Handling All General MIDI Instruments

When composing electronic music, the agent will classify instruments by sonic characteristics:

**Fast attack, plucky (guitars, harps, ethnic):**
- Programs 24-31 (Guitars)
- Programs 46, 104-111 (Harp, Sitar, Banjo, Koto)
- Work well for: rhythm parts, strums, melodic riffs

**Sustained melody (strings, brass, woodwinds):**
- Programs 40-47 (Strings)
- Programs 56-63 (Brass)
- Programs 64-79 (Woodwinds)
- Work well for: lead melodies, sustained lines, buildups

**Bass (all bass types):**
- Programs 32-39 (Acoustic, electric, synth bass)
- Work well for: grooves, sub-bass, walking bass

**Synth lead (cutting leads):**
- Programs 80-87 (Synth leads)
- Programs 0-7 (Pianos for percussive melodies)
- Work well for: main melodic hooks, solos

**Atmospheric (soft backgrounds):**
- Programs 88-95 (Synth pads)
- Programs 52-54 (Choir/voice)
- Work well for: background textures, atmosphere

## Genre-Specific Guidelines

### Deep House / House Music

**Philosophy**: House is harmonically simple but rhythmically complex. Groove emerges from how elements interact, not from held notes.

**Key characteristics:**
- **Driving 4-on-floor kick** with syncopated bassline that grooves between kicks (not on every beat)
- **Layered percussion**: shakers (continuous 16ths for motion), congas/bongos (accents on 2.5, 3.5), claps (double with snare), rim shots
- **Deep sub-bass** in octave 1-2 range (A1-E2) playing rhythmic patterns that follow chord roots for 4-8 bars
- **Harmonic bed**: sustained pads (octaves 2-4) or Rhodes/piano chords that change every 4-8 bars, not 16
- **Sparse melodic elements**: synth leads, piano riffs, vocal samples - play 2-4 bars then rest, enter after intro builds
- **Arrangement arc**: intro (8-16 bars, gradual layering) → full groove (16-32 bars) → breakdown (8-16 bars, strip to bass+pads, no kick) → drop (full return) → outro
- **Groove through syncopation**: bass hits on offbeats (1.5, 2.5, 3.5), rests create pocket, varied note lengths within repeated patterns

### Techno

**Philosophy**: Aggressive, hypnotic, industrial. Repetition with subtle evolution.

**Key characteristics:**
- **Hard-hitting kick** at 128-135 BPM, often every quarter note with no variation
- **Aggressive synth bass** (program 39) with distorted/gritty tone, tight rhythmic patterns locked to kick
- **Minimal but evolving**: start with kick+bass loop, gradually add hi-hats (16th rolls), claps, then pads/leads after 16+ bars
- **Harsh timbres**: metallic percussion, distorted leads (program 84), bright polysynth pads (program 90)
- **Long builds with filter sweeps**: bring elements in/out over 8-16 bar cycles, create tension through repetition and subtle changes

### Trance

**Philosophy**: Euphoric, melodic, emotional. Big buildups and drops.

**Key characteristics:**
- **Driving 4-on-floor** at 130-140 BPM with rolling hi-hat patterns (continuous 16ths)
- **Prominent melodic leads** (program 81) playing arpeggios or sustained melodies - louder than other genres
- **Layered pads** (programs 88-91) creating lush atmospheric bed, often multiple pad tracks
- **String buildups** (program 48) for emotional peaks and transitions, crescendo over 8-16 bars
- **Dramatic arrangement**: long intro (16-32 bars) → breakdown with just pads+arp (16 bars) → massive drop with full energy

### Ambient / Downtempo

**Philosophy**: Atmospheric, spacious, meditative. Focus on texture over rhythm.

**Key characteristics:**
- **Minimal or no drums**: if present, very sparse kick/percussion at 80-110 BPM with lots of space between hits
- **Layered pad textures** (programs 88-95) at different octaves and velocities, slowly evolving
- **Atmospheric FX** (programs 96-103) for movement: rain, crystal, atmosphere sounds at low velocity (40-55)
- **Subtle bass** (program 38) if used at all - long sustained notes (16.0-32.0 quarterLength), octave 1-2
- **Space and silence**: embrace long sections with only 1-2 elements, let sounds breathe and decay naturally

## Synthesis Features & Intelligent Volume

**Note**: While the soundfont handles synthesis, velocities should still be managed intelligently:

### Velocity Guidelines for Electronic Music

**By Role:**
- Lead synths: **95-110** (bright, cutting)
- Bass: **75-85** (powerful but not overpowering)
- Pads: **50-65** (background, atmospheric)
- Drums: **75-95** (punchy, present)

**By Frequency:**
- **Sub-bass (<100Hz)**: Keep at 75-80 velocity (powerful but controlled)
- **Mid-range (200-800Hz)**: Most important range - leads at 95+, pads at 50-65
- **High-range (>800Hz)**: Hi-hats and bright leads at 85-95

## Best Practices for Electronic Music

**Groove and Rhythm:**
- Create **syncopated patterns** where bass/percussion hit between main beats (offbeats like 1.5, 2.5, 3.5) - this is what creates groove
- **Layer multiple percussion elements** at different rhythmic densities (shakers on 16ths, congas on offbeats, claps on 2 and 4)
- Use **rests and space** in basslines and melodies - silence creates pocket and anticipation

**Arrangement and Structure:**
- Build **dynamic arcs**: intro (sparse, gradual layering) → full section → breakdown (strip elements) → drop (full return) → outro
- **Enter elements gradually** over 8-16 bar cycles, not all at once - each element should have its entrance moment
- Create **contrast between sections**: breakdown strips to just pads+bass (no kick), drop brings everything back with impact

**Harmonic Approach:**
- Stay on the **same chord root for 4-8 bars** (harmonic simplicity) but create **rhythmic variation** within that (groove complexity)
- Keep bass in **octave 1-2 range** (A1, C2, E2) - octave 0 is inaudible on most systems
- Use **extended chords** (7ths, 9ths) in pads for color without harmonic complexity

**Sound Selection and Velocity:**
- Use **all 128 GM programs** appropriately: synths (38-39, 80-95), but also guitars (24-31), strings (40-47), brass (56-63) for texture
- Set **velocities by role**: leads 95-110 (cutting), bass 75-85 (powerful), pads 50-65 (atmospheric), drums 75-95 (punchy)
- Add **humanization**: slight random variations in velocity (±3-5) and timing (±0.05 quarterLength) to avoid robotic feel

## Common Mistakes

1. **Confusing harmonic with rhythmic simplicity** - Staying on Am for 8 bars is good (harmonic), holding A1 for 32 seconds is boring (no rhythm)
2. **Static arrangements** - Electronic music needs intro/build/drop/breakdown structure, not 64 bars of identical loop
3. **Missing the groove** - Bass should syncopate with kick, not play on every beat or hold long notes
4. **No percussion layering** - One hi-hat pattern isn't enough, layer shakers/congas/claps/rims at different densities
5. **Default velocity 64** - Will create flat, lifeless mix; explicitly set velocities based on role (leads bright, pads quiet)
