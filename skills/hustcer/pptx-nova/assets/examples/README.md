# pptx-nova Examples

Examples are grouped by purpose. Bundled DeckKit showcases are synthetic, generated materials
intended to be redistributable with the skill; source examples demonstrate workflow input formats.

| Directory                           | Purpose                                       | Entry points                                                                        |
| ----------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------- |
| [`deckkits/`](deckkits/README.md)   | Curated editable DeckKit showcases            | `manifest.json`, then `<id>/` with source content, PPTX, preview, brief and summary |
| [`generator/`](generator/README.md) | Exploratory generator for DeckKit development | Template plus its adjacent generated themes                                         |
| [`create/`](create/README.md)       | Creation input examples                       | Quarterly review outline and quarterly-report patch                                 |
| [`edit/`](edit/README.md)           | Existing-deck edit examples                   | Title patch and Micro Edit evidence matrix                                          |

Use DeckKit content and the standard create runner for ordinary delivery. The generator is a
development starting point for creating or extending DeckKits.

Showcase manifests and summaries retain the metadata of their generation run. Their recorded
`readiness` can differ from a later promotion; use the current
[DeckKit catalog](../deckkits/catalog.json) and readiness audit for selection eligibility.
Regeneration can legitimately change metadata when the catalog changes.

`just deckkit-examples` updates only `deckkits/`; it does not replace this index or the other examples.
Use `just deckkit-examples -d broadside` for one showcase, `just deckkit-examples check` to check
reproducibility without writing committed assets, or `just deckkit-examples all` for all visual cases.
Each `just` invocation uses a fresh temporary run unless an explicit `--tmp` or `--out` is supplied.

Keep new examples in the owning directory and generator dependencies adjacent. Preserve showcase
manifest hashes and update the deck catalog whenever asset paths change.
Full and single-kit updates keep manifest entries in the DeckKit catalog's order.
