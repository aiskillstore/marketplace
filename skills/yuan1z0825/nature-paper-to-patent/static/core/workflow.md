# Patent Generation Workflow

Run all applicable stages. A later stage must not silently repair missing
evidence from an earlier stage.

## Stage 0 - Intake and risk flags

Record the source files, requested deliverables, target jurisdiction,
publication status, known disclosure dates, and missing inventor facts.

Output: `work/00-intake.json`.

Gate: every input file is identified; unknown publication, inventorship, and
ownership facts are explicitly marked.

## Stage 1 - Source map

Extract the entire substantive disclosure, not only the abstract. Assign stable
IDs to text blocks, equations, figures, and supplementary/code evidence. Keep
page, section, caption, file, or line locators.

Output: `work/01-source-map.json`.

Gate: the method, implementation, experiments, limitations, formulas, and
methodology figures have all been inspected or marked unavailable.

## Stage 2 - Technical inventories

Create:

- a terminology ledger with one canonical Chinese term per object;
- an input-operation-output map;
- a formula inventory with symbols and technical role;
- a figure inventory distinguishing methodology figures from result charts;
- an implementation-gap list.

Output: `work/02-technical-inventory.json`.

Gate: every core operation has an identified input and output; every core
formula and source methodology figure has a disposition.

## Stage 3 - Evidence ledger

Convert candidate features into an evidence ledger. Assign support state,
source IDs, technical role, effect, and proposed destination.

Output: `work/03-evidence-ledger.json`.

Gate: no candidate essential feature is `unsupported`; every
`needs-confirmation` feature becomes an inventor question or is removed.

## Stage 4 - Invention concept and claim strategy

Write the one-sentence concept:

`technical problem -> cooperating technical means -> specific technical output/effect`

Select the principal protected object, essential feature chain, fallback
positions, and technically appropriate claim categories. Avoid automatically
adding device, medium, system, or use claims.

Output: `work/04-claim-strategy.json`.

Gate: each essential feature has evidence; the principal claim forms a closed
input-operation-output chain.

## Stage 5 - Claims

Draft the principal independent claim first. Draft dependent claims in the same
technical order, then add other supported categories. Create a claim-feature
map from every material limitation to evidence IDs.

Output:

- `work/05-claims.txt`;
- `work/05-claim-map.json`.

Gate: `scripts/audit_claims.py` has no `ERROR`; every formal claim has mapped
source support; no `[TO CONFIRM]` marker remains in formal claims.

## Stage 6 - Specification and figures

Draft the specification around the claims while adding enough implementation
detail from the source. Include core formulas, symbol definitions, alternatives,
figure descriptions, and embodiments. Generate the main claim-aligned
flowchart and supported methodology figures.

Output: `work/06-draft.json`.

Gate: every claimed term appears in the specification; every claim step is
explained; every figure is referenced; every core formula has editable-math
source and symbol definitions.

## Stage 7 - Abstract and package

Draft the abstract last. Keep terminology aligned with the principal claim.
Use the same main figure as the abstract figure and specification figure.

Output: separate Chinese DOCX files, SVG/PNG figures, structured JSON, and
audit reports under `outputs/`.

Gate: `scripts/validate_patent_draft.py` and
`scripts/build_patent_package.py` complete without errors.

## Stage 8 - Final review

Score evidence support, claim architecture, consistency, enablement,
technical-effect reasoning, formula coverage, and figure alignment. List
unresolved inventor questions and publication risks.

Gate: meet the thresholds in `static/core/output-contract.md`; otherwise label
the package `incomplete draft`.
