# Email Operations API / 邮箱操作接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---

## get_temp_email

`GET/POST /api/v1/temp-mail/get_temp_email`

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| (varies) | | | See https://www.aconfig.cn for details |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

## get_emails

`GET/POST /api/v1/temp-mail/get_emails`

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| (varies) | | | See https://www.aconfig.cn for details |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

## get_email_by_id

`GET/POST /api/v1/temp-mail/get_email_by_id`

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| (varies) | | | See https://www.aconfig.cn for details |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

---

## Common Workflows / 常用工作流

See SKILL.md for cross-group orchestration patterns.
