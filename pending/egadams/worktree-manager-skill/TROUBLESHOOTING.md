# Worktree Troubleshooting Guide

Common issues and their solutions when managing worktrees.

## Issue 1: "My worktree isn't working"

### Symptoms
- User can't access the worktree
- Services appear down
- URLs not responding

### Diagnosis Steps
1. Run `/list_worktrees` to check status
2. Look for service status (running/stopped)
3. Check port configuration

### Solutions
- If services are stopped, recreate the worktree
- If ports conflict, use a different port offset
- Check if processes crashed (look at PIDs)

### What to tell the user
> Let me check the status of your worktrees...
> [run /list_worktrees]
> I see the issue - [explain problem and solution]

---

## Issue 2: "I can't create a worktree"

### Symptoms
- Creation command fails
- Error messages about existing worktrees
- Port conflicts

### Common Causes
1. **Worktree already exists** - Branch already has a worktree
2. **Invalid branch name** - Branch doesn't exist in repository
3. **Port already in use** - Another service using the ports

### Solutions
1. Check existing worktrees: `/list_worktrees`
2. Verify branch exists: `git branch -a`
3. Try a different port offset if ports conflict
4. Remove old worktree first if recreating

### What to tell the user
> It looks like [diagnosis]. Let me [solution approach].

---

## Issue 3: "How do I access my worktree?"

### User doesn't know the URLs

### Solution
1. Run `/list_worktrees` to see access URLs
2. Show the Dashboard URL for their specific worktree
3. Explain the port scheme

### What to tell the user
> Here are the access URLs for your worktree:
> - Dashboard: http://localhost:[CLIENT_PORT]/dashboard
> - Server API: http://localhost:[SERVER_PORT]
> - Client: http://localhost:[CLIENT_PORT]

---

## Issue 4: "Services won't stop"

### Symptoms
- Processes still running after removal attempt
- Ports still in use
- Can't recreate worktree due to conflicts

### Solutions
1. Use `/remove_worktree` which force-kills processes
2. If still stuck, run `/list_worktrees` to see PIDs
3. Can manually kill processes if needed: `kill -9 <PID>`

### What to tell the user
> I'll use the remove command which will force-stop all services...
> [run /remove_worktree]

---

## Issue 5: "Port conflicts"

### Symptoms
- Error about port already in use
- Services fail to start
- Multiple worktrees on same ports

### Solutions
1. List existing worktrees to see port allocation
2. Use explicit port offset when creating: `/create_worktree branch-name 4`
3. Remove unused worktrees to free up ports

### Port Allocation Reference
- Main: 4000, 5173
- Offset 1: 4010, 5183
- Offset 2: 4020, 5193
- Offset 3: 4030, 5203
- Pattern: BASE + (offset * 10)

---

## Issue 6: "Worktree directory exists but not listed"

### Symptoms
- Directory in `trees/` folder
- Not showing in `/list_worktrees`
- Git doesn't recognize it

### Likely Cause
Incomplete removal or manual deletion

### Solutions
1. Check `git worktree list` to see git's view
2. If orphaned, remove directory manually: `rm -rf trees/branch-name`
3. If needed, prune git worktrees: `git worktree prune`

### What to tell the user
> It looks like there's an orphaned worktree. Let me clean it up...

---

## Issue 7: "Dependencies not installing"

### Symptoms
- Services fail to start
- Missing modules errors
- Build failures

### Solutions
1. Check the creation output for install errors
2. Manually run install in worktree: `cd trees/branch-name && npm install`
3. Verify package.json exists in worktree

---

## Issue 8: "Database issues in worktree"

### Symptoms
- Database errors
- Data conflicts between main and worktree
- Migrations not running

### Note
Each worktree should have isolated database configuration. Check:
1. .env file in worktree has unique DB settings
2. Database name includes branch identifier
3. Migrations ran successfully during creation

---

## General Debugging Approach

When user reports any issue:

1. **Gather information**
   - Run `/list_worktrees` first
   - Ask which specific worktree
   - Ask what they were trying to do

2. **Diagnose**
   - Check service status
   - Verify port configuration
   - Look for error patterns

3. **Resolve**
   - Use appropriate command
   - Verify fix worked
   - Explain what happened

4. **Prevent**
   - Suggest best practices
   - Recommend cleanup of unused worktrees
   - Note any configuration issues

---

## Quick Diagnostic Checklist

When troubleshooting, check:

- ✓ Does worktree directory exist? (`ls trees/`)
- ✓ Is git aware of it? (`git worktree list`)
- ✓ Are services running? (`/list_worktrees`)
- ✓ Are ports available? (check PIDs)
- ✓ Is configuration correct? (check .env, settings.json)
- ✓ Did dependencies install? (check node_modules)
