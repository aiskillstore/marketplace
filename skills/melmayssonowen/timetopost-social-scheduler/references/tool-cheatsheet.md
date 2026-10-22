# TimeToPost tools used by this workflow

Tool names below are from the supplied public TimeToPost reference.

- `whoami`: workspace and publish capability. First call.
- `get_capabilities`, `list_integrations`: supported platforms and connected account IDs.
- `list_posts`: recent work for voice matching.
- `prompt_suggest`: hook or video prompt ideas.
- `create_drafts`: distinct pending-approval drafts by platform and account.
- `get_optimal_times`: account history based timing suggestions.
- `list_approvals`, `list_drafts`: inspect the review queue.
- `approve_draft`: approves and schedules; requires explicit user instruction.
- `reject_draft`: rejects a draft.
- `get_post`: inspect final status and permalink.

The hosted service may expose `build_campaign_urls`; it is not listed in the supplied stdio tool reference. Do not call an unavailable tool. Use the local URL helper when needed.
