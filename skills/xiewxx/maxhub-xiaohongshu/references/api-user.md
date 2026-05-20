# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_follower_list

`GET /api/v1/xiaohongshu/web_v2/fetch_follower_list`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_follower_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 604a28420000000001005211 |
| cursor | string |  | 游标/Cursor (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户粉丝列表
### 参数:
- user_id: 用户ID
- cursor: 游标
### 返回:
- 用户粉丝列表

## fetch_following_list

`GET /api/v1/xiaohongshu/web_v2/fetch_following_list`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_following_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 604a28420000000001005211 |
| cursor | string |  | 游标/Cursor (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户关注列表
### 参数:
- user_id: 用户ID
- cursor: 游标
### 返回:
- 用户关注列表

## fetch_search_users

`GET /api/v1/xiaohongshu/web_v2/fetch_search_users`

<!-- Full path: /api/v1/xiaohongshu/web_v2/fetch_search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keywords | 口红 |
| page | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取搜索用户
### 参数:
- keywords：搜索关键词
- page：页码
### 返回:
- 搜索用户

## fetch_search_users

`GET /api/v1/xiaohongshu/web_v2/fetch_search_users`

<!-- Full path: /api/v1/xiaohongshu/web_v3/fetch_search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keywords | 口红 |
| page | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索用户
 ### 接口优先级:
 - 小红书接口推荐优先级: `App V2` > `App` > `Web V3（本接口）` > `Web V2` > `Web`
 ### 参数:
 - keyword: 搜索关键词
 - page: 页码
 ### 返回:
 - 搜索用户结果

## get_user_id_and_xsec_token

`GET /api/v1/xiaohongshu/app/get_user_id_and_xsec_token`

<!-- Full path: /api/v1/xiaohongshu/app/get_user_id_and_xsec_token -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_link | string | ✅ | 用户分享链接/User share link | https://xhslink.com/m/Ap1vXtgAixh |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 从用户分享链接中提取用户ID和xsec_token
 ### 参数:
 - share_link: 小红书用户分享链接，支持短链接和长链接
 ### 返回:
 - 提取的信息对象，包含：
    - user_id: 用户ID
    - xsec_token: 安全令牌（如果URL中包含）
 ### 使用说明:
 - 支持短链接格式：https://xhslink.com/m/xxxxx
 - 支持长链接格式：https://www.xiaohongshu.com/user/profile/xxxxx
 - 提取的user_id可用于get_user_info接口

## search_users

`GET /api/v1/xiaohongshu/app_v2/search_users`

<!-- Full path: /api/v1/xiaohongshu/app_v2/search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 美食博主 |
| page | integer |  | 页码，从1开始/Page number, start from 1 (default: 1) | 1 |
| search_id | string |  | 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination (default: '') |  |
| source | string |  | 来源/Source (default: explore_feed) | explore_feed |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词搜索小红书用户，每页返回 20 条结果，支持分页
 ### 参数:
 - keyword: 搜索关键词（必需），如 "美食博主"
 - page: 页码，从 1 开始
 - search_id: 搜索ID，翻页时传入首次搜索返回的值
 - source: 来源，默认 "explore_feed"
 ### 返回:
 - 搜索结果数据，包含用户列表和分页信息
 ### 翻页说明:
 - 首次请求：只传keyword和page
 - 翻页请求：传入首次搜索返回的 search_id

## search_users

`GET /api/v1/xiaohongshu/app_v2/search_users`

<!-- Full path: /api/v1/xiaohongshu/web/search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Keyword | 美食 |
| page | integer |  | 页码/Page (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索用户
### 参数:
- keyword: 搜索关键词
- page: 页码，默认为1
### 返回:
- 用户列表

---

See SKILL.md for cross-group orchestration patterns.