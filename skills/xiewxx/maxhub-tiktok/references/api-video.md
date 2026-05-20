# Video & Content API / 视频与内容接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## TTencrypt_algorithm

`POST /api/v1/tiktok/app/v3/TTencrypt_algorithm`

<!-- Full path: /api/v1/tiktok/app/v3/TTencrypt_algorithm -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - TikTok APP加密算法，用于生成请求头中的加密参数。
 - 生成的加密参数列表：
    - `x-ladon`
    - `x-khronos`
    - `x-argus`
    - `x-gorgon` （8404）
 ### 参数:
 - url: 需要加密的完整URL
 - data: 如果接口是POST请求，请填写POST请求的数据参与加密计算，GET请求时传入空字符串即可。
 - device_info: 设备信息，可选参数，如果不填写则使用默认设备信息，设备信息会修改传入的URL中的参数。
  ### 返回:
 - 加密参数列表


### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_type | integer | ✅ | 作品类型/Video type | 0 |
| item_id | string | ✅ | 作品id/Video id | 7419966340443819295 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据视频ID来增加作品的播放数
 ### 参数:
 - aweme_type: 作品类型，0:视频 1:图文，可以从单一作品数据接口中获取。
 - item_id: 作品id，别名为aweme_id
 - invite_code: 邀请码，此接口需要邀请码才能使用。
 ### 返回:
 - 当前时间戳和状态码，状态码为200时表示成功，否则为失败，可以尝试更换一个作品id再次调用，或者等待一段时间后再次调用。

## check_live_room_online

`GET /api/v1/tiktok/app/v3/check_live_room_online`

<!-- Full path: /api/v1/tiktok/app/v3/check_live_room_online -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间id/Live room id | 7358603858249009962 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 检测直播间是否在线
 - 直播间的Room ID可以通过直播间链接从`/api/v1/tiktok/web/get_live_room_id`接口获取
 ### 参数:
 - room_id: 直播间id
 ### 返回:
 - 是否在线

## check_live_room_online_batch

`POST /api/v1/tiktok/app/v3/check_live_room_online_batch`

<!-- Full path: /api/v1/tiktok/app/v3/check_live_room_online_batch -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 批量检测多个 TikTok 直播间是否在线，最大支持50个直播间ID
 - Room ID 可以通过 `/api/v1/tiktok/web/get_live_room_id` 获取
 ### 参数:
 - room_ids: 多个直播间 ID 的数组
 ### 返回:
 - 每个直播间的在线状态

## decrypt_strData

`GET /api/v1/tiktok/web/decrypt_strData`

<!-- Full path: /api/v1/tiktok/web/decrypt_strData -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| encrypted_data | string | ✅ | 加密后的strData字符串/Encrypted strData string | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 解密strData指纹数据，用于分析msToken请求中的指纹信息
 ### 参数:
 - encrypted_data: 加密后的strData字符串，从浏览器自行抓包获取
 ### 返回:
 - 解密后的原始指纹数据，包含浏览器指纹信息和环境信息等。

## detect_fake_views

`GET /api/v1/tiktok/analytics/detect_fake_views`

<!-- Full path: /api/v1/tiktok/analytics/detect_fake_views -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过高级算法分析TikTok视频流量数据，精确检测可能存在的虚假观看量和不自然互动
- 基于TikTok赛马机制(Traffic Pool)流量池理论，评估内容真实性和流量质量
- 提供全面的欺诈风险分析，包含8种维度、20+指标的深度评估
- 为创作者、MCN机构和内容管理者提供专业的流量质量报告和优化建议
### 参数:
- item_id: 视频作品ID，必填参数，可从视频URL中提取(例如:
https://www.tiktok.com/@tiktok/video/7460937381265411370
中的7460937381265411370)
- content_category: 内容分类，可选参数，影响互动率基准值，选项包括:
  - default: 默认类别，通用内容
  - entertainment: 娱乐内容，预期有较高互动率
  - education: 教育内容，预期有适中互动和较高收藏率
  - product: 产品内容，预期有较低互动但较高转化
  - verified_large: 大型认证账号，预期互动率适当降低
### 返回内容详解:
- `video_metrics`: 视频核心指标
  - `total_views`: 总观看量，视频被观看的总次数
  - `total_likes`: 总点赞数，用户点赞互动次数
  - `total_comments`: 总评论数，用户评论互动次数
  - `total_favorites`: 总收藏数，用户收藏次数
  - `total_shares`: 总分享数，用户分享次数
  - `engagement_rates`: 互动率指标，值越高越好
    - `like_ratio`: 点赞率，正常值 1-10%，大账号可能较低
    - `comment_ratio`: 评论率，正常值 0.1-0.5%，高于1%极佳
    - `favorite_ratio`: 收藏率，正常值 0.05-0.8%
    - `share_ratio`: 分享率，正常值 0.05-0.5%，高于1%极佳
- `creator_metrics`: 创作者账号健康指标
  - `account_age_days`: 账号存在天数，越长越可信
  - `follower_count`: 粉丝数量，影响预期观看量
  - `verified`: 是否验证账号，认证账号可信度更高
  - `trust_score`: 账号信任度评分(0-100)，越高越可信
- `content_metrics`: 内容质量指标
  - `content_type`: 内容类型(video, image等)
  - `created_by_ai`: 是否AI生成，AI生成内容可能有特定流量模式
  - `high_quality_upload`: 是否高质量上传，高质量上传更可信
- `fake_view_analysis`: 虚假流量综合分析
  - `fake_score`: 虚假流量评分(0-100)，评分越低越好:
    - 0-20: 极低风险，自然流量模式
    - 20-40: 低风险，可能有少量异常但不构成问题
    - 40-60: 中等风险，存在值得关注的异常
    - 60-80: 高风险，明显的虚假流量特征
    - 80-100: 极高风险，几乎确定存在虚假流量
  - `confidence_level`: 风险等级，分为"Minimal", "Low", "Medium", "High"
  - `estimated_fake_views`: 估计虚假观看量，基于虚假流量模型推算
  - `fake_view_percentage`: 虚假观看百分比，虚假占总量的比例
  - `is_suspicious`: 是否可疑，综合判断是否需要关注
  - `main_detection_reason`: 主要检测原因，最显著的异常特征
  - `component_scores`: 各维度异常评分，各项都是0-100，越低越好:
    - `engagement_score`: 互动异常评分
    - `distribution_score`: 分布异常评分
    - `consistency_score`: 一致性异常评分
    - `creator_credibility_score`: 创作者可信度异常评分
    - `content_authenticity_score`: 内容真实性异常评分
    - `follower_correlation_score`: 粉丝相关性异常评分
    - `racing_mechanism_score`: 竞马机制异常评分
    - `fan_growth_score`: 粉丝增长异常评分
- `traffic_pool`: 流量池分析(TikTok竞马机制)
  - `current_tier`: 当前流量池级别(1-8)，越高代表流量越大
  - `current_tier_name`: 当前流量池名称
  - `expected_tier`: 预期流量池级别，基于有机流量预测
  - `expected_tier_name`: 预期流量池名称
  - `current_views_range`: 当前流量池预期观看范围
  - `expected_views_range`: 预期流量池观看范围
  - `estimated_organic_views`: 估计有机观看量，扣除虚假后的真实观看
- `suspicious_features`: 可疑特征列表，检测到的具体异常现象
- `recommendations`: 建议操作
  - `action`: 建议操作类型，可能值包括:
    - `no_action`: 无需操作，健康内容
    - `monitor`: 持续监控，存在轻微异常
    - `scheduled_review`: 安排审核，存在值得关注的异常
    - `immediate_review`: 立即审核，存在严重异常
  - `risk_level`: 风险等级("low", "medium", "high", "critical")
  - `potential_revenue_impact`: 潜在收益影响
  - `suggested_steps`: 建议步骤，具体操作建议
- `mcn_report`: (可选)MCN商业影响分析报告，适用于商业账号
  - `summary`: 摘要信息
  - `business_impact`: 商业影响评估
    - `revenue_impact`: 收益影响评估
    - `brand_safety_impact`: 品牌安全影响
    - `platform_relationship`: 平台关系影响
    - `contract_impact`: 合约影响评估
  - `recommended_actions`: 建议操作清单
  - `historical_context`: 历史背景数据
### 特性与优势:
- 基于TikTok原生流量池(Traffic Pool)理论构建的精确评估系统
- 8个维度、20+指标的全面分析，覆盖流量、互动、创作者、内容等全方位评估
- 自适应算法，根据账号规模、认证状态、内容类型自动调整阈值
- 基于大数据统计模型的异常检测，准确识别不自然流量模式
- 为不同规模账号(微型、小型、中型、大型、超大型)提供定制化评估标准
- 提供详细的商业影响分析和具体可行的建议步骤
### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/analytics/detect_fake_views",
  "params": {
    "item_id": "7460937381265411370",
    "content_category": "verified_large"
  },
  "data": {
    "video_metrics": {
      "total_views": 159414915,
      "total_likes": 15817234,
      "total_comments": 392493,
      "total_favorites": 1051470,
      "total_shares": 1312741,
      "engagement_rates": {
        "like_ratio": 0.09922,
        "comment_ratio": 0.00246,
        "favorite_ratio": 0.0066,
        "share_ratio": 0.00823
      }
    },
    "creator_metrics": {
      "account_age_days": 3733.94,
      "follower_count": 89827771,
      "verified": true,
      "trust_score": 100
    },
    "content_metrics": {
      "content_type": "video",
      "created_by_ai": false,
      "high_quality_upload": true
    },
    "fake_view_analysis": {
      "fake_score": 7.16,
      "confidence_level": "Minimal",
      "estimated_fake_views": 7970745,
      "fake_view_percentage": 5.0,
      "is_suspicious": false,
      "main_detection_reason": "Statistical View Anomalies",
      "component_scores": {
        "engagement_score": 0.0,
        "distribution_score": 10.0,
        "consistency_score": 0,
        "creator_credibility_score": 0,
        "content_authenticity_score": 34.0,
        "follower_correlation_score": 35.0,
        "racing_mechanism_score": 0,
        "fan_growth_score": 45
      }
    },
    "traffic_pool": {
      "current_tier": 8,
      "current_tier_name": "8th-Level Traffic Pool",
      "expected_tier": 8,
      "expected_tier_name": "8th-Level Traffic Pool",
      "current_views_range": "30M+",
      "expected_views_range": "30M+",
      "estimated_organic_views": 148000807
    },
    "suspicious_features": [
      "Suspicious: Reached 100000 followers from 10000 in only 31 days",
      "Suspicious: Account gaining 24063 followers per day on average"
    ],
    "recommendations": {
      "action": "no_action",
      "risk_level": "low",
      "potential_revenue_impact": "minimal",
      "suggested_steps": [
        "No immediate action required",
        "Include in routine monitoring"
      ]
    },
    "mcn_report": {
      "summary": {
        "estimated_revenue_impact": 7970.745,
        "recommended_actions": "No immediate action required"
      },
      "business_impact": {
        "revenue_impact": {
          "level": "low",
          "estimated_amount": 7970.745
        },
        "brand_safety_impact": {
          "level": "minimal"
        },
        "platform_relationship": {
          "status": "good"
        }
      }
    }
  }
}
```

## device_register

`GET /api/v1/tiktok/web/device_register`

<!-- Full path: /api/v1/tiktok/web/device_register -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 设备注册，为TikTok Web生成设备ID和游客Cookie
### 参数:
- 无
### 返回:
- 设备注册信息，包括设备ID和游客Cookie

## encrypt_decrypt_login_request

`POST /api/v1/tiktok/app/v3/encrypt_decrypt_login_request`

<!-- Full path: /api/v1/tiktok/app/v3/encrypt_decrypt_login_request -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 加密/解密 TikTok APP 登录请求体，用于登录接口的请求体加密和解密。
 ### 参数:
 - username: 用户名，可以是密文或明文。
 - password: 密码，可以是密文或明文。
 - mode: 模式
    - `encrypt`: 加密
    - `decrypt`: 解密
### 返回:
 - 加密/解密后的请求体

## encrypt_strData

`GET /api/v1/tiktok/web/encrypt_strData`

<!-- Full path: /api/v1/tiktok/web/encrypt_strData -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| data | string | ✅ | >- | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 加密strData指纹数据，用于生成msToken请求
 ### 参数:
 - data: 原始指纹数据字符串（请先将JSON格式然后转换成字符串进行请求）
 ### 返回:
 - 加密后的strData

## fetch_batch_check_live_alive

`GET /api/v1/tiktok/web/fetch_batch_check_live_alive`

<!-- Full path: /api/v1/tiktok/web/fetch_batch_check_live_alive -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_ids | string | ✅ | >- | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 批量直播间开播状态检测
 - 最多支持50个直播间同时查询
 - 如果某个直播间不存在或已下播，则对应位置返回空或null。
 ### 参数:
 - room_ids: 直播间ID列表，用英文逗号分隔，如：7530611486784277278,7530633767468288782
 ### 返回:
 - 批量直播间开播状态列表
 - 定价0.025$，请尽量达到50个直播间查询，避免浪费API调用次数。
 ### 说明:
 - 同一个room_id不会重复返回开播状态。

## fetch_check_live_alive

`GET /api/v1/tiktok/web/fetch_check_live_alive`

<!-- Full path: /api/v1/tiktok/web/fetch_check_live_alive -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间ID/Live room ID | 7381444193462078214 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 直播间开播状态检测
 - 如果当前直播间不存在或已下播，则返回空。
 ### 参数:
 - room_id: 直播间ID
 ### 返回:
 - 直播间开播状态

## fetch_comment_keywords

`GET /api/v1/tiktok/analytics/fetch_comment_keywords`

<!-- Full path: /api/v1/tiktok/analytics/fetch_comment_keywords -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7502551047378832671 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 分析视频评论中出现的热门关键词和话题，挖掘用户反馈
- 提取观众评论中的主要内容和观点，帮助理解受众关注点
- 支持创作者优化内容策略，增强与观众的互动和连接
### 参数:
- item_id: 视频作品ID，必填参数，可从视频分享链接或TikTok Studio获取
### 返回内容说明:
- `item_id`: 请求的视频ID
- `key_words`: 评论中提取的关键词列表，包含以下字段:
  - `key_word`: 关键词文本
  - `comments`: 包含该关键词的评论列表，每条评论包含:
    - `cid`: 评论ID
    - `text`: 评论内容
    - `create_date`: 评论创建时间戳
    - `digg_count`: 评论获赞数量
    - `comment_type`: 评论类型
    - `comment_author`: 评论作者信息
      - `uid`: 用户ID
      - `nick_name`: 用户昵称
      - `cover`: 用户头像信息
        - `url_list`: 头像URL列表
### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/analytics/fetch_comment_keywords",
  "params": {
    "item_id": "7502551047378832671"
  },
  "data": {
    "item_id": "7502551047378832671",
    "key_words": [
      {
        "key_word": "tik tok",
        "comments": [
          {
            "cid": "7502621950457463574",
            "comment_author": {
              "nick_name": "ollie_russell05",
              "uid": "7332627012203414560"
            },
            "create_date": 1746840350,
            "digg_count": 17,
            "text": "Imagine been tik tok and only getting 700 likes 🥀🙏😭"
          }
        ]
      },
      {
        "key_word": "go viral",
        "comments": [
          {
            "cid": "7502743477604680465",
            "comment_author": {
              "nick_name": "★ 🇦🇫",
              "uid": "7274239704915149829"
            },
            "create_date": 1746868614,
            "digg_count": 13,
            "text": "I want to go viral"
          }
        ]
      }
    ]
  }
}
```

## fetch_content_translate

`POST /api/v1/tiktok/app/v3/fetch_content_translate`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_content_translate -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取内容翻译数据
 ### 参数:
 - trg_lang: 目标语言
    - zh-Hans: 简体中文
    - zh-Hant: 繁体中文
    - en: 英语
    - ja: 日语
    - ko: 韩语
    - fr: 法语
    - de: 德语
    - ru: 俄语
    - es: 西班牙语
    - pt: 葡萄牙语
    - vi: 越南语
    - th: 泰语
    - id: 印尼语
    - ar: 阿拉伯语
    - it: 意大利语
    - tr: 土耳其语
    - he: 希伯来语
    - pl: 波兰语
    - nl: 荷兰语
    - sv: 瑞典语
    - da: 丹麦语
    - fi: 芬兰语
    - no: 挪威语
    - cs: 捷克语
    - hu: 匈牙利语
- src_content: 源内容，也就是需要翻译的内容，长度不超过5000个字符，如果超过5000个字符，只会翻译前5000个字符。
 ### 返回:
 - 内容翻译数据

## fetch_creator_info

`GET /api/v1/tiktok/app/v3/fetch_creator_info`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_creator_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| creator_uid | string | ✅ | 创作者uid/Creator uid | 6555451606845243393 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者信息，包括创作者的基本信息、粉丝数、橱窗商品数量、带货直播间等信息。
 ### 参数:
 - creator_uid: 创作者uid
 ### 返回:
 - 创作者信息

## fetch_creator_search_insights

`GET /api/v1/tiktok/app/v3/fetch_creator_search_insights`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_creator_search_insights -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| offset | integer |  | 分页偏移量/Pagination offset (default: 0) | 0 |
| limit | integer |  | 每页数量/Number per page (default: 20) | 20 |
| tab | string |  | >- (default: all) | all |
| language_filters | string |  | 语言过滤器，多个用逗号分隔/Language filters (id/de/en/es/fr/pt/vi/tr/ar/th/ja/ko) (default: en) | en |
| category_filters | string |  | >- (default: '') |  |
| creator_source | string |  | 创作者来源/Creator source (default: general_search) | general_search |
| force_refresh | boolean |  | 是否强制刷新/Force refresh (default: false) | false |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者搜索洞察数据，用于了解热门搜索趋势和创作灵感
 ### 参数:
 - offset: 分页偏移量，默认0
 - limit: 每页数量，默认20
 - tab: 标签页类型，可选值:
    - all: 全部
    - content_gap: 内容差距
    - follower_searched: 粉丝常搜
    - life_style: 生活方式
    - topics: 话题
    - challenges: 挑战
    - sounds: 声音
    - hashtags: 标签
- language_filters: 语言过滤器，多个用逗号分隔，可选值: id, de, en, es, fr, pt, vi, tr,
ar, th, ja, ko
 - category_filters: 分类过滤器，多个用逗号分隔，可选值: Gaming, Fashion, Tourism,
Science, Food, Sports
 - creator_source: 创作者来源，默认 "general_search"
 - force_refresh: 是否强制刷新，默认 False
 ### 返回:
 - 创作者搜索洞察数据

## fetch_creator_search_insights_detail

