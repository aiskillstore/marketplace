---
name: chrome-extension-icons
description: Search and generate icons for Chrome browser extensions. Automatically downloads SVG icons from Iconify (275,000+ free icons), converts them to required PNG sizes (16x16, 32x32, 48x48, 128x128), and updates manifest.json configuration. Use when the user mentions "extension icon", "browser extension icon", "chrome icon", "add icon to extension", "generate icon for extension", or when working with Chrome extension manifest.json icon setup. Supports color customization, local SVG conversion, and batch generation for multiple projects.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
version: 1.0.0
---

# Chrome Extension Icons

Generate professional icons for Chrome browser extensions in seconds using Iconify's vast library of 275,000+ free open-source icons.

## Quick Start Workflow

When the user requests an extension icon, follow these steps:

### 1. Understand the Request

Extract key information:
- **Icon theme/keyword**: What type of icon? (e.g., "calendar", "music", "settings", "bookmark")
- **Target directory**: Where to save icons (default: `./icons`)
- **Manifest location**: Path to manifest.json (default: `./manifest.json`)
- **Color preference**: Any specific color requirement (optional)
- **Context**: Is manifest.json already present? Is this a new project?

### 2. Search for Icons Automatically

Run the search command with the extracted keyword:

```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js search "<keyword>"
```

**Expected output**:
- List of matching icons with preview URLs
- Best match automatically identified
- Top 5 results displayed (best match + 4 alternatives)

**Present to user**:
- Show the best matching icon with its ID and preview link
- Briefly mention that 4 alternative options are also available if they want to choose differently
- Provide the preview URL so they can see what the icon looks like

**Example presentation**:
```
I found a great calendar icon for your extension:

Best match: mdi:calendar
Preview: https://icon-sets.iconify.design/mdi/icons/calendar.html

I'll generate this icon in 4 sizes (16x16, 32x32, 48x48, 128x128) for your Chrome extension.
If you'd prefer a different style, I also have 4 alternatives saved that you can choose from.

Shall I proceed with this icon?
```

### 3. Generate Icons

Once confirmed (or auto-proceed if user said "yes" to any icon), run:

```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js generate \
  --icon "<icon-id>" \
  --output "./icons" \
  --manifest "./manifest.json"
```

**With custom color** (if user specified a color):
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js generate \
  --icon "<icon-id>" \
  --output "./icons" \
  --manifest "./manifest.json" \
  --color "#ba3329"
```

### 4. Verify Results

After generation, check the output:

```bash
ls -lh ./icons/
```

Verify 4 PNG files are created:
- `icon16.png`
- `icon32.png`
- `icon48.png`
- `icon128.png`

Check manifest.json was updated:
```bash
cat ./manifest.json | grep -A 6 '"icons"'
```

### 5. Report to User

Provide a summary:

```
✅ Icon generation complete!

Generated files:
- icons/icon16.png (1.2 KB)
- icons/icon32.png (2.4 KB)
- icons/icon48.png (3.8 KB)
- icons/icon128.png (9.5 KB)

