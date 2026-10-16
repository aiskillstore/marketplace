# Gravitas -- Task Contract Reference

A task contract is a machine-readable declaration established at the start of any complex task. It defines the mode, objective, acceptance criteria, scope boundaries, and budget profile.

## When to Use

Use a task contract when:
- The task has multiple acceptance criteria
- The allowed write scope should be constrained
- The task must run in a specific mode (plan-only, research, etc.)
- Interruption recovery may be needed

## Schema

{
  "mode": "implement",
  "objective": "add cursor pagination to /posts endpoint",
  "acceptance_criteria": [
    "supports cursor parameter",
    "preserves existing response shape",
    "adds tests covering cursor and edge cases",
    "does not modify authentication"
  ],
  "non_goals": ["do not add offset pagination"],
  "risk": "medium",
  "budget": "balanced",
  "allowed_write_scope": ["src/routes/posts.ts", "tests/posts.test.ts"],
  "verification": "targeted"
}

## Modes

| Mode | Allowed writes | Use when |
|------|:------:|----------|
| answer | None | Pure question answering |
| research | None | Codebase exploration only |
| plan | None | Planning/design work, no implementation |
| review | None | Code review, no changes |
| debug | Limited | Diagnosis + targeted fix |
| implement | Scoped | Standard feature/fix work |
| migration | Confirmed | Schema/data migrations (destructive risk) |
| security-review | None | Security audit only |

Legacy contracts may use `plan-only` / `review-only`; the runtime accepts
them as aliases of `plan` / `review`. New contracts should use the
canonical names.

## Action Lock

In read-only modes (answer, research, plan, review, security-review), the runtime blocks writes and non-query shell execution at hook level before they reach the model. Prompt compliance is not relied upon.

## Policy Dimensions

Beyond `risk` / `budget`, contracts may declare explicit policy dimensions
(see `schemas/contract.json`: `action_risk`, `reversibility`,
`uncertainty`, `blast_radius`, `verification_depth`, `reason_codes`).
Absent dimensions are treated as unknown, never as safe. The planning
policy (`gravitas decide`) consumes these plus task signals and emits a
machine-readable planning record.

## Acceptance Criteria

Each criterion maps to a required evidence entry in the ledger. The Stop hook checks all criteria before allowing task completion.

Write criteria as verifiable outcomes, not process steps:
- GOOD: "returns 400 on invalid cursor"
- BAD: "handle edge cases appropriately"

## Allowed Write Scope

List specific files or directory prefixes. The PreToolUse hook blocks writes outside this scope.

## Interruption Recovery

The contract is written to .gravitas/sessions/<task-id>/contract.json at task start. If interrupted, the new context reads the contract and resumes from the evidence ledger state.
