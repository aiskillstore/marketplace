---
name: skills-cli
description: Use when users ask to discover, install, list, check, update, remove, back up, restore, sync, or initialize Agent Skills, mention `bunx skills`, `npx skills`, `skills.sh`, or `skills-lock.json`, ask "find a skill for X", or want help extending agent capabilities with installable skills.
---

# Skills CLI

Use this skill to help users work with the open Agent Skills ecosystem through the `skills` CLI.

## Overview

The `skills` CLI is the package manager for installable Agent Skills. Use it to discover skills, install them with the right flags, and manage them after installation.

Examples below use `bunx skills`, but `npx skills` is the same workflow if Bun is not available in the user's environment.

Always prefer the current CLI syntax:

```bash
bunx skills add <source> --skill <name>
```

Do not use older `owner/repo@skill-name` examples.

## When to Use

Use this skill when the user:

- asks "find a skill for X", "is there a skill for X", or "how do I do X" and X sounds like a reusable workflow
- asks "can you do X" and X sounds like a specialized capability that may already exist as a skill
- wants help with `bunx skills`, `npx skills`, `skills.sh`, skill package installation, or `skills-lock.json`
- wants to install a skill for a specific agent such as Codex or OpenCode
- wants to list, check, update, remove, restore, sync, back up, or initialize installed skills
- wants help searching for workflows, tools, templates, or domain-specific capabilities such as design, testing, deployment, documentation, or code review

Do not use this skill when the user already has a local skill and wants help writing or improving its contents. In that case, use a skill-authoring workflow instead.

## Discovery Workflow

When a user needs a skill, follow this sequence:

1. Identify the domain and task.
   Examples: React performance, PR review, changelog generation, PDF extraction.
   Also judge whether the task is common enough that a reusable skill is likely to exist.
