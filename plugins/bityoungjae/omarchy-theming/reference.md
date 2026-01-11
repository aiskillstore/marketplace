# Omarchy Theme Variable Reference

Detailed reference for color variables and application-specific template usage. Use this when customizing templates or troubleshooting theme integration.

<reference_summary>
- **22 required variables**: 6 core UI + 16 ANSI colors
- **3 format suffixes**: `{{ var }}`, `{{ var_strip }}`, `{{ var_rgb }}`
- **Template location**: `$OMARCHY_PATH/default/themed/*.tpl`
</reference_summary>

## Variable Quick Reference

<variables>
| Variable | Purpose | Semantic Use |
|----------|---------|--------------|
| `accent` | Primary accent | Borders, buttons, highlights |
| `cursor` | Terminal cursor | Cursor color |
| `foreground` | Primary text | Main text color |
| `background` | Primary background | Main bg color |
| `selection_foreground` | Selected text fg | Selection text |
| `selection_background` | Selected text bg | Selection highlight |
| `color0` | Black | Dark surfaces |
| `color1` | Red | Errors, destructive |
| `color2` | Green | Success, confirmations |
| `color3` | Yellow | Warnings, attention |
| `color4` | Blue | Links, info |
| `color5` | Magenta | Special highlights |
| `color6` | Cyan | Code, secondary info |
| `color7` | White | Light text |
| `color8` | Bright Black | Muted, disabled, dividers |
| `color9-15` | Bright variants | Higher contrast versions |
</variables>

## Format Suffixes

| Suffix | Example | Output | Use Case |
|--------|---------|--------|----------|
| (none) | `{{ accent }}` | `#89b4fa` | CSS, TOML, JSON |
| `_strip` | `{{ accent_strip }}` | `89b4fa` | Hyprland `rgb()` |
| `_rgb` | `{{ accent_rgb }}` | `137,180,250` | RGBA values |

## Application Templates

### Terminal Emulators

#### Alacritty (`alacritty.toml.tpl`)

```toml
[colors.primary]
background = "{{ background }}"
foreground = "{{ foreground }}"

[colors.cursor]
text = "{{ background }}"
cursor = "{{ cursor }}"

[colors.selection]
text = "{{ selection_foreground }}"
background = "{{ selection_background }}"

[colors.search.matches]
foreground = "{{ background }}"
background = "{{ color3 }}"

[colors.search.focused_match]
foreground = "{{ background }}"
background = "{{ color1 }}"

[colors.normal]
black = "{{ color0 }}"
red = "{{ color1 }}"
green = "{{ color2 }}"
yellow = "{{ color3 }}"
blue = "{{ color4 }}"
magenta = "{{ color5 }}"
cyan = "{{ color6 }}"
white = "{{ color7 }}"

[colors.bright]
black = "{{ color8 }}"
red = "{{ color9 }}"
green = "{{ color10 }}"
yellow = "{{ color11 }}"
blue = "{{ color12 }}"
magenta = "{{ color13 }}"
cyan = "{{ color14 }}"
white = "{{ color15 }}"
```

#### Kitty (`kitty.conf.tpl`)

```
foreground {{ foreground }}
background {{ background }}
selection_foreground {{ selection_foreground }}
selection_background {{ selection_background }}
cursor {{ cursor }}
cursor_text_color {{ background }}
active_border_color {{ accent }}
active_tab_background {{ accent }}
color0 {{ color0 }}
...
color15 {{ color15 }}
```

#### Ghostty (`ghostty.conf.tpl`)

```
background = {{ background }}
foreground = {{ foreground }}
cursor-color = {{ cursor }}
selection-background = {{ selection_background }}
selection-foreground = {{ selection_foreground }}
palette = 0={{ color0 }}
...
palette = 15={{ color15 }}
```

### Window Manager

#### Hyprland (`hyprland.conf.tpl`)

Uses `_strip` format for rgb() function:

```
$activeBorderColor = rgb({{ accent_strip }})

general {
    col.active_border = $activeBorderColor
}

group {
    col.border_active = $activeBorderColor
}
```

#### Hyprlock (`hyprlock.conf.tpl`)

Uses `_rgb` format for rgba() values:

```
$color = rgba({{ background_rgb }}, 1.0)
$inner_color = rgba({{ background_rgb }}, 0.8)
$outer_color = rgba({{ foreground_rgb }}, 1.0)
$font_color = rgba({{ foreground_rgb }}, 1.0)
$check_color = rgba({{ accent_rgb }}, 1.0)
```

