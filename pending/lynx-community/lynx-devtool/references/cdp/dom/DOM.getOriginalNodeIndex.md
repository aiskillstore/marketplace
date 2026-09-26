# DOM.getOriginalNodeIndex

Scope: This method documents a LynxView-specific DOM extension. For WebView targets, use standard Chrome DevTools Protocol DOM methods instead; this method may return `method not found`.

- `DOM.getOriginalNodeIndex` - Get original node index
- Input: `{nodeId: NodeId}`
- Output: `{nodeIndex?: number}`
- Description: Returns the raw Lynx source node index stored on the resolved element.

## Notes

- `nodeIndex` is the element's `Element::NodeIndex()` value. It is not the element's position among its parent's children.
- If `nodeId` cannot be resolved, the result is an empty object and `nodeIndex` is omitted.
