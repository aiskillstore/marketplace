# Gmail Tools

Secure Gmail access via IMAP/SMTP with 1Password credential storage. Supports listing, reading, searching, sending, and replying to emails with proper threading and attachments.

## When to Use

- Reading and managing Gmail emails
- Sending emails with attachments
- Replying to emails while maintaining thread continuity
- Searching emails using IMAP queries

## Prerequisites

### 1Password Setup

Create a 1Password item with:

- **Item name**: Any descriptive name (e.g., "Gmail Work Claude", "Gmail Personal")
- **username** field: Your Gmail address (e.g., `user@gmail.com`)
- **password** field: Gmail App Password (NOT your regular password)

### Getting a Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. Go to "App passwords" (under "2-Step Verification")
4. Generate a new app password for "Mail"
5. Copy the 16-character password to your 1Password item

## MCP Server Tools

The plugin provides these MCP tools:

### list_emails

List recent emails from an account.

```text
account: "Gmail Work Claude"  # 1Password item name
folder: "INBOX"               # Optional, default: INBOX
limit: 10                     # Optional, default: 10
```

### read_email

Read full email content including threading headers.

```text
account: "Gmail Work Claude"
email_id: "46"                # From list_emails
folder: "INBOX"               # Optional
```

### send_email

Send a new email with optional attachments.

```text
account: "Gmail Work Claude"
to: "recipient@example.com"
subject: "Hello"
body: "Email content here"
cc: "cc@example.com"          # Optional
bcc: "bcc@example.com"        # Optional
attachments: ["/path/to/file.pdf"]  # Optional
```

### reply_email

Reply to an email, maintaining the thread.

```text
account: "Gmail Work Claude"
email_id: "46"                # Email to reply to
body: "Thanks for your message!"
attachments: ["/path/to/doc.pdf"]  # Optional
folder: "INBOX"               # Optional
```

### search_emails

Search using IMAP syntax.

```text
account: "Gmail Work Claude"
query: "FROM sender@example.com"  # or "SUBJECT hello", "UNSEEN", etc.
folder: "INBOX"               # Optional
limit: 10                     # Optional
```

## Standalone Scripts

For CLI usage without MCP, use scripts in `scripts/`:

### List Emails

```bash
./scripts/gmail_list.py "Gmail Work Claude" --limit 20
./scripts/gmail_list.py "Gmail Work Claude" --json  # JSON output
```

### Read Email

```bash
./scripts/gmail_read.py "Gmail Work Claude" "46"
./scripts/gmail_read.py "Gmail Work Claude" "46" --json
```

### Reply to Email

```bash
# Dry run (preview without sending)
./scripts/gmail_reply.py "Gmail Work Claude" "46" \
  --body "Thanks for your email." \
  --attachment ~/document.pdf \
  --dry-run

# Send reply
./scripts/gmail_reply.py "Gmail Work Claude" "46" \
  --body "Thanks for your email." \
  --attachment ~/document.pdf
```

## Email Threading

When using `reply_email`, the tool automatically:

1. Extracts the original email's `Message-ID` and `References` headers
2. Sets `In-Reply-To` to the original `Message-ID`
3. Builds proper `References` header chain
4. Adds `RE:` prefix to subject if not present
5. Sends to the sender's email address

This ensures replies appear in the same thread in all email clients.

## Common IMAP Search Queries

| Query                  | Description                   |
| ---------------------- | ----------------------------- |
| `ALL`                  | All messages                  |
| `UNSEEN`               | Unread messages               |
| `FROM "john"`          | From sender containing "john" |
| `SUBJECT "meeting"`    | Subject containing "meeting"  |
| `SINCE "01-Jan-2024"`  | Messages since date           |
| `BEFORE "01-Jan-2024"` | Messages before date          |
| `BODY "keyword"`       | Body containing "keyword"     |

Combine with parentheses: `(FROM "john" SUBJECT "meeting")`

## Troubleshooting

### "1Password item not found"

Verify the exact item name in 1Password matches what you're using.

### "Authentication failed"

- Ensure you're using an App Password, not your regular Gmail password
- Verify 2FA is enabled on your Google account
- Check the App Password hasn't been revoked

### "IMAP not enabled"

Enable IMAP in Gmail Settings → Forwarding and POP/IMAP → Enable IMAP
