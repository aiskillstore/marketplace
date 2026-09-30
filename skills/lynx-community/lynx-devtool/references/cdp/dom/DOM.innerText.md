# DOM.innerText

Scope: This method documents a LynxView-specific DOM extension. For WebView targets, use standard Chrome DevTools Protocol DOM or Runtime methods instead; this method may return `method not found`.

- `DOM.innerText` - Get inner text
- Input: `{nodeId: NodeId}`
- Output: `{nodeId: NodeId, rawTextValues: Array<{nodeId: NodeId, text: string}>}`
- Description: Returns raw text values from direct raw-text children of a Lynx `text` element.

## Notes

- The method does not calculate visible text or concatenate text values.
- It only inspects attached elements whose local name is `text`, then reads the `text` attribute of their direct raw-text children.
- For a missing, detached, or non-`text` node, the response retains the requested `nodeId` and has an empty `rawTextValues` array.
