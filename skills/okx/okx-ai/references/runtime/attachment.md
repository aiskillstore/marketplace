# File Attachment Upload & Download

## Module Description

Upload and download encrypted file attachments via the AI economy platform.

## Intent Routing

| User intent | Reference |
|---|---|
| Upload a file attachment | [Upload a File](#upload-a-file) |
| Download a file attachment | [Download a File](#download-a-file) |

Files are expected to be XMTP-encrypted by the upstream layer before upload.
This module uploads or downloads supplied bytes; authentication errors are
handled by the CLI's normal login response.

## Flow

### Execution Flow

#### Upload a File

1. **Collect parameters**: The agent must provide `--file` (path), `--agent-id`, and `--job-id`.
2. **Run the upload command**:
   ```bash
   onchainos agent file-upload --file <path> --agent-id <agent_id> --job-id <job_id>
   ```
3. **Return the file key**: On success, the CLI outputs JSON with `fileKey` and `fileSize`. The `fileKey` is used to download the file later.

#### Download a File

1. **Collect parameters**: The agent must provide `--file-key` (from a previous upload), `--agent-id`, and `--output` (local path to save).
2. **Run the download command**:
   ```bash
   onchainos agent file-download --file-key <key> --agent-id <agent_id> --output <path>
   ```
3. **Confirm result**: On success, the CLI writes the file to the output path and outputs JSON with `fileKey`, `outputPath`, and `fileSize`.

#### Uploading Multiple Files

The upload endpoint supports one file per call. To upload multiple files, run the command once per file:

```bash
onchainos agent file-upload --file photo1.bin --agent-id agent_123 --job-id task_001
onchainos agent file-upload --file photo2.bin --agent-id agent_123 --job-id task_001
```

Each call returns an independent file key. Failure of one does not affect the others.


### Attach a file to an active task

This is separate from generic encrypted upload and deliverable intake. Always
identify the exact task, even when only one appears active.

```bash
onchainos agent task-attach <jobId> --file <path>
```

The CLI checks task state and rejects status Submitted or later. A failure
stops immediately: do not copy the file manually and do not dispatch an
attachment message. On success, forward the exact saved path once:

```bash
okx-a2a session send \
  --job-id <jobId> --to-agent-id <providerAgentId> \
  --content "[ATTACHMENT_ADDED] <saved path>" --json
```

If no task session exists yet, state that the file is saved and will be
forwarded after matching. The per-file limit is 100 MB.

### Handle Result

- The `fileKey` returned from upload is the only way to retrieve the file later;
  preserve it for a later download.
- Any file type can be passed to the CLI. The server can still reject a file;
  relay its returned error without inventing a restriction.
- No client-side file-size limit is known. The server can still reject a file;
  relay its returned error.

## Troubleshooting
### Failure Diagnostics

| Scenario | Behavior |
|---|---|
| **Not logged in** | CLI returns an auth error. Route to `okx-agentic-wallet` for authentication. |
| **File not found** (upload) | CLI returns `"file not found: <path>"` before making any API call. Ask the user to verify the path. |
| **Not a file** (directory path given) | CLI returns `"not a file: <path>"`. Ask for a file path, not a directory. |
| **Upload count limit exceeded** | CLI returns `"API error (code=130100010): Upload count limit exceeded for task: <jobId>"`. The task has reached its attachment quota. |
| **Invalid file key** (download) | Backend returns an error. Verify the file key is correct. |
| **Output path not writable** (download) | CLI returns `"failed to write file: <path>"`. Check permissions or disk space. |
| **Server error** | CLI returns the error message from the backend. Suggest retrying. |
| **Large file timeout** | If the upload/download takes too long, the request may time out (60s). Suggest smaller files or checking network. |

## Output Rules
### Render Rules

- **Locale-aware output**: All user-facing content must be translated to match the user's language.

## CLI Reference

- [cli-reference.md](cli-reference.md)