### Status Bar & Launcher

#### Waybar (`waybar.css.tpl`)

```css
@define-color foreground {{ foreground }};
@define-color background {{ background }};
```

#### Walker (`walker.css.tpl`)

```css
@define-color selected-text {{ accent }};
@define-color text {{ foreground }};
@define-color base {{ background }};
@define-color border {{ foreground }};
@define-color foreground {{ foreground }};
@define-color background {{ background }};
```

### Notifications & OSD

#### Mako (`mako.ini.tpl`)

```ini
text-color={{ foreground }}
border-color={{ accent }}
background-color={{ background }}
```

#### SwayOSD (`swayosd.css.tpl`)

```css
@define-color background-color {{ background }};
@define-color border-color {{ foreground }};
@define-color label {{ foreground }};
@define-color image {{ foreground }};
@define-color progress {{ accent }};
```

### System Monitor

#### btop (`btop.theme.tpl`)

Extensive use of semantic colors:

```
theme[main_bg]="{{ background }}"
theme[main_fg]="{{ foreground }}"
theme[title]="{{ foreground }}"
theme[hi_fg]="{{ accent }}"
theme[selected_bg]="{{ color8 }}"
theme[selected_fg]="{{ accent }}"
theme[inactive_fg]="{{ color8 }}"
theme[graph_text]="{{ foreground }}"
theme[meter_bg]="{{ color8 }}"
theme[proc_misc]="{{ foreground }}"

# Box outlines
theme[cpu_box]="{{ color5 }}"
theme[mem_box]="{{ color2 }}"
theme[net_box]="{{ color1 }}"
theme[proc_box]="{{ accent }}"
theme[div_line]="{{ color8 }}"

# Temperature gradient
theme[temp_start]="{{ color2 }}"
theme[temp_mid]="{{ color3 }}"
theme[temp_end]="{{ color1 }}"

# CPU gradient
theme[cpu_start]="{{ color6 }}"
theme[cpu_mid]="{{ color4 }}"
theme[cpu_end]="{{ color5 }}"

# Memory gradients
theme[free_start]="{{ color5 }}"
theme[free_mid]="{{ color4 }}"
theme[free_end]="{{ color6 }}"

theme[cached_start]="{{ color4 }}"
theme[cached_mid]="{{ color6 }}"
theme[cached_end]="{{ color5 }}"

theme[available_start]="{{ color3 }}"
theme[available_mid]="{{ color1 }}"
theme[available_end]="{{ color1 }}"

theme[used_start]="{{ color2 }}"
theme[used_mid]="{{ color6 }}"
theme[used_end]="{{ color4 }}"

# Network gradients
theme[download_start]="{{ color3 }}"
theme[download_mid]="{{ color1 }}"
theme[download_end]="{{ color1 }}"

theme[upload_start]="{{ color2 }}"
theme[upload_mid]="{{ color6 }}"
theme[upload_end]="{{ color4 }}"

# Process gradient
theme[process_start]="{{ color6 }}"
theme[process_mid]="{{ color4 }}"
theme[process_end]="{{ color5 }}"
```

### Applications

#### Obsidian (`obsidian.css.tpl`)

```css
.theme-dark, .theme-light {
  --background-primary: {{ background }};
  --text-normal: {{ foreground }};
  --text-selection: {{ selection_background }};
  --background-modifier-border: {{ color8 }};

  /* Semantic heading colors */
  --text-title-h1: {{ color1 }};
  --text-title-h2: {{ color2 }};
  --text-title-h3: {{ color3 }};
  --text-title-h4: {{ color4 }};
  --text-title-h5: {{ color5 }};
  --text-title-h6: {{ color5 }};

  /* Links and accents */
  --text-link: {{ color4 }};
  --text-accent: {{ accent }};
  --interactive-accent: {{ accent }};

  /* Muted text */
  --text-muted: {{ color8 }};
  --text-faint: {{ color8 }};

  /* Code */
  --code-normal: {{ color6 }};

  /* Errors and success */
  --text-error: {{ color1 }};
  --text-success: {{ color2 }};

  /* Tags */
  --tag-color: {{ color6 }};
  --tag-background: {{ color8 }};

  /* Graph */
  --graph-line: {{ color8 }};
  --graph-node: {{ accent }};
  --graph-node-focused: {{ color4 }};
  --graph-node-tag: {{ color6 }};
  --graph-node-attachment: {{ color2 }};
}

/* Syntax highlighting */
.cm-s-obsidian span.cm-keyword { color: {{ color1 }}; }
.cm-s-obsidian span.cm-string { color: {{ color2 }}; }
.cm-s-obsidian span.cm-number { color: {{ color3 }}; }
.cm-s-obsidian span.cm-comment { color: {{ color8 }}; }
.cm-s-obsidian span.cm-operator { color: {{ color4 }}; }
.cm-s-obsidian span.cm-def { color: {{ color4 }}; }
```

