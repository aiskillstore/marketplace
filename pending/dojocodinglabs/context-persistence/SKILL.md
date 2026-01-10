---
name: context-persistence
description: Waypoint plans methodology and session survival patterns for Claude Code. Use when working on long-running features, need to resume after context reset, want to document task progress, or need to survive session interruptions. Covers three-file structure (plan/context/tasks), SESSION PROGRESS tracking, quick resume instructions, update frequency, and context handoff patterns.
---

# Context Persistence Skill

## Purpose

Ensure Claude Code can resume work seamlessly after context resets, session interruptions, or long breaks by maintaining structured documentation of current work, decisions, and progress.

## When to Use This Skill

Automatically activates when you mention:
- Waypoint plans, waypoint planning
- Resuming work, continuing work
- Session survival, context reset
- Task handoff, progress tracking
- Long-running features or projects
- Need to document current state

## The Problem: Context Resets

**What happens during a context reset**:
- ❌ All conversation history lost
- ❌ Current task context forgotten
- ❌ Decisions and rationale gone
- ❌ Progress not tracked
- ❌ Have to re-explain everything

**With context persistence**:
- ✅ Current task documented
- ✅ Decisions and rationale preserved
- ✅ Progress clearly tracked
- ✅ Quick resume in < 1 minute
- ✅ Seamless handoff to future sessions

---

## Three-File Structure

The core pattern uses **three complementary files** in `plans/active/{task-name}/`:

### 1. `{task-name}-plan.md` - The Strategic Plan

**Purpose**: High-level strategy and approach

**Contains**:
- Feature/task overview
- Requirements and acceptance criteria
- Architecture approach
- Implementation phases
- Dependencies and constraints
- Risks and mitigations

**Update frequency**: Rarely (only when approach changes)

**Example**:
```markdown
# Authentication Implementation Plan

## Overview
Add JWT-based authentication to replace session cookies for mobile app support.

## Requirements
- JWT tokens with refresh mechanism
- Supabase Auth integration
- Protected API routes
- Mobile-friendly (stateless)

## Architecture
- Auth middleware in Edge Functions
- Token storage in httpOnly cookies (web) + AsyncStorage (mobile)
- Row-Level Security policies for data access

## Implementation Phases
1. Supabase Auth setup
2. Edge Function auth middleware
3. Frontend auth hooks
4. RLS policies
5. Migration from existing auth

## Dependencies
- Supabase setup complete
- Database schema finalized
```

### 2. `{task-name}-context.md` - Current State & Progress

**Purpose**: Living document of current state, decisions, and progress

**Contains**:
- SESSION PROGRESS (updated frequently)
- Key decisions made
- Important discoveries
- Current blockers
- Files modified
- Quick resume instructions

**Update frequency**: After each significant change or decision

**Example**:
```markdown
# Authentication Implementation Context

## SESSION PROGRESS (2025-01-15 14:30)

### ✅ COMPLETED
- [x] Supabase Auth configured
- [x] Created auth middleware for Edge Functions
- [x] Implemented login/signup pages
- [x] Added auth context provider

### 🟡 IN PROGRESS
- [ ] Implementing token refresh logic (CURRENT)
  - Working on: lib/supabase/auth.ts
  - Next: Handle token expiration gracefully

### ⏳ PENDING
- [ ] Add RLS policies
- [ ] Migrate existing users
- [ ] Add mobile auth flow
- [ ] Write auth tests

### 🎯 NEXT ACTION
Continue implementing refreshToken() function in lib/supabase/auth.ts
- Handle expired tokens
- Refresh transparently
- Redirect to login if refresh fails

## KEY DECISIONS

### Decision: JWT vs. Session Cookies (2025-01-12)
**Chose**: JWT tokens
**Rationale**: Need stateless auth for mobile apps
**Impact**: Requires token refresh mechanism

### Decision: Supabase Auth vs. Custom (2025-01-13)
**Chose**: Supabase Auth
**Rationale**: Built-in RLS integration, handles token refresh
**Impact**: Less custom code, tighter Supabase integration

## IMPORTANT DISCOVERIES

### Token Refresh Timing
Discovered tokens expire after 1 hour by default. Need to:
- Refresh proactively at 50 minutes
- Handle edge case of offline user
- Store refresh token securely

### RLS Row vs. Column Level
Supabase RLS is row-level only, not column-level.
For sensitive columns, need separate tables.

## CURRENT BLOCKERS

None currently. Auth flow is straightforward with Supabase.

## FILES MODIFIED

### Created
- lib/supabase/auth.ts (auth utilities)
- app/(auth)/login/page.tsx
- app/(auth)/signup/page.tsx
- components/auth/auth-provider.tsx

### Modified
- lib/supabase/client.ts (added auth hooks)
- middleware.ts (added auth middleware)

## QUICK RESUME

To continue this work:
1. Read this file (context.md) for current state
2. Check tasks.md for checklist
3. Refer to plan.md for overall strategy
4. Current file: lib/supabase/auth.ts
5. Next: Implement refreshToken() function
6. After that: Test token refresh flow
```

