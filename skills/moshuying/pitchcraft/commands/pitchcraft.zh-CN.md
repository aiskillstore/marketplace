---
description: 安装 pitchcraft skill（结构化说服与汇报）
allowed-tools: Bash, Read, Edit
---

# pitchcraft 安装

## Step 1: 检测安装位置

**macOS / Linux**:
```bash
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILL_DIR="$CLAUDE_DIR/skills/pitchcraft"
if [ -d "$SKILL_DIR" ]; then echo "ALREADY_INSTALLED"; else echo "NEED_INSTALL"; fi
```

## Step 2: 安装 SKILL 文件

默认安装英文 `SKILL.md`。若需中文，将 `SKILL.zh-CN.md` 复制为 `SKILL.md`。

**macOS / Linux**:
```bash
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$CLAUDE_DIR/skills/pitchcraft"
cp "$REPO_DIR/.claude/skills/pitchcraft/SKILL.md" "$CLAUDE_DIR/skills/pitchcraft/SKILL.md"
# 中文：cp "$REPO_DIR/.claude/skills/pitchcraft/SKILL.zh-CN.md" "$CLAUDE_DIR/skills/pitchcraft/SKILL.md"
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

## Step 3: 验证安装

确认文件存在：

```bash
ls -la "$CLAUDE_DIR/skills/pitchcraft/SKILL.md"
```

## Step 4: 通知用户

告诉用户已安装完成，使用触发词：
- **「汇报」或「简报」** — 跨级汇报
- **「立项汇报」** — 说服决策层批准启动
- **「阶段汇报」** — 同步进展
- **「结项总结」** — 复盘目标达成
- **「路演」** — 向投资人展示
- **「方案推销」** — 向客户推荐解决方案
