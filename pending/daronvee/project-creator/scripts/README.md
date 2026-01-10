# Project Creator Scripts

## validate_project.py

**RECOMMENDED**: Python validation script (cross-platform, no bash required)

Validates that a CCGG Business Operations project has all required mechanisms.

**Usage**:
```bash
py scripts/validate_project.py <project-name>
```

**What it checks**:
- Project folder exists
- CLAUDE.md exists with PARENT SYSTEM INTEGRATION section
- All 4 sub-sections present (Index Sync, Operations Logging, Strategic Alignment, Cross-Project Intelligence)
- README.md exists
- Active Projects Index entry exists
- operations_log.txt entry exists
- No template variables left unreplaced

**Exit codes**:
- 0: Validation passed (or passed with warnings)
- 1: Validation failed (errors found)

**Examples**:
```bash
py scripts/validate_project.py ccgg-offers-pricing
py scripts/validate_project.py magnetic-content-os
```

---

## validate_project.sh

**LEGACY**: Bash version of validation script (use validate_project.py instead)

Same functionality as validate_project.py, but requires bash shell (Git Bash or WSL on Windows).

**Usage**:
```bash
bash scripts/validate_project.sh <project-name>
```

**Note**: Python version (validate_project.py) is preferred for cross-platform compatibility.

---

## create_project.py (Planned - Not Yet Implemented)

Automated project structure creation script.

**Planned usage**:
```bash
py scripts/create_project.py <project-name> --complexity <simple|complex>
```

**Planned functionality**:
- Prompt for project details (title, purpose, scope, etc.)
- Assess project complexity (simple vs complex)
- Create project folder structure
- Copy appropriate template files
- Replace template variables with user input
- Create Active Projects Index entry
- Log to operations_log.txt
- Run validation
- Report project creation summary

**Status**: Not implemented yet. For now, use manual creation workflow in SKILL.md.

---

**Development Note**: Scripts are being migrated from bash to Python for cross-platform compatibility. Python scripts can run on Windows, macOS, and Linux without requiring bash shell.
