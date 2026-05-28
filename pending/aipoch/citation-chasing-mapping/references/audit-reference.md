# Audit Reference

## Scope

- Skill: `citation-chasing-mapping`
- Core purpose: Use when identifying seminal papers in a research field, mapping research lineage and intellectual heritage, discovering related work through reference tracking, or finding potential collaborators through co-citation analysis. Maps citation networks to trace research evolution, identify influential papers, and discover hidden connections in scientific literature. Supports systematic reviews, bibliometric analysis, and research planning through comprehensive citation tracking.
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
