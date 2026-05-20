# Ads & Analytics API / 广告与分析接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_account_health_status

`POST /api/v1/tiktok/creator/get_account_health_status`

<!-- Full path: /api/v1/tiktok/creator/get_account_health_status -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号的健康状况信息，包括过去 90 天内的健康评分（风险等级）以及当前累计的违规积分数量。
 - 关于违规积分：
    - 违规积分是 TikTok 用于衡量账号健康状况的重要指标。
    - 违规积分越高，账号健康状况越差，可能面临限流、禁播、封禁等处罚。
    - 违规积分将直接影响账号的曝光量和推荐量。
 ### 累计违规积分对应的惩罚等级：
 | 分数范围  | 惩罚措施                                                | 惩罚时长 |
 | --------- | ---------------------------------------------------------
| -------- |
 | 9-11      | 警告（Warning）                                           |
无       |
 | 12-14     | 暂停电商权限（视频、直播、商品展示功能）                  | 24 小时  |
 | 15-17     | 暂停电商权限                                              | 48
小时  |
 | 18-20     | 暂停电商权限                                              | 72
小时  |
 | 21-23     | 暂停电商权限                                              | 1
周     |
 | 24 及以上 | 永久移除电商权限，封禁 TikTok Shop 创作者账号             | 永久禁用 |
  ### 备注:
 - 此接口仅适用于已开通 TikTok Shop 的创作者账号。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - `risk_info`（健康状态信息）:
  - `risk_level_text`: 当前风险等级描述（如 Healthy）
  - `light_color`: 健康状态浅色展示色值（rgba 格式）
  - `dark_color`: 健康状态深色展示色值（rgba 格式）
- `vio_score_rule_learn_url`: 查看违规积分规则说明的链接
 - `is_show_score`: 是否展示违规积分（布尔值）
 - `violation_score`: 当前违规积分数量
 - `creator_status`: 创作者账号状态码（0=正常）

## get_account_insights_overview

`POST /api/v1/tiktok/creator/get_account_insights_overview`

<!-- Full path: /api/v1/tiktok/creator/get_account_insights_overview -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号在指定时间范围内的表现概览，包括收益、曝光、点击、成交等多维度数据。
 - 默认统计从 `start_date` 当月起 1 个自然月（如传入 2025-04-01，则统计整个 4 月的数据）。
  ### 备注:
 - 此接口仅适用于已开通 TikTok Shop 功能的创作者账号。
 - 数据按照时间粒度进行分段统计，可用于数据分析和趋势观察。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询开始时间，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - `segments`（分段数据列表）:
  - `time_selector`: 当前统计段的时间设置，包括周期、起止时间戳、时区、语言等
  - `timed_stats`: 每天/每段的详细数据，包含以下字段：
    - `live_revenue.amount`: 直播带货收益
    - `video_revenue.amount`: 视频带货收益
    - `revenue.amount`: 总收益（直播 + 视频）
    - `base_revenue.amount`: 基础收益
    - `commission_estimated.amount`: 预估佣金
    - `alc_base_revenue.amount`: ALC 模式下基础收益
    - `overall_item_sold_cnt`: 商品成交数
    - `product_show_cnt`: 商品展示次数
    - `product_click_cnt`: 商品点击次数
    - `alc_pay_sku_order_cnt`: ALC 成交订单数
- `meta.is_bound_shop`: 是否绑定 TikTok 店铺

## get_ad_interactive_analysis

`GET /api/v1/tiktok/ads/get_ad_interactive_analysis`

<!-- Full path: /api/v1/tiktok/ads/get_ad_interactive_analysis -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| material_id | string | ✅ | 广告素材ID/Ad material ID | 7213258221116751874 |
| metric_type | string |  | 分析类型/Analysis type (ctr, cvr, clicks, conversion, remain) (default: remain) |  |
| period_type | integer |  | 时间范围(天)/Period type (days) (default: 180) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取广告的互动时间分析，了解观众在视频不同时间点的留存和互动情况
 - 分析广告视频的吸引力曲线，找出最佳时长和关键互动点
 - 优化广告内容结构，提高整体效果
  ### 参数:
 - material_id: 广告素材ID，必填参数
 - metric_type: 分析类型
    - ctr: 点击率分析
    - cvr: 转化率分析
    - clicks: 点击次数分析
    - conversion: 转化次数分析
    - remain: 留存率分析 (默认)
