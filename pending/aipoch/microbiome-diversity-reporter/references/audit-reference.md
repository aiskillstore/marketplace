# Audit Reference

## Scope

- Skill directory: `microbiome-diversity-reporter`
- Core purpose: Interpret Alpha and Beta diversity metrics from 16S rRNA sequencing results.
- Use only within the documented workflow and category boundary defined in `SKILL.md`

## Supported Audit Paths

- `python -m py_compile scripts/main.py`
- `python scripts/main.py --help`
- `python scripts/main.py -h`

## Fallback Boundary

If required inputs are incomplete, the skill should still return:

- the missing required inputs
- the steps that can still be completed safely
- assumptions that need confirmation before execution
- the next checks before accepting the final deliverable
