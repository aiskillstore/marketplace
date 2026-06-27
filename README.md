# Skill Store — Marketplace Repository

This is the open-source content repository behind **[Skill Store](https://skillstore.io)**. It stores every approved [Agent Skill](https://agentskills.io/specification), the records that go with it, and the automated security audits each skill must pass before it ships.

> **This repo is a companion to the Skill Store platform, not the place to submit skills.**
> Skills are added through [skillstore.io](https://skillstore.io) — its review pipeline writes to this repo automatically. Please **do not open a pull request here to add a skill**; PRs adding skills will be closed. See [Contributing a skill](#contributing-a-skill) below.

## Installing a skill

The recommended way to install any skill is the **`skillstore` CLI** — one command works for both **Claude Code** and **Codex**:

```sh
npx skillstore add author/skill-name
```

For example:

```sh
npx skillstore add aiskillstore/code-review
```

It downloads the skill and drops it into the right `skills/` directory for your tool. Claude Code auto-discovers it; for Codex, restart the session.

Prefer to do it by hand, or installing via Claude Web? See the full **[Installation Guides](https://skillstore.io/docs/install-guides)** for every method (CLI, manual, and ZIP upload) and the scope directories (`.claude/skills/`, `~/.claude/skills/`, `.codex/skills/`, …).

## Contributing a skill

Submit through the platform — not through a pull request:

1. Go to **[skillstore.io/submit](https://skillstore.io/submit)**.
2. Enter the GitHub repository URL that contains your `SKILL.md`.
3. Your submission runs through automated security analysis.
4. A maintainer reviews and approves it.
5. On approval, the skill is published here and appears on [skillstore.io](https://skillstore.io).

### What makes a valid skill

- `SKILL.md` — the skill definition (**required**, per the [Agent Skills spec](https://agentskills.io/specification))
- Supporting files the skill references (optional)
- `LICENSE` (recommended)

### Security audit

Every submission is scanned automatically before it can be published. The audit flags things like:

- Dangerous code patterns (`eval`, `exec`, raw system commands)
- File access outside the project scope
- Network calls to external hosts
- Obfuscated or minified code
- Credential / secret handling

Skills that fail are not published.

## Repository layout

```
.
├── skills/        # Approved, published skills (one folder each, with SKILL.md)
├── pending/       # Submissions awaiting review
├── packages/
│   ├── cli/       # The `skillstore` CLI (npx skillstore add …)
│   └── skillstore/
├── schemas/       # JSON schemas for skill records
├── scripts/       # Maintenance & scoring scripts
└── .github/workflows/   # Submission, audit, and sync automation
```

The contents of this repo are maintained by Skill Store's automated pipeline. Manual changes are limited to maintainers.

## Links

- **Website**: [skillstore.io](https://skillstore.io)
- **Submit a skill**: [skillstore.io/submit](https://skillstore.io/submit)
- **Install guides**: [skillstore.io/docs/install-guides](https://skillstore.io/docs/install-guides)
- **Docs**: [skillstore.io/docs](https://skillstore.io/docs)
- **Agent Skills spec**: [agentskills.io/specification](https://agentskills.io/specification)

## License

The marketplace catalog is MIT-licensed. Individual skills carry their own licenses — check each skill's `LICENSE` file.
