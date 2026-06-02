---
description: Install pitchcraft skill for structured persuasion and executive reporting
allowed-tools: Bash, Read, Edit
---

# Install pitchcraft

## Step 1: Detect install location

**macOS / Linux**:
```bash
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILL_DIR="$CLAUDE_DIR/skills/pitchcraft"
if [ -d "$SKILL_DIR" ]; then echo "ALREADY_INSTALLED"; else echo "NEED_INSTALL"; fi
```

## Step 2: Install SKILL file

Installs English `SKILL.md` by default. For Chinese, copy `SKILL.zh-CN.md` to `SKILL.md` instead.

**macOS / Linux**:
```bash
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$CLAUDE_DIR/skills/pitchcraft"
cp "$REPO_DIR/.claude/skills/pitchcraft/SKILL.md" "$CLAUDE_DIR/skills/pitchcraft/SKILL.md"
# Chinese: cp "$REPO_DIR/.claude/skills/pitchcraft/SKILL.zh-CN.md" "$CLAUDE_DIR/skills/pitchcraft/SKILL.md"
echo "pitchcraft installed at $CLAUDE_DIR/skills/pitchcraft/"
```

**Windows (PowerShell)**:
```powershell
$claudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$repoDir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
New-Item -ItemType Directory -Force -Path (Join-Path $claudeDir "skills\pitchcraft")
Copy-Item (Join-Path $repoDir ".claude\skills\pitchcraft\SKILL.md") (Join-Path $claudeDir "skills\pitchcraft\SKILL.md")
Write-Output "pitchcraft installed at $(Join-Path $claudeDir 'skills\pitchcraft\')"
```

## Step 3: Verify

```bash
ls -la "$CLAUDE_DIR/skills/pitchcraft/SKILL.md"
```

## Step 4: Notify user

Installation complete. Trigger phrases:

**English**

- **status update** / **briefing** — cross-level briefing
- **project kickoff** — approve and fund
- **milestone review** — sync progress
- **wrap-up** / **retrospective** — outcomes and assets
- **pitch** / **fundraising** — investors or partners
- **solution selling** — customer stakeholders

**中文**（若安装了 `SKILL.zh-CN.md`）

- **汇报** / **简报** · **立项汇报** · **阶段汇报** · **结项总结** · **路演** · **方案推销**
