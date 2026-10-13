# Content troubleshooting

Common errors in the `content` domain and how to fix them.

## `unknown command 'file'` / `unknown command 'library'`

File and library commands moved from the `ai` domain to the new top-level **`content`** domain in CLI ≥ 1.0.19. Use `cargo-ai content file …` / `cargo-ai content library …` — the old `cargo-ai ai file …` path no longer exists. If you still hit this on the new path, bump the CLI: `npm install -g @cargo-ai/cli@latest`.

## `fileNotFound`

The file UUID does not exist or has been deleted. Run `cargo-ai content file list` to get the current list.

## `folderNotFound`

The folder UUID passed to `--folder-uuid` does not exist. Folders are managed by the [`cargo-workspace-management`](../../cargo-workspace-management/SKILL.md) skill — run `cargo-ai workspaceManagement folder list` to find valid folder UUIDs, or `cargo-ai workspaceManagement folder create --kind file ...` to create one.

## Upload fails or times out

Large files may take longer to upload. Ensure the file path is correct and the file is not locked by another process.

## Library created but the agent doesn't use it

A file or library is inert until it's attached to an agent's **deployed** release. Add it to the draft release `resources` array and deploy — see [`cargo-ai`](../../cargo-ai/SKILL.md) and `examples/files.md`.
