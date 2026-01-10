# Screen README Template

Use this for `docs/screens/{screen-name}/README.md`

**Max Lines**: 300
**Purpose**: Screen overview and quick start

---

```markdown
# {Screen Name} Screen

Brief one-line description of what this screen does.

## Overview

2-3 sentences explaining the screen's purpose and when users see it.

## Features

### Core Features
1. **Feature Name**: Brief description
2. **Another Feature**: Brief description
3. **Third Feature**: Brief description

### Advanced Features (if applicable)
4. **Advanced Feature**: Brief description

## Usage

### Basic Usage

Describe the most common use case with example:

\```
User action → Result
User action → Result
\```

### Keyboard Shortcuts

| Key      | Action           |
|----------|------------------|
| `Enter`  | Action           |
| `ESC`    | Action           |
| `Ctrl+C` | Action           |

## Components

- **MainComponent**: Brief description (path:line)
- **SubComponent**: Brief description (path:line)
- **HookName**: Brief description (path:line)

## Layout

\```
┌─────────────────────────────────────┐
│  Component Hierarchy                │
├─────────────────────────────────────┤
│  Visual representation              │
└─────────────────────────────────────┘
\```

## State Management

Brief description of how state is managed.

## Performance

Key performance metrics or optimizations.

## Related

- [Related Doc 1](../path/to/doc.md)
- [Related Doc 2](../../path/to/doc.md)
```

---

## Variables

- `{Screen Name}` → Capitalized (e.g., "Home", "Config", "Welcome")
- `{screen-name}` → Lowercase with hyphens (e.g., "home", "config", "welcome")

## Sections

**Required:**
- Title
- Overview
- Features
- Components

**Optional:**
- Keyboard Shortcuts (if applicable)
- Layout (if helpful)
- State Management (brief)
- Performance (brief)
- Related links

## Example

See: `docs/screens/home/README.md`
