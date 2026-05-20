# Cameo API / 出镜秀接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_cameo_leaderboard

`GET /api/v1/sora2/get_cameo_leaderboard`

<!-- Full path: /api/v1/sora2/get_cameo_leaderboard -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cursor | string |  | 翻页参数（可选）/Cursor for pagination (optional) (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora Cameo 出镜秀达人排行榜
 - 展示在 Cameo 功能中被使用最多的用户
 - 支持分页获取更多排行榜数据
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - cursor: 翻页参数（可选），从上一次响应的 cursor 字段获取，每页返回 10 个用户
  ### 返回:
 - items: 用户排行榜列表（每页 10 个用户）
    - user_id: 用户 ID
    - username: 用户名
    - display_name: 显示名称
    - profile_picture_url: 头像链接
    - follower_count: 粉丝数
    - cameo_count: 被使用次数
- cursor: 下一页参数，用于获取更多数据（如果为 null 表示已到末页）

## get_user_cameo_appearances

`GET /api/v1/sora2/get_user_cameo_appearances`

<!-- Full path: /api/v1/sora2/get_user_cameo_appearances -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | user-xiCyLclE6KJcdTXyvVq3Ontc |
| cursor | string |  | 翻页参数，从上一次响应中获取/Pagination cursor from previous response (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 Sora 用户的 Cameo 出镜秀列表
 - Cameo 出镜秀指该用户在其他创作者作品中的出镜视频
 - 支持分页加载，每页返回 30 条记录
 - 可用于展示用户的协作作品、出镜记录等
 - 本接口支持使用免费额度，每天可通过在用户后台签到获取免费调用次数。
  ### 参数:
 - user_id: 用户 ID，必填
 - cursor: 翻页参数（可选），首次请求留空，后续请求使用上一次响应中的 cursor 值
  ### 返回:
 - items: Cameo 出镜秀列表（30条/页）
    - post: 作品信息（该用户出镜的作品）
        - id: 作品 ID
        - text: 作品描述
        - attachments: 视频附件信息
        - like_count: 点赞数
        - view_count: 浏览数
        - shared_by: 原创作者 ID
        - posted_at: 发布时间戳
    - profile: 原创作者信息
- cursor: 下一页参数（用于获取更多记录，无更多时为 null）
 - has_more: 是否有更多数据

## upload_image

`POST /api/v1/sora2/upload_image`

<!-- Full path: /api/v1/sora2/upload_image -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 上传图片到 Sora 服务器获取 media_id
 - 获取的 media_id 可用于后续的 AI 视频生成功能
 - 支持 PNG、JPG、JPEG 格式的图片文件
 - 速率限制：每秒最多请求 1 次（1 request/second）
 - 如果请求过快可能会被限流，建议间隔至少 1 秒
  ### 参数说明:
 - **file** (必填): 图片文件
  - 支持格式: PNG, JPG, JPEG
  - 文件大小: 最大 10MB
 ### 返回数据:
 - **id**: Media ID（用于视频生成）
 - **url**: 图片访问链接
 - **kind**: 资源类型（通常为 "image"）
 - **width**: 图片宽度（像素）
 - **height**: 图片高度（像素）
 - **file_name**: 文件名
  ### 注意事项:
 - 上传的图片会存储在服务器上
 - 返回的 media_id 有效期通常为 24 小时
 - 建议在获取 media_id 后及时使用
 - 文件名会自动清理特殊字符以确保安全
  ---

---

See SKILL.md for cross-group orchestration patterns.