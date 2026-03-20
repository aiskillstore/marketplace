---
name: vibe-kanban
description: Manage AI coding agents on a visual Kanban board. Run parallel agents through a To Do→In Progress→Review→Done flow with automatic git worktree isolation and GitHub PR creation.
allowed-tools: Read Write Bash Grep Glob
metadata:
  tags: vibe-kanban, kanban, kanbanview, multi-agent, git-worktree, github-pr, task-management, claude-code, codex, gemini, open-code, mcp
  platforms: Claude, Codex, Gemini, OpenCode
  keyword: kanbanview
  version: 1.2.0
  source: "https://github.com/BloopAI/vibe-kanban"
  verified: 2026-02-22
  verified-with: playwright
---


## Platform Support Status (Current)

| Platform | Current Support | Requirements |
|---|---|---|
| Claude | Native MCP integration | Register in `mcpServers` |
| Codex | MCP script integration | `scripts/mcp-setup.sh --codex` or equivalent config |
| Gemini | MCP registration | `mcpServers`/bridge configuration |
| OpenCode | MCP/bridge integration | `omx`/`ohmg` or equivalent setup |

Whether this skill alone is sufficient:
- Claude/Gemini: **Yes**
- Codex: **Yes (requires script-based setup)**
- OpenCode: **Yes (via orchestration)**

# Vibe Kanban — AI Agent Kanban Board

> Manage multiple AI agents (Claude/Codex/Gemini) from a single Kanban board.
> Moving a card (task) to In Progress automatically creates a git worktree and starts the agent.

## When to use this skill

- When breaking an epic into independent tasks for parallel agent assignment
- When you want to visually track the status of ongoing AI work
- When you want to review agent results as diffs/logs in the UI and retry them
- When combining GitHub PR-based team collaboration with AI agent work

---

## Prerequisites

```bash
# Node.js 18+ required
node --version

# Complete agent authentication beforehand
claude --version    # Set ANTHROPIC_API_KEY
codex --version     # Set OPENAI_API_KEY (optional)
gemini --version    # Set GOOGLE_API_KEY (optional)
opencode --version  # No separate setup needed (GUI-based)
```

> **Verified versions (as of 2026-02-22)**
> - vibe-kanban: v0.1.17
> - claude (Claude Code): 2.1.50
> - codex: 0.104.0
> - gemini: 0.29.5
> - opencode: 1.2.10

---

## Installation & Running

### npx (fastest)

```bash
# Run immediately (no installation needed)
npx vibe-kanban

# Specify port (default port 3000)
npx vibe-kanban --port 3001

# Specify port and environment variable together
PORT=3001 npx vibe-kanban --port 3001

# Use wrapper script
bash scripts/vibe-kanban-start.sh
```

Browser opens `http://localhost:3000` automatically.

> ⚠️ **Port conflict warning**: If another dev server like Next.js is using port 3000,
> run `PORT=3001 npx vibe-kanban --port 3001`.
> Confirm `Main server on :3001` in the startup log, then visit `http://localhost:3001`.

Normal startup log:
```
Starting vibe-kanban v0.1.17...
No user profiles.json found, using defaults only
Starting PR monitoring service with interval 60s
Remote client initialized with URL: https://api.vibekanban.com
Main server on :3001, Preview proxy on :XXXXX
Opening browser...
```

### Clone + dev mode

```bash
git clone https://github.com/BloopAI/vibe-kanban.git
cd vibe-kanban
pnpm i
pnpm run dev
```

---

## Environment Variables

| Variable | Description | Default |
|------|------|--------|
| `PORT` | Server port | `3000` |
| `HOST` | Server host | `127.0.0.1` |
| `VIBE_KANBAN_REMOTE` | Allow remote connections | `false` |
| `VK_ALLOWED_ORIGINS` | CORS allowed origins | Not set |
| `DISABLE_WORKTREE_CLEANUP` | Disable worktree cleanup | Not set |
| `ANTHROPIC_API_KEY` | For Claude Code agent | — |
| `OPENAI_API_KEY` | For Codex/GPT agent | — |
| `GOOGLE_API_KEY` | For Gemini agent | — |

Set in `.env` file before starting the server.

> **API key location per agent (Settings → Agents → Environment variables)**
> - Claude Code: `ANTHROPIC_API_KEY`
> - Codex: `OPENAI_API_KEY`
> - Gemini: `GOOGLE_API_KEY`
> - Opencode: No separate setup needed (built-in auth)

---

## MCP Configuration

