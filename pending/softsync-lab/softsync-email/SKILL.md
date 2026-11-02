---
name: softsync-email
description: "Write email templates and send them to one contact or a list, and follow or cancel the send. Use when the user wants to write, fix or send a reusable email, or check how a send is going."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Email

Mail goes out from a mailbox the workspace has already connected. Each recipient gets their own personalised copy, so a list send is many single emails, not one group message.

## Order of operations
1. `list_mailboxes`: check a mailbox is connected. If the list is empty, stop. Connecting a mailbox needs a sign-in in the app.
2. `email_templates` with action `list`, then action `get` to read the one you will send.
3. No suitable template, or one needs fixing? Follow the `email-templates` reference.
4. `manage_email_campaigns` with action `send`, the template and the recipient record ids. One recipient is fine.
5. `get_email_campaign` to follow progress, and `manage_email_campaigns` with action `cancel` to stop what has not gone out yet.

## What to know
- A template belongs to one object (for example contacts) and can only be sent to records of that object.
- A placeholder the recipient's record has no value for renders as empty text.
- Sending is paced under the mailbox's hourly and daily limits, so a large list can take a long time. The call returns before anything is delivered.
- Sent mail cannot be recalled.

## Rules
- Never invent addresses: each email goes to the address on the recipient's record. Resolve recipients with the records skill.
- Show the user the template and the recipient count and wait for a clear yes before sending.

## More detail
Read these when the task needs them:
- [email-templates](references/email-templates.md): Writing, changing and deleting templates, and which {{placeholders}} you may use.
