# Prompt Writing Guide

This reference helps construct high-quality music generation prompts.

## Core Principle

**Write prompts as vivid English sentences, not comma-separated tags.**

The API responds best to descriptive, narrative-style prompts that paint a complete picture
of the song. Each prompt should read like a creative brief for a musician.

## Prompt Structure

A complete prompt follows this sentence pattern:

```
A [mood/emotion] [BPM optional] [genre + sub-genre] [song/piece/track].
[Vocal description OR "Instrumental with..." description].
[Narrative/theme — what the song is about].
[Atmosphere/scene details].
[Key instruments and production elements].
```

**Vocal Track Example:**
```
A melancholic yet defiant Pop-House song, featuring emotional vocals, about
lighting a torch in the cold dark night as a form of romantic rebellion,
energetic rhythm with synth elements.
```

**Instrumental Example:**
```
A warm and uplifting 100 BPM indie folk instrumental piece, evoking a sunny
afternoon stroll through a small town market, featuring bright acoustic guitar
fingerpicking, gentle ukulele strums, light hand claps, and a whistled melody
that feels like pure contentment.
```

## How to Build a Prompt Step by Step

**1. Open with mood + genre (required)**

| Pattern | Example |
|---------|---------|
| Single mood | "A melancholic R&B song" |
| Contrasting moods | "A melancholic yet defiant Pop-House song" |
| With BPM | "A smoky 74 BPM Neo-Soul fusion" |
| With era/region | "A laid-back 90 BPM Island Reggae" |
| Genre blend | "An Avant-Garde Jazz and Neo-Soul fusion" |

**2. Describe the vocals (for vocal tracks)**

Good vocal descriptions:
- "featuring smooth emotional vocals"
- "Vocals: Ultra-low, gravelly baritone with authentic phrasing"
- "Vocals: Sultry, sophisticated male baritone with smooth jazz inflections and breathy delivery"
- "Vocals: Ethereal, crystal-clear Enya-style vocals with lush reverb"
- "Vocals: Relaxed, soul-flavored vocals with ad-libs and melodic scats"

Bad (too vague): "female vocal"

**3. Add narrative/theme (recommended)**

- "about lighting a torch in the cold dark night as a form of romantic rebellion"
- "about letting go of perfectionism and embracing your true self like flowing water"

For instrumentals, describe the scene: "evoking a sunrise drive along a coastal highway"

**4. Set the mood/atmosphere (recommended)**

- "bittersweet but healing mood"
- "empowering and self-loving mood"

**5. Specify production elements (recommended)**

- "mellow beats with lo-fi elements"
- "featuring a warm fretless bassline, shimmering Rhodes piano, and brushed jazz drums"

## Genre Reference

| Category | Genres |
|----------|--------|
| Pop & Dance | Pop, Dance Pop, Electropop, Synth-pop, Dream Pop, K-pop, J-pop, C-pop, City Pop, House, Future Bass, EDM |
| Rock & Alt | Rock, Indie Rock, Pop Rock, Post-Rock, Shoegaze, Punk, Metal, Alternative |
| R&B/Soul/Funk | R&B, Neo-Soul, Contemporary R&B, Funk, Gospel, Soul |
| Hip-Hop | Hip-Hop, Trap, Boom Bap, Lo-fi Hip-Hop, Cloud Rap, Drill, Afrobeats |
| Electronic | Ambient, Techno, Drum and Bass, Chillwave, Vaporwave, Amapiano |
| Folk/Acoustic | Folk, Indie Folk, Country, Chinese Traditional, Celtic Folk |
| Jazz/Blues | Jazz, Smooth Jazz, Jazz Fusion, Bossa Nova, Blues, Avant-Garde Jazz |
| Classical | Classical, Orchestral, Cinematic, Film Score, Epic, Neoclassical, Piano Solo |
| World | Reggae, Latin, Waltz, Tango, Flamenco |

## Vocal Style Reference

| Style | Prompt phrase |
|-------|--------------|
| Smooth & emotional | "smooth emotional vocals" |
| Raw & unpolished | "raw, unpolished vocals shifting between whispers and screams" |
| Breathy & intimate | "breathy delivery with intimate phrasing" |
| Powerful & soulful | "powerful soulful vocals with gospel inflections" |
| Sultry & sophisticated | "sultry, sophisticated baritone with jazz inflections" |
| Ethereal & clear | "ethereal, crystal-clear vocals with lush reverb" |
| Aggressive & intense | "aggressive vocal delivery with rhythmic intensity" |

## Instrument & Production Reference

| Category | Examples |
|----------|---------|
| Strings & Guitar | acoustic guitar fingerpicking, electric guitar riffs, fretless bass, violin, cello, erhu, guzheng, pipa |
| Keys & Synth | piano, Rhodes piano, synth pad, synth lead, arpeggiator, music box, organ |
| Drums & Percussion | brushed jazz drums, electronic drums, 808 hi-hats, trap percussion, cajon, bongos |
| Wind & Brass | saxophone, trumpet, flute, harmonica, bamboo flute, xiao |
| Texture & Effects | vinyl crackle, tape hiss, ambient pads, glitch elements, rain sounds |

## BPM Reference

| Feel | BPM | Use in prompt |
|------|-----|---------------|
| Very slow, meditative | 40-60 | "a meditative 50 BPM..." |
| Slow ballad | 60-80 | "a slow 70 BPM ballad..." |
| Mid-tempo groove | 80-110 | "a groovy 95 BPM..." |
| Upbeat, energetic | 110-130 | "an upbeat 120 BPM..." |
| Fast, driving | 130-160 | "a driving 140 BPM..." |

## Tips for High-Quality Prompts

1. **Write sentences, not tag lists**: "A melancholic R&B song about..." beats "R&B, sad, slow, piano".
2. **Be vivid and specific**: "salvaging memory fragments in space-time" > "sad memories".
3. **Describe vocals as a character**: "Sultry baritone with jazz inflections" not "male vocal".
4. **Include a scene or vibe**: "A high-end rooftop lounge at night" gives the model a coherent world.
5. **Mix detail levels**: Specify 2-3 key instruments precisely, leave the rest to the model.
6. **English prompts work best**: Chinese scene descriptions can be mixed in for flavor.
7. **For instrumentals**: Replace vocal descriptions with instrument focus and scene narrative.
