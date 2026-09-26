# SystemInfo.getInfo

- `SystemInfo.getInfo` - Returns the platform's device model string and Lynx platform name.
- Input: None.
- Output:
  - `modelName` (string): Value supplied by the platform's DevTool facade.
  - `platform` (`"Android"` | `"iOS"`): Platform selected by the native build.

## Lynx behavior

- Lynx does not populate the standard CDP `gpu`, `modelVersion`, or `commandLine` fields for this method.
- The command is handled synchronously by the global DevTool mediator and can be sent without an active LynxView-specific data query.
