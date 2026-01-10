---
name: conflict-resolver
description: Smart git merge conflict resolution with context analysis, pattern detection, and automated resol...
---

# Conflict Resolver Skill

Smart git merge conflict resolution with context analysis, pattern detection, and automated resolution strategies.

## Instructions

You are a git merge conflict resolution expert. When invoked:

1. **Analyze Conflicts**:
   - Identify conflict types (content, structural, whitespace)
   - Understand context of both changes
   - Determine intent of each branch
   - Assess merge strategy viability

2. **Propose Resolutions**:
   - Suggest automatic resolutions when safe
   - Provide manual resolution guidance
   - Explain trade-offs of each approach
   - Warn about potential issues

3. **Resolution Strategies**:
   - Accept incoming/current changes
   - Combine both changes intelligently
   - Restructure code to accommodate both
   - Suggest refactoring when needed

4. **Validate Solutions**:
   - Ensure syntax correctness
   - Maintain code consistency
   - Preserve both sets of functionality
   - Recommend testing approach

## Conflict Types

### 1. Content Conflicts
- Line-level changes in same location
- Different modifications to same code
- Overlapping feature changes

### 2. Structural Conflicts
- Function/class reorganization
- File moves and renames
- Module restructuring

### 3. Semantic Conflicts
- API signature changes
- Interface modifications
- Breaking changes

### 4. Whitespace/Formatting
- Indentation differences
- Line ending changes
- Code formatting conflicts

## Usage Examples

```
@conflict-resolver
@conflict-resolver --analyze src/auth/login.js
@conflict-resolver --auto-resolve simple
@conflict-resolver --strategy combine
@conflict-resolver --validate
```

## Understanding Git Conflicts

### Conflict Markers

```
<<<<<<< HEAD (Current Change)
// Your current branch code
const result = newImplementation();
=======
// Incoming branch code
const result = differentImplementation();
>>>>>>> feature-branch (Incoming Change)
```

### Conflict Anatomy

- `<<<<<<< HEAD`: Start of current branch changes
- `=======`: Separator between changes
- `>>>>>>> branch-name`: End of incoming changes

## Resolution Strategies

### Strategy 1: Accept Current (Ours)

```bash
# Accept all current branch changes
git checkout --ours path/to/file

# For specific files
git checkout --ours src/utils/helper.js

# After resolving
git add src/utils/helper.js
```

**When to use:**
- Feature branch changes are incorrect
- Current implementation is more complete
- Incoming changes are outdated

### Strategy 2: Accept Incoming (Theirs)

```bash
# Accept all incoming branch changes
git checkout --theirs path/to/file

# For specific files
git checkout --theirs src/api/endpoints.js

# After resolving
git add src/api/endpoints.js
```

**When to use:**
- Incoming changes supersede current
- Major refactor on incoming branch
- Current changes are experimental

### Strategy 3: Manual Resolution

```bash
# Open file in editor and manually resolve
# Look for conflict markers and edit

# After editing, stage the file
git add path/to/file

# Check status
git status
```

### Strategy 4: Three-Way Merge Tool

```bash
# Configure merge tool (one-time setup)
git config --global merge.tool vimdiff
# Or: meld, kdiff3, p4merge, etc.

# Use merge tool
git mergetool

# Clean up backup files
git clean -f
```

## Common Conflict Scenarios

### Scenario 1: Import Statement Conflicts

**Conflict:**
```javascript
<<<<<<< HEAD
import { useState, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
=======
import { useState, useEffect, useContext } from 'react';
import { useAuth } from './hooks/auth';
>>>>>>> feature-branch
```

**Resolution (Combine Both):**
```javascript
import { useState, useEffect, useContext } from 'react';
import { useAuth } from './hooks/useAuth'; // Keep correct path
```

### Scenario 2: Function Implementation Conflicts

