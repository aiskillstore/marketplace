# AI assist

The meta-primitive: hand a natural-language problem description to a backend-side LLM agent that combines the other primitives ([logs](logs.md), [metrics](metrics.md), [db-health](db-health.md), [advisor](advisor.md), [policies](policies.md), [metadata](metadata.md)) on its own and returns a diagnosis plus suggested solutions.

**Unlike every other primitive in this skill, `diagnose --ai` returns suggestions, not just observations.** Verify before acting.

## Command

```bash
npx -y @insforge/cli diagnose --ai "<issue description>"
```

The description should include: the error / failing URL / HTTP status / function slug — whatever concrete signal the user has.

## When to use first

- User pasted an error, request URL, or status code and asks "why?"
- You want a fast first pass before deciding which primitive to drill into
- The problem spans multiple subsystems (frontend + backend + database) and the right starting primitive isn't obvious

## When to skip

- The symptom clearly maps to one primitive (e.g., "Vercel deploy failed" → go straight to [deploy-state](deploy-state.md))
- You're doing a proactive audit (no concrete error — that's [advisor](advisor.md))
- You already know exactly which log source has the error

## How to verify the output

The agent's diagnosis names primitives and observations. Re-check each:

| If the diagnosis says... | Verify with... |
|--------------------------|----------------|
| "An RLS policy is blocking the request" | [policies](policies.md) — read the actual policy on that table |
| "Slow query on table X" | [db-health](db-health.md) `slow-queries` + [logs](logs.md) `postgres.logs` for the actual query |
| "Function is timing out" | [logs](logs.md) `function.logs` — read the actual timeout/error stack |
| "Connection pool exhausted" | [db-health](db-health.md) `connections` — confirm the count and idle-in-transaction state |
| "Missing index on column Y" | [db-health](db-health.md) `index-usage` + [advisor](advisor.md) performance — both should agree |

If the verification disagrees with the diagnosis, **trust the primitive observation**, not the suggestion. Suggestions can be plausible-sounding but wrong (LLM may pattern-match on similar errors); raw `pg_stat` numbers and log lines can't lie.

## Boundaries

- **Returns suggestions, not just data.** Different from every other primitive — treat the output as a starting hypothesis, not a verdict.
- **Doesn't replace [advisor](advisor.md).** Advisor surfaces issues based on a static rule catalog; `--ai` reasons about a specific reported symptom. They serve different goals.
- **Consumes the other primitives.** When this fails or seems off, fall back to the primitives directly.

## Example

User pastes: "I invoked `https://kttprzh4.functions.insforge.app/newton` and got `508: Loop Detected (LOOP_DETECTED). Recursive requests to the same deployment cannot be processed.`"

```bash
npx -y @insforge/cli diagnose --ai "I invoked edge function https://kttprzh4.functions.insforge.app/newton, got error: 508: Loop Detected (LOOP_DETECTED)\n\nRecursive requests to the same deployment cannot be processed."
```

Read the diagnosis and suggestions, then verify with:

```bash
# Verify with function logs
npx -y @insforge/cli logs function.logs --limit 50

# Verify the function code doesn't actually call itself
npx -y @insforge/cli functions code newton
```

## Frequently paired with

- All other primitives — `--ai` consumes them and you verify back against them. Treat AI assist as a router that points at primitives; the primitives are the ground truth.