### 3. `{task-name}-tasks.md` - Actionable Checklist

**Purpose**: Granular, actionable tasks with acceptance criteria

**Contains**:
- Detailed task breakdown
- Acceptance criteria for each task
- Dependencies between tasks
- Task status (pending/in-progress/complete)

**Update frequency**: Daily or after completing tasks

**Example**:
```markdown
# Authentication Implementation Tasks

## Phase 1: Supabase Setup ✅

- [x] Create Supabase project (Acceptance: Project created, credentials stored)
- [x] Enable Email auth provider (Acceptance: Can sign up via email)
- [x] Configure redirect URLs (Acceptance: Auth callbacks work locally + prod)
- [x] Add auth schema to database (Acceptance: Users table exists)

## Phase 2: Backend Auth 🟡

- [x] Create auth utilities (Acceptance: getUser(), signIn(), signUp() functions work)
- [ ] Implement token refresh **(IN PROGRESS)**
  - Acceptance: Tokens refresh automatically before expiry
  - Dependencies: Auth utilities complete
  - Notes: Need to handle offline case
- [ ] Add auth middleware to Edge Functions
  - Acceptance: Protected routes return 401 if not authenticated
  - Dependencies: Token refresh working
- [ ] Create auth helper for server components
  - Acceptance: Can check auth in Server Components

## Phase 3: Frontend Auth ⏳

- [x] Create auth context provider (Acceptance: Auth state available app-wide)
- [x] Build login page (Acceptance: Can log in with email/password)
- [x] Build signup page (Acceptance: Can create account)
- [ ] Add protected route wrapper
  - Acceptance: Redirects to login if not authenticated
  - Dependencies: Auth context complete
- [ ] Add loading states
  - Acceptance: Shows loading spinner during auth checks

## Phase 4: Security 🔒

- [ ] Add RLS policies
  - Acceptance: Users can only access their own data
  - Files: supabase/migrations/xxx_rls_policies.sql
- [ ] Test auth edge cases
  - Expired tokens
  - Invalid tokens
  - Network failures
  - Concurrent sessions

## Phase 5: Migration 📦

- [ ] Create migration script for existing users
- [ ] Test migration locally
- [ ] Schedule maintenance window
- [ ] Execute migration in production
- [ ] Verify all users migrated successfully
```

---

## SESSION PROGRESS Pattern

The **SESSION PROGRESS** section is the most important part of context.md:

### Structure

```markdown
## SESSION PROGRESS (2025-01-15 14:30)

### ✅ COMPLETED
[What's done - be specific]

### 🟡 IN PROGRESS
[What you're working on RIGHT NOW]

### ⏳ PENDING
[What's coming next]

### 🚫 BLOCKED
[What's preventing progress - if any]

### 🎯 NEXT ACTION
[Specific next step with file + function]
```

### Best Practices

**DO ✅**:
- Update after each significant milestone
- Be specific about current file/function
- Include "NEXT ACTION" for easy resume
- Mark completed items immediately
- Note blockers as they arise

