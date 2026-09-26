# Page.getResourceContent

Scope: The input shape is the standard CDP shape. The LynxView behavior below differs from a browser resource lookup.

- `Page.getResourceContent` - Get resource content
- Input: `{frameId: FrameId, url: string}`
- Output: `{content: string, base64Encoded: boolean}`
- Description: Returns content for a page resource.

## LynxView behavior

- The current handler ignores both `frameId` and `url`. It serializes the current element root instead of looking up a resource by URL.
- `content` is an empty string when no element root is available.
- `base64Encoded` is always `false`.

### Screencast
