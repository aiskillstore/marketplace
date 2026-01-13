# Worktree Operations Guide

Detailed step-by-step instructions for each worktree operation.

## CREATE Operations

**When user wants to create a worktree:**

### Step 1: Extract information
- **Branch name** (required) - The git branch to create the worktree from
- **Port offset** (optional) - Custom port offset, defaults to auto-calculated

### Step 2: Invoke command
```
/create_worktree <branch-name> [port-offset]
```

### Step 3: What happens automatically
The command handles:
- Creates git worktree in `trees/<branch-name>`
- Configures unique ports (auto-calculated if offset not provided)
- Sets up all environment files (.env, .claude/settings.json)
- Installs dependencies (npm/bun install)
- Starts services in background (server + client)
- Provides access URLs

### Step 4: Share results with user
Include:
- Dashboard URL (e.g., http://localhost:5183/dashboard)
- Configured ports (server + client)
- How to access the running services
- Location of worktree directory

---

## LIST Operations

**When user wants to see worktrees:**

### Step 1: Invoke command
```
/list_worktrees
```

### Step 2: What the command shows
The output includes:
- All existing worktrees with their paths
- Port configuration for each (server + client)
- Service status (running/stopped with PIDs)
- Access URLs for each worktree
- Quick action commands for management

### Step 3: Share the overview with user
Highlight:
- Which worktrees are currently running
- How to access each one
- Any issues or conflicts

---

## REMOVE Operations

**When user wants to remove a worktree:**

### Step 1: Extract information
- **Branch name** (required) - The name of the worktree to remove

### Step 2: Invoke command
```
/remove_worktree <branch-name>
```

### Step 3: What happens automatically
The command handles:
- Stops running services (server + client)
- Kills processes on worktree ports
- Removes git worktree
- Cleans up directories
- Validates complete removal
- Reports success or any issues

### Step 4: Confirm removal with user
Share:
- Confirmation that worktree was removed
- Services that were stopped
- Any cleanup actions performed
