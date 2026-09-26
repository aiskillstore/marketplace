# DOM.describeNode

Scope: This page documents the LynxView implementation of `DOM.describeNode`. For WebView targets, use the standard Chrome DevTools Protocol `DOM.describeNode` documentation as the source of truth for parameters and response shape.

- `DOM.describeNode` - Describe a DOM node
- Input: `{nodeId?: NodeId, backendNodeId?: BackendNodeId, depth?: number, pierce?: boolean}`
- Output: `{node?: Node | string, compress: boolean}`
- Description: Returns the requested node, optionally including descendants.

## Version Support

- Requires Lynx 3.8 or later.
- On older Lynx versions, this method may be unavailable. Use `DOM.getDocument` plus `DOM.requestChildNodes` as a fallback.

## Node Selection

- Pass either `nodeId` or `backendNodeId`.
- In Lynx DevTool, `nodeId` and `backendNodeId` are resolved through the same element id lookup.
- If both are present, `nodeId` is used.
- `objectId` is not supported by the current Lynx implementation. A request with only `objectId`, or with an unknown node id, returns an empty result without a CDP error.

## Depth

- Default depth is `1`.
- `depth: 0` returns only the requested node metadata and `childNodeCount`; `children` is omitted.
- `depth: 1` returns the requested node and its direct children.
- `depth: -1` returns the full subtree below the requested node.
- Values smaller than `-1` are treated as the default depth `1`.
- `pierce` is currently ignored.

## Important: compression behavior

- `DOM.describeNode` may return a compressed `node` value when DOM compression is enabled.
- Compression is controlled by `DOM.enable` with `useCompression` and `compressionThreshold`.
- When compression is active and the serialized `node` exceeds the threshold, `compress` is `true` and `node` is a zlib-compressed, base64-encoded string.
- If you need the full, uncompressed JSON payload, call `DOM.enable` first with `{"useCompression": false}`.

## Example

```bash
agent-lynx cdp -m DOM.describeNode '{"nodeId": 42, "depth": 0}'
```
