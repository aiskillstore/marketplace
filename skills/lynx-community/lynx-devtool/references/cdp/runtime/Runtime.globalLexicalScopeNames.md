# Runtime.globalLexicalScopeNames

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.globalLexicalScopeNames` - Returns all let, const and class variables from global scope.
- Input:
  - `executionContextId` (integer, optional): Required (or defaults). Specifies in which execution context to lookup global scope variables (such as global variables defined by let/const).
- Output:
  - `names` (array of string): Names of the global lexical scope variables.
- Description: Returns all variable names in the global lexical scope.
