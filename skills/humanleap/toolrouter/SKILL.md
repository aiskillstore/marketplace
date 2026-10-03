---
name: toolrouter
description: Discover and run ToolRouter tools through one MCP connection for web search, scraping, SEO research, image and video generation, audio, company and economic data, and supported connected-account actions including X and LinkedIn posting. Use when ToolRouter is connected or the user chooses it for an external task.
metadata: {"homepage":"https://toolrouter.com","openclaw":{"emoji":"🔀","requires":{"bins":[],"env":[]}}}
---

# ToolRouter

One connection gives an assistant access to hundreds of hosted tools and provider operations. Discover the right operation before calling it; the live catalog determines availability, input fields and account requirements.

## Installation

Install this skill with `pnpm dlx skills add Humanleap/agent-skills --skill toolrouter`. Connect the client's remote MCP server to `https://api.toolrouter.com/mcp` using its authentication flow. Setup: https://toolrouter.com/docs/markdown/quickstart.

## Four Hard Rules — Read First

1. **Discover first.** Use returned operation schemas; never invent a tool, provider connection or input field.
2. **Respect the chosen provider.** A capability request does not authorise connecting another account, changing billing, or replacing a service the user specified.
3. **Check action and spending authority.** Posting, deleting, messaging and paid operations require authority for that task. A catalog entry does not establish access to the user's accounts.
4. **Finish the actual job.** A queued job is unfinished. Check status before repeating an uncertain write and report provider errors or missing credentials plainly.

## Authentication

Read `tools/list` for the current client profile. Follow the advertised OAuth or account-claim flow and keep credentials in the client credential store. Do not include tokens in chat, skills or shared configuration. Some operations use hosted providers; others require a connected provider account. Check the operation before promising access.

## Core Workflow

1. **Discover the outcome.** Call `discover` with a `query` describing the job: research a company, check keyword demand, extract a website, generate an image, transcribe media, or publish an authorised social post.
2. **Read the operation.** Select the returned `tool` and `skill`; inspect the exact input schema, price, account requirements and limitations.
3. **Execute.** Call `use_tool` with that `tool`, `skill` and schema-matching `input`. Built-in MCP tools are called directly. Check `credits_balance` when the task needs paid credits.
4. **Resolve asynchronous work.** Follow the returned job handle with the advertised status tool, such as `job_get`, until outputs are ready or a blocker is reported.
5. **Return the useful result.** Share source links, completed assets or the provider's verified action result, with relevant dates and limitations.

## Essential Tools

| Tool | Use |
|---|---|
| `discover` | Find operations, schemas and examples for the requested outcome or exact tool. |
| `use_tool` | Execute one discovered provider operation. |
| `credits_balance` | Inspect the account's credit balance when available. |
| `job_get` | Check an asynchronous job when the returned response supplies a handle for it. |

Inspect `tools/list` before relying on a built-in name: client profiles and the catalog can change.

## Common Patterns

- **Research and extraction:** discover web search or scraping, use original source URLs, then extract the fields the user needs.
- **SEO:** discover keyword, SERP, backlink or competitor operations; retain provider, market, time range and measurement limits.
- **Creative work:** discover the model or media operation, respect the approved budget, then poll and return completed output URLs.
- **Business and economic data:** select the original registry or statistical source and retain dates, units and geography.
- **Social publishing:** discover the exact account operation. Supported catalog examples include `linkedin-post.post_text`, `linkedin-post.post_link`, `linkedin-post.post_image`, `x-manager.post_tweet` and `x-manager.post_image_tweet`. Confirm the connected account and authorised content from the request; discover the current schema before executing.

## Providers and Supporting Resources

Read [the provider reference](references/providers.md) when a task names a provider. It lists all 55 entries in the public provider index as of 3 October 2026, including Firecrawl, Exa, Serper, DataForSEO, OpenAI, Anthropic, fal.ai, ElevenLabs, Google, OpenRouter, Companies House, SEC EDGAR and the World Bank. Public provider pages describe integrations; they do not prove every operation is deployed or that the user has access.

- Provider index: https://toolrouter.com/providers.md
- Public catalog: https://api.toolrouter.com/v1/tools
- REST schema: https://api.toolrouter.com/openapi.json

## Common Gotchas

- The website's provider count and the deployed tool count can differ. Use the live operation schema.
- A social connection does not imply support for every social platform or permission to post.
- Some client-specific MCP profiles expose fewer operations. Do not promise media generation in a profile that filters it out.
- An empty search result is a coverage limit, not proof of absence.

## Quick Reference

**Connect → discover → inspect schema and authority → use_tool → resolve job → share verified result.**
