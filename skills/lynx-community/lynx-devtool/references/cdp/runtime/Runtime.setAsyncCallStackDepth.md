# Runtime.setAsyncCallStackDepth

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.setAsyncCallStackDepth` - Enables or disables async call stacks tracking.
- Input:
  - `maxDepth` (integer): Maximum depth of async call stacks. Setting to `0` will effectively disable collecting async call stacks (default).
- Output: `{}`
- Description: Sets the depth limit for capturing asynchronous call stacks. Passing 0 turns off async call stack tracking.
