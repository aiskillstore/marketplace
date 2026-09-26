# WhiteBoard.setSharedData

Scope: This is a LynxView-specific CDP extension. For WebView targets, use standard Chrome DevTools Protocol storage/runtime APIs instead; this method may return `method not found`.

- `WhiteBoard.setSharedData` - Set or update a shared data entry
- Input: `{key: string, value: string}`
- Output: `{}`
- Description: Writes the given key/value pair into WhiteBoard shared data. The `value` must be a valid serialized JSON string.

### Notes

- If `key` does not exist, WhiteBoard adds a new entry.
- If `key` already exists, WhiteBoard updates the existing entry.
- If `value` is not a valid JSON string, the protocol returned `{"error":{"code":-32602,"message":"The value must be a valid JSON string!"},"id":...}`.
- Returned and emitted values may be re-serialized by WhiteBoard, so JSON formatting and field order may differ from the original input string.