Vibe Kanban runs as an MCP (Model Context Protocol) server, letting agents control the board directly.

### Claude Code MCP Setup

`~/.claude/settings.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "vibe-kanban": {
      "command": "npx",
      "args": ["vibe-kanban", "--mcp"],
      "env": {
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "3001"
      }
    }
  }
}
```

### OpenCode MCP Setup

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "vibe-kanban": {
      "command": "npx",
      "args": ["vibe-kanban", "--mcp"],
      "env": {
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "3001"
      }
    }
  }
}
```

After restarting, `vk_*` tools are available directly in your OpenCode session.


### MCP Tool List

| Tool | Description |
|------|------|
| `vk_list_cards` | List all cards (workspaces) |
| `vk_create_card` | Create a new card |
| `vk_move_card` | Change card status |
| `vk_get_diff` | Get card diff |
| `vk_retry_card` | Re-run a card |

> ⚠️ **Tool name changes from older versions**: `vk_list_tasks` → `vk_list_cards`, `vk_create_task` → `vk_create_card`
> These are the confirmed tool names from the actual MCP API as of v0.1.17.

### Codex MCP Integration

To connect Vibe Kanban with Codex, run the following from your project root:

```bash
bash scripts/mcp-setup.sh --codex
```

This command adds the `vibe-kanban` MCP server config to `~/.codex/config.toml`.  
Hook-based auto-looping is not default Codex behavior, so retry/loop management is handled via board card progress states or a higher-level orchestrator.

---

## Workspace → Parallel Agents → PR Workflow

> **v0.1.17 actual UI structure**: Vibe Kanban is a Kanban board, but
> the actual unit of work is a **Workspace**.
> Each workspace handles one task independently.

### 1. Start the server

```bash
# Default run
npx vibe-kanban
# → http://localhost:3000

# Port conflict (e.g., Next.js)
PORT=3001 npx vibe-kanban --port 3001
# → http://localhost:3001
```

### 2. (Optional) Review epic plan with planno

```text
Review the implementation plan for this feature with planno
```

planno (plannotator) is an independent skill — usable without Vibe Kanban.

### 3. Create a Workspace

1. Open the UI → click **"+ Create Workspace"** or the `+` button in the left sidebar
2. **Which repositories?** screen:
   - **Browse** → select a git repo from the filesystem (manual path entry supported)
   - **Recent** → previously used repos
   - Select a repo, then choose a branch (default: `main`)
   - Click **Continue**
3. **What would you like to work on?** screen:
   - Select an agent (Opencode, Claude Code, Codex, Gemini, Amp, Qwen Code, Copilot, Droid, Cursor Agent)
   - Enter a task description (Markdown supported)
   - Select a mode (Default, Build, etc.)
   - Click **Create**

### 4. Automatic agent execution

When a workspace is created:
- A `vk/<hash>-<slug>` branch is created automatically (e.g., `vk/3816-add-a-comment-to`)
- A git worktree is created automatically (fully isolated per agent)
- The selected agent CLI runs with log streaming

Workspace states:
- **Running**: Agent is executing (left sidebar)
- **Idle**: Waiting
- **Needs Attention**: Agent finished or needs input

### 5. Review results

- **Changes panel**: View file diffs
- **Logs panel**: Agent execution logs
- **Preview panel**: Web app preview
- **Terminal**: Run commands directly
- **Notes**: Write notes

### 6. Create PR & finish

- Workspace detail → **"Open pull request"** button
- PR merge → workspace moves to Archive
- Worktree cleaned up automatically

---

## Git Worktree Isolation Structure

Workspace directory (configurable in Settings → General → Workspace Directory):
```
~/.vibe-kanban-workspaces/          ← default location (under home directory)
├── <workspace-uuid-1>/             ← workspace 1 isolated environment
├── <workspace-uuid-2>/             ← workspace 2 isolated environment
└── <workspace-uuid-3>/             ← workspace 3 isolated environment
```

Branch naming (configurable in Settings → General → Git → Branch Prefix):
```
vk/<4-char ID>-<task-slug>
e.g.: vk/3816-add-a-comment-to-readme
```

Internal behavior:
```bash
git worktree add <workspace-dir> -b vk/<hash>-<task-slug> main
<agent-cli> -p "<task-description>" --cwd <workspace-dir>
```

> **Recommended .gitignore entries:**
> ```
> .vibe-kanban-workspaces/
> .vibe-kanban/
> ```

---

## Remote Deployment

### Docker

```bash
# Official image
docker run -p 3000:3000 vibekanban/vibe-kanban

