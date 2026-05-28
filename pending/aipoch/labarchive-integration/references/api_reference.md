# LabArchives API Reference Guide

## API Structure

All LabArchives API calls follow this URL pattern:

```
https://<base_url>/api/<api_class>/<api_method>?<authentication_parameters>&<method_parameters>
```

## Regional API Endpoints

| Region | Base URL |
|--------|----------|
| US/International | `https://api.labarchives.com/api` |
| Australia | `https://auapi.labarchives.com/api` |
| UK | `https://ukapi.labarchives.com/api` |

## Authentication

All API calls require authentication parameters:

- `access_key_id`: Provided by LabArchives administrator
- `access_password`: Provided by LabArchives administrator
- Some operations may require additional user-specific credentials

## API Classes and Methods

### Users API Class

#### `users/user_access_info`

Get user ID and notebook access information.

**Parameters:**
- `login_or_email` (required): User's email address or login username
- `password` (required): User's external applications password (not regular login password)

**Returns:** XML or JSON response containing:
- User ID (uid)
- List of accessible notebooks with their IDs (nbid)
- Account status and permissions

**Example:**
```python
params = {
    'login_or_email': 'researcher@university.edu',
    'password': 'external_app_password'
}
response = client.make_call('users', 'user_access_info', params=params)
```

#### `users/user_info_via_id`

Get detailed user information by user ID.

**Parameters:**
- `uid` (required): User ID obtained from user_access_info

**Returns:** User profile information including:
- Name and email
- Account creation date
- Institution
- Roles and permissions
- Storage quota and usage

**Example:**
```python
params = {'uid': '12345'}
response = client.make_call('users', 'user_info_via_id', params=params)
```

### Notebooks API Class

#### `notebooks/notebook_backup`

Download complete notebook data including entries, attachments, and metadata.

**Parameters:**
- `uid` (required): User ID
- `nbid` (required): Notebook ID
- `json` (optional, default: false): Return data in JSON format instead of XML
- `no_attachments` (optional, default: false): Exclude attachments from backup

**Returns:**
- When `no_attachments=false`: 7z compressed archive containing all notebook data
- When `no_attachments=true`: XML or JSON structured data containing entry content

**File Format:**
The returned archive contains:
- Entry text content in HTML format
- File attachments in original format
- Metadata XML files with timestamps, authors, and version history
- Comment threads and annotations

**Example:**
```python
# Full backup with attachments
params = {
    'uid': '12345',
    'nbid': '67890',
    'json': 'false',
    'no_attachments': 'false'
}
response = client.make_call('notebooks', 'notebook_backup', params=params)

# Write to file
with open('notebook_backup.7z', 'wb') as f:
    f.write(response.content)
```

```python
# Metadata-only backup (JSON format, no attachments)
params = {
    'uid': '12345',
    'nbid': '67890',
    'json': 'true',
    'no_attachments': 'true'
}
response = client.make_call('notebooks', 'notebook_backup', params=params)
import json
notebook_data = json.loads(response.content)
```

#### `notebooks/list_notebooks`

Get all notebooks accessible to a user (method name may vary by API version).

**Parameters:**
- `uid` (required): User ID

**Returns:** List of notebooks containing:
- Notebook ID (nbid)
- Notebook name
- Creation and modification dates
- Access level (owner, editor, viewer)
- Member count

### Entries API Class

#### `entries/create_entry`

Create a new entry in a notebook.

**Parameters:**
- `uid` (required): User ID
- `nbid` (required): Notebook ID
- `title` (required): Entry title
- `content` (optional): Entry content in HTML format
- `date` (optional): Entry date (defaults to current date)

**Returns:** Entry ID and creation confirmation

**Example:**
```python
params = {
    'uid': '12345',
    'nbid': '67890',
    'title': 'Experiment 2025-10-20',
    'content': '<p>Conducted PCR amplification of target gene...</p>',
    'date': '2025-10-20'
}
response = client.make_call('entries', 'create_entry', params=params)
```

#### `entries/create_comment`

Add a comment to an existing entry.

**Parameters:**
- `uid` (required): User ID
- `nbid` (required): Notebook ID
- `entry_id` (required): Target entry ID
- `comment` (required): Comment text (HTML supported)

