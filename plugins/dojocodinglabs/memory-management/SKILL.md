---
name: memory-management
description: Context tracking and decision logging patterns for intentional memory management in Claude Code Waypoint Plugin. Use when you need to remember user preferences, track decisions, capture context across sessions, learn from corrections, or maintain project-specific knowledge. Covers when to persist context, how to track decisions, context boundaries, storage mechanisms, and memory refresh strategies.
---

# Memory Management Skill

## Purpose

Guide Claude Code to intentionally capture, store, and use context, decisions, and preferences across sessions, enabling true "memory" that survives context resets and improves over time.

## When to Use This Skill

Automatically activates when you mention:
- Remembering user preferences or choices
- Tracking decisions made during development
- Capturing important context
- Learning from user corrections
- Persisting project-specific knowledge
- Memory that survives session resets

## The Problem: Context Loss

**Without intentional memory**:
- ❌ Same mistakes repeated across sessions
- ❌ User has to re-explain preferences every time
- ❌ Important decisions forgotten after context reset
- ❌ No learning from corrections
- ❌ Starting from scratch each session

**With intentional memory**:
- ✅ Preferences remembered and auto-applied
- ✅ Decisions documented and retrievable
- ✅ Context persists across sessions
- ✅ Learn and adapt from corrections
- ✅ Continuous improvement over time

---

## Core Principles

### 1. Be Selective

**Track signal, not noise**:
- ✅ User explicitly states preference ("always use X")
- ✅ User corrects same pattern 2+ times
- ✅ Important architectural decisions
- ✅ Project-specific conventions
- ❌ One-time experiments
- ❌ Formatting preferences (use linter config)
- ❌ Temporary changes
- ❌ Information already in codebase

### 2. Be Transparent

**User should always know what's stored**:
- Store in visible location (`.claude/memory/`)
- Use human-readable format (JSON with comments)
- Provide commands to view memory (`/show-memory`)
- Log when memory is created/updated
- Allow user to clear memory anytime

### 3. Be Intentional

**Only capture what adds value**:
- Preferences that save time
- Decisions that provide context
- Patterns that prevent mistakes
- Knowledge that's hard to rediscover

### 4. Be Respectful

**Never store sensitive data**:
- ❌ API keys, tokens, credentials
- ❌ Personal information (unless necessary)
- ❌ Private repository URLs with tokens
- ❌ Business-sensitive logic
- ✅ Preferences, patterns, conventions
- ✅ Architecture decisions, rationale

---

## What to Remember

### User Preferences

**Examples**:
- Naming conventions (camelCase vs. snake_case)
- Import style (named vs. default)
- Error handling approach (try/catch vs. error boundaries)
- State management choice (Context vs. Zustand vs. TanStack Query)
- Component structure preferences

**Storage location**: `.claude/memory/{skill-name}/preferences.json`

**Example**:
```json
{
  "naming": {
    "convention": "camelCase",
    "learned_from": "user_correction",
    "correction_count": 2,
    "examples": [
      "userId (not user_id)",
      "createdAt (not created_at)"
    ],
    "confidence": "high",
    "last_updated": "2025-01-15T10:30:00Z"
  }
}
```

### Architectural Decisions

**Examples**:
- Why a specific pattern was chosen
- Alternatives considered and rejected
- Trade-offs and constraints
- Future considerations

**Storage location**: `.claude/memory/project/decisions.json`

**Example**:
```json
{
  "decisions": [
    {
      "id": "auth-jwt-2025-01-15",
      "date": "2025-01-15",
      "decision": "Use JWT authentication instead of sessions",
      "rationale": "Need stateless auth for mobile apps",
      "alternatives_considered": [
        "Session-based auth (rejected: not stateless)",
        "OAuth only (rejected: need custom auth flow)"
      ],
      "impact": "Requires database migration for refresh tokens",
      "files_affected": [
        "lib/supabase/auth.ts",
        "app/api/auth/**/*.ts"
      ]
    }
  ]
}
```

### Correction Patterns

**Examples**:
- User repeatedly corrects same mistake
- User provides specific guidance
- User rejects suggested approach

**Storage location**: `.claude/memory/{skill-name}/corrections.json`

**Example**:
```json
{
  "corrections": [
    {
      "pattern": "Import style",
      "count": 3,
      "first_seen": "2025-01-10T09:00:00Z",
      "last_seen": "2025-01-15T14:30:00Z",
      "examples": [
        "import { Component } from 'lib' ✓",
        "import Component from 'lib' ✗"
      ],
      "action": "Always use named imports",
      "confidence": "high"
    }
  ]
}
```

### Project Knowledge

**Examples**:
- Tech stack and versions
- Project structure and organization
- Integration points (APIs, databases)
- Deployment patterns

**Storage location**: `.claude/memory/project/knowledge.json`

