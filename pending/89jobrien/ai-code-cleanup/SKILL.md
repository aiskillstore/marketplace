---
name: ai-code-cleanup
description: Remove AI-generated code slop from branches. Use after AI-assisted coding
  sessions to clean up defensive bloat, unnecessary comments, type casts, and style
  inconsistencies. Focuses on identifying and removing AI artifacts that degrade code
  quality.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# AI Code Cleanup

This skill identifies and removes AI-generated artifacts that degrade code quality, including defensive bloat, unnecessary comments, type casts, and style inconsistencies.

## When to Use This Skill

- After AI-assisted coding sessions
- Before code reviews or merging branches
- When cleaning up code that feels "over-engineered"
- When removing unnecessary defensive code
- When standardizing code style after AI generation
- When preparing code for production

## What This Skill Does

1. **Identifies AI Artifacts**: Detects patterns typical of AI-generated code
2. **Removes Bloat**: Eliminates unnecessary defensive code and comments
3. **Fixes Type Issues**: Removes unnecessary type casts and workarounds
4. **Standardizes Style**: Ensures consistency with project conventions
5. **Preserves Functionality**: Maintains code behavior while improving quality
6. **Validates Changes**: Ensures code still compiles and tests pass

## How to Use

### Clean Up Branch

```
Remove AI slop from this branch
```

```
Clean up the code in this pull request
```

### Specific Cleanup

```
Remove unnecessary comments and defensive code from src/
```

## Slop Patterns to Remove

### 1. Unnecessary Comments

**Patterns:**

- Comments explaining obvious code
- Comments inconsistent with file's documentation style
- Redundant comments that restate the code
- Over-documentation of simple operations

**Example:**

```javascript
// ❌ AI-generated: Obvious comment
// Set the user's name
user.name = name;

// ✅ Clean: Self-documenting code
user.name = name;
```

### 2. Defensive Bloat

**Patterns:**

- Extra try/catch blocks abnormal for that codebase
- Defensive null/undefined checks on trusted paths
- Redundant input validation when callers already validate
- Error handling that can never trigger

**Example:**

```javascript
// ❌ AI-generated: Unnecessary defensive code
function processUser(user) {
  try {
    if (user && user.name && typeof user.name === 'string') {
      return user.name.toUpperCase();
    }
    return null;
  } catch (error) {
    console.error(error);
    return null;
  }
}

// ✅ Clean: Trust the input, handle real errors
function processUser(user) {
  return user.name.toUpperCase();
}
```

### 3. Type Workarounds

**Patterns:**

- Casts to `any` to bypass type issues
- Unnecessary type assertions (`as X`)
- `@ts-ignore` or `@ts-expect-error` without legitimate reason
- Overly complex generic constraints

**Example:**

```typescript
// ❌ AI-generated: Type workaround
const data = response.data as any;
const result = processData(data as ProcessedData);

// ✅ Clean: Proper typing
const data = response.data;
const result = processData(data);
```

### 4. Style Inconsistencies

**Patterns:**

- Naming conventions different from rest of file
- Formatting that doesn't match surrounding code
- Import organization inconsistent with file patterns
- Variable declarations inconsistent with file style

**Example:**

```javascript
// ❌ AI-generated: Inconsistent style
const UserData = fetchUser();
var processedData = process(UserData);
let FinalResult = format(processedData);

// ✅ Clean: Consistent style
const userData = fetchUser();
const processedData = process(userData);
const finalResult = format(processedData);
```

### 5. AI Tells

**Patterns:**

- Unnecessary emoji usage in code or comments
- Overly verbose variable names
- Redundant intermediate variables
- "Just in case" code with no actual use case

## Cleanup Process

### 1. Get the Diff

```bash
git diff $(git merge-base HEAD main)..HEAD --name-only
```

### 2. Analyze Each File

For each changed file:

- Read the full file to understand existing style
- Identify patterns from slop categories
- Make surgical edits to remove slop
- Preserve functionality

### 3. Verification

- Ensure code still compiles/runs
- Changes should reduce code, not add more
- Run tests to verify behavior
- Check for any regressions

## Examples

### Example 1: Comment Cleanup

**Input**: Remove unnecessary comments from `src/auth.js`

**Output**:

```markdown
## AI Code Cleanup: src/auth.js

### Removed
- 12 redundant comments explaining obvious code
- 3 comments inconsistent with file style
- 5 over-documented simple operations

### Changes
```javascript
// Before
// Function to validate user email
// Takes email string as input
// Returns boolean indicating validity
function validateEmail(email) {
  // Check if email is not empty
  if (!email) {
    return false; // Return false if empty
  }
  // Return regex test result
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// After
function validateEmail(email) {
  if (!email) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

### Result

- Lines reduced: 12 → 4
- Functionality preserved
- Tests pass

```

### Example 2: Defensive Bloat Removal

**Input**: Remove defensive bloat from `src/api/users.js`

**Output**:
```markdown
## AI Code Cleanup: src/api/users.js

### Removed
- 3 unnecessary try/catch blocks
- 8 redundant null checks on validated inputs
- 2 error handlers that can never trigger

### Changes
```javascript
// Before
async function getUser(userId) {
  try {
    if (!userId || typeof userId !== 'string') {
      throw new Error('Invalid userId');
    }
    const user = await db.users.findById(userId);
    if (user && user.id) {
      return user;
    }
    return null;
  } catch (error) {
    console.error(error);
    throw error;
  }
}

// After
async function getUser(userId) {
  const user = await db.users.findById(userId);
  return user || null;
}
```

### Result

- Code reduced: 15 lines → 3 lines
- Functionality preserved
- Error handling appropriate for context

```

## Reference Files

- **`references/REFACTORING_PLAN.template.md`** - Refactoring plan template with code smells, before/after metrics, and rollback strategy

## Best Practices

### Cleanup Guidelines

1. **Preserve Functionality**: Only remove code that doesn't affect behavior
2. **Maintain Style**: Follow existing project conventions
3. **Keep Real Errors**: Don't remove legitimate error handling
4. **Test After Changes**: Always verify code still works
5. **Incremental**: Make changes incrementally, test as you go

### What to Keep

- Legitimate error handling
- Necessary type assertions
- Helpful comments that add context
- Defensive code for untrusted inputs
- Style that matches the codebase

### What to Remove

- Obvious comments
- Unnecessary defensive code
- Type workarounds
- Style inconsistencies
- AI-generated artifacts

## Related Use Cases

- Post-AI coding cleanup
- Code review preparation
- Code quality improvement
- Style standardization
- Removing technical debt
