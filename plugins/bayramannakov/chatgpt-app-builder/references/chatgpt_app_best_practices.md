# ChatGPT App Best Practices

Guidelines for building high-quality ChatGPT Apps.

## Tool Naming

### Convention
Use `service_verb_noun` pattern in snake_case:
```
taskflow_get_tasks       ✓
taskflow_create_task     ✓
taskflow_complete_task   ✓
getTasks                 ✗ (no prefix, wrong case)
task-list               ✗ (not action-oriented)
```

### Prefix Requirement
Always prefix with service name to prevent conflicts when multiple connectors are active:
```
taskflow_get_tasks
taskflow_create_task
slack_send_message
slack_list_channels
```

### Action Verbs
Use clear, action-oriented verbs:
| Verb | Use For |
|------|---------|
| get | Retrieve single item |
| list | Retrieve collection |
| search | Query with filters |
| create | Make new item |
| update | Modify existing |
| delete | Remove item |
| complete | Mark as done |
| send | Transmit message |

---

## Tool Descriptions

Descriptions are the primary trigger mechanism. Write them carefully.

### Format
Start with "Use this when..." to guide model selection:
```
✓ "Use this when the user wants to see their current tasks,
   optionally filtered by status or due date."

✗ "Gets tasks from the API"  (too vague)
✗ "TaskFlow task retrieval endpoint"  (too technical)
```

### Include
- When to use this tool
- What parameters are available
- What the user will get back

### Avoid
- Marketing language ("Best task manager ever!")
- Recommending overly broad triggering
- Technical implementation details
- Comparisons to competitors

---

## Tool Annotations

Mark tools correctly to inform the model about behavior:

### readOnlyHint: true
For tools that only retrieve data without side effects:
```typescript
// Examples: get_*, list_*, search_*, view_*
_meta: { "openai/readOnlyHint": true }
```

### destructiveHint: true
For tools that delete or irreversibly modify data:
```typescript
// Examples: delete_*, remove_*, archive_*
_meta: { "openai/destructiveHint": true }
```

### openWorldHint: true
For tools that interact with external systems or publish content:
```typescript
// Examples: send_*, publish_*, create_* (when creates external records)
_meta: { "openai/openWorldHint": true }
```

### Combinations
Tools can have multiple hints:
```typescript
// delete_task: removes data (destructive) and affects external system (openWorld)
_meta: {
  "openai/destructiveHint": true,
  "openai/openWorldHint": true
}
```

**Common rejection reason**: Incorrect or missing annotations.

---

## Response Structure

ChatGPT Apps use three response layers:

### content (Model-visible narration)
Text the model sees and can reference in conversation:
```typescript
content: [{
  type: "text",
  text: "Found 5 tasks, 2 are overdue"
}]
```
Keep concise. Model uses this to understand what happened.

### structuredContent (Model-readable data)
Machine-readable data the model can process and reference:
```typescript
structuredContent: {
  tasks: [
    { id: "t1", title: "Review PR", status: "active", due: "2024-01-15" },
    { id: "t2", title: "Deploy", status: "completed" }
  ],
  total: 5,
  overdue: 2
}
```
Include IDs, timestamps, and status fields. Model may use these in follow-up tool calls.

### _meta (Widget-only data)
Rich data only the widget sees, hidden from model:
```typescript
_meta: {
  fullTaskObjects: [...],  // Complete data with all fields
  userPreferences: {...},  // UI preferences
  pagination: { hasMore: true, nextCursor: "abc" }
}
```
Use for large datasets, sensitive data, or widget-specific info.

### Separation Principle
- `structuredContent`: Minimal, what model needs
- `_meta`: Everything widget needs beyond that

---

## Widget State Management

### Persist State Correctly
Use `setWidgetState` for data that should survive widget re-renders:
```typescript
// Good: User selections, filters, UI state
window.openai.setWidgetState({
  selectedTaskId: "t1",
  viewMode: "list",
  sortOrder: "due_date"
});
```

### State Size Limits
Keep state under ~4k tokens. Model receives widget state, so large states waste context.

### State Scope
- State persists within widget instance
- State clears when user types in main composer (starts fresh flow)
- State persists when user interacts via widget controls

---

## Error Handling

Return actionable error messages:

### Good Error Messages
```typescript
// Specific, actionable
"Task not found. The task may have been deleted. Try listing your tasks first."
"Rate limit exceeded. Please wait 60 seconds before trying again."
"Permission denied. You don't have access to this project."
```

### Bad Error Messages
```typescript
// Vague, unhelpful
"Error occurred"
"Request failed"
"500 Internal Server Error"
```

### Error Structure
```typescript
return {
  content: [{
    type: "text",
    text: "Could not complete the action: [specific reason]"
  }],
  structuredContent: {
    error: true,
    errorType: "not_found",
    message: "Task with ID 't999' not found"
  }
};
```

---

## CSP Configuration

Configure Content Security Policy for widget resources:

```typescript
_meta: {
  "openai/widgetCSP": {
    // Domains for fetch/XHR requests
    connect_domains: ["https://api.yourservice.com"],

    // Domains for images, fonts, scripts
    resource_domains: ["https://cdn.yourservice.com"],

    // Domains for openExternal() navigation
    redirect_domains: ["https://checkout.yourservice.com"],

    // Domains for embedded iframes (triggers stricter review)
    frame_domains: ["https://embed.yourservice.com"]
  }
}
```

### Principles
- Only whitelist domains you actually need
- `frame_domains` triggers additional review scrutiny
- Use specific domains, not wildcards when possible

---

## Input Validation

Use Zod with `.strict()` for runtime validation:

