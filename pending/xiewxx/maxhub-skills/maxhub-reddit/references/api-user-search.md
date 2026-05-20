# User & Search API / 用户与搜索接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_comment_replies

`GET /api/v1/reddit/app/fetch_comment_replies`

<!-- Full path: /api/v1/reddit/app/fetch_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID (e.g., t3_1qmup73) |  |
| cursor | string | ✅ | >- |  |
| sort_type | string |  | >- (default: CONFIDENCE) |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP指定评论下的回复（二级评论/子评论）
 - 当评论节点有 more.cursor 字段时，使用此接口获取该评论的子评论
 ### 参数:
 - post_id: 帖子ID，格式如 "t3_XXXXXX"
 - cursor: 评论游标，从评论数据的 more.cursor 字段获取，格式如 "commenttree:ex:(xxx)"
 - sort_type: 排序方式，支持CONFIDENCE, NEW, TOP, HOT, CONTROVERSIAL, OLD,
RANDOM
 ### 返回:
 - 指定评论下的回复JSON数据，包含：
  - 子评论列表
  - 每个子评论的详细信息（内容、作者、点赞数等）
  - 分页信息
### 使用步骤:
 1. 先调用 fetch_post_comments 获取帖子的一级评论
 2. 在返回数据中找到有子评论的节点（childCount > 0）
 3. 获取该节点的 more.cursor 值
 4. 使用该 cursor 调用本接口获取子评论
 ### 注意:
 - cursor 值来自评论数据的 more.cursor 字段
 - 路径示例: $.data.postInfoById.commentForest.trees[*].more.cursor
 - cursor 格式类似: "commenttree:ex:(RjiJd"

## fetch_user_profile

`GET /api/v1/reddit/app/fetch_user_profile`

<!-- Full path: /api/v1/reddit/app/fetch_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | 用户名/Username |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Reddit APP指定用户的详细资料信息
### 参数:
- username: Reddit用户名(不带u/前缀)
### 返回:
- 用户资料JSON数据,包含:
  - 用户名和ID
  - 账号创建时间
  - Karma值(帖子karma和评论karma)
  - 头像和横幅图片
  - 个人简介
  - 是否验证账号
  - 徽章和奖励
  - 关注者数量

---

See SKILL.md for cross-group orchestration patterns.