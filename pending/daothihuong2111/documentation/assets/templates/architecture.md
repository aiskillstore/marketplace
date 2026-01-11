# Architecture Document Template

Use this for `docs/architecture/*.md`

**Max Lines**: 500
**Purpose**: Architecture patterns and design decisions

---

```markdown
# {Architecture Topic}

## Overview

High-level description of this architectural component.

## Architecture Diagram

\```
┌──────────────────────────────────────┐
│         Layer 1: Name                │
│  Components, responsibilities        │
└────────────────┬─────────────────────┘
                 │ depends on
┌────────────────▼─────────────────────┐
│         Layer 2: Name                │
│  Components, responsibilities        │
└────────────────┬─────────────────────┘
                 │ depends on
┌────────────────▼─────────────────────┐
│         Layer 3: Name                │
│  Components, responsibilities        │
└──────────────────────────────────────┘
\```

## Components

### Component 1

**Purpose**: What it does

**Responsibilities**:
- Responsibility 1
- Responsibility 2

**Location**: path/to/directory/

**Key Files**:
- `File.ts:line` - Description
- `File.ts:line` - Description

**Example**:

\```typescript
// Code example showing usage
\```

### Component 2

[Repeat structure above]

## Patterns

### Pattern 1: Name

**When to use**: Description

**Implementation**:

\```typescript
// Code example
\```

**Benefits**:
- Benefit 1
- Benefit 2

**Trade-offs**:
- Trade-off 1
- Trade-off 2

### Pattern 2: Name

[Repeat structure above]

## Data Flow

\```
Input
  → Processing Step 1
  → Processing Step 2
  → Output
\```

## Design Decisions

### Decision 1: Title

**Context**: What problem we were solving

**Options Considered**:
1. Option A - Pros/Cons
2. Option B - Pros/Cons
3. Option C - Pros/Cons (chosen)

**Rationale**: Why we chose option C

**Consequences**: What this means for the codebase

### Decision 2: Title

[Repeat structure above]

## Examples

### Example 1: Common Pattern

\```typescript
// Complete code example
\```

### Example 2: Advanced Pattern

\```typescript
// Complete code example
\```

## Testing

How to test this architectural component.

## Migration Guide (if applicable)

How to migrate from old to new architecture.

## Related

- [Related Doc 1](../path/to/doc.md)
- [Related Doc 2](../path/to/doc.md)
```

---

## Sections

**Required:**
- Overview
- Architecture Diagram
- Components
- Patterns (or Data Flow)

**Optional:**
- Design Decisions (recommended)
- Examples
- Testing
- Migration Guide

## Example

See: `docs/architecture/overview.md`
