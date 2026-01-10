---
name: Microsoft Graph API
description: This skill should be used when the user asks to "read my emails", "send an email", "compose email", "check my calendar", "get calendar events", "create a meeting", "schedule an event", "add calendar event", "search emails", "list mail folders", "show unread messages", "what meetings do I have", "fetch emails from Microsoft", "access Outlook", or mentions Microsoft Graph, Office 365 email, or Outlook calendar integration.
version: 0.3.0
---

# Microsoft Graph API Integration

Access Microsoft 365 emails and calendar through TypeScript scripts executed via Bun.

## Overview

This skill provides access to Microsoft Graph API for:
- **Email**: List, read, search, and send emails
- **Calendar**: View, search, and create calendar events

All scripts return JSON and handle authentication automatically.

## Response Format

All scripts output JSON with a consistent structure:

### Success
```json
{"status": "success", "data": [...]}
```

### Authentication Required
```json
{
  "status": "auth_required",
  "userCode": "ABC123",
  "verificationUri": "https://microsoft.com/devicelogin",
  "expiresAt": "2024-01-15T10:30:00.000Z",
  "message": "To sign in, use a web browser..."
}
```

When you receive `auth_required`, display to the user:
```
To access your email, please authenticate:
1. Go to: https://microsoft.com/devicelogin
2. Enter code: ABC123

Let me know when you've completed authentication.
```

Then **retry the same command** - the script will automatically complete authentication.

### Authentication Pending
```json
{
  "status": "auth_pending",
  "userCode": "ABC123",
  "verificationUri": "https://microsoft.com/devicelogin",
  "expiresAt": "...",
  "message": "..."
}
```

User has been shown the code but hasn't completed login yet. Remind them to complete authentication.

### Error
```json
{"status": "error", "error": "Error description"}
```

## Email Access

All scripts are located at `${CLAUDE_PLUGIN_ROOT}/skills/microsoft-graph/scripts/`.

### List Emails

```bash
bun run ${CLAUDE_PLUGIN_ROOT}/skills/microsoft-graph/scripts/emails.ts list
bun run emails.ts list --folder "Sent Items" --top 5
bun run emails.ts list --profile work
```

### Read Specific Email

```bash
bun run emails.ts read --id AAMkAG...
```

Get the ID from the `list` command output.

### Search Emails

```bash
bun run emails.ts search --query "from:boss@company.com"
bun run emails.ts search --query "subject:quarterly report"
bun run emails.ts search --query "hasAttachments:true"
```

### List Mail Folders

```bash
bun run emails.ts folders
```

### Send Email

```bash
# Simple email
bun run emails.ts send --to "user@example.com" --subject "Hello" --body "Hi there!"

# Multiple recipients with CC
bun run emails.ts send --to "a@example.com,b@example.com" --cc "c@example.com" --subject "Team Update" --body "Here's the update..."

# HTML email
bun run emails.ts send --to "user@example.com" --subject "Report" --body "<h1>Monthly Report</h1><p>Details...</p>" --html

# With BCC
bun run emails.ts send --to "team@example.com" --bcc "manager@example.com" --subject "Announcement" --body "..."
```

## Calendar Access

### List Upcoming Events

```bash
bun run ${CLAUDE_PLUGIN_ROOT}/skills/microsoft-graph/scripts/calendar.ts list
bun run calendar.ts today
bun run calendar.ts week
bun run calendar.ts list --start tomorrow --end +7d
```

### View Specific Event

```bash
bun run calendar.ts view --id AAMkAG...
```

### Search Events

```bash
bun run calendar.ts search --query "team standup"
```

### Date Formats

- **Relative**: `today`, `tomorrow`, `+7d`, `+1m`, `+1y`
- **Absolute**: ISO format `2024-01-15` or `2024-01-15T14:00:00`

### Create Calendar Event

```bash
# Basic event (1 hour default duration)
bun run calendar.ts create --subject "Team Meeting" --start "2024-01-15T14:00:00"

# Event with end time
bun run calendar.ts create --subject "Workshop" --start "2024-01-15T09:00:00" --end "2024-01-15T12:00:00"

# Event with location and description
bun run calendar.ts create --subject "Lunch" --start "2024-01-15T12:00:00" --location "Cafe" --body "Team lunch"

# Event with attendees
bun run calendar.ts create --subject "1:1" --start tomorrow --end +1d --attendees "colleague@example.com"

# Multiple attendees
bun run calendar.ts create --subject "Review" --start "2024-01-15T10:00:00" --attendees "a@ex.com,b@ex.com,c@ex.com"

# All-day event
bun run calendar.ts create --subject "Holiday" --start "2024-12-25" --all-day

# Using relative dates
bun run calendar.ts create --subject "Follow-up" --start tomorrow --end +1d
```

## Multi-Profile Support

Store multiple accounts using profiles:

```bash
# Use work profile
bun run emails.ts list --profile work
bun run calendar.ts today --profile work

# Use personal profile
bun run emails.ts list --profile personal
```

## Manual Authentication

For explicit auth management (listing/deleting profiles):

```bash
# List all profiles
bun run ${CLAUDE_PLUGIN_ROOT}/skills/microsoft-graph/scripts/auth.ts --list

# Delete a profile
bun run auth.ts --delete --profile old-account

# Authenticate with custom Azure AD app
bun run auth.ts --client-id your-app-id --tenant-id your-tenant-id
```

## Token Lifecycle

| Token Type | Lifetime | Handling |
|------------|----------|----------|
| Access Token | ~1 hour | Automatically refreshed |
| Refresh Token | ~90 days | When expired, scripts return `auth_required` |

Users only need to re-authenticate when the refresh token expires (~90 days).

## Credential Storage

Credentials are stored at `~/.config/api-skills/credentials.json`.

## Script Reference

| Script | Purpose |
|--------|---------|
| `emails.ts` | Email list, read, search, send, and folder operations |
| `calendar.ts` | Calendar view, search, and create operations |
| `auth.ts` | Manual credential management (list, delete profiles) |

## Additional Resources

For detailed API reference, see:
- **`references/graph-api.md`** - Microsoft Graph API endpoints and parameters
