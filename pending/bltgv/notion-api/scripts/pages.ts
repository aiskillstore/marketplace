#!/usr/bin/env bun
/**
 * Notion Pages Script
 *
 * Get, create, and update pages in Notion.
 *
 * Usage:
 *   bun run pages.ts <command> [options]
 *
 * Commands:
 *   get       Get a page by ID
 *   create    Create a new page
 *   update    Update page properties
 *
 * Options:
 *   --id          Page ID (required for get/update)
 *   --parent-id   Parent page or database ID (required for create)
 *   --parent-type Type of parent: page, database (default: page)
 *   --title       Page title (required for create, optional for update)
 *   --properties  JSON string of properties to set (for database pages)
 *   --icon        Emoji icon for the page (optional)
 *   --archived    Set to true to archive the page (for update)
 *
 * Output:
 *   JSON with status field indicating success, auth_required, or error.
 */

import { parseArgs } from "util";
import { checkAuth, notionRequest, output, getPageTitle } from "./lib/notion-client";
import type { NotionPage } from "./lib/types";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    id: { type: "string" },
    "parent-id": { type: "string" },
    "parent-type": { type: "string", default: "page" },
    title: { type: "string" },
    properties: { type: "string" },
    icon: { type: "string" },
    archived: { type: "string" },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
});

const command = positionals[0];

if (values.help) {
  console.log(`
Notion Pages

Get, create, and update pages in Notion.

Usage:
  bun run pages.ts <command> [options]

Commands:
  get       Get a page by ID
  create    Create a new page
  update    Update page properties

Options:
  --id <id>              Page ID (required for get/update)
  --parent-id <id>       Parent page or database ID (required for create)
  --parent-type <type>   Type of parent: page, database (default: page)
  --title <text>         Page title (required for create)
  --properties <json>    JSON string of properties (for database pages)
  --icon <emoji>         Emoji icon for the page
  --archived <bool>      Set to true to archive (for update)
  -h, --help             Show this help message

Environment:
  NOTION_TOKEN           Your Notion integration token (required)

Examples:
  bun run pages.ts get --id abc123
  bun run pages.ts create --parent-id xyz789 --title "New Page"
  bun run pages.ts create --parent-id db123 --parent-type database --title "New DB Entry"
  bun run pages.ts update --id abc123 --title "Updated Title"
  bun run pages.ts update --id abc123 --archived true
`);
  process.exit(0);
}

function formatPage(page: NotionPage) {
  const parentInfo = (() => {
    switch (page.parent.type) {
      case "database_id":
        return { type: "database", id: page.parent.database_id };
      case "page_id":
        return { type: "page", id: page.parent.page_id };
      case "workspace":
        return { type: "workspace" };
      default:
        return { type: "unknown" };
    }
  })();

  return {
    id: page.id,
    title: getPageTitle(page.properties),
    url: page.url,
    createdTime: page.created_time,
    lastEditedTime: page.last_edited_time,
    archived: page.archived,
    inTrash: page.in_trash,
    parent: parentInfo,
    icon: page.icon,
    cover: page.cover,
    properties: page.properties,
  };
}

async function getPage(token: string, pageId: string) {
  const page = await notionRequest<NotionPage>(token, `/pages/${pageId}`);
  return formatPage(page);
}

async function createPage(
  token: string,
  options: {
    parentId: string;
    parentType: string;
    title: string;
    properties?: string;
    icon?: string;
  }
) {
  const { parentId, parentType, title, properties, icon } = options;

  // Build parent object
  const parent =
    parentType === "database"
      ? { database_id: parentId }
      : { page_id: parentId };

  // Build properties
  let pageProperties: Record<string, unknown>;

  if (parentType === "database" && properties) {
    // For database pages, use provided properties and add title
    try {
      pageProperties = JSON.parse(properties);
      // Ensure title is set if not in properties
      if (!pageProperties.title && !pageProperties.Name) {
        pageProperties.title = {
          title: [{ text: { content: title } }],
        };
      }
    } catch {
      throw new Error("Invalid JSON in --properties");
    }
  } else {
    // For regular pages, just set title
    pageProperties = {
      title: {
        title: [{ text: { content: title } }],
      },
    };
  }

  const body: {
    parent: { database_id: string } | { page_id: string };
    properties: Record<string, unknown>;
    icon?: { type: "emoji"; emoji: string };
  } = {
    parent,
    properties: pageProperties,
  };

  if (icon) {
    body.icon = { type: "emoji", emoji: icon };
  }

  const page = await notionRequest<NotionPage>(token, "/pages", {
    method: "POST",
    body,
  });

  return formatPage(page);
}

async function updatePage(
  token: string,
  pageId: string,
  options: {
    title?: string;
    properties?: string;
    icon?: string;
    archived?: string;
  }
) {
  const body: {
    properties?: Record<string, unknown>;
    icon?: { type: "emoji"; emoji: string };
    archived?: boolean;
  } = {};

  if (options.title) {
    body.properties = {
      title: {
        title: [{ text: { content: options.title } }],
      },
    };
  }

  if (options.properties) {
    try {
      const props = JSON.parse(options.properties);
      body.properties = { ...body.properties, ...props };
    } catch {
      throw new Error("Invalid JSON in --properties");
    }
  }

  if (options.icon) {
    body.icon = { type: "emoji", emoji: options.icon };
  }

  if (options.archived === "true") {
    body.archived = true;
  } else if (options.archived === "false") {
    body.archived = false;
  }

  const page = await notionRequest<NotionPage>(token, `/pages/${pageId}`, {
    method: "PATCH",
    body,
  });

  return formatPage(page);
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

  try {
    switch (command) {
      case "get": {
        if (!values.id) {
          output({ status: "error", error: "--id is required for 'get' command" });
          return;
        }
        const page = await getPage(token, values.id);
        output({ status: "success", data: page });
        break;
      }

      case "create": {
        if (!values["parent-id"]) {
          output({ status: "error", error: "--parent-id is required for 'create' command" });
          return;
        }
        if (!values.title) {
          output({ status: "error", error: "--title is required for 'create' command" });
          return;
        }
        const page = await createPage(token, {
          parentId: values["parent-id"],
          parentType: values["parent-type"]!,
          title: values.title,
          properties: values.properties,
          icon: values.icon,
        });
        output({ status: "success", data: page });
        break;
      }

      case "update": {
        if (!values.id) {
          output({ status: "error", error: "--id is required for 'update' command" });
          return;
        }
        const page = await updatePage(token, values.id, {
          title: values.title,
          properties: values.properties,
          icon: values.icon,
          archived: values.archived,
        });
        output({ status: "success", data: page });
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
