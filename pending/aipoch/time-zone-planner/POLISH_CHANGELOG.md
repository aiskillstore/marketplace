# POLISH_CHANGELOG — time-zone-planner

**Original Score:** 84  
**Polish Date:** 2026-03-19

## Issues Addressed

### P0 / Veto Fixes
- None (no veto failures)

### P1 Fixes
- **Region alias ambiguity:** Added "Region Alias Mapping" section with a table showing how short aliases (`US`, `EU`, `Asia`) map to representative IANA timezones, with a note that sub-region specification is recommended for accuracy.
- **Parameters table enriched:** Added `preferred_hours` parameter and updated `regions` description to recommend IANA timezone names. Added format guidance for region input.

### P2 Fixes
- None beyond P1 fixes.

### QS-1 (Input Validation)
- Already present and well-formed.

### QS-2 (Progressive Disclosure)
- File is 115 lines — within 300-line limit. No content moved to references/.

### QS-3 (Canonical YAML Frontmatter)
- Already present with all four required fields.
