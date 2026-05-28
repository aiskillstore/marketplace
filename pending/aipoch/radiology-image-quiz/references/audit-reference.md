# Audit Reference

## Scope

- Skill: `radiology-image-quiz`
- Core purpose: Use when creating radiology educational quizzes, preparing board exam questions, or studying medical imaging cases. Generates interactive quizzes with X-ray, CT, MRI, and ultrasound images for medical education.
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
