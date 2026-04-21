---
name: skill-market-publisher
description: Publish, submit, and verify local skills across public skill marketplaces, directories, and registries. Use when an agent needs to take a skill folder or skill repository, confirm current submission paths, prepare cross-market metadata, run verified live adapters, or generate manual submission bundles for markets such as AgentSkill.sh, Skillstore, SkillNet, agent-skills.md, SkillsMD, SkillHub, SkillHQ, and related registries.
---

# Skill Market Publisher

## Overview

Use this skill to turn one local skill folder into a reusable market release plan. Keep the skill itself timeless: document current submission surfaces, verification patterns, and adapter logic, but keep one-off submission IDs, sample URLs, and dated field logs outside the reusable skill folder.

## Quick Start

1. Re-check live market surfaces before making claims about support:

```bash
python3 scripts/skill_market_publish.py recon
```

2. Inspect one skill and build a market readiness plan:

```bash
python3 scripts/skill_market_publish.py plan /abs/path/to/skill \
  --repo-url https://github.com/owner/repo \
  --git-ref main \
  --tag automation \
  --tag research
```

3. Generate a review bundle before any live submission:

```bash
python3 scripts/skill_market_publish.py bundle /abs/path/to/skill \
  --repo-url https://github.com/owner/repo \
  --git-ref main \
  --author-name "Your Name" \
  --author-email you@example.com \
  --version 0.1.0 \
  --skillz-category automation \
  --bogen-category development \
  --a2a-category research \
  --a2a-price 9.0 \
  --a2a-seller 0xYourWalletAddress \
  --out-dir /tmp/skill-market-bundle
```

4. Publish one wrapped live target at a time. Live submission requires `--execute`.

```bash
python3 scripts/skill_market_publish.py publish agentskill-sh /abs/path/to/skill \
  --repo-url https://github.com/owner/repo \
  --execute
```

5. Verify the result using the market-specific checks in [references/verification-playbook.md](references/verification-playbook.md).

## Workflow

### 1. Normalize the Release Unit

Treat the publishable unit as one skill folder containing `SKILL.md`.

- If the repository contains many skills, publish each skill separately.
- If the repository is a pack, split markets into:
  - pack importers that should ingest the public repo once
  - per-skill submitters that should receive a folder URL or raw `SKILL.md` content
- If a market works at repository scope, make sure the chosen public repository layout matches that market before submitting.

### 2. Detect Repository Layout

Run `inspect` or `plan` first. The bundled CLI classifies the current repository as:

- `single-skill-repo`
- `root-pack`
- `skills-subdir-pack`
- `nested-skill-dir`
- `standalone-skill-dir`

Some markets accept any repository URL. Others currently prefer a repository with a top-level `skills/` directory. When layout and market expectations conflict, create a mirror or release repository instead of reshaping the source repository for one listing.

Treat submit-page copy as a hint, not proof. Some live backends accept `root-pack` repositories even when the visible page copy talks about a repo-root `skills/` directory. Verify layout assumptions from the live preview, submit response, or public read API before forcing a mirror.

### 3. Choose the Market Mode

Use automated publishing only for targets that are currently verified in [references/market-matrix.md](references/market-matrix.md).

Current modes:

- `auto-cli`: official CLI publishing wrapped by this skill
- `auto-http`: stable HTTP form or API submission wrapped by this skill
- `manual-web`: browser submission workflow with no stable documented endpoint in this skill
- `index-only`: discovery depends on installability, GitHub App ingestion, or passive indexing rather than explicit submission
- `incompatible`: expects a different artifact format than a plain skill folder
- `needs-recon`: public site exists, but the current publish path is not verified

Some markets also expose official CLI or seller dashboards that this skill records but does not proxy. Treat those as documented manual flows unless the bundled CLI explicitly supports them.

### 4. Prepare Market Inputs

Provide explicit values for market-only fields instead of guessing.