**DON'T ❌**:
- Leave stale progress (update regularly)
- Be vague ("working on auth" → "implementing refreshToken() in auth.ts")
- Forget to mark completed items
- Skip the NEXT ACTION (critical for resume)

### Update Frequency

| Event | Update SESSION PROGRESS? |
|-------|-------------------------|
| Completed a full task | ✅ Yes |
| Significant decision made | ✅ Yes |
| Discovered blocker | ✅ Yes |
| Changed approach | ✅ Yes |
| Switching to different task | ✅ Yes |
| Minor code change | ❌ No |
| Formatting/cleanup | ❌ No |
| Reading code | ❌ No |

---

## Quick Resume Instructions

Always include this section in context.md:

```markdown
## QUICK RESUME

To continue this work:
1. **Read**: This file (context.md) for current state
2. **Check**: tasks.md for detailed checklist
3. **Reference**: plan.md for overall strategy
4. **Current file**: [exact file path]
5. **Current function**: [exact function/component name]
6. **Next step**: [specific action to take]
7. **After that**: [following step]
8. **Expected time**: [estimate for next step]

### If Context is Stale (> 3 days old)
1. Verify current code state matches context
2. Check for changes by others (git log)
3. Update context.md before proceeding
```

---

## When to Create Waypoint Plans

### Always Create For

✅ Features taking > 2 hours
✅ Multi-session work
✅ Complex implementations
✅ Work likely to be interrupted
✅ Team handoffs
✅ Refactorings affecting multiple files

### Optional For

⚠️ Simple bug fixes (< 30 min)
⚠️ Documentation updates
⚠️ Minor UI tweaks
⚠️ Configuration changes

### Never Create For

❌ Trivial changes
❌ Automated tasks
❌ One-liner fixes

**Rule of Thumb**: If you might forget context after lunch, create a waypoint plan.

---

## Directory Structure

```
plans/
├── active/                      # Current work
│   ├── auth-implementation/
│   │   ├── auth-implementation-plan.md
│   │   ├── auth-implementation-context.md
│   │   └── auth-implementation-tasks.md
│   ├── payments-integration/
│   │   ├── payments-integration-plan.md
│   │   ├── payments-integration-context.md
│   │   └── payments-integration-tasks.md
│   └── README.md               # Active work index
├── archived/                   # Completed work
│   └── [moved completed tasks]
└── templates/                  # Templates for new tasks
    ├── template-plan.md
    ├── template-context.md
    └── template-tasks.md
```

---

## File Naming Convention

**Pattern**: `{task-slug}-{type}.md`

**Examples**:
- `auth-implementation-plan.md`
- `auth-implementation-context.md`
- `auth-implementation-tasks.md`

**task-slug**:
- Lowercase
- Hyphen-separated
- Descriptive (not generic)
- Max 3-4 words

**Good slugs**:
- `auth-implementation`
- `stripe-payments`
- `user-dashboard`

**Bad slugs**:
- `feature` (too generic)
- `task-123` (meaningless)
- `implement_new_authentication_system_with_jwt` (too long)

---

## Commands for Claude Code Waypoint Plugin

Provide these commands:

```bash
# Create new waypoint plan
/create-plan [task-name]          # Creates 3-file structure

# Update existing waypoint
/update-context                   # Updates SESSION PROGRESS

# Resume work
/resume                           # Shows latest context + next action
/resume [task-name]               # Resume specific task

# Archive completed work
/archive [task-name]              # Moves to archived/
```

---

## Integration with Commands

### `/create-plan` Command

Creates the three-file structure automatically:

```bash
/create-plan auth-implementation

Creates:
- plans/active/auth-implementation/auth-implementation-plan.md
- plans/active/auth-implementation/auth-implementation-context.md
- plans/active/auth-implementation/auth-implementation-tasks.md
```

See the `/create-plan` command documentation for details.

### `/update-context` Command

Updates SESSION PROGRESS section with prompts:

```bash
/update-context

Prompts:
- What did you complete?
- What are you currently working on?
- What's the specific file/function?
- What's the next action?
- Any blockers?
```

### `/resume` Command

