# Gravitas -- Delegation Reference

## The Principle

Subagents are opt-in by spawn condition. The default is single-agent execution. Subagents are added only when they provide measurable benefit exceeding their quota and coordination cost.

Sophistication = knowing when NOT to orchestrate.

## Three Conditional Roles

### Investigator

File: plugins/gravitas-antigravity/agents/investigator.md

Spawn when:
- Uncertainty is high and solution space is genuinely unclear
- Codebase or subsystem is unfamiliar and requires broad exploration
- Search fan-out is high (many files needed to form a plan)

Do NOT spawn when:
- Target file and tests are known and already read
- Task has been done in this codebase before
- Recon is straightforward and bounded

### Verifier

File: plugins/gravitas-antigravity/agents/verifier.md

Spawn when:
- Risk is medium or high (Tier 1+ by classification)
- Implementation confidence is low after completion
- Acceptance criteria are complex or interdependent

Do NOT spawn when:
- Change is trivial and test suite clearly covers it
- Implementation agent can run validators directly
- Task is read-only

### Impact Auditor

File: plugins/gravitas-antigravity/agents/impact-auditor.md

Spawn when:
- A public API or interface is being changed
- A shared abstraction (utility, middleware, base class) is modified
- Dependency fan-out exceeds 5 direct callers

Do NOT spawn when:
- Change is internal/private with no external consumers
- Caller graph has already been fully reviewed in recon
- Scope is well-bounded and self-contained

## Simple Task Rule

Simple tasks (isolated bug fix, single-file change, config update, comment) must use zero subagents. If you find yourself about to spawn a subagent for a simple task, reconsider.

## Spawn Decision Record

When spawning a subagent, emit a decision record:
delegation:
  role: verifier
  reason: auth middleware change, risk high, test coverage unclear
  spawn_condition_met: risk=high AND criteria complex
  expected_benefit: independent verification of auth behavior change
  quota_estimate: medium

## Budget Profiles and Delegation

| Profile | Delegation behavior |
|---------|--------------------|
| eco | No delegation unless completely blocked |
| balanced | Conditional -- follows spawn conditions above |
| deep | Conditional verifier for medium/high risk |
| team | Full parallel decomposition for large projects |