- Use `--version` for ClawHub publishing.
- Use `--author-email` and `--skillz-category` for Skillz Directory.
- Map domain-specific categories onto the market's real enum. If the market does not expose `research`, `browser`, or another domain label you want, choose the closest supported value or `other` instead of inventing one.
- Use `--a2a-price`, `--a2a-category`, and `--a2a-seller` for A2A Market.
- Use `--git-ref` when the bundle should include stable GitHub `blob` and raw `SKILL.md` URLs, or when a market benefits from a folder-scoped GitHub `tree` URL.
- When a market accepts a GitHub URL, decide deliberately between:
  - repository URL
  - repo-root pack URL
  - folder `tree/<ref>/<path>` URL

Accepted input alone does not prove scoping. Some markets accept a folder URL but still ingest the entire repository pack.

Run `plan` after setting these fields. The CLI reports missing inputs and layout blockers per market.

### 5. Build A Review Bundle

Use `bundle` before live submission. The bundle gives you:

- normalized skill metadata
- a per-market readiness matrix
- payloads for wrapped live targets
- manual submission notes for every non-wrapped target

Use the bundle as an operator review packet, not just a payload dump. Before live submit, check that it exposes:

- the canonical repository URL and `SKILL.md` URL
- the exact URL scope you intend to submit
- one short example task or prompt for the listing
- the strongest verification URLs you expect to use after submit

### 6. Publish Safely

Use this order:

1. `inspect`
2. `plan`
3. `bundle`
4. `publish <market>` without `--execute`
5. `publish <market>` with `--execute`
6. verify with the market-specific public checks

Do not claim one-click support for a market marked `manual-web`, `index-only`, `incompatible`, or `needs-recon`.

Interpret live responses by semantics, not by HTTP status alone:

- `alreadyExists` or `updated` often means the market recognized an existing public listing.
- `processing` or `submission received` means the intake pipeline accepted the request, not that the listing is public yet.
- duplicate-name or pending-review errors can still prove the market recognized the listing identity.
- a redirect to a public detail page is stronger evidence than a flash message or success banner.

### 7. Record Outcomes Outside The Skill

Keep reusable skill docs free of sample-specific evidence.

- Do not store live submission IDs, PR numbers, sample slugs, or dated field logs inside this skill.
- Put one-off execution evidence in the task conversation, a separate operator notebook, or a temporary bundle outside the reusable skill folder.
- Update this skill only when the reusable workflow changes.

## Bundled CLI

### `inspect`

Parse frontmatter, derive summary text, detect repository layout, and show normalized metadata.

### `plan`

Build a readiness matrix for known markets and report missing fields or layout warnings.

### `bundle`

Write a reusable submission bundle containing:

- `manifest.json`
- `market-plan.json`
- per-market payload files
- manual submission notes

### `publish <market>`

Supports live execution only when `--execute` is present.

Wrapped live targets:

- `clawhub`
- `agent-skills-md`
- `agentskill-sh`
- `skillz-directory`
- `skillstore-io`
- `skillsmd-dev`
- `bogen-ai`
- `skillsrep`
- `a2a-market`

### `recon`

Fetch known market pages and check expected markers. Run this when a marketplace may have changed since the last verification pass.

## Operating Rules

- Publish from a public repository URL unless the market is local-CLI only.
- Keep skill content English-only unless a target market explicitly requires localized marketing copy.
- Prefer stable repository URLs and stable `SKILL.md` URLs when the market supports deep links.
- When a market expects a different repository layout, create a publish mirror instead of mutating the source repository just for one listing.
- Prefer the strongest public verification surface the market exposes: status API, workflow URL, detail page, public read API, then search page.
- If a folder URL submission returns a pack-sized import count, treat the scope as repository-wide until the public result proves otherwise.
- Keep the reusable skill free of sample submission logs, IDs, and dated evidence.
- Treat market behavior as time-sensitive. Re-run `recon` before changing adapters or writing claims about current support.

## References

- Read [references/market-matrix.md](references/market-matrix.md) when choosing markets or checking current compatibility.
- Read [references/publish-playbook.md](references/publish-playbook.md) when mapping a skill repo to each market's intake model.
- Read [references/verification-playbook.md](references/verification-playbook.md) when checking whether a submission is public, pending, blocked, or only indexed.
- Read [references/recon-playbook.md](references/recon-playbook.md) when adding a new market or repairing a broken adapter.
