---
name: skill-marketplace-publisher
description: Publish a Codex or Claude skill to Skillstore, SkillMap, or similar public skill marketplaces. Use when you need to audit a skill for public safety, build a public package, create a public GitHub repo, or submit a repo URL to marketplace intake endpoints.
---

# Skill Marketplace Publisher

## Overview

Use this workflow when a local skill should become a public, reviewable marketplace submission.
It covers four things end-to-end: public-safety audit, public packaging, GitHub publication, and marketplace submission.

This skill is optimized for:

- `Skillstore` self-serve submission
- `SkillMap` listing request via its current public intake channels
- any future marketplace that expects a public GitHub repo with a valid `SKILL.md`

## Required Inputs

Before running the workflow, confirm:

1. the source skill path
2. the target marketplace list
3. the public GitHub repo owner/name
4. whether the source skill is already public-safe or must be packaged in `public` mode first

If the user asks to publish a skill but does not say otherwise, assume:

- target mode: `public`
- source of truth stays in `ai-shared/skills/`
- packaged output goes to `ai-shared/skill-packages/`

## Workflow

### Step 1: Audit Public Safety

Run the local scanner first. It looks for secrets, local absolute paths, secret-hub references, and obvious non-portable material.

```bash
python3 scripts/public_skill_audit.py /absolute/path/to/skill
```

Interpretation:

- no `HIGH` findings: okay to continue
- `HIGH` findings: stop and sanitize first
- `MEDIUM` findings: review manually before publishing

If the skill references shared secrets, local private paths, or owner-only runtime assumptions, do not publish the source folder directly.

### Step 2: Decide Source vs Public Package

If the skill is already self-contained and clean, you may publish the source skill directory directly.

If the skill is not obviously portable, package it in `public` mode:

```bash
python3 ../../skill-package/scripts/skill_package.py analyze /absolute/path/to/skill
python3 ../../skill-package/scripts/skill_package.py build /absolute/path/to/skill --mode public
```

Use the packaged output as the publishable artifact for marketplaces.

Default packaged output root is the shared `skill-packages/` directory configured by the local `skill-package` workflow.

### Step 3: Validate Skill Metadata

Public submissions should include:

- a valid `SKILL.md` with frontmatter `name` and `description`
- supporting files referenced by the skill
- `agents/openai.yaml` when available
- a permissive repo-level license such as `MIT` or `Apache-2.0`

Validate the skill structure before publishing:

```bash
python3 ../skill-creator/scripts/quick_validate.py /absolute/path/to/skill-marketplace-publisher
```

For the target skill, at minimum manually confirm:

- `SKILL.md` loads cleanly
- referenced scripts and documents exist
- no broken relative links remain after packaging

### Step 4: Publish to a Public GitHub Repo

Create a clean git repo that contains either:

- the source skill folder, or
- the public package output

Typical flow:

```bash
mkdir -p /path/to/public-repo
rsync -a /path/to/publishable-artifact/ /path/to/public-repo/
cd /path/to/public-repo
git init
git checkout -b main
git add .
git commit -m "Publish skill for marketplace submission"
gh repo create <owner>/<repo> --public --source=. --remote=origin --push
```

If the skill lives inside a larger repo, marketplaces that support subdirectory URLs can accept a path such as:

```text
https://github.com/<owner>/<repo>/tree/main/path/to/skill
```

### Step 5: Submit to Skillstore

Skillstore has a real self-serve intake endpoint. Submit the public repo or public subdirectory URL:

```bash
python3 scripts/submit_marketplace.py skillstore \
  --repo-url https://github.com/<owner>/<repo>/tree/main/path/to/skill \
  --notes "Public-safe skill package prepared on 2026-03-26."
```

Expected result:

- JSON response with `success`
- a `submission_id`
- a status URL of the form `https://skillstore.io/submissions/<id>`

Save the submission ID and URL in the final delivery note.

### Step 6: Send SkillMap Listing Request

As of `2026-03-26`, SkillMap exposes public marketplace pages and public feedback/contact channels, but no clearly documented self-serve “publish skill” form was verified.

Use the feedback endpoint to send a listing request that includes:

- the public GitHub repo URL
- the skill summary
- installation notes if relevant

```bash
python3 scripts/submit_marketplace.py skillmap-feedback \
  --repo-url https://github.com/<owner>/<repo>/tree/main/path/to/skill \
  --skill-name <skill-name> \
  --email you@example.com
```

If needed, also use the contact email listed in `references/marketplaces.md`.

### Step 7: Record Outcome

For each marketplace, record:

- submitted URL
- submission/request timestamp
- returned submission ID or acknowledgement
- pending manual follow-up items

Formal delivery notes should be written to the user-facing outbox, not pasted only in chat.

## Decision Rules

- If the source skill contains any real secrets or private business logic, do not publish the source directly.
- If the skill depends on local-only files, prefer packaged `public` output.
- If the marketplace accepts only a repo URL, publish a dedicated clean repo.
- If the marketplace accepts a subdirectory URL, you may publish only the skill subtree.
- If a marketplace name cannot be verified with a public live submission path, mark it `unverified` and do not pretend it is a supported route.

## Current Marketplace Notes

Read these before claiming a marketplace is supported:

- `references/marketplaces.md`

Key current state:

- `Skillstore`: verified live submission route
- `SkillMap`: verified live marketplace plus verified public intake channels, but no confirmed self-serve listing form
- `CrowdHub`: unverified for this workflow as of `2026-03-26`

## Scripts

### `scripts/public_skill_audit.py`

Checks a skill tree for:

- likely secret values
- local absolute paths
- secret-hub references
- obvious non-portable content

### `scripts/submit_marketplace.py`

Supports:

- `skillstore` submission
- `skillmap-feedback` listing request

## References

- `references/marketplaces.md`: dated marketplace research and current submission paths
