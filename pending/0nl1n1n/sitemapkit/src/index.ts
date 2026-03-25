#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";

const API_BASE = "https://app.sitemapkit.com/api/v1/sitemap";

function getApiKey(): string {
  const key = process.env.SITEMAPKIT_API_KEY;
  if (!key) {
    throw new Error(
      "SITEMAPKIT_API_KEY environment variable is not set. " +
      "Get your API key at https://app.sitemapkit.com/settings/api"
    );
  }
  return key;
}

async function callApi<T>(
  endpoint: string,
  body: Record<string, unknown>
): Promise<{ data: T; meta: Record<string, unknown> }> {
  const apiKey = getApiKey();

  const res = await fetch(`${API_BASE}/${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(body),
  });

  const json = await res.json() as Record<string, unknown>;

  if (!res.ok) {
    const error = json.error as string ?? "Unknown error";
    const message = json.message as string | undefined;
    const upgrade = json.upgrade as string | undefined;

    let msg = `SitemapKit API error (${res.status}): ${error}`;
    if (message) msg += `\n${message}`;
    if (upgrade) msg += `\nUpgrade at: ${upgrade}`;

    throw new Error(msg);
  }

  return { data: json.data as T, meta: json.meta as Record<string, unknown> };
}

type SitemapEntry = {
  loc: string;
  lastmod?: string;
  changefreq?: string;
  priority?: string;
};

type DiscoverResult = {
  domain: string;
  sitemaps: string[];
  source: string[];
};

type ExtractResult = {
  sitemapUrl: string;
  urls: SitemapEntry[];
  totalUrls: number;
  sitemapsProcessed: number;
  truncated: boolean;
};

type FullResult = {
  domain: string;
  sitemapsDiscovered: number;
  sitemapsProcessed: number;
  urls: SitemapEntry[];
  totalUrls: number;
  truncated: boolean;
  sources: string[];
};

const TOOLS: Tool[] = [
  {
    name: "discover_sitemaps",
    description:
      "Find all sitemap files for a given domain by checking robots.txt, common paths, and sitemap indexes. " +
      "Returns a list of sitemap URLs. Use this first to understand a site's sitemap structure.",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description:
            "The domain to check, e.g. 'https://example.com'. Only the domain is used — path is ignored.",
        },
      },
      required: ["url"],
    },
  },
  {
    name: "extract_sitemap",
    description:
      "Extract all URLs from a specific sitemap file (including sitemap indexes that link to child sitemaps). " +
      "Returns URL entries with optional lastmod, changefreq, and priority metadata.",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "The full URL of the sitemap file, e.g. 'https://example.com/sitemap.xml'.",
        },
        max_urls: {
          type: "number",
          description: "Maximum number of URLs to return. Defaults to 1000. Max allowed by your plan.",
          default: 1000,
        },
      },
      required: ["url"],
    },
  },
  {
    name: "full_crawl",
    description:
      "Discover all sitemaps for a domain and extract every URL across all of them in one call. " +
      "This is the most convenient tool when you want the complete URL list for a site. " +
      "Returns deduplicated URLs with metadata.",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "The domain to crawl, e.g. 'https://example.com'.",
        },
        max_urls: {
          type: "number",
          description: "Maximum number of URLs to return. Defaults to 1000. Max allowed by your plan.",
          default: 1000,
        },
      },
      required: ["url"],
    },
  },
];

const server = new Server(
  { name: "sitemapkit-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "discover_sitemaps") {
      const url = args?.url as string;
      const { data, meta } = await callApi<DiscoverResult>("discover", { url });

      const quota = meta?.quota as { remaining: number; limit: number } | undefined;
      let text = `Found ${data.sitemaps.length} sitemap(s) for ${data.domain}\n`;
      text += `Discovery methods: ${data.source.join(", ")}\n\n`;
      text += data.sitemaps.map((s) => `• ${s}`).join("\n");
      if (quota) text += `\n\nQuota: ${quota.remaining} requests remaining this month`;

      return { content: [{ type: "text", text }] };
    }

    if (name === "extract_sitemap") {
      const url = args?.url as string;
      const maxUrls = (args?.max_urls as number | undefined) ?? 1000;
      const { data, meta } = await callApi<ExtractResult>("extract", { url, maxUrls });

      const quota = meta?.quota as { remaining: number; limit: number } | undefined;
      let text = `Extracted ${data.totalUrls} URL(s) from ${data.sitemapUrl}\n`;
      text += `Sitemaps processed: ${data.sitemapsProcessed}`;
      if (data.truncated) text += ` (truncated at ${maxUrls})`;
      text += "\n\n";
      text += data.urls.map((u) => {
        let line = u.loc;
        if (u.lastmod) line += ` [lastmod: ${u.lastmod}]`;
        return line;
      }).join("\n");
      if (quota) text += `\n\nQuota: ${quota.remaining} requests remaining this month`;

      return { content: [{ type: "text", text }] };
    }

    if (name === "full_crawl") {
      const url = args?.url as string;
      const maxUrls = (args?.max_urls as number | undefined) ?? 1000;
      const { data, meta } = await callApi<FullResult>("full", { url, maxUrls });

      const quota = meta?.quota as { remaining: number; limit: number } | undefined;
      let text = `Full crawl of ${data.domain}\n`;
      text += `Sitemaps discovered: ${data.sitemapsDiscovered} | Processed: ${data.sitemapsProcessed}\n`;
      text += `Total URLs: ${data.totalUrls}`;
      if (data.truncated) text += ` (truncated at ${maxUrls})`;
      text += "\n\n";
      text += data.urls.map((u) => {
        let line = u.loc;
        if (u.lastmod) line += ` [lastmod: ${u.lastmod}]`;
        return line;
      }).join("\n");
      if (quota) text += `\n\nQuota: ${quota.remaining} requests remaining this month`;

      return { content: [{ type: "text", text }] };
    }

    return {
      content: [{ type: "text", text: `Unknown tool: ${name}` }],
      isError: true,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: message }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
