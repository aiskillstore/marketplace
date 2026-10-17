---
name: appie-reddit-marketing
description: Find Reddit threads that mention your keywords or competitors and draft replies via Appie.run. Use when the user asks to monitor Reddit, set Reddit keywords or competitors, list Reddit mentions or threads, or write a reply for a Reddit thread. Triggers include watch Reddit for, Reddit keywords, Reddit mentions, find Reddit threads, draft a Reddit reply, Reddit competitors.
license: MIT
---

# Appie Reddit Marketing

## Overview

Save Reddit keywords, competitors and reply guidance for the current Appie project, list the Reddit threads that match them, and draft replies the user posts themselves.

- Reading and updating settings is free.
- Listing mentions is free; a scan runs at most once per day and costs 10 credits.
- Each `draft_reddit_reply` costs 2 credits.
- Appie drafts replies but never posts to Reddit. The user pastes the reply on the thread themselves.
- Never invent threads, mentions or reply drafts — only return API results.

## Prerequisites (always run first)

This skill needs the Appie.run MCP server connected to your agent.

1. Check whether the Appie tools (e.g. `list_reddit_mentions`, `draft_reddit_reply`) are already available. If they are, continue.
2. If not, ask the user to connect the Appie MCP server:
   - URL: `https://appie.run/mcp` (transport: streamable HTTP)
   - Header: `Authorization: Bearer <esk_...>` (your Appie.run project API key, starting with `esk_`)
   - Setup docs for each client: https://appie.run/docs/mcp
3. New Appie.run accounts get 500 free credits. Never ask the user to paste their key into chat, and never invent one.
   Stop and wait until the tools are available before continuing.

## Tool Reference

| Action              | Tool name                  | Cost | Notes |
|---------------------|----------------------------|------|-------|
| Read settings       | `get_reddit_settings`      | free | seeded from the Brain if nothing is saved yet |
| Update settings     | `update_reddit_settings`   | free | send only the fields to change |
| List mentions       | `list_reddit_mentions`     | free to list; scan 10 | scan runs at most once per day |
| Draft reply         | `draft_reddit_reply`       | 2    | user posts it themselves |
| Get brain           | `get_brain`                | free | optional brand context |

### update_reddit_settings parameters
- `keywords` (optional list, up to 25 items)
- `competitors` (optional list, up to 25 items)
- `custom_prompt` (optional) — reply guidance
- Send only the fields to change.

### list_reddit_mentions parameters
- `limit` (optional, default 20, maximum 50)
- Returns threads for the saved keywords and competitors, each with its latest reply draft, plus `credits_remaining`.
- If the balance is too low for a scan, `scan_skipped` is true and `message` says no scan ran.

### draft_reddit_reply parameters
- `mention_id` (required, from `list_reddit_mentions`)
- Returns `content` (the reply) and `source_url` (the thread to paste it on).

## Full Workflow

### 1. Check or set up what to watch
1. Call get_reddit_settings to read the saved keywords, competitors and reply guidance.
2. If nothing was saved yet and the project Brain has a website, about text, key messages or competitors, those are saved as the Reddit settings and returned. Show them to the user.
3. If the user wants changes, call update_reddit_settings with only the fields to change (each list holds up to 25 items).

### 2. List matching threads
1. Call list_reddit_mentions, optionally with a `limit`.
2. Mention that a scan runs at most once per day and costs 10 credits.
3. If `scan_skipped` is true, tell the user no scan ran and show the `message`.
4. Present each thread with its title or link and whether it already has a reply draft.

### 3. Draft a reply
1. Ask which thread to reply to if it's not clear, and get its `mention_id`.
2. Call draft_reddit_reply with the `mention_id` (2 credits).
3. Return the exact `content` and the `source_url`.
4. Tell the user to paste the reply on that thread themselves. Appie does not post to Reddit, and neither should you.

## Error Handling & Edge Cases

- No keywords or competitors saved → offer to set them with update_reddit_settings before listing.
- More than 25 items in a list → ask the user which to keep.
- `scan_skipped` true or `insufficient_credits` → report the cost (10 credits per scan, 2 per draft) and stop. Do not retry.
- Unknown `mention_id` → surface the error and re-list mentions.
- `app_not_allowed` → the key's owner can't use the Reddit app; ask a project owner or admin.
- Never invent threads, drafts or credit balances, and never claim a reply was posted.

## Cross-skill Integration

- Brand context from get_brain seeds the Reddit settings when none are saved, and can help the user write a good `custom_prompt`.
- A useful thread can become an article topic for appie-article-writer, or a short link to share via appie-url-shortener.

## Response Style

- Lead with the threads or the drafted reply.
- Mention credit costs before a scan or draft the first time.
- Always include the `source_url` with a draft and remind the user they post it themselves.
- Keep drafts exactly as returned unless the user asks you to edit them.
