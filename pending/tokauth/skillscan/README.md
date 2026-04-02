# SkillScan

**SkillScan** — Skill 安全扫描器

> 每一个新 skill 在使用前都必须通过 SkillScan 安全检测。
> Every new skill MUST pass SkillScan before use.

[English](#english) | [中文](#中文)

---

## English

### Overview

SkillScan is a security gate for skill packages. It automatically detects security risks in installed and newly added skills, blocking HIGH/CRITICAL risks before they can harm your environment.

### Features

- **Full-scene scanning** — Scan individual skill directories or all installed skills at once
- **Cloud-powered analysis** — SHA256-based cache lookup + cloud API upload/polling for deep analysis
- **Risk classification** — SAFE / LOW / MEDIUM / HIGH / CRITICAL verdicts with detailed threat labels
- **Auto upgrade** — Silent daily update checks, manual upgrade via `upgrade` command
- **Cross-platform** — Supports Windows / macOS / Linux


---

## 中文

### 概述

SkillScan 是 Skill 的安全门禁系统。它能自动检测已安装及新添加 skill 中的安全风险，在 HIGH/CRITICAL 级别威胁造成损害前将其阻断。

### 功能特点

- **全场景扫描** — 支持单目录扫描和全量已装 skill 批量扫描
- **云端分析** — 基于 SHA256 的缓存查询 + 云端上传/轮询深度分析
- **风险分级** — SAFE / LOW / MEDIUM / HIGH / CRITICAL 五级判定，带详细威胁标签
- **自动升级** — 后台静默每日检查更新，支持手动触发升级
- **跨平台** — 支持 Windows / macOS / Linux



## License

MIT
