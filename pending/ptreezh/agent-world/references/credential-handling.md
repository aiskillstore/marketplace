# Credential Handling — Discipline for Multi-Platform Agent Accounts

## Rules (field-tested, non-negotiable)

1. **Never commit credentials.** API keys, private keys, claim tokens, verification codes → always in gitignored files. The agent-world skill itself never contains secrets — only the *method*.
2. **Server-issued private keys cannot be recovered.** agentid.sh returns a private key and explicitly does not store it. The moment you receive it: save to a gitignored file, note the path in your local index, never echo it into chat logs or commits.
3. **Per-platform credential files** (pattern used by AgentBazaar):
   ```
   docs/geo/<platform>-promo/<handle>-account.md   (gitignored)
   ```
   Content: handle, api_key/token, id, verification code, claim URL, creation date, status.
4. **Rotation**: if a credential leaks into any commit or chat, rotate it immediately (re-register or regenerate), record the rotation in the platform log.
5. **Beware tokens in URLs / headers in logs**: use `--noproxy "*"` and never print full Bearer tokens in command output you will paste back.
6. **The skill is public; secrets are private.** Everything in `skills/agent-world/` and `docs/agent-world-map.md` must stay publishable — no tokens, no keys, no cookies.

## Minimal gitignore pattern

```gitignore
# agent credentials (never commit)
docs/geo/*/agent*.md
*.account.md
*.identity.md
*.key
*.pem
```

## If you must hand off to a human

- SMS-claim (XiaLiao), phone (InStreet user claim), X-post (Agentica), or CAPTCHA → stop that platform branch and hand off to the operator with the exact URL and what to do. Do not fake completion; do not bypass.
