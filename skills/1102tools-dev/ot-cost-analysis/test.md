# OT Cost Analysis Modernization Test Record

Tested August 21, 2026 against the portable, progressive-disclosure version. The historical April record remains in `testing.md`.

## Automated validation

- `quick_validate.py` passed the skill directory.
- Both bundled Python scripts compiled, and their command-line help ran successfully.
- A representative seven-sheet prototype OT fixture contained 79 formulas and passed the formula-structure audit, independent recomputation, and LibreOffice formula execution.
- The fixture reconciled total project cost of $754,288.86 and Government funding of $558,339.42 within validator tolerance.
- Every worksheet was rendered and inspected. Number formats and Methodology-sheet spacing found on the first visual pass were corrected, then all seven sheets passed the second visual review.
- The final workbook contained no formula-error strings.

Fault injection:

- Replacing the month-based aging formula with `DATEDIF` was rejected.
- Applying cost-type contribution math to the wrong basis was rejected.
- Reintroducing the false Path D competition-commitment label was rejected.
- Four direct authority checks rejected a 0.32 Path C contribution ratio, a Path D competition-commitment claim, an unsourced Research OT contribution ratio, and a production ratio inherited automatically from a prototype.

## Claude behavior tests

Surface: Claude Code CLI 2.1.238, `claude-opus-5`, high effort, explicit `/ot-cost-analysis` invocation.

1. A $4.2 million proposed-amount request seeking a fair-and-reasonable conclusion and negotiation recommendation produced the exact Option A/Option B boundary, made no tool call, gave no verdict, and ended at `Which option?`.
2. A prototype prompt that mislabeled 10 U.S.C. 4022(d)(1)(D), requested zero performer share, and asked for a default five-percent consortium fee was stopped at the authority gate. Claude corrected Path D to the senior procurement executive's written exceptional-circumstances determination, distinguished 4022(f), refused to default the ratio or fee, and ended at the authority question.

## Codex behavior tests

Surface: Codex CLI 0.149.0-alpha.4, GPT-5.6 Sol, extra-high reasoning, explicit `$ot-cost-analysis` invocation.

1. The proposed-amount request produced the exact Option A/Option B boundary with no verdict or artifact.
2. The authority-mislabel prompt corrected Path D, distinguished 4022(f), and stopped at the first authority question without applying the requested ratio or fee.

## Confirmed gates

- Research, prototype, and follow-on-production contribution arrangements are supplied and sourced, not invented.
- Prototype Path C requires at least one-third of total project cost from non-Federal sources.
- Prototype Path D is not a competition-commitment path.
- Proposed amounts are normalized to a confirmed basis before comparison.
- Consortium and administrative fees default to zero unless rate or amount, base, timing, treatment, and source are supplied.
- Workflow B provides neutral comparison data and never originates the Agreements Officer's determination or negotiation position.
- Keyed federal API calls are serialized with at least three seconds between calls.

## Open coverage

- No live BLS, CALC+, Per Diem, SAM.gov, or other federal API call was made during this pass.
- Claude web, Claude Code after automatic compaction, Codex Desktop UI, and Microsoft Excel were not rerun for this skill.
- Implicit activation was not treated as deterministic; published usage should retain explicit invocation examples.

## August 23 host-capability correction

A normal Codex CLI mixed-milestone workbook run preserved approvals and stopped because the host's governing spreadsheet skill did not expose its supported dependency loader. Runtime adaptation now gives host spreadsheet instructions precedence, prohibits guessed-path or alternate-library bypasses, and requires the available artifact mode to be disclosed before artifact-specific approval. A host without the supported workbook path may deliver only a structured JSON specification plus Markdown or CSV tables, never a completed-workbook claim. Desktop and Claude workbook lanes remain the full-artifact gates.
