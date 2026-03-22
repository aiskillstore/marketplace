---
name: plannotator
description: Interactive plan and diff review for AI coding agents. Visual browser UI for annotating agent plans — approve or request changes with structured feedback. Supports code review, image annotation, and auto-save to Obsidian/Bear Notes.
allowed-tools: Read Bash Write
metadata:
  tags: plan, planning, planno, plannotator, plan-review, diff-review, code-review, claude-code, opencode, annotation, visual-review, plan-review, design-review
  platforms: Claude, OpenCode, Codex, Gemini
  keyword: plan
  version: 0.9.2
  source: backnotprop/plannotator
---


# plannotator — Interactive Plan & Diff Review

> Keyword: `plan` | Source: https://github.com/backnotprop/plannotator
>
> Annotate and review AI coding agent plans visually, share with your team, send feedback with one click.
> Works with **Claude Code**, **OpenCode**, **Gemini CLI**, and **Codex CLI**.

## When to use this skill

- You want to review an AI agent's implementation plan BEFORE it starts coding
- You want to annotate a git diff after the agent makes changes
- You need a feedback loop: visually mark up what to change, then send structured feedback back
- You want to share plan reviews with teammates via a link
- You want to auto-save approved plans to Obsidian or Bear Notes

---

## Scripts (Automated Patterns)

All patterns have a corresponding script in `scripts/`. Run them directly or let the agent call them.

| Script | Pattern | Usage |
|--------|---------|-------|
| `scripts/install.sh` | CLI Install | One-command install; `--all` sets up every AI tool |
| `scripts/setup-hook.sh` | Claude Code Hook | Configure Claude Code ExitPlanMode hook |
| `scripts/setup-gemini-hook.sh` | Gemini CLI Hook | Configure Gemini CLI ExitPlanMode hook + GEMINI.md |
| `scripts/setup-codex-hook.sh` | Codex CLI Setup | Configure Codex CLI developer_instructions + prompt |
| `scripts/setup-opencode-plugin.sh` | OpenCode Plugin | Register plugin + slash commands |
| `scripts/check-status.sh` | Status Check | Verify all integrations and configuration |
| `scripts/configure-remote.sh` | Remote Mode | SSH / devcontainer / WSL configuration |
| `scripts/review.sh` | Code Review | Launch diff review UI |

---

## Pattern 1: Install

```bash
# Install CLI only (macOS / Linux / WSL)
bash scripts/install.sh

# Install CLI and get Claude Code plugin commands
bash scripts/install.sh --with-plugin

# Install CLI + configure Gemini CLI
bash scripts/install.sh --with-gemini

# Install CLI + configure Codex CLI
bash scripts/install.sh --with-codex

# Install CLI + register OpenCode plugin
bash scripts/install.sh --with-opencode

# Install CLI + all AI tool integrations at once
bash scripts/install.sh --all
```

What it does:
- Detects OS (macOS / Linux / WSL / Windows)
- Checks for Obsidian and shows install link if missing: https://obsidian.md/download
- Installs via `https://plannotator.ai/install.sh`
- Verifies install and PATH
- Optionally runs integration scripts for each AI tool
- On Windows: prints PowerShell / CMD commands to run manually

---

## Pattern 2: Hook Setup (Plan Review trigger)

```bash
# Add hook to ~/.claude/settings.json
bash scripts/setup-hook.sh

# Preview what would change (no writes)
bash scripts/setup-hook.sh --dry-run
```

What it does:
- Checks plannotator CLI is installed
- Merges `ExitPlanMode` hook into `~/.claude/settings.json` safely (backs up first)
- Skips if hook already configured
- **Restart Claude Code after running this**

### Alternative: Claude Code Plugin (no manual hook needed)

Run inside Claude Code:

```bash
/plugin marketplace add backnotprop/plannotator
/plugin install plannotator@plannotator
# IMPORTANT: Restart Claude Code after plugin install
```

---

## Pattern 3: Plan Review (Before Coding)

> Triggered automatically via hook when Claude Code exits plan mode.

When your agent finishes planning (Claude Code: `Shift+Tab×2` to enter plan mode), plannotator opens automatically:

1. **View** the agent's plan in the visual UI
2. **Annotate** with clear intent:
   - `delete` — remove risky or unnecessary step
   - `insert` — add missing step
   - `replace` — revise incorrect approach
   - `comment` — clarify constraints or acceptance criteria
3. **Submit** one outcome:
   - **Approve** → agent proceeds with implementation
   - **Request changes** → your annotations are sent back as structured feedback for replanning

