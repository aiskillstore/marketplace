# DOM.getBoxModel

- `DOM.getBoxModel` - Get element's box model
- Input: `{nodeId: NodeId}`
- Output: `{model: BoxModel}`
- Description: Returns the box model for the specified node in logical coordinates.

## Coordinate System

- `model.content`, `model.padding`, `model.border`, and `model.margin` are returned in CDP logical coordinates.
- These coordinates match the input space expected by:
  - `DOM.getNodeForLocation`
  - `Input.emulateTouchFromMouseEvent`

## Pairing With `Input.emulateTouchFromMouseEvent`

- Compute a target point from the box model and pass the same `x/y` to `Input.emulateTouchFromMouseEvent`.
- The safest point is usually the center of `model.content`:
  - `x = (min(content x values) + max(content x values)) / 2`
  - `y = (min(content y values) + max(content y values)) / 2`
- Validate the computed point with `DOM.getNodeForLocation` before sending Input.

## When Conversion Is Needed

- No conversion is needed when the point comes from `DOM.getBoxModel` and is used with `DOM.getNodeForLocation` or `Input.emulateTouchFromMouseEvent`.
- Avoid using screenshot pixels as click input. Find the corresponding node and recompute the point from its box model.

## Notes

- If `DOM.getNodeForLocation` validates the point but Input still misses, see [Click Coordinate Troubleshooting](../../troubleshooting/click-coordinates.md).
