# MCP Security Best Practices

This guide covers security considerations when integrating MCP servers into Claude Code plugins.

## The Golden Rules

1. **Never hardcode secrets** - Always use environment variables
2. **Use secure protocols** - HTTPS for HTTP, WSS for WebSocket
3. **Validate all inputs** - Never trust data from MCP servers blindly
4. **Minimize permissions** - Only allow necessary tools
5. **Document requirements** - Users need to know what secrets are needed

## Environment Variables

### Correct Usage

```json
{
  "mcpServers": {
    "my-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${MY_API_KEY}"
      }
    }
  }
}
```

### Common Patterns

| Secret Type | Variable Name Convention | Example |
|-------------|-------------------------|---------|
| API Keys | `SERVICE_API_KEY` | `${OPENAI_API_KEY}` |
| Database URLs | `DATABASE_URL` | `${POSTGRES_URL}` |
| OAuth Tokens | `SERVICE_TOKEN` | `${GITHUB_TOKEN}` |
| Passwords | `SERVICE_PASSWORD` | `${DB_PASSWORD}` |

### Setting Environment Variables

**For development (.env file - DO NOT COMMIT):**
```bash
export MY_API_KEY="sk-..."
export DATABASE_URL="postgres://..."
```

**For production:**
- Use your deployment platform's secret management
- AWS Secrets Manager, HashiCorp Vault, etc.

## Protocol Security

### HTTP vs HTTPS

```json
// ❌ INSECURE - data transmitted in plaintext
{
  "url": "http://api.example.com/mcp"
}

// ✅ SECURE - encrypted connection
{
  "url": "https://api.example.com/mcp"
}
```

**Exception:** localhost/127.0.0.1 can use HTTP for local development.

### WebSocket Security

```json
// ❌ INSECURE
{
  "url": "ws://api.example.com/mcp/ws"
}

// ✅ SECURE
{
  "url": "wss://api.example.com/mcp/ws"
}
```

## Tool Allowlisting

### Restrict Allowed Tools

Instead of allowing all tools from an MCP server, explicitly list which ones are safe:

```json
{
  "mcpServers": {
    "database": {
      "type": "stdio",
      "command": "...",
      "allowedTools": [
        "query",      // Allow read queries
        "list_tables" // Allow listing tables
        // "drop_table" is NOT allowed
      ]
    }
  }
}
```

### Tool Risk Categories

| Risk Level | Examples | Recommendation |
|------------|----------|----------------|
| Low | Read-only queries, list operations | Can auto-allow |
| Medium | Create, update operations | Require confirmation |
| High | Delete, admin operations | Never auto-allow |

## Input Validation

When processing data from MCP servers:

1. **Validate types** - Ensure data matches expected schema
2. **Sanitize strings** - Escape special characters
3. **Check bounds** - Validate numeric ranges
4. **Verify permissions** - Ensure operation is allowed

## Path Security

### Use Portable Paths

```json
// ❌ INSECURE - hardcoded absolute path
{
  "args": ["/home/user/plugin/server.js"]
}

// ✅ SECURE - portable path variable
{
  "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"]
}
```

### Why It Matters

- Hardcoded paths break on other machines
- Can expose system structure to attackers
- Makes plugins non-portable

## Credential Storage

### DO NOT Store

- API keys in code
- Passwords in configuration
- Tokens in git repositories

### DO Store

- Environment variable references
- Instructions for obtaining credentials
- Links to credential management docs

## Auditing Checklist

Before publishing an MCP integration:

- [ ] No hardcoded secrets in configuration
- [ ] All URLs use HTTPS/WSS (except localhost)
- [ ] Environment variables documented in README
- [ ] Tool allowlist configured (if applicable)
- [ ] No absolute paths (use ${CLAUDE_PLUGIN_ROOT})
- [ ] Sensitive operations require confirmation
- [ ] Error messages don't leak secrets

## Common Vulnerabilities

### 1. Credential Leakage

**Problem:** Secrets appear in logs or error messages

**Solution:**
- Mask secrets in logging
- Use generic error messages

### 2. Man-in-the-Middle

**Problem:** HTTP allows traffic interception

**Solution:**
- Always use HTTPS/WSS
- Validate SSL certificates

### 3. Injection Attacks

**Problem:** User input used in commands

**Solution:**
- Sanitize all inputs
- Use parameterized queries

### 4. Privilege Escalation

**Problem:** MCP server has too many permissions

**Solution:**
- Principle of least privilege
- Explicit tool allowlisting
