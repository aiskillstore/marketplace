/**
 * {{APP_NAME}} ChatGPT App - MCP Server
 *
 * This MCP server uses SSE transport to communicate with ChatGPT.
 * Based on official OpenAI examples (pizzaz_server_node, kitchen_sink_server_node).
 *
 * Endpoints:
 *   GET  /mcp          - SSE stream connection
 *   POST /mcp/messages - Message handling (with sessionId query param)
 *   GET  /health       - Health check
 */

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
  ListResourceTemplatesRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  type CallToolRequest,
  type ListResourceTemplatesRequest,
  type ListResourcesRequest,
  type ListToolsRequest,
  type ReadResourceRequest,
  type Resource,
  type ResourceTemplate,
  type Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// ============================================================================
// Configuration
// ============================================================================

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ASSETS_DIR = path.resolve(__dirname, "..", "dist", "widget");

const config = {
  name: process.env.APP_NAME || "{{APP_NAME}}",
  version: process.env.APP_VERSION || "1.0.0",
  apiBaseUrl: process.env.API_BASE_URL || "https://api.{{APP_DOMAIN}}",
};

const TEMPLATE_URI = "ui://widget/app.html";
const MIME_TYPE = "text/html+skybridge";

// ============================================================================
// Widget HTML Loading
// ============================================================================

function readWidgetHtml(): string {
  const bundlePath = path.join(ASSETS_DIR, "bundle.js");
  const cssPath = path.join(ASSETS_DIR, "bundle.css");

  if (!fs.existsSync(bundlePath)) {
    console.warn(
      `Widget bundle not found at ${bundlePath}. Run "npm run build:widget" first.`
    );
    return `<!DOCTYPE html><html><body><p>Widget not built. Run npm run build:widget</p></body></html>`;
  }

  const js = fs.readFileSync(bundlePath, "utf-8");
  const css = fs.existsSync(cssPath) ? fs.readFileSync(cssPath, "utf-8") : "";

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.5;
    }
    ${css}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module">
    ${js}
  </script>