`GET /api/v1/tiktok/app/v3/fetch_creator_search_insights_detail`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_creator_search_insights_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query_id_str | string | ✅ | >- | 122991006 |
| time_range | string |  | >- (default: past_30_days) | past_30_days |
| start_date | integer |  | >- |  |
| end_date | integer |  | >- |  |
| dimension_list | string |  | 维度列表，多个用逗号分隔/Dimension list (gender/age/country) (default: gender,age,country) | gender,age,country |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者搜索洞察详情数据，用于查询特定搜索词条的搜索统计数据
 ### 参数:
 - query_id_str: 搜索词条ID，从 fetch_creator_search_insights 接口返回的数据中获取
 - time_range: 时间范围，可选值:
    - past_7_days: 过去7天
    - past_30_days: 过去30天（默认）
    - past_60_days: 过去60天
    - past_6_months: 过去6个月
    - custom: 自定义时间（需配合 start_date 和 end_date 使用，不能超过6个月）
- start_date: 开始时间戳（秒），仅当 time_range=custom 时生效
 - end_date: 结束时间戳（秒），仅当 time_range=custom 时生效
 - dimension_list: 维度列表，多个用逗号分隔，可选值: gender（性别）, age（年龄）, country（国家）
 ### 返回:
 - 搜索洞察详情数据，包含搜索趋势、用户画像等

## fetch_creator_search_insights_trend

`GET /api/v1/tiktok/app/v3/fetch_creator_search_insights_trend`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_creator_search_insights_trend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query_id_str | string | ✅ | >- | 7555720035176562699 |
| from_tab_path | string |  | 来源标签路径/From tab path (default: TRENDING,TOPICS) | TRENDING,TOPICS |
| query_analysis_required | boolean |  | 是否需要查询分析/Whether query analysis is required (default: true) | true |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者搜索洞察趋势数据，包含地区和时间维度的搜索热度
 ### 参数:
 - query_id_str: 搜索词条ID，从 fetch_creator_search_insights 接口返回的数据中获取
 - from_tab_path: 来源标签路径，默认 "TRENDING,TOPICS"
 - query_analysis_required: 是否需要查询分析，默认 True
 ### 返回:
 - 搜索趋势数据，包含地区热度、时间趋势等

## fetch_creator_search_insights_videos

`GET /api/v1/tiktok/app/v3/fetch_creator_search_insights_videos`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_creator_search_insights_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | headshots 2 2 3 |
| offset | integer |  | 分页偏移量/Pagination offset (default: 0) | 0 |
| count | integer |  | 每页数量/Number per page (default: 20) | 20 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者搜索洞察相关视频，查询该搜索词条下比较火的相关视频
 ### 参数:
 - keyword: 搜索关键词，从 fetch_creator_search_insights 或
fetch_creator_search_insights_trend 接口获取
 - offset: 分页偏移量，默认0
 - count: 每页数量，默认20
 ### 返回:
 - 相关热门视频列表

## fetch_creator_showcase_product_list

`GET /api/v1/tiktok/app/v3/fetch_creator_showcase_product_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_creator_showcase_product_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kol_id | string | ✅ | 创作者的sec_user_id/Creator's sec_user_id | >- |
| count | integer |  | 数量/Number (default: 20) |  |
| next_scroll_param | string |  | 翻页参数/Page parameter (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者橱窗商品列表
 ### 参数:
 - kol_id: 创作者的sec_user_id
 - count: 数量
 - next_scroll_param: 翻页参数，第一页为空字符串，后续请求使用上一次请求返回的next_scroll_param值。
 ### 返回:
 - 创作者橱窗商品列表

## fetch_explore_post

`GET /api/v1/tiktok/web/fetch_explore_post`

<!-- Full path: /api/v1/tiktok/web/fetch_explore_post -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| categoryType | string |  | 作品分类/Video category (default: '120') |  |
| count | integer |  | 每页数量/Number per page (default: 16) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取探索作品数据
 ### 参数:
 - categoryType: 作品分类
    - 100: 动画与漫画
    - 101: 表演
    - 102: 美容护理
    - 103: 游戏
    - 104: 喜剧
    - 105: 日常生活
    - 106: 家庭
    - 107: 情感关系
    - 108: 戏剧
    - 109: 穿搭
    - 110: 对口型
    - 111: 美食
    - 112: 运动
    - 113: 动物
    - 114: 社会
    - 115: 汽车
    - 116: 教育
    - 117: 健身和健康
    - 118: 科技
    - 119: 唱歌跳舞
    - 120: 全部
- count: 每页数量
 ### 返回:
 - 作品数据
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_general_search

`GET /api/v1/tiktok/web/fetch_general_search`

<!-- Full path: /api/v1/tiktok/web/fetch_general_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | TikTok |
| offset | integer |  | 翻页游标/Page cursor (default: 0) |  |
| search_id | string |  | 搜索id，翻页时需要提供/Search id, need to provide when paging (default: '') |  |
| cookie | string |  | 用户cookie(按需提供)/User cookie(if needed) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取综合搜索列表
 ### 参数:
 - keyword: 搜索关键词
 - offset: 翻页游标，第一次请求时为0，第二次请求时从上一次请求的返回响应中获取，一般这个值的关键字为offset或者cursor。
 - search_id: 搜索id，第一次请求时为空，第二次翻页时需要提供，需要从上一次请求的返回响应中获取。
    - 例如: search_id = "20240828035554C02011379EBB6A00E00B"
    - JSON Path-1 : $.data.extra.logid
    - JSON Path-2 : $.data.log_pb.impr_id
- cookie: 用户cookie(如果你需要使用自己的账号搜索，或者遇到接口报错，可以自行提供cookie，默认不需要提供)
 ### 返回:
 - 综合搜索列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_general_search_result

`GET /api/v1/tiktok/app/v3/fetch_general_search_result`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_general_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | 中华娘 |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| count | integer |  | 数量/Number (default: 20) | 20 |
| sort_type | integer |  | 排序类型/Sort type (default: 0) | 0 |
| publish_time | integer |  | 发布时间/Publish time (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定关键词的综合搜索结果
 ### 参数:
 - keyword: 关键词
 - offset: 偏移量
 - count: 数量
 - sort_type: 0-相关度，1-最多点赞
 - publish_time: 0-不限制，1-最近一天，7-最近一周，30-最近一个月，90-最近三个月，180-最近半年
 ### 返回:
 - 综合搜索结果

## fetch_hashtag_detail

`GET /api/v1/tiktok/app/v3/fetch_hashtag_detail`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_hashtag_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ch_id | string | ✅ | 话题id/Hashtag id | 7551 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定话题的详情数据
### 参数:
- ch_id: 话题id
### 返回:
- 话题详情数据

## fetch_hashtag_search_result

`GET /api/v1/tiktok/app/v3/fetch_hashtag_search_result`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_hashtag_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Cat |
| offset | integer |  | 偏移量/Offset (default: 0) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定关键词的话题搜索结果
### 参数:
- keyword: 关键词
- offset: 偏移量
- count: 数量
### 返回:
- 话题搜索结果

## fetch_hashtag_video_list

`GET /api/v1/tiktok/app/v3/fetch_hashtag_video_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_hashtag_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ch_id | string | ✅ | 话题id/Hashtag id | 7551 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定话题的作品数据
 ### 参数:
 - ch_id: 话题id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量
 ### 返回:
 - 话题作品数据

## fetch_home_feed

`POST /api/v1/tiktok/app/v3/fetch_home_feed`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_home_feed -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取主页视频推荐数据
 ### 参数:
 - cookie: 用户自己的cookie，可选参数，用于接口返回数据的个性化推荐。
 ### 返回:
 - 视频推荐数据

## fetch_home_feed

`POST /api/v1/tiktok/app/v3/fetch_home_feed`

<!-- Full path: /api/v1/tiktok/web/fetch_home_feed -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 首页推荐作品
 ### 参数:
 - count: 每页数量
 - cookie: 用户自己的cookie，可选参数，用于接口返回数据的个性化推荐。
 ### 返回:
 - 首页推荐作品
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_hot_selling_products_list

`GET /api/v1/tiktok/shop/web/fetch_hot_selling_products_list`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_hot_selling_products_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| region | string |  | 地区代码/Region code (default: US) | US |
| count | integer |  | 返回商品数量/Number of products to return (default: 100) | 100 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取TikTok Shop的热卖商品列表
- 返回当前最受欢迎的商品
### 参数:
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
- count: 返回商品数量，默认100 (可选)
### 返回数据结构:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "products": [                // 热卖商品列表(最多1000个)
            {
                "product_id": "xxx",
                "title": "商品标题",
                "image": "商品图片",
                "price": {},              // 价格信息
                "rating": {},             // 评分信息
                "sales": {},              // 销量信息
                "rank": 1                 // 热卖排名
            }
        ]
    }
}
```

## fetch_live_daily_rank

`GET /api/v1/tiktok/app/v3/fetch_live_daily_rank`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_live_daily_rank -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| anchor_id | string |  | 主播id/Anchor id (default: '6952422426752205830') |  |
| room_id | string |  | 直播间id/Live room id (default: '7380221319910312750') |  |
| rank_type | integer |  | 榜单类型/Rank type (default: 8) |  |
| region_type | integer |  | 地区类型/Region type (default: 1) |  |
| gap_interval | integer |  | 时间间隔/Time interval (default: 0) |  |
| cookie | string |  | 用户自己的cookie/User's own cookie (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取直播每日榜单数据
 ### 参数:
 - anchor_id: 主播id，可以从直播间信息接口获取，使用默认值即可，该参数会影响返回的数据，你可以尝试不同直播间的主播id。
 - room_id: 直播间id，可以从直播间信息接口获取，使用默认值即可，该参数会影响返回的数据，你可以尝试不同直播间的id。
 - rank_type: 榜单类型，参数值如下表：
     | type | rankName | 分组类型 | 说明 |
    |------|----------|----------|------|
    | 0 | `hourly_rank` | GIFT_RANK | 小时榜 |
    | 1 | `weekly_rank` | GIFT_RANK | 周榜 |
    | 5 | `rookie_star_rank` | GIFT_RANK | 新星榜 |
    | 6 | `sale_rank` | E_COMMERCE | 带货榜 |
    | 8 | `daily_rank` | GIFT_RANK | 日榜 |
    | 10 | `weekly_game_rank` | GAME_RANK | 周游戏榜 |
    | 11 | `daily_game_rank` | GAME_RANK | 日游戏榜 |
    | 12 | `hall_of_fame_rank` | GIFT_RANK | 名人堂 |
    | 13 | `champion_tournament` | GIFT_RANK | 冠军赛（含phase_one/two/three） |
    | 14 | `daily_rookie_star_rank` | GIFT_RANK | 日新星榜 |
    | 15 | `fans_team_rank` | GIFT_RANK | 粉丝团榜 |
    | 16 | `ranking_league` | GIFT_RANK | 排位联赛（App内显示: D5段位榜） |
    | 20 | `pubg` | GAME_RANK | PUBG游戏榜 |
    | 21 | `mlbb` | GAME_RANK | MLBB游戏榜（Mobile Legends: Bang Bang） |
    | 22 | `free_fire` | GAME_RANK | Free Fire游戏榜 |
    | 23 | `sub_weekly_game_rank1` | GAME_RANK | 子周游戏榜1 |
    | 24 | `sub_weekly_game_rank2` | GAME_RANK | 子周游戏榜2 |
    | 25 | `sub_weekly_game_rank3` | GAME_RANK | 子周游戏榜3 |
    | 26 | `collectibles` | E_COMMERCE | 收藏品榜 |
    | 27 | `beauty` | E_COMMERCE | 美妆榜 |
    | 28 | `women_wear` | E_COMMERCE | 女装榜 |
    | 29 | `sale_rank_daily` | E_COMMERCE | 日带货榜 |
    | 1001 | `league_campaign_rank` | GIFT_RANK | 联赛活动榜 |
    | -1 | `unknown` | DEFAULT | 未知 |
 - region_type: 地区类型，使用默认值即可，具体含义不明。
 - gap_interval: 时间间隔，使用默认值代表当天，使用-1代表排名记录。
 - cookie: 用户自己的cookie，可选参数，用于接口不可用时使用。
 ### 返回:
 - 直播每日榜单数据

## fetch_live_gift_list

`GET /api/v1/tiktok/web/fetch_live_gift_list`

<!-- Full path: /api/v1/tiktok/web/fetch_live_gift_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string |  | 直播间ID，可选参数/Live room ID, optional parameter (default: '') | 7381444193462078214 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取直播间礼物列表
 - room_id为可选参数，不传则获取通用礼物列表（2025年08月15日统计是256种礼物）
 ### 参数:
 - room_id: 直播间ID（可选）
 ### 返回:
 - 直播间礼物列表数据
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_live_im_fetch

`GET /api/v1/tiktok/web/fetch_live_im_fetch`

<!-- Full path: /api/v1/tiktok/web/fetch_live_im_fetch -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间号/Live room id | 7382517534467115826 |
| user_unique_id | string |  | 用户唯一ID/User unique ID | 7382524529011246630 |
| resp_content_type | string |  | '响应格式: protobuf 或 json / Response format: protobuf or json' (default: protobuf) | protobuf |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- TikTok直播间弹幕参数获取
### 参数:
- room_id: 直播间号
- user_unique_id: 用户唯一ID（可选）
- resp_content_type: 响应格式，protobuf（默认）或 json
 ### 返回:
- 弹幕参数数据

## fetch_live_ranking_list

`GET /api/v1/tiktok/app/v3/fetch_live_ranking_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_live_ranking_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间id/Live room id | 7358603858249009962 |
| anchor_id | string | ✅ | 主播id/Anchor id | 7222941468722758702 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取直播间内观众的排行榜数据
### 参数:
- room_id: 直播间id
- anchor_id: 主播id
### 返回:
- 排行榜数据

## fetch_live_recommend

`GET /api/v1/tiktok/web/fetch_live_recommend`

<!-- Full path: /api/v1/tiktok/web/fetch_live_recommend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| related_live_tag | string | ✅ | 相关直播标签/Related live tag | VALORANT |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取直播间首页推荐列表
 ### 参数:
 - related_live_tag: 相关直播标签
 ### 返回:
 - 直播间首页推荐列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_live_room_info

`GET /api/v1/tiktok/app/v3/fetch_live_room_info`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_live_room_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间id/Live room id | 7358603858249009962 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定直播间的数据
### 参数:
- room_id: 直播间id
### 返回:
- 直播间数据

## fetch_live_room_product_list

`GET /api/v1/tiktok/app/v3/fetch_live_room_product_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_live_room_product_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间id/Live room id | 7420741353250507562 |
| author_id | string | ✅ | 主播id/Anchor id | 7408859677050274859 |
| page_size | integer |  | 数量/Number (default: 15) |  |
| offset | integer |  | 数量/Number (default: 0) |  |
| region | string |  | 地区/Region (default: US) |  |
| cookie | string |  | 用户自己的cookie/User's own cookie (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取直播间商品列表数据
 ### 参数:
 - room_id: 直播间id，必填参数。
 - author_id: 主播id，必填参数。
 - page_size: 每页数量，可选参数，默认为15。
 - offset: 翻页游标，可选参数，默认为0，每次翻页增加15。
 - region: 地区，可选参数，默认为`US`，如果使用其他地区，如：`VN`，请自行携带Cookie，否则无法获取数据。
 - cookie: 用户自己的cookie，可选参数，用于爬取除`US`以外的地区数据。
 ### 参数获取:

第一步：使用接口`f"{maxhub_Domain}/api/v1/tiktok/web/get_live_room_id"`接口获取直播间id（room_id）。

第二步：使用接口`f"{maxhub_Domain}/api/v1/tiktok/app/v3/fetch_live_room_info"`接口获取直播间信息。

第三步：使用第二步返回的JSON数据中使用JSONPATH获取`$.data.data.owner.id_str`字段的值作为主播id（author_id）。
 ### 返回:
 - 直播间商品列表数据

## fetch_live_room_product_list_v2

`GET /api/v1/tiktok/app/v3/fetch_live_room_product_list_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_live_room_product_list_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间id/Live room id | 7420741353250507562 |
| author_id | string | ✅ | 主播id/Anchor id | 7408859677050274859 |
| page_size | integer |  | 数量/Number (default: 15) |  |
| offset | integer |  | 数量/Number (default: 0) |  |
| region | string |  | 地区/Region (default: US) |  |
| cookie | string |  | 用户自己的cookie/User's own cookie (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取直播间商品列表数据 V2
 ### 参数:
 - room_id: 直播间id，必填参数。
 - author_id: 主播id，必填参数。
 - page_size: 每页数量，可选参数，默认为15。
 - offset: 翻页游标，可选参数，默认为0，每次翻页增加15。
 - region: 地区，可选参数，默认为`US`，如果使用其他地区，如：`VN`，请自行携带Cookie，否则无法获取数据。
 - cookie: 用户自己的cookie，可选参数，用于爬取除`US`以外的地区数据。
 ### 参数获取:

第一步：使用接口`f"{maxhub_Domain}/api/v1/tiktok/web/get_live_room_id"`接口获取直播间id（room_id）。

第二步：使用接口`f"{maxhub_Domain}/api/v1/tiktok/app/v3/fetch_live_room_info"`接口获取直播间信息。

第三步：使用第二步返回的JSON数据中使用JSONPATH获取`$.data.data.owner.id_str`字段的值作为主播id（author_id）。
 ### 返回:
 - 直播间商品列表数据

## fetch_live_search_result

