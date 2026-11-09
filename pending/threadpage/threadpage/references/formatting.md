# Formatting ThreadPage notes

A Note is a rich document: headings, paragraphs, lists, checklists, quotes, tables, code, links, images, files and Note references. Write new content as **Markdown** (recommended). Send a **document** (JSON, below) when you edit an existing note or need what Markdown cannot express.

## Content forms

Every tool that takes `content` (`create_note`, `update_note`, `complete_request`, the `question` of `report_request_status`) accepts exactly one of:

| You send | Read as |
| --- | --- |
| `"## Plan\n- [ ] Ship"` (a string) | Markdown |
| `{"markdown": "…"}` | Markdown |
| `{"text": "…"}` | Plain text: blank lines separate paragraphs, single line breaks stay, nothing else is interpreted as formatting; an address written in it becomes a link, as in Markdown |
| `{"document": {…}}` | A ThreadPage document (RichDocument v4), exactly as written |

Limits: Markdown up to 32 KiB; any note up to 256 KiB as a document. Markdown longer than 500 lines, with more than 500 of the characters `` * _ ~ ` < [ ``, tables over 2,000 cells in total, or quotes nested deeper than 8 levels is refused with `invalid_content`: split it into several notes or send a document.

## Markdown

| Markdown | In the note |
| --- | --- |
| `# Title` · `## Heading` · `### Subheading` | Title, Heading, Subheading. `####` and deeper become Subheading |
| Text, a blank line, more text | Two paragraphs. A single line break stays a line break |
| `**bold**` `*italic*` `~~strike~~` `` `code` `` | Bold, italic, strikethrough, monospace |
| `[label](https://example.com)` · `<https://example.com>` · `[mail](mailto:a@example.com)` | Links (http, https, mailto only). An address written as text becomes a link too, as in the app: `https://…`, `www.…` (over https) and `name@example.com`; a bare domain such as `example.com` stays text, and punctuation after an address stays outside the link |
| `- item` (or `*`, `+`); nest under the item's text: 2 spaces after `- `, 3 after `1. ` | Bulleted list, up to 8 levels |
| `1. item` (`3.` starts at 3) | Numbered list |
| `- [ ] open` · `- [x] done` | Checklist. Every item of that list needs a box, or the boxes stay text |
| `> quoted text` | Quote (top level only) |
| ```` ```bash ```` … ```` ``` ```` or 4-space indent | Monostyled lines (code). The language tag is ignored |
| A pipe table with a `\| --- \|` row | Table; the first row is the header row |
| `![description](attachment:<attachment_id>)` on its own line | Image (upload it first, see Images) |
| `[name](attachment:<file_id>)` on its own line | File (upload it first, see Files) |
| A ThreadPage note link on its own line | Note reference block (see Note references) |

Tables: one line of text per cell (bold, italic, code and links work); write `\|` for a literal pipe. Every row gets the header row's number of cells: missing cells stay empty, extra cells are dropped. Column alignment and merged cells are not supported.

Not available in Markdown: HTML (shown as text), horizontal rules (a `---` line after a blank line is dropped; right under a line of text it turns that text into a Heading), footnotes, images from web URLs (they become a link), headings, lists or tables inside quotes and headings or tables inside list items (they become plain lines), underline, text colour, highlight, font size, alignment, tags. `@Name` and `#word` stay plain text: you cannot address a note to anyone, and tags need a document.

Example:

````markdown
## QA results — 1.4

| Check | Result | Notes |
| --- | --- | --- |
| Smoke tests | **Passed** | all 42 green |
| Payments sandbox | **Failed** | card declined on retry |

Next steps:

- [ ] Fix payment retry
- [ ] Re-run sandbox
- [x] Tag the build

```bash
git tag v1.4.0 && git push --tags
```

> Never deploy on Friday.

https://thread.page/app/notes/0b7f6a62-5d3c-4f0e-9a51-6f2f1c8d4e21
````

## Note references

A Note reference is a block that shows another note (its Thread, date and first lines) and opens it. It never grants access to the note it shows.

- In Markdown, put a ThreadPage note link **alone on its own line**: `https://thread.page/app/notes/<note_id>`, `<https://thread.page/app/notes/<note_id>>` or `[any label](https://thread.page/app/notes/<note_id>)`. It becomes a reference block between the paragraphs around it; the label is not kept. A note link inside a sentence stays an ordinary link.
- In a document: `{"type": "entryReference", "attrs": {"entryId": "<note_id>"}}`, a top-level block only.
- Use the `id` of a note you found with `search`, `get_thread` or `get_note`. A reference to a note that is deleted or outside someone's access shows as unavailable.

## Images

1. `upload_note_image` with the image as base64 (PNG, JPEG or WebP, up to 5 MB and 20 megapixels), its lowercase hex SHA-256 as `checksum`, the `thread_id` of the note it goes in and, when that note already exists, its `note_id`. Never pass a URL: ThreadPage does not fetch from the web. The base64 passes through your own output, so keep images small or ask the person to add a large one.
2. Place the returned `attachment_id` on its own line: `![What the image shows](attachment:<attachment_id>)` — or as a document block `{"type": "image", "attrs": {"attachmentId": "<attachment_id>", "alt": "What the image shows", "width": null}}`. Images are top-level blocks only: not in lists, quotes, tables, headings or sentences.