#### Chromium (`chromium.theme.tpl`)

Uses `_rgb` format for browser theme:

```
{{ background_rgb }}
```

#### Hyprland Share Picker (`hyprland-preview-share-picker.css.tpl`)

```css
@define-color foreground {{ foreground }};
@define-color background {{ background }};
@define-color accent {{ accent }};
@define-color muted {{ color8 }};
@define-color card_bg {{ color0 }};
@define-color text_dark {{ background }};
@define-color accent_hover {{ color12 }};
@define-color selected_tab {{ accent }};
@define-color text {{ foreground }};
```

## Additional Theme Files

### btop.theme

Static btop theme file with 45+ color variables. Placed directly in theme directory (not generated from template):

```
theme[main_bg]="#1e1e2e"
theme[main_fg]="#cdd6f4"
theme[title]="#cdd6f4"
theme[hi_fg]="#89b4fa"
theme[selected_bg]="#585b70"
theme[selected_fg]="#89b4fa"
theme[inactive_fg]="#585b70"
theme[graph_text]="#cdd6f4"
theme[meter_bg]="#585b70"
theme[proc_misc]="#cdd6f4"

# Box outlines
theme[cpu_box]="#f5c2e7"
theme[mem_box]="#a6e3a1"
theme[net_box]="#f38ba8"
theme[proc_box]="#89b4fa"
theme[div_line]="#585b70"

# Temperature/CPU/Memory gradients
theme[temp_start]="#a6e3a1"
theme[temp_mid]="#f9e2af"
theme[temp_end]="#f38ba8"
theme[cpu_start]="#94e2d5"
theme[cpu_mid]="#89b4fa"
theme[cpu_end]="#f5c2e7"
```

### icons.theme

Single line with GTK icon theme name:

```
Yaru-blue
```

Common icon themes: `Yaru-blue`, `Yaru-purple`, `Papirus-Dark`, `Adwaita`

### light.mode

Empty marker file. Presence indicates light theme:

```bash
# Create light mode marker
touch ~/.config/omarchy/themes/my-theme/light.mode
```

When present:
- GNOME uses `prefer-light` color scheme
- GTK uses `Adwaita` theme (not `Adwaita-dark`)
- Browser sets light color scheme

### chromium.theme

Single line with RGB decimal values for browser theme color:

```
239,241,245
```

Format: `R,G,B` where each value is 0-255. Used by `omarchy-theme-set-browser` for Chromium/Brave/Helium.

### hyprland.conf

Static Hyprland configuration override. Placed in theme directory to override template-generated config:

```
$activeBorderColor = rgb(7aa2f7)

general {
    col.active_border = $activeBorderColor
    col.inactive_border = rgb(32344a)
}

group {
    col.border_active = $activeBorderColor
}
```

## Color Palette Guidelines

### Standard ANSI Color Semantics

| Index | Name | Typical Use |
|-------|------|-------------|
| 0 | Black | Dark surfaces, code backgrounds |
| 1 | Red | Errors, deletions, warnings |
| 2 | Green | Success, additions, confirmations |
| 3 | Yellow | Warnings, highlights, attention |
| 4 | Blue | Links, info, primary actions |
| 5 | Magenta | Special, keywords, decorative |
| 6 | Cyan | Secondary info, strings, paths |
| 7 | White | Primary text (dark themes) |
| 8 | Bright Black | Muted text, comments, disabled |
| 9-15 | Bright variants | Higher contrast versions |

### Contrast Recommendations

**Dark themes:**
- `background` should be #1a-#2e range
- `foreground` should be #a0-#f0 range
- `color8` between background and foreground (muted)

**Light themes:**
- `background` should be #e0-#ff range
- `foreground` should be #20-#60 range
- `color8` lighter than foreground (muted)

### Accent Color Tips

