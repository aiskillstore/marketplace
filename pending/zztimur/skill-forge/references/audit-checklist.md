# Audit Checklist

Use this checklist while reviewing a skill.

## Request and Evidence Boundary

- Requested mode is identified: evaluation, validation, repair, or release gate
- Evaluation and validation are read-only; suggestions, plans, and draft patches do not authorize mutation
- Repair has an explicit mutation verb and a confirmed mutable artifact
- Evaluation or validation does not authorize repackaging, installation, commits, pushes, publication, or external actions
- One intended artifact is selected from an explicit path/attachment or a documented single-candidate assumption
- Multiple candidate packages are not silently merged or selected by filename guess
- Draft-only or pasted-text reviews are labeled as such and do not claim package or release validation
- Target platform/profile is stated: Portable or OpenAI; generic/no-host review maps to Portable rather than Unknown
- Unavailable files, validators, permissions, and runtime checks are recorded as limitations
- Artifact role and source of truth are identified using `../references/artifact-and-mode-matrix.md`
- Portfolio or multi-Skill review records independent findings, scores, and release verdicts for every member

## Package and Structure

- Exactly one intended `SKILL.md`
- Frontmatter meets the selected target's required fields
- `name` follows the selected target's rule only when the target requires it or a name is supplied
- `description` is concise, specific, trigger-oriented, and within a selected target's documented limit when one exists
- `agents/openai.yaml` is inspected only when the selected OpenAI workflow requires UI metadata; do not imply that it is a public OpenAI host requirement
- No template leftovers or unused example files remain
- ZIP size meets the selected target's documented product upload limit, or the report records a Not Applicable rationale
- Directories are meaningful: `scripts/`, `references/`, `assets/`
- Archive preflight has no unsafe paths, duplicate members, symlinks, encrypted files, excessive size, or suspicious compression ratio
- Direct folder preflight has no root or nested symlinks, path escapes, excessive file count, oversized files, or excessive total size
- ZIP packages do not contain unexpected files outside the detected skill root
- ZIP safety scanning covers bounded content under `.git`, `node_modules`, `.venv`, caches, and metadata paths

## Validation Evidence

- Skill Forge helper inspection was run when applicable and its evidence boundary was recorded
- Trusted official validator provenance was verified outside the inspected artifact before execution
- Official validator outcome is classified as Pass, Artifact Fail, Unavailable, Execution Error, or Not Applicable
- Validator outcome, gate result, compatibility result, and Skill Forge quality-policy result are reported as separate fields
- Only an Artifact Fail may support a validator-derived artifact defect; Unavailable and Execution Error are evidence limitations
- Skill Forge findings, independent-evaluator results, official validator results, and package self-test results are reported separately
- Independent Skill Forge evidence, when used, records a previously trusted complete-tree SHA-256, expected candidate SHA-256, exact inspector schema `6`, portable/OpenAI result, and declared sandbox limitations; a stale schema is Not Assessed
- For Skill Forge `v2.0.0` only, schema 5 to 6 bootstrap transition evidence requires both exact opt-in arguments, every `independent_evaluator_policy.bootstrap_transition` requirement, reduced output without raw frontmatter, and an explicit statement that it is not an independent schema-6 pass or reusable after that release
- Target-bundled scripts are never treated as official evidence or executed solely because their name suggests validation
- Package self-tests run only after purpose and provenance review, with copied or synthetic inputs, network default-deny, credentials absent, source read-only, scratch-only writes, bounded process/time/memory, and external side effects forbidden; if any control is unavailable, do not execute and required evidence is Not Assessed
- Inspector finding codes are interpreted using `../references/inspector-output-schema.md` when needed
- Inspector output was checked for `outside_root_findings`, not just the summary status
- Inspector output has `coverage_complete: true` and no unexpected `unscanned_paths` before a strict or release claim
- Custom inspector limits, if used, are recorded from `effective_limits` and justified in the report
- `--strict` mode was used when the user requested validation, release gating, or CI-style pass/fail behavior
- Strict mode fails on incomplete coverage as well as structural errors, unsafe archives/directories, and high-confidence suspected secrets
- After any evaluator or script change, `python3 scripts/run_source_tests.py` passes and `../scripts/run_self_tests.py` passes from the extracted archive built from and source-proved against a committed revision
- For Skill Forge releases, `scripts/package_skill.py verify --source-repo` passes canonical archive integrity, manifest-digest binding, local Git source proof, and Portable/OpenAI profiles

## Triggering

- Description says what the skill does
- Description says when to use it
- Description names relevant input types, tasks, domains, and user intents
- Body does not contain crucial trigger information missing from the description
- Scope is neither too broad nor too narrow

## Instructions

- Workflow is ordered and actionable
- Input requirements are clear
- Output format is clear
- Tool usage is explicit
- Script usage is explicit
- Reference-loading conditions are explicit
- Fallback behavior is explicit
- Error handling is realistic
- Safety boundaries are clear
- Evaluation-only behavior is distinguished from edit/repackage behavior
- Installed runtimes are not treated as mutable source checkouts or git-backed packaging sources

## Resources

- Scripts are deterministic, documented, and safe to run
- References are linked from `SKILL.md`
- Assets are needed for output, not just documentation
- No orphaned files or confusing names
- Dependencies are documented
- Representative scripts are tested under the required sandbox controls, or required evidence is Not Assessed

## Safety and Privacy

- No secrets, tokens, private keys, or `.env` / `.env.*` files, including outside the detected skill root
- Direct folder inputs are not symlinks and do not contain nested symlinks or oversized files that could cause unsafe reads
- Direct-source-tree reviews that skip VCS/cache paths are marked incomplete and are never used as strict or release evidence
- Potentially destructive scripts outside the detected Skill root are treated as strict failures, not warning-only findings
- Secret scanning is treated as heuristic and non-exhaustive
- No hidden network calls without user awareness
- No destructive file operations without safeguards
- No instructions to expose private chain-of-thought
- No unsafe handling of sensitive uploaded data

## Platform Compatibility

- Target platform(s) are stated when relevant: Portable, OpenAI, or both.
- Directory/name and ZIP-root requirements come from the selected `target_contracts` record, not a generic cross-platform assumption.
- `agents/openai.yaml` is present when required for OpenAI workflows, and its absence does not block a generic portable review.
- `dependencies` frontmatter is treated as platform-specific rather than automatically invalid.
- Trusted platform-specific validators are run when available and reported separately; unavailable optional validators are Not Applicable, not artifact defects.

## Reporting Integrity

- Material claims are labeled Verified, Inferred, or Unverified.
- Each Critical or High issue cites evidence, explains its severity, and names a re-test.
- Unavailable evidence is recorded as a limitation, not presented as a verified defect.
- Every rubric category has a whole-number score and brief evidence.
- Category scores sum exactly to 100, and any applicable score cap is stated.
- Quality score, evidence boundary, severity list, and release verdict do not contradict one another.
- Release readiness is claimed only when every applicable release gate passes; Partial, Fail, and Not Assessed are not release-ready.
- Every Not Applicable pressure-test result has a recorded rationale.
- G20 measures both completed category coverage and behavioral success: a Partial test counts as coverage but not success, blocks release through a Partial G20, and does not alone trigger the 79-point missing/failed-evidence cap.
- The complete G01–G23 matrix from `audit-contract.json` is present for a release-gate report; its counts, scorecard, caps, severity list, and release verdict reconcile.