---

## Pattern 4: Code Review (After Coding)

```bash
# Review all uncommitted changes
bash scripts/review.sh

# Review a specific commit
bash scripts/review.sh HEAD~1

# Review branch diff
bash scripts/review.sh main...HEAD
```

What it does:
- Checks CLI and git repo state
- Shows diff summary before opening
- Launches `plannotator review` UI
- In the UI: select line numbers to annotate, switch unified/split views, attach images

---

## Pattern 5: Remote / Devcontainer Mode

```bash
# Interactive setup (SSH, devcontainer, WSL)
bash scripts/configure-remote.sh

# View current configuration
bash scripts/configure-remote.sh --show

# Set port directly
bash scripts/configure-remote.sh --port 9999
```

What it does:
- Detects shell profile (`.zshrc`, `.bashrc`, `.profile`)
- Writes `PLANNOTATOR_REMOTE=1` and `PLANNOTATOR_PORT` to shell profile
- Shows SSH and VS Code port-forwarding instructions
- Optionally sets custom browser or share URL

Manual environment variables:

```bash
export PLANNOTATOR_REMOTE=1    # No auto browser open
export PLANNOTATOR_PORT=9999   # Fixed port for forwarding
```

| Variable | Description |
|----------|-------------|
| `PLANNOTATOR_REMOTE` | Remote mode (no auto browser open) |
| `PLANNOTATOR_PORT` | Fixed local/forwarded port |
| `PLANNOTATOR_BROWSER` | Custom browser path/app |
| `PLANNOTATOR_SHARE_URL` | Custom share portal URL |

---

## Pattern 6: Status Check

```bash
bash scripts/check-status.sh
```

Checks all of:
- CLI installed and version
- Claude Code hook in `~/.claude/settings.json` (or plugin detected)
- Gemini CLI hook in `~/.gemini/settings.json`
- Codex CLI `~/.codex/config.toml` developer_instructions
- OpenCode plugin in `opencode.json` + slash commands
- Obsidian installation
- Environment variables configured
- Git repo available for diff review

---

## Pattern 7: Gemini CLI Integration

```bash
# Configure Gemini CLI (hook + GEMINI.md instructions)
bash scripts/setup-gemini-hook.sh

# Preview what would change (no writes)
bash scripts/setup-gemini-hook.sh --dry-run

# Only update settings.json hook (skip GEMINI.md)
bash scripts/setup-gemini-hook.sh --hook-only

# Only update GEMINI.md (skip settings.json)
bash scripts/setup-gemini-hook.sh --md-only
```

What it does:
- Checks plannotator CLI is installed
- Merges `ExitPlanMode` hook into `~/.gemini/settings.json` (same format as Claude Code)
- Appends plannotator usage instructions to `~/.gemini/GEMINI.md`
- Backs up existing files before modifying

Usage in Gemini CLI after setup:

```bash
# Enter planning mode (hook fires when you exit)
gemini --approval-mode plan

# Manual plan review (validated format)
python3 -c "
import json
plan = open('plan.md').read()
print(json.dumps({'tool_input': {'plan': plan, 'permission_mode': 'acceptEdits'}}))
" | plannotator > /tmp/plannotator_feedback.txt 2>&1 &

# Code review after implementation
plannotator review
```

> **Note:** Gemini CLI supports `gemini hooks migrate --from-claude` to auto-migrate existing Claude Code hooks.

---

## Pattern 8: Codex CLI Integration

```bash
# Configure Codex CLI (developer_instructions + prompt file)
bash scripts/setup-codex-hook.sh

# Preview what would change (no writes)
bash scripts/setup-codex-hook.sh --dry-run
```

What it does:
- Adds plannotator instruction to `developer_instructions` in `~/.codex/config.toml`
- Creates `~/.codex/prompts/plannotator.md` (invoke with `/prompts:plannotator`)
- Backs up existing config before modifying

Usage in Codex CLI after setup:

```bash
# Use the plannotator agent prompt
/prompts:plannotator

# Manual plan review (validated format)
python3 -c "
import json
plan = open('plan.md').read()
print(json.dumps({'tool_input': {'plan': plan, 'permission_mode': 'acceptEdits'}}))
" | plannotator > /tmp/plannotator_feedback.txt 2>&1 &

# Code review after implementation
plannotator review HEAD~1
```

> Note: `plannotator plan -` with heredoc/echo can fail with `Failed to parse hook event from stdin`. Use the python3 JSON format above.

