# Touch Using DOM Coordinates

This example shows the recommended flow: get the target point from CDP DOM methods and pass that same point to `Input.emulateTouchFromMouseEvent`.

## Why this works

- `DOM.getBoxModel`, `DOM.getNodeForLocation`, and `Input.emulateTouchFromMouseEvent` use the same CDP logical coordinate space for the current mode.
- No screenshot pixel conversion is needed when the point comes from DOM.

## 1) Find the target node

Get the document root:

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.getDocument '{"depth":0}'
```

Query a stable selector under the root node:

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.querySelector '{"nodeId":<root_node_id>,"selector":"[lynx-test-tag=\"target\"]"}'
```

## 2) Scroll it into view

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.scrollIntoViewIfNeeded '{"nodeId":<target_node_id>}'
```

## 3) Compute a center point from `DOM.getBoxModel`

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.getBoxModel '{"nodeId":<target_node_id>}'
```

Use `result.model.content`, which is a quad:

```js
const quad = result.model.content;
const xs = [quad[0], quad[2], quad[4], quad[6]];
const ys = [quad[1], quad[3], quad[5], quad[7]];
const x = (Math.min(...xs) + Math.max(...xs)) / 2;
const y = (Math.min(...ys) + Math.max(...ys)) / 2;
```

## 4) Validate the point

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m DOM.getNodeForLocation '{"x":<center_x>,"y":<center_y>}'
```

If the returned `nodeId` is the target you expect, use the same point for touch.

## 5) Tap with the same coordinates

```bash
agent-lynx cdp -c <client_id> -s <session_id> -m Input.emulateTouchFromMouseEvent '{"type":"mousePressed","x":<center_x>,"y":<center_y>,"timestamp":0,"button":"left","clickCount":1}'
agent-lynx cdp -c <client_id> -s <session_id> -m Input.emulateTouchFromMouseEvent '{"type":"mouseReleased","x":<center_x>,"y":<center_y>,"button":"left","clickCount":1}'
```
