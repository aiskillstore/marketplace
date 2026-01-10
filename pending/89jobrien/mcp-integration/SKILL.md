---
name: mcp-integration
description: Model Context Protocol (MCP) integration specialist. Use when creating
  MCP server configurations, implementing MCP integrations, or optimizing MCP performance.
  Specializes in MCP server architecture and integration patterns.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# MCP Integration

This skill creates and optimizes Model Context Protocol (MCP) integrations, including server configurations, authentication, and performance optimization.

## When to Use This Skill

- When creating new MCP server configurations
- When integrating services with MCP
- When optimizing MCP performance
- When implementing MCP authentication
- When structuring MCP servers
- When troubleshooting MCP integrations

## What This Skill Does

1. **MCP Configuration**: Creates MCP server configurations
2. **Integration Design**: Designs MCP integrations with services
3. **Authentication**: Implements secure authentication
4. **Performance**: Optimizes MCP performance
5. **Security**: Ensures MCP security best practices
6. **Testing**: Tests and validates MCP configurations

## How to Use

### Create MCP Integration

```
Create an MCP integration for GitHub API
```

```
Configure MCP server for database access
```

### Specific Tasks

```
Optimize this MCP server configuration for performance
```

## MCP Configuration

### Standard Format

```json
{
  "mcpServers": {
    "ServiceName MCP": {
      "command": "npx",
      "args": ["-y", "package-name@latest"],
      "env": {
        "API_KEY": "required-env-var"
      }
    }
  }
}
```

### Server Types

**API Integration MCPs:**

- REST API connectors
- GraphQL integrations
- Database connectors
- Cloud service integrations

**Development Tool MCPs:**

- Code analysis integrations
- Build system connectors
- Testing framework integrations
- CI/CD pipeline connectors

## Examples

### Example 1: GitHub MCP

**Input**: Create GitHub MCP integration

**Output**:

```markdown
## MCP Integration: GitHub

### Configuration
```json
{
  "mcpServers": {
    "GitHub Integration MCP": {
      "command": "npx",
      "args": ["-y", "github-mcp@latest"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_API_URL": "https://api.github.com"
      }
    }
  }
}
```

### Usage

Install with: `npx claude-code-templates@latest --mcp="github-integration"`

```

## Best Practices

### MCP Design

1. **Security**: Use environment variables for secrets
2. **Performance**: Implement connection pooling
3. **Error Handling**: Robust error handling and retries
4. **Validation**: Validate all inputs and responses
5. **Documentation**: Document required environment variables

## Related Use Cases

- MCP server creation
- Service integration
- MCP configuration
- Performance optimization
- Security implementation