`GET /api/v1/tiktok/app/v3/fetch_live_search_result`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_live_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Cat |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| count | integer |  | 数量/Number (default: 20) | 20 |
| region | string |  | 地区/Region (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定关键词的直播搜索结果
 ### 参数:
 - keyword: 关键词
 - offset: 偏移量，从0开始，第二页从响应中获取cursor的值作为offset继续请求。
 - count: 数量，不要超过20
 - region: 地区，默认为US-美国，可选值请参考TikTok地区代码或ISO 3166-1 alpha-2国家代码。
 ### 返回:
 - 直播搜索结果

## fetch_location_search

`GET /api/v1/tiktok/app/v3/fetch_location_search`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_location_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Shanghai |
| offset | integer |  | 偏移量/Offset (default: 0) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取地点搜索结果
### 参数:
- keyword: 关键词
- offset: 偏移量
- count: 数量
### 返回:
- 地点搜索结果

## fetch_multi_video

`POST /api/v1/tiktok/app/v3/fetch_multi_video`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_multi_video -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 如果本接口报错，请使用 fetch_multi_video_v3 接口。
 ### 参数:
 - aweme_ids: 作品id列表，最多支持10个作品id。
 ### 返回:
 - 作品数据

## fetch_multi_video_v2

`POST /api/v1/tiktok/app/v3/fetch_multi_video_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_multi_video_v2 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 注意：此接口为V2版本，支持更多功能和更高效的数据获取，一秒可以获取25个视频数据。
 - 如果本接口报错，请使用 fetch_multi_video_v3 接口。
 ### 参数:
 - aweme_ids: 作品id列表，最多支持25个作品id。
 ### 返回:
 - 作品数据

## fetch_music_chart_list

`GET /api/v1/tiktok/app/v3/fetch_music_chart_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_music_chart_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| scene | integer |  | '排行榜类型/Chart type (0: Top 50, 1: Viral 50)' (default: 0) | 0 |
| cursor | integer |  | 分页游标/Pagination cursor (default: 0) | 0 |
| count | integer |  | 每页数量/Number per page (max 50) (default: 50) | 50 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取TikTok音乐排行榜数据
### 参数:
- scene: 排行榜类型
    - 0: Top 50 (热门前50)
    - 1: Viral 50 (病毒式传播前50)
- cursor: 分页游标，默认0
- count: 每页数量，默认50，最大50
### 返回:
- 音乐排行榜数据，包含歌曲信息、排名变化等

## fetch_music_detail

`GET /api/v1/tiktok/app/v3/fetch_music_detail`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_music_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| music_id | string | ✅ | 音乐id/Music id | 6943027371519772674 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定音乐的详情数据
### 参数:
- music_id: 音乐id
### 返回:
- 音乐详情数据

## fetch_music_search_result

`GET /api/v1/tiktok/app/v3/fetch_music_search_result`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_music_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Cat |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| count | integer |  | 数量/Number (default: 20) | 20 |
| filter_by | integer |  | 过滤类型/Filter type (default: 0) | 0 |
| sort_type | integer |  | 排序类型/Sort type (default: 0) | 0 |
| region | string |  | 地区/Region (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定关键词的音乐搜索结果
 ### 参数:
 - keyword: 关键词
 - offset: 偏移量，从0开始，第二页从响应中获取cursor的值作为offset继续请求。
 - count: 数量，不要超过20
 - filter_by: 过滤类型，0-全部，1-标题，2-作者，默认为0-全部
 - sort_type: 排序类型，0-相关度，1-最多使用，2-最新，3-时长最短，4-时长最长，默认为0-相关度
 - region: 地区，默认为US-美国，可选值请参考TikTok地区代码或ISO 3166-1 alpha-2国家代码。
 ### 返回:
 - 音乐搜索结果

## fetch_music_video_list

`GET /api/v1/tiktok/app/v3/fetch_music_video_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_music_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| music_id | string | ✅ | 音乐id/Music id | 6943027371519772674 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定音乐的视频列表数据
 ### 参数:
 - music_id: 音乐id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量
 ### 返回:
 - 音乐视频列表数据

## fetch_one_video

`GET /api/v1/tiktok/app/v3/fetch_one_video`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7350810998023949599 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个作品数据
### 参数:
- aweme_id: 作品id
### 返回:
- 作品数据

## fetch_one_video_by_share_url_v2

`GET /api/v1/tiktok/app/v3/fetch_one_video_by_share_url_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_one_video_by_share_url_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_url | string | ✅ | 分享链接/Share link | https://www.tiktok.com/t/ZTFNEj8Hk/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据分享链接获取单个作品数据 V2，数据结构会有些不一样，会返回region字段。
 ### 参数:
 - share_url: 分享链接
 ### 返回:
 - 作品数据

## fetch_one_video_v2

`GET /api/v1/tiktok/app/v3/fetch_one_video_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_one_video_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7350810998023949599 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个作品数据 V2
### 参数:
- aweme_id: 作品id
### 返回:
- 作品数据

## fetch_one_video_v3

`GET /api/v1/tiktok/app/v3/fetch_one_video_v3`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_one_video_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7350810998023949599 |
| region | string |  | 国家代码/Country code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据 V3
 ### 参数:
 - aweme_id: 作品id
 - region: 国家代码，默认US，支持ISO 3166-1 alpha-2国家代码，例如：US、GB、FR、DE、IN、JP等。
 - 备注：某些视频可能在特定国家/地区不可用，设置region参数可以尝试获取该国家/地区的视频数据。
 ### 返回:
 - 作品数据

## fetch_post_comment

`GET /api/v1/tiktok/web/fetch_post_comment`

<!-- Full path: /api/v1/tiktok/web/fetch_post_comment -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7304809083817774382 |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| current_region | string |  | 当前地区/Current region (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取作品的评论列表
### 参数:
- aweme_id: 作品id
- cursor: 翻页游标
- count: 每页数量
- current_region: 当前地区，默认为空。
### 返回:
- 作品的评论列表

## fetch_post_comment_reply

`GET /api/v1/tiktok/web/fetch_post_comment_reply`

<!-- Full path: /api/v1/tiktok/web/fetch_post_comment_reply -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7304809083817774382 |
| comment_id | string | ✅ | 评论id/Comment id | 7304877760886588191 |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| current_region | string |  | 当前地区/Current region (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取作品的评论回复列表
### 参数:
- item_id: 作品id
- comment_id: 评论id
- cursor: 翻页游标
- count: 每页数量
- current_region: 当前地区，默认为空。
### 返回:
- 作品的评论回复列表

## fetch_post_detail

`GET /api/v1/tiktok/web/fetch_post_detail`

<!-- Full path: /api/v1/tiktok/web/fetch_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| itemId | string | ✅ | 作品id/Video id | 7339393672959757570 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据
 ### 参数:
 - itemId: 作品id
 ### 返回:
 - 作品数据
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_post_detail_v2

`GET /api/v1/tiktok/web/fetch_post_detail_v2`

<!-- Full path: /api/v1/tiktok/web/fetch_post_detail_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| itemId | string | ✅ | 作品id/Video id | 7339393672959757570 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据
 ### 参数:
 - itemId: 作品id
 ### 返回:
 - 作品数据
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_product_detail

`GET /api/v1/tiktok/app/v3/fetch_product_detail`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品id/Product id | 1729385239712731370 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品详情数据
 - 即将弃用，使用 fetch_product_detail_v2 代替
 ### 参数:
 - product_id: 商品id，有时候需要从product_id_str字段中获取。
 ### 返回:
 - 商品详情数据

## fetch_product_detail

`GET /api/v1/tiktok/app/v3/fetch_product_detail`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_product_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 1729556436942358002 |
| seller_id | string |  | 卖家ID(可选)/Seller ID (optional) (default: '') | 7494629757824764402 |
| region | string |  | 地区代码/Region code (default: MY) | MY |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok Shop商品的详细信息
 - 包含商品基本信息、价格、库存、评价、推荐商品等完整数据
 - 某些特殊地区的商品可能无法获取到数据（如：泰国），如果遇到此情况请尝试使用 `fetch_product_detail_v3` 接口
 ### 参数:
 - seller_id: 卖家ID (可传空字符串)
 - product_id: 商品ID (必填)
 - region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
 ### 重要提示:
 - 由于接口风控原因，请务必将请求timeout设置为30秒
 - 如遇到400错误代码，请重试请求3次
 ### 返回数据结构:
 ```json
 {
    "code": 0,
    "message": "success",
    "data": {
        "global_fe_config": {},      // 全局前端配置
        "components_map": [],         // 组件映射列表
        "global_data": {              // 全局数据
            "product_info": {},       // 商品信息
            "seller_info": {},        // 卖家信息
            "shipping_info": {},      // 物流信息
            "review_info": {}         // 评价信息
        }
    }
}
 ```

## fetch_product_detail_v2

`GET /api/v1/tiktok/app/v3/fetch_product_detail_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_detail_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品id/Product id | 1729385239712731370 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品详情数据V2
 ### 参数:
 - product_id: 商品id，有时候需要从product_id_str字段中获取。
 ### 返回:
 - 商品详情数据V2

## fetch_product_detail_v2

`GET /api/v1/tiktok/app/v3/fetch_product_detail_v2`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_product_detail_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 1729556436942358002 |
| seller_id | string |  | 卖家ID(可选)/Seller ID (optional) (default: '') | 7494629757824764402 |
| region | string |  | 地区代码/Region code (default: MY) | MY |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok Shop商品详情(移动端接口)
 - 数据结构更精简，响应速度更快
 - 此接口返回的数据更少，如果需要更完整的数据请使用 `fetch_product_detail` 或
`fetch_product_detail_v3` 接口
 ### 参数:
 - seller_id: 卖家ID (可传空字符串)
 - product_id: 商品ID (必填)
 - region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
 ### 重要提示:
 - 由于接口风控原因，请务必将请求timeout设置为30秒
 - 如遇到400错误代码，请重试请求3次
 ### 返回数据结构:
 ```json
 {
    "code": 0,
    "message": "success",
    "data": {
        "productDetailSchema": {},    // 商品详细信息
        "productCategoryInfoSchema": {}, // 分类信息
        "pdpRelatedKwSchema": [],     // 相关关键词
        "productsForComponentListSchema": [] // 推荐商品组件
    }
}
 ```

## fetch_product_detail_v3

`GET /api/v1/tiktok/app/v3/fetch_product_detail_v3`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_detail_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品id / Product ID | 1729385239712731370 |
| region | string |  | 商品的国家/地区代码/ Country/region code of the product (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品详情数据V3。如果商品详情数据V2无法获取，可以尝试使用此接口。
  ### 参数:
 - product_id: 商品id，有时候需要从 `product_id_str` 字段中获取，也可以从商品分享链接中获取。
 - region: 商品的国家/地区代码，默认值为 "US"。
  ### 支持的国家/地区代码（按区域分组）：
 - 东南亚 Southeast Asia:
  ID（印度尼西亚）, SG（新加坡）, MY（马来西亚）, PH（菲律宾）, TH（泰国）
- 北美 North America:
  US（美国）, MX（墨西哥）
- 欧洲 Europe:
  IE（爱尔兰）, GB（英国）, ES（西班牙）
- 越南 Vietnam:
  VN（越南）
 ### 返回:
 - 商品详情数据V3

## fetch_product_detail_v3

`GET /api/v1/tiktok/app/v3/fetch_product_detail_v3`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_product_detail_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 1732108663255959373 |
| region | string |  | 地区代码/Region code (default: SG) | SG |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok Shop商品详情
 - 提供最完整的商品信息，包括推荐商品、相关视频、店铺信息等
 - 适用于所有地区的商品
 ### 参数:
 - product_id: 商品ID (必填)
 - region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
 ### 重要提示:
 - **请务必确保 `product_id` 对应的 `region` 是正确的，否则接口将不会返回数据。**
 - 由于接口风控原因，请务必将请求timeout设置为30秒
 - 如遇到400错误代码，请重试请求3次
 ### 返回数据结构:
 ```json
 {
    "code": 200,
    "data": {
        "productInfo": {},                           // 商品详细信息
        "frequentlyBoughtTogether": [],              // 经常一起购买的商品
        "similarProductsInCategory": [],             // 同类别相似商品
        "exploreMoreFromShop": [],                   // 店铺更多商品
        "brandInCategoryRecommendedProducts": [],    // 品牌分类推荐商品
        "customersAlsoBought": [],                   // 顾客还购买了
        "moreInThisColorStyle": [],                  // 更多颜色款式
        "relatedVideos": [],                         // 相关视频
        "shopPerformance": {},                       // 店铺表现
        "categoryInfo": {},                          // 分类信息
        "searchRecommendWords": [],                  // 搜索推荐词
        "randomSearchWord": "",                      // 随机搜索词
        "shopInfo": {},                              // 店铺信息
        "shopHotReviews": []                         // 店铺热门评论
    }
}
 ```

## fetch_product_detail_v4

`GET /api/v1/tiktok/app/v3/fetch_product_detail_v4`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_detail_v4 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品id / Product ID | 1729385239712731370 |
| region | string |  | 商品的国家/地区代码/ Country/region code of the product (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品详情数据V4。如果商品详情数据V3无法获取，可以尝试使用此接口。
  ### 参数:
 - product_id: 商品id，有时候需要从 `product_id_str` 字段中获取，也可以从商品分享链接中获取。
 - region: 商品的国家/地区代码，默认值为 "US"。
  ### 支持的国家/地区代码（按区域分组）：
 - 东南亚 Southeast Asia:
  ID（印度尼西亚）, SG（新加坡）, MY（马来西亚）, PH（菲律宾）, TH（泰国）
- 北美 North America:
  US（美国）, MX（墨西哥）
- 欧洲 Europe:
  IE（爱尔兰）, GB（英国）, ES（西班牙）
- 越南 Vietnam:
  VN（越南）
 ### 返回:
 - 商品详情数据V4

## fetch_product_id_by_share_link

`GET /api/v1/tiktok/app/v3/fetch_product_id_by_share_link`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_id_by_share_link -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_link | string | ✅ | 分享链接/Share link | https://www.tiktok.com/t/ZT98v9dPs6aEC-qHWeW/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过分享链接获取商品ID
 ### 参数:
 - share_link: 分享链接
 ### 返回:
 - 商品ID

## fetch_product_review

`GET /api/v1/tiktok/app/v3/fetch_product_review`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_review -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品id/Product id | 1729448812983194615 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| size | integer |  | 数量/Number (default: 10) |  |
| filter_id | integer |  | 筛选条件/Filter condition (default: 0) |  |
| sort_type | integer |  | 排序条件/Sorting conditions (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品评价数据
 ### 参数:
 - product_id: 商品id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - size: 数量
 - filter_id: 筛选条件
    - 0: 全部评价
    - 1: 1星评价
    - 2: 2星评价
    - 3: 3星评价
    - 4: 4星评价
    - 5: 5星评价
    - 102: 有图评价
    - 104: 已购买的评价
- sort_type: 排序条件
    - 1: 相关度
    - 2: 从新到旧
### 返回:
 - 商品评价数据

## fetch_product_reviews_v2

`GET /api/v1/tiktok/shop/web/fetch_product_reviews_v2`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_product_reviews_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 1729556436942358002 |
| page_start | integer |  | 起始页码/Page start (default: 1) | 1 |
| sort_rule | integer |  | 排序规则/Sort rule (default: 2) | 2 |
| filter_type | integer |  | '筛选类型/Filter type: 1=默认, 2=有图片/视频, 3=真实购买' (default: 1) | 1 |
| filter_value | integer |  | '星级筛选/Star filter: 6=全部, 5-1=对应星级' (default: 6) | 6 |
| region | string |  | 地区代码/Region code (default: MY) | MY |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取TikTok Shop商品评论
- 支持多种筛选和排序方式
- 数据结构更完整，包含更多评论详情
### 参数:
- product_id: 商品ID (必填)
- page_start: 起始页码，默认1
    - 当响应中 has_more=1 时，使用当前页码 +1 进行下一页请求
- sort_rule: 排序规则，默认2
- filter_type: 筛选类型
    - 1: 默认不选择任何过滤
    - 2: 包含图片或视频
    - 3: 真实购买过滤
- filter_value: 星级筛选
    - 6: 所有星级的评论(默认)
    - 5: 5星评价
    - 4: 4星评价
    - 3: 3星评价
    - 2: 2星评价
    - 1: 1星评价
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 重要提示:
- 由于接口风控原因，请务必将请求timeout设置为30秒
- 如遇到400错误代码，请重试请求3次
### 返回数据结构:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "reviews": [                      // 评论列表(每页20条)
            {
                "review_id": "xxx",
                "user": {                 // 用户信息
                    "user_id": "xxx",
                    "nickname": "用户昵称",
                    "avatar": "头像URL"
                },
                "rating": 5,              // 评分(1-5星)
                "content": "评论内容",
                "medias": [               // 媒体文件(图片/视频)
                    {
                        "type": "image",
                        "url": "媒体URL"
                    }
                ],
                "create_time": 0,         // 创建时间戳
                "verified_purchase": true, // 是否认证购买
                "product_info": {},       // 商品信息
                "likes_count": 10,        // 点赞数
                "seller_reply": {}        // 卖家回复
            }
        ],
        "has_more": 1,                    // 是否有更多: 1=有, 0=无
        "page_start": 1,                  // 当前页码
        "total_count": 500,               // 总评论数
        "review_summary": {               // 评论摘要
            "average_rating": 4.8,
            "star_distribution": {        // 星级分布
                "5": 400,
                "4": 80,
                "3": 15,
                "2": 3,
                "1": 2
            }
        }
    }
}
```

## fetch_product_search

`GET /api/v1/tiktok/app/v3/fetch_product_search`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_product_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Cat Toy |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 12) |  |
| sort_type | integer |  | 商品排序条件/Product sorting conditions (default: 1) |  |
| customer_review_four_star | boolean |  | 四星以上评价/Four-star or more reviews (default: false) |  |
| have_discount | boolean |  | 有优惠/Having discount (default: false) |  |
| min_price | string |  | 最低价格/Minimum price (default: '') |  |
| max_price | string |  | 最高价格/Maximum price (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商品搜索结果
 ### 参数:
 - keyword: 关键词
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量
 - sort_type: 商品排序条件
    - 1: 综合排序
    - 2: 销量排序
    - 3: 价格从高到低
    - 4: 价格从低到高
    - 5: 最新发布
- customer_review_four_star: 四星以上评价
 - have_discount: 有优惠
 - min_price: 最低价格
 - max_price: 最高价格
 ### 返回:
 - 商品搜索结果

## fetch_products_by_category_id

`GET /api/v1/tiktok/shop/web/fetch_products_by_category_id`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_products_by_category_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| category_id | integer | ✅ | 分类ID/Category ID | 963976 |
| offset | integer |  | 翻页偏移量/Offset for pagination (default: 0) | 0 |
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据商品分类ID获取该分类下的商品列表
 - 可用于构建分类浏览功能
 ### 参数:
 - category_id: 分类ID (必填，从fetch_products_category_list接口获取)
 - offset: 翻页偏移量 (默认0)
    - 每页默认20个商品，每次请求增加20，当响应中的 `hasMore` 为true时可继续请求下一页，否则已到最后一页。
    - 例如: 第1页offset=0，第2页offset=20，第3页offset=40，以此类推。
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
 ### 重要提示:
 - 由于接口风控原因，请务必将请求timeout设置为30秒
 - 如遇到400错误代码，请重试请求3次
 ### 返回数据结构:
 ```json
 {
    "code": 0,
    "message": "success",
    "data": {
        "products": [                // 商品列表(最多20个)
            {
                "product_id": "xxx",
                "title": "商品标题",
                "image": "商品图片",
                "price": {},              // 价格信息
                "rating": {},             // 评分信息
                "sales": {}               // 销量信息
            }
        ]
    }
}
 ```

## fetch_products_category_list

`GET /api/v1/tiktok/shop/web/fetch_products_category_list`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_products_category_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取TikTok Shop的商品分类目录
- 返回完整的分类树结构
### 参数:
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 返回数据结构:
```json
[
    {
        "self": {                     // 分类自身信息
            "category_id": "xxx",
            "category_level": 1,
            "is_leaf": false,
            "parent_category_id": "0",
            "category_name": "分类名称",
            "category_name_en": "Category Name",
            "image_url": "分类图片URL"
        },
        "children": [                 // 子分类列表
            {
                "self": {...},
                "children": [...]
            }
        ]
    }
]
```
- 总共约28个主分类

## fetch_search_keyword_suggest

`GET /api/v1/tiktok/web/fetch_search_keyword_suggest`

<!-- Full path: /api/v1/tiktok/web/fetch_search_keyword_suggest -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | TikTok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索关键字推荐
### 参数:
- keyword: 搜索关键词
### 返回:
- 关键字推荐列表

## fetch_search_products_list

`GET /api/v1/tiktok/shop/web/fetch_search_products_list`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_search_products_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| search_word | string | ✅ | 搜索关键词/Search keyword | labubu |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| page_token | string |  | 分页标记/Page token (default: '') |  |
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据关键词搜索商品
- 支持分页加载更多结果
### 参数:
- search_word: 搜索关键词 (必填)
- offset: 偏移量，用于分页 (默认0)
- page_token: 分页标记，用于获取下一页
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 重要提示:
- 由于接口风控原因，请务必将请求timeout设置为30秒
- 如遇到400错误代码，请重试请求3次
### 返回数据结构:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "products": [                // 商品列表(每页30个)
            {
                "product_id": "xxx",
                "title": "商品标题",
                "image": "商品图片URL",
                "product_price_info": {},  // 价格信息
                "rate_info": {},           // 评分信息
                "sold_info": {},           // 销量信息
                "seller_info": {},         // 卖家信息
                "seo_url": "商品SEO链接",
                "product_marketing_info": {} // 营销信息
            }
        ],
        "has_more": true,             // 是否有更多
        "load_more_params": {         // 分页参数
            "offset": 30,
            "page_token": "xxx",
            "api_source": 2
        }
    }
}
```

## fetch_search_products_list_v2

`GET /api/v1/tiktok/shop/web/fetch_search_products_list_v2`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_search_products_list_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| search_word | string | ✅ | 搜索关键词/Search keyword | labubu |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| page_token | string |  | 分页标记/Page token (default: '') |  |
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索商品(移动端接口)
- 数据结构更精简，响应更快
### 参数:
- search_word: 搜索关键词 (必填)
- offset: 偏移量 (默认0)
- page_token: 分页标记
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 返回数据结构:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "products": [...],            // 商品列表
        "has_more": true,             // 是否有更多
        "load_more_params": {}        // 加载更多参数
    }
}
```

## fetch_search_video

`GET /api/v1/tiktok/web/fetch_search_video`

<!-- Full path: /api/v1/tiktok/web/fetch_search_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | TikTok |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| offset | integer |  | 翻页游标/Page cursor (default: 0) |  |
| search_id | string |  | 搜索id，翻页时需要提供/Search id, need to provide when paging (default: '') |  |
| cookie | string |  | 用户cookie(按需提供)/User cookie(if needed) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索视频
 ### 参数:
 - keyword: 搜索关键词
 - count: 每页数量，建议保持默认值20。
 - offset: 翻页游标，第一次请求时为0，第二次请求时从上一次请求的返回响应中获取。
 - search_id: 搜索id，第一次请求时为空，第二次翻页时需要提供，需要从上一次请求的返回响应中获取。
    - 例如: search_id = "20240828035554C02011379EBB6A00E00B"
    - JSON Path-1 : $.data.extra.logid
    - JSON Path-2 : $.data.log_pb.impr_id
- cookie: 用户cookie(如果你需要使用自己的账号搜索，或者遇到接口报错，可以自行提供cookie，默认不需要提供)
 ### 返回:
 - 视频列表

## fetch_search_word_suggestion_v2

`GET /api/v1/tiktok/shop/web/fetch_search_word_suggestion_v2`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_search_word_suggestion_v2 -->

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
- 获取搜索关键词建议(移动端接口)
- 专为电商搜索结果优化
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
        "关键词1",
        "关键词2",
        "..."
    ]
}
```

