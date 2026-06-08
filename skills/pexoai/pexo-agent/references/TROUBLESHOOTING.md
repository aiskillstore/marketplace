# Troubleshooting

## Script Exit Behavior

- Exit `0`: success
- Exit `1`: request/transport/backend failure
- Exit `2`: local usage error (missing args, invalid flags, invalid local input)

On request failure, scripts print compact JSON to `stderr`, for example:

```json
{"ok":false,"httpCode":429,"message":"Daily creation limit reached. Contact support email for more access."}
```

Fields you may see:

- `httpCode`: the real HTTP status code returned to the script
- `error`: auth/proxy error code such as `INVALID_API_KEY` or `INTERNAL_ERROR`
- `message`: the most useful user-facing message extracted from the response
- `details`: extra backend detail when available

When the error is credit-related (`httpCode` 429 or 412 from `pexo-project-create.sh` or `pexo-chat.sh`), the script automatically fetches the user's credit balance and appends two extra lines to stderr:

```
Credits balance: 0 — your account has no available credits.
To purchase credits: visit https://pexo.ai/home → click Credits (top-right) → Buy Credits → Extra Credits
```


## Auth And Proxy Errors

These can happen on every script that makes API calls:

| HTTP | `error` | Meaning | What to do |
|---|---|---|---|
| 401 | `INVALID_API_KEY` | API key is invalid or revoked | Update `PEXO_API_KEY` in `~/.pexo/config`. Get a new key at pexo.ai. |
| 401 | `MISSING_TOKEN` | The request was sent without an API key | Run `pexo-doctor.sh` to verify config. Make sure `~/.pexo/config` is sourced correctly. |
| 401 | `INTERNAL_ERROR` | The service failed to process the request before authentication completed | This is a temporary service issue, not a problem with the API key. Wait a moment and retry; if it persists, contact support. |
| 409 | `SESSION_REPLACED` | This API key's session was invalidated by a new login elsewhere | Unusual for API-key usage. Retry the command. If it keeps happening, regenerate the API key at pexo.ai. |

If the message says `Invalid API key`, it is an auth problem.
If the body says `error=INTERNAL_ERROR`, do not tell the user to rotate the key first; the service may simply be temporarily down.

## Script-Specific Errors

### `pexo-project-create.sh`

Real statuses:

- `400`: project name is too long. Ask the user to use a shorter name and retry.
- `401`: auth failure — see Auth and Proxy Errors above.
- `429`: creation limit reached — could be any of:
  - User already has an active project running (must wait for it to finish)
  - Insufficient credits to start a new project
  The script automatically fetches and prints the credit balance + top-up URL after any `429`.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Notes:

- If no project name is provided, the script defaults to `"Untitled"`.

### `pexo-project-list.sh`

Real statuses:

- `401`: auth failure — see Auth and Proxy Errors above.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Notes:

- Invalid `page` / `page_size` values are handled locally by the script before request time.
- Backend page size is effectively capped at `100`.

### `pexo-project-get.sh`

Real statuses from the first project fetch:

- `401`: auth failure — see Auth and Proxy Errors above.
- `404`: the project does not exist or has been deleted. Verify the project_id; if correct, start a new project.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Subsequent status fetches can also fail with:

- `401`: auth failure — see Auth and Proxy Errors above.
- `404`: project not found. Same action as above.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

### `pexo-upload.sh`

This script has three phases, and the failure source matters.

#### Phase 1: upload credential

Real statuses:

- `400`: the file name or file size is invalid. Check that the file exists and is not empty; rename it if it contains special characters.
- `401`: auth failure — see Auth and Proxy Errors above.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Notes:

- The script rejects unsupported extensions locally. Supported formats:
  - Images: `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tiff`, `heic`, `heif`
  - Videos: `mp4`, `mov`, `avi`
  - Audio: `mp3`, `wav`, `aac`, `m4a`, `ogg`, `flac`

#### Phase 2: file transfer

Possible failures:

- `4xx/5xx`: the file storage service rejected the upload. Check network connectivity and retry. If the problem persists, contact support at pexo.ai.

The script surfaces this directly as:

```text
Error: upload failed with HTTP <code>
```

#### Phase 3: finalize

Real statuses:

- `400`: the file was rejected — possible reasons: file exceeds the size limit, file format is not supported, or the file content does not match its extension. Convert or compress the file and re-upload from scratch using `pexo-upload.sh`.
- `401`: auth failure — see Auth and Proxy Errors above.
- `404`: the file record was not found. The upload session may have been cleaned up. Re-upload from scratch using `pexo-upload.sh`.
- `412`: the upload session has already expired or been completed. Re-upload from scratch using `pexo-upload.sh`.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

### `pexo-chat.sh`

Real statuses:

