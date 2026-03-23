# Troubleshooting

This file describes the actual failure modes of the shell scripts under `infra/docs/agent-skills/pexo-video/scripts`.

## Script Exit Behavior

- Exit `0`: success
- Exit `1`: request/transport/backend failure
- Exit `2`: local usage error (missing args, invalid flags, invalid local input)

On request failure, the shared layer now prints compact JSON to `stderr`, for example:

```json
{"ok":false,"httpCode":429,"businessCode":400001,"message":"Daily creation limit reached. Contact support email for more access."}
```

Fields you may see:

- `httpCode`: the real HTTP status code returned to the script
- `businessCode`: nested backend business code when the BFF wrapped it (for example `400001`)
- `error`: auth/proxy error code such as `INVALID_API_KEY` or `INTERNAL_ERROR`
- `message`: the most useful user-facing message extracted from the response
- `details`: extra backend detail when available

## Important Response Shapes

The scripts hit two kinds of frontend endpoints, and the error body shape is different:

### `/api/biz/*` routes

These usually return a wrapper:

```json
{"code":429,"message":"Too Many Requests","data":{"code":400001,"message":"..."}}
```

The shared layer unwraps success bodies and, on failure, promotes the nested `data.message` / `data.code` into the compact `stderr` JSON.

### `/api/chat`

This is an SSE endpoint, not a normal JSON endpoint.

- Success means the SSE stream was opened.
- `pexo-chat.sh` only waits for the initial `: stream opened` acknowledgement, then disconnects intentionally.
- On non-auth failure, the current frontend route returns a generic body like `{"error":"Chat error: 412"}` and preserves the HTTP status.

That means for `pexo-chat.sh`, the status code is often more informative than the message text.

## Auth And Proxy Errors

These can happen on every script that talks to the frontend:

| HTTP | `error` | Meaning | What to do |
|---|---|---|---|
| 401 | `INVALID_API_KEY` | API key is invalid or revoked | Update `PEXO_API_KEY` in `~/.pexo/config` |
| 401 | `MISSING_TOKEN` | Auth header missing | Check script environment / wrapper |
| 401 | `INTERNAL_ERROR` | Frontend BFF/proxy failed before completing the request | Treat as infra/backend issue, not as a bad API key |
| 409 | `SESSION_REPLACED` | JWT session was replaced by another login | Mostly relevant for browser/JWT auth, unusual for API-key usage |

If the message says `Invalid API key`, it is an auth problem.
If the body says `error=INTERNAL_ERROR`, do not tell the user to rotate the key first; the proxy/backend path may simply be down.

## Script-Specific Errors

### `pexo-project-create.sh`

Real statuses:

- `400`: invalid `project_name` (empty after local processing should no longer happen, too long still can)
- `401`: auth failure
- `429`: quota/business limit
  - `businessCode=400001`: daily creation limit reached
  - `businessCode=400002`: user already has an active project and must wait
- `500`: backend/internal failure

Notes:

- The script now defaults the project name to `"Untitled"` when no name is provided, because the backend requires `project_name`.

### `pexo-project-list.sh`

Real statuses:

- `401`: auth failure
- `500`: backend/internal failure

Notes:

- Invalid `page` / `page_size` values are handled locally by the script before request time.
- Backend page size is effectively capped at `100`.

### `pexo-project-get.sh`

Real statuses from the first project fetch:

- `401`: auth failure
- `404`: project not found
- `500`: backend/internal failure

Secondary history fetches (`/history`) can also fail with:

- `401`: auth failure
- `404`: project not found
- `500`: backend/internal failure

### `pexo-upload.sh`

This script has three phases, and the failure source matters.

#### Phase 1: upload credential

Endpoint: `POST /api/biz/projects/:project_id/assets/upload-credential`

Real statuses:

- `400`: invalid `file_name` / `file_size`
- `401`: auth failure
- `500`: backend/internal failure

Notes:

- This endpoint does not currently perform a strict project existence check before creating the upload credential.
- The script now rejects unsupported extensions locally, matching the backend allowlist:
  - Images: `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tiff`, `heic`, `heif`
  - Videos: `mp4`, `mov`, `avi`
  - Audio: `mp3`, `wav`, `aac`, `m4a`, `ogg`, `flac`

#### Phase 2: raw PUT to the presigned URL

This phase does not go through the BFF wrapper.