- period_type: 时间范围，默认180天
  ### 返回内容说明:
 - `interactive_data`: 互动分析数据
  - `time_series`: 时间序列数据
    - `time`: 视频播放时间点（秒）
    - `value`: 对应的指标值（如留存率）
  - `average_watch_time`: 平均观看时长
  - `completion_rate`: 完播率
  - `peak_interaction_time`: 互动高峰时间点
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_ad_interactive_analysis",
  "params": {
    "material_id": "7213258221116751874",
    "metric_type": "remain",
    "period_type": 180
  },
  "data": {
    "interactive_data": {
      "time_series": [
        {"time": 0, "value": 100},
        {"time": 1, "value": 95},
        {"time": 2, "value": 88}
      ],
      "average_watch_time": 8.5,
      "completion_rate": 65.2,
      "peak_interaction_time": 3
    }
  }
}
 ```

## get_ad_keyframe_analysis

`GET /api/v1/tiktok/ads/get_ad_keyframe_analysis`

<!-- Full path: /api/v1/tiktok/ads/get_ad_keyframe_analysis -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| material_id | string | ✅ | 广告素材ID/Ad material ID | 7213258221116751874 |
| metric | string |  | >- (default: retain_ctr) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取广告视频的关键帧分析，了解视频在不同时间点的观众留存情况
 - 分析哪些时间点最吸引观众，哪些时间点观众流失最多
 - 帮助优化广告视频结构，提高观看完成率
  ### 参数:
 - material_id: 广告素材ID，必填参数
 - metric: 分析指标，可选值：
  - retain_ctr: 留存点击率（默认）
  - retain_cvr: 留存转化率
  - click_cnt: 点击次数
  - convert_cnt: 转化次数
  - play_retain_cnt: 播放留存量
 ### 返回内容说明:
 - `keyframe_data`: 关键帧数据
  - `time_points`: 时间点列表（秒）
  - `retention_rates`: 对应时间点的留存率（百分比）
  - `drop_points`: 流失率较高的时间点
  - `highlight_points`: 观众兴趣较高的时间点
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_ad_keyframe_analysis",
  "params": {
    "material_id": "7213258221116751874"
  },
  "data": {
    "keyframe_data": {
      "time_points": [0, 1, 2, 3, 4, 5],
      "retention_rates": [100, 95, 88, 82, 78, 75],
      "drop_points": [2, 4],
      "highlight_points": [1, 5]
    }
  }
}
 ```

## get_ad_percentile

`GET /api/v1/tiktok/ads/get_ad_percentile`

<!-- Full path: /api/v1/tiktok/ads/get_ad_percentile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| material_id | string | ✅ | 广告素材ID/Ad material ID | 7213258221116751874 |
| metric | string |  | >- (default: ctr_percentile) |  |
| period_type | integer |  | 时间范围(天)/Time period (days) (default: 180) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取广告在同行业中的百分位排名数据
 - 了解广告在各项指标上相对于同行的表现水平
 - 帮助评估广告效果并制定优化策略
  ### 参数:
 - material_id: 广告素材ID，必填参数
 - metric: 分析指标，可选值：
  - ctr_percentile: 点击率百分位（默认）
  - time_attr_conversion_rate_percentile: 时间归因转化率百分位
  - click_cnt_percentile: 点击次数百分位
  - time_attr_convert_cnt_percentile: 时间归因转化次数百分位
  - show_cnt_percentile: 展示次数百分位
- period_type: 时间范围(天)，默认180天
  ### 返回内容说明:
 - `percentile_data`: 百分位数据
  - `ctr_percentile`: 点击率百分位（0-100）
  - `cvr_percentile`: 转化率百分位
  - `engagement_percentile`: 互动率百分位
  - `view_percentile`: 观看量百分位
  - `industry_average`: 行业平均值对比
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_ad_percentile",
  "params": {
    "material_id": "7213258221116751874"
  },
  "data": {
    "percentile_data": {
      "ctr_percentile": 85,
      "cvr_percentile": 72,
      "engagement_percentile": 90,
      "view_percentile": 88,
      "industry_average": {
        "ctr": 2.5,
        "cvr": 1.2,
        "engagement": 5.8
      }
    }
  }
}
 ```

## get_creative_patterns

`GET /api/v1/tiktok/ads/get_creative_patterns`

<!-- Full path: /api/v1/tiktok/ads/get_creative_patterns -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| first_industry_id | string |  | 一级行业ID/First industry ID (default: '25000000000') |  |
| period_type | string |  | 时间周期类型/Period type (week, month) (default: week) |  |
| order_field | string |  | 排序字段/Order field (ctr, play_over_rate) (default: ctr) |  |
| order_type | string |  | 排序方式/Sort order (desc, asc) (default: desc) |  |
| week | string |  | 特定周（可选）/Specific week (optional) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定行业的创意模式排行榜，了解哪些创意模式效果最好
 - 分析不同创意模式的点击率、完播率等关键指标
 - 为广告创意制作提供数据支持的最佳实践
  ### 参数:
 - first_industry_id: 行业ID，如游戏行业：25000000000
 - period_type: 时间类型，"week"=周数据，"month"=月数据
 - order_field: 排序字段，"ctr"=点击率，"play_over_rate"=播放完成率
 - order_type: 排序方式，desc（降序）或asc（升序）
 - week: 查看特定周的数据，格式：YYYY-MM-DD（可选）
  ### 返回内容说明:
 - `list`: 创意模式列表
  - `label_info`: 模式标签信息
    - `value`: 模式名称
    - `description`: 模式描述
  - `ctr`: 点击率（百分比）
  - `play_over_rate`: 播放完成率（百分比）
  - `avg_watch_time`: 平均观看时长
  - `example_count`: 示例数量
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_creative_patterns",
  "params": {
    "first_industry_id": "25000000000",
    "period_type": "week",
    "order_field": "ctr"
  },
  "data": {
    "list": [
      {
        "label_info": {
          "value": "Problem-Solution",
          "description": "Present a problem and show the solution"
        },
        "ctr": 4.5,
        "play_over_rate": 68.2,
        "avg_watch_time": 12.3,
        "example_count": 234
      }
    ]
  }
}
 ```