- `400`: the message could not be sent due to invalid content. Check the message text; if the issue persists, start a new project.
- `401`: auth failure — see Auth and Proxy Errors above.
- `404`: the project does not exist or has been deleted. Start a new project.
- `412`: two possible causes:
  - **Project no longer supported**: this project was created with an older version of Pexo's production system and cannot be continued. Start a new project.
  - **Account billing issue**: the account's credits are frozen or suspended. The script automatically fetches and prints the credit balance + top-up URL. Direct the user to top up or contact support at pexo.ai.
- `429`: limit reached — could be insufficient credits or the project's video output limit. The script automatically fetches and prints the credit balance + top-up URL after a `429`.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Business errors (credit-related):

- `error=”credits.insufficient_credits_err”`: account has no available credits. `pexo-chat.sh` exits non-zero and prints compact JSON to `stderr`, for example:

```json
{“ok”:false,”httpCode”:200,”message”:”Insufficient credits”,”error”:”credits.insufficient_credits_err”}
```

Notes:

- `pexo-chat.sh` is asynchronous. Success means the request was accepted, not that the video is done.
- For non-auth failures, use the HTTP status code as the primary signal. The automatically-appended credit balance lines are the most actionable hint.
- A successful `pexo-chat.sh` call should be followed by `pexo-project-get.sh` polling, typically every `60` seconds.

### `pexo-entitlements.sh`

Real statuses:

- `401`: auth failure — see Auth and Proxy Errors above.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Notes:

- Returns JSON with `credits.availableCredits`, `credits.subscriptionCredits`, `credits.bonusCredits`, `credits.purchaseCredits`, and plan info.
- When `availableCredits` is `0`, the top-up URL is also printed to stderr.
- You generally do not need to call this script manually — `pexo-project-create.sh` and `pexo-chat.sh` call it automatically on `429`/`412` failures and include the balance in their error output.

### `pexo-asset-get.sh`

Real statuses:

- `401`: auth failure — see Auth and Proxy Errors above.
- `404`: the file does not exist, or it belongs to a different project. Verify the asset_id and project_id.
- `500`: an unexpected server error occurred. Retry in a moment; if the problem persists, contact support at pexo.ai.

Secondary download failures after metadata fetch:

- `403`: the download link has expired. Re-run `pexo-asset-get.sh` to get a fresh link.
- `000`: network request failed before receiving a response. Check network connectivity and retry.
- local filesystem write failure: the temp directory (`~/.pexo/tmp/`) is not writable or the disk is full. Free up space or set `PEXO_TMP_DIR` to a writable path.

Notes:

- The script downloads the file into `~/.pexo/tmp/` (or `$PEXO_TMP_DIR`) and returns both `url` and `localPath`.
- If the asset metadata exists but `downloadUrl` is absent, the script returns `localPath: null`.

### `pexo-doctor.sh`

- `200`: config and API key look healthy
- `401` + `INVALID_API_KEY`: API key is invalid or revoked. Update `PEXO_API_KEY` in `~/.pexo/config`.
- `401` + `INTERNAL_ERROR`: the service failed temporarily — not a key problem. Wait and retry.
- `409`: session conflict, unusual for API-key usage. Retry the command.
- `000`: no response received — network is unreachable or DNS failed. Check connectivity.

## Common Scenarios

### Insufficient credits — `429` or `412` with credit balance printed

When `pexo-project-create.sh` or `pexo-chat.sh` fails with `429` or `412`, the script automatically fetches the credit balance and appends:

```
Credits balance: 0 — your account has no available credits.
To purchase credits: visit https://pexo.ai/home → click Credits (top-right) → Buy Credits → Extra Credits
```

If `availableCredits` is `0`:

- Explain to the user that they have run out of credits.
- Guide them to purchase credits: visit https://pexo.ai/home, click Credits in the top-right corner → Buy Credits, then find Extra Credits.
- Do NOT retry the failed operation — it will fail again until credits are added.

If `availableCredits` is non-zero but the error still appears:

- The `429` is likely the concurrent-project limit: the user already has an active project running.
- Re-read the `message` field from the error JSON to confirm, then tell the user to wait for the current project to finish before creating a new one.

### `pexo-chat.sh` returns success immediately

This is expected.

The script only confirms that the request was accepted by the server, then exits.
It does not stream progress or final results to the terminal.

Next step:

1. Wait `60` seconds.
2. Run `pexo-project-get.sh <project_id>`.
3. Follow `nextAction`.

### `pexo-chat.sh` prints `credits.insufficient_credits_err`

Meaning:

- The account has no available credits.

Action:

1. Tell the user the account has no available credits for this chat request.
2. Direct them to top up credits at `https://pexo.ai/home`.
3. Do not retry `pexo-chat.sh` until credits are added; it will fail again with the same error.

### `WAIT` lasts a long time

This is normal for video generation.

Practical guideline:

1. Keep polling every `60` seconds.
2. Do not send another `pexo-chat.sh` message while `nextAction=WAIT`.
3. If the project later becomes `RECONNECT`, send a short continuation message and resume polling.

### `RECONNECT` keeps appearing

Meaning:

- The connection to the video generation service was interrupted.

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
- `error=INTERNAL_ERROR`: treat it as a temporary service issue, not a key problem
