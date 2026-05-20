# Video & Feed API / 视频与推荐接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_city_list

`GET /api/v1/weibo/web_v2/fetch_city_list`

<!-- Full path: /api/v1/weibo/web_v2/fetch_city_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| normalized | boolean |  | 是否返回标准化结构（省份列表+城市数组）/Whether to return normalized structure (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取地区省市映射数据，用于用户搜索等接口的地区筛选参数。
 ### 参数:
 - normalized: 是否返回标准化结构（默认True）
 ### 返回:
 - 省市映射数据，用于fetch_user_search等接口的region参数
 ### 注意:
 - 返回的编码格式为 custom:省代码:市代码，如 custom:11:1

## fetch_config_list

`GET /api/v1/weibo/web/fetch_config_list`

<!-- Full path: /api/v1/weibo/web/fetch_config_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博移动端所有频道的配置信息
 ### 返回:
 - 频道列表，包含频道名称和 containerid
 ### 说明:
 - 返回的 containerid 可用于 fetch_trend_top 接口获取对应频道的热门内容

---

See SKILL.md for cross-group orchestration patterns.