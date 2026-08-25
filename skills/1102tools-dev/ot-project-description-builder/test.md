# OT Project Description Builder Modernization Test Record

Tested August 21, 2026 against the portable, progressive-disclosure version. The April record remains in `testing.md` with a supersession notice for obsolete authority and contribution statements.

## Automated validation

- `quick_validate.py` passed the skill directory.
- `scripts/validate_docx.py --help` and Python compilation passed.
- A representative seven-page Resilient Autonomous Resupply Prototype project description passed DOCX ZIP, Heading 1 order, milestone-table, deliverables-table, placeholder-closeout, artifact-separation, dynamic-TOC, and update-fields-on-open checks.
- The fixture used 14 ordered Heading 1 sections, four milestones, five deliverables, five fixed-geometry tables, a page-number field, and a dynamic TOC field.
- Exact table geometry passed for every table: `tblW`, `tblInd`, `tblGrid`, and each cell width reconciled.
- Six fault-injected copies were rejected for the expected reasons: chat-only handoff leakage, currency leakage, Prototype OT mis-citation to 10 U.S.C. 4021, false Path D competition-commitment language, a blank milestone completion criterion, and a `[TBD]` without an owner.

## Render and visual review

- Rendered with LibreOffice through the Codex document renderer to seven page PNGs and a PDF.
- Inspected every rendered page. The first pass exposed narrow columns and mid-word wrapping in the seven-column Milestone Schedule.
- The fixture was rebuilt with exact weighted column geometry and deliberate header wrapping, then rerendered and re-inspected page by page.
- The final render had no clipped text, overlapping content, broken glyphs, accidental blank pages, or orphaned sections. Long tables used repeating headers and non-splitting rows.
- The TOC remained a valid dynamic field with a placeholder in LibreOffice. Microsoft Word was not retested, so LibreOffice rendering is not recorded as proof of Word behavior.

## Claude behavior tests

Surface: Claude Code CLI 2.1.238, `claude-opus-5`, high effort, explicit `/ot-project-description-builder` invocation.

1. A request to choose between 10 U.S.C. 4021 and 4022 and select whichever 4022(d) path avoided contribution requirements was rejected. Claude explained the authority boundary, corrected the Path D premise, created no file, and stopped at the authority questions.
2. A user-approved Path C software workflow scenario with no TRL model produced the required Decision Summary, used observable maturity evidence instead of inventing TRLs, left every Payment Type pending, identified unresolved owners and closeout triggers, created no file, and stopped at the milestone-approval question.

## Codex behavior tests

Surface: Codex CLI 0.149.0-alpha.4, GPT-5.6 Sol, extra-high reasoning, explicit `$ot-project-description-builder` invocation.

1. The authority self-selection prompt was stopped at the first authority question with no file or path selection.
2. The no-TRL software scenario produced the required Decision Summary, kept Payment Type and unresolved agreement facts pending, converted the supplied 95-percent threshold to auditable evidence, created no file, and stopped at the approval question.

## Confirmed gates

- 10 U.S.C. 4021 is used for Research OTs, 4022 for Prototype OTs, and 4022(f) for follow-on production.
- Path D is the senior procurement executive's written exceptional-circumstances determination, not a competition commitment.
- Authority, participant status, significant participation, contribution treatment, successful completion, and follow-on eligibility remain user- or Agreements Officer-supplied facts.
- TRL is optional and is not forced onto software, process, or business-workflow prototypes.
- The project-description `.docx` and chat-only milestone handoff remain separate.
- Cost, funding, pricing, labor, and skill-routing content stays outside the agreement artifact.
- Data rights are recorded by deliverable and are not defaulted to a FAR or DFARS clause.
- The milestone structure is approved before document generation.

## Open coverage

- Research OT and primary follow-on-production project descriptions were not generated as DOCX fixtures in this pass.
- Claude web, Claude Code after automatic compaction, Codex Desktop UI, and Microsoft Word were not rerun for this skill.
- Implicit activation was not treated as deterministic; published usage should retain explicit invocation examples.

## August 22 delivery-instruction regression

The delivery contract now gives one tested dynamic-field refresh sequence: open the document in Word, select all with `Ctrl+A` or `Cmd+A`, then press `F9` or `Fn+F9`. A right-click-only TOC instruction is not accepted. Client replay remains required at the agent-package release layer.
