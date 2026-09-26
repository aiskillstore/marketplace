# DOM.getNodeForLocation

- `DOM.getNodeForLocation` - Get node by location
- Input: `{x: number, y: number}`
- Output: `{nodeId: NodeId, backendNodeId: BackendNodeId}`
- Description: Returns the node at the specified logical coordinates.

## Coordinate System

- `x` and `y` use CDP logical coordinates.
- These coordinates match `DOM.getBoxModel` and `Input.emulateTouchFromMouseEvent` for the current mode.
- This API is the safest way to validate a target point before sending touch events.

## Pairing With `Input.emulateTouchFromMouseEvent`

- If `DOM.getNodeForLocation` returns the expected node, pass the same `x/y` directly to `Input.emulateTouchFromMouseEvent`.
- Do not apply screenshot pixel scaling to DOM-derived points.

## Common Sources And Conversion

- From `DOM.getBoxModel`:
  - Use directly for `DOM.getNodeForLocation`.
  - Use directly for `Input.emulateTouchFromMouseEvent`.
- From screenshot pixels or `Lynx.getRectToWindow`:
  - Do not use them as the primary source for clicks.
  - Instead, identify the target node and recompute the point with `DOM.getBoxModel`.

## Empty Or Zero Result

A result like `{nodeId: 0, backendNodeId: 0}` should be treated as "no reliable node was hit".

Recommended checks:

1. Use `DOM.getBoxModel` to compute the center of a known visible node.
2. Pass that logical center directly to `DOM.getNodeForLocation`.
3. If validation works but Input misses, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).

## Notes

- This method is a validation step for clicks; do not skip it when automating touch input.
