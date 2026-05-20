# Search API / 搜索接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_search_photo

`GET /api/v1/tiktok/web/fetch_search_photo`

<!-- Full path: /api/v1/tiktok/web/fetch_search_photo -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | TikTok |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| offset | integer |  | 翻页游标/Page offset (default: 0) |  |
| search_id | string |  | 搜索id，翻页时需要提供/Search id, need to provide when paging (default: '') |  |
| cookie | string |  | 用户cookie(按需提供)/User cookie(if needed) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索照片
 ### 参数:
 - keyword: 搜索关键词
 - count: 每页数量，建议保持默认值20。
 - offset: 翻页游标，第一次请求时为0，第二次请求时从上一次请求的返回响应中获取，一般这个值的关键字为offset或者cursor。
 - search_id: 搜索id，第一次请求时为空，第二次翻页时需要提供，需要从上一次请求的返回响应中获取。
    - 例如: search_id = "20240828035554C02011379EBB6A00E00B"
    - JSON Path-1 : $.data.extra.logid
    - JSON Path-2 : $.data.log_pb.impr_id
- cookie: 用户cookie(如果你需要使用自己的账号搜索，或者遇到接口报错，可以自行提供cookie，默认不需要提供)
 ### 返回:
 - 视频列表

## fetch_search_word_suggestion

`GET /api/v1/tiktok/shop/web/fetch_search_word_suggestion`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_search_word_suggestion -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| search_word | string | ✅ | 搜索关键词/Search keyword | labubu |
| lang | string |  | 语言/Language (default: en-US) | en-US |
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取搜索关键词的自动补全建议
- 用于搜索框的智能提示功能
### 参数:
- search_word: 搜索关键词 (必填)
- lang: 语言代码 (en-US/zh-CN等)
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 重要提示:
- 由于接口风控原因，请务必将请求timeout设置为30秒
- 如遇到400错误代码，请重试请求3次
### 返回数据结构:
```json
{
    "code": 0,
    "message": "",
    "data": [                        // 建议列表(最多50个)
        "phone case",
        "phone mount",
        "phone holder for car",
        "..."
    ]
}
```

## fetch_trending_searchwords

`GET /api/v1/tiktok/web/fetch_trending_searchwords`

<!-- Full path: /api/v1/tiktok/web/fetch_trending_searchwords -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取每日趋势搜索关键词
### 返回:
- 趋势搜索关键词

## get_hashtag_filters

`GET /api/v1/tiktok/ads/get_hashtag_filters`

<!-- Full path: /api/v1/tiktok/ads/get_hashtag_filters -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取热门标签功能的可用筛选选项
 - 了解支持的国家/地区、行业等筛选维度
 - 为标签分析提供筛选参数参考
  ### 返回内容说明:
 - `country`: 支持的国家/地区列表
  - `id`: 国家代码
  - `value`: 国家名称
- `industry`: 支持的行业列表
  - `id`: 行业ID
  - `value`: 行业名称
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_hashtag_filters",
  "params": {},
  "data": {
    "country": [
      {"id": "US", "value": "United States"},
      {"id": "UK", "value": "United Kingdom"},
      {"id": "JP", "value": "Japan"}
    ],
    "industry": [
      {"id": "27000000000", "value": "Games"},
      {"id": "19000000000", "value": "E-commerce"},
      {"id": "10000000000", "value": "Education"}
    ]
  }
}
 ```

## get_keyword_filters

`GET /api/v1/tiktok/ads/get_keyword_filters`

<!-- Full path: /api/v1/tiktok/ads/get_keyword_filters -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取关键词洞察功能的可用筛选选项
 - 了解支持的国家/地区、行业、关键词类型等筛选维度
 - 为关键词分析提供筛选参数参考
  ### 返回内容说明:
 - `country_list`: 支持的国家/地区列表
  - `id`: 国家代码
  - `value`: 国家名称
- `industry_list`: 支持的行业列表
  - `id`: 行业ID
  - `value`: 行业名称
- `keyword_type`: 支持的关键词类型
 - `objective_list`: 支持的广告目标列表
  ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_keyword_filters",
  "params": {},
  "data": {
    "country_list": [
      {"id": "US", "value": "United States"},
      {"id": "UK", "value": "United Kingdom"}
    ],
    "industry_list": [
      {"id": "27000000000", "value": "Games"},
      {"id": "19000000000", "value": "E-commerce"}
    ],
    "keyword_type": ["general", "brand", "product"],
    "objective_list": [
      {"id": "1", "value": "Traffic"},
      {"id": "2", "value": "Conversions"}
    ]
  }
}
 ```

