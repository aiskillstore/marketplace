---
name: charset-fix
description: >-
  Fix Chinese/Unicode character encoding issues when running AI agents on
  Windows via POSIX shells (Git Bash, MSYS2, WSL, BusyBox, etc.). Handles
  Python, PowerShell, and cmd.exe GBK/CP936 output encoding mismatch with
  UTF-8 terminals.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
    os:
      - windows
    emoji: 🔤
---

# Windows Character Encoding Fix for AI Agents

> Fix garbled Chinese/Unicode text output when running AI agents on Windows through POSIX-compatible shells.

## Problem

When AI agents run commands on Windows through POSIX shells (Git Bash, MSYS2, BusyBox, or any Unix-like shell layer), text output containing Chinese or extended Unicode characters often appears garbled:

```
$ python3 -c "print('中文测试')"
���Ĳ���  ← garbled
$ echo "中文测试"
中文测试       ← correct
```

### Root Cause

| Layer | Encoding | Why |
|-------|----------|-----|
| **Windows system** | GBK/GB2312 (CP936) | Default code page for Chinese Windows |
| **Python 3** | GBK | `sys.stdout.encoding` auto-detects system code page |
| **PowerShell (powershell.exe)** | GB2312 | `[Console]::OutputEncoding` defaults to system CP |
| **cmd.exe** | GBK | Native Windows command processor |
| **POSIX shell** (Git Bash, BusyBox, MSYS2) | UTF-8 | Expects UTF-8 input |
| **PowerShell Core (pwsh.exe)** | UTF-8 | ✅ Defaults to UTF-8, no fix needed |

The mismatch: Windows-native tools output GBK-encoded text, but the POSIX shell terminal reads it as UTF-8, producing garbled characters.

## Quick Fix

### Python

```bash
PYTHONIOENCODING=utf-8 python3 -c "print('中文测试 ✅')"
```

Set it for the whole session:

```bash
export PYTHONIOENCODING=utf-8
python3 script.py
```

### PowerShell (Windows PowerShell, not Core)

```powershell
powershell.exe -NoProfile -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Write-Host '中文测试'"
```

### cmd.exe / Windows native tools

Use Python's `subprocess` as a GBK→UTF-8 bridge:

```bash
PYTHONIOENCODING=utf-8 python3 -c "
import subprocess
r = subprocess.run(['cmd.exe', '/c', 'systeminfo | findstr 系统'],
    capture_output=True, text=True, encoding='gbk')
print(r.stdout)
"
```

### Code-level fix (Python)

```python
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

## Verification

```bash
PYTHONIOENCODING=utf-8 python3 -c "print('charset-fix: 中文测试成功 ✅')"
```

Expected: `charset-fix: 中文测试成功 ✅`

## How It Works

| Fix | Mechanism |
|-----|-----------|
| `PYTHONIOENCODING=utf-8` | Overrides Python's stdout encoding detection |
| `[Console]::OutputEncoding = UTF8` | Sets PowerShell's console output to UTF-8 |
| `subprocess(..., encoding='gbk')` | Decodes cmd.exe output correctly, then emits as UTF-8 |

## Compatibility

| Platform | Status |
|----------|--------|
| Windows + Git Bash | ✅ Works |
| Windows + BusyBox | ✅ Works |
| Windows + MSYS2 | ✅ Works |
| Windows + WSL | ✅ Works |
| macOS / Linux | ⬜ Not needed |
| PowerShell Core (pwsh) | ⬜ Not needed |

Works with: Claude Code, Codex CLI, Cline, Cursor, GitHub Copilot, OpenClaw agents.

## Debugging

```bash
# Check code page
powershell.exe -NoProfile -Command "chcp"

# Check Python encoding
python3 -c "import sys; print(sys.stdout.encoding)"

# Test raw shell output
echo "中文测试"
```

## License

MIT
