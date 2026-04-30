---
name: promote-skill
description: Use when publishing a SKILL.md-style agent skill across uGig, sh1pt, GitHub/gists, and follow-on skill marketplaces such as ClawHub, Goose, LobeHub, Kilo, Skillstore, FreeMyGent, ClawMart, Manus, VS Code Agent Skills, and Moltbook.
version: 1.0.0
author: Hermes Agent
license: MIT
when_to_use: Use when publishing, promoting, or packaging SKILL.md-style agent skills for uGig, sh1pt, GitHub/gists, ClawHub, Goose, LobeHub, Kilo, Skillstore, FreeMyGent, ClawMart, Manus, VS Code Agent Skills, or Moltbook.
metadata:
  supported_agents:
    - hermes
    - openclaw
    - claude-code
    - codex
    - cursor
    - windsurf
    - goose
  hermes:
    tags: [skills, marketplace, ugig, sh1pt, publishing, promotion]
    related_skills: [skill-marketplace-publishing, hermes-agent-skill-authoring, github-repo-management]
---

# Promote Skill

## Overview

Use this skill to turn a local `SKILL.md` into a public marketplace listing and promotion checklist. The workflow is agent-friendly:

1. Validate and sanitize the skill source.
2. Create a public source URL, preferably a GitHub repo or public gist raw URL.
3. Publish to uGig first because uGig imports the raw `SKILL.md`, scans it, and exposes a "Publish Everywhere" checklist.
4. Use sh1pt as the cross-marketplace promotion manifest/command generator.
5. Work through other marketplaces by CLI, PR, account submission, or manual upload depending on the platform.

Never include credentials, cookies, private env values, or personal secrets in a public skill file or marketplace listing.

## When to Use

Use this when the user says:

- "publish this skill"
- "promote this skill"
- "put it on uGig / ClawHub / LobeHub / Goose / Kilo"
- "make a public SKILL.md"
- "publish everywhere"
- "create a promote-skill workflow"

Do not use this for job applications themselves; use job-board specific skills for that.

## Inputs to collect or infer

Required:

- Local `SKILL.md` path or directory containing it.
- Public-safe title, slug, tagline, description, category, tags.
- Price in sats; `0` means free.

Optional:

- Existing public raw `SKILL.md` URL.
- GitHub repo/gist preference.
- uGig credentials or already-authenticated browser profile.
- Marketplace-specific credentials/API keys for platforms that need them.

## Safety checklist before publishing

Run a secrets scan before any public upload:

```bash
grep -RInE 'password|passwd|secret|token|api[_-]?key|BEGIN .*PRIVATE|private[_-]?key|cookie|credential' SKILL.md . 2>/dev/null || true
```

Then manually inspect hits. Mentions of environment variable names are fine; real values are not.

For paid listings, remember: marketplaces that import from a public raw URL may expose the artifact publicly. If the artifact is not intended to be free, verify access-gating from an anonymous browser before claiming it is paywalled.

## uGig workflow

Preferred CLI path once `ugig` supports `skills new`:

```bash
ugig skills new \
  --title "My Skill" \
  --description "Public credential-free SKILL.md for ..." \
  --tagline "Short marketplace tagline" \
  --category Automation \
  --price 0 \
  --tags "skills,automation,agents" \
  --source-url "https://raw-or-gist-url/SKILL.md"
```

`ugig skills create` is an alias for `ugig skills new`. If the installed CLI is older or does not support the needed fields, use the uGig browser form:

```text
https://ugig.net/dashboard/skills/new
```

Known form fields:

- Skill File URL: raw/direct public `SKILL.md` URL.
- Title.
- Tagline.
- Description.
- Price: `0` for free.
- Category.
- Tags: keep combined tags short; supported-agent chips may count toward the maximum.
- ClawHub URL: fill after publishing to ClawHub.

Verification:

- Listing URL is `/skills/<slug>`.
- Page says `Free` or the expected price.
- Security scan says `Clean`.
- Medium warning for environment variable access is expected if the skill documents env vars.
- Source URL is correct and contains no secrets.

## sh1pt workflow

The sh1pt CLI should provide top-level skill promotion commands:

```bash
sh1pt skills new --skill-file ./SKILL.md --source-url "https://raw-or-gist-url/SKILL.md" --price 0
sh1pt skills publish --all --dry-run
sh1pt skills publish --marketplace ugig clawhub goose
sh1pt skills marketplaces
```

Expected behavior:

- `sh1pt skills new` creates `sh1pt.skill.json` by reading frontmatter from the local `SKILL.md` and filling title/slug/description/tags/price/source URL.
- `sh1pt skills publish --all --dry-run` prints exact commands or manual steps for every known marketplace.
- Non-dry runs should not blindly execute unknown third-party CLIs until credentials/API setup is verified; print commands and mark manual/action-required states.

Implementation locations vary by project. In a typical sh1pt-style monorepo, add the command module under the CLI package and register it from the CLI entrypoint.

## Marketplace matrix

| Marketplace | Method | Publish pattern |
|---|---|---|
| uGig | CLI/API or browser | `ugig skills new ... --source-url <raw SKILL.md>` |
| ClawHub | CLI | `clawhub publish . --slug <slug> --version 1.0.0` |
| skills.sh | Auto-indexed | Push public GitHub repo containing `SKILL.md` |
| LobeHub Skills | Submit | Use site submission; install command shown as `npx @lobehub/cli skill install <slug>` |
| Goose Skills | PR / install URL | `goose skill add <raw SKILL.md URL>`; submit PR if directory requires it |
| Kilo Marketplace | PR | Fork + PR with valid `SKILL.md`; install command `kilo skill install <slug>` |
| Skillstore | GitHub repo | Submit repo/raw URL for security analysis |
| FreeMyGent | Upload | Upload `skill.md`, set price, connect wallet |
| ClawMart | API | `clawmart publish . --name <slug>` |
| Manus Agent Skills | Account | Free account required; submit through account UI |
| VS Code Agent Skills | GitHub | Publish via extension-indexed GitHub repo/PR |
| Moltbook / NormieClaw | Submit | Submit, set price, pass quality check |

## Public source choices

Quick gist:

```bash
gh gist create ./SKILL.md --public --desc "<skill title>"
gh api gists/<gist-id> --jq '.files["SKILL.md"].raw_url'
```

Better for auto-indexers:

```bash
mkdir -p /tmp/<slug>
cp ./SKILL.md /tmp/<slug>/SKILL.md
cd /tmp/<slug>
git init
git add SKILL.md
git commit -m "Add <slug> skill"
gh repo create <owner>/<slug>-skill --public --source=. --push
```

Prefer a repo over a gist when targeting skills.sh, VS Code Agent Skills, Goose/Kilo PRs, or marketplaces that require repository metadata.

## Common pitfalls

1. Using a human gist page instead of the raw URL. Use `gist.githubusercontent.com/.../raw/.../SKILL.md` for import.
2. Publishing credentials in examples. Use placeholder env var names only.
3. Too many tags on uGig. Keep tags under 10 and leave supported-agent chips blank if validation complains.
4. Assuming "Publish Everywhere" means automatic publication. It is a per-marketplace checklist; many require account registration, API keys, or PRs.
5. Calling unknown CLIs live without checking auth. Prefer dry-run until `command -v`, login status, and target repo/account are verified.

## Final report format

```text
Published:
- uGig: https://ugig.net/skills/<slug>
- GitHub source: https://github.com/<owner>/<repo>
- Raw SKILL.md: https://...

Ready/manual next:
- ClawHub: <command or login needed>
- Goose: <PR/command>
- LobeHub: <submission URL>

Security:
- Secret scan: clean / reviewed
- uGig scan: Clean; env-var warning expected
```
