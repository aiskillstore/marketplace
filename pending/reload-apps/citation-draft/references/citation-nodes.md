# Citation editor nodes

Use source IDs already saved in the target document. An inline citation node belongs inside a paragraph alongside text nodes:

```json
{
  "type": "citation",
  "attrs": {
    "id": "unique-cluster-id",
    "sourceIds": ["SAVED_SOURCE_UUID"],
    "text": "Formatted inline text",
    "label": "page",
    "locator": "12"
  }
}
```

Replace placeholders with the saved source ID and a unique cluster ID. Omit the locator unless the cited passage has a verified locator. Preserve the original source's page numbering. The formatter's `in_text` items expose `id`, `text` and `html`; match the entry by source ID.

Read the current editor object with `include_content: true` before editing. Keep every unrelated node and attribute. The MCP server validates the content, checks that referenced sources belong to the document, and checks both document and collaboration revisions when saving. The TXT exporter resolves citation sequence in document context, including numeric styles. Formatting individual references does not save citation nodes.

MCP does not edit documents with mentions or attachments because their file and notification semantics require the Citation editor. It also bounds editor JSON and source counts; use the editor if a document exceeds those limits. Do not work around a limit by dropping nodes or sources.
