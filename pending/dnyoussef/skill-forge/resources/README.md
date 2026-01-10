# Skill Forge Resources

Supporting scripts and utilities for the Skill Forge SOP.

## Scripts

### validate_skill.py

Validates skill structure, metadata, and conventions.

**Usage:**
```bash
python validate_skill.py <path-to-skill>

# JSON output
python validate_skill.py <path-to-skill> --json
```

**Checks:**
- YAML frontmatter format and required fields
- Directory structure and file organization
- Resource references (all referenced files exist)
- Imperative voice usage (heuristic check)

**Exit Codes:**
- 0: All validations passed
- 1: Some validations failed

### package_skill.py

Creates distributable .zip package of a skill.

**Usage:**
```bash
python package_skill.py <path-to-skill>

# Custom output directory
python package_skill.py <path-to-skill> --output <output-dir>
```

**Features:**
- Creates timestamped .zip file
- Maintains directory structure
- Excludes Python cache and system files
- Shows file count and package size

**Output:**
- `{skill-name}-{timestamp}.zip` in parent directory (or specified output dir)

## Installation

These scripts require Python 3.7+ with PyYAML:

```bash
pip install pyyaml
```

## Integration with Skill Forge SOP

These scripts are referenced in:
- **Phase 6**: Validation Testing (uses `validate_skill.py`)
- **Phase 7**: Quality Review (uses `package_skill.py` for deployment)

## Examples

**Validate a skill:**
```bash
cd ~/.claude/skills
python skill-forge/resources/validate_skill.py my-new-skill
```

**Package for distribution:**
```bash
python skill-forge/resources/package_skill.py my-new-skill --output ~/Desktop
```

**Automated pipeline:**
```bash
# Validate then package
python skill-forge/resources/validate_skill.py my-skill && \
python skill-forge/resources/package_skill.py my-skill
```

## Troubleshooting

**Import Error: No module named 'yaml'**
```bash
pip install pyyaml
```

**Permission Denied**
```bash
chmod +x validate_skill.py package_skill.py
```

**File Not Found**
- Ensure you're providing the full path to the skill directory
- Check that SKILL.md exists in the skill directory
