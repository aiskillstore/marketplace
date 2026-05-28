# Audit Reference

## Scope

- Skill: `patent-claim-mapper`
- Core purpose: Use when mapping patent claims to products, analyzing patent infringement, or preparing freedom-to-operate analyses. Compares patent claims against product features for biotech and pharmaceutical IP assessment.
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
