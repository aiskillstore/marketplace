# DOM.performSearch

- `DOM.performSearch` - Perform search
- Input: `{query: string, includeUserAgentShadowDOM?: boolean}`
- Output: `{searchId: number | string, resultCount: number}`
- Description: Searches for nodes in the DOM tree
- Compatibility: `searchId` is `number` on older Lynx versions and `string` on Lynx 3.7+
