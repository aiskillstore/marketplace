# Search & Explore API / 搜索与发现接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_cities

`GET /api/v1/instagram/v1/fetch_cities`

<!-- Full path: /api/v1/instagram/v1/fetch_cities -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| country_code | string | ✅ | 国家代码（如US、CN、JP）/Country code (e.g. US, CN, JP) | US |
| page | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定国家的城市/地区列表
### 参数:
- country_code: 国家代码，如US、CN、JP
- page: 页码，默认1
### 返回:
- `country_info`: 国家信息
- `city_list`: 城市列表
- `next_page`: 下一页页码

## fetch_explore_sections

`GET /api/v1/instagram/v1/fetch_explore_sections`

<!-- Full path: /api/v1/instagram/v1/fetch_explore_sections -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Instagram探索页面的所有分类和子分类
 ### 返回:
 - `sections`: 分类列表，包含分类名称、子分类和推荐内容

## fetch_locations

`GET /api/v1/instagram/v1/fetch_locations`

<!-- Full path: /api/v1/instagram/v1/fetch_locations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| city_id | string | ✅ | 城市ID（从fetch_cities获取）/City ID (from fetch_cities) | c2791472 |
| page | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定城市下的Instagram地点列表
### 参数:
- city_id: 城市ID（可从fetch_cities接口获取）
- page: 页码，默认1
### 返回:
- `country_info`: 国家信息
- `city_info`: 城市信息
- `location_list`: 地点列表
- `next_page`: 下一页页码

## general_search

`GET /api/v1/instagram/v2/general_search`

<!-- Full path: /api/v1/instagram/v2/general_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | cat |
| pagination_token | string |  | 分页token/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词进行Instagram综合搜索
 - 支持分页获取
 ### 参数:
 - keyword: 搜索关键词
 - pagination_token: 分页token，从上一次响应获取
 ### 返回:
 - `data.items`: 综合搜索结果列表，包含用户、帖子、Reels等
 - `pagination_token`: 下一页token

## general_search

`GET /api/v1/instagram/v2/general_search`

<!-- Full path: /api/v1/instagram/v3/general_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | justin |
| next_max_id | string |  | >- |  |
| rank_token | string |  | >- |  |
| enable_metadata | boolean |  | 是否启用元数据/Enable metadata (default: true) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - Instagram综合搜索接口（支持分页）
 - 支持通过 next_max_id 分页获取大量搜索结果
 - 返回用户、话题标签、地点等综合结果
 ### 参数:
 - query: 搜索关键词
 - next_max_id: 分页ID，首次请求不传，从上一次响应的 `data.next_max_id` 获取
 - rank_token: 排序token，首次请求不传，从上一次响应的 `data.rank_token` 获取
 - enable_metadata: 是否启用元数据
 ### 返回:
 - `data.num_results`: 结果数量
 - `data.users`: 用户搜索结果列表
 - `data.places`: 地点搜索结果列表
 - `data.hashtags`: 话题标签搜索结果列表
 - `data.next_max_id`: 下一页分页ID（传给下次请求的next_max_id参数）
 - `data.rank_token`: 排序token（传给下次请求的rank_token参数）
 - `data.has_more`: 是否有更多结果
 ### 注意事项:
 - ⚠️ **已知问题**: 综合搜索结果可能存在重复数据，这是 Instagram API 的已知行为
 - 搜索话题标签时，query 需要带上 `#` 前缀，例如搜索 fashion 话题应传入 `#fashion`
 - `#` 符号在 URL 中需要进行 URL 编码为 `%23`，例如: `?query=%23fashion`
 - 如果使用 HTTP 客户端库（如 requests/httpx），直接传入 `#fashion` 即可，库会自动处理编码
 ### 分页使用方法:
 1. 首次请求：只传 `query` 参数
 2. 获取响应中的 `next_max_id` 和 `rank_token`
 3. 下次请求：传入 `query`、`next_max_id` 和 `rank_token`
 4. 重复步骤 2-3 直到 `has_more` 为 false

## search_by_coordinates

`GET /api/v1/instagram/v2/search_by_coordinates`

<!-- Full path: /api/v1/instagram/v2/search_by_coordinates -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| latitude | number | ✅ | 纬度/Latitude | 40.7 |
| longitude | number | ✅ | 经度/Longitude | -74 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据GPS坐标搜索附近的Instagram地点
 ### 参数:
 - latitude: 纬度
 - longitude: 经度
 ### 返回:
 - `data.items`: 附近地点列表，包含名称、地址、分类等

## search_hashtags

`GET /api/v1/instagram/v2/search_hashtags`

<!-- Full path: /api/v1/instagram/v2/search_hashtags -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | cat |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据关键词搜索Instagram话题标签
### 参数:
- keyword: 搜索关键词
### 返回:
- `data.items`: 话题标签列表，包含名称、帖子数量等

## search_hashtags

`GET /api/v1/instagram/v2/search_hashtags`

<!-- Full path: /api/v1/instagram/v3/search_hashtags -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword | fashion |
| rank_token | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- Instagram话题标签搜索接口
- 仅返回话题标签搜索结果
### 参数:
- query: 搜索关键词
- rank_token: 上一次搜索返回的rank_token，用于翻页
### 返回:
- `data.hashtags`: 话题标签搜索结果列表
- `data.rank_token`: 排序token
- `data.see_more`: 更多信息
- `data.inform_module`: 提示模块

## search_locations

`GET /api/v1/instagram/v2/search_locations`

<!-- Full path: /api/v1/instagram/v2/search_locations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | paris |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据关键词搜索Instagram地点
### 参数:
- keyword: 搜索关键词（地点名称、城市等）
### 返回:
- `data.items`: 地点列表，包含名称、地址、坐标等

## search_music

`GET /api/v1/instagram/v2/search_music`

<!-- Full path: /api/v1/instagram/v2/search_music -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | happy |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据关键词搜索Instagram上可用的音乐
 ### 参数:
 - keyword: 搜索关键词
 ### 返回:
 - `data.items`: 音乐列表，包含标题、艺术家、时长、音频ID等

---

See SKILL.md for cross-group orchestration patterns.