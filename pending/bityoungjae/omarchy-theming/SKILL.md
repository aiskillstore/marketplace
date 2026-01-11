---
name: omarchy-theming
description: Create and manage Omarchy desktop themes. Use when working with colors.toml, terminal themes (Alacritty/Kitty/Ghostty), Hyprland colors, Waybar styling, btop themes, or theme installation/removal.
---

# Omarchy Theme Creation

Create themes for Omarchy by defining colors in `colors.toml`. Colors automatically propagate to all desktop applications.

## Quick Start

<steps>
1. Create theme directory:
   ```bash
   mkdir -p ~/.config/omarchy/themes/my-theme/backgrounds
   ```

2. Create `colors.toml` with all 22 required variables (see schema below)

3. Add wallpaper images to `backgrounds/`

4. Apply theme:
   ```bash
   omarchy-theme-set my-theme
   ```
</steps>

## Instructions

When creating or modifying Omarchy themes:

1. **Always define all 22 color variables** in `colors.toml` - missing variables cause errors
2. **Use HEX format only** (`#RRGGBB`) - no RGB, HSL, or named colors
3. **Include `backgrounds/` directory** with at least one wallpaper image
4. **For light themes**, create empty `light.mode` file in theme directory
5. **Test with `omarchy-theme-set`** after changes

For detailed variable usage per application, see [reference.md](reference.md).

## Theme Structure

```
~/.config/omarchy/themes/{theme-name}/
├── colors.toml        # [Required] 22 color definitions
├── backgrounds/       # [Required] Wallpaper images (PNG/JPG)
├── preview.png        # [Recommended] Theme preview
├── icons.theme        # [Recommended] GTK icon theme name
├── neovim.lua         # [Recommended] LazyVim colorscheme
├── vscode.json        # [Recommended] VS Code theme metadata
├── btop.theme         # [Recommended] btop color theme
├── light.mode         # [Optional] Empty file = light theme
├── chromium.theme     # [Optional] Browser theme RGB
└── hyprland.conf      # [Optional] Static Hyprland override
```

## colors.toml Schema

<schema>
```toml
# Core UI (6 variables)
accent = "#89b4fa"                 # Primary accent color
cursor = "#f5e0dc"                 # Terminal cursor
foreground = "#cdd6f4"             # Primary text
background = "#1e1e2e"             # Primary background
selection_foreground = "#1e1e2e"   # Selected text foreground
selection_background = "#f5e0dc"   # Selected text background

# ANSI Normal (8 variables)
color0 = "#45475a"    # Black
color1 = "#f38ba8"    # Red (errors)
color2 = "#a6e3a1"    # Green (success)
color3 = "#f9e2af"    # Yellow (warnings)
color4 = "#89b4fa"    # Blue (links)
color5 = "#f5c2e7"    # Magenta (special)
color6 = "#94e2d5"    # Cyan (code)
color7 = "#bac2de"    # White (text)

# ANSI Bright (8 variables)
color8 = "#585b70"    # Bright Black (muted/disabled)
color9 = "#f38ba8"    # Bright Red
color10 = "#a6e3a1"   # Bright Green
color11 = "#f9e2af"   # Bright Yellow
color12 = "#89b4fa"   # Bright Blue
color13 = "#f5c2e7"   # Bright Magenta
color14 = "#94e2d5"   # Bright Cyan
color15 = "#a6adc8"   # Bright White
```
</schema>

## Template Variables

Each color supports 3 formats for different contexts:

| Format | Example | Output | Use Case |
|--------|---------|--------|----------|
| `{{ name }}` | `{{ accent }}` | `#89b4fa` | CSS, TOML |
| `{{ name_strip }}` | `{{ accent_strip }}` | `89b4fa` | Hyprland `rgb()` |
| `{{ name_rgb }}` | `{{ accent_rgb }}` | `137,180,250` | RGBA values |

## Examples

<example title="Dark Theme (Tokyo Night)">
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
</example>

<example title="Light Theme (Catppuccin Latte)">
```toml
# Note: Create empty light.mode file for light themes
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
</example>

<example title="neovim.lua">
```lua
return {
    { "folke/tokyonight.nvim", priority = 1000 },
    { "LazyVim/LazyVim", opts = { colorscheme = "tokyonight" } },
}
```
</example>

<example title="vscode.json">
```json
{ "name": "Tokyo Night", "extension": "enkia.tokyo-night" }
```
</example>

## Theme Commands

```bash
omarchy-theme-set my-theme      # Apply theme
omarchy-theme-current           # Show current theme
omarchy-theme-list              # List available themes
omarchy-theme-install <git-url> # Install from git
omarchy-theme-remove my-theme   # Remove theme
omarchy-theme-update            # Update git themes
omarchy-theme-bg-next           # Cycle wallpaper
```

## Troubleshooting

<troubleshooting>
**Colors not applying:**
- Verify all 22 variables defined
- Check HEX format (`#RRGGBB`)
- Run `omarchy-theme-set` to regenerate

**App not themed:**
- Place static config in theme folder to override template
- Check variable names match colors.toml keys

**yq errors:**
```bash
sudo pacman -S yq
```
</troubleshooting>
