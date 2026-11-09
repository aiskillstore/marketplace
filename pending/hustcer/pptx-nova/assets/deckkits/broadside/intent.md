# Broadside 2.0

Broadside is a flat protest-poster editorial language: enormous heavy upright type, near-black
records, fire-orange declarations, warm cream text, monospace metadata, slash bullets and hairlines.
The JSON contract owns colors, font roles, region geometry, capacity and registered compositions.
Its public `createDeck(content)` adapter resolves a component plan and executes that plan; there is
one creation path and no 1.x fallback. Discover fields and layouts with the standard design/slots CLI.

The sixteen retained slide types cover cover, chapter, statement, split image shell, statistics,
fading words, list, quotation, comparison, native bar/column chart, flow, native doughnut chart,
categorical hierarchy, timeline, cycle and closing. Twelve responsibilities have alternative
compositions; the remaining four keep their characteristic geometry. Explicit layouts must fit.
`auto` selects deterministically from fitting compositions and recent rhythm. A complete deck starts
with cover and ends with closing; use `meta.designScope: "excerpt"` for extracts. The skin does not
supply a business argument, facts, sources, dates, units, labels or domain policy.

The original HTML/CSS and design prose occasionally disagree. The actual sixteen DOM pages govern
responsibilities, rather than the stale metadata count of twenty. Statement keeps its observed
chrome; the real four-item list remains supported despite a three-item prose preference. The later
suggestion of Chinese serif/handwritten fonts conflicts with the original unified sans stack; this
implementation keeps a heavy sans heading and regular sans body for bilingual consistency.

## Typography and composition

The source uses Barlow and IBM Plex Mono. This implementation uses available close substitutes,
Arial Black, Arial and Menlo, with Noto Sans SC for CJK. CJK headings explicitly request bold and more
open line spacing; Latin display remains the already-heavy upright Arial Black. Fonts are not
bundled or embedded. Availability, regular/bold appearance and wrapping need checking in each host.
Use sentence case for ordinary English content headings: capitalize the first word and retain the
correct casing of proper names and acronyms, such as PowerPoint and AI. This includes chart titles,
comparison headings, process/cycle steps, timeline milestones and hierarchy labels. A line break
does not start a new heading. All-lowercase display is an optional, deliberate poster treatment for
covers, chapter openers and short declarations, including fading-word slogans and closing calls.
It is not a requirement for every page. Follow a user's or brand's title-case convention when supplied.
Uppercase metadata remains an authoring option. The renderer preserves supplied casing, punctuation
and facts without converting text or rejecting another valid casing choice. CJK has no lowercase
distinction. Negative CSS
tracking is omitted to keep mixed text safe; the two color registers, weight and spatial hierarchy
carry the identity. Small source/chrome text is enlarged and contrast is improved. Faded words use
three readable solid ink tones, rather than relying on low-contrast exceptions.

Content cannot be shortened or dropped by the renderer. Capacity checks use the actual components,
including value+unit text, repetition count and shared comparison bands. They are conservative
estimates; canonical PDF/PNG review remains required. Schema budgets are discovery hints, and dynamic
components still need instance resolution. When no registered layout fits, reorganize or split the
page. Statistics accept display strings without interpreting them as quantities. Hierarchy bars are
categorical levels: their width does not encode a measured value. The vertical flow is a numbered
stage register; the horizontal flow adds directional arrows, and the cycle always closes its loop.

## Numeric objects and 1.x input changes

Bar and doughnut pages require numeric values, `unit`, `source` and `seriesName`. Bar values are
nonnegative and start at zero; zero never receives a fabricated minimum height. At most one bar
may explicitly set `accent: true`; absence means all bars are neutral. `numberFormat` controls the
native bar labels while raw values remain unchanged. Labels may round according to that format;
the canonical renderer may fall back to full values for unsupported formats, so inspect its output.
very small values can be subpixel on a common linear scale. `seriesName` identifies the native
workbook series, even when a redundant one-series legend is hidden.

Doughnut values are nonnegative quantities in the supplied unit, with a positive total. They are
not parsed from percentage strings or silently normalized into a new business measure. For example,
`40` with unit `%` displays 40 percent; `0.4` is a different source quantity. Segment colors follow the
registered single-orange/gray palette. `total` remains an optional content-authored display note.
The independent legend shows values and units from the same source numbers, using bounded decimal
or scientific display precision. Editing native chart data in PowerPoint does **not** update this
separate editable text legend; regenerate from content to synchronize it. Readback verifies every
native category, series name and raw value; it does not prove workbook XML byte equality.

Migration mapping:

- Retain all sixteen `broadside*Slide` type names and the valid title/body/metadata/list fields.
- Remove `bars[].display`; supply numeric `bars[].value`, an explicit unit/source/seriesName and,
  where useful, `numberFormat`. There is no guessed conversion from a currency display string.
- Replace doughnut `items[].value: "40%"` with numeric `40` and explicit unit `%` only when the
  caller knows that is the source meaning. Remove arbitrary `items[].color`.
- Keep `image.split` as a native editable placeholder shell. It still rejects external image assets;
  the reference contains no reusable image. `imageLabel` and `caption` remain optional content.
- The exported `C`, `FONT_DISPLAY`, `FONT_MONO`, `FONT_CN` are aliases of the new contract. Code
  reading retired 1.x color-token names must move to semantic contract roles.

The independent refurbishment profile is retained. A validated creation route does not establish
arbitrary existing-deck preservation, native skinning or animation playback. HTML navigation and
entry animations are excluded. Current readiness and evidence are recorded in the catalog and the
repository migration report, rather than inferred from this intent document.
