# ddd-check

DDD compliance check skill for Claude Code. Validates Java projects against Domain-Driven Design layer rules.

## Install

```bash
npx skillstore add bookiosk/ddd-check
```

Or add to `.claude/settings.json`:

```json
{
  "skills": {
    "ddd-check": {
      "path": "ddd-check-skill/SKILL.md"
    }
  }
}
```

## Usage

```
# Incremental — check changed files only
/ddd-check

# Full — audit entire project
/ddd-check-full
```

## Modes

| Mode | Scope | Speed | Use Case |
|---|---|---|---|
| Incremental | git diff Java files | Fast | Pre-commit, PR review |
| Full | All Java files | Slow | Architecture review, pre-release |

## What It Checks

- Layer isolation (no wrong cross-layer imports)
- Base class usage (aggregate, entity, value object)
- Naming conventions (Cmd, Qry, Exe, ExtPt, etc.)
- Dependency direction (domain → infrastructure = CRITICAL)
- Identity protection (setId must be protected)
- Anti-patterns (anemic model, service overuse)

## File Layout

```
ddd-check-skill/
├── SKILL.md                  # Main skill definition
├── rules/                    # DDD layer rules (checked against code)
│   ├── domain-layer.md
│   ├── application-layer.md
│   ├── adaptor-layer.md
│   ├── infrastructure-layer.md
│   ├── client-layer.md
│   ├── model-layer.md
│   └── anti-patterns.md
├── references/               # Education and onboarding (not checked)
│   ├── overview.md
│   ├── base-classes-reference.md
│   ├── anemic-vs-ddd.md
│   └── quick-start-tutorial.md
└── README.md
```

## License

Apache 2.0 — see [LICENSE](LICENSE)
