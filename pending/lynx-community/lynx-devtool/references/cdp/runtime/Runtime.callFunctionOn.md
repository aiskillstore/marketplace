# Runtime.callFunctionOn

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.callFunctionOn` - Calls function with given declaration on the given object. Object group of the result is inherited from the target object.
- Input:
  - `functionDeclaration` (string): Required. Declaration of the function to call (e.g., `"(function() { return this.x; })"`).
  - `objectId` (string, optional): Optional. Specified `this` object. If provided, `this` is bound to this object during execution; if omitted, it will attempt to use the `executionContextId` below to execute with the global object.
  - `executionContextId` (integer, optional): Optional. If `objectId` is not provided, this ID specifies the global context to use.
  - `arguments` (array of CallArgument, optional): Implicitly supported. Call arguments arrays to pass to the function.
  - `returnByValue` (boolean, optional): Implicitly supported. Whether the result is expected to be a JSON object which should be sent by value.
- Output:
  - `result` (RemoteObject): Call result.
  - `exceptionDetails` (ExceptionDetails, optional): Exception details.
- Description: Calls a specified function declaration using a target object as the `this` context (or the global scope).

## Notes

- Wrap anonymous function declarations in parentheses, or use a named function. A bare `function() { ... }` string is not handled reliably by the current Lynx runtime.