---

## Pattern 10: Manual Save via Export → Notes Tab

Save the current plan to Obsidian or Bear Notes at any time — without approving or denying.

### How to access

1. Click **Export** button in the plannotator UI toolbar
2. Click the **Notes** tab (not Share or Annotations)
3. You see:
   - **Obsidian** row with configured vault path and **Save** button
   - **Bear** row with **Save** button
   - **Save All** button to save both at once
4. A green dot next to each row means that integration is configured
5. Clicking **Save** shows **Saved** when complete

### When to use

- Save work-in-progress plans without committing to Approve/Deny
- Quick archive after reviewing without final decision
- Save annotated plans for team reference

### Requirements

- plannotator must be running in **hook mode** (normal Claude Code ExitPlanMode hook invocation = hook mode)
- Obsidian/Bear must be configured in Settings (⚙️) → Saving tab
- Settings are stored in **cookies** (not localStorage) and persist across restarts

> **Note:** The Notes tab uses `POST /api/save-notes` which writes directly to the vault filesystem (Obsidian) or calls `bear://x-callback-url/create` (Bear). This endpoint is only available in hook mode.

---

## Recommended Workflow

### Quick Start (all AI tools)

```bash
# 1. Install CLI + configure all AI tool integrations at once
bash scripts/install.sh --all

# 2. Verify everything
bash scripts/check-status.sh

# 3. Restart your AI tools (Claude Code, Gemini CLI, OpenCode, Codex)
```

### Claude Code (manual)

```
1. bash scripts/install.sh --with-plugin
   └─ Installs CLI + shows plugin install commands

2. bash scripts/setup-hook.sh          ← skip if using plugin
   └─ Configures automatic plan review trigger

3. bash scripts/check-status.sh
   └─ Confirm everything is ready

4. [Code with agent in plan mode → Shift+Tab×2]
   └─ plannotator opens automatically

5. bash scripts/review.sh              ← after agent finishes coding
   └─ Opens visual diff review
```

### Gemini CLI (manual)

```
1. bash scripts/install.sh
2. bash scripts/setup-gemini-hook.sh
3. gemini --approval-mode plan          ← work in plan mode
   └─ plannotator fires on exit
```

### Codex CLI (manual)

```
1. bash scripts/install.sh
2. bash scripts/setup-codex-hook.sh
3. /prompts:plannotator                 ← inside Codex session
```

---

## OpenCode Setup

```bash
# Automated (recommended)
bash scripts/setup-opencode-plugin.sh

# Or add manually to opencode.json:
```

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@plannotator/opencode@latest"]
}
```

After setup, restart OpenCode. Available slash commands:
- `/plannotator-review` — open code review UI for current git diff
- `/plannotator-annotate <file.md>` — annotate a markdown file

The `submit_plan` tool is automatically available to the agent for plan submission.

---

## Pattern 9: Obsidian Integration Setup

Auto-save approved plans to your Obsidian vault with YAML frontmatter and tags.

### Prerequisites

1. **Install Obsidian**: https://obsidian.md/download
2. **Create a Vault**: Open Obsidian → Create new vault → Choose location
   - Example: `~/Documents/Obsidian/MyVault`
3. **Verify Vault Exists**: Obsidian creates `obsidian.json` config after first vault creation

```bash
# Check Obsidian installation (macOS)
ls /Applications/Obsidian.app

# Check Obsidian config exists (vault detection depends on this)
# macOS
cat ~/Library/Application\ Support/obsidian/obsidian.json
# Linux
cat ~/.config/obsidian/obsidian.json
# Windows
cat %APPDATA%/obsidian/obsidian.json
```

### Step-by-Step Setup

```bash
# Step 1: Verify Obsidian is installed and has at least one vault
bash scripts/check-status.sh

# Step 2: Trigger a plan review (any method)
# Claude Code: Shift+Tab×2 → plan mode → exit plan mode
# Gemini CLI: gemini --approval-mode plan
# OpenCode: Agent creates a plan

# Step 3: In the plannotator UI:
#   1. Click ⚙️ (Settings gear icon)
#   2. Go to "Saving" tab
#   3. Toggle ON "Obsidian Integration"
#   4. Select your vault from dropdown (auto-detected)
#      - Or enter custom path if vault not detected
#   5. Set folder name (default: "plannotator")

