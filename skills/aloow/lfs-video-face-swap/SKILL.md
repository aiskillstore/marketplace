---
name: lfs-video-face-swap
description: Estimate credits, prepare and start an approved face swap for an uploaded MP4, or check and download an existing video face swap using the Live Face Swap MCP. Use when the user wants Live Face Swap to process a prerecorded video or asks about a Live Face Swap task.
---

# Live Face Swap for uploaded video

Use the connected Live Face Swap MCP tools. If they are unavailable, point the user to the [installation instructions](README.md) or the [Live Face Swap MCP guide](https://live-face-swap.net/mcp). Use the connection the user selected. For local testing, keep every call on the local connection.

## Estimate and prepare

- For a price estimate, call `quote_video_face_swap` with `durationSeconds` between 1 and 30. Ask for the duration if it is unknown. Report `estimatedCredits` as an estimate. A quote-only request ends here.
- When the user wants to prepare a job, call `prepare_video_face_swap` with no arguments. Keep the returned `draftId` and share `preparationUrl` privately. The link expires after 30 minutes. Ask the user to open it with the same Live Face Swap account, select a 1–30 second MP4 with one clearly visible face and a portrait they have permission to use, and approve the exact quote shown on the site. Keep source files in that browser workflow.

## Start an approved job

- After the user confirms that they approved the exact quote on the site and explicitly asks to start, call `create_video_face_swap` with the same `draftId`. Starting reserves credits. Save the returned `taskId` for status checks.
- If the server reports `VIDEO_MCP_APPROVAL_REQUIRED`, send the user back to the preparation link. If the draft expired or the quote changed, offer a fresh preparation link and repeat the approval step. If the start request times out or the outcome is unclear, retry with the same `draftId` to avoid a duplicate job.

## Check and download

- Call `get_video_face_swap_result` with the existing `taskId`. For a status-only request, report the current state. While waiting for completion, honor `retryAfterSeconds` before checking again. If a call hits a rate limit, use the server's retry delay.
- On `completed`, report `billedCredits` when returned and share the private `resultUrl` with the user. The result page finishes the video in the browser and offers MP4 preview and download. On `failed`, report the failure and any billed credits returned. A new attempt requires a new approval.
