# Docs Creator Reference

## Paths
- **Content Root**: `src/content/docs/`
- **Engine**: `src/lib/docs/source.ts`
- **Icons**: [Lucide React](https://lucide.dev/icons)

## Frontmatter
```yaml
---
title: string
description: string
icon: string # Lucide icon name (e.g. "Home", "Settings")
full: boolean # true to hide sidebar (optional)
---
```

## Meta.json
```json
{
  "title": "Folder Title",
  "description": "Optional description",
  "icon": "IconName",
  "root": boolean, // true = Separate section/tab
  "defaultOpen": boolean,
  "pages": [
    "file-name", // No extension
    "folder-name",
    "---Separator---",
    "[External Link](https://...)"
  ]
}
```

## Components (Fumadocs UI)
```tsx
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';
import { Step, Steps } from 'fumadocs-ui/components/steps';
import { Callout } from 'fumadocs-ui/components/callout';

<Callout type="info">Info message</Callout>

<Steps>
  <Step>
    ### Step 1
    Do this
  </Step>
  <Step>
    ### Step 2
    Do that
  </Step>
</Steps>
```

