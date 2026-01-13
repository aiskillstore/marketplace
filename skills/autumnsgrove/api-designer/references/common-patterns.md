# Common API Patterns

Reusable patterns and practices for API design and implementation.

## Table of Contents

- [Health Check Endpoints](#health-check-endpoints)
- [Batch Operations](#batch-operations)
- [Webhook Patterns](#webhook-patterns)
- [Idempotency](#idempotency)
- [Long-Running Operations](#long-running-operations)
- [File Upload and Download](#file-upload-and-download)
- [Search and Autocomplete](#search-and-autocomplete)
- [Soft Deletes](#soft-deletes)

## Health Check Endpoints

### Basic Health Check

```http
GET /health

Response: 200 OK
{
  "status": "ok",
  "timestamp": "2025-10-25T10:30:00Z",
  "version": "1.2.3"
}
```

### Detailed Health Check

```http
GET /health/detailed

Response: 200 OK
{
  "status": "ok",
  "timestamp": "2025-10-25T10:30:00Z",
  "version": "1.2.3",
  "uptime": 86400,
  "services": {
    "database": {
      "status": "ok",
      "responseTime": 5,
      "connection": "active"
    },
    "cache": {
      "status": "ok",
      "responseTime": 2,
      "hitRate": 0.85
    },
    "externalApi": {
      "status": "degraded",
      "responseTime": 500,
      "lastError": "Timeout after 5s"
    }
  },
  "metrics": {
    "requestsPerMinute": 1200,
    "errorRate": 0.02,
    "averageResponseTime": 150
  }
}
```

### Readiness and Liveness

**Liveness** (is the service running?):
```http
GET /health/live

Response: 200 OK if service is running
Response: 503 Service Unavailable if service is down
```

**Readiness** (is the service ready to accept traffic?):
```http
GET /health/ready

Response: 200 OK if ready
Response: 503 Service Unavailable if not ready (e.g., initializing)
```

## Batch Operations

### Batch Create/Update

```http
POST /api/v1/users/batch

Request:
{
  "operations": [
    {
      "method": "POST",
      "path": "/users",
      "body": {
        "username": "user1",
        "email": "user1@example.com"
      }
    },
    {
      "method": "PATCH",
      "path": "/users/123",
      "body": {
        "email": "newemail@example.com"
      }
    },
    {
      "method": "DELETE",
      "path": "/users/456"
    }
  ]
}

Response: 200 OK
{
  "results": [
    {
      "status": 201,
      "body": { "id": "789", "username": "user1", ... }
    },
    {
      "status": 200,
      "body": { "id": "123", "email": "newemail@example.com", ... }
    },
    {
      "status": 204,
      "body": null
    }
  ],
  "summary": {
    "total": 3,
    "successful": 3,
    "failed": 0
  }
}
```

### Batch with Transactions

```http
POST /api/v1/batch

Request:
{
  "atomic": true,  # All operations succeed or all fail
  "operations": [...]
}

# If any operation fails with atomic=true
Response: 400 Bad Request
{
  "error": "BATCH_OPERATION_FAILED",
  "message": "Operation 2 failed, all operations rolled back",
  "failedOperation": {
    "index": 1,
    "error": "User with email already exists"
  }
}
```

## Webhook Patterns

### Webhook Registration

```http
POST /api/v1/webhooks

Request:
{
  "url": "https://your-app.com/webhook",
  "events": ["user.created", "post.published", "comment.added"],
  "secret": "webhook_secret_key_for_signature_validation",
  "active": true,
  "description": "Production webhook for user events"
}

Response: 201 Created
{
  "id": "webhook_abc123",
  "url": "https://your-app.com/webhook",
  "events": ["user.created", "post.published", "comment.added"],
  "active": true,
  "createdAt": "2025-10-25T10:00:00Z"
}
```

### Webhook Payload

```http
POST https://your-app.com/webhook

Headers:
X-Webhook-ID: webhook_abc123
X-Webhook-Signature: sha256=abc123...
X-Webhook-Event: user.created
X-Webhook-Delivery: delivery_xyz789

Body:
{
  "event": "user.created",
  "timestamp": "2025-10-25T10:30:00Z",
  "data": {
    "id": "usr_123",
    "username": "johndoe",
    "email": "john@example.com",
    "createdAt": "2025-10-25T10:30:00Z"
  }
}
```

### Webhook Signature Validation

**Server-side (sending)**:
```python
import hmac
import hashlib

def generate_signature(payload, secret):
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"
```

**Client-side (receiving)**:
```python
def verify_signature(payload, signature, secret):
    expected = generate_signature(payload, secret)
    return hmac.compare_digest(signature, expected)
```

### Webhook Retry Logic

```
Retry schedule on failure:
- Attempt 1: Immediately
- Attempt 2: After 1 minute
- Attempt 3: After 5 minutes
- Attempt 4: After 15 minutes
- Attempt 5: After 1 hour
- Attempt 6: After 6 hours
- Give up after 24 hours

Response handling:
- 2xx: Success, no retry
- 4xx: Client error, no retry (except 429)
- 429: Rate limited, retry with backoff
- 5xx: Server error, retry with backoff
- Timeout: Retry
```

## Idempotency

### Idempotency Keys

```http
POST /api/v1/payments
Idempotency-Key: unique-key-12345

Request:
{
  "amount": 1000,
  "currency": "USD",
  "description": "Payment for order #123"
}

# First request
Response: 201 Created
{
  "id": "pay_abc123",
  "amount": 1000,
  "status": "completed"
}

# Duplicate request (same idempotency key)
Response: 200 OK  # Returns cached result
{
  "id": "pay_abc123",  # Same payment ID
  "amount": 1000,
  "status": "completed"
}
```

### Implementation Guidelines

**Key Generation** (client-side):
```javascript
// Use UUID v4 for idempotency keys
const idempotencyKey = crypto.randomUUID();

fetch('/api/v1/payments', {
  method: 'POST',
  headers: {
    'Idempotency-Key': idempotencyKey
  },
  body: JSON.stringify(paymentData)
});
```

**Server-side Storage**:
```python
# Store idempotency key with result
{
  "idempotencyKey": "unique-key-12345",
  "method": "POST",
  "path": "/api/v1/payments",
  "responseStatus": 201,
  "responseBody": {...},
  "createdAt": "2025-10-25T10:00:00Z",
  "expiresAt": "2025-10-26T10:00:00Z"  # 24 hour expiration
}
```

**Best Practices**:
- Store idempotency keys for 24 hours
- Return exact same response for duplicate requests
- Use idempotency for all non-GET operations
- Include idempotency key in error responses
- Validate key format (UUID recommended)

## Long-Running Operations

### Async Operation Pattern

**Initial Request**:
```http
POST /api/v1/reports/generate

Request:
{
  "type": "sales_report",
  "startDate": "2025-01-01",
  "endDate": "2025-10-25"
}

Response: 202 Accepted
Location: /api/v1/jobs/job_abc123
{
  "jobId": "job_abc123",
  "status": "pending",
  "createdAt": "2025-10-25T10:00:00Z",
  "estimatedDuration": 300,
  "statusUrl": "/api/v1/jobs/job_abc123"
}
```

**Status Check**:
```http
GET /api/v1/jobs/job_abc123

# While processing
Response: 200 OK
{
  "jobId": "job_abc123",
  "status": "processing",
  "progress": 45,
  "progressMessage": "Processing records 4500/10000",
  "createdAt": "2025-10-25T10:00:00Z",
  "estimatedCompletion": "2025-10-25T10:05:00Z"
}

# When complete
Response: 200 OK
{
  "jobId": "job_abc123",
  "status": "completed",
  "progress": 100,
  "result": {
    "reportUrl": "/api/v1/reports/report_xyz789",
    "downloadUrl": "/api/v1/downloads/xyz789.pdf"
  },
  "completedAt": "2025-10-25T10:04:32Z"
}

# If failed
Response: 200 OK
{
  "jobId": "job_abc123",
  "status": "failed",
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "Failed to generate report due to insufficient data"
  },
  "failedAt": "2025-10-25T10:03:15Z"
}
```

### Job Status States

```
pending → processing → completed
                    → failed
                    → cancelled
```

**Status Definitions**:
- `pending`: Job queued but not started
- `processing`: Job actively running
- `completed`: Job finished successfully
- `failed`: Job encountered error
- `cancelled`: Job cancelled by user

## File Upload and Download

### File Upload (Multipart)

```http
POST /api/v1/files/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[Binary file data]
------WebKitFormBoundary
Content-Disposition: form-data; name="description"

Monthly report
------WebKitFormBoundary--

Response: 201 Created
{
  "id": "file_abc123",
  "filename": "document.pdf",
  "size": 1048576,
  "mimeType": "application/pdf",
  "url": "/api/v1/files/file_abc123",
  "uploadedAt": "2025-10-25T10:00:00Z"
}
```

### Chunked Upload (Large Files)

**Step 1: Initiate Upload**:
```http
POST /api/v1/uploads/initiate

Request:
{
  "filename": "large-video.mp4",
  "size": 524288000,
  "mimeType": "video/mp4",
  "chunkSize": 5242880  # 5MB chunks
}

Response: 201 Created
{
  "uploadId": "upload_xyz789",
  "chunkSize": 5242880,
  "totalChunks": 100,
  "expiresAt": "2025-10-25T22:00:00Z"
}
```

**Step 2: Upload Chunks**:
```http
PUT /api/v1/uploads/upload_xyz789/chunks/1
Content-Type: application/octet-stream

[Binary chunk data]

Response: 200 OK
{
  "uploadId": "upload_xyz789",
  "chunkNumber": 1,
  "uploaded": true
}
```

**Step 3: Complete Upload**:
```http
POST /api/v1/uploads/upload_xyz789/complete

Response: 201 Created
{
  "id": "file_abc123",
  "filename": "large-video.mp4",
  "size": 524288000,
  "url": "/api/v1/files/file_abc123"
}
```

### File Download

**Direct Download**:
```http
GET /api/v1/files/file_abc123/download

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
Content-Length: 1048576

[Binary file data]
```

**Presigned URL** (for direct S3/cloud storage access):
```http
POST /api/v1/files/file_abc123/download-url

Response: 200 OK
{
  "url": "https://s3.amazonaws.com/bucket/file?signature=...",
  "expiresAt": "2025-10-25T11:00:00Z",
  "expiresIn": 3600
}
```

## Search and Autocomplete

### Full-Text Search

```http
GET /api/v1/posts/search?q=graphql api design&limit=20

Response: 200 OK
{
  "query": "graphql api design",
  "results": [
    {
      "id": "post_123",
      "title": "GraphQL API Design Best Practices",
      "excerpt": "Learn how to design scalable <mark>GraphQL</mark> <mark>APIs</mark>...",
      "score": 0.95,
      "highlights": {
        "title": ["<mark>GraphQL</mark>", "<mark>API</mark>", "<mark>Design</mark>"],
        "content": ["building <mark>GraphQL</mark> <mark>APIs</mark>"]
      }
    }
  ],
  "total": 42,
  "took": 23
}
```

### Autocomplete

```http
GET /api/v1/search/autocomplete?q=grap&limit=5

Response: 200 OK
{
  "query": "grap",
  "suggestions": [
    {
      "text": "GraphQL",
      "category": "topic",
      "count": 145
    },
    {
      "text": "Graph Database",
      "category": "topic",
      "count": 89
    },
    {
      "text": "Grape (Ruby Framework)",
      "category": "library",
      "count": 34
    }
  ]
}
```

### Faceted Search

```http
GET /api/v1/products/search?q=laptop&facets=brand,price_range,rating

Response: 200 OK
{
  "results": [...],
  "facets": {
    "brand": [
      { "value": "Apple", "count": 45 },
      { "value": "Dell", "count": 78 },
      { "value": "HP", "count": 62 }
    ],
    "price_range": [
      { "value": "0-500", "count": 23 },
      { "value": "500-1000", "count": 89 },
      { "value": "1000+", "count": 73 }
    ],
    "rating": [
      { "value": "4+", "count": 156 },
      { "value": "3+", "count": 185 }
    ]
  }
}
```

## Soft Deletes

### Soft Delete Pattern

```http
# Soft delete (mark as deleted)
DELETE /api/v1/posts/123

Response: 200 OK
{
  "id": "post_123",
  "title": "My Post",
  "deleted": true,
  "deletedAt": "2025-10-25T10:00:00Z"
}

# Default behavior: exclude soft-deleted
GET /api/v1/posts
# Returns only non-deleted posts

# Include soft-deleted (admin/owner only)
GET /api/v1/posts?includeDeleted=true

# Permanently delete (hard delete)
DELETE /api/v1/posts/123?permanent=true

Response: 204 No Content
```

### Restore Deleted Items

```http
POST /api/v1/posts/123/restore

Response: 200 OK
{
  "id": "post_123",
  "title": "My Post",
  "deleted": false,
  "deletedAt": null,
  "restoredAt": "2025-10-25T10:30:00Z"
}
```

### Trash/Recycle Bin

```http
# List deleted items
GET /api/v1/trash

Response: 200 OK
{
  "items": [
    {
      "id": "post_123",
      "type": "post",
      "title": "My Post",
      "deletedAt": "2025-10-25T10:00:00Z",
      "permanentDeleteAt": "2025-11-24T10:00:00Z"  # Auto-delete after 30 days
    }
  ]
}

# Empty trash
DELETE /api/v1/trash

Response: 200 OK
{
  "deletedCount": 15
}
```
