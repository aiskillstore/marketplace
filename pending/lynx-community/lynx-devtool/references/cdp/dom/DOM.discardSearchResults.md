# DOM.discardSearchResults

- `DOM.discardSearchResults` - Discard search results
- Input: `{searchId: number | string}`
- Output: `{}`
- Description: Discards search results and frees resources
- Compatibility: `searchId` accepts `number` on older Lynx versions and `string` on Lynx 3.7+
- Important: Use the exact `searchId` returned by `DOM.performSearch` without coercing or converting its type

### View Operations
