# Private configuration and usage

Set `WORKFLOW_CONFIG` to a private JSON file outside the public repository. Required issue settings: `jira_url`, `jira_project`, `jira_board_id`, `jira_sprint_field`. Branch work also requires `bitbucket_workspace` and `local_root`, where each clone is stored as `<local_root>/<repository-slug>`. Obtain the sprint field ID and board ID from your own Jira configuration; do not copy illustrative IDs without verification.

Credentials come only from `JIRA_EMAIL`, `JIRA_API_TOKEN`, `BITBUCKET_USERNAME` and `BITBUCKET_API_TOKEN`. Configure these through your usual credential manager. Do not print them or store them in request files. Use the provider's supported API-token authentication and the minimum permissions needed for the requested work.

Save this complete example as `request.json` in the task's private working directory:

```json
{
  "summary": "Show saved inventory items",
  "description": "Observed: saved inventory items disappear after reloading the inventory page. Expected: authorized users can still see saved items after reload.",
  "issue_type": "Bug"
}
```

From this skill's directory:

```bash
python scripts/create_branch.py --input request.json
python scripts/create_branch.py --input request.json --apply
python scripts/create_branch.py DEMO-1 --repo service
python scripts/create_branch.py DEMO-1 --repo service --apply
```

The second command creates a real issue; the fourth creates/reuses a real branch and applies the configured board defaults. Use the returned real issue key, not the illustrative `DEMO-1`. Combine `--input` and `--repo` only when both operations are requested. `--assignee-account-id`, `--status`, `--type` and `--from` express explicit user choices.

Do not repeat the create command after a timeout. Search for the issue first and resume using its key. Previewing is not an authorization prompt; when the user has already requested the complete operation, finish the authorized work and verify it.
