# Consulting Dark 2.1

An executive consulting language built around a deep navy canvas on every page, decisive warm-white
typography and open evidence structures. Warm copper directs attention to numbers and short indexes;
light teal distinguishes outputs. Neither color is a business policy or a category palette.

The design contract is the numerical authority. Everyday authors use the registered slide types and
`layoutId`; they do not write coordinates. The resolver checks actual text and data capacity, records
each component, and chooses deterministically among legal compositions. Explicit layouts must fit.
If none fits, reorganise or split the content. No field is truncated and no font is shrunk to pass.

## Visual decisions

- Use open ledgers, typographic proof numbers, comparison columns and a shared timeline instead of
  repeating a panel around every item. Cut-corner surfaces are not registered in this version.
  Reserve solid rectangles for the position statement, process engine and editable output nodes.
  Fine rules explain relationships without turning every page into another card grid.
  Preserve different-sized native circle ornaments on cover and decision pages, outside text zones.
  Do not attach colored caps to rounded cards or add shadows and gradients.
- Keep separate visual structures for achievements, audience groups, process flow, comparison and
  roadmap. Equal-role items receive equal styling: an array index never makes a peer a recommended
  option or a current stage. Copper proof numbers share one hierarchy; teal identifies outputs.
  Process arrows enter an open bracket around the whole output group, rather than
  implying that only its first item is produced. Derive this bracket from actual node bounds and
  draw it above their fills so the guides remain continuous.
- Use 13pt for allocated capability, audience and comparison reading regions, 12pt for chart labels,
  and 34pt for achievement proof values. Compact labels, dense native table text and provenance retain
  their validated 10–11.5pt roles. Instance fit checks still reject excess copy instead of shrinking it.
- Keep every role dark, including native table/chart evidence. Slate node fills and fine blue-gray
  rules provide local depth; pale supporting text remains readable against navy. Layout, density and
  typography create the deck rhythm. Do not turn evidence pages light or infer business meaning from
  the dark palette.
- Explicitly request upright Arial and Arial Unicode MS, including regular and bold runs. Fonts are
  not embedded; another font environment requires new visual checks.
- The source note, units, dates, claims and every business label come from content. Example figures
  are synthetic, not product benchmarks. The kit inserts only structural page numbering.

## Roles and composition choices

| Slide type          | Purpose                                             | Layouts               |
| ------------------- | --------------------------------------------------- | --------------------- |
| heroSlide           | Opening argument and project metadata               | split / stacked       |
| profileTableSlide   | Experience history and supporting metrics           | ledger / bands        |
| kpiRowSlide         | Numbered achievements with evidence badges          | quadrants / ledger    |
| previewProductSlide | Product proposition, metrics and capabilities       | strip / rail          |
| landscapeSlide      | Position, alternatives, strengths and limitations   | columns / ledger      |
| multiCardSlide      | Audience or workstream groups                       | columns / ledger      |
| convertFlowSlide    | Source, process, outputs and capabilities           | horizontal / vertical |
| benchmarkSlide      | Native table and single-series bar evidence         | rail / stacked        |
| timelineSlide       | Ordered phases with explicit status and description | horizontal / ledger   |
| askSlide            | Decision statement and concrete requests            | columns / rows        |

The two benchmark layouts change the order of chart and interpretation; they retain the same table.
Table and chart are independent evidence supplied by the author. A displayed callout is not silently
recomputed from a series. Keep its provenance and calculation in the source content.

## Migration from 0.1

The kit id and `createDeck(content)` interface remain. This is a major content-contract change;
old tuples, raw hex accents, aliases and business fallbacks are rejected.

| Former field                                        | 2.0 field                                     |
| --------------------------------------------------- | --------------------------------------------- |
| meta.footerLeft / data.footerLeft                   | data.source, required on every page           |
| profile rows `[period, organisation, role]`         | rows `[{period, organisation, role}]`         |
| profile cards `[accent, value, label, description]` | metrics `[{value, label, note}]`              |
| achievement `[accent, index, title, body, badge]`   | items `[{index, title, body, badge}]`         |
| product kpis `[accent, value, label, note]`         | kpis `[{value, label, note}]`                 |
| competitors `[accent, name, tag, pro, con]`         | comps `[{name, tag, strength, limitation}]`   |
| audiences `[accent, index, name, items]`            | cards `[{index, name, items}]`                |
| outputs `[accent, title, description]`              | outputs `[{title, description}]`              |
| steps `[accent, index, title, description, status]` | steps `[{index, title, description, status}]` |
| asks `[accent, title, description]`                 | asks `[{title, description}]`                 |
| benchmark rows / takeNum / takeTxt                  | tableRows / calloutNum / calloutText          |
| benchmark chart without unit                        | explicit unit; series name is also visible    |
| thankYou / tagline / optional closing               | closing / closingR, both explicit             |

No permanent legacy renderer or implicit input converter ships. The old arbitrary tableWidth,
tableName and chartName knobs are replaced by named component plans. Use the registered layout
instead. Unknown fields fail rather than pretending to affect output.

## Editability and boundaries

All text, circular ornaments, rectangular process nodes, rules, arrows, the benchmark table and the clustered bar chart remain native editable
PowerPoint objects. The chart uses one finite numeric series, with original zero, negative and tiny
values retained. No normalisation or fabricated minimum width is applied. Data labels use General;
the caller supplies units, and a small value may appear in scientific notation.

Changing a chart value in PowerPoint does not update a separate callout or the table. Rebuild from
content for consistent related annotations. The two evidence objects do not imply that their input
datasets must be equal. This kit is not a general chart authoring API.

Schemas and projected budgets are discovery aids. Maximum item counts do not guarantee that every
combination of long text fits every layout. Each component still runs an instance capacity check.
The release report records actual maximum-density, sparse, Chinese, mixed and alternative-layout
coverage, visual review and native-host evidence. Candidate is not automatic production eligibility.

## Compatibility from 2.0

The ten slide types, twenty layout ids and named content fields are unchanged. Rebuild existing content
to receive the open composition; editing an old deck's colors alone does not remove its old container
geometry. The renderer and style gate both reject the retired folded-corner language. See
[the design review and validation record](design-review.md) for the changes and checked scope.

The refurbishment fallback shares the dark palette and Arial font roles. It preserves source object
geometry and does not convert arbitrary source layouts into these open compositions. Its color/font
configuration is distinct from the content-first generator's composition and native readback gates.