**Example**:
```json
{
  "tech_stack": {
    "frontend": "Next.js 14, React 19, shadcn/ui, Tailwind",
    "backend": "Supabase Edge Functions, PostgreSQL",
    "deployment": "Vercel (frontend), Supabase (backend)",
    "last_verified": "2025-01-15"
  },
  "structure": {
    "components": "app/components/",
    "pages": "app/(routes)/",
    "api": "app/api/",
    "supabase_functions": "supabase/functions/"
  }
}
```

---

## When to Persist

### Immediate Persistence

Capture immediately when:
- ✅ User explicitly says "always" or "never"
- ✅ User provides architectural decision with rationale
- ✅ User corrects same pattern for the 2nd time
- ✅ User defines project-specific convention

### Deferred Persistence

Capture after confirmation when:
- User provides preference once (wait for second instance)
- Pattern seems emerging but not confirmed
- Decision has significant impact (confirm first)

### Never Persist

Don't capture:
- ❌ Experimental or temporary changes
- ❌ Information already in code/config
- ❌ Generic best practices (not project-specific)
- ❌ Sensitive data of any kind

---

## Storage Patterns

### Directory Structure

```
.claude/memory/
├── project/
│   ├── knowledge.json          # Tech stack, structure
│   ├── decisions.json          # Architectural decisions
│   └── context.json            # Current feature context
├── {skill-name}/
│   ├── preferences.json        # User preferences for this skill
│   ├── corrections.json        # User corrections tracked
│   └── learned_patterns.json  # Patterns learned over time
└── .gitignore                  # Don't commit sensitive memory
```

### File Format

Use JSON with clear structure:

```json
{
  "version": "1.0",
  "created": "2025-01-15T10:00:00Z",
  "last_updated": "2025-01-15T14:30:00Z",
  "data": {
    // Actual content
  }
}
```

### Schema Example

```typescript
interface MemoryEntry {
  version: string;
  created: string;           // ISO timestamp
  last_updated: string;      // ISO timestamp
  expires?: string;          // Optional expiry
  confidence: 'low' | 'medium' | 'high';
  source: 'user_stated' | 'user_correction' | 'inferred';
  data: Record<string, any>;
}
```

---

## Decision Tracking

### What Makes a Good Decision Log

**Include**:
1. **What**: What was decided
2. **Why**: Rationale and reasoning
3. **When**: Date/time
4. **Alternatives**: What else was considered
5. **Impact**: Files affected, breaking changes
6. **Context**: Current constraints/requirements

**Example Template**:
```markdown
## Decision: [Short Title]

**Date**: 2025-01-15
**Context**: [What problem were we solving?]

**Decision**: [What we decided to do]

**Rationale**:
- [Key reason 1]
- [Key reason 2]

**Alternatives Considered**:
- **Option A**: [Why rejected]
- **Option B**: [Why rejected]

**Impact**:
- Files: [List of affected files]
- Breaking: [Yes/No - details]
- Migration: [What needs to change]

**Trade-offs**:
- ✅ Pro: [Benefit]
- ❌ Con: [Drawback]
```

### When to Log Decisions

**Always log**:
- ✅ Architecture changes (auth, state management, routing)
- ✅ Technology choices (new library, framework change)
- ✅ Breaking changes to APIs or database
- ✅ Deviation from established patterns

**Optional logging**:
- Component structure choices
- File organization changes
- Refactoring approaches

**Don't log**:
- Bug fixes (unless revealing design issue)
- Minor implementation details
- Routine tasks

---

## Correction Tracking

### Detecting Corrections

User corrections happen when:
1. User explicitly corrects Claude's output
2. User provides same feedback multiple times
3. User rejects suggested approach and provides alternative

### Tracking Pattern

```typescript
interface Correction {
  pattern: string;                    // What's being corrected
  count: number;                      // How many times
  first_seen: string;                 // ISO timestamp
  last_seen: string;                  // ISO timestamp
  examples: string[];                 // Examples of correct/incorrect
  action: string;                     // What to do instead
  threshold: number;                  // Apply after N corrections
  confidence: 'low' | 'medium' | 'high';
}
```

### Auto-Application

After threshold corrections (typically 2-3):
1. Store preference as "high confidence"
2. Auto-apply in future
3. Notify user: "📚 Learned preference from your corrections"
4. Provide way to reset if incorrect

### Example Workflow

```markdown
## First Correction
User: "Use named imports, not default"
Action: Note correction, don't apply yet

## Second Correction (same pattern)
User: "Again, please use named imports"
Action: Log pattern, apply going forward
Notify: "📚 Learned: Always use named imports"

## Future Usage
Claude automatically uses named imports
User can reset with: /clear-memory import-style
```

---

## Context Boundaries

### What Belongs in Memory vs. Code

