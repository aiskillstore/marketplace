---
name: ghe-thread-manager
description: |
  Use this skill when the user expresses ANY intent related to issue/thread management:

  - Switching issues: "let's work on X", "switch to #Y", "go to the auth issue"
  - Checking status: "what are we working on?", "current issue?", "status?"
  - Background work: "what's in background?", "any features ready?", "check progress"
  - Starting development: "implement X", "add feature", "fix bug Y", "build a..."
  - Joining reviews: "let me see the review", "check that feature", "join #X"
  - Pausing/resuming: "pause this", "come back later", "resume #X"
  - Stopping transcription: "stop tracking", "don't record this", "private mode"
  - Resuming last session: "what were we working on?", "resume last issue", "continue where we left off"
  - Any natural expression of wanting to change focus or check work status

  This skill interprets natural language - users should NOT memorize commands.
  For the full GHE workflow protocol, see skill: github-elements-tracking
---

## IRON LAW: User Specifications Are Sacred

**THIS LAW IS ABSOLUTE AND ADMITS NO EXCEPTIONS.**

1. **Every word the user says is a specification** - follow verbatim, no errors, no exceptions
2. **Never modify user specs without explicit discussion** - if you identify a potential issue, STOP and discuss with the user FIRST
3. **Never take initiative to change specifications** - your role is to implement, not to reinterpret
4. **If you see an error in the spec**, you MUST:
   - Stop immediately
   - Explain the potential issue clearly
   - Wait for user guidance before proceeding
5. **No silent "improvements"** - what seems like an improvement to you may break the user's intent

**Violation of this law invalidates all work produced.**

## Background Agent Boundaries

When running as a background agent, you may ONLY write to:
- The project directory and its subdirectories
- The parent directory (for sub-git projects)
- ~/.claude (for plugin/settings fixes)
- /tmp

Do NOT write outside these locations.

---

## GHE_REPORTS Rule (MANDATORY)

