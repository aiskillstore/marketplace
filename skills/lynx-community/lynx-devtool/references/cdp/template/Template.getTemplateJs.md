# Template.getTemplateJs

- `Template.getTemplateJs` - Returns a base64-encoded slice of saved template binary bytes.
- Input:
  - `offset` (integer, required): Non-negative byte offset into the saved template binary.
  - `size` (integer, required): Non-negative maximum number of bytes to read.
- Output: `{data: string}`, where `data` is the base64-encoded byte range.

## Notes

- Both fields are required. If either is missing, Lynx returns the CDP error `Params must have offset and size properties`.
- The native executor reads both values as unsigned integers; use non-negative integers only.
- Android returns a range from saved binary template data, including bytes captured after a URL template load. The returned range is clamped to the remaining available bytes.
- `data` is empty if no saved template exists, `offset` is beyond its end, or the platform delegate is unavailable. The generic embedder also returns an empty string.
