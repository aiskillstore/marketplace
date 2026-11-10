# Biennale Yellow 2.0

Warm paper, disciplined ink, editorial display type and solar yellow form the identity.
Yellow carries a structural plane, an atmospheric bloom or one data emphasis; it is not a body-text color.
Thin rules organize programmes and evidence. Keep the quiet institutional rhythm without cards,
shadows, decorative icons, photography or screenshot backgrounds. Ember remains atmospheric decoration.

`design.json` owns palette, fonts, regions, text styles, decorations, spacing, capacity preferences and
executable checks. `biennale-editorial/v1` resolves the eight editorial roles; the evidence renderer
supplies three native chart compositions. Every page enters the same complete design plan. The kit
entry exports `createDeck`, `DESIGN`, `C` and font aliases, all derived from that contract.

Use `layoutId: "auto"`. Covers offer `poster` and `wide`; manifestos offer `statement` and `reading`.
Programme, chapter, data, quote, calendar and colophon use their registered role-specific composition.
Evidence offers `chart-left`, `chart-wide` and `chart-top`. Explicit choices still need to fit. Actual
programme text heights, combined KPI value+suffix, all four credit instances and every table cell are
checked together. Overflow fails with field paths; split or reorganize content rather than hiding it.
Approximate font measurement never replaces canonical PDF/PNG review.

The nine slide type names remain public. All non-data fields retain their responsibilities. A calendar
is an editable native four-column table containing date, title, venue and length, including all four
headings. A complete deck opens with a cover and closes with a colophon. Short extracts and proof-only
decks need no invented editorial pages; set `meta.designScope: "excerpt"` to make that intent explicit.

## Data migration from 0.2

`biennaleDataSlide.data.bars[].value` is now a finite number; `pct` is rejected. Add explicit `unit` and
`source`. The native chart geometry, labels and workbook use this one numeric model. Optional
`numberFormat` is `#,##0`, `#,##0.##` or `0.00E+00`; absent format selects scientific notation for very
small/large observations. Zero, fractional and negative observations remain exact source numbers.
At most one observation may carry `accent: true`. KPI value/suffix strings remain display text.

The bundled Aurora fixture treats the former displayed counts (76,400; 112,800; 141,200; 164,900;
182,300) as its synthetic source data, in visitors. Former decorative proportions are discarded;
this is an explicit fixture correction, not a conversion rule for external data. Ambiguous old
inputs fail with a migration diagnostic. Choose authoritative source values before migrating them.
There is no old renderer, implicit string parser, compatibility switch or permanent legacy kit.

## Rendering and release evidence

Large editorial text and safe footer margins intentionally improve the old baseline. The programme
panel gives numbered entries enough width and separator clearance. Native gradient blooms preserve
the solar identity. The CJK font is Arial Unicode MS, chosen from installed fonts for the validation
environment; Latin display/body/mono use Times New Roman, Arial and Courier New. Other environments
must supply these fonts or independently review substitutions, regular/bold and mixed-script output.

New 2.0 evidence controls readiness; old production status is not inherited. The catalog records the
current status. Readability, native chart/table editing and no-Repair save/reopen checks concern the
exact reviewed candidate, not arbitrary future content or historical PPTX files.
