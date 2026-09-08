# npx -y @insforge/cli login

Authenticate with the InsForge platform.

## Syntax

```bash
npx -y @insforge/cli login [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--user-api-key <key>` | Authenticate directly with a `uak_` user API key (no browser, no prompt) — best for headless / agent / CI use |
| `--email` | Use email/password login instead of OAuth |
| `--device` | Device login (RFC 8628): user approves a short code on the dashboard while the CLI polls — use this in sandboxes (ChatGPT app, SSH, containers) |
| `--client-id <id>` | Custom OAuth client ID |

## Authentication Methods

### OAuth (Default)

Opens your browser for OAuth 2.0 authentication with PKCE:

```bash
npx -y @insforge/cli login
```

The CLI starts a local callback server, opens the browser, and waits up to 5 minutes for you to authorize.

### Device login (`--device`) — use this in sandboxes

In sandboxed environments (the ChatGPT app, remote/SSH sessions, containers), the browser runs on the host but the CLI's `127.0.0.1` callback server is inside the sandbox, so the default flow can never complete (it waits until its callback timeout). Use the device flow instead (requires `@insforge/cli` ≥ 0.2): no callback and nothing to paste — the user approves a short code in their browser while the CLI polls.

**Run it as two steps.** `login --device` prints the link, then keeps running until the user approves — but most agent harnesses only return a command's output when the process exits, so a single blocking run shows you nothing to relay. Bound the first run to capture the link, relay it, then rerun to complete (the rerun resumes the SAME pending code from `~/.insforge/pending-device.json`):

```bash
# Step 1 — capture the verification link (process is killed after 15s; that's expected)
timeout 15 npx -y @insforge/cli login --device --json 2>&1 || true
```

Output includes the link and code, e.g.:

```text
To sign in, ask the user to open:

  https://insforge.dev/auth/device?user_code=BCDF-GHJK

and confirm the code BCDF-GHJK. Waiting for approval...
```

Relay that link and code to the user. They open it, check the code matches, and click **Authorize** — nothing to type or paste. Then:

```bash
# Step 2 — after relaying (or once the user says they approved): resume and complete
npx -y @insforge/cli login --device --json
```

If the user already approved, step 2 completes immediately with the `--json` success object; otherwise it polls until they do. Codes expire after 15 minutes; both steps must run with the same `$HOME`. In an interactive terminal (a human at a shell), skip the two-step dance — just run `npx -y @insforge/cli login --device` and wait.

### User API Key (direct) — recommended for headless / agent / CI

No browser, no interactive prompt. Create a key in the dashboard (Profile → API Keys):

```bash
npx -y @insforge/cli login --user-api-key "$INSFORGE_USER_API_KEY"
```

The key is stored and sent directly as the bearer credential on every request — it authenticates as your account with full access. There is no token exchange or refresh: if the key is revoked or expires, the CLI asks you to log in again.

### Email/Password

```bash
npx -y @insforge/cli login --email
```

Prompts for email and password interactively. For non-interactive use (CI/CD), set environment variables:

```bash
INSFORGE_EMAIL=user@example.com INSFORGE_PASSWORD=secret npx -y @insforge/cli login --email
```

## Credential Storage

Credentials are saved to `~/.insforge/credentials.json` with restricted file permissions (0600). The shape depends on the login method:
- OAuth / email — `access_token` (JWT) + `refresh_token`
- User API key — `user_api_key` (the `uak_`, used directly as the bearer)

Plus user info (id, name, email). OAuth/email sessions refresh their JWT automatically on 401; a user-API-key session isn't refreshed — an invalid key prompts a re-login.

## Examples

```bash
# Interactive OAuth login (recommended for humans)
npx -y @insforge/cli login

# Headless / agent / CI: user API key login (no browser)
npx -y @insforge/cli login --user-api-key "$INSFORGE_USER_API_KEY" --json

# Sandbox (e.g. ChatGPT app): device login, two steps — capture link, relay, resume
timeout 15 npx -y @insforge/cli login --device --json 2>&1 || true
npx -y @insforge/cli login --device --json

# Email/password login
npx -y @insforge/cli login --email

# CI/CD non-interactive login via email/password
INSFORGE_EMAIL=$EMAIL INSFORGE_PASSWORD=$PASSWORD npx -y @insforge/cli login --email --json
```
