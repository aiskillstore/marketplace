# Chrome Extension Icons - Usage Examples

This document provides detailed usage examples for the Chrome Extension Icons skill, covering common scenarios and edge cases.

## Example 1: Basic Icon Generation

**User**: "I need a calendar icon for my Chrome extension"

**Claude Response**:
```
Let me search for calendar icons for you.
```

**Claude runs**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js search "calendar"
```

**Claude presents**:
```
I found a great calendar icon for your extension:

Best match: mdi:calendar
Preview: https://icon-sets.iconify.design/mdi/icons/calendar.html

I'll generate this icon in 4 sizes (16x16, 32x32, 48x48, 128x128) for your Chrome extension.
If you'd prefer a different style, I also have 4 alternatives saved.

Shall I proceed with this icon?
```

**User**: "Yes, that looks good"

**Claude runs**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js generate \
  --icon "mdi:calendar" \
  --output "./icons" \
  --manifest "./manifest.json"
```

**Claude reports**:
```
✅ Icon generation complete!

Generated files:
- icons/icon16.png (1.2 KB)
- icons/icon32.png (2.5 KB)
- icons/icon48.png (4.1 KB)
- icons/icon128.png (11.2 KB)

Your manifest.json has been updated with the icon paths.

📌 Alternative icons (if you want to try a different style):
1. mdi:calendar-month - https://icon-sets.iconify.design/mdi/icons/calendar-month.html
2. fa:calendar - https://icon-sets.iconify.design/fa/icons/calendar.html
3. heroicons:calendar - https://icon-sets.iconify.design/heroicons/icons/calendar.html
4. carbon:calendar - https://icon-sets.iconify.design/carbon/icons/calendar.html
```

---

## Example 2: Custom Color Icon

**User**: "Generate a home icon in my brand color #ba3329"

**Claude runs search**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js search "home"
```

**Claude presents**:
```
Found home icons. Best match: mdi:home
I'll generate it in your brand color #ba3329.
```

**Claude runs**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js generate \
  --icon "mdi:home" \
  --color "#ba3329" \
  --output "./icons" \
  --manifest "./manifest.json"
```

**Claude reports**:
```
✅ Icon generated with custom color #ba3329!

Generated files:
- icons/icon16.png (1.4 KB)
- icons/icon32.png (2.8 KB)
- icons/icon48.png (4.5 KB)
- icons/icon128.png (12.1 KB)

manifest.json updated successfully.
```

---

## Example 3: User Doesn't Like First Result

**User**: "I need a music icon for my extension"

**Claude searches and presents**: mdi:music

**User**: "That looks too simple, do you have something more detailed?"

**Claude responds**:
```
Of course! Here are the 4 alternative music icons I found:

1. mdi:music-note - More detailed musical note
   Preview: https://icon-sets.iconify.design/mdi/icons/music-note.html

2. fa:music - Classic Font Awesome style
   Preview: https://icon-sets.iconify.design/fa/icons/music.html

3. heroicons:musical-note - Modern outline style
   Preview: https://icon-sets.iconify.design/heroicons/icons/musical-note.html

4. carbon:music - IBM Carbon design
   Preview: https://icon-sets.iconify.design/carbon/icons/music.html

Which one would you prefer?
```

**User**: "The third one looks perfect"

**Claude runs**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js generate \
  --icon "heroicons:musical-note" \
  --output "./icons" \
  --manifest "./manifest.json"
```

---

## Example 4: Convert Local SVG Logo

**User**: "I have my company logo in logo.svg, can you convert it to Chrome extension icons?"

**Claude checks file**:
```bash
ls -lh logo.svg
```

**Claude responds**:
```
Perfect! I found your logo.svg file (3.2 KB). I'll convert it to the 4 required PNG sizes for Chrome extensions.
```

**Claude runs**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js convert \
  --input "./logo.svg" \
  --output "./icons" \
  --manifest "./manifest.json"
```

**Claude reports**:
```
✅ Conversion complete!

Your logo has been converted to:
- icons/icon16.png (1.8 KB)
- icons/icon32.png (3.2 KB)
- icons/icon48.png (5.1 KB)
- icons/icon128.png (14.8 KB)

manifest.json has been updated with the new icon paths.
```

---

## Example 5: Batch Generation for Multiple Projects

**User**: "I'm working on 3 Chrome extensions and need icons for all of them. Project A needs a calendar icon, Project B needs a music icon, and Project C needs a settings icon."

**Claude creates config file**:
```json
{
  "projects": [
    {
      "name": "Project A - Calendar Extension",
      "icon": "mdi:calendar",
      "output": "./project-a/icons",
      "manifest": "./project-a/manifest.json"
    },
    {
      "name": "Project B - Music Extension",
      "icon": "mdi:music",
      "output": "./project-b/icons",
      "manifest": "./project-b/manifest.json"
    },
    {
      "name": "Project C - Settings Extension",
      "icon": "mdi:cog",
      "output": "./project-c/icons",
      "manifest": "./project-c/manifest.json"
    }
  ]
}
```

**Claude writes file**:
```bash
cat > icons-batch-config.json << 'EOF'
{ ... config content ... }
EOF
```

**Claude runs batch**:
```bash
node ~/.claude/skills/chrome-extension-icons/scripts/generate-icons.js batch \
  --config icons-batch-config.json
```

**Claude reports**:
```
✅ Batch generation complete!

Summary:
✓ Project A - Calendar Extension: Success (4 icons, 18.9 KB total)
✓ Project B - Music Extension: Success (4 icons, 19.2 KB total)
✓ Project C - Settings Extension: Success (4 icons, 20.1 KB total)

All 3 projects completed successfully!
Each manifest.json has been updated with the icon paths.
```

