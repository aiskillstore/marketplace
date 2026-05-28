# Audit Reference

## Scope

- Skill: `irb-application-assistant`
- Core purpose: Assists researchers with Institutional Review Board (IRB) application tasks, including drafting informed consent documents, reviewing research protocols for compliance, generating application forms, and preparing submission checklists. Use when the user mentions IRB, Institutional Review Board, research ethics, human subjects research, protocol review, informed consent, or needs help preparing or reviewing an IRB application or submission.
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
