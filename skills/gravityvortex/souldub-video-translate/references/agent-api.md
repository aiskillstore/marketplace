# SoulDub Video Translation Agent API Reference

Audience: agents, backend services, and scripts that automate SoulDub video translation.

Updated: 2026-07-04

This document is a runtime reference for the skill. It does not replace `scripts/video_translation.py`. Normal translation runs should use the script first; read this document only when debugging API calls, authentication, idempotency, rate limits, result downloads, or error codes.

## 1. Agent Quick Reference

- Current API base URL: `https://xxx.com/api/v1`.
- External API paths are under `/api/v1/...`.
- All `/api/v1/...` endpoints require an Agent API key. Prefer `Authorization: Bearer ${AGENT_API_KEY}`.
- Binary video uploads use `PUT {presignedUrl}` directly against the storage presigned URL and do not include an API key.
- Media gateway URLs are downloaded directly and do not include an API key.
- Subtitle download endpoints are still Agent API endpoints and require an API key.
- Task creation and retranslation must include a stable `Idempotency-Key`.
- Do not write API keys, upload presigned URLs, temporary media download URLs, or signature parameters to logs, state files, test reports, or prompts.
- For 429 responses, wait according to `Retry-After`. Also wait for concurrency limits; do not retry aggressively.
- When a temporary URL expires, request a fresh URL from the result endpoint.

## 2. Call Flow

Main flow:

| Order | Stage | Endpoint |
| --- | --- | --- |
| 1 | Initiate upload | `POST /video-uploads/initiate` |
| 2 | Presign part URL | `POST /video-uploads/presign-part` |
| 3 | Upload video bytes | `PUT {presignedUrl}` |
| 4 | Complete upload | `POST /video-uploads/complete` |
| 5 | Create translation task | `POST /video-translations` |
| 6 | Poll task status | `GET /video-translations/{taskId}` |
| 7 | List results | `GET /video-translations/{taskId}/results` |
| 8 | Get one media URL | `GET /video-translations/{taskId}/results/files/{variant}` |
| 9 | Download subtitles | `GET /video-translations/{taskId}/results/subtitles/{variant}` |

Optional retranslation:

```http
POST /video-translations/{existingTaskId}/retranslate
```

## 3. Authentication and Common Conventions

The Agent API supports two authentication headers. Prefer the first:

```http
Authorization: Bearer ${AGENT_API_KEY}
```

```http
X-API-Key: ${AGENT_API_KEY}
```

Common JSON request headers:

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer ${AGENT_API_KEY}
X-Request-Id: agent-run-20260704-0001
```

`X-Request-Id` is optional. If provided, it must be 8..64 characters and may contain only `A-Z a-z 0-9 _ . : -`. The server returns the final request id in response headers.

Successful responses use a JSON envelope:

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

Error responses also use a JSON envelope:

```json
{
  "code": -1,
  "message": "INVALID_REQUEST",
  "data": null,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Validation failed.",
    "requestId": "req_abc123",
    "details": {}
  }
}
```

When debugging, inspect in this order:

1. HTTP status
2. `error.code`
3. `error.details`
4. `X-Request-Id` response header

Rate-limit headers may appear on all Agent API responses:

```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 119
X-RateLimit-Reset: 1782300000
```

Rate-limited response:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 17
```

When `RATE_LIMITED` is returned, wait according to `Retry-After` before retrying.

## 4. Video Upload

### 4.1 Initiate Upload

```http
POST /video-uploads/initiate
```

Request:

```json
{
  "filename": "demo.mp4",
  "contentType": "video/mp4",
  "fileSizeBytes": 342556
}
```

Field rules:

| Field | Required | Notes |
| --- | --- | --- |
| `filename` | Yes | Must be a `.mp4` filename |
| `contentType` | Yes | Must be exactly `video/mp4` |
| `fileSizeBytes` | Yes | Must be greater than 0 and within the account file-size limit |

Save `fileId`, `uploadId`, `key`, and `bucket` from the response. Later complete-upload and task-creation calls need them.

### 4.2 Presign Part URL

```http
POST /video-uploads/presign-part
```

Request:

```json
{
  "uploadId": "opaque-r2-upload-id",
  "key": "storage-key-from-initiate",
  "partNumber": 1,
  "expiresInSeconds": 900
}
```

Field rules:

| Field | Required | Notes |
| --- | --- | --- |
| `uploadId` | Yes | Returned by upload initiation |
| `key` | Yes | Returned by upload initiation |
| `partNumber` | Yes | `1..10000` |
| `expiresInSeconds` | No | URL TTL; the server clamps it to `60..86400` seconds |

Use the returned `presignedUrl` only for the current upload. Do not persist it to logs or state files.

### 4.3 Upload Video Bytes

```http
PUT {presignedUrl}
Content-Type: video/mp4
```

The body is the video bytes. This request is not an Agent API request:

- Do not include `Authorization`.
- Do not include `X-API-Key`.
- Do not log `presignedUrl`.
- If the URL expires, call `presign-part` again.
- A successful PUT usually returns 200. The client does not need to send ETag back to the Agent API.

### 4.4 Complete Upload