## fetch_seller_products_list

`GET /api/v1/tiktok/shop/web/fetch_seller_products_list`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_seller_products_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 卖家ID/Seller ID | 7495150558072178725 |
| search_params | string |  | 搜索参数(用于分页)/Search params (for pagination) (default: '') | >- |
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定商家的商品列表
- 支持分页加载更多商品
### 参数:
- seller_id: 卖家ID (必填)
- search_params: 搜索参数，用于分页加载(可选)
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 重要提示:
- 由于接口风控原因，请务必将请求timeout设置为30秒
- 如遇到400错误代码，请重试请求3次
### 返回数据结构:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "products": [                // 商品列表(每页30个)
            {
                "product_id": "xxx",
                "title": "商品标题",
                "image": "商品图片URL",
                "product_price_info": {},  // 价格信息
                "rate_info": {},           // 评分信息
                "sold_info": {},           // 销量信息
                "seller_info": {},         // 卖家信息
                "seo_url": "商品SEO链接"
            }
        ],
        "has_more": true,             // 是否有更多商品
        "load_more_params": {}        // 加载更多参数(用于下一页)
    }
}
```

## fetch_seller_products_list_v2

`GET /api/v1/tiktok/shop/web/fetch_seller_products_list_v2`

<!-- Full path: /api/v1/tiktok/shop/web/fetch_seller_products_list_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 卖家ID/Seller ID | 7495150558072178725 |
| searchParams | string |  | 搜索参数/Search params (default: '') |  |
| region | string |  | 地区代码/Region code (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取商家商品列表(移动端接口)
- 数据结构更精简
### 参数:
- seller_id: 卖家ID (必填)
- searchParams: 搜索参数(可选)
- region: 地区代码 (US/GB/SG/MY/PH/TH/VN/ID)
### 重要提示:
- 由于接口风控原因，请务必将请求timeout设置为30秒
- 如遇到400错误代码，请重试请求3次
### 返回数据结构:
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "products": [...],            // 商品列表
        "has_more": true,             // 是否有更多
        "load_more_params": {}        // 加载更多参数
    }
}
```

## fetch_share_qr_code

`GET /api/v1/tiktok/app/v3/fetch_share_qr_code`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_share_qr_code -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| object_id | string | ✅ | 对象id/Object id | 6762244951259661318 |
| schema_type | integer |  | 模式类型/Schema type (default: 4) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取分享二维码
 ### 参数:
 - object_id: 对象id，当前支持个人主页接口响应中的uid作为参数。
 ### 返回:
 - 二维码图片

## fetch_share_short_link

`GET /api/v1/tiktok/app/v3/fetch_share_short_link`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_share_short_link -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 分享链接/Share link | https://www.tiktok.com/passport/web/logout/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取分享短链接
### 参数:
- url: 长链接或想要转换的链接
### 返回:
- 短链接

## fetch_shop_home

`GET /api/v1/tiktok/app/v3/fetch_shop_home`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_home -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page_id | string | ✅ | 爬取的商家主页Page id/Page id of the crawled shop home page | 7314705727611930410 |
| seller_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 8646929864612614278 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商家主页的商品数据
 ### 参数:
 - page_id: 爬取的商家主页Page id，可以从`fetch_shop_home_page_list`这个接口获取
 - seller_id: 商家id,店铺id
 ### 返回:
 - 商家主页数据

## fetch_shop_home_page_list

