# npx -y @insforge/cli config

Deep reference for `config export | plan | apply`. The SKILL.md Configuration section has the principles and rules; this file has output shapes and the error table.

**Scope today:** auth redirects and verification flags, password policy, SMTP, storage upload size, realtime/schedule retention, and cloud deployment subdomain. TOML does not manage external provider resources such as OAuth apps, storage bucket lifecycle, realtime channels, deployment env vars, functions, or secrets.

## Commands

```bash
npx -y @insforge/cli config export [--out insforge.toml] [--force]
npx -y @insforge/cli config plan   [--file insforge.toml]
npx -y @insforge/cli config apply  [--file insforge.toml] [--dry-run] [--auto-approve]
```

## File location

`insforge.toml` lives at the project root, alongside `package.json` and `.insforge/project.json`. Safe to commit to git.

## Output shapes (`--json` mode)

`config export`:

```json
{
  "written": "/abs/path/to/insforge.toml",
  "config": {
    "auth": {
      "allowed_redirect_urls": ["https://app.com"],
      "require_email_verification": true,
      "verify_email_method": "link",
      "reset_password_method": "code",
      "disable_signup": false,
      "password": {
        "min_length": 8,
        "require_number": false,
        "require_lowercase": true,
        "require_uppercase": false,
        "require_special_char": false
      },
      "smtp": {
        "enabled": false,
        "host": "",
        "port": 587,
        "username": "",
        "sender_email": "",
        "sender_name": "",
        "min_interval_seconds": 60
      }
    },
    "storage": { "max_file_size_mb": 100 },
    "realtime": { "retention_days": null },
    "schedules": { "retention_days": 7 },
    "deployments": { "subdomain": "my-app" }
  },
  "skipped": []
}
```

`config plan`:

```json
{
  "changes": [
    {
      "section": "auth",
      "op": "modify",
      "key": "allowed_redirect_urls",
      "from": ["https://app.com"],
      "to": ["https://app.com", "https://staging.app.com"]
    }
  ],
  "summary": { "add": 0, "modify": 1, "remove": 0, "kept": 0 },
  "skipped": []
}
```

`config apply`:

```json
{
  "plan": {
    /* same shape as plan output */
  },
  "applied": [
    /* DiffChange objects that were applied */
  ],
  "skipped": [
    {
      "key": "storage.max_file_size_mb",
      "reason": "your backend doesn't expose storage.max_file_size_mb — upgrade the project to apply this section"
    }
  ]
}
```

## Common mistakes

| Mistake                                                                                                                       | What to do instead                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Calling raw admin APIs directly for TOML-supported settings                                                                   | Use `config apply` — it's version-aware; direct writes can silently drop on older backends                                        |
| Treating `skipped[]` as an error to retry                                                                                     | It's intentional; surface verbatim with the upgrade ask and stop                                                                  |
| Running `config apply` in `--json` mode without `--yes`                                                                       | Add `-y`/`--yes` (global) or `--auto-approve` (subcommand alias — same effect); otherwise fails fast with `CONFIRMATION_REQUIRED` |
| Re-running with `--force` to "fix" a skip                                                                                     | `--force` is only for `export`'s overwrite gate; skips need a backend upgrade                                                     |
| Managing OAuth apps, email templates, storage buckets, realtime channels, secrets, functions, or deployment env vars via TOML | Use their dedicated dashboard or CLI flows; TOML only carries supported project config knobs                                      |

## Related

- `npx -y @insforge/cli metadata` — read-only view of all backend config slices
- **insforge** app-integration skill `auth/sdk-integration.md` — how SDK code reads auth config at runtime
