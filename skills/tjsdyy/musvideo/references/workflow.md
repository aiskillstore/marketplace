# Tools and recovery

Always use the host's live `tools/list` schemas. These are the eleven public tools; internal Director planning tools are not part of this integration.

| Tool | Main inputs | Effect |
| --- | --- | --- |
| `get_account` | none | Read connected account |
| `get_credit_balance` | none | Read remaining credits |
| `import_song` | exactly one of `audioUrl` or host-provided `file`; optional `title` | Import, no credit charge |
| `create_mv_project` | `songId`, fresh `requestId`; optional `stylePrompt`, `aspectRatio`, `title` | Spend approved analysis/story fee |
| `get_mv_progress` | `projectId` | Read state, story, progress, billing and result |
| `approve_story` | `projectId`, optional `feedback` | Approve displayed story; generate storyboard |
| `quote_mv_render` | `projectId` | Read current render estimate and quote |
| `start_mv_render` | `projectId`, `quoteId` | Spend credits as approved rendering progresses |
| `cancel_mv_render` | `projectId`, current `renderId` | Stop future work on user request; running work may still finish and incur charges |
| `list_my_videos` | optional `limit` (1–20), `cursor`, `status` | Find projects; status is `all`, `completed` or `in_progress` |
| `get_video` | `projectId` | Read playable result and watch page |

## Resume instead of duplicating

- Keep project ID, last confirmed story, creation request ID and render ID in the conversation or the host's normal task state. Do not store passwords, tokens or signed playback URLs in public files.
- After a timeout creating a project, repeat the exact call with the same `requestId`. After an uncertain render start, check progress before retrying; never create a new project as a workaround.
- `story_ready`: show the actual story; wait for approval. `storyboard_ready`: obtain a render quote and cost approval.
- `needs_credits`: state the reported balance and requirement. Keep the existing project, without purchase advice.
- `render_failed` or `failed`: report the real error. Completed work remains available. Read billing for actual refunds. Offer a fresh quote for recoverable remaining work; confirm its cost.
- Already-running operation: wait and check progress. Don't start parallel duplicate operations.
- Expired quote / changed storyboard: re-quote and reconfirm, even if an earlier price was approved.
- Cancellation: only on explicit user request, with the current render ID. Do not promise a full refund.
- `website_only`: older editor projects can be viewed through MCP but continued on musvideo.ai.
- For any unknown error, explain what was observed; do not claim a backend change, refund, cancellation or completion without a tool receipt.
