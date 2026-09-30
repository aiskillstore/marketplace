# LayerTree.compositingReasons

- `LayerTree.compositingReasons` - Returns the Lynx element name and node ID associated with a layer ID.
- Input: `{layerId: string}`. The value must be a decimal element node ID, as exposed by Lynx's `LayerTree.layerTreeDidChange` event.
- Output:
  - `compositingReasons` (string array): Contains the element's local tag name when the element exists; otherwise an empty array.
  - `compositingReasonsIds` (number array): Contains the element's node ID when the element exists; otherwise an empty array.

## Lynx behavior

- Lynx does not return Chromium's compositing-reason descriptions or reason IDs. It returns one element name and one node ID instead.
- The second output key is `compositingReasonsIds` in the current Lynx implementation. This differs from the upstream CDP key `compositingReasonIds`.
- The handler parses `layerId` as an integer. Do not pass opaque Chrome layer IDs.
