# Click Coordinate Troubleshooting

Use this page only when the standard click flow fails:

1. Find the target node with `DOM.querySelector`, `DOM.performSearch`, or `DOM.getDocument`.
2. Call `DOM.scrollIntoViewIfNeeded`.
3. Call `DOM.getBoxModel` and compute the center of `model.content` or `model.border`.
4. Validate the point with `DOM.getNodeForLocation`.
5. Send `Input.emulateTouchFromMouseEvent` with the same `x/y`.

## Fast Rules

- Do not pick click positions from screenshots.
- Do not apply density, DPR, scale, or platform-specific conversion yourself.
- Do not use `Lynx.getRectToWindow` or `Lynx.getViewLocationOnScreen` as the source of click coordinates.
- Recompute the box model after scrolling, page reloads, layout changes, or opening a new session.
- If `DOM.getNodeForLocation` returns `{nodeId: 0}`, do not send Input yet.

## If `DOM.getNodeForLocation` Returns `0`

Common causes:

- The point is outside the visible Lynx view.
- The target is hidden, detached, or not laid out yet.
- The target is covered by an overlay.
- The point was derived from a screenshot or host-window geometry instead of DOM geometry.
- The page changed after `DOM.getBoxModel` was read.

Checks:

1. Call `DOM.scrollIntoViewIfNeeded` for the target node.
2. Call `DOM.getBoxModel` again.
3. Use the center of `model.content` first; if it is too small or empty, try `model.border`.
4. Validate that exact point with `DOM.getNodeForLocation`.
5. If the returned node is an overlay, query the overlay node and compute its target point instead.

## If Validation Works But Input Misses

Checks:

1. Ensure no screenshot command or `Page.startScreencast` changed coordinate mode between validation and Input.
2. Ensure the page did not relayout between validation and Input.
3. Send `mousePressed` and `mouseReleased` with exactly the same `x/y`.
4. Prefer the programmatic stream example so the two Input messages are delivered back-to-back.
5. Rerun `list-sessions`; stale sessions can make a correct point target the wrong page.

## Platform Notes

These details explain why callers should not do their own conversion:

- Android receives CDP logical `x/y`, multiplies by display density internally, and dispatches native `MotionEvent`.
- In Android `fullscreen` mode, the touch helper subtracts the LynxView physical screen origin internally before dispatch.
- iOS devtoolng receives CDP logical `x/y`; in `lynxview` mode it converts the point to the key window before sending synthesized `UIEvent` touches.
- `DOM.getNodeForLocation` and `DOM.getBoxModel` use the corresponding engine-side layout-unit conversions, so DOM-derived `x/y` should be passed directly to Input.

## Screenshot Mismatch

Screenshots are still useful for visual inspection. If a screenshot appears to disagree with DOM hit-testing:

- trust `DOM.getBoxModel` plus `DOM.getNodeForLocation` for clicking;
- use screenshots only to check visibility, overlays, or obvious layout changes;
- avoid converting screenshot pixels back into click coordinates unless you are explicitly debugging engine coordinate internals.