## get_keyword_insights

`GET /api/v1/tiktok/ads/get_keyword_insights`

<!-- Full path: /api/v1/tiktok/ads/get_keyword_insights -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| period | integer |  | 时间段（天）/Time period (days, 7/30/120/180) (default: 7) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| order_by | string |  | 排序字段/Sort field (post, ctr, click_rate, etc.) (default: post) |  |
| order_type | string |  | 排序方式/Sort order (desc, asc) (default: desc) |  |
| industry | string |  | 行业ID/Industry ID |  |
| objective | string |  | 广告目标/Ad objective |  |
| keyword_type | string |  | 关键词类型/Keyword type |  |
| keyword | string |  | 关键词/Keyword |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok广告关键词洞察数据，了解热门关键词的表现指标
 - 分析不同关键词的点击率、发布量、增长趋势等核心数据
 - 帮助广告主优化关键词策略，提升广告投放效果
  ### 参数:
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - period: 时间范围（天），如7、30、120天
 - country_code: 国家代码，如US、UK、JP等
 - order_by: 排序字段，可选：post（发布量）、ctr（点击率）、click_rate（点击率）、trend（趋势）
 - order_type: 排序方式，desc（降序）或asc（升序）
 - industry: 行业ID，多个用逗号分隔
 - objective: 广告目标
 - keyword_type: 关键词类型
  ### 返回内容说明:
 - `keyword_list`: 关键词列表
  - `comment`: 评论数
  - `cost`: 花费金额
  - `cpa`: 每次转化成本
  - `ctr`: 点击率（百分比）
  - `cvr`: 转化率（百分比）
  - `impression`: 展示量
  - `keyword`: 关键词文本
  - `like`: 点赞数
  - `play_six_rate`: 6秒播放率（百分比）
  - `post`: 发布量
  - `post_change`: 发布量变化率（百分比）
  - `share`: 分享数
  - `video_list`: 视频ID列表
- `pagination`: 分页信息
  - `page`: 当前页
  - `size`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_keyword_insights",
  "params": {
    "page": "1",
    "limit": "20",
    "period": "7",
    "country_code": "US",
    "order_by": "post",
    "order_type": "desc"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "keyword_list": [
        {
          "comment": 4785,
          "cost": 756000,
          "cpa": 20.2,
          "ctr": 0.53,
          "cvr": 9.75,
          "impression": 164000000,
          "keyword": "summer",
          "like": 475734,
          "play_six_rate": 6.43,
          "post": 14200,
          "post_change": 111.21,
          "share": 5754,
          "video_list": [
            "7504060523021896977",
            "7512164952346529031",
            "7511370341621435679",
            "7511483560939785514",
            "7506971390613015854"
          ]
        },
        {
          "comment": 2151,
          "cost": 264000,
          "cpa": 17.8,
          "ctr": 1.38,
          "cvr": 6.15,
          "impression": 38100000,
          "keyword": "free shipping",
          "like": 84131,
          "play_six_rate": 8.64,
          "post": 7810,
          "post_change": 91.91,
          "share": 3707,
          "video_list": [
            "7471433861654727943",
            "7515178617568070930",
            "7502578466194312456",
            "7513186274711244054",
            "7514776490123201810"
          ]
        }
      ],
      "pagination": {
        "page": 1,
        "size": 20,
        "total": 484,
        "has_more": true
      }
    }
  }
}
 ```

## get_related_keywords

`GET /api/v1/tiktok/ads/get_related_keywords`

<!-- Full path: /api/v1/tiktok/ads/get_related_keywords -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 目标关键词/Target keyword (default: free shipping) |  |
| period | integer |  | 时间段（天）/Time period (days, 7/30/120) (default: 7) |  |
| country_code | string |  | 国家/地区代码/Country code (default: US) |  |
| rank_type | string |  | '排名类型/Rank type (popular: 热门, breakout: 突破性)' (default: popular) |  |
| content_type | string |  | 内容类型/Content type (keyword, hashtag) (default: keyword) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 50) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取与指定关键词相关的其他关键词或标签
- 发现关键词的相关搜索词，扩展广告投放词库
- 分析突破性关键词，抓住新兴趋势
 ### 参数:
- keyword: 主关键词，必填参数
- period: 时间范围（天），如7、30天
- country_code: 国家代码，如US、UK、JP等
- rank_type: 排序类型，"popular"=热门，"breakout"=突破性
- content_type: 内容类型，"keyword"=关键词，"hashtag"=标签
 ### 返回内容说明:
- `list`: 相关关键词列表
  - `keyword`: 相关关键词文本
  - `relevance_score`: 相关性评分
  - `search_volume`: 搜索量级别
  - `growth_rate`: 增长率（突破性关键词）
  - `post_count`: 使用该词的广告数量
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_related_keywords",
  "params": {
    "keyword": "free shipping",
    "period": 7,
    "rank_type": "popular"
  },
  "data": {
    "list": [
      {
        "keyword": "fast delivery",
        "relevance_score": 95,
        "search_volume": "high",
        "post_count": 8934
      },
      {
        "keyword": "discount code",
        "relevance_score": 88,
        "search_volume": "medium",
        "post_count": 5621
      }
    ]
  }
}
```

