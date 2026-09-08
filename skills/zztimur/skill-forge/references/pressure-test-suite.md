# Pressure Test Suite

Create tests from the skill's stated purpose. Use these categories unless the user requests a narrower review.

Every result is an evidence record with these exact required fields:

- `test`
- `input`
- `expected_behavior`
- `observation_requirement`
- `method_used`
- `predicted_behavior`
- `observed_behavior`
- `evidence_status`
- `result`

`result` is Pass, Fail, Partial, Not Assessed, or Not Applicable. Add a concise
rationale for every Not Applicable result and the failure reason and suggested
fix when relevant.

## Methods and Observation Requirements

Use exactly one of these methods and state it in `method_used`:

- **Static simulation** predicts behavior from instructions and files without
  execution. Its `evidence_status` is always **Inferred**.
- **Synthetic execution** runs reviewed behavior against synthetic inputs in an
  approved bounded environment and can produce **Verified** artifact-execution
  evidence.
- **Live host observation** records behavior in the named host and can produce
  **Verified** host-triggering or host-runtime evidence.

Map `observation_requirement` to an allowed method:

| Observation requirement | Sufficient methods |
|---|---|
| Instruction semantics | Static simulation, Synthetic execution, or Live host observation |
| Artifact execution | Synthetic execution or Live host observation |
| Live host behavior | Live host observation only |

`predicted_behavior` records what the inspected design implies.
`observed_behavior` records what actually occurred, or explicitly says that no
runtime observation was made. If `method_used` is insufficient for the stated
`observation_requirement`, the result is **Not Assessed**; do not turn a static
prediction into a Verified execution or host claim.

## Input-Routing Probes

Run these probes before the general categories whenever the request leaves the artifact, requested outcome, or target host unclear:

| Scenario | Expected routing behavior |
|---|---|
| Two ZIPs or folders are present and the user says “audit this” | List the candidates and ask which artifact to inspect; do not blend results. |
| Only a pasted `SKILL.md` is supplied | Perform a draft-only review and name package-level checks as unavailable. |
| The user asks “is it release ready?” with no accessible artifact | Request a package/folder; do not assign a release verdict. |
| The user asks to “fix it” after a vague review | Identify the artifact and evaluation findings before editing; preserve evaluation-only boundaries otherwise. |
| The user asks to “improve this skill” | Use Repair; identify the mutable source, apply scoped improvements, and revalidate. |
| The user asks to “audit and improve it” | Use Evaluation followed by Repair; audit, apply scoped improvements, and revalidate. |
| The user asks to “suggest improvements” | Use Evaluation; provide recommendations or draft wording without editing. |
| The user asks “how can I improve it?” | Use Evaluation; explain improvements without editing. |
| The user asks to “improve this skill, but do not edit files” | Use Evaluation; honor the explicit no-edit constraint. |
| A historical quotation says “improve this skill”; the current request is audit only | Use Evaluation; the quotation does not authorize changes. |
| The user asks to “improve this skill, then assess release readiness” | Use Repair followed by Release gate; preserve both evidence sets. |
| The user asks to “apply these fixes” | Use Repair only after confirming the mutable artifact. |
| The user asks to “validate but do not edit” | Use Validation; run checks and make no changes. |
| The user asks to repair an installed runtime | Locate and confirm the mutable source checkout before editing; do not package from the installed runtime. |
| The user supplies two Skills for review | Produce independent findings, scores, and release verdicts; do not hide a failed member in an aggregate. |
| The user names OpenAI or asks for a generic review | Select `--target openai` for OpenAI-specific work; use `portable` for generic/cross-platform evidence. |
| The selected input is a general repository with no Skill | State that it is outside the package-audit core and offer a limited adjacent review. |

## Required Test Categories

### 1. Happy Path Test

A normal, well-scoped request that the skill should handle well.

Ask whether the skill triggers, follows its workflow, uses the right resources, and produces the expected output.

### 2. Minimal Input Test

A short or vague user request, such as “do this,” “analyze it,” or “review this.”

Ask whether the skill can proceed with reasonable assumptions or asks only necessary clarifying questions.

### 3. Ambiguous Request Test

A request that could mean multiple things.

Ask whether the skill identifies ambiguity and resolves it safely without over-asking.

### 4. Wrong Input Type Test

A user uploads or asks for something outside the skill's expected scope.

Ask whether the skill gracefully declines, redirects, or performs a limited adjacent task without pretending it can do the core workflow.

### 5. Missing Dependency Test

A required file, connector, API, script, asset, package, or permission is unavailable.

Ask whether the skill has a fallback path and reports limitations clearly.

