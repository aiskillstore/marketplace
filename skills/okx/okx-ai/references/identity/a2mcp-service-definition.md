# Define an A2MCP Service

Defines the A2MCP service flow used during Agent registration and updates.

## Rules

- **NEVER** edit probed MCP `name`/`title`, `description`, or `inputSchema`.
- **NEVER** collect or accept a user-supplied `fee`.
- **MUST** localize static display text, but preserve endpoints, tool names, and IDs verbatim.

## Workflow

### 1. Probe the endpoint

Collect a valid HTTPS [`endpoint`](service-contract.md#endpoint), then run `agent a2mcp tool-list
--endpoint <endpoint>` once. **NEVER** use `--all`.

On a probe error, show [Endpoint unavailable](#endpoint-unavailable) and stop.

### 2. Define the service workflow

**MUST** branch only on `data.type`:

- `"mcp"`: enter the MCP workflow.
- `"http"`: enter the HTTP workflow.

#### MCP workflow

1. If `data.tools` is empty, show the [Empty MCP tools](#empty-mcp-tools) card and stop.
2. Show [MCP tool selection](#mcp-tool-selection) for loaded tools. If `nextCursor` is returned,
   retain it and offer `Load more MCP tools`. Fetch the next page only when the user explicitly
   requests it.
3. On that explicit request, call `tool-list --cursor <nextCursor>` once, append the tools, retain
   the new cursor, and repeat step 2. Keep existing numbers stable; selections may span pages.
4. Collect one or more selections. **After selection and before any verification or addition,
   MUST check every selected tool. If `title` or `description` is missing, null, or blank, MUST
   immediately show [Incomplete MCP tool fields](#incomplete-mcp-tool-fields) and stop. NEVER use
   `name` as a fallback for `title`, and NEVER continue with verification or Service addition.**
5. For every selected tool, set `serviceName` to `title`, `toolName` to `name`,
   `serviceDescription` to `description`, `inputSchema` to the returned schema when available,
   `reqType:"MCP"`, and `method:"POST"`.

#### HTTP workflow

1. Show [HTTP service information](#http-service-information). `serviceName` **MUST** meet its
   [requirements](service-contract.md#servicename).
2. Show [HTTP request method](#http-request-method) and collect exactly one numbered choice.
3. Show [HTTP request parameters](#http-request-parameters), collect parameters, then assemble
   `inputSchema` as specified [below](#http-inputschema-assembly); skip when requested.
4. Set `reqType:"HTTP"`.

### 3. Verify callability

Generate typed `exampleParams` for `inputSchema.required`, or `{}` when absent. Base64-encode the
exact UTF-8 candidate Service and parameters, then run `agent a2mcp invoke` once with
`--service-base64` and `--params-base64 --verify`. **NEVER** pass raw JSON.

- A `result` sets `fee:"0"`.
- A parseable `feeQuote` sets `fee` to `feeQuote.amount` when
  `feeQuote.asset` is `USDT`, `USDC`, or `USDG`; otherwise stop.
- Read `feeQuote` from x402 `accepts[]`: MCP v2 `structuredContent`, then `content[0].text`, or
  HTTP 402—never endpoint prose.
- With parameterized `inputSchema`, a successful check **MUST** set `reqExample` to the checked compact JSON. Without request parameters, **MUST** omit `inputSchema` and `reqExample`; **NEVER** emit `reqExample:"{}"`.

### 4. Resolve a failed callability check

After one failed attempt, show [Request parameters](#request-parameters) and stop. For HTTP and
MCP, use supplied values only for the next check, then repeat §3.

### 5. Build the service payload

Build an element with `serviceType:"A2MCP"`, `serviceName`, `serviceDescription`, `fee`,
`endpoint`, and required [A2MCP fields](service-contract.md#a2mcp-fields).

## MCP-specific cards

### MCP tool selection

```markdown
Select MCP tools.

| # | Name | Tool name | Description |
|---|---|---|---|
| {n} | {title} | `{name}` | {description} |

Reply with one or more loaded service numbers or names. If more are available, offer `Load more MCP tools`.
```

### Empty MCP tools

```markdown
This MCP service has no available tools. Add at least one valid tool, then retry.
```

### Incomplete MCP tool fields

```markdown
MCP tool information is incomplete. Complete the following fields, then retry.
Tool 1: missing title; Tool 2: missing description
```

## HTTP-specific collection

### HTTP service information

```markdown
Provide the HTTP service information:

1. Service name (5–100 characters): {serviceName}
2. Service description (up to 1,000 characters): {serviceDescription}
```

### HTTP request method

```markdown
Select the request method:

1. GET
2. POST

Reply `1` or `2`.
```

### HTTP request parameters

```markdown
1. Parameter name: {parameterName}
   a. Type: {type}
   b. Description: {description}
   c. Required: yes / no
```

**MUST** use this format. For `array`/`object`, collect `Item type` recursively; **NEVER** infer or verify incomplete schema.

### HTTP inputSchema assembly

Build exactly one JSON Schema object from all collected HTTP parameters:

```json
{
  "type": "object",
  "properties": {
    "{parameterName}": {
      "type": "{type}",
      "description": "{description}",
      "items": { "type": "string" }
    }
  },
  "required": ["{requiredParameterName}"]
}
```

- If no parameters are collected, omit `inputSchema`.
- Every parameter name **MUST** be non-blank and unique.
- Include each collected parameter's type and description in `properties`.
- Map array item types to `items`; map object child parameters to `properties` and `required`.
- Preserve a user-provided JSON Schema unchanged.
- Add to `required[]` only parameters marked `yes`, preserving collected order.
- Add no uncollected schema fields.

## Shared callability cards

### Request parameters

````markdown
Service {n}: {name} — simulated parameters:

```json
{exampleParams}
```

Please fill in the real values for these parameters.
````

When parameters are required, render `{exampleParams}` from `inputSchema`: required properties
in schema order, or all if `required` is empty/absent, using type-appropriate placeholders.

### Endpoint unavailable

```markdown
We couldn't retrieve tools. Check the endpoint and try again.
```

## CLI reference

Prefix commands with `onchainos`; use `--help` for exact flags. Run each prescribed call once.

| CLI | Usage | Response / rules |
|---|---|---|
| `agent a2mcp tool-list` | `onchainos agent a2mcp tool-list --endpoint <url> [--cursor <nextCursor>] [--tool-name <name>]` | Never use `--all`. Read `data.type`, `tools[]`, and `nextCursor`. Use `--cursor` once per explicit load-more request, retaining each new cursor. It conflicts with `--tool-name`. |
| `agent a2mcp invoke` | Registration verification: `onchainos agent a2mcp invoke --service-base64 <b64> --params-base64 <b64> --verify` | Only params are audit-redacted; Service JSON **MUST** remain secret-free. `callable:true` means verification succeeded. |
