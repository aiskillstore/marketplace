# DateTime and Timezone Patterns

Handle datetime values correctly across the full stack: browser → API → database → browser.

## The Golden Rule

**Store UTC, Display Local**

```
Browser (local) → Convert to UTC → API → Store UTC → Database
Database → Return UTC → API → Browser → Display in local
```

## Critical Pitfall: datetime-local Input

The HTML `<input type="datetime-local">` returns a string **WITHOUT timezone info**:

```html
<input type="datetime-local" value="2025-12-15T23:13">
```

This gives `"2025-12-15T23:13"` - but is this UTC? Local time? **The browser doesn't tell you.**

### The Bug

```typescript
// WRONG - Backend interprets as UTC, but user entered local time!
const dueDate = "2025-12-15T23:13"  // User in PKT (UTC+5)
await api.createTask({ due_date: dueDate })
// Backend stores as 23:13 UTC
// But user meant 23:13 PKT = 18:13 UTC
// Task is now 5 hours late!
```

### The Fix

```typescript
// CORRECT - Convert local datetime to UTC ISO string
function handleSubmit() {
  let dueDateUTC: string | undefined = undefined

  if (dueDate) {
    // datetime-local gives "2025-12-15T23:13" (local time, no TZ)
    // new Date() interprets it in browser's local timezone
    // toISOString() converts to UTC: "2025-12-15T18:13:00.000Z"
    const localDate = new Date(dueDate)
    dueDateUTC = localDate.toISOString()
  }

  await api.createTask({ due_date: dueDateUTC })
}
```

## Frontend Patterns (TypeScript/React)

### Converting datetime-local to UTC

```typescript
// Input: "2025-12-15T23:13" (from datetime-local)
// Output: "2025-12-15T18:13:00.000Z" (UTC ISO string)

function localToUTC(localDatetime: string): string {
  const date = new Date(localDatetime)
  return date.toISOString()
}
```

### Converting UTC to datetime-local (for editing)

```typescript
// Input: "2025-12-15T18:13:00Z" (UTC from API)
// Output: "2025-12-15T23:13" (local, for datetime-local input)

function utcToLocal(utcDatetime: string): string {
  const date = new Date(utcDatetime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}
```

### Full Form Example

```tsx
"use client"
import { useState } from "react"

export function TaskForm() {
  const [dueDate, setDueDate] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Convert local to UTC for API
    let dueDateUTC: string | undefined
    if (dueDate) {
      dueDateUTC = new Date(dueDate).toISOString()
    }

    await api.createTask({
      title: "My Task",
      due_date: dueDateUTC,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="datetime-local"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
      />
      <button type="submit">Create</button>
    </form>
  )
}
```

## Backend Patterns (Python/FastAPI)

### Pydantic Validator

```python
from datetime import UTC, datetime
from pydantic import field_validator
from sqlmodel import SQLModel

class TaskCreate(SQLModel):
    title: str
    due_date: datetime | None = None

    @field_validator("due_date", mode="after")
    @classmethod
    def normalize_datetime(cls, v: datetime | None) -> datetime | None:
        """Convert timezone-aware to naive UTC for storage."""
        if v is None:
            return None
        if v.tzinfo is not None:
            v = v.astimezone(UTC).replace(tzinfo=None)
        return v
```

## Database Storage

**Always store as naive UTC**:

```sql
-- PostgreSQL
due_date TIMESTAMP  -- NOT TIMESTAMP WITH TIME ZONE
```

```python
# SQLModel
class Task(SQLModel, table=True):
    due_date: datetime | None = Field(default=None)
```

## Displaying Times

```typescript
import { formatDistanceToNow, format } from 'date-fns'

// Relative: "in 2 hours", "3 days ago"
formatDistanceToNow(new Date(utcDatetime), { addSuffix: true })

// Absolute local: "Dec 15, 2025 11:13 PM"
format(new Date(utcDatetime), 'MMM d, yyyy h:mm a')
```

## Common Pitfalls

| Pitfall | Wrong | Right |
|---------|-------|-------|
| Sending datetime-local directly | `api.post({ due_date: "2025-12-15T23:13" })` | `api.post({ due_date: new Date("2025-12-15T23:13").toISOString() })` |
| Displaying UTC to user | `<span>{task.due_date}</span>` | `<span>{new Date(task.due_date).toLocaleString()}</span>` |
| Comparing dates | `task.due_date < datetime.now(UTC)` | `task.due_date < datetime.utcnow()` |

## Summary

| Location | Format | Example |
|----------|--------|---------|
| `datetime-local` input | Local, no TZ | `2025-12-15T23:13` |
| API request/response | UTC ISO 8601 | `2025-12-15T18:13:00.000Z` |
| Database | Naive UTC | `2025-12-15 18:13:00` |
| Display to user | Local formatted | `Dec 15, 2025 11:13 PM` |