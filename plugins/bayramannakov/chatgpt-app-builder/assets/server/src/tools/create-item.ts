/**
 * Create Item Tool
 *
 * Write tool to create a new item in the backend.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { handleApiError } from "../lib/errors.js";
import { apiClient } from "../lib/api-client.js";

const CreateItemSchema = z
  .object({
    title: z
      .string()
      .min(1)
      .max(200)
      .describe("Title of the new item"),
    description: z
      .string()
      .max(2000)
      .optional()
      .describe("Optional detailed description"),
    due_date: z
      .string()
      .optional()
      .describe("Due date in ISO 8601 format (e.g., 2024-01-15)"),
    priority: z
      .enum(["low", "medium", "high"])
      .default("medium")
      .describe("Priority level"),
  })
  .strict();

type CreateItemInput = z.infer<typeof CreateItemSchema>;

interface Config {
  apiBaseUrl: string;
}

export function registerCreateItem(server: McpServer, _config: Config): void {
  server.registerTool(
    "{{APP_PREFIX}}_create_item",
    {
      title: "Create Item",
      description:
        "Use this when the user wants to create a new item. " +
        "Requires a title, optionally accepts description, due date, and priority.",
      inputSchema: CreateItemSchema,
      _meta: {
        "openai/outputTemplate": "ui://widget/app.html",
        "openai/toolInvocation/invoking": "Creating item...",
        "openai/toolInvocation/invoked": "Item created.",
        "openai/openWorldHint": true,
      },
    },
    async (params: CreateItemInput) => {
      try {
        const newItem = await apiClient.createItem({
          title: params.title,
          description: params.description,
          dueDate: params.due_date,
          priority: params.priority,
        });

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
      } catch (error) {
        return {
          content: [{ type: "text", text: handleApiError(error) }],
          structuredContent: { error: true },
        };
      }
    }
  );
}