# Step 4: Approve a plan to test the integration
#   - Click "Approve" in the plannotator UI
#   - Check your vault for the saved file
```

### Obsidian Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| **Vault** | Path to Obsidian vault | Auto-detected |
| **Folder** | Subfolder in vault for plans | `plannotator` |
| **Custom Path** | Manual path if auto-detect fails | - |

### Saved File Format

Files are saved with human-readable names and YAML frontmatter:

```
Filename: {Title} - {Month} {Day}, {Year} {Hour}-{Minute}{am/pm}.md
Example:  User Authentication - Feb 22, 2026 10-45pm.md
```

```yaml
---
created: 2026-02-22T22:45:30.000Z
source: plannotator
tags: [plannotator, project-name, typescript, ...]
---

[[Plannotator Plans]]

# Original plan content...
```

**Tag extraction:**
- `plannotator` — always included
- Project name — from git repo or directory
- Title words — first 3 meaningful words from H1 heading
- Languages — from code blocks (```typescript → typescript)

### Folder Organization

Organize plans within the vault using subfolders:

```
vault/plannotator/
├── approved/          ← approved plans
├── denied/            ← rejected plans
└── 2026-02/           ← monthly archive
```

Create subfolders manually (Obsidian detects them automatically):

```bash
mkdir -p ~/path/to/vault/plannotator/approved
mkdir -p ~/path/to/vault/plannotator/denied
mkdir -p ~/path/to/vault/plannotator/2026-02
```

Or write directly to any subfolder:

```bash
cp ~/.plannotator/plans/<name>-approved.md ~/path/to/vault/plannotator/approved/
```

### Bear Notes (Alternative)

If you prefer Bear Notes over Obsidian:

1. Toggle ON "Bear Notes" in Settings → Saving tab
2. Plans are saved via `bear://x-callback-url/create`
3. Tags are appended as hashtags
4. Validate callback from terminal:

```bash
open "bear://x-callback-url/create?title=Plannotator%20Check&text=Bear%20callback%20OK"
```

| Feature | Obsidian | Bear |
|---------|----------|------|
| Storage | File system | x-callback-url |
| Frontmatter | YAML | None (hashtags) |
| Platforms | macOS/Win/Linux | macOS/iOS |

### Troubleshooting

**Vault not detected:**

```bash
# 1. Check Obsidian config exists
ls ~/Library/Application\ Support/obsidian/obsidian.json  # macOS

# 2. If missing, open Obsidian and create a vault first
open /Applications/Obsidian.app

# 3. After creating vault, restart plannotator
```

**Plans not saving:**

```bash
# Check write permissions on vault folder
ls -la ~/path/to/vault/plannotator/

# Check browser console for errors (F12 → Console)
```

**Export → Notes tab Save buttons require hook mode:**
- Export → Notes tab Save buttons require plannotator running in **hook mode** (stdin JSON input). In CLI `review`/`annotate` modes, the `/api/save-notes` endpoint is not active. Normal Claude Code hook invocation (ExitPlanMode hook) always runs in hook mode.

**Settings not visible in automated/headless browsers:**
- Obsidian Integration settings must be configured in the **system browser** that plannotator auto-opens. Settings are stored in cookies (not localStorage). Automated/headless browser profiles (Playwright, Puppeteer) use isolated cookie jars and will not see these settings.

**Bear export not working:**
- Confirm Bear app is installed and opened at least once
- Confirm `open "bear://x-callback-url/create?..."` works from terminal
- Use system browser session for plannotator settings; automated/headless sessions can block custom URI handlers

**Settings not persisting:**
- Settings are stored in cookies (not localStorage)
- Ensure cookies are enabled for localhost
- Settings persist across different ports

---

## Auto-save (Summary)

> Obsidian integration is **optional** — plans can still be reviewed and approved without it.

---

## Best Practices

1. Use plan review BEFORE the agent starts coding — catch wrong approaches early
2. Keep each annotation tied to one concrete, actionable change
3. Include acceptance criteria in "request changes" feedback
4. For diff review, annotate exact line ranges tied to expected behavior changes
5. Use image annotation for UI/UX feedback where text is insufficient

---

## References

- [GitHub: backnotprop/plannotator](https://github.com/backnotprop/plannotator)
- [Official site: plannotator.ai](https://plannotator.ai)
- [Obsidian download](https://obsidian.md/download)
- [Hook README: apps/hook/README.md](https://github.com/backnotprop/plannotator/blob/main/apps/hook/README.md)
- [OpenCode plugin: apps/opencode-plugin/README.md](https://github.com/backnotprop/plannotator/blob/main/apps/opencode-plugin/README.md)
