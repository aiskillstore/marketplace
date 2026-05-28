# POLISH_CHANGELOG — patient-consent-simplifier

**Original Score:** 80  
**Polish Date:** 2026-03-19

## Issues Addressed

### P0 / Veto Fixes
- None (no veto failures)

### P1 Fixes
- **PHI/PII check missing from workflow:** Added step 1 as a mandatory sensitive data check. If patient identifiers (name, DOB, MRN, address) are detected in the input, the skill now emits a mandatory warning before proceeding.
- **Input Validation redirect improved:** Added specific redirect suggestion ("consult your institution's IRB template library or a regulatory affairs specialist") for out-of-scope consent drafting requests.

### P2 Fixes
- None beyond P1 fixes.

### QS-1 (Input Validation)
- Already present; redirect message strengthened with actionable alternative.

### QS-2 (Progressive Disclosure)
- File is 115 lines — within 300-line limit. No content moved to references/.

### QS-3 (Canonical YAML Frontmatter)
- Already present with all four required fields.
