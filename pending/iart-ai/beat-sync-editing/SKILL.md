---
name: beat-sync-editing
description: This skill should be used when the user asks to "cut to the beat", "fix the pacing", "edit this sequence", "sync cuts to music/BPM", "add a match cut / J-cut / L-cut", "build a speed ramp", or "plan a shot sequence / edit timeline". Covers editing rhythm, transitions, retiming, and translating an edit plan to an NLE or a code timeline (Remotion/AE frames).
version: 0.1.0
---

# Beat-Sync Editing (Cuts & Rhythm)

The timeline craft: how clips and beats assemble into a piece that *feels* right. Editing is temporal design — when a cut lands matters as much as what is on screen. This skill turns musical and narrative structure into concrete cut points, transitions, and retimes, expressible in an NLE or as frame numbers in code.

## When to use

- Assembling a sequence or cutting footage to a music track.
- Pacing drags or feels choppy; transitions feel arbitrary.
- Building speed ramps, match cuts, or tension/release structure.
- Converting an edit plan into a frame-accurate timeline (Remotion, AE, NLE).

## Decision tree

```
What's the editing problem?
├─ Cuts feel off the music
│   └─ get BPM + offset → frames_per_beat = (60/BPM)*fps
│      → cut on PHRASES (2/4/8 beats), biggest visual on the drop
├─ A cut feels jarring / visible
│   └─ cut on action (mid-motion), match direction + velocity
│      → still rough? motivate a transition (match / J / L), else hard cut
├─ Pacing drags or feels flat
│   └─ shape an arc: Establish → Develop → Climax → Resolve
│      → shorten avg shot length toward climax, hold after it
├─ A hit needs impact
│   └─ speed ramp INTO it (slow-mo), snap back; land slowest frame on the beat
└─ Need to hand it to code
    └─ express every cut as a frame number, clip as from/duration,
       transition as overlap, retime as eased time-remap (Remotion/AE)
```

**Cross-reference — apply the shared frameworks.**

- **Motion Personality** (`motion-art-direction`) sets cut rhythm: the chosen energy maps straight to phrase length and transition family. Pick one and commit (see the table below).
- **Three Pillars** + beat-sync (`animation-principles`): settle *emotional intent* first (hype vs. calm) — it decides whether you cut every bar or hold for four. `animation-principles` defines the BPM→beat relationship; this skill turns it into frame-accurate cut points and the transition/retime craft on top.

### Motion Personality → cut rhythm

| Personality | Phrase (cut every) | Transition family | Retime | Reads as |
|---|---|---|---|---|
| **Playful** | 4 beats, syncopated accents | match cuts, quick whips | light ramps, bouncy | fun, kinetic |
| **Premium** | 8–16 beats, long holds | hard cut + occasional dissolve | slow, smooth ramps | elegant, unhurried |
| **Corporate** | 8 beats, steady | hard cut, clean | minimal | clean, trustworthy |
| **Energetic** | 1–2 beats at climax | hard cut, whips, hard snaps | aggressive ramps on beats | bold, hype |

## Core workflow

### 1. Find the grid: BPM → frames

Cut on the music's rhythmic grid, not on arbitrary timecodes. Convert BPM to frames so cut points are frame-accurate.

```
frames_per_beat = (60 / BPM) * fps
```

At 120 BPM, 30 fps: `(60/120)*30 = 15` frames per beat (500ms/beat) — a cut every 15 frames is on-beat. Cut on *phrases* (every 2/4/8 beats), not every beat, or the edit feels frantic. Land the single biggest visual moment on the musical drop.

The **eighth-grid**: subdivisions of the beat give finer accent points without going off-grid. At 120 BPM / 30 fps:

| Subdivision | ms | frames @30fps | Use |
|---|---|---|---|
| 1 beat (quarter) | 500 | 15 | main cut grid |
| ½ beat (eighth) | 250 | 7.5 | accent / quick flash cut |
| ¼ beat (sixteenth) | 125 | 3.75 | hits, stutter, transient FX |
| 1 bar (4 beats) | 2000 | 60 | phrase / section boundary |

Snap accents to the eighth-grid; keep structural cuts on the beat or bar.

```js
// Generate on-beat frame numbers (JS / Remotion / AE-friendly)
const bpm = 120, fps = 30;
const framesPerBeat = (60 / bpm) * fps;       // 15
const phrase = 4;                              // cut every 4 beats
const cuts = Array.from({length: 16}, (_, i) =>
  Math.round(i * framesPerBeat * phrase));     // [0,60,120,180,...]
```

### 2. Hide the seam: cut on action / motion

A cut is invisible when motion carries the eye across it. Cut *during* a movement (a turn, a hand reaching, a whip) so the brain tracks the action through the cut. Match the motion's direction and speed across the cut. For motion-graphics, cut on a transform peak — at the moment a shape is mid-travel, not at rest.

