# Artifact and Mode Matrix

Read this before changing, packaging, or releasing a reviewed Skill. The request
mode controls authority; the artifact role controls what can safely serve as the
source of truth.

## Request Modes

| Mode | Triggers | Allowed outcome | Never authorized without a separate explicit request |
|---|---|---|---|
| Evaluation | Review, audit, assess, score, pressure test, suggest, recommend, outline, plan, find improvements, draft patches, or replacement wording | Read-only findings, score, simulations, and a proposed fix plan | Editing, repackaging, installation, commits, pushes, publication, or external actions |
| Validation | Validate, verify, CI check, or pass/fail | Read-only automated evidence and a validation result | Editing, repackaging, installation, commits, pushes, publication, or external actions |
| Repair | Implement, apply, edit, update, repair, modify, improve, fix, correct, rewrite, refactor, or return an updated artifact | Changes to the confirmed mutable artifact plus revalidation | Changing an unconfirmed artifact, packaging, installation, commits, pushes, publication, or external actions unless separately requested |
| Release gate | Ready to install, publish, ship, or release | Applicable strict checks and a release verdict | Mutating, packaging, installing, committing, pushing, publishing, or external actions unless separately requested |

Route compound requests into ordered phases, with exactly one active mode per
phase. Only an affirmative directive addressed to the agent grants mutation
authority. A mutation verb that is quoted, negated, descriptive, historical,
or hypothetical does not authorize a Repair phase. When wording mixes outcomes
without an affirmative mutation directive, choose Evaluation and provide a
proposed fix plan. “Improve this skill” requests Repair; “audit and improve it”
requests Evaluation followed by Repair. “Suggest improvements” and “how can I
improve it?” are read-only requests. Explicit no-edit constraints take precedence
over improvement wording. These examples describe intent, not a verb allowlist.

## Artifact Roles

| Artifact role | Are edits allowed? | Git-backed packaging possible? | Release verdict possible? | Source of truth | Expected validation path |
|---|---|---|---|---|---|
| Pasted draft | Only with an explicit Repair request to the supplied text | No | No; draft-only result is Not Assessed | Supplied text only | Manual text review; label package, metadata, scripts, and archive evidence unavailable |
| Release ZIP | No; identify a mutable source before changing anything | No | Yes, for that exact complete archive | The exact ZIP | Strict ZIP inspection, target-specific evidence, and release-gate checks; archive-only Skill Forge verification can pass the package command, but G23 also requires local source proof and is Not Assessed when that proof is unavailable |
| Installed runtime | No; locate and confirm its source checkout first | No; installed copies do not establish committed Git history | Runtime audit only; not a new committed-release verdict | Installed files for runtime behavior, confirmed source checkout for repair/release | Inspect the installed copy; for self-repair or packaging, switch to the confirmed source checkout |
| Mutable source checkout | Yes, only for explicit Repair | Yes, after confirmation, a committed revision, and explicit packaging authority | Yes, only after an exact archive has been built from the committed revision and verified | Confirmed source checkout | With explicit packaging authority, build the exact archive from a committed revision, prove it against the caller-selected local Git repository, then run target checks and release gates |
| General repository | No, unless the user explicitly identifies a mutable Skill inside it | No for the repository as a whole | No core Skill verdict; limited adjacent review only | Named repository paths only | Explain the boundary; inspect an identified Skill separately if one exists |
| Portfolio or multi-Skill input | Only per explicitly named member and explicit Repair scope | Per member only after source confirmation | Yes, independently per member | Each selected Skill, not the aggregate | Inspect, score, and issue a release verdict for every member; aggregate only after preserving all member outcomes |

An installed Skill Forge runtime cannot build an archive from a committed revision in its own
directory because it has no `.git`. For self-repair, locate and confirm the
mutable source checkout before editing, packaging, or making release claims.
It may supply independent strict-inspection evidence only when its complete
tree was separately pretrusted and pinned before the run, the exact candidate
is pinned, and the inspector output uses the required schema. That evaluator
role still does not make the installed runtime a packaging source or a complete
release verdict.

## Manual Routing Fixtures

Use this table to test routing language before delivery:

| User request | Expected mode | Expected action |
|---|---|---|
| “Improve this skill.” | Repair | Identify the mutable source, apply scoped improvements, and revalidate. |
| “Audit and improve it.” | Evaluation → Repair | Audit, apply scoped improvements to the confirmed mutable source, and revalidate. |
| “Suggest improvements.” | Evaluation | Return recommendations or replacement wording without editing. |
| “How can I improve it?” | Evaluation | Explain improvements without editing. |
| “Improve this skill, but do not edit files.” | Evaluation | Return findings and proposed changes without editing. |
| “The old request said 'improve this skill'; audit the current version.” | Evaluation | Follow the current audit request; the historical quotation grants no authority. |
| “Improve this skill, then assess release readiness.” | Repair → Release gate | Improve the confirmed source, revalidate, and assess release evidence separately. |
| “Apply these fixes.” | Repair | Confirm the mutable artifact, apply the named fixes, and revalidate. |
| “Fix the parser.” | Repair | Confirm the mutable artifact, apply the scoped fix, and revalidate. |
| “Correct this frontmatter.” | Repair | Confirm the mutable artifact, correct it, and revalidate. |
| “Rewrite this workflow.” | Repair | Confirm the mutable artifact, rewrite the requested scope, and revalidate. |
| “Refactor this script.” | Repair | Confirm the mutable artifact, refactor the requested scope, and revalidate. |
| “Validate but do not edit.” | Validation | Run the relevant checks and report results without changing files. |
| “Audit this and explain how to fix it. Do not edit.” | Evaluation | Return findings and a proposed repair without editing. |
| “The old request said ‘fix the parser’; audit the current version.” | Evaluation | Treat the quoted historical verb as evidence, not authority. |
| “Fix these findings, then assess release readiness.” | Repair → Release gate | Apply the confirmed fixes, revalidate, then issue a separate gate verdict from fresh evidence. |
| “Repair the installed runtime.” | Repair, blocked pending source confirmation | Locate and confirm the mutable source checkout; do not edit or package the installed runtime. |
| “Review these two Skills.” | Evaluation, per-Skill | Produce separate findings, scores, and release verdicts; aggregate only as a comparison. |

When multiple named platforms are requested, run an independent profile phase
for each one. Do not replace named profiles with `portable`; portable is a
shared baseline, not host certification. A cross-profile summary must preserve
each member result and may never soften a Fail or Not Assessed result.

## Pressure-Test Result States

Use **Pass**, **Fail**, **Partial**, **Not Assessed**, or **Not Applicable** for pressure tests.
Use Not Applicable only when a category truly does not apply to the selected
artifact or scope, and always record the rationale. It cannot hide an available
or required test. Use Not Assessed when the evidence needed to run the test was
unavailable; it is not a release pass.
