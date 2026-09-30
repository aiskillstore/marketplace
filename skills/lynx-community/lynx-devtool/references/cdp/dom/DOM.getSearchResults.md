# DOM.getSearchResults

- `DOM.getSearchResults` - Get search results
- Input: `{searchId: number | string, fromIndex: number, toIndex: number}`
- Output: `{nodeIds: Array<NodeId>}`
- Description: Returns search results for the specified range
- Compatibility: `searchId` accepts `number` on older Lynx versions and `string` on Lynx 3.7+
- Important: Use the exact `searchId` returned by `DOM.performSearch` without coercing or converting its type
