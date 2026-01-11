# Mermaid Common Reference

This document covers syntax and features shared across all Mermaid diagram types.

---

## 1. Code Block Format

In Obsidian, use fenced code blocks:

````markdown
```mermaid
<diagram-type>
    <content>
```
````

---

## 2. Comments

Use `%%` for single-line comments (works in all diagram types):

```mermaid
flowchart TD
    %% This comment won't appear in the diagram
    A --> B
    %% Another comment
    B --> C
```

---

## 3. Direction (Flowchart/Subgraph)

| Direction | Description |
|-----------|-------------|
| `TB` / `TD` | Top to Bottom (default) |
| `BT` | Bottom to Top |
| `LR` | Left to Right |
| `RL` | Right to Left |

```mermaid
flowchart LR
    A --> B --> C
```

Subgraphs can have independent directions:

```mermaid
flowchart LR
    subgraph sub1 [Vertical Group]
        direction TB
        A --> B
    end
    subgraph sub2 [Horizontal Group]
        direction LR
        C --> D
    end
    sub1 --> sub2
```

---

## 4. Styling Nodes

### Inline Style

```mermaid
flowchart LR
    A --> B
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#f66,stroke-width:2px,color:#fff
```

### Style Properties

| Property | Description | Example |
|----------|-------------|---------|
| `fill` | Background color | `fill:#f9f` |
| `stroke` | Border color | `stroke:#333` |
| `stroke-width` | Border thickness | `stroke-width:2px` |
| `color` | Text color | `color:#fff` |
| `stroke-dasharray` | Dashed border | `stroke-dasharray: 5 5` |

### Class Definition

Define reusable styles with `classDef`:

```mermaid
flowchart LR
    A:::success --> B:::warning --> C:::error

    classDef success fill:#4CAF50,stroke:#2E7D32,color:white
    classDef warning fill:#FFC107,stroke:#FF8F00,color:black
    classDef error fill:#F44336,stroke:#C62828,color:white
```

### Apply Class to Multiple Nodes

```mermaid
flowchart TD
    A --> B --> C --> D
    class A,C highlight
    classDef highlight fill:#ff0,stroke:#f00,stroke-width:2px
```

### Default Style

Override the default style for all nodes:

```mermaid
flowchart LR
    A --> B --> C
    classDef default fill:#e1f5fe,stroke:#01579b
```

---

## 5. Styling Links (Edges)

### By Index

Links are numbered starting from 0 in order of appearance:

```mermaid
flowchart LR
    A --> B --> C --> D
    linkStyle 0 stroke:red,stroke-width:2px
    linkStyle 1 stroke:green,stroke-width:2px
    linkStyle 2 stroke:blue,stroke-width:2px
```

### Default Link Style

```mermaid
flowchart LR
    A --> B --> C
    linkStyle default stroke:#999,stroke-width:1px
```

### Multiple Links at Once

```mermaid
flowchart LR
    A --> B --> C --> D --> E
    linkStyle 0,2,4 stroke:red,stroke-width:3px
```

---

## 6. Directives and Configuration

### Inline Directives

Use `%%{init: {...}}%%` at the start of a diagram:

```mermaid
%%{init: {'theme': 'forest'}}%%
flowchart LR
    A --> B --> C
```

### Common Configuration Options

```mermaid
%%{init: {
    'theme': 'base',
    'themeVariables': {
        'primaryColor': '#ff6b6b',
        'primaryTextColor': '#fff',
        'primaryBorderColor': '#ee5a5a',
        'lineColor': '#333',
        'secondaryColor': '#4ecdc4',
        'tertiaryColor': '#ffe66d'
    }
}}%%
flowchart LR
    A[Primary] --> B[Secondary] --> C[Tertiary]
```

---

## 7. Themes

### Available Themes

| Theme | Description |
|-------|-------------|
| `default` | Standard blue-ish theme |
| `neutral` | Grayscale, good for printing |
| `dark` | Dark background |
| `forest` | Green-toned |
| `base` | Minimal, best for custom theming |

### Theme Examples

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    A --> B --> C
```

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A --> B --> C
```

