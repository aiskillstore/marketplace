# Audit Reference

## Supported Scope

- Build or refine biotech fundraising narratives from user-supplied scientific, clinical, and business context.
- Support stage-aware and audience-aware framing for investor communication.
- Keep outputs bounded to messaging structure, not investment advice or factual diligence completion.

## Stable Audit Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Fallback Boundaries

- If the user lacks stage, audience, or evidence inputs, request the minimum missing fields before drafting a final narrative.
- If the request implies unsupported market, valuation, or regulatory certainty, keep the answer at the assumption and scenario-planning level.
- If script execution fails, provide a manual deck scaffold rather than implying a validated investor narrative.

## Output Guardrails

- Separate confirmed facts from narrative framing.
- Call out unsupported claims, missing diligence, and review dependencies.
- Keep legal, regulatory, and financial advice explicitly out of scope.
