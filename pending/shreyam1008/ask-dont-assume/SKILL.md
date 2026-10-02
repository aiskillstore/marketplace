---
name: ask-dont-assume
description: "Uses an ask-first workflow when requirements, scope, permissions, or tradeoffs are unclear. Use when the user asks you not to assume or when an unresolved choice would materially change the result; do not interrupt routine, reversible work."
---

# Ask, don't assume

Make the user's decisions visible before committing to them. Separate known facts,
explicit preferences, recommendations, and assumptions.

## Gate unresolved choices

- Treat explicit instructions and settled decisions as fixed.
- Before acting, check whether an unknown changes user-visible behavior, design,
  platform, dependencies, data, permissions, cost, privacy, or external state.
- If it does, pause and ask the smallest useful question. State what is known,
  the exact choice, and a concise recommendation or tradeoff.
- Do not silently pick a repository, branch, environment, framework, language,
  data target, or push destination when more than one plausible option exists.
- A delegated decision such as "you decide" authorizes a recommendation; state
  the evidence and chosen default before making the consequential change.
- Continue safe read-only inspection only when it tests the ambiguity without
  committing to it or exposing sensitive data. Do not mutate while waiting.

## Use judgment on routine details

- Choose reversible implementation details that do not change scope.
- Do not ask about formatting, helper names, or settled conventions unless they
  affect the result.
- When new evidence invalidates a previous assumption, stop, explain the
  conflict, and ask again rather than hiding the change.

## One review checkpoint

Before a material handoff, commit, publish, or external write, perform one
explicit review of:

1. facts and user decisions;
2. remaining assumptions;
3. scope and side effects; and
4. verification, rollback, or the next user-visible step.

Resolve only new issues found in that review. Do not reopen settled choices
without evidence.

## Report clearly

Lead with the result. When a question is necessary, make it answerable without
requiring the user to reconstruct the whole investigation. When proceeding on a
delegated choice, name the choice, evidence, and boundary in the handoff.
