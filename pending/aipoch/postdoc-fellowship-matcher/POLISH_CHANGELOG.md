# POLISH_CHANGELOG — postdoc-fellowship-matcher

**Original Score:** 79  
**Polish Date:** 2026-03-19

## Issues Addressed

### P0 / Veto Fixes
- None (no veto failures)

### P1 Fixes
- **Fellowship database details missing:** Added "Field Input Normalization" section with alias mapping table (e.g., `neuro` → `neuroscience`). Added link to `references/fellowships.md` from the Fellowship Database section.
- **references/fellowships.md created:** New file with full fellowship details (NIH F32, NSF PRFB, HFSP, EMBO, MSCA, Schmidt Science Fellows) including eligibility, deadlines, duration, and official URLs.

### P2 Fixes
- **Input Validation redirect improved:** Added specific redirect suggestion ("consult your institution's postdoc office") for out-of-scope application writing requests.

### QS-1 (Input Validation)
- Already present; redirect message strengthened.

### QS-2 (Progressive Disclosure)
- Fellowship details moved to `references/fellowships.md` to keep SKILL.md concise.

### QS-3 (Canonical YAML Frontmatter)
- Already present with all four required fields.
