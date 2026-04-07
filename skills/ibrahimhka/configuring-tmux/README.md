# configuring-tmux — Claude Code Skill

A Claude Code skill that guides complete tmux setup: framework selection, plugin installation, multi-bar status lines, and custom widgets.

## What It Does

- **Framework selection** — walks you through oh-my-tmux, Catppuccin, tmux-powerline, or your own framework
- **Plugin setup** — installs TPM + resurrect, continuum, cpu, net-speed out of the box
- **Multiple status bars** — teaches the correct `status-format[]` syntax (tmux 3.2+) and common pitfalls
- **Widget scripts** — caching patterns for weather, finance (Yahoo Finance), GitHub activity, world clocks, rotating news ticker

## Install

```bash
claude skill add https://github.com/ibrahimhka/claude-skill-configuring-tmux
```

Or clone manually:
```bash
git clone https://github.com/ibrahimhka/claude-skill-configuring-tmux ~/.claude/skills/tmux-config
```

## Usage

Once installed, Claude will automatically apply this skill when you ask about tmux customization. For example:

- *"Set up tmux with a nice status bar"*
- *"Add a world clock to my tmux bar"*
- *"Why aren't my tmux bar changes showing up?"*
- *"Add a second status bar with finance info"*

## Key Reference

### Multiple bars (tmux 3.2+)
```bash
set -g status 3
set -g status-format[1] "#[bg=#1a1b26,fg=#c0caf5,align=right]#(~/.config/tmux/scripts/weather.sh)"
set -g status-format[2] "#[bg=#16161e,fg=#e0af68,align=right]#(~/.config/tmux/scripts/news-ticker.sh)"
```

> ⚠️ `status2-right` does **not** exist — always use `status-format[]`.

### oh-my-tmux: use theme variables, not raw set
```bash
# ✅ Works
tmux_conf_theme_status_right="... widgets ..."

# ❌ Gets overridden on reload
set -g status-right "... widgets ..."
```

## License

MIT
