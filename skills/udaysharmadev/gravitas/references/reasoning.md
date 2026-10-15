# Gravitas -- Adaptive Reasoning Reference

## The Core Principle

Reasoning depth must be proportional to expected error cost, not to task size or preference for showing thorough work.

Do not apply:
- Fixed token floors (always think 4K tokens for medium tasks)
- Always-on deep reasoning for every coding task
- Reasoning theater (visible thinking that does not change the output)

Do apply:
- Deeper reasoning when getting it wrong is expensive
- Brief reasoning when the path forward is unambiguous
- Explicit reasoning when the user needs to understand the decision

## Reasoning Depth Formula

reasoning_depth = base
  + risk_weight(risk_tier)
  + uncertainty_weight(requirement_clarity)
  + fan_out_weight(dependency_count)
  + failure_weight(prior_failed_attempts)
  + irreversibility_weight(can_this_be_undone)
  + deficit_weight(missing_evidence_for_decision)

## Reasoning by Scenario

| Scenario | Depth | Why |
|----------|-------|-----|
| Typo fix in config | Minimal | Low risk, obvious path |
| New utility function | Brief | Contained scope, reversible |
| Multi-file feature | Moderate | Multiple failure modes |
| Auth/security change | Deep | High irreversible risk |
| Ambiguous requirements | Deep | Uncertainty requires exploration |
| 2nd attempt after failure | Deep | Prior approach failed, need different angle |
| Schema migration | Maximum | Destructive, production impact |

## Selective CoT

Research (2026) found mandatory CoT across all tasks can reduce instruction-following accuracy. Selective application recovers the loss.

Practical rule:
- Emit explicit reasoning when it changes what you do or helps the user decide
- Do not emit reasoning as proof of thoroughness
- A decision record (see SKILL.md) is better than narrated chain-of-thought

## Red Flags for Under-Reasoning

- Going from task description directly to code without a plan
- Attempting the same approach that failed in the same session
- Missing a non-obvious dependency that a brief impact analysis would catch
- Writing to a file before understanding its current state

## Red Flags for Over-Reasoning

- Extended analysis of trivial, single-line, fully reversible changes
- Multiple alternatives for a task with one clear solution
- Subagent spawning for a fix that stays within one file
