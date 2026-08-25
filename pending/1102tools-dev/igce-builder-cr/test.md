# August 2026 Modernization Test Record

Date: 2026-08-21

Historical April tests remain in [testing.md](testing.md). This file records tests against the portable, progressive-disclosure version.

## Clients and models

- Claude Code CLI 2.1.126, canonical `claude-opus-5`, high effort, explicit `/igce-builder-cr` invocation.
- Codex CLI 0.149.0-alpha.4, GPT-5.6 Sol, xhigh, explicit `$igce-builder-cr` invocation.
- Local Python 3 with openpyxl and LibreOffice headless.

## Behavior results

| Test | Expected | First run | Final result |
|---|---|---|---|
| CPFF fair-and-reasonable memo request | Exact Option A/Option B boundary and no data call | Claude added one workflow-label sentence | Instruction strengthened; exact Claude rerun and Codex run passed |
| Raw exploratory-research BAA with no contract type | Do not self-select CPFF; decompose; Stage A only | Claude bundled an assumptions-or-hold choice into Stage A | Instruction strengthened; exact rerun ended at decomposition confirmation and passed |
| Keyed federal APIs | No calls in boundary or Stage A tests | None | Pass |

## August 23 host-capability correction

Runtime adaptation now follows a governing host spreadsheet workflow and its hard stops before choosing Python/openpyxl. When the supported workbook path is unavailable, the skill must disclose structured fallback mode before artifact-specific approval and may deliver only a structured JSON specification plus Markdown or CSV tables. Installed-client degradation replay remains an agent-package gate.

## Workbook fixture

A one-labor-category CPFF fixture with non-fee-bearing travel was generated outside the repository. Results:

- Formula-structure audit: pass
- Independent cost, fee, and estimated-price recomputation: pass
- LibreOffice formula execution and cached-value comparison: pass
- Independent total estimated price: matched within validator tolerance

Fault injection:

- Replacing the month-gap formula with `DATEDIF` was rejected.
- Referencing the aged-annual-wage row as a cross-sheet rate was rejected.

## Static checks

- Skill frontmatter validator: pass
- Core length: 238 lines at test time
- Python compile and command-line help: pass
- Core-to-reference links: pass

## Open coverage

- A full multi-period CPAF workbook and CPIF 3-by-3 scenario workbook were not generated in this modernization pass.
- Formula assertions for CPAF pool outcomes and CPIF min/max bound crossings remain required in each build's validation sidecar.
- Claude Code implicit activation and post-compaction replay were not treated as deterministic test surfaces; use explicit invocation for CLI evaluation.
