# Audit Reference

## Scope

- Skill: `ectd-xml-compiler`
- Core purpose: Automatically convert uploaded drug application documents (Word/PDF) into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.
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
