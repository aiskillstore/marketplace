---
name: maxhub-tiktok
description: TikTok/TikTok平台TikTok数据采集、创作者分析与电商洞察。当用户提到tiktok、国际版抖音、海外短视频、creator、analytics等相关需求时激活此Skill。
version: 1.1.0
author: MaxHub Team
license: MIT
metadata:
  openclaw:
    requires:
      env:
        - MAXHUB_API_KEY
        - MAXHUB_BASE_URL
    primaryEnv: MAXHUB_API_KEY
    security:
      dataHandling: "本Skill仅通过HTTPS调用MaxHub API获取公开数据，不存储、不转发用户凭证，不访问本地文件系统，不执行任何平台操纵操作"
      permissions:
        - "network: 仅与用户配置的MAXHUB_BASE_URL通信（HTTPS）"
        - "env: 仅读取MAXHUB_API_KEY和MAXHUB_BASE_URL环境变量"
      noAccess:
        - "不访问本地文件系统"
        - "不访问浏览器Cookie或Session"
        - "不读取SSH密钥或AWS凭证"
        - "不修改系统配置文件"
        - "不执行任何刷量、刷播放、刷点赞等平台操纵操作"
        - "不生成平台安全绕过签名"
    emoji: 📦
    homepage: https://www.aconfig.cn
    repository: https://gitee.com/wwwwwwwwwwwwwwww/maxhub-api
    tags:
      - tiktok
      - 国际版抖音
      - 海外短视频
      - creator
---
# 🎶 TikTok（TikTok）Skill

你是TikTok平台的数据专家。你精通TikTok平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 `https://www.aconfig.cn`）

## API能力全景 / API Capabilities Overview

本Skill掌握TikTok **194个API**，覆盖7大能力域：

| 能力域 | API数量 | 核心能力 |
|--------|---------|----------|
| 数据采集 | 99 | 获取用户的作品列表/Get user p、获取用户的个人信息/Get user p、获取探索作品数据/Get explore |
| 数据分析 | 20 | 获取直播间排行榜数据/Get live 、音乐排行榜/Music Chart Li、获取直播每日榜单数据/Get live  |
| 搜索查询 | 32 | 获取每日趋势搜索关键词/Get dail、搜索用户/Search user、获取综合搜索列表/Get general |
| 互动操作 | 20 | 获取用户的点赞列表/Get user l、获取用户的粉丝列表/Get user f、获取用户的收藏列表/Get user f |
| 工具服务 | 4 | 生成哈希ID/Generate has、生成TikTok分享链接/Generate、生成TikTok分享链接/Generate |
| 内容解析 | 7 | 提取列表用户sec_user_id/Ex、提取单个作品id/Extract sin、提取列表作品id/Extract lis |
| 创作者/达人 | 12 | 获取创作者橱窗商品列表/Get crea、获取创作者账号概览/Get Creato、获取带货创作者信息/Get shoppi |



## 🚀 快速开始 / Quick Start

### 首次使用 / First Time Use

如果您是第一次使用本 Skill，请先完成以下步骤：