### 3. Choose transitions with intent

Default to the **hard cut**. Reach for anything else only when motivated:

- **Match cut** — outgoing and incoming frames share a shape, position, or motion vector, so the cut reads as a transformation (a circle becomes the moon; a wipe of an arm reveals the next scene). The strongest transition in motion design.
- **J-cut** — audio of the *next* shot starts *before* its picture (sound leads). Pulls the viewer forward; great for dialogue and reveals.
- **L-cut** — audio of the *current* shot continues *under* the next picture (sound trails). Smooths scene changes.
- **Whip / motion blur transition** — fast pan blends two shots; needs matched blur direction.
- **Luma/wipe/dissolve** — signals time passing or a softer mood; overuse reads as amateur.

Cut-type quick table:

| Cut type | What aligns | Signals | Typical offset | Reach for it when |
|---|---|---|---|---|
| Hard cut | nothing — instant | neutral, default | 0 | 90% of cuts |
| Match cut | shared shape / position / motion vector | transformation | 0 (1–2f tolerance) | two shots rhyme visually |
| J-cut | audio of B leads its picture | pulls viewer forward | audio 4–12f early | dialogue, reveals |
| L-cut | audio of A trails under B | smooths the change | audio 12–24f late | scene changes, ambient |
| Whip / motion blur | matched blur direction across pan | energy, "swoosh" | ~6–10f blend | hype, scene jumps |
| Speed ramp | retime, not a cut | impact / emphasis | lands on beat | a hit needs to land |

### 4. Retime: speed ramps

Speed ramps (gradual time-warp) add impact: ramp *into* a hit with slow-motion, then snap back to speed. Keep motion blur consistent through the ramp or the slow section looks strobed.

```
Speed ramp on an impact (frames, 30fps):
  0–20    100% speed   (run-up)
  20–28   ease down to 25%  (anticipation, slow-mo on the hit)
  28      IMPACT lands on the beat
  28–40   ease back to 100% (release)
```

In an NLE use time-remap keyframes with smooth interpolation and enable frame-blending/optical-flow for clean slow-mo. In Remotion/AE, drive a `timeRemap`/`valueAtTime` curve with eased interpolation and keep a consistent shutter/motion-blur setting.

### 5. Shape the arc: sequence pacing

A piece needs a shape, not one constant intensity:

```
Establish → Develop → Climax → Resolve
  longer holds   shortening cuts   fastest + the drop   release/breathe
```

Vary shot length deliberately: fast cuts build energy, longer holds let key moments land. Build toward the climax by shortening average shot length, then give a beat of rest after it. The classic mistake is uniform pacing — it reads as flat regardless of content.

Pacing arc — tension → release (energy is the *derivative* of cut frequency):

| Phase | Cut every | Avg shot length | Tension | Note |
|---|---|---|---|---|
| Establish | 8–16 beats | longest | low | set place/mood, let it breathe |
| Develop | 8 → 4 beats | shortening | rising | accelerate cuts to build |
| Climax | 1–2 beats | shortest | peak | the drop; biggest visual + speed ramp |
| Resolve | one long hold | longest | release | logo/CTA breathes after the peak |

## Quick reference

| Goal | Move |
|---|---|
| On-beat cut | `(60/BPM)*fps` frames per beat; cut on phrases |
| Land the drop | biggest visual on the musical drop |
| Invisible cut | cut on action / matched motion |
| Transform feel | match cut (shared shape/motion) |
| Pull forward | J-cut (audio leads) |
| Smooth scene change | L-cut (audio trails) |
| Impact | speed ramp into the hit, snap out |
| Build energy | shorten average shot length |
| Let it breathe | hold after the climax |

## Worked examples

### GOOD — 30s energetic product spot, 128 BPM, 30 fps

> **Brief**: hype sneaker drop, Energetic personality, drop at beat 32.
>
> - **Grid**: 14.06 f/beat. Drop = beat 32 ≈ frame 450 (rounded cumulatively to avoid drift).
> - **Arc**: Establish 0–120 (two 2s holds). Develop 120–450 (cuts shortening 8→4→2 beats, rising energy — matches Energetic). Climax at 450 (the drop). Resolve 700–900 (one long CTA hold).
> - **Cuts**: structural cuts on the bar; two accent flash-cuts snapped to the eighth-grid in Develop.
> - **Craft**: f112 is a match cut (shared circular logo → wheel). The drop at 450 carries the biggest visual *and* a speed ramp 100%→25%→100% landing the slowest frame on the downbeat. CTA enters under an L-cut (audio trails ~18f).
> - **To code**: each cut a frame number, each clip `<Sequence from/durationInFrames>`, ramp = eased time-remap, beats verified `frame/fps` against detected beat seconds.
>
> Why it works: phrase-based grid, an arc, one big moment on the drop, motivated transitions, frame-accurate and portable.

