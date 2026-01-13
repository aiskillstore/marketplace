/**
 * Example Tool: Get Items
 *
 * This is a read-only tool that retrieves items from the backend.
 * Use this as a template for creating new tools.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// ============================================================================
// Schema Definition
// ============================================================================

/**
 * Input schema with Zod validation.
 *
 * Best practices:
 * - Use .describe() for every parameter
 * - Use .strict() to reject unexpected fields
 * - Set sensible defaults for optional parameters
 * - Add meaningful validation constraints
 */
const GetItemsSchema = z
  .object({
    status: z
      .enum(["active", "completed", "all"])
      .default("all")
      .describe("Filter items by status"),

    limit: z
      .number()
      .int()
      .min(1)
      .max(100)
      .default(20)
      .describe("Maximum number of items to return (1-100)"),

    cursor: z
      .string()
      .optional()
      .describe("Pagination cursor from previous response"),
  })
  .strict();

type GetItemsInput = z.infer<typeof GetItemsSchema>;

// ============================================================================
// Response Types
// ============================================================================

interface Item {
  id: string;
  title: string;
  status: "active" | "completed";
  priority: "low" | "medium" | "high";
  dueDate?: string;
  createdAt: string;
}

interface GetItemsResponse {
  items: Item[];
  total: number;
  hasMore: boolean;
}

// ============================================================================
// Tool Registration
// ============================================================================

interface Config {
  apiBaseUrl: string;
}

export function registerGetItems(server: McpServer, config: Config): void {
  server.registerTool(
    // Tool name: service_verb_noun pattern
    "{{APP_PREFIX}}_get_items",

    // Tool configuration
    {
      // Human-readable title
      title: "Get Items",

      // Description for model selection
      // Start with "Use this when..." to guide the model
      description:
        "Use this when the user wants to see their items, " +
        "optionally filtered by status. Returns a list of items with " +
        "titles, statuses, due dates, and priorities.",

      // Zod schema for input validation
      inputSchema: GetItemsSchema,

      // Tool metadata
      _meta: {
        // Widget to render results
        "openai/outputTemplate": "ui://widget/app.html",

        // Loading state messages
        "openai/toolInvocation/invoking": "Loading items...",
        "openai/toolInvocation/invoked": "Items ready.",

        // Tool annotations
        "openai/readOnlyHint": true, // This tool only reads data
        // "openai/destructiveHint": true,  // For delete/modify tools
        // "openai/openWorldHint": true,    // For external system tools
      },
    },

    // Tool handler
    async (params: GetItemsInput) => {
      try {
        // TODO: Replace with actual API call
        const response = await fetchItems(config.apiBaseUrl, params);

        // Build summary for model
        const summary =
          response.items.length === 0
            ? "No items found"
            : `Found ${response.items.length} item${response.items.length === 1 ? "" : "s"}`;

        return {
          // Text content for model (concise summary)
          content: [{ type: "text", text: summary }],

          // Structured content for model (machine-readable, kept minimal)
          structuredContent: {
            items: response.items.map((item) => ({
              id: item.id,
              title: item.title,
              status: item.status,
              due_date: item.dueDate,
              priority: item.priority,
            })),
            total: response.total,
            hasMore: response.hasMore,
          },

          // Metadata for widget only (hidden from model)
          _meta: {
            // Full item data for widget rendering
            fullItems: response.items,

            // Pagination info
            pagination: {
              cursor:
                response.items.length > 0
                  ? response.items[response.items.length - 1].id
                  : null,
              hasMore: response.hasMore,
            },
          },
        };
      } catch (error) {
        // Return actionable error message
        const message = handleError(error);

        return {
          content: [{ type: "text", text: message }],
          structuredContent: {
            error: true,
            items: [],
          },
        };
      }
    }
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Fetch items from the backend API.
 * TODO: Replace with actual implementation.
 */
async function fetchItems(
  baseUrl: string,
  params: GetItemsInput
): Promise<GetItemsResponse> {
  // Example implementation - replace with actual API call
  const url = new URL("/items", baseUrl);
  if (params.status !== "all") {
    url.searchParams.set("status", params.status);
  }
  url.searchParams.set("limit", params.limit.toString());
  if (params.cursor) {
    url.searchParams.set("cursor", params.cursor);
  }

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${process.env.API_TOKEN}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Convert errors to actionable user messages.
 */
function handleError(error: unknown): string {
  if (error instanceof Error) {
    // Check for common HTTP errors
    if (error.message.includes("401")) {
      return "Authentication required. Please reconnect your account.";
    }
    if (error.message.includes("403")) {
      return "Permission denied. You don't have access to this resource.";
    }
    if (error.message.includes("404")) {
      return "Resource not found. It may have been deleted.";
    }
    if (error.message.includes("429")) {
      return "Rate limit exceeded. Please wait a moment and try again.";
    }
    if (error.message.includes("500") || error.message.includes("502")) {
      return "Service temporarily unavailable. Please try again later.";
    }

    return `An error occurred: ${error.message}`;
  }

  return "An unexpected error occurred. Please try again.";
}
