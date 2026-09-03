# SitemapKit MCP Server

Give AI agents a reliable XML sitemap crawler through the Model Context Protocol (MCP). [SitemapKit](https://sitemapkit.com) discovers sitemap files, parses nested sitemap indexes, and extracts deduplicated page URLs for SEO audits, content inventories, research, and agent workflows.

Works with MCP-compatible clients including Claude Desktop, Cursor, Windsurf, and other AI assistants that support local stdio servers.

## Tools

| Tool | Description |
|------|-------------|
| `discover_sitemaps` | Find all sitemap files for a domain (checks robots.txt, common paths, sitemap indexes) |
| `extract_sitemap` | Extract all URLs from a specific sitemap file |
| `full_crawl` | Discover + extract all URLs across all sitemaps in one call |

## Setup

### 1. Get an API key

Sign up at [sitemapkit.com](https://sitemapkit.com) and grab your API key from [app.sitemapkit.com/settings/api](https://app.sitemapkit.com/settings/api).

### 2. Configure your MCP client

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sitemapkit": {
      "command": "npx",
      "args": ["-y", "sitemapkit-mcp"],
      "env": {
        "SITEMAPKIT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Cursor

Add to `.cursor/mcp.json` in your project (or the global `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "sitemapkit": {
      "command": "npx",
      "args": ["-y", "sitemapkit-mcp"],
      "env": {
        "SITEMAPKIT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "sitemapkit": {
      "command": "npx",
      "args": ["-y", "sitemapkit-mcp"],
      "env": {
        "SITEMAPKIT_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Usage examples

Once configured, you can ask your AI assistant:

- *"Find all sitemaps for stripe.com"*
- *"Extract every URL from https://example.com/sitemap.xml"*
- *"Get the full URL list for shopify.com, up to 5000 URLs"*

## Continuous sitemap monitoring

This MCP server is designed for on-demand discovery and extraction. To watch a website continuously, detect newly published pages, and send signed webhook alerts, use [SitemapKit Monitoring](https://sitemapkit.com/sitemap-monitoring).

The free plan includes one daily monitor. Paid plans add more websites, higher URL limits, and checks as often as every hour. See the [webhook documentation](https://sitemapkit.com/sitemap-monitoring/webhooks) for payloads, signatures, and retry behavior.

## API limits

Limits depend on your [SitemapKit plan](https://sitemapkit.com/pricing). The `meta.quota` field in each response tells you how many requests you have remaining this month.

| Plan | API requests/month | URLs per extraction |
|------|-------------------:|--------------------:|
| Free | 100 | 1,000 |
| Starter | 5,000 | 10,000 |
| Pro | 50,000 | 50,000 |

See current API and monitoring allowances on the [pricing page](https://sitemapkit.com/pricing).

## License

MIT
