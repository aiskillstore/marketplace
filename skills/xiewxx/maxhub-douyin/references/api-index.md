# Index & Analytics API / 指数与分析接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_all_valid_date

`GET /api/v1/douyin/index/fetch_all_valid_date`

<!-- Full path: /api/v1/douyin/index/fetch_all_valid_date -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音指数各类型数据的最新有效日期
 ### 返回:
 - 包含关键词、品牌、话题等维度的日/周/月最新可用日期

## fetch_brand_cycles

`POST /api/v1/douyin/index/fetch_brand_cycles`

<!-- Full path: /api/v1/douyin/index/fetch_brand_cycles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| brand_name | string | ✅ | 品牌名称/Brand name |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取品牌的周期数据（周期性热度分析）
### 参数:
- brand_name: 品牌名称
- start_date/end_date: 日期范围
- app_name: 平台选择
### 返回:
- 品牌周期性热度数据

## fetch_brand_radar_chart

`POST /api/v1/douyin/index/fetch_brand_radar_chart`

<!-- Full path: /api/v1/douyin/index/fetch_brand_radar_chart -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| brand_name | string | ✅ | 品牌名称/Brand name |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取品牌的雷达图数据（多维度评分）
### 参数:
- brand_name: 品牌名称
- start_date/end_date: 日期范围，格式 YYYYMMDD
- app_name: 平台选择
### 返回:
- 品牌多维度评分雷达图数据

## fetch_brand_valid_info

`POST /api/v1/douyin/index/fetch_brand_valid_info`

<!-- Full path: /api/v1/douyin/index/fetch_brand_valid_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword_list | string | ✅ | 品牌名称列表逗号分隔/Brand list comma separated |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取品牌的有效信息和品牌指数数据
### 参数:
- keyword_list: 品牌名称列表，逗号分隔
### 返回:
- 品牌指数、可用日期范围等

## fetch_portrait

`POST /api/v1/douyin/index/fetch_portrait`

<!-- Full path: /api/v1/douyin/index/fetch_portrait -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |
| app_name | string (aweme/toutiao) |  | '平台/Platform: aweme(抖音), toutiao(头条)' (default: aweme) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取关键词的人群画像分析数据
### 参数:
- keyword: 要分析的关键词
- start_date: 开始日期，格式 YYYYMMDD
- end_date: 结束日期，格式 YYYYMMDD
- app_name: 平台选择，aweme=抖音，toutiao=头条
### 返回:
- 性别分布、年龄分布、地域分布、兴趣分布等人群画像数据

## fetch_valid_date_for_relation

`GET /api/v1/douyin/index/fetch_valid_date_for_relation`

<!-- Full path: /api/v1/douyin/index/fetch_valid_date_for_relation -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音指数关联分析功能的有效日期范围
### 返回:
- 关联分析的起止可用日期

## get_author_market_fields

`GET /api/v1/douyin/xingtu_v2/get_author_market_fields`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_market_fields -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| market_scene | integer |  | 市场场景，1=默认场景/Market scene, 1=default (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取达人广场所有筛选字段选项
### 参数:
- market_scene: 市场场景，1=默认场景
### 返回:
- 达人广场筛选字段数据

## kol_xingtu_index_v1

`GET /api/v1/douyin/xingtu/kol_xingtu_index_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_xingtu_index_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol星图指数V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol星图指数

---

See SKILL.md for cross-group orchestration patterns.