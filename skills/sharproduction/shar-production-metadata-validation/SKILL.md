---
name: shar-production-metadata-validation
description: Validate rights-aware AI-hybrid video-production metadata with SHAR Production's local read-only MCP tool.
---

# SHAR Production metadata validation

Use this skill when a production manifest must be checked before delivery or release. The validator checks required production metadata and returns a deterministic `releasable` result with any errors. It does not publish content, modify files, access credentials, or make network requests.

## Install

```bash
git clone https://github.com/SHARProduction/production-metadata-mcp.git
cd production-metadata-mcp
npm ci
```

## Run as an MCP server

Configure the client to launch:

```json
{
  "command": "node",
  "args": ["/absolute/path/to/production-metadata-mcp/server.js"]
}
```

Call `validate_production_manifest` with one object field, `manifest`. The manifest may contain arbitrary fields; validate the returned `releasable` boolean and `errors` array before treating a production asset as ready.

## Safety boundary

Use only factual production metadata. Do not treat a passing validation result as legal advice, a rights clearance, or permission to publish.
