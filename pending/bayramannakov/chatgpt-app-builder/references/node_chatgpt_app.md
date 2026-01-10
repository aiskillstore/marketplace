# Node.js ChatGPT App Implementation Guide

Complete reference for building ChatGPT Apps with Node.js/TypeScript.

Based on official OpenAI examples: [pizzaz_server_node](https://github.com/openai/openai-apps-sdk-examples/tree/main/pizzaz_server_node) and [kitchen_sink_server_node](https://github.com/openai/openai-apps-sdk-examples/tree/main/kitchen_sink_server_node).

## Project Structure

```
myapp-chatgpt/
├── package.json
├── tsconfig.json
├── .env.example
├── src/
│   ├── index.ts                 # HTTP server + MCP handlers
│   ├── widget/
│   │   ├── App.tsx              # React widget
│   │   └── embed.ts             # Widget bundling
│   ├── types/
│   │   └── openai.d.ts          # window.openai types
│   └── lib/
│       ├── api-client.ts        # Your backend API client
│       └── errors.ts            # Error handling utilities
├── scripts/
│   └── build-widget.ts          # esbuild config
└── dist/                        # Build output
    └── widget/
        ├── bundle.js
        └── bundle.css
```

---

## Package Configuration

### package.json
```json
{
  "name": "myapp-chatgpt",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "npm run build:widget && tsc",
    "build:widget": "tsx scripts/build-widget.ts",
    "dev": "tsx watch src/index.ts",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "esbuild": "^0.20.0",
    "tsx": "^4.0.0",
    "typescript": "^5.3.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "jsx": "react-jsx"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Server Implementation

The server uses **SSE (Server-Sent Events) transport** with a single path:
- `GET /mcp` - SSE stream connection
- `POST /mcp` - Message handling (same path, different method)

**Important**: Use the SAME path for both GET and POST. Using separate paths (e.g., `/mcp/messages`) can cause session mismatch issues with proxies like MCP Inspector.

### src/index.ts

```typescript
import {
  createServer,
  type IncomingMessage,
  type ServerResponse,
} from "node:http";
import fs from "node:fs";
import path from "node:path";
import { URL, fileURLToPath } from "node:url";

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  type CallToolRequest,
  type ListResourcesRequest,
  type ListToolsRequest,
  type ReadResourceRequest,
  type Resource,
  type Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// ============================================================================
// Configuration
// ============================================================================

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ASSETS_DIR = path.resolve(__dirname, "..", "dist", "widget");

const TEMPLATE_URI = "ui://widget/app.html";
const MIME_TYPE = "text/html+skybridge";

// ============================================================================
// Widget HTML Loading
// ============================================================================

function readWidgetHtml(): string {
  const bundlePath = path.join(ASSETS_DIR, "bundle.js");
  const cssPath = path.join(ASSETS_DIR, "bundle.css");

  if (!fs.existsSync(bundlePath)) {
    return `<!DOCTYPE html><html><body><p>Widget not built</p></body></html>`;
  }

  const js = fs.readFileSync(bundlePath, "utf-8");
  const css = fs.existsSync(cssPath) ? fs.readFileSync(cssPath, "utf-8") : "";

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>${css}</style>
</head>
<body>
  <div id="root"></div>
  <script type="module">${js}</script>
</body>
</html>`;
}

const widgetHtml = readWidgetHtml();

// ============================================================================
// Tool Definitions
// ============================================================================

// Use JSON Schema for tool definitions (not Zod directly)
const tools: Tool[] = [
  {
    name: "myapp_get_items",
    title: "Get Items",
    description: "Use this when the user wants to see their items.",
    inputSchema: {
      type: "object",
      properties: {
        status: {
          type: "string",
          enum: ["active", "completed", "all"],
          description: "Filter items by status",
        },
        limit: {
          type: "number",
          description: "Maximum items to return (1-100)",
        },
      },
      required: [],
      additionalProperties: false,
    },
    _meta: {
      "openai/outputTemplate": TEMPLATE_URI,
      "openai/toolInvocation/invoking": "Loading items...",
      "openai/toolInvocation/invoked": "Items loaded",
      "openai/widgetAccessible": true,
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      openWorldHint: false,
    },
  },
];

// Zod parsers for runtime validation
const getItemsParser = z.object({
  status: z.enum(["active", "completed", "all"]).optional().default("all"),
  limit: z.number().int().min(1).max(100).optional().default(20),
});

// ============================================================================
// Resource Definitions
// ============================================================================

const resources: Resource[] = [
  {
    uri: TEMPLATE_URI,
    name: "App Widget",
    mimeType: MIME_TYPE,
    _meta: {
      "openai/outputTemplate": TEMPLATE_URI,
      "openai/widgetAccessible": true,
    },
  },
];

// ============================================================================
// Server Factory (creates new instance per SSE connection)
// ============================================================================

function createAppServer(): Server {
  const server = new Server(
    { name: "myapp-chatgpt", version: "1.0.0" },
    { capabilities: { resources: {}, tools: {} } }
  );

  // List tools
  server.setRequestHandler(
    ListToolsRequestSchema,
    async (_request: ListToolsRequest) => ({ tools })
  );

  // List resources
  server.setRequestHandler(
    ListResourcesRequestSchema,
    async (_request: ListResourcesRequest) => ({ resources })
  );

  // Read resource (widget HTML)
  // IMPORTANT: _meta must include all widget configuration
  server.setRequestHandler(
    ReadResourceRequestSchema,
    async (_request: ReadResourceRequest) => ({
      contents: [{
        uri: TEMPLATE_URI,
        mimeType: MIME_TYPE,
        text: widgetHtml,
        _meta: {
          "openai/outputTemplate": TEMPLATE_URI,
          "openai/widgetAccessible": true,
          "openai/widgetPrefersBorder": true,
          "openai/widgetCSP": {
            connect_domains: ["https://api.myapp.com"],  // Your API domains
            resource_domains: [],  // CDN domains for assets
          },
          "openai/widgetDomain": "your-app.fly.dev",  // Your deployment domain
        },
      }],
    })
  );

  // Handle tool calls
  server.setRequestHandler(
    CallToolRequestSchema,
    async (request: CallToolRequest) => {
      const { name, arguments: args } = request.params;

      if (name === "myapp_get_items") {
        const parsed = getItemsParser.parse(args ?? {});
        // Your API call here
        const items = [{ id: "1", title: "Sample item", status: "active" }];

        return {
          content: [{ type: "text", text: `Found ${items.length} items` }],
          structuredContent: { items, total: items.length },
          _meta: { fullItems: items },
        };
      }

      throw new Error(`Unknown tool: ${name}`);
    }
  );

  return server;
}

// ============================================================================
// Session Management
// ============================================================================

type SessionRecord = { server: Server; transport: SSEServerTransport };
const sessions = new Map<string, SessionRecord>();

// IMPORTANT: Use same path for GET (SSE) and POST (messages)
const mcpPath = "/mcp";

// ============================================================================
// HTTP Server
// ============================================================================

const port = Number(process.env.PORT ?? 8000);

const httpServer = createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://localhost:${port}`);

  // CORS headers for all responses
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  // CORS preflight
  if (req.method === "OPTIONS") {
    res.writeHead(204).end();
    return;
  }

  // Health check
  if (url.pathname === "/health") {
    res.writeHead(200).end("OK");
    return;
  }

  // SSE connection (GET /mcp)
  if (req.method === "GET" && url.pathname === mcpPath) {
    const server = createAppServer();
    // Pass the SAME path where POST will be handled
    const transport = new SSEServerTransport(mcpPath, res);
    const sessionId = crypto.randomUUID();

    sessions.set(sessionId, { server, transport });

    res.on("close", () => {
      sessions.delete(sessionId);
      server.close();
    });

    await server.connect(transport);
    return;
  }

  // Message handling (POST /mcp)
  if (req.method === "POST" && url.pathname === mcpPath) {
    // Collect request body
    let body = "";
    for await (const chunk of req) {
      body += chunk;
    }

    // Let SSEServerTransport handle session matching internally
    // Don't implement custom session validation - it conflicts with SDK
    let handled = false;
    for (const [, session] of sessions) {
      try {
        await session.transport.handlePostMessage(req, res, body);
        handled = true;
        break;
      } catch {
        // This transport doesn't match, try next
        continue;
      }
    }

    if (!handled) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "No active session" }));
    }
    return;
  }

  res.writeHead(404).end("Not Found");
});

