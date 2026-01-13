/**
 * Tool Registration
 *
 * Export and register all tools for the MCP server.
 * Add new tools here as you create them.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerGetItems } from "./get-items.js";
import { registerCreateItem } from "./create-item.js";

interface Config {
  name: string;
  version: string;
  apiBaseUrl: string;
}

export function registerTools(server: McpServer, config: Config): void {
  // Register read-only tools
  registerGetItems(server, config);

  // Register write tools
  registerCreateItem(server, config);

  // Add more tools here:
  // registerUpdateItem(server, config);
  // registerDeleteItem(server, config);
}
