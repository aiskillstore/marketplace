# File & library examples

> **CLI ≥ 1.0.19:** files and libraries live in the top-level **`content`** domain (`cargo-ai content file …`, `cargo-ai content library …`). The old `cargo-ai ai file …` commands no longer exist.

## Files

### List all files

```bash
cargo-ai content file list
```

### Upload a file

```bash
cargo-ai content file upload --file ./knowledge-base.pdf
```

Supported content types include PDFs, CSVs, plain text, and other common document formats. The response includes the `uuid` and `s3Filename` needed to reference the file.

### Upload and attach to an agent

```bash
# 1. Upload the file
cargo-ai content file upload --file ./product-docs.pdf
# → file.uuid

# 2. Add the file as a resource on the agent's draft release
cargo-ai ai release update-draft --agent-uuid <agent-uuid> \
  --resources '[{"kind":"file","slug":"product_docs","name":"Product Docs","description":null,"prompt":null,"items":[{"kind":"file","fileUuid":"<file-uuid>"}]}]'

# 3. Deploy
cargo-ai ai release deploy-draft --agent-uuid <agent-uuid> \
  --language-model-slug gpt-4o \
  --integration-slug openai
```

### Upload to a folder

Folders are managed by the [`cargo-workspace-management`](../../../cargo-workspace-management/SKILL.md) skill — see its `references/examples/folders.md` for create/list/update.

```bash
# 1. Find the folder (kind: "file")
cargo-ai workspaceManagement folder list

# 2a. Upload straight into the folder…
cargo-ai content file upload --file ./notes.pdf --folder-uuid <folder-uuid>

# 2b. …or move an existing file afterwards
cargo-ai content file update --uuid <file-uuid> --folder-uuid <folder-uuid>
```

### Rename a file

```bash
cargo-ai content file update --uuid <file-uuid> --name "Q1 Research Notes"
```

### Remove a file

```bash
cargo-ai content file remove <file-uuid>
```

### Audit files by size

```bash
cargo-ai content file list
# → Check the "size" field (in bytes) for each file
# → 1048576 bytes = 1 MB
```

## Libraries

A library groups files into one resource an agent can reference. `native` libraries are workspace-managed; `connector`-backed libraries sync documents from an external source through an unstructured-data extractor.

```bash
# List libraries, optionally filtered
cargo-ai content library list
cargo-ai content library list --kind native
cargo-ai content library list --kind connector --connector-uuid <connector-uuid>

# Get one
cargo-ai content library get <library-uuid>

# Create a connector-backed library
cargo-ai content library create \
  --name "Help Center" \
  --connector-uuid <connector-uuid> \
  --extractor-slug <extractor-slug> \
  --folder-uuid <folder-uuid> \
  --config '{}'

# Update / remove
cargo-ai content library update --uuid <library-uuid> --name "Updated Name"
cargo-ai content library remove <library-uuid>
```