`GET /api/v1/tiktok/app/v3/fetch_shop_home_page_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_home_page_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 8646929864612614278 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取商家主页Page列表数据, 用于商家主页展示，以及爬取商家主页的商品数据
 ### 参数:
 - seller_id: 商家id,店铺id
 ### 返回:
 - 商家主页Page列表数据

## fetch_shop_id_by_share_link

`GET /api/v1/tiktok/app/v3/fetch_shop_id_by_share_link`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_id_by_share_link -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_link | string | ✅ | 分享链接/Share link | https://vt.tiktok.com/ZT2AHoGsE/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过分享链接获取店铺ID
### 参数:
- share_link: 分享链接
### 返回:
- 店铺ID

## fetch_shop_info

`GET /api/v1/tiktok/app/v3/fetch_shop_info`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| shop_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 8646942781241463007 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取商家信息数据
### 参数:
- shop_id: 商家id,店铺id
### 返回:
- 商家信息数据

## fetch_shop_product_category

`GET /api/v1/tiktok/app/v3/fetch_shop_product_category`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_product_category -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 7495294980909468039 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取商家产品分类数据
### 参数:
- seller_id: 商家id,店铺id
### 返回:
- 商家产品分类数据

## fetch_shop_product_list

`GET /api/v1/tiktok/app/v3/fetch_shop_product_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_product_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 8646929864612614278 |
| scroll_params | string |  | 滚动参数，用于加载更多商品数据/Scroll parameter, used to load more product data (default: '') |  |
| page_size | integer |  | 每页数量/Number per page (default: 10) |  |
| sort_field | integer |  | 排序字段/Sorting field (default: 1) |  |
| sort_order | integer |  | 排序方式/Sorting method (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取商家商品列表数据
### 参数:
- seller_id: 商家id,店铺id
- scroll_params: 滚动参数，用于加载更多商品数据
- page_size: 每页数量
- sort_field: 排序字段
    - 1: 综合排序
    - 3: 最新发布
    - 4: 销量最好
    - 5: 价格排序
- sort_order: 排序方式
    - 0: 默认价格排序
    - 1: 价格从高到低
    - 2: 价格从低到高
### 返回:
- 商家商品列表数据

## fetch_shop_product_list_v2

`GET /api/v1/tiktok/app/v3/fetch_shop_product_list_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_product_list_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 8646929864612614278 |
| scroll_params | string |  | 滚动参数，用于加载更多商品数据/Scroll parameter, used to load more product data (default: '') |  |
| page_size | integer |  | 每页数量/Number per page (default: 10) |  |
| sort_field | integer |  | 排序字段/Sorting field (default: 1) |  |
| sort_order | integer |  | 排序方式/Sorting method (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取商家商品列表数据
### 参数:
- seller_id: 商家id,店铺id
- scroll_params: 滚动参数，用于加载更多商品数据
- page_size: 每页数量
- sort_field: 排序字段
    - 1: 综合排序
    - 3: 最新发布
    - 4: 销量最好
    - 5: 价格排序
- sort_order: 排序方式
    - 0: 默认价格排序
    - 1: 价格从高到低
    - 2: 价格从低到高
### 返回:
- 商家商品列表数据

## fetch_shop_product_recommend

`GET /api/v1/tiktok/app/v3/fetch_shop_product_recommend`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_shop_product_recommend -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| seller_id | string | ✅ | 商家id,店铺id/Seller id, shop id | 8646929864612614278 |
| scroll_param | string |  | 滚动参数，用于加载更多商品数据/Scroll parameter, used to load more product data (default: '') |  |
| page_size | integer |  | 每页数量/Number per page (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取商家商品推荐数据
### 参数:
- seller_id: 商家id,店铺id
- scroll_param: 滚动参数，用于加载更多商品数据
- page_size: 每页数量
### 返回:
- 商家商品推荐数据

## fetch_similar_user_recommendations

`GET /api/v1/tiktok/app/v3/fetch_similar_user_recommendations`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_similar_user_recommendations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_uid/User sec_uid | >- |
| page_token | string |  | 分页标记/Page token (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取类似用户推荐
 ### 参数:
 - sec_uid: 用户sec_uid
 - page_token: 分页标记，第一次请求时不需要传递，后续请求时传递上一次响应中的next_page_token值。
 ### 返回:
 - 类似用户推荐

## fetch_tag_detail

`GET /api/v1/tiktok/web/fetch_tag_detail`

<!-- Full path: /api/v1/tiktok/web/fetch_tag_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_name | string | ✅ | Tag名称/Tag name | tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- Tag详情
### 参数:
- tag_name: Tag名称
### 返回:
- Tag详情

## fetch_tag_post

`GET /api/v1/tiktok/web/fetch_tag_post`

<!-- Full path: /api/v1/tiktok/web/fetch_tag_post -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| challengeID | string | ✅ | Tag ID | 7551 |
| count | integer |  | 每页数量/Number per page (default: 30) |  |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - Tag作品
 ### 参数:
 - challengeID: Tag ID
 - count: 每页数量
 - cursor: 翻页游标
 ### 返回:
 - Tag作品
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_tiktok_live_data

`GET /api/v1/tiktok/web/fetch_tiktok_live_data`

<!-- Full path: /api/v1/tiktok/web/fetch_tiktok_live_data -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| live_room_url | string | ✅ | 直播间链接/Live room link | https://www.tiktok.com/@.caseoh_daily/live |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过直播链接获取直播间信息
- 此接口可获取离线直播间信息
### 参数:
- live_room_url: 直播间链接
### 返回:
- 直播间信息

## fetch_tiktok_web_guest_cookie

`GET /api/v1/tiktok/web/fetch_tiktok_web_guest_cookie`

<!-- Full path: /api/v1/tiktok/web/fetch_tiktok_web_guest_cookie -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_agent | string | ✅ | 用户浏览器代理/User browser agent | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Web的游客Cookie
 - 可以用于爬取 TikTok Web 的数据，如用户作品、合辑作品等。
 - 可以固定身份避免部分接口重复数据。
 - 请注意：游客Cookie无法爬取所有数据，有一定的限制。
 - 可以配合开源项目使用此接口实现TikTok Web的数据爬取。
 ### 参数:
 - user_agent: 用户浏览器代理
 ### 返回:
 - 游客Cookie

## fetch_user_country_by_username

`GET /api/v1/tiktok/app/v3/fetch_user_country_by_username`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_country_by_username -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | 用户名/Username | tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过用户名获取用户账号国家地区
 ### 参数:
 - username:
用户名，可以从用户主页链接中获取，例如：https://www.tiktok.com/@tiktok，用户名即为tiktok。
 ### 返回:
 - 用户账号国家地区

## fetch_user_follower_list

`GET /api/v1/tiktok/app/v3/fetch_user_follower_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_follower_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID (与sec_user_id二选一/One of user_id and sec_user_id) (default: '') | 7486586574684881927 |
| sec_user_id | string |  | >- (default: '') | >- |
| count | integer |  | 数量/Number (default: 20) | 20 |
| min_time | integer |  | 最小时间，用于翻页/Minimum time for paging (default: 0) | 0 |
| page_token | string |  | 翻页token/Page token (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的粉丝列表数据
 ### 参数:
 - user_id: 用户ID，这是一个纯数字版本的用户ID (与sec_user_id二选一/One of user_id and
sec_user_id)
 - sec_user_id: 用户sec_user_id，这是一个混合字母和数字的版本ID (与user_id二选一/One of
user_id and sec_user_id)
 - count: 数量，不要超过20，保持固定。
 - min_time: 最小时间，用于翻页，第一次请求使用默认值0，后续请求使用上一次请求返回的min_time值。
 - page_token: 翻页token，第一次请求使用默认值""，后续请求使用上一次请求返回的page_token值。
 ### 返回:
 - 粉丝列表数据

## fetch_user_following_list

`GET /api/v1/tiktok/app/v3/fetch_user_following_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_following_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户ID/User ID (与sec_user_id二选一/One of user_id and sec_user_id) (default: '') | 7486586574684881927 |
| sec_user_id | string |  | >- (default: '') | >- |
| count | integer |  | 数量/Number (default: 20) | 20 |
| min_time | integer |  | 最小时间，用于翻页/Minimum time for paging (default: 0) | 0 |
| page_token | string |  | 翻页token/Page token (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的关注列表数据
 ### 参数:
 - user_id: 用户ID，这是一个纯数字版本的用户ID (与sec_user_id二选一/One of user_id and
sec_user_id)
 - sec_user_id: 用户sec_user_id，这是一个混合字母和数字的版本ID (与user_id二选一/One of
user_id and sec_user_id)
 - count: 数量，不要超过20，保持固定。
 - min_time: 最小时间，用于翻页，第一次请求使用默认值0，后续请求使用上一次请求返回的min_time值。
 - page_token: 翻页token，第一次请求使用默认值""，后续请求使用上一次请求返回的page_token值。
 ### 返回:
 - 关注列表数据

## fetch_user_like_videos

`GET /api/v1/tiktok/app/v3/fetch_user_like_videos`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_like_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 用户sec_user_id/User sec_user_id | >- |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| counts | integer |  | 每页数量/Number per page (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户喜欢作品数据
 ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_cursor: 最大游标，用于翻页，第一页为0，第二页为第一次响应中的max_cursor值。
 - count: 最大数量
 ### 返回:
 - 用户作品数据

## fetch_user_live_detail

`GET /api/v1/tiktok/web/fetch_user_live_detail`

<!-- Full path: /api/v1/tiktok/web/fetch_user_live_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uniqueId | string | ✅ | 用户uniqueId/User uniqueId | tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的直播详情
 ### 参数:
 - uniqueId: 用户uniqueId
 ### 返回:
 - 用户的直播详情
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_mix

`GET /api/v1/tiktok/web/fetch_user_mix`

<!-- Full path: /api/v1/tiktok/web/fetch_user_mix -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| mixId | string | ✅ | 合辑id/Mix id | 7101538765474106158 |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 30) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的合辑列表
 ### 参数:
 - mixId: 合辑id
 - cursor: 翻页游标
 - count: 每页数量
 ### 返回:
 - 用户的合辑列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_music_list

`GET /api/v1/tiktok/app/v3/fetch_user_music_list`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_music_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_uid/User sec_uid | >- |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户音乐列表数据
 ### 参数:
 - sec_uid: 用户sec_uid
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量
 ### 返回:
 - 用户音乐列表数据

## fetch_user_play_list

`GET /api/v1/tiktok/web/fetch_user_play_list`

<!-- Full path: /api/v1/tiktok/web/fetch_user_play_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| secUid | string | ✅ | 用户secUid/User secUid | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 30) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的播放列表
 ### 参数:
 - secUid: 用户secUid
 - cursor: 翻页游标
 - count: 每页数量
 ### 返回:
 - 用户的播放列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_post

`GET /api/v1/tiktok/web/fetch_user_post`

<!-- Full path: /api/v1/tiktok/web/fetch_user_post -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| secUid | string | ✅ | 用户secUid/User secUid | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) | 0 |
| count | integer |  | 每页数量/Number per page (default: 20) | 20 |
| coverFormat | integer |  | 封面格式/Cover format (default: 2) | 2 |
| post_item_list_request_type | integer |  | 排序方式/Sort type (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的作品列表
 ### 参数:
 - secUid: 用户secUid
 - cursor: 翻页游标
 - count: 每页数量，默认为20，不可变更。
 - coverFormat: 封面格式，默认为2，可选值为1或2。
 - post_item_list_request_type: 排序方式
    - 0：默认排序
    - 1：热门排序
    - 2：最旧排序
### 返回:
 - 用户的作品列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_post_videos

`GET /api/v1/tiktok/app/v3/fetch_user_post_videos`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_post_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: '') | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| unique_id | string |  | 用户unique_id/User unique_id (default: '') |  |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| sort_type | integer |  | 排序类型/Sort type (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户主页作品数据
 ### 参数:
 - sec_user_id:
用户sec_user_id，优先使用sec_user_id获取用户作品数据，如果sec_user_id为空，则使用unique_id获取用户作品数据。
 - max_cursor: 最大游标，用于翻页，第一页为0，第二页为第一次响应中的max_cursor值。
 - count: 最大数量，建议保持默认值20。
 - sort_type: 排序类型，0-最新，1-热门
 - unique_id:
用户unique_id，可选参数，如果sec_user_id为空，则使用unique_id获取用户作品数据，unique_id也是用户的用户名。
 - 关于用户ID的参数，优先级为sec_user_id >
unique_id，优先级越高速度越快，并且建议只使用sec_user_id获取用户数据。
 ### 返回:
 - 用户作品数据

## fetch_user_post_videos_v2

`GET /api/v1/tiktok/app/v3/fetch_user_post_videos_v2`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_post_videos_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: '') | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| unique_id | string |  | 用户unique_id/User unique_id (default: '') |  |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| sort_type | integer |  | 排序类型/Sort type (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户主页作品数据
 ### 参数:
 - sec_user_id:
用户sec_user_id，优先使用sec_user_id获取用户作品数据，如果sec_user_id为空，则使用unique_id获取用户作品数据。
 - max_cursor: 最大游标，用于翻页，第一页为0，第二页为第一次响应中的max_cursor值。
 - count: 最大数量，建议保持默认值20。
 - sort_type: 排序类型，0-最新，1-热门
 - unique_id:
用户unique_id，可选参数，如果sec_user_id为空，则使用unique_id获取用户作品数据，unique_id也是用户的用户名。
 - 关于用户ID的参数，优先级为sec_user_id >
unique_id，优先级越高速度越快，并且建议只使用sec_user_id获取用户数据。
 ### 返回:
 - 用户作品数据

## fetch_user_post_videos_v3

`GET /api/v1/tiktok/app/v3/fetch_user_post_videos_v3`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_post_videos_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: '') | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| unique_id | string |  | 用户unique_id/User unique_id (default: '') |  |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| sort_type | integer |  | 排序类型/Sort type (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户主页作品数据
 ### 参数:
 - sec_user_id:
用户sec_user_id，优先使用sec_user_id获取用户作品数据，如果sec_user_id为空，则使用unique_id获取用户作品数据。
 - max_cursor: 最大游标，用于翻页，第一页为0，第二页为第一次响应中的max_cursor值。
 - count: 最大数量，建议保持默认值20。
 - sort_type: 排序类型，0-最新，1-热门
 - unique_id:
用户unique_id，可选参数，如果sec_user_id为空，则使用unique_id获取用户作品数据，unique_id也是用户的用户名。
 - 关于用户ID的参数，优先级为sec_user_id >
unique_id，优先级越高速度越快，并且建议只使用sec_user_id获取用户数据。
 ### 返回:
 - 用户作品数据

## fetch_user_repost

`GET /api/v1/tiktok/web/fetch_user_repost`

<!-- Full path: /api/v1/tiktok/web/fetch_user_repost -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| secUid | string | ✅ | 用户secUid/User secUid | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| cursor | integer |  | 翻页游标/Page cursor (default: 0) | 0 |
| count | integer |  | 每页数量/Number per page (default: 20) | 20 |
| coverFormat | integer |  | 封面格式/Cover format (default: 2) | 2 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的转发作品列表
 ### 参数:
 - secUid: 用户secUid
 - cursor: 翻页游标
 - count: 每页数量，默认为20，不可变更。
 - coverFormat: 封面格式，默认为2，可选值为1或2。
 ### 返回:
 - 用户的转发作品列表
 ### 备注:
 - 此接口返回的所有视频CDN链接均需要携带返回的 `tt_chain_token` 参数才能正常访问，否则会返回HTTP403错误。
 - 在访问视频CDN链接时，请务必在请求头中携带 `Cookie: tt_chain_token={tt_chain_token}`，其中
`{tt_chain_token}` 替换为接口返回的 `tt_chain_token` 参数值。
 - **如果访问视频CDN链接时返回HTTP 403错误**:
  1. 请使用接口响应中以 `https://www.tiktok.com/aweme/v1/play/` 开头的视频链接(通常在响应数据的 `video.playAddr` 或类似字段中)
  2. 在请求该链接时，务必在请求头中添加 `Cookie: tt_chain_token={tt_chain_token}`，其中 `{tt_chain_token}` 为接口返回的 `tt_chain_token` 参数值
  3. 示例请求头: `Cookie: tt_chain_token=xxx`
- 如果需要绕过此限制获取可以直接访问的无水印视频CDN链接，请使用 TikTok APP V3 目录下的接口。

## fetch_user_repost_videos

`GET /api/v1/tiktok/app/v3/fetch_user_repost_videos`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_repost_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | integer | ✅ | 用户id/User id | 107955 |
| offset | integer |  | 偏移量/Offset (default: 0) |  |
| count | integer |  | 数量/Number (default: 21) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户转发的作品数据
 ### 参数:
 - user_id: 用户id，可以通过 handler_user_profile 端点获取，响应中的关键字为uid。
 - offset: 偏移量
 - count: 数量
 ### 返回:
 - 用户转发作品数据

## fetch_user_search_result

`GET /api/v1/tiktok/app/v3/fetch_user_search_result`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_user_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Cat |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| count | integer |  | 数量/Number (default: 20) | 20 |
| user_search_follower_count | string |  | 根据粉丝数排序/Sort by number of followers (default: '') |  |
| user_search_profile_type | string |  | 根据账号类型排序/Sort by account type (default: '') |  |
| user_search_other_pref | string |  | 根据其他偏好排序/Sort by other preferences (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定关键词的用户搜索结果
### 参数:
- keyword: 关键词
- offset: 偏移量
- count: 数量
- user_search_follower_count（根据粉丝数排序）:
    - 空-不限制，
    - ZERO_TO_ONE_K = 0-1K，
    - ONE_K_TO_TEN_K-1K = 1K-10K，
    - TEN_K_TO_ONE_H_K = 10K-100K，
    - ONE_H_K_PLUS = 100K以上
- user_search_profile_type（根据账号类型排序）:
    - 空-不限制，
    - VERIFIED = 认证用户
- user_search_other_pref（根据其他偏好排序）:
    - USERNAME = 根据用户名相关性
### 返回:
- 用户搜索结果

## fetch_video_comment_replies

`GET /api/v1/tiktok/app/v3/fetch_video_comment_replies`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_video_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7326156045968067873 |
| comment_id | string | ✅ | 评论id/Comment id | 7327061675382260482 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定视频的评论回复数据
 ### 参数:
 - item_id: 作品id
 - comment_id: 评论id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量
 ### 返回:
 - 评论回复数据

## fetch_video_comments

`GET /api/v1/tiktok/app/v3/fetch_video_comments`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_video_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7326156045968067873 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个视频评论数据
 ### 参数:
 - aweme_id: 作品id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量
 ### 返回:
 - 评论数据

## fetch_video_metrics

`GET /api/v1/tiktok/analytics/fetch_video_metrics`

<!-- Full path: /api/v1/tiktok/analytics/fetch_video_metrics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7502551047378832671 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok视频的详细统计数据，包括观看量、点赞数、评论数和收藏数等核心指标
 - 提供总量统计以及从发布日期起14天的每日趋势数据，便于分析视频表现
 - 帮助创作者分析内容效果，评估用户互动情况，优化内容策略
  ### 参数:
 - item_id: 视频作品ID，必填参数，可从视频分享链接或TikTok Studio获取
  ### 返回内容说明:
 - `item_id`: 请求的视频ID
 - `video_views`: 视频总观看次数
  - `value`: 观看次数数值
- `video_views_14_days`: 近14天的每日观看量趋势数据
  - `interval`: 数据间隔类型
  - `value`: 每日数据列表
- `likes`: 视频总点赞数
  - `value`: 点赞数值
- `likes_14_days`: 近14天的每日点赞数趋势数据
 - `comments`: 视频总评论数
  - `value`: 评论数值
- `comments_14_days`: 近14天的每日评论数趋势数据
 - `favorites`: 视频总收藏数
  - `value`: 收藏数值
- `favorites_14_days`: 近14天的每日收藏数趋势数据
 - `video_summary`: 视频表现的概览分析
  - `title`: 概览标题
  - `content`: 概览内容
  - `summary_type`: 概览类型
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/analytics/fetch_video_metrics",
  "params": {
    "item_id": "7502551047378832671"
  },
  "data": {
    "item_id": "7502551047378832671",
    "video_views": {
      "value": 1555500
    },
    "likes": {
      "value": 11571
    },
    "comments": {
      "value": 6920
    },
    "favorites": {
      "value": 1243
    },
    "video_summary": {
      "title": "Overview",
      "content": "This post received more comments per view than most other posts."
    }
  }
}
 ```

## fetch_video_search_result

`GET /api/v1/tiktok/app/v3/fetch_video_search_result`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_video_search_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | 中华娘 |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |
| count | integer |  | 数量/Number (default: 20) | 20 |
| sort_type | integer |  | 排序类型/Sort type (default: 0) | 0 |
| publish_time | integer |  | 发布时间/Publish time (default: 0) | 0 |
| region | string |  | 地区/Region (default: US) | US |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定关键词的视频搜索结果
 ### 参数:
 - keyword: 关键词
 - offset: 偏移量
 - count: 数量
 - sort_type: 0-相关度，1-最多点赞
 - publish_time: 0-不限制，1-最近一天，7-最近一周，30-最近一个月，90-最近三个月，180-最近半年
 - region: 地区，默认为US-美国，可选值请参考TikTok地区代码或ISO 3166-1 alpha-2国家代码。
 ### 返回:
 - 视频搜索结果

## fetch_webcast_user_info

`GET /api/v1/tiktok/app/v3/fetch_webcast_user_info`

<!-- Full path: /api/v1/tiktok/app/v3/fetch_webcast_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户uid （可选，纯数字）/User uid (optional, pure number) (default: '') |  |
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: '') | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的信息
 ### 参数:
 - sec_user_id: 用户sec_user_id，优先使用sec_user_id获取用户信息。
 - user_id: 用户uid，可选参数，纯数字，如果使用请保持sec_user_id以及unique_id为空。
 - 以上参数必须至少填写一个，优先级为sec_user_id > user_id，优先级越高速度越快。
 ### 返回:
 - 用户信息

## generate_fingerprint

`GET /api/v1/tiktok/web/generate_fingerprint`

<!-- Full path: /api/v1/tiktok/web/generate_fingerprint -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| browser_type | string |  | '' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成随机浏览器指纹数据，可用于自定义msToken请求
### 参数:
- browser_type: 指定浏览器类型，可选值:
    - chrome_windows: Chrome + Windows
    - chrome_mac: Chrome + macOS
    - firefox_windows: Firefox + Windows
    - firefox_mac: Firefox + macOS
    - 不传则随机选择
### 返回:
- 浏览器指纹数据

## generate_hashed_id

`GET /api/v1/tiktok/web/generate_hashed_id`

<!-- Full path: /api/v1/tiktok/web/generate_hashed_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| email | string | ✅ | 邮箱地址/Email address | test@example.com |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成TikTok Web的哈希ID
### 参数:
- email: 邮箱地址
### 返回:
- 生成的哈希ID字符串

## generate_real_msToken

`GET /api/v1/tiktok/web/generate_real_msToken`

<!-- Full path: /api/v1/tiktok/web/generate_real_msToken -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| random_strData | boolean |  | '' (default: false) |  |
| browser_type | string |  | '' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成真实msToken
 ### 参数:
 - random_strData: 是否使用随机化的浏览器指纹数据（推荐开启以提高反爬虫能力）
 - browser_type: 指定浏览器类型，可选值:
    - chrome_windows: Chrome + Windows
    - chrome_mac: Chrome + macOS
    - firefox_windows: Firefox + Windows
    - firefox_mac: Firefox + macOS
    - 不传则随机选择
### 返回:
 - 真实msToken

## generate_ttwid

`GET /api/v1/tiktok/web/generate_ttwid`

<!-- Full path: /api/v1/tiktok/web/generate_ttwid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_agent | string |  | '' (default: >-) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成ttwid
### 参数:
- 无
### 返回:
- ttwid

## generate_webid

`GET /api/v1/tiktok/web/generate_webid`

<!-- Full path: /api/v1/tiktok/web/generate_webid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cookie | string |  | '' |  |
| user_agent | string |  | '' (default: >-) |  |
| url | string |  | '' (default: https://www.tiktok.com/explore) |  |
| referer | string |  | '' (default: '') |  |
| user_unique_id | string |  | '' (default: '') |  |
| app_id | integer |  | '' (default: 1988) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成 TikTok web_id （Web接口请求参数中的device_id）
 ### 参数:
 - cookie: 自定义 cookie（需包含 odin_tt），如不传则使用随机生成的游客Cookie值
 - user_agent: 用户代理字符串
 - url: 请求来源 URL
 - referer: 来源页面
 - user_unique_id: 用户唯一 ID（可选）
 - app_id: 应用 ID，默认 1988，代表 TikTok Web 应用
 ### 返回:
 - web_id: 生成的 web_id
 - e: 错误码 (0 表示成功)
 - ssid: 会话 ID

## generate_wss_xb_signature

`GET /api/v1/tiktok/web/generate_wss_xb_signature`

<!-- Full path: /api/v1/tiktok/web/generate_wss_xb_signature -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_agent | string |  | 用户浏览器代理（可选）/User browser agent (optional) | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成TikTok直播WSS连接所需的X-Bogus签名
 ### 参数:
 - user_agent: 用户浏览器代理（可选，不填则使用默认UA）
 ### 返回:
 - x_bogus: WSS X-Bogus签名字符串

## generate_xbogus

`POST /api/v1/tiktok/web/generate_xbogus`

<!-- Full path: /api/v1/tiktok/web/generate_xbogus -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成xbogus
### 参数:
- url: 未签名的API URL
- user_agent: 用户浏览器User-Agent
### 返回:
- xbogus

## generate_xgnarly

`POST /api/v1/tiktok/web/generate_xgnarly`

<!-- Full path: /api/v1/tiktok/web/generate_xgnarly -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成 XGnarly 加密，用于 TikTok Web API 请求
 - 此接口使用最新版本（V5.2.0，截至2026年3月）的签名服务，不可自定义 User-Agent，会自动生成一个常见浏览器的
User-Agent
 - 此接口为完美还原算法，无视除验证码外的一切风控
 ### 参数:
 - url (str): 不携带签名（X-Bogus 或 X-Gnarly）并且包含域名的请求URL，不需要进行URL编码
 - body (str): 请求的API参数，适用于POST请求，如果是GET请求则不需要提供
 ### 返回:
 - X-Gnarly 加密字符串 + 随机浏览器的 User-Agent

## generate_xgnarly_and_xbogus

`POST /api/v1/tiktok/web/generate_xgnarly_and_xbogus`

<!-- Full path: /api/v1/tiktok/web/generate_xgnarly_and_xbogus -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成 XGnarly 和 XBogus 加密，用于 TikTok Web API 请求
 - 用这个接口可以生成最新版本的加密参数 X-Bogus 和 X-Gnarly，不可自定义 User-Agent，会自动生成一个常见浏览器的
User-Agent
 - 本接口生成的 X-Bogus 和 X-Gnarly 均为最新版本（V5.2.0，截至2026年3月）
 ### 参数:
 - url (str): 不携带签名（X-Bogus 或 X-Gnarly）并且包含域名的请求URL，不需要进行URL编码
 - body (str): 请求的API参数，适用于POST请求，如果是GET请求则不需要提供
 ### 返回:
 - 最新版本的 X-Gnarly 加密 + 最新版本的 X-Bogus 加密 + 随机浏览器的 User-Agent

## get_account_violation_list

`POST /api/v1/tiktok/creator/get_account_violation_list`

<!-- Full path: /api/v1/tiktok/creator/get_account_violation_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号的违规记录信息，用于了解账号在运营期间的违规历史和处理情况。
 - 返回的违规记录包含违规类型、违规时间、违规原因、违规处理措施、申诉状态、是否可申诉等信息。
 - 支持分页查询，可按时间顺序获取多条违规记录。
 - 适用于创作者账号违规风险管理、账号健康监控和数据合规审计。
  ### 备注:
 - 此接口仅适用于 TikTok Shop 创作者账号。
 - 支持分页查询，每次默认返回最新的违规记录。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - page: 整数类型，页码，默认为第 1 页
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - `records`（违规记录列表）:
  - `record_id`: 违规记录 ID
  - `violation_time`: 违规发生时间（Unix 时间戳）
  - `violation_info`:
    - `violation_reason`: 违规原因描述
    - `violation_detail`: 违规详情描述
    - `violation_suggestion`: 平台提供的整改建议
    - `policy_url`: 相关政策链接
    - `violation_type`: 违规类别（如视频违规）
  - `record_status`: 记录状态（1 表示有效）
  - `appeal_status`: 申诉状态（0=未申诉，1=已申诉）
  - `enforcement_title`: 平台针对违规采取的执行措施描述（例如扣分、佣金冻结等）
  - `appeal_valid_time`: 申诉有效截止时间（Unix 时间戳）
  - `can_appeal`: 是否允许发起申诉（布尔值）
- `total`: 总违规记录数
 - `has_more`: 是否还有更多数据
 - `start_time`: 查询起始时间
 - `end_time`: 查询结束时间
 - `creator_status`: 创作者账号状态码（如 0=正常）

## get_ads_detail

`GET /api/v1/tiktok/ads/get_ads_detail`

<!-- Full path: /api/v1/tiktok/ads/get_ads_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ads_id | string | ✅ | 广告ID/Ad ID | 7131673574381518849 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok单个广告的详细信息，包括广告素材、创作者信息、互动数据等
 - 分析广告的表现指标，如观看量、点赞数、评论数等核心数据
 - 帮助广告主和营销人员深入了解特定广告的效果和用户反馈
  ### 参数:
 - ads_id: 广告ID，必填参数，可从广告列表或TikTok Ads Creative Center获取
  ### 返回内容说明:
 - `ad_title`: 广告标题
 - `brand_name`: 品牌名称
 - `comment`: 评论数
 - `cost`: 花费等级(1-5)
 - `country_code`: 投放国家代码列表
 - `ctr`: 点击率（百分比）
 - `favorite`: 是否收藏
 - `has_summary`: 是否有摘要
 - `highlight_text`: 高亮文本
 - `id`: 广告ID
 - `industry_key`: 行业标签
 - `is_search`: 是否搜索结果
 - `keyword_list`: 关键词列表
 - `landing_page`: 落地页URL
 - `like`: 点赞数
 - `objective_key`: 广告目标键
 - `objectives`: 广告目标列表
  - `label`: 目标标签
  - `value`: 目标值
- `pattern_label`: 模式标签列表
 - `share`: 分享数
 - `source`: 来源
 - `source_key`: 来源键值
 - `tag`: 标签
 - `video_info`: 视频信息
  - `vid`: 视频ID
  - `duration`: 时长（秒）
  - `cover`: 封面图URL
  - `video_url`: 视频播放地址
    - `720p`: 720p质量视频URL
  - `width`: 视频宽度
  - `height`: 视频高度
- `voice_over`: 是否有配音
  ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_ads_detail",
  "params": {
    "ads_id": "7131673574381518849"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "ad_title": "BLACK FRIDAY SALE at 50% OFF + FREE SHIPPING",
      "brand_name": "The Bamboo Breeze Shop",
      "comment": 232,
      "cost": 2,
      "country_code": ["US", "CA", "PH", "SE", "FI"],
      "ctr": 0.14,
      "favorite": false,
      "has_summary": true,
      "highlight_text": "",
      "id": "7131673574381518849",
      "industry_key": "label_29100000000",
      "is_search": false,
      "keyword_list": [
        "adjustable back posture corrector",
        "poor posture",
        "eliminate unnecessary back pain"
      ],
      "landing_page": "https://thebamboobreezeshop.com/products/adjustable-back-shoulder-posture-corrector",
      "like": 61242,
      "objective_key": "campaign_objective_conversion",
      "objectives": [
        {
          "label": "campaign_objective_conversion",
          "value": 3
        },
        {
          "label": "campaign_objective_product_sales",
          "value": 15
        }
      ],
      "pattern_label": [],
      "share": 6486,
      "source": "TikTok Ads Manager",
      "source_key": 1,
      "tag": 3,
      "video_info": {
        "vid": "v12025gd0000cuavia7og65o5g7ucnb0",
        "duration": 17,
        "cover": "https://p16-sign-va.tiktokcdn.com/xxx",
        "video_url": {
          "720p": "https://v16m-default.tiktokcdn.com/xxx"
        },
        "width": 576,
        "height": 1024
      },
      "voice_over": true
    }
  }
}
 ```

## get_all_aweme_id

`POST /api/v1/tiktok/web/get_all_aweme_id`

<!-- Full path: /api/v1/tiktok/web/get_all_aweme_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取列表作品id
### 参数:
- url: 作品链接 (最多支持20个链接)
### 返回:
- 作品id

## get_all_sec_user_id

`POST /api/v1/tiktok/web/get_all_sec_user_id`

<!-- Full path: /api/v1/tiktok/web/get_all_sec_user_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 提取列表用户id
 ### 参数:
 - url: 用户主页链接（最多支持10个链接）、
 ### 返回:

如果链接成功获取到sec_user_id，则返回sec_user_id，否则返回原始的输入链接，后续可以手动校验链接无法获取sec_user_id的原因。

## get_all_unique_id

`POST /api/v1/tiktok/web/get_all_unique_id`

<!-- Full path: /api/v1/tiktok/web/get_all_unique_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取列表unique_id
### 参数:
- url: 用户主页链接 (最多支持20个链接)
### 返回:
- unique_id

## get_aweme_id

`GET /api/v1/tiktok/web/get_aweme_id`

<!-- Full path: /api/v1/tiktok/web/get_aweme_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 作品链接/Video link | https://www.tiktok.com/@owlcitymusic/video/7218694761253735723 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取单个作品id
### 参数:
- url: 作品链接
### 返回:
- 作品id

## get_creator_list

`GET /api/v1/tiktok/ads/get_creator_list`

<!-- Full path: /api/v1/tiktok/ads/get_creator_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| sort_by | string |  | 排序方式/Sort by (follower, engagement, avg_views) (default: follower) |  |
| creator_country | string |  | 创作者国家/Creator country (default: US) |  |
| audience_country | string |  | 受众国家/Audience country (default: '') |  |
| audience_count | integer |  | 受众数量筛选/Audience count filter (default: 0) |  |
| keyword | string |  | 关键词/Keyword |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取符合条件的创作者列表，包括粉丝数、互动率等数据
 - 发现高质量的广告合作创作者
 - 分析不同类型创作者的表现和特点
  ### 参数:
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - sort_by: 排序方式
  - follower: 按粉丝数排序
  - engagement: 按互动率排序
  - avg_views: 按平均观看量排序
- creator_country: 创作者所在国家
 - audience_country: 受众所在国家（可选）
 - audience_count: 受众数量筛选（可选）
  ### 返回内容说明:
 - `creators`: 创作者列表
  - `tcm_id`: TCM ID
  - `user_id`: 用户ID
  - `nick_name`: 昵称
  - `avatar_url`: 头像URL
  - `country_code`: 国家代码
  - `follower_cnt`: 粉丝数
  - `liked_cnt`: 获赞总数
  - `tt_link`: TikTok链接
  - `tcm_link`: TCM链接
  - `items`: 作品列表
    - `item_id`: 作品ID
    - `cover_url`: 封面URL
    - `tt_link`: TikTok链接
    - `vv`: 观看量
    - `liked_cnt`: 点赞数
    - `create_time`: 创建时间
- `pagination`: 分页信息
  - `page`: 当前页
  - `size`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_creator_list",
  "params": {
    "page": "1",
    "limit": "20",
    "sort_by": "follower",
    "creator_country": "US",
    "audience_country": "",
    "audience_count": "0"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "creators": [
        {
          "tcm_id": "7414477993612935173",
          "user_id": "62133858422239232",
          "nick_name": "Fernanda",
          "avatar_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/200b649d30f76f1238d771f4aff51ee1~tplv-tiktokx-cropcenter:100:100.png",
          "country_code": "US",
          "follower_cnt": 9135515,
          "liked_cnt": 668294555,
          "tt_link": "https://www.tiktok.com/@ferchugimenez",
          "tcm_link": "https://creatormarketplace.tiktok.com/ad#/author/7414477993612935173",
          "items": [
            {
              "item_id": "7444674312784645432",
              "cover_url": "https://p16-sign-va.tiktokcdn.com/tos-maliva-p-0068/oQIBhn2EeBMUWQR5wVQACFEBtlDxgUDdAfoB8J~tplv-noop.image",
              "tt_link": "https://www.tiktok.com/@author/video/7444674312784645432",
              "vv": 13733332,
              "liked_cnt": 516217,
              "create_time": 1733348322
            }
          ]
        }
      ],
      "pagination": {
        "page": 1,
        "size": 20,
        "total": 459,
        "has_more": true
      }
    }
  }
}
 ```

## get_hashtag_list

`GET /api/v1/tiktok/ads/get_hashtag_list`

<!-- Full path: /api/v1/tiktok/ads/get_hashtag_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| period | integer |  | 时间范围（天）/Time period (days) (default: 120) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| sort_by | string |  | 排序方式/Sort by (popular, new) (default: popular) |  |
| industry_id | string |  | 行业ID/Industry ID (default: '') |  |
| filter_by | string |  | 筛选条件/Filter (new_on_board) (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok广告中的热门标签排行榜，了解当前流行的话题标签
 - 分析标签的使用量、观看量等数据，发现潜力标签
 - 帮助广告主选择合适的标签，提升广告曝光和互动率
  ### 参数:
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - period: 时间范围（天），如7、30、120天
 - country_code: 国家代码，如US、UK、JP等
 - sort_by: 排序方式，"popular"=热门，"new"=最新
 - industry_id: 行业ID，留空返回所有行业
 - filter_by: 筛选条件，"new_on_board"=新上榜标签
  ### 返回内容说明:
 - `list`: 标签列表
  - `hashtag_id`: 标签ID
  - `hashtag_name`: 标签名称
  - `country_info`: 国家信息
    - `id`: 国家ID
    - `value`: 国家名称
    - `label`: 国家标签
  - `industry_info`: 行业信息
    - `id`: 行业ID
    - `value`: 行业名称
    - `label`: 行业标签
  - `is_promoted`: 是否推广
  - `trend`: 趋势数据列表
    - `time`: 时间戳
    - `value`: 该时间点的值
  - `creators`: 创作者列表
    - `nick_name`: 昵称
    - `avatar_url`: 头像URL
  - `publish_cnt`: 发布数量
  - `video_views`: 视频观看量
  - `rank`: 排名
  - `rank_diff`: 排名变化
  - `rank_diff_type`: 排名变化类型
- `pagination`: 分页信息
  - `page`: 当前页
  - `size`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_hashtag_list",
  "params": {
    "page": "1",
    "limit": "20",
    "period": "120",
    "country_code": "US",
    "sort_by": "popular",
    "industry_id": "",
    "filter_by": ""
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "list": [
        {
          "hashtag_id": "4100",
          "hashtag_name": "summer",
          "country_info": {
            "id": "US",
            "value": "United States",
            "label": "US"
          },
          "industry_info": {
            "id": 28000000000,
            "value": "Sports & Outdoor",
            "label": "label_28000000000"
          },
          "is_promoted": false,
          "trend": [
            {
              "time": 1740787200,
              "value": 0.38
            },
            {
              "time": 1741392000,
              "value": 0.37
            },
            {
              "time": 1741996800,
              "value": 0.43
            },
            {
              "time": 1749254400,
              "value": 1
            }
          ],
          "creators": [
            {
              "nick_name": "Mark Broze",
              "avatar_url": "https://p16-sign-sg.tiktokcdn.com/tos-alisg-avt-0068/28bb3ad309c2165f9579a67515d17ca9~tplv-tiktokx-cropcenter:100:100.png"
            },
            {
              "nick_name": "Liam 🤠",
              "avatar_url": "https://p16-sign-sg.tiktokcdn.com/tos-alisg-avt-0068/a27b40671c78f8af17cdd2618ad8ba20~tplv-tiktokx-cropcenter:100:100.png"
            }
          ],
          "publish_cnt": 2886791,
          "video_views": 19583705445,
          "rank": 1,
          "rank_diff": 1,
          "rank_diff_type": 1
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

## get_keyword_details

`GET /api/v1/tiktok/ads/get_keyword_details`

<!-- Full path: /api/v1/tiktok/ads/get_keyword_details -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 关键词（可选）/Keyword (optional) (default: '') |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| period | integer |  | 时间范围（天）/Time period (days) (default: 7) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| order_by | string |  | 排序字段/Sort field (default: post) |  |
| order_type | string |  | 排序方式/Sort order (desc, asc) (default: desc) |  |
| industry | string |  | 行业ID/Industry ID |  |
| objective | string |  | 广告目标/Ad objective |  |
| keyword_type | string |  | 关键词类型/Keyword type |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定关键词的详细数据，包括发布量、示例视频等
 - 不提供关键词时，返回热门关键词排名列表
 - 深入分析关键词的使用情况和效果
  ### 参数:
 - keyword: 关键词，可选。不提供时返回排名列表
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - period: 时间范围（天），如7、30天
 - country_code: 国家代码，如US、UK、JP等
 - order_by: 排序字段，如"post"（发布量）
 - order_type: 排序方式，desc（降序）或asc（升序）
  ### 返回内容说明:
 - `keyword_list`: 关键词详情列表
  - `comment`: 评论数
  - `cost`: 花费金额
  - `cpa`: 每次转化成本
  - `ctr`: 点击率
  - `cvr`: 转化率
  - `impression`: 展示量
  - `keyword`: 关键词文本
  - `like`: 点赞数
  - `play_six_rate`: 6秒播放率
  - `post`: 发布量
  - `post_change`: 发布量变化率
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
  "router": "/api/v1/tiktok/ads/get_keyword_details",
  "params": {
    "keyword": "",
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
            "7512164952346529031"
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

## get_keyword_list

`GET /api/v1/tiktok/ads/get_keyword_list`

<!-- Full path: /api/v1/tiktok/ads/get_keyword_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string |  | 关键词/Keyword (default: cat toy) |  |
| period | integer |  | 时间范围（天）/Time period (days) (default: 120) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 6) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| industry | string |  | 行业ID列表，逗号分隔/Industry IDs, comma separated (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定关键词的广告投放数据，了解关键词在TikTok广告中的使用情况
 - 分析关键词的发布量趋势、相关视频等信息
 - 帮助广告主发现有效的广告关键词
  ### 参数:
 - keyword: 搜索关键词，必填参数
 - period: 时间范围（天），如7、30、120天
 - page: 页码，默认1
 - limit: 每页数量，默认6
 - country_code: 国家代码，如US、UK、JP等
 - industry: 行业ID列表，多个ID用逗号分隔
  ### 返回内容说明:
 - `keyword_info_list`: 关键词信息列表
  - `keyword`: 关键词文本
  - `post`: 使用该关键词的广告发布数量
  - `video_list`: 使用该关键词的示例视频ID列表
- `pagination`: 分页信息
  ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_keyword_list",
  "params": {
    "keyword": "cat toy",
    "period": 120,
    "page": 1,
    "limit": 6
  },
  "data": {
    "keyword_info_list": [
      {
        "keyword": "cat toy",
        "post": 12345,
        "video_list": ["7213258221116751874", "7213258221116751875"]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 6,
      "total": 50,
      "has_more": true
    }
  }
}
 ```

