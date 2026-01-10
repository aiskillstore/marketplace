# tRPC Scaffolder Skill

Automates creation of type-safe tRPC routers, procedures, and Zod schemas for DevPrep AI.

## What It Does

- 🏗️ **Scaffold Routers**: Create new router files with correct structure
- ⚡ **Add Procedures**: Add query/mutation procedures to existing routers
- 🛡️ **Generate Schemas**: Create Zod validation schemas with type inference
- ✅ **Validate Setup**: Check router registration and schema compliance

## Quick Start

```bash
# Create a new router
./.claude/skills/trpc-scaffolder/scripts/create-router.sh user

# Add a procedure to existing router
./.claude/skills/trpc-scaffolder/scripts/add-procedure.sh ai getHints

# Create a schema file
./.claude/skills/trpc-scaffolder/scripts/create-schema.sh hint

# Validate your tRPC setup
./.claude/skills/trpc-scaffolder/scripts/validate-trpc.sh
```

## Files

- **SKILL.md** - Complete self-sufficient guide (read this first)
- **scripts/** - Automation scripts for scaffolding
- **templates/** - Router, schema, and procedure templates
- **docs/** - Extended patterns and best practices
- **examples/** - Annotated examples of good code

## When to Use

Trigger keywords: "new endpoint", "tRPC", "API procedure", "new router", "Zod schema"

## Pattern

Follows the same structure as `quality-reviewer` skill:
- Self-contained SKILL.md covers 80% of use cases
- Automated scripts do the heavy lifting
- Templates based on existing DevPrep AI patterns
- Progressive disclosure for advanced topics

## Time Saved

**~20-30 minutes** per new tRPC endpoint (router + schemas + registration + validation)

---

## Token Economics

| Action | Files Loaded | Tokens | Use Case |
|--------|-------------|--------|----------|
| **Auto-trigger** | SKILL.md | ~1,500 | Most scaffolding tasks |
| **Advanced patterns** | + trpc-patterns.md | ~3,200 | Complex procedures & error handling |
| **Full tutorial** | + quick-start-guide.md | ~2,800 | Learning tRPC from scratch |
| **Complete exploration** | All docs | ~4,500 | Deep understanding |

**Design benefit:** ~55% token savings vs monolithic file

**Pattern:** Minimal core (SKILL.md) + progressive disclosure for advanced topics

---

**Version:** 1.0.0 | **Created:** October 2025
