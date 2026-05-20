# Search & Trending API / 搜索与热门接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_search_timeline

`GET /api/v1/twitter/web/fetch_search_timeline`

<!-- Full path: /api/v1/twitter/web/fetch_search_timeline -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键字/Search Keyword | Elon Musk |
| search_type | string |  | 搜索类型/Search Type (default: Top) | Top |
| cursor | string |  | 游标/Cursor |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索
 ### 参数:
 - keyword: 搜索关键字
 - search_type: 搜索类型，默认为Top，其他可选值为Latest，Media，People, Lists
 - cursor: 游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取
 ### 返回:
 - 搜索结果

## fetch_trending

`GET /api/v1/twitter/web/fetch_trending`

<!-- Full path: /api/v1/twitter/web/fetch_trending -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| country | string |  | 国家/Country (default: UnitedStates) | UnitedStates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取趋势
 ### 参数:
 - country: 国家，默认为UnitedStates，其他可选值见下方
    - China
    - India
    - Japan
    - Russia
    - Germany
    - Indonesia
    - Brazil
    - France
    - UnitedKingdom
    - Turkey
    - Italy
    - Mexico
    - SouthKorea
    - Canada
    - Spain
    - SaudiArabia
    - Egypt
    - Australia
    - Poland
    - Iran
    - Pakistan
    - Vietnam
    - Nigeria
    - Bangladesh
    - Netherlands
    - Argentina
    - Philippines
    - Malaysia
    - Colombia
    - UniteArabEmirates
    - Romania
    - Belgium
    - Switzerland
    - Singapore
    - Sweden
    - Norway
    - Austria
    - Kazakhstan
    - Algeria
    - Chile
    - Czechia
    - Peru
    - Iraq
    - Israel
    - Ukraine
    - Denmark
    - Portugal
    - Hungary
    - Greece
    - Finland
    - NewZealand
    - Belarus
    - Slovakia
    - Serbia
    - Lithuania
    - Luxembourg
    - Estonia
 ### 返回:
 - 趋势

---

See SKILL.md for cross-group orchestration patterns.