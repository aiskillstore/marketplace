#!/usr/bin/env bun
/**
 * Notion Search Script
 *
 * Search pages and databases across your Notion workspace.
 *
 * Usage:
 *   bun run search.ts [options]
 *
 * Options:
 *   --query      Search query text (optional, returns all if omitted)
 *   --filter     Filter by object type: page, database (optional)
 *   --top        Number of results (default: 10, max: 100)
 *
 * Output:
 *   JSON with status field indicating success, auth_required, or error.
 */

import { parseArgs } from "util";
import { checkAuth, notionRequest, output, richTextToPlain, getPageTitle } from "./lib/notion-client";
import type { NotionSearchResult, NotionPage, NotionDatabase } from "./lib/types";

const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    query: { type: "string" },
    filter: { type: "string" },
    top: { type: "string", default: "10" },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: false,
});

if (values.help) {
  console.log(`
Notion Search

Search pages and databases across your Notion workspace.

Usage:
  bun run search.ts [options]

Options:
  --query <text>     Search query (optional, returns all if omitted)
  --filter <type>    Filter by type: page, database (optional)
  --top <n>          Number of results (default: 10, max: 100)
  -h, --help         Show this help message

Environment:
  NOTION_TOKEN       Your Notion integration token (required)

Examples:
  bun run search.ts --query "meeting notes"
  bun run search.ts --filter database --top 5
  bun run search.ts --query "project" --filter page
`);
  process.exit(0);
}

function formatPage(page: NotionPage) {
  return {
    id: page.id,
    type: "page",
    title: getPageTitle(page.properties),
    url: page.url,
    lastEdited: page.last_edited_time,
    archived: page.archived,
  };
}

function formatDatabase(db: NotionDatabase) {
  return {
    id: db.id,
    type: "database",
    title: richTextToPlain(db.title),
    description: richTextToPlain(db.description),
    url: db.url,
    lastEdited: db.last_edited_time,
    archived: db.archived,
    propertyCount: Object.keys(db.properties).length,
  };
}

async function main() {
  const auth = checkAuth();
  if (!auth.ok) {
    output(auth.response);
    return;
  }

  const token = auth.token;
  const top = Math.min(parseInt(values.top!, 10) || 10, 100);

  // Build request body
  const body: {
    query?: string;
    filter?: { value: "page" | "database"; property: "object" };
    page_size: number;
  } = {
    page_size: top,
  };

  if (values.query) {
    body.query = values.query;
  }

  if (values.filter === "page" || values.filter === "database") {
    body.filter = {
      value: values.filter,
      property: "object",
    };
  }

  try {
    const result = await notionRequest<NotionSearchResult>(token, "/search", {
      method: "POST",
      body,
    });

    const formattedResults = result.results.map((item) => {
      if (item.object === "page") {
        return formatPage(item as NotionPage);
      } else {
        return formatDatabase(item as NotionDatabase);
      }
    });

    output({
      status: "success",
      data: {
        results: formattedResults,
        hasMore: result.has_more,
        nextCursor: result.next_cursor,
      },
    });
  } catch (error) {
    output({
      status: "error",
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
}

main();
