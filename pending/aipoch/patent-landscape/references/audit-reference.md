# Audit Reference

## Scope

- Skill: `patent-landscape`
- Core purpose: Use when analyzing biotech patent landscapes, identifying white spaces in pharmaceutical IP, tracking competitor patents, or assessing freedom to operate for drug development. Provides comprehensive patent analysis and strategic insights for life sciences innovation.
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
