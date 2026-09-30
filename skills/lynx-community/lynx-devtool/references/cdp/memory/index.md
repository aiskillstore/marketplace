# Memory Methods

The `Memory` domain is a Lynx global CDP extension. It is handled by the global DevTool mediator, so it can be sent with session ID `-1` and does not require an active LynxView session.

The current payload reports global totals plus `instances[]` for live registered Lynx instances. It does not expose a nested child LynxView memory tree; UI view details are category/tag aggregates.

For WebView targets, use standard Chrome DevTools Protocol memory-related APIs instead; these Lynx global methods may return `method not found`.

## Methods

- [Memory.getAllMemoryUsage](Memory.getAllMemoryUsage.md) - Get global Lynx memory usage across live instances
