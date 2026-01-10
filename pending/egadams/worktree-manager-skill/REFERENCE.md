# Worktree Quick Reference

Technical details, command syntax, and configuration reference.

## Command Syntax

### Create Worktree
```bash
/create_worktree <branch-name> [port-offset]
```

**Parameters:**
- `branch-name` (required) - Name of the git branch
- `port-offset` (optional) - Port offset number (default: auto-calculated)

**Example:**
```bash
/create_worktree feature-auth
/create_worktree hotfix-bug 3
```

---

### List Worktrees
```bash
/list_worktrees
```

**Parameters:** None

**Output includes:**
- Worktree paths
- Port configurations
- Service status with PIDs
- Access URLs
- Quick commands

---

### Remove Worktree
```bash
/remove_worktree <branch-name>
```

**Parameters:**
- `branch-name` (required) - Name of the worktree to remove

**Example:**
```bash
/remove_worktree feature-auth
```

---

## Port Allocation

### Port Calculation Formula
```
SERVER_PORT = 4000 + (offset * 10)
CLIENT_PORT = 5173 + (offset * 10)
```

### Port Map

| Environment | Offset | Server Port | Client Port |
|-------------|--------|-------------|-------------|
| Main Repo   | 0      | 4000        | 5173        |
| Worktree 1  | 1      | 4010        | 5183        |
| Worktree 2  | 2      | 4020        | 5193        |
| Worktree 3  | 3      | 4030        | 5203        |
| Worktree 4  | 4      | 4040        | 5213        |
| Worktree 5  | 5      | 4050        | 5223        |

### Auto-calculated Offsets
When no port offset is specified, the system:
1. Lists existing worktrees
2. Finds highest used offset
3. Increments by 1
4. Uses that as the new offset

---

## Directory Structure

### Main Repository
```
project/
├── .claude/
│   ├── settings.json
│   └── commands/
├── .env
├── server/
└── client/
```

### Worktree Structure
```
project/
└── trees/
    └── <branch-name>/
        ├── .claude/
        │   └── settings.json (isolated config)
        ├── .env (unique ports)
        ├── server/
        └── client/
```

---

## Configuration Files

### .env (Worktree-specific)
```env
VITE_SERVER_URL=http://localhost:[SERVER_PORT]
VITE_CLIENT_PORT=[CLIENT_PORT]
SERVER_PORT=[SERVER_PORT]
```

### .claude/settings.json (Worktree-specific)
```json
{
  "hooks": {
    "userPromptSubmit": {
      "script": "...",
      "env": {
        "AGENT_SERVER_URL": "http://localhost:[SERVER_PORT]"
      }
    }
  }
}
```

---

## Service Management

### What Runs in a Worktree
1. **Server** - Backend API (Express/Node)
2. **Client** - Frontend dev server (Vite)

### Background Process Management
- Services run in detached background processes
- PIDs tracked for process management
- Automatic cleanup on removal
- Force-kill on stuck processes

### Service States
- **Running** - Process active with valid PID
- **Stopped** - No process running
- **Zombie** - PID exists but process unresponsive

---

## Git Worktree Fundamentals

### What is a Git Worktree?
A git worktree is an additional working directory attached to the same repository. Multiple worktrees can exist simultaneously, each checked out to different branches.

### Benefits
- Work on multiple branches simultaneously
- No need to stash/switch branches
- Isolated development environments
- Test multiple features in parallel

### Limitations
- Each branch can only be checked out in one worktree
- Worktrees share git history/objects
- Disk space required for each copy

---

## Isolation Features

Each worktree has:

| Feature | Isolation Level | Notes |
|---------|----------------|-------|
| **File System** | Complete | Separate working directory |
| **Ports** | Complete | Unique port allocation |
| **Configuration** | Complete | Own .env and settings.json |
| **Database** | Configurable | Can use separate DBs |
| **Dependencies** | Complete | Own node_modules |
| **Git History** | Shared | Same repository |
| **Git Config** | Shared | Same git settings |

---

## Related Capabilities

### Main Repository
- Default environment
- Uses ports 4000 and 5173
- No special setup needed
- Can run alongside worktrees

### Parallel Development
- Run main + multiple worktrees simultaneously
- Each fully isolated
- No conflicts between environments
- Test features against different bases

### Branch Preservation
- Removing a worktree doesn't delete the branch
- Branch still exists in git
- Can recreate worktree anytime
- Safe to cleanup unused worktrees

### Service Lifecycle
- Services start automatically on creation
- Run in background until removal
- Can be restarted manually if needed
- Stopped automatically on removal

---

## Best Practices

### When to Create Worktrees
✓ Testing multiple features simultaneously
✓ Reviewing PRs while working on features
✓ Hot-fixing production while developing
✓ Running integration tests in isolation

### When NOT to Create Worktrees
✗ Simple branch switching (use git checkout)
✗ Temporary file viewing (use git show)
✗ Quick edits (stash and switch)

### Cleanup Recommendations
- Remove worktrees when feature is merged
- Don't let unused worktrees accumulate
- Regular audit with `/list_worktrees`
- Free up ports for active development

### Naming Conventions
- Use descriptive branch names
- Avoid special characters
- Keep names concise
- Match branch naming scheme

---

## Technical Implementation

### Creation Process
1. Validate branch exists
2. Calculate/verify port offset
3. Create git worktree
4. Copy configuration templates
5. Update ports in configs
6. Install dependencies
7. Start services
8. Verify startup
9. Report access info

### Removal Process
1. Find processes on worktree ports
2. Kill server process
3. Kill client process
4. Remove git worktree
5. Clean up directories
6. Validate removal
7. Report results

### Status Checking
1. List git worktrees
2. Read configuration for each
3. Check if processes running
4. Verify port accessibility
5. Generate comprehensive report
