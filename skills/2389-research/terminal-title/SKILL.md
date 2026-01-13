---
name: terminal-title
description: This skill should be used to update terminal window title with context. Triggers automatically at session start via hook. Also triggers on topic changes during conversation (debugging to docs, frontend to backend). Updates title with emoji + project + current topic.
---

<!-- ABOUTME: Terminal title skill that automatically updates terminal window title -->
<!-- ABOUTME: Uses emoji from environment + Claude's project detection + current topic -->

# Terminal Title Management

## Overview

This skill updates the terminal window title to show current context:
- Work/fun emoji (from `$TERMINAL_TITLE_EMOJI` environment variable)
- Project name (intelligently detected by Claude)
- Current topic (what you're working on)

**Format:** `💼 ProjectName - Topic`

## CRITICAL: When to Invoke

**MANDATORY invocations:**
1. **Session start**: Automatically triggered by SessionStart hook. Claude must respond by setting title to "Claude Code" as default topic.
2. **Topic changes**: Claude MUST detect and invoke when user shifts to new topic.

**Topic change patterns (Claude must detect these):**
- ✅ "let's talk about X" / "can you tell me about Y" → invoke immediately
- ✅ User switches domains: debugging → documentation, frontend → backend, feature → tests
- ✅ User starts working on different module/component after sustained discussion
- ✅ User asks about completely unrelated topic after 3+ exchanges on current topic
- ❌ Follow-up questions on same topic ("add a comment to that function") → do NOT invoke
- ❌ Small refinements to current work ("make it blue") → do NOT invoke
- ❌ Clarifications about current task → do NOT invoke

**Claude's responsibility:** Actively monitor conversation flow and invoke this skill whenever topic materially shifts. Do not wait for explicit permission.

**Example titles:**
- `💼 Skills Repository - Terminal Title`
- `🎉 dotfiles - zsh config`
- `💼 OneOnOne - Firebase Config`

## Setup Requirements

**Required Permission:**

This skill runs scripts to update the terminal title. To prevent Claude from prompting for permission every time, add this to your `~/.claude/settings.json`:

**For Unix/Linux/macOS:**
```json
{
  "permissions": {
    "allow": [
      "Bash(bash *skills/scripts/set_title.sh:*)"
    ]
  }
}
```

**For Windows:**
```json
{
  "permissions": {
    "allow": [
      "Bash(pwsh *skills/scripts/set_title.ps1:*)"
    ]
  }
}
```

**Why this permission is needed:** The skill executes a script that sends terminal escape sequences silently in the background to update your window title without interrupting your workflow.

**Cross-platform support:** The plugin includes both bash scripts (`.sh`) for Unix-like systems and PowerShell scripts (`.ps1`) for Windows. The SessionStart hook automatically detects your OS and uses the appropriate script.

## Project Detection Strategy

**Primary method: Claude's intelligence**

Claude analyzes the current context to determine the project name:
- Current working directory and recent conversation
- Files read during the session
- Git repository information
- Package metadata (package.json, README.md, etc.)
- Overall understanding of what the project represents

**Key principle:** Use intelligent understanding, not just mechanical file parsing.

**Detection examples:**
- `/Users/dylanr/work/2389/skills` → "Skills Repository" (not just "skills")
- `/Users/dylanr/work/2389/oneonone/hosting` → "OneOnOne"
- `/Users/dylanr/dotfiles` → "dotfiles"
- `/Users/dylanr/projects/my-app` → "My App" (humanized from directory)

**Supporting evidence Claude checks:**
1. Git remote URL or repository directory name
2. `package.json` name field (Node.js projects)
3. First heading in README.md
4. Directory basename (last resort)

**Fallback:** If Claude cannot determine context, use current directory name.

**Always include project name** - Claude can always determine something meaningful.

## Title Formatting

**Standard format:**
```
$emoji ProjectName - Topic
```

**Component details:**

**1. Emoji (from environment):**
- Read from `$TERMINAL_TITLE_EMOJI` environment variable
- Set by zsh theme based on directory context
- Common values: 💼 (work), 🎉 (fun/personal)
- Fallback: Use 🎉 if variable not set

**2. Project Name (from Claude's detection):**
- Human-friendly name, not slug format
- Proper capitalization (e.g., "OneOnOne" not "oneonone")
- Always present (use directory name as minimum)

**3. Topic (from invocation context):**
- Short description of current work (2-4 words)
- Provided when skill is invoked
- Examples: "Terminal Title", "Firebase Config", "CSS Refactor"

**Script usage:**
```bash
bash scripts/set_title.sh "ProjectName" "Topic"
```

**Note:** The script automatically reads emoji from environment and handles terminal escape sequences.

**Edge cases:**
- No `$TERMINAL_TITLE_EMOJI`: Use 🎉 as default
- Very long project/topic: Let terminal handle truncation naturally
- Empty topic: Use "Claude Code" as default

## Workflow

**When Claude detects a topic change (or session start), immediately invoke this workflow:**

Follow these steps to update the terminal title:

**Step 1: Determine project name**

Use Claude's understanding of the current codebase and context to determine the project name. Check:
- What you know about this project from conversation and files
- Git repository name/remote URL
- package.json name field (if Node.js project)
- README.md first heading
- Directory basename (minimum fallback)

Generate a human-friendly name (e.g., "Skills Repository" not "skills").

**Step 2: Get topic from context**

The topic should come from:
- Invocation parameter (if provided explicitly)
- Current conversation context (what user is working on)
- Default to "Claude Code" for session start

**Step 3: Detect operating system**

Before executing the script, detect the operating system:

```bash
# Check if running on Windows (check for common Windows indicators)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    OS="unix"
fi
```

**Step 4: Execute title update script (cross-platform)**

Find the skill base directory (available in the skill loading message) and execute the appropriate script based on OS:

**For Unix/Linux/macOS:**
```bash
bash <skill-base-dir>/scripts/set_title.sh "Project Name" "Topic"
```

**For Windows:**
```bash
pwsh -NoProfile -ExecutionPolicy Bypass -File <skill-base-dir>/scripts/set_title.ps1 "Project Name" "Topic"
```

The scripts handle:
- Reading emoji from `$TERMINAL_TITLE_EMOJI` (Unix) or `$env:TERMINAL_TITLE_EMOJI` (Windows)
- Sanitizing inputs
- Formatting and sending terminal escape sequences

Execute this command silently using the Bash tool (pre-approved via permissions).

**Step 5: Done**

Title updated silently. Continue responding to user without mentioning the title update unless they ask about it.

## Examples

### Example 1: Session Start in Skills Repository

**Context:** User starts Claude Code in `/Users/dylanr/work/2389/skills`

**Environment:** `TERMINAL_TITLE_EMOJI=💼`

**Execution:**
1. Project: "Skills Repository" (Claude's knowledge)
2. Topic: "Claude Code" (session start default)
3. Command: `bash /Users/dylanr/work/2389/claude-plugins/terminal-title/skills/scripts/set_title.sh "Skills Repository" "Claude Code"`

**Result:** Terminal title shows `💼 Skills Repository - Claude Code` (script reads emoji from environment)

---

### Example 2: Topic Change Detection

**Context:** Conversation shifts from "terminal title implementation" to "rare VWs"

**Claude's detection:** User asked "can you tell me about rare vws?" - this is a clear topic shift

**Environment:** `TERMINAL_TITLE_EMOJI=🎉`

**Claude's action:**
1. Detect topic change (from terminal implementation to VWs)
2. Invoke terminal-title skill workflow
3. Project: "Home" (current directory basename)
4. Topic: "Rare VWs" (from new conversation direction)
5. Command: `bash <skill-base-dir>/scripts/set_title.sh "Home" "Rare VWs"`
6. Continue answering user's question about rare VWs

**Result:** Terminal title silently updates to `🎉 Home - Rare VWs` (script reads emoji from environment)

---

### Example 3: Personal Project Without Environment Variable

**Context:** User working in `~/projects/dotfiles` directory

**Environment:** `TERMINAL_TITLE_EMOJI` not set

**Execution:**
1. Project: "dotfiles" (from directory)
2. Topic: "zsh config" (from conversation)
3. Command: `bash <skill-base-dir>/scripts/set_title.sh "dotfiles" "zsh config"`

**Result:** Terminal title shows `🎉 dotfiles - zsh config` (script uses 🎉 as fallback when TERMINAL_TITLE_EMOJI not set)

---

### Example 4: Different Project Context

**Context:** User working in `/Users/dylanr/work/2389/oneonone/hosting`

**Environment:** `TERMINAL_TITLE_EMOJI=💼`

**Execution:**
1. Project: "OneOnOne" (Claude knows this project name)
2. Topic: "Firebase Config" (from conversation)
3. Command: `bash <skill-base-dir>/scripts/set_title.sh "OneOnOne" "Firebase Config"`

**Result:** Terminal title shows `💼 OneOnOne - Firebase Config` (script reads emoji from environment)

---

### Example 5: Windows User Session Start

**Context:** Windows user starts Claude Code in `C:\Users\Nat\projects\my-app`

**Environment:** `$env:TERMINAL_TITLE_EMOJI=💻` (Windows environment variable)

**OS Detection:** Claude detects Windows via `$OSTYPE` check

**Execution:**
1. Project: "My App" (from directory name, humanized)
2. Topic: "Claude Code" (session start default)
3. Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File <skill-base-dir>/scripts/set_title.ps1 "My App" "Claude Code"`

**Result:** Terminal title shows `💻 My App - Claude Code` (PowerShell script reads emoji from `$env:TERMINAL_TITLE_EMOJI`)

**Note:** The SessionStart hook automatically detected Windows and invoked the PowerShell version of the script instead of the bash version.
