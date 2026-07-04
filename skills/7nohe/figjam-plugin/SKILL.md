---
name: figjam-plugin
description: FigJam plugin development workflow. Use when modifying code.ts (canvas rendering), ui.ts (WebSocket/UI), fixing plugin build errors, or adding new rendering features.
---

# FigJam Plugin Development

## Architecture

| Thread | File | APIs | Role |
|--------|------|------|------|
| Main | `code.ts` | `figma.*` only | Canvas rendering |
| UI | `ui.ts` | Browser APIs | WebSocket client, connection UI |

**Critical**: `code.ts` has NO browser APIs (`window`, `document`, `fetch`, `WebSocket`).

## Communication

```
CLI ←─ WebSocket ─→ ui.ts ←─ postMessage ─→ code.ts ←─ figma.* ─→ Canvas
```

## Build & Import

```bash
cd packages/plugin && bun run build
```

Import: Figma Desktop → Plugins → Development → Import from manifest → `packages/plugin/manifest.json`

## Debugging

- **UI errors**: Right-click plugin UI → Inspect
- **Main errors**: Plugins → Development → Open console

## JSON Import

- Accepts DSL (nodes array) or IR (nodes object)
- Validates with `@figram/core`, normalizes to IR
- Errors shown in alert with path + message

## Key Files

| File | Purpose |
|------|---------|
| `manifest.json` | Plugin config |
| `src/code.ts` | Canvas rendering |
| `src/ui.ts` | WebSocket + UI |
| `src/icons/` | Service icons |
