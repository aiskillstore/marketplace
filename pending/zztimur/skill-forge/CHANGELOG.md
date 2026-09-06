# Changelog

All notable changes to Skill Forge are documented here. The project follows
[Semantic Versioning](https://semver.org/) and keeps unreleased changes at the
top until the local release command promotes them into a versioned entry.

## [Unreleased]

## [v2.2.1] - 2026-09-06

### Fixed

- Route direct requests to improve a skill into scoped Repair while keeping suggestions, questions, historical quotations, and explicit no-edit requests read-only.
- Preserve exact request text in routing golden cases so changing a prompt cannot silently retain an unrelated expected result.

## [v2.2.0] - 2026-09-06

### Added

- Transactional verified-archive installation with rollback and obsolete-file removal.
- Reviewer-pinned release receipts and exact-commit CI checks before dispatch-authorized publication. Tag pushes build candidates without publishing.
- Explicit tool-free API grading controller and paired outcome comparisons; live evidence remains unavailable until actual sessions run.

### Fixed

- Enforce published description/compatibility field limits and metadata string maps; previously accepted invalid fields now fail strict inspection.
- Remove duplicated README score and separate package, design, observed behavior and host evidence.
- Label rubric-only controls accurately and avoid eagerly loading every reference in grading trials.

## [v2.1.0] - 2026-09-06

### Added

- Added rubric 2.0 with fourteen anchored criteria and a versioned scorecard
  calculator. Quality, evidence coverage, optional legacy score caps, and release
  verdicts are reported separately; historical scores retain their rubric version.
- Added source-only synthetic agent evaluation fixtures and trace checks. Live
  grading consistency and human calibration are not claimed by these fixtures.
- Added a capability-checked self-test launcher with a pinned Linux Docker image,
  bounded copied inputs and output, resource probes, and fail-closed unsupported
  host behavior. macOS target execution remains unavailable.

- Added a security policy, contribution guide, and structured issue forms for
  bugs, false positives, new checks, compatibility requests, and safe security
  contact requests.

### Changed

- Standard audits lead with the decision and findings; the complete release gate
  matrix and historical evaluator bootstrap guidance load only for release work.
- Description quality no longer receives automatic short-text or English-keyword
  penalties. Required fields and objective target limits remain enforced.

- Rebuilt the README front door with a faster quick start, Agent Skill
  installation guidance, an example release verdict, and a concise comparison
  with basic package linting.
- Promoted the tested `npx skills` installation path, added the `skills.sh`
  badge, and retained checksum-verified release installation instructions.

### Fixed

- Redacted sensitive values across public inspector paths, mapping keys, CLI
  diagnostics, JSON, and Markdown without conflating distinct findings.
- Resolved document-relative dependency links consistently, including normalized
  paths and transitive references, with bounded traversal and containment checks.
- Reconciled example scorecards and pressure-report guidance with legacy-only caps.

## [v2.0.2] - 2026-07-17

### Added

- Added post-publication verification that downloads release assets by exact
  tag, compares them with the validated workflow artifact, verifies the
  published checksum, and source-proves both canonical profiles.

### Changed

- Updated official GitHub Actions to immutable Node 24-native releases.
- Limited the cross-platform Self Tests workflow to branch pushes, pull
  requests, and manual dispatches so atomic branch-and-tag releases do not run
  the same matrix twice; tag validation remains in Release Skill.

## [v2.0.1] - 2026-07-17

### Fixed

- Normalized contract reference identities to POSIX paths so Windows validation
  recognizes the shipped reference files consistently.

## [v2.0.0] - 2026-07-17

### Added

- Added a one-time, explicitly pinned schema 5 to 6 bootstrap path for
  independently inspecting the exact v2.0.0 candidate without exposing raw
  frontmatter or treating the transition as a reusable schema-6 pass.

### Changed

- Changed inspector JSON to schema 6. Frontmatter output is now structural and
  redacted instead of serializing raw values; integrations that consume this
  field must update for the new output contract.
- Centralized the canonical runtime-file boundary shared by packaging, source
  proof, and tests, and aligned the audit contract and resource-routing guidance
  with the supported Portable and OpenAI profiles.

### Fixed

- Rejected payload-bearing ZIP directory entries and non-finite YAML numbers,
  detected absolute shell pipeline targets, and recognized source-only tool
  declarations without weakening strict inspection coverage.

## [v1.0.1] - 2026-07-17

### Changed

- Aligned the documentation, release contract, and regression harness with the
  supported portable and OpenAI profiles.

### Removed

- Removed retired profile fixtures, routing, and compatibility guidance.

## [v1.0.0] - 2026-07-17

### Changed

- Re-established Skill Forge as a clean v1 release with portable and OpenAI as
  its supported validation profiles.

### Removed

- Removed retired host-specific profiles and their related validation paths.

## [v0.6.1] - 2026-07-16

### Fixed

- Made local release preparation calculate the staged changelog blob through
  Git clean filters, so Windows CRLF worktrees no longer reject valid releases.
- Made independent-evaluator tree snapshots use fresh pre- and post-hash file
  metadata, avoiding Windows `DirEntry` cache false positives.
- Preserved annotated release tags through GitHub Actions checkout and required
  the remote tag to exist before GitHub Release publication.

## [v0.6.0] - 2026-07-17

### Added

- Added a canonical runtime manifest, byte-reproducible ZIP construction,
  local Git source proof, and digest binding between archive and source evidence.
- Added a source-only regression runner and a pinned independent-evaluator
  harness with explicit Pass, Fail, and Not Assessed semantics.

### Changed

- Every supported OS/Python CI cell now runs source tests, builds and
  source-proves the submitted commit, extracts it, and tests the shipped runtime.
- Release metadata now requires exact committed changelog, commit, annotated-tag,
  and tagger-date evidence; release notes use the tagged changelog blob and
  publication guidance uses an atomic branch-and-tag push.
- Split source-only release checks from the runtime regression suite, superseding
  the installed-runtime SKIP behavior introduced in v0.5.2.

### Fixed

- Hardened manifest and finding integrity, multi-profile request routing,
  evidence/scoring reconciliation, and artifact trust/redaction boundaries.
- Closed safety-scan gaps across shell, PowerShell, batch, Python, and
  JavaScript/TypeScript, including bounded hidden and extensionless content.
- Enforced portable path identity, Unicode, Windows-name, ancestor-conflict, and
  length rules consistently for folders, ZIP inspection, and package verification.

## [v0.5.2] - 2026-07-16

### Fixed

- Made release checksums use the archive's portable filename so the published
  ZIP verifies after users download both release assets.
- Made the installed runtime regression runner skip source-only release checks
  instead of failing to import helpers deliberately excluded from the package.

### Changed

- Clarified generic host routing and the boundary between standalone-Skill
  validation and plugin-manifest validation.

## [v0.5.1] - 2026-07-15

### Fixed

- Made the release publication job pass its repository explicitly when it
  creates a GitHub Release without checking out Git metadata.
- Made the unreadable-directory regression fixture detect permission denial
  before it runs, avoiding false failures on Windows filesystems that do not
  apply POSIX traversal permissions.

## [v0.5.0] - 2026-07-15

### Added

- A committed changelog and local release command that validates, records,
  commits, and tags a semantic version before publication.
- Release metadata validation that requires a semantic-version tag and a
  matching changelog entry before GitHub can publish a release.
- Seeded regression fuzzing for portable ZIP identities, frontmatter parsing,
  numeric limits, and report/gate matrices.
- Cross-platform GitHub Actions coverage on Linux, macOS, and Windows, plus a
  pull-request gate that verifies the actual submitted runtime archive.

### Changed

- GitHub Release notes now use the committed changelog entry for the tagged
  version, with a commit-range link for detailed history.
- Release workflow validation is read-only; publication is isolated to the
  job that needs `contents: write` and ships a SHA-256 checksum with the ZIP.
- Runtime installation parity now means parity with the verified runtime
  archive; repository-only CI and release-note tooling remain excluded.

### Fixed

- Made strict secret and dangerous-command coverage fail closed across POSIX,
  PowerShell, and Windows batch script formats.
- Rejected ZIP path collisions, Unicode and Windows filesystem ambiguities,
  unsafe extraction paths, and bounded archive-verification failures.
- Corrected profile-aware YAML/frontmatter validation and automated report
  contract integrity checks.
- Hardened Skill Forge's self-audit evidence boundary so bundled tests cannot
  be mistaken for independent release validation.

## [v0.4.0] - 2026-07-15

### Added

- Enforced audit and release-report contracts.
- Added explicit platform-validation profiles.

### Fixed

- Separated evaluation plans from repair actions.
- Established trusted validator-evidence boundaries.
- Enforced OpenAI Skill metadata constraints.
- Closed strict safety-scan coverage gaps.