## get_creator_filters

`GET /api/v1/tiktok/ads/get_creator_filters`

<!-- Full path: /api/v1/tiktok/ads/get_creator_filters -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者搜索和筛选的可用选项
 - 了解支持的国家、排序方式等筛选维度
 - 为创作者分析提供参数参考
  ### 返回内容说明:
 - `audience_country`: 受众国家列表
  - `id`: 国家代码
  - `value`: 国家名称
- `creator_country`: 创作者所在国家列表
 - `sort_by`: 支持的排序方式
  - follower: 按粉丝数排序
  - engagement: 按互动率排序
  - avg_views: 按平均观看量排序
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_creator_filters",
  "params": {},
  "data": {
    "audience_country": [
      {"id": "US", "value": "United States"},
      {"id": "UK", "value": "United Kingdom"}
    ],
    "creator_country": [
      {"id": "US", "value": "United States"},
      {"id": "UK", "value": "United Kingdom"}
    ],
    "sort_by": ["follower", "engagement", "avg_views"]
  }
}
 ```

## get_product_filters

`GET /api/v1/tiktok/ads/get_product_filters`

<!-- Full path: /api/v1/tiktok/ads/get_product_filters -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取产品分析功能的可用筛选选项
 - 了解支持的电商类目、时间类型等筛选维度
 - 为产品数据分析提供筛选参数参考
  ### 返回内容说明:
 - `country`: 国家列表
  - `id`: 国家ID
  - `value`: 国家名称
  - `label`: 国家标签
- `ecom_category`: 电商类目列表
  - `id`: 类目ID
  - `value`: 类目名称
  - `label`: 类目标签
- `latest_month`: 最新月份
 - `latest_week`: 最新周
  ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_product_filters",
  "params": {},
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
      ],
      "ecom_category": [
        {
          "id": 605196,
          "value": "Automotive & Motorbike",
          "label": "category_605196"
        },
        {
          "id": 602284,
          "value": "Baby & Maternity",
          "label": "category_602284"
        }
      ],
      "latest_month": "2025-05",
      "latest_week": "2025-06-07"
    }
  }
}
 ```

## get_product_metrics

`GET /api/v1/tiktok/ads/get_product_metrics`

