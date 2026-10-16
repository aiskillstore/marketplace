# Configuration and request format

Helpers require Python 3.10+, `requests`, Git and Bitbucket Cloud. Point `WORKFLOW_CONFIG` to a private JSON file containing `base_branch`, nonempty `reviewers` (objects with `uuid`), `review_bot_user_id`, `review_channel_id` and `announcement_channel_id`. Resolve the IDs in your own workspace; examples are not usable identities. Set `BITBUCKET_USERNAME` and `BITBUCKET_API_TOKEN` privately. The connected Slack tools supply Slack access as the intended user; no Slack credential is accepted by these scripts.

Save this complete illustrative request privately, replacing the local path and description with the actual requested change:

```json
{
  "summary": "PRs for saved inventory visibility:",
  "pull_requests": [
    {
      "repository": "/path/to/your/service",
      "base": "develop",
      "title": "Keep saved inventory items visible after reload",
      "description": "Reloading the inventory page previously hid saved items. Load the persisted items for authorized users. Validation: describe only checks actually completed for this source commit."
    }
  ]
}
```

From this skill's directory:

```bash
python scripts/prepare_prs.py --request request.json --output plan.json
python scripts/prepare_prs.py --request request.json --output handoff.json --apply
python scripts/check_review.py --handoff handoff.json --thread thread.txt
```

The second command writes real PRs when authorized; the others perform reads. `prepare_prs.py` does not post Slack messages. `check_review.py` consumes a detailed connected-tool thread snapshot with `From: ... (USER_ID)`, `Time:` and `Message TS:` lines. Convert another connector's response faithfully to that format or adapt the parser. Preserve sender identity and timestamps; never invent a clean review.
