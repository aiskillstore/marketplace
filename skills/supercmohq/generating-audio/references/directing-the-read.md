# Directing the read

These four settings ride on the request as a group, overriding what is stored against the voice
itself. **Send them explicitly whenever delivery matters** — leaving them out doesn't give you the
documented defaults, it gives you whatever that voice was saved with. Start from `stability` 0.5,
`similarity_boost` 0.75 and `style` 0, then move one value at a time so you can tell what changed
the read.

## `stability`

Governs how steady the voice is, and how much a re-run differs from the last. Default 0.5; the
tool accepts 0 to 1.

| Value | Effect | Suits |
| --- | --- | --- |
| Below 0.5 | Broader emotional range; too far down turns random and rushes the delivery | Character work, ad reads with attack |
| 0.5 | The documented starting point | Anything you have no reason to move yet |
| Above 0.5 | Steadier between runs; too far up goes monotone | Long narration, matching a take already made |

On `eleven-v3` this is the most consequential setting, and the vendor describes it there as three broad
regimes rather than a smooth scale. Expect the dial to be coarse on that model: move it in visible steps and don't fine-tune. On `eleven-multilingual-v2` and
`eleven-flash-v2.5` it behaves as a continuous number.

## `similarity_boost`

How closely the output holds to the voice it is built from. Default 0.75. Raising it costs latency,
so raise it only when the read drifts off the voice you chose.

## `style`

Style exaggeration. Default 0. Any non-zero value spends extra computation and can add latency.
**Leave it at 0** — this is the one setting the vendor tells you not to move.

## `speed` (0.7–1.2)

Default 1.0; below slows the read, above speeds it up. Values near the ends degrade quality, so move
in small steps and never to make a long script fit.

## When a read comes out wrong

Almost every bad generation is fixed by regenerating, rewriting the text, or changing the voice —
not by moving a setting.

- **Corrupt or muffled speech** — regenerate that clip.
- **A glitch between paragraphs** — regenerate the clip before it.
- **Quality falling away across a long read** — split it into clips under 800 characters.
- **Drifting language or accent** — pick a voice that covers the language, and keep each clip under roughly 800 characters.
- **Numbers, symbols or acronyms read wrong** — write them out as they should be spoken.
- **Stress landing on the wrong word** — rewrite the line. Punctuation and clause order place  emphasis; no setting will.
- **Over-exaggerated delivery** — set `style` back to 0.
- **Right words, wrong character** — change the voice rather than the settings.
