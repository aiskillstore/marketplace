# README Preservation Checklist

Use this checklist before and after translating a README.

| Element                   | Translate?          | Preserve exactly                         | What to verify                                                    |
| ------------------------- | ------------------- | ---------------------------------------- | ----------------------------------------------------------------- |
| Headings                  | Yes, visible text   | Heading level and order                  | Same hierarchy; anchor links updated for localized headings       |
| Paragraphs and lists      | Yes                 | Markdown structure                       | Lists still nest and render like the source                       |
| Inline code               | No                  | Backticks and literal content            | Commands, flags, paths, env vars unchanged                        |
| Fenced code blocks        | No                  | Fence markers, language tags, code       | Same count and same code content                                  |
| Badge markdown            | Usually no          | Image URL, target URL, query params      | Visible label changes do not alter URL mechanics                  |
| Images                    | Alt text sometimes  | Image source URL and relative path       | Image links still resolve                                         |
| Tables                    | Yes for prose cells | Column count, separator row, alignment   | Table shape matches the source                                    |
| Raw HTML blocks           | Visible text only   | Tags, attributes, wrappers, IDs, classes | HTML still renders and custom anchors survive                     |
| GitHub alerts             | Body text only      | Alert marker such as `[!NOTE]`           | Alert syntax remains valid                                        |
| Relative file links       | Usually no          | Link destination path                    | Links still point at the same file unless intentionally localized |
| Same-file anchors         | Link text sometimes | Link intent                              | Every `(#...)` target exists after heading translation            |
| HTML comments and markers | No                  | Marker text                              | Existing selector markers remain single and intact                |

## Fast Pass

- Count code fences before and after.
- Scan for `](#` and verify each target still exists.
- Search for `README.` links and confirm selector links point at the intended siblings.
- Search for `http` and confirm badge/image URLs were not mutated.
- Search for backticks and spot-check that literal tokens stayed literal.
