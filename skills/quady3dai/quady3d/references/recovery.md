# Recover without replacing a generation

| Observation | Continue with |
| --- | --- |
| Create interrupted; action ID known but job ID unknown | Same `create_job` action ID, quote ID and limit; MCP reuses its original body |
| Job ID known | `get_job` on that ID; use `list_jobs` if needed |
| Job says `submission_unknown` | Query that task while the service confirms acceptance |
| Wait ended while queued or processing | Continue the same task; stopping a wait does not cancel it |
| Download interrupted or file failed validation | Same asset download, preserving the original task |
| Destination already exists | Choose a different path or inspect the existing file |
| New submission definitively rejected for expired quote or upload | Refresh input and quote within the user's authorization; use a new action identity for the new body |
| Budget or balance insufficient | Explain the restriction; do not increase limits, change accounts or buy credits |
| Credential changed on the same API/account and `local_recovery.across_keys` is true | Reuse the original action, quote and limit; the saved original request can be replayed even after its quote expires |
| Older credential was revoked before its recovery records were associated | Query a known job with server ownership checks; preserve unassociated records, and do not infer their account from balance or project paths |
| Identity cannot be confirmed or saved requests conflict | Repair the connection and preserve original IDs. Do not reconstruct an unknown submission with a new quote or action |
| `local_recovery_saved: false` with a job or file | Preserve the returned identity/path; fix local storage separately without regenerating |
| Confirmed terminal action was cleaned from local history | Query the original job ID. Local action records expire seven days after the first observed terminal status; this does not remove the project file or authorize a replacement |

Retain available request, action, job and asset IDs and describe the actual stage. If both the original record and task identity are missing after an ambiguous submission, explain what needs recovery instead of silently creating another task.

Only `succeeded` and `failed` are terminal. Returned credit state determines refunds; do not promise one from a local timeout or canceled conversation. Read current capabilities before suggesting another model or operation.
