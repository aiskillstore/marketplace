# Memory Patterns for Claude Code Skills

## Table of Contents
- [Context Persistence](#context-persistence)
- [User Preference Tracking](#user-preference-tracking)
- [Plan-Approval Workflows](#plan-approval-workflows)
- [Session State Management](#session-state-management)
- [Memory Refresh Triggers](#memory-refresh-triggers)

---

## Context Persistence

### Purpose

Maintain information across Claude Code sessions so that knowledge doesn't get lost when context resets or conversations restart.

### When to Persist Context

**Persist when**:
- User explicitly states a preference ("always use X pattern")
- User corrects Claude multiple times on the same issue
- Project-specific conventions are established
- Long-running tasks span multiple sessions
- User provides domain knowledge worth remembering

**Don't persist**:
- One-time experiments or temporary changes
- Formatting preferences (use project's linter config instead)
- Information already in codebase files
- Sensitive data (API keys, credentials)

### Implementation Pattern

**Storage Location**:
```
.claude/memory/
  {skill-name}/
    preferences.json      # User preferences
    context.json          # Project context
    corrections.json      # User corrections history
```

**Example: Database Column Naming Preference**

After user corrects column naming twice:

```json
// .claude/memory/database-verification/preferences.json
{
  "column_naming": {
    "convention": "camelCase",
    "learned_from": "user_correction",
    "correction_count": 2,
    "examples": [
      "userId (not user_id)",
      "createdAt (not created_at)"
    ],
    "last_updated": "2025-01-15T10:30:00Z"
  },
  "auto_approve_tables": ["users", "posts", "comments"],
  "always_verify_tables": ["payments", "sensitive_data"]
}
```

**Skill Hook Implementation**:

```typescript
// In PreToolUse hook
const memory = await loadMemory('database-verification');

if (memory?.preferences?.column_naming?.convention === 'camelCase') {
  // Auto-apply learned preference
  if (columnName.includes('_')) {
    blockWithMessage(`
      📚 LEARNED PREFERENCE: Use camelCase for columns
      Found: ${columnName}
      Expected: ${toCamelCase(columnName)}
    `);
  }
}
```

### Best Practices

✅ **DO**:
- Store in `.claude/memory/{skill-name}/` directory
- Include timestamps for staleness detection
- Provide user commands to view/clear memory (`/show-memory`, `/clear-memory`)
- Gracefully handle missing or corrupted memory files
- Log memory updates for transparency

❌ **DON'T**:
- Store sensitive data without encryption
- Assume memory is always valid (check staleness)
- Persist everything (be selective and intentional)
- Make memory opaque (user should understand what's stored)
- Forget to document memory schema

---

## User Preference Tracking

### Purpose

Remember user choices and patterns to reduce repetitive corrections and improve Claude's accuracy over time.

### Tracking Strategies

#### 1. Correction Counter

Track how many times user corrects the same pattern:

```typescript
interface CorrectionTracker {
  pattern: string;
  count: number;
  first_seen: string;  // ISO timestamp
  last_seen: string;
  examples: string[];
  threshold: number;    // Auto-apply after N corrections
}
```

**Example**:
```json
{
  "import_style": {
    "pattern": "Use named imports, not default",
    "count": 3,
    "first_seen": "2025-01-10T09:00:00Z",
    "last_seen": "2025-01-15T14:30:00Z",
    "examples": [
      "import { Component } from 'lib' ✓",
      "import Component from 'lib' ✗"
    ],
    "threshold": 2
  }
}
```

After 2 corrections → Auto-apply preference

#### 2. Choice Patterns

Track repeated user choices in ambiguous situations:

```json
{
  "choices": {
    "error_handling": {
      "strategy": "async-error-wrapper",
      "alternatives_rejected": ["try-catch", "error-boundary"],
      "confidence": 0.85,
      "choice_count": 7
    },
    "state_management": {
      "strategy": "TanStack-Query",
      "alternatives_rejected": ["Redux", "Zustand"],
      "confidence": 0.90,
      "choice_count": 12
    }
  }
}
```

#### 3. Workflow Preferences

Track how user prefers to work:

```json
{
  "workflow": {
    "prefers_plan_before_code": true,
    "prefers_tests_first": false,
    "prefers_commit_per_feature": true,
    "approval_required_for": ["database", "api_changes", "security"]
  }
}
```

### Integration Example

```typescript
// In UserPromptSubmit hook
const preferences = await loadPreferences('workflow');

if (isComplexChange && preferences.prefers_plan_before_code) {
  console.log(`
    📋 PREFERENCE DETECTED

    You prefer to see a plan before implementation.
    Suggesting: Use /create-plan command first
  `);
}
```

---

## Plan-Approval Workflows

### Purpose

Complex operations requiring user review before execution to prevent mistakes and enable learning from plans.

### Workflow Stages

#### Stage 1: Analysis & Planning

```typescript
interface Plan {
  id: string;
  type: 'feature' | 'refactor' | 'fix' | 'config';
  request: string;
  analysis: {
    files_to_create: string[];
    files_to_modify: string[];
    dependencies_to_add: string[];
    risks: string[];
    breaking_changes: string[];
  };
  estimated_complexity: 'low' | 'medium' | 'high';
  estimated_time: string;
  alternatives_considered: string[];
}
```

**Example**:
```json
{
  "id": "auth-jwt-2025-01-15",
  "type": "feature",
  "request": "Add JWT authentication",
  "analysis": {
    "files_to_create": [
      "src/middleware/auth.middleware.ts",
      "src/services/auth.service.ts",
      "src/models/refresh-token.model.ts"
    ],
    "files_to_modify": [
      "src/app.ts",
      "src/models/user.model.ts",
      "package.json"
    ],
    "dependencies_to_add": [
      "jsonwebtoken@^9.0.0",
      "@types/jsonwebtoken@^9.0.0"
    ],
    "risks": [
      "Existing session-based auth will be replaced",
      "Requires database migration for refresh tokens",
      "All existing auth middleware must be updated"
    ],
    "breaking_changes": [
      "Session cookies will no longer work",
      "All clients must update to JWT tokens"
    ]
  },
  "estimated_complexity": "medium",
  "estimated_time": "30-45 minutes",
  "alternatives_considered": [
    "Keep session-based auth (rejected: not stateless)",
    "Use Passport.js (rejected: too heavyweight)"
  ]
}
```

#### Stage 2: Plan Presentation

Display plan using Stop hook or command:

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 AUTHENTICATION IMPLEMENTATION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary
Add JWT authentication with refresh tokens

## Files to Create (3)
1. `src/middleware/auth.middleware.ts` - JWT verification
2. `src/services/auth.service.ts` - Token generation/validation
3. `src/models/refresh-token.model.ts` - Refresh token storage

## Files to Modify (3)
1. `src/app.ts` - Register auth middleware
2. `src/models/user.model.ts` - Add refreshToken field
3. `package.json` - Add jsonwebtoken dependency

## Dependencies
- jsonwebtoken (^9.0.0)
- @types/jsonwebtoken (^9.0.0)

## Risks ⚠️
- Existing session-based auth will be replaced
- Requires database migration for refresh tokens
- All clients must update to JWT tokens

## Breaking Changes 🚨
- Session cookies will no longer work
- All existing auth middleware must be updated

## Alternatives Considered
- Keep session-based auth (rejected: not stateless)
- Use Passport.js (rejected: too heavyweight)

## Estimated Time: 30-45 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Do you approve this plan? (yes/no/modify)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Stage 3: User Decision

User can:
1. **Approve** → Save plan, proceed to execution
2. **Reject** → Cancel, save rejection reason for learning
3. **Modify** → User describes changes, regenerate plan

```typescript
interface PlanDecision {
  plan_id: string;
  decision: 'approved' | 'rejected' | 'modified';
  timestamp: string;
  user_comment?: string;
  modifications?: string[];
}
```

#### Stage 4: Execution with Tracking

```json
{
  "plan_id": "auth-jwt-2025-01-15",
  "status": "in_progress",
  "approved_at": "2025-01-15T11:00:00Z",
  "execution_started": "2025-01-15T11:05:00Z",
  "completed_steps": [
    {
      "step": "Created auth.middleware.ts",
      "timestamp": "2025-01-15T11:08:00Z"
    },
    {
      "step": "Created auth.service.ts",
      "timestamp": "2025-01-15T11:12:00Z"
    }
  ],
  "remaining_steps": [
    "Create refresh-token.model.ts",
    "Modify app.ts",
    "Modify user.model.ts",
    "Run database migration"
  ],
  "current_step": "Create refresh-token.model.ts"
}
```

#### Stage 5: Completion & Learning

```json
{
  "plan_id": "auth-jwt-2025-01-15",
  "status": "completed",
  "completed_at": "2025-01-15T11:35:00Z",
  "actual_time": "30 minutes",
  "estimated_time": "30-45 minutes",
  "accuracy": "within_estimate",
  "user_satisfaction": "high",
  "lessons_learned": [
    "User prefers JWT over sessions for this project",
    "Always include migration step in auth changes",
    "Refresh token pattern is preferred for mobile apps"
  ],
  "deviations_from_plan": []
}
```

### Implementation with Hooks

**Using Stop Hook**:
```typescript
// .claude/hooks/plan-approval.ts
export async function handleStopEvent(data: StopEventData) {
  const plan = await detectPlanInResponse(data.response);

  if (plan && plan.requiresApproval) {
    console.log(formatPlanForApproval(plan));
    await savePlan(plan);
    process.exit(0); // Display to user
  }
}
```

**Using PreToolUse Hook** (for blocking until approval):
```typescript
// Only proceed if plan is approved
const pendingPlan = await getPendingPlan();

if (pendingPlan && !pendingPlan.approved) {
  console.error(`
    ⚠️ APPROVAL REQUIRED

    Plan "${pendingPlan.id}" needs approval before execution.

    Review plan and respond with:
    - "approve" to proceed
    - "reject" to cancel
    - "modify: [your changes]" to adjust plan
  `);
  process.exit(2); // Block execution
}
```

---

## Session State Management

### Purpose

Track state beyond simple "skill used" flags to enable sophisticated memory and learning.

### Enhanced Session State Schema

```typescript
interface EnhancedSessionState {
  // Basic tracking (existing)
  skills_used: string[];
  files_verified: string[];

  // User preferences (NEW)
  user_preferences: {
    [skill_name: string]: {
      [preference_key: string]: any;
      last_updated: string;
    };
  };

  // Corrections tracking (NEW)
  corrections: {
    [skill_name: string]: {
      count: number;
      last_correction: string;
      pattern: string;
      examples: string[];
    };
  };

  // Context accumulation (NEW)
  context: {
    current_feature?: string;
    current_task?: string;
    related_files: string[];
    key_decisions: Array<{
      timestamp: string;
      decision: string;
      rationale: string;
    }>;
    blockers: string[];
    last_updated: string;
  };

  // Plan tracking (NEW)
  active_plan?: {
    plan_id: string;
    status: 'proposed' | 'approved' | 'in_progress';
    current_step: number;
    total_steps: number;
  };
}
```

### Example Usage

```typescript
// In PostToolUse hook
const sessionState = await loadSessionState();

// Track decisions
if (isSignificantEdit(toolInput)) {
  sessionState.context.key_decisions.push({
    timestamp: new Date().toISOString(),
    decision: extractDecision(toolInput),
    rationale: inferRationale(toolInput, userPrompt)
  });
}

// Update active plan progress
if (sessionState.active_plan) {
  sessionState.active_plan.current_step++;

  if (sessionState.active_plan.current_step >= sessionState.active_plan.total_steps) {
    // Plan complete!
    await completePlan(sessionState.active_plan.plan_id);
  }
}

await saveSessionState(sessionState);
```

---

## Memory Refresh Triggers

### Purpose

Detect when stored memory becomes stale or invalid and refresh/invalidate automatically.

### Trigger Conditions

#### 1. File-Based Triggers

Watch critical files for changes:

```typescript
const refreshTriggers = {
  'package.json': ['dependencies', 'devDependencies'],
  'tsconfig.json': ['compilerOptions'],
  '.env.example': ['*'], // Any change
  'prisma/schema.prisma': ['model', 'enum'],
};
```

**Implementation**:
```typescript
// In PostToolUse hook
if (editedFile === 'package.json') {
  const diff = await getFileDiff('package.json');

  if (diff.includes('dependencies')) {
    // Dependencies changed → invalidate tech stack memory
    await invalidateMemory('tech-stack');
    await invalidateMemory('backend-dev-guidelines');

    console.log(`
      🔄 MEMORY REFRESHED
      package.json dependencies changed
      → Tech stack memory invalidated
      → Will re-detect on next use
    `);
  }
}
```

#### 2. Time-Based Expiry

Set expiry times for different memory types:

```json
{
  "memory_expiry": {
    "user_preferences": "never",      // User choices don't expire
    "project_structure": "7 days",    // Re-scan after 1 week
    "dependencies": "1 day",          // Check daily
    "temp_context": "1 hour"          // Forget after session
  }
}
```

**Check on load**:
```typescript
const memory = await loadMemory('project-structure');

if (isStale(memory, '7 days')) {
  console.log('📊 Memory is stale, refreshing...');
  const fresh = await scanProjectStructure();
  await saveMemory('project-structure', fresh);
}
```

#### 3. Conflict Detection

Detect when memory contradicts current state:

```typescript
const memoryStack = await loadMemory('tech-stack');
const actualStack = await detectFromPackageJson();

if (memoryStack.orm !== actualStack.orm) {
  console.log(`
    ⚠️ MEMORY CONFLICT DETECTED

    Memory says: ${memoryStack.orm}
    Actual code: ${actualStack.orm}

    → Updating memory with actual state
  `);

  await saveMemory('tech-stack', actualStack);
}
```

#### 4. User-Initiated Refresh

Provide commands for manual refresh:

```typescript
// /refresh-memory command
if (command === 'refresh-memory') {
  await invalidateAllMemory();
  console.log('✅ All memory cleared. Will re-learn from codebase.');
}

// /refresh-memory [skill-name] command
if (command.startsWith('refresh-memory ')) {
  const skillName = command.split(' ')[1];
  await invalidateMemory(skillName);
  console.log(`✅ Memory for ${skillName} cleared.`);
}
```

### Graceful Degradation

Always handle missing or stale memory gracefully:

```typescript
async function getPreference(key: string): Promise<any> {
  try {
    const memory = await loadMemory('preferences');

    if (!memory || isStale(memory)) {
      // Fall back to defaults or re-detect
      return await detectFromCodebase(key);
    }

    return memory[key];
  } catch (error) {
    // Memory corrupted or missing
    console.warn(`Memory unavailable, using defaults for ${key}`);
    return getDefaultValue(key);
  }
}
```

### Best Practices

✅ **DO**:
- Set appropriate expiry times (not too short, not too long)
- Watch critical config files for changes
- Validate memory on load
- Provide user control over refresh
- Log refresh actions for transparency
- Fall back gracefully when memory unavailable

❌ **DON'T**:
- Refresh too aggressively (performance impact)
- Trust stale memory (always validate)
- Refresh without notifying user
- Make refresh synchronous (use background tasks)
- Forget to handle corrupted memory files

---

## Complete Example: Memory-Aware Skill

Here's how all memory patterns work together in a complete skill:

```typescript
// .claude/hooks/database-verification-hook.ts

export async function verifyDatabaseOperation(toolInput: any) {
  // 1. Load memory
  const memory = await loadMemory('database-verification');

  // 2. Check staleness
  if (isStale(memory, '7 days')) {
    memory = await refreshFromPrismaSchema();
  }

  // 3. Apply learned preferences
  if (memory.preferences?.column_naming === 'camelCase') {
    if (hasSnakeCase(toolInput.column_name)) {
      return blockWithSuggestion(
        `Use camelCase for columns (learned preference)`,
        toCamelCase(toolInput.column_name)
      );
    }
  }

  // 4. Check against plan
  const activePlan = await getActivePlan();
  if (activePlan && !planAllowsOperation(activePlan, toolInput)) {
    return blockWithMessage(`
      Operation not in approved plan: ${activePlan.id}
      Modify plan or get approval for deviation
    `);
  }

  // 5. Track correction if user overrides
  if (userOverrode(toolInput)) {
    memory.corrections.push({
      timestamp: new Date().toISOString(),
      blocked: toolInput.original,
      user_chose: toolInput.override,
      pattern: inferPattern(toolInput)
    });

    // Learn after 2 corrections
    if (memory.corrections.filter(c => c.pattern === 'column_naming').length >= 2) {
      memory.preferences.column_naming = inferPreference(memory.corrections);
      console.log('📚 Learned new preference from your corrections');
    }

    await saveMemory('database-verification', memory);
  }

  // 6. Update session state
  const session = await loadSessionState();
  session.context.related_files.push(toolInput.file_path);
  session.context.key_decisions.push({
    timestamp: new Date().toISOString(),
    decision: `Modified table: ${toolInput.table_name}`,
    rationale: toolInput.reason
  });
  await saveSessionState(session);

  // Allow operation
  return { allow: true };
}
```

This example demonstrates:
- ✅ Context persistence (load/save memory)
- ✅ User preference tracking (learned column naming)
- ✅ Plan-approval workflow (check active plan)
- ✅ Session state management (track decisions)
- ✅ Memory refresh (staleness check)
- ✅ Correction learning (adapt after 2 corrections)

---

## Storage Location Standards

### Directory Structure

```
.claude/memory/
  {skill-name}/
    preferences.json          # User preferences
    context.json              # Project context
    corrections.json          # Correction history
    plans/
      active.json             # Currently active plan
      {plan-id}.json         # Individual plan details
      history.json           # Past plans for learning
    session/
      {session-id}.json      # Session-specific state
```

### File Permissions

```bash
# Memory files should be:
chmod 600 .claude/memory/**/*.json  # Owner read/write only
```

### .gitignore Entry

```gitignore
# Don't commit user memory
.claude/memory/
.claude/session/

# But DO commit memory templates
!.claude/memory/.templates/
```

---

## Privacy & Security

### What to Store

✅ **Safe to store**:
- User preferences (naming conventions, workflow choices)
- Project patterns (file structure, architecture)
- Correction patterns (what mistakes were made)
- Plan histories (what was built when)

❌ **Never store**:
- API keys, tokens, credentials
- Personal information (names, emails, unless necessary)
- Sensitive business logic
- Private repository URLs with tokens

### User Control

Provide commands for transparency:

```bash
/show-memory [skill-name]      # View what's stored
/clear-memory [skill-name]     # Clear specific memory
/clear-all-memory              # Clear everything
/export-memory                 # Export for backup
```

### Encryption (Optional)

For sensitive preferences:

```typescript
import { encrypt, decrypt } from './crypto';

async function saveSecurePreference(key: string, value: any) {
  const encrypted = encrypt(JSON.stringify(value), getUserKey());
  await saveMemory(key, encrypted);
}
```

---

## Summary

Memory patterns enable Claude Code skills to:

1. **Remember** user preferences and project patterns
2. **Learn** from corrections and improve over time
3. **Plan** complex operations with user approval
4. **Track** context across sessions and tasks
5. **Refresh** automatically when dependencies change
6. **Respect** user privacy and provide transparency

Use these patterns to create skills that feel truly intelligent and personalized to each project.