**Returns:** Comment ID and timestamp

#### `entries/create_part`

Add a component/part to an entry (e.g., text section, table, image).

**Parameters:**
- `uid` (required): User ID
- `nbid` (required): Notebook ID
- `entry_id` (required): Target entry ID
- `part_type` (required): Part type (text, table, image, etc.)
- `content` (required): Part content in corresponding format

**Returns:** Part ID and creation confirmation

#### `entries/upload_attachment`

Upload a file attachment to an entry.

**Parameters:**
- `uid` (required): User ID
- `nbid` (required): Notebook ID
- `entry_id` (required): Target entry ID
- `file` (required): File data (multipart/form-data)
- `filename` (required): Original filename

**Returns:** Attachment ID and upload confirmation

**Example using requests library:**
```python
import requests

url = f'{api_url}/entries/upload_attachment'
files = {'file': open('/path/to/data.csv', 'rb')}
params = {
    'uid': '12345',
    'nbid': '67890',
    'entry_id': '11111',
    'filename': 'data.csv',
    'access_key_id': access_key_id,
    'access_password': access_password
}
response = requests.post(url, files=files, data=params)
```

### Site Reports API Class

Enterprise edition only, for institutional reporting and analytics.

#### `site_reports/detailed_usage_report`

Generate comprehensive usage statistics for an institution.

**Parameters:**
- `start_date` (required): Report start date (YYYY-MM-DD)
- `end_date` (required): Report end date (YYYY-MM-DD)
- `format` (optional): Output format (csv, json, xml)

**Returns:** Usage metrics including:
- User login frequency
- Entry creation counts
- Storage utilization
- Collaboration statistics
- Time-based activity patterns

#### `site_reports/detailed_notebook_report`

Generate detailed report of all notebooks in an institution.

**Parameters:**
- `include_settings` (optional, default: false): Include notebook settings
- `include_members` (optional, default: false): Include member list

**Returns:** Notebook inventory containing:
- Notebook name and ID
- Owner information
- Creation and last modification dates
- Member count and access levels
- Storage size
- Settings (if requested)

#### `site_reports/pdf_offline_generation_report`

Track PDF export records for compliance and auditing purposes.

**Parameters:**
- `start_date` (required): Report start date
- `end_date` (required): Report end date

**Returns:** Export activity log containing:
- User who generated PDF
- Notebooks and entries exported
- Export timestamp
- IP address

### Utilities API Class

#### `utilities/institutional_login_urls`

Get institution login URLs for SSO integration.

**Parameters:** None (uses access key authentication)

**Returns:** List of institution login endpoints

## Response Formats

### XML Response Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <uid>12345</uid>
    <email>researcher@university.edu</email>
    <notebooks>
        <notebook>
            <nbid>67890</nbid>
            <name>Lab Notebook 2025</name>
            <role>owner</role>
        </notebook>
    </notebooks>
</response>
```

### JSON Response Example

```json
{
    "uid": "12345",
    "email": "researcher@university.edu",
    "notebooks": [
        {
            "nbid": "67890",
            "name": "Lab Notebook 2025",
            "role": "owner"
        }
    ]
}
```

## Error Codes

| Code | Message | Meaning | Solution |
|------|---------|---------|----------|
| 401 | Unauthorized | Invalid credentials | Verify access_key_id and access_password |
| 403 | Forbidden | Insufficient permissions | Check user role and notebook access |
| 404 | Not Found | Resource does not exist | Verify uid, nbid, or entry_id is correct |
| 429 | Too Many Requests | Rate limit exceeded | Implement exponential backoff |
| 500 | Internal Server Error | Server-side issue | Retry request or contact support |

## Rate Limiting

LabArchives implements rate limiting to ensure service stability:

- **Recommended:** Maximum 60 requests per minute per API key
- **Burst tolerance:** Up to 100 requests may be tolerated for short periods
- **Best practice:** Implement 1-2 second delays between requests during bulk operations

## API Versioning

LabArchives API is backward compatible. Addition of new methods will not break existing implementations. Please watch LabArchives announcements for new feature information.

## Support and Documentation

For API access requests, technical issues, or feature suggestions:
- Email: support@labarchives.com
- Please include your institution name and specific use case in your email for faster assistance.
