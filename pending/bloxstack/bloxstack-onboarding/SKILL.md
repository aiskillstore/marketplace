---
name: bloxstack-onboarding
description: Connect an AI assistant to a Roblox team's BloxStack workspace through the BloxStack MCP server. Use when a creator asks to get started on BloxStack, connect Claude Code, Codex, Cursor or another MCP client, or get a first briefing on their studio's games and tasks.
license: "May be installed and redistributed verbatim with attribution to BloxStack."
metadata:
  author: BloxStack
  runtime: "MCP clients with remote HTTP and OAuth support"
  permissions: "Read studio context for onboarding. The user selects one studio and approves access in their browser."
---

# BloxStack onboarding

Get a Roblox creator from “connect my agent” to an answer about their own team. The official remote HTTP MCP endpoint is `https://bloxstack.app/mcp`.

## Start where the creator is

- If BloxStack tools are already available, go straight to the first studio read. If a configured connection needs to sign in again, reuse it.
- If the creator is new, open [BloxStack Studio](https://bloxstack.app/studio). Let them sign in with Roblox and select an existing studio or create one. Use an existing team's studio when joining teammates. If an expected studio is missing, check the Roblox identity and membership with the creator.
- If you can configure the current client, do that for the creator. If you need their input, give just the next step for their app. Ask which app they use only if you cannot tell.

## Connect the current app

| Client | Setup |
| --- | --- |
| Claude Code | Run `claude mcp add --transport http bloxstack https://bloxstack.app/mcp`. In Claude Code, open `/mcp` and select `bloxstack` to sign in. |
| Codex CLI | Run `codex mcp add bloxstack --url https://bloxstack.app/mcp`, then `codex mcp login bloxstack`. |
| Gemini CLI | Run `gemini mcp add --transport http bloxstack https://bloxstack.app/mcp`, then enter `/mcp auth bloxstack` in Gemini. |
| Cursor or VS Code | Open the studio's **Agent → Connect**, select the editor, and use its install button. Then connect or start the server in the editor. |
| Claude or ChatGPT | Open **Agent → Connect** and select the app for its current connector settings. Use the remote address above and OAuth when prompted. |
| Other MCP clients | Add a remote Streamable HTTP server named `bloxstack` at the official address and start the client's OAuth flow. |

Let the creator finish the browser handoff. They check the app, choose one studio, and turn off **Allow changes** for a read-only introduction before selecting **Allow**. Leave sign-in details and tokens in the client and browser. If the client needs to reload its tools, resume from the first read in the refreshed session.

## Deliver the first result

1. Call the connected server's `get_studio` with `{}` first. Use the client-qualified tool name when shown. Verify the studio name matches the creator's intended team. If it differs, pause before reading further and have them reconnect to the intended studio.
2. Answer the creator's original question using the returned data. For a general introduction, give the studio name and one concrete detail, such as a real game or open task. If they asked about upcoming work, look for `list_tasks` in the connected tools and read the board. On an empty board, say so and offer to draft a first task in chat.
3. Stop once the creator has that first result. Keep a draft in chat until they ask you to save it. Opening a hosted Roblox Studio session uses Studio hours and is a separate workflow.

A configured endpoint alone is insufficient to verify access. If the studio read is unavailable, describe the last successful step and the single action that will unblock it. If an access or connection-limit notice appears, use its instructions. The creator can review or end a connection from the studio's **Agent** page.

[Set up a studio](https://bloxstack.app/learn/studio) · [Connect an AI app](https://bloxstack.app/learn/studio/agents)
