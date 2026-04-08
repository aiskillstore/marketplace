# obsidian-theme-designer — Claude Code Skill

A Claude Code skill for designing Obsidian themes visually in the browser — style direction, color palette, font showcase, dual light/dark mode preview, and automated font installation. No CSS knowledge needed.

## What It Does

- **Visual style selection** — pick from 5 style directions (Academic, Minimal, Dark immersive, Cyberpunk-dev, Warm texture) shown as live browser mockups
- **Color palette picker** — choose cool, warm, or neutral tones with instant visual previews
- **Font showcase** — browse 8-10 distinctive font pairings rendered with bilingual sample content; mix and match Chinese and English fonts
- **Dual-mode preview** — see light and dark themes side by side in a full Obsidian simulation (sidebar + editor)
- **Auto font install** — downloads and installs Google Fonts to your system (Windows/macOS/Linux)
- **CSS snippet generation** — produces a ready-to-use Obsidian CSS snippet placed directly in `.obsidian/snippets/`

## Install

```bash
claude skill add https://github.com/XiangyuSu611/obsidian-theme-designer
```

Or clone manually:
```bash
git clone https://github.com/XiangyuSu611/obsidian-theme-designer ~/.claude/skills/obsidian-theme-designer
```

## Usage

Once installed, Claude will automatically apply this skill when you ask about Obsidian theme customization. For example:

- *"Design my Obsidian theme"*
- *"I want a warm, academic-looking theme for my vault"*
- *"Help me pick fonts for my Obsidian notes"*
- *"Create a dark mode color scheme for Obsidian"*

## Key Features

- **Visual-first** — every choice is shown in the browser, not described in text
- **Bilingual previews** — all previews include Chinese + English mixed content
- **Non-designer friendly** — relatable analogies, recommended defaults, and reference image support
- **Iterative refinement** — preview and tweak until satisfied before generating CSS

## Requirements

- [Claude Code](https://claude.ai/code)
- [superpowers](https://github.com/claude-plugins-official/superpowers) plugin (for Visual Companion browser previews)
- [frontend-design](https://github.com/claude-plugins-official/frontend-design) plugin (optional, for font selection)

## License

MIT
