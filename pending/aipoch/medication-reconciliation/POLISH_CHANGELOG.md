# POLISH_CHANGELOG — medication-reconciliation

**Original Score:** 83  
**Polish Date:** 2026-03-19

## Issues Addressed

### P0 / Veto Fixes
- None (no veto failures)

### P1 Fixes
- **PHI check missing from workflow:** Added step 1 as a mandatory PHI/data authorization prompt before processing any patient data.
- **Dose-change detection undocumented:** Added step 6 to workflow for dose-change detection. Added `dose_changed` category to Output Format with a JSON example showing the warning message format.

### P2 Fixes
- **Output Format schema clarified:** Replaced the vague "→ Full schema: see original documentation" reference with a complete inline output format description including the new `dose_changed` category.

### QS-1 (Input Validation)
- Already present and well-formed.

### QS-2 (Progressive Disclosure)
- File is 130 lines — within 300-line limit. No content moved to references/.

### QS-3 (Canonical YAML Frontmatter)
- Already present with all four required fields.
