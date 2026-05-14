# charset-fix 🔤

**修复在 Windows POSIX 终端下运行 AI Agent 时的中文乱码问题。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skill: Windows](https://img.shields.io/badge/Skill-Windows-0078D4)](SKILL.md)

## 问题

在 Windows 上通过 Git Bash、BusyBox、MSYS2 等 POSIX 兼容终端运行 AI 编程助手（Claude Code、Codex CLI、Cline、Cursor 等）时，中文输出会出现乱码：

```
$ python3 -c "print('中文测试')"
���Ĳ���
$ echo "中文测试"
中文测试
```

**原因**：Python、PowerShell、cmd.exe 等 Windows 原生工具默认使用 **GBK/CP936** 编码输出，而 POSIX 终端期望 **UTF-8**，编码不匹配导致乱码。

## 这个技能有什么用

AI Agent 装上此 skill 后，遇到中文乱码会自动应用正确的修复方案：

| 场景 | 修复方式 |
|------|---------|
| Python 输出乱码 | `PYTHONIOENCODING=utf-8` |
| PowerShell 输出乱码 | `[Console]::OutputEncoding = [Text.Encoding]::UTF8` |
| cmd.exe / 系统命令乱码 | Python subprocess 桥接 + `encoding='gbk'` |

## 安装方式

此技能适用于各类 AI Agent，安装方式取决于你使用的工具：

### Claude Code / Codex CLI

```bash
git clone https://github.com/gkd2323c/charset-fix.git
cd charset-fix
# Claude Code
claude add-skill ./
# Codex CLI
codex add-skill ./
```

### Cline / Cursor

将 `charset-fix` 文件夹放入项目的 `.cline/skills/` 或 `.cursor/skills/` 目录。

### OpenClaw / ClawHub

```bash
clawhub install charset-fix
```

### 直接使用（不装 skill）

```bash
export PYTHONIOENCODING=utf-8
python3 -c "print('中文测试 ✅')"
```

## 快速验证

```bash
PYTHONIOENCODING=utf-8 python3 -c "print('charset-fix: 中文测试成功 ✅')"
```

预期输出：`charset-fix: 中文测试成功 ✅`

## 仓库结构

```
charset-fix/
├── SKILL.md       ← Agent 技能定义（主入口）
├── README.md      ← 本文件
├── LICENSE        ← MIT 许可证
└── scripts/
    └── fix.py     ← 诊断和测试辅助脚本
```

## 兼容性

| 平台 | 状态 |
|------|------|
| Windows + Git Bash | ✅ 已验证 |
| Windows + BusyBox | ✅ 已验证 |
| Windows + MSYS2 | ✅ 已验证 |
| Windows + WSL | ✅ 可用 |
| macOS / Linux | ❌ 不需要 |

## License

MIT
