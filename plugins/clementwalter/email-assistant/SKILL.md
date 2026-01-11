---
name: email-assistant
description: User asks to read, check, or manage emails - User asks to reply to or send an email - User asks to draft an email response
---

# Email Assistant

Guidelines for reading and writing emails via Gmail MCP tools.

## When to Use

- User asks to read, check, or manage emails
- User asks to reply to or send an email
- User asks to draft an email response

## Core Rules

### 1. Succinct Responses

Keep email drafts **short and to the point**. Avoid:

- Unnecessary pleasantries
- Verbose explanations
- Redundant information

### 2. Match Input Language

**Always reply in the same language as the original email.**

- French email → French reply
- English email → English reply
- Mixed → Follow the dominant language

### 3. Validate Before Sending

**Never send an email without user approval.**

Workflow:

1. Read the email
2. Draft a response
3. Show the draft to the user
4. Wait for explicit confirmation ("yes", "send it", "ok")
5. Only then send the email

## Workflow

### Reading Emails

```text
1. Use list_emails to show recent emails
2. Use read_email to get full content when user selects one
3. Summarize key points if email is long
```

### Replying to Emails

```text
1. Read the original email
2. Identify the language
3. Draft a succinct reply in the same language
4. Present the draft:
   ---
   **To:** recipient@example.com
   **Subject:** RE: Original Subject
   **Attachment:** file.pdf (if any)

   > Draft content here
   ---
5. Ask: "Should I send this?"
6. Wait for confirmation
7. Use reply_email tool only after approval
```

### Sending New Emails

```text
1. Gather: recipient, subject, content
2. Draft the email
3. Present for validation
4. Send only after explicit approval
```

## Draft Format

Always present drafts in this format:

```text
**To:** recipient@example.com
**Subject:** Subject line
**Attachment:** filename.pdf (if applicable)

---

[Email body here]

---

Ready to send?
```

## Examples

### Good Draft (French)

```text
Bonjour,

Veuillez trouver ci-joint le document demandé.

Cordialement,
[Name]
```

### Bad Draft (Too verbose)

```text
Bonjour Monsieur,

J'espère que vous allez bien et que vous passez une excellente journée.
Je me permets de vous écrire pour vous transmettre le document que vous
m'avez demandé lors de notre dernier échange. Vous trouverez ci-joint
le fichier en question. N'hésitez pas à me contacter si vous avez des
questions ou si vous avez besoin d'informations supplémentaires.

Je vous souhaite une excellente fin de journée et reste à votre
entière disposition.

Bien cordialement,
[Name]
```

## Available Tools

| Tool            | Use For                            |
| --------------- | ---------------------------------- |
| `list_emails`   | Browse inbox                       |
| `read_email`    | Get full email content             |
| `search_emails` | Find specific emails               |
| `reply_email`   | Reply in thread (with attachments) |
| `send_email`    | New email (with attachments)       |

## Account Parameter

Use the 1Password item name for the `account` parameter:

- `"Gmail Zama Claude"` - Work account
- `"Gmail Personal Claude"` - Personal account

Ask user which account if unclear.