**ALL reports MUST be posted to BOTH locations:**
1. **GitHub Issue Thread** - Full report text (NOT just a link!)
2. **GHE_REPORTS/** - Same full report text (FLAT structure, no subfolders!)

**Report naming:** `<TIMESTAMP>_<title or description>_(<AGENT>).md`
**Timestamp format:** `YYYYMMDDHHMMSSTimezone`

**ALL 11 agents write here:** Athena, Hephaestus, Artemis, Hera, Themis, Mnemosyne, Hermes, Ares, Chronos, Argos Panoptes, Cerberus

**REQUIREMENTS/** is SEPARATE - permanent design documents, never deleted.

**Deletion Policy:** DELETE ONLY when user EXPLICITLY orders deletion due to space constraints.

---

# GHE Thread Manager

You are Claude. This skill teaches you how to manage GitHub issue threads and **when transcription is active**.

---

## CRITICAL: Transcription Rules

**Transcription = posting conversation exchanges to GitHub issue**

### The Golden Rule

```
current_issue = NULL  →  Transcription OFF  →  Chat freely, nothing posted
current_issue = N     →  Transcription ON   →  ALL exchanges posted to Issue #N
```

---

## MANDATORY: Always Notify User of Transcription State

**THIS IS NON-NEGOTIABLE. You MUST inform the user whenever transcription state changes.**

### Why This Matters

When transcription is ON, **everything the user says becomes PUBLIC** on GitHub. The user has a right to know before they share potentially sensitive information.

### Required Notifications

| Event | You MUST Say |
|-------|--------------|
| **Transcription turns ON** | "Transcription is now ACTIVE. Everything we discuss will be posted to Issue #N on GitHub." |
| **Transcription turns OFF** | "Transcription is now OFF. Our conversation is private." |
| **Switching issues** | "Switching transcription from Issue #OLD to Issue #NEW. Our conversation will now be posted to #NEW." |
| **Session resumes with active issue** | "Resuming session. Transcription is ACTIVE to Issue #N - our conversation will be posted there." |

### Visual Indicators (Use These)

When transcription is **ON**:
```
[TRANSCRIPTION ACTIVE - Issue #N]
```

When transcription is **OFF**:
```
[PRIVATE CHAT - No transcription]
```

### Never Assume User Knows

- **Always** announce when turning transcription ON
- **Always** announce when turning transcription OFF
- **Always** remind user if they might have forgotten (e.g., after a long pause)
- **Never** silently change transcription state

---

### Transcription State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│                    STATE: NO ISSUE SELECTED                      │
│                                                                  │
│  current_issue: null                                            │
│  Transcription: OFF                                             │
│                                                                  │
│  User and Claude chat normally.                                 │
│  NOTHING is posted to GitHub.                                   │
│  This is the DEFAULT starting state.                            │
│                                                                  │
│  Actions possible:                                              │
│  • "implement X" → Create background thread, STAY in this state │
│  • "work on #42" → TRANSITION to Issue Selected state          │
│  • "check status" → Report no active issue                      │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
                    User says: "work on #42"
                    User says: "let's discuss issue 42"
                    User says: "join review #99"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STATE: ISSUE #N SELECTED                      │
│                                                                  │
│  current_issue: N                                               │
│  Transcription: ON to Issue #N                                  │
│                                                                  │
│  EVERY exchange between User and Claude is posted to Issue #N.  │
│  This creates a permanent record in GitHub.                     │
│                                                                  │
│  Actions possible:                                              │
│  • "implement X" → Create background thread, STAY on #N         │
│  • "switch to #50" → Change to #50, transcription follows       │
│  • "stop tracking" → TRANSITION back to No Issue state          │
│  • "go back" → Return to previous issue (if any)                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Behaviors

| Scenario | Transcription State | What Happens |
|----------|---------------------|--------------|
| **Fresh start** | OFF | User chats with Claude, nothing posted |
| **User says "work on #42"** | ON → #42 | All exchanges now posted to #42 |
| **User says "implement X"** (no issue) | STAYS OFF | Background thread created, main chat stays private |
| **User says "implement X"** (on #42) | STAYS ON → #42 | Background thread created, main chat stays on #42 |
| **User says "switch to #50"** | ON → #50 | Transcription moves to #50 |
| **User says "join review #99"** | ON → #99 | Transcription moves to #99 |
| **User says "stop tracking"** | OFF | Back to private chat |
| **Session starts with existing issue** | ON → that issue | Resume transcription |

### CRITICAL: Background Threads Don't Change Main State

When user asks to implement/build/fix something:

1. **Create background thread** (agents handle it)
2. **DO NOT change current_issue**
3. **Main conversation continues** in its current state

```
User on #42: "implement dark mode"
                │
                ├── Create Issue #99 for dark mode (background)
                │   Athena writes requirements
                │   Hephaestus implements
                │   (all in background)
                │
                └── Main conversation STAYS on #42
                    Transcription CONTINUES to #42
                    User can keep chatting with Claude
```

---

## Execution Guide

### 1. Check Current Transcription State

**ALWAYS check state before any operation:**

```bash
CURRENT_ISSUE=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)
```

- If empty/null: Transcription is OFF
- If number: Transcription is ON to that issue

### 2. Start Transcription (User Selects Issue)

When user wants to work on a specific issue:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" set-issue <NUMBER>
```

**MANDATORY - Tell the user IMMEDIATELY:**
> "[TRANSCRIPTION ACTIVE - Issue #N]
>
> Transcription is now ACTIVE. Everything we discuss will be posted to Issue #N on GitHub.
>
> Say 'stop tracking' or 'go private' at any time to disable transcription."

**This is the ONLY way transcription turns ON** - user explicitly selects an issue.

**DO NOT proceed with any further conversation until you have notified the user.**

### 3. Switch Issues (Change Transcription Target)

When user wants to switch to a different issue:

```bash
# Remember current for "go back" functionality
PREVIOUS=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)

# Switch to new issue
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" set-issue <NEW_NUMBER>
```

**MANDATORY - Tell the user IMMEDIATELY:**
> "[SWITCHING TRANSCRIPTION]
>
> Switching from Issue #PREVIOUS to Issue #NEW. Our conversation will now be posted to #NEW on GitHub.
>
> Say 'go back' to return to #PREVIOUS."

### 4. Stop Transcription (User Wants Privacy)

When user wants to stop recording:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" clear-issue
```

**MANDATORY - Tell the user IMMEDIATELY:**
> "[TRANSCRIPTION OFF]
>
> Transcription stopped. Our conversation is now private - nothing will be posted to GitHub."

### 5. Create Background Development Thread

When user wants to implement/build/fix something:

```bash
# Get current issue (may be null)
PARENT=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)

# Create background thread
bash "${CLAUDE_PLUGIN_ROOT}/scripts/create_feature_thread.py" <feature|bug> "<title>" "<description>" "${PARENT:-}"
```

**IMPORTANT:** This does NOT change current_issue. Main conversation continues as before.

**Tell the user:**
> "Created Issue #N for [feature/bug]. Athena is writing requirements, then agents will implement it. I'll notify you when ready for review. We can continue our conversation [here on #PARENT / privately]."

### 6. Check Background Thread Status

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/check_review_ready.py"
```

Report status without changing transcription state.

### 7. Join a Background Thread (Switch Context)

When user wants to participate in a feature thread:

```bash
# This IS a switch - transcription moves to the feature thread
PREVIOUS=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" set-issue <FEATURE_NUMBER>
```

**MANDATORY - Tell the user IMMEDIATELY:**
> "[TRANSCRIPTION ACTIVE - Issue #FEATURE]
>
> Joined Issue #FEATURE. Everything we discuss will now be posted to this thread on GitHub.
>
> Say 'back to #PREVIOUS' when done to return."

---

## Edge Cases

### Edge Case 1: Session Start with Existing Issue

On session start, check if there's a saved current_issue:

```bash
CURRENT=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)
```

- If set: **IMMEDIATELY** inform user transcription will resume to that issue
- If not set: Transcription is OFF, chat privately (no notification needed)

**MANDATORY - Tell the user IMMEDIATELY (if issue exists):**
> "[TRANSCRIPTION ACTIVE - Issue #N]
>
> Resuming session with transcription ACTIVE to Issue #N. Everything we discuss will be posted there.
>
> Say 'stop tracking' to disable transcription."

**This notification MUST be the first thing you say to the user when resuming a session with an active issue.**

### Edge Case 2: User Creates Feature Without Main Issue

User hasn't selected an issue but asks to implement something:

```bash
# PARENT will be empty
PARENT=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)

# Create without parent link
bash "${CLAUDE_PLUGIN_ROOT}/scripts/create_feature_thread.py" feature "Dark mode" "Add dark mode toggle" ""
```

- Background thread created
- Main conversation stays private (no issue set)
- When feature reaches REVIEW, user can choose to join

**Tell the user:**
> "Created Issue #N for dark mode. Agents will handle it in background. Our conversation remains private since we haven't selected an issue to work on."

### Edge Case 3: User Wants to Return to Previous Issue

Save previous issue when switching:

```bash
# When switching FROM #42 TO #99
echo "42" > /tmp/ghe_previous_issue

# Later, when user says "go back"
PREVIOUS=$(cat /tmp/ghe_previous_issue 2>/dev/null)
if [[ -n "$PREVIOUS" ]]; then
    bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" set-issue "$PREVIOUS"
fi
```

### Edge Case 4: User Asks "What Are We Working On?"

```bash
CURRENT=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-issue)

if [[ -z "$CURRENT" || "$CURRENT" == "null" ]]; then
    echo "No issue selected. Transcription is OFF. Chat is private."
else
    echo "Working on Issue #$CURRENT. Transcription is ON."
fi
```

### Edge Case 5: User Says "Stop" or "Private"

Detect intent to disable transcription:
- "stop tracking" / "stop transcribing"
- "go private" / "private mode"
- "don't record this"
- "off the record"

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" clear-issue
```

### Edge Case 6: User Asks "What Were We Working On Last Time?"

When user wants to resume a previous session but doesn't remember the issue number:
- "what were we working on?"
- "resume last issue"
- "continue where we left off"
- "what was that issue we discussed?"

**The `auto_transcribe.py` script automatically tracks the last active issue.** When you clear or switch issues, it saves the previous one to `.claude/last_active_issue.json`.

**Check Last Issue:**

```bash
# Show the last active issue details
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" get-last-issue

# Output:
# Last Active Issue Found
#   Issue:       #42
#   Title:       Implement dark mode toggle
#   Last Active: 2025-01-15T10:30:00Z
```

**Resume Last Issue (One Command):**

```bash
# Automatically resume transcription to the last active issue
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" resume
```

This is equivalent to:
```bash
LAST=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" last-issue-number)
bash "${CLAUDE_PLUGIN_ROOT}/scripts/auto_transcribe.py" set-issue "$LAST"
```

**JSON File Structure** (automatically maintained):

```json
{
  "issue": 42,
  "title": "Implement dark mode toggle",
  "last_active": "2025-01-15T10:30:00Z"
}
```

**Automatic Tracking:**
- When you call `clear-issue`: Previous issue is saved automatically
- When you call `set-issue N` while on another issue: Previous issue is saved automatically
- No manual saving needed!

**Fallback - Search by User Avatar:**

If `last_active_issue.json` doesn't exist (e.g., first session or file deleted), search GitHub:

```bash
# Get GitHub username
GITHUB_USER="${GITHUB_OWNER:-$(gh api user --jq .login 2>/dev/null || echo "")}"

# List recent issues with comments
RECENT_ISSUES=$(gh issue list --state open --json number,title,updatedAt --limit 20)

# For each issue, check if it has USER avatar in comments
for issue_num in $(echo "$RECENT_ISSUES" | jq -r '.[].number'); do
    COMMENTS=$(gh issue view "$issue_num" --json comments --jq '.comments[].body')

    if echo "$COMMENTS" | grep -q "avatars.githubusercontent.com/${GITHUB_USER}"; then
        echo "Found: Issue #$issue_num"
        LAST_CONVERSATION="$issue_num"
        break  # Most recently updated is first
    fi
done
```

**Response Template:**

If found:
> "Your last conversation was on Issue #N: [Title]. Would you like to resume? (This will turn transcription ON)"

If not found:
> "I couldn't find a previous conversation thread. Would you like to start working on a specific issue?"

---

## Natural Language Intent Mapping

| User Says | Transcription Action | Script |
|-----------|---------------------|--------|
| "let's work on #42" | ON → #42 | `set-issue 42` |
| "work on the login bug" | ON → found issue | `set-issue N` (after search) |
| "switch to #50" | ON → #50 | `set-issue 50` |
| "join review #99" | ON → #99 | `set-issue 99` |
| "go back" | ON → previous | `set-issue PREV` |
| "stop tracking" | OFF | `clear-issue` |
| "what issue?" | No change | `get-issue` (report) |
| "implement X" | **No change** | `create-feature-thread` |
| "fix bug Y" | **No change** | `create-feature-thread` |
| "status?" | No change | `check-review-ready` |
| "what were we working on?" | Report last | `get-last-issue` |
| "resume last issue" | ON → last found | `resume` |
| "continue where we left off" | ON → last found | `resume` |

---

## Issue Resolution (Fuzzy Matching)

When user describes issue by name, not number:

```bash
# Search GitHub
gh issue list --search "login" --json number,title --limit 5
```

**Decision Tree:**
1. **One match** → Use that issue number
2. **Multiple matches** → Ask user to clarify
3. **No matches** → Ask if they want to create new issue

---

## Communication Templates (MANDATORY - Use These Exact Phrases)

**You MUST use these notifications. They are not optional.**

### When Transcription Turns ON (MUST SAY)
> "[TRANSCRIPTION ACTIVE - Issue #N]
>
> Transcription is now ACTIVE. Everything we discuss will be posted to Issue #N: [Title] on GitHub.
>
> Say 'stop tracking' or 'go private' at any time to disable transcription."

### When Transcription Target Changes (MUST SAY)
> "[SWITCHING TRANSCRIPTION]
>
> Switching from Issue #OLD to Issue #NEW. Our conversation will now be posted to #NEW on GitHub.
>
> Say 'go back' to return to #OLD."

### When Transcription Turns OFF (MUST SAY)
> "[TRANSCRIPTION OFF]
>
> Transcription stopped. Our conversation is now private - nothing will be posted to GitHub."

### When Session Starts with Active Issue (MUST SAY)
> "[TRANSCRIPTION ACTIVE - Issue #N]
>
> Resuming session with transcription ACTIVE to Issue #N. Everything we discuss will be posted there.
>
> Say 'stop tracking' to disable transcription."

### When Background Thread Created (No Main Issue)
> "Created Issue #N for [feature]. Agents will handle it in background.
>
> [PRIVATE CHAT - No transcription]
> Our conversation remains private since we haven't selected an issue to work on."

### When Background Thread Created (Has Main Issue)
> "Created Issue #N for [feature]. Agents will handle it in background.
>
> [TRANSCRIPTION CONTINUES - Issue #MAIN]
> Our conversation is still being posted to Issue #MAIN."

### When Feature Ready for Review
> "Issue #N ([feature]) is ready for review! Hera is conducting the code review.
>
> Would you like to join? **Warning: This will switch transcription to Issue #N.**"

---

## Scripts Reference

| Script | Purpose | Changes Transcription? |
|--------|---------|------------------------|
| `auto_transcribe.py set-issue N` | Select issue | YES - turns ON to #N |
| `auto_transcribe.py get-issue` | Check current | NO |
| `auto_transcribe.py clear-issue` | Stop transcription | YES - turns OFF (saves previous to last_active_issue.json) |
| `auto_transcribe.py get-last-issue` | Show last active issue | NO |
| `auto_transcribe.py last-issue-number` | Get issue number only (for scripting) | NO |
| `auto_transcribe.py resume` | Resume last active issue | YES - turns ON to last issue |
| `create_feature_thread.py` | Create background thread | NO - main unchanged |
| `check_review_ready.py` | Check background status | NO |

---

## Summary: The Rules

1. **Default state is OFF** - No transcription until user selects an issue
2. **User controls transcription** - Only user actions turn it ON/OFF
3. **Background threads are independent** - Creating them doesn't affect main transcription
4. **Switching issues = moving transcription** - Only one target at a time
5. **ALWAYS NOTIFY THE USER** - This is mandatory, not optional

### The Cardinal Rule

```
EVERY transcription state change → IMMEDIATE user notification
```

**Before transcription turns ON:**
> "Transcription is now ACTIVE. Everything we discuss will be posted to Issue #N on GitHub."

**Before transcription turns OFF:**
> "Transcription is now OFF. Our conversation is private."

**Never** change transcription state silently. The user must **always** know whether their words are being made public.

**Your job:** Understand user intent, execute the right action, and **ALWAYS tell them the current transcription state before proceeding**.