# Pass environment variables
docker run -p 3000:3000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e VK_ALLOWED_ORIGINS=https://vk.example.com \
  vibekanban/vibe-kanban
```

### Reverse Proxy (Nginx/Caddy)

```bash
# CORS must be allowed
VK_ALLOWED_ORIGINS=https://vk.example.com

# Or multiple origins
VK_ALLOWED_ORIGINS=https://a.example.com,https://b.example.com
```

### SSH Remote Access

Integrates with VSCode Remote-SSH:
```
vscode://vscode-remote/ssh-remote+user@host/path/to/.vk/trees/<task-slug>
```

---

## Troubleshooting

### Worktree conflicts / orphaned worktrees

```bash
# Clean up orphaned worktrees
git worktree prune

# List current worktrees
git worktree list

# Force remove a specific worktree
git worktree remove .vk/trees/<slug> --force
```

### 403 Forbidden (CORS error)

```bash
# CORS config required for remote access
VK_ALLOWED_ORIGINS=https://your-domain.com npx vibe-kanban
```

### Agent won't start

```bash
# Test CLI directly
claude --version
codex --version

# Check API keys
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

### Port conflict

```bash
# Use a different port
npx vibe-kanban --port 3001

# Or use environment variable
PORT=3001 npx vibe-kanban
```

### SQLite lock error

```bash
# Disable worktree cleanup and restart
DISABLE_WORKTREE_CLEANUP=1 npx vibe-kanban
```

---

## UI vs CLI Decision Guide

| Situation | Mode |
|------|------|
| Shared team board, visual progress tracking | UI (`npx vibe-kanban`) |
| CI/CD pipeline, script automation | CLI (`scripts/pipeline.sh`) |
| Quick local experiments | CLI (`scripts/conductor.sh`) |
| Browser diff/log review | UI |

---

## Supported Agents (verified v0.1.17)

Configure each agent in Settings → Agents:

| Agent | Command | API Key |
|----------|------|--------|
| **Opencode** | `opencode` | Built-in (default) |
| **Claude Code** | `claude` | `ANTHROPIC_API_KEY` |
| **Codex** | `codex` | `OPENAI_API_KEY` |
| **Gemini** | `gemini` | `GOOGLE_API_KEY` |
| **Amp** | `amp` | Separate |
| **Qwen Code** | `qwen-coder` | Separate |
| **Copilot** | `copilot` | GitHub account |
| **Droid** | `droid` | Separate |
| **Cursor Agent** | `cursor` | Cursor subscription |

Configurable per agent:
- **Append prompt**: Additional instructions appended at agent runtime
- **Model**: Model name to use (e.g., `claude-opus-4-6`)
- **Variant**: Model variant
- **Auto Approve**: Auto-approve agent actions (default: ON)
- **Auto Compact**: Auto-compress context (default: ON)
- **Environment variables**: API keys and other env vars

## Representative Use Cases

### 1. Parallel epic decomposition

```
"Payment Flow v2" epic
  ├── Workspace 1: Frontend UI  → Claude Code
  ├── Workspace 2: Backend API  → Codex
  └── Workspace 3: Integration tests → Opencode
→ 3 workspaces Running simultaneously → parallel implementation
```

### 2. Role-based specialist agent assignment

```
Claude Code  → design/domain-heavy features
Codex        → types/tests/refactoring
Gemini       → docs/storybook writing
Opencode     → general tasks (default)
```

### 3. GitHub PR-based team collaboration

```
Set VIBE_KANBAN_REMOTE=true
→ Team members check status on the board
→ Review/approval only via GitHub PR
→ Parallel agents + traditional PR process combined
```

### 4. Implementation comparison

```
Same task, two workspaces:
  Workspace A → Claude Code (UI structure focus)
  Workspace B → Codex (performance optimization focus)
→ Compare PRs, pick best-of-both
```

### 5. OpenCode + ulw parallel delegation

Combine with OpenCode's ulw (ultrawork) mode to run agents in parallel at the epic level:

```python
# ulw keyword → activates ultrawork parallel execution layer
# Vibe Kanban board: npx vibe-kanban (run in a separate terminal)

task(category="visual-engineering", run_in_background=True,
     load_skills=["frontend-ui-ux", "vibe-kanban"],
     description="[Kanban WS1] Frontend UI",
     prompt="Implement payment flow UI — card input, order confirmation, and completion screens in src/components/payment/")

task(category="unspecified-high", run_in_background=True,
     load_skills=["vibe-kanban"],
     description="[Kanban WS2] Backend API",
     prompt="Implement payment flow API — POST /charge, POST /refund, GET /status/:id")

task(category="unspecified-low", run_in_background=True,
     load_skills=["vibe-kanban"],
     description="[Kanban WS3] Integration tests",
     prompt="Write payment E2E tests — success/failure/refund scenarios")

# → 3 workspaces appear simultaneously in Running state on the Kanban board
# → On each completion: Needs Attention → PR created → Archive
```