A note may use an image this connection uploaded to that Thread (for a note that already exists, with its `note_id`), or one already in a note it can read. Anything else answers `image_unavailable`.

## Files

A file of any type goes in a note the same way: upload it, then place it.

1. `upload_note_file` with the file as base64 (any type, up to 5 MB, in the same daily limit as images), its `name` with its extension, its lowercase hex SHA-256 as `checksum`, the `thread_id` of the note it goes in and, when that note already exists, its `note_id`. Uploading does not add it to the note: the note's `files` stay as they were until you place it.
2. Place the returned `file_id` on its own line: `[Q3 report.pdf](attachment:<file_id>)` (the answer's `markdown`) — or as a document block `{"type": "file", "attrs": {"attachmentId": "<file_id>", "name": "Q3 report.pdf"}}`. Files are top-level blocks only, like images.

ThreadPage checks every file before a note holds it. The upload answers `state`: `checking` while it does, then `uploaded`; `get_operation` with the upload's `operation_id` says which. A note write that places a file still being checked answers `attachment_upload_in_progress` and changes nothing: wait `details.retry_after` seconds and send the same call again. `failed` means the file was refused or deleted: upload it again with a new `operation_id`.

The rule for images holds for files too: a note may use a file this connection uploaded for it, or one already in a note it can read, and anything else answers `image_unavailable` (the code keeps its name). An upload is for the Thread and the note it was made for: if the note moved to another Thread since, upload the file again for the note there. Read a note's file with `read_note_file`.

## Documents (RichDocument v4)

`get_note` returns content in this form; send it back the same way.

```json
{"format": "work-threads.richtext", "schemaVersion": 4,
 "doc": {"type": "doc", "content": [
   {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Plan"}]},
   {"type": "paragraph", "content": [
     {"type": "text", "text": "Owner: "},
     {"type": "text", "text": "Maria", "marks": [{"type": "bold"}]}]},
   {"type": "taskList", "content": [
     {"type": "taskItem", "attrs": {"checked": false},
      "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Ship"}]}]}]}
 ]}}
```

Blocks (the `content` of `doc`):

| Block | Shape and attributes |
| --- | --- |
| `paragraph` | inline content (may be empty). `variant`: `body` (default) or `monostyled` (code). `textAlign`: `start`, `left`, `center`, `right`, `justify`. `direction`: `auto`, `ltr`, `rtl`. `indent`: 0–6 |
| `heading` | inline content. `level` (required): 1 Title, 2 Heading, 3 Subheading; also `textAlign`, `direction`, `indent` |
| `bulletList` | `listItem`s. `marker`: `bullet` or `dash` |
| `orderedList` | `listItem`s. `start`: 1–999999 |
| `taskList` | `taskItem`s, each with `checked`: `true` or `false` (required) |
| `listItem`, `taskItem` | a `paragraph` first, then paragraphs or nested lists (up to 8 levels) |
| `blockquote` | `paragraph`s only; top level only |
| `table` | `tableRow`s, all with the same number of cells (at least one) |
| `tableRow` | `tableHeader` or `tableCell` cells; no attributes |
| `tableHeader`, `tableCell` | `paragraph`s. `colwidth`: `null` or `[pixels]`; no merged cells |
| `image` | top level only, no content: `{"attachmentId": "<id>", "alt": "<up to 2,000 chars>", "width": null}` (`width` in pixels at the 680px reading measure, shown relative to the reader's column, or `null` for the default size, 400). `name`, optional: the image's file name |
| `file` | top level only, no content: `{"attachmentId": "<file_id>", "name": "<file name>"}`. `name` is optional (without it the note shows the file's own name): 1–255 characters, no slashes or control characters |
| `entryReference` | top level only, no content: `{"entryId": "<note_id>"}` |

Inline content: `{"type": "text", "text": "…", "marks": […]}` (text is never empty), `{"type": "hardBreak"}` (line break), and tags `{"type": "hashtag", "attrs": {"name": "release"}}` (up to 64 characters, lowercase: letters and digits of any language, and `_` or `-` after the first character; `-` never last).

Marks, each at most once per text node:

| Mark | Attributes |
| --- | --- |
| `bold`, `italic`, `underline`, `strike` | none |
| `link` | `href`: an `http`, `https` or `mailto` URL |
| `textStyle` | `fontFamily`: `sans-serif`, `serif` or `monospace` (inline code); `fontSize`: `"10px"`–`"48px"`; `colorRole`: `accent`, `red`, `orange`, `green`, `blue`, `purple` |
| `highlight` | `colorRole`: `yellow` (default), `green`, `blue`, `pink`, `purple` |

Limits of a document: 256 KiB as JSON, 500,000 characters, 50,001 nodes, 2,000 table cells, depth 32. Unknown node types, marks or attributes are refused with `invalid_document`; nothing is dropped silently.

## Editing an existing note

Edit the document `get_note` returned and send the whole result to `update_note` as `{"document": …}`. Keep every block you were not asked to change exactly as it was: images, files, references, tables, tags and styles included. Do not rebuild a rich note from Markdown: underline, colours, highlights, sizes, alignment, tags, image widths and lines inside table cells and headings would be lost, so `update_note` refuses such a Markdown or text replacement with `lossy_markdown` and changes nothing.
