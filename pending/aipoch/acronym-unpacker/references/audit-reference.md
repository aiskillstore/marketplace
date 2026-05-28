# Audit Reference

## Scope

- Skill: `acronym-unpacker`
- Core purpose: Intelligent medical abbreviation disambiguation tool that resolves ambiguous acronyms using clinical context, specialty-specific knowledge, and document-level semantic analysis.
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