Displays context for quick resume:

```bash
/resume

Output:
📂 Resuming: auth-implementation
📋 CONTEXT SUMMARY:
- Last updated: 2 hours ago
- In progress: Implementing token refresh
✅ COMPLETED (3/8): ...
🟡 IN PROGRESS (1/8): ...
➡️ NEXT ACTION: Implement refreshToken() in lib/supabase/auth.ts
```

---

## Best Practices

### DO ✅

1. **Update context after significant changes** (not after every line)
2. **Be specific in NEXT ACTION** (file + function + what to do)
3. **Mark tasks complete immediately** (don't batch them)
4. **Document decisions with rationale** (the "why" not just "what")
5. **Include code snippets in context** (for complex logic)
6. **Add timestamps to SESSION PROGRESS** (know when it was updated)
7. **Archive completed tasks** (keep active/ directory clean)

### DON'T ❌

1. **Don't let context get stale** (> 3 days without update = stale)
2. **Don't be vague** ("working on auth" tells you nothing)
3. **Don't skip NEXT ACTION** (critical for resuming)
4. **Don't forget to update after decisions** (decisions are context!)
5. **Don't duplicate info** (plan vs. context vs. tasks have different purposes)
6. **Don't commit sensitive info** (credentials, API keys)

---

## Handling Context Staleness

### Detecting Staleness

Context is stale if:
- Last updated > 3 days ago
- Code changed significantly since update
- Blocker was noted but not resolved
- IN PROGRESS task completed but not marked

### Refreshing Stale Context

```markdown
## Context Refresh Checklist

Before resuming stale context:
- [ ] Read current code in "current file"
- [ ] Check git log for changes since last update
- [ ] Verify IN PROGRESS task is actually in progress
- [ ] Update completed tasks
- [ ] Remove resolved blockers
- [ ] Update NEXT ACTION if changed
- [ ] Add note: "Context refreshed on [date]"
```

---

## Example: Complete Context Lifecycle

### Day 1: Create Waypoint Plan

```bash
User: "Let's implement JWT authentication"
Claude: "I'll create a waypoint plan for this task"
/create-plan auth-implementation

Creates 3 files with:
- Plan: Overall strategy
- Context: Empty SESSION PROGRESS
- Tasks: Broken down checklist
```

### Day 1: Work & Update

```markdown
After 2 hours of work:

## SESSION PROGRESS (2025-01-15 14:30)

### ✅ COMPLETED
- [x] Supabase Auth configured
- [x] Created auth utilities

### 🟡 IN PROGRESS
- [ ] Implementing login page

### 🎯 NEXT ACTION
Complete LoginForm component in app/(auth)/login/page.tsx
```

### Day 2: Resume

```bash
User: "Continue with authentication"
Claude: /resume
→ Shows SESSION PROGRESS
→ "You were implementing LoginForm component"
→ Continues seamlessly
```

### Day 3: Context Reset

```
Context reset happens (100K tokens)

User: "Continue with authentication"
Claude: /resume
→ Reads context.md
→ "I see you're implementing JWT auth"
→ "Last worked on: LoginForm component"
→ "Next action: Add form validation"
→ Continues without missing a beat
```

### Day 5: Complete & Archive

```bash
User: "Authentication is done"
Claude: Updates all tasks to completed
/archive auth-implementation

Moves files to:
plans/archived/auth-implementation/
```

---

## Summary

**Claude Code Waypoint Plugin enables**:
1. ✅ Seamless resume after context resets
2. ✅ Quick handoff between sessions
3. ✅ Clear progress tracking
4. ✅ Decision documentation
5. ✅ Team collaboration

**Three-file structure**:
- **plan.md**: Strategy (rarely changes)
- **context.md**: Current state (updated frequently)
- **tasks.md**: Actionable checklist (updated daily)

**Key section**: SESSION PROGRESS in context.md

**Commands**: `/create-plan`, `/update-context`, `/resume`

**Rule**: If work takes > 2 hours or spans multiple sessions, create a waypoint plan!

Use this skill to make Claude Code resilient to context resets and interruptions.
