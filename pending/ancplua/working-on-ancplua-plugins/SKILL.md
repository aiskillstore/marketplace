---
name: working-on-ancplua-plugins
description: Primary instruction manual for working within the ancplua-claude-plugins monorepo. Use when creating, modifying, or debugging plugins in this repository.
---

# Skill: working-on-ancplua-plugins

## Purpose

This is the **primary instruction manual** for an agent working within the
`ancplua-claude-plugins` monorepo. It defines the mandatory conventions, architectural patterns,
and workflows required to contribute safely and effectively.

## When to Use

Use this skill when:

- **Creating a new plugin**: Follow the `publishing.md` guide to scaffold correctly.
- **Modifying existing plugins**: Check `conventions.md` to ensure you don't break architecture.
- **Debugging issues**: Use `testing.md` to verify JSON syntax, permissions, and paths.
- **Preparing a PR**: Run the validation commands listed in `testing.md`.

## Reference Library

| Resource | Description |
|----------|-------------|
| [Conventions](./references/conventions.md) | Critical rules, naming, directory layout, Git flow |
| [Publishing](./references/publishing.md) | Step-by-step guide to create and release plugins |
| [Testing](./references/testing.md) | Validation commands and debugging steps |

## Official Documentation

| Topic | Link |
|-------|------|
| Plugins | [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) |
| Skills | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| Hooks | [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) |
| Marketplaces | [code.claude.com/docs/en/plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) |

## Quick Actions

**Validate everything:**

```bash
./tooling/scripts/local-validate.sh
```

**Check marketplace sync:**

```bash
./tooling/scripts/sync-marketplace.sh
```

**Validate single plugin:**

```bash
claude plugin validate plugins/<plugin-name>
```

## Repo Layout

```text
ancplua-claude-plugins/
├── plugins/              # Individual plugins live here
│   └── <plugin-name>/
│       ├── .claude-plugin/plugin.json
│       ├── skills/
│       ├── commands/
│       ├── agents/
│       ├── hooks/
│       └── README.md
├── agents/               # Repo-level Agent SDK experiments
├── skills/               # Repo-level shared skills (like this one)
├── .claude-plugin/       # Marketplace manifest
├── tooling/              # Validation scripts, templates
└── docs/                 # Architecture, specs, ADRs
```
