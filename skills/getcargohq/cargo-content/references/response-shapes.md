# Content response shapes

Full JSON response structures for the `content` domain. All commands output JSON to stdout; failures exit non-zero with `{"errorMessage": "..."}`.

## cargo-ai content file list

```json
{
  "files": [
    {
      "uuid": "file-uuid",
      "workspaceUuid": "...",
      "libraryUuid": "library-uuid",
      "userUuid": null,
      "name": "knowledge-base.pdf",
      "isTemporary": false,
      "folderUuid": null,
      "s3Filename": "...",
      "openAiFileId": "...",
      "contentType": "application/pdf",
      "size": 1048576,
      "isIndexedInOpenAiVectorStore": true,
      "externalId": null,
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-15T00:00:00Z",
      "deletedAt": null,
      "kind": "native"
    }
  ]
}
```

Each file is a discriminated union on `kind`: `"native"` (as above) or `"connector"`, which adds a `connectorUuid: string`.

**Key fields:** `uuid` (used to reference in agent release `resources` — see [`cargo-ai`](../../cargo-ai/SKILL.md)), `libraryUuid` (the library the file belongs to), `name`, `contentType`, `size` (in bytes), `folderUuid` (null unless filed into a folder), `isIndexedInOpenAiVectorStore` (whether it's retrievable for RAG yet), `kind` (`native` or `connector`; the latter carries `connectorUuid`).

## cargo-ai content library list

> The exact JSON envelope isn't pinned here (capture it from a live `cargo-ai content library list` when you need field-level certainty). Each library carries at least: `uuid` (referenced in agent release `resources`), `name`, `kind` (`native` or `connector`), and — for `connector`-backed libraries — the `connectorUuid` and the extractor it syncs through. Filter the list with `--kind native|connector` and `--connector-uuid <uuid>`.
