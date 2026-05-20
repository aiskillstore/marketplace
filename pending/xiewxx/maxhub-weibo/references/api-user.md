# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_all_groups

`GET /api/v1/weibo/web_v2/fetch_all_groups`

<!-- Full path: /api/v1/weibo/web_v2/fetch_all_groups -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博平台的所有分组信息，包括默认分组和用户自定义分组。
 ### 参数:
 - 无需额外参数
 ### 返回:
 - 分组列表，包含分组ID、名称、容器ID等
 ### 注意:
 - 返回的gid和containerid可用于时间轴接口的参数
 - 分组信息变化不频繁，建议缓存

## fetch_channel_feed

`GET /api/v1/weibo/web/fetch_channel_feed`

<!-- Full path: /api/v1/weibo/web/fetch_channel_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| channel_name | string |  | 频道名称，不传则使用默认频道/Channel name, use default if not provided | 热门 |
| page | integer |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据频道名称获取热门内容（便捷接口）
 ### 参数:
 - channel_name: 频道名称，如 "热门"、"榜单"、"社会" 等，不传则使用默认频道
 - page: 页码，默认1
 ### 返回:
 - 热门微博列表
 ### 说明:
 - 此接口会自动调用 fetch_config_list 获取频道配置，然后获取对应频道的热门内容
 - 如果指定的频道名称不存在，会返回错误信息
 - 可用频道：热门、榜单、同城、社会、科技、明星、电影、音乐、数码、汽车、游戏

## fetch_home_recommend_feed

`GET /api/v1/weibo/app/fetch_home_recommend_feed`

<!-- Full path: /api/v1/weibo/app/fetch_home_recommend_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | string |  | 页码，首页不传，第二页传2 |  |
| count | integer |  | 每页数量 (default: 15) | 15 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博首页推荐Feed流。
 ### 参数:
 - page: 页码，首页不传或传空，第二页传"2"，依次递增
 - count: 每页数量，默认15，最大50
 ### 返回:
 - 首页推荐Feed流数据
 ### 注意:
 - 推荐内容基于热门话题和热点事件

## fetch_user_album

`GET /api/v1/weibo/app/fetch_user_album`

<!-- Full path: /api/v1/weibo/app/fetch_user_album -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 7648703289 |
| since_id | string |  | 翻页游标 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的相册内容。
 ### 参数:
 - uid: 用户ID（必填）
 - since_id: 翻页游标，初次请求不传，后续请求使用返回的since_id值
 ### 返回:
 - 用户相册数据，包含图片列表等信息
 ### 注意:
 - 如果用户设置了隐私保护，可能无法获取相册
 - 使用游标翻页（since_id），不使用页码翻页

## fetch_user_articles

`GET /api/v1/weibo/app/fetch_user_articles`

<!-- Full path: /api/v1/weibo/app/fetch_user_articles -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 1725941200 |
| since_id | string |  | 翻页游标 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的文章列表。
 ### 参数:
 - uid: 用户ID（必填）
 - since_id: 翻页游标，初次请求不传，后续请求使用返回的since_id值
 ### 返回:
 - 用户文章列表数据
 ### 注意:
 - 如果用户没有发布过文章，返回空列表
 - 使用游标翻页（since_id），不使用页码翻页

## fetch_user_audios

`GET /api/v1/weibo/app/fetch_user_audios`

<!-- Full path: /api/v1/weibo/app/fetch_user_audios -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 1725941200 |
| since_id | string |  | 翻页游标 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的音频列表。
 ### 参数:
 - uid: 用户ID（必填）
 - since_id: 翻页游标，初次请求不传，后续请求使用返回的since_id值
 ### 返回:
 - 用户音频列表数据
 ### 注意:
 - 如果用户没有发布过音频，返回空列表
 - 使用游标翻页（since_id），不使用页码翻页

## fetch_user_basic_info

`GET /api/v1/weibo/web_v2/fetch_user_basic_info`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_basic_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 7277477906 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博用户的基本信息（轻量级接口）。
 ### 参数:
 - uid: 用户ID（必填）
 ### 返回:
 - 用户基本信息，包括用户ID、用户名、头像、简介、认证信息
 ### 注意:
 - 与fetch_user_info相比，本接口返回数据更少，响应更快
 - 适合批量用户信息获取和用户卡片展示

## fetch_user_fans

