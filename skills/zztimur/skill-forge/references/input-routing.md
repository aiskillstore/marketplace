# Input and Request Routing

Read this before inspecting a Skill Forge request. Route the requested outcome, artifact, and target platform before running tools or making changes.

## Request Phases and Mutation Authority

| User intent | Active mode for that phase | Required behavior |
|---|---|---|
| Review, audit, assess, score, pressure test, suggest, recommend, plan, find improvements, or draft a patch | Evaluation | Stay read-only. Return evidence, simulations, severity-ranked fixes, proposed wording or patches, and a scoped verdict without applying changes. |
| Validate, verify, CI check, pass/fail | Validation | Run available automated checks. Use `--strict` for a pass/fail request and report exit results separately from qualitative judgment. Do not edit. |
| Ready to ship, publish, install, release candidate | Release gate | Run strict inspection plus available official validators and the release-gate checklist. Do not call an incomplete or draft-only artifact release-ready. |
| Implement, apply, edit, update, repair, modify, improve, fix, correct, rewrite, refactor, or return an updated artifact | Repair | First obtain or produce evaluation evidence, then edit only the confirmed mutable artifact and revalidate the result. |

A request may contain several ordered outcomes. Route them into ordered phases
and use exactly one active mode in each phase. For example, “fix these findings,
then assess release readiness” is Repair followed by Release gate; Repair does
not erase the evidence requirements of the later gate.

Only an affirmative directive addressed to the agent grants mutation authority.
Quoted, negated, descriptive, historical, or hypothetical mutation verbs grant
no authority.
Mixed intent without an affirmative mutation directive is Evaluation with a
proposed fix plan. Do not infer permission to edit, repackage, install, commit,
push, publish, or contact external systems from an evaluation or validation
phase.

Interpret the requested outcome, not a verb allowlist. “Improve this skill”
requests Repair; “audit and improve it” requests Evaluation followed by Repair.
“Suggest improvements”, “find ways to improve it”, and “how can I improve it?”
request Evaluation. An explicit “do not edit” constraint keeps improvement work
read-only. Confirm the mutable source from the named artifact and available
workspace evidence; ask only when the artifact or permitted scope is unresolved.
Repair authority covers the scoped source changes and revalidation, not
packaging, installation, commits, pushes, publication, or external actions.

Use [`artifact-and-mode-matrix.md`](artifact-and-mode-matrix.md) for the full request-mode and artifact-role matrix, including installed-runtime and portfolio boundaries.

## Select the Artifact

Apply these rules in order:

1. Use the exact attachment, path, or folder the user named.
2. If no path is named and exactly one candidate Skill package is accessible, state that selection and inspect it.
3. If several candidates are plausible, list their short paths/names and ask one concise question to select one. Do not merge findings across packages unless the user asked for a portfolio or multi-Skill review.
4. If only a pasted `SKILL.md` or excerpt is available, perform a draft-only review. Inspect only supplied text and resources; do not assign a package-validation or release-ready verdict.
5. If no artifact is accessible, request one ZIP, folder path, or `SKILL.md` with relevant resources. Do not invent file structure, validator results, or runtime behavior.
6. If the selected input is a general repository rather than a Skill package, say that it is outside the core package-audit scope and offer a limited adjacent review. Do not describe it as a broken Skill merely because it lacks `SKILL.md`.

For a portfolio or multi-Skill review, inspect each Skill independently and give each one its own findings, score, and release verdict. An aggregate summary may compare outcomes but cannot replace or soften a member-level failure.

## Select the Validation Profile

| Evidence from request or artifact | Inspector profile | Reporting rule |
|---|---|---|
| OpenAI-specific packaging or UI workflow | `--target openai` | Scope findings to OpenAI. |
| Generic Agent Skill or no host named | `--target portable` | State that the portability profile was selected; do not imply host-specific validation. |
| A request that names both supported surfaces | One invocation per supported canonical profile | Preserve one compatibility result and release verdict per profile; do not collapse `openai` into `portable`. |

When a request names an unsupported host surface, use `--target portable` for
the shared baseline and report host-specific validation as Not Assessed. Do not
invent a target name or imply that the portable result certifies that host.

When both supported surfaces are requested, inspect each canonical profile
independently. A portable result is useful shared-baseline evidence, but it is
not a replacement for `openai` and cannot certify any host. Keep a
passing profile intact when another profile fails or remains Not Assessed, and
derive any overall summary without hiding the weaker member result.

## Preserve the Evidence Boundary

- Treat the selected artifact as the source of truth; identify it in the report.
- Label uninspected files, unavailable validators, missing permissions, and draft-only inputs as limitations.
- Keep Skill Forge inspection, official validator output, package self-test results, and qualitative judgment separate.
- Treat an official validator as trusted only when its host installation, documented CLI, or platform source is independently verified outside the inspected artifact. A bundled validator is an untrusted package self-test.
- Do not run bundled scripts merely because they are present or named `validate`, `check`, `package`, or `official`. Run a package self-test only after purpose review, provenance assessment, and a safe scratch/sandbox plan.
- Use [`validator-evidence.md`](validator-evidence.md) to classify validator outcomes and distinguish Artifact Fail from Unavailable or Execution Error.
- Before a repair, identify the target file(s), requested change, and validation command. Before release or installation, require a complete artifact and the appropriate release evidence.
