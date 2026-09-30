# CSS.getMediaQueries

- `CSS.getMediaQueries` - Get media queries
- Input: None
- Output: `{medias: Array<CSSMedia>}`
- Description: Returns media queries discovered in the current Lynx element tree.

## LynxView response shape

- Each returned item has `text`, `source: "mediaRule"`, and `range`.
- `styleSheetId` is present when Lynx can associate the query with a style-value element.
- `range` is a synthetic locator: its line number is the query's zero-based index within that stylesheet, and its end column is the length of `text`. It is not a source-file location.
- The current handler returns media-rule descriptors only. It does not populate the standard optional `sourceURL` or `mediaList` fields.
