# native-transparent-imagegen

[简体中文](README.md) | [English](README.en.md)

[![Native-alpha Tuanzi and Hutao case](assets/tuanzi-hutao-native-alpha-example.png)](../../examples/native-transparent-imagegen-tuanzi-hutao.md)

Generate and verify PNG or WebP assets with native alpha transparency. The skill targets
stickers, sprites, character assets, product cutouts, and fine-edged subjects such as fur,
hair, glass, or smoke where post-generation background removal is unacceptable.

This is not a magic transparency prompt and it never treats a checkerboard as proof. It
generates one asset at a time, validates the untouched original, retries within a fixed limit,
and fails clearly when the file remains RGB. It does not use matting, chroma key, segmentation,
or locally synthesized alpha to manufacture success.

## Native transparency versus a visual imitation

| Output | File evidence | Skill verdict |
|---|---|---|
| Model-native transparency | Encoded PNG/WebP alpha with both transparent and visible pixels | Continue to fine-edge visual QA |
| Drawn checkerboard | RGB file containing gray and white squares | Fail |
| Post-generation extraction | Opaque source later segmented, keyed, or masked into alpha | Not native generation |

A viewer may display transparent pixels over black, white, or a checkerboard. None of those
previews proves transparency. The untouched model output must be decoded and inspected; a correct
prompt, a successful tool call, or a `.png` suffix is not acceptance evidence.

## What the skill enforces

1. **Scope.** Handle newly generated assets that explicitly require native transparency. Route
   removal from an existing opaque image to a disclosed background-extraction edit workflow.
2. **Serialization.** Generate one asset at a time on prompt-only built-in image surfaces unless
   concurrent native-alpha behavior is currently verified.
3. **Original bytes.** Do not resize, optimize, composite, or rewrite alpha before validation.
4. **Hard gate.** Report format, dimensions, SHA-256, encoded alpha, extrema, fully transparent
   pixels, and corner alpha for every requested deliverable.
5. **Bounded retry.** Allow at most three native-generation attempts per asset by default, then
   fail instead of rescuing an opaque image with extraction.
6. **Visual QA.** After metadata passes, inspect fur tips, matte fringes, low-alpha haze, unintended
   shadows, and cropping over contrasting viewer backgrounds.
7. **State separation.** Keep `generated`, `alpha-validated`, `edge-inspected`, `user-accepted`,
   and `published` distinct.

## First-version Tuanzi and Hutao fur case

The displayed image is the untouched PNG returned by built-in ImageGen using a first-version
Tuanzi and Hutao character sheet supplied directly by the rights holder. Fine fur and a plume tail
make the gap between model-native alpha and later background removal especially visible.

| Field | Inspected value |
|---|---|
| Dimensions | 1536×1024 |
| Format / mode | PNG / RGBA |
| Alpha extrema | 0–254 |
| Fully transparent pixels | 854,016 (54.2969%) |
| Corner alpha | 0 / 0 / 0 / 0 |
| SHA-256 | `066d5b134cbc267a52bbca681afc742b7c64cc2313e1cd77ff3fce5180a8fbb8` |
| Postprocessing | None |
| Provenance | Original C2PA / GPT Image markers preserved |

The repository preserves the original generated-media provenance instead of stripping metadata.
The file passes the technical alpha gate but retains broad low-alpha atmospheric haze around the
fur. It demonstrates that native alpha exists; it is not presented as a perfectly clean
production cutout. See the [full case record](../../examples/native-transparent-imagegen-tuanzi-hutao.md)
for all three attempts, prompts, and failure boundaries.

## Install

```sh
git clone https://github.com/ZSeven-W/craft-skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R craft-skills/skills/native-transparent-imagegen \
  "${CODEX_HOME:-$HOME/.codex}/skills/"

python3 -m pip install -r \
  "${CODEX_HOME:-$HOME/.codex}/skills/native-transparent-imagegen/scripts/requirements.txt"
```

## Invoke

```text
Use $native-transparent-imagegen with my authorized character reference to create a transparent
PNG sticker. It must contain model-native alpha. Do not use background removal, chroma key,
segmentation, or a drawn checkerboard.

Generate and validate one untouched original at a time. If three attempts still lack real alpha,
report failure.
```

For an explicitly selected API surface with output controls, request:

```json
{
  "background": "transparent",
  "output_format": "png"
}
```

The API parameter still does not replace final-file validation.

## Validate the original

```sh
python3 \
  "${CODEX_HOME:-$HOME/.codex}/skills/native-transparent-imagegen/scripts/validate_alpha.py" \
  --require-transparent-corners \
  /path/to/original-output.png
```

The script is read-only. A passing file reports encoded alpha, extrema, transparent pixel counts,
corner values, and SHA-256. An RGB checkerboard fails with `missing-alpha-channel` and a nonzero
exit status.

## Read more

- [Agent workflow and trigger boundaries](SKILL.md)
- [Full English guide](../../docs/native-transparent-imagegen.md)
- [中文使用指南](../../docs/native-transparent-imagegen.zh-CN.md)
- [First-version Tuanzi and Hutao fur case](../../examples/native-transparent-imagegen-tuanzi-hutao.md)
- [Back to Craft Skills](../../README.en.md)

**Status: v0.1 experimental.** Native transparency and its host toolchain may change. Fini Yang
explicitly authorized the displayed image for this skill case; the characters and artwork remain
rights-reserved and are not Apache-2.0 licensed. See
[THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md).