## get_live_room_id

`GET /api/v1/tiktok/web/get_live_room_id`

<!-- Full path: /api/v1/tiktok/web/get_live_room_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| live_room_url | string | ✅ | 直播间链接/Live room link | https://www.tiktok.com/@maksukaracun/live |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 根据直播间链接提取直播间Room ID
- 支持短链接，如：https://vt.tiktok.com/ZSjuyJnWQ/
- 支持长链接，如：https://www.tiktok.com/@maksukaracun/live
### 参数:
- live_room_url: 直播间链接
### 返回:
- 直播间Room ID

## get_popular_trends

`GET /api/v1/tiktok/ads/get_popular_trends`

<!-- Full path: /api/v1/tiktok/ads/get_popular_trends -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| period | integer |  | 时间范围（天）/Time period (days) (default: 7) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 10) |  |
| order_by | string |  | 排序字段/Order by (vv, like, comment, repost) (default: vv) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定时间段内的流行趋势视频
- 了解当前热门内容的特点和趋势
- 为广告创意提供灵感和参考
 ### 参数:
- period: 时间范围（天），如7、30天
- page: 页码，默认1
- limit: 每页数量，默认10
- order_by: 排序字段
  - vv: 按观看量排序
  - like: 按点赞数排序
  - comment: 按评论数排序
  - repost: 按转发数排序
- country_code: 国家代码
 ### 返回内容说明:
- `pagination`: 分页信息
  - `has_more`: 是否有更多
  - `limit`: 每页数量
  - `page`: 当前页
  - `total_count`: 总数量
- `videos`: 趋势视频列表
  - `country_code`: 国家代码
  - `cover`: 封面图URL
  - `duration`: 时长（秒）
  - `id`: 视频ID
  - `item_id`: 视频项目ID
  - `item_url`: 视频链接
  - `region`: 地区
  - `title`: 视频标题
 ### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_popular_trends",
  "params": {
    "period": "7",
    "page": "1",
    "limit": "10",
    "order_by": "vv",
    "country_code": "US"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "pagination": {
        "has_more": true,
        "limit": 10,
        "page": 1,
        "total_count": 500
      },
      "videos": [
        {
          "country_code": "US",
          "cover": "https://p16-sign-va.tiktokcdn.com/tos-maliva-p-0068c799-us/osAmHI2QkEfCyjJI57DfCFPhVDQJqnImEusfHA~tplv-noop.image",
          "duration": 15,
          "id": "7512918118663081262",
          "item_id": "7512918118663081262",
          "item_url": "https://www.tiktok.com/@mnm_pipi/video/7512918118663081262",
          "region": "United States",
          "title": "We've lowered MSRP on Rogue and Pathfinder, because Nissan is here for you."
        },
        {
          "country_code": "US",
          "cover": "https://p16-sign-va.tiktokcdn.com/tos-maliva-p-0068c799-us/ocQjW3QOfqt0seM0CA8gWfAqC5I2BO1LIkjQUI~tplv-noop.image",
          "duration": 15,
          "id": "7514018454932835615",
          "item_id": "7514018454932835615",
          "item_url": "https://www.tiktok.com/@mnm_pipi/video/7514018454932835615",
          "region": "United States",
          "title": "Wanna see something gorgeous? Apple's new look is coming soon. Learn more at www.apple.com/os/. #LiquidGlass #WWDC25 #Apple #iOS26 #macOS26"
        }
      ]
    }
  }
}
```

## get_product_analytics_list

`POST /api/v1/tiktok/creator/get_product_analytics_list`

<!-- Full path: /api/v1/tiktok/creator/get_product_analytics_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号在指定时间范围内推广的商品列表及其销售数据分析。
 - 支持按商品成交额、商品上架时间排序，可分页查询。
  ### 返回内容说明:
 - `segments`（分段数据列表）:
  - `filter.creator_id`: 创作者账号 ID
  - `list_control`:
    - `rules`: 列表排序规则（如按成交额、商品 ID 排序）
    - `next_pagination`: 翻页信息（是否还有更多页、下一页页码、总页数、总记录数）
  - `timed_lists`: 每个时间段内的商品数据，包括：
    - `product`:
      - `id`: 商品 ID
      - `name`: 商品标题
      - `cover_image.thumb_url_list`: 商品封面图列表
    - `item_sold_cnt`: 销售商品数量
    - `revenue.amount`: 该商品带来的总成交金额（GMV）
    - `commission.amount`: 该商品预估佣金收入
 ### 备注:
 - 此接口仅适用于 TikTok Shop 创作者账号。
 - 数据以自然月或自定义时间范围统计。
 - 默认排序为成交额（GMV）从高到低。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 开始日期，格式为 'YYYY-MM-DD'，如 '2025-04-01'
 - end_date: 结束日期，格式为 'YYYY-MM-DD'，如 '2025-05-01'
 - page: 页码，默认为第一页 `0`
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - 创作者账号商品列表及商品销售分析数据

## get_product_detail

`GET /api/v1/tiktok/ads/get_product_detail`

<!-- Full path: /api/v1/tiktok/ads/get_product_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string | ✅ | 产品类目ID/Product category ID | 601583 |
| last | integer |  | 最近天数/Last days (default: 30) |  |
| ecom_type | string |  | 电商类型/E-commerce type (default: l3) |  |
| period_type | string |  | 时间类型/Period type (default: last) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定产品类目的完整详细信息
 - 包括受众分析、热门标签、相关帖子等多维度数据
 - 为产品营销策略提供全面的数据支持
  ### 参数:
 - id: 产品类目ID，如香水：601583
 - last: 最近天数，如7、30天
 - ecom_type: 电商类型，默认"l3"
 - period_type: 时间类型，默认"last"
  ### 返回内容说明:
 - `info`: 产品详细信息
  - `audience_ages`: 受众年龄分布
    - `age_level`: 年龄数值
    - `score`: 占比分数
  - `audience_interests`: 受众兴趣分布
    - `interest_info`: 兴趣信息
      - `id`: 兴趣ID
      - `label`: 兴趣标签
      - `value`: 兴趣名称
    - `score`: 占比分数
  - `cover_url`: 封面图URL（可能为null）
  - `ecom_type`: 电商类型
  - `first_ecom_category`: 一级电商类目
    - `id`: 类目ID
    - `label`: 类目标签
    - `value`: 类目名称
  - `hashtags`: 热门标签列表
  - `posts`: 相关帖子列表
  - `second_ecom_category`: 二级电商类目
  - `third_ecom_category`: 三级电商类目
  - `url_title`: URL标题
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_product_detail",
  "params": {
    "id": "601583",
    "last": "30",
    "ecom_type": "l3",
    "period_type": "last"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "info": {
        "audience_ages": [
          {
            "age_level": 35,
            "score": 27
          },
          {
            "age_level": 25,
            "score": 22
          },
          {
            "age_level": 18,
            "score": 22
          },
          {
            "age_level": 45,
            "score": 18
          },
          {
            "age_level": 55,
            "score": 11
          }
        ],
        "audience_interests": [
          {
            "interest_info": {
              "id": "13105000000",
              "label": "label_13105000000",
              "value": "Pawn Shops"
            },
            "score": 135
          },
          {
            "interest_info": {
              "id": "24104000000",
              "label": "label_24104000000",
              "value": "Electronics & Electrical"
            },
            "score": 127
          }
        ],
        "cover_url": null,
        "ecom_type": "l3",
        "first_ecom_category": {
          "id": "601450",
          "label": "category_601450",
          "value": "Beauty & Personal Care"
        },
        "hashtags": [
          "vlog",
          "perfumetiktok",
          "perfume",
          "fragrance",
          "fragrancetiktok"
        ],
        "posts": [
          "7436474042036522248",
          "7486253493716536584",
          "7503974461725740295"
        ],
        "url_title": "Perfume"
      }
    }
  }
}
 ```