---

## Tips

- Keep card scope narrow (1 card = 1 commit unit)
- For changes spanning 2+ files, review the plan with planno first
- Use `VIBE_KANBAN_REMOTE=true` only on trusted networks
- If an agent stalls, reassign or split the card

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Vibe Kanban UI                       │
│   ┌──────────┬──────────┬──────────┬──────────┐        │
│   │  To Do   │In Progress│  Review  │   Done   │        │
│   └──────────┴──────────┴──────────┴──────────┘        │
└───────────────────────────┬─────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────┐
│                    Rust Backend                         │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │
│  │ server  │  │executors │  │   git   │  │ services │  │
│  └─────────┘  └──────────┘  └─────────┘  └──────────┘  │
│                   │                                     │
│             ┌─────▼─────┐                               │
│             │  SQLite   │                               │
│             └───────────┘                               │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌─────▼─────┐       ┌────▼────┐
   │ Claude  │        │   Codex   │       │ Gemini  │
   │worktree1│        │ worktree2 │       │worktree3│
   └─────────┘        └───────────┘       └─────────┘
```

---

## References

- [GitHub repo: BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban)
- [Official landing page: vibekanban.com](https://vibekanban.online)
- [Architecture analysis: vibe-kanban – a Kanban board for AI agents](https://virtuslab.com/blog/ai/vibe-kanban/)
- [Adoption story](https://bluedreamer-twenty.tistory.com/7)
- [Demo: Run Multiple Claude Code Agents Without Git Conflicts](https://www.youtube.com/watch?v=W45XJWZiwPM)
- [Demo: Claude Code Just Got Way Better | Auto Claude Kanban Boards](https://www.youtube.com/watch?v=vPPAhTYoCdA)

---

## Skill File Structure

```
.agent-skills/vibe-kanban/
├── SKILL.md              # Main skill document
├── SKILL.toon            # TOON format (compressed)
├── scripts/
│   ├── start.sh          # Server start wrapper
│   ├── cleanup.sh        # Worktree cleanup
│   ├── mcp-setup.sh      # MCP setup automation
│   └── health-check.sh   # Server health check
├── references/
│   ├── environment-variables.md  # Environment variable reference
│   └── mcp-api.md                # MCP API reference
└── templates/
    ├── claude-mcp-config.json    # Claude Code MCP config
    ├── docker-compose.yml        # Docker deployment template
    └── .env.example              # Environment variable example
```

### Script Usage

```bash
# Start server
bash scripts/start.sh --port 3001

# Worktree cleanup
bash scripts/cleanup.sh --dry-run  # Preview
bash scripts/cleanup.sh --all       # Remove all VK worktrees

# MCP setup
bash scripts/mcp-setup.sh --claude  # Claude Code setup
bash scripts/mcp-setup.sh --all     # Setup for all agents

# Health check
bash scripts/health-check.sh
bash scripts/health-check.sh --json  # JSON output
```

---

## Quick Reference

```
=== Start server ===
npx vibe-kanban                       Run immediately (port 3000)
PORT=3001 npx vibe-kanban --port 3001 Port conflict (e.g., Next.js)
http://localhost:3000                  Board UI

=== Environment variables ===
PORT=3001                        Change port
VK_ALLOWED_ORIGINS=https://...   Allow CORS
ANTHROPIC_API_KEY=...            Claude Code auth
OPENAI_API_KEY=...               Codex auth
GOOGLE_API_KEY=...               Gemini auth

=== MCP integration ===
npx vibe-kanban --mcp            MCP mode
vk_list_cards                    List cards (workspaces)
vk_create_card                   Create card
vk_move_card                     Change status

=== Workspace flow ===
Create → Running → Needs Attention → Archive
Running: worktree created + agent started
Needs Attention: finished or needs input
Archive: PR merge complete

=== MCP config file locations ===
Opencode: ~/.config/opencode/opencode.json
Claude Code: ~/.claude/settings.json or .mcp.json

=== worktree cleanup ===
git worktree prune               Clean up orphans
git worktree list                List all
git worktree remove <path>       Force remove
```
