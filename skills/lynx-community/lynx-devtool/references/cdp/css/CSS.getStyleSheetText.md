# CSS.getStyleSheetText

- `CSS.getStyleSheetText` - Get stylesheet text
- Input: `{styleSheetId: StyleSheetId}`
- Output: `{text: string}`
- Description: Returns the current serialized CSS rules for the stylesheet associated with `styleSheetId`.

## Notes

- Obtain `styleSheetId` from CSS data such as `CSS.getMatchedStylesForNode`.
- LynxView reconstructs the returned text from its current CSS rule data; it is not necessarily the original source-file text or formatting.
- If `styleSheetId` does not resolve to an element, the current handler returns `{error: {code: -32000, message: "Node is not an Element"}}` in the result instead of `text`.