## get_sound_filters

`GET /api/v1/tiktok/ads/get_sound_filters`

<!-- Full path: /api/v1/tiktok/ads/get_sound_filters -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| rank_type | string |  | 排行类型/Rank type (popular, surging) (default: popular) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取热门音乐功能的可用筛选选项
- 了解不同排行类型下的筛选维度
- 为音乐选择提供参数参考
 ### 参数:
- rank_type: 排行类型，"popular"=热门，"surging"=上升最快
 ### 返回内容说明:
- `country`: 国家列表
  - `id`: 国家ID
  - `value`: 国家名称
  - `label`: 国家标签
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_sound_filters",
  "params": {
    "rank_type": "popular"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "country": [
        {
          "id": "AR",
          "value": "Argentina",
          "label": "AR"
        },
        {
          "id": "AU",
          "value": "Australia",
          "label": "AU"
        }
      ]
    }
  }
}
```

## search_ads

`GET /api/v1/tiktok/ads/search_ads`

<!-- Full path: /api/v1/tiktok/ads/search_ads -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| objective | integer |  | 广告目标类型/Ad objective (1:流量 2:应用安装 3:转化 4:视频浏览 5:触达 6:潜在客户 7:产品销售) (default: 1) |  |
| like | integer |  | 表现排名/Performance rank (1:前1-20% 2:前21-40% 3:前41-60% 4:前61-80%) (default: 1) |  |
| period | integer |  | 时间段/Time period (days) (default: 180) |  |
| industry | string |  | 行业ID/Industry ID |  |
| keyword | string |  | 搜索关键词/Search keyword |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| order_by | string |  | 排序方式/Sort by (for_you, likes) (default: for_you) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| ad_format | integer |  | 广告格式/Ad format (1:视频) (default: 1) |  |
| ad_language | string |  | 广告语言/Ad language (default: en) |  |
| search_id | string |  | 搜索ID（可选）/Search ID (optional) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索TikTok广告创意库中的广告，支持多维度筛选和排序
 - 发现特定行业、关键词或目标相关的高效广告案例
 - 为广告策划和创意制作提供参考和灵感
  ### 参数:
 - keyword: 搜索关键词，可选参数，留空返回所有广告
 - objective: 广告目标，1=全部
 - like: 点赞数筛选，1=全部
 - period: 时间范围（天），如7、30、120、180天
 - industry: 行业ID列表，多个ID用逗号分隔。完整行业ID列表见:
https://github.com/maxhub/TikTok-Ads-Industry-Code
 - page: 页码，默认1
 - limit: 每页数量，默认20，最大50
 - order_by: 排序方式，"for_you"=为你推荐，"likes"=按点赞数排序
 - country_code: 国家代码，如US、UK、JP等
 - ad_format: 广告格式，1=视频广告
 - ad_language: 广告语言代码，如en、zh等
  ### 常用行业ID示例:
 - 游戏: 27000000000
 - 电子商务: 19000000000
 - 金融服务: 30000000000
 - 教育: 10000000000
 - 美妆个护: 22000000000
 - 食品饮料: 16000000000
  ### 返回内容说明:
 - `materials`: 广告素材列表
  - `id`: 广告素材ID
  - `aweme_id`: 广告视频ID
  - `desc`: 广告描述
  - `create_time`: 创建时间
  - `video_info`: 视频信息
    - `cover`: 封面图URL
    - `duration`: 时长（秒）
  - `statistics`: 统计数据
    - `digg_count`: 点赞数
    - `comment_count`: 评论数
    - `share_count`: 分享数
  - `ads_info`: 广告信息
    - `advertiser_name`: 广告主名称
    - `landing_page`: 落地页URL
- `pagination`: 分页信息
  - `page`: 当前页
  - `limit`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/search_ads",
  "params": {
    "keyword": "cat toy",
    "period": 180,
    "industry": "27000000000",
    "page": 1,
    "limit": 20
  },
  "data": {
    "materials": [
      {
        "id": "7213258221116751874",
        "aweme_id": "7213258221116751874",
        "desc": "Best interactive cat toys! Keep your cats entertained 🐱",
        "create_time": 1680234567,
        "video_info": {
          "cover": "https://p16-ad-sg.tiktokcdn.com/img/xxx.jpeg",
          "duration": 15
        },
        "statistics": {
          "digg_count": 128456,
          "comment_count": 3421,
          "share_count": 892
        },
        "ads_info": {
          "advertiser_name": "PetToys Inc.",
          "landing_page": "https://example.com/cat-toys"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1523,
      "has_more": true
    }
  }
}
 ```