1. 访问 [MaxHub 官网](https://www.aconfig.cn) 注册账号
2. 在控制台创建 API Key
3. 将 API Key 配置到环境变量 `MAXHUB_API_KEY` 中

### API 调用格式 / API Call Format

所有 API 请求直接使用原始接口路径，无需额外前缀：

```bash
# 基本调用格式
curl -X GET "${MAXHUB_BASE_URL}/api/v1/{platform}/web/fetch_data" \
  -H "x-api-key: $MAXHUB_API_KEY"
```


### 认证说明 / Authentication Instructions

所有 API 请求需在请求头中携带 API Key：
- 请求头：`x-api-key: $MAXHUB_API_KEY`
- 在 [MaxHub 官网](https://www.aconfig.cn) 注册并获取 API Key


### 🔒 安全声明 / Security Statement

- 本Skill **仅** 通过MaxHub API获取公开数据 / This Skill **only** fetches public data via MaxHub API，不访问用户本地文件系统
- API Key 通过环境变量 / API Key is passed via environment variable `MAXHUB_API_KEY` 安全传递，**不会** 被存储、记录或转发到第三方
- 所有API请求均通过HTTPS加密传输 / All API requests are encrypted via HTTPS
- 本Skill **不会** 读取浏览器Cookie / This Skill **will not** read browser cookies、SSH密钥、AWS凭证等敏感信息
- 本Skill **不会** 修改任何系统配置文件 / This Skill **will not** modify any system configuration files


## 智能调度规则 / Intelligent Scheduling Rules

### 1. 意图识别 → API选择 / Intent Recognition → API Selection

根据用户描述，按以下优先级匹配API：

1. **精确匹配**：用户明确指定操作（如"搜索xxx的视频"→搜索API）
2. **语义推断**：根据上下文推断意图（如"这个博主有多少粉丝"→用户信息API）
3. **默认兜底**：无法精确匹配时，优先使用搜索类API获取基础数据

### 2. 链式调用策略 / Chain Call Strategy

当单个API无法满足需求时，按以下模式链式调用：

**模式A：搜索→详情 / Pattern A: Search → Details**
```
用户: "帮我找TikTok上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**
```
用户: "分析这个TikTok博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**
```
用户: "找TikTok美妆领域的头部达人"
步骤1: 调用搜索API → 获取相关用户
步骤2: 对每个用户调用详情API → 获取粉丝数等
步骤3: 调用分析/榜单API → 交叉验证排名
步骤4: 综合排序 → 输出Top达人列表
```

### 3. 参数智能填充 / Intelligent Parameter Filling

- 必填参数缺失时，主动向用户询问
- 可选参数根据上下文智能推断默认值
- 分页参数自动管理（首次page=1，根据需要自动翻页）


## ⚡ 调用限制 / Rate Limits

为保护用户账户安全和控制费用，本Skill遵循以下限制：

| 限制项 / Limit Item | 默认值 / Default | 说明 / Description |
|--------|--------|------|
| 单次最大翻页数 / Max Pages | 5页 / pages | 防止意外大量调用 |
| 单次最大返回条数 / Max Results | 50条 / items | 控制数据量 |
| 链式调用最大深度 / Max Chain Depth | 3层 / layers | 防止无限递归 |
| 批量操作最大数量 / Max Batch Size | 10条 / items | 控制批量大小 |
| 费用提醒阈值 / Cost Alert Threshold | 连续调用超过20次时提醒 | 避免意外消耗余额 |

**重要规则 / Important Rules:**
- 每次调用前检查账户余额是否充足 / Check account balance before each call
- 翻页超过5页时必须提醒用户并确认 / Must remind and confirm with user when pagination exceeds 5 pages
- 批量操作前必须告知用户预计调用次数和费用 / Must inform user of estimated calls and costs before batch operations
- 不自动执行可能产生大量费用的操作 / Will not automatically execute operations that may incur high costs

## API详细目录 / API Detailed Catalog

### 数据采集

1. **获取单个作品数据/Get single video data**
   - `GET /api/v1/tiktok/web/fetch_post_detail`（必填: itemId）
2. **获取单个作品数据 V2/Get single video data V2**
   - `GET /api/v1/tiktok/web/fetch_post_detail_v2`（必填: itemId）
3. **获取探索作品数据/Get explore video data**
   - `GET /api/v1/tiktok/web/fetch_explore_post`
4. **获取用户的个人信息/Get user profile**
   - `GET /api/v1/tiktok/web/fetch_user_profile`
5. **获取用户的作品列表/Get user posts**
   - `GET /api/v1/tiktok/web/fetch_user_post`（必填: secUid）
6. **获取用户的转发作品列表/Get user reposts**
   - `GET /api/v1/tiktok/web/fetch_user_repost`（必填: secUid）
7. **获取用户的播放列表/Get user play list**
   - `GET /api/v1/tiktok/web/fetch_user_play_list`（必填: secUid）
8. **获取用户的合辑列表/Get user mix list**
   - `GET /api/v1/tiktok/web/fetch_user_mix`（必填: mixId）
9. **获取用户的直播详情/Get user live details**
   - `GET /api/v1/tiktok/web/fetch_user_live_detail`（必填: uniqueId）
10. **Tag详情/Tag Detail**
   - `GET /api/v1/tiktok/web/fetch_tag_detail`（必填: tag_name）
11. **Tag作品/Tag Post**
   - `GET /api/v1/tiktok/web/fetch_tag_post`（必填: challengeID）
12. **首页推荐作品/Home Feed**
   - `POST /api/v1/tiktok/web/fetch_home_feed`
13. **加密strData/Encrypt strData**
   - `GET /api/v1/tiktok/web/encrypt_strData`（必填: data）
14. **解密strData/Decrypt strData**
   - `GET /api/v1/tiktok/web/decrypt_strData`（必填: encrypted_data）
15. **获取用户unique_id/Get user unique_id**
   - `GET /api/v1/tiktok/web/get_unique_id`（必填: url）
16. **获取列表unique_id/Get list unique_id**
   - `POST /api/v1/tiktok/web/get_all_unique_id`
17. **TikTok直播间弹幕参数获取/tiktok live room danmaku parameters**
   - `GET /api/v1/tiktok/web/fetch_live_im_fetch`（必填: room_id）
18. **直播间开播状态检测/Live room start status check**
   - `GET /api/v1/tiktok/web/fetch_check_live_alive`（必填: room_id）
19. **批量直播间开播状态检测/Batch live room start status check**
   - `GET /api/v1/tiktok/web/fetch_batch_check_live_alive`（必填: room_ids）
20. **通过直播链接获取直播间信息/Get live room information via live link**
   - `GET /api/v1/tiktok/web/fetch_tiktok_live_data`（必填: live_room_url）
21. **获取直播间首页推荐列表/Get live room homepage recommendation list**
   - `GET /api/v1/tiktok/web/fetch_live_recommend`（必填: related_live_tag）
22. **获取直播间礼物列表/Get live room gift list**
   - `GET /api/v1/tiktok/web/fetch_live_gift_list`
23. **获取SSO登录二维码/Get SSO login QR code**
   - `GET /api/v1/tiktok/web/fetch_sso_login_qrcode`（必填: device_id, region, proxy）
24. **获取SSO登录状态/Get SSO login status**
   - `GET /api/v1/tiktok/web/fetch_sso_login_status`（必填: token, device_id, verifyFp, region, proxy）
25. **认证SSO登录/Authenticate SSO login**
   - `GET /api/v1/tiktok/web/fetch_sso_login_auth`（必填: device_id, verifyFp, region, proxy）
26. **根据Gift ID查询礼物名称/Get gift name by gift ID**
   - `POST /api/v1/tiktok/web/fetch_gift_name_by_id`
27. **批量查询Gift ID对应的礼物名称($0.025/次,建议50个)/Batch get gift names by gift IDs ($0.025/call, suggest 50)**
   - `POST /api/v1/tiktok/web/fetch_gift_names_by_ids`
28. **获取单个作品数据/Get single video data**
   - `GET /api/v1/tiktok/app/v3/fetch_one_video`（必填: aweme_id）
29. **获取单个作品数据 V2/Get single video data V2**
   - `GET /api/v1/tiktok/app/v3/fetch_one_video_v2`（必填: aweme_id）
30. **获取单个作品数据 V3(支持国家参数)/Get single video data V3 (support country parameter)**
   - `GET /api/v1/tiktok/app/v3/fetch_one_video_v3`（必填: aweme_id）
31. **批量获取视频信息/Batch Get Video Information**
   - `POST /api/v1/tiktok/app/v3/fetch_multi_video`
32. **批量获取视频信息 V2/Batch Get Video Information V2**
   - `POST /api/v1/tiktok/app/v3/fetch_multi_video_v2`
33. **根据分享链接获取单个作品数据/Get single video data by sharing link**
   - `GET /api/v1/tiktok/app/v3/fetch_one_video_by_share_url_v2`（必填: share_url）
34. **根据分享链接获取单个作品数据/Get single video data by sharing link**
   - `GET /api/v1/tiktok/app/v3/fetch_one_video_by_share_url`（必填: share_url）
35. **使用用户名获取用户 user_id 和 sec_user_id/Get user_id and sec_user_id by Username**
   - `GET /api/v1/tiktok/app/v3/get_user_id_and_sec_user_id_by_username`（必填: username）
36. **获取指定用户的信息/Get information of specified user**
   - `GET /api/v1/tiktok/app/v3/handler_user_profile`
37. **获取指定 Webcast 用户的信息/Get information of specified Webcast user**
   - `GET /api/v1/tiktok/app/v3/fetch_webcast_user_info`
38. **通过用户名获取用户账号国家地区/Get user account country by username**
   - `GET /api/v1/tiktok/app/v3/fetch_user_country_by_username`（必填: username）
39. **获取类似用户推荐/Similar User Recommendations**
   - `GET /api/v1/tiktok/app/v3/fetch_similar_user_recommendations`（必填: sec_uid）
40. **获取用户转发的作品数据/Get user repost video data**
   - `GET /api/v1/tiktok/app/v3/fetch_user_repost_videos`（必填: user_id）
41. **获取用户主页作品数据 V1/Get user homepage video data V1**
   - `GET /api/v1/tiktok/app/v3/fetch_user_post_videos`
42. **获取用户主页作品数据 V2/Get user homepage video data V2**
   - `GET /api/v1/tiktok/app/v3/fetch_user_post_videos_v2`
43. **获取用户主页作品数据 V3（精简数据-更快速）/Get user homepage video data V3 (simplified data - faster)**
   - `GET /api/v1/tiktok/app/v3/fetch_user_post_videos_v3`
44. **获取指定音乐的详情数据/Get details of specified music**
   - `GET /api/v1/tiktok/app/v3/fetch_music_detail`（必填: music_id）
45. **获取指定音乐的视频列表数据/Get video list of specified music**
   - `GET /api/v1/tiktok/app/v3/fetch_music_video_list`（必填: music_id）
46. **获取指定话题的详情数据/Get details of specified hashtag**
   - `GET /api/v1/tiktok/app/v3/fetch_hashtag_detail`（必填: ch_id）
47. **获取指定话题的作品数据/Get video list of specified hashtag**
   - `GET /api/v1/tiktok/app/v3/fetch_hashtag_video_list`（必填: ch_id）
48. **获取指定直播间的数据/Get data of specified live room**
   - `GET /api/v1/tiktok/app/v3/fetch_live_room_info`（必填: room_id）
49. **检测直播间是否在线/Check if live room is online**
   - `GET /api/v1/tiktok/app/v3/check_live_room_online`（必填: room_id）
50. **批量检测直播间是否在线/Batch check if live rooms are online**
   - `POST /api/v1/tiktok/app/v3/check_live_room_online_batch`
51. **获取分享短链接/Get share short link**
   - `GET /api/v1/tiktok/app/v3/fetch_share_short_link`（必填: url）
52. **获取分享二维码/Get share QR code**
   - `GET /api/v1/tiktok/app/v3/fetch_share_qr_code`（必填: object_id）
53. **通过分享链接获取店铺ID/Get Shop ID by Share Link**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_id_by_share_link`（必填: share_link）
54. **通过分享链接获取商品ID/Get Product ID by Share Link**
   - `GET /api/v1/tiktok/app/v3/fetch_product_id_by_share_link`（必填: share_link）
55. **获取商品详情数据（即将弃用，使用 fetch_product_detail_v2 代替）/Get product detail data (will be deprecated, use fetch_product_detail_v2 instead)**
   - `GET /api/v1/tiktok/app/v3/fetch_product_detail`（必填: product_id）
56. **获取商品详情数据V2/Get product detail data V2**
   - `GET /api/v1/tiktok/app/v3/fetch_product_detail_v2`（必填: product_id）
57. **获取商品详情数据V3 / Get product detail data V3**
   - `GET /api/v1/tiktok/app/v3/fetch_product_detail_v3`（必填: product_id）
58. **获取商品详情数据V4 / Get product detail data V4**
   - `GET /api/v1/tiktok/app/v3/fetch_product_detail_v4`（必填: product_id）
59. **获取商品评价数据/Get product review data**
   - `GET /api/v1/tiktok/app/v3/fetch_product_review`（必填: product_id）
60. **获取商家主页Page列表数据/Get shop home page list data**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_home_page_list`（必填: seller_id）
61. **获取商家主页数据/Get shop home page data**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_home`（必填: page_id, seller_id）
62. **获取商家商品推荐数据/Get shop product recommend data**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_product_recommend`（必填: seller_id）
63. **获取商家商品列表数据/Get shop product list data**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_product_list`（必填: seller_id）
64. **获取商家商品列表数据 V2/Get shop product list data V2**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_product_list_v2`（必填: seller_id）
65. **获取商家信息数据/Get shop information data**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_info`（必填: shop_id）
66. **获取商家产品分类数据/Get shop product category data**
   - `GET /api/v1/tiktok/app/v3/fetch_shop_product_category`（必填: seller_id）
67. **获取用户音乐列表数据/Get user music list data**
   - `GET /api/v1/tiktok/app/v3/fetch_user_music_list`（必填: sec_uid）
68. **获取内容翻译数据/Get content translation data**
   - `POST /api/v1/tiktok/app/v3/fetch_content_translate`
69. **获取主页视频推荐数据/Get home feed(recommend) video data**
   - `POST /api/v1/tiktok/app/v3/fetch_home_feed`
70. **TikTok APP加密算法/TikTok APP encryption algorithm**
   - `POST /api/v1/tiktok/app/v3/TTencrypt_algorithm`
71. **获取直播间商品列表数据/Get live room product list data**
   - `GET /api/v1/tiktok/app/v3/fetch_live_room_product_list`（必填: room_id, author_id）
72. **获取直播间商品列表数据 V2 /Get live room product list data V2**
   - `GET /api/v1/tiktok/app/v3/fetch_live_room_product_list_v2`（必填: room_id, author_id）
73. **加密或解密 TikTok APP 登录请求体/Encrypt or Decrypt TikTok APP login request body**
   - `POST /api/v1/tiktok/app/v3/encrypt_decrypt_login_request`
74. **获取单个广告详情/Get single ad detail**
   - `GET /api/v1/tiktok/ads/get_ads_detail`（必填: ads_id）
75. **获取关键词洞察数据/Get keyword insights data**
   - `GET /api/v1/tiktok/ads/get_keyword_insights`
76. **获取热门产品列表/Get top products list**
   - `GET /api/v1/tiktok/ads/get_top_products`
77. **获取热门标签列表/Get popular hashtags list**
   - `GET /api/v1/tiktok/ads/get_hashtag_list`
78. **获取关键词列表/Get keyword list**
   - `GET /api/v1/tiktok/ads/get_keyword_list`
79. **获取热门广告聚光灯/Get top ads spotlight**
   - `GET /api/v1/tiktok/ads/get_top_ads_spotlight`
80. **获取广告百分位数据/Get ad percentile data**
   - `GET /api/v1/tiktok/ads/get_ad_percentile`（必填: material_id）
81. **获取推荐广告/Get recommended ads**
   - `GET /api/v1/tiktok/ads/get_recommended_ads`（必填: material_id）
82. **获取关键词筛选器/Get keyword filters**
   - `GET /api/v1/tiktok/ads/get_keyword_filters`
83. **获取相关关键词/Get related keywords**
   - `GET /api/v1/tiktok/ads/get_related_keywords`
84. **获取关键词详细信息/Get keyword details**
   - `GET /api/v1/tiktok/ads/get_keyword_details`
85. **获取产品筛选器/Get product filters**
   - `GET /api/v1/tiktok/ads/get_product_filters`
86. **获取产品指标数据/Get product metrics**
   - `GET /api/v1/tiktok/ads/get_product_metrics`（必填: id）
87. **获取产品详细信息/Get product detail**
   - `GET /api/v1/tiktok/ads/get_product_detail`（必填: id）
88. **获取标签筛选器/Get hashtag filters**
   - `GET /api/v1/tiktok/ads/get_hashtag_filters`
89. **获取音乐筛选器/Get sound filters**
   - `GET /api/v1/tiktok/ads/get_sound_filters`
90. **获取音乐详情/Get sound detail**
   - `GET /api/v1/tiktok/ads/get_sound_detail`（必填: clip_id）
91. **获取音乐推荐/Get sound recommendations**
   - `GET /api/v1/tiktok/ads/get_sound_recommendations`（必填: clip_id）
92. **获取商品详情V1(桌面端-数据完整)/Get product detail V1(Full data)**
   - `GET /api/v1/tiktok/shop/web/fetch_product_detail`（必填: product_id）
93. **获取商品详情V2(移动端-数据少)/Get product detail V2 (Less Data)**
   - `GET /api/v1/tiktok/shop/web/fetch_product_detail_v2`（必填: product_id）
94. **获取商品详情V3(移动端-数据完整)/Get product detail V3 (Full Data)**
   - `GET /api/v1/tiktok/shop/web/fetch_product_detail_v3`（必填: product_id）
95. **获取商家商品列表V1/Get seller products list V1**
   - `GET /api/v1/tiktok/shop/web/fetch_seller_products_list`（必填: seller_id）
96. **获取商家商品列表V2(移动端)/Get seller products list V2 (Mobile)**
   - `GET /api/v1/tiktok/shop/web/fetch_seller_products_list_v2`（必填: seller_id）
97. **获取商品分类列表/Get product category list**
   - `GET /api/v1/tiktok/shop/web/fetch_products_category_list`
98. **根据分类ID获取商品列表/Get products by category ID**
   - `GET /api/v1/tiktok/shop/web/fetch_products_by_category_id`（必填: category_id）
99. **获取热卖商品列表/Get hot selling products list**
   - `GET /api/v1/tiktok/shop/web/fetch_hot_selling_products_list`

### 数据分析

1. **获取每日热门内容作品数据/Get daily trending video data**
   - `GET /api/v1/tiktok/web/fetch_trending_post`
2. **音乐排行榜/Music Chart List**
   - `GET /api/v1/tiktok/app/v3/fetch_music_chart_list`
3. **获取直播间排行榜数据/Get live room ranking list**
   - `GET /api/v1/tiktok/app/v3/fetch_live_ranking_list`（必填: room_id, anchor_id）
4. **获取直播每日榜单数据/Get live daily rank data**
   - `GET /api/v1/tiktok/app/v3/fetch_live_daily_rank`
5. **获取创作者直播概览/Get Creator Live Overview**
   - `POST /api/v1/tiktok/creator/get_live_analytics_summary`
6. **获取创作者视频概览/Get Creator Video Overview**
   - `POST /api/v1/tiktok/creator/get_video_analytics_summary`
7. **获取创作者视频列表分析/Get Creator Video List Analytics**
   - `POST /api/v1/tiktok/creator/get_video_list_analytics`
8. **获取创作者商品列表分析/Get Creator Product List Analytics**
   - `POST /api/v1/tiktok/creator/get_product_analytics_list`
9. **获取视频详细分段统计数据/Get Video Detailed Statistics**
   - `POST /api/v1/tiktok/creator/get_video_detailed_stats`
10. **获取视频与商品关联统计数据/Get Video-Product Association Statistics**
   - `POST /api/v1/tiktok/creator/get_video_to_product_stats`
11. **获取视频受众分析数据/Get Video Audience Analysis Data**
   - `POST /api/v1/tiktok/creator/get_video_audience_stats`
12. **获取作品的统计数据/Get video metrics**
   - `GET /api/v1/tiktok/analytics/fetch_video_metrics`（必填: item_id）
13. **检测视频虚假流量分析/Detect fake views in video**
   - `GET /api/v1/tiktok/analytics/detect_fake_views`（必填: item_id）
14. **获取视频评论关键词分析/Get comment keywords analysis**
   - `GET /api/v1/tiktok/analytics/fetch_comment_keywords`（必填: item_id）
15. **获取创作者信息和里程碑数据/Get creator info and milestones**
   - `GET /api/v1/tiktok/analytics/fetch_creator_info_and_milestones`（必填: user_id）
16. **获取热门音乐排行榜/Get popular sound rankings**
   - `GET /api/v1/tiktok/ads/get_sound_rank_list`
17. **获取广告关键帧分析/Get ad keyframe analysis**
   - `GET /api/v1/tiktok/ads/get_ad_keyframe_analysis`（必填: material_id）
18. **获取广告互动分析/Get ad interactive analysis**
   - `GET /api/v1/tiktok/ads/get_ad_interactive_analysis`（必填: material_id）
19. **获取创意模式排行榜/Get creative pattern rankings**
   - `GET /api/v1/tiktok/ads/get_creative_patterns`
20. **获取流行趋势视频/Get popular trend videos**
   - `GET /api/v1/tiktok/ads/get_popular_trends`

### 搜索查询

1. **获取每日趋势搜索关键词/Get daily trending search words**
   - `GET /api/v1/tiktok/web/fetch_trending_searchwords`
2. **获取综合搜索列表/Get general search list**
   - `GET /api/v1/tiktok/web/fetch_general_search`（必填: keyword）
3. **搜索关键字推荐/Search keyword suggest**
   - `GET /api/v1/tiktok/web/fetch_search_keyword_suggest`（必填: keyword）
4. **搜索用户/Search user**
   - `GET /api/v1/tiktok/web/fetch_search_user`（必填: keyword）
5. **搜索视频/Search video**
   - `GET /api/v1/tiktok/web/fetch_search_video`（必填: keyword）
6. **搜索直播/Search live**
   - `GET /api/v1/tiktok/web/fetch_search_live`（必填: keyword）
7. **搜索照片/Search photo**
   - `GET /api/v1/tiktok/web/fetch_search_photo`（必填: keyword）
8. **获取指定关键词的综合搜索结果/Get comprehensive search results of specified keywords**
   - `GET /api/v1/tiktok/app/v3/fetch_general_search_result`（必填: keyword）
9. **获取指定关键词的视频搜索结果/Get video search results of specified keywords**
   - `GET /api/v1/tiktok/app/v3/fetch_video_search_result`（必填: keyword）
10. **获取指定关键词的用户搜索结果/Get user search results of specified keywords**
   - `GET /api/v1/tiktok/app/v3/fetch_user_search_result`（必填: keyword）
11. **获取指定关键词的音乐搜索结果/Get music search results of specified keywords**
   - `GET /api/v1/tiktok/app/v3/fetch_music_search_result`（必填: keyword）
12. **获取指定关键词的话题搜索结果/Get hashtag search results of specified keywords**
   - `GET /api/v1/tiktok/app/v3/fetch_hashtag_search_result`（必填: keyword）
13. **获取指定关键词的直播搜索结果/Get live search results of specified keywords**
   - `GET /api/v1/tiktok/app/v3/fetch_live_search_result`（必填: keyword）
14. **获取地点搜索结果/Get location search results**
   - `GET /api/v1/tiktok/app/v3/fetch_location_search`（必填: keyword）
15. **创作者搜索洞察/Creator Search Insights**
   - `GET /api/v1/tiktok/app/v3/fetch_creator_search_insights`
16. **创作者搜索洞察详情/Creator Search Insights Detail**
   - `GET /api/v1/tiktok/app/v3/fetch_creator_search_insights_detail`（必填: query_id_str）
17. **创作者搜索洞察趋势/Creator Search Insights Trend**
   - `GET /api/v1/tiktok/app/v3/fetch_creator_search_insights_trend`（必填: query_id_str）
18. **创作者搜索洞察相关视频/Creator Search Insights Videos**
   - `GET /api/v1/tiktok/app/v3/fetch_creator_search_insights_videos`（必填: keyword）
19. **搜索粉丝列表/Search follower list**
   - `GET /api/v1/tiktok/app/v3/search_follower_list`（必填: user_id, keyword）
20. **搜索关注列表/Search following list**
   - `GET /api/v1/tiktok/app/v3/search_following_list`（必填: user_id, keyword）
21. **获取商品搜索结果/Get product search results**
   - `GET /api/v1/tiktok/app/v3/fetch_product_search`（必填: keyword）
22. **生成TikTok分享链接，唤起TikTok APP，跳转指定关键词搜索结果/Generate TikTok share link, call TikTok APP, and jump to the specified keyword search result**
   - `GET /api/v1/tiktok/app/v3/open_tiktok_app_to_keyword_search`（必填: keyword）
23. **搜索广告/Search ads**
   - `GET /api/v1/tiktok/ads/search_ads`
24. **获取查询建议/Get query suggestions**
   - `GET /api/v1/tiktok/ads/get_query_suggestions`
25. **搜索音乐提示/Search sound hints**
   - `GET /api/v1/tiktok/ads/search_sound_hint`（必填: keyword）
26. **搜索音乐/Search sounds**
   - `GET /api/v1/tiktok/ads/search_sound`（必填: keyword）
27. **搜索创作者/Search creators**
   - `GET /api/v1/tiktok/ads/search_creators`（必填: keyword）
28. **获取搜索关键词建议V1/Get search keyword suggestions V1**
   - `GET /api/v1/tiktok/shop/web/fetch_search_word_suggestion`（必填: search_word）
29. **获取搜索关键词建议V2(移动端)/Get search keyword suggestions V2 (Mobile)**
   - `GET /api/v1/tiktok/shop/web/fetch_search_word_suggestion_v2`（必填: search_word）
30. **搜索商品列表V1/Search products list V1**
   - `GET /api/v1/tiktok/shop/web/fetch_search_products_list`（必填: search_word）
31. **搜索商品列表V2(移动端)/Search products list V2 (Mobile)**
   - `GET /api/v1/tiktok/shop/web/fetch_search_products_list_v2`（必填: search_word）
32. **搜索商品列表V3/Search products list V3**
   - `GET /api/v1/tiktok/shop/web/fetch_search_products_list_v3`（必填: keyword）

### 互动操作

1. **获取用户的点赞列表/Get user likes**
   - `GET /api/v1/tiktok/web/fetch_user_like`（必填: secUid）
2. **获取用户的收藏列表/Get user favorites**
   - `GET /api/v1/tiktok/web/fetch_user_collect`（必填: cookie, secUid）
3. **获取作品的评论列表/Get video comments**
   - `GET /api/v1/tiktok/web/fetch_post_comment`（必填: aweme_id）
4. **获取作品的评论回复列表/Get video comment replies**
   - `GET /api/v1/tiktok/web/fetch_post_comment_reply`（必填: item_id, comment_id）
5. **获取用户的粉丝列表/Get user followers**
   - `GET /api/v1/tiktok/web/fetch_user_fans`（必填: secUid）
6. **获取用户的关注列表/Get user followings**
   - `GET /api/v1/tiktok/web/fetch_user_follow`（必填: secUid）
7. **获取用户喜欢作品数据/Get user like video data**
   - `GET /api/v1/tiktok/app/v3/fetch_user_like_videos`（必填: sec_user_id）
8. **获取单个视频评论数据/Get single video comments data**
   - `GET /api/v1/tiktok/app/v3/fetch_video_comments`（必填: aweme_id）
9. **获取指定视频的评论回复数据/Get comment replies data of specified video**
   - `GET /api/v1/tiktok/app/v3/fetch_video_comment_replies`（必填: item_id, comment_id）
10. **获取指定用户的粉丝列表数据/Get follower list of specified user**
   - `GET /api/v1/tiktok/app/v3/fetch_user_follower_list`
11. **获取指定用户的关注列表数据/Get following list of specified user**
   - `GET /api/v1/tiktok/app/v3/fetch_user_following_list`
12. **获取商品评论V1/Get product reviews V1**
   - `GET /api/v1/tiktok/shop/web/fetch_product_reviews_v1`（必填: product_id）
13. **获取商品评论V2/Get product reviews V2**
   - `GET /api/v1/tiktok/shop/web/fetch_product_reviews_v2`（必填: product_id）
14. **申请使用TikTok交互API权限（Scope）/Apply for TikTok Interaction API permission (Scope)**
   - `GET /api/v1/tiktok/interaction/apply`（必填: api_key, invite_code）
15. **发送评论/Post comment**
   - `POST /api/v1/tiktok/interaction/post_comment`
16. **回复评论/Reply to comment**
   - `POST /api/v1/tiktok/interaction/reply_comment`
17. **点赞/Like**
   - `POST /api/v1/tiktok/interaction/like`
18. **关注/Follow**
   - `POST /api/v1/tiktok/interaction/follow`
19. **收藏/Collect**
   - `POST /api/v1/tiktok/interaction/collect`
20. **转发/Forward**
   - `POST /api/v1/tiktok/interaction/forward`

### 工具服务

1. **生成哈希ID/Generate hashed ID**
   - `GET /api/v1/tiktok/web/generate_hashed_id`（必填: email）
2. **生成TikTok分享链接，唤起TikTok APP，跳转指定作品详情页/Generate TikTok share link, call TikTok APP, and jump to the specified video details page**
   - `GET /api/v1/tiktok/app/v3/open_tiktok_app_to_video_detail`（必填: aweme_id）
3. **生成TikTok分享链接，唤起TikTok APP，跳转指定用户主页/Generate TikTok share link, call TikTok APP, and jump to the specified user profile**
   - `GET /api/v1/tiktok/app/v3/open_tiktok_app_to_user_profile`（必填: uid）
4. **生成TikTok分享链接，唤起TikTok APP，给指定用户发送私信/Generate TikTok share link, call TikTok APP, and send private messages to specified users**
   - `GET /api/v1/tiktok/app/v3/open_tiktok_app_to_send_private_message`（必填: uid）

### 内容解析

1. **提取用户user_id/Extract user user_id**
   - `GET /api/v1/tiktok/web/get_user_id`（必填: url）
2. **提取用户sec_user_id/Extract user sec_user_id**
   - `GET /api/v1/tiktok/web/get_sec_user_id`（必填: url）
3. **提取列表用户sec_user_id/Extract list user sec_user_id**
   - `POST /api/v1/tiktok/web/get_all_sec_user_id`
4. **提取单个作品id/Extract single video id**
   - `GET /api/v1/tiktok/web/get_aweme_id`（必填: url）
5. **提取列表作品id/Extract list video id**
   - `POST /api/v1/tiktok/web/get_all_aweme_id`
6. **提取直播间弹幕/Extract live room danmaku**
   - `GET /api/v1/tiktok/web/tiktok_live_room`（必填: live_room_url, danmaku_type）
7. **根据直播间链接提取直播间ID/Extract live room ID from live room link**
   - `GET /api/v1/tiktok/web/get_live_room_id`（必填: live_room_url）

### 创作者/达人

1. **获取带货创作者信息/Get shopping creator information**
   - `GET /api/v1/tiktok/app/v3/fetch_creator_info`（必填: creator_uid）
2. **获取创作者橱窗商品列表/Get creator showcase product list**
   - `GET /api/v1/tiktok/app/v3/fetch_creator_showcase_product_list`（必填: kol_id）
3. **获取创作者账号健康状态/Get Creator Account Health Status**
   - `POST /api/v1/tiktok/creator/get_account_health_status`
4. **获取创作者账号违规记录列表/Get Creator Account Violation Record List**
   - `POST /api/v1/tiktok/creator/get_account_violation_list`
5. **获取创作者账号概览/Get Creator Account Overview**
   - `POST /api/v1/tiktok/creator/get_account_insights_overview`
6. **获取创作者账号信息/Get Creator Account Info**
   - `POST /api/v1/tiktok/creator/get_creator_account_info`
7. **获取橱窗商品列表/Get Showcase Product List**
   - `POST /api/v1/tiktok/creator/get_showcase_product_list`
8. **获取视频关联商品列表/Get Video Associated Product List**
   - `POST /api/v1/tiktok/creator/get_video_associated_product_list`
9. **获取同款商品关联视频/Get Product Related Videos**
   - `POST /api/v1/tiktok/creator/get_product_related_videos`
10. **获取标签创作者信息/Get hashtag creator info**
   - `GET /api/v1/tiktok/ads/get_hashtag_creator`（必填: hashtag）
11. **获取创作者筛选器/Get creator filters**
   - `GET /api/v1/tiktok/ads/get_creator_filters`
12. **获取创作者列表/Get creator list**
   - `GET /api/v1/tiktok/ads/get_creator_list`

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/tiktok/web/fetch_explore_post" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/tiktok/web/fetch_post_detail?itemId=1234567890" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "${MAXHUB_BASE_URL}/api/v1/tiktok/web/fetch_home_feed" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "BASE_URL/API_PATH?param1=value1&param2=value2" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "BASE_URL/API_PATH" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## 注意事项 / Important Notes

- 所有请求必须携带有效的MaxHub API Key / All requests must carry a valid MaxHub API Key
- API调用按次计费，注意控制调用次数 / API calls are billed per use, pay attention to call frequency
- 遵守平台数据使用规范，不采集敏感个人隐私数据 / Follow platform data usage guidelines, do not collect sensitive personal privacy data
- 分页数据建议逐页获取，避免一次性请求过多 / For paginated data, fetch page by page to avoid requesting too much at once
- 高频调用注意限流（默认60次/分钟）/ Pay attention to rate limiting for high-frequency calls (default 60 calls/minute)
