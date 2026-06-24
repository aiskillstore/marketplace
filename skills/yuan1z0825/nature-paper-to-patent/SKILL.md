---
name: nature-paper-to-patent
description: Convert scientific papers, theses, technical reports, source code, figures, or research manuscripts into evidence-grounded Chinese invention patent drafts. Use when an AI agent must extract patentable technical contributions, map every claimed feature to source evidence, preserve core formulas as editable Office Math, generate claim-aligned flowcharts and methodology figures, compare a paper with an existing patent, audit support and consistency, or deliver separate Chinese DOCX files for claims, specification, abstract, and abstract figure.
---

# Paper to Chinese Patent

Use this file as the router for the patent-drafting workflow. Do not draft the
application directly from the paper abstract or contribution list.

## 1. Load the workflow

Read `manifest.yaml`, then read every file under `always_load`.

Detect these axes from the user's files and request:

- `source_format`: selectable PDF, scanned PDF, pasted text, or mixed project;
- `task_mode`: full draft, claim set, disclosure analysis, or paper-patent audit;
- `invention_type`: algorithm/software, apparatus/system, process/material, or mixed.

State the detected values in one short line. Load only the matching fragments
declared in the manifest. Load detailed references only when their condition
applies.

## 2. Preserve source grounding

Create stable source IDs before drafting:

- `P001...` for paper text blocks;
- `E001...` for equations;
- `F001...` for source figures;
- `C001...` for source-code or supplementary evidence.

Every material feature in a formal claim must map to one or more source IDs.
Use only `explicit`, `inherent`, `needs-confirmation`, or `unsupported` as
support states. Exclude `unsupported` features from formal claims.

Never infer inventorship, ownership, unpublished implementation details,
publication dates, prior-art conclusions, or legal sufficiency. Use
`[TO CONFIRM: specific question]` outside formal claims when facts are missing.

## 3. Draft through stage gates

Complete the stages in `static/core/workflow.md` in order. Persist the
intermediate artifacts specified there. Do not move to formal claims until the
source map, terminology ledger, inventories, evidence ledger, and invention
concept pass their gates.

For a full application, draft claims first, then align the specification,
figures, embodiments, and abstract to the claim terminology and step order.

## 4. Produce Chinese formal documents

Agent-facing analysis may use the user's preferred language. Produce formal
Chinese patent deliverables in Chinese:

- 权利要求书;
- 说明书;
- 说明书摘要;
- 摘要附图;
- figure labels and descriptions.

For algorithmic inventions, retain source-supported core formulas, define every
symbol, explain each formula's technical operation, and render formulas as
native editable Office Math in DOCX. Do not use plain LaTeX strings as the
visible formula.

Generate the main flowchart from the ordered steps of the principal method
claim. Its final node must name the concrete domain output, such as a defect
detection result, target pose, state estimate, or control instruction. Reuse
the same main figure as the abstract figure and a specification figure.

## 5. Validate before delivery

Populate the structured draft described in `references/draft-schema.md`, then
run:

```bash
python scripts/validate_patent_draft.py draft.json
python scripts/build_patent_package.py draft.json --output-dir outputs --prefix patent
```

Resolve all validation `ERROR` findings. Review every `WARNING` against the
source. Label the result `incomplete draft` when a required quality threshold
in `static/core/output-contract.md` is not met.

The generated package is a drafting aid for inventor and patent-professional
review, not a patentability opinion, infringement opinion, or filing guarantee.
