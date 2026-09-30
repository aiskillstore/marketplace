# Lynx.getProperties

Scope: This is a LynxView-specific CDP extension. For WebView targets, use
standard Chrome DevTools Protocol DOM and runtime methods instead; this method
may return `method not found`.

- `Lynx.getProperties` - Get serialized component properties
- Input: `{nodeId: integer}`
- Output: `{properties: string}`
- Description: Returns serialized properties for a component node. Returns an
  empty string if the node is missing, is not a component node, or no properties
  are available.

## Notes

- The `nodeId` is resolved in the current Lynx element tree.
- The current native component-properties helper returns an empty string.
- If the TASM task runner is unavailable, the current handler does not send an
  explicit CDP response.

## Example

```bash
agent-lynx cdp -m Lynx.getProperties '{"nodeId":42}'
```
