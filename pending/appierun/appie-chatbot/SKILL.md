---
name: appie-chatbot
description: Create, train, and chat with project chatbots via Appie.run. Use when the user asks to create a chatbot, add knowledge or training data, ask a bot a question, check training status, or list chatbots. Triggers include make a chatbot, train bot on this URL, add knowledge, ask the chatbot, chatbot status, list my bots.
license: MIT
---

# Appie Chatbot

## Overview

Create free project chatbots, add knowledge sources, wait for training, then converse.

- Creation and training-status checks are free.
- Each `ask_chatbot` message costs 1 credit.
- Never invent bot replies or training status — only return API results.

## Prerequisites (always run first)

This skill needs the Appie.run MCP server connected to your agent.

1. Check whether the Appie tools (e.g. `create_chatbot`, `ask_chatbot`) are already available. If they are, continue.
2. If not, ask the user to connect the Appie MCP server:
   - URL: `https://appie.run/mcp` (transport: streamable HTTP)
   - Header: `Authorization: Bearer <esk_...>` (your Appie.run project API key, starting with `esk_`)
   - Setup docs for each client: https://appie.run/docs/mcp
3. New Appie.run accounts get 500 free credits. Never ask the user to paste their key into chat, and never invent one.
   Stop and wait until the tools are available before continuing.

## Tool Reference

| Action              | Tool name                                              | Cost | Notes |
|---------------------|--------------------------------------------------------|------|-------|
| Create chatbot      | `create_chatbot`         | free | returns chatbot_id |
| List chatbots       | `list_chatbots`          | free | readiness flags |
| Add knowledge       | `add_chatbot_content`    | free | text / url / sitemap / article |
| Chatbot status      | `chatbot_status`         | free | poll until ready |
| Ask chatbot         | `ask_chatbot`            | 1    | session_id for continuity |
| Get brain           | `get_brain`              | free | optional brand context |

### create_chatbot parameters
- `name` (required)
- `system_prompt` (optional) — how the bot should answer
- `openai_model` (optional) — `"gpt-4o-mini"` | `"gpt-4o"` | `"gpt-3.5-turbo"`
- `temperature` (optional, 0–1, default 0.2)

### add_chatbot_content parameters
- `chatbot_id` (required)
- `content_type` (required) — `"text"` | `"url"` | `"sitemap"` | `"article"`
- For text: supply `title` + `content`
- For url or sitemap: supply `url` (crawled in background)
- For article: supply `article_id` (from Content Writer / appie-article-writer)

### ask_chatbot parameters
- `chatbot_id` (required)
- `message` (required)
- `session_id` (optional integer) — omit to start new conversation; reuse to continue

## Full Workflow

### 1. Discover or create a chatbot
1. Call list_chatbots to see existing bots and readiness.
2. If the user wants a new bot:
   - Call create_chatbot with a clear name.
   - Optionally set system_prompt (can be derived from get_brain brand voice if the user wants brand-aligned answers).
   - Capture the returned chatbot_id.
3. Tell the user the id and that creation was free.

### 2. Add knowledge sources
1. Call add_chatbot_content one or more times:
   - text — paste content directly
   - url / sitemap — supply the URL; crawling happens in the background
   - article — pass an article_id previously created with the article-writer skill
2. Multiple sources can be added sequentially.
3. After each add, inform the user that training has started (or is queued).

### 3. Wait for training (mandatory before asking)
1. Call chatbot_status with the chatbot_id.
2. Repeat until the response indicates knowledge is ready / training complete.
3. Do **not** call ask_chatbot while training is still running.
4. If the user asks a question early, check status first and tell them to wait if needed.

### 4. Converse
1. Call ask_chatbot with chatbot_id + message.
2. On first message of a conversation, omit session_id.
3. On subsequent messages in the same thread, reuse the returned session_id.
4. Each call costs 1 credit — mention this the first time or when the user may not expect it.
5. Return the exact reply from the API. Never invent or expand it.

### 5. Ongoing management
- Re-list chatbots when the user asks "what bots do I have?"
- Re-check status when the user asks whether a bot is ready.
- Add more knowledge at any time; re-poll status afterward.

## Error Handling & Edge Cases

- Training still running → tell the user, show current status, and refuse to ask questions yet.
- Bot has zero knowledge → refuse to answer and guide the user to add at least one source.
- Insufficient credits on ask → report the 1-credit cost and stop.
- Invalid content_type or missing required field (content / url / article_id) → surface the validation error and ask for the missing piece.
- Article_id from another project or non-existent → surface the error; offer to create a new article first via the article-writer skill.
- Multiple bots → list them with ids and readiness; ask which one to use if ambiguous.
- Session continuity lost → start a new session (omit session_id) and inform the user.
- Never invent replies, status, or knowledge sources.

## Cross-skill Integration

- When the user wants a chatbot trained on a freshly written article, create the article first (appie-article-writer), wait until it is ready, then pass its article_id to add_chatbot_content with content_type `"article"`.
- Brand voice from get_brain can be used to craft a good system_prompt.

## Response Style

- Always confirm the chatbot_id after creation.
- State when training is in progress vs ready.
- Mention the 1-credit cost on the first ask of a conversation.
- Preserve session_id silently for follow-ups unless the user starts a new topic.
- Keep answers focused on the bot's actual reply once conversation starts.