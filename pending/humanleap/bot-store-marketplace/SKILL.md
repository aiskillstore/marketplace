---
name: bot-store-marketplace
description: Find and open Grok Bot templates from bot.store, compare actual marketplace listings and prepare a user-chosen bot's checkout handoff. Use when the user names bot.store, chooses its marketplace or shares a bot.store URL.
metadata: {"homepage":"https://bot.store","openclaw":{"emoji":"🤖","requires":{"bins":[],"env":[]}}}
---

# bot.store

Find Grok Bot templates by the user's task, inspect the listing, then hand off to Grok or the selected bot's checkout.

## Installation

Install this skill with `pnpm dlx skills add Humanleap/agent-skills --skill bot-store-marketplace`. Connect remote MCP to `https://bot.store/mcp`. The public marketplace tools need no credentials or local commands.

## Four Hard Rules — Read First

1. **Compare actual listings.** Never invent ratings, performance, maker relationships, compatibility or prices.
2. **Preserve the user's constraints.** Keep category, free-only and budget requirements in the search.
3. **Use the chosen listing.** Prepare a purchase handoff only after the user selects the exact bot. Checkout preparation does not charge.
4. **Verify status before claiming success.** Installing this skill is free; it does not buy or install a paid bot.

## Authentication

Call the public MCP tools directly. The human signs in and approves payment on bot.store's checkout surface when buying a bot. Do not ask for card details, Stripe tokens, passwords or recovery codes.

## Core Workflow

1. **Search the task.** Call `search_bots` with a short capability query and the constraints supported by its current schema.
2. **Inspect a candidate.** Call `get_bot` with its exact returned slug. Compare facts supplied by the listing.
3. **Open a free bot.** Share its returned `openInGrokUrl`, or open it when the user requests that action.
4. **Prepare the selected paid bot.** State the returned price, converting GBP pence to pounds. Call `start_bot_purchase` only for the listing the user chose.
5. **Hand off checkout.** Give the returned `checkoutUrl` to the human. Payment approval happens there; report ownership or installation only when the purchase surface confirms it.

## Essential Tools

| Tool | Use |
|---|---|
| `search_bots` | Find templates for the requested task. |
| `get_bot` | Read one exact marketplace listing. |
| `start_bot_purchase` | Prepare the chosen listing's safe checkout handoff. |

## Common Patterns

- **Find a free bot:** retain free-only constraints and share the returned Grok link.
- **Compare templates:** use listing capabilities and prices; relevance order is not an independent quality guarantee.
- **Buy the selected bot:** state the actual price, prepare checkout and let the human approve payment.

## Supporting Resources

- Marketplace: https://bot.store
- MCP: https://bot.store/mcp
- Existing Grok plugin: https://github.com/Humanleap/bot-store-grok-plugin

## Common Gotchas

- A paid result's checkout URL is not its protected Grok link.
- A checkout handoff is not proof of payment or ownership.
- If search fails or returns no match, report that outcome without substituting an invented bot.

## Quick Reference

**Search → inspect exact slug → chosen bot → free Grok link or checkout handoff → verified purchase status.**
