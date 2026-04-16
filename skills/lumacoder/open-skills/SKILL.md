---
name: open-skills
description: 一个交互式 CLI 工具，帮助开发者按分类浏览、空格多选、一键批量安装/同步 AI Agent skills 到多个编辑器。
version: 2.0.0
author: lumacoder
license: MIT
---

# open-skills

安装后运行 `open-skills` 启动交互式引导：

1. 选择目标编辑器（可多选）
2. 选择安装范围（全局 / 本地）
3. 选择分类（前端 / 后端 / 运维 / 产品 / UI / ...）
4. 空格键多选具体 skills
5. 确认后自动下载、转换、输出

## 安装

```bash
npx skills add lumacoder/open-skills -g -y
```

## 使用

```bash
open-skills
```

## 支持的目标编辑器

- Claude Code
- Hermes
- Cursor
- Windsurf
- Cline
- Cursor Skills
- Roo-Cline
- Antigravity
- GitHub Copilot