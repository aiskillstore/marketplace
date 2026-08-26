# Changelog

## 0.3.5 - 2026-05-07

### patch

- [#170](https://github.com/equinor/fusion-skills/pull/170) [`5e43223`](https://github.com/equinor/fusion-skills/commit/5e432232917b2b1642431d80cf1698bbefe80ee8) - Apply caveman-compress prose style to SKILL.md and references.


  - Drop articles, filler, hedging from SKILL.md activation body
  - Compress instructions, mcp-server, questions references

## 0.3.4 - 2026-05-04

### patch

- [#153](https://github.com/equinor/fusion-skills/pull/153) [`3911da5`](https://github.com/equinor/fusion-skills/commit/3911da5922ab0b392d6c9b93a284ce0746870364) - Clarify sub_issue_id requires object ID, not issue number


  - Promote the ID vs number distinction to a prominent warning block above the example
  - Add a `gh api` command showing how to retrieve the object ID
  - Add a troubleshooting table covering 404, invalid input, and silent-failure modes
  - Clarify that `after_id`/`before_id` in reprioritize are also object IDs
  - Add sub-issue linking activation cues to SKILL.md triggers

  resolves equinor/fusion-skills#79

- [#156](https://github.com/equinor/fusion-skills/pull/156) [`3ed5296`](https://github.com/equinor/fusion-skills/commit/3ed52962820549c21ddbec57df01273c5c930749) - Strengthen devil's-advocate agent for task-planning context


  Expands the devil's advocate with:
  - Auto-escalation to interrogator mode when a task-planning pass surfaces two or more architecture-ambiguity signals (no user trigger required)
  - Extended Task concerns in moderate mode: premature decomposition, implicit cross-task contracts, and tasks that hide unresolved architecture assumptions
  - New "Task-planning context" section in interrogator mode with four targeted decision branches: premature decomposition, implicit contracts, sequencing pressure, and hidden assumptions

  resolves equinor/fusion-skills#132

## 0.3.3 - 2026-04-06

### patch

- [#135](https://github.com/equinor/fusion-skills/pull/135) [`5fa9384`](https://github.com/equinor/fusion-skills/commit/5fa938467edfad41d381f0ee2d7320b609c156ed) - Make draft location flexible — check user preferences and session memory before defaulting to `.tmp/`


  - Step 4 now checks user preferences and session memory for a preferred draft location
  - Asks once when intent is ambiguous and remembers the answer for the session
  - Falls back to `.tmp/{TYPE}-{CONTEXT}.md` only when no preference is found

## 0.3.2 - 2026-03-23

### patch

- [#121](https://github.com/equinor/fusion-skills/pull/121) [`831f8ee`](https://github.com/equinor/fusion-skills/commit/831f8eed3054ee747d3300c9144312ef3b5c02e0) - Add devil's advocate agent for issue authoring


  - Always-on moderate mode raises 2-3 key concerns after classification
  - Interrogator mode runs full structured interview on explicit user request or when scope/criteria gaps are significant
  - Wired into SKILL.md agent modes section

  Refs: equinor/fusion-core-tasks#847

## 0.3.1 - 2026-03-21

### patch

- [#112](https://github.com/equinor/fusion-skills/pull/112) [`e90fb97`](https://github.com/equinor/fusion-skills/commit/e90fb97b20d1aceb0929dbc96bddf28fdf358f0a) - Add contributor-guide-aware repository routing to issue authoring


  - SKILL.md Step 2: read active workspace `CONTRIBUTING.md` / `contribute/` for routing rules before asking the user
  - `references/instructions.md`: add Repository routing note pointing to SKILL.md Step 2 as authoritative flow

## 0.3.0 - 2026-03-18

### minor

- [#98](https://github.com/equinor/fusion-skills/pull/98) [`6bb9cdc`](https://github.com/equinor/fusion-skills/commit/6bb9cdcc1e2e0ed25d562bfd5db4dfab52559c0f) - Consolidate issue-authoring capability into a single skill with agent modes


  - Merge type-specific drafting logic from 4 subordinate skills into agent mode files (`agents/*.agent.md`)
  - Move all 10 issue templates into `assets/issue-templates/` within this skill
  - Update orchestrator to route to internal agent modes instead of external subordinate skills
  - Retain full 8-step workflow, shared gates, caching strategy, and MCP mutation sequencing

  Resolves equinor/fusion-core-tasks#802

## 0.2.4 - 2026-03-17

### patch

- [#85](https://github.com/equinor/fusion-skills/pull/85) [`c8ba3df`](https://github.com/equinor/fusion-skills/commit/c8ba3df924c5a712c835cdb9f4de44bac03b7ad4) - Make all GitHub-API-consuming skills more conservative with token usage.


  - `fusion-issue-authoring`: concrete session-cache flow for labels and assignee candidates; per-session budget table
  - `fusion-issue-solving`: expanded low-token strategy with session-cache references and budget awareness
  - `fusion-github-review-resolution`: token budget guidance for thread-heavy reviews; cache PR metadata once
  - `fusion-issue-task-planning`: session-cache delegation rules and batch-size warning for large task plans
  - `fusion-dependency-review`: explicit data-reuse rules across parallel advisor fan-out
  - `fusion-discover-skills`: tighter GraphQL budget and call-count cap for discovery sessions

  resolves equinor/fusion-core-tasks#797

## 0.2.3 - 2026-03-11

### patch

- [#76](https://github.com/equinor/fusion-skills/pull/76) [`3efc478`](https://github.com/equinor/fusion-skills/commit/3efc47886871a14b18eb9f68abd562a10c6cf277) - Reduce token-heavy issue authoring behaviors by tightening MCP-first mutation sequencing and fallback guidance.


  - Replace redundant two-pass issue update guidance with single-call-first `issue_write` sequencing
  - Clarify cache-first behavior for labels and issue types to avoid repeated lookups
  - Add explicit rate-limit handling guidance that avoids retry loops and preserves local draft state
  - Tighten duplicate-search guidance to one focused pass unless scope changes

  resolves equinor/fusion-core-tasks#535

## 0.2.2 - 2026-03-05

### patch

- [#55](https://github.com/equinor/fusion-skills/pull/55) [`2d346c8`](https://github.com/equinor/fusion-skills/commit/2d346c812b4927ed1fdf17c92d51856d1fdc09c3) - Add required ownership metadata (`metadata.owner`, `metadata.status`) to all skills. Owner is set to `@equinor/fusion-core` (repository default) and status is set according to skill lifecycle (`active` for production skills, `experimental` for early-stage skills). Sponsor metadata was considered but is not required for MVP.


  resolves equinor/fusion-core-tasks#474

## 0.2.1 - 2026-03-03

### patch

- [#42](https://github.com/equinor/fusion-skills/pull/42) [`947c0ab`](https://github.com/equinor/fusion-skills/commit/947c0ab73844f5eb13b80e7cb2f3e5ea8146ea59) - Normalize issue-authoring orchestration/reference docs to canonical MCP tool naming (`mcp_github::tool`) for duplicate checks, ordered mutations, and issue-type lookup guidance.


  Maintains MCP-first behavior and adds documented GraphQL fallback query assets for parent/sub-issue and issue-type operations where MCP write coverage is unavailable.

  refs equinor/fusion-skills#40
  resolves equinor/fusion-core-tasks#446

## 0.2.0 - 2026-02-20

### minor

- [#23](https://github.com/equinor/fusion-skills/pull/23) [`14b9c99`](https://github.com/equinor/fusion-skills/commit/14b9c9902dbf8bafdae9fe0fc6c08c81dec004b1) - Migrate issue authoring guidance from helper scripts to GitHub MCP-first workflows, including MCP metadata declarations and updated orchestration/ref docs.


  resolves equinor/fusion-skills#21

## 0.1.1 - 2026-02-20

### patch

- [#20](https://github.com/equinor/fusion-skills/pull/20) [`66d85b8`](https://github.com/equinor/fusion-skills/commit/66d85b8200f7712fd916148e75906bf7fa15101c) - Clarify issue-closing keyword guidance across skill and contributor docs:


  - align wording to keyword families (`fix|fixes|resolve|resolves|close|closes`)
  - standardize direct issue reference examples (`owner/repo#123`)
  - keep `Refs`/`Ref` as the default for non-closing references

- [#13](https://github.com/equinor/fusion-skills/pull/13) [`205df94`](https://github.com/equinor/fusion-skills/commit/205df948ffaaf785e15f2cacd392126ca4c398e3) - Improve issue automation reliability in `fusion-issue-authoring`:


  - switch issue-type updates to GraphQL `updateIssue(issueTypeId: ...)` in shell and PowerShell helpers
  - add explicit post-update verification output for issue type
  - guard `set -u` in VS Code integrated zsh sessions to avoid shell integration hook failures
  - update runbook/docs snippets to use the robust pattern and verification command

  resolves equinor/fusion-core-tasks#402

## 0.1.0 - 2026-02-20

### minor

- [#10](https://github.com/equinor/fusion-skills/pull/10) [`d473723`](https://github.com/equinor/fusion-skills/commit/d4737239be54736e344d74be4ce8271b9be84313) - Adds structured frontmatter metadata for discoverability and clarifies skill relationship semantics.


  Scope delivered:
  - Added `metadata.tags` to affected skills for discoverability.
  - Renamed relationship keys to a clearer schema: `skill_role` → `role`, `required_skill` → `orchestrator`, `sub_skills` → `skills`.
  - Updated dependent role value from `subskill` to `subordinate` to explicitly indicate orchestrator dependency.
  - Updated skill authoring guidance to document `metadata.role`, `metadata.orchestrator`, `metadata.skills`, and `metadata.tags`.

- [#7](https://github.com/equinor/fusion-skills/pull/7) [`2194e7a`](https://github.com/equinor/fusion-skills/commit/2194e7a99f6055dd394dffca6e0e6286d3bb2d41) - Implements `equinor/fusion-core-tasks#395` (sub-task of `#391`) by restructuring issue authoring skills into a top-level orchestrator plus type-specific specialists.


  Refs: `equinor/fusion-core-tasks#391`

  closes equinor/fusion-core-tasks#395

  Scope delivered:
  - `fusion-issue-authoring` is now the orchestration layer for shared gates (classification, labels, assignee, confirmation, publish flow).
  - Added specialist skills: `fusion-issue-author-bug`, `fusion-issue-author-feature`, `fusion-issue-author-user-story`, and `fusion-issue-author-task`.
  - Specialist skills now explicitly depend on `fusion-issue-authoring` and keep only type-specific guidance.
  - Moved fallback templates from shared assets to each specialist skill’s own `assets/issue-templates/`.
  - Added label listing helpers: `list-labels.sh` and `list-labels.ps1`.
  - Hardened relationship scripts for reliable GraphQL calls and idempotent "already linked" handling.
