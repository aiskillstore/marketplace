# Audit Reference

## Supported Scope

- Blind manuscripts for double-blind review using supported local file formats.
- Remove or highlight likely identity cues such as names, affiliations, contact details, acknowledgments, and self-citations.
- Keep outputs bounded to anonymization preparation, not final publication compliance.

## Stable Audit Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Fallback Boundaries

- If no valid manuscript file path is provided, stop and request the file path instead of pretending the anonymization ran.
- If the file format is unsupported, provide a manual review checklist and known risk areas.
- If `python-docx` is unavailable, limit automated processing to `.md` and `.txt` or report the dependency gap explicitly.

## Output Guardrails

- Separate automated changes from remaining manual review items.
- Never claim complete anonymity without a final human review.
- Call out metadata, figure labels, and supplementary files as separate risk surfaces.
