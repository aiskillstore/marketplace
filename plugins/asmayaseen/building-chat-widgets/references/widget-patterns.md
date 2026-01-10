# Widget Patterns Reference

Complete patterns for ChatKit widget implementation.

## Widget Template Format

```json
{
  "version": "1.0",
  "name": "task_list",
  "template": "{\"type\":\"ListView\",\"children\":[...jinja template...]}",
  "jsonSchema": {
    "type": "object",
    "properties": {
      "tasks": { "type": "array", "items": {...} }
    }
  }
}
```

## Loading Templates in Python

```python
from chatkit.widgets import WidgetTemplate, WidgetRoot

# Load template from file
task_list_template = WidgetTemplate.from_file("task_list.widget")

def build_task_list_widget(tasks: list[Task]) -> WidgetRoot:
    return task_list_template.build(
        data={
            "tasks": [task.model_dump() for task in tasks],
            "selected": None,
        }
    )
```

## Client-to-Server Action Forwarding

When client handles action locally then notifies server:

```typescript
widgets: {
  onAction: async (action, widgetItem) => {
    if (action.type === "select_name") {
      // Forward to server for processing
      await chatkit.sendCustomAction(action, widgetItem.id);

      // Refresh local state after server processes
      const data = await refreshStatus();
      if (data) handleStatusUpdate(data);
    }
  },
}
```

## Thread Item Actions (Feedback/Retry/Share)

```typescript
const chatkit = useChatKit({
  api: { url: API_URL, domainKey: DOMAIN_KEY },

  threadItemActions: {
    feedback: true,   // Thumbs up/down
    retry: true,      // Regenerate response
    share: true,      // Share message
  },

  onLog: ({ name, data }) => {
    if (name === "message.feedback") {
      trackFeedback(data);
    }
  },
});
```

## Widget Streaming from Tools

When agent tool generates a widget:

```python
from chatkit.types import WidgetItem, ThreadItemDoneEvent
from agents import function_tool

@function_tool
async def show_article_list(ctx: AgentContext, query: str) -> str:
    """Show a list of articles matching the query."""

    articles = await article_store.search(query)

    # Build widget
    widget = build_article_list_widget(articles)

    # Create widget item
    widget_item = WidgetItem(
        id=ctx.store.generate_item_id("widget", ctx.thread, ctx.request_context),
        thread_id=ctx.thread.id,
        created_at=datetime.now(),
        widget=widget,
    )

    # Save to store
    await ctx.store.add_thread_item(ctx.thread.id, widget_item, ctx.request_context)

    # Yield as event
    yield ThreadItemDoneEvent(item=widget_item)

    return f"Showing {len(articles)} articles"
```

## Local Tool Wrappers for Widget Streaming

**Problem**: MCP tools alone don't stream widgets - need local wrappers.

```python
from agents import function_tool

@function_tool
async def show_task_form(
    ctx: RunContextWrapper[AgentContext],
) -> str:
    """Show interactive task creation form widget."""

    agent_ctx = ctx.context
    mcp_url = agent_ctx.mcp_server_url

    # Call MCP tool via HTTP
    result = await _call_mcp_tool(
        mcp_url,
        "show_task_form",
        arguments={"params": {"user_id": agent_ctx.user_id}},
        access_token=agent_ctx.access_token,
    )

    # Return result - RunHooks will stream widget
    return json.dumps(result)

# In RunHooks.on_tool_end()
async def on_tool_end(self, output: str | None, tool_name: str) -> None:
    if tool_name == "show_task_form":
        result = json.loads(output)
        if result.get("action") == "show_form":
            widget = build_task_form_widget()
            yield WidgetItem(...)
```

## Entity Conversion in Backend

Convert @mentions to model-readable markers:

```python
class EntityAwareConverter(BasicThreadItemConverter):
    async def to_agent_input(self, items: list[ThreadItem]) -> list:
        result = []
        for item in items:
            if isinstance(item, UserMessageItem):
                content = item.content
                for entity in item.entities or []:
                    if entity.type == "article":
                        content = content.replace(
                            f"@{entity.title}",
                            f"<ARTICLE id='{entity.id}'>{entity.title}</ARTICLE>"
                        )
                result.append({"role": "user", "content": content})
        return result
```

## Common Validation Errors

### Error 1: 'Action' object has no attribute 'arguments'

```
AttributeError: 'Action[str, Any]' object has no attribute 'arguments'
```

**Fix**: Use `action.payload` instead of `action.arguments`

### Error 2: UserMessageTextContent type mismatch

```
ValidationError: Input should be 'input_text' [type=literal_error, input_value='text']
```

**Fix**: Use `type="input_text"` for user input, not `type="text"`

### Error 3: UserMessageItem missing required fields

```
4 validation errors for UserMessageItem
- id: Field required
- thread_id: Field required
- created_at: Field required
- inference_options: Field required
```

**Fix**: Include all required fields when creating UserMessageItem

### Error 4: RequestContext wrapping issue

```
2 validation errors for RequestContext
metadata: Input should be a valid dictionary [input_value=RequestContext(...)]
```

**Fix**: Don't wrap `context` - it's already a RequestContext object

## Widget Action Testing Checklist

- [ ] Widget renders with correct data
- [ ] All buttons have clear labels
- [ ] Client actions navigate/update UI correctly
- [ ] Server actions call backend successfully
- [ ] Action payload contains all required data
- [ ] Widget updates after server action completes
- [ ] No AttributeError on action.payload access
- [ ] No ValidationError on UserMessageItem creation
- [ ] Local tool wrappers trigger widget streaming

## Evidence Sources

Patterns derived from:
- `cat-lounge/backend/app/widgets/cat_name_suggestions.widget`
- `cat-lounge/frontend/src/components/ChatKitPanel.tsx`
- `metro-map/backend/app/server.py`
- `metro-map/frontend/src/components/ChatKitPanel.tsx`
- `news-guide/frontend/src/components/ChatKitPanel.tsx`
- `news-guide/backend/app/agents/news_agent.py`