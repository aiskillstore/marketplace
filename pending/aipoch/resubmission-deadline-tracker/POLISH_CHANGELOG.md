# POLISH_CHANGELOG — resubmission-deadline-tracker

**Original Score:** 84  
**Polish Date:** 2026-03-19

## Issues Addressed

### P0 / Veto Fixes
- None (no veto failures)

### P1 Fixes
- **Timezone default undocumented:** Added step 2 to workflow with an explicit timezone default note. When `--timezone` is not provided, the skill now emits a note stating it defaults to `Asia/Shanghai` and provides guidance to specify timezone explicitly.
- **Urgency level boundary gap:** Fixed the Urgency Levels table — the 3–7 day range was inconsistent with the actual 3–14 day boundary for Urgent mode. Added a clarifying note.

### P2 Fixes
- None beyond P1 fixes.

### QS-1 (Input Validation)
- Already present and well-formed.

### QS-2 (Progressive Disclosure)
- File is 120 lines — within 300-line limit. No content moved to references/.

### QS-3 (Canonical YAML Frontmatter)
- Already present with all four required fields.
