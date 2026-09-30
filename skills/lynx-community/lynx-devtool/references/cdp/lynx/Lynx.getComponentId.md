# Lynx.getComponentId

Scope: This is a LynxView-specific CDP extension. For WebView targets, use
standard Chrome DevTools Protocol DOM and runtime methods instead; this method
may return `method not found`.

- `Lynx.getComponentId` - Get the component id for a DevTool node
- Input: `{nodeId: integer}`
- Output: `{componentId: string | integer}`
- Description: Returns the component id for a component node. Returns the integer
  `-1` if the node is missing or is not a component node.

## Notes

- The `nodeId` is resolved in the current Lynx element tree.
- Component ids are strings. The fallback `-1` is an integer, so callers must
  handle the mixed result type.
- If the TASM task runner is unavailable, the current handler does not send an
  explicit CDP response.

## Example

```bash
agent-lynx cdp -m Lynx.getComponentId '{"nodeId":42}'
```
