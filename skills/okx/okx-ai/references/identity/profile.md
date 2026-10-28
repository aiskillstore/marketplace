# Agent profile

## Module Description

Use to list owned Agents, inspect Agent details, and list services.


## Flow
### Agent ID normalization

- Agent IDs **MUST** be digits only; normalize `agent9967` to `9967`.

### My Agents

Run:

```bash
onchainos agent get-my-agents [--role <role>]
```

Add `--role` only when the user supplied one.

### Agent Details

Own Agent — the user says "my Agent"/"mine", or the ID matches one already returned by
`get-my-agents` in this conversation → `get-my-agents`. Any other ID (named or pasted with no
such match) → `get-agents`:

```bash
onchainos agent get-my-agents --agent-ids <id[,id...]>   # own Agent
onchainos agent get-agents --agent-ids <id[,id...]>      # otherwise
```

### Services for an explicit Agent ID

For ASPs only, immediately after rendering the Agent detail below, run:

```bash
onchainos agent service-list --agent-id <id> --page 1 --page-size 3
```

**MUST** use the `Service table` in `output-templates.md` to render only
returned `cells[]` in order.

If any returned service is `A2MCP`, localize and append once: `Want to view method, inputSchema, or reqExample? Tell me which service.`

#### Pagination

When `hasMore == true` and the user asks for more, run:

```bash
onchainos agent service-list --agent-id <id> --page <page+1> --page-size 3
```


## Output Rules
### My Agents

#### Agent Table

**MUST** render Account groups and each group's display-ready
`agentList[].cells[]` in returned order, localizing this template's labels:

```markdown
### <accountName> (Address: <ownerAddress>)

| Agent ID | Name | Role | Status | Approval status | Rating |
|---|---|---|---|---|---|
| <agentId> | <name> | <role> | <status> | <approvalStatus> | <rating> |
```

##### Rules

- User/Evaluator: `Status` and `Approval status` MUST be `—`.

#### Pagination

When `hasMore == true`, offer to show the next page after all Account tables.
On request, run:

```bash
onchainos agent get-my-agents [--role <role>] --page <page+1>
```

Keep `--role` only when used in the initial request.

### Detail for explicit Agent IDs

#### Agent detail

**MUST** render each Agent from its `card[]` — a top-level array entry for `get-agents`, or the
matching agent's own `card[]` nested at `list[*].agentList[*]` for `get-my-agents`:

```markdown
| Field | Value |
|---|---|
| Agent ID | <agentId> |
| Name | <name> |
| Role | <role> |
| Status | <status> |
| Approval status | <approvalStatus> |
| Address | <address> |
| Description | <description> |
| Profile photo | <profilePhoto> |
| Rating | <rating> |
```

##### Rules

- Render exactly the rows present in `card[]`, in order.
- User/Evaluator: **NEVER** show `Status` or `Approval status`.
