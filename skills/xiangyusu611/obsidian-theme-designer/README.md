# Obsidian Theme Designer

[中文](README_CN.md) | English

**Stop trial-and-error. Design your Obsidian theme visually in the browser.**

A Claude Code skill that guides you through designing a custom Obsidian theme — step by step, visually, with live browser previews. No CSS knowledge needed.

---

## How It Works

### Step 1: Choose a Style Direction

Pick from 5 visual directions — each shown as a live mockup, not just a label.

![Style Direction Selection](screenshots/style-directions.png)

### Step 2: Pick Your Colors

Choose cool, warm, or neutral tones. See them applied instantly.

![Color Palette Selection](screenshots/color-palettes.png)

### Step 3: Find Your Font

Browse 8-10 distinctive font pairings rendered with your actual content. Mix and match — pick Chinese from one card, English from another.

![Font Showcase](screenshots/font-showcase.png)

### Step 4: Preview & Refine

See your complete theme in a full Obsidian simulation — sidebar, editor, light & dark mode side by side. Iterate until perfect.

![Dual Mode Preview](screenshots/dual-mode-preview.png)

### Step 5: One-Click Install

The skill generates a CSS snippet, installs fonts, and tells you exactly how to enable it in Obsidian. Done.

---

## Features

- **Visual-first** — Every choice is shown in the browser, not described in text
- **Bilingual previews** — All previews include Chinese + English mixed content
- **Font intelligence** — Uses the `frontend-design` skill to pick distinctive, non-generic fonts
- **Dual mode** — Light and dark themes with independent accent colors
- **Auto font install** — Downloads and installs Google Fonts to your system (Windows/macOS/Linux)
- **Non-designer friendly** — Relatable analogies ("like a LaTeX PDF"), recommended defaults, reference image support

---

## Quick Start

1. Copy `obsidian-theme-designer/` to `~/.claude/skills/`
2. Open your Obsidian vault folder in Claude Code
3. Say: **"Design my Obsidian theme"**

## Requirements

- [Claude Code](https://claude.ai/code)
- [superpowers](https://github.com/claude-plugins-official/superpowers) plugin (for Visual Companion browser previews)
- [frontend-design](https://github.com/claude-plugins-official/frontend-design) plugin (optional, for font selection)

## License

MIT
