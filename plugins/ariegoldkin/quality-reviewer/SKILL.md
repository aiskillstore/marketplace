---
name: quality-reviewer
description: Automatically reviews DevPrep AI code for quality standards including ESLint compliance, TypeScript strict mode, 180-line file limits, complexity under 15, proper naming conventions, import patterns, and architectural compliance with the 6-folder structure
allowed-tools: [Read, Bash, Grep, Glob]
---

# Quality Reviewer

Automatically enforces DevPrep AI code quality standards during development.

---

## Auto-Triggers

Auto-triggered by keywords:
- "review", "check", "validate", "verify"
- "lint", "quality", "standards"
- "type check", "typescript"
- "complexity", "file size", "architecture"

---

## Quick Standards

### File Limits
- **≤180 lines** per file (code only)
- **Complexity ≤15** per function
- **≤50 lines** per function
- **≤4 parameters** per function

### TypeScript
- Strict mode enabled
- No `any` types
- Interfaces: `I` prefix (e.g., `IButtonProps`)
- Type imports: `import type { ... }`

### Naming
- Interfaces: `IUserProfile`, `IButtonProps`
- Types: `QuestionType`, `Difficulty`
- Functions: `camelCase`
- Components: `PascalCase`

### Imports
Use path aliases:
```typescript
@shared/ui/button      // ✅ Correct
@modules/practice/*    // ✅ Correct
@lib/trpc/client       // ✅ Correct
@store/hooks           // ✅ Correct

../../../shared/ui/*   // ❌ Wrong
```

### Architecture (6-Folder)
```
app/      Routes only
modules/  Features (practice, assessment, results, profile, questions, home)
shared/   Cross-cutting (ui, components, hooks, utils)
lib/      Integrations (trpc, claude)
store/    Zustand state
styles/   Design system
```

---

## Run Checks

### Single Check
```bash
# Target specific issues
./.claude/skills/quality-reviewer/scripts/check-file-size.sh
./.claude/skills/quality-reviewer/scripts/check-complexity.sh
./.claude/skills/quality-reviewer/scripts/check-imports.sh
./.claude/skills/quality-reviewer/scripts/check-architecture.sh
./.claude/skills/quality-reviewer/scripts/check-naming.sh
```

### Full Review
```bash
# Run all 7 checks at once
./.claude/skills/quality-reviewer/scripts/full-review.sh
```

Checks: file size → complexity → imports → architecture → naming → ESLint → TypeScript

---

## Common Fixes

### Interface Missing 'I' Prefix
```typescript
interface ButtonProps { }  // ❌
interface IButtonProps { } // ✅
```

### Direct React Import
```typescript
import { ReactElement } from 'react';      // ❌
import type { ReactElement } from 'react'; // ✅
```

### Relative Import
```typescript
import { Button } from '../../../shared/ui/button'; // ❌
import { Button } from '@shared/ui/button';         // ✅
```

### Using 'any'
```typescript
const data: any = fetchData();    // ❌
const data: IUserData = fetchData(); // ✅
```

### File Too Large
Split into:
- `Component.tsx` - UI only
- `hooks.ts` - Logic
- `types.ts` - Types
- `utils.ts` - Helpers

See: `examples/refactor-after/`

### Complexity Too High (>15)
```typescript
// ❌ Before: Nested ifs (complexity 18)
if (user.role === 'admin') {
  if (user.isActive) {
    if (user.permissions.includes('write')) {
      // do something
    }
  }
}

// ✅ After: Early returns (complexity 3)
if (!user.role === 'admin') return;
if (!user.isActive) return;
if (!user.permissions.includes('write')) return;
// do something
```

**Quick fixes:**
- Extract conditionals → separate functions
- Use early returns → avoid nesting
- Replace switch → lookup objects `const MAP = { key: 'value' };`

---

## When to Load Additional Docs

**SKILL.md is self-sufficient for:**
- Running checks (all scripts listed above)
- Simple fixes (naming, imports, basic refactoring)
- Understanding standards

**Load additional docs only when needed:**

| Need | Load | Lines |
|------|------|-------|
| File splitting strategies | `examples/refactor-after/` | ~256 |
| Complexity reduction tactics | `docs/standards.md` (lines 75-163) | ~88 |
| Architecture patterns | `docs/standards.md` (lines 224-280) | ~56 |
| Type safety patterns | `docs/standards.md` (lines 283-348) | ~65 |
| Deep-dive on any violation | `docs/standards.md` (full file) | ~370 |

**Code examples:**
- ✅ Perfect: `examples/good-code.tsx`
- ❌ Violations: `examples/bad-code.tsx`
- 🔄 Refactoring: `examples/refactor-after/`

**Full project standards:** `Docs/code-standards.md`

---

**Version:** 1.1.0 (Optimized) | **Updated:** October 2025
**Optimization**: 31% smaller, 52% fewer tokens for typical usage

**Note**: Example files use `// @ts-nocheck` and `/* eslint-disable */` directives to suppress IDE warnings, since they demonstrate intentional violations or reference non-existent paths for educational purposes. They are also excluded from build-time TypeScript compilation via `frontend/tsconfig.json`.
