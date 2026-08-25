# August 2026 Modernization Test Record

Date: 2026-08-21

Historical April tests remain in [testing.md](testing.md). This file records tests against the portable, progressive-disclosure version.

## Clients and models

- Codex Desktop, GPT-5.6 Sol, xhigh: behavior review and workbook inspection.
- Codex CLI: full raw-PWS and continuous-coverage workbook builds.
- claude.ai, Opus 5 Max: fresh-chat implicit activation and Workflow B boundary.
- Claude Code CLI 2.1.126, canonical `claude-opus-5`, high effort: explicit skill invocation for boundary, approved handoff, and raw-PWS staging.

Claude Code noninteractive `-p` did not reliably activate the skill implicitly, even with a front-loaded description and a canonical FFP prompt. Explicit `/igce-builder-ffp` invocation was deterministic. This is recorded as client discovery behavior because the same body passed when explicitly invoked and activated implicitly in claude.ai.

## Behavior results

| Test | Expected | Result |
|---|---|---|
| Workflow B memo and determination request | Emit Option A/Option B boundary, no data call, stop | Pass on Codex and Claude |
| Approved staffing handoff | Preserve staffing; skip decomposition and Stage A; batch Stage B | Pass on Claude Opus 5 and Codex |
| Hybrid handoff | Retain only FFP CLINs; surface conflicts; wait | Pass on Codex |
| Raw PWS | Decompose; Stage A only; stop at confirmation | Initial Claude run previewed Stage B; instruction repaired; exact rerun passed |
| Continuous 24x7 coverage | Use 8,760 / 1,880 = 4.6596 FTE | Pass |
| Zero-night day trip | Use city lookup, zero lodging, one discounted M&IE | Pass |
| Keyed API pacing | Serialize calls with at least 3 seconds between completions and starts | Pass; 9 calls, shortest observed gap 5.883 seconds |

## Workbook validation

Two generated seven-sheet workbooks passed:

- Formula-structure audit
- Independent Python recomputation
- LibreOffice headless formula execution and cached-value comparison
- ZIP integrity
- Visual inspection of all sheets

Six fault-injection workbooks were rejected for their intended defects, including incorrect aging, wrong cross-sheet row, incompatible coverage hours, and formula-structure failures.

## Static checks

- Skill frontmatter validator: pass
- Python compile and command-line help: pass
- Markdown links and relative references: pass
- Host-specific literal sweep: pass
- `git diff --check`: pass at the FFP checkpoint

## Open limitation

Claude Code post-compaction replay was not tested with a controlled harness. The core keeps every load-bearing gate front-loaded, and detailed references remain one level deep.

## August 23 host-capability correction

A normal Codex CLI run correctly stopped because the host's governing spreadsheet skill did not expose its supported dependency loader. Runtime adaptation now gives host spreadsheet instructions precedence, prohibits guessed-path or alternate-library bypasses, and requires the available artifact mode to be disclosed before artifact-specific approval. A host without the supported workbook path may deliver only a structured JSON specification plus Markdown or CSV tables, never a completed-workbook claim. Desktop and Claude workbook lanes remain the full-artifact gates.
