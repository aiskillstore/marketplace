# Parameter Mapping Reference / 参数映射参考表

## Common API Parameters / 通用API参数

| Parameter | Type | Default | Description |
|---|---|---|---|
| page | int | 1 | Page number (≥1) |
| page_size / count | int | 20 | Results per page (1-100) |
| cursor / max_cursor | int/string | 0 | Pagination cursor |
| sort_type / order_by | string | "" | Sort field |
| keyword / query | string | "" | Search keyword |

## Response Code / 响应码

| Code | Meaning | Description |
|---|---|---|
| 200 | Success | 请求成功 |
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | API Key 无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 数据不存在 |
| 422 | Validation Error | 参数验证失败 |
| 429 | Rate Limit | 请求过快 |
| 500 | Server Error | 服务器错误 |

## Cache / 缓存

- 成功响应包含 `cache_url`，有效期 24 小时
- 访问缓存结果不产生额外费用
