# WhiteBoard Methods

Scope: The `WhiteBoard.*` methods are LynxView-specific CDP extensions for Lynx shared data. For WebView targets, use standard Chrome DevTools Protocol storage/runtime APIs instead; these methods may return `method not found`.

The `WhiteBoard` domain provides access to Lynx shared global data. Values are read and written as serialized JSON strings.

## Related APIs

- `lynx.getSessionStorageItem`
- `lynx.setSessionStorageItem`
- `lynx.subscribeSessionStorage`
- `lynx.unsubscribeSessionStorage`

## Methods

- [WhiteBoard.enable](WhiteBoard.enable.md) - Enable WhiteBoard domain events
- [WhiteBoard.disable](WhiteBoard.disable.md) - Disable WhiteBoard domain events
- [WhiteBoard.setSharedData](WhiteBoard.setSharedData.md) - Create or update a shared data entry
- [WhiteBoard.getSharedData](WhiteBoard.getSharedData.md) - Get all shared data entries
- [WhiteBoard.removeSharedData](WhiteBoard.removeSharedData.md) - Remove a shared data entry by key
- [WhiteBoard.clear](WhiteBoard.clear.md) - Clear all shared data entries
