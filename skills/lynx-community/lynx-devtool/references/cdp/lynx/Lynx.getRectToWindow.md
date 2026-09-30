# Lynx.getRectToWindow

Scope: This is a LynxView-specific CDP extension. For WebView targets, use standard Chrome DevTools Protocol geometry and DOM methods instead; this method may return `method not found`.

- `Lynx.getRectToWindow` - Get rectangle relative to window
- Input: None
- Output: `{left: number, top: number, width: number, height: number}`
- Description: Returns the LynxView rectangle relative to its containing window.

The native handler does not read request parameters. Android obtains the root UI
rectangle from `UITreeHelper`; Darwin obtains the root UI rectangle and scales it
by the screen scale.

## Coordinate System

- The returned rectangle is intended for window/screen-space workflows (for example fullscreen capture alignment), not direct touch injection coordinates.

## Pairing With `Input.emulateTouchFromMouseEvent`

- Do not use this API as the source of click coordinates.
- For reliable clicks, find the target node and compute the point with `DOM.getBoxModel`.
- Use `DOM.getNodeForLocation` to validate that point, then pass the same `x/y` to `Input.emulateTouchFromMouseEvent`.

## Typical Use Cases

- Check where the Lynx root sits in the host window.
- Debug visual mismatches between screenshots and DOM hit-testing.

## Notes

- For coordinate debugging, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).
