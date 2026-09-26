# Input.emulateTouchFromMouseEvent

- `Input.emulateTouchFromMouseEvent` - Emulate touch from mouse event
- Input: `{type: string, x: number, y: number, timestamp: number, button: string, clickCount?: number, deltaX?: number, deltaY?: number}`
- Output: `{}`
- Description: Converts mouse-style coordinates into touch events for testing touch interactions.

## Coordinate System

- `x` and `y` are CDP logical coordinates.
- Use the same `x/y` produced by `DOM.getBoxModel` and validated by `DOM.getNodeForLocation`.
- Do not use screenshot pixel positions for clicks.

## How To Pair With Other Coordinate APIs

- `DOM.getBoxModel`:
  - Compute the center of `model.content` or `model.border`.
  - Pass the computed logical `x/y` directly to Input.
- `DOM.getNodeForLocation`:
  - Validate the same logical `x/y` before tapping.
  - Treat `{nodeId: 0}` as "no reliable target hit".
- `DOM.scrollIntoViewIfNeeded`:
  - Use it before `DOM.getBoxModel` when the target may be outside the visible area.
- `Lynx.getRectToWindow`, `Lynx.getViewLocationOnScreen`, and screenshots:
  - Use these for diagnostics or visual alignment only, not as the source of click coordinates.

## Practical CDP Click Recipe

1. Get the root node with `DOM.getDocument`.
2. Find the target node with `DOM.querySelector` or `DOM.performSearch`.
3. Call `DOM.scrollIntoViewIfNeeded` for the target node.
4. Call `DOM.getBoxModel` for the target node.
5. Compute a center point from the returned quad:
   - `x = (min(content x values) + max(content x values)) / 2`
   - `y = (min(content y values) + max(content y values)) / 2`
6. Call `DOM.getNodeForLocation` with the same `x/y` and confirm the expected node.
7. Send `mousePressed` and `mouseReleased` with the same `x/y`.

## Notes

- If the validated point still misses, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).