## search_creators

`GET /api/v1/tiktok/ads/search_creators`

<!-- Full path: /api/v1/tiktok/ads/search_creators -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | jo |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| sort_by | string |  | 排序方式/Sort by (follower, avg_views) (default: follower) |  |
| creator_country | string |  | 创作者国家/Creator country (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过关键词搜索创作者
- 快速找到特定领域或名称的创作者
- 支持按粉丝数或平均观看量排序
 ### 参数:
- keyword: 搜索关键词，可以是用户名、昵称的一部分
- page: 页码，默认1
- limit: 每页数量，默认20
- sort_by: 排序方式
  - follower: 按粉丝数排序
  - avg_views: 按平均观看量排序
- creator_country: 创作者所在国家
 ### 返回内容说明:
- `creators`: 创作者列表
  - `tcm_id`: 创作者市场ID
  - `user_id`: 用户ID
  - `nick_name`: 昵称
  - `avatar_url`: 头像URL
  - `country_code`: 国家代码
  - `follower_cnt`: 粉丝数
  - `liked_cnt`: 总点赞数
  - `tt_link`: TikTok个人主页链接
  - `tcm_link`: 创作者市场链接
  - `items`: 作品列表
    - `item_id`: 作品ID
    - `cover_url`: 封面URL
    - `tt_link`: 作品链接
    - `vv`: 观看量
    - `liked_cnt`: 点赞数
    - `create_time`: 创建时间戳
- `pagination`: 分页信息
  - `page`: 当前页码
  - `size`: 每页数量
  - `total`: 总数
  - `has_more`: 是否有更多
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/search_creators",
  "params": {
    "keyword": "jo",
    "page": "1",
    "limit": "20",
    "sort_by": "follower",
    "creator_country": "US"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "creators": [
        {
          "tcm_id": "6894787532572065797",
          "user_id": "6684747467718820870",
          "nick_name": "Josh Zilberberg",
          "avatar_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/f11c960c637601225c29d6e7849069eb~tplv-tiktokx-cropcenter:100:100.png",
          "country_code": "US",
          "follower_cnt": 3048368,
          "liked_cnt": 130131619,
          "tt_link": "https://www.tiktok.com/@josh.zilberberg",
          "tcm_link": "https://creatormarketplace.tiktok.com/ad#/author/6894787532572065797",
          "items": [
            {
              "item_id": "7406005139112283397",
              "cover_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-p-0068/6e0c79311c2b49758674ae64721c495b_1724344961~tplv-noop.image",
              "tt_link": "https://www.tiktok.com/@author/video/7406005139112283397",
              "vv": 3266905,
              "liked_cnt": 4057,
              "create_time": 1724344950
            }
          ]
        }
      ],
      "pagination": {
        "page": 1,
        "size": 20,
        "total": 6,
        "has_more": false
      }
    }
  }
}
```

## search_sound

`GET /api/v1/tiktok/ads/search_sound`

<!-- Full path: /api/v1/tiktok/ads/search_sound -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | taylor swift |
| period | integer |  | 时间范围（天）/Time period (days) (default: 7) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| rank_type | string |  | 排行类型/Rank type (popular, surging) (default: popular) |  |
| new_on_board | boolean |  | 是否只看新上榜/Only new on board (default: false) |  |
| commercial_music | boolean |  | 是否商业音乐/Commercial music only (default: false) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索符合条件的音乐列表
 - 支持按关键词、热度、商业类型等多维度筛选
 - 为广告配乐选择提供全面的搜索功能
  ### 参数:
 - keyword: 搜索关键词
 - period: 时间范围（天），如7、30、120天
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - rank_type: 排行类型，"popular"=热门，"surging"=上升最快
 - new_on_board: 是否只看新上榜音乐
 - commercial_music: 是否只看商业音乐
 - country_code: 国家代码
  ### 返回内容说明:
 - `sound_list`: 音乐列表
  - `id`: 音乐ID
  - `title`: 音乐标题
  - `author`: 音乐作者
  - `duration`: 时长（秒）
  - `trend`: 趋势数据
  - `related_items`: 使用该音乐的视频数量
  - `is_commercial`: 是否商业音乐
- `pagination`: 分页信息
  ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/search_sound",
  "params": {
    "keyword": "taylor swift",
    "period": 7,
    "page": 1
  },
  "data": {
    "sound_list": [
      {
        "id": "7156826385225353217",
        "title": "Karma",
        "author": "Taylor Swift",
        "duration": 30,
        "trend": [
          {"time": 1746000000, "value": 15000}
        ],
        "related_items": 5678,
        "is_commercial": true
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 156,
      "has_more": true
    }
  }
}
 ```

