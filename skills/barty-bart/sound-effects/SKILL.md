---
name: sound-effects
description: Add a measured sound pass to a motion-graphics video made with Claude Code (HyperFrames, Remotion, GSAP, Claude Motion or the motion-broll skill). Builds a cue list, checks the music's beat grid against the kick drums, lands cuts on the beat, places one real sound effect per cue from a bundled CC0 library, mixes to -16 LUFS with true peaks below -4 dBFS measured on the exported MP4, and proves it with frames, waveforms and 5 timestamps for a human to check. Use when someone wants sound effects, sound design or music added to a motion-graphics video, or says their AI video sounds like cheap beeps.
---

# Sound effects

Claude can't hear. So this skill never judges sound by feel: it measures every step, and it hands the user 5 timestamps to check with headphones. It never says "it sounds good".

The approach is Vox's sound-pass prompt (@Voxyz_ai, https://x.com/Voxyz_ai/status/2109358372873183564, 11 Oct 2026). Keep that credit.

## Default kit (use this first)
`sfx/manifest.json` → `default_kit`: one sound per core category, picked by ear by Bart (12 Oct 2026). Use it unless the user asks for something else.

| Category | Sound | Where it comes from |
|---|---|---|
| whoosh | "Whoosh" by qubodup | bundled `sfx/kit/whoosh.ogg` (CC0) |
| click | "Classic Click" by adh.dreaming | bundled `sfx/kit/click.ogg` (CC0) |
| pop | "POP SFX Neutral" by ethernel0 | bundled `sfx/kit/pop.ogg` (CC0) |
| riser | "Cinematic Riser #3 subtle" | bundled `sfx/kit/riser.ogg` (CC0) |
| impact | "soft_impact3" by peoplearehappy | bundled `sfx/kit/impact.ogg` (CC0) |
| tick | "Click / Tick" by Squirrel_404 | bundled `sfx/kit/tick.ogg` (CC0) |
| typing | Mixkit "Fast laptop keyboard typing" (#1392) | **downloaded at runtime** into `<out>/sound-effects-cache/` (Mixkit licence: never commit it) |

Everything else in the manifest is an alternative (`alt_categories` lists which categories can stand in for each other). See `TOP-PICKS.md` for credits.

## Rules
- **Never synthesize music or sound effects in code** (no oscillator or sine beeps). Use real recorded files.
- **Sound effects: use the bundled library first.** `sfx/manifest.json` lists every file with its category, duration, source and licence. All bundled files are CC0.
- If the bundled library has nothing that fits, use the `runtime` entries in the manifest (Mixkit). Download them into the user's project, never into this skill folder, and never commit them. Mixkit allows use in videos but not standalone redistribution.
- **Music:** a track the user gives you, or one from `MUSIC.md` (suggested free tracks by feel, downloaded at runtime, never committed). Write the source and licence into `SOUND.md`. If the user has no track, suggest 2–3 from `MUSIC.md` that fit the video and let them pick.
- **Licences:** only CC0 and Mixkit Free License count as free and safe; the script checks every sound it places. Don't list licences sound by sound. If all are known, tell the user once: the sounds are listed as CC0 or Mixkit Free License by their sources, sources can change their terms so check the source page now and then. If the script reports an unknown licence, name that exact sound, its licence and its source link, and tell the user not to publish until it is checked or swapped. Never describe an unknown licence as probably fine.
- **Music licence:** ask where the track came from and pass `--music-source "track, artist, link"` and `--music-license "..."`. Without them the run marks the music LICENCE NOT CONFIRMED; say so plainly.
- **Credits:** every run writes `CREDITS.txt`, a paste-ready list of the sounds actually used and the music. Recommend it once: optional, for a YouTube, Instagram or TikTok description; CC0 needs no credit, but the list is proof of source if a platform flags the audio.
- Measure the **exported MP4**, never the intermediate WAV.
- Measure the **exported MP4**, never the intermediate WAV.

## 0. Licence check (during the edit, before you export)
Sources change their terms, so check the current terms for **what this video actually uses**, every time, before the final export:

1. **Use case.** Ask where the video will be published, unless it is already clear (for example "my YouTube video"): YouTube, Instagram, TikTok, other social, online ads, a podcast, client work, TV or radio broadcast, a video game, CDs or DVDs, or a template or tool for other people. Pass it as `--use-case "..."` so it lands in `SOUND.md`.
2. **Sources.** For each source used in this video (the providers in `CREDITS.txt`, plus the music), open its current licence page (web fetch; if the site blocks it, the user's browser) and check two things: the terms still say what the table below says, and the use case is allowed. For Freesound, open the page of each sound actually used and confirm it still says Creative Commons 0. For the music, open the track's page.
3. **Report it plainly**, one line per source: "Checked today: Mixkit Stock Music Free License, unchanged, YouTube allowed." If a source changed its terms or the use case is not allowed, name the exact sound or track and why, and swap it before exporting. Never call an unchecked or unclear licence fine.

| Source | Licence page | Allows (checked 13 Oct 2026) | Doesn't allow |
|---|---|---|---|
| Freesound, CC0 | the sound's own page | anything, no credit needed | nothing (CC-BY needs a credit; never use CC-BY-NC commercially) |
| Kenney | the pack's page on kenney.nl | anything (CC0) | nothing |
| Mixkit sound effects | https://mixkit.co/license/#sfxFree | web, social, podcasts, games, films, CDs/DVDs, TV/radio | redistributing the file on its own or inside a tool or template; registering it with a rights service |
| Mixkit music | https://mixkit.co/license/#musicFree | YouTube, social, online ads, podcasts, education | CDs/DVDs, TV/radio, video games, remixing, registering it with Content ID |

Mixkit forbids redistributing its files "in a tool or template", which is why this skill never stores Mixkit sounds or music: they are downloaded into the user's project at runtime.

## 1. Set up
Needs ffmpeg and Python 3.10+. Install into a folder you can delete:
```
python3 -m venv .sound-effects
.sound-effects/bin/pip install librosa soundfile numpy scipy matplotlib
```

## 2. Build the cue list
Read the video's duration and fps with `ffprobe`. List every moment that needs a sound. Take them from the composition source when you can (HyperFrames/Remotion timeline, GSAP labels, motion-broll `plan.json`). Otherwise detect scene cuts with `ffmpeg -i in.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -`.
Write `cues.json` as `[{"t": 2.0, "type": "scene_cut", "desc": "cut to card"}, {"t": 4.2, "type": "typing", "dur": 1.3, "desc": "..."}]`.

The cue types map to library categories (`category_map` in the manifest):

| Cue type | Category | Notes |
|---|---|---|
| movement (slide, camera move) | whoosh | starts 2 frames early; pick length to match the move |
| scene_cut | whoosh | short whoosh, 2 frames early (`transition` sounds are alternatives) |
| appear | pop | on the frame |
| click | click | on the frame |
| typing | typing | looped/trimmed to `dur`, quiet |
| build_up | riser | **ends** on the next hit |
| reveal | impact | the loudest SFX |
| success | pop | (`ding` sounds are alternatives) |
| error_or_tech | glitch | |
| hover_or_small_ui | tick | very quiet (`ui-blip` and `click` are alternatives) |
| bed | ambience | under everything, optional |

Use one sound per cue. Vary takes within a category so repeats don't sound robotic.

## 3. Beat grid, and check it
Run `librosa.beat.beat_track`. **librosa sometimes locks onto the off-beat.** Low-pass the music below 120 Hz, plot it against the beat lines for the first 4 bars, and compare where the kicks land. If the kicks don't sit on the lines, shift the whole grid by the median offset and plot again. Show the user `beatgrid.png`.

## 4. Put the big moves on the beat
Hard cuts and reveals should land on a beat. If you can change the animation timings, change them. If you can't, move where the music starts (search offsets and pick the one with the smallest cut-to-beat error). Report the error per cut in ms.

## 5. Place SFX and mix
Priority: **voiceover > SFX > music.** The music bed sits around -12 dB under the SFX and ducks under any voiceover by 8–12 dB.
Target **about -16 LUFS integrated** with **true peak below -4 dBFS**, so nothing clips after AAC compression or on a phone speaker. Export, measure, adjust gain or add a limiter, then export and measure again:
```
ffmpeg -nostats -i after.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
ffmpeg -nostats -i after.mp4 -ac 1 -af ebur128=peak=true -f null - 2>&1 | tail -12   # mono check
```

## 6. Prove it
For every cue, grab one frame just before and just after it from the exported MP4, and plot the waveform around it (`checks/cue-XX.png`). Then pick the **5 riskiest timestamps** (largest beat error, long sounds such as typing and risers, the reveal) and give them to the user to check with headphones.

## Original-quality files
The bundled sounds are compressed OGG Vorbis previews (trimmed, normalised, often mono), which is fine for most videos. If a sound is too low quality for the job (audible artefacts, a close-up hero sound, a final master), fetch the original:
- Look up the entry's `source_url` in `sfx/manifest.json`. Every bundled and `default_kit` entry has one.
- **Freesound** (`freesound.org/people/<user>/sounds/<id>/`): the original is the Download button on that page. It needs a free Freesound account, so ask the user to download it (or use their API key if they give you one).
- **Kenney** (`kenney.nl/assets/<pack>`): download the pack zip from that page. Each Kenney entry's `original_file` in the manifest names the exact file, e.g. `kenney_interface-sounds.zip → Audio/click_001.ogg`. The rule: drop the prefix (`kenney-interface-` → interface-sounds, `kenney-ui-` → ui-audio, `kenney-digital-` → digital-audio, `kenney-impact-` → impact-sounds, `kenney-sci-` → sci-fi-sounds), then match the rest inside `Audio/` ignoring case, with `-` read as `_` (`kenney-digital-phaserup1` → `Audio/phaserUp1.ogg`, `kenney-impact-impactpunch-heavy-000` → `Audio/impactPunch_heavy_000.ogg`). Kenney's originals are OGG too, but unprocessed.
- Save originals into the user's project (for example `sound-effects-cache/originals/`), never into this skill folder, and pass the file to the script via `--swaps` or by editing a copy of the manifest. Apply the same trim and level as the bundled file.

## Find more sounds
When the user wants more or different sounds, search these sources, suggest 3–5 candidates with a link, creator and licence for each, and let the user pick. Before using any of them, open its page, confirm the licence shown today, and check it allows the user's use case (step 0); add it to `CREDITS.txt`. Only use or redistribute a sound as its licence allows. For music, see `MUSIC.md`.

| Source | Search | Licence notes |
|---|---|---|
| Freesound | `https://freesound.org/search/?q=<words>&f=license:"Creative Commons 0"` | Use the CC0 filter. CC0 can be bundled and needs no credit (credit anyway). CC-BY needs credit in the video description; never bundle CC-BY-NC or use it commercially. |
| Kenney | `https://kenney.nl/assets/category:Audio` | All CC0. Free to use and bundle. |
| Mixkit | `https://mixkit.co/free-sound-effects/<category>/` (e.g. `whoosh`, `typing`) | Mixkit SFX Free License: fine in videos, including monetised ones, but **no redistribution**. Download only into the user's project at runtime; never commit or bundle it. |
| Pixabay | `https://pixabay.com/sound-effects/search/<words>/` | Free in videos, no credit needed, but no standalone redistribution. The user downloads it in a browser; never bundle it. |
| Sonniss GDC bundles | `https://sonniss.com/gameaudiogdc/` | Royalty-free in videos; no raw redistribution or AI training. Local use only. |
| YouTube Audio Library | YouTube Studio → Audio Library | For YouTube videos only; available only inside Studio. Never bundle it. |

Only CC0 sounds may be added to this repo's `sfx/` folder, each with a manifest entry (file, category, duration, source_url, licence, attribution) and a row in `LICENSES.md`.

## Script
`scripts/sound_pass.py` runs steps 3–6 end to end:
```
.sound-effects/bin/python scripts/sound_pass.py --video silent.mp4 --cues cues.json \
  --music track.mp3 --manifest sfx/manifest.json --out out/
```
Add `--use-case "..."`, and `--music-source`/`--music-license` once confirmed. It outputs `after.mp4`, `report.html`, `SOUND.md` (licence check, log, cue → file table, LUFS and peak numbers, the 5 timestamps), `CREDITS.txt`, `beatgrid.png` and `checks/`. Read its log and fix anything over target. If you changed the animation timings, re-render first.

## 7. Swap report
`sound_pass.py` also writes `report.html`. It lists every cue with its timestamp, category, the sound used (with a play button), the source page, licence and credit, plus the alternatives in that category, each with a play button and a "let model decide" option. Open it for the user. They choose, click **Download swaps.json**, and you re-run with `--swaps swaps.json`. `"auto"` means pick another sound from the alternatives. Keep cue indices stable between runs.

## Report to the user
Report the licence check (all known, or each unknown sound by name), the use case and whether it is allowed, the music source and licence (or that it is not confirmed), that `CREDITS.txt` is there if they want it, the beat-grid result (shifted or not, and by how much), the cut-to-beat errors, final LUFS and true peak (stereo and mono), and the 5 timestamps. Don't tell them it sounds good.
