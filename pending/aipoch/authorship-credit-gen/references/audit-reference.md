# Audit Reference

## Scope

- Skill: `authorship-credit-gen`
- Core purpose: Use when determining author order on research manuscripts, assigning CRediT contributor roles for transparency, documenting individual contributions to collaborative projects, or resolving authorship disputes in multi-institutional research. Generates fair and transparent authorship assignments following ICMJE guidelines and CRediT taxonomy. Helps research teams document contributions, resolve disputes, and ensure equitable credit distribution in academic publications.
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
