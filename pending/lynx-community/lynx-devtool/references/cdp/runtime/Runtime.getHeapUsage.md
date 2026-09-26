# Runtime.getHeapUsage

> Note: Call `Runtime.enable` on the same session and thread before invoking this CDP method.

- `Runtime.getHeapUsage` - Returns the JavaScript engine's heap usage.
- Input: None
- Output:
  - `usedSize` (number): Used heap size in bytes.
  - `totalSize` (number): Allocated heap size in bytes.
- Description: Gets the heap memory usage of the current JavaScript engine (such as used memory size and memory limit).
