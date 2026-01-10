---
name: module-scaffolder
description: Scaffolds new feature modules in DevPrep AI following the 6-folder architecture with proper TypeScript interfaces, path aliases, and quality standards. Use when creating new domains like 'analytics', 'notifications', or any new feature module.
allowed-tools: [Read, Write, Bash, Glob]
---

# Module Scaffolder

Automate creation of feature modules with proper structure, boilerplate files, and enforced quality standards.

---

## Auto-Triggers

Auto-triggered by keywords:
- "new module", "create module", "scaffold module"
- "new feature module", "add module"

---

## Quick Commands

```bash
# Create new module
./.claude/skills/module-scaffolder/scripts/create-module.sh <module-name>

# Add component to module
./.claude/skills/module-scaffolder/scripts/add-component.sh <module-name> <ComponentName>

# Validate module
./.claude/skills/module-scaffolder/scripts/validate-module.sh <module-name>
```

---

## Generated Structure

```
modules/<module-name>/
├── components/
│   ├── ExampleCard.tsx  # Starter component (rename/delete)
│   └── index.ts         # Barrel exports
├── hooks/
│   └── index.ts
├── utils/
│   └── index.ts
└── types.ts             # Module-specific types
```

**All generated files automatically follow DevPrep AI quality standards.**

---

## Usage Workflow

### 1. Creating a New Module

**Example:** Create analytics module

```bash
# 1. Scaffold
./scripts/create-module.sh analytics

# 2. Add components as needed
./scripts/add-component.sh analytics AnalyticsChart
./scripts/add-component.sh analytics AnalyticsSummary

# 3. Validate
./scripts/validate-module.sh analytics
```

**What happens:**
- Module directory created with proper structure
- Boilerplate files generated from templates
- TypeScript interfaces with I prefix
- Path aliases configured
- Quality standards enforced

### 2. Adding Components

```bash
./scripts/add-component.sh <module-name> <ComponentName>
```

**Result:**
- Component file generated with proper TypeScript patterns
- Barrel export (`index.ts`) automatically updated
- I prefix interface included
- Ready to implement logic

### 3. Validating Modules

```bash
./scripts/validate-module.sh <module-name>
```

**Checks:**
- Directory structure (6-folder architecture)
- File size limits (≤180 lines)
- Interface naming (I prefix)
- No `any` types
- Import patterns

---

## Integration

**Before scaffolding:** Use `brainstorming` skill to plan module design

**After scaffolding:**
- Use `trpc-scaffolder` to create API endpoints
- Use `quality-reviewer` to review code quality

---

## Documentation

Detailed references available in `references/`:

- `6-folder-architecture.md` - Where modules fit, structure rules
- `naming-conventions.md` - I prefix, PascalCase, camelCase rules
- `path-aliases.md` - Import patterns, @shared, @lib usage
- `quality-checklist.md` - Complete quality standards

**Examples:** See `examples/complete-module/` for fully structured reference module

---

## Troubleshooting

**Module name:** Use lowercase-with-hyphens (`analytics`, `user-profile`)

**Component name:** Use PascalCase (`AnalyticsChart`, `UserCard`)

**Path errors:** Ensure running from project root or use absolute paths

---

## Templates

All templates in `templates/` directory are automatically used by scripts. Modify templates to customize generated code patterns.
