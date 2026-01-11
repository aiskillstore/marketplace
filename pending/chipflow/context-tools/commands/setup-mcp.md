---
name: setup-mcp
description: Troubleshooting guide for MCP server configuration (auto-configures by default)
---

# MCP Server Troubleshooting

**Note**: The MCP server should auto-configure when you install the plugin and restart Claude Code. This guide is only needed if auto-configuration fails.

## Check if Already Configured

First, verify the server isn't already running:
```bash
claude mcp list
```

If you see `repo-map: ... - ✓ Connected`, it's already working! No action needed.

## Manual Configuration (If Auto-Config Failed)

If the server isn't listed or shows an error, configure it manually:

1. Get the plugin version:
```bash
PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('${HOME}/.claude/plugins/cache/chipflow-context-tools/context-tools/.claude-plugin/plugin.json'))['version'])")
```

2. Add the MCP server:
```bash
claude mcp add --scope user --transport stdio repo-map \
  --env PROJECT_ROOT='${PWD}' \
  -- uv run "${HOME}/.claude/plugins/cache/chipflow-context-tools/context-tools/${PLUGIN_VERSION}/servers/repo-map-server.py"
```

3. Verify it's configured:
```bash
claude mcp list
```

You should see: `repo-map: ... - ✓ Connected`

## After Setup

**Restart Claude Code** for the MCP server to load.

After restart, the MCP tools will be available in all projects. The server automatically:
- Indexes your codebase on first use
- Monitors for file changes and reindexes
- Stores symbols in `.claude/repo-map.db`

## Troubleshooting

If `claude mcp list` shows an error:
- Check that `uv` is installed: `uv --version`
- Verify the plugin is installed: `claude plugin list`
- Check the plugin cache path exists: `ls ~/.claude/plugins/cache/chipflow-context-tools/context-tools/`

## To Remove

```bash
claude mcp remove repo-map
```
