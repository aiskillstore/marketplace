# Prompt recipes

These are the deterministic templates the CLI assembles for the specialized subcommands. Knowing them helps you reason about output and tune flags.

## `icon`

```
{prompt}, {style} style {type}[, {corners} corners][, {background} background], clean design, high quality, professional[, {N}x{N}px]
```

- `{corners}` clause **only** when `--type=app-icon`
- `{background}` clause **omitted** when `--background=transparent`
- One generation per size in `--sizes`; `{N}x{N}px` appended per call

## `pattern`

```
{prompt}, {style} style {type} pattern, {density} density, {colors} colors[, tileable, repeating pattern], {size} tile size, high quality
```

- `tileable, repeating pattern` clause **only** when `--type=seamless`

## `diagram`

```
{prompt}, {type} diagram, {style} style, {layout} layout, {complexity} level of detail, {colors} color scheme, {annotations} annotations and labels, clean technical illustration, clear visual hierarchy
```

## `story` — per-step template

```
{prompt}, step {N} of {total}, {type-suffix}[, {transition} transition from previous step]
```

`type-suffix`:

| `--type` | Suffix |
|---|---|
| story | `narrative sequence, {style} art style` |
| process | `procedural step, instructional illustration` |
| tutorial | `tutorial step, educational diagram` |
| timeline | `chronological progression, timeline visualization` |

Transition clause appended for steps `2..N`.
