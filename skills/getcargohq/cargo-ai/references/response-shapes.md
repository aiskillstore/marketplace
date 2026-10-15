# Response shapes

JSON response structures returned by Cargo CLI commands used in the `cargo-ai` skill.

## cargo-ai ai agent list

```json
{
  "agents": [
    {
      "uuid": "agent-uuid",
      "workspaceUuid": "...",
      "name": "Sales Research Agent",
      "icon": { "color": "blue", "face": "🤖" },
      "description": "Researches leads and enriches data",
      "triggers": [],
      "deployedRelease": {
        "uuid": "release-uuid",
        "version": "3",
        "description": "Added email step",
        "systemPrompt": "You are a sales research assistant...",
        "languageModelSlug": "gpt-4o",
        "integrationSlug": "openai",
        "temperature": 0.3,
        "maxSteps": 10,
        "actions": [],
        "resources": [],
        "capabilities": [],
        "mcpClients": [],
        "deployedAt": "2025-01-10T09:00:00Z",
        "createdAt": "2025-01-10T09:00:00Z"
      },
      "folderUuid": null,
      "template": null,
      "isReadOnly": false,
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-15T00:00:00Z"
    }
  ]
}
```

**Key fields:** `uuid` (needed for chat create, release operations), `name` (match by name), `deployedRelease` (current live config — `null` if never deployed).

**Agent icon colors:** `grey`, `green`, `purple`, `yellow`, `blue`, `red`.

## cargo-ai ai agent get

Same structure as a single item from `agent list`, nested under `agent`:

```json
{
  "agent": {
    "uuid": "agent-uuid",
    "name": "Sales Research Agent",
    "icon": { "color": "blue", "face": "🤖" },
    "deployedRelease": { ... },
    ...
  }
}
```

## cargo-ai ai release list

```json
{
  "releases": [
    {
      "uuid": "release-uuid",
      "agentUuid": "agent-uuid",
      "version": "3",
      "status": "deployed",
      "description": "Added research actions",
      "systemPrompt": "You are a sales research assistant...",
      "languageModelSlug": "gpt-4o",
      "integrationSlug": "openai",
      "temperature": 0.3,
      "maxSteps": 10,
      "withReasoning": false,
      "actions": [],
      "resources": [],
      "capabilities": [],
      "suggestedActions": [],
      "mcpClients": [],
      "deployedAt": "2025-01-10T09:00:00Z",
      "createdAt": "2025-01-10T09:00:00Z",
      "updatedAt": "2025-01-10T09:00:00Z"
    }
  ]
}
```

**Status values:** `draft`, `deployed`, `archived`.

Supports `--agent-uuid`, `--limit`, `--offset`.

## cargo-ai ai release get

```json
{
  "release": {
    "uuid": "release-uuid",
    "agentUuid": "agent-uuid",
    "version": "3",
    "status": "deployed",
    "description": "Added research actions",
    "systemPrompt": "You are a sales research assistant...",
    "languageModelSlug": "gpt-4o",
    "integrationSlug": "openai",
    "connectorUuid": null,
    "temperature": 0.3,
    "maxSteps": 10,
    "withReasoning": false,
    "actions": [
      {
        "kind": "connector",
        "integrationSlug": "clearbit",
        "connectorUuid": "connector-uuid",
        "actionSlug": "company_enrich",
        "slug": "enrich_company",
        "name": "Enrich Company",
        "description": "Enriches company data",
        "isBulkAllowed": false,
        "config": {}
      }
    ],
    "resources": [
      {
        "kind": "file",
        "slug": "knowledge_base",
        "name": "Knowledge Base",
        "description": null,
        "prompt": null,
        "items": [{ "kind": "file", "fileUuid": "file-uuid" }]
      }
    ],
    "capabilities": [],
    "suggestedActions": [],
    "mcpClients": [
      {
        "kind": "custom",
        "name": "Internal Tools",
        "url": "https://mcp.example.com",
        "authentication": null,
        "disabledToolSlugs": []
      }
    ],
    "deployedAt": "2025-01-10T09:00:00Z",
    "createdAt": "2025-01-10T09:00:00Z",
    "updatedAt": "2025-01-10T09:00:00Z"
  }
}
```

