---
name: gate-mcp-installer
version: "2026.3.4-1"
updated: "2026-03-04"
description: One-click installer and configurator for Gate MCP (mcporter) in OpenClaw. Use when the user wants to (1) Install mcporter CLI tool, (2) Configure Gate MCP server connection, (3) Verify Gate MCP setup, or (4) Troubleshoot Gate MCP connectivity issues.
---

# Gate MCP Installer

One-click setup for Gate MCP (mcporter) in OpenClaw.

## Quick Start

To set up Gate MCP, run the install script:

```bash
bash ~/.openclaw/skills/gate-mcp-installer/scripts/install-gate-mcp.sh
```

Or execute the skill directly and I will guide you through the installation.

## What This Skill Does

This skill automates the complete Gate MCP setup process:

1. **Installs mcporter CLI** globally via npm
2. **Configures Gate MCP server** with proper endpoint
3. **Verifies connectivity** by listing available tools
4. **Provides usage examples** for common queries

## Manual Installation Steps (if script fails)

### Step 1: Install mcporter

```bash
npm i -g mcporter
# Or verify installation
npx mcporter --version
```

### Step 2: Configure Gate MCP

```bash
mcporter config add gate https://api.gatemcp.ai/mcp --scope home
```

### Step 3: Verify Configuration

```bash
# Check config is written
mcporter config get gate

# List available tools
mcporter list gate --schema
```

If tools are listed, Gate MCP is ready to use!

## Common Usage Examples

After installation, use Gate MCP with queries like:

- "check BTC/USDT price"
- "use gate mcp to analyze SOL"
- "what arbitrage opportunities are there on Gate?"
- "check ETH funding rate"

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: mcporter` | Run `npm i -g mcporter` |
| Config not found | Run the config add command again |
| Connection timeout | Check internet connection to fulltrust.link |
| No tools listed | Verify config URL is correct |

## Resources

- **Install Script**: `scripts/install-gate-mcp.sh` - Automated one-click installer
