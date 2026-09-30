# DOM.focus

Scope: This page documents the LynxView implementation of `DOM.focus`. For WebView targets, use the standard Chrome DevTools Protocol `DOM.focus` documentation as the source of truth.

- `DOM.focus` - Focus a node
- Input: `{nodeId: NodeId}`
- Output: `{}`
- Description: Requests focus for the UI element represented by the specified node.

## Usage

Use a `nodeId` returned by `DOM.getDocument`, `DOM.querySelector`, or another DOM lookup method:

```bash
agent-lynx cdp -m DOM.focus '{"nodeId": 42}'
```

To insert text, focus the input and then call `Input.insertText`:

```bash
agent-lynx cdp -m DOM.focus '{"nodeId": 42}'
agent-lynx cdp -m Input.insertText '{"text": "hello"}'
```

## Supported Node Identifiers

- LynxView supports only the required numeric `nodeId` parameter.
- `backendNodeId` and `objectId`, which may be accepted by standard CDP implementations, are not supported here.
- If the requested node is virtual or layout-only, Lynx resolves it to the nearest ancestor with a native UI element and requests focus for that ancestor.

## Errors And Platform Support

- Missing or non-numeric `nodeId` returns CDP error `-32602` with the message `DOM.focus requires a numeric nodeId parameter.`
- A node that cannot be resolved, including one whose ancestor chain has no native UI element, returns CDP error `-32000` with the message `Element not found.`
- Native focus handling is implemented for Android and iOS LynxView targets. On other LynxView platforms, the request may return `{}` without changing focus.
- A successful `{}` response confirms that the focus request was dispatched. Native focus rejection is reported only in platform logs, not as a CDP error.