2. Check [skills.sh](https://skills.sh/) first.
   Prefer well-known, well-installed skills when the domain is already covered there.
3. If the leaderboard does not clearly answer the need, search with:

```bash
bunx skills find <query>
```

1. Verify quality before recommending anything:
   - install count: prefer skills with 1K+ installs and be cautious with anything under 100
   - source reputation: prefer official or well-established maintainers such as `openai`, `anthropics`, `microsoft`, or similarly trusted publishers
   - repository quality: check the source repository and treat skills from repos with fewer than 100 stars skeptically
2. Present the options clearly.
   Include the skill name, what it helps with, the install count and source, why it looks trustworthy, the install command, and a link to learn more on `skills.sh`.
3. Offer installation help if the user wants to proceed.
4. If nothing fits, say so directly, help with the task using your general capabilities, and mention that the user can create their own package with `bunx skills init`.

## Installation Quick Reference

### Common sources

```bash
# GitHub shorthand
bunx skills add xixu-me/skills

# Full GitHub URL
bunx skills add https://github.com/xixu-me/skills

# Direct path to one skill inside a repo
bunx skills add https://github.com/xixu-me/skills/tree/main/skills/skills-cli

# GitLab URL
bunx skills add https://gitlab.com/org/repo

# Any git URL
bunx skills add git@github.com:owner/repo.git

# Local package path
bunx skills add ./my-local-skills
```

### Common install patterns

```bash
# List skills in a package without installing
bunx skills add <source> --list

# Install one skill
bunx skills add <source> --skill skills-cli

# Install multiple skills
bunx skills add <source> --skill pr-review --skill commit

# Install globally
bunx skills add <source> --skill skills-cli -g -y

# Install to a specific agent
bunx skills add <source> --skill skills-cli -a codex -y

# Install all skills to all agents
bunx skills add <source> --all

# Install all skills to one agent
bunx skills add <source> --skill '*' -a codex -y

# Copy files instead of symlinking
bunx skills add <source> --skill skills-cli -a codex --copy -y
```

### Installation methods

When the user is choosing how to install:

- symlink is the default and usually the best choice because updates stay centralized
- `--copy` creates independent copies and is the fallback when symlinks are unsupported or inconvenient

If the user only asks to install a skill, prefer the default symlink workflow unless they mention CI packaging, portability, filesystem restrictions, or explicitly ask for copies.

### Important flags

| Flag                  | Use                                            |
| --------------------- | ---------------------------------------------- |
| `--skill <name>`      | install one or more named skills               |
| `-a, --agent <agent>` | target specific agents such as `codex`         |
| `-g, --global`        | install at user scope instead of project scope |
| `-y, --yes`           | skip prompts                                   |
| `--list`              | list available skills in a package             |
| `--copy`              | copy instead of symlink                        |
| `--all`               | shorthand for all skills to all agents         |

## Managing Installed Skills

Use these commands for ongoing maintenance:

```bash
# List installed skills
bunx skills ls
bunx skills ls -g
bunx skills ls -a codex
bunx skills ls --json

# Check for updates
bunx skills check

# Update installed skills
bunx skills update

# Remove installed skills
bunx skills remove my-skill
bunx skills remove my-skill -a codex
bunx skills remove -g my-skill
bunx skills remove --all

# Initialize a new skill package
bunx skills init
bunx skills init my-skill

# Restore from skills-lock.json
bunx skills experimental_install

# Sync node_modules skills into agent directories
bunx skills experimental_sync
bunx skills experimental_sync -a codex -y
```

When the user asks to initialize a skill, explain whether they want:

- `bunx skills init` to create `SKILL.md` in the current directory
- `bunx skills init <name>` to create a new subdirectory containing `SKILL.md`

## Related Tool: Skills Vault

If the user wants declarative backup and restore of installed skills across machines or teams, use [Skills Vault](https://github.com/xixu-me/skills-vault).

Skills Vault is a separate CLI companion for the `skills` ecosystem. It is not a `skills add` installable skill source. Use it when the user wants to snapshot installed skills into a manifest, preview restore commands, or reproduce the same setup elsewhere.

Common companion commands:

```bash
# Back up installed skills into skvlt.yaml
bunx skvlt backup

# Preview a restore
bunx skvlt restore --dry-run

# Restore everything from the manifest
bunx skvlt restore --all

# Diagnose the local environment
bunx skvlt doctor
```

Prefer this tool over `skills experimental_*` when the user explicitly wants a portable manifest workflow, cross-machine backup and restore, or team-sharing of installed skill setups.

## Recommendation Format

When recommending a skill, keep the answer concrete and installable.

Use a structure like this:

```text
I found a skill that should fit.

Skill: <skill-name>
Why it matches: <one sentence>
Source: <owner/repo or URL>
Quality check: <install count / source reputation / repository confidence note>
Install:
bunx skills add <source> --skill <skill-name> [optional flags]
Learn more: https://skills.sh/<publisher>/<package>/<skill-name>

If you want, I can install it for <agent-or-scope>.
```

If the user mentions a target agent or scope, include it in the command. Examples:

```bash
bunx skills add <source> --skill <skill-name> -a codex -y
bunx skills add <source> --skill <skill-name> -g -y
```

Example:

```text
I found a skill that might help.

Skill: screenshot
Why it matches: it focuses on OS-level desktop and window screenshot capture.
Source: openai/skills
Quality check: high install volume, trusted publisher, and a widely used source repository.
Install:
bunx skills add openai/skills --skill screenshot
Learn more: https://skills.sh/openai/skills/screenshot
```

## Common Skill Categories

When the user's wording is vague, map it to likely categories:

| Category        | Example queries                                    |
| --------------- | -------------------------------------------------- |
| Web Development | `react`, `nextjs`, `typescript`, `css`, `tailwind` |
| Testing         | `testing`, `jest`, `playwright`, `e2e`             |
| DevOps          | `deploy`, `docker`, `kubernetes`, `ci-cd`          |
| Documentation   | `docs`, `readme`, `changelog`, `api-docs`          |
| Code Quality    | `review`, `lint`, `refactor`, `best-practices`     |
| Design          | `ui`, `ux`, `design-system`, `accessibility`       |
| Productivity    | `workflow`, `automation`, `git`                    |

## Search Tips

- Use specific keywords. `react testing` is better than just `testing`.
- Try alternative terms. If `deploy` fails, try `deployment` or `ci-cd`.
- Check popular sources first. Many strong skills come from established publishers.
- If the first search is too broad, narrow by domain plus task.

## Common Mistakes

- Recommending a skill from search results without checking whether it looks established.
- Forgetting to specify `-a <agent>` when the user asked for one particular agent.
- Treating `bunx skills find --help` like a real help command. Use `bunx skills --help` for command help instead.
- Assuming no skill exists after one weak search term. Try a more specific or adjacent query first.

## Troubleshooting

If the user hits an error or confusing result:

- "No skills found" - suggest a better query, check [skills.sh](https://skills.sh/), or help directly and mention `bunx skills init`
- interactive prompts in automation or CI - add `-y`
- wrong installation scope - switch between project install and `-g`
- symlink issues - retry with `--copy`
- uncertainty about available package contents - run `bunx skills add <source> --list`
- uncertainty about installed state - run `bunx skills ls` or `bunx skills ls --json`
- portable backup or restore across machines - mention [Skills Vault](https://github.com/xixu-me/skills-vault) and its `backup` / `restore --dry-run` workflow

When you are unsure about exact flags, use:

```bash
bunx skills --help
```
