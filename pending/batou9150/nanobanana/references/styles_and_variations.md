# `generate` — full reference

## `--styles` (artistic styles)

Each value is appended as `, <style> style` to the base prompt.

| Value | Effect |
|---|---|
| photorealistic | Photographic-quality output |
| watercolor | Watercolor painting |
| oil-painting | Oil painting technique |
| sketch | Hand-drawn sketch |
| pixel-art | Retro pixel art |
| anime | Anime / manga |
| vintage | Vintage / retro aesthetic |
| modern | Contemporary |
| abstract | Abstract |
| minimalist | Clean, minimal |

## `--variations` (parameterized variants)

Each variation expands into **two** suffixes — doubling the prompt count.

| Variation | Suffix A | Suffix B |
|---|---|---|
| lighting | dramatic lighting | soft lighting |
| angle | from above | close-up view |
| color-palette | warm color palette | cool color palette |
| composition | centered composition | rule of thirds composition |
| mood | cheerful mood | dramatic mood |
| season | in spring | in winter |
| time-of-day | at sunrise | at sunset |

## Combination rules

1. If both `--styles` and `--variations` are passed, variations are applied to **each** styled prompt.
2. If only `--count=N` is passed (no styles/variations), N copies of the same prompt are submitted.
3. The expanded prompt list is **truncated** to `--count` if the count is smaller.

Example: `--styles=watercolor,sketch --variations=lighting --count=4`
expands to:
- `..., watercolor style, dramatic lighting`
- `..., watercolor style, soft lighting`
- `..., sketch style, dramatic lighting`
- `..., sketch style, soft lighting`