## get_product_related_videos

`POST /api/v1/tiktok/creator/get_product_related_videos`

<!-- Full path: /api/v1/tiktok/creator/get_product_related_videos -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取与指定商品关联的所有视频列表和对应的互动数据（如点赞数、评论数、分享数）。
 - 可用于分析同款商品在不同创作者视频中的推广效果和差异。
 - 支持按时间筛选，默认查询指定 start_date 所在自然月内的数据。
  ### 备注:
 - 必须同时提供 item_id（当前视频 ID）和 product_id（商品 ID）。
 - 返回数据按时间范围查询，同一商品下的其他视频列表。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询起始日期，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - item_id: 当前视频 ID，例如 "7496499484705246507"
 - product_id: 商品 ID，例如 "1731050202505515549"
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回内容说明:
 - `segments`（数据分段列表）:
  - `time_selector`: 时间筛选参数（period, granularity, start_timestamp, end_timestamp）
  - `filter`: 查询条件（creator_id, product_id, item_id）
  - `timed_lists`: 视频列表
    - `start_timestamp`: 开始时间戳
    - `end_timestamp`: 结束时间戳
    - `stats`:
      - `video_product_id`: 商品 ID
      - `video`:
        - `item_id`: 视频 ID
        - `video_id`: 视频内部唯一 ID
        - `name`: 视频文案标题
        - `publish_time`: 发布时间戳
        - `duration`: 视频时长（秒）
        - `video_play_info`:
          - `post_url`: 视频封面图片链接
          - `video_infos.main_url`: 视频播放地址
      - `video_like_cnt`: 视频点赞数
      - `video_comment_cnt`: 视频评论数
      - `video_share_cnt`: 视频分享数
 ### 示例请求体:
 ```json
 {
  "cookie": "your_cookie",
  "start_date": "04-01-2025",
  "item_id": "7496499484705246507",
  "product_id": "1731050202505515549"
}
 ```

## get_recommended_ads

`GET /api/v1/tiktok/ads/get_recommended_ads`

<!-- Full path: /api/v1/tiktok/ads/get_recommended_ads -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| material_id | string | ✅ | 广告素材ID/Ad material ID | 7213258221116751874 |
| industry | string |  | 行业ID/Industry ID (default: '25308000000') |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 基于指定广告获取相似的推荐广告列表
 - 发现同行业或相似风格的优秀广告案例
 - 为广告创意提供更多参考和灵感
  ### 参数:
 - material_id: 参考广告素材ID，必填参数
 - industry: 行业ID，如游戏行业：25308000000
 - country_code: 国家代码，如US、UK、JP等
  ### 返回内容说明:
 - `materials`: 推荐广告素材列表
  - `ad_title`: 广告标题
  - `brand_name`: 品牌名称
  - `cost`: 花费等级
  - `ctr`: 点击率
  - `favorite`: 是否收藏
  - `id`: 广告ID
  - `industry_key`: 行业键值
  - `is_search`: 是否搜索结果
  - `like`: 点赞数
  - `objective_key`: 广告目标键值
  - `tag`: 标签
  - `video_info`: 视频信息
    - `vid`: 视频ID
    - `duration`: 时长（秒）
    - `cover`: 封面图URL
    - `video_url`: 视频播放地址
      - `360p`: 360p画质
      - `480p`: 480p画质
      - `540p`: 540p画质
      - `720p`: 720p画质
    - `width`: 视频宽度
    - `height`: 视频高度
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_recommended_ads",
  "params": {
    "material_id": "7213258221116751874",
    "industry": "25308000000",
    "country_code": "US"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "materials": [
        {
          "ad_title": "What will you decide?",
          "brand_name": "Eatventure",
          "cost": 2,
          "ctr": 0.07,
          "favorite": false,
          "id": "7164756134804979714",
          "industry_key": "label_25308000000",
          "is_search": false,
          "like": 1009024,
          "objective_key": "campaign_objective_conversion",
          "tag": 3,
          "video_info": {
            "vid": "v10033g50000ctgjtl7og65ivnpdo87g",
            "duration": 30.016,
            "cover": "https://p16-sign-sg.tiktokcdn.com/v0201/ogKcNlWrjIQwDVBDpBbeR7PDQXnAIeA9Dgbb4w~tplv-noop.image",
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
      ]
    }
  }
}
 ```

## get_sec_user_id

`GET /api/v1/tiktok/web/get_sec_user_id`

<!-- Full path: /api/v1/tiktok/web/get_sec_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 用户主页链接/User homepage link | https://www.tiktok.com/@tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取列表用户id
### 参数:
- url: 用户主页链接
### 返回:
- 用户id

## get_showcase_product_list

`POST /api/v1/tiktok/creator/get_showcase_product_list`

<!-- Full path: /api/v1/tiktok/creator/get_showcase_product_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号橱窗中正在展示的商品列表。
 - 可用于商品管理、数据分析、查看当前推广商品等场景。
  ### 备注:
 - 仅适用于已开通橱窗功能的 TikTok Shop 创作者账号。
 - 支持分页查询，通过 `count` 和 `offset` 控制数据量。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - count: 每页返回商品数量，默认 20
 - offset: 分页偏移量，默认 0
 - proxy: 可选 HTTP 代理地址
    - 示例: `http://username:password@host:port`
 ### 返回内容说明:
 - `products` (List[Dict]): 商品列表，每项包含以下字段：
  - `product_id` (str): 商品ID
  - `title` (str): 商品标题
  - `format_available_price` (str): 商品展示价格（格式化后的字符串，如 `$7.94`）
  - `seller_info` (dict):
    - `seller_id` (str): 卖家ID
    - `shop_name` (str): 店铺名称
  - `cover` (dict): 主图信息
    - `url_list` (List[str]): 主图 URL 列表（300x300）
  - `images` (List[dict]): 图片列表
    - 每张图片包含 `url_list` (原图 URL)
  - `source` (str): 商品来源渠道（如 `Affiliate`）
  - `stock_status` (int): 库存状态（1: 有货）
  - `review_status` (int): 审核状态（1: 通过）
  - `affiliate_info` (dict): 联盟佣金信息
    - `commission_with_currency` (str): 佣金金额（如 `$0.95`）
    - `commission_rate` (int): 佣金比例（如 1200 = 12%）
  - `category_info` (dict): 类目信息
    - `name` (str): 主分类名（如 `Beauty & Personal Care`）
 ### 示例请求体:
 ```json
 {
  "cookie": "your_cookie_string",
  "count": 20,
  "offset": 0
}
 ```
  ### 示例返回数据片段:
 ```json
 {
  "products": [
    {
      "product_id": "1730905148396180014",
      "title": "Car Paint Care Spray",
      "format_available_price": "$7.94",
      "seller_info": {
        "seller_id": "7496108716782225966",
        "shop_name": "moon moon shop shop"
      },
      "cover": {
        "url_list": [
          "https://example.com/xxx.jpg"
        ]
      },
      "images": [
        {
          "url_list": [
            "https://example.com/xxx.jpg"
          ]
        }
      ],
      "source": "Affiliate",
      "stock_status": 1,
      "review_status": 1,
      "affiliate_info": {
        "commission_with_currency": "$0.95",
        "commission_rate": 1200
      },
      "category_info": {
        "name": "Beauty & Personal Care"
      }
    }
  ]
}
 ```

## get_sound_detail

`GET /api/v1/tiktok/ads/get_sound_detail`

<!-- Full path: /api/v1/tiktok/ads/get_sound_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| clip_id | string | ✅ | 音乐ID/Sound clip ID | 7251810329461147649 |
| period | integer |  | 时间范围（天）/Time period (days) (default: 120) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取特定音乐的详细信息和使用数据
 - 分析音乐的受众分布、使用趋势等多维度数据
 - 帮助选择合适的背景音乐提升广告效果
  ### 参数:
 - clip_id: 音乐ID，必填参数
 - period: 时间范围（天），如7、30、120天
 - country_code: 国家代码，如US、UK、JP等
  ### 返回内容说明:
 - `disliked`: 是否不喜欢（可能为null）
 - `like_count`: 点赞数（可能为null）
 - `liked`: 是否点赞（可能为null）
 - `sound`: 音乐详细信息
  - `audience_ages`: 受众年龄分布
    - `age_level`: 年龄级别
    - `score`: 分数
  - `audience_countries`: 受众国家分布
    - `country_info`: 国家信息
      - `id`: 国家ID
      - `label`: 国家标签
      - `value`: 国家名称
    - `score`: 分数
  - `audience_interests`: 受众兴趣分布
    - `interest_info`: 兴趣信息
    - `score`: 分数
  - `author`: 音乐作者
  - `clip_id`: 片段ID
  - `country_code`: 国家代码
  - `cover`: 封面图URL
  - `duration`: 时长（秒）
  - `if_cml`: 是否商业音乐
  - `is_search`: 是否搜索结果
  - `link`: 音乐链接
  - `longevity`: 持久度信息
    - `popular_days`: 流行天数
    - `current_popularity`: 当前流行度
  - `music_url`: 音乐播放URL（可能为null）
  - `on_list_times`: 上榜次数（可能为null）
  - `promoted`: 是否推广
  - `rank`: 排名（可能为null）
  - `rank_diff`: 排名变化（可能为null）
  - `related_items`: 相关视频列表
    - `item_id`: 视频ID
    - `cover_uri`: 封面URI
  - `song_id`: 歌曲ID
  - `title`: 音乐标题
  - `trend`: 趋势数据
    - `time`: 时间戳
    - `value`: 数值
  - `url_title`: URL标题
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_sound_detail",
  "params": {
    "clip_id": "7251810329461147649",
    "period": 120,
    "country_code": "US"
  },
  "data": {
    "sound": {
      "title": "Upbeat Summer Vibes",
      "author": "Music Producer",
      "duration": 30,
      "music_url": "https://music.tiktok.com/xxx",
      "cover_url": "https://p16-sign-sg.tiktokcdn.com/xxx",
      "audience_ages": [
        {"age_level": "18-24", "percentage": 45.2},
        {"age_level": "25-34", "percentage": 32.8}
      ],
      "audience_countries": [
        {"country": "US", "percentage": 35.6},
        {"country": "UK", "percentage": 18.4}
      ],
      "related_items": ["7213258221116751874", "7213258221116751875"],
      "usage_trend": [
        {"date": "2025-01-01", "count": 1234},
        {"date": "2025-01-02", "count": 1456}
      ]
    }
  }
}
 ```

## get_sound_rank_list

`GET /api/v1/tiktok/ads/get_sound_rank_list`

<!-- Full path: /api/v1/tiktok/ads/get_sound_rank_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| period | integer |  | 时间范围（天）/Time period (days) (default: 30) |  |
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
 - 获取TikTok广告中的热门音乐排行榜，了解当前流行的音乐素材
 - 分析音乐的使用量、增长趋势等数据，发现潜力音乐
 - 帮助广告主选择合适的背景音乐，提升广告吸引力和传播效果
  ### 参数:
 - period: 时间范围（天），如7、30、120天
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - rank_type: 排行类型，"popular"=热门，"surging"=上升最快
 - new_on_board: 是否只看新上榜音乐，默认False
 - commercial_music: 是否只看商业音乐，默认False
 - country_code: 国家代码，如US、UK、JP等
  ### 返回内容说明:
 - `pagination`: 分页信息
  - `page`: 当前页
  - `size`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
- `sound_list`: 音乐列表
  - `author`: 音乐作者
  - `clip_id`: 片段ID
  - `cml_mid`: 商业音乐ID
  - `country_code`: 国家代码
  - `cover`: 封面图URL
  - `duration`: 时长（秒）
  - `if_cml`: 是否商业音乐
  - `is_search`: 是否搜索结果
  - `link`: 音乐链接
  - `music_url`: 音乐播放URL
  - `on_list_times`: 上榜次数（可能为null）
  - `promoted`: 是否推广
  - `rank`: 排名
  - `rank_diff`: 排名变化
  - `rank_diff_type`: 排名变化类型
  - `related_items`: 相关视频列表
    - `item_id`: 视频ID
    - `cover_uri`: 封面URI
  - `song_id`: 歌曲ID
  - `title`: 音乐标题
  - `trend`: 趋势数据
    - `time`: 时间戳
    - `value`: 该时间点的值
  - `url_title`: URL标题
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_sound_rank_list",
  "params": {
    "period": "30",
    "page": "1",
    "limit": "20",
    "rank_type": "popular",
    "new_on_board": "false",
    "commercial_music": "false",
    "country_code": "US"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "pagination": {
        "page": 1,
        "size": 20,
        "total": 99,
        "has_more": true
      },
      "sound_list": [
        {
          "author": "CYRIL & MOONLGHT & The La's",
          "clip_id": "7424014547218565904",
          "cml_mid": "7512350022513852432",
          "country_code": "US",
          "cover": "https://p16-sg.tiktokcdn.com/aweme/720x720/tos-alisg-v-2774/osxQt9H6AFAPAzveAQL4SQgGreoyVe6IDaCCXQ.jpeg",
          "duration": 22,
          "if_cml": true,
          "is_search": false,
          "link": "https://www.tiktok.com/music/x-7424014547218565904",
          "music_url": "https://sf16-ies-music-sg.tiktokcdn.com/obj/tos-alisg-ve-2774/o0W7XTIwoABiiicgwksz8EfQKFBPAA1M4Oq0kj",
          "on_list_times": null,
          "promoted": false,
          "rank": 1,
          "rank_diff": 0,
          "rank_diff_type": 2,
          "related_items": [
            {
              "item_id": 7512619474084711723,
              "cover_uri": "https://p16-sign-va.tiktokcdn.com/tos-maliva-p-0068c799-us/osLDIJAZvBbnB4E0gCiaBbHnigExB8CUIGvI4~tplv-noop.image"
            }
          ],
          "song_id": "7503950818010335233",
          "title": "There She Goes",
          "trend": [
            {
              "time": 1740787200,
              "value": 0.15
            }
          ],
          "url_title": "There She Goes (CYRIL Remix)"
        }
      ]
    }
  }
}
 ```

## get_sound_recommendations

`GET /api/v1/tiktok/ads/get_sound_recommendations`

<!-- Full path: /api/v1/tiktok/ads/get_sound_recommendations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| clip_id | string | ✅ | 参考音乐ID/Reference sound clip ID | 7156826385225353217 |
| limit | integer |  | 推荐数量/Number of recommendations (default: 6) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 基于指定音乐获取相似的推荐音乐
- 发现风格相近或使用场景类似的音乐
- 扩展音乐选择范围，找到更多合适的配乐
### 参数:
- clip_id: 参考音乐ID，必填参数
- limit: 推荐数量，默认6
### 返回内容说明:
- `musics`: 推荐音乐列表
  - `author`: 音乐作者
  - `cover`: 封面图URL
  - `music_id`: 音乐ID
  - `music_url`: 音乐播放URL
  - `title`: 音乐标题
### 示例响应:
```json
{
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_sound_recommendations",
  "params": {
    "clip_id": "7156826385225353217",
    "limit": "6"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "musics": [
        {
          "author": "zomap",
          "cover": "https://p16-sg-default.akamaized.net/aweme/720x720/tiktok-obj/6f9903752958820d144fa90d54cb5f3a.png.jpeg",
          "music_id": "6949146013727653889",
          "music_url": "https://sf16-sg-default.akamaized.net/obj/tiktok-obj/d0d0dca4400886718099898494b7e31b.mp3",
          "title": "Relaxed and gentle fashionable chillout(810161)"
        },
        {
          "author": "zomap",
          "cover": "https://p16-sg-default.akamaized.net/aweme/720x720/tiktok-obj/6f9903752958820d144fa90d54cb5f3a.png.jpeg",
          "music_id": "6949294080044843010",
          "music_url": "https://sf16-sg-default.akamaized.net/obj/tiktok-obj/451acbadd83a76748a99878ccfef2df5.mp3",
          "title": "Relaxed and gentle fashionable chillout(816672)"
        }
      ]
    }
  }
}
```

## get_top_products

`GET /api/v1/tiktok/ads/get_top_products`

<!-- Full path: /api/v1/tiktok/ads/get_top_products -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| last | integer |  | 最近天数/Last days (default: 7) |  |
| page | integer |  | 页码/Page number (default: 1) |  |
| limit | integer |  | 每页数量/Items per page (default: 20) |  |
| country_code | string |  | 国家代码/Country code (default: US) |  |
| first_ecom_category_id | string |  | 电商类目ID，多个用逗号分隔/E-commerce category IDs, comma separated (default: '') |  |
| ecom_type | string |  | 电商类型/E-commerce type (l3) (default: l3) |  |
| period_type | string |  | 时间类型/Period type (last) (default: last) |  |
| order_by | string |  | 排序字段/Sort field (post, ctr, cvr) (default: post) |  |
| order_type | string |  | 排序方式/Sort order (desc, asc) (default: desc) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取TikTok广告中的热门产品排行榜，了解各类目下的爆款产品
 - 分析产品的广告投放量、点击率、转化率等核心指标
 - 帮助电商卖家发现潜力产品，优化选品和营销策略
  ### 参数:
 - last: 最近天数，如7、30天
 - page: 页码，默认1
 - limit: 每页数量，默认20
 - country_code: 国家代码，如US、UK、JP等
 - first_ecom_category_id: 电商类目ID，多个用逗号分隔
 - ecom_type: 电商类型，默认"l3"
 - period_type: 时间类型，默认"last"
 - order_by: 排序字段，可选：post（发布量）、ctr（点击率）、cvr（转化率）
 - order_type: 排序方式，desc（降序）或asc（升序）
  ### 常用电商类目ID:
 - 美妆个护: 605196
 - 女装女内衣: 602284
 - 时尚配饰: 601450
 - 手机电子: 801928
 - 健康产品: 951432
 - 家居用品: 601755
 - 男装男内衣: 605248
 - 香水: 601583
  ### 返回内容说明:
 - `list`: 产品列表
  - `comment`: 评论数
  - `cost`: 花费金额
  - `cover_url`: 封面图URL（可能为null）
  - `cpa`: 每次转化成本
  - `ctr`: 点击率（百分比）
  - `cvr`: 转化率（百分比）
  - `ecom_type`: 电商类型
  - `first_ecom_category`: 一级电商类目
    - `id`: 类目ID
    - `label`: 类目标签
    - `value`: 类目名称
  - `impression`: 展示量
  - `like`: 点赞数
  - `play_six_rate`: 6秒播放率（百分比）
  - `post`: 发布量
  - `post_change`: 发布量变化率（百分比）
  - `second_ecom_category`: 二级电商类目
    - `id`: 类目ID
    - `label`: 类目标签
    - `parent_id`: 父类目ID
    - `value`: 类目名称
  - `share`: 分享数
  - `third_ecom_category`: 三级电商类目
    - `id`: 类目ID
    - `label`: 类目标签
    - `parent_id`: 父类目ID
    - `value`: 类目名称
  - `url_title`: URL标题
