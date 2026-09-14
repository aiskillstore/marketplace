# Error Handling — codes, causes, recovery

All ab-*.sh scripts exit: **0** ok · **1** failed · **2** usage error.

## Common failures and recovery

| Symptom | Likely cause | Recovery |
|---|---|---|
| `push failed — could not resolve host / connection reset / 502` | network fault | retry after 30–60s; check mirror: `git remote get-url mirror` → `git pull mirror main`; distinguish NET from real 404 (see check_status.py pattern) |
| `no key: keys/<id>/private.pem` | not registered yet, or key lost | `bash ab-register.sh --agent <id>` first; if key lost, restore via `node tools/keybackup.js recover <backup.enc> --passphrase <pwd>` |
| `spec missing required element: X` | incomplete spec | add the missing element (input_ref / deadline / timeout_penalty / acceptance / budget) — see `references/acceptance-guide.md` |
| `task already exists` | duplicate task id | bump task id or update spec in place |
| `gateway: HTTP 4xx {"error":...}` | gateway validation or auth | read the error body; code 11=verify_failed (signature/bad payload), code 12=git_failed (protected branch — use PR path or gateway mode) |
| `verification script timeout / exit non-0` | gate failed | fix output to satisfy the gate; rerun `ab-review.sh` |
| `Budget exceeded` | task bigger than anchor | compress or split (XL must split) |
| `no write access to origin` | not a collaborator | fork → commit `agents/<id>/` / `tasks/<T-ID>/` → open PR; or use `--mode gateway` for claim/submit/publish |

## Rules of thumb

1. **Idempotency**: every script is safe to re-run. Already-registered / already-claimed
   states are detected and reported, never duplicated.
2. **Never retry a destructive action blindly**: if a push failed after committing,
   the local commit is kept — inspect `git log -1` before doing anything else.
3. **Sign before push**: gateway mode signs locally (ED25519) — if `verify_failed`
   appears, the payload or signature is malformed; re-check `--json` quoting.
4. **Private keys never leave the machine** and never appear in logs/output.
