---
name: appie-article-writer
description: Write short light articles or long deeply-researched articles with Appie.run Content Writer. Use when the user asks to write an article, generate a blog post, create deeply researched content, draft in an author voice, or check article status. Triggers include write a short article, deeply researched piece, blog post about, generate content in my voice, article status.
license: MIT
---

# Appie Article Writer

## Overview

Generate articles in a chosen author voice via Appie.run Content Writer.

- **light** — ~500 words, 100 credits
- **deeply_researched** — ~3000 words, 500 credits

Generation is asynchronous. Always poll status. Never invent article content — only return what the API provides.

## Prerequisites (always run first)

This skill needs the Appie.run MCP server connected to your agent.

1. Check whether the Appie tools (e.g. `create_article`, `list_authors`) are already available. If they are, continue.
2. If not, ask the user to connect the Appie MCP server:
   - URL: `https://appie.run/mcp` (transport: streamable HTTP)
   - Header: `Authorization: Bearer <esk_...>` (your Appie.run project API key, starting with `esk_`)
   - Setup docs for each client: https://appie.run/docs/mcp
3. New Appie.run accounts get 500 free credits. Never ask the user to paste their key into chat, and never invent one.
   Stop and wait until the tools are available before continuing.

## Tool Reference

| Action              | Tool name                                              | Cost     | Notes |
|---------------------|--------------------------------------------------------|----------|-------|
| List authors        | `list_authors`           | free     | Check readiness |
| Create author       | `create_author`          | free     | bio ≥50 chars |
| Add author sample   | `add_author_sample`      | free     | content ≥100 chars or blog_url |
| Create article      | `create_article`         | 100 / 500| charged on generation |
| Article status      | `article_status`         | free     | poll until ready |
| Get brain           | `get_brain`              | free     | brand context (auto-used) |
| Update brain        | `update_brain`           | free     | only if user asks |

### create_article parameters
> Note: `create_article` fails with `author_profile_required` until an author exists. Create one with `create_author` first (or check with `list_authors`).

- `topic` (required) — clear description of the article subject
- `article_type` — `"light"` (default) or `"deeply_researched"`
- `author_id` (optional integer) — omit to use the project's active author

### create_author parameters
- `author_name` (required)
- `bio` (required, ≥50 characters)
- `is_active` (optional boolean, default true)
- `sample_title` / `sample_content` (optional, sample_content ≥100 chars)

## Full Workflow

### 1. Clarify type and topic
- If the user says only "write an article", ask whether they want **light** (~500 words, 100 credits) or **deeply_researched** (~3000 words, 500 credits).
- Confirm the exact topic if ambiguous.

### 2. Ensure a usable author
1. Call list_authors.
2. Prefer an author marked ready / active.
3. If none exist or the desired voice is missing:
   - Create one with create_author (bio ≥50 chars).
   - Optionally add a writing sample (≥100 chars) via add_author_sample so the voice is stronger.
4. If an author exists but is not ready, add a sample and re-check.

### 3. Start generation
1. Call create_article with topic, chosen article_type, and optional author_id.
2. Immediately tell the user:
   - The article id
   - Expected cost
   - That generation is running in the background
3. Capture the returned id for polling.

### 4. Poll until ready
1. Call article_status with the id.
2. Repeat every few turns or when the user asks "is it ready?" until content appears or status is failed/complete.
3. On success, return the full article text, title (if provided), id, and type.
4. On failure, surface the exact error message and stop.

### 5. Optional Brain context
- Call get_brain if the user wants to inspect brand voice, ICP, competitors, or key messages.
- Only call update_brain when the user explicitly requests brand or ICP changes.
- Content Writer already uses Brain context automatically; you do not need to inject it.

## Error Handling & Edge Cases

- `create_article` fails with `author_profile_required` until the project has an author → check with `list_authors`, create one with `create_author` (bio ≥50 chars), then retry.
- Author not ready → add sample (≥100 chars) then retry create_article.
- Insufficient credits → report the exact cost (100 or 500) and stop. Do not start generation.
- Ambiguous topic → ask one clarifying question before calling create_article.
- Multiple authors → list them and let the user choose, or use the active one if the user does not care.
- Generation stuck / failed → show the status payload and offer to start a new article with a refined topic.
- Never invent or paraphrase the article body. Quote or present the exact content returned by article_status.
- If the user later wants the same article fed into a chatbot, note the article_id for the appie-chatbot skill.

## Response Style

- State cost and async nature up front.
- After creation, give the id and offer to check status.
- When ready, deliver the full content cleanly (preserve headings and structure).
- Keep follow-up questions minimal and focused.