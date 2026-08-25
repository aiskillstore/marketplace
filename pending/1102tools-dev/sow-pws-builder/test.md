# SOW/PWS Builder Modernization Test Record

Tested August 21, 2026 against the modernized skill. The historical April test record remains in `testing.md`.

## Automated validation

- `quick_validate.py` passed the skill directory.
- `scripts/validate_docx.py --help` and Python compilation passed.
- A representative eight-page Enterprise Service Desk PWS fixture passed the DOCX ZIP, heading-order, QASP, separation, dynamic-TOC, and update-fields-on-open checks.
- The fixture used 13 ordered Heading 1 sections, six structured tables, repeating table headers, explicit table geometry, a page-number field, and a dynamic TOC field.
- Six fault-injected copies were rejected for the expected reasons: staffing handoff leakage, SOC/FTE leakage, CLIN handoff leakage, the incorrect FAR 37.102(d) citation, the incorrect FAR 52.237-2 key-personnel citation, and a missing QASP Summary.

## Render and visual review

- Rendered with LibreOffice through the Codex document renderer to eight page PNGs and a PDF.
- Inspected every rendered page. The first pass exposed table rows splitting across pages. The fixture was rebuilt with non-splitting rows and repeating headers, then rerendered and re-inspected.
- The final render had no clipped text, overlapping content, broken glyphs, accidental blank pages, or orphaned Heading 1 sections.
- The TOC remained a valid dynamic field with a placeholder in the LibreOffice render. The skill correctly requires a Word field refresh disclosure when Word has not populated it.
- Microsoft Word was not retested in this pass. LibreOffice rendering is not recorded as proof of Word behavior.

## Claude behavior tests

Surface: Claude Code CLI 2.1.238, `claude-opus-5`, explicit `/sow-pws-builder` invocation.

1. A rich FFP help-desk prompt with one 24x7x365 Tier 1 seat and 1,880 productive hours produced 4.6596 FTE for the coverage floor, preserved SOC 43-4051, kept staffing in chat, did not create a file, and ended at the staffing confirmation question.
2. A CPFF research-support prompt that asked the model to choose the form was stopped at the FAR 16.306(d) gate. Claude explained Completion and Term, refused to originate the choice, and ended by asking the user to confirm one form.

## Codex behavior test

Surface: Codex CLI 0.149.0-alpha.4, GPT-5.6 Sol, extra-high reasoning, explicit `$sow-pws-builder` invocation.

- The CPFF self-selection prompt was stopped at the required gate. Codex presented Completion and Term without choosing either and ended at the confirmation question.

## Confirmed gates

- Staffing, SOC, IGCE, CLIN, and pricing content stays outside the contract-file artifact.
- FAR 37.602(b)(1), not FAR 37.102(d), is used for results-oriented PWS language.
- T&M/LH labor-category rates, estimated hours, and overall ceiling inputs remain in the chat-only Section B handoff.
- CPFF Completion versus Term is user-confirmed.
- A 24x7x365 seat at 1,880 productive hours is 4.6596 FTE.
- Tier 1 help-desk intake remains SOC 43-4051.
- Both the staffing gate and Decision Summary gate stop and wait for approval.

## Open coverage

- Claude web, Claude Code after automatic compaction, Codex Desktop UI, and Microsoft Word were not rerun for this skill in this pass.
- Implicit activation was not treated as deterministic; published usage should retain explicit invocation examples.
