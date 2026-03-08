# Gate MCP Installer

## Overview

An AI Agent skill that provides one-click installation and configuration for Gate MCP (mcporter) in [OpenClaw](https://openclaw.ai), enabling natural-language access to Gate.io market data.

### Core Capabilities

| Capability | Description | Example |
|------------|-------------|---------|
| **One-Click Install** | Automated mcporter CLI + Gate MCP setup | "help me install Gate MCP" |
| **Config Management** | Configure Gate MCP server endpoint | "configure Gate MCP" |
| **Connectivity Verification** | Verify MCP tools are accessible | "is Gate MCP installed correctly?" |
| **Troubleshooting** | Diagnose and fix common setup issues | "what if MCP cannot connect?" |

> 🚀 **One command**: `bash scripts/install-gate-mcp.sh` handles the entire setup — install mcporter, configure endpoint, verify connectivity.

---

## Architecture

```
User Request ("help me install Gate MCP")
    ↓
AI Agent
    ↓
install-gate-mcp.sh
    ├── npm i -g mcporter                    → Install CLI
    ├── mcporter config add gate <endpoint>  → Configure server
    └── mcporter list gate --schema          → Verify tools
    ↓
Gate MCP Ready → Other skills can use Gate MCP tools
```

**Dependencies:**
- Node.js / npm (for mcporter installation)
- Network access (to download mcporter and connect to Gate MCP endpoint)

---

## Agent Use Cases

### 1. First-Time Setup
> "help me install Gate MCP"

- Full automated installation and configuration
- Verify connectivity and show available tools
- For: new users setting up Gate AI skills

### 2. Health Check
> "is Gate MCP installed correctly?"

- Verify config and connectivity
- Report status with actionable suggestions
- For: users troubleshooting other skills

### 3. Troubleshooting
> "Gate MCP cannot connect"

- Step-by-step diagnosis
- Automated fix attempts
- For: users experiencing connectivity issues

### 4. Update / Reinstall
> "update mcporter"

- Reinstall latest mcporter version
- Re-verify configuration
- For: users needing to update

---

## Quick Start

### Prerequisites

1. Node.js and npm installed
2. Network access

### Installation

```bash
# Automated (recommended)
bash ~/.openclaw/skills/gate-mcp-installer/scripts/install-gate-mcp.sh

# Or just ask the agent
"help me install Gate MCP"
```

### Manual Steps (if script fails)

```bash
# Step 1: Install mcporter
npm i -g mcporter

# Step 2: Configure Gate MCP
mcporter config add gate https://api.gatemcp.ai/mcp --scope home

# Step 3: Verify
mcporter config get gate
mcporter list gate --schema
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `command not found: mcporter` | Run `npm i -g mcporter` |
| Config not found | Re-run the config add command |
| Connection timeout | Check internet connectivity |
| No tools listed | Verify the config URL is correct |

---

## File Structure

```
gate-mcp-installer/
├── README.md           # This file
├── SKILL.md            # Skill instructions and workflow
├── CHANGELOG.md        # Version history
├── scripts/
│   └── install-gate-mcp.sh  # Automated installer script
└── references/
    └── scenarios.md    # Scenario examples and prompt templates
```

---

## Security

- Single bash script (`install-gate-mcp.sh`) — auditable in seconds
- Installs mcporter from npm public registry
- Connects to public Gate MCP endpoint (no API keys required)
- No credential handling or storage
- No destructive operations
- No data collection, telemetry, or analytics

## License

MIT
