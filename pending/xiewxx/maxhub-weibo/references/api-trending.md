# Trending & Hot API / 热搜与趋势接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_trend_top

`GET /api/v1/weibo/web/fetch_trend_top`

<!-- Full path: /api/v1/weibo/web/fetch_trend_top -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| containerid | string | ✅ | 频道容器ID/Channel container ID | 102803_ctg1_8999_-_ctg1_8999_home |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定频道的热门趋势内容
 ### 参数:
 - containerid: 频道容器ID，可从 fetch_config_list 接口获取
 - page: 页码，默认1
 ### 返回:
 - 热门微博列表
 ### 说明:
 - containerid 示例: 102803_ctg1_8999_-_ctg1_8999_home
 - 可通过 fetch_config_list 获取所有可用的 containerid

---

See SKILL.md for cross-group orchestration patterns.