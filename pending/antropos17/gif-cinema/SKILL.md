---
name: gif-cinema
description: Generate short GPT GIF shots, review their continuity, choose retakes, and assemble them into a film using the public GIF Cinema CLI.
---

# GIF Cinema

Create a small film from individually reviewable animated shots. This skill runs a
public, source-available CLI; it is not the private Studio application. It requires
Python 3.10+, Git, Pillow, and FFmpeg. Script execution also requires ffprobe. New GIF
generation requires the user's own OpenAI API key, billing and model access.

## Set up and verify

Use an isolated environment and the pinned reference-enabled public runtime:

```text
python -m venv .venv
```

Activate that environment using the current shell's normal activation command, then:

```text
python -m pip install --upgrade pip "setuptools>=77" wheel
python -m pip install --no-build-isolation "gif-cinema @ git+https://github.com/antropos17/chatgpt-gif-cinema.git@41c06dd09ebe5b40c8e5173abd4a2e5fd8a1eb70"
python -m gif_cinema --help
ffmpeg -version
ffprobe -version
```

Keep the runtime's [evaluation license](https://github.com/antropos17/chatgpt-gif-cinema/blob/41c06dd09ebe5b40c8e5173abd4a2e5fd8a1eb70/LICENSE): personal non-commercial evaluation/research is permitted; commercial use, redistribution and hosting require permission. The included LICENSE preserves those terms.

Run this skill's `scripts/smoke_test.py --out NEW_DIRECTORY` with that environment's
Python (resolve the helper path relative to this skill directory, not the current
project) to verify synthetic GIF inspection, endpoint extraction, continuity reporting,
MP4 assembly and unchanged source hashes without a key. When real ffprobe is present,
the same check also executes and resumes a zero-call film script. The helper creates
a new dedicated output directory and refuses to overwrite an existing one.

## Direct the film

Translate the user's idea into a few short actions with a beginning, response and
payoff. Describe each shot's first/last pose, camera, subject scale, horizon and motion
direction. Keep identity details stable while allowing deliberate camera changes.
Read the pinned runtime's [script schema](https://github.com/antropos17/chatgpt-gif-cinema/blob/41c06dd09ebe5b40c8e5173abd4a2e5fd8a1eb70/docs/SCRIPT-FORMAT.md)
before authoring a JSON script. Source paths and still-image references resolve
relative to that script, not the shell directory.

The skill includes a real three-shot astronaut example in `assets/example/`: three
16-frame GPT GIFs plus `film.json`. From this skill's folder, run:

```text
python -m gif_cinema render assets/example/film.json --dry-run
python -m gif_cinema render assets/example/film.json --execute --max-api-calls 0 --out output/first-film
```

From another project, resolve the script to its absolute path and put output in that
project's own new directory. This produces a 7.68-second silent MP4 without a key.
It preserves native drawing cadence; the showcased private smoothing is separate.

Plan first, without a key or paid request:

```text
python -m gif_cinema render film.json --dry-run
```

For a source-only montage:

```text
python -m gif_cinema render film.json --execute --max-api-calls 0 --out output/edit-01
```

For authorized generation, use the agreed call cap and `--retries 0` initially.
Read OPENAI_API_KEY from the user's environment without displaying or saving it.
Account/model support is checked by the actual request; a model label in this
historical runtime is not a promise of current access. Unsupported input, permission
errors and uncertain delivery need review before another paid attempt.

## Chain and replace shots

Use `endpoints SHOT.gif -o UNIQUE_PREFIX` to obtain `UNIQUE_PREFIX-last.png`.
For the next generated shot, the JSON `references` field accepts local still PNG,
JPEG or WebP files. Use the clean identity reference plus the reviewed previous last
frame; explain which controls identity and which controls composition. This runtime
supports explicit references in `render`, not in the simple `generate` command.
Its supported frame range is 2–16; longer frame delays extend playback rather than
creating additional motion. Review each shot before passing its endpoint onward.
Render dependent shots in separate small scripts/output directories as their
references become available; preflight rejects missing future reference files.
Then assemble accepted GIFs as `source` entries in a final import-only script.
Keep each source entry mapped to its generating script and output directory.

For a retake, retain the original generating script and render directory, revise only
the target shot, then dry-run again. Execute with `--force-shot SHOT_ID`, an explicit call cap
and `--retries 0`. Accepted unchanged neighbors are reused by hash. The runtime
preserves older shot files and archives the previous tracked movie on replacement;
keep them for rollback. Multiple candidates use separate copied scripts/output
directories. This public runtime has no automatic take ranking or graphical undo.
Update the final montage's `source` only after choosing the reviewed replacement;
retain the old montage script/export to undo that choice.

Watch a replacement inside the full montage and inspect **both** neighboring cuts:
identity, costume/props, pose, scale, camera geography, lighting and action direction.
Pixel MAE and successful decoding are technical evidence, not visual acceptance.
Changing a middle shot does not automatically regenerate its neighbors.

## Deliver

Verify the exact exported MP4 and playback before linking it. Report native GIF
frames separately from export FPS. This public package does not include the private
editor, RIFE smoothing, automatic last-frame dependency graph or generated sound.
Use actual matching usage plus current official rates for a cost estimate; identify
discarded takes and references, and distinguish an estimate from a billing charge.
Describe remaining visual faults directly and keep private keys, prompts and
unreviewed artifacts out of any public deliverable.