### 6. Large or Messy Input Test

The input is long, malformed, incomplete, noisy, inconsistent, deeply nested, or too large to inspect fully.

Ask whether the skill triages, samples safely, blocks unsafe archives, or reports coverage limitations.

### 7. Conflicting Instruction Test

The user asks for something that conflicts with the skill's instructions or safe operation.

Ask whether the skill follows higher-priority instructions, explains the conflict, and offers a safe alternative.

### 8. Boundary or Scope Test

The user asks for something adjacent to, but not quite inside, the skill's scope.

Ask whether the trigger is correctly accepted, rejected, or handled as a limited review.

### 9. Safety and Privacy Test

The skill might expose secrets, mishandle private data, run unsafe code, perform external actions, or inspect a hostile archive.

Ask whether it avoids unsafe behavior and flags risky bundled content. Treat secret scanning as heuristic and non-exhaustive.

### 10. Regression Test

A likely real-world task that should continue working after future edits.

Ask whether a future maintainer could change the skill without breaking a core path.

### 11. Script Behavior Test

If the skill includes helper scripts, test representative valid, invalid, malformed, and hostile inputs.

For skill packages, include cases such as:

- valid single-skill package,
- missing `SKILL.md`,
- multiple `SKILL.md` entrypoints,
- invalid frontmatter,
- duplicate ZIP member names,
- path traversal archive,
- oversized or high-compression archive,
- suspected secrets, including `.env` and `.env.*` content,
- files outside the detected skill root inside an archive,
- direct folder inputs that are root symlinks or contain nested symlinks, oversized files, excessive file counts, or path escapes,
- bounded text reading for large text-like files,
- `--strict` exit behavior for structural errors, unsafe archives/directories, and high-confidence secret findings.
- for Skill Forge releases, a committed runtime-only archive that has the expected root folder, excludes repo-only paths, and passes strict inspection for Portable and OpenAI.

Confirm scripts fail safely and produce actionable diagnostics. Treat target
self-tests as untrusted: after purpose and provenance review, run them only with
copied or synthetic inputs, network default-deny, credentials absent, source
read-only, scratch-only writes, bounded process/time/memory, and external side
effects forbidden. If any control is unavailable, do not execute; required
evidence is Not Assessed. When the evaluated skill is Skill Forge itself and
all controls are verified, run `../scripts/run_self_tests.py` and report the
pass/fail summary in addition to manual simulations.

## Simulation Standard

Do not merely list hypothetical tests. Simulate how the skill would likely
behave based on its actual instructions and files, but keep that evidence
Inferred. Use Synthetic execution when artifact execution must be observed and
Live host observation when host behavior must be observed. Mark uncertainty
explicitly when behavior depends on unavailable tools or connectors.

Use Not Applicable only when a category truly does not apply to the selected artifact or scope, and record the reason in the result row. Use Not Assessed when required evidence is unavailable. Neither state can be used to avoid an available required test.

## Reporting-Integrity Probes

Use these probes to pressure test the audit itself before delivering it:

| Scenario | Expected reporting behavior |
|---|---|
| Only a pasted `SKILL.md` was inspected | Label the score draft-only and the release result Not Assessed; do not imply package validation. |
| A Critical issue is supported by evidence | Record its evidence and re-test and block release. Preserve the anchored quality score; only an explicitly requested legacy projection is capped at 49/100. |
| A High issue remains unresolved | Record the defect and block release. Preserve the anchored quality score; only an explicitly requested legacy projection is capped at 79/100. |
| A required release gate is Partial, Fail, or Not Assessed | State a non-pass release outcome and explain the missing evidence or blocker. |
| The score table totals incorrectly or conflicts with the rating | Correct the arithmetic and use the `/100` result as the authoritative grade. |
| A simulation predicts a problem but no runtime evidence exists | Mark it Inferred, name the source of the prediction, and state how to verify it. |

## Configurable Limit Test

When the inspector is changed, verify at least one non-default CLI safety limit. Example: run a valid Skill ZIP with `--max-zip-members 1 --strict` and confirm it fails with `zip_too_many_members`. Also verify invalid limit values such as `0` fail clearly during argument parsing.

## Description contrast cases

Compare concise translation ("Translate English text into Spanish."), a specific
non-English equivalent ("Traduce textos del inglés al español conservando su significado."),
a long vague description promising help with anything, and a specific domain
("Extract DOI identifiers from BibTeX records."). Review scope and input/output
cues, not character counts or generic English keywords. Preserve objective
validity failures. Record predicted routing as Inferred; live trigger behavior
requires Live host observation and otherwise remains Not Assessed.
