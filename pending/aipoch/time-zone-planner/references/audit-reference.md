# Audit Reference

## Supported Scope

- Recommend meeting windows across a fixed set of regions.
- Explain timezone tradeoffs and local-time conversions.
- Keep outputs bounded to scheduling support rather than live calendar coordination.

## Stable Audit Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py
```

## Fallback Boundaries

- If participant regions are missing, request them before proposing a final schedule.
- If the user asks for real-time DST validation or live availability checks, state that those require external confirmation.
- If conflicting constraints cannot all be satisfied, return the least-bad option and explain the tradeoff instead of inventing a perfect overlap.

## Output Guardrails

- Separate known inputs from assumed time-window preferences.
- Keep recommended windows explicit by region.
- Call out any manual confirmation still required before a meeting is booked.