`GET /api/v1/weibo/web_v2/fetch_user_fans`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_fans -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 1722594714 |
| page | integer |  | 页码/Page number (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的粉丝列表（谁关注了该用户）。
 ### 参数:
 - uid: 用户ID（必填）
 - page: 页码，从0开始（默认0）
 ### 返回:
 - 粉丝用户列表，包含用户名、头像、简介、粉丝数等
 ### 注意:
 - 粉丝列表受用户隐私设置影响
 - page参数从0开始，而不是1
 - 与fetch_user_following的区别：本接口获取谁关注了该用户，fetch_user_following获取用户关注了谁

## fetch_user_following

`GET /api/v1/weibo/web_v2/fetch_user_following`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_following -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 1722594714 |
| page | integer |  | 页码/Page number (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的关注列表（该用户关注了谁）。
 ### 参数:
 - uid: 用户ID（必填）
 - page: 页码，从0开始（默认0）
 ### 返回:
 - 关注用户列表，包含用户名、头像、简介、粉丝数等
 ### 注意:
 - 关注列表受用户隐私设置影响
 - page参数从0开始，而不是1
 - 与fetch_user_fans的区别：本接口获取用户关注了谁，fetch_user_fans获取谁关注了该用户

## fetch_user_info

`GET /api/v1/weibo/app/fetch_user_info`

<!-- Full path: /api/v1/weibo/app/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 7648703289 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博用户的基本信息，包括昵称、头像、简介、关注数、粉丝数等。
 ### 参数:
 - uid: 用户ID（必填）
 ### 返回:
 - 用户基本信息数据
 ### 注意:
 - 如果用户设置了隐私保护，部分信息可能无法获取

## fetch_user_info

`GET /api/v1/weibo/app/fetch_user_info`

<!-- Full path: /api/v1/weibo/web/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID/User ID | 2992978081 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微博用户信息
### 参数:
- uid: 用户ID
### 返回:
- 用户信息

## fetch_user_info

`GET /api/v1/weibo/app/fetch_user_info`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string |  | 用户id/User id (default: '') | 1722594714 |
| custom | string |  | 自定义微博用户名/Custom Weibo username (default: '') | shuqi |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博用户的详细信息，包括昵称、头像、简介、关注数、粉丝数等。
 ### 参数:
 - uid: 用户ID（可选，与custom二选一）
 - custom: 自定义用户名（可选，与uid二选一）
 ### 返回:
 - 用户详细信息数据
 ### 注意:
 - uid和custom参数至少需要提供一个
 - 如果同时提供，优先使用uid
 - 建议优先使用uid参数

## fetch_user_profile_feed

`GET /api/v1/weibo/app/fetch_user_profile_feed`

<!-- Full path: /api/v1/weibo/app/fetch_user_profile_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 6580994757 |
| since_id | string |  | 翻页游标 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户主页的动态流。
 ### 参数:
 - uid: 用户ID（必填）
 - since_id: 翻页游标，初次请求不传，后续请求使用返回的since_id值
 ### 返回:
 - 用户主页动态数据
 ### 注意:
 - 如果用户设置了隐私保护，可能无法获取动态
 - 使用游标翻页（since_id），不使用页码翻页

## fetch_user_search

`GET /api/v1/weibo/web_v2/fetch_user_search`

<!-- Full path: /api/v1/weibo/web_v2/fetch_user_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string |  | 搜索关键词/Query（提供则视为“全部”搜索；留空则仅应用高级筛选参数） | yu7 |
| page | integer |  | 页码/Page (default: 1) | 1 |
| region | string |  | 地区编码，从 /city_list 获取/Region code from /city_list | custom:11:1 |
| auth | string |  | 认证类型 org_vip(机构)/per_vip(个人)/ord(普通)/Auth type | org_vip |
| gender | string |  | 性别 man / women / Gender | man |
| age | string |  | 年龄段 18y/22y/29y/39y/40y / Age bucket | 22y |
| nickname | string |  | 昵称筛选/Nickname filter | 张三 |
| tag | string |  | 标签筛选/Tag filter | 摄影 |
| school | string |  | 学校筛选/School filter | 清华大学 |
| work | string |  | 公司筛选/Company filter | 字节跳动 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索微博用户，支持多种筛选条件。
### 参数:
- query: 搜索关键词（可选）
- page: 页码（默认1）
- region: 地区编码，从/fetch_city_list获取（可选）
- auth: 认证类型 org_vip/per_vip/ord（可选）
- gender: 性别 man/women（可选）
- age: 年龄段 18y/22y/29y/39y/40y（可选）
- nickname: 昵称筛选（可选）
- tag: 标签筛选（可选）
- school: 学校筛选（可选）
- work: 公司筛选（可选）
### 返回:
- 用户列表，包含uid、昵称、头像、粉丝数、主页链接
### 注意:
- 筛选参数过多可能导致无结果

## fetch_user_super_topics

`GET /api/v1/weibo/app/fetch_user_super_topics`

<!-- Full path: /api/v1/weibo/app/fetch_user_super_topics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 7648703289 |
| page | integer |  | 页码 (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户参与的超话列表。
 ### 参数:
 - uid: 用户ID（必填）
 - page: 页码，从1开始（默认1）
 ### 返回:
 - 用户参与的超话列表数据
 ### 注意:
 - 如果用户设置了隐私保护，可能无法获取超话列表

## fetch_user_videos

`GET /api/v1/weibo/app/fetch_user_videos`

<!-- Full path: /api/v1/weibo/app/fetch_user_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户ID | 7648703289 |
| since_id | string |  | 翻页游标 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户发布的视频列表（瀑布流展示）。
 ### 参数:
 - uid: 用户ID（必填）
 - since_id: 翻页游标，初次请求不传，后续请求使用返回的since_id值
 ### 返回:
 - 视频列表数据，包含视频标题、封面、播放量等信息
 - 包含 moreInfo.params.since_id 字段用于翻页
 ### 注意:
 - 只返回包含视频的微博
 - 使用游标翻页（since_id），不使用页码翻页

## fetch_video_featured_feed

`GET /api/v1/weibo/app/fetch_video_featured_feed`

<!-- Full path: /api/v1/weibo/app/fetch_video_featured_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| page | string |  | 页码，首页不传，第二页传2 |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微博短视频精选页的Feed流。
 ### 参数:
 - page: 页码，首页不传或传空，第二页传"2"，依次递增
 ### 返回:
 - 短视频精选Feed流数据，包含视频列表等
 ### 注意:
 - 每页返回约20条视频

---

See SKILL.md for cross-group orchestration patterns.