</body>
</html>`;
}

const widgetHtml = readWidgetHtml();

// ============================================================================
// Tool Metadata Helpers
// ============================================================================

function toolDescriptorMeta(invokingMsg: string, invokedMsg: string) {
  return {
    "openai/outputTemplate": TEMPLATE_URI,
    "openai/toolInvocation/invoking": invokingMsg,
    "openai/toolInvocation/invoked": invokedMsg,
    "openai/widgetAccessible": true,
  } as const;
}

// ============================================================================
// Tool Definitions
// ============================================================================

// Input schemas for Zod validation
const getItemsParser = z.object({
  status: z.enum(["active", "completed", "all"]).optional().default("all"),
  limit: z.number().int().min(1).max(100).optional().default(20),
  cursor: z.string().optional(),
});

const createItemParser = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(2000).optional(),
  due_date: z.string().optional(),
  priority: z.enum(["low", "medium", "high"]).optional().default("medium"),
});

// Tool definitions with JSON Schema (for MCP protocol)
const tools: Tool[] = [
  {
    name: "{{APP_PREFIX}}_get_items",
    title: "Get Items",
    description:
      "Use this when the user wants to see their items, tasks, or list. " +
      "Optionally filter by status (active, completed, all) or limit results.",
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
        cursor: {
          type: "string",
          description: "Pagination cursor from previous response",
        },
      },
      required: [],
      additionalProperties: false,
    },
    _meta: toolDescriptorMeta("Loading items...", "Items loaded"),
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      openWorldHint: false,
    },
  },
  {
    name: "{{APP_PREFIX}}_create_item",
    title: "Create Item",
    description:
      "Use this when the user wants to create a new item, task, or entry. " +
      "Requires a title, optionally accepts description, due date, and priority.",
    inputSchema: {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "Title of the new item",
        },
        description: {
          type: "string",
          description: "Optional detailed description",
        },
        due_date: {
          type: "string",
          description: "Due date in ISO 8601 format (e.g., 2024-01-15)",
        },
        priority: {
          type: "string",
          enum: ["low", "medium", "high"],
          description: "Priority level",
        },
      },
      required: ["title"],
      additionalProperties: false,
    },
    _meta: toolDescriptorMeta("Creating item...", "Item created"),
    annotations: {
      readOnlyHint: false,
      destructiveHint: false,
      openWorldHint: true,
    },
  },
  {
    name: "{{APP_PREFIX}}_complete_item",
    title: "Complete Item",
    description:
      "Use this when the user wants to mark an item as complete or done. " +
      "Requires the item ID.",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "ID of the item to complete",
        },
      },
      required: ["id"],
      additionalProperties: false,
    },
    _meta: toolDescriptorMeta("Completing item...", "Item completed"),
    annotations: {
      readOnlyHint: false,
      destructiveHint: false,
      openWorldHint: true,
    },
  },
];

// ============================================================================
// Resource Definitions
// ============================================================================

const resources: Resource[] = [
  {
    uri: TEMPLATE_URI,
    name: `${config.name} Widget`,
    description: `Main application widget for ${config.name}`,
    mimeType: MIME_TYPE,
    _meta: {
      "openai/outputTemplate": TEMPLATE_URI,
    },
  },
];

const resourceTemplates: ResourceTemplate[] = [
  {
    uriTemplate: TEMPLATE_URI,
    name: `${config.name} Widget Template`,
    description: `Widget markup template for ${config.name}`,
    mimeType: MIME_TYPE,
    _meta: {
      "openai/outputTemplate": TEMPLATE_URI,
    },
  },
];

// ============================================================================
// Mock Data (Replace with your API client)
// ============================================================================

interface Item {
  id: string;
  title: string;
  description?: string;
  status: "active" | "completed";
  dueDate?: string;
  priority: "low" | "medium" | "high";
  createdAt: string;
}

// Mock items - replace with actual API calls
let mockItems: Item[] = [
  {
    id: "1",
    title: "Review documentation",
    status: "active",
    priority: "high",
    createdAt: new Date().toISOString(),
  },
  {
    id: "2",
    title: "Update dependencies",
    status: "active",
    priority: "medium",
    createdAt: new Date().toISOString(),
  },
  {
    id: "3",
    title: "Write tests",
    status: "completed",
    priority: "low",
    createdAt: new Date().toISOString(),
  },
];

// ============================================================================
// Server Factory
// ============================================================================

function createAppServer(): Server {
  const server = new Server(
    {
      name: `${config.name}-chatgpt`,
      version: config.version,
    },
    {
      capabilities: {
        resources: {},
        tools: {},
      },
    }
  );

  // List resources
  server.setRequestHandler(
    ListResourcesRequestSchema,
    async (_request: ListResourcesRequest) => ({
      resources,
    })
  );

  // Read resource (widget HTML)
  server.setRequestHandler(
    ReadResourceRequestSchema,
    async (_request: ReadResourceRequest) => ({
      contents: [
        {
          uri: TEMPLATE_URI,
          mimeType: MIME_TYPE,
          text: widgetHtml,
          _meta: {
            "openai/widgetPrefersBorder": true,
            "openai/widgetDomain": "https://chatgpt.com",
            "openai/widgetCSP": {
              connect_domains: [config.apiBaseUrl],
              resource_domains: ["https://*.oaistatic.com"],
              redirect_domains: [],
            },
          },
        },
      ],
    })
  );

  // List resource templates
  server.setRequestHandler(
    ListResourceTemplatesRequestSchema,
    async (_request: ListResourceTemplatesRequest) => ({
      resourceTemplates,
    })
  );

  // List tools
  server.setRequestHandler(
    ListToolsRequestSchema,
    async (_request: ListToolsRequest) => ({
      tools,
    })
  );

  // Handle tool calls
  server.setRequestHandler(
    CallToolRequestSchema,
    async (request: CallToolRequest) => {
      const { name, arguments: args } = request.params;

      // Get Items
      if (name === "{{APP_PREFIX}}_get_items") {
        const parsed = getItemsParser.parse(args ?? {});
        let items = [...mockItems];

        // Filter by status
        if (parsed.status !== "all") {
          items = items.filter((item) => item.status === parsed.status);
        }

        // Apply limit
        const limited = items.slice(0, parsed.limit);
        const hasMore = items.length > parsed.limit;

        const summary =
          limited.length === 0
            ? "No items found"
            : `Found ${limited.length} item${limited.length === 1 ? "" : "s"}`;

        return {
          content: [{ type: "text", text: summary }],
          structuredContent: {
            items: limited.map((item) => ({
              id: item.id,
              title: item.title,
              status: item.status,
              due_date: item.dueDate,
              priority: item.priority,
            })),
            total: limited.length,
            hasMore,
          },
          _meta: {
            fullItems: limited,
            pagination: {
              cursor: hasMore ? limited[limited.length - 1].id : null,
              hasMore,
            },
          },
        };
      }

      // Create Item
      if (name === "{{APP_PREFIX}}_create_item") {
        const parsed = createItemParser.parse(args ?? {});
        const newItem: Item = {
          id: String(Date.now()),
          title: parsed.title,
          description: parsed.description,
          status: "active",
          dueDate: parsed.due_date,
          priority: parsed.priority,
          createdAt: new Date().toISOString(),
        };
        mockItems.push(newItem);

        return {
          content: [
            {
              type: "text",
              text: `Created item "${newItem.title}" with ID ${newItem.id}`,
            },
          ],
          structuredContent: {
            id: newItem.id,
            title: newItem.title,
            status: newItem.status,
            created_at: newItem.createdAt,
          },
          _meta: {
            fullItem: newItem,
          },
        };
      }

      // Complete Item
      if (name === "{{APP_PREFIX}}_complete_item") {
        const id = (args as { id: string })?.id;
        if (!id) {
          return {
            content: [{ type: "text", text: "Error: Item ID is required" }],
            structuredContent: { error: true, message: "Missing item ID" },
          };
        }

        const item = mockItems.find((i) => i.id === id);
        if (!item) {
          return {
            content: [{ type: "text", text: `Error: Item ${id} not found` }],
            structuredContent: { error: true, message: "Item not found" },
          };
        }

        item.status = "completed";

        return {
          content: [{ type: "text", text: `Completed item "${item.title}"` }],
          structuredContent: {
            id: item.id,
            title: item.title,
            status: item.status,
          },
          _meta: {
            fullItem: item,
          },
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

type SessionRecord = {
  server: Server;
  transport: SSEServerTransport;
};

const sessions = new Map<string, SessionRecord>();

// ============================================================================
// HTTP Handlers
// ============================================================================

const ssePath = "/mcp";
const postPath = "/mcp/messages";

async function handleSseRequest(res: ServerResponse) {
  res.setHeader("Access-Control-Allow-Origin", "*");

  const server = createAppServer();
  const transport = new SSEServerTransport(postPath, res);
  const sessionId = transport.sessionId;

  sessions.set(sessionId, { server, transport });

  transport.onclose = async () => {
    sessions.delete(sessionId);
    await server.close();
  };

  transport.onerror = (error) => {
    console.error("SSE transport error:", error);
  };

  try {
    await server.connect(transport);
  } catch (error) {
    sessions.delete(sessionId);
    console.error("Failed to start SSE session:", error);
    if (!res.headersSent) {
      res.writeHead(500).end("Failed to establish SSE connection");
    }
  }
}

async function handlePostMessage(
  req: IncomingMessage,
  res: ServerResponse,
  url: URL
) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");

  const sessionId = url.searchParams.get("sessionId");

  if (!sessionId) {
    res.writeHead(400).end("Missing sessionId query parameter");
    return;
  }

  const session = sessions.get(sessionId);

  if (!session) {
    res.writeHead(404).end("Unknown session");
    return;
  }

  try {
    await session.transport.handlePostMessage(req, res);
  } catch (error) {
    console.error("Failed to process message:", error);
    if (!res.headersSent) {
      res.writeHead(500).end("Failed to process message");
    }
  }
}

// ============================================================================
// HTTP Server
// ============================================================================

const portEnv = Number(process.env.PORT ?? 8000);
const port = Number.isFinite(portEnv) ? portEnv : 8000;

const httpServer = createServer(
  async (req: IncomingMessage, res: ServerResponse) => {
    if (!req.url) {
      res.writeHead(400).end("Missing URL");
      return;
    }

    const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

    // CORS preflight
    if (
      req.method === "OPTIONS" &&
      (url.pathname === ssePath || url.pathname === postPath)
    ) {
      res.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "content-type",
      });
      res.end();
      return;
    }

    // SSE stream endpoint
    if (req.method === "GET" && url.pathname === ssePath) {
      await handleSseRequest(res);
      return;
    }

    // Message endpoint
    if (req.method === "POST" && url.pathname === postPath) {
      await handlePostMessage(req, res, url);
      return;
    }

    // Health check
    if (url.pathname === "/health") {
      res.writeHead(200).end("OK");
      return;
    }

    res.writeHead(404).end("Not Found");
  }
);

httpServer.on("clientError", (err: Error, socket) => {
  console.error("HTTP client error:", err);
  socket.end("HTTP/1.1 400 Bad Request\r\n\r\n");
});

httpServer.listen(port, () => {
  console.log(`${config.name} MCP server listening on http://localhost:${port}`);
  console.log(`  SSE stream:      GET  http://localhost:${port}${ssePath}`);
  console.log(`  Message endpoint: POST http://localhost:${port}${postPath}?sessionId=...`);
  console.log(`  Health check:    GET  http://localhost:${port}/health`);
});
