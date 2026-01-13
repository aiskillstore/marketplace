# ChatGPT App Troubleshooting Guide

Common issues and solutions when building ChatGPT Apps.

Based on [official troubleshooting guide](https://developers.openai.com/apps-sdk/deploy/troubleshooting).

---

## Critical: Multi-Connection Session Routing

> **⚠️ This is the #1 cause of "tool works but widget shows nothing" bugs.**

ChatGPT opens **multiple SSE connections** for the same tool call (speculative execution, retries, widget resource loading). If POST messages are routed to the wrong session, responses are **silently lost**.

**Symptoms:**
- Widget shows `hasToolOutput: false` despite server logs showing successful response
- SSE connection closes unexpectedly after tool completes
- Intermittent failures (works sometimes, fails other times)
- Server logs show correct response generated but widget times out

**Root Cause:** Iterating through all sessions and handling with whichever "works":

```typescript
// ❌ WRONG - Do NOT do this
for (const [, transport] of transports) {
  try {
    await transport.handlePostMessage(req, res, body);
    return;
  } catch { continue; }
}
```

**Correct Pattern:** Route to the specific session by `sessionId` query parameter:

```typescript
// ✅ CORRECT - Direct session lookup
const sessionId = url.searchParams.get("sessionId");
const session = sessions.get(sessionId);

if (session) {
  await session.transport.handlePostMessage(req, res, body);
} else {
  res.writeHead(404).end("Unknown session");
}
```

**Why This Matters:**
- ChatGPT tracks which SSE connection should receive which response
- Wrong session = response goes to connection ChatGPT isn't monitoring
- The response is generated and sent, but ChatGPT never sees it

---

## Server-Side Issues

### SSE Session Management Issues

**Symptoms**: MCP Inspector shows "Connection Error" or "Invalid session ID" errors. SSE connections establish but immediately close.

**Root Cause**: Custom session management conflicts with SSEServerTransport's internal session handling. The SDK uses URL query params (`?sessionId=xxx`) for sessions, not headers.

**Common Mistakes**:

1. **Using separate endpoints for GET and POST**:
   ```typescript
   // WRONG: Separate paths cause session mismatch with proxies
   const ssePath = "/mcp";
   const postPath = "/mcp/messages";
   ```

2. **Custom header-based session validation**:
   ```typescript
   // WRONG: SSEServerTransport doesn't use headers for sessions
   const sessionId = req.headers["mcp-session-id"];
   const transport = transports.get(sessionId);
   if (!transport) {
     res.writeHead(400).end("Invalid session");
   }
   ```

**Correct Pattern**:

```typescript
// Session storage
const sessions = new Map<string, { server: Server; transport: SSEServerTransport }>();

// GET /mcp - SSE connection
if (url.pathname === "/mcp" && req.method === "GET") {
  const server = createMcpServer();
  const transport = new SSEServerTransport("/mcp", res);

  // Store session AFTER transport is created (sessionId is available immediately)
  sessions.set(transport.sessionId, { server, transport });

  // Clean up on disconnect
  res.on("close", () => sessions.delete(transport.sessionId));

  await server.connect(transport);
}

// POST /mcp - Message handling
if (url.pathname === "/mcp" && req.method === "POST") {
  // Get sessionId from query parameter (ChatGPT sends this)
  const sessionId = url.searchParams.get("sessionId");

  if (!sessionId) {
    res.writeHead(400).end("Missing sessionId");
    return;
  }

  // Direct lookup - DO NOT iterate through all sessions!
  const session = sessions.get(sessionId);

  if (session) {
    await session.transport.handlePostMessage(req, res);
  } else {
    res.writeHead(404).end("Unknown session");
  }
}
```

**Key Points**:
- Route POSTs to the **specific session** matching the `sessionId` query parameter
- **NEVER iterate through sessions** - this causes the multi-connection bug
- Store sessions by their transport's `sessionId` property
- Clean up sessions on SSE disconnect to prevent memory leaks

---

### "No tools listed" in ChatGPT connector

**Symptoms**: When creating a connector, the tools list is empty.

**Solutions**:
1. Verify server is running and accessible
2. Check that your MCP endpoint URL is correct (should be `/mcp`, not `/`)
3. Test with MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector@latest http://localhost:8000/mcp
   ```
4. Check server logs for connection errors
5. Ensure CORS headers are present:
   ```typescript
   res.setHeader("Access-Control-Allow-Origin", "*");
   ```

---

### "Structured content only, no component"

**Symptoms**: Tool returns data but widget doesn't render. ChatGPT shows text fallback instead of widget UI.

**Root Cause**: Missing or incomplete `_meta` in resource definitions. ChatGPT requires specific metadata on BOTH the resource listing AND the resource contents.

**Solutions**:

1. **Add `_meta` to ListResourcesRequestSchema response**:
   ```typescript
   server.setRequestHandler(ListResourcesRequestSchema, async () => ({
     resources: [{
       uri: "ui://widget/app.html",
       name: "My Widget",
       mimeType: "text/html+skybridge",
       _meta: {
         "openai/outputTemplate": "ui://widget/app.html",
         "openai/widgetAccessible": true,
       },
     }],
   }));
   ```

2. **Add full `_meta` to ReadResourceRequestSchema response**:
   ```typescript
   server.setRequestHandler(ReadResourceRequestSchema, async (request) => ({
     contents: [{
       uri: request.params.uri,
       mimeType: "text/html+skybridge",
       text: widgetHtml,
       _meta: {
         "openai/outputTemplate": "ui://widget/app.html",
         "openai/widgetAccessible": true,
         "openai/widgetPrefersBorder": true,
         "openai/widgetCSP": {
           connect_domains: [],  // Add external API domains here
           resource_domains: [],
         },
         "openai/widgetDomain": "your-app.fly.dev",
       },
     }],
   }));
   ```

3. **Ensure tool response also has `_meta`**:
   ```typescript
   return {
     content: [{ type: "text", text: "Summary" }],
     structuredContent: { /* data */ },
     _meta: {
       "openai/outputTemplate": "ui://widget/app.html",
       "openai/widgetAccessible": true,
     },
   };
   ```

**Key Fields**:
- `openai/outputTemplate` - Links response to widget resource
- `openai/widgetAccessible` - Allows widget to call tools
- `openai/widgetCSP` - Security policy for external connections
- `openai/widgetDomain` - Your app's domain (required for submission)

---

### Widget Changes Not Taking Effect

**Symptoms**: After updating resource metadata (CSP, domain, etc.), widget still doesn't render or shows old behavior.

**Root Cause**: ChatGPT caches widget templates when the connector is first created. Changes to resource metadata don't take effect until cache is cleared.

**Solution**: Delete and recreate the connector:
1. Go to ChatGPT Settings → Connected Apps
2. Delete your connector
3. Add it again with the same MCP endpoint URL

This forces ChatGPT to re-fetch and cache the updated widget template.

---

### Schema Mismatch Errors

**Symptoms**: Tool calls fail with validation errors.

**Solutions**:
1. Ensure tool `inputSchema` is valid JSON Schema (not Zod)
2. Verify `required` array only includes required properties
3. Use `additionalProperties: false` to catch unexpected inputs
4. Check parameter types match (e.g., `"type": "number"` not `"type": "integer"`)

---

### Slow Responses

**Symptoms**: Tool calls take several seconds or timeout.

**Solutions**:
1. Profile backend API calls - aim for <500ms response times
2. Add request timeouts to external API calls:
   ```typescript
   const controller = new AbortController();
   const timeout = setTimeout(() => controller.abort(), 10000);
   ```
3. Consider caching frequently-accessed data
4. Return partial results with `hasMore: true` for large datasets

---

## Widget Rendering Issues

### Widget Doesn't Load

**Symptoms**: Widget area is blank or shows error.

**Solutions**:
1. Check browser console for errors:
   - CSP violations (see CSP section below)
   - JavaScript syntax errors
   - Missing dependencies
2. Verify widget HTML is valid:
   ```bash
   npm run build:widget
   ```
3. Ensure all JavaScript is inlined in the HTML (no external script tags)
4. Check that React is bundled correctly (no missing imports)

---

### window.openai API Errors

**Symptoms**: Console shows `TypeError: window.openai.notifyIntrinsicHeight is not a function` or similar errors for other `window.openai` methods.

**Root Cause**: The `window.openai` API may not be fully initialized when the widget first renders, or certain functions may not be available in all contexts (e.g., during development vs. production).

**Solutions**:

1. **Use explicit type checks** (not just truthiness):
   ```typescript
   // WRONG: May pass if property exists but isn't callable
   if (window.openai?.notifyIntrinsicHeight) { ... }

   // CORRECT: Explicitly check it's a function
   if (typeof window.openai?.notifyIntrinsicHeight === "function") {
     window.openai.notifyIntrinsicHeight(height);
   }
   ```

2. **Add try-catch for safety**:
   ```typescript
   try {
     if (typeof window.openai?.notifyIntrinsicHeight === "function") {
       window.openai.notifyIntrinsicHeight(containerRef.current.scrollHeight);
     }
   } catch (err) {
     console.warn("notifyIntrinsicHeight failed:", err);
   }
   ```

3. **Delay initial call slightly** (for React useEffect):
   ```typescript
   useEffect(() => {
     const timer = setTimeout(() => {
       if (typeof window.openai?.notifyIntrinsicHeight === "function") {
         window.openai.notifyIntrinsicHeight(height);
       }
     }, 100);
     return () => clearTimeout(timer);
   }, []);
   ```

**Note**: These errors may appear in the console but don't necessarily break the widget. If the widget renders correctly, you can safely ignore the errors.

---

### CSP Violations

**Symptoms**: Console shows "Refused to connect to..." or similar CSP errors.

**Solutions**:
1. Add required domains to `widgetCSP`:
   ```typescript
   _meta: {
     "openai/widgetCSP": {
       connect_domains: ["https://api.yourservice.com"],
       resource_domains: ["https://cdn.yourservice.com"],
       redirect_domains: ["https://checkout.yourservice.com"],
       frame_domains: ["https://embed.yourservice.com"]
     }
   }
   ```
2. Only include domains you actually need (stricter is better)
3. Note: `frame_domains` triggers additional review scrutiny

---

### State Not Persisting

**Symptoms**: Widget state resets unexpectedly.

**Solutions**:
1. Ensure you're calling `setWidgetState` after updates:
   ```typescript
   window.openai.setWidgetState({ selectedId: "123" });
   ```
2. Rehydrate state on mount from `window.openai.widgetState`
3. Understand scope: state persists within widget instance but resets when user types in main composer
4. Keep state under ~4k tokens for performance

---

### Widget UI Not Updating After Tool Calls

**Symptoms**: User clicks buttons in widget (add, delete, etc.), server logs show tools are called successfully, but the widget UI doesn't update. User must ask ChatGPT to "show items" again to see changes.

**Root Cause**: `window.openai.toolOutput` is set once when ChatGPT renders the widget for a specific message turn. It's immutable for that widget instance. When tools are called from within the widget via `window.openai.callTool()`, the original widget doesn't receive the updated data automatically.

**Why This Happens**:
1. Widget reads from `toolOutput` (or `useToolOutput()` hook)
2. User clicks a button → `window.openai.callTool()` is called
3. Tool executes on server and returns new data
4. But `toolOutput` in the current widget instance remains unchanged
5. ChatGPT may render a NEW widget in the conversation, but the original stays static

**Solution**: Manage local React state and update it from tool call responses:

```typescript
interface ToolResult {
  structuredContent?: {
    items?: Item[];
  };
}

export function App() {
  const output = useToolOutput<{ items: Item[] }>();

  // Local state - initialized from toolOutput
  const [items, setItems] = useState<Item[]>(output?.items || []);

  // Sync when ChatGPT re-renders widget with new toolOutput
  useEffect(() => {
    if (output?.items) {
      setItems(output.items);
    }
  }, [output?.items]);

  const handleDelete = async (id: string) => {
    // Optimistic update - remove immediately from UI
    setItems(prev => prev.filter(item => item.id !== id));

    try {
      const result = await window.openai.callTool("myapp_delete", { id }) as ToolResult;
      // Sync with server response if available
      if (result?.structuredContent?.items) {
        setItems(result.structuredContent.items);
      }
    } catch (error) {
      console.error("Delete failed:", error);
      // On error, could re-fetch to restore accurate state
    }
  };

  const handleAdd = async (text: string) => {
    try {
      const result = await window.openai.callTool("myapp_create", { text }) as ToolResult;
      // Update from server response
      if (result?.structuredContent?.items) {
        setItems(result.structuredContent.items);
      }
    } catch (error) {
      console.error("Create failed:", error);
    }
  };

  // ... render items
}
```

**Key Pattern**:
1. **Local state**: Don't rely solely on `toolOutput`; maintain React state
2. **Optimistic updates**: Update UI immediately for responsive feel
3. **Use return value**: `callTool()` returns a promise with `structuredContent`
4. **Error recovery**: Revert or re-fetch on failure

**Server-Side Requirement**: Tool handlers must return the updated data in `structuredContent`:

```typescript
function handleDeleteItem(args: { id: string }) {
  items.delete(args.id);

  return {
    content: [{ type: "text", text: "Deleted" }],
    structuredContent: {
      items: Array.from(items.values()), // Return updated list!
    },
    _meta: { "openai/outputTemplate": "ui://widget/app.html" },
  };
}
```

---

### Mobile Layout Issues

**Symptoms**: Widget looks broken on mobile.

**Solutions**:
1. Check `window.openai.displayMode` and adapt layout:
   ```typescript
   const mode = window.openai.displayMode; // "inline" | "fullscreen" | etc
   ```
2. Respect `window.openai.maxHeight` for sizing
3. Use `window.openai.safeArea` for mobile safe area insets
4. Test with mobile viewport in browser DevTools
5. Avoid fixed heights - use `notifyIntrinsicHeight` for dynamic sizing

---

## Tool Invocation Issues

### Tool Not Triggering for Expected Prompts

**Symptoms**: ChatGPT doesn't invoke your tool when it should.

**Solutions**:
1. Improve tool description with "Use this when..." phrasing:
   ```typescript
   description: "Use this when the user wants to see their tasks or to-do items."
   ```
2. Test with your golden prompts (direct, indirect, negative)
3. Add more specific keywords to the description
4. Avoid overlapping descriptions between similar tools

---

### Wrong Tool Selected

**Symptoms**: ChatGPT picks the wrong tool from your app.

**Solutions**:
1. Make tool descriptions more distinct
2. Add clarifying details about when NOT to use each tool
3. Consider combining similar tools if they're too overlapping
4. Use specific parameter names that match user intent

---

### Tool Calls Multiple Apps

**Symptoms**: ChatGPT triggers tools from multiple connectors.

**Solutions**:
1. Prefix tool names with your service name: `myapp_get_tasks`
2. Add specific keywords to descriptions that distinguish your app
3. Include your app name in the description where appropriate

---

## OAuth & Authentication Issues

### 401 Errors Not Triggering OAuth Flow

**Symptoms**: User sees error instead of login prompt.

**Solutions**:
1. Include `WWW-Authenticate` header in 401 responses:
   ```typescript
   if (response.status === 401) {
     res.setHeader("WWW-Authenticate", "Bearer");
     res.writeHead(401).end("Unauthorized");
   }
   ```
2. Verify OAuth well-known endpoints are accessible
3. Check that your issuer URL is correct

---

### OAuth Flow Fails

**Symptoms**: Login button doesn't work or errors after login.

**Solutions**:
1. Verify well-known endpoints return valid JSON:
   - `/.well-known/oauth-authorization-server`
   - `/.well-known/openid-configuration`
2. Ensure `registration_endpoint` is exposed for dynamic registration
3. Check that newly created clients have login connections enabled
4. Verify redirect URIs match expected patterns

---

### Token Refresh Failing

**Symptoms**: App works initially but fails after some time.

**Solutions**:
1. Implement proper token refresh flow
2. Check refresh token expiration settings
3. Verify the refresh endpoint returns valid tokens
4. Handle token errors gracefully with re-authentication prompt

---

## Deployment Issues

### Ngrok Timeouts

**Symptoms**: Tunnel disconnects during development.

**Solutions**:
1. Restart ngrok and update connector URL
2. Verify local server is still running
3. Consider using a persistent tunnel service for longer sessions
4. Check ngrok's free tier limits

---

### Streaming Failures Behind Proxies

**Symptoms**: SSE connection drops or doesn't establish.

**Solutions**:
1. Ensure load balancer/CDN permits server-sent events
2. Disable HTTP response buffering:
   ```
   X-Accel-Buffering: no
   ```
3. Check proxy timeout settings (SSE needs long connections)
4. Verify WebSocket/SSE support on your hosting platform

---

### Health Check Failing

**Symptoms**: Deployment shows unhealthy or container restarts.

**Solutions**:
1. Add `/health` endpoint that returns 200:
   ```typescript
   if (url.pathname === "/health") {
     res.writeHead(200).end("OK");
     return;
   }
   ```
2. Ensure health check runs quickly (<5 seconds)
3. Match health check path with deployment config

---

### Multi-Machine Deployment Breaks Sessions (Fly.io, Railway, etc.)

**Symptoms**: SSE connection establishes successfully, but POST requests fail with "No matching transport found" or "No active session". Server logs show `0 transports` when handling POST.

**Root Cause**: Platforms like Fly.io create multiple machines by default for high availability. SSE transport uses **in-memory state** to track sessions:

```
User → SSE GET /mcp → Machine A (stores transport in memory)
User → POST /mcp    → Machine B (has no transports - empty Map!)
```

Each machine has its own in-memory `transports` Map. When POST goes to a different machine than SSE, the session doesn't exist there.

**Solutions**:

1. **Scale to single machine** (simplest for development/testing):
   ```bash
   # Fly.io
   fly scale count 1 --yes

   # Or in fly.toml
   [http_service]
     min_machines_running = 1
     max_machines_running = 1
   ```

2. **Use sticky sessions** (for production with multiple machines):
   ```toml
   # fly.toml - route by source IP
   [http_service]
     [http_service.concurrency]
       type = "connections"
       soft_limit = 25
       hard_limit = 30
   ```

3. **External session storage** (for true horizontal scaling):
   - Use Redis to store session→machine mapping
   - Implement session affinity at load balancer level
   - Consider Streamable HTTP transport instead of SSE

**Key Insight**: SSE transport is inherently stateful. For production deployments with multiple machines, you need either sticky sessions or external session coordination.

---

### sessionId Not Available Before connect()

**Symptoms**: Transport stored with `undefined` key, sessions never match.

**Root Cause**: `SSEServerTransport` generates its `sessionId` during the `connect()` phase, not during construction. Accessing `transport.sessionId` before calling `server.connect(transport)` returns undefined.

**Wrong Pattern**:
```typescript
// WRONG: sessionId is undefined here!
const transport = new SSEServerTransport("/mcp", res);
const sessionId = (transport as any).sessionId;  // undefined!
transports.set(sessionId, transport);
await server.connect(transport);
```

**Correct Pattern**:
```typescript
// CORRECT: Get sessionId AFTER connect()
const transport = new SSEServerTransport("/mcp", res);
const server = createMcpServer();

// Connect first - this generates the sessionId
await server.connect(transport);

// NOW get the sessionId
const sessionId = (transport as any).sessionId || (transport as any)._sessionId;
if (sessionId) {
  transports.set(sessionId, transport);
}
```

**Note**: The sessionId property may be named `sessionId` or `_sessionId` depending on SDK version. Check both for compatibility.

---

## Submission Rejection Issues

### "Incorrect Tool Annotations"

**Symptoms**: Rejection citing annotation problems.

**Solutions**:
1. Verify annotations match actual tool behavior:
   - `readOnlyHint: true` - tool only reads data, no side effects
   - `destructiveHint: true` - tool deletes or irreversibly modifies
   - `openWorldHint: true` - tool affects external systems
2. Double-check write operations have `openWorldHint: true`
3. Don't mark delete operations as `readOnlyHint: true`

---

### "Incomplete App"

**Symptoms**: Rejection for non-functional app.

**Solutions**:
1. Ensure all tools work completely (not demos/trials)
2. Test all edge cases and error scenarios
3. Provide working test credentials if auth required
4. Verify app handles errors gracefully

---

### "Data Collection Concerns"

**Symptoms**: Rejection citing data handling issues.

**Solutions**:
1. Remove any fields collecting:
   - PCI DSS data (credit cards)
   - PHI (health info)
   - Government IDs
   - Credentials
2. Don't request full chat history/transcripts
3. Use coarse location instead of precise GPS
4. Only request data necessary for the task

---

## Response Size Issues

### Large Responses Fail to Deliver

**Symptoms**: Tool completes successfully (server logs show response), but widget shows timeout or empty state. Works for small responses, fails for large ones.

**Root Cause**: Responses over ~300KB may fail to deliver completely over SSE, or hit ChatGPT's internal limits.

**Solutions**:

1. **Remove duplicate data**:
   ```typescript
   // ❌ WRONG - Duplicates data in response
   return {
     structuredContent: { items: items.slice(0, 10) },
     _meta: {
       fullItems: items,           // Duplicates structuredContent!
       experience: person.experience,
       education: person.education,
     },
   };

   // ✅ CORRECT - No duplication
   return {
     structuredContent: { items: items.slice(0, 10) },
     _meta: {
       viewType: "items",
       hasMore: items.length > 10,
     },
   };
   ```

2. **Limit image sizes**:
   ```typescript
   // Convert images to data URLs with size limit
   async function imageToDataUrl(url: string, maxSizeKb = 200): Promise<string | null> {
     const response = await fetch(url);
     const buffer = await response.arrayBuffer();

     if (buffer.byteLength / 1024 > maxSizeKb) {
       console.log(`Image too large: ${buffer.byteLength / 1024}KB > ${maxSizeKb}KB`);
       return null;  // Skip oversized images
     }

     const base64 = Buffer.from(buffer).toString('base64');
     const contentType = response.headers.get('content-type') || 'image/jpeg';
     return `data:${contentType};base64,${base64}`;
   }
   ```

3. **Log response sizes**:
   ```typescript
   const response = { content, structuredContent, _meta };
   const size = JSON.stringify(response).length;
   console.log(`Response size: ${(size / 1024).toFixed(1)}KB`);

   if (size > 300 * 1024) {
     console.warn('Response exceeds 300KB - may fail to deliver');
   }

   return response;
   ```

4. **Paginate large datasets**:
   ```typescript
   return {
     structuredContent: {
       items: items.slice(0, 20),
       pagination: {
         total: items.length,
         hasMore: items.length > 20,
         cursor: items[19]?.id,
       },
     },
   };
   ```

---

### Widget Diagnostic Logging

When widgets timeout or show empty state, add diagnostic logging:

```javascript
// Log when timeout occurs
function onTimeout() {
  console.log('Widget timeout diagnostic:', {
    hasToolOutput: !!window.openai?.toolOutput,
    toolOutputKeys: Object.keys(window.openai?.toolOutput || {}),
    hasToolResponseMetadata: !!window.openai?.toolResponseMetadata,
    viewType: window.openai?.toolResponseMetadata?.viewType,
    hasToolInput: !!window.openai?.toolInput,
    toolInputKeys: Object.keys(window.openai?.toolInput || {}),
    theme: window.openai?.theme,
    displayMode: window.openai?.displayMode,
  });
}
```

**What to look for**:
- `hasToolOutput: false` + server logs show success = **session routing bug** (see Critical section)
- `hasToolOutput: true` but wrong keys = **response structure mismatch**
- `viewType: undefined` = **missing `_meta.viewType`** in response

---

## Debugging Tools

### MCP Inspector
```bash
npx @modelcontextprotocol/inspector@latest http://localhost:8000/mcp
```
Use to test tools and resources directly without ChatGPT.

### Browser Console
Open DevTools console in ChatGPT to see:
- Widget JavaScript errors
- CSP violations
- Network request failures

### Server Logs
Add logging to track:
- Incoming requests
- Tool call parameters
- Response times
- Errors

```typescript
console.log("Tool called:", name, "with args:", JSON.stringify(args));
```