<!-- Full path: /api/v1/tiktok/ads/get_product_metrics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string | ✅ | 产品类目ID/Product category ID | 601583 |
| last | integer |  | 最近天数/Last days (default: 30) |  |
| metrics | string |  | 指标类型，逗号分隔/Metrics types, comma separated (default: post,ctr) |  |
| ecom_type | string |  | 电商类型/E-commerce type (default: l3) |  |
| period_type | string |  | 时间类型/Period type (default: last) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定产品类目的详细指标数据和时间趋势
 - 分析产品的发布量、点击率、转化率等核心指标变化
 - 帮助了解产品类目的市场表现和发展趋势
  ### 参数:
 - id: 产品类目ID，如香水：601583
 - last: 最近天数，如7、30天
 - metrics: 指标类型，多个用逗号分隔，如"post,ctr,cvr"
 - ecom_type: 电商类型，默认"l3"
 - period_type: 时间类型，默认"last"
  ### 返回内容说明:
 - `info`: 产品指标信息
  - `comment`: 评论数
  - `cost`: 花费金额
  - `cover_url`: 封面图URL（可能为null）
  - `cpa`: 每次转化成本
  - `ctr`: 点击率
  - `ctr_metrics`: 点击率时间序列数据
    - `time`: 时间戳
    - `value`: 对应时间的点击率
  - `cvr`: 转化率
  - `ecom_type`: 电商类型
  - `first_ecom_category`: 一级电商类目
  - `impression`: 展示量
  - `like`: 点赞数
  - `play_six_rate`: 6秒播放率
  - `post`: 发布量
  - `post_change`: 发布量变化率
  - `post_metrics`: 发布量时间序列数据
    - `time`: 时间戳
    - `value`: 对应时间的发布量
  - `second_ecom_category`: 二级电商类目
  - `share`: 分享数
  - `third_ecom_category`: 三级电商类目
  - `url_title`: URL标题
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_product_metrics",
  "params": {
    "id": "601583",
    "last": "30",
    "metrics": "post,ctr",
    "ecom_type": "l3",
    "period_type": "last"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "info": {
        "comment": 13559,
        "cost": 2330000,
        "cover_url": null,
        "cpa": 12.4,
        "ctr": 1.04,
        "ctr_metrics": [
          {
            "time": 1747267200,
            "value": 0.88
          },
          {
            "time": 1747353600,
            "value": 0.99
          }
        ],
        "cvr": 15.2,
        "ecom_type": "l3",
        "post": 52300,
        "post_change": -8.12,
        "post_metrics": [
          {
            "time": 1747267200,
            "value": 1800
          }
        ]
      }
    }
  }
}
 ```

## get_top_ads_spotlight

`GET /api/v1/tiktok/ads/get_top_ads_spotlight`

<!-- Full path: /api/v1/tiktok/ads/get_top_ads_spotlight -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| industry | string |  | 行业ID/Industry ID (default: '25000000000') |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定行业的热门广告聚光灯，展示行业内最受关注的广告案例
 - 分析行业内的广告创意趋势和优秀案例
 - 为广告创意制作提供灵感和参考
  ### 参数:
 - industry: 行业ID，必填参数，如教育行业：25000000000
 - page: 页码，默认1
 - limit: 每页数量，默认20
  ### 返回内容说明:
 - `materials`: 广告素材列表
  - `cost`: 花费等级
  - `ctr`: 点击率
  - `highlight`: 亮点描述
  - `id`: 广告ID
  - `like`: 点赞数
  - `video_info`: 视频信息
    - `vid`: 视频ID
    - `duration`: 时长（秒）
    - `cover`: 封面图片URL
    - `video_url`: 多种画质的视频播放URL
      - `360p`: 360p画质视频URL
      - `480p`: 480p画质视频URL
      - `540p`: 540p画质视频URL
      - `720p`: 720p画质视频URL
    - `width`: 视频宽度
    - `height`: 视频高度
- `pagination`: 分页信息
  - `page`: 当前页
  - `size`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_top_ads_spotlight",
  "params": {
    "industry": "25000000000",
    "page": "1",
    "limit": "20"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "materials": [
        {
          "cost": 2,
          "ctr": 0.14,
          "highlight": "Through the lens of a real person talking his way through the game, the video appears credible with commentary that sounds trustworthy.",
          "id": "7165768841499066370",
          "like": 377333,
          "video_info": {
            "vid": "v0911dg40001cdo7ukjc77ua0r66rqqg",
            "duration": 19.156,
            "cover": "https://p16-sign-va.tiktokcdn.com/tos-maliva-v-2c3654-us/1c87385bed544878bb94b61816a653a1~tplv-noop.image",
            "video_url": {
              "360p": "https://v16m-default.tiktokcdn.com/9e086e91176219d756e9c875fb739dc4/684d7e29/video/tos/useast2a/tos-useast2a-ve-0051c799-euttp/oIQcoRBNNpXbALnjIeLgbKfwWPDDDDIgQ9l6BF",
              "480p": "https://v16m-default.tiktokcdn.com/2f304931bd351dad0e43e9771364bd78/684d7e29/video/tos/useast2a/tos-useast2a-ve-0051c799-euttp/o8lIsnPILWelBwDbDgDuwQj9UlNebAYdDUXBKS",
              "540p": "https://v16m-default.tiktokcdn.com/351ae3acb3121d42db8a5091811b2340/684d7e29/video/tos/useast2a/tos-useast2a-ve-0051c799-euttp/oQwpeXyWjDBg7KXcBDeDgPnDDbANoISoQIb9Ql",
              "720p": "https://v16m-default.tiktokcdn.com/a04bacceb906e5336a68158479f5eac5/684d7e29/video/tos/useast2a/tos-useast2a-ve-0051c799-euttp/oQQnWCmCDfpgIxegjrKAXZlbIPDNBDDbZQBHw9"
            },
            "width": 720,
            "height": 1280
          }
        }
      ],
      "pagination": {
        "page": 1,
        "size": 20,
        "total": 100,
        "has_more": true
      }
    }
  }
}
 ```

---

See SKILL.md for cross-group orchestration patterns.