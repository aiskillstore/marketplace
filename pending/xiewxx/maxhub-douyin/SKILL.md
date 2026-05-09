***

name: maxhub-douyin
description: 抖音/Douyin平台数据采集与智能分析。当用户提到抖音、douyin、短视频、直播、达人等相关需求时激活此Skill。
version: 1.1.0
author: MaxHub Team
license: MIT
metadata:
openclaw:
requires:
env:
\- MAXHUB\_API\_KEY
\- MAXHUB\_BASE\_URL
primaryEnv: MAXHUB\_API\_KEY
security:
dataHandling: "本Skill仅通过HTTPS调用MaxHub API获取公开数据，不存储、不转发用户凭证，不访问本地文件系统，不执行任何平台操纵操作"
permissions:
\- "network: 仅与用户配置的MAXHUB\_BASE\_URL通信（HTTPS）"
\- "env: 仅读取MAXHUB\_API\_KEY和MAXHUB\_BASE\_URL环境变量"
noAccess:
\- "不访问本地文件系统"
\- "不访问浏览器Cookie或Session"
\- "不读取SSH密钥或AWS凭证"
\- "不修改系统配置文件"
\- "不执行任何刷量、刷播放、刷点赞等平台操纵操作"
\- "不生成平台安全绕过签名"
emoji: 🎵
homepage: <https://www.aconfig.cn>
repository: <https://gitee.com/wwwwwwwwwwwwwwww/maxhub-api>
tags:
\- douyin
\- 抖音
\- 短视频
\- 直播
\- 数据采集
-------

# 🎵 抖音（Douyin）Skill

你是抖音平台的数据专家。你精通抖音平台所有API的能力和限制，能根据用户需求智能选择最合适的API，必要时链式调用多个API完成复杂任务。

## ⚠️ 重要提示 / Important Notice

### 环境变量配置（必须）/ Environment Variables Configuration (Required)

在 OpenClaw 中**必须**配置以下环境变量才能正常使用:

```bash
# 必需环境变量
MAXHUB_API_KEY=mh_sk_your_api_key_here
MAXHUB_BASE_URL=https://www.aconfig.cn
```

**获取 API Key 步骤 / Steps to Get API Key:**

