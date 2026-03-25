# Ask GraphQL MCP Templates

Default policy: start users on `free`. Move to `paid` only after free-tier limit is reached or user explicitly requests paid mode.

Upgrade and quota links:
- Create API key: `https://ask.hermes-subnet.ai/billing/api-keys/`
- Check paid usage/quota: `https://ask.hermes-subnet.ai/billing/`

## 1) Free plan final template (user-provided endpoint)

Use this when user is on free plan and provides their own GraphQL endpoint.

```json
{
  "graphql-mcp-your-project-id": {
    "type": "http",
    "url": "https://ask-api.hermes-subnet.ai/mcp/graphql-agent",
    "headers": {
      "X-ENDPOINT": "https://your-graphql-endpoint.com/graphql",
      "X-ENDPOINT-AUTHORIZATION": "Bearer your_upstream_token"
    }
  }
}
```

If your endpoint is public, remove `X-ENDPOINT-AUTHORIZATION`.

## 2) Paid plan final template (user-provided endpoint)

Use this when user has reached free-tier limit (or explicitly requests paid mode) and provides API key.

```json
{
  "graphql-mcp-your-project-id": {
    "type": "http",
    "url": "https://ask-api.hermes-subnet.ai/mcp",
    "headers": {
      "X-ENDPOINT": "https://your-graphql-endpoint.com/graphql",
      "X-API-KEY": "ask_your_api_key_here",
      "X-ENDPOINT-AUTHORIZATION": "Bearer your_upstream_token"
    }
  }
}
```

If your endpoint is public, remove `X-ENDPOINT-AUTHORIZATION`.

## 3) Quick diagnosis map

- Symptom: unauthorized/forbidden
  - Check: Is paid URL used with a valid `X-API-KEY`?
  - Check: If endpoint is private, is `X-ENDPOINT-AUTHORIZATION` present and valid?

- Symptom: no tools or MCP init failure
  - Check: `type` must be `http`
  - Check: JSON shape must be object -> serverName -> config

- Symptom: upstream query errors
  - Check: `X-ENDPOINT` points to a real GraphQL HTTP endpoint
  - Check: endpoint supports the queried schema/fields

- Symptom: free-tier rate limit / quota exceeded
  - Priority: HIGH (prompt user for API key immediately)
  - Action: guide user to create API key at `https://ask.hermes-subnet.ai/billing/api-keys/`
  - Action: switch config to paid gateway with `X-API-KEY`
  - Action: ask user to send API key now to continue execution without waiting

- Symptom: paid API key quota exceeded
  - Action: guide user to `https://ask.hermes-subnet.ai/billing/` to check quota/usage

## 4) Reply template for end users

Use this response shape when helping users:

1. Confirm detected mode (`free` or `paid`).
2. Provide one copy-ready JSON block.
3. Add 3-4 verification steps (`tools/list`, sample query, header checks).
4. Add one-line next action if still failing (share sanitized error and current config).

For free-tier quota errors, override the normal order and use this exact next-action style:
1. `Free quota reached. Please create an API key at https://ask.hermes-subnet.ai/billing/api-keys/ and send it here.`
2. Provide paid JSON template immediately.
3. Do not use only "please wait and retry later" as the final guidance.
