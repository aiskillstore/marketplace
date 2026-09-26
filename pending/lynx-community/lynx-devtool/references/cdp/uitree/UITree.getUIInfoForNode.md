# UITree.getUIInfoForNode

> Note: Call `UITree.enable` on the same session before invoking this CDP method.

- `UITree.getUIInfoForNode` - Get detailed platform UI information for one node
- Input: `{UINodeId: integer}`
- Output: Platform-owned UI information for the requested node
- Description: Returns detailed platform UI information. Android, Darwin, and
  Harmony expose different fields, so callers must tolerate missing fields.

## Output

- `id` (integer, optional): Platform UI node id.
- `isFlatten` (boolean, optional): Android-only flattened-node flag.
- `editableProps` (object, optional): Editable platform UI properties, including
  `border`, `margin`, `frame`, and `visible` when supplied by the platform.
- `readonlyProps` (object, optional): Android root-level readonly properties.
- `ui` (object, optional): Platform UI object metadata, including `name` and
  reflection-derived `readonlyProps` when present.
- `view` (object, optional): Backing view metadata, including `name` and
  reflection-derived `readonlyProps` when present.
- `layers` (object, optional): Darwin layer metadata for the view and Lynx
  background or border layers.

## Behavior

- The platform UI node id is passed as `UINodeId` (capital `UI`).
- If the platform returns an empty string or cannot resolve the node, the result
  is an empty object.
- If UI tree inspection is not enabled, the current handler returns without
  sending a CDP response.

## Example

```bash
agent-lynx cdp -m UITree.getUIInfoForNode '{"UINodeId":42}'
```
