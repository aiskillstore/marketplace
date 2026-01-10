# ChatKit Integration Patterns

Complete patterns for ChatKit integration with evidence references.

## Backend Principles

1. **Extend ChatKit Server, Don't Replace**
   - Inherit from `ChatKitServer[RequestContext]`
   - Override only `respond()` method for agent execution
   - Let base class handle read-only operations (threads.list, items.list)
   - **Rationale**: ChatKit handles protocol, you handle agent logic

2. **Context Injection in Prompt**
   - Include conversation history as string in system prompt
   - Include user context (name, profile) in system prompt
   - Include page context (current page) in system prompt
   - **Rationale**: Agent SDK receives single prompt, history must be in prompt

3. **User Isolation via RequestContext**
   - All operations scoped by `user_id` in `RequestContext`
   - Store operations filter by `user_id` automatically
   - Never expose data across users
   - **Rationale**: Multi-tenant safety, data privacy

4. **Connection Pool Warmup**
   - Pre-warm database connections on startup
   - Avoids 7+ second first-request delay
   - Test connections before use (`pool_pre_ping=True`)

## Frontend Principles

1. **Custom Fetch Interceptor**
   - Provide custom `fetch` function to `useChatKit` config
   - Add authentication headers (`X-User-ID`)
   - Add metadata (userInfo, pageContext) to request body

2. **Build-Time Configuration**
   - Read env vars in build config (docusaurus.config.ts)
   - Add to `customFields` for client-side access
   - Don't use `process.env` in browser code

3. **Authentication Gate**
   - Require login before allowing chat access
   - Show login prompt if not authenticated
   - Redirect to OAuth flow

## Text Selection "Ask" Feature

Allow users to ask questions about selected content:

```typescript
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      setSelectedText('');
      return;
    }

    const selectedText = selection.toString().trim();
    if (selectedText.length > 0) {
      setSelectedText(selectedText);

      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      setSelectionPosition({
        x: rect.left + rect.width / 2,
        y: rect.top - 10,
      });
    }
  };

  document.addEventListener('selectionchange', handleSelection);
  document.addEventListener('mouseup', handleSelection);

  return () => {
    document.removeEventListener('selectionchange', handleSelection);
    document.removeEventListener('mouseup', handleSelection);
  };
}, []);

const handleAskSelectedText = useCallback(async () => {
  const pageContext = getPageContext();
  const messageText = `Can you explain this from "${pageContext.title}":\n\n"${selectedText}"`;

  if (!isOpen) {
    setIsOpen(true);
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  await sendUserMessage({
    text: messageText,
    newThread: false,
  });

  window.getSelection()?.removeAllRanges();
  setSelectedText('');
}, [selectedText, isOpen, sendUserMessage, getPageContext]);
```

**Evidence**: `robolearn-interface/src/components/ChatKitWidget/index.tsx:153-187`

## Separate ChatKit Store Configuration

When ChatKit needs its own database schema/connection:

```python
# config.py - Ignore ChatKit env vars in main Settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    @property
    def chat_enabled(self) -> bool:
        return os.getenv("TASKFLOW_CHATKIT_DATABASE_URL") is not None

# chatkit_store/config.py - Separate config
class StoreConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TASKFLOW_CHATKIT_")
    database_url: str
    schema_name: str = "taskflow_chat"
```

## Tier Boundaries

### This Skill Covers (Tier 1: Foundation)

- ChatKitServer setup with `respond()` method
- `useChatKit` basic configuration
- Custom fetch interceptor for authentication
- Context injection (user info, page context)
- Script loading detection
- httpOnly cookie proxy (Next.js)
- Database persistence setup
- MCP tool authentication via prompt

### Use streaming-llm-responses For (Tier 2: Real-time)

- `onResponseStart` / `onResponseEnd` handlers
- `onEffect` for fire-and-forget client updates
- `ProgressUpdateEvent` for loading states
- Thread lifecycle events
- Thread title generation

### Use building-chat-widgets For (Tier 3: Interactive)

- Widget templates (.widget files)
- `widgets.onAction` handler
- `action()` method in ChatKitServer
- `sendCustomAction()` for widget updates
- Entity tagging (@mentions)
- Composer tools (mode selection)

## Evidence Sources

Patterns derived from:
- `rag-agent/chatkit_server.py`
- `robolearn-interface/src/components/ChatKitWidget/`
- `web-dashboard/src/app/api/chatkit/route.ts`
- `web-dashboard/src/components/chat/ChatKitWidget.tsx`