**Key fields:** `actions` (array of tool/connector/agent actions), `resources` (file or model resources), `mcpClients` (MCP server connections), `systemPrompt`, `languageModelSlug`, `temperature`, `maxSteps`.

**Action kinds:** `tool` (workflow tool), `connector` (integration action), `agent` (sub-agent).

**Resource kinds:** `file` (uploaded files/folders), `model` (data model reference).

**MCP client kinds:** `custom` (URL-based), `connector` (integration-backed).

## cargo-ai ai template list

```json
{
  "templates": [
    {
      "slug": "lead-researcher",
      "name": "Lead Researcher",
      "description": "Researches and qualifies leads using web data",
      "scope": "public",
      "isPreset": true,
      "kind": "agent",
      "icon": { "color": "purple", "face": "🔍" },
      "languageModelSlug": "gpt-4o",
      "temperature": 0.3,
      "categories": ["prospecting"],
      "author": {
        "name": "Cargo",
        "title": "Platform",
        "company": { "name": "Cargo", "url": "https://getcargo.ai" }
      },
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-15T00:00:00Z"
    }
  ]
}
```

**Key fields:** `slug` (the handle you filter this list by), `name`, `languageModelSlug`, `temperature`.

**Template categories:** `prospecting`, `ops`, `enablement`, `outreach`, `expansion`, `public`, `private`.

## `cargo-ai ai template list` — one entry

Each element of `templates[]` is returned in full. There is no `template get` subcommand; filter this response by `slug` instead.

```json
{
  "template": {
    "slug": "lead-researcher",
    "name": "Lead Researcher",
    "kind": "agent",
    "description": "...",
    "systemPrompt": "You are a lead research assistant...",
    "languageModelSlug": "gpt-4o",
    "integrationSlug": "openai",
    "temperature": 0.3,
    "maxSteps": 10,
    "withReasoning": false,
    "actions": [...],
    "resources": [...],
    "capabilities": [],
    "suggestedActions": [],
    "icon": { "color": "purple", "face": "🔍" },
    "scope": "public",
    "isPreset": true,
    "categories": ["prospecting"],
    "author": { ... },
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-15T00:00:00Z"
  }
}
```

> **Content files & libraries** (`cargo-ai content file …` / `content library …`) live in the [`cargo-content`](../../cargo-content/SKILL.md) skill — see `cargo-content/references/response-shapes.md` for their shapes.

## cargo-ai ai mcp-server list

```json
{
  "mcpServers": [
    {
      "uuid": "mcp-server-uuid",
      "workspaceUuid": "...",
      "name": "Internal Tools",
      "actions": [
        {
          "kind": "tool",
          "slug": "search_docs",
          "name": "Search Docs",
          "description": "Searches internal documentation",
          "isBulkAllowed": false,
          "config": {}
        }
      ],
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-15T00:00:00Z"
    }
  ]
}
```

**Key fields:** `uuid`, `name`, `actions` (discovered actions from the MCP server).

## cargo-ai ai memory list

```json
{
  "memories": [
    {
      "mem0Id": "memory-id",
      "content": "The user prefers concise responses with bullet points",
      "scope": "agent",
      "agentUuid": "agent-uuid",
      "workspaceUuid": "...",
      "createdAt": "2025-01-15T10:00:00Z",
      "updatedAt": "2025-01-15T10:00:00Z"
    }
  ]
}
```

**Memory scopes:**

- `workspace` — shared across all agents and users in the workspace. Has `workspaceUuid`.
- `user` — specific to a user. Has `userUuid`.
- `agent` — specific to an agent. Has `agentUuid` and `workspaceUuid`.

**Key field:** `mem0Id` (needed for update and remove operations).
