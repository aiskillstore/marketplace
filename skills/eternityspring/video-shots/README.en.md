[![中文](https://img.shields.io/badge/%E4%B8%AD%E6%96%87-ece9e7?style=for-the-badge&labelColor=ece9e7&color=8a8785)](README.md)
[![English](https://img.shields.io/badge/English-a02128?style=for-the-badge)](README.en.md)

# video-shots

**Shot breakdown** for a finished film: every shot's **duration, size, category, camera move,
frame description and rhythm role**.

The premise is baked in: **shot boundaries are measured, not eyeballed.** The least reliable
thing a model does with video is report time, so there is a hard line down the middle:

```
Code measures : cuts (ffmpeg scene detection) → duration (cut minus cut, 2 decimals) → motion (median frame difference)
Model judges  : size → category → camera → frame → rhythm  ← these things, and nothing else
Code checks   : 15 quality gates, one by one            ← a wrong call is blocked on the spot
```

![shots-report.html](assets/report.png)

**The report is a single interactive page**: an embedded player (playback highlights the
current shot, click a shot to jump, the timeline fills with progress), a pace strip, a shot
list you can search, filter and sort (list or card view, first and last keyframe side by side,
click a frame to enlarge), distributions, cast, and the quality gates. No external
dependencies — double-click it offline.

The look and the behaviour live in `scripts/report.css` and `report.js`, two **directly
editable assets** that are inlined at render time. You can redesign the report without
touching the generator, and every number on the page is computed from `shots.json`:

<img src="assets/report-mobile.png" width="380" alt="the shot list on a narrow screen">

## The hardest gate: camera claims checked against pixels

If the camera really moved, the pixels cannot stay still. So one direction is **blocked
outright**: claiming push / pull / pan / truck / tracking while the **measured frame-to-frame
change is near zero**. That is the most common hallucination in model shot analysis, and this
catches it every time.

The reverse (claiming static while the measurement is high) is **not blocked** — it only
raises a hint. A locked-off camera pointed at someone dancing produces exactly the same
frame difference. **A gate that fires wrongly is worse than no gate**, so this one only
guards the direction it can actually guard.

```
✅ camera vs. measured motion
Hints (not blocking):
   · S46: annotated "static", measured frame change 12.3 is high — fine if the subject is moving,
     but if the camera is moving the annotation needs fixing
```

## Read contact sheets, not one frame at a time

Two keyframes per shot — **frame a** (15% in) and **frame b** (85% in) — tiled into contact sheets:

- **Sheet a is content**: twenty-odd shots on one screen tells you what the section is about
- **Sheet b is camera work**: compare the same cell across the two sheets. Framing changed →
  push/pull/pan/truck. Framing identical, only the subject moved → static camera

Only go back to a single frame for the few shots you cannot call. Paging through an entire
film one frame at a time is a waste of tokens.

## Detection misses cuts and invents cuts — fix with `recut`, never by hand

Scene detection fails in exactly two places: it **misses** dissolves and dark-on-dark cuts,
and it **invents** cuts on handheld shake and flashes.

```bash
node scripts/video-shots.mjs recut shots.json --track track.json \
  --split 63.5 --split 127.37 --merge 45.97 > shots.new.json
```

It renumbers, recomputes durations and measured motion, and records added cuts in
`manualCuts`. **Shots whose boundaries did not move keep their annotations; shots that were
split or merged have their annotations cleared, with their origin written into `note`** —
whether the two halves are the same thing is something you have to look at again.

Editing `start` / `end` by hand fails the `boundary` gate: **a cut you added must be declared.**

## Quality gates: 15 of them, all code

Same position as the skills this one learned from: **a checklist the model polices itself
against is worthless.**

| Gate | Rule |
| --- | --- |
| **Timeline is continuous** | Sorted, end-to-end, starts at 0.00, lands on the film's duration (tolerance configurable) |
| Duration is self-consistent | `seconds` = `end − start`; a shot under 0.3 s must say in `note` whether it is a flash cut or detector noise |
| Shot numbering | Starts at `S01`, zero-padded, no gaps — the number *is* the keyframe filename |
| Size / category / camera | Three vocabularies checked term by term; left blank is also a failure |
| Transition enum | Optional; if written, it must be in the table |
| **Frame description is checkable** | Long enough (≥ 12 Chinese characters / ≥ 8 English words), no filler ("氛围感" / "visually stunning"…), no "这个镜头…" / "This shot…" openers |
| **No duplicate descriptions** | Two shots word-for-word identical = nobody looked twice |
| Subject reconciliation | Every id in `subjects` must exist in `cast`; with no cast, the gate **says it is skipping** |
| **Categories need evidence** | Dialogue needs a line, a title card needs on-screen text, a reaction needs a subject, an empty shot may not contain people |
| **Camera vs. measured motion** | Claiming a large move while the measurement is near zero → blocked (this direction only). Without `--track` the gate **says it is skipping** |
| **Boundaries come from detection** | Every boundary is either in `seedCuts` or declared in `manualCuts`. Moving a cut out of thin air fails |
| Keyframes present | The report embeds images; a missing one **is reported as missing**, never faked |
| **Rhythm annotation is checkable** | `rhythm` is optional, but it is **all shots or none**; once tagged, the reason must say what the viewer sees, and filler is blocked |

Every gate has a **breaking test case** in the self-test, proving it really blocks:

```bash
node scripts/selftest.mjs
# ✅ 449 assertions passed (every one of the 15 gates has a breaking case)
```

## Usage

```bash
# 1. Cuts and durations (check the shot count on stderr; re-run with a different --threshold if it is off)
node scripts/video-shots.mjs seed video.mp4 --track track.json --title "Title" > shots.json

# 2. Keyframes and contact sheets
node scripts/video-shots.mjs frames shots.json --video video.mp4
node scripts/video-shots.mjs sheet  shots.json --cols 4 --rows 6
node scripts/video-shots.mjs sheet  shots.json --cols 4 --rows 6 --pick b

# 3. Read the sheets, fill in size / category / camera / frame in batches (the model's job)

# 4. Add missed cuts, merge invented ones
node scripts/video-shots.mjs recut shots.json --track track.json --split 63.5 > shots.new.json

# 5. Validate (exit code 1 on any violation)
node scripts/video-shots.mjs validate shots.json --track track.json --frames frames

# 6. Shot list and report (--video points the player at the source film)
node scripts/video-shots.mjs render shots.json --md   --track track.json > shots.md
node scripts/video-shots.mjs render shots.json --html --track track.json \
  --video ../video.mp4 > shots-report.html
```

`--lang zh|en` works on **every command** (default Chinese; precedence is `--lang` > the `lang`
field in the JSON > Chinese): gate names, violation messages, CLI output, the report UI and all
four vocabularies switch together. It switches **labels only** — descriptions, dialogue and names
written by the model are left exactly as they are.

`seed --lang en` records `lang: "en"` in the working draft, so every later command follows English
without repeating the flag — down to the `note` that `recut` writes when it adds a cut, and the
punctuation in the English tables.

The frame-description gate follows **the language of the description itself**, not the UI
language: Chinese is counted in characters (≥ 12), English in words (≥ 8), and each has its own
filler list ("氛围感" / "visually stunning") and its own banned openers ("这个镜头…" / "This shot…").

Requirements: `node` >= 18 (standard library only) + `ffmpeg` / `ffprobe`.
**No npm dependencies, no API keys.**

## Bundled example

`examples/demo-shots.json` — a complete breakdown of a 202.9-second AI short film.

| | |
| --- | --- |
| Shots | 53 |
| Average / median shot | 3.83 s / 3.16 s |
| Shortest / longest | 0.33 s (a flash cut of running through snow) / 16.06 s (the closing shot in a shaft of light) |
| Cuts per minute | 15.7 |
| Top categories | dialogue 58%, reaction 10%, insert 9% |
| Top camera | static 55%, handheld 42% |
| Manual cuts | 10 (half dissolves, half end-title cards), all recorded in `manualCuts` |
| Gates | all 15 green, with two hints left in as examples (measured motion vs. a static call; six end-card shots in a row flattening the rhythm) |

It is both the quality benchmark and the self-test fixture.

## Run it yourself

`demo-report/` at the repository root is the **complete output** for that example
(report + 106 keyframes + the data). Double-click `shots-report.html`. To reproduce from scratch:

```bash
node scripts/video-shots.mjs seed ../../demo-video.mp4 --threshold 0.15 --track track.json > shots.json
```

## Credits

The way this skill is written, the visual language of the report, and the position that
**quality gates must be deterministic code** are learned from
[eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) (Apache-2.0).
The methodology has been internalised into this directory's own `references/` —
**the skill is self-contained and depends on no external skill.**

That set of skills runs the forward pipeline, novel → storyboard → video. This one runs it
backwards: **finished film → shot table.** The `size` and `camera` vocabularies line up on
both sides, so a breakdown can be fed straight back in as a reference for imitation.
