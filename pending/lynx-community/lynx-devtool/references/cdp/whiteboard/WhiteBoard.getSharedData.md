# WhiteBoard.getSharedData

Scope: This is a LynxView-specific CDP extension. For WebView targets, use standard Chrome DevTools Protocol storage/runtime APIs instead; this method may return `method not found`.

- `WhiteBoard.getSharedData` - Get all shared data entries
- Input: None
- Output: `{entries: Array<{key: string, value: string}>}`
- Description: Returns all current WhiteBoard shared data records.

### Notes

- Each `value` in `entries` is returned as a serialized JSON string.
