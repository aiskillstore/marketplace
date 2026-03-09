# Steel Browser Troubleshooting

Use this reference when automation fails or behaves inconsistently.

## First diagnostic pass

Run:

```bash
steel browser sessions
steel browser live
# or: steel browser live --session <name>
```

Then verify:

- same mode across commands (cloud vs local/self-hosted),
- same `--session <name>` across workflow steps,
- auth and endpoint inputs are present.

## Common failures and fixes

### Missing auth

Symptom:

- `Missing browser auth. Run steel login or set STEEL_API_KEY.`

Fix:

```bash
steel login
```

or set `STEEL_API_KEY` in runtime environment.

### Self-hosted API unreachable

Symptom:

- Errors reaching Steel session API in local/self-hosted mode.

Fix:

1. Check endpoint flags/env resolution.
2. For local runtime flow:

```bash
steel dev install
steel dev start
steel browser start --local --session local-debug
```

### Session not reused

Symptom:

- New browser appears unexpectedly between steps.

Fix:

- Ensure exact same `--session <name>` value on every command.
- Ensure commands do not mix cloud and local mode.

### CAPTCHA encountered mid-flow

Important constraints:

- CAPTCHA solving requires a paid Steel plan.
- Proxies are strongly recommended for CAPTCHA and anti-bot evasion.
- `--proxy <url>` + CAPTCHA solving is the strongest default combo.

**Checking CAPTCHA solving progress:**

```bash
# Quick status check (shows type if solving)
steel browser captcha status
# Output: solving recaptchaV2

# Wait for CAPTCHA to resolve (blocks until done)
steel browser captcha status --wait
# Output: solved

# With custom timeout (2 minutes)
steel browser captcha status --wait --timeout 120000

# Full JSON for debugging
steel browser captcha status --raw
```

Use status checks to:

- Verify CAPTCHA was detected
- Wait for auto-solve to complete before continuing
- Diagnose failed solves (see type in output)

If session is auto solving (`--stealth`):

1. Check status and wait for resolution:

```bash
steel browser captcha status --wait
```

2. Or capture screenshots while waiting:

```bash
steel browser screenshot /tmp/captcha-auto-progress.png --session <name>
```

If session is manual solving (`--session-solve-captcha`):

1. Trigger solve:

```bash
steel browser captcha solve --session <name>
```

2. Wait for completion:

```bash
steel browser captcha status --wait
```

3. If needed, target a specific task:

```bash
steel browser captcha solve --session <name> --page-id <id> --task-id <id>
```

If session has no CAPTCHA solving enabled (default):

1. Start a new session with solving enabled.
2. Re-open the blocked page and continue.

```bash
SESSION="captcha-recovery-$(date +%s)"
steel browser start --session "$SESSION" --session-solve-captcha --proxy http://user:pass@host:port
steel browser open <blocked-url> --session "$SESSION"
```

### No active live session

Symptom:

- `No active live session found.`

Fix:

```bash
steel browser start --session my-job
steel browser live
```

### Stale state or stuck mapping

Fix:

```bash
steel browser stop --all
steel browser start --session fresh-job
```

## Safe CDP handling

- Treat `connect_url`/`connectUrl` as display-safe only.
- Build auth-bearing URLs from `session id` plus environment key in runtime, not from copied log output.

## Recovery pattern for agents

1. Capture failing command and exact error text.
2. Identify whether issue is auth, mode, endpoint, or session continuity.
3. Apply the smallest fix that addresses root cause.
4. Re-run prior command before attempting additional workflow steps.
