# Overlay.highlightNode

- `Overlay.highlightNode` - Highlight node
- Input: `{nodeId: NodeId, highlightConfig?: HighlightConfig}`
- Output: `{}`
- Description: Highlights the specified DOM node in the page

## Notes

- The `nodeId` must identify an element node. Passing the document/root node can return `{error: {code: -32000, message: "Node is not an Element"}}`.
