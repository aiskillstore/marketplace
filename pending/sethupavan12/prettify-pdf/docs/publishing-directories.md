# Publishing To Skill Directories

The public repository is:

```text
https://github.com/sethupavan12/prettify-pdf
```

## Current Status

- GitHub repo is public and installable.
- `skills.sh` install has been tested with `npx skills add sethupavan12/prettify-pdf`.
- Login-gated directories still need the maintainer account to complete submission or publication.

## skills.sh

`skills.sh` lists skills based on anonymous install telemetry from the `skills` CLI. The docs say a skill appears on the leaderboard once users install it with `npx skills add <owner/repo>`.

Install command:

```bash
npx skills add sethupavan12/prettify-pdf
```

README badge:

```markdown
[![skills.sh](https://skills.sh/b/sethupavan12/prettify-pdf)](https://skills.sh/sethupavan12/prettify-pdf)
```

Telemetry opt-out for users who do not want installs counted:

```bash
DISABLE_TELEMETRY=1 npx skills add sethupavan12/prettify-pdf
```

## agentskill.sh

Submit page:

```text
https://agentskill.sh/submit
```

Use the GitHub repository import:

```text
https://github.com/sethupavan12/prettify-pdf
```

The directory scans the repo for `SKILL.md` files. After import, it can sync from GitHub. For instant updates, add this GitHub webhook:

```text
https://agentskill.sh/api/webhooks/github
```

Webhook settings:

- Content type: `application/json`
- Events: push only

## Skillstore

Submit page:

```text
https://skillstore.io/submit
```

Use:

```text
https://github.com/sethupavan12/prettify-pdf
```

Skillstore accepts a repository containing a valid `SKILL.md`; skills with scripts may receive additional security review.

## SkillUse

SkillUse publishes repositories through its authenticated CLI.

```bash
skilluse auth login
skilluse publish --repo sethupavan12/prettify-pdf --version 0.1.0
```

If the CLI expects a nested skill folder, use the repository URL in its web import flow instead of duplicating this skill inside the repo.

## ClawHub / OpenClaw

ClawHub is OpenClaw's skill registry. Publishing requires ClawHub login.

Install CLI:

```bash
npm i -g clawhub
```

Authenticate:

```bash
clawhub login
clawhub whoami
```

Dry-run first:

```bash
clawhub skill publish . \
  --slug prettify-pdf \
  --name "Prettify PDF" \
  --version 0.1.0 \
  --changelog "Initial public release" \
  --dry-run
```

Publish:

```bash
clawhub skill publish . \
  --slug prettify-pdf \
  --name "Prettify PDF" \
  --version 0.1.0 \
  --changelog "Initial public release"
```

Install from OpenClaw after publication:

```bash
openclaw skills install prettify-pdf
```

Until it is published on ClawHub, install directly from GitHub:

```bash
mkdir -p "$HOME/.openclaw/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.openclaw/skills/prettify-pdf"
openclaw skills list
```

## openclawskill.ai

OpenClaw Skill describes a marketplace for SKILL.md files and exposes an upload flow. Use the public GitHub repository URL:

```text
https://github.com/sethupavan12/prettify-pdf
```

If the upload form requests metadata:

- Name: `prettify-pdf`
- Display name: `Prettify PDF`
- Category: `Productivity`, `Documents`, or `PDF`
- Description: `Redesign or QA PDFs while preserving IDs, dates, amounts, barcodes, QR codes, seals, signatures, labels, and source meaning.`
- Repository: `https://github.com/sethupavan12/prettify-pdf`
- License: `MIT`

## skills.re

Submit page:

```text
https://skills.re/submit
```

The current submit page expects a repository containing a `skills/` folder with at least one `SKILL.md`. This repository keeps the skill at the root, so either:

1. Ask the directory to support root-level `SKILL.md` repos, or
2. Add a mirrored `skills/prettify-pdf/` folder in a separate distribution repo.

Do not duplicate the skill in this repo unless you also update validation to avoid two divergent copies.

## mdskills.ai

mdskills.ai documents skills as plain folders with `SKILL.md` files. Submit or list this repo using:

```text
https://github.com/sethupavan12/prettify-pdf
```

Recommended categories:

- `Documents`
- `PDF`
- `Productivity`
- `Quality Assurance`

## skillsdir.dev

Submit page:

```text
https://skillsdir.dev/add
```

Use:

```text
Unique ID: prettify-pdf
Summary: Prettify PDFs without breaking IDs, dates, amounts, barcodes, QR codes, seals, signatures, or source meaning.
Repository: https://github.com/sethupavan12/prettify-pdf
```

## OmniSkill

Submit page:

```text
https://omniskill.online/
```

Use the repository submission field with:

```text
https://github.com/sethupavan12/prettify-pdf
```

## Agensi

Agensi is a curated SKILL.md marketplace. Submit through the website using the repository URL:

```text
https://github.com/sethupavan12/prettify-pdf
```

Recommended listing copy:

```text
Prettify PDF is a local-first Agent Skill for redesigning and QAing PDFs without breaking critical source data. It focuses on receipts, invoices, appointments, forms, tickets, resumes, and reports where IDs, timestamps, totals, barcodes, QR codes, seals, and labels must survive exactly.
```

## GitHub Discovery

Keep these topics on the repository:

- `agent-skills`
- `skill-md`
- `pdf`
- `pdf-tools`
- `document-ai`
- `local-first`
- `privacy`
- `codex`
- `claude-code`
- `openclaw`
- `opencode`
- `llm-tools`

Use this description:

```text
Agent Skill for prettifying PDFs without breaking IDs, dates, amounts, barcodes, QR codes, seals, signatures, or source meaning.
```
