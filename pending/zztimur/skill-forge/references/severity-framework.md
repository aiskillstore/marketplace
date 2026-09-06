# Severity Framework

Use these severity levels for fixes.

## Critical

The skill may not load, trigger, validate, package, or perform its core task. Also use Critical for serious safety/security problems.

Examples:

- Missing or invalid `SKILL.md`
- Invalid frontmatter
- Multiple unintended `SKILL.md` entrypoints
- Description so vague the skill will not reliably trigger
- Core required script is missing or broken
- Bundled secrets, credentials, private keys, or destructive commands
- Required connector/API/tool is not documented or unavailable with no fallback

## High

The skill works in some cases but will fail or behave unreliably in common real-world use.

Examples:

- Trigger description misses common user intents
- Workflow skips important steps
- Required inputs/outputs are unclear
- Scripts exist but are not documented, tested, or safely runnable
- References are necessary but not linked from `SKILL.md`
- Common edge cases are not handled

## Medium

The skill is usable but has unclear instructions, missing edge cases, or avoidable friction.

Examples:

- Some vague language requiring inference
- Error handling is present but incomplete
- Resource organization could be cleaner
- Simulations reveal partial failures in uncommon but realistic cases
- Instructions are too verbose or duplicated

## Low

Minor quality, polish, formatting, naming, or maintainability issue.

Examples:

- Slightly awkward wording
- Non-blocking naming inconsistency
- Missing small example
- Minor output formatting ambiguity

## Nit

Tiny wording, style, or cosmetic improvement.

Examples:

- Typo
- Punctuation issue
- Tiny markdown cleanup
- Display-name polish

## Fix Entry Format

For each issue, include:

- **Severity:** Critical, High, Medium, Low, or Nit
- **Evidence status:** Verified, Inferred, or Unverified
- **Evidence:** exact file/section, command output, or simulation basis; include a finding code when relevant
- **File/section:** where the issue appears
- **Problem:** concise description
- **Why it matters:** practical impact
- **Recommended fix:** concrete action
- **Example patch:** revised wording or patch when useful
- **Re-test:** the check that would confirm the fix, especially for Critical and High issues

Do not report an Unverified limitation as a verified defect. An Inferred issue may be High or Critical when the predicted impact is serious, but explain the reasoning and what evidence would confirm it.

## Scoring independence

Severity classifies impact and release risk; it does not automatically subtract
points or cap quality. Use [scoring-contract.json](scoring-contract.json) and
[scorecard-schema.md](scorecard-schema.md) for anchored deductions. Record a
finding ID, underlying defect ID, primary criterion ID and evidence IDs. A
second scoring deduction needs its own distinct impact and evidence. Missing
evidence remains Not Assessed rather than an assumed defect. Full quality is
compatible with a blocked release; no numeric result overrides required gates.