```http
POST /video-uploads/complete
```

Request:

```json
{
  "uploadId": "opaque-r2-upload-id",
  "key": "storage-key-from-initiate"
}
```

Confirm `data.success == true`, `data.status == "completed"`, and `data.fileId` matches the `fileId` returned by upload initiation.

## 5. Create Translation Task

```http
POST /video-translations
Idempotency-Key: ${UNIQUE_IDEMPOTENCY_KEY}
```

Request:

```json
{
  "fileId": "uploaded-file-id",
  "videoDurationSeconds": 6,
  "checksumSha256": "optional-file-sha256",
  "sourceLanguage": "auto",
  "targetLanguage": "en",
  "speakerCount": 1,
  "allowDynamicDuration": true
}
```

Field rules:

| Field | Required | Notes |
| --- | --- | --- |
| `fileId` | Yes | Completed upload `fileId` |
| `videoDurationSeconds` | Yes | `1..3600` seconds |
| `checksumSha256` | No | Source file SHA-256 for tracking and validation |
| `sourceLanguage` | Yes | Source language; `auto` is allowed |
| `targetLanguage` | Yes | Target language; `auto` is not allowed |
| `speakerCount` | No | `0..15`; default `0` means auto-detect |
| `allowDynamicDuration` | No | `true` allows dynamic duration synchronization |

Supported languages are defined by `references/languages.json` and server-side validation.

Save `taskId`, `fileId`, `creditsConsumed`, and the `Idempotency-Key` used for this request.

Credits are rounded up by minute:

```text
durationInMinutes = max(1, ceil(videoDurationSeconds / 60))
creditsConsumed = durationInMinutes * credit.points_per_minute
```

The current default is `credit.points_per_minute=3`; the actual value is determined by server configuration.

Idempotency rules:

| Case | Result |
| --- | --- |
| First successful request | Creates task, charges credits, returns `taskId` |
| Same key + same body again | Returns the same response without charging again |
| Same key + different body | 409 `IDEMPOTENCY_KEY_REUSED` |
| Same key request still processing | 409 `IDEMPOTENCY_REQUEST_IN_PROGRESS` |

If a network timeout leaves uncertainty about whether the server received the request, retry the exact same body with the same `Idempotency-Key`.

## 6. Query Task Progress

```http
GET /video-translations/{taskId}
```

Important response fields:

| Field | Notes |
| --- | --- |
| `taskId` | Task ID |
| `status` | `pending`, `processing`, `completed`, `failed`, `cancelled` |
| `progress` | Task progress, usually `0..100` |
| `errorMessage` | Failure reason; usually empty for success or in-progress tasks |

Status rules:

| `status` | Terminal | Handling |
| --- | --- | --- |
| `pending` | No | Keep polling |
| `processing` | No | Keep polling |
| `completed` | Yes | Fetch results |
| `failed` | Yes | Stop polling and report `errorMessage` |
| `cancelled` | Yes | Stop polling |

Recommended polling strategy:

1. Query for the first time 2 seconds after task creation.
2. Back off while incomplete: `2s -> 5s -> 10s -> 20s -> 30s`.
3. Recommended maximum interval is 30 seconds.
4. For HTTP 429, wait according to `Retry-After`.
5. For HTTP 5xx, use exponential backoff with an overall timeout.

Stop polling only when the API returns `completed`, `failed`, or `cancelled`.

## 7. Fetch Results

### 7.1 List Results

```http
GET /video-translations/{taskId}/results?expiresIn=600
```

The task must be `completed`. `expiresIn` is optional. Media download URL TTL is clamped by the server to `60..3600` seconds and defaults to 3600.

Result file types:

| `type` | `variant` | Notes |
| --- | --- | --- |
| `video` | `video` | Final composed MP4 video |
| `audio` | `vocal` | Separated vocal WAV |
| `audio` | `background` | Separated background WAV |
| `audio` | `full` | Complete synthesized vocal audio WAV |
| `subtitle` | `source` | Source-language SRT subtitles |
| `subtitle` | `translated` | Target-language SRT subtitles |
| `subtitle` | `bilingual` | Bilingual SRT subtitles |

Handling rules:

- URLs with `access=media_gateway` are downloaded directly without an API key.
- Subtitle URLs with `access=api` and `requiresAuthorization=true` need the API key.
- If a media URL expires, call this endpoint or the single-file endpoint again to get a fresh URL.

### 7.2 Get One Media File URL

```http
GET /video-translations/{taskId}/results/files/{variant}?expiresIn=600
```

Supported `variant` values:

| `variant` | Content |
| --- | --- |
| `video` | Final composed MP4 video |
| `vocal` | Vocal WAV |
| `background` | Background WAV |
| `full` | Complete synthesized vocal audio WAV |

The response `url` is a temporary media gateway URL:

- Do not include the API key.
- Do not persist it long term.
- If download fails near `expiresAt`, call this endpoint again to refresh the URL.
- The media gateway supports Range GET for resumable large-file downloads.

### 7.3 Download Subtitles

```http
GET /video-translations/{taskId}/results/subtitles/{variant}
```

Supported `variant` values:

