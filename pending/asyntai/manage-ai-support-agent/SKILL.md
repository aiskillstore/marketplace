---
name: manage-ai-support-agent
description: Set up and manage an Asyntai AI customer support agent (website chatbot) through the Asyntai MCP server - add knowledge, edit the agent's instructions, change the widget look, read conversations, leads and analytics, find topics that need more knowledge, and reply live to visitors. Use when the user wants to train, configure, review or run their Asyntai chatbot, or when the asyntai MCP server needs to be connected.
---

# Manage an Asyntai AI support agent

[Asyntai](https://asyntai.com) puts an AI support agent on the user's website.
The hosted Asyntai MCP server gives you the same controls as the Asyntai
dashboard.

## Connect the MCP server (one time)

Check first: if tools such as `list_websites` are already available, skip this
section.

The server is `https://asyntai.com/mcp` (remote, Streamable HTTP, OAuth
sign-in). No API key is needed. Any Asyntai account works, including the Free
plan.

- **Claude Code**: run `claude mcp add --transport http asyntai https://asyntai.com/mcp`,
  then run `/mcp`, choose `asyntai` and pick **Authenticate**.
- **Kiro**: the Asyntai power already includes the server. On the first
  connection Kiro opens the Asyntai sign-in page in the browser.
- **GitHub Copilot CLI**: the Asyntai plugin (`copilot plugin install
  asyntai/agent-skills`) already includes the server. On the first connection
  Copilot opens the Asyntai sign-in page in the browser.
- **Other agents with remote MCP support** (Cursor, VS Code, Windsurf and
  others): add a remote MCP server with the URL `https://asyntai.com/mcp`.
- **Agents that can only start a local command**: use the bridge package:

  ```json
  {
    "mcpServers": {
      "asyntai": { "command": "npx", "args": ["-y", "@asyntai/mcp"] }
    }
  }
  ```

The first tool call opens a browser once to approve access. If the user has no
account, they can create one free at https://asyntai.com/auth/ .

## Start every task the same way

1. Call `list_websites`. Most accounts have one website. Some have several.
2. If there are several, ask which one before any change. Tools that change
   data take a `website_id`. Do not guess it.
3. Read before you change: `get_ai_instructions` before
   `update_ai_instructions`, `list_knowledge` before you add or delete
   knowledge, `get_widget_settings` before `update_widget_settings`.

## Common jobs

- **Put the chatbot on the site**: `list_websites` gives the `widget_id`. Then
  follow the `add-ai-chatbot` skill.
- **Teach the agent**: `add_knowledge_url` for a page, `start_crawl` for a
  whole site, `add_knowledge_text` for a fact or a policy. Check with
  `list_crawls` and `list_knowledge`.
- **Test an answer**: `ask_ai` asks the agent a question, the same way a
  visitor does.
- **Change how it answers**: `get_ai_instructions`, then
  `update_ai_instructions`.
- **Change the look**: `get_widget_settings`, then `update_widget_settings`
  (name, colors, first message and more).
- **See what visitors ask**: `list_conversations`, `get_conversation`,
  `list_visitor_questions`, `get_analytics`.
- **Find gaps**: `list_knowledge_gaps` lists real visitor questions that need more
  knowledge. Add knowledge for them, then test with `ask_ai`.
- **Leads and tickets**: `list_leads`, `list_tickets`.
- **Reply to a live visitor yourself**: `list_active_sessions`,
  `take_over_conversation`, `send_agent_reply`, then `release_conversation`.
- **Plan and limits**: `get_account`, `list_plans`.
- **How a feature works**: `search_asyntai_docs`, then `get_asyntai_doc`.

Tool names are exact. If you are not sure, list the server's tools.

## Rules

- Read tools are safe to call at any time.
- Ask the user before you delete knowledge, change the instructions, change
  the widget settings or reply to a visitor on a live site.
- Show the user the new instructions text before you save it.
