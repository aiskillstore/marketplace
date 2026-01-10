# Microsoft Graph API Reference

Detailed API documentation for Microsoft Graph endpoints used by this skill.

## Base URL

All requests go to: `https://graph.microsoft.com/v1.0`

## Authentication

Microsoft Graph uses OAuth 2.0. This skill uses the device code flow:

1. App requests device code from Azure AD
2. User opens URL and enters code in browser
3. User authenticates with Microsoft account
4. App receives access token and refresh token

### Token Refresh

Access tokens expire after ~1 hour. The `GraphClient` automatically:
1. Checks token expiration before requests
2. Uses refresh token to get new access token
3. Updates stored credentials

### Scopes

| Scope | Permission | Use Case |
|-------|------------|----------|
| `User.Read` | Read user profile | Get current user info |
| `Mail.Read` | Read all mail | Full email access |
| `Mail.ReadBasic` | Read basic mail | Subject, sender, date only |
| `Calendars.Read` | Read calendars | View calendar events |

## Email Endpoints

### List Messages

```
GET /me/messages
GET /me/mailFolders/{folder-id}/messages
```

**Parameters:**
- `$top` - Number of results (max 1000)
- `$skip` - Offset for pagination
- `$select` - Fields to return
- `$orderby` - Sort order
- `$filter` - OData filter
- `$search` - Search query

**Example:**
```
GET /me/messages?$top=10&$orderby=receivedDateTime desc
```

### Get Message

```
GET /me/messages/{message-id}
```

**Fields:**
- `id` - Message ID
- `subject` - Subject line
- `from` - Sender info
- `toRecipients` - Recipients
- `receivedDateTime` - When received
- `body` - Full body content
- `bodyPreview` - First 255 chars
- `isRead` - Read status
- `hasAttachments` - Has files
- `importance` - low, normal, high

### Search Messages

```
GET /me/messages?$search="query"
```

**Search syntax:**
- `from:email@example.com`
- `to:email@example.com`
- `subject:keyword`
- `body:keyword`
- `hasAttachments:true`
- `isRead:false`
- `received>=2024-01-01`
- `"exact phrase"`

Combine with spaces: `from:boss@company.com subject:urgent`

### List Folders

```
GET /me/mailFolders
```

**Well-known folder names:**
- `inbox`
- `drafts`
- `sentitems`
- `deleteditems`
- `junkemail`
- `archive`

Custom folders use their ID.

## Calendar Endpoints

### Calendar View

```
GET /me/calendarView?startDateTime={start}&endDateTime={end}
```

Returns events within date range, including recurring event instances.

**Parameters:**
- `startDateTime` - ISO 8601 datetime
- `endDateTime` - ISO 8601 datetime
- `$top` - Number of results
- `$orderby` - Sort order

**Example:**
```
GET /me/calendarView?startDateTime=2024-01-01T00:00:00Z&endDateTime=2024-01-31T23:59:59Z
```

### List Events

```
GET /me/events
```

Returns event masters (not recurring instances).

**Parameters:**
- `$top` - Number of results
- `$filter` - OData filter
- `$orderby` - Sort order

**Filter examples:**
```
$filter=contains(subject,'meeting')
$filter=start/dateTime ge '2024-01-01'
```

### Get Event

```
GET /me/events/{event-id}
```

**Fields:**
- `id` - Event ID
- `subject` - Event title
- `start` - Start datetime and timezone
- `end` - End datetime and timezone
- `location` - Location info
- `organizer` - Who created it
- `attendees` - List of attendees
- `body` - Description
- `bodyPreview` - Short preview
- `isAllDay` - All day event
- `recurrence` - Recurrence pattern

## Error Responses

### 401 Unauthorized

Token expired or invalid:
```json
{
  "error": {
    "code": "InvalidAuthenticationToken",
    "message": "Access token has expired."
  }
}
```

**Solution:** Refresh token or re-authenticate.

### 403 Forbidden

Missing required permission:
```json
{
  "error": {
    "code": "Authorization_RequestDenied",
    "message": "Insufficient privileges to complete the operation."
  }
}
```

**Solution:** Re-authenticate with required scopes.

### 404 Not Found

Resource doesn't exist:
```json
{
  "error": {
    "code": "ErrorItemNotFound",
    "message": "The specified object was not found in the store."
  }
}
```

### 429 Too Many Requests

Rate limited:
```json
{
  "error": {
    "code": "TooManyRequests",
    "message": "Too many requests"
  }
}
```

**Solution:** Wait and retry. Check `Retry-After` header.

## Rate Limits

Microsoft Graph has per-app and per-user limits:

| Limit Type | Requests |
|------------|----------|
| Per app per second | 2000 |
| Per user per 10 minutes | 10000 |

The scripts don't implement retry logic - if rate limited, wait and retry manually.

## Pagination

Large result sets are paginated:

```json
{
  "value": [...],
  "@odata.nextLink": "https://graph.microsoft.com/v1.0/me/messages?$skip=10"
}
```

Use `@odata.nextLink` to get next page. The scripts use `$top` to limit results instead of pagination.

## OData Query Options

### $select

Return only specific fields:
```
$select=id,subject,from
```

### $top and $skip

Pagination:
```
$top=10&$skip=20
```

### $orderby

Sort results:
```
$orderby=receivedDateTime desc
$orderby=start/dateTime asc
```

### $filter

Filter results:
```
$filter=isRead eq false
$filter=importance eq 'high'
$filter=contains(subject,'report')
```

### $search

Full-text search (messages only):
```
$search="from:john subject:meeting"
```

## Timezone Handling

Calendar events include timezone info:
```json
{
  "start": {
    "dateTime": "2024-01-15T10:00:00.0000000",
    "timeZone": "Pacific Standard Time"
  }
}
```

The scripts convert to local time for display. JSON output preserves original timezone.

## References

- [Microsoft Graph documentation](https://learn.microsoft.com/en-us/graph/)
- [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
- [Permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference)
