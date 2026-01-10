#!/usr/bin/env bun
/**
 * Notion Databases Script
 *
 * Query and get information about Notion databases.
 *
 * Usage:
 *   bun run databases.ts <command> [options]
 *
 * Commands:
 *   get       Get database schema/info by ID
 *   query     Query database pages with optional filters
 *
 * Options:
 *   --id       Database ID (required)
 *   --filter   JSON filter object (for query)
 *   --sorts    JSON array of sort objects (for query)
 *   --top      Number of results (default: 10, max: 100)
 *
 * Output:
 *   JSON with status field indicating success, auth_required, or error.
 */

import { parseArgs } from "util";
import { checkAuth, notionRequest, output, richTextToPlain, getPageTitle } from "./lib/notion-client";
import type { NotionDatabase, NotionDatabaseQueryResult, NotionPage, NotionFilter, NotionSort } from "./lib/types";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    id: { type: "string" },
    filter: { type: "string" },
    sorts: { type: "string" },
    top: { type: "string", default: "10" },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
});

const command = positionals[0];

if (values.help) {
  console.log(`
Notion Databases

Query and get information about Notion databases.

Usage:
  bun run databases.ts <command> [options]

Commands:
  get       Get database schema/info by ID
  query     Query database pages with optional filters

Options:
  --id <id>          Database ID (required)
  --filter <json>    JSON filter object (for query command)
  --sorts <json>     JSON array of sort objects (for query)
  --top <n>          Number of results (default: 10, max: 100)
  -h, --help         Show this help message

Environment:
  NOTION_TOKEN       Your Notion integration token (required)

Filter Examples:
  Single condition:
    --filter '{"property": "Status", "select": {"equals": "Done"}}'

  Multiple conditions (AND):
    --filter '{"and": [{"property": "Status", "select": {"equals": "Done"}}, {"property": "Priority", "select": {"equals": "High"}}]}'

Sort Examples:
  --sorts '[{"property": "Created", "direction": "descending"}]'
  --sorts '[{"timestamp": "last_edited_time", "direction": "descending"}]'

Examples:
  bun run databases.ts get --id abc123
  bun run databases.ts query --id abc123
  bun run databases.ts query --id abc123 --filter '{"property": "Status", "select": {"equals": "Done"}}'
  bun run databases.ts query --id abc123 --top 20 --sorts '[{"property": "Date", "direction": "descending"}]'
`);
  process.exit(0);
}

function formatDatabase(db: NotionDatabase) {
  return {
    id: db.id,
    title: richTextToPlain(db.title),
    description: richTextToPlain(db.description),
    url: db.url,
    createdTime: db.created_time,
    lastEditedTime: db.last_edited_time,
    archived: db.archived,
    isInline: db.is_inline,
    properties: Object.entries(db.properties).map(([name, prop]) => ({
      name,
      id: prop.id,
      type: prop.type,
    })),
  };
}

function formatQueryResult(page: NotionPage) {
  return {
    id: page.id,
    title: getPageTitle(page.properties),
    url: page.url,
    createdTime: page.created_time,
    lastEditedTime: page.last_edited_time,
    archived: page.archived,
    properties: page.properties,
  };
}

async function getDatabase(token: string, databaseId: string) {
  const db = await notionRequest<NotionDatabase>(token, `/databases/${databaseId}`);
  return formatDatabase(db);
}

async function queryDatabase(
  token: string,
  databaseId: string,
  options: {
    filter?: string;
    sorts?: string;
    pageSize: number;
  }
) {
  const body: {
    page_size: number;
    filter?: NotionFilter;
    sorts?: NotionSort[];
  } = {
    page_size: options.pageSize,
  };

  if (options.filter) {
    try {
      body.filter = JSON.parse(options.filter);
    } catch {
      throw new Error("Invalid JSON in --filter");
    }
  }

  if (options.sorts) {
    try {
      body.sorts = JSON.parse(options.sorts);
    } catch {
      throw new Error("Invalid JSON in --sorts");
    }
  }

  const result = await notionRequest<NotionDatabaseQueryResult>(
    token,
    `/databases/${databaseId}/query`,
    { method: "POST", body }
  );

  return {
    results: result.results.map(formatQueryResult),
    hasMore: result.has_more,
    nextCursor: result.next_cursor,
  };
}

async function main() {
  if (!command) {
    output({ status: "error", error: "No command specified. Use --help for usage." });
    return;
  }

  const auth = checkAuth();
  if (!auth.ok) {
    output(auth.response);
    return;
  }

  const token = auth.token;

  if (!values.id) {
    output({ status: "error", error: "--id is required" });
    return;
  }

  const top = Math.min(parseInt(values.top!, 10) || 10, 100);

  try {
    switch (command) {
      case "get": {
        const db = await getDatabase(token, values.id);
        output({ status: "success", data: db });
        break;
      }

      case "query": {
        const results = await queryDatabase(token, values.id, {
          filter: values.filter,
          sorts: values.sorts,
          pageSize: top,
        });
        output({ status: "success", data: results });
        break;
      }

      default:
        output({ status: "error", error: `Unknown command: ${command}. Use --help for usage.` });
    }
  } catch (error) {
    output({
      status: "error",
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
}

main();