httpServer.listen(port, () => {
  console.log(`MCP server listening on http://localhost:${port}`);
  console.log(`  MCP endpoint: http://localhost:${port}${mcpPath}`);
  console.log(`  Health check: http://localhost:${port}/health`);
});
```

---

## Key Patterns

### 1. SSE Transport (Not Stdio)

ChatGPT Apps require HTTP-based transport. The official examples use SSE:

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

// Create new server instance per connection
const server = createAppServer();
const transport = new SSEServerTransport("/mcp", res);

// IMPORTANT: Connect first, then access sessionId
await server.connect(transport);

// sessionId is generated during connect(), not before
const sessionId = (transport as any).sessionId;
```

### 2. Single Path, Two Methods

Use the SAME path for both operations (critical for proxy compatibility):
- `GET /mcp` - Establishes SSE stream connection
- `POST /mcp` - Handles messages (SSEServerTransport manages sessions internally)

**Do NOT use separate paths** like `/mcp/messages` - this causes session mismatch with MCP Inspector proxy.

### 3. Tool Definitions Use JSON Schema

Tool input schemas must be JSON Schema objects, not Zod schemas:

```typescript
const tools: Tool[] = [{
  name: "myapp_action",
  inputSchema: {
    type: "object",
    properties: {
      param: { type: "string", description: "..." }
    },
    required: ["param"],
    additionalProperties: false,
  },
  // ...
}];
```