### Custom Theme Variables

```mermaid
%%{init: {
    'theme': 'base',
    'themeVariables': {
        'primaryColor': '#BB2528',
        'primaryTextColor': '#fff',
        'primaryBorderColor': '#7C0000',
        'lineColor': '#F8B229',
        'secondaryColor': '#006100'
    }
}}%%
flowchart TD
    A[Christmas] --> B[Theme]
    B --> C[Example]
```

---

## 8. Accessibility

Add title and description for screen readers:

```mermaid
flowchart TD
    accTitle: User Login Flow
    accDescr: Diagram showing the authentication process from login to dashboard

    A[Login Page] --> B{Valid?}
    B -->|Yes| C[Dashboard]
    B -->|No| D[Error]
```

---

## 9. Special Characters

### Escaping

Wrap text in quotes for special characters:

```mermaid
flowchart LR
    A["Text with (parentheses)"]
    B["Arrow -> symbol"]
    A --> B
```

### HTML Entities

```mermaid
flowchart LR
    A["Quoted: #quot;text#quot;"]
    B["Heart: #9829;"]
    A --> B
```

### Unicode

```mermaid
flowchart LR
    A["Check: ✓"] --> B["Cross: ✗"]
```

---

## 10. Multiline Text

Use `<br/>` or actual line breaks within quotes:

```mermaid
flowchart TD
    A["Line 1<br/>Line 2<br/>Line 3"]
```

---

## 11. Troubleshooting

### Diagram Not Rendering

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blank output | Syntax error | Check for missing arrows, unclosed brackets |
| Partial render | Invalid node ID | Avoid starting IDs with numbers; use letters |
| Theme ignored | Obsidian override | Use explicit `style` commands |

### Common Syntax Errors

```
%% WRONG: Space in node ID
flow chart TD  %% Should be: flowchart TD

%% WRONG: Missing arrow type
A - B          %% Should be: A --> B or A --- B

%% WRONG: Unquoted special characters
A[Text -> here] %% Should be: A["Text -> here"]
```

### Performance Issues

- **50+ nodes**: Split into multiple diagrams
- **Complex styling**: Use `classDef` instead of individual `style`
- **Large Gantt**: Limit visible date range

### Obsidian-Specific Issues

| Issue | Solution |
|-------|----------|
| Colors differ between themes | Use explicit hex colors in `style` |
| Click events don't work | Obsidian disables JS for security |
| New Mermaid features missing | Wait for Obsidian update or use stable syntax |
| PDF export issues | Diagram is rasterized; use high-res capture |

---

## 12. Quick Reference

### Flowchart Shapes

| Shape | Syntax |
|-------|--------|
| Rectangle | `[text]` |
| Rounded | `(text)` |
| Stadium | `([text])` |
| Diamond | `{text}` |
| Hexagon | `{{text}}` |
| Circle | `((text))` |
| Cylinder | `[(text)]` |

### Arrow Types

| Arrow | Syntax | Description |
|-------|--------|-------------|
| Solid | `-->` | Standard arrow |
| Dotted | `-.->` | Dependency/optional |
| Thick | `==>` | Emphasized |
| No arrow | `---` | Association |
| Circle end | `--o` | Aggregation |
| X end | `--x` | Failure/block |
| Bidirectional | `<-->` | Two-way |

### Sequence Arrows

| Arrow | Syntax | Use |
|-------|--------|-----|
| Sync call | `->>` | Request |
| Response | `-->>` | Reply |
| Async | `-)` | Fire and forget |
| Async response | `--)` | Async reply |
| Failed | `-x` | Error/termination |

---

## 13. Diagram Type Keywords

| Diagram | Keyword |
|---------|---------|
| Flowchart | `flowchart` or `graph` |
| Sequence | `sequenceDiagram` |
| Class | `classDiagram` |
| State | `stateDiagram-v2` |
| Gantt | `gantt` |
| Gitgraph | `gitGraph` |
| Mindmap | `mindmap` |
| Pie | `pie` |
| ER Diagram | `erDiagram` |
| Journey | `journey` |

---

## External Resources

- [Mermaid Official Docs](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
