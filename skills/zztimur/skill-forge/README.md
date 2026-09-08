# Skill Forge — Agent Skill Validator & Release Gate

[![Self Tests](https://github.com/zztimur/skill-forge/actions/workflows/self-tests.yml/badge.svg?branch=main)](https://github.com/zztimur/skill-forge/actions/workflows/self-tests.yml)
[![skills.sh](https://skills.sh/b/zztimur/skill-forge)](https://skills.sh/zztimur/skill-forge)
[![Latest release](https://img.shields.io/github/v/release/zztimur/skill-forge?sort=semver)](https://github.com/zztimur/skill-forge/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Skill Forge validates, pressure-tests, and release-gates `SKILL.md` packages for OpenAI and portable agent runtimes.

It combines a dependency-free static inspector with an agent-led audit workflow. Deterministic inspection, official-validator outcomes when available, package self-tests, and qualitative judgment remain separate evidence sources, so an unavailable check cannot quietly turn into a pass.

## Why Skill Forge

- **Catch package blockers early.** Inspect frontmatter, layout, archive paths, symlinks, missing resources, likely secrets, and risky bundled commands before release.
- **Test the instructions, not just the files.** Pressure-test triggering, ambiguous requests, wrong inputs, privacy boundaries, fallbacks, and regression behavior.
- **Make an evidence-backed ship decision.** Reconcile findings, validator results, self-tests, required gates, score caps, and unresolved risks into an honest release verdict.

## Install as an Agent Skill

The fastest path uses the open-source [skills CLI](https://skills.sh/docs/cli) and requires Node.js 18 or newer:

```bash
npx skills add zztimur/skill-forge
```

The CLI detects supported agents and lets you choose project or user scope. For a non-interactive, project-scoped Codex install:

```bash
npx --yes skills add zztimur/skill-forge --skill skill-forge --agent codex --copy -y
```

Run the non-interactive command from the project where you want Skill Forge available. It installs the repository's default-branch source at `<current directory>/.agents/skills/skill-forge`. The skills CLI says its anonymous telemetry includes the skill name, skill files, and a timestamp—not personal or device information; set `DISABLE_TELEMETRY=1` to opt out. skills.sh also displays independent automated audits, which may flag the synthetic hostile-input fixtures and intentional handling of untrusted skill text; review the [scanner fixture context](#third-party-scanner-context) or use the checksum-verified release path below. Then try:

```text
Use $skill-forge to release-gate /path/to/my-skill.zip for OpenAI.
```

### Checksum-verified release install

Use a reviewed, exact release tag and its runtime-only archive when you want a reproducible installation. The installer requires Python 3.9 or newer and a separate trusted source checkout: it is a source-maintenance helper, excluded from the installed runtime ZIP. Obtain the source at a reviewed full commit ID that contains `scripts/install_skill.py`; older releases may not include this helper:

```bash
INSTALLER_COMMIT=REPLACE_WITH_REVIEWED_FULL_COMMIT_ID
git clone --no-checkout https://github.com/zztimur/skill-forge.git skill-forge-installer-source
cd skill-forge-installer-source
git checkout --detach "$INSTALLER_COMMIT"
git rev-parse HEAD
```

Confirm the displayed commit matches the independently reviewed ID before running its helper. Choose the archive tag explicitly; do not combine assets fetched through a moving `latest` URL. Download both assets from the same tag using the GitHub CLI:

```bash
RELEASE_TAG=vX.Y.Z # Replace with the exact release tag you reviewed.
DOWNLOAD_DIR="$HOME/Downloads/skill-forge-$RELEASE_TAG"
gh release download "$RELEASE_TAG" --repo zztimur/skill-forge \
  --pattern skill-forge.zip --pattern skill-forge.zip.sha256 --dir "$DOWNLOAD_DIR"
```

Review that release's checksum file and copy its 64-character SHA-256 into `EXPECTED_SHA256` below. From this reviewed source checkout, run:

```bash
EXPECTED_SHA256=REPLACE_WITH_REVIEWED_64_CHARACTER_SHA256
mkdir -p "$HOME/.agents/skills"
python3 -S scripts/install_skill.py "$DOWNLOAD_DIR/skill-forge.zip" \
  --sha256 "$EXPECTED_SHA256" --skills-dir "$HOME/.agents/skills"
```

The helper makes no downloads. It checks the supplied digest, archive preflight, canonical manifest, package shape, and strict inspections before installation. These checks prove archive integrity; source provenance remains a separate check with `scripts/package_skill.py verify ARCHIVE --source-repo CHECKOUT --json`.

Installation stages outside the active skills directory, then replaces the entire `skill-forge` tree so stale files disappear. Any old tree, including local edits, remains at the backup path printed in the JSON result. Repeating an install with identical files and modes returns `unchanged`. Symlinks, hardlinks in an existing installation, special files, and unsupported filesystem layouts fail closed. Use real paths without symlink ancestors, and keep the skills directory and its parent on the same filesystem. Do not edit or run another installation during the swap. Handled errors and keyboard interruptions roll back; power loss or forced process termination can require manual recovery from the printed or retained `.skill-forge-install-*` directory. The two directory renames have a brief interval where the active path is absent.

If the existing installation contains `.env` or `.env.*` paths, the helper refuses the installation before opening those files and leaves the old tree unchanged.

For a project installation, create its `.agents/skills` directory first and pass that real path as `--skills-dir`. On Windows, download both assets from the same exact release tag and invoke the same Python helper with native paths and the reviewed digest. Codex normally detects newly installed skills automatically; restart it if Skill Forge does not appear.

## Run the standalone inspector

The standalone inspector requires Python 3.9 or newer and no third-party Python packages.

```bash
git clone --depth 1 https://github.com/zztimur/skill-forge.git
cd skill-forge
python3 -S scripts/inspect_skill_package.py /path/to/skill-or-skill.zip --target portable --strict
```

A successful inspection ends with output like this:

```text
Status: pass / Findings: 0 errors, 0 warnings.
```

In strict mode, exit code `0` means pass, `1` means the input could not be inspected, and `2` means strict validation found an error or could not establish complete required safety or manifest evidence. Use `--target openai` when OpenAI is the intended host, or add `--json` for CI and automation.

## Example release-gate result

The bundled [example evaluation](references/example-report.md) shows how a structurally valid package can still fail its release gate:

```text
Release gate verdict: Fail
Blocking gates:
- G05: Trigger description is too thin
- G14: A bundled script is orphaned
- G20: Wrong-input and privacy pressure tests fail
```

The linked example contains the complete scoped score and assessment evidence. Its score and verdict come from the full audit workflow, not from the standalone inspector alone.

## How it differs from basic package linting

| Question | Basic package linting | Skill Forge |
|---|---|---|
| Is the frontmatter and folder shape valid? | Core focus | Deterministic inspection |
| Do archive paths pass bounded safety checks, and do referenced resources exist? | Varies | Path, symlink, size, reference, and coverage checks |
| Will the skill trigger and behave well on difficult requests? | Usually out of scope | Qualitative pressure-test workflow |
| Did an official validator, package self-test, or reviewer produce the evidence? | Often combined or omitted | Reported separately |
| Is the exact artifact ready to ship? | Not usually answered | Separate quality, coverage and release verdicts with evidence links |

`portable` is a conservative shared baseline, not universal host certification. Secret and dangerous-command scanning is heuristic and non-exhaustive, and audits remain read-only unless repair is explicitly requested.

## What Skill Forge checks

Skill Forge evaluates two distinct failure classes:

1. **Package integrity** — structure, metadata, archive safety, resources, scripts, and compatibility risks that deterministic inspection can evaluate.
2. **Agent behavior quality** — triggering, instruction clarity, scope control, fallback behavior, safety posture, and pressure-test results that require judgment.

It accepts Skill ZIPs, folders, or `SKILL.md` drafts and can operate in evaluation, validation, repair, release-gate, draft-only, or limited adjacent-review modes. A complete release review reports Skill Forge inspection, trusted official-validator evidence when available, approved package self-tests, and qualitative evidence separately.

## Request and artifact boundaries

Reviews, audits, validation, suggestions, improvement plans, and draft patches
are read-only. Repair requires an explicit mutation request such as “apply,”
“edit,” “implement,” “fix,” “correct,” “rewrite,” or “refactor,” and a confirmed mutable source artifact. Evaluation and
validation do not authorize packaging, installation, commits, pushes,
publication, or external actions.

Use [`references/artifact-and-mode-matrix.md`](references/artifact-and-mode-matrix.md)
for the full routing and artifact-role matrix. In particular, an installed Skill
Forge runtime is not a Git source checkout: locate and confirm the source before
self-repair or building an archive from a committed revision. Portfolio reviews keep findings,
scores, and release verdicts separate for every Skill.

## Inspector reference

The inspector is dependency-free and uses only the Python standard library. It requires Python 3.9 or newer.

```bash
python3 -S scripts/inspect_skill_package.py /path/to/skill-or-skill.zip --json
```

For CI-style checks, use strict mode. It blocks error findings and incomplete required safety or manifest evidence.

```bash
python3 -S scripts/inspect_skill_package.py /path/to/skill-or-skill.zip --json --strict
```

Human-readable markdown output is available by omitting `--json`:

```bash
python3 -S scripts/inspect_skill_package.py /path/to/skill-or-skill.zip
```

The markdown output ends with a status and finding-count footer. JSON output includes a versioned `schema_version`, a redacted structural `frontmatter` summary, a stable `detected_root_relative` path for ZIP automation, explicit `requested_target` / `canonical_target` / alias fields, and a top-level `summary` object for release-gate and CI integrations. Schema 6 no longer emits raw frontmatter values.

## Compatibility notes

Use the inspector process exit code as the canonical machine signal for CI and release gates.

Choose a canonical host profile deliberately:

```bash
python3 -S scripts/inspect_skill_package.py /path/to/skill --target portable --json --strict
python3 -S scripts/inspect_skill_package.py /path/to/skill --target openai --json --strict
```

`portable` is a conservative shared baseline, not proof that every host-specific workflow will accept the package. The inspector's default 30 MB pre-open ZIP threshold is an explicitly configurable internal safety boundary, not a vendor upload-limit assertion. See [platform compatibility profiles](references/platform-compatibility.md) for documented limits and source links.

In strict mode:

- Exit code `0` means the inspected package passed strict checks.
- Exit code `1` means the input does not exist or could not be inspected in a basic way (for example, a missing path or an unreadable archive).
- Exit code `2` means strict validation found an error-severity finding, could not establish complete safety-scan coverage, or could not fully verify an applicable critical YAML manifest.

The top-level JSON `summary` object is retained for compatibility with existing automation that reads fields such as:

- `summary.status`
- `summary.strict_pass`
- `summary.error_count`
- `summary.finding_codes`

New integrations should still treat the process exit code as the source of truth for pass/fail decisions. Use `summary` for reporting, dashboards, or compatibility with older pipelines.

## Running self-tests

After any evaluator or script change, run both test layers. Start with the
contract and source-only suite:

```bash
python3 -S scripts/validate_audit_contract.py
python3 -S scripts/run_source_tests.py
```

Then build from a committed revision, source-prove the exact archive against
that revision, extract it, and run the tests that actually shipped:

```bash
python3 -S scripts/package_skill.py build --revision HEAD --output /tmp/skill-forge.zip
python3 -S scripts/package_skill.py verify /tmp/skill-forge.zip --json --source-repo .
python3 -S -m zipfile -e /tmp/skill-forge.zip /tmp/skill-forge-runtime
python3 -S /tmp/skill-forge-runtime/skill-forge/scripts/run_self_tests.py
```

Together, the suites use temporary valid, malformed, hostile, and release fixtures. They
need no network access or third-party packages. Source-only checks never ship in
the runtime, and the runtime runner has no source-helper import or skip path.

## Continuous integration

This repository includes a GitHub Actions workflow at `.github/workflows/self-tests.yml`.

Every Ubuntu, macOS, and Windows job runs on Python `3.9` and the latest stable
release. Each of the six matrix cells validates the contract, runs source-only
tests, builds the exact submitted commit, verifies archive integrity and local
Git source proof across both canonical profiles, extracts the archive, and
runs its packaged runtime suite. Pull requests check out the contributor's HEAD
instead of GitHub's temporary merge ref. Keep the workflow dependency-free;
every third-party GitHub Action is pinned to an immutable commit SHA.

## Versioning and changelog

Release candidates use ASCII-only semantic-version tags:
`vMAJOR.MINOR.PATCH`.
`CHANGELOG.md` is the committed release record: add user-visible changes under
**Unreleased** as normal work lands, then use the local release command to
promote that section into the next version.

The command never pushes or publishes by itself. It requires clean `main` and
the highest reachable SemVer tag, runs the source and extracted-runtime gates,
then creates a one-file release commit with exact subject
`chore(release): <tag>` and an annotated local tag. It requires one visible,
exact changelog heading with a real calendar date matching the tagger date.
`HEAD`, reachable tags, and changelog bytes are rechecked after the gates;
replacement refs, unsafe inherited Git repository/config variables, hooks, and
automatic signing are disabled for the generated local commit and tag.

```bash
python3 -S scripts/release_skill.py patch --dry-run
TAG=<exact tag printed by the dry run>
python3 -S scripts/release_skill.py patch
python3 -S scripts/release_skill.py --verify-tag "$TAG"
git push --atomic origin main "$TAG"
```

Use `minor` or `major` instead of `patch` when the change warrants it. A version
does not change merely because source files change; it changes only when this
release command is intentionally run. The tag push builds a validated candidate;
it does not publish a GitHub Release. Complete the independent review, capture
the externally pinned receipt, and dispatch publication for the exact tag as
described in the [release receipt procedure](references/release-receipt.md).
These controls establish local metadata integrity, not cryptographic
author identity, release authorization, or remote-origin authenticity.

## Release-gate workflow

For install, publish, ship, or release-candidate decisions, use `references/audit-contract.json`, `references/release-gate-checklist.md`, and `references/release-report-template.md`. The complete G01–G23 gate matrix is the proof; the five-row executive summary cannot replace it.

A skill is release-ready only when every applicable required gate passes; a Critical gate failure is always disqualifying.

Treat the following as blockers unless the user explicitly requested only a draft review:

- Strict inspector failures.
- Likely bundled secrets.
- Unsafe archive structures.
- Missing or multiple `SKILL.md` entrypoints.
- Trusted official-validator Artifact Fail outcomes.
- Safety risks that could cause the agent to take unsafe, misleading, destructive, or unsupported actions.

Release readiness should mean something. Otherwise it is just ceremony wearing a badge.

An official validator must come from a trusted host installation, documented CLI,
or independently verified platform source outside the inspected package. A
target-bundled `validate`, `check`, `package`, or `official` script is an
untrusted self-test, never official evidence, and is not executed merely because
of its name. An unavailable optional validator is Not Applicable; dependency,
sandbox, and timeout failures are execution limitations rather than evidence
that the package is invalid. See [`references/validator-evidence.md`](references/validator-evidence.md).

## Independent evaluation

`scripts/verify_independent_evaluator.py` can run an exact candidate through a
separately installed, previously trusted Skill Forge runtime. It requires a
pretrusted SHA-256 for the evaluator's complete tree and an expected candidate
SHA-256; an optional inspector-file pin is supplemental. It executes scratch
copies under isolated Python with a credential-reduced environment and bounded
tree, file, time, and output limits, then checks both canonical profiles.

```bash
python3 -S scripts/verify_independent_evaluator.py \
  --evaluator-root /trusted/skill-forge \
  --archive /tmp/skill-forge.zip \
  --expected-evaluator-tree-sha256 "$TRUSTED_EVALUATOR_TREE_SHA256" \
  --expected-candidate-sha256 "$CANDIDATE_SHA256" \
  --json
```

The required evaluator pin must come from prior trusted evidence, not from the
candidate checkout during the same run. Inspector schema `6` is required;
stale schemas, missing provenance, timeouts, and output-limit failures are
**Not Assessed**, never Pass. Exit codes are `0` Pass, `2` Fail, and `3` Not
Assessed. The helper does not provide an OS filesystem sandbox or network
sandbox and makes no continuous-immutability claim. A Pass is independent
strict-inspection evidence, not a complete release verdict.

The sole exception is the one-time schema 5 to 6 bootstrap for `v2.0.0`. It
requires a pretrusted schema-5 evaluator plus both
`--bootstrap-schema-transition 5:6` and `--bootstrap-release-tag v2.0.0`.
The reduced report excludes raw schema-5 frontmatter and labels a successful
run **bootstrap transition evidence**, not an independent schema-6 pass. It can
support G09 only with every contract requirement and cannot be reused after
`v2.0.0`.

## Safety notes

Treat uploaded archives and bundled scripts as untrusted input.

The secret scan is heuristic and non-exhaustive. A clean scan does not prove that no secrets exist.

The inspector flags high-confidence destructive behavior in bundled shell,
PowerShell, Windows batch, Python, and JavaScript/TypeScript scripts as
`script_dangerous_command`. Examples include remote content piped or evaluated
into a shell and recursive deletion of root, home, or system paths. The scan is
heuristic and non-exhaustive; a clean result is not proof of safety.

Do not run bundled scripts that appear destructive, credential-harvesting, network-dependent, or unrelated to validation.

Before running any target-bundled self-test, review its purpose and provenance
and use copied or synthetic inputs with network default-deny, credentials
absent, source read-only, scratch-only writes, bounded process/time/memory, and
external side effects forbidden. If any control is unavailable, do not run the
self-test; required evidence is Not Assessed.

### Third-party scanner context

`scripts/run_self_tests.py` intentionally contains synthetic malicious-command,
remote-URL, and fake-credential strings. The harness writes them into temporary
fixture packages and asks the inspector to reject them; it never executes those
fixture payloads. Automated scanners that do not distinguish test data from
runtime behavior may therefore report them as suspicious. The qualitative
workflow also reads untrusted package prose in order to evaluate it, but
artifact content remains evidence rather than authority and its directives are
never followed. See [validator evidence boundaries](references/validator-evidence.md).

## Contributing and security

Contributions are welcome. Use [CONTRIBUTING.md](CONTRIBUTING.md) for setup,
safe reproduction guidance, required checks, and pull-request expectations.
Report ordinary bugs and false positives through the structured issue forms.

Do not disclose vulnerability details in a public issue. Follow
[SECURITY.md](SECURITY.md) for the supported-version policy, security scope,
private-reporting route, and third-party scanner context.

Keep `SKILL.md` compact. Move detailed rubrics, examples, schemas, and extended guidance into directly linked files under `references/`.

The skill should help the agent load the right amount of context at the right time — not bury it under a pile of instructions and then act surprised when behavior drifts.

## Packaging

A distributable Skill ZIP should contain the `skill-forge/` directory as the archive root entry.

Build from a committed revision, not the mutable working tree. The verified
runtime archive is the installation source of truth: installed-runtime parity
means the installed files match that exact verified archive, not the broader
repository checkout. The package command admits only the runtime skill surface:
`SKILL.md`, `README.md`, `LICENSE`, `agents/`, `references/`, plus the inspector,
package verifier, portable-path policy, runtime-manifest helper, and runtime
regression suite. It intentionally excludes `.github/`, Git metadata, generated
output, caches, and source-only helpers including `generate_release_notes.py`,
`release_metadata.py`, `release_skill.py`, `run_source_tests.py`, and
`verify_independent_evaluator.py`.

```bash
python3 -S scripts/package_skill.py build --revision HEAD --output /tmp/skill-forge.zip
python3 -S scripts/package_skill.py verify /tmp/skill-forge.zip --json --source-repo .
```

Every archive contains a generated `runtime-manifest.json` that records the exact
committed source identity, selector policy, file modes, sizes, and SHA-256
digests. The ZIP uses a canonical deterministic byte layout. Verification
separately reports archive integrity, local Git source proof, and their shared
manifest-digest binding, then runs strict inspection for Portable and OpenAI.
`--source-repo` proves consistency with
the caller-selected local Git object graph; it does not prove remote origin,
signatures, author identity, or release authorization. See the
[runtime manifest schema](references/runtime-manifest-schema.md).

The `.github/workflows/release-skill.yml` workflow has a read-only validation
job and a separate publication job. Validation builds the committed `HEAD`
runtime archive, runs source-only tests, proves the archive against the checkout,
extracts it, runs the packaged runtime suite, verifies both canonical
profiles, and writes `skill-forge.zip.sha256` beside the ZIP. On a tag, it also
verifies the exact release metadata and generates deterministic notes from the
tagged commit's changelog blob rather than mutable working-tree text. Only the
dependent publication job receives `contents: write`. Tag pushes stop after
validation and upload the candidate assets. Publication requires a manual
`workflow_dispatch` with the exact `release_tag`, successful capture
`receipt_run_id`, and reviewer-trusted `receipt_sha256`. Both validation and
publication verify the receipt, independent evaluator report, and all seven
successful Self Tests jobs on the exact commit. The publication job rechecks
live CI and the remote tag immediately before attaching the ZIP and checksum
to a GitHub Release. Follow the [release receipt procedure](references/release-receipt.md)
to upload reviewed evidence without changing the release commit.

## Repository layout

The product overview and quick start stay above; implementation and contributor details live here.

```text
skill-forge/
├── SKILL.md                  # Agent workflow and routing instructions
├── scripts/                  # Inspector, tests, packaging, and release tools
├── references/               # Audit contract, rubrics, schemas, and templates
├── agents/openai.yaml        # OpenAI-facing skill metadata
├── .github/                  # Cross-platform workflows and structured issue forms
├── CONTRIBUTING.md           # Development and contribution guidance
├── SECURITY.md               # Supported versions, reporting, and threat model
├── README.md                 # Usage and technical reference
├── CHANGELOG.md              # Unreleased and published changes
└── LICENSE                   # MIT license
```

## License

This repository is distributed under the MIT License.

Update the copyright holder in `LICENSE` if your organization requires a different owner or license.
