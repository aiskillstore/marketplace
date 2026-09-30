# DOM.getDocumentWithBoxModel

Scope: This method documents a LynxView-specific DOM extension. For WebView targets, use standard Chrome DevTools Protocol DOM methods instead; this method may return `method not found`.

- `DOM.getDocumentWithBoxModel` - Get document with box model
- Input: None
- Output: `{compress: boolean, root: NodeWithBoxModel | string}`
- Description: Returns document with layout box model information

## Important: compression behavior

- `DOM.getDocumentWithBoxModel` may return a compressed result in some cases.
- When `compress` is `true`, `root` is a zlib-compressed, base64-encoded string.
- Box model data is nested on returned DOM nodes, not returned as a top-level `nodes` array.
- If you need the full, uncompressed JSON payload, call `DOM.enable` first with `{"useCompression": false}`.
- Recommended call order:
  1. `DOM.enable` with `{"useCompression": false}`
  2. `DOM.getDocumentWithBoxModel`
