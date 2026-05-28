# Audit Reference

## Scope

- Skill: `discussion-section-architect`
- Core purpose: Structures and writes discussion sections for academic papers and research reports. Use when writing a discussion section, interpreting research results, connecting findings to existing literature, addressing study limitations, synthesizing conclusions, or drafting any part of an academic discussion. Helps researchers organize arguments, contextualize data, and produce clear, publication-ready discussion prose.
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
