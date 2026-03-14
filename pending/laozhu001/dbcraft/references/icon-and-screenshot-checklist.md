# DB Craft Icon And Screenshot Checklist

## Purpose

Use this checklist to prepare marketplace-ready visual assets for DB Craft.

## 1. Icon Checklist

## Icon Goal

- Simple
- Product-like
- Recognizable at small sizes
- Consistent with the current `DB` square brand used in the app

## Icon Content Recommendation

- Main mark: `DB`
- Shape: rounded square
- Visual direction:
  - deep blue background
  - white or near-white letters
  - clean high contrast
- Avoid:
  - too much text
  - complex gradients that blur at small sizes
  - tiny database cylinder details that disappear when reduced

## Recommended Icon Deliverables

- [ ] `icon-1024.png`
- [ ] `icon-512.png`
- [ ] `icon-256.png`
- [ ] `icon-128.png`
- [ ] source file, for example:
  - `icon-source.svg`
  - or `icon-source.fig`

## Icon Review Criteria

- [ ] readable at `32x32`
- [ ] still recognizable on white backgrounds
- [ ] still recognizable on dark thumbnail strips
- [ ] matches DB Craft's current visual tone
- [ ] no copyrighted third-party logo elements

## 2. Screenshot Checklist

## Minimum Submission Set

- [ ] `01-main-workspace.png`
- [ ] `02-ai-build-or-sql-build.png`
- [ ] `03-sync-and-sql-preview.png`

## Recommended Extended Set

- [ ] `04-send-to-codex.png`
- [ ] `05-help-or-multilanguage.png`

## Screenshot 1: Main Workspace

File:
- `01-main-workspace.png`

What to show:
- DB Craft top bar
- current project information
- sample schema on canvas
- right-side inspector visible

Recommended source:
- open `D:\DBdesigner\samples\sample.dbmodel.json`

Goal:
- show the product at a glance
- communicate that this is a visual schema tool

Capture checklist:
- [ ] browser maximized
- [ ] no unrelated desktop clutter
- [ ] diagram centered
- [ ] enough tables visible to feel real, but not overcrowded
- [ ] language set to English for marketplace use unless the marketplace targets Chinese only

## Screenshot 2: AI Build Or SQL Build

File:
- `02-ai-build-or-sql-build.png`

Choose one primary scene:
- `AI Build` dialog open with model preset selector visible
- or `Build from SQL` dialog with a clean sample `CREATE TABLE` snippet

Goal:
- show that DB Craft can accelerate schema creation

Capture checklist:
- [ ] dialog fully visible
- [ ] no exposed real API key
- [ ] no private file path clutter unless necessary
- [ ] clear label showing AI preset or SQL import capability

## Screenshot 3: Sync And SQL Preview

File:
- `03-sync-and-sql-preview.png`

What to show:
- successful sync flow
- SQL preview dialog
- model path / SQL path if useful, but avoid overexposing highly local machine-specific details in the final public version

Goal:
- show the handoff outcome from modeling to SQL

Capture checklist:
- [ ] SQL content visible enough to feel real
- [ ] dialog not cropped
- [ ] avoid noisy temporary paths if a cleaner crop works

## Screenshot 4: Send To Codex

File:
- `04-send-to-codex.png`

What to show:
- `Send to Codex` panel
- handoff options
- positioning as a fallback or collaboration flow

Goal:
- highlight a differentiator

Use when:
- the marketplace allows multiple screenshots
- you want to emphasize the AI fallback and collaboration angle

## Screenshot 5: Help Or Multilanguage

File:
- `05-help-or-multilanguage.png`

Choose one:
- help manual page
- language switch with a localized interface

Goal:
- support trust and polish
- show that the product is not a rough prototype

## 3. Capture Standards

- [ ] use a clean browser window
- [ ] keep browser zoom at `100%`
- [ ] avoid showing unrelated bookmarks or personal browser profile noise
- [ ] hide sensitive email, token, or machine-specific information when not needed
- [ ] keep screenshots bright, readable, and high contrast
- [ ] export in `PNG`

## 4. Suggested Capture Flow

1. Open DB Craft
2. Open `D:\DBdesigner\samples\sample.dbmodel.json`
3. Run `Fit`
4. Make sure language is set to the target marketplace language
5. Capture the main workspace
6. Open AI Build or SQL Build and capture the second screenshot
7. Run Sync and capture SQL preview
8. Optionally capture Send to Codex and Help

## 5. Asset Folder Suggestion

Use one folder so the final submission package stays tidy:

- [ ] `marketplace-assets/icon/`
- [ ] `marketplace-assets/screenshots/`
- [ ] `marketplace-assets/demo/`

## 6. Final Asset Gate

Before submission, confirm:

- [ ] icon is final
- [ ] at least 3 polished screenshots are ready
- [ ] filenames are clean and consistent
- [ ] screenshots reflect the current product, not old UI states
- [ ] no secrets or confusing machine-specific noise are visible