**In Memory** (`.claude/memory/`):
- Preferences not in code/config
- Decision rationale (the "why")
- Correction patterns
- Temporary feature context

**In Code/Config**:
- Linting rules (ESLint, Prettier)
- Type definitions
- Constants and configuration
- Architecture (visible in structure)

**Rule of Thumb**: If it can be in code, put it in code. Memory is for what code can't capture.

---

## Memory Refresh

### When to Invalidate

Memory should refresh when:
- ✅ Dependencies change (package.json updated)
- ✅ Tech stack changes (new framework adopted)
- ✅ Project structure refactored significantly
- ✅ User explicitly requests reset
- ✅ Memory is stale (> 30 days old, configurable)

### Staleness Detection

```typescript
function isStale(memory: MemoryEntry, maxAge: string): boolean {
  const age = Date.now() - new Date(memory.last_updated).getTime();
  const maxAgeMs = parseAge(maxAge); // "7 days", "30 days"
  return age > maxAgeMs;
}
```

### Refresh Strategies

**Automatic Refresh**:
- Watch critical files (package.json, tsconfig.json)
- Invalidate related memory on change
- Re-scan and update

**Manual Refresh**:
```bash
/refresh-memory              # Refresh all
/refresh-memory [skill]      # Refresh specific skill
/clear-memory [skill]        # Clear and start fresh
```

---

## Best Practices

### DO ✅

1. **Log important decisions with rationale**
2. **Track user corrections (2+ times = pattern)**
3. **Store in human-readable format (JSON)**
4. **Provide user control (view/clear commands)**
5. **Include timestamps and confidence levels**
6. **Refresh memory when dependencies change**
7. **Notify user when learning from corrections**

### DON'T ❌

1. **Don't store sensitive data**
2. **Don't persist everything (be selective)**
3. **Don't assume memory is always valid (check staleness)**
4. **Don't make memory opaque (user should understand)**
5. **Don't persist what belongs in code**
6. **Don't keep stale memory indefinitely**

---

## Commands for Memory Management

Provide these commands to users:

```bash
# View memory
/show-memory                  # Show all memory
/show-memory [skill]          # Show specific skill memory

# Clear memory
/clear-memory [skill]         # Clear specific skill
/clear-all-memory             # Clear everything (confirm first)

# Refresh memory
/refresh-memory               # Refresh all memory
/refresh-memory [skill]       # Refresh specific skill

# Export/backup
/export-memory                # Export for backup
/import-memory [file]         # Restore from backup
```

---

## Integration with Other Skills

### With context-persistence Skill

Memory management stores **preferences and patterns**.
Context persistence stores **current task state**.

**Example**:
- Memory: "User prefers named imports" (permanent)
- Context: "Currently implementing auth feature" (temporary)

### With plan-approval Skill

Memory management stores **approved decisions**.
Plan approval handles **future decisions requiring approval**.

**Example**:
- Memory: "JWT auth was approved on 2025-01-15"
- Plan: "Proposing addition of OAuth - needs approval"

---

## Example: Complete Memory Management Workflow

### Scenario: User Corrects Import Style Twice

**First Correction**:
```
User: "Please use named imports instead of default"
Claude: ✓ Fixed import style
Action: Log correction in memory (count: 1)
```

**Second Correction** (same pattern):
```
User: "Again, use named imports"
Claude: ✓ Fixed import style
Action: Mark as learned pattern (count: 2)
Notify: "📚 Learned preference: Always use named imports"
Storage: .claude/memory/project/preferences.json
```

**Future Usage**:
```
Claude automatically uses named imports
User sees: "✓ Using your preferred import style (named imports)"
```

**User Can Reset**:
```
User: /clear-memory import-style
Claude: ✓ Cleared import style preference
```

---

## Privacy & Security

### What to Store

✅ **Safe**:
- Code preferences (naming, structure)
- Architecture decisions (patterns, approaches)
- Correction patterns
- Project knowledge (tech stack, structure)

❌ **Never Store**:
- API keys, tokens, credentials
- Personal information
- Sensitive business logic
- Private URLs with tokens

### User Control

**Transparency**:
- Memory files in visible location
- Human-readable format
- Clear documentation of what's stored

**Control**:
- View memory anytime
- Clear memory anytime
- Export/backup memory
- Memory not committed to git (add to .gitignore)

---

## Summary

**Memory management enables Claude Code to**:
1. ✅ Remember user preferences across sessions
2. ✅ Learn from corrections and adapt
3. ✅ Document decisions with rationale
4. ✅ Provide continuity across context resets
5. ✅ Improve over time without user repetition

**Key principle**: Be selective, transparent, intentional, and respectful of user privacy.

**Storage**: `.claude/memory/` directory with JSON files

**Commands**: `/show-memory`, `/clear-memory`, `/refresh-memory`

Use this skill to make Claude Code feel like it truly "remembers" your project!
