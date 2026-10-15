# Jira acceptance comment example

This is synthetic formatting guidance. Replace each statement with observed evidence; never copy a PASS without running the test. Screenshots must exist beneath the draft's directory before posting.

```markdown
### Dev acceptance: PASS

Inventory page:

| What was verified | Role | Result | Screenshot |
| --- | --- | --- | --- |
| A saved item remains visible after a fresh login | Authorized editor | PASS | ![](screenshots/item-after-login.png) |
| An account without edit permission cannot edit the item | Viewer | PASS | ![](screenshots/viewer-readonly.png) |

### Test data

- Dedicated test accounts were used; no credentials are included.
- Changed test records were restored and the restoration was verified.
```

Keep approval, commit and deployment provenance in the local report. Agreed requirement changes belong in the issue description only when its edit is requested. The comment reports verification; it does not silently redefine the scope.

From the skill directory, preview the real draft:

```bash
python scripts/post_jira_acceptance.py --issue DEMO-1 --comment-file /path/to/private/report/jira-comment.md
```

Add `--apply` only for explicitly requested posting. Add `--transition` only when the user requests the specific status change. Inspect the issue after an unknown write outcome before retrying; do not duplicate comments or attachments.
