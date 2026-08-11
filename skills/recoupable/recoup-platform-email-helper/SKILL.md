---
name: recoup-platform-email-helper
description: Send an email via the Recoup API the reliable way — a Node helper that serializes the body correctly and fails loudly instead of sending an empty email. Use whenever a task needs to email a report/summary/notification to the account owner or a recipient. ALWAYS use this script to send email; never hand-build `curl … -d "{…}"` with inline `jq`/shell interpolation (that silently produces empty "Message from Recoup" footer-only emails). Pairs with recoup-platform-api-access (which it sends through).
---

# Sending email from a task

Send email by running the bundled Node script — **do not** assemble JSON in the shell.

## Why this exists

Hand-rolling the send (`curl -sS … -d "{… \"html\": $(echo "$HTML" | jq -R -s '.') …}"`) is fragile: depending on quoting/escaping it produces a **malformed body**, and the API used to silently deliver an empty footer-only email titled **"Message from Recoup"** with `success:true`. The model gets this wrong stochastically. This script removes shell serialization entirely.

## How to send

1. Write the email body to a file (recommended for HTML — avoids all escaping issues):

   ```bash
   cat > /tmp/report.html <<'HTML'
   <h1>Daily Report</h1>
   <p>…your real content…</p>
   HTML
   ```

2. Send it:

   ```bash
   node "$SKILL_DIR/scripts/send-email.mjs" \
     --subject "Daily Report — $(date '+%B %d, %Y')" \
     --html-file /tmp/report.html \
     --to owner@example.com
   ```

`$SKILL_DIR` is this skill's install directory (`~/.agents/skills/recoup-platform-email-helper`); use the absolute path to `scripts/send-email.mjs`.

## Flags

| Flag | Meaning |
|------|---------|
| `--subject <s>` | Subject line (optional — the API derives one from the body if omitted). |
| `--html-file <path>` / `--html <s>` | HTML body. Prefer `--html-file`. |
| `--text-file <path>` / `--text <s>` | Plain-text body. |
| `--to <email>` | Recipient (repeatable). **Omit to default to the account's own email** ("email me this"). |
| `--cc <email>` | CC (repeatable). |
| `--chat-id <id>` | Room id for the footer "continue the conversation" link. |
| `--dry-run` | Serialize + validate and print the payload; do **not** send. Use to preview. |

## Rules

- **Exactly one body is required.** The script **refuses to send** (exit code 2) if there is no non-empty `--html`/`--text`. Never try to send an empty email.
- **Check the exit code.** Non-zero means it did **not** send — read stderr and fix it; do not report success. The script prints the Resend message id on a real send.
- The script reads `RECOUP_API_KEY` / `RECOUP_ACCESS_TOKEN` and `RECOUP_API_BASE` from the environment — these are already set in the sandbox. Never print or hard-code them.
- Node only (the sandbox runtime is `node22`; `python3` is not guaranteed). Zero dependencies.
