# Lynx.getViewLocationOnScreen

Scope: This is a LynxView-specific CDP extension. For WebView targets, use standard Chrome DevTools Protocol geometry and DOM methods instead; this method may return `method not found`.

- `Lynx.getViewLocationOnScreen` - Get view location on screen
- Input: None
- Output: `{x: number, y: number}`
- Description: Returns the Lynx view origin in screen-like coordinates.

The native handler does not read request parameters. If the platform cannot
provide two coordinates, it returns `{x: -1, y: -1}`.

## Coordinate System

- This API provides the LynxView origin in screen-like coordinates.

## Pairing With `Input.emulateTouchFromMouseEvent`

- Do not use this API as the source of click coordinates.
- For reliable clicks, find the target node and compute the point with `DOM.getBoxModel`.
- Use `DOM.getNodeForLocation` to validate that point, then pass the same `x/y` to `Input.emulateTouchFromMouseEvent`.

## Typical Use Cases

- Confirm the LynxView origin when debugging host window geometry.
- Diagnose why screenshot-based visual inspection does not match DOM hit-testing.

## Notes

- For coordinate debugging, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).
