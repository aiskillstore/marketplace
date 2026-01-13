# Quality Reviewer Skill

**Version:** 1.0.0
**Status:** Production Ready
**Auto-triggers:** Code review keywords

---

## Overview

Automatically enforces DevPrep AI code quality standards through executable scripts and on-demand documentation. This skill provides instant feedback on code violations without requiring manual invocation.

---

## Structure

```
quality-reviewer/
├── SKILL.md (155 lines)           Core skill loaded automatically
├── README.md                      This file
│
├── docs/                          Loaded on-demand when needed
│   ├── standards.md (284 lines)   Deep-dive violation fixes
│   ├── quickstart.md (252 lines)  Workflow patterns
│   └── reference.md (74 lines)    External links
│
├── examples/                      Referenced, not loaded
│   ├── good-code.tsx              Perfect example following all standards
│   ├── bad-code.tsx               Common violations
│   └── refactor-after/            3-file split pattern
│       ├── Component.tsx          UI separation
│       ├── hooks.ts               Logic extraction
│       └── types.ts               Type definitions
│
└── scripts/                       Executed directly via Bash
    ├── check-file-size.sh         Verify ≤180 lines
    ├── check-complexity.sh        Verify ≤15 complexity
    ├── check-imports.sh           Validate path aliases
    ├── check-architecture.sh      Verify 6-folder structure
    ├── check-naming.sh            Check interface 'I' prefix
    └── full-review.sh             Run all 7 checks
```

---

## How It Works

### Automatic Loading
When Claude detects quality-related keywords ("review", "lint", "check"), it automatically loads **SKILL.md** (~1,200 tokens) to understand:
- What standards to check
- Which scripts to run
- Where to find detailed help

### On-Demand Documentation
When you ask "how to fix?", Claude reads the appropriate doc file:
- **standards.md** - Detailed violation explanations
- **quickstart.md** - Workflow patterns
- **reference.md** - External resources

### Example Files
Referenced by path only, never loaded into context. You can read them manually or Claude can read them when showing examples.

### Scripts
Executed directly via Bash tool. Return standardized output:
```
✅ Check passed
❌ Check failed with violations list
💡 Fix suggestions
```

---

## Usage

### Auto-Triggered
```
You: "Review this code"
→ Claude loads SKILL.md
→ Runs appropriate checks
→ Reports violations

You: "How do I fix this?"
→ Claude reads docs/standards.md
→ Shows detailed fix with examples
```

### Manual Script Execution
```bash
# Single check
./.claude/skills/quality-reviewer/scripts/check-file-size.sh

# Full review (all 7 checks)
./.claude/skills/quality-reviewer/scripts/full-review.sh
```

---

## Standards Enforced

### File Limits
- **≤180 lines** per file (code only)
- **Complexity ≤15** per function
- **≤50 lines** per function
- **≤4 parameters** per function

### TypeScript
- Strict mode enabled
- No `any` types
- Interfaces must have `I` prefix
- Type-only imports: `import type { ... }`

### Imports
- Use path aliases (`@shared/`, `@modules/`, `@lib/`, `@store`)
- No deep relative imports (`../../../`)

### Architecture
- 6-folder structure: `app/`, `modules/`, `shared/`, `lib/`, `store/`, `styles/`
- Files must be in correct folder
- No invalid top-level directories

---

## Token Economics

| Action | Files Loaded | Tokens | Use Case |
|--------|-------------|--------|----------|
| **Auto-trigger** | SKILL.md | ~1,200 | Most checks |
| **Detailed help** | + standards.md | ~3,000 | Complex fixes |
| **Workflow guide** | + quickstart.md | ~2,500 | Multi-step scenarios |
| **Full exploration** | All docs | ~5,000 | Complete understanding |

**Design:** Minimal core (SKILL.md) + on-demand details = 60% token savings vs monolithic file

---

## Integration

### Git Hooks
```bash
# .husky/pre-commit
./.claude/skills/quality-reviewer/scripts/full-review.sh || exit 1
```

### CI/CD
```yaml
# GitHub Actions
- run: ./.claude/skills/quality-reviewer/scripts/full-review.sh
```

### VS Code
```json
// .vscode/tasks.json
{
  "label": "Quality Review",
  "command": "./.claude/skills/quality-reviewer/scripts/full-review.sh"
}
```

---

## Maintenance

### Adding New Checks
1. Create script in `scripts/`
2. Make executable: `chmod +x scripts/new-check.sh`
3. Add to `full-review.sh`
4. Document in `SKILL.md`

### Updating Standards
1. **Quick reference changes** → Update `SKILL.md`
2. **Detailed explanations** → Update `docs/standards.md`
3. **Workflow changes** → Update `docs/quickstart.md`
4. **New examples** → Add to `examples/`

### Testing Changes
```bash
# Test single script
./scripts/check-file-size.sh

# Test full review
./scripts/full-review.sh

# Verify token count
wc -l SKILL.md  # Should stay ~155 lines
```

---

## Related Documentation

- **Project standards**: `Docs/code-standards.md`
- **Architecture guide**: `Docs/technical-architecture.md`
- **Developer guide**: `Docs/developer-guide.md`
- **Design system**: `Docs/design-system.md`

---

## Changelog

### v1.0.0 (October 2025)
- Initial release
- 6 automated check scripts
- 4 example files (good, bad, refactor suite)
- 3 documentation files (standards, quickstart, reference)
- Auto-trigger capability
- Optimized for minimal token usage

---

**Maintained by:** DevPrep AI Team
**License:** MIT
**Last Updated:** October 2025
