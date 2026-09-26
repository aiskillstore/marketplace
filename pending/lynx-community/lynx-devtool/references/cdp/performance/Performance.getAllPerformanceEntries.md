# Performance.getAllPerformanceEntries

Scope: This method documents LynxView-specific performance data exposed by Lynx DevTool. For WebView targets, use standard Chrome DevTools Protocol Performance APIs instead; this method may return `method not found`.

- `Performance.getAllPerformanceEntries` - Get cached PerformanceEntry objects from the current page.
- Input: None
- Output: `{entries: Array<PerformanceEntry>}`
- Description: Returns the PerformanceEntry records cached by the Lynx runtime while DevTool is enabled.

## Version Support

- Requires Lynx 3.8 or later.
- On older Lynx versions, this method may be unavailable. Use `Performance.getAllTimingInfo` for aggregated timing metrics as a fallback.

## Behavior

- This method is independent of the CDP `Performance.enable` method; calling it is not a prerequisite.
- The engine's native DevTool cache stores pipeline entries only when Lynx DevTool is enabled.
- If no entries have been recorded, or if DevTool was not enabled when entries were produced, `entries` may be an empty array.
- Entries are cleared when the runtime resets timing state before reload.

## Entry Shape

Each entry is a plain object. The current native cache contains `pipeline` entries. Common fields include:

- `entryType`: `pipeline`.
- `name`: A pipeline name, usually derived from its origin, such as `loadBundle` or `updateTriggeredByNative`.
- `instanceId`: Lynx instance id added by the performance controller.

Other fields depend on the pipeline type and the Timing API:

- Entries may include pipeline timing fields, `frameworkRenderingTiming`, and `hostPlatformTiming`.

## Example

```bash
agent-lynx cdp -m Performance.getAllPerformanceEntries
```
