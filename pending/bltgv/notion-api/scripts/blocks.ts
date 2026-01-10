#!/usr/bin/env bun
/**
 * Notion Blocks Script
 *
 * Read page content as blocks from Notion.
 *
 * Usage:
 *   bun run blocks.ts <command> [options]
 *
 * Commands:
 *   list      List child blocks of a page or block
 *   get       Get a specific block by ID
 *
 * Options:
 *   --id       Page or block ID (required)
 *   --top      Number of results (default: 50, max: 100)
 *   --recursive  Fetch child blocks recursively (default: false)
 *
 * Output:
 *   JSON with status field indicating success, auth_required, or error.
 */

import { parseArgs } from "util";
import { checkAuth, notionRequest, output, richTextToPlain } from "./lib/notion-client";
import type { NotionBlock, NotionBlockList, NotionRichText } from "./lib/types";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    id: { type: "string" },
    top: { type: "string", default: "50" },
    recursive: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
});

const command = positionals[0];

if (values.help) {
  console.log(`
Notion Blocks

Read page content as blocks from Notion.

Usage:
  bun run blocks.ts <command> [options]

Commands:
  list      List child blocks of a page or block
  get       Get a specific block by ID

Options:
  --id <id>        Page or block ID (required)
  --top <n>        Number of results (default: 50, max: 100)
  --recursive      Fetch child blocks recursively
  -h, --help       Show this help message

Environment:
  NOTION_TOKEN     Your Notion integration token (required)

Block Types:
  paragraph, heading_1, heading_2, heading_3, bulleted_list_item,
  numbered_list_item, to_do, toggle, code, quote, callout,
  divider, table, image, bookmark, and more.

Examples:
  bun run blocks.ts list --id abc123
  bun run blocks.ts list --id abc123 --recursive
  bun run blocks.ts get --id block456
`);
  process.exit(0);
}

interface FormattedBlock {
  id: string;
  type: string;
  hasChildren: boolean;
  content?: string;
  checked?: boolean;
  language?: string;
  url?: string;
  caption?: string;
  children?: FormattedBlock[];
}

function extractContent(block: NotionBlock): Partial<FormattedBlock> {
  const type = block.type;
  const blockData = block[type] as Record<string, unknown> | undefined;

  if (!blockData) {
    return {};
  }

  const result: Partial<FormattedBlock> = {};

  // Extract rich text content
  if ("rich_text" in blockData && Array.isArray(blockData.rich_text)) {
    result.content = richTextToPlain(blockData.rich_text as NotionRichText[]);
  }

  // Extract text content (used by some block types)
  if ("text" in blockData && Array.isArray(blockData.text)) {
    result.content = richTextToPlain(blockData.text as NotionRichText[]);
  }

  // Extract checked state for to_do
  if ("checked" in blockData && typeof blockData.checked === "boolean") {
    result.checked = blockData.checked;
  }

  // Extract language for code blocks
  if ("language" in blockData && typeof blockData.language === "string") {
    result.language = blockData.language;
  }

  // Extract URL for bookmarks, images, etc.
  if ("url" in blockData && typeof blockData.url === "string") {
    result.url = blockData.url;
  }

  // Handle file/image types
  if ("file" in blockData && typeof blockData.file === "object" && blockData.file !== null) {
    const file = blockData.file as { url?: string };
    if (file.url) {
      result.url = file.url;
    }
  }

  if ("external" in blockData && typeof blockData.external === "object" && blockData.external !== null) {
    const external = blockData.external as { url?: string };
    if (external.url) {
      result.url = external.url;
    }
  }

  // Extract caption
  if ("caption" in blockData && Array.isArray(blockData.caption)) {
    const caption = richTextToPlain(blockData.caption as NotionRichText[]);
    if (caption) {
      result.caption = caption;
    }
  }

  return result;
}

function formatBlock(block: NotionBlock, children?: FormattedBlock[]): FormattedBlock {
  const formatted: FormattedBlock = {
    id: block.id,
    type: block.type,
    hasChildren: block.has_children,
    ...extractContent(block),
  };

  if (children && children.length > 0) {
    formatted.children = children;
  }

  return formatted;
}

async function listBlocks(
  token: string,
  blockId: string,
  pageSize: number,
  recursive: boolean
): Promise<{ blocks: FormattedBlock[]; hasMore: boolean; nextCursor: string | null }> {
  const result = await notionRequest<NotionBlockList>(
    token,
    `/blocks/${blockId}/children?page_size=${pageSize}`
  );

  const blocks: FormattedBlock[] = [];

  for (const block of result.results) {
    let children: FormattedBlock[] | undefined;

    if (recursive && block.has_children) {
      const childResult = await listBlocks(token, block.id, pageSize, true);
      children = childResult.blocks;
    }

    blocks.push(formatBlock(block, children));
  }

  return {
    blocks,
    hasMore: result.has_more,
    nextCursor: result.next_cursor,
  };
}

async function getBlock(token: string, blockId: string): Promise<FormattedBlock> {
  const block = await notionRequest<NotionBlock>(token, `/blocks/${blockId}`);
  return formatBlock(block);
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

  const top = Math.min(parseInt(values.top!, 10) || 50, 100);

  try {
    switch (command) {
      case "list": {
        const result = await listBlocks(token, values.id, top, values.recursive!);
        output({
          status: "success",
          data: {
            blocks: result.blocks,
            hasMore: result.hasMore,
            nextCursor: result.nextCursor,
          },
        });
        break;
      }

      case "get": {
        const block = await getBlock(token, values.id);
        output({ status: "success", data: block });
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
