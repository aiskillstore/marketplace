# Audit Reference

## Scope

- Skill: `open-source-license-check`
- Core purpose: Check if referenced bioinformatics software/code licenses allow commercial use (GPL vs MIT, etc.).
- Use only within the documented workflow and category boundary defined in `SKILL.md`

## Supported Audit Paths

- `python -m py_compile scripts/main.py`
- `python scripts/main.py --help`

## Fallback Boundary

If required inputs are incomplete, the skill should still return:

- the missing required inputs
- the steps that can still be completed safely
- assumptions that need confirmation before execution
- the next checks before accepting the final deliverable
