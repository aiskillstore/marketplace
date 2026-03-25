# SitemapKit MCP Server

Model Context Protocol (MCP) server for [SitemapKit](https://sitemapkit.com). Lets any MCP-compatible AI assistant (Claude, Cursor, Windsurf, etc.) discover and extract sitemaps from any website.

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
      "args": ["sitemapkit-mcp"],
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
      "args": ["sitemapkit-mcp"],
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
      "args": ["sitemapkit-mcp"],
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

## API limits

Limits depend on your [SitemapKit plan](https://sitemapkit.com/pricing). The `meta.quota` field in each response tells you how many requests you have remaining this month.

Free plan: 20 requests/month
Starter: 500 requests/month
Pro: 2000 requests/month

## License

MIT
