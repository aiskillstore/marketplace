# Audit Reference

## Scope

- Skill: `cross-disciplinary-bridge-finder`
- Core purpose: Use when identifying collaboration opportunities across fields, finding experts in complementary disciplines, translating methodologies between scientific domains, or building interdisciplinary research teams. Identifies synergies between scientific disciplines, matches researchers with complementary expertise, and facilitates cross-domain collaborations. Supports interdisciplinary grant applications and innovative research team formation.
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