Your manifest.json has been updated:
{
  "icons": {
    "16": "icons/icon16.png",
    "32": "icons/icon32.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}

📌 Alternative icons (if you want to try a different style):
1. mdi:calendar-month - https://icon-sets.iconify.design/mdi/icons/calendar-month.html
2. fa:calendar - https://icon-sets.iconify.design/fa/icons/calendar.html
3. heroicons:calendar - https://icon-sets.iconify.design/heroicons/icons/calendar.html
4. carbon:calendar - https://icon-sets.iconify.design/carbon/icons/calendar.html

Just let me know if you'd like to try any of these alternatives!
```

## Advanced Features

### Custom Color Icons

When user requests a specific color (e.g., "make it red", "use my brand color #ba3329"):

```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js generate \
  --icon "mdi:home" \
  --color "#ba3329" \
  --output "./icons"
```

**Note**: Color customization works best with single-color SVG icons. Complex gradients may not render as expected.

### Convert Local SVG File

When user has their own logo or SVG file:

1. First check if the file exists:
   ```bash
   ls -lh <svg-file-path>
   ```

2. Convert it:
   ```bash
   node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js convert \
     --input "<svg-file-path>" \
     --output "./icons" \
     --manifest "./manifest.json"
   ```

3. Optionally apply color:
   ```bash
   node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js convert \
     --input "./logo.svg" \
     --output "./icons" \
     --color "#ff0000"
   ```

### Batch Generation

When user needs icons for multiple projects:

1. Create a configuration file `icons-config.json`:
   ```json
   {
     "projects": [
       {
         "name": "Project A",
         "icon": "mdi:calendar",
         "output": "./project-a/icons",
         "manifest": "./project-a/manifest.json"
       },
       {
         "name": "Project B",
         "icon": "mdi:music",
         "output": "./project-b/icons",
         "manifest": "./project-b/manifest.json",
         "color": "#ff0000"
       },
       {
         "name": "Project C",
         "input": "./project-c/logo.svg",
         "output": "./project-c/icons",
         "manifest": "./project-c/manifest.json"
       }
     ]
   }
   ```

2. Run batch generation:
   ```bash
   node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js batch \
     --config icons-config.json
   ```

3. Report summary showing success/failure for each project

## Chrome Extension Icon Requirements

Always inform users about Chrome's icon requirements:

- **16x16 pixels**: Favicon, toolbar icon (small displays)
- **32x32 pixels**: Windows taskbar (optional but recommended)
- **48x48 pixels**: Extension management page (**required**)
- **128x128 pixels**: Chrome Web Store, installation dialog (**required**)

**Format**: PNG only (SVG is not supported in manifest.json)

**Transparency**: Supported and recommended for non-square logos

**File size**: Aim for < 100 KB total for all 4 files

## Manifest.json Configuration

The script automatically creates or updates the `icons` field:

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "icons": {
    "16": "icons/icon16.png",
    "32": "icons/icon32.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

If `action` or `browser_action` exists, `default_icon` is also updated:

```json
{
  "action": {
    "default_icon": {
      "16": "icons/icon16.png",
      "32": "icons/icon32.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

## Error Handling

### Missing Dependencies

If the script fails with Sharp installation error:

**macOS**:
```bash
brew install vips
cd ~/.claude/skills/chrome-extension-icons && npm install
```

**Ubuntu/Debian**:
```bash
sudo apt-get install libvips-dev
cd ~/.claude/skills/chrome-extension-icons && npm install
```

**Windows**:
```bash
npm install --global windows-build-tools
cd ~/.claude/skills/chrome-extension-icons && npm install
```

Inform the user of these steps if installation fails.

### API Failures

The script has built-in retry logic (3 attempts with exponential backoff). If Iconify API fails:
- Suggest trying again in a moment
- Offer to use a local SVG if available
- Check internet connection

### Rate Limiting

If HTTP 429 error occurs, the script automatically waits and retries. Inform user:
```
The icon API is experiencing high traffic. Waiting 60 seconds before retry...
```

### Invalid Icon Selection

If an icon doesn't render well or user doesn't like it:
- Present the 4 saved alternative icons
- Offer to search for a different keyword
- Suggest using their own SVG file

## Best Practices

1. **Always preview**: Show the user the icon preview URL before generating
2. **Confirm before generating**: Unless user explicitly requested immediate action
3. **Check manifest.json exists**: If not, inform user a new one will be created
4. **Verify output**: Always run `ls` to confirm files were created successfully
5. **File sizes**: Report file sizes to ensure they're reasonable (< 20 KB each)
6. **Backup warning**: If manifest.json exists, mention it will be updated (not replaced)

## Common User Phrases That Trigger This Skill

- "I need an icon for my Chrome extension"
- "Add a calendar icon to my extension"
- "Generate extension icons"
- "Can you create icons for my browser extension?"
- "I need icons for manifest.json"
- "Convert my logo to Chrome extension format"
- "Make extension icons from this SVG"

## Examples

See [examples/usage.md](examples/usage.md) for detailed conversation examples and edge cases.

## Technical Details

- **Icon source**: Iconify API (https://iconify.design/)
- **Total icons**: 275,000+ from 200+ icon sets
- **Image processing**: Sharp library (high-performance Node.js)
- **Supported input**: SVG (from Iconify or local file)
- **Output format**: PNG with transparency
- **Node.js requirement**: >= 18.17.0

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Sharp won't install | Install libvips: `brew install vips` (macOS) |
| API timeout | Retry after a moment, check connection |
| Icon looks bad | Try a different icon from alternatives |
| Wrong colors | Use `--color` flag for single-color icons |
| File too large | Complex SVGs may create large PNGs, try simpler icon |
| Manifest not updating | Check file permissions, verify path is correct |

---

**Remember**: This skill automates a tedious process. Be helpful, present clear options, and make the experience smooth for the user. Always show preview links so users know what they're getting before generation.
