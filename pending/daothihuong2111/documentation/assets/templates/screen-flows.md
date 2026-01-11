# Screen Flows Template

Use this for `docs/screens/{screen-name}/flows.md`

**Max Lines**: 300
**Purpose**: User interaction flows and state transitions
**When to Use**: Screen has complex multi-step workflows

---

```markdown
# {Screen Name} - User Flows

## Flow 1: Primary Flow Name

### Description

What this flow accomplishes.

### Steps

\```
1. User Action
   → System Response
   → State Change

2. Next Action
   → System Response
   → State Change

3. Final Action
   → System Response
   → Result
\```

### Visual Flow

\```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Action    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Result    │
└─────────────┘
\```

### Mermaid Diagram (optional)

\```mermaid
graph TD
  A[Start] --> B[Action]
  B --> C{Condition}
  C -->|Yes| D[Result 1]
  C -->|No| E[Result 2]
\```

### Error Cases

**Error 1**: Description
\```
User Action → Error → Recovery
\```

**Error 2**: Description
\```
User Action → Error → Recovery
\```

---

## Flow 2: Secondary Flow Name

[Repeat structure above]

---

## State Transitions

\```
State A
  ├─ Event 1 → State B
  ├─ Event 2 → State C
  └─ Event 3 → State A (no change)

State B
  ├─ Event 4 → State C
  └─ Event 5 → State A
\```

## Sequence Diagrams

For complex interactions:

\```
User          Component       Service       API
  │               │              │           │
  ├─ Action ─────>│              │           │
  │               ├─ Process ───>│           │
  │               │              ├─ Call ───>│
  │               │              │<── Response
  │               │<── Result ───┤           │
  │<── Update ────┤              │           │
\```
```

---

## Flow Types

**Happy Path**: Normal successful flow
**Error Path**: Error handling and recovery
**State Transition**: State changes over time
**Sequence**: Multi-party interactions

## Diagram Options

- **ASCII**: Simple, fast, always renders
- **Mermaid**: Complex, interactive, requires support

## Example

See: `docs/screens/home/flows.md`
