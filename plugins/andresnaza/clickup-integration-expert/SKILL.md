---
name: ClickUp Integration Expert
description: When the user asks about ClickUp synchronization or syncing roadmaps with ClickUp
---

# ClickUp Integration Expertise

You are an expert in integrating local roadmaps with ClickUp using the official ClickUp MCP.

## Sync Mapping

| Local | ClickUp |
|-------|---------|
| Epic | Task (type: Epic) |
| Milestone | Subtask under Epic |
| Status: planned | To Do |
| Status: in-progress | In Progress |
| Status: done | Complete |

## Configuration

Stored in `.roadmap/clickup-config.json`:

```json
{
  "workspace": { "id": "...", "name": "..." },
  "space": { "id": "...", "name": "..." },
  "epicFolder": { "id": "...", "name": "Epics" },
  "syncMapping": {
    "epics": { "user-auth": "abc123" },
    "milestones": { "user-auth:M1": "def456" }
  },
  "lastSync": null
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/clickup-sync:setup` | Configure ClickUp connection |
| `/clickup-sync:push` | Push to ClickUp |
| `/clickup-sync:pull` | Pull from ClickUp |
| `/clickup-sync:sync` | Full bidirectional sync |
| `/clickup-sync:status` | View sync status |
| `/clickup-sync:link` | Manually link items |
| `/clickup-sync:unlink` | Remove sync links |

## MCP Setup

Install the ClickUp MCP:
```bash
claude mcp add --transport http clickup https://mcp.clickup.com/mcp
```

Then run `/mcp` to authenticate via OAuth.

## Best Practices

1. **Pull before push**: Get remote changes first
2. **Use dry-run**: Preview with `--dry-run`
3. **Check status**: Spot issues early

## Conflict Resolution

- **Status**: ClickUp wins (current state)
- **Points**: Local wins (planning)
- **Title**: Local wins (planning)
