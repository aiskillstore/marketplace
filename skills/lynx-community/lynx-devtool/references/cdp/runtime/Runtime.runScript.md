# Runtime.runScript

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.runScript` - Runs script with given id in a given context.
- Input:
  - `scriptId` (string | integer): Required. Id of the script to run (generated previously by compileScript).
  - `executionContextId` (integer, optional): Optional. Specifies in which execution context to perform script run.
  - `silent` (boolean, optional): Optional. In silent mode exceptions thrown during evaluation are not reported and do not pause execution.
  - `generatePreview` (boolean, optional): Optional. Whether preview should be generated for the result.
- Output:
  - `result` (RemoteObject): Run result.
  - `exceptionDetails` (ExceptionDetails, optional): Exception details.
- Description: Runs a previously compiled and persisted script using its `scriptId`.

## Notes

- On the tested Android Lynx runtime, an unknown or missing `scriptId` can return `{result: {type: "undefined"}}` instead of a CDP error.
