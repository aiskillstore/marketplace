# Authentication workflows

## Preferred approach

Use vault/state-based authentication so secrets are not repeatedly passed in prompts.

## Login once, reuse session state

```bash
agent-browser open https://app.example.com/login
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json
```

## Reuse saved auth

```bash
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

## Security notes

- Prefer environment variables for credentials.
- Avoid embedding secrets in committed scripts.
- Scope auth files per environment and rotate regularly.