---

## Example 6: Error Recovery - Missing Dependencies

**User**: "Generate a star icon for my extension"

**Claude runs generate command, but it fails**:

**Claude detects Sharp error**:
```
❌ Failed to load sharp. Please install it: npm install sharp
```

**Claude responds**:
```
I encountered an issue with the image processing library (Sharp). Let me help you install it.

For macOS, run:
```bash
brew install vips
cd ~/.claude/skills/chrome-extension-icons && npm install
```

Would you like me to try installing it automatically?
```

**User**: "Yes please"

**Claude runs**:
```bash
cd ~/.claude/skills/chrome-extension-icons && npm install
```

**After installation**:
```
✅ Dependencies installed successfully! Now generating your star icon...
```

---

## Example 7: Working with Existing Extension

**User**: "My extension already has icons, but I want to replace them with a better design. Can you help?"

**Claude checks current setup**:
```bash
cat manifest.json | grep -A 6 '"icons"'
ls -lh icons/
```

**Claude responds**:
```
I can see your extension currently has icons set up. I'll search for a new design and replace them.

What theme or keyword should I search for? (e.g., "modern star", "minimalist bookmark", etc.)
```

**User**: "Modern bookmark icon"

**Claude searches, presents options, and after confirmation**:
```
I'll replace your existing icons with the new design. Your old icons will be overwritten.

Proceeding with icon generation...
```

**Claude runs generate and reports**:
```
✅ Icons replaced successfully!

Note: Existing icons were overwritten (consider backing them up before running).
New icons generated:
- icons/icon16.png (1.3 KB)
- icons/icon32.png (2.6 KB)
- icons/icon48.png (4.2 KB)
- icons/icon128.png (11.8 KB)

manifest.json updated with new icon paths.
```

---

## Example 8: No manifest.json Present

**User**: "Create icons for my new extension project"

**Claude checks for manifest**:
```bash
ls manifest.json
```

**File doesn't exist, Claude responds**:
```
I notice you don't have a manifest.json file yet. I'll create one for you along with the icons.

What type of icon would you like to search for?
```

**User**: "Bookmark icon"

**Claude generates and reports**:
```
✅ Setup complete!

Created:
- manifest.json (basic Chrome Extension manifest)
- icons/icon16.png (1.2 KB)
- icons/icon32.png (2.4 KB)
- icons/icon48.png (3.9 KB)
- icons/icon128.png (10.5 KB)

Your new manifest.json includes:
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

You can now customize the name, version, and other fields in manifest.json.
```

---

## Example 9: Complex Color Customization

**User**: "I need a settings icon, but the colors in my extension are #2563eb for primary and #1e40af for secondary. Can you make the icon match?"

**Claude responds**:
```
Color customization works best with single-color SVG icons. I'll generate the icon with your primary color #2563eb.

Note: If the icon has multiple colors, only solid fills will be replaced. Gradients and complex effects may not render as expected.

Shall I proceed?
```

**User**: "Yes"

**Claude generates with color and checks result**:
```
✅ Icon generated with color #2563eb!

If the colors don't look quite right, I can:
1. Try a different icon style that might work better with color customization
2. Generate in a different color
3. Use your original logo/SVG if you have one

Would you like to see the result first, or shall we try an alternative?
```

---

## Example 10: Troubleshooting - API Failure

**User**: "Generate a clock icon"

**Claude runs command, but Iconify API is temporarily down**:

**Claude detects retry attempts**:
```
⏳ Attempting to download icon... (attempt 1/3)
⚠️  API request failed. Retrying in 2 seconds...
⏳ Attempting to download icon... (attempt 2/3)
✓ Successfully downloaded icon
```

**Claude reports**:
```
✅ Icon generated successfully!

Note: There was a temporary network issue, but the script automatically retried and succeeded.

Generated files:
- icons/icon16.png (1.4 KB)
- icons/icon32.png (2.7 KB)
- icons/icon48.png (4.3 KB)
- icons/icon128.png (11.9 KB)
```

---

## Edge Cases

### Large File Sizes

If generated PNGs are > 20 KB each:
```
⚠️  Notice: The generated icons are larger than typical (icon128.png is 45 KB).
    This might be due to a complex SVG design.

Suggestions:
1. Try a simpler icon style
2. Use a minimalist icon set like "heroicons" or "lucide"
3. Manually optimize the PNG files with a tool like TinyPNG
```

### No Results Found

If search returns no results:
```
❌ No icons found for keyword "xyzabc123".

Suggestions:
1. Try a more common keyword (e.g., "home", "user", "settings")
2. Use synonyms (e.g., "person" instead of "user")
3. Browse icon sets directly: https://icon-sets.iconify.design/
4. Use your own SVG logo instead
```

### Permission Errors

If manifest.json or icons directory has permission issues:
```
❌ Permission denied: Cannot write to ./icons/

Please check:
1. Directory permissions: chmod 755 ./icons
2. File permissions: chmod 644 ./icons/*.png
3. Current working directory: pwd

Would you like me to help troubleshoot?
```

---

## Best Practices Summary

1. **Always show preview**: Let users see what they're getting
2. **Save alternatives**: Store top 5 for easy switching
3. **Verify output**: Check files were created and sizes are reasonable
4. **Handle errors gracefully**: Provide clear solutions for common problems
5. **Inform about changes**: Tell users when manifest.json is being created/updated
6. **Offer choices**: Present alternatives when users aren't satisfied

These examples should help you handle various scenarios when users request Chrome extension icons.
