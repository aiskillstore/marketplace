---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: jira
---

# Jira REST API v3 Endpoints Reference

Base URL: `https://{domain}.atlassian.net/rest/api/3`

## Authentication

All requests require Basic Auth with email and API token:

```bash
AUTH=$(echo -n "email@example.com:API_TOKEN" | base64)
curl -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" ...
```

## Issue Operations

### Get Issue

```
GET /issue/{issueIdOrKey}
```

Query params: `fields`, `expand` (changelog, transitions, renderedFields)

### Create Issue

```
POST /issue
```

```json
{
  "fields": {
    "project": { "key": "PROJ" },
    "issuetype": { "name": "Task" },
    "summary": "Issue title",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Description text" }]
        }
      ]
    },
    "assignee": { "accountId": "user-account-id" },
    "labels": ["label1", "label2"],
    "priority": { "name": "High" }
  }
}
```

### Update Issue

```
PUT /issue/{issueIdOrKey}
```

Same body format as create, only include fields to update.

### Delete Issue

```
DELETE /issue/{issueIdOrKey}
```

### Add Comment

```
POST /issue/{issueIdOrKey}/comment
```

```json
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": "Comment text" }]
      }
    ]
  }
}
```

### Get Transitions

```
GET /issue/{issueIdOrKey}/transitions
```

Returns available status transitions for the issue.

### Transition Issue

```
POST /issue/{issueIdOrKey}/transitions
```

```json
{
  "transition": { "id": "21" }
}
```

### Assign Issue

```
PUT /issue/{issueIdOrKey}/assignee
```

```json
{ "accountId": "user-account-id" }
```

To unassign: `{ "accountId": null }`

### Add Labels

```
PUT /issue/{issueIdOrKey}
```

```json
{
  "update": {
    "labels": [
      { "add": "new-label" }
    ]
  }
}
```

### Link Issues

```
POST /issueLink
```

```json
{
  "type": { "name": "Blocks" },
  "inwardIssue": { "key": "PROJ-123" },
  "outwardIssue": { "key": "PROJ-456" }
}
```

## Search

### Search with JQL

```
GET /search?jql={jql}&maxResults=50&startAt=0
```

Or POST for complex queries:

```
POST /search
```

```json
{
  "jql": "project = PROJ AND status = 'In Progress'",
  "startAt": 0,
  "maxResults": 50,
  "fields": ["summary", "status", "assignee"]
}
```

## Project Operations

### List Projects

```
GET /project
```

### Get Project

```
GET /project/{projectIdOrKey}
```

Query params: `expand` (issueTypes, lead, description)

### Get Project Issue Types

```
GET /project/{projectIdOrKey}/statuses
```

## User Operations

### Get Current User

```
GET /myself
```

### Search Users

```
GET /user/search?query={query}
```

### Get User by Account ID

```
GET /user?accountId={accountId}
```

## Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No content (success) |
| 400 | Bad request - check parameters |
| 401 | Unauthorized - check credentials |
| 403 | Forbidden - check permissions |
| 404 | Not found |
| 429 | Rate limited |