- Choose a vibrant, distinctive color
- Should have good contrast against both background and foreground
- Often matches `color4` (blue) or a unique theme color
- Used heavily in UI (borders, buttons, selections)

## Existing Theme Palettes

### Catppuccin (Mocha - Dark)

```toml
accent = "#89b4fa"
cursor = "#f5e0dc"
foreground = "#cdd6f4"
background = "#1e1e2e"
selection_foreground = "#1e1e2e"
selection_background = "#f5e0dc"
color0 = "#45475a"
color1 = "#f38ba8"
color2 = "#a6e3a1"
color3 = "#f9e2af"
color4 = "#89b4fa"
color5 = "#f5c2e7"
color6 = "#94e2d5"
color7 = "#bac2de"
color8 = "#585b70"
color9 = "#f38ba8"
color10 = "#a6e3a1"
color11 = "#f9e2af"
color12 = "#89b4fa"
color13 = "#f5c2e7"
color14 = "#94e2d5"
color15 = "#a6adc8"
```

### Catppuccin Latte (Light)

```toml
accent = "#1e66f5"
cursor = "#dc8a78"
foreground = "#4c4f69"
background = "#eff1f5"
selection_foreground = "#eff1f5"
selection_background = "#dc8a78"
color0 = "#bcc0cc"
color1 = "#d20f39"
color2 = "#40a02b"
color3 = "#df8e1d"
color4 = "#1e66f5"
color5 = "#ea76cb"
color6 = "#179299"
color7 = "#5c5f77"
color8 = "#acb0be"
color9 = "#d20f39"
color10 = "#40a02b"
color11 = "#df8e1d"
color12 = "#1e66f5"
color13 = "#ea76cb"
color14 = "#179299"
color15 = "#6c6f85"
```

### Tokyo Night (Dark)

```toml
accent = "#7aa2f7"
cursor = "#c0caf5"
foreground = "#a9b1d6"
background = "#1a1b26"
selection_foreground = "#c0caf5"
selection_background = "#7aa2f7"
color0 = "#32344a"
color1 = "#f7768e"
color2 = "#9ece6a"
color3 = "#e0af68"
color4 = "#7aa2f7"
color5 = "#ad8ee6"
color6 = "#449dab"
color7 = "#787c99"
color8 = "#444b6a"
color9 = "#ff7a93"
color10 = "#b9f27c"
color11 = "#ff9e64"
color12 = "#7da6ff"
color13 = "#bb9af7"
color14 = "#0db9d7"
color15 = "#acb0d0"
```

### Gruvbox (Dark)

```toml
accent = "#7daea3"
cursor = "#bdae93"
foreground = "#d4be98"
background = "#282828"
selection_foreground = "#ebdbb2"
selection_background = "#d65d0e"
color0 = "#3c3836"
color1 = "#ea6962"
color2 = "#a9b665"
color3 = "#d8a657"
color4 = "#7daea3"
color5 = "#d3869b"
color6 = "#89b482"
color7 = "#d4be98"
color8 = "#3c3836"
color9 = "#ea6962"
color10 = "#a9b665"
color11 = "#d8a657"
color12 = "#7daea3"
color13 = "#d3869b"
color14 = "#89b482"
color15 = "#d4be98"
```

### Flexoki Light (requires `light.mode` file)

```toml
accent = "#205EA6"
cursor = "#100F0F"
foreground = "#100F0F"
background = "#FFFCF0"
selection_foreground = "#100F0F"
selection_background = "#E6E4D9"
color0 = "#100F0F"
color1 = "#AF3029"
color2 = "#66800B"
color3 = "#AD8301"
color4 = "#205EA6"
color5 = "#A02F6F"
color6 = "#24837B"
color7 = "#6F6E69"
color8 = "#575653"
color9 = "#D14D41"
color10 = "#879A39"
color11 = "#D0A215"
color12 = "#4385BE"
color13 = "#CE5D97"
color14 = "#3AA99F"
color15 = "#343331"
```

## Complete Light Theme Structure

A complete light theme directory includes the `light.mode` marker:

```
flexoki-light/
├── colors.toml        # Light color palette
├── backgrounds/       # Light-appropriate wallpapers
├── preview.png        # Theme preview
├── icons.theme        # Light-friendly icon theme
├── neovim.lua         # Light colorscheme
├── vscode.json        # Light VS Code theme
├── btop.theme         # Light btop colors
├── chromium.theme     # Light browser RGB
└── light.mode         # Empty file (marker for light mode)
```
