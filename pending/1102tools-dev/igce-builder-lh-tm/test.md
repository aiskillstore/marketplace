# August 2026 Modernization Test Record

Date: 2026-08-21

Historical April tests remain in [testing.md](testing.md). This file records tests against the portable, progressive-disclosure version.

## Clients and models

- Claude Code CLI 2.1.126, canonical `claude-opus-5`, high effort, explicit `/igce-builder-lh-tm` invocation.
- Codex CLI 0.149.0-alpha.4, GPT-5.6 Sol, xhigh, explicit `$igce-builder-lh-tm` invocation.
- Local Python 3 with openpyxl and LibreOffice headless.

## Behavior results

| Test | Expected | Result |
|---|---|---|
| LH rate plus fair-and-reasonable memo request | Exact Option A/Option B boundary; no data call | Pass on Claude and Codex |
| Raw PWS with labor, AWS, and SaaS but no contract type | Do not default to T&M; decompose; Stage A only | Pass on Claude |
| Stage A terminator | Only decomposition confirmation, no Stage B question | Pass |
| Keyed federal APIs | No call during boundary or Stage A | Pass |

## August 23 host-capability correction

Runtime adaptation now follows a governing host spreadsheet workflow and its hard stops before choosing Python/openpyxl. When the supported workbook path is unavailable, the skill must disclose structured fallback mode before artifact-specific approval and may deliver only a structured JSON specification plus Markdown or CSV tables. Installed-client degradation replay remains an agent-package gate.

## August 23 material-handling validator correction

A multi-period Claude T&M qualification workbook exposed a validator-coverage defect: an injected undisclosed 7% material-handling formula passed the canonical validator even though an independent integrity audit rejected it. The delivered workbook was not defective; all of its handling inputs were numeric zero.

The canonical validator now audits every populated cell beneath a `Material Handling` header. Zero remains the default. A nonzero numeric input or formula passes only when `material_handling_assertions` identifies the exact cell and value or formula and records a non-empty user-supplied accounting or solicitation basis.

Deterministic regression results:

- Valid numeric-zero handling fixture: pass through the integrated validator.
- Undisclosed `=D2*E2*0.07` injection: rejected through the integrated validator.
- The same formula with an exact sidecar assertion and disclosed basis: pass.
- Delivered seven-sheet Claude T&M workbook: pass after LibreOffice recalculation and cached-value audit.

## Workbook fixture

A one-category T&M fixture with cloud-hosting materials was generated outside the repository.

- Formula-structure audit: pass
- Independent low, mid, and high recomputation: pass
- LibreOffice formula execution and cached-value comparison: pass
- Independent mid estimate: matched within validator tolerance

Fault injection:

- `DATEDIF` in the month-gap formula was rejected.
- A cross-sheet reference to Aged Annual Wage instead of an hourly rate was rejected.
- Positive materials in an LH sidecar were rejected.

## Static checks

- Skill frontmatter validator: pass
- Core length: 231 lines at test time
- Python compile and command-line help: pass
- Core-to-reference links: pass

## Regulatory correction verified

The April skill described material handling as a possible percentage fee. The modernized skill treats it as applicable indirect cost only when clearly excluded from labor-hour rates and allocated to direct materials under the contractor's usual accounting procedures. It prohibits arbitrary handling profit and keeps labor burden off materials.

## Open coverage

- A full multi-period T&M workbook with multiple materials classes was not generated in this pass.
- A controlled post-compaction replay test was not available.
- Claude Code implicit activation was not used as a deterministic evaluation surface; explicit invocation was used.