- `pagination`: 分页信息
  - `page`: 当前页
  - `size`: 每页数量
  - `total`: 总数量
  - `has_more`: 是否有更多
 ### 示例响应:
 ```json
 {
  "code": 200,
  "router": "/api/v1/tiktok/ads/get_top_products",
  "params": {
    "last": "7",
    "page": "1",
    "limit": "20",
    "country_code": "US",
    "first_ecom_category_id": "",
    "ecom_type": "l3",
    "period_type": "last",
    "order_by": "post",
    "order_type": "desc"
  },
  "data": {
    "code": 0,
    "msg": "OK",
    "data": {
      "list": [
        {
          "comment": 3449,
          "cost": 477000,
          "cover_url": null,
          "cpa": 9.21,
          "ctr": 1.29,
          "cvr": 12.94,
          "ecom_type": "l3",
          "first_ecom_category": {
            "id": "601450",
            "label": "category_601450",
            "value": "Beauty & Personal Care"
          },
          "impression": 65000000,
          "like": 166618,
          "play_six_rate": 7.62,
          "post": 10600,
          "post_change": -10.16,
          "second_ecom_category": {
            "id": "848648",
            "label": "category_848648",
            "parent_id": "601450",
            "value": "Makeup & Perfume"
          },
          "share": 2359,
          "third_ecom_category": {
            "id": "601583",
            "label": "category_601583",
            "parent_id": "848648",
            "value": "Perfume"
          },
          "url_title": "Perfume"
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
}
 ```

## get_unique_id

`GET /api/v1/tiktok/web/get_unique_id`

<!-- Full path: /api/v1/tiktok/web/get_unique_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 用户主页链接/User homepage link | https://www.tiktok.com/@tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户unique_id
### 参数:
- url: 用户主页链接
### 返回:
- unique_id

## get_user_id

`GET /api/v1/tiktok/web/get_user_id`

<!-- Full path: /api/v1/tiktok/web/get_user_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 用户主页链接/User homepage link | https://www.tiktok.com/@tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取用户user_id
### 参数:
- url: 用户主页链接
### 返回:
- 用户id

## get_user_id_and_sec_user_id_by_username

`GET /api/v1/tiktok/app/v3/get_user_id_and_sec_user_id_by_username`

<!-- Full path: /api/v1/tiktok/app/v3/get_user_id_and_sec_user_id_by_username -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | 用户名/Username | tiktok |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 使用用户名获取用户 user_id 和 sec_user_id
### 参数:
- username: 用户名
### 返回:
- 用户 user_id 和 sec_user_id

## get_video_analytics_summary

`POST /api/v1/tiktok/creator/get_video_analytics_summary`

<!-- Full path: /api/v1/tiktok/creator/get_video_analytics_summary -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号在指定时间范围内的视频表现概览。
 - 默认统计从调用当天向前 30 天的数据（或按平台设定的自然月分段）。
 - 适合用于视频表现分析，例如视频数量、播放量、粉丝增长、成交数据等。
  ### 返回内容说明:
 - `segments`（分段数据列表）:
  - `time_selector`: 时间范围设置信息（周期、起止时间戳、时区、语言）
  - `filter.creator_id`: 创作者账号 ID
  - `timed_stats`: 每个时间段的视频表现数据，包含：
    - `vv_cnt`: 视频播放量（Video Views Count）
    - `new_follower_cnt`: 新增粉丝数量
    - `video_cnt`: 发布视频数量
    - `gmv.amount`: 视频带货产生的 GMV 金额
    - `items_sold`: 售出商品数量
 ### 备注:
 - 此接口仅适用于 TikTok Shop 创作者账号。
 - 如果某个时间段无数据，返回的 `stats` 字段可能为空 `{}`。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - 创作者账号视频表现概览

## get_video_associated_product_list

`POST /api/v1/tiktok/creator/get_video_associated_product_list`

<!-- Full path: /api/v1/tiktok/creator/get_video_associated_product_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定视频在 TikTok Shop 中关联展示的商品列表及其推广表现数据。
 - 可用于分析每个视频挂载商品的数量、商品价格区间、商品跳转链接，以及商品销售和推广效果。
  ### 备注:
 - 必须提供 item_ids（视频 ID 列表）。
 - 时间范围默认使用 start_date 所在自然月。
 - 支持单次查询多个视频，返回每个视频关联的所有商品信息及对应商品的推广数据。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询起始日期，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - item_ids: 视频 ID 列表，例如 ["7496499484705246507", "7496110433699482923"]
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回内容说明:
 - `segments`（分段数据列表）:
  - `time_selector`: 时间筛选信息（起止时间戳）
  - `filter`: 查询条件（视频 ID 列表）
  - `timed_lists`: 每个时间段下的视频商品关联列表
    - `videoToProductsMap`:
      - `item_id`: 视频 ID
      - `products`: 关联商品列表
        - `id`: 商品 ID
        - `name`: 商品名称
        - `cover_image.thumb_url_list`: 商品图片 URL 列表
        - `product_detail_page_url`: 商品跳转链接
        - `price_min` / `price_max`: 商品价格区间
      - `stats`:
        - `product.id`: 商品 ID
        - 商品销售推广表现（如销量、点击率等）
 ### 示例请求体:
 ```json
 {
  "cookie": "your_cookie",
  "start_date": "04-01-2025",
  "item_ids": ["7496499484705246507", "7496110433699482923"]
}
 ```

## get_video_audience_stats

`POST /api/v1/tiktok/creator/get_video_audience_stats`

<!-- Full path: /api/v1/tiktok/creator/get_video_audience_stats -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定 TikTok 视频观众的用户画像统计数据，包括性别分布、年龄分布、地区分布等维度。
 - 可用于精准了解视频观众群体特征，指导内容创作、商品选择和营销策略优化。
 - 支持按时间段（日/周/月）分析变化趋势。
  ### 备注:
 - 此接口需要提供 item_id（视频 ID）。
 - 受众画像数据来源于观看和互动用户的统计特征。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询起始日期，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - item_id: 视频 ID，例如 "7496499484705246507"
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回内容说明:
 - `segments`（数据分段列表）:
  - `time_selector`: 时间筛选参数（period, granularity, start_timestamp, end_timestamp）
  - `filter`: 查询条件（creator_id, item_id）
  - `timed_profile`: 分段画像统计数据
    - `start_timestamp`: 开始时间戳
    - `end_timestamp`: 结束时间戳
    - `stats`:
      - `follower_genders`: 性别分布
        - `key`: 性别（female/male）
        - `value`: 占比（字符串，0-1）
      - `follower_ages`: 年龄段分布
        - `key`: 年龄段（如 "18-24", "25-34", 等）
        - `value`: 占比（字符串，0-1）
      - `follower_regions`: 地区分布
        - `key`: 国家代码（如 "US"）
        - `value`: 占比（字符串，0-1）
      - `profile_type`: 画像类型，固定值 2（受众画像）
 ### 示例请求体:
 ```json
 {
  "cookie": "your_cookie",
  "start_date": "04-01-2025",
  "item_id": "7496499484705246507"
}
 ```

## get_video_detailed_stats

`POST /api/v1/tiktok/creator/get_video_detailed_stats`

<!-- Full path: /api/v1/tiktok/creator/get_video_detailed_stats -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定 TikTok 视频在指定自然月内的详细分段统计数据。
 - 支持按时间段（日/周/月）统计新粉丝、点赞、评论、分享、商品浏览、完播率等多维指标。
 - 可用于深入分析单个视频在不同时间段的表现变化，优化内容策略和推广效果。
  ### 备注:
 - 必须提供 item_id（视频 ID）。
 - 时间范围基于 start_date 所在自然月。
 - 若数据量大，返回的数据将按不同时间粒度分段统计（granularity=日/周/月）。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询起始日期，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - item_id: 视频 ID，例如 "7496499484705246507"
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回内容说明:
 - `segments`（数据分段列表）:
  - `time_selector`: 时间筛选条件（period, granularity, start_timestamp, end_timestamp）
  - `filter`: 查询条件（creator_id, item_id）
  - `timed_stats`: 按时间段返回的统计数据列表
    - `start_timestamp`: 开始时间戳
    - `end_timestamp`: 结束时间戳
    - `stats`:
      - `creator_id`: 创作者账号 ID
      - `item_id`: 视频 ID
      - `new_follower_cnt`: 新增粉丝数量
      - `share_cnt`: 分享次数
      - `comment_cnt`: 评论次数
      - `like_cnt`: 点赞次数
      - `product_view_cnt`: 商品浏览量
      - `video_completion_rate`: 视频完播率（字符串，0-1）
 ### 示例请求体:
 ```json
 {
  "cookie": "your_cookie",
  "start_date": "04-01-2025",
  "item_id": "7496499484705246507"
}
 ```

## get_video_list_analytics

`POST /api/v1/tiktok/creator/get_video_list_analytics`

<!-- Full path: /api/v1/tiktok/creator/get_video_list_analytics -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 TikTok Shop 创作者账号在指定时间范围内发布的视频列表及其详细数据表现。
 - 支持分页查询，每页返回指定时间段内的视频及其播放、成交等详细数据。
  ### 返回内容说明:
 - `segments`（分段数据列表）:
  - `time_selector`: 查询时间范围（起止时间戳、时区、语言等）
  - `filter.creator_id`: 创作者账号 ID
  - `list_control`:
    - `rules`: 列表排序规则（通常按发布时间降序）
    - `next_pagination`: 翻页信息（是否有更多页，当前页，总页数，总记录数）
  - `timed_lists`: 每个时间段内的视频数据，包括：
    - `video_meta`:
      - `item_id`: 视频 Item ID
      - `name`: 视频标题
      - `publish_time`: 视频发布时间（Unix 时间戳）
      - `duration`: 视频时长（秒）
      - `video_play_info`: 视频播放资源信息（封面图、播放链接等）
    - `new_follower_cnt`: 视频期间新增粉丝数
    - `vv_cnt`: 视频播放量
    - `ctr`: 商品点击率（Click Through Rate）
    - `gmv.amount`: 视频带货产生的总 GMV 金额
    - `item_sold_cnt`: 视频带动的商品售出数量
    - `direct_gmv.amount`: 直接带货 GMV
    - `completion_rate`: 视频观看完成率
 ### 备注:
 - 此接口仅适用于 TikTok Shop 创作者账号。
 - 数据按自然日或周分组，且每条视频数据对应一段时间内的统计值。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询起始日期，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - page: 页码，默认为第一页 `0`
 - rules: 列表排序规则，默认按发布时间排序，可选值如下：
    - `"VIDEO_LIST_PUBLISH_TIME"`：按发布时间排序
    - `"VIDEO_LIST_GMV"`：按商品交易总额排序
    - `"VIDEO_LIST_DIRECT_GMV"`：按直接商品交易总额排序
    - `"VIDEO_LIST_VV_CNT"`：按观看人次数排序
    - `"VIDEO_LIST_ITEM_SOLD_CNT"`：按成交件数排序
    - `"VIDEO_LIST_CTR"`：按商品点击率排序
    - `"VIDEO_LIST_COMPLETION_RATE"`：按观看完播率排序
    - `"VIDEO_LIST_LIKE_CNT"`：按点赞数排序
    - `"VIDEO_LIST_NEW_FOLLOWER_CNT"`：按新增粉丝数排序
- proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回:
 - 创作者账号视频列表及详细分析数据

## get_video_to_product_stats

`POST /api/v1/tiktok/creator/get_video_to_product_stats`

<!-- Full path: /api/v1/tiktok/creator/get_video_to_product_stats -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定 TikTok 视频与指定商品关联的推广详细统计数据。
 - 支持分析视频为商品带来的商品浏览量、点击量、销售量、订单量、商品收入、直接收入等多维度指标。
 - 返回数据按时间段（日/周/月）分段统计，便于观察趋势变化。
  ### 备注:
 - 必须同时提供 item_id（视频 ID）和 product_id（商品 ID）。
 - 时间范围基于 start_date 所在自然月。
  ### 参数:
 - cookie: 用户 Cookie 字符串（用于身份认证）
 - start_date: 查询起始日期，格式为 'MM-DD-YYYY'，如 '04-01-2025'
 - item_id: 视频 ID，例如 "7496499484705246507"
 - product_id: 商品 ID，例如 "1731050202505515549"
 - proxy: 可选 HTTP 代理地址，如不使用可省略
    - 示例格式: `http://username:password@host:port`
 ### 返回内容说明:
 - `segments`（数据分段列表）:
  - `time_selector`: 时间筛选参数（period, granularity, start_timestamp, end_timestamp）
  - `filter`: 查询条件（creator_id, item_id, product_id）
  - `timed_stats`: 按时间段分段的统计数据
    - `start_timestamp`: 时间段开始时间戳
    - `end_timestamp`: 时间段结束时间戳
    - `stats`:
      - `item_id`: 视频 ID
      - `product_id`: 商品 ID
      - `product_revenue.amount_formatted`: 商品产生的总收入（格式化字符串，如 "$100.00"）
      - `product_revenue.amount`: 商品产生的总收入（数值）
      - `direct_revenue.amount_formatted`: 直接成交产生的收入（格式化字符串）
      - `product_sales_cnt`: 商品销售数量
      - `product_view_cnt`: 商品浏览量
      - `product_click_cnt`: 商品点击量
      - `order_cnt`: 生成订单数量
 ### 示例请求体:
 ```json
 {
  "cookie": "your_cookie",
  "start_date": "04-01-2025",
  "item_id": "7496499484705246507",
  "product_id": "1731050202505515549"
}
 ```

## handler_user_profile

`GET /api/v1/tiktok/app/v3/handler_user_profile`

<!-- Full path: /api/v1/tiktok/app/v3/handler_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户uid （可选，纯数字）/User uid (optional, pure number) (default: '') |  |
| sec_user_id | string |  | 用户sec_user_id/User sec_user_id (default: '') | MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM |
| unique_id | string |  | 用户unique_id （用户名）/User unique_id (username) (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的信息
 ### 参数:
 - sec_user_id: 用户sec_user_id，优先使用sec_user_id获取用户信息。
 - user_id: 用户uid，可选参数，纯数字，如果使用请保持sec_user_id以及unique_id为空。
 - unique_id:
用户unique_id，可选参数，如果sec_user_id为空，则使用unique_id获取用户信息，unique_id也是用户的用户名，如果使用请保持sec_user_id以及user_id为空。
 - 以上参数必须至少填写一个，优先级为sec_user_id > user_id > unique_id，优先级越高速度越快。
 ### 返回:
 - 用户信息

## open_tiktok_app_to_keyword_search

`GET /api/v1/tiktok/app/v3/open_tiktok_app_to_keyword_search`

<!-- Full path: /api/v1/tiktok/app/v3/open_tiktok_app_to_keyword_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 关键词/Keyword | Evil0ctal |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成TikTok分享链接，唤起TikTok APP，跳转指定关键词搜索结果。
  ### 参数:
 - keyword: 关键词
 - 注意: 如果未能跳转，请确保APP已经在后台运行。
  ### 返回:
 - 分享链接

## open_tiktok_app_to_send_private_message

`GET /api/v1/tiktok/app/v3/open_tiktok_app_to_send_private_message`

<!-- Full path: /api/v1/tiktok/app/v3/open_tiktok_app_to_send_private_message -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 7059867056504407087 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成TikTok分享链接，唤起TikTok APP，给指定用户发送私信。
  ### 参数:
 - uid: 用户id，从用户主页接口中获取。
 - 注意: 如果未能跳转，请确保APP已经在后台运行。
  ### 返回:
 - 分享链接

## open_tiktok_app_to_user_profile

`GET /api/v1/tiktok/app/v3/open_tiktok_app_to_user_profile`

<!-- Full path: /api/v1/tiktok/app/v3/open_tiktok_app_to_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 7059867056504407087 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成TikTok分享链接，唤起TikTok APP，跳转指定用户主页。
  ### 参数:
 - uid: 用户id，从用户主页接口中获取。
 - 注意: 如果未能跳转，请确保APP已经在后台运行。
  ### 返回:
 - 分享链接

## open_tiktok_app_to_video_detail

`GET /api/v1/tiktok/app/v3/open_tiktok_app_to_video_detail`

<!-- Full path: /api/v1/tiktok/app/v3/open_tiktok_app_to_video_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7440436579409153311 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成TikTok分享链接，唤起TikTok APP，跳转指定作品详情页。
  ### 参数:
 - aweme_id: 作品id
 - 注意: 如果未能跳转，请确保APP已经在后台运行。
  ### 返回:
 - 分享链接

## search_follower_list

`GET /api/v1/tiktok/app/v3/search_follower_list`

<!-- Full path: /api/v1/tiktok/app/v3/search_follower_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 7540849481009988663 |
| keyword | string | ✅ | 搜索关键词/Search keyword | a |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索指定用户的粉丝列表，可以用于查找某个用户的粉丝中是否有特定昵称的用户。
 ### 参数:
 - user_id: 用户ID，这是一个纯数字版本的用户ID，可以先通过获取用户信息接口获取。
 - keyword: 搜索关键词，用户的昵称中包含该关键词即可匹配
 ### 返回:
 - 搜索结果列表

## search_following_list

`GET /api/v1/tiktok/app/v3/search_following_list`

<!-- Full path: /api/v1/tiktok/app/v3/search_following_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | 用户ID/User ID | 7540849481009988663 |
| keyword | string | ✅ | 搜索关键词/Search keyword | a |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索指定用户的关注列表，可以用于查找某个用户的关注中是否有特定昵称的用户。
 ### 参数:
 - user_id: 用户ID，这是一个纯数字版本的用户ID，可以先通过获取用户信息接口获取。
 - keyword: 搜索关键词，用户的昵称中包含该关键词即可匹配。
 ### 返回:
 - 搜索结果列表

## tiktok_live_room

`GET /api/v1/tiktok/web/tiktok_live_room`

<!-- Full path: /api/v1/tiktok/web/tiktok_live_room -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| live_room_url | string | ✅ | 直播间链接/Live room link | https://www.tiktok.com/@mpl.id.official/live |
| danmaku_type | string | ✅ | 消息类型/Message type | WebcastChatMessage |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 提取直播间弹幕

该接口已不再提供线上服务，需要自行购买源代码后在本地部署使用，购买源代码请在Discord服务器联系管理员，Discord邀请链接：https://discord.gg/aMEAS8Xsvz
 #### 价格:
 ### 参数:
 - live_room_url: 直播间链接
 - danmaku_type: 消息类型
    - WebcastChatMessage: 聊天消息
    - WebcastMemberMessage: 成员消息
    - WebcastRoomUserSeqMessage: 用户序列消息
    - WebcastGiftMessage: 礼物消息
    - WebcastSocialMessage: 社交消息
    - WebcastLikeMessage: 点赞消息
    - WebcastLinkMicFanTicketMethod: 连麦粉丝票方法
    - WebcastLinkMicMethod: 连麦方法
### 返回:
 - 弹幕数据的WebSocket连接信息，需要使用WebSocket连接获取弹幕数据，此接口不返回弹幕数据。

---

See SKILL.md for cross-group orchestration patterns.