Possible failures:

- `4xx/5xx` from object storage or CDN

The script surfaces this directly as:

```text
Error: upload failed with HTTP <code>
```

#### Phase 3: finalize

Endpoint: `POST /api/biz/projects/:project_id/assets/:asset_id/finalize`

Real statuses:

- `400`: invalid finalize body, file size limit hit, MIME/type mismatch, unsupported media type
- `401`: auth failure
- `404`: asset not found, or asset does not belong to the given project/user
- `412`: asset is not in `UPLOADING` state anymore
- `500`: internal/storage verification failure

Notes:

- The script may omit `mime_type` during finalize if local MIME detection returns a value that is outside the backend allowlist. This lets the backend detect MIME from the uploaded file instead of failing on a bad local alias.

### `pexo-chat.sh`

Endpoint: `POST /api/chat`, which forwards to SSE `POST /api/projects/:project_id/messages`

Real statuses:

- `400`: invalid request body
- `401`: auth failure
- `404`: project not found
- `412`: agent schema version incompatible
- `429`: project video limit reached
- `500`: backend/internal failure

Notes:

- `pexo-chat.sh` is intentionally asynchronous now. Success means “the backend accepted the chat request and opened the SSE stream”, not “the video is done”.
- The frontend chat route currently hides detailed backend JSON on non-auth errors and returns only `Chat error: <status>`. For this script, use the status code as the primary signal.
- A successful `pexo-chat.sh` call should be followed by `pexo-project-get.sh` polling, typically every `60` seconds.

### `pexo-asset-get.sh`

Real statuses:

- `401`: auth failure
- `404`: asset not found, or asset/project ownership mismatch
- `500`: backend/internal failure

Secondary download failures after metadata fetch:

- `403`: signed `downloadUrl` expired or object storage denied access
- `000`: local network failure while downloading the signed URL
- local filesystem write failure: `~/.pexo/tmp/` is not writable or disk is full

Notes:

- The script now downloads `downloadUrl` into `~/.pexo/tmp/` (or `$PEXO_TMP_DIR`) and returns both `url` and `localPath`.
- If the asset metadata exists but `downloadUrl` is absent, the script returns `localPath: null`.

### `pexo-doctor.sh`

This script does not use the shared request wrapper, but its API check uses the same real endpoint:

- `200`: config and API key look healthy
- `401` + `INVALID_API_KEY`: bad key
- `401` + `INTERNAL_ERROR`: proxy/BFF problem
- `409`: JWT session conflict, unusual for API-key use
- `000`: no HTTP response received at all (network/DNS/TLS/connectivity issue)

## Common Scenarios

### `pexo-chat.sh` returns success immediately

This is expected.

The script only confirms that the SSE stream was accepted, then it disconnects on purpose.
It does not stream progress or final results to the terminal.

Next step:

1. Wait `60` seconds.
2. Run `pexo-project-get.sh <project_id>`.
3. Follow `nextAction`.

### `WAIT` lasts a long time

This is normal for video generation.

Practical guideline:

1. Keep polling every `60` seconds.
2. Do not send another `pexo-chat.sh` message while `nextAction=WAIT`.
3. If the project later becomes `RECONNECT`, send a short continuation message and resume polling.

### `RECONNECT` keeps appearing

Meaning:

- The run was marked `RUNNING`, but no worker stream is currently attached.

Action:

1. Send a short message with `pexo-chat.sh`, for example `continue`.
2. Resume polling with `pexo-project-get.sh`.
3. If this repeats multiple times, start a new project instead of looping forever.

### Download URL expired or returns `403`

Signed URLs are temporary.

Action:

1. Re-run `pexo-asset-get.sh <project_id> <asset_id>`.
2. The script will fetch a fresh `downloadUrl` and re-download the file into `~/.pexo/tmp/`.
3. Deliver the fresh `downloadUrl`.

### Upload fails locally with “unsupported file type”

This is a local pre-check, not a backend outage.

Action:

1. Convert the file into one of the supported formats listed above.
2. Retry `pexo-upload.sh`.

### A script says `401`, but the API key may still be fine

Inspect the error payload:

- `error=INVALID_API_KEY`: fix the key
- `error=INTERNAL_ERROR`: treat it as proxy/backend trouble

This distinction matters because the frontend BFF currently uses `401` for some internal proxy failures.
