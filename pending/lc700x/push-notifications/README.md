# push-notifications

Get push notifications on your phone when **any coding agent** finishes a turn — Claude Code, GitHub Copilot, Codex, aider, or any terminal-based agent. Uses [ntfy.sh](https://ntfy.sh) (free, open-source).

**Works on macOS, Linux, and Windows.**

## Supported agents

| Agent | Integration | Method |
|-------|-------------|--------|
| Claude Code CLI | ✅ Native | Stop hook in `~/.claude/settings.json` |
| Claude Code (VS Code) | ✅ Log watcher | Daemon tails extension logs for `time_to_response` |
| GitHub Copilot Chat (VS Code) | ✅ Log watcher | Same daemon — best-effort activity detection |
| OpenAI Codex (VS Code) | ✅ Log watcher | Same daemon — best-effort activity detection |
| GitHub Copilot CLI | ✅ | Shell wrapper function |
| Any CLI agent | ✅ | Shell wrapper function |
| Cursor / Windsurf | ⚠️ | Use built-in OS notifications |

## How it works

```
Agent finishes → notify.sh → curl ntfy.sh → phone notification
```

A single `notify.sh` script is the engine. It auto-detects the platform (macOS/Linux/Windows) and plays the appropriate local sound. Each agent is wired to call it — **one toggle** (`/push-notifications off`) disables all agents at once.

## Install

```bash
# Clone into your agents skills directory (shared by Claude Code & Copilot CLI)
git clone https://github.com/YOUR_USERNAME/push-notifications.git ~/.agents/skills/push-notifications

# Symlink into Claude Code skills directory
ln -sf ~/.agents/skills/push-notifications ~/.claude/skills/push-notifications
```

**Windows (Git Bash or WSL):** Same commands — paths using `~` work in Git Bash.
**Windows (PowerShell):** Use `$env:USERPROFILE` instead of `~`, or run from Git Bash.

Then in any Claude Code session, type `/push-notifications`. It auto-detects your platform, installed agents, and configures each one.

Or with Copilot CLI:
```bash
copilot skill add ~/.agents/skills/push-notifications
```

## Platform support

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| CLI agents | ✅ Full | ✅ Full | ✅ Full (Git Bash or PowerShell wrappers) |
| VS Code watcher | ✅ Native | ✅ Native | ⚠️ Requires Git Bash or WSL |
| Local sound | afplay | paplay/aplay | PowerShell Media.SoundPlayer |
| QR code setup | brew install qrencode | apt install qrencode | winget install qrencode |

## Requirements

- One of: Claude Code, GitHub Copilot CLI, Codex CLI, aider, or any terminal-based agent
- [ntfy](https://ntfy.sh/) app on your phone (free, iOS & Android)
- `qrencode` for QR code setup (or Python `qrcode` fallback)
- **Windows:** Git Bash or WSL for the VS Code watcher feature (CLI integrations work without it)

## Commands

| Command | What it does |
|---------|-------------|
| `/push-notifications` | First run: full setup with QR code. After: show status. |
| `/push-notifications setup` | Force re-run setup |
| `/push-notifications off` | Disable push for all agents (chmod -x notify.sh) |
| `/push-notifications on` | Re-enable push for all agents (chmod +x notify.sh) |
| `/push-notifications test` | Send a test notification |
| `/push-notifications status` | Show platform, topic, on/off state, configured agents |
| `/push-notifications sound` | Change the local alert sound (platform-specific) |
| `/push-notifications add <agent>` | Configure a newly installed agent |
| `/push-notifications add vscode` | Start/restart the VS Code watcher daemon |

## VS Code watcher

The universal watcher daemon monitors all three major AI VS Code extensions simultaneously:

```bash
# Start (auto-discovers extensions on your platform)
watch-vscode.sh --daemon

# List what it found
watch-vscode.sh --list

# Check status
watch-vscode.sh --status
```

It auto-detects your platform's VS Code log directory and tails all AI extension logs in the current session. One daemon covers Claude Code, Copilot Chat, and Codex.

## Privacy

Your ntfy topic is a UUID — the only "authentication." Anyone who knows it can send you notifications, so treat it like a password. The topic is stored in `~/.push-notifications-topic`. All notification logic is local — `notify.sh` runs on your machine and only calls ntfy.sh to deliver.
