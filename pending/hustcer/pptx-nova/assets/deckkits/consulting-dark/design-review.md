# Consulting Dark 2.1 design review

Reviewed 2026-10-25. The source demonstration has ten pages. The updated deck retains all ten,
all source business text, the native comparison table, the native bar chart and its embedded workbook.
The content contract and twenty public layout ids remain compatible with 2.0.

## Design changes

- Use navy on every page. Warm-white primary text, pale supporting text, warm copper proof numbers
  and light teal output relationships establish a dark identity across all ten roles.
- Remove all 35 folded-corner containers from the demonstration. The renderer no longer implements
  facets, and the style gate rejects freeform corner panels and light slide backgrounds.
- Use open history ledgers, achievement quadrants, KPI rails, peer comparisons, audience columns,
  native tabular evidence, shared timelines and open decision requests. Equal peers receive equal styles.
- Retain meaningful solid position/process/output nodes. Derive the output-group brackets from the
  actual node bounds and paint them after node fills in both horizontal and vertical layouts.
- Increase allocated capability/audience/comparison reading text to 13pt, achievement proof values
  to 34pt and chart labels to 12pt. Chart fit, projected budgets and schemas use the same 12pt size.
  Compact labels, native tables, vertical merged capability text and provenance retain validated roles.
- Align the refurbishment fallback palette aliases and Arial font roles with the dark contract.
  That fallback preserves source geometry; it does not reconstruct arbitrary slides into these compositions.

## Validation scope

| Evidence                   | Result                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------- |
| Golden demonstration       | 10/10 canonical PNGs reviewed; Create finalized from the bound candidate                          |
| Alternative compositions   | 10/10 canonical PNGs reviewed; all twenty layout ids covered                                      |
| Maximum-density fixture    | 10/10 canonical PNGs reviewed; six chart values include negative, zero and tiny values            |
| Chinese / mixed fixture    | 4/4 canonical PNGs reviewed; text, table and chart labels checked                                 |
| Benchmark                  | All three cases pass; no visual high, medium or low findings                                      |
| Content/native readback    | All source paragraphs and table cells retained; chart values and workbook unchanged               |
| Style / capacity contracts | Explicit composition, palette, navy background, node layering and fallback alias regressions pass |
| Schema projections / slots | No generated-budget drift; all ten slot-consistency checks pass                                   |
| Structure / compatibility  | ZIP and full-package integrity pass; Microsoft 365 compatibility gate passes                      |
| Native host                | macOS PowerPoint clean-open passed without a Repair dialog for the final golden bytes             |

The stress fixture intentionally exceeds the table soft limits (nine rows and five columns). Its two
advisory diagnostics remain; fit, native data, static vision and canonical rendering pass without
lowering the font floor or hiding findings.

The full repository suite also exposed an existing maintenance mismatch: a test invokes `just list`,
while the current Justfile names the recipe `ls`. This is outside the DeckKit implementation and was
not changed as a side effect of the design task.

The review uses xdoc 0.20.0 with a frozen display date of 2026-10-25. Arial / Arial Unicode MS are not
embedded. A clean-open is not certification of native editing, other Office releases, Windows,
PowerPoint pixel parity or real projection-distance readability. No reference business facts were added.

See the maintained [intent and editing boundaries](intent.md), the
[golden benchmark review](../../../benchmarks/visual/cases/consulting-dark/golden-roadshow/review.md)
and the [editable demonstration](../../examples/deckkits/consulting-dark/deck.pptx).
