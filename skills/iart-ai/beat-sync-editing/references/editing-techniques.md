# Editing Techniques — Detailed Cookbook

Concrete recipes for rhythm, transitions, and retiming, with the math to make cuts frame-accurate.

## BPM → frame math

```
frames_per_beat = (60 / BPM) * fps
seconds_per_beat = 60 / BPM
```

Reference (frames per beat):

| BPM | 24 fps | 25 fps | 30 fps | 60 fps |
|----|----|----|----|----|
| 90  | 16.0 | 16.7 | 20.0 | 40.0 |
| 100 | 14.4 | 15.0 | 18.0 | 36.0 |
| 120 | 12.0 | 12.5 | 15.0 | 30.0 |
| 128 | 11.25| 11.7 | 14.06| 28.13|
| 140 | 10.3 | 10.7 | 12.86| 25.7 |

When `frames_per_beat` is fractional (e.g. 128 BPM at 30 fps = 14.06), round each *cumulative* beat to avoid accumulating drift:

```js
const cut = (i) => Math.round(i * (60 / bpm) * fps); // round at the end, not per-step
```

Cut on phrases, not beats:

| Energy | Cut every |
|---|---|
| Frantic / climax | 1–2 beats |
| Energetic | 4 beats (1 bar in 4/4) |
| Moderate | 8 beats (2 bars) |
| Calm / establishing | 16 beats (4 bars) |

Detect BPM offline (aubio, `web-audio-beat-detector`, or tap-tempo) and also capture the *offset* of beat 1 — the grid rarely starts at 0:00.

## Cut on action / cut on motion

The eye tracks moving subjects; a cut placed mid-motion is masked by that movement.

- Identify a continuous action spanning two shots (door opening, head turn, object thrown).
- Place the cut roughly one-third into the action, and continue the *same* action and direction in the next shot.
- Match screen direction (subject moving left exits left, enters from right) and velocity.
- In motion graphics: cut while a shape is mid-travel (transform velocity high), not when it has settled — the motion blur and momentum hide the splice.

## Match cut, step by step

A match cut equates two shots via a shared visual so the cut reads as a transformation.

1. Find or design a shape/position/motion shared by the end of shot A and the start of shot B (a round clock → a round wheel; an arm wiping frame → next scene revealed).
2. Align them in screen space: same size, same position, same orientation at the cut frame.
3. Match motion vector and speed across the cut so momentum carries through.
4. Cut on the exact frame where the two forms register; a 1–2 frame mismatch breaks the illusion.
5. Optionally add a 1–3 frame motion-blur bridge to fuse them.

Common forms: graphic match (shape), motion match (direction/velocity), audio match (a sound bridges the cut), and the "invisible wipe" where a foreground object wipes the frame and the next shot is revealed behind it.

## J-cut and L-cut

Audio and picture do not have to cut at the same frame.

```
J-CUT  (audio of B leads its picture — pulls forward)
  Picture:  AAAAAAAA | BBBBBBBB
  Audio:    AAAAA BBBBBBBBBBBBB
                  ^ B's audio starts ~6–12 frames early

L-CUT  (audio of A trails under B's picture — smooths)
  Picture:  AAAAAAAA | BBBBBBBB
  Audio:    AAAAAAAAAAAA BBBBBB
                       ^ A's audio continues ~6–18 frames past the picture cut
```

Typical offsets: dialogue J-cuts 4–12 frames; ambient L-cuts 12–24 frames. In an NLE, unlink audio/video and trim only the audio edge. In a code timeline, place the `<Audio>` for shot B with a `from` earlier than B's picture sequence.

## Speed ramp recipe (with motion blur)

```
Impact ramp, 30 fps, drop on frame 28:
  Frame   Speed     Note
  0–20    100%      run-up, normal motion blur
  20–28   100%→25%  ease-OUT deceleration into the hit
  28      25%       IMPACT, lands on the downbeat
  28–34   25%→100%  ease-IN re-acceleration
  34+     100%      release
```

Settings:
- Use smooth (Bezier) interpolation on time-remap keyframes; linear ramps look mechanical.
- Enable **optical flow** (or frame-blending) for sub-100% speeds so slow-mo isn't strobed; optical flow generates intermediate frames.
- Keep motion-blur shutter consistent across the ramp — if the source has motion blur, the slow section keeps it; if synthetic, hold a constant shutter angle (e.g. 180°).
- Land the slowest frame *on the beat*; the ramp is felt, the impact is heard.

In AE: enable time remapping, keyframe the source time, ease the keyframes, set frame blending to Pixel Motion. In Remotion: drive a remapped source time via eased `interpolate` and keep effects deterministic.

## Sequence arc templates

```
30s social spot (≈ 900 frames @30fps):
  Establish  0–120    2 shots, ~2s each (longer holds)
  Develop    120–540  shots shortening 1.5s → 0.8s, rising energy
  Climax     540–720  fastest cuts 0.3–0.5s, the drop at ~600
  Resolve    720–900  one long hold, logo/CTA breathes
```

Plot average shot length as a curve: high at the start, descending to the climax, then a single long shot to release. Energy is the *derivative* of cut frequency — accelerate cuts to build, decelerate to land.

## NLE timeline vs code timeline

| Concept | NLE | Remotion | After Effects |
|---|---|---|---|
| Clip placement | drag to track at TC | `<Sequence from durationInFrames>` | layer in/out points |
| Back-to-back shots | adjacent clips | `<Series>` | trimmed layers |
| Crossfade | overlap + dissolve | overlap `Series` + opacity interp | opacity keyframes / overlap |
| Speed ramp | time-remap keyframes | eased source-time `interpolate` | time remap + frame blending |
| J/L cut | unlink + trim audio | `<Audio from>` ≠ picture seq | offset audio layer |
| Beat marker | timeline markers | beat array `frame/fps` | comp markers / expression |

To port an edit plan: express each cut as a frame number (from the BPM math), each clip as `from`/`duration`, each transition as an overlap, and each retime as an eased time-remap. The plan is renderer-agnostic; only the placement syntax differs.

## Example edit plan (portable)

```
Track: 128 BPM, 30fps → 14.06 f/beat, drop at beat 32 (frame 450)
Cut on 4-beat phrases (≈56 frames):
  f0    ShotA  establish, hold
  f56   ShotB  cut on action (subject turns)
  f112  ShotC  match cut from B (shared circle)
  f168  ...    cuts shorten toward climax
  f450  DROP   biggest visual; speed ramp 100→25→100 around f450
  f700  CTA    long hold, L-cut audio trails in
```

---
Cut on the beat and ramp with purpose and the edit moves with the music. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=motion-design-skills&utm_content=skill_footer&utm_term=beat-sync-editing)** — the AI motion agent for editable, on-brand motion graphics.
