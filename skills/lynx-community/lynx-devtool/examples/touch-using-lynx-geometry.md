# Touch Using Lynx Geometry APIs

`Lynx.getRectToWindow` and `Lynx.getViewLocationOnScreen` are useful for diagnosing host-window geometry, but they should not be the source of click coordinates.

For clicking, prefer DOM CDP methods because they return the same logical coordinates consumed by `Input.emulateTouchFromMouseEvent`.

## 1) Use Lynx geometry only for diagnostics

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m Lynx.getRectToWindow '{"nodeId":<root_node_id>}'
agent-lynx cdp -c <client_id> -s <session_id> -m Lynx.getViewLocationOnScreen '{"nodeId":<root_node_id>}'
```

These values can help explain host app placement when a page appears visually shifted.

## 2) Compute the click point from DOM

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.getBoxModel '{"nodeId":<target_node_id>}'
```

Compute the center from `result.model.content`:

```js
const quad = result.model.content;
const xs = [quad[0], quad[2], quad[4], quad[6]];
const ys = [quad[1], quad[3], quad[5], quad[7]];
const x = (Math.min(...xs) + Math.max(...xs)) / 2;
const y = (Math.min(...ys) + Math.max(...ys)) / 2;
```

## 3) Validate and send touch

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.getNodeForLocation '{"x":<center_x>,"y":<center_y>}'
agent-lynx cdp -c <client_id> -s <session_id> -m Input.emulateTouchFromMouseEvent '{"type":"mousePressed","x":<center_x>,"y":<center_y>,"timestamp":0,"button":"left","clickCount":1}'
agent-lynx cdp -c <client_id> -s <session_id> -m Input.emulateTouchFromMouseEvent '{"type":"mouseReleased","x":<center_x>,"y":<center_y>,"button":"left","clickCount":1}'
```

## Practical tip

If geometry APIs and DOM hit-testing appear to disagree, use `DOM.getBoxModel` plus `DOM.getNodeForLocation` as the click source. For deeper debugging, see [Click Coordinate Troubleshooting](../references/troubleshooting/click-coordinates.md).
