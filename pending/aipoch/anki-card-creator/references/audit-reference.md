# Audit Reference

## Supported Scope

- Create Anki-style study cards from structured medical study content.
- Support Q/A text files and simple structured card generation for drug and anatomy topics.
- Keep outputs bounded to supplied content and declared study goals.

## Stable Audit Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Fallback Boundaries

- If the user provides raw prose instead of structured study content, convert only after stating the assumptions and card-selection logic.
- If the input is incomplete, request the minimum missing fields instead of inventing answers.
- If direct execution fails, provide a manual card blueprint rather than claiming successful deck generation.

## Output Guardrails

- Keep cards atomic and non-duplicative.
- Separate assumptions from extracted facts.
- Flag any content that still requires domain review before import into Anki.
