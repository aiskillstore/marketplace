---
name: motion-broll
description: Turn a talking-head video and its transcript into motion-graphic B-roll timed to the speaker's words, in a continuous one-shape style (one element that morphs and never cuts, driven by a cursor, spring motion). Use when someone gives a video (and ideally a transcript) and asks for motion graphics, B-roll, animated cutaways or overlays.
---

# Motion B-roll

You make motion-graphic clips for a creator's video. Every clip is **one shape that never cuts**: it morphs its size, corners and colour from state to state while its content swaps with a short blur. A cursor drives the changes with real clicks and drags, and every change lands on a spoken word.

The output is a set of clips the creator drops into their editor. You also give them a preview render of their video with the clips cut in, and two HTML pages: one to step through the clips, one to compare before and after.

Everything you need is in this skill folder:

- `engine/`: the motion engine (`motion.js`), the page shell (`base.css`), `build.py` (clip → self-contained HTML), `render.js` (frame-by-frame render with motion blur), `beats.js` (contact sheets of stills), fonts (Geist, OFL).
- `scripts/`: `setup.sh`, `inspect_video.py`, `words.py`, `composite.py`, `make_pages.py`.
- `reference/engine-api.md`: how to write a clip. **Read it before writing your first clip.**
- `examples/opus-aoe2/`: six finished clips for a real 54-second video. Use them as the quality bar and as starting points.

Below, `$SKILL` means this skill's folder. Work in a `motion/` folder in the user's project.

## 1. Set up (first run only)

```bash
bash $SKILL/scripts/setup.sh ./motion
```

This checks for Node, Python 3 and ffmpeg, and installs Playwright + Chromium into `motion/node_modules`. Run every engine script with `NODE_PATH=./motion/node_modules`.

## 2. Interview

Use the AskUserQuestion tool; keep it to one round. You need:

- **The video.** A path. Copy or reference it as `motion/work/source.*`.
- **The transcript.** An SRT or VTT with timestamps is best. With plain text only, get word timestamps from the audio (`pip install faster-whisper`) or ask for an SRT.
- **Density:**
  - Light: 2–4 clips per minute, only the strongest moments.
  - Medium (default): 4–7 per minute.
  - Heavy: most lines covered, with short gaps of face.
- **Look:**
  - The default palette: warm gray canvas, black and white components, one orange accent.
  - Or their brand: colours, and optionally a font. Ask them to drop a logo, screenshots or brand colours into `motion/inputs/`, and read those.
- **Anything to avoid or include.** Lines to leave on their face, real numbers or names to show, product screenshots to recreate.

Skip any question the user already answered.

## 3. Inspect the footage

```bash
python3 $SKILL/scripts/inspect_video.py motion/work/source.mp4 motion/work
python3 $SKILL/scripts/words.py transcript.srt > motion/work/words.txt   # .vtt works too
```

Look at `motion/work/contact.png` yourself. `video.json` gives resolution, fps and layout sections:
- **full:** the speaker fills the frame.
- **pip:** the speaker is in a box and the rest is empty. It includes the box position and a warning if the box changes size or moves.
- **black:** the whole frame is black (a fade, intro or outro).

Clips must match the video's resolution and fps. Word times from an SRT or VTT are estimates (±0.2s); treat them as such.

## 4. Plan, and get approval before any code

Show a table with one row per clip:

| # | In–Out | The line it covers | What the shape does, on which words | Treatment | Why |

**Creative direction: decide how much of the frame each clip takes.** This is the most important call; make it per clip and give the reason.

- **Full-frame cutaway.** The frame is all speaker, and the line describes something to *see*: a product, a process, a comparison, a number, a chapter change.
  - Cut away for the length of the idea (3–10s), then give the face back.
  - Don't cut away in the first second of the hook or on personal, emotional or opinion lines.
  - Leave at least ~2s of face between cutaways.
- **Panel in the empty space.** The edit already leaves room: a PiP box, a split, a plain region.
  - Render a transparent clip (`bg:null`) centred in the empty area, sized to stay clear of the speaker's box at every moment.
  - It can run long (15s+) as one continuous morph, because the speaker stays on screen.
  - If `inspect_video.py` reports the box changing, ask whether that's intended, then size for the largest box or split the panel at the change.
