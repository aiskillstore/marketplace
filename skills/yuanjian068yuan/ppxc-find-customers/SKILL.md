---
name: ppxc-find-customers
description: Use this skill when the user wants to find customer leads from short-video comments, generate customer-discovery keywords, review lead intent, query a customer pool, or prepare outreach scripts with PPXC.
---

# PPXC Find Customers

Use this skill when the user wants to find customers, discover leads, analyze short-video comments, generate search keywords, review a customer pool, or prepare outreach scripts with PPXC.

## Trigger Phrases

- find customer leads
- find buyers for my product
- discover customers from comments
- analyze short-video comments
- generate customer-search keywords
- build a lead list
- review my customer pool
- write outreach scripts

## Workflow

1. Check PPXC connection status.
2. Ask the user to connect PPXC if the account is not ready.
3. List products and choose the right product or offer.
4. Generate customer-discovery keywords.
5. Search comments for buying signals.
6. Query the customer pool and rank lead intent.
7. Prepare outreach scripts and next-step actions.
8. Export diagnostics when the user needs support or verification.

## MCP Install

```json
{
  "mcpServers": {
    "ppxc-find-customers": {
      "command": "npx",
      "args": ["-y", "ppxc-leads-mcp"]
    }
  }
}
```

## Recommended First Message

```text
Find customer leads for my product.
```

## Tool Guidance

- Start with `check_status_and_login` to confirm the account is ready.
- Use `list_products` before searching so results match the right offer.
- Use `suggest_search_keywords` to build search angles.
- Use `search_keyword_for_leads` or `analyze_video_comments` to collect customer signals.
- Use `query_leads` to review saved leads and buying intent.
- Use `export_diagnostics` if the user needs a support package.

## Positioning

PPXC Find Customers is for marketing and sales discovery. It turns real comment intent into lead lists, customer signals, and outreach-ready actions.

## Official Setup

https://opc1.me/download/mcp