### ANTI-PATTERN — "cut on every beat with a dissolve each time"

> - A hard cut on all 32 beats → relentless, no focal moment, viewer fatigues by beat 8.
> - A 12-frame crossfade on *every* cut to "smooth it" → mushy, amateur, and now nothing is on the beat because the dissolve midpoint drifts off-grid.
> - Uniform 15-frame shots start to finish → flat; no establish, no climax, the drop lands on nothing.
> - BPM math done from frame 0 ignoring the track's offset → every cut sits a few frames early, feels "almost right" but wrong.
>
> Fix: cut on 4/8-beat phrases, hard cut by default, build an arc, anchor the grid to beat-1 offset, and put the one biggest visual on the drop.

## Common mistakes

| Symptom | Why | Fix |
|---|---|---|
| Edit feels frantic / busy | cutting on every beat | cut on 2/4/8-beat phrases; accent on the eighth-grid sparingly |
| Cuts feel "almost on beat" | grid started at 0:00, ignored track offset | capture beat-1 offset; anchor cumulative frame math to it |
| Drift over a long edit | rounding frames_per_beat per step | round each *cumulative* beat, not per-step |
| Cut feels jarring | placed at rest, between motions | cut on action / mid-motion; match direction + velocity |
| Slow-mo strobes | sub-100% speed without interpolated frames | enable optical-flow / frame-blending; consistent shutter |
| Whole piece feels flat | uniform pacing | shape Establish→Develop→Climax→Resolve; shorten toward the drop |
| Transitions look amateur | dissolves/wipes used as a crutch | default to hard cut; motivate match/J/L; fix timing first |
| Nothing lands | no single climax | put the biggest visual on the drop; hold after it |

## Deliverable — an edit-timing plan

A good plan is renderer-agnostic and hands off to an NLE or a code timeline (`remotion-video`, `after-effects`):

- **Track spec**: BPM, fps, beat-1 offset, drop frame(s), frames_per_beat.
- **Arc**: the four phases with frame ranges and target average shot length per phase.
- **Cut list**: every cut as an absolute **frame number** (from the BPM math), the clip at that cut, and the cut type.
- **Transitions**: type (hard/match/J/L/whip), and for J/L the audio offset in frames.
- **Retimes**: each speed ramp as eased time-remap keyframes (from→to %, frames, optical-flow on).
- **Beat markers**: the on-beat/eighth-grid frame array for verification.
- **Cross-refs**: the Motion Personality that set the rhythm.

> For Remotion/AE this plan IS the frame timing: cuts → `from`/`durationInFrames` (or layer in/out), ramps → eased `interpolate`/time-remap, J/L → offset `<Audio from>` / audio layer. See `references/editing-techniques.md` for the NLE↔code mapping table.

### Before you finish — checklist

- [ ] BPM + fps + beat-1 offset captured; frames_per_beat computed and cumulatively rounded.
- [ ] Cuts on phrases (2/4/8 beats), not every beat; accents on the eighth-grid only.
- [ ] The single biggest visual lands on the drop.
- [ ] An arc exists (Establish→Develop→Climax→Resolve); avg shot length shortens toward the climax, then a hold.
- [ ] Hard cut is the default; every other transition is motivated; J/L audio offsets specified in frames.
- [ ] Speed ramps land the slowest frame on the beat; optical-flow/frame-blending enabled.
- [ ] Cut rhythm matches the chosen Motion Personality.
- [ ] Every cut, transition, and retime expressed as a frame number / from-duration so it ports to Remotion/AE/NLE.
- [ ] Audio sync verified: `frame/fps` against detected beat seconds.

## Gotchas

- Cutting on *every* beat is busy; cut on 2/4/8-beat phrases and accent sparingly.
- Speed ramps without consistent motion blur look strobed; enable optical-flow/frame-blending for slow-mo.
- Crossfades/dissolves are not a fix for a bad cut — fix the timing first.
- Audio sync drift: in code timelines verify `frame/fps` against detected beat seconds; in NLEs lock audio to a frame-accurate guide track.
- One pacing throughout = flat. Always shape an arc.

## Reference files

- `references/editing-techniques.md` — BPM→frame math with phrase tables, cut-on-action breakdowns, building a match cut step by step, J-cut/L-cut audio-lead/trail diagrams with frame offsets, full speed-ramp recipe with motion-blur/optical-flow settings, sequence-arc templates with shot-length curves, and mapping an edit plan between an NLE timeline and a code timeline (Remotion `<Sequence>` / AE time-remap).
