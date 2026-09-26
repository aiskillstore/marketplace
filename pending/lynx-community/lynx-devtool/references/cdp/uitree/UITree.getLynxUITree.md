# UITree.getLynxUITree

> Note: Call `UITree.enable` on the same session before invoking this CDP method.

- `UITree.getLynxUITree` - Get the rendered Lynx UI tree with native UI metadata.
- Input: None
- Output:
  - `root` (object | string | null): The root node of the native UI tree when uncompressed; a base64-encoded compressed string when `compress` is `true`; or `null` when the platform has no tree string. An uncompressed root can contain:
    - `name` (string): The native class name (e.g. `com.lynx.tasm.behavior.ui.LynxUI`).
    - `id` (number): The native node identifier.
    - `tagName` (string, optional): The Lynx element tag name (e.g. `view`, `text`). Present on Android and Darwin.
    - `nodeIndex` (number, optional): The index mapping back to the DOM node. Present on Android and Darwin.
    - `props` (object, optional): Key-value pairs of element properties. Present on Android and Darwin.
    - `label` (string, optional): A human-readable label when the platform provides one.
    - `frame` (array): Bounding box as `[x, y, width, height]`.
    - `children` (array): Child nodes with the same structure.
  - `compress` (boolean): Whether `root` was compressed and base64-encoded by the native handler.
- Description: Returns the full rendered native UI tree. Android and Darwin provide `name`, `id`, `tagName`, `nodeIndex`, `props`, `label`, `frame`, and `children`; Harmony provides `name`, `id`, `frame`, and `children`.