| `variant` | Content |
| --- | --- |
| `source` | Source-language subtitles |
| `translated` | Target-language subtitles |
| `bilingual` | Bilingual subtitles |

The response is plain SRT text, not JSON:

```http
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
```

Append `?download=1` to request attachment-style download. The subtitle endpoint is still an Agent API endpoint and requires an API key.

## 8. Retranslation

```http
POST /video-translations/{existingTaskId}/retranslate
Idempotency-Key: ${UNIQUE_IDEMPOTENCY_KEY}
```

Allowed existing task statuses:

- `completed`
- `failed`
- `cancelled`

The request body may be empty. If a body is provided, the API currently supports only:

```json
{
  "allowDynamicDuration": true
}
```

Retranslation creates a new task, charges credits, is subject to concurrency limits, and must use an `Idempotency-Key`.

## 9. Recoverable State Machine Guidance

Persist at least:

```json
{
  "apiBase": "https://xxx.com/api/v1",
  "fileId": "string",
  "uploadId": "string",
  "key": "string",
  "taskId": "string",
  "idempotencyKey": "string",
  "sourceLanguage": "auto",
  "targetLanguage": "en",
  "status": "pending|processing|completed|failed|cancelled"
}
```

Do not persist:

- Plaintext Agent API key
- Upload presigned URL
- Temporary media download URL
- Temporary signature query parameters, signatures, or credentials

Recommended state machine:

```text
NEW
  -> UPLOAD_INITIATED
  -> PART_PRESIGNED
  -> PART_UPLOADED
  -> UPLOAD_COMPLETED
  -> TASK_CREATED
  -> TASK_PROCESSING
  -> TASK_COMPLETED
  -> RESULT_DOWNLOADED
```

Recovery rules:

- If `uploadId` and `key` exist, presign unfinished parts again.
- If task creation may have reached the server, replay the same create body with the same `Idempotency-Key`.
- If `taskId` exists, resume from `GET /video-translations/{taskId}`.
- If a download URL expires, request `results/files/{variant}` or `results` again.

## 10. Error Code Quick Reference

| `error.code` | HTTP | Meaning | Auto-retry |
| --- | --- | --- | --- |
| `UNAUTHORIZED` | 401 | Missing API key | No |
| `API_KEY_INVALID` | 401 | Invalid API key | No |
| `API_KEY_EXPIRED` | 401 | Expired API key | No |
| `API_KEY_REVOKED` | 401 | Revoked API key | No |
| `RATE_LIMITED` | 429 | Rate-limited | Yes, wait for `Retry-After` |
| `CONCURRENCY_LIMIT_REACHED` | 429 | Account concurrency limit reached | Yes, wait for a task to finish |
| `INSUFFICIENT_CREDITS` | 402 | Insufficient credits | No |
| `INVALID_REQUEST` | 400 | Invalid request body, field, or variant | No |
| `MISSING_IDEMPOTENCY_KEY` | 400 | Missing or invalid idempotency key | No |
| `INVALID_FILE_SIZE` | 400 | Non-positive file size | No |
| `FILE_TOO_LARGE` | 400 | File too large | No |
| `INVALID_CONTENT_TYPE` | 400 | Not an MP4 file | No |
| `INVALID_LANGUAGE` | 400 | Unsupported language | No |
| `INVALID_SPEAKER_COUNT` | 400 | Invalid speaker count | No |
| `INVALID_DURATION` | 400 | Invalid video duration | No |
| `IDEMPOTENCY_KEY_REUSED` | 409 | Same key reused with a different body | No, upper layer must decide |
| `IDEMPOTENCY_REQUEST_IN_PROGRESS` | 409 | Same idempotent request is still processing | Yes, retry same body and key later |
| `UPLOAD_NOT_FOUND` | 404 / 409 | Upload session missing, expired, or not in an allowed state | Depends |
| `UPLOAD_NOT_COMPLETED` | 409 | File upload is not complete | No, complete upload first |
| `TASK_NOT_FOUND` | 404 | Task missing or unauthorized | No |
| `TASK_NOT_COMPLETED` | 409 | Task is not complete | Yes, keep polling |
| `LANGUAGE_PAIR_TASK_EXISTS` | 409 | Existing task for the same file and language pair | No, inspect `details.existingTaskId` |
| `FINAL_VIDEO_EXPIRED` | 409 | Final video output expired | No, reprocess or recover |
| `FINAL_AUDIO_EXPIRED` | 409 | Final audio output expired | No, reprocess or recover |
| `RESULT_NOT_READY` | 404 | Result file not ready yet | Yes, wait briefly and retry |
| `SUBTITLE_NOT_FOUND` | 404 | Subtitle missing or empty | No, except for brief retry just after completion |
| Any 5xx | 500 / 503 | Service temporarily unavailable | Yes, exponential backoff with a cap |

## 11. External Call Notes

- Callers only need the Base URL, Agent API key, and endpoint paths listed in this document.
- Do not cache or persist upload presigned URLs or temporary media download URLs.
- Do not write API keys, upload presigned URLs, or media download URLs to logs or conversation context.
- When a download URL expires, call the result endpoint again to get a fresh URL.
