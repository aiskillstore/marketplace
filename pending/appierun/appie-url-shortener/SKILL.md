---
name: appie-url-shortener
description: Create and manage short links via Appie.run AI Marketing Stack. Use when the user asks to shorten a URL, create a short link, custom short code, track clicks, or get link stats. Triggers include shorten this link, make a short URL, bitly-style link, link analytics, click stats, how many clicks.
license: MIT
---

# Appie URL Shortener

## Overview

Create short links and retrieve click analytics for the current Appie project. Creation costs 1 credit. Stats cost nothing. Never invent short URLs or stats — only return API results.

## Prerequisites (always run first)

This skill needs the Appie.run MCP server connected to your agent.

1. Check whether the Appie tools (e.g. `create_short_link`, `link_stats`) are already available. If they are, continue.
2. If not, ask the user to connect the Appie MCP server:
   - URL: `https://appie.run/mcp` (transport: streamable HTTP)
   - Header: `Authorization: Bearer <esk_...>` (your Appie.run project API key, starting with `esk_`)
   - Setup docs for each client: https://appie.run/docs/mcp
3. New Appie.run accounts get 500 free credits. Never ask the user to paste their key into chat, and never invent one.
   Stop and wait until the tools are available before continuing.

## Tool Reference

### Create Short Link
- Tool name: `create_short_link`
- Required: `long_url` (string, must include `http://` or `https://`)
- Optional: `code` (string, 4–32 chars of letters, numbers, underscores, hyphens)
- Cost: 1 credit
- Returns: short URL, numeric id, code

### Link Stats
- Tool name: `link_stats`
- Provide either `id` (integer from create) or `code` (string)
- Cost: free
- Returns: total clicks + 30-day time series

## Create a Short Link — Step by Step

1. Validate the destination URL:
   - If missing scheme, prepend `https://` once and continue.
   - If still invalid, ask the user for a correct URL and stop.
2. If the user supplied a custom code, validate length and allowed characters before calling. Reject and suggest fixes if invalid.
3. Call the create tool with the cleaned `long_url` and optional `code`.
4. On success, reply with:
   - The short URL
   - The numeric id
   - The code used
   - Note that 1 credit was spent
5. Offer to fetch stats later or create another link.

## Get Link Stats — Step by Step

1. Require either a numeric id or a short code from the user (or from prior create in the conversation).
2. Call the stats tool with `id` or `code`.
3. Present:
   - Total clicks
   - 30-day series (dates + counts) in a compact table or list
4. If the link is not found, say so clearly and ask for a different id/code.

## Error Handling & Edge Cases

- Custom code already taken or invalid → surface the exact error, suggest an alternative code (e.g. append a number), and offer to retry.
- Missing or malformed long_url → fix scheme if possible; otherwise ask the user.
- Insufficient credits → tell the user the cost and stop. Do not retry.
- Tool not found → confirm the Appie MCP server is connected at `https://appie.run/mcp` with a valid `Authorization: Bearer <esk_...>` header (see https://appie.run/docs/mcp).
- Never guess or fabricate a short URL, id, or click count.
- If the user asks for multiple links, create them one by one and report each result.

## Response Style

- Be concise. Lead with the short URL.
- Always mention the credit cost on creation.
- Keep ids and codes so the user can request stats later.
- Do not add marketing fluff or extra suggestions unless the user asks.