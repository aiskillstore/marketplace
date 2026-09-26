# Runtime.compileScript

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.compileScript` - Compiles expression.
- Input:
  - `expression` (string): Required. The JavaScript source string to compile.
  - `sourceURL` (string, optional): Source url to be set for the script, convenient for subsequent identification in the Source panel.
  - `persistScript` (boolean, optional): Specifies whether the compiled script should be persisted in the engine (kept for subsequent repeated calls via runScript).
  - `executionContextId` (integer, optional): Optional. Specifies in which execution context to perform script compilation.
- Output:
  - `scriptId` (ScriptId, optional): Id of the script.
  - `exceptionDetails` (ExceptionDetails, optional): Exception details.
- Description: Compiles a JavaScript script string into bytecode without immediately executing it, typically used to pre-check syntax errors and generate a `scriptId`.

## Notes

- Use `persistScript: true` when you need a `scriptId` for `Runtime.runScript`. Without persistence, the command can return `{}`.
- On the tested Android main-thread VM, `Runtime.compileScript` may return `scriptId: "-1"`; running that id returns `undefined`. Use the background thread for persisted script workflows when you need the compiled script to execute.
