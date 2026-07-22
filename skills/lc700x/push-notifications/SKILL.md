---
name: push-notifications
slug: push-notifications
displayName: Push Notifications
version: 1.0.0
description: Set up, toggle, and test push notifications via ntfy.sh — get iPhone/Android alerts when any coding agent finishes. Works on macOS, Linux, and Windows.
argument-hint: "[setup|toggle|on|off|test|status|sound]"
license: MIT
compatibility: Requires Claude Code, GitHub Copilot CLI, or any terminal-based coding agent. Requires ntfy app on phone (free, iOS/Android). qrencode for QR setup.
metadata:
  author: lc700x
  platforms: macOS, Linux, Windows
  category: productivity
---

# Push Notifications for Coding Agents

Get push notifications on your phone when any coding agent finishes a turn — Claude Code, GitHub Copilot, Codex, aider, or any CLI agent. Uses [ntfy.sh](https://ntfy.sh) (free, open-source). Works on **macOS, Linux, and Windows**.

## Architecture

```
Any agent finishes → notify.sh → curl ntfy.sh → phone notification
```

A single `notify.sh` script is the engine. It reads the topic from `~/.push-notifications-topic` and fires the curl. Each agent is wired to call this script — the mechanism varies by agent but the script is the same.

**One toggle controls all agents:** `chmod -x notify.sh` (off) / `chmod +x notify.sh` (on).

## Platform support

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| Local sound | `afplay` | `paplay` / `aplay` | `powershell` Media.SoundPlayer |
| VS Code log path | `~/Library/Application Support/Code/logs/` | `~/.config/Code/logs/` | `%APPDATA%/Code/logs/` |
| QR code tool | `brew install qrencode` | `apt install qrencode` | `winget install qrencode` |
| Shell rc file | `~/.zshrc` | `~/.bashrc` / `~/.zshrc` | PowerShell `$PROFILE` |
| UUID generation | `uuidgen` | `uuidgen` | `[guid]::NewGuid()` (PowerShell) |
| Watcher daemon | ✅ native | ✅ native | ⚠️ requires Git Bash or WSL |

## Agent integration strategies

| Agent | Method | Mechanism |
|-------|--------|-----------|
| **Claude Code CLI** | Native Stop hook | `~/.claude/settings.json` → calls `notify.sh` |
| **Claude Code (VS Code)** | Log watcher daemon | `watch-vscode.sh --daemon` tails extension logs for `time_to_response` events |
| **GitHub Copilot Chat (VS Code)** | Log watcher daemon | Same watcher — best-effort log activity detection |
| **OpenAI Codex (VS Code)** | Log watcher daemon | Same watcher — best-effort log activity detection |
| **GitHub Copilot CLI** | Shell wrapper | `copilot()` function in shell rc file |
| **Any CLI agent** | Shell wrapper | `agent-name()` function in shell rc file |
| **Cursor / Windsurf** | OS notifications | Use the IDE's built-in notification settings |

## State detection (run first)

1. Check if `~/.push-notifications-topic` exists
2. Check `~/.claude/settings.json` for a Stop hook calling `notify.sh`
3. Check the shell rc file for wrappers:
   - **macOS/Linux**: `~/.zshrc`, `~/.bashrc`
   - **Windows (PowerShell)**: run `echo $PROFILE` to find the profile path
   - **Windows (Git Bash)**: `~/.bashrc`
4. Check for VS Code extension: look for Claude Code extension in the extensions directory
5. Detect installed CLI agents: `which claude copilot codex aider`
6. Check watcher daemon: `watch-vscode.sh --status`

Determine mode:

| State | Action |
|-------|--------|
| No `~/.push-notifications-topic` | → **Setup mode** |
| Topic exists, no integrations configured | → **Partial setup** — configure integrations |
| Topic + at least one integration active | → **Manage mode** |

## Setup mode

### Step 1: Generate a topic

**macOS / Linux (Git Bash on Windows):**
```bash
uuidgen | tr '[:upper:]' '[:lower:]' | tee ~/.push-notifications-topic
```

**Windows (PowerShell):**
```powershell
[guid]::NewGuid().ToString().ToLower() | Set-Content ~/.push-notifications-topic
```

Write the generated UUID to `~/.push-notifications-topic`. Restrict permissions:
```bash
chmod 600 ~/.push-notifications-topic  # macOS/Linux only
```

### Step 2: Generate a QR code

The ntfy app supports deep-link subscription. Generate a QR code for the topic URL.

**Install qrencode (if not already available):**

| Platform | Command |
|----------|---------|
| macOS | `brew install qrencode` |
| Linux | `sudo apt install qrencode` (Debian/Ubuntu) or `sudo dnf install qrencode` (Fedora) |
| Windows | `winget install qrencode` or `choco install qrencode` |

**Generate the QR code:**
```bash
qrencode -t ANSIUTF8 "https://ntfy.sh/$(cat ~/.push-notifications-topic)"
```

**Fallback if qrencode can't be installed** (uses Python — works on all platforms):
```bash
python3 -c "
try:
    import qrcode
    qr = qrcode.QRCode()
    qr.add_data('https://ntfy.sh/' + open('$HOME/.push-notifications-topic').read().strip())
    qr.make(fit=True)
    qr.print_ascii(invert=True)
except ImportError:
    print('Install qrencode: brew install qrencode  (macOS)')
    print('                  apt install qrencode   (Linux)')
    print('                  winget install qrencode (Windows)')
"
```

The QR encodes `https://ntfy.sh/<topic>` — when scanned with an iPhone camera, it opens the ntfy app and auto-subscribes to the topic. Android users: install ntfy from Google Play and use the + button to subscribe or scan.

### Step 3: Present the setup card

Show the user:

```
╔══════════════════════════════════════════════════════════╗
║        Push Notifications for Coding Agents             ║
╠══════════════════════════════════════════════════════════╣
║                                                        ║
║   Topic: <uuid>                                        ║
║                                                        ║
║   [QR CODE DISPLAYED ABOVE]                            ║
║   ↑ Scan with your phone camera ↑                      ║
║                                                        ║
║   1. Install ntfy on your phone (iOS/Android)          ║
║   2. Open ntfy, tap + to subscribe                     ║
║   3. Scan the QR code (or paste the topic)             ║
║   4. I'll detect your agents and configure each        ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

### Step 4: Detect agents and configure

Run `which claude copilot codex aider` to detect installed CLI agents.
Check for the VS Code Claude extension at the platform-appropriate path:
- **macOS**: `~/.vscode/extensions/anthropic.claude-code-*`
- **Linux**: `~/.vscode/extensions/anthropic.claude-code-*`
- **Windows**: `%USERPROFILE%/.vscode/extensions/anthropic.claude-code-*`

For each detected agent, configure the appropriate integration:

#### Claude Code (native Stop hook — all platforms)

Edit `~/.claude/settings.json` — add a Stop hook that calls `notify.sh`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.agents/skills/push-notifications/notify.sh 'Claude Code'"
          }
        ]
      }
    ]
  }
}
```

Merge with any existing settings keys (`env`, `permissions`, `theme`, etc.). If `hooks.Stop` already exists, add the notify entry to the array — never remove existing hooks.

If Claude Code is running, tell the user to run `/hooks` to activate.

#### GitHub Copilot CLI (shell wrapper)

**macOS / Linux:** Add to `~/.zshrc` (or `~/.bashrc`):

```bash
# Push notification wrapper — calls notify.sh when Copilot finishes
copilot() {
  command copilot "$@"
  ~/.agents/skills/push-notifications/notify.sh "Copilot"
}
```

**Windows (PowerShell):** Add to `$PROFILE`:

```powershell
# Push notification wrapper — calls notify.sh when Copilot finishes
function copilot {
  & "copilot.exe" @args
  & "bash" "~/.agents/skills/push-notifications/notify.sh" "Copilot"
}
```

**Windows (Git Bash):** Same as macOS/Linux — add to `~/.bashrc`.

If a `copilot` alias/function already exists, warn the user and show both versions — let them choose.

#### OpenAI Codex CLI (shell wrapper)

Same pattern as Copilot above — replace `copilot` with `codex`.

#### aider (shell wrapper)

Same pattern — replace with `aider`.

#### Any other CLI agent

Offer the same pattern — a shell function wrapping the binary.

#### Claude Code VS Code Extension (log watcher daemon — all platforms)

The VS Code extension logs a `"time_to_response"` event every time Claude finishes a turn. The watcher tails the logs and fires `notify.sh` on each match.

```bash
# Start the watcher as a background daemon
~/.agents/skills/push-notifications/watch-vscode.sh --daemon

# Check status
~/.agents/skills/push-notifications/watch-vscode.sh --status

# List discovered AI extensions
~/.agents/skills/push-notifications/watch-vscode.sh --list

# Stop it
~/.agents/skills/push-notifications/watch-vscode.sh --stop
```

The daemon writes its PID to `~/.push-notifications-vscode-watcher.pid` and logs to `~/.push-notifications-vscode-watcher.log`. It auto-discovers the most recent VS Code log directory for your platform.

The watcher covers all three major AI VS Code extensions:
- **Anthropic.claude-code** → `time_to_response` marker (reliable)
- **GitHub.copilot-chat** → `_any_activity` marker (best-effort)
- **openai.chatgpt** → `_any_activity` marker (best-effort)

**Windows note:** The watcher requires Git Bash or WSL (`tail`, `find`, `pkill` are POSIX tools). It won't run under native cmd.exe or PowerShell. Users on Windows should install [Git for Windows](https://git-scm.com/download/win) (includes Git Bash).

**To auto-start the watcher on login**, offer to add to the shell rc file:
```bash
# macOS/Linux: add to ~/.zshrc
~/.agents/skills/push-notifications/watch-vscode.sh --daemon

# Windows: add to PowerShell $PROFILE or Git Bash ~/.bashrc
bash ~/.agents/skills/push-notifications/watch-vscode.sh --daemon
```

#### Cursor / Windsurf / IDE agents

These are GUI apps with no terminal lifecycle hook to intercept. Tell the user:
- **Cursor**: Settings → Features → enable "Show notifications"
- **Copilot in VS Code**: Already has built-in notifications in the Copilot Chat panel
- IDE notifications can't be mirrored to phone via this mechanism — they stay on desktop

### Step 5: Confirm and test

After configuring all agents, tell the user:
- Which agents were configured and how (hook vs wrapper vs watcher)
- "The next time you use `<agent>`, you'll get a push notification when it finishes"
- "To test now: `/push-notifications test`"
- "To toggle all push notifications off: `/push-notifications off` (disables notify.sh for all agents at once)"

If Claude Code was configured via Stop hook: "This very response will trigger your first notification — the Stop hook fires now."

## Manage mode

### Toggle on/off

**Off** (`/push-notifications off`): `chmod -x ~/.agents/skills/push-notifications/notify.sh`
This makes the script a no-op for ALL agents simultaneously. Hook commands and shell wrappers still run, but `notify.sh` exits silently.

**On** (`/push-notifications on`): `chmod +x ~/.agents/skills/push-notifications/notify.sh`

### Test

Run directly:
```bash
~/.agents/skills/push-notifications/notify.sh "Test"
```

### Status

Read `~/.push-notifications-topic` and `~/.claude/settings.json`. Report:
- Topic (masked: first 8 chars + `...`)
- Whether notify.sh is executable (push enabled or disabled)
- Platform detected (macOS/Linux/Windows)
- Which agents are configured:
  - Claude Code CLI: hook present in settings.json? (yes/no)
  - Claude Code (VS Code): watcher daemon running? (check `watch-vscode.sh --status`)
  - Copilot: wrapper in shell rc? (yes/no)
  - Codex: wrapper in shell rc? (yes/no)
  - aider: wrapper in shell rc? (yes/no)
- VS Code watcher: extensions discovered and their marker types
- Local sound: which sound is configured (platform-specific)

### Add a new agent

If the user says "add copilot" / "add codex" / "add aider":
- Detect if the agent binary exists
- Add the appropriate shell wrapper (platform-aware: `.zshrc` on macOS, `$PROFILE` on Windows PowerShell)
- Tell the user to `source ~/.zshrc` (macOS/Linux) or `. $PROFILE` (Windows PowerShell) to activate

If the user says "add vscode":
- Check for the Claude Code VS Code extension
- Start the log watcher daemon: `watch-vscode.sh --daemon`
- Optionally add to shell rc for auto-start

### Remove an agent

If the user says "remove copilot" / "remove codex" / etc.:
- For shell wrappers: remove the function from the shell rc file
- For Claude Code stop hook: remove only the hook entry calling `notify.sh` (preserve other stop hooks)
- For VS Code watcher: `watch-vscode.sh --stop` and remove from rc file if auto-start was added

### VS Code watcher daemon

If the user mentions VS Code ("vscode watcher", "watch daemon", "is the watcher running"):
- Check status: `watch-vscode.sh --status`
- If not running, offer to start it: `watch-vscode.sh --daemon`
- If the user wants to stop it: `watch-vscode.sh --stop`
- If the watcher seems broken (stale PID, no recent notifications): stop, then restart with `--daemon`
- The watcher auto-finds the most recent log — it survives VS Code restarts
- **Windows users:** remind that Git Bash or WSL is required

### Sound

Offer to change the local alert sound:

**macOS:**
```
1. Glass.aiff     (default, gentle)
2. Ping.aiff      (subtle)
3. Pop.aiff       (sharp)
4. Purr.aiff      (warm)
5. Hero.aiff      (triumphant)
6. Basso.aiff     (deep)
7. Blow.aiff
8. Funk.aiff
9. Morse.aiff
10. Submarine.aiff
11. Tink.aiff
```

**Linux:** Can change the `paplay` or `aplay` sound path in `notify.sh`.

**Windows:** Only the default `Windows Notify.wav` is configured. Users can change the path in `notify.sh`.

Edit `notify.sh` to update the sound command for the detected platform.

## Customization (offer when relevant)

### Priority levels

ntfy supports: `default` (respects DnD), `high` (bypasses DnD), `urgent` (bypasses DnD + repeated alerts). Edit `notify.sh` to change `-H "Priority: default"` to `high` or `urgent`.

### Self-hosted ntfy

Replace `ntfy.sh` with the user's server URL in `notify.sh`. A single edit — all agents use the same script.

### Custom messages

Edit the `-d` body in `notify.sh`. Variables: `$DIR` (current directory name), `$1` (agent label).

### Apple Watch haptic-only / Android silent

In the ntfy app, set the topic's notification sound to "None." Notifications still arrive but silently.

## Edge cases

- **settings.json has syntax errors**: Validate JSON before editing. Use `python3 -m json.tool` to check (works on all platforms).
- **Shell wrapper conflicts**: If a function/alias already exists for the agent, show both versions and let the user decide. Never overwrite without asking.
- **User runs agent in a different terminal**: Shell wrappers only work when the agent is invoked by name. The Claude Code Stop hook is immune to this — it fires regardless of how Claude was launched.
- **IDE-based agents**: Can't be intercepted from the terminal. Don't promise what can't be delivered.
- **Multiple shell rc files**: Check the platform-appropriate file. macOS/Linux: `~/.zshrc`, `~/.bashrc`. Windows PowerShell: `$PROFILE`. Windows Git Bash: `~/.bashrc`.
- **notify.sh permissions during toggle**: `chmod -x` is the atomic off switch. On Windows (Git Bash), `chmod` works on NTFS too. Verify with `ls -l`.
- **Windows watcher not starting**: The watcher script requires Git Bash or WSL. If neither is available, the VS Code log watching feature is unavailable — but CLI integrations (Stop hook, shell wrappers) still work.
- **Platform-specific VS Code log paths**: The watcher auto-detects the platform and finds the correct log directory. If it fails, the `--list` command shows what it found.
