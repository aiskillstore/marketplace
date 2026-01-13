---
name: standards-extraction
description: "Extract coding standards and conventions from CONTRIBUTING.md, .editorconfig, linter configs. Use for onboarding and ensuring consistent contributions."
---

# Standards Extraction Skill

Extract coding standards, formatting rules, and contribution guidelines from project configuration files. Returns structured data about project conventions.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| INCLUDE_LINTER_RULES | true | Parse ESLint, Prettier, Ruff configs |
| INCLUDE_EDITOR_CONFIG | true | Parse .editorconfig |
| INCLUDE_GIT_HOOKS | true | Check for pre-commit, husky configs |
| OUTPUT_FORMAT | json | Output format: json, markdown, or toon |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order. Do not skip steps.

1. Check for CONTRIBUTING.md or similar guide files
2. Parse formatting configuration files
3. Parse linting configuration files
4. Check for git hooks and CI checks
5. Compile standards summary

## Red Flags - STOP and Reconsider

If you're about to:
- Assume formatting rules without checking config files
- Skip CONTRIBUTING.md because "it's probably standard"
- Infer conventions without evidence from configs
- Report rules that contradict actual config files

**STOP** -> Read the config files -> Extract actual rules -> Then report

## Workflow

### 1. Discover Standards Files

Check for these files (in order):

| File | Type | Purpose |
|------|------|---------|
| `CONTRIBUTING.md` | Markdown | Contribution guidelines |
| `CONTRIBUTING` | Text | Contribution guidelines |
| `docs/CONTRIBUTING.md` | Markdown | Contribution guidelines |
| `.github/CONTRIBUTING.md` | Markdown | Contribution guidelines |
| `.editorconfig` | INI | Editor formatting |
| `.prettierrc*` | JSON/YAML | Prettier config |
| `prettier.config.*` | JS/TS | Prettier config |
| `.eslintrc*` | JSON/YAML | ESLint config |
| `eslint.config.*` | JS/TS | ESLint flat config |
| `pyproject.toml` | TOML | Python tools (ruff, black, isort) |
| `.ruff.toml` | TOML | Ruff config |
| `.pre-commit-config.yaml` | YAML | Pre-commit hooks |
| `.husky/` | Directory | Git hooks |
| `.github/PULL_REQUEST_TEMPLATE.md` | Markdown | PR template |
| `.github/ISSUE_TEMPLATE/` | Directory | Issue templates |

### 2. Extract Contribution Guidelines

From CONTRIBUTING.md, extract:
- **Commit message format**: Conventional commits, gitmoji, etc.
- **Branch naming**: feature/, fix/, etc.
- **PR process**: Required reviewers, checks, etc.
- **Code style notes**: Any explicit guidance
- **Testing requirements**: What tests are required

### 3. Extract Formatting Rules

From .editorconfig:
```ini
[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

From Prettier config:
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "printWidth": 100
}
```

### 4. Extract Linting Rules

From ESLint:
- Key enabled/disabled rules
- Extended configs (airbnb, standard, etc.)
- Custom rules

From Ruff/Black (pyproject.toml):
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.black]
line-length = 88
```

### 5. Extract Git Hooks

From .pre-commit-config.yaml:
- Hooks that run on commit
- Required checks

From .husky/:
- Pre-commit scripts
- Pre-push scripts

### 6. Compile Output

```json
{
  "project_root": "/path/to/project",
  "extracted_at": "2025-12-21T12:00:00Z",
  "contribution_guidelines": {
    "source": "CONTRIBUTING.md",
    "commit_format": "conventional",
    "branch_naming": "type/description",
    "pr_requirements": ["tests", "review"],
    "notes": []
  },
  "formatting": {
    "indent_style": "space",
    "indent_size": 2,
    "line_length": 100,
    "quotes": "single",
    "semicolons": true,
    "trailing_commas": "es5",
    "sources": [".editorconfig", ".prettierrc"]
  },
  "linting": {
    "javascript": {
      "tool": "eslint",
      "extends": ["next/core-web-vitals"],
      "key_rules": {}
    },
    "python": {
      "tool": "ruff",
      "line_length": 88,
      "select": ["E", "F", "I"]
    }
  },
  "git_hooks": {
    "pre_commit": ["lint-staged", "prettier"],
    "pre_push": ["test"]
  },
  "ci_checks": {
    "source": ".github/workflows/",
    "checks": ["lint", "test", "build"]
  }
}
```

## Cookbook

### Parsing Configurations
- IF: Need to parse any config file
- THEN: Read and execute `./cookbook/config-parsing.md`

## Quick Reference

### Commit Format Detection

| Pattern in CONTRIBUTING.md | Format |
|---------------------------|--------|
| "Conventional Commits" | conventional |
| "feat:", "fix:", "chore:" | conventional |
| ":emoji:" or gitmoji | gitmoji |
| "JIRA-123" pattern | jira |
| No pattern found | freeform |

### Common Formatter Configs

| File | Tool |
|------|------|
| `.prettierrc*` | Prettier |
| `biome.json` | Biome |
| `.editorconfig` | EditorConfig |
| `dprint.json` | dprint |

### Common Linter Configs

| File | Tool |
|------|------|
| `.eslintrc*`, `eslint.config.*` | ESLint |
| `pyproject.toml [tool.ruff]` | Ruff |
| `pyproject.toml [tool.pylint]` | Pylint |
| `.golangci.yml` | golangci-lint |
| `clippy.toml` | Clippy (Rust) |

## Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "project_root": {"type": "string"},
    "extracted_at": {"type": "string", "format": "date-time"},
    "contribution_guidelines": {
      "type": "object",
      "properties": {
        "source": {"type": "string"},
        "commit_format": {"type": "string"},
        "branch_naming": {"type": "string"},
        "pr_requirements": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "array", "items": {"type": "string"}}
      }
    },
    "formatting": {
      "type": "object",
      "properties": {
        "indent_style": {"type": "string"},
        "indent_size": {"type": "integer"},
        "line_length": {"type": "integer"},
        "quotes": {"type": "string"},
        "semicolons": {"type": "boolean"},
        "sources": {"type": "array", "items": {"type": "string"}}
      }
    },
    "linting": {"type": "object"},
    "git_hooks": {"type": "object"},
    "ci_checks": {"type": "object"}
  }
}
```

## Integration

This skill is used by:
- `/ai-dev-kit:quickstart-codebase` - Onboarding workflow
- `lane-executor` - To follow project conventions
- Contribution validation - To check PR compliance
