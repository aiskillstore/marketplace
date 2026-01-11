# Worktree Usage Examples

Real-world examples demonstrating how to handle different worktree management scenarios.

## Example 1: Create a new worktree

**User says:** "Create a worktree for the feature-authentication branch"

**Your action:**
1. Use SlashCommand: `/create_worktree feature-authentication`
2. Share the output showing access URLs and ports

**Result:** New worktree created at `trees/feature-authentication` with services running

**Sample response to user:**
> I've created a new worktree for the `feature-authentication` branch. It's running at:
> - Dashboard: http://localhost:5183/dashboard
> - Server: http://localhost:4010
> - Client: http://localhost:5183

---

## Example 2: Create with specific port offset

**User says:** "Set up a parallel environment on branch hotfix-security with port offset 3"

**Your action:**
1. Use SlashCommand: `/create_worktree hotfix-security 3`
2. Share output (will use ports 4030, 5203)

**Result:** Worktree created with custom ports

**Sample response to user:**
> Created worktree for `hotfix-security` with port offset 3:
> - Server: http://localhost:4030
> - Client: http://localhost:5203

---

## Example 3: List all worktrees

**User says:** "What worktrees do I have?"

**Your action:**
1. Use SlashCommand: `/list_worktrees`
2. Share the comprehensive overview

**Result:** User sees all worktrees with their configuration and status

---

## Example 4: Check worktree status

**User says:** "Show me the status of my worktrees"

**Your action:**
1. Use SlashCommand: `/list_worktrees`
2. Highlight key information: running services, ports in use, access URLs

**Result:** User sees which worktrees are active and their details

**What to highlight:**
- Which services are running vs stopped
- Port conflicts if any
- Quick access URLs
- PIDs of running processes

---

## Example 5: Remove a worktree

**User says:** "Delete the feature-auth worktree"

**Your action:**
1. Use SlashCommand: `/remove_worktree feature-auth`
2. Confirm removal completed

**Result:** Worktree removed, services stopped, directory cleaned up

**Sample response to user:**
> Successfully removed the `feature-auth` worktree:
> - Stopped all running services
> - Cleaned up directories
> - Worktree has been removed

---

## Example 6: Remove with different wording

**User says:** "Clean up the old-branch worktree, I don't need it anymore"

**Your action:**
1. Use SlashCommand: `/remove_worktree old-branch`
2. Share confirmation

**Result:** Worktree removed successfully

**Note:** Recognize variations: "clean up", "don't need", "remove", "delete" all indicate removal.

---

## Example 7: Multiple operations workflow

**User says:** "Show me my worktrees, then create a new one for refactor-api"

**Your action:**
1. Use SlashCommand: `/list_worktrees`
2. Share current worktrees
3. Use SlashCommand: `/create_worktree refactor-api`
4. Share new worktree details

**Result:** User sees existing worktrees, then gets a new one created

**Sample response to user:**
> Here are your current worktrees:
> [list output]
>
> Now creating a new worktree for `refactor-api`...
> [creation output with URLs]

---

## Example 8: Managing parallel environments

**User says:** "I need three worktrees for branches: feature-a, feature-b, and feature-c"

**Your action:**
1. Use SlashCommand: `/create_worktree feature-a`
2. Use SlashCommand: `/create_worktree feature-b`
3. Use SlashCommand: `/create_worktree feature-c`
4. Use SlashCommand: `/list_worktrees` (to show all three)

**Result:** Three parallel worktrees created with unique ports

**Sample response to user:**
> Created three worktrees for parallel development:
>
> 1. **feature-a**
>    - Server: http://localhost:4010
>    - Client: http://localhost:5183
>
> 2. **feature-b**
>    - Server: http://localhost:4020
>    - Client: http://localhost:5193
>
> 3. **feature-c**
>    - Server: http://localhost:4030
>    - Client: http://localhost:5203
>
> All services are running and ready for development!

---

## Pattern Recognition

### Create Keywords
- "create", "new", "setup", "make", "build", "start", "initialize"
- "I need a worktree for..."
- "Set up a parallel environment..."

### List Keywords
- "list", "show", "display", "what", "which", "status", "check", "view"
- "What worktrees do I have?"
- "Show me my environments..."

### Remove Keywords
- "remove", "delete", "cleanup", "destroy", "stop", "kill", "terminate"
- "Clean up the...", "I don't need..."
- "Get rid of...", "Delete the..."
