# Plate.js Reference

## 1. Installation Commands

### Core & UI
```bash
pnpm dlx shadcn@latest add @plate/editor
```

### Basic Marks & Toolbar
```bash
pnpm dlx shadcn@latest add @plate/basic-nodes-kit @plate/fixed-toolbar @plate/mark-toolbar-button
```

### Full "Basic" Suite (Shortcut for Detailed Editors)
```bash
pnpm dlx shadcn@latest add @plate/editor-basic
```

## 2. Project Structure
Recommended path for editor implementations:
- `src/components/plate-editor/simple-editor.tsx`
- `src/components/plate-editor/detailed-editor.tsx`
- `src/components/ui/` (contains `editor.tsx`, `fixed-toolbar.tsx`, etc. - managed by shadcn)

## 3. Configuration Examples

### A. Small Editor (Basic Marks)
Use for comments, chat inputs, or simple descriptions.

```tsx
'use client';

import * as React from 'react';
import { Plate, usePlateEditor } from 'platejs/react';
import { BoldPlugin, ItalicPlugin, UnderlinePlugin } from '@platejs/basic-nodes/react';
import { Editor, EditorContainer } from '@/components/ui/editor';
import { FixedToolbar } from '@/components/ui/fixed-toolbar';
import { MarkToolbarButton } from '@/components/ui/mark-toolbar-button';

export function SimpleEditor() {
  const editor = usePlateEditor({
    plugins: [BoldPlugin, ItalicPlugin, UnderlinePlugin],
    value: [{ type: 'p', children: [{ text: '' }] }],
  });

  return (
    <Plate editor={editor}>
      <FixedToolbar className="justify-start rounded-t-lg border-b p-2">
        <MarkToolbarButton nodeType="bold" tooltip="Bold (⌘+B)">B</MarkToolbarButton>
        <MarkToolbarButton nodeType="italic" tooltip="Italic (⌘+I)">I</MarkToolbarButton>
        <MarkToolbarButton nodeType="underline" tooltip="Underline (⌘+U)">U</MarkToolbarButton>
      </FixedToolbar>
      <EditorContainer>
        <Editor placeholder="Type here..." className="p-4" />
      </EditorContainer>
    </Plate>
  );
}
```

### B. Detailed Editor (Elements + Marks)
Use for blog posts, document editing, or rich content fields.

```tsx
'use client';

import * as React from 'react';
import { Plate, usePlateEditor } from 'platejs/react';
import {
  BlockquotePlugin, BoldPlugin, H1Plugin, H2Plugin, H3Plugin,
  ItalicPlugin, UnderlinePlugin
} from '@platejs/basic-nodes/react';
import { BlockquoteElement } from '@/components/ui/blockquote-node';
import { Editor, EditorContainer } from '@/components/ui/editor';
import { FixedToolbar } from '@/components/ui/fixed-toolbar';
import { H1Element, H2Element, H3Element } from '@/components/ui/heading-node';
import { MarkToolbarButton } from '@/components/ui/mark-toolbar-button';
import { ToolbarButton } from '@/components/ui/toolbar';

export function DetailedEditor() {
  const editor = usePlateEditor({
    plugins: [
      BoldPlugin,
      ItalicPlugin,
      UnderlinePlugin,
      H1Plugin.withComponent(H1Element),
      H2Plugin.withComponent(H2Element),
      H3Plugin.withComponent(H3Element),
      BlockquotePlugin.withComponent(BlockquoteElement),
    ],
    value: [{ type: 'h1', children: [{ text: 'Untitled' }] }],
  });

  return (
    <Plate editor={editor}>
      <FixedToolbar className="flex justify-start gap-1 rounded-t-lg border-b p-2">
        {/* Elements */}
        <ToolbarButton onClick={() => editor.tf.h1.toggle()}>H1</ToolbarButton>
        <ToolbarButton onClick={() => editor.tf.h2.toggle()}>H2</ToolbarButton>
        <ToolbarButton onClick={() => editor.tf.h3.toggle()}>H3</ToolbarButton>
        <ToolbarButton onClick={() => editor.tf.blockquote.toggle()}>Quote</ToolbarButton>
        <div className="mx-2 h-6 w-px bg-border" />
        {/* Marks */}
        <MarkToolbarButton nodeType="bold" tooltip="Bold (⌘+B)">B</MarkToolbarButton>
        <MarkToolbarButton nodeType="italic" tooltip="Italic (⌘+I)">I</MarkToolbarButton>
        <MarkToolbarButton nodeType="underline" tooltip="Underline (⌘+U)">U</MarkToolbarButton>
      </FixedToolbar>
      <EditorContainer>
        <Editor placeholder="Start writing..." className="min-h-[300px] p-6" />
      </EditorContainer>
    </Plate>
  );
}
```

## 4. Best Practices
1.  **Component Registration**: Use `.withComponent(YourComponent)` when registering plugins that render elements (Headings, Blockquotes).
2.  **Storage**: Use `onChange` to capture `value` (JSON) and store it. Avoid `dangerouslySetInnerHTML` unless rendering read-only HTML (use Plate's `serializeHtml` if needed).
3.  **Shadcn UI**: Always install base components via `shadcn` CLI to ensure they match the project's design system (Tailwind/Radix).

