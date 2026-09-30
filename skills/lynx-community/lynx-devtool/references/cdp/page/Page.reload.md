# Page.reload

- `Page.reload` - Reload page
- Input: `{ignoreCache?: boolean, url?: string}`
- Output: `{}`
- Description: Reloads the current page. Can ignore cache, or use specific template URL for reloading.

### URL Parameter Requirements

- **Protocol**: Must start with `http` (supports HTTP or HTTPS).
- **Format**: Must be a valid URL string.

### Examples

**Reload with specific URL:**

```json
{
  "url": "http://example.com/template.js",
  "ignoreCache": true
}
```

> Note that the `url` in `list-sessions` would not change after `Page.reload`.
