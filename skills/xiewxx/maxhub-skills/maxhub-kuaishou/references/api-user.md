# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_get_user_id

`GET /api/v1/kuaishou/web/fetch_get_user_id`

<!-- Full path: /api/v1/kuaishou/web/fetch_get_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_link | string | ✅ | '' | https://v.kuaishou.com/KcdKDwFp |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过用户分享链接获取用户ID
 ### 参数:
 - share_link: 用户分享链接
 ### 返回:
 - 用户ID

## fetch_kuaishou_hot_list_v1

`GET /api/v1/kuaishou/web/fetch_kuaishou_hot_list_v1`

<!-- Full path: /api/v1/kuaishou/web/fetch_kuaishou_hot_list_v1 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取快手热榜 V1
### 参数:
- 无
### 返回:
- 快手热榜 V1 列表

## fetch_kuaishou_hot_list_v2

`GET /api/v1/kuaishou/web/fetch_kuaishou_hot_list_v2`

<!-- Full path: /api/v1/kuaishou/web/fetch_kuaishou_hot_list_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| board_type | string |  | '' (default: '1') | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取快手热榜 V2
### 参数:
- board_type 榜单类型，默认值为 1:
    1 - 热榜
    2 - 文娱
    3 - 社会
    4 - 有用
    5 - 挑战
    6 - 搜索
### 返回:
- 快手热榜 V2 列表

## fetch_user_info

`GET /api/v1/kuaishou/web/fetch_user_info`

<!-- Full path: /api/v1/kuaishou/web/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | '' | 3xz63mn6fngqtiq |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
    - 获取用户信息
    - 备注：
    - 此接口在请求时请将超时时间设置为30秒以上，否则可能会导致客户端未及时收到请求响应。
    - 此接口由于风控的特殊性，我们尽可能保持稳定，但仍然无法保证100%稳定，如果遇到请求失败，请稍后重试。
    - 推荐一直重复请求，直到成功为止，并且超时时间设置为30秒以上。
    ### 参数:
    - user_id: 用户ID，这个接口需要传入用户的 eid，可以从用户主页链接中提取
    - 例如：https://www.kuaishou.com/profile/3xz63mn6fngqtiq 其中 3xz63mn6fngqtiq 即为用户的 eid
    - 备注：不支持使用uid也就是纯数字的用户ID查询
    ### 返回:
    - 用户信息，包括昵称、头像、粉丝数、关注数、获赞数、性别等

---

See SKILL.md for cross-group orchestration patterns.