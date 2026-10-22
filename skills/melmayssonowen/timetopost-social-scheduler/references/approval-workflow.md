# Draft and approval lifecycle

`whoami` reports workspace and token capabilities. Read-only actions inspect state; draft actions create content; publish actions can reach an audience.

1. `create_drafts` creates pending approval items and does not publish them.
2. Display every pending draft for human review.
3. `approve_draft` approves and schedules the item. Call it only after the user explicitly approves that specific copy, account, and timing.
4. Use `reject_draft` only when the user asks to reject. A rejected draft cannot be posted.
5. Confirm status with `list_drafts` or `get_post` where appropriate.

If multiple accounts share a platform, specify the account IDs from `list_integrations`; never let the server guess.
