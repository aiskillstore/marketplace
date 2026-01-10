# SnowTower Project Structure Reference

Quick reference for the maintainer skill.

## Directory Layout

```
snowtower/
├── .claude/                    # Claude Code configuration
│   ├── skills/                 # Skills (model-invoked capabilities)
│   │   └── snowtower-maintainer/
│   ├── agents/                 # Agent definitions
│   └── patterns/               # Reusable patterns
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD workflows
│   │   ├── ci.yml             # PR validation
│   │   ├── labeler.yml        # Auto-labeling
│   │   ├── changelog.yml      # Changelog generation
│   │   └── release.yml        # Release automation
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── snowddl/                    # SnowDDL YAML configurations
│   ├── user.yaml              # User accounts
│   ├── business_role.yaml     # Business roles
│   ├── tech_role.yaml         # Technical roles
│   ├── warehouse.yaml         # Warehouses
│   ├── *_policy.yaml          # Security policies
│   └── {DATABASE}/            # Database-specific configs
├── src/                        # Python source code
│   ├── snowddl_core/          # OOP framework
│   ├── user_management/       # User lifecycle
│   ├── web/                   # Streamlit apps
│   └── management_cli.py      # CLI entry points
├── scripts/                    # Standalone scripts
├── tests/                      # Test suite
├── docs/                       # Documentation
│   ├── guide/                 # User guides
│   ├── agents/                # Agent documentation
│   └── releases/              # Release documentation
├── pyproject.toml             # Project configuration
├── README.md                  # Main documentation
└── CLAUDE.md                  # Claude Code instructions
```

## Key Files to Monitor

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `README.md` | Main project documentation | After features/releases |
| `CLAUDE.md` | Claude Code instructions | When patterns change |
| `pyproject.toml` | Commands and dependencies | When adding commands |
| `.claude/agents/*.md` | Agent definitions | When capabilities change |
| `docs/guide/*.md` | User guides | When workflows change |

## Current Statistics (Update These)

```yaml
# Last updated: 2024-XX-XX
users: ~13
databases: ~6
warehouses: ~8
agents: ~20+
workflows: 4
```

## Maintenance Schedule

- **Weekly**: Check for broken links, outdated statistics
- **Per Release**: Full documentation audit
- **Per Feature**: Update relevant docs and README
- **Quarterly**: Agent consolidation review
