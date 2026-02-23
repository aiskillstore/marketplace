# Bot API Quick Reference

Base URL: `https://api.unlock.govilo.xyz`

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/bot/uploads/presign` | Bearer sk_live_xxx | Get presigned upload URL |
| POST | `/api/v1/bot/items` | Bearer sk_live_xxx | Confirm upload and create item |

## Presign Request

```json
POST /api/v1/bot/uploads/presign
{"seller_address": "0x..."}
```

Response: `upload_url`, `session_id`, `object_path`, `expires_at`

## Upload

```
PUT <upload_url>
Content-Type: application/zip
Body: <raw ZIP bytes>
```

## Create Item Request

```json
POST /api/v1/bot/items
{"session_id": "...", "title": "...", "price": "5.00", "description": "..."}
```

Response: `id`, `unlock_url`, `file_count`, `total_size`, `upload_status`

## Error Codes

| Code | HTTP | Message |
|------|------|---------|
| 809108001 | 401 | invalid api key |
| 809108002 | 401 | api key has been revoked |
| 809108003 | 401 | api key has expired |
| 809108005 | 429 | daily api key usage limit exceeded |
| 809108006 | 429 | api key rate limit exceeded |
| 809104001 | 404 | upload session not found |
| 809104002 | 410 | upload session expired |
| 809104003 | 404 | file not found |
