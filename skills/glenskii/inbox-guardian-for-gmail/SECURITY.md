# Security and Privacy Policy

## Privacy Statement

Inbox Guardian for Gmail is local software that runs on your own computer.
- All email analysis, rule checking, and token management happen on your machine.
- No analytics or telemetry are sent to a developer-operated service.
- The tool communicates with the official Google Gmail API at `https://gmail.googleapis.com` through the mailbox owner's Google Cloud OAuth client.
- Local activity history can retain sender and subject excerpts for reviewed actions in `guardian_stats.json`. The local reputation database can retain trusted sender addresses and domains. Both files are ignored by Git.

---

## Security Model and Design Rules

### 1. Header Analysis
Spam messages often change the visible sender name to imitate trusted brands while sending from unrelated servers. Gmail Guardian inspects both the visible `From:` header and the hidden `Return-Path:` address to determine where the email actually came from.

### 2. Protection for Legitimate Contacts
To avoid quarantining important messages, the tool applies a clear order of checks:
1. **Protected Mail**: Any message that you star, send, or save as a draft is always marked safe.
2. **Whitelist Priority**: Any sender address or domain in your allowed list always takes priority over keyword filters.
3. **Reputation Tracking**: The tool keeps a local record of people you email. These local contacts receive trusted-sender precedence. This is a convenience rule, not an identity verification service.
4. **Audit First**: The default action is an audit dry-run. It writes a signed, time-limited review file so you can verify results before any labels change.

### 3. Minimal Access Permissions
By default, the tool requests only the `https://www.googleapis.com/auth/gmail.modify` permission. This allows reading message headers, applying labels, archiving messages, and moving messages to Gmail Trash. It does not grant administrative access to the Google account.

Permanent deletion is not available through this skill. The strongest available action is an owner-approved move to Gmail Trash, which remains recoverable through Gmail's normal retention window.

Before execution, the utility verifies the review file signature, expiry, structure, message identifier format, and current classification. A changed or stale review file cannot trigger a mailbox action.

### 4. Unsubscribe Boundary

`List-Unsubscribe` headers are treated as untrusted review material. The tool shows the header but does not follow its links, send a request, or decide that the sender is legitimate. Use a known vendor site or Gmail's own unsubscribe interface when you choose to unsubscribe.

---

## How to Revoke Access

If you ever wish to disconnect the tool from your Google account:
1. Visit your [Google Account Third-Party Access Page](https://myaccount.google.com/permissions).
2. Find the application name you created in Google Cloud (for example, `Gmail-Guardian`).
3. Click **Remove Access**.
4. Delete the local `token.json` file from your project folder.