## search_sound_hint

`GET /api/v1/tiktok/ads/search_sound_hint`

<!-- Full path: /api/v1/tiktok/ads/search_sound_hint -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | taylor swift |
| period | integer |  | 时间范围（天）/Time period (days) (default: 7) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 5) |  |
| rank_type | string |  | 排行类型/Rank type (popular, surging) (default: popular) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| filter_by_checked | boolean |  | 是否只看已验证/Only verified (default: false) |  |
| commercial_music | boolean |  | 是否商业音乐/Commercial music only (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取音乐搜索的自动完成提示和推荐
- 帮助用户快速找到相关音乐
- 提供搜索建议优化音乐选择
 ### 参数:
- keyword: 搜索关键词
- period: 时间范围（天）
- page: 页码，默认1
- limit: 每页数量，默认5
- rank_type: 排行类型，"popular"=热门，"surging"=上升最快
- country_code: 国家代码
- filter_by_checked: 是否只看已验证音乐
- commercial_music: 是否只看商业音乐
 ### 返回内容说明:
- `sound_list`: 音乐提示列表
  - `title`: 音乐标题
  - `author`: 音乐作者
  - `match_type`: 匹配类型（标题/作者/标签）
  - `popularity`: 热度评分
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/search_sound_hint",
  "params": {
    "keyword": "taylor swift",
    "limit": 5
  },
  "data": {
    "sound_list": [
      {
        "title": "Anti-Hero",
        "author": "Taylor Swift",
        "match_type": "artist",
        "popularity": 98
      },
      {
        "title": "Blank Space",
        "author": "Taylor Swift",
        "match_type": "artist",
        "popularity": 95
      }
    ]
  }
}
```

---

See SKILL.md for cross-group orchestration patterns.