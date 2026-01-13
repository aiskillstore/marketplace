/**
 * Get Items Tool
 *
 * Read-only tool to retrieve items from the backend.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { handleApiError } from "../lib/errors.js";
import { apiClient } from "../lib/api-client.js";

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
      .describe("Maximum items to return (1-100)"),
    cursor: z.string().optional().describe("Pagination cursor"),
  })
  .strict();

type GetItemsInput = z.infer<typeof GetItemsSchema>;

interface Config {
  apiBaseUrl: string;
}

export function registerGetItems(server: McpServer, _config: Config): void {
  server.registerTool(
    "{{APP_PREFIX}}_get_items",
    {
      title: "Get Items",
      description:
        "Use this when the user wants to see their items, " +
        "optionally filtered by status. Returns items with titles, " +
        "statuses, and due dates.",
      inputSchema: GetItemsSchema,
      _meta: {
        "openai/outputTemplate": "ui://widget/app.html",
        "openai/toolInvocation/invoking": "Loading items...",
        "openai/toolInvocation/invoked": "Items ready.",
        "openai/readOnlyHint": true,
      },
    },
    async (params: GetItemsInput) => {
      try {
        const items = await apiClient.getItems({
          status: params.status,
          limit: params.limit,
          cursor: params.cursor,
        });

        const summary =
          items.length === 0
            ? "No items found"
            : `Found ${items.length} item${items.length === 1 ? "" : "s"}`;

        return {
          content: [{ type: "text", text: summary }],
          structuredContent: {
            items: items.map((item) => ({
              id: item.id,
              title: item.title,
              status: item.status,
              due_date: item.dueDate,
              priority: item.priority,
            })),
            total: items.length,
            hasMore: items.length === params.limit,
          },
          _meta: {
            fullItems: items,
            pagination: {
              cursor: items.length > 0 ? items[items.length - 1].id : null,
              hasMore: items.length === params.limit,
            },
          },
        };
      } catch (error) {
        return {
          content: [{ type: "text", text: handleApiError(error) }],
          structuredContent: { error: true, items: [] },
        };
      }
    }
  );
}
