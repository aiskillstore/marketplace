# Troubleshooting

Common errors and solutions for `cargo-ai` commands.

## General

**`{"errorMessage": "..."}`**
All failed commands exit non-zero and return an error JSON. Read the `errorMessage` for the specific issue.

**`Unauthorized` / `403`**
Your API token may lack the required permissions. Verify with `cargo-ai whoami` and check that your role includes `ai:agent:*` or `ai:agent:write` actions.

## Agents

**`agentNotFound`**
The agent UUID does not exist or has been deleted. Re-run `cargo-ai ai agent list` to get the current list of agents.

**`folderNotFound`**
The folder UUID passed to `--folder-uuid` does not exist. Folders are managed by the [`cargo-workspace-management`](../../cargo-workspace-management/SKILL.md) skill — run `cargo-ai workspaceManagement folder list` to find valid folder UUIDs, or `cargo-ai workspaceManagement folder create --kind agent ...` to create one.

**Agent has no deployed release**
If `agent get` shows `deployedRelease: null`, the agent has never been deployed. Follow the release workflow:
1. `cargo-ai ai release get-draft --agent-uuid <uuid>`
2. `cargo-ai ai release update-draft --agent-uuid <uuid> --language-model-slug gpt-4o --system-prompt "..."`
3. `cargo-ai ai release deploy-draft --agent-uuid <uuid> --language-model-slug gpt-4o --integration-slug openai`

## Releases

**`draftReleaseNotFound`**
The agent does not have a draft release. This can happen if the agent was just created. Try `cargo-ai ai release get-draft --agent-uuid <uuid>` first — it may auto-create the draft.

**`invalidParent`**
The `--parent-uuid` passed to `release update-draft` does not match a valid release. Omit it or use a UUID from `release list`.

**`invalidReleaseVersion`**
The version string is invalid. Version must be a non-empty string (not a number).

**`invalidConnector`**
A connector UUID referenced in the release actions or configuration does not exist. Verify connector UUIDs with `cargo-ai connection connector list`.

**`failedToReconciliateAgentAiTools`**
The actions configuration in the release is invalid — a referenced tool, agent, or connector UUID may not exist. Verify all UUIDs in the actions array.

**Can't set structured (JSON Schema) output or a heartbeat from the CLI**
`release update-draft` / `release deploy-draft` have no `--output` / `--output-schema` or `--heartbeat` flag, even though the release API payload accepts `output` and `heartbeat`. The generic `--options` flag won't carry them. See the "Structured output & heartbeat" section in [`../SKILL.md`](../SKILL.md) for the shapes and the direct-API workaround, and file a `workspaceManagement report` to request the flags.

## Templates

**`templateNotFound`**
The template slug does not exist. Run `cargo-ai ai template list` to see available templates.

## Files & libraries

Knowledge files and libraries moved to the `content` domain (CLI ≥ 1.0.19). For `fileNotFound`, `folderNotFound`, upload failures, and the `unknown command` error on the old `ai file …` path, see [`cargo-content`](../../cargo-content/SKILL.md) → `references/troubleshooting.md`.

## MCP Servers

**`mcpServerNotFound`**
The MCP server UUID does not exist or has been deleted. Run `cargo-ai ai mcp-server list` to get the current list.

**MCP actions not appearing in agent**
MCP servers are connected to agents via MCP clients on the release. After creating an MCP server, add it as an MCP client to the agent's draft release using `release update-draft`, then deploy.

## Memories

**`memoryNotFound`**
The `mem0Id` does not match any existing memory. Run `cargo-ai ai memory list` with the correct `--scope` and `--agent-uuid` to find valid memory IDs.

**Wrong scope**
Memory operations require the correct scope. An agent-scoped memory needs `--scope agent --agent-uuid <uuid>`. A workspace-scoped memory needs `--scope workspace`. Mismatched scopes return not-found errors.