1. 访问 [MaxHub 官网](https://www.aconfig.cn) 注册账号
2. 登录后在控制台创建 API Key
3. API Key 格式: `mh_sk_xxxxxxxxxxxxxxxx`
4. 将 API Key 配置到环境变量 `MAXHUB_API_KEY` 中

### 🔒 安全声明 / Security Statement

- 本Skill **仅** 通过MaxHub API获取公开数据 / This Skill **only** fetches public data via MaxHub API，不访问用户本地文件系统
- API Key 通过环境变量 / API Key is passed via environment variable `MAXHUB_API_KEY` 安全传递，**不会** 被存储、记录或转发到第三方
- 所有API请求均通过HTTPS加密传输 / All API requests are encrypted via HTTPS
- 本Skill **不会** 读取浏览器Cookie / This Skill **will not** read browser cookies、SSH密钥、AWS凭证等敏感信息
- 本Skill **不会** 修改任何系统配置文件 / This Skill **will not** modify any system configuration files

### 常见错误及解决方法 / Common Errors and Solutions

#### 错误 1: 401 Unauthorized / Error 1: 401 Unauthorized

**原因 / Cause**: 未提供 API Key 或 API Key 无效

**解决方法 / Solution**:
确保请求头包含有效的 x-api-key

#### 错误 2: 402 Payment Required / Error 2: 402 Payment Required

**原因 / Cause**: 账户余额不足

**解决方法 / Solution**: 登录 MaxHub 控制台充值账户余额

#### 错误 3: 404 Not Found / Error 3: 404 Not Found

**原因 / Cause**: API 端点不存在

**解决方法 / Solution**:

- 检查 API 路径是否正确
- 查看 API 文档: ${MAXHUB\_BASE\_URL}/api/docs

#### 错误 4: 429 Too Many Requests / Error 4: 429 Too Many Requests

**原因 / Cause**: 请求频率超过限制（默认 60 次/分钟）

**解决方法 / Solution**: 等待一段时间后重试

## 认证方式 / Authentication Method

所有API请求通过MaxHub API中转站调用，需在请求头中携带API Key：

```
x-api-key: ${MAXHUB_API_KEY}
```

基础URL：`${MAXHUB_BASE_URL}`（默认 <https://www.aconfig.cn）>

## API能力全景 / API Capabilities Overview

本Skill掌握抖音 **280个API**，覆盖7大能力域：

| 能力域    | API数量 | 核心能力                                                            |
| ------ | ----- | --------------------------------------------------------------- |
| 数据采集   | 67    | 获取单个作品数据 V2/Get sing、根据分享链接获取单个作品数据/Get s、获取单个作品数据/Get single   |
| 互动操作   | 8     | 获取用户关注列表 (弃用，使用 /api、获取用户喜欢作品数据/Get user 、获取用户关注列表/Get user fo  |
| 数据分析   | 88    | 根据视频ID获取作品的统计数据（点赞数、、获取创作者中心创作热点/Get crea、获取创作者中心热门视频榜单/Get cr  |
| 搜索查询   | 59    | \[已弃用/Deprecated] 获取指、获取指定关键词的用户搜索结果(废弃，替代、获取指定关键词的用户搜索结果 V2 (已 |
| 工具服务   | 5     | 生成抖音短链接/Generate、生成抖音视频分享二维码/Generate、生成抖音分享链接/Generate         |
| 内容解析   | 7     | 提取列表用户id/Extract lis、提取直播间号/Extract webca、提取单个作品id/Extract sin  |
| 创作者/达人 | 46    | 获取创作者活动列表/Get creato、获取创作者内容创作合集分类/Get cr、获取创作者热门课程/Get creato  |

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
用户: "帮我找抖音上关于美食的热门内容"
步骤1: 调用搜索API → 获取内容ID列表
步骤2: 对每个ID调用详情API → 获取完整数据
```

**模式B：用户→内容 / Pattern B: User → Content**

```
用户: "分析这个抖音博主的内容数据"
步骤1: 调用用户信息API → 获取用户ID和基础数据
步骤2: 调用用户作品列表API → 获取内容列表
步骤3: 对关键作品调用详情API → 获取互动数据
```

**模式C：搜索→用户→分析 / Pattern C: Search → User → Analysis**

```
用户: "找抖音美妆领域的头部达人"
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
| -------- | ------------ | -------- |
| 单次最大翻页数 / Max Pages | 5页 / pages | 防止意外大量调用 |
| 单次最大返回条数 / Max Results | 50条 / items | 控制数据量    |
| 链式调用最大深度 / Max Chain Depth | 3层 / layers | 防止无限递归   |
| 批量操作最大数量 / Max Batch Size | 10条 / items | 控制批量大小   |
| 费用提醒阈值 / Cost Alert Threshold | 连续调用超过20次时提醒 | 避免意外消耗余额 |

**重要规则 / Important Rules:**

- 每次调用前检查账户余额是否充足 / Check account balance before each call
- 翻页超过5页时必须提醒用户并确认 / Must remind and confirm with user when pagination exceeds 5 pages
- 批量操作前必须告知用户预计调用次数和费用 / Must inform user of estimated calls and costs before batch operations
- 不自动执行可能产生大量费用的操作 / Will not automatically execute operations that may incur high costs

## API详细目录 / API Detailed Catalog

### 数据采集

1. **获取单个作品数据/Get single video data**
   - `GET /api/v1/douyin/web/fetch_one_video`（必填: aweme\_id）
2. **获取单个作品数据 V2/Get single video data V2**
   - `GET /api/v1/douyin/web/fetch_one_video_v2`（必填: aweme\_id）
3. **根据分享链接获取单个作品数据/Get single video data by sharing link**
   - `GET /api/v1/douyin/web/fetch_one_video_by_share_url`（必填: share\_url）
4. **获取视频的最高画质播放链接/Get the highest quality play URL of the video**
   - `GET /api/v1/douyin/web/fetch_video_high_quality_play_url`
5. **批量获取视频的最高画质播放链接/Batch get the highest quality play URL of videos**
   - `POST /api/v1/douyin/web/fetch_multi_video_high_quality_play_url`
6. **批量获取视频信息/Batch Get Video Information**
   - `POST /api/v1/douyin/web/fetch_multi_video`
7. **获取单个作品视频弹幕数据/Get single video danmaku data**
   - `GET /api/v1/douyin/web/fetch_one_video_danmaku`（必填: item\_id, duration, end\_time, start\_time）
8. **获取首页推荐数据/Get home feed data**
   - `GET /api/v1/douyin/web/fetch_home_feed`
9. **获取相关作品推荐数据/Get related posts recommendation data**
   - `GET /api/v1/douyin/web/fetch_related_posts`（必填: aweme\_id）
10. **获取用户主页作品数据/Get user homepage video data**

- `GET /api/v1/douyin/web/fetch_user_post_videos`（必填: sec\_user\_id）

1. **获取用户收藏作品数据/Get user collection video data**

- `POST /api/v1/douyin/web/fetch_user_collection_videos`

1. **获取用户收藏夹/Get user collection**

- `POST /api/v1/douyin/web/fetch_user_collects`

1. **获取用户收藏夹数据/Get user collection data**

- `GET /api/v1/douyin/web/fetch_user_collects_videos`（必填: collects\_id）

1. **获取用户合辑作品数据/Get user mix video data**

- `GET /api/v1/douyin/web/fetch_user_mix_videos`（必填: mix\_id）

1. **获取用户直播流数据/Get user live video data**

- `GET /api/v1/douyin/web/fetch_user_live_videos`（必填: webcast\_id）

1. **通过sec\_uid获取指定用户的直播流数据/Get live video data of specified user by sec\_uid**

- `GET /api/v1/douyin/web/fetch_user_live_videos_by_sec_uid`（必填: sec\_uid）

1. **通过room\_id获取指定用户的直播流数据 V1/Get live video data of specified user by room\_id V1**

- `GET /api/v1/douyin/web/fetch_user_live_videos_by_room_id`（必填: room\_id）

1. **通过room\_id获取指定用户的直播流数据 V2/Gets the live stream data of the specified user by room\_id V2**

- `GET /api/v1/douyin/web/fetch_user_live_videos_by_room_id_v2`（必填: room\_id）

1. **抖音直播间商品信息/Douyin live room product information**

- `GET /api/v1/douyin/web/fetch_live_room_product_result`（必填: room\_id, author\_id）

1. **获取商品详情/Get product detail**

- `GET /api/v1/douyin/web/fetch_product_detail`（必填: product\_id）

1. **获取商品SKU列表/Get product SKU list**

- `GET /api/v1/douyin/web/fetch_product_sku_list`（必填: product\_id, author\_id）

1. **获取商品优惠券信息/Get product coupon information**

- `GET /api/v1/douyin/web/fetch_product_coupon`（必填: product\_id, shop\_id, price, author\_id, sec\_user\_id）

1. **获取商品评价评分/Get product review score**

- `GET /api/v1/douyin/web/fetch_product_review_score`（必填: product\_id, shop\_id）

1. **获取商品评价列表/Get product review list**

- `GET /api/v1/douyin/web/fetch_product_review_list`（必填: product\_id, shop\_id）

1. **使用UID获取用户信息/Get user information by UID**

- `GET /api/v1/douyin/web/fetch_user_profile_by_uid`（必填: uid）

1. **获取批量用户信息(最多10个)/Get batch user profile (up to 10)**

- `GET /api/v1/douyin/web/fetch_batch_user_profile_v1`（必填: sec\_user\_ids）

1. **获取批量用户信息(最多50个)/Get batch user profile (up to 50)**

- `GET /api/v1/douyin/web/fetch_batch_user_profile_v2`（必填: sec\_user\_ids）

1. **使用UID获取用户开播信息/Get user live information by UID**

- `GET /api/v1/douyin/web/fetch_user_live_info_by_uid`（必填: uid）

1. **使用Short ID获取用户信息/Get user information by Short ID**

- `GET /api/v1/douyin/web/fetch_user_profile_by_short_id`（必填: short\_id）

1. **生成短链接**

- `GET /api/v1/douyin/web/handler_shorten_url`（必填: target\_url）

1. **使用sec\_user\_id获取指定用户的信息/Get information of specified user by sec\_user\_id**

- `GET /api/v1/douyin/web/handler_user_profile`（必填: sec\_user\_id）

1. **使用unique\_id（抖音号）获取指定用户的信息/Get information of specified user by unique\_id**

- `GET /api/v1/douyin/web/handler_user_profile_v2`（必填: unique\_id）

1. **加密用户uid到sec\_user\_id/Encrypt user uid to sec\_user\_id**

- `GET /api/v1/douyin/web/encrypt_uid_to_sec_user_id`（必填: uid）

1. **根据抖音uid获取指定用户的信息/Get information of specified user by uid**

- `GET /api/v1/douyin/web/handler_user_profile_v3`（必填: uid）

1. **根据sec\_user\_id获取指定用户的信息（性别，年龄，直播等级、牌子）/Get information of specified user by sec\_user\_id (gender, age, live level、brand)**

- `GET /api/v1/douyin/web/handler_user_profile_v4`（必填: sec\_user\_id）

1. **获取用户粉丝列表/Get user fans list**

- `GET /api/v1/douyin/web/fetch_user_fans_list`

1. **话题作品/Challenge Posts**

- `POST /api/v1/douyin/web/fetch_challenge_posts`

1. **抖音视频频道数据/Douyin video channel data**

- `GET /api/v1/douyin/web/fetch_video_channel_result`（必填: tag\_id）

1. **直播间号转房间号/Webcast id to room id**

- `GET /api/v1/douyin/web/webcast_id_2_room_id`（必填: webcast\_id）

1. **抖音直播间弹幕参数获取/Douyin live room danmaku parameters**

- `GET /api/v1/douyin/web/fetch_live_im_fetch`（必填: room\_id, user\_unique\_id）

1. **短剧作品/Series Video**

- `GET /api/v1/douyin/web/fetch_series_aweme`（必填: offset, count, content\_type）

1. **知识作品推荐/Knowledge Video**

- `GET /api/v1/douyin/web/fetch_knowledge_aweme`（必填: count）

1. **游戏作品推荐/Game Video**

- `GET /api/v1/douyin/web/fetch_game_aweme`（必填: count）

1. **二次元作品推荐/Anime Video**

- `GET /api/v1/douyin/web/fetch_cartoon_aweme`（必填: count）

1. **音乐作品推荐/Music Video**

- `GET /api/v1/douyin/web/fetch_music_aweme`（必填: count）

1. **美食作品推荐/Food Video**

- `GET /api/v1/douyin/web/fetch_food_aweme`（必填: count）

1. **获取单个作品数据/Get single video data**

- `GET /api/v1/douyin/app/v3/fetch_one_video`（必填: aweme\_id）

1. **获取单个作品数据 V2/Get single video data V2**

- `GET /api/v1/douyin/app/v3/fetch_one_video_v2`（必填: aweme\_id）

1. **获取单个作品数据 V3 (无版权限制)/Get single video data V3 (No copyright restrictions)**

- `GET /api/v1/douyin/app/v3/fetch_one_video_v3`（必填: aweme\_id）

1. **根据分享口令获取分享信息/Get share info by share code**

- `GET /api/v1/douyin/app/v3/fetch_share_info_by_share_code`（必填: share\_code）

1. **批量获取视频信息 V1/Batch Get Video Information V1**

- `POST /api/v1/douyin/app/v3/fetch_multi_video`

1. **批量获取视频信息 V2/Batch Get Video Information V2**

- `POST /api/v1/douyin/app/v3/fetch_multi_video_v2`

1. **根据分享链接获取单个作品数据/Get single video data by sharing link**

- `GET /api/v1/douyin/app/v3/fetch_one_video_by_share_url`（必填: share\_url）

1. **获取视频的最高画质播放链接/Get the highest quality play URL of the video**

- `GET /api/v1/douyin/app/v3/fetch_video_high_quality_play_url`

1. **批量获取视频的最高画质播放链接/Batch get the highest quality play URL of videos**

- `POST /api/v1/douyin/app/v3/fetch_multi_video_high_quality_play_url`

1. **获取指定用户的信息/Get information of specified user**

- `GET /api/v1/douyin/app/v3/handler_user_profile`（必填: sec\_user\_id）

1. **获取用户粉丝列表/Get user fans list**

- `GET /api/v1/douyin/app/v3/fetch_user_fans_list`

1. **获取用户主页作品数据/Get user homepage video data**

- `GET /api/v1/douyin/app/v3/fetch_user_post_videos`（必填: sec\_user\_id）

1. **获取抖音视频合集详情数据/Get Douyin video mix detail data**

- `GET /api/v1/douyin/app/v3/fetch_video_mix_detail`（必填: mix\_id）

1. **获取抖音视频合集作品列表数据/Get Douyin video mix post list data**

- `GET /api/v1/douyin/app/v3/fetch_video_mix_post_list`（必填: mix\_id）

1. **获取用户短剧合集列表/Get user series list**

- `GET /api/v1/douyin/app/v3/fetch_user_series_list`

1. **获取短剧视频列表/Get series video list**

- `GET /api/v1/douyin/app/v3/fetch_series_video_list`（必填: series\_id）

1. **获取短剧详情信息/Get series detail**

- `GET /api/v1/douyin/app/v3/fetch_series_detail`（必填: series\_id）

1. **获取指定音乐的详情数据/Get details of specified music**

- `GET /api/v1/douyin/app/v3/fetch_music_detail`（必填: music\_id）

1. **获取指定音乐的视频列表数据/Get video list of specified music**

- `GET /api/v1/douyin/app/v3/fetch_music_video_list`（必填: music\_id）

1. **获取指定话题的详情数据/Get details of specified hashtag**

- `GET /api/v1/douyin/app/v3/fetch_hashtag_detail`（必填: ch\_id）

1. **获取指定话题的作品数据/Get video list of specified hashtag**

- `GET /api/v1/douyin/app/v3/fetch_hashtag_video_list`（必填: ch\_id）

### 互动操作

1. **获取用户喜欢作品数据/Get user like video data**
   - `POST /api/v1/douyin/web/fetch_user_like_videos`
2. **获取用户关注列表/Get user following list**
   - `GET /api/v1/douyin/web/fetch_user_following_list`
3. **获取单个视频评论数据/Get single video comments data**
   - `GET /api/v1/douyin/web/fetch_video_comments`（必填: aweme\_id）
4. **获取指定视频的评论回复数据/Get comment replies data of specified video**
   - `GET /api/v1/douyin/web/fetch_video_comment_replies`（必填: item\_id, comment\_id）
5. **获取用户关注列表 (弃用，使用 /api/v1/douyin/web/fetch\_user\_following\_list 替代)/Get user following list (Deprecated, use /api/v1/douyin/web/fetch\_user\_following\_list instead)**
   - `GET /api/v1/douyin/app/v3/fetch_user_following_list`
6. **获取用户喜欢作品数据/Get user like video data**
   - `GET /api/v1/douyin/app/v3/fetch_user_like_videos`（必填: sec\_user\_id）
7. **获取单个视频评论数据/Get single video comments data**
   - `GET /api/v1/douyin/app/v3/fetch_video_comments`（必填: aweme\_id）
8. **获取指定视频的评论回复数据/Get comment replies data of specified video**
   - `GET /api/v1/douyin/app/v3/fetch_video_comment_replies`（必填: item\_id, comment\_id）

### 数据分析

1. **获取直播间送礼用户排行榜/Get live room gift user ranking**
   - `GET /api/v1/douyin/web/fetch_live_gift_ranking`（必填: room\_id）
2. **根据视频ID获取作品的统计数据（点赞数、下载数、播放数、分享数）/Get the statistical data of the Post according to the video ID (like count, download count, play count, share count)**
   - `GET /api/v1/douyin/app/v3/fetch_video_statistics`（必填: aweme\_ids）
3. **根据视频ID批量获取作品的统计数据（点赞数、下载数、播放数、分享数）/Get the statistical data of the Post according to the video ID (like count, download count, play count, share count)**
   - `GET /api/v1/douyin/app/v3/fetch_multi_video_statistics`（必填: aweme\_ids）
4. **获取创作者中心热门视频榜单/Get creator material center billboard**
   - `GET /api/v1/douyin/creator/fetch_creator_material_center_billboard`
5. **获取创作者中心创作热点/Get creator hot spot billboard**
   - `GET /api/v1/douyin/creator/fetch_creator_hot_spot_billboard`
6. **获取创作者热门话题榜单/Get creator hot topic billboard**
   - `GET /api/v1/douyin/creator/fetch_creator_hot_topic_billboard`
7. **获取创作者热门道具榜单/Get creator hot props billboard**
   - `GET /api/v1/douyin/creator/fetch_creator_hot_props_billboard`
8. **获取创作者热门挑战榜单/Get creator hot challenge billboard**
   - `GET /api/v1/douyin/creator/fetch_creator_hot_challenge_billboard`
9. **获取创作者热门音乐榜单/Get creator hot music billboard**
   - `GET /api/v1/douyin/creator/fetch_creator_hot_music_billboard`
10. **获取作品流量来源统计/Fetch item play source statistics**

- `POST /api/v1/douyin/creator_v2/fetch_item_play_source`

1. **获取作品观看趋势分析/Fetch item watch trend analysis**

- `POST /api/v1/douyin/creator_v2/fetch_item_watch_trend`

1. **获取作品弹幕分析/Fetch item bullet analysis**

- `POST /api/v1/douyin/creator_v2/fetch_item_danmaku_analysis`

1. **获取作品观众数据分析/Fetch item audience portrait**

- `POST /api/v1/douyin/creator_v2/fetch_item_audience_portrait`

1. **获取作品观众其他数据分析/Fetch item audience others analysis**

- `POST /api/v1/douyin/creator_v2/fetch_item_audience_others`

1. **获取投稿分析概览/Fetch item analysis overview**

- `POST /api/v1/douyin/creator_v2/fetch_item_analysis_overview`

1. **获取所有有效日期/Get all valid dates**

- `GET /api/v1/douyin/index/fetch_all_valid_date`

1. **获取关联分析有效日期/Get valid date for relation**

- `GET /api/v1/douyin/index/fetch_valid_date_for_relation`

1. **获取所有地区列表/Get all area list**

- `GET /api/v1/douyin/index/fetch_all_area`

1. **获取实时热点排行/Get current hot topics**

- `GET /api/v1/douyin/index/fetch_current_hot_topic`

1. **获取热门关键词/Get hot words**

- `GET /api/v1/douyin/index/fetch_hot_words`

1. **获取关键词有效日期/Get keyword valid date**

- `POST /api/v1/douyin/index/fetch_keyword_valid_date`（必填: keyword\_list）

1. **获取多关键词热度趋势/Get multi-keyword hot trend**

- `POST /api/v1/douyin/index/fetch_multi_keyword_hot_trend`（必填: keyword\_list, start\_date, end\_date）

1. **获取多关键词解读/Get multi-keyword interpretation**

- `POST /api/v1/douyin/index/fetch_multi_keyword_interpretation`（必填: keyword\_list, start\_date, end\_date）

1. **获取关联词分析/Get relation word analysis**

- `POST /api/v1/douyin/index/fetch_relation_word`（必填: keyword, start\_date, end\_date）

1. **获取人群画像/Get crowd portrait**

- `POST /api/v1/douyin/index/fetch_portrait`（必填: keyword, start\_date, end\_date）

1. **获取用户订阅关键词/Get user subscribed keywords**

- `POST /api/v1/douyin/index/fetch_get_user_sub_word`

1. **抖音 uid 转加密 user\_id/Encrypt Douyin uid to user\_id**

- `GET /api/v1/douyin/index/fetch_encrypt_user_id`（必填: uid）

1. **达人趋势对比/Daren compare users**

- `POST /api/v1/douyin/index/fetch_daren_compare_users_stable`（必填: user\_list）

1. **获取相似达人/Get similar daren**

- `POST /api/v1/douyin/index/fetch_daren_similar_users`（必填: user\_id）

1. **获取达人视频/Get daren top videos**

- `POST /api/v1/douyin/index/fetch_daren_great_user_top_video`（必填: user\_id, start\_date, end\_date）

1. **获取达人核心指标/Get daren core metrics**

- `POST /api/v1/douyin/index/fetch_daren_great_item_mile_info`（必填: user\_id）

1. **获取达人粉丝分析/Get daren fans analysis**

- `POST /api/v1/douyin/index/fetch_daren_great_user_fans_info`（必填: user\_id）

1. **获取品牌指数/Get brand index**

- `POST /api/v1/douyin/index/fetch_brand_valid_info`（必填: keyword\_list）

1. **获取品牌雷达图/Get brand radar chart**

- `POST /api/v1/douyin/index/fetch_brand_radar_chart`（必填: brand\_name, start\_date, end\_date）

1. **获取品牌趋势线/Get brand trend lines**

- `POST /api/v1/douyin/index/fetch_brand_lines`（必填: brand\_name, start\_date, end\_date）

1. **获取品牌周期数据/Get brand cycles**

- `POST /api/v1/douyin/index/fetch_brand_cycles`（必填: brand\_name, start\_date, end\_date）

1. **获取品牌主动排行周榜/Get brand initiative rank weekly**

- `POST /api/v1/douyin/index/fetch_brand_initiative_rank_weekly`（必填: brand\_name, start\_date, end\_date）

1. **创作指南有效日期/Get content valid date**

- `GET /api/v1/douyin/index/fetch_content_valid_date`

1. **热门视频时间范围/Brand hot videos time scope**

- `POST /api/v1/douyin/index/fetch_brand_hot_videos_time_scope`

1. **创作热门关键词/Content creative keywords**

- `POST /api/v1/douyin/index/fetch_content_creative_keywords`（必填: tag\_id, end\_date）

1. **关键词相关视频/Creative keyword related items**

- `POST /api/v1/douyin/index/fetch_content_creative_keyword_items`（必填: tag\_id, end\_date, keyword）

1. **创作热门话题/Content creative topic**

- `POST /api/v1/douyin/index/fetch_content_creative_topic`（必填: tag\_id, end\_date）

1. **内容发布趋势/Content publish trend**

- `GET /api/v1/douyin/index/fetch_content_publish_trend`（必填: tag\_id, start\_date, end\_date）

1. **创作时长分布/Content creative duration**

- `POST /api/v1/douyin/index/fetch_content_creative_duration`（必填: tag\_id, end\_date）

1. **创作者画像/Content author portrait**

- `POST /api/v1/douyin/index/fetch_content_author_portrait`（必填: tag\_id, end\_date）

1. **消费者画像/Content consumer portrait**

- `POST /api/v1/douyin/index/fetch_content_consumer_portrait`（必填: tag\_id, end\_date）

1. **互动趋势/Content interact trend**

- `POST /api/v1/douyin/index/fetch_content_interact_trend`（必填: tag\_id, start\_date, end\_date）

1. **消费趋势/Content consume trend**

- `POST /api/v1/douyin/index/fetch_content_consume_trend`（必填: tag\_id, start\_date, end\_date）

1. **获取推荐报告/Get recommended insight reports**

- `GET /api/v1/douyin/index/fetch_insight_recommend`

1. **获取报告详情/Get report detail**

- `GET /api/v1/douyin/index/fetch_report_detail`（必填: report\_id）

1. **获取报告相关推荐/Get related insight recommendations**

- `GET /api/v1/douyin/index/fetch_insight_get_rec`（必填: report\_id）

1. **获取中国城市列表/Fetch Chinese city list**

- `GET /api/v1/douyin/billboard/fetch_city_list`

1. **获取垂类内容标签/Fetch vertical content tags**

- `GET /api/v1/douyin/billboard/fetch_content_tag`

1. **获取热点榜分类/Fetch hot list category**

- `GET /api/v1/douyin/billboard/fetch_hot_category_list`（必填: billboard\_type）

1. **获取上升热点榜/Fetch rising hot list**

- `GET /api/v1/douyin/billboard/fetch_hot_rise_list`（必填: page, page\_size, order）

1. **获取同城热点榜/Fetch city hot list**

- `GET /api/v1/douyin/billboard/fetch_hot_city_list`（必填: page, page\_size, order）

1. **获取挑战热榜/Fetch hot challenge list**

- `GET /api/v1/douyin/billboard/fetch_hot_challenge_list`（必填: page, page\_size）

1. **获取热点总榜/Fetch total hot list**

- `GET /api/v1/douyin/billboard/fetch_hot_total_list`（必填: page, page\_size, type）

1. **获取活动日历/Fetch activity calendar**

- `POST /api/v1/douyin/billboard/fetch_hot_calendar_list`

1. **获取活动日历详情/Fetch activity calendar detail**

- `GET /api/v1/douyin/billboard/fetch_hot_calendar_detail`（必填: calendar\_id）

1. **获取作品点赞观众画像-仅限热门榜/Fetch work like audience portrait - hot list only**

- `GET /api/v1/douyin/billboard/fetch_hot_user_portrait_list`（必填: aweme\_id）

1. **获取作品评论分析-词云权重/Fetch work comment analysis word cloud weight**

- `GET /api/v1/douyin/billboard/fetch_hot_comment_word_list`（必填: aweme\_id）

1. **获取作品数据趋势/Fetch post data trend**

- `GET /api/v1/douyin/billboard/fetch_hot_item_trends_list`

1. **获取热门账号/Fetch hot account list**

- `POST /api/v1/douyin/billboard/fetch_hot_account_list`

1. **获取账号粉丝数据趋势/Fetch account fan data trend**

- `GET /api/v1/douyin/billboard/fetch_hot_account_trends_list`（必填: sec\_uid）

1. **获取账号作品分析-上周/Fetch account work analysis - last week**

- `GET /api/v1/douyin/billboard/fetch_hot_account_item_analysis_list`（必填: sec\_uid）

1. **获取粉丝画像/Fetch fan portrait**

- `GET /api/v1/douyin/billboard/fetch_hot_account_fans_portrait_list`（必填: sec\_uid）

1. **获取粉丝兴趣作者 20个用户/Fetch fan interest author 20 users**

- `GET /api/v1/douyin/billboard/fetch_hot_account_fans_interest_account_list`（必填: sec\_uid）

1. **获取粉丝近3天感兴趣的话题 10个话题/Fetch fan interest topic in the last 3 days 10 topics**

- `GET /api/v1/douyin/billboard/fetch_hot_account_fans_interest_topic_list`（必填: sec\_uid）

1. **获取视频热榜/Fetch video hot list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_video_list`

1. **获取低粉爆款榜/Fetch low fan explosion list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_low_fan_list`

1. **获取高完播率榜/Fetch high completion rate list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_high_play_list`

1. **获取高点赞率榜/Fetch high like rate list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_high_like_list`

1. **获取高涨粉率榜/Fetch high fan rate list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_high_fan_list`

1. **获取话题热榜/Fetch topic hot list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_topic_list`

1. **获取热度飙升的话题榜/Fetch topic list with rising popularity**

- `POST /api/v1/douyin/billboard/fetch_hot_total_high_topic_list`

1. **获取全部热门内容词/Fetch all hot content words**

- `POST /api/v1/douyin/billboard/fetch_hot_total_hot_word_list`

1. **获取内容词详情/Fetch content word details**

- `GET /api/v1/douyin/billboard/fetch_hot_total_hot_word_detail_list`（必填: keyword, word\_id, query\_day）

1. **获取kol转化能力分析V1/Get kol Conversion Ability Analysis V1**

- `GET /api/v1/douyin/xingtu/kol_conversion_ability_analysis_v1`（必填: kolId, \_range）

1. **获取kol星图指数V1/Get kol Xingtu Index V1**

- `GET /api/v1/douyin/xingtu/kol_xingtu_index_v1`（必填: kolId）

1. **获取kol性价比能力分析V1/Get kol Cp Info V1**

- `GET /api/v1/douyin/xingtu/kol_cp_info_v1`（必填: kolId）

1. **获取kol热词分析评论V1/Get Author Hot Comment Tokens V1**

- `GET /api/v1/douyin/xingtu/author_hot_comment_tokens_v1`（必填: kolId）

1. **获取kol热词分析内容V1/Get Author Content Hot Comment Keywords V1**

- `GET /api/v1/douyin/xingtu/author_content_hot_comment_keywords_v1`（必填: kolId）

1. **获取星图热榜分类/Get Ranking List Catalog**

- `GET /api/v1/douyin/xingtu_v2/get_ranking_list_catalog`

1. **获取星图达人商业榜数据/Get Ranking List Data**

- `GET /api/v1/douyin/xingtu_v2/get_ranking_list_data`

1. **获取短剧演员热榜分类/Get Playlet Actor Rank Catalog**

- `POST /api/v1/douyin/xingtu_v2/get_playlet_actor_rank_catalog`

1. **获取短剧演员热榜/Get Playlet Actor Rank List**

- `GET /api/v1/douyin/xingtu_v2/get_playlet_actor_rank_list`

1. **获取内容趋势指南/Get Content Trend Guide**

- `GET /api/v1/douyin/xingtu_v2/get_content_trend_guide`

### 搜索查询

1. **\[已弃用/Deprecated] 获取指定关键词的综合搜索结果/Get comprehensive search results of specified keywords**
   - `GET /api/v1/douyin/web/fetch_general_search_result`（必填: keyword）
2. **\[已弃用/Deprecated] 获取指定关键词的视频搜索结果/Get video search results of specified keywords**
   - `GET /api/v1/douyin/web/fetch_video_search_result`（必填: keyword）
3. **获取指定关键词的视频搜索结果 V2 （废弃，替代接口请参考下方文档）/Get video search results of specified keywords V2 (Deprecated, please refer to the following document for replacement interface)**
   - `GET /api/v1/douyin/web/fetch_video_search_result_v2`（必填: keyword）
4. **获取指定关键词的用户搜索结果(废弃，替代接口请参考下方文档)/Get user search results of specified keywords (deprecated, please refer to the following document for replacement interface)**
   - `GET /api/v1/douyin/web/fetch_user_search_result`（必填: keyword）
5. **获取指定关键词的用户搜索结果 V2 (已弃用，替代接口请参考下方文档)/Get user search results of specified keywords V2 (deprecated, please refer to the following document for replacement interface)**
   - `GET /api/v1/douyin/web/fetch_user_search_result_v2`（必填: keyword）
6. **获取指定关键词的用户搜索结果 V3 (已弃用，替代接口请参考下方文档)/Get user search results of specified keywords V3 (deprecated, please refer to the following document for replacement interface)**
   - `GET /api/v1/douyin/web/fetch_user_search_result_v3`（必填: keyword）
7. **\[已弃用/Deprecated] 获取指定关键词的直播搜索结果/Get live search results of specified keywords**
   - `GET /api/v1/douyin/web/fetch_live_search_result`（必填: keyword）
8. **\[已弃用/Deprecated] 搜索话题/Search Challenge**
   - `POST /api/v1/douyin/web/fetch_search_challenge`
9. **获取抖音热榜数据/Get Douyin hot search results**
   - `GET /api/v1/douyin/web/fetch_hot_search_result`
10. **查询抖音用户基本信息/Query Douyin user basic information**

- `POST /api/v1/douyin/web/fetch_query_user`

1. **获取指定关键词的综合搜索结果（弃用，替代接口见下方文档说明）/Get comprehensive search results of specified keywords (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_general_search_result`（必填: keyword）

1. **获取指定关键词的视频搜索结果（弃用，替代接口见下方文档说明）/Get video search results of specified keywords (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_video_search_result`（必填: keyword）

1. **获取指定关键词的视频搜索结果 V2 （弃用，替代接口见下方文档说明）/Get video search results of specified keywords V2 (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_video_search_result_v2`（必填: keyword）

1. **获取指定关键词的用户搜索结果（弃用，替代接口见下方文档说明）/Get user search results of specified keywords (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_user_search_result`（必填: keyword）

1. **获取指定关键词的直播搜索结果（弃用，替代接口见下方文档说明）/Get live search results of specified keywords (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_live_search_result`（必填: keyword）

1. **获取指定关键词的音乐搜索结果（弃用，替代接口见下方文档说明）/Get music search results of specified keywords (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_music_search_result`（必填: keyword）

1. **获取指定关键词的话题搜索结果（弃用，替代接口见下方文档说明）/Get hashtag search results of specified keywords (deprecated, see the documentation below for alternative interfaces)**

- `GET /api/v1/douyin/app/v3/fetch_hashtag_search_result`（必填: keyword）

1. **获取抖音热搜榜数据/Get Douyin hot search list data**

- `GET /api/v1/douyin/app/v3/fetch_hot_search_list`

1. **获取抖音直播热搜榜数据/Get Douyin live hot search list data**

- `GET /api/v1/douyin/app/v3/fetch_live_hot_search_list`

1. **获取抖音音乐榜数据/Get Douyin music hot search list data**

- `GET /api/v1/douyin/app/v3/fetch_music_hot_search_list`

1. **获取抖音品牌热榜分类数据/Get Douyin brand hot search list data**

- `GET /api/v1/douyin/app/v3/fetch_brand_hot_search_list`

1. **获取抖音品牌热榜具体分类数据/Get Douyin brand hot search list detail data**

- `GET /api/v1/douyin/app/v3/fetch_brand_hot_search_list_detail`（必填: category\_id）

1. **生成抖音分享链接，唤起抖音APP，跳转指定关键词搜索结果/Generate Douyin share link, call Douyin APP, and jump to the specified keyword search result**

- `GET /api/v1/douyin/app/v3/open_douyin_app_to_keyword_search`（必填: keyword）

1. **搜索用户/Search users**

- `GET /api/v1/douyin/creator/fetch_user_search`（必填: user\_name）

1. **获取作品搜索关键词统计/Fetch item search keywords statistics**

- `POST /api/v1/douyin/creator_v2/fetch_item_search_keyword`

1. **达人搜索建议/Daren search suggest**

- `POST /api/v1/douyin/index/fetch_daren_sug_great_user_list`（必填: keyword）

1. **获取视频搜索筛选选项/Get video search filter options**

- `GET /api/v1/douyin/index/fetch_item_filter_options`

1. **视频搜索建议/Video search suggest**

- `POST /api/v1/douyin/index/fetch_item_sug`（必填: query）

1. **视频搜索结果/Video search results**

- `POST /api/v1/douyin/index/fetch_item_query`（必填: query）

1. **品牌搜索建议/Brand search suggest**

- `POST /api/v1/douyin/index/fetch_brand_suggest`（必填: keyword）

1. **话题搜索建议/Topic search suggest**

- `POST /api/v1/douyin/index/fetch_topic_suggest`（必填: keyword）

1. **话题搜索结果/Topic search results**

- `POST /api/v1/douyin/index/fetch_topic_query`（必填: keyword, start\_date, end\_date）

1. **搜索趋势报告/Search trend reports**

- `POST /api/v1/douyin/index/fetch_report_search`

1. **获取综合搜索 V1/Fetch general search V1**

- `POST /api/v1/douyin/search/fetch_general_search_v1`

1. **获取综合搜索 V2/Fetch general search V2**

- `POST /api/v1/douyin/search/fetch_general_search_v2`

1. **获取搜索关键词推荐/Fetch search keyword suggestions**

- `POST /api/v1/douyin/search/fetch_search_suggest`

1. **获取视频搜索 V1/Fetch video search V1**

- `POST /api/v1/douyin/search/fetch_video_search_v1`

1. **获取视频搜索 V2/Fetch video search V2**

- `POST /api/v1/douyin/search/fetch_video_search_v2`

1. **获取多重搜索/Fetch multi-type search**

- `POST /api/v1/douyin/search/fetch_multi_search`

1. **获取用户搜索/Fetch user search**

- `POST /api/v1/douyin/search/fetch_user_search`

1. **获取用户搜索 V2/Fetch user search V2**

- `POST /api/v1/douyin/search/fetch_user_search_v2`

1. **获取图片搜索/Fetch image search**

- `POST /api/v1/douyin/search/fetch_image_search`

1. **获取图文搜索 V3/Fetch image-text search V3**

- `POST /api/v1/douyin/search/fetch_image_search_v3`

1. **获取直播搜索 V1/Fetch live search V1**

- `POST /api/v1/douyin/search/fetch_live_search_v1`

1. **获取话题搜索 V1/Fetch hashtag search V1**

- `POST /api/v1/douyin/search/fetch_challenge_search_v1`

1. **获取话题搜索 V2/Fetch hashtag search V2**

- `POST /api/v1/douyin/search/fetch_challenge_search_v2`

1. **获取话题推荐搜索/Fetch hashtag suggestions**

- `POST /api/v1/douyin/search/fetch_challenge_suggest`

1. **获取经验搜索/Fetch experience search**

- `POST /api/v1/douyin/search/fetch_experience_search`

1. **获取音乐搜索/Fetch music search**

- `POST /api/v1/douyin/search/fetch_music_search`

1. **获取讨论搜索/Fetch discussion search**

- `POST /api/v1/douyin/search/fetch_discuss_search`

1. **获取学校搜索/Fetch school search**

- `POST /api/v1/douyin/search/fetch_school_search`

1. **获取图像识别搜索/Fetch vision search (image-based search)**

- `POST /api/v1/douyin/search/fetch_vision_search`

1. **搜索用户名或抖音号/Fetch account search list**

- `GET /api/v1/douyin/billboard/fetch_hot_account_search_list`（必填: keyword, cursor）

1. **获取粉丝近3天搜索词 10个搜索词/Fetch fan interest search term in the last 3 days 10 search terms**

- `GET /api/v1/douyin/billboard/fetch_hot_account_fans_interest_search_list`（必填: sec\_uid）

1. **获取搜索热榜/Fetch search hot list**

- `POST /api/v1/douyin/billboard/fetch_hot_total_search_list`

1. **获取热度飙升的搜索榜/Fetch search list with rising popularity**

- `POST /api/v1/douyin/billboard/fetch_hot_total_high_search_list`

1. **关键词搜索kol V1/Search Kol V1**

- `GET /api/v1/douyin/xingtu/search_kol_v1`（必填: keyword, platformSource, page）

1. **高级搜索kol V2/Search Kol Advanced V2**

- `GET /api/v1/douyin/xingtu/search_kol_v2`（必填: keyword）

1. **搜索MCN机构列表/Get Demander MCN List**

- `GET /api/v1/douyin/xingtu_v2/get_demander_mcn_list`

### 工具服务

1. **生成抖音短链接/Generate Douyin short link**
   - `GET /api/v1/douyin/app/v3/generate_douyin_short_url`（必填: url）
2. **生成抖音视频分享二维码/Generate Douyin video share QR code**
   - `GET /api/v1/douyin/app/v3/generate_douyin_video_share_qrcode`（必填: object\_id）
3. **生成抖音分享链接，唤起抖音APP，跳转指定作品详情页/Generate Douyin share link, call Douyin APP, and jump to the specified video details page**
   - `GET /api/v1/douyin/app/v3/open_douyin_app_to_video_detail`（必填: aweme\_id）
4. **生成抖音分享链接，唤起抖音APP，跳转指定用户主页/Generate Douyin share link, call Douyin APP, and jump to the specified user profile**
   - `GET /api/v1/douyin/app/v3/open_douyin_app_to_user_profile`（必填: uid, sec\_uid）
5. **生成抖音分享链接，唤起抖音APP，给指定用户发送私信/Generate Douyin share link, call Douyin APP, and send private messages to specified users**
   - `GET /api/v1/douyin/app/v3/open_douyin_app_to_send_private_message`（必填: uid, sec\_uid）

### 内容解析

1. **提取单个用户id/Extract single user id**
   - `GET /api/v1/douyin/web/get_sec_user_id`（必填: url）
2. **提取列表用户id/Extract list user id**
   - `POST /api/v1/douyin/web/get_all_sec_user_id`
3. **提取单个作品id/Extract single video id**
   - `GET /api/v1/douyin/web/get_aweme_id`（必填: url）
4. **提取列表作品id/Extract list video id**
   - `POST /api/v1/douyin/web/get_all_aweme_id`
5. **提取直播间号/Extract webcast id**
   - `GET /api/v1/douyin/web/get_webcast_id`（必填: url）
6. **提取列表直播间号/Extract list webcast id**
   - `POST /api/v1/douyin/web/get_all_webcast_id`
7. **提取直播间弹幕/Extract live room danmaku**
   - `GET /api/v1/douyin/web/douyin_live_room`（必填: live\_room\_url, danmaku\_type）

### 创作者/达人

1. **获取创作者活动列表/Get creator activity list**
   - `GET /api/v1/douyin/creator/fetch_creator_activity_list`（必填: start\_time, end\_time）
2. **获取创作者活动详情/Get creator activity detail**
   - `GET /api/v1/douyin/creator/fetch_creator_activity_detail`（必填: activity\_id）
3. **获取创作者中心配置/Get creator material center config**
   - `GET /api/v1/douyin/creator/fetch_creator_material_center_config`
4. **获取创作者热门课程/Get creator hot course**
   - `GET /api/v1/douyin/creator/fetch_creator_hot_course`
5. **获取创作者内容创作合集分类/Get creator content creation category**
   - `GET /api/v1/douyin/creator/fetch_creator_content_category`
6. **获取创作者内容创作课程/Get creator content creation course**
   - `GET /api/v1/douyin/creator/fetch_creator_content_course`（必填: category\_id）
7. **获取作品弹幕列表/Get video danmaku list**
   - `GET /api/v1/douyin/creator/fetch_video_danmaku_list`（必填: item\_id）
8. **获取商单任务列表/Get mission task list**
   - `GET /api/v1/douyin/creator/fetch_mission_task_list`
9. **获取行业分类配置/Get industry category config**
   - `GET /api/v1/douyin/creator/fetch_industry_category_config`
10. **获取作品总览数据/Fetch item overview data**

- `POST /api/v1/douyin/creator_v2/fetch_item_overview_data`

1. **获取作品垂类标签/Fetch item analysis involved vertical**

- `POST /api/v1/douyin/creator_v2/fetch_item_analysis_involved_vertical`

1. **获取投稿表现数据/Fetch item analysis item performance**

- `POST /api/v1/douyin/creator_v2/fetch_item_analysis_item_performance`

1. **获取投稿作品列表/Fetch item list**

- `POST /api/v1/douyin/creator_v2/fetch_item_list`

1. **导出投稿作品列表/Download item list**

- `POST /api/v1/douyin/creator_v2/fetch_item_list_download`

1. **获取直播场次历史记录/Fetch live room history list**

- `POST /api/v1/douyin/creator_v2/fetch_live_room_history_list`

1. **获取创作者账号诊断/Fetch author diagnosis**

- `POST /api/v1/douyin/creator_v2/fetch_author_diagnosis`

1. **获取加密图片解析/Get Sign Image**

- `GET /api/v1/douyin/xingtu/get_sign_image`（必填: uri）

1. **根据抖音用户ID获取游客星图kolid/Get XingTu kolid by Douyin User ID**

- `GET /api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`（必填: uid）

1. **根据抖音sec\_user\_id获取游客星图kolid/Get XingTu kolid by Douyin sec\_user\_id**

- `GET /api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`（必填: sec\_user\_id）

1. **根据抖音号获取游客星图kolid/Get XingTu kolid by Douyin unique\_id**

- `GET /api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`（必填: unique\_id）

1. **获取kol基本信息V1/Get kol Base Info V1**

- `GET /api/v1/douyin/xingtu/kol_base_info_v1`（必填: kolId, platformChannel）

1. **获取kol观众画像V1/Get kol Audience Portrait V1**

- `GET /api/v1/douyin/xingtu/kol_audience_portrait_v1`（必填: kolId）

1. **获取kol粉丝画像V1/Get kol Fans Portrait V1**

- `GET /api/v1/douyin/xingtu/kol_fans_portrait_v1`（必填: kolId）

1. **获取kol服务报价V1/Get kol Service Price V1**

- `GET /api/v1/douyin/xingtu/kol_service_price_v1`（必填: kolId, platformChannel）

1. **获取kol数据概览V1/Get kol Data Overview V1**

- `GET /api/v1/douyin/xingtu/kol_data_overview_v1`（必填: kolId, \_type, \_range, flowType）

1. **获取kol视频表现V1/Get kol Video Performance V1**

- `GET /api/v1/douyin/xingtu/kol_video_performance_v1`（必填: kolId, onlyAssign）

1. **获取kol转化视频展示V1/Get kol Convert Video Display V1**

- `GET /api/v1/douyin/xingtu/kol_convert_video_display_v1`（必填: kolId, detailType, page）

1. **获取kol连接用户V1/Get kol Link Struct V1**

- `GET /api/v1/douyin/xingtu/kol_link_struct_v1`（必填: kolId）

1. **获取kol连接用户来源V1/Get kol Touch Distribution V1**

- `GET /api/v1/douyin/xingtu/kol_touch_distribution_v1`（必填: kolId）

1. **获取kol内容表现V1/Get kol Rec Videos V1**

- `GET /api/v1/douyin/xingtu/kol_rec_videos_v1`（必填: kolId）

1. **获取kol粉丝趋势V1/Get kol Daily Fans V1**

- `GET /api/v1/douyin/xingtu/kol_daily_fans_v1`（必填: kolId, startDate, endDate）

1. **获取达人广场筛选字段/Get Author Market Fields**

- `GET /api/v1/douyin/xingtu_v2/get_author_market_fields`

1. **获取创作者基本信息/Get Author Base Info**

- `GET /api/v1/douyin/xingtu_v2/get_author_base_info`（必填: o\_author\_id）

1. **获取创作者商业卡片信息/Get Author Business Card Info**

- `GET /api/v1/douyin/xingtu_v2/get_author_business_card_info`（必填: o\_author\_id）

1. **获取创作者位置信息/Get Author Local Info**

- `GET /api/v1/douyin/xingtu_v2/get_author_local_info`（必填: o\_author\_id）

1. **获取创作者视频列表/Get Author Show Items**

- `GET /api/v1/douyin/xingtu_v2/get_author_show_items`（必填: o\_author\_id）

1. **获取创作者评论热词/Get Author Hot Comment Tokens**

- `GET /api/v1/douyin/xingtu_v2/get_author_hot_comment_tokens`（必填: author\_id）

1. **获取创作者内容热词/Get Author Content Hot Keywords**

- `GET /api/v1/douyin/xingtu_v2/get_author_content_hot_keywords`（必填: author\_id）

1. **获取相似创作者推荐/Get Recommend Similar Star Authors**

- `POST /api/v1/douyin/xingtu_v2/get_recommend_for_star_authors`

1. **获取优秀行业分类列表/Get Excellent Case Category List**

- `GET /api/v1/douyin/xingtu_v2/get_excellent_case_category_list`

1. **获取创作者传播价值/Get Author Spread Info**

- `GET /api/v1/douyin/xingtu_v2/get_author_spread_info`（必填: o\_author\_id）

1. **获取用户主页二维码/Get User Profile QRCode**

- `GET /api/v1/douyin/xingtu_v2/get_user_profile_qrcode`

1. **获取星图IP日历行业列表/Get IP Activity Industry List**

- `GET /api/v1/douyin/xingtu_v2/get_ip_activity_industry_list`

1. **获取星图IP日历活动列表/Get IP Activity List**

- `POST /api/v1/douyin/xingtu_v2/get_ip_activity_list`

1. **获取星图IP活动详情/Get IP Activity Detail**

- `GET /api/v1/douyin/xingtu_v2/get_ip_activity_detail`（必填: id）

1. **获取营销活动案例/Get Resource List**

- `GET /api/v1/douyin/xingtu_v2/get_resource_list`（必填: resource\_id）

## 调用示例 / API Call Examples

### 基础调用 / Basic Call

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/douyin/web/fetch_hot_search_result" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json"
```

### 带参数调用 / Call with Parameters

```bash
curl -X GET "${MAXHUB_BASE_URL}/api/v1/douyin/web/fetch_one_video?aweme_id=123456" \
  -H "x-api-key: $MAXHUB_API_KEY"
```

### POST请求 / POST Request

```bash
curl -X POST "${MAXHUB_BASE_URL}/api/v1/douyin/web/fetch_user_like_videos" \
  -H "x-api-key: $MAXHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sec_user_id": "xxx"}'
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

