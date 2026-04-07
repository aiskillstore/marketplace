---
name: configuring-tmux
description: Configures tmux status bars, installs frameworks and plugins, adds widgets and scripts, and sets up multiple status bars. Use when working with oh-my-tmux, Catppuccin, or tmux-powerline; adding weather/finance/clock/news widgets; troubleshooting why bar changes aren't appearing; or setting up tmux on a new machine.
---

# Configuring tmux

## Step 0: Choose a Framework

Ask the user which framework they want **before** touching any config.

### Option 1: oh-my-tmux
```bash
cd ~ && git clone https://github.com/gpakosz/.tmux.git
ln -sf .tmux/.tmux.conf .tmux.conf
cp .tmux/.tmux.conf.local .tmux.conf.local
```
- Theming via `tmux_conf_theme_*` variables in `~/.tmux.conf.local` — never edit `~/.tmux.conf`
- **Gotcha:** its theming layer owns bar 0 and overrides raw `set -g status-right` — use `status-format[]` for extra bars

### Option 2: Catppuccin (TPM-based, no clone needed)
```bash
set -g @plugin 'catppuccin/tmux#v2.1.3'
set -g @catppuccin_flavor 'mocha'
set -g @catppuccin_status_modules_right "application session date_time"
```
- Module list controls bar 0 — add custom `#()` calls via `status-right-append`
- Extra bars use `status-format[]` directly

### Option 3: tmux-powerline
```bash
git clone https://github.com/erikw/tmux-powerline.git ~/.config/tmux-powerline
set-option -g status-left "#(~/.config/tmux-powerline/powerline.sh left)"
set-option -g status-right "#(~/.config/tmux-powerline/powerline.sh right)"
```
- Requires Nerd Font or Powerline-patched font
- Segments live in `~/.config/tmux-powerline/segments/`

### Option 4: User-provided framework
Ask for: repo URL, install method, where customizations live, how it handles status content. Then apply the patterns below.

---

## Plugin Setup (all frameworks)

```bash
# Install TPM
git clone https://github.com/tmux-plugins/tpm ~/.config/tmux/plugins/tpm

# Essential plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @plugin 'tmux-plugins/tmux-cpu'          # #{cpu_percentage} #{ram_percentage}
set -g @plugin 'tmux-plugins/tmux-net-speed'    # #{net_speed_up} #{net_speed_down}

set -g @continuum-restore 'on'
set -g @continuum-save-interval '10'
set -g @resurrect-capture-pane-contents 'on'

run '~/.config/tmux/plugins/tpm/tpm'
# Install: prefix + I
```

---

## Multiple Status Bars

tmux 3.2+ supports 2–5 bars. **The correct syntax is `status-format[]` array** — not `status2-right` (invalid, will error).

```bash
set -g status 3

# Bar 1: widgets row
set -g status-format[1] "#[bg=#1a1b26,fg=#c0caf5,align=right]#(~/.config/tmux/scripts/weather.sh)  #(~/.config/tmux/scripts/finance.sh)  #[fg=#1e3a8a,bg=#b8970d,bold]PT #(TZ=America/Los_Angeles date +%H:%M) EST #(TZ=America/New_York date +%H:%M)#[default]"

# Bar 2: news ticker
set -g status-format[2] "#[bg=#16161e,fg=#e0af68,align=right]  #(~/.config/tmux/scripts/news-ticker.sh)"
```

With `status-position top` and `status 3`:
```
Bar 0  ← framework owns (oh-my-tmux / Catppuccin)
Bar 1  ← status-format[1]  — configure freely
Bar 2  ← status-format[2]  — configure freely
──────────────────────────────
Terminal panes
```

Verify: `tmux show-options -g status` (must equal your total bar count)

---

## Widget Scripts

### Single-line output rule
Scripts in `#()` must emit **one line**. Multi-line output corrupts the bar.

### Caching pattern (required for network scripts)
```bash
#!/bin/bash
CACHE="/tmp/my-widget-cache"
CACHE_AGE=300

if [ -f "$CACHE" ]; then
    age=$(( $(date +%s) - $(stat -c %Y "$CACHE") ))
    [ "$age" -lt "$CACHE_AGE" ] && cat "$CACHE" && exit 0
fi

python3 << 'PYEOF' | tee "$CACHE"
# fetch and print ONE line
PYEOF
```

### World clocks (no cache needed)
```bash
# In status-format[]: use %H:%M directly
"PT #(TZ=America/Los_Angeles date +%H:%M) EST #(TZ=America/New_York date +%H:%M)"

# In oh-my-tmux tmux_conf_theme_status_right: escape % as %%
"PT #(TZ=America/Los_Angeles date +%%H:%%M)"
```

### Rotating news ticker
```bash
#!/bin/bash
CACHE="/tmp/news-cache"  # one headline per line, refreshed by background fetch
[ ! -s "$CACHE" ] && echo "Loading..." && exit 0
count=$(wc -l < "$CACHE")
idx=$(( ($(date +%s) / 20) % count ))   # rotates every 20s
sed -n "$((idx + 1))p" "$CACHE"
```

### Finance widget (Yahoo Finance v8)
Use `-A "Mozilla/5.0"` — Yahoo blocks default curl UA:
```bash
curl -sf --max-time 4 -A "Mozilla/5.0 (X11; Linux x86_64)" \
  "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?interval=1d&range=1d"
```

---

## oh-my-tmux: Bar 0 Reference

```bash
# ~/.tmux.conf.local
tmux_conf_theme_status_right="#{prefix}#{mouse} 🌿 #[fg=#000,bg=#2ea043,bold]#(git -C #{pane_current_path} symbolic-ref --short HEAD 2>/dev/null)#[default] #[fg=#fff,bg=#cc1111,bold]⚡#{cpu_percentage}/💾#{ram_percentage}#[default]"
tmux_conf_theme_status_right_fg="#000000,#000000,#000000"
tmux_conf_theme_status_right_bg="#2ea043,#1155cc,#2ea043"
tmux_conf_theme_status_right_length=300
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `set -g status-right` overridden | Use `tmux_conf_theme_status_right=` (oh-my-tmux) or framework equivalent |
| `status2-right` → invalid option | Use `set -g status-format[1] "..."` |
| New bars not visible | `tmux show-options -g status` must equal bar count |
| Bar appears blank | Script must output exactly one non-empty line |
| Script works in terminal, blank in bar | tmux `#()` has minimal PATH — use `~/` or absolute paths |
| `%%` vs `%` confusion | `%%` in `tmux_conf_theme_*`; `%H:%M` directly in `status-format[]` |

## Reload

```bash
tmux source-file ~/.tmux.conf        # full reload (re-applies framework theming)
tmux source-file ~/.tmux.conf.local  # local overrides only
```
