# DOM.getDocument

- `DOM.getDocument` - Get document root node
- Input: `{depth?: number}`
- Output: `{compress: boolean, root: Node | string}`
- Description: Returns the root node of the document tree, optionally including descendants.

## Version Support

- `depth` requires Lynx 3.8 or later.
- On older Lynx versions, `depth` may be ignored or unavailable. Use `DOM.requestChildNodes` as a fallback when you need to expand children incrementally.

## Depth

- Without `depth`, Lynx returns the runtime's default document tree shape.
- `depth: 0` returns the document root and top-level metadata without expanding deeper descendants. Because `#document` and the page node are synthetic in Lynx, the top-level page node may still appear while its `children` are omitted.
- `depth: 1` returns one level of descendants below the document/page wrapper.
- Larger positive values include additional descendant levels.
- `depth: -1` returns the full subtree.

## Important: compression behavior

- `DOM.getDocument` may return a compressed result in some cases.
- When `compress` is `true`, `root` is a zlib-compressed, base64-encoded string.
- If you need the full, uncompressed JSON payload, call `DOM.enable` first with `{"useCompression": false}`.
- Recommended call order:
  1. `DOM.enable` with `{"useCompression": false}`
  2. `DOM.getDocument`

## Example

```bash
agent-lynx cdp -m DOM.getDocument '{"depth": -1}'
```
