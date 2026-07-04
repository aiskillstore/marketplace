---
name: debug-connection
description: Debug WebSocket connection issues between CLI and FigJam plugin. Use when diagrams aren't syncing, connection fails, plugin shows "Connecting..." indefinitely, or patches aren't being applied to canvas.
---

# WebSocket Connection Debugging

## Architecture

```
CLI serve (Bun) ←── WebSocket ──→ Plugin UI (ui.ts) ←── postMessage ──→ Plugin Main (code.ts)
     │                                  │                                    │
  File watcher                    Browser APIs                          Figma API
  YAML parsing                    WebSocket client                      Canvas rendering
```

## Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| CLI not running | "Connecting..." indefinitely | Start `bun run packages/cli/src/index.ts serve diagram.yaml` |
| Port in use | Connection refused | Check `lsof -i :3456`, use different port |
| Secret mismatch | Connects then immediately closes | Match `--secret` value in CLI and plugin |
| YAML errors | Connected but no updates | Fix validation errors in CLI output |
| docId mismatch | No response after hello | Ensure plugin docId matches YAML `docId` |
| Patches not applied | Connected, canvas unchanged | Check Plugin Main console for render errors |

## Debugging Steps

1. **CLI side**: Check terminal for errors, verify YAML with `bun run packages/cli/src/index.ts build diagram.yaml`
2. **Plugin UI**: Right-click plugin → Inspect → Console for WebSocket events
3. **Plugin Main**: Figma Desktop → Plugins → Development → Open console

## Message Flow

```
Plugin                          CLI
  │                              │
  │──── hello ─────────────────►│  {type:"hello", docId, secret?}
  │◄──── full ─────────────────│  {type:"full", rev, ir}
  │                              │
  │      [YAML changes]          │
  │◄──── patch ────────────────│  {type:"patch", baseRev, nextRev, ops}
  │                              │
  │      [Reconnect]             │
  │──── requestFull ───────────►│  {type:"requestFull", docId}
  │◄──── full ─────────────────│
```

## JSON Import Errors

- JSON must be an object with `version`, `docId`, `nodes`
- DSL format: `nodes` as array
- IR format: `nodes` as object (Record)
- Validation errors shown in alert with path + message

## Quick Test

```bash
# Start server
bun run packages/cli/src/index.ts serve examples/diagram.yaml

# Test with wscat
wscat -c ws://localhost:3456
> {"type":"hello","docId":"test"}
```
