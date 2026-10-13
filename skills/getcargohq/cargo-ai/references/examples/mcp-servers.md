# MCP server examples

## List all MCP servers

```bash
cargo-ai ai mcp-server list
```

## Create an MCP server

```bash
cargo-ai ai mcp-server create --name "Internal Tools"
```

## Connect an MCP server to an agent

MCP servers are connected to agents as MCP clients on the release:

```bash
# 1. Create or find the MCP server
cargo-ai ai mcp-server list
# → mcp-server-uuid

# 2. Add as an MCP client on the agent's draft release
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --mcp-clients '[{"kind":"custom","name":"Internal Tools","url":"https://mcp.example.com","authentication":null,"disabledToolSlugs":[]}]'

# 3. Deploy
cargo-ai ai release deploy-draft --agent-uuid <agent-uuid> \
  --language-model-slug gpt-4o \
  --integration-slug openai
```

**MCP client kinds:**

- `custom` — URL-based MCP server. Requires `name`, `url`, and optionally `authentication`.
- `connector` — Integration-backed MCP client. Requires `name`, `connectorUuid`, `integrationSlug`.

## Connect a connector-backed MCP client

```bash
# 1. Find the connector
cargo-ai connection connector list
# → connector-uuid, integrationSlug

# 2. Add as an MCP client
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --mcp-clients '[{"kind":"connector","name":"HubSpot Tools","connectorUuid":"<connector-uuid>","integrationSlug":"hubspot","disabledToolSlugs":[]}]'

# 3. Deploy
cargo-ai ai release deploy-draft --agent-uuid <agent-uuid> \
  --language-model-slug gpt-4o \
  --integration-slug openai
```

## Disable specific actions from an MCP server

Use `disabledToolSlugs` to prevent the agent from using specific MCP actions:

```bash
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --mcp-clients '[{"kind":"custom","name":"Internal Tools","url":"https://mcp.example.com","authentication":null,"disabledToolSlugs":["dangerous_tool","admin_tool"]}]'
```

## Update an MCP server name

```bash
cargo-ai ai mcp-server update --uuid <mcp-server-uuid> --name "Production Tools"
```

## Remove an MCP server

```bash
cargo-ai ai mcp-server remove <mcp-server-uuid>
```