Use Zod separately for runtime validation:

```typescript
const actionParser = z.object({ param: z.string() });
const parsed = actionParser.parse(args ?? {});
```

### 4. Tool Metadata

```typescript
_meta: {
  "openai/outputTemplate": "ui://widget/app.html",
  "openai/toolInvocation/invoking": "Loading...",
  "openai/toolInvocation/invoked": "Done",
  "openai/widgetAccessible": true,  // Widget can call this tool
}
```

### 5. Tool Annotations

```typescript
annotations: {
  readOnlyHint: true,      // No side effects
  destructiveHint: false,  // Doesn't delete data
  openWorldHint: false,    // Doesn't affect external systems
}
```

### 6. Response Structure

```typescript
return {
  content: [{ type: "text", text: "Summary for model" }],
  structuredContent: { /* Data model can process */ },
  _meta: { /* Widget-only data, hidden from model */ },
};
```

### 7. Interactive Widget State Management

When widgets call tools via `window.openai.callTool()`, the widget UI won't automatically update because `toolOutput` is immutable for each widget instance. Widgets must manage local React state.

**The Pattern:**

```typescript
interface ToolResult {
  structuredContent?: { items?: Item[] };
}

export function App() {
  const output = useToolOutput<{ items: Item[] }>();

  // Local state - initialized from toolOutput
  const [items, setItems] = useState<Item[]>(output?.items || []);

  // Sync when ChatGPT re-renders widget with new toolOutput
  useEffect(() => {
    if (output?.items) setItems(output.items);
  }, [output?.items]);

  const handleDelete = async (id: string) => {
    // Optimistic update
    setItems(prev => prev.filter(item => item.id !== id));

    try {
      const result = await window.openai.callTool("myapp_delete", { id }) as ToolResult;
      if (result?.structuredContent?.items) {
        setItems(result.structuredContent.items);
      }
    } catch (error) {
      // Re-fetch on error to restore accurate state
    }
  };
}
```

**Server-Side Requirement:** Tool handlers must return updated data in `structuredContent`:

```typescript
function handleDeleteItem(args: { id: string }) {
  items.delete(args.id);

  return {
    content: [{ type: "text", text: "Deleted" }],
    structuredContent: {
      items: Array.from(items.values()), // Return updated list!
    },
    _meta: { "openai/outputTemplate": TEMPLATE_URI },
  };
}
```

---

## Environment Variables

### .env.example
```bash
# Server configuration
PORT=8000

# Your backend API
API_BASE_URL=https://api.myapp.com
API_TOKEN=your_api_token_here

# Widget asset URL (for production)
BASE_URL=https://your-app.fly.dev
```

---

## Development Workflow

### 1. Build Widget
```bash
npm run build:widget
```

### 2. Start Server
```bash
npm run dev
# Server runs at http://localhost:8000
```

### 3. Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector@latest http://localhost:8000/mcp
```

### 4. Create Tunnel for ChatGPT
```bash
ngrok http 8000
# Use the https URL in ChatGPT connector settings
```

---

## Deployment (Fly.io)

### Dockerfile
```dockerfile
FROM node:20-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["node", "dist/index.js"]
```

### fly.toml
```toml
app = 'myapp-chatgpt'
primary_region = 'sjc'

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 0
  processes = ['app']

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

### Deploy Commands
```bash
# Build first
npm run build

# Launch (first time)
fly launch

# Deploy (subsequent)
fly deploy

# CRITICAL: Scale to 1 machine for SSE
fly scale count 1 --yes
```

### Multi-Machine Session Issue

**SSE transport uses in-memory state.** If your platform creates multiple machines (Fly.io defaults to 2), SSE connections and POST requests may go to different machines:

```
User → SSE GET /mcp → Machine A (stores session)
User → POST /mcp    → Machine B (no session - fails!)
```

**Solutions**:
1. **Single machine** (simplest): `fly scale count 1 --yes`
2. **Sticky sessions**: Configure load balancer affinity
3. **External storage**: Use Redis for session coordination

---

## Quality Checklist

### Server Implementation
- [ ] Uses `Server` from `@modelcontextprotocol/sdk/server/index.js`
- [ ] Uses `SSEServerTransport` (not Stdio)
- [ ] Uses SAME path `/mcp` for both GET and POST (not separate paths!)
- [ ] SSEServerTransport constructor receives same path as POST handler
- [ ] POST handler collects body and passes to `handlePostMessage(req, res, body)`
- [ ] No custom session validation (let SDK handle it internally)
- [ ] Accesses `transport.sessionId` AFTER `server.connect()` (not before!)
- [ ] Includes CORS headers on all responses
- [ ] Health check endpoint at `/health`

### Tool Configuration
- [ ] Tool schemas are JSON Schema objects (not Zod)
- [ ] Tool annotations are correct (readOnlyHint, destructiveHint, openWorldHint)
- [ ] Response uses content/structuredContent/_meta layers
- [ ] `_meta["openai/outputTemplate"]` matches resource URI
- [ ] Mutating tools return updated data in `structuredContent` for widget sync

### Widget & Resources
- [ ] Widget bundles correctly with `npm run build:widget`
- [ ] Widget HTML is self-contained (no external scripts)
- [ ] Resource registered with `mimeType: "text/html+skybridge"`
- [ ] ListResources includes `_meta` with `openai/outputTemplate` and `openai/widgetAccessible`
- [ ] ReadResource includes full `_meta` with CSP, domain, and all required fields
- [ ] Tool responses include `_meta["openai/outputTemplate"]` matching resource URI
- [ ] `window.openai` API calls use `typeof === "function"` guards
- [ ] Interactive widgets manage local state (not just `toolOutput`)
- [ ] Widget updates local state from `callTool()` response `structuredContent`

### Testing & Deployment
- [ ] Tested with MCP Inspector before ChatGPT deployment
- [ ] Deployed to single machine (or configured sticky sessions)
- [ ] Verified SSE+POST work on production URL
- [ ] ChatGPT connector created and tools visible
- [ ] After metadata changes, recreated connector to clear cache