- **Nothing.** The line is about the speaker, or it's too close to another clip.

**Content rules:**
- Show the subject's real objects: the folder, the terminal, the file, the product, the result. Pull them from the words. Map each idea onto an interaction from the vocabulary in `reference/engine-api.md` (pill + click, progress, check, status island, card with a drag, slider, toggle, tabs, chart + tooltip, search/filter, file drag-and-drop, terminal typing, side-by-side comparison, chapter card).
- **Never invent numbers, quotes, prices or results.** Use relative bars, skeleton text lines or labels taken from the transcript, and list what is illustrative. Put real figures in only when the user gives them.
- One idea per clip. A continuous stretch (a whole PiP section) can be one long clip with several states.
- Pace to speech, not music: one change per spoken beat, about 0.4–1.2s apart.

Wait for the user to approve or edit the plan.

## 5. Build

Write one fragment per clip in `motion/clips/NN-name.html`, following `reference/engine-api.md` and the examples. Then build:

```bash
python3 $SKILL/engine/build.py motion/dist motion/clips/*.html
```

Put each state change on its word: clip-local time = word time − clip in-point.

## 6. Check stills on the key words

```bash
NODE_PATH=./motion/node_modules node $SKILL/engine/beats.js motion/dist/NN-name.html motion/work/NN.png 0.4 1.2 2.1 …
```

Pick the times where each state has settled and a couple of mid-morph moments. Look at every sheet yourself. Fix anything cramped, clipped, unreadable or off-word, or where the cursor leaves the frame. Then check once more. Panel clips render on black in the sheet so you can judge them.

## 7. Render

```bash
NODE_PATH=./motion/node_modules node $SKILL/engine/render.js motion/dist/NN-name.html motion/out/NN-name_0m32s40.mp4 30000/1001
```

- Use the video's fps.
- Panel clips (`bg:null`) must be written to `.mov`, which gives ProRes 4444 with alpha.
- Name each file by its timeline in-point (`0m32s40` = 0:32.40).
- Rendering takes 4 subframes per frame, so it is slower than real time. Run two clips in parallel on a multi-core machine.

## 8. Deliver

Write `motion/plan.json` (schema in `reference/engine-api.md`), then:

```bash
python3 $SKILL/scripts/composite.py motion/plan.json motion/out/preview.mp4
python3 $SKILL/scripts/make_pages.py motion/plan.json motion/out/preview.mp4
```

The user gets, all in `motion/out/`:
- the clips
- `TIMING.md`: file, in, out, the line it covers, the treatment, and what is illustrative
- `preview.mp4`: their video with the clips cut in, hard cuts, original audio
- `viewer.html`: step through the clips
- `compare.html`: original vs preview, synced, as side by side, stacked or wipe

Say plainly that the preview is for review: for the final cut they place the clips in their own editor, where they can nudge timing, add transitions and mix audio.

## Style defaults

The user's brand overrides these.

- **Colour:** canvas `#E9E7E2`, ink `#0B0B0B`, white components, one accent `#FF5A1F`. Panel clips on dark footage use light shapes (`#F4F2EE`).
- **Type and icons:** Geist for UI text, Geist Mono for code, file names and terminals. One icon set with one stroke weight (`M.icon`).
- **Motion:** springs with a tiny overshoot at most. Leading and trailing edges ride different springs so indicators stretch. The camera zooms so each state fills the frame.
- **Banned:** bouncy easing, particles, glows, gradients on UI chrome, mixed icon strokes, dead time, anything that looks like a template, made-up data.

## Gotchas

- Never put `will-change` on anything the camera scales; text renders blurry.
- Text swapping inside a morphing container needs its own enter and exit timing (`M.vis` din/lin/lout), or the old and new text overlap.
- `mix-blend-mode: difference` labels must sit in a layer that has the blend mode itself. A filtered parent isolates them.
- Items that slide under a highlight need `M.FAST` springs, or the highlight row sits empty for a moment.
- Keep the cursor inside the frame at every camera zoom, including during morphs.
- Word estimates from an SRT drift within a cue; put important changes on the first or last word of a cue when you can.
- A clip ends by holding its last state; the composite holds the last frame if its slot is longer.