```typescript
const GetTasksSchema = z.object({
  status: z.enum(["active", "completed", "all"]).default("all")
    .describe("Filter tasks by status"),
  limit: z.number().int().min(1).max(100).default(20)
    .describe("Maximum number of tasks to return"),
  cursor: z.string().optional()
    .describe("Pagination cursor from previous response")
}).strict();
```

### Requirements
- Use `.describe()` for every parameter
- Add meaningful validation constraints
- Apply `.strict()` to reject unexpected fields
- Set sensible defaults for optional parameters

---

## Design Principles Summary

1. **One job per tool** - Don't combine read + write in one tool
2. **Clear naming** - `service_verb_noun` pattern
3. **Accurate annotations** - Mark read-only, destructive, open-world correctly
4. **Layer separation** - structuredContent for model, _meta for widget
5. **Actionable errors** - Tell users what went wrong and how to fix it
6. **Minimal input** - Only request what's needed for the task
7. **Consistent output** - Same structure across similar tools

---

## Advanced Patterns

### Idempotency Keys

ChatGPT may retry tool calls. Prevent duplicate operations by accepting an idempotency key:

```typescript
const CreateItemSchema = z.object({
  title: z.string(),
  description: z.string().optional(),
  idempotencyKey: z.string().optional()
    .describe("Client-generated UUID to prevent duplicate creation on retries"),
}).strict();

async function handleCreateItem(args: CreateItemInput) {
  // Check for existing operation with same key
  if (args.idempotencyKey) {
    const existing = await findByIdempotencyKey(args.idempotencyKey);
    if (existing) {
      // Return existing result - idempotent!
      return {
        content: [{ type: "text", text: `Item already created: ${existing.title}` }],
        structuredContent: existing,
      };
    }
  }

  // Create new item
  const item = await createItem({
    ...args,
    idempotencyKey: args.idempotencyKey,
  });

  return {
    content: [{ type: "text", text: `Created item: ${item.title}` }],
    structuredContent: item,
  };
}
```

**When to use**: Any mutation tool (create, update, delete, send).

---

### Disambiguation Pattern

When user input could match multiple items, return options for selection:

```typescript
async function handleUpdateItem(args: { name: string; status: string }) {
  // Search for matching items
  const matches = await findItemsByName(args.name);

  // No matches
  if (matches.length === 0) {
    return {
      content: [{ type: "text", text: `No items found matching "${args.name}"` }],
      structuredContent: { error: true, type: "not_found" },
    };
  }

  // Single match - proceed with update
  if (matches.length === 1) {
    const updated = await updateItem(matches[0].id, { status: args.status });
    return {
      content: [{ type: "text", text: `Updated "${updated.title}" to ${args.status}` }],
      structuredContent: updated,
    };
  }

  // Multiple matches - ask for clarification
  return {
    content: [{
      type: "text",
      text: `Found ${matches.length} items matching "${args.name}". Which one did you mean?`
    }],
    structuredContent: {
      disambiguation: true,
      matches: matches.map(item => ({
        id: item.id,
        title: item.title,
        description: item.description,  // Include distinguishing details
        createdAt: item.createdAt,
      })),
      originalQuery: args.name,
    },
  };
}
```

**Key principles**:
- Include unique identifiers in disambiguation list
- Add distinguishing details (dates, descriptions, IDs)
- Store original query for context
- Widget can show selection UI for user to pick

---

### Confirmation Receipts

After mutations, echo back exactly what changed to build user trust:

```typescript
async function handleMoveItem(args: { id: string; toStatus: string }) {
  const item = await getItem(args.id);
  const fromStatus = item.status;

  await updateItem(args.id, { status: args.toStatus });

  // Confirmation receipt with before/after
  const receipt = `Moved "${item.title}" from ${fromStatus} to ${args.toStatus}`;

  return {
    content: [{ type: "text", text: receipt }],
    structuredContent: {
      receipt: true,
      action: "move",
      item: {
        id: item.id,
        title: item.title,
      },
      changes: {
        status: {
          from: fromStatus,
          to: args.toStatus,
        },
      },
    },
  };
}
```

**Receipt patterns**:
- `"Created [item] with [key details]"`
- `"Moved [item] from [X] to [Y]"`
- `"Updated [item]: [field] changed from [old] to [new]"`
- `"Deleted [item] (was [status])"`

**Why receipts matter**:
- Users trust the system more when they see confirmation
- Helps catch mistakes ("Wait, I didn't want to delete that!")
- Enables undo patterns ("Undo the last change")

---

### Undo Pattern

Support undoing recent changes by tracking operations:

```typescript
// Store recent operations in activity log
interface Activity {
  id: string;
  action: "create" | "update" | "delete";
  itemId: string;
  previousState: Record<string, unknown>;
  newState: Record<string, unknown>;
  timestamp: Date;
  isUndone: boolean;
}

async function handleUndo(args: { itemName?: string }) {
  // Find recent undoable activity
  const activity = await findRecentActivity({
    itemName: args.itemName,
    isUndone: false,
    limit: 1,
  });

  if (!activity) {
    return {
      content: [{ type: "text", text: "Nothing to undo" }],
      structuredContent: { error: true, type: "nothing_to_undo" },
    };
  }

  // Restore previous state
  await updateItem(activity.itemId, activity.previousState);

  // Mark as undone
  await markActivityUndone(activity.id);

  return {
    content: [{
      type: "text",
      text: `Undone: Restored "${activity.previousState.title}" to previous state`
    }],
    structuredContent: {
      undone: true,
      activity: activity.id,
      restored: activity.previousState,
    },
  };
}
```

**Best practices**:
- Store previous state before every mutation
- Limit undo window (e.g., last 10 operations, last 24 hours)
- Mark activities as undone to prevent double-undo
- Include item name in undo confirmation
