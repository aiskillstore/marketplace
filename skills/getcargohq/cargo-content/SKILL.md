---
name: cargo-content
description: "Manage the knowledge a Cargo workspace holds — upload files (PDF, CSV, text), rename and organize them, and build native or connector-backed libraries that sync from an external source, so agents can retrieve them (RAG). Triggers: \"upload this PDF\", \"add these docs as knowledge\", \"build a knowledge base\", \"sync our help center into Cargo\", \"what files are in the workspace\", \"index this folder\", \"attach our pricing sheet\". Skip when: wiring the file or library into an agent — use cargo-ai; uploading a CSV that drives a batch run — that is a workspace-management file upload."
version: "1.0.1"
compatibility: Requires @cargo-ai/cli (npm). Sign in or create an account with `cargo-ai login --email` (emailed code, no browser), `--oauth`, or an API token
homepage: https://github.com/getcargohq/cargo-skills
metadata:
  author: getcargo
  openclaw:
    requires:
      bins:
        - cargo-ai
    install:
      - kind: node
        package: "@cargo-ai/cli@latest"
        bins:
          - cargo-ai
    homepage: https://github.com/getcargohq/cargo-skills
---

# Cargo CLI — Content

Workspace **knowledge** management: upload and organize **files** (PDFs, CSVs, text) and group or sync them into **libraries**. These are the binary/grouped knowledge resources that ground agent responses (retrieval-augmented generation, RAG).

> **New top-level domain (CLI ≥ 1.0.19).** Files and libraries moved out of the `ai` domain into the `content` domain — `cargo-ai content file …` and `cargo-ai content library …`. The old `cargo-ai ai file …` commands no longer exist; an `unknown command` error means you're on the old path.

> For **attaching** a file or library to an agent (via the release `resources` array), use [`cargo-ai`](../cargo-ai/SKILL.md).
> For **folders** that organize files, use [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) (`cargo-ai workspaceManagement folder …`).
> For batch-run **input** files (CSVs uploaded to drive a batch), that's a different surface — `cargo-ai workspaceManagement file upload` — documented in [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md).

> See `references/examples/files.md` for end-to-end file, library, and attach-to-agent examples.
> See `references/response-shapes.md` for full JSON response structures.
> See `references/troubleshooting.md` for common errors and how to fix them.

## Bootstrap

Already signed in (`cargo-ai whoami` returns a workspace)? Skip to the next section.

```bash
npm install -g @cargo-ai/cli            # no global install? prefix every command with `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # emailed code, no browser; creates the account on first use
                                        # alternatives: --oauth (browser) · --token <api-token> (CI)
cargo-ai whoami                         # confirm the active workspace before any write
```

Every command prints JSON to stdout; failures exit non-zero with `{"errorMessage": "..."}`. Anything that creates a run or a batch is async — pass `--wait-until-finished` or poll the matching `get`. When the full skill bundle is installed, [`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) adds the CLI version pin, token scopes, and the admin-only surface.

## Discover resources first

```bash
cargo-ai content file list                 # all uploaded files (uuid, name, contentType, size)
cargo-ai content library list              # knowledge libraries (native or connector-backed)
```

## Files

Upload files (PDFs, CSVs, text) so an agent can ground its responses in specific knowledge. The upload response includes the `uuid` you reference when attaching the file to an agent release (see [`cargo-ai`](../cargo-ai/SKILL.md)).

```bash
# List all files
cargo-ai content file list

# Get a single file
cargo-ai content file get <file-uuid>

# Upload a file (optionally straight into a folder)
cargo-ai content file upload --file ./knowledge-base.pdf
cargo-ai content file upload --file ./knowledge-base.pdf --folder-uuid <folder-uuid>

# Update a file's name or folder
cargo-ai content file update --uuid <file-uuid> --name "Q1 Research Notes"
cargo-ai content file update --uuid <file-uuid> --folder-uuid <folder-uuid>

# Remove a file
cargo-ai content file remove <file-uuid>
```

> **Reading content files from the context sandbox.** Uploaded content files are also available **read-only** under `.files/` in the context runtime sandbox, so a command run there can consume them — e.g. `cargo-ai context runtime execute --command ls --args '["-1",".files"]'`. The directory sits outside the committed context tree (never pushed, not writable); to add or change files use `content file` here. See [`cargo-context`](../cargo-context/SKILL.md).

## Libraries

A library groups files into one resource an agent can reference. There are two kinds:

- **`native`** — workspace-managed collections of uploaded files.
- **`connector`** — synced from an external source (e.g. a help center or knowledge base) through an unstructured-data extractor (`--extractor-slug`). Get the `connectorUuid` from [`cargo-connection`](../cargo-connection/SKILL.md).

```bash
# List libraries (filter by kind or connector)
cargo-ai content library list
cargo-ai content library list --kind native
cargo-ai content library list --kind connector --connector-uuid <connector-uuid>

# Get a single library
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

## Attaching to an agent

Files and libraries are knowledge **resources** — they do nothing until attached to an agent via that agent's draft release `resources` array, then deployed. That wiring lives in [`cargo-ai`](../cargo-ai/SKILL.md) (`ai release update-draft --resources …` → `ai release deploy-draft`). See `references/examples/files.md` for the upload → attach → deploy sequence.

## Help

Every command supports `--help`:

```bash
cargo-ai content file upload --help
cargo-ai content library create --help
```
