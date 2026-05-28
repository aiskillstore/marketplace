# Audit Reference

## Scope

- Skill: `nih-biosketch-builder`
- Core purpose: Generate NIH Biosketch documents compliant with the 2022 OMB-approved.
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