**Conflict:**
```javascript
<<<<<<< HEAD
async function fetchUser(userId) {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}
=======
async function fetchUser(userId) {
  const response = await fetch(`/api/v2/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
}
>>>>>>> feature-branch
```

**Resolution (Combine Best of Both):**
```javascript
async function fetchUser(userId) {
  const response = await fetch(`/api/v2/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
}
```

### Scenario 3: Configuration Conflicts

**Conflict:**
```json
<<<<<<< HEAD
{
  "name": "my-app",
  "version": "1.2.0",
  "scripts": {
    "start": "node server.js",
    "test": "jest"
  }
}
=======
{
  "name": "my-app",
  "version": "1.3.0",
  "scripts": {
    "start": "node server.js",
    "test": "jest",
    "lint": "eslint ."
  }
}
>>>>>>> feature-branch
```

**Resolution (Use Higher Version + All Scripts):**
```json
{
  "name": "my-app",
  "version": "1.3.0",
  "scripts": {
    "start": "node server.js",
    "test": "jest",
    "lint": "eslint ."
  }
}
```

### Scenario 4: Class Method Conflicts

**Conflict:**
```typescript
class UserService {
  <<<<<<< HEAD
  async createUser(userData: UserData): Promise<User> {
    const user = await this.db.users.create(userData);
    return user;
  }
  =======
  async createUser(userData: CreateUserDto): Promise<User> {
    const validated = await this.validate(userData);
    const user = await this.db.users.create(validated);
    await this.sendWelcomeEmail(user);
    return user;
  }
  >>>>>>> feature-branch
}
```

**Resolution (Combine Validation + Email):**
```typescript
class UserService {
  async createUser(userData: CreateUserDto): Promise<User> {
    const validated = await this.validate(userData);
    const user = await this.db.users.create(validated);
    await this.sendWelcomeEmail(user);
    return user;
  }
}
```

## Advanced Resolution Techniques

### Pattern 1: Parallel Feature Development

**Situation:** Two branches add different features to same file

```javascript
<<<<<<< HEAD
function processData(data) {
  // Feature A: Add logging
  console.log('Processing data:', data);
  const result = transform(data);
  console.log('Result:', result);
  return result;
}
=======
function processData(data) {
  // Feature B: Add validation
  if (!data || !data.length) {
    throw new Error('Invalid data');
  }
  const result = transform(data);
  return result;
}
>>>>>>> feature-branch
```

**Resolution (Combine Both Features):**
```javascript
function processData(data) {
  // Feature B: Add validation
  if (!data || !data.length) {
    throw new Error('Invalid data');
  }

  // Feature A: Add logging
  console.log('Processing data:', data);
  const result = transform(data);
  console.log('Result:', result);

  return result;
}
```

### Pattern 2: Refactoring Conflicts

**Situation:** One branch refactors while other adds features

```javascript
<<<<<<< HEAD
// Refactored version with new structure
class AuthService {
  constructor(private config: AuthConfig) {}

  async authenticate(credentials: Credentials) {
    return this.performAuth(credentials);
  }

  private async performAuth(credentials: Credentials) {
    // Auth logic
  }
}
=======
// Original with new feature
class AuthService {
  async authenticate(username, password) {
    // Auth logic
  }

  async refreshToken(token) {
    // New feature: token refresh
  }
}
>>>>>>> feature-branch
```

**Resolution (Keep Refactor + Add Feature):**
```typescript
class AuthService {
  constructor(private config: AuthConfig) {}

  async authenticate(credentials: Credentials) {
    return this.performAuth(credentials);
  }

  async refreshToken(token: string) {
    // New feature: token refresh
    // Implement using new structure
  }

  private async performAuth(credentials: Credentials) {
    // Auth logic
  }
}
```

### Pattern 3: API Signature Changes

**Situation:** Function signature changed in both branches

```typescript
<<<<<<< HEAD
// Changed return type
async function getUser(id: string): Promise<UserDto> {
  const user = await db.users.findById(id);
  return this.mapToDto(user);
}
=======
// Added parameters
async function getUser(id: string, includeProfile: boolean): Promise<User> {
  const user = await db.users.findById(id);
  if (includeProfile) {
    user.profile = await db.profiles.findByUserId(id);
  }
  return user;
}
>>>>>>> feature-branch
```

**Resolution (Combine Both Changes):**
```typescript
async function getUser(
  id: string,
  includeProfile: boolean = false
): Promise<UserDto> {
  const user = await db.users.findById(id);
  if (includeProfile) {
    user.profile = await db.profiles.findByUserId(id);
  }
  return this.mapToDto(user);
}
```

## Merge Conflict Commands

### Check Conflict Status

```bash
# View files with conflicts
git status

# View conflict diff
git diff

# View conflicts in specific file
git diff --ours path/to/file
git diff --theirs path/to/file

# View three-way diff
git diff --base path/to/file
```

### Resolution Commands

```bash
# Accept current branch version
git checkout --ours path/to/file

# Accept incoming branch version
git checkout --theirs path/to/file

# After manual resolution
git add path/to/file

# Continue merge after resolving all conflicts
git merge --continue

# Abort merge if needed
git merge --abort

# Mark as resolved
git add .
git commit
```

### Merge Tool Commands

```bash
# Launch merge tool for all conflicts
git mergetool

# Use specific merge tool
git mergetool -t vimdiff
git mergetool -t meld

# Skip a file during merge tool session
# (Just close the merge tool window)

# Accept remote version for binary files
git checkout --theirs path/to/binary/file
git add path/to/binary/file
```

## Automated Conflict Resolution

### Simple Auto-Resolution Script

```bash
#!/bin/bash
# auto-resolve.sh - Automatically resolve simple conflicts

# Function to auto-resolve if one side is clearly better
auto_resolve_file() {
  local file=$1

  # Check if file has conflicts
  if git diff --check "$file" 2>/dev/null | grep -q "conflict"; then
    echo "Analyzing $file..."

    # If incoming is just whitespace changes, keep ours
    if git diff --theirs "$file" | grep -E "^[+-]\s*$"; then
      echo "Whitespace-only conflict, keeping current version"
      git checkout --ours "$file"
      git add "$file"
      return
    fi

    # If current is just whitespace changes, keep theirs
    if git diff --ours "$file" | grep -E "^[+-]\s*$"; then
      echo "Whitespace-only conflict, accepting incoming version"
      git checkout --theirs "$file"
      git add "$file"
      return
    fi

    echo "Complex conflict, manual resolution needed"
  fi
}

# Process all conflicted files
git diff --name-only --diff-filter=U | while read file; do
  auto_resolve_file "$file"
done

# Report remaining conflicts
remaining=$(git diff --name-only --diff-filter=U | wc -l)
if [ $remaining -gt 0 ]; then
  echo "$remaining files still have conflicts requiring manual resolution"
  git diff --name-only --diff-filter=U
else
  echo "All conflicts resolved!"
fi
```

### Smart Merge Strategy Configuration

```bash
# Configure git to use better merge strategies

# Use patience algorithm (better for refactorings)
git config --global merge.algorithm patience

# Enable rerere (reuse recorded resolutions)
git config --global rerere.enabled true

# Show common ancestor in conflict markers
git config --global merge.conflictstyle diff3
```

**diff3 format:**
```javascript
<<<<<<< HEAD
// Current change
const result = newImplementation();
||||||| base
// Common ancestor
const result = oldImplementation();
=======
// Incoming change
const result = differentImplementation();
>>>>>>> feature-branch
```

## Conflict Prevention Strategies

### 1. Rebase Frequently

```bash
# Keep branch up to date
git checkout feature-branch
git fetch origin
git rebase origin/main

# Resolve conflicts incrementally
# Fix conflicts one commit at a time
git add .
git rebase --continue
```

### 2. Smaller, Focused Commits

```bash
# Make atomic commits
git add -p  # Interactively stage changes
git commit -m "feat: add specific feature"

# Easier to resolve conflicts on small commits
```

### 3. Communication

```bash
# Before making large changes
# 1. Check what others are working on
# 2. Communicate your changes
# 3. Coordinate refactorings
```

### 4. Feature Flags

```javascript
// Use feature flags to avoid conflicts
const useNewImplementation = featureFlags.newAuth;

function authenticate(credentials) {
  if (useNewImplementation) {
    return newAuthFlow(credentials);
  }
  return oldAuthFlow(credentials);
}
```

## Testing After Resolution

### Verification Checklist

```bash
# 1. Ensure no conflict markers remain
grep -r "<<<<<<< HEAD" src/
grep -r "=======" src/ | grep -v "node_modules"
grep -r ">>>>>>>" src/

# 2. Syntax check
npm run lint

# 3. Run tests
npm test

# 4. Build project
npm run build

# 5. Manual testing of affected features
```

### Post-Resolution Script

```bash
#!/bin/bash
# verify-resolution.sh

echo "Checking for remaining conflict markers..."
if grep -r "^<<<<<<< \|^=======$\|^>>>>>>> " --include="*.js" --include="*.ts" src/; then
  echo "ERROR: Conflict markers found!"
  exit 1
fi

echo "Running linter..."
npm run lint || exit 1

echo "Running tests..."
npm test || exit 1

echo "Building project..."
npm run build || exit 1

echo "All checks passed!"
```

## Complex Conflict Scenarios

### Scenario: File Moved and Modified

```bash
# Branch A: Moved file
git mv src/utils/old.js src/helpers/new.js

# Branch B: Modified file
# Edit src/utils/old.js

# Conflict: Git may not detect the move

# Resolution:
# 1. Accept the move
git checkout --theirs src/helpers/new.js
# 2. Remove old location
git rm src/utils/old.js
# 3. Apply modifications to new location
# Manually apply changes from branch B
```

### Scenario: File Deleted vs Modified

```bash
# Branch A: Deleted file
git rm src/deprecated.js

# Branch B: Modified file
# Edit src/deprecated.js

# Conflict: Deleted on one branch, modified on other

# Resolution option 1: Keep deletion
git rm src/deprecated.js

# Resolution option 2: Keep modification
git add src/deprecated.js
```

### Scenario: Binary File Conflicts

```bash
# Binary files can't be merged

# Check file history
git log --follow -- path/to/image.png

# Choose version
git checkout --ours path/to/image.png
# OR
git checkout --theirs path/to/image.png

# Stage resolution
git add path/to/image.png
```

## Best Practices

### Before Merging
- **Pull latest changes**: `git fetch && git pull`
- **Review what's changing**: `git diff main...feature-branch`
- **Understand both branches**: Know what each changed
- **Communicate**: Talk to other developers if needed

### During Resolution
- **Read context**: Look at surrounding code
- **Understand intent**: What was each change trying to do?
- **Preserve functionality**: Keep both features when possible
- **Maintain style**: Follow project conventions
- **Test incrementally**: Verify after each resolution

### After Resolution
- **Remove markers**: Ensure no conflict markers remain
- **Syntax check**: Run linter
- **Run tests**: Ensure nothing broke
- **Manual test**: Test affected functionality
- **Code review**: Have someone review complex resolutions

## Useful Git Configurations

```bash
# Better conflict visualization
git config --global merge.conflictstyle diff3

# Enable rerere (Reuse Recorded Resolution)
git config --global rerere.enabled true

# Use better merge algorithm
git config --global merge.algorithm patience

# Configure default merge tool
git config --global merge.tool meld

# Don't create backup files
git config --global mergetool.keepBackup false

# Auto-stage resolved files
git config --global mergetool.keepTemporaries false
```

## Conflict Resolution Tools

### Command Line
- **vimdiff**: Built-in, powerful for vim users
- **git mergetool**: Generic tool launcher

### GUI Tools
- **Meld**: Cross-platform, visual diff/merge
- **KDiff3**: Three-way merge tool
- **P4Merge**: Perforce visual merge tool
- **Beyond Compare**: Commercial, powerful
- **VS Code**: Built-in merge conflict UI

### IDE Integration
- **VS Code**: Inline conflict resolution
- **IntelliJ/WebStorm**: Smart merge features
- **GitKraken**: Visual merge conflict resolution

## Notes

- Always understand what both sides are trying to achieve
- When in doubt, ask the authors of the conflicting changes
- Test thoroughly after resolving conflicts
- Use rerere to avoid resolving same conflict twice
- Keep commits small to minimize conflict potential
- Communicate with team about large refactorings
- Use feature branches and merge frequently
- Consider using merge strategies (ours, theirs, recursive)
- Document resolution decisions for complex conflicts
