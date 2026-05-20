# Video & Content API / 视频与内容接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---


### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_type | integer | ✅ | 作品类型/Video type | 0 |
| item_id | string | ✅ | 作品id/Video id | 7197598285882789120 |
| cookie | string |  | 可选，默认使用游客Cookie/Optional, use guest Cookie by default |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据视频ID来增加作品的播放数
 - 该接口默认使用游客Cookie，如果需要使用登录用户的Cookie，请在参数中传入。
 - 单一作品每次调用增加1次播放数，请求约 `1000` 次后会被抖音限制，需要等待一段时间（如：2小时后）后再继续调用。
 - 该限制是针对作品的，不是针对接口的，在未登录的情况下，使用不同IP的浏览器或在APP中浏览作品，该作品的播放数也不会增加。
 - 可以携带抖音网页端的Cookie来请求此接口，但是不保证一定有效，需要自行测试。
 - 上述的限制是根据测试结果得出的，具体限制可能会有所不同，仅供参考。
 ### 参数:
 - aweme_type: 作品类型，0:视频 1:图文，可以从单一作品数据接口中获取。
 - item_id: 作品id，别名为aweme_id
 - cookie: 可选，默认使用游客Cookie
 ### 返回:
 - 当前时间戳和状态码，状态码为200时表示成功，否则为失败，可以尝试更换一个作品id再次调用，或者等待一段时间后再次调用。

## douyin_live_room

`GET /api/v1/douyin/web/douyin_live_room`

<!-- Full path: /api/v1/douyin/web/douyin_live_room -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| live_room_url | string | ✅ | 直播间链接/Live room link | https://live.douyin.com/834624950943 |
| danmaku_type | string | ✅ | 消息类型/Message type | WebcastRoomMessage |

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
    - WebcastRoomMessage：直播间消息
    - WebcastLikeMessage：点赞消息
    - WebcastMemberMessage：成员消息
    - WebcastChatMessage：聊天消息
    - WebcastGiftMessage：礼物消息
    - WebcastSocialMessage：社交消息
    - WebcastRoomUserSeqMessage：用户序列消息
    - WebcastUpdateFanTicketMessage：更新粉丝消息
    - WebcastCommonTextMessage：常规文本消息
    - WebcastMatchAgainstScoreMessage：比赛得分消息
    - WebcastFansclubMessage：粉丝俱乐部消息
    - WebcastRanklistHourEntranceMessage：排行榜小时入口消息
    - WebcastRoomStatsMessage：直播间统计消息
    - WebcastLiveShoppingMessage: 直播购物消息
    - WebcastLiveEcomGeneralMessage: 直播电商通用消息
    - WebcastProductChangeMessage: 直播商品变更消息
    - WebcastRoomStreamAdaptationMessage: 直播间流适配消息
    - WebcastNotifyEffectMessage: 通知效果消息
    - WebcastLightGiftMessage: 亮礼物消息
    - WebcastProfitInteractionScoreMessage: 收益互动分消息
    - WebcastRoomRankMessage: 直播间排行消息
### 返回:
 - 弹幕数据的WebSocket连接信息，需要使用WebSocket连接获取弹幕数据，此接口不返回弹幕数据。

## fetch_brand_hot_search_list_detail

`GET /api/v1/douyin/app/v3/fetch_brand_hot_search_list_detail`

<!-- Full path: /api/v1/douyin/app/v3/fetch_brand_hot_search_list_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| category_id | integer | ✅ | 分类id/Category id | 10 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音品牌热榜具体分类数据
### 参数:
- category_id: 分类id
### 返回:
- 品牌热搜榜具体分类数据

## fetch_brand_hot_videos_time_scope

`POST /api/v1/douyin/index/fetch_brand_hot_videos_time_scope`

<!-- Full path: /api/v1/douyin/index/fetch_brand_hot_videos_time_scope -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取品牌热门视频功能可查询的时间范围
 - 用于在请求其他品牌相关接口前确定合法的日期边界
 ### 参数:
 - 无
 ### 返回:
 - 时间范围信息（起止日期、周期单位等）

## fetch_cartoon_aweme

`GET /api/v1/douyin/web/fetch_cartoon_aweme`

<!-- Full path: /api/v1/douyin/web/fetch_cartoon_aweme -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer | ✅ | 每页数量/Number per page | 16 |
| refresh_index | integer |  | 翻页索引/Paging index (default: 1) |  |
| cookie | string |  | 用户自行提供的Cookie/User provided Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 二次元作品
 ### 参数:
 - count: 每页数量，默认为16
 - refresh_index: 翻页索引，默认为1
 - cookie: 用户自行提供的Cookie，推荐使用自己的抖音Cookie，否则在翻页时可能会出现数据重复的问题

游客cookie获取接口：https://api.maxhub.io/api/v1/douyin/web/fetch_douyin_web_guest_cookie
  ### 返回:
 - 二次元作品数据

## fetch_challenge_posts

`POST /api/v1/douyin/web/fetch_challenge_posts`

<!-- Full path: /api/v1/douyin/web/fetch_challenge_posts -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 话题作品
### 参数:
- challenge_id: 话题id
- sort_type: 排序类型
    - 0:综合排序 1:最热排序 2:最新排序
- cursor: 游标
- count: 数量
- cookie: 用户自行提供的Cookie，用于获取更多数据。
### 返回:
- 话题作品

## fetch_challenge_suggest

`POST /api/v1/douyin/search/fetch_challenge_suggest`

<!-- Full path: /api/v1/douyin/search/fetch_challenge_suggest -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中话题(挑战/标签)的推荐搜索结果。
 - 根据输入的关键词，返回相关的话题建议列表，包含话题名称、浏览量等信息。
  ### 备注:
 - 本接口可用于话题联想推荐场景，如输入关键词实时展示相关热门话题。
 - 初次请求时 `cursor` 传入 0，`search_id` 传空字符串。
  ### 参数:
 - keyword: 搜索关键词，如 "游戏"
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "游戏"
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `sug_list[]`: 推荐话题列表
  - `cha_name`: 话题名称（如 "#游戏"）
  - `view_count`: 话题总浏览量
  - `cid`: 话题ID
  - `group_id`: 话题关联的群组ID（可以用于跳转）
  - `tag`: 话题标签分类（0=普通话题，1=流量风向标）
- `status_code`: 状态码（0=成功）
 - `status_msg`: 状态信息（通常为空）
 - `rid`: 请求ID
 - `words_query_record`:
  - `info`: 额外信息（目前为空）
  - `words_source`: 关键词来源（固定"sug"）
  - `query_id`: 查询ID（通常为空）
- `extra`:
  - `now`: 当前服务器时间戳
  - `logid`: 日志ID
  - `fatal_item_ids`: 错误项目ID列表（通常为空）
  - `search_request_id`: 搜索请求ID（通常为空）
- `log_pb`:
  - `impr_id`: 曝光ID（日志追踪用）

## fetch_content_creative_keyword_items

`POST /api/v1/douyin/index/fetch_content_creative_keyword_items`

<!-- Full path: /api/v1/douyin/index/fetch_content_creative_keyword_items -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | string | ✅ | >- |  |
| period | string ('1'/'3'/'7') |  | '时间周期/Period: 1, 3, 7' (default: '7') |  |
| end_date | string | ✅ | >- |  |
| keyword | string | ✅ | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定垂类下、指定热门关键词的相关视频列表
 - 用于查看某个热门关键词具体由哪些视频贡献
 ### 参数:
 - tag_id: 垂类ID（与 fetch_item_query 的 category_id 含义一致）
 - period: 时间周期 "1"=近1天 / "3"=近3天 / "7"=近7天
 - end_date: 结束日期 YYYYMMDD。**仅当 period=7 时必须为周日**（如 20260412），period=1/3
时可为任意日期
 - keyword: 热门关键词（**必须**先调 fetch_content_creative_keywords 拿到关键词列表后选取，
    且 tag_id / period / end_date 三个参数必须与查询关键词时完全一致，否则会返回 "json data error"）
### 返回:
 - 与该关键词相关的视频列表

## fetch_creator_activity_detail

`GET /api/v1/douyin/creator/fetch_creator_activity_detail`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_activity_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| activity_id | string | ✅ | 活动ID/Activity ID | 7545335931785450534 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音创作者活动详情数据
### 参数:
- activity_id: 活动ID（从活动列表接口获取）
### 返回:
- 创作者活动详情数据

## fetch_creator_hot_music_billboard

`GET /api/v1/douyin/creator/fetch_creator_hot_music_billboard`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_hot_music_billboard -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| billboard_tag | integer |  | 榜单标签/Billboard tag (0=全部，具体分类值可通过配置接口获取) (default: 0) | 0 |
| order_key | integer |  | 排序键/Order key (1=播放最高, 2=点赞最多, 4=热度最高, 5=投稿最多) (default: 1) | 1 |
| time_filter | integer |  | 时间筛选/Time filter (1=24小时, 2=7天, 3=30天) (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者平台热门音乐榜单数据
 ### 参数:
 - billboard_tag: 榜单标签，0=全部，其他值请通过配置接口获取
 - order_key: 排序键 (1=播放最高, 2=点赞最多, 4=热度最高, 5=投稿最多)
 - time_filter: 时间筛选 (1=24小时, 2=7天, 3=30天)
 ### 返回:
 - 热门音乐榜单数据

## fetch_creator_material_center_billboard

`GET /api/v1/douyin/creator/fetch_creator_material_center_billboard`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_material_center_billboard -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| billboard_tag | integer |  | >- (default: 0) |  |
| order_key | integer |  | >- (default: 1) |  |
| time_filter | integer |  | >- (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者中心热门视频榜单数据
 ### 参数:
 - billboard_tag: 榜单标签，0=全部，其他值请通过config接口获取
    - 0: 全部
    - 333: 美食
    - 334: 旅行
    - 299: 泛生活
    - 335: 汽车
    - 336: 科技
    - 302: 游戏
    - 296: 二次元
    - 337: 娱乐
    - 311: 明星
    - 298: 体育
    - 300: 文化教育
    - 301: 校园
    - 297: 政务
    - 305: 时尚
    - 306: 才艺
    - 669: 财经
    - 314: 随拍
    - 307: 动植物
    - 309: 图文控
    - 308: 剧情
    - 315: 亲子
    - 718: 三农
    - 310: 创意
    - 312: 户外
    - 926: 公益
- order_key: 排序键
    - 1: 播放最高
    - 2: 点赞最多
    - 3: 评论最多
    - 4: 热度最高
- time_filter: 时间筛选
    - 1: 24小时
    - 2: 7天
    - 3: 30天
### 返回:
 - 创作者中心热门视频榜单数据

## fetch_creator_material_center_related

`GET /api/v1/douyin/creator/fetch_creator_material_center_related`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_material_center_related -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query_id | string | ✅ | 查询ID/Query ID (话题ID/热点ID，从其他榜单接口获取) | 2488260 |
| billboard_type | integer |  | 榜单类型/Billboard type (2=热点, 3=话题, 4=道具, 5=音乐) (default: 2) | 2 |
| limit | integer |  | 每页数量/Items per page (default: 20) | 20 |
| offset | integer |  | 偏移量/Offset (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者中心某个话题/热点/道具/音乐的相关视频列表
 - 通过其他榜单接口（如
fetch_creator_hot_spot_billboard、fetch_creator_hot_topic_billboard）拿到
query_id 后，再用本接口拉取该条目下的相关视频
 ### 参数:
 - query_id: 查询ID（话题ID/热点ID等）
 - billboard_type: 榜单类型
    - 2: 热点
    - 3: 话题
    - 4: 道具
    - 5: 音乐
- limit: 每页数量 (默认 20, 范围 1-100)
 - offset: 偏移量 (分页起始位置)
 ### 返回:
 - 该 query_id 对应的相关视频列表数据

## fetch_daren_great_user_top_video

`POST /api/v1/douyin/index/fetch_daren_great_user_top_video`

<!-- Full path: /api/v1/douyin/index/fetch_daren_great_user_top_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212' |  |
| start_date | string | ✅ | 开始日期/Start date YYYYMMDD |  |
| end_date | string | ✅ | 结束日期/End date YYYYMMDD |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取达人在指定时间范围内的热门视频列表
 ### 参数:
 - user_id: 达人抖音 uid（纯数字，如 "3100268042915212"）
 - start_date: 开始日期，格式 YYYYMMDD
 - end_date: 结束日期，格式 YYYYMMDD
 ### 注意:
 - **日期范围不能超过30天**，否则接口会报错
 ### 返回:
 - 达人热门视频列表（播放量、点赞数等）

## fetch_douyin_web_guest_cookie

`GET /api/v1/douyin/web/fetch_douyin_web_guest_cookie`

<!-- Full path: /api/v1/douyin/web/fetch_douyin_web_guest_cookie -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_agent | string | ✅ | 用户浏览器代理/User browser agent | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音Web的游客Cookie
 - 可以用于爬取抖音Web的数据，如用户作品、合辑作品等。
 - 可以固定身份避免部分接口重复数据。
 - 请注意：游客Cookie无法爬取所有数据，有一定的限制。
 - 可以配合开源项目使用此接口实现抖音Web的数据爬取。
 ### 参数:
 - user_agent: 用户浏览器代理
 ### 返回:
 - 游客Cookie

## fetch_food_aweme

`GET /api/v1/douyin/web/fetch_food_aweme`

<!-- Full path: /api/v1/douyin/web/fetch_food_aweme -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer | ✅ | 每页数量/Number per page | 16 |
| refresh_index | integer |  | 翻页索引/Paging index (default: 1) |  |
| cookie | string |  | 用户自行提供的Cookie/User provided Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 美食作品
 ### 参数:
 - count: 每页数量，默认为16
 - refresh_index: 翻页索引，默认为1
 - cookie: 用户自行提供的Cookie，推荐使用自己的抖音Cookie，否则在翻页时可能会出现数据重复的问题

游客cookie获取接口：https://api.maxhub.io/api/v1/douyin/web/fetch_douyin_web_guest_cookie
  ### 返回:
 - 美食作品数据

## fetch_game_aweme

`GET /api/v1/douyin/web/fetch_game_aweme`

<!-- Full path: /api/v1/douyin/web/fetch_game_aweme -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer | ✅ | 每页数量/Number per page | 16 |
| refresh_index | integer |  | 翻页索引/Paging index (default: 1) |  |
| cookie | string |  | 用户自行提供的Cookie/User provided Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 知识作品
 ### 参数:
 - count: 每页数量，默认为16
 - refresh_index: 翻页索引，默认为1
 - cookie: 用户自行提供的Cookie，推荐使用自己的抖音Cookie，否则在翻页时可能会出现数据重复的问题

游客cookie获取接口：https://api.maxhub.io/api/v1/douyin/web/fetch_douyin_web_guest_cookie
  ### 返回:
 - 游戏作品数据

## fetch_hashtag_detail

`GET /api/v1/douyin/app/v3/fetch_hashtag_detail`

<!-- Full path: /api/v1/douyin/app/v3/fetch_hashtag_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ch_id | integer | ✅ | 话题id/Hashtag id | 1575791821492238 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定话题的详情数据
### 参数:
- ch_id: 话题id
### 返回:
- 话题详情数据

## fetch_hashtag_video_list

`GET /api/v1/douyin/app/v3/fetch_hashtag_video_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_hashtag_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| ch_id | string | ✅ | 话题id/Hashtag id | 1575791821492238 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| sort_type | integer |  | 排序类型/Sort type (default: 0) |  |
| count | integer |  | 数量/Number (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定话题的作品数据
 ### 参数:
 - ch_id: 话题id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - sort_type: 0:综合排序 1:最多点赞 2:最新发布
 - count: 数量，请保持默认，否则会出现BUG。
 ### 返回:
 - 话题作品数据

## fetch_home_feed

`GET /api/v1/douyin/web/fetch_home_feed`

<!-- Full path: /api/v1/douyin/web/fetch_home_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer |  | 数量/Number (default: 10) |  |
| refresh_index | integer |  | 翻页索引/Paging index (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取首页推荐数据
 ### 参数:
 - count: 数量，默认为10，建议保持不变。
 - refresh_index: 翻页索引，默认为0，然后每次增加1用于翻页。
 ### 返回:
 - Feed数据

## fetch_hot_account_item_analysis_list

`GET /api/v1/douyin/billboard/fetch_hot_account_item_analysis_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_account_item_analysis_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_id | MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取账号作品分析
### 参数:
- sec_uid: 用户sec_id
- day: 天数，默认7天
### 返回:
- 账号作品分析

## fetch_hot_calendar_detail

`GET /api/v1/douyin/billboard/fetch_hot_calendar_detail`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_calendar_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| calendar_id | string | ✅ | 活动id | 1720 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取活动日历详情
### 参数:
- calendar_id: 活动id
### 返回:
- 活动日历详情

## fetch_hot_comment_word_list

`GET /api/v1/douyin/billboard/fetch_hot_comment_word_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_comment_word_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id | 7456035425539329340 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取作品评论分析-词云权重
### 参数:
- aweme_id: 作品id
### 返回:
- 作品评论分析-词云权重

## fetch_hot_item_trends_list

`GET /api/v1/douyin/billboard/fetch_hot_item_trends_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_item_trends_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string |  | 作品id (default: '') |  |
| option | integer |  | 选项，7 点赞量 8 分享量 9 评论量 (default: 7) |  |
| date_window | integer |  | 时间窗口，1 按小时 2 按天 (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取作品数据趋势
### 参数:
- aweme_id: 作品id
- option: 选项，7 点赞量 8 分享量 9 评论量
- date_window: 时间窗口，1 按小时 2 按天
### 返回:
- 作品数据趋势

## fetch_hot_total_high_play_list

`POST /api/v1/douyin/billboard/fetch_hot_total_high_play_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_high_play_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取高完播率榜
 ### 参数:
 - page: 页码
 - page_size: 每页数量
 - date_window: 时间窗口，1 按小时 2 按天
 - tags: 子级垂类标签，空则为全部，多个标签需传入
    {"value": "{顶级垂类标签id}", "children": [
        {"value": "{子级垂类标签id}"},
        {"value": "{子级垂类标签id}"}
    ]}
### 返回:
 - 高完播率榜

## fetch_hot_total_hot_word_detail_list

`GET /api/v1/douyin/billboard/fetch_hot_total_hot_word_detail_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_hot_word_detail_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键字 |  |
| word_id | string | ✅ | 内容词id |  |
| query_day | integer | ✅ | 查询日期，格式为YYYYMMDD，需为当日 | 20250105 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取内容词详情
### 参数:
- keyword: 搜索关键字
- word_id: 内容词id
- query_day: 查询日期，格式为YYYYMMDD
### 返回:
- 内容词详情

## fetch_hot_total_video_list

`POST /api/v1/douyin/billboard/fetch_hot_total_video_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_total_video_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频榜
 ### 参数:
 - page: 页码，默认1
 - page_size: 每页数量，默认10
 - date_window: 时间窗口，1 按小时 2 按天
 - sub_type: 榜单分类，1001 视频总榜 1002 低粉爆款 1003 高完播率 1004 高涨粉率 1005 高点赞率
 - tags: 子级垂类标签，空则为全部，多个标签需传入
    {"value": "{顶级垂类标签id}", "children": [
        {"value": "{子级垂类标签id}"},
        {"value": "{子级垂类标签id}"}
    ]}
### 返回:
 - 视频榜

## fetch_hot_user_portrait_list

`GET /api/v1/douyin/billboard/fetch_hot_user_portrait_list`

<!-- Full path: /api/v1/douyin/billboard/fetch_hot_user_portrait_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id | 7456035425539329340 |
| option | integer |  | 选项，1 手机价格分布 2 性别分布 3 年龄分布 4 地域分布-省份 5 地域分布-城市 6 城市等级 7 手机品牌分布 (default: 4) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取作品点赞观众画像
### 参数:
- aweme_id: 作品id
- option: 选项，1 手机价格分布 2 性别分布 3 年龄分布 4 地域分布-省份 5 地域分布-城市 6 城市等级 7 手机品牌分布
### 返回:
- 作品点赞观众画像

## fetch_insight_get_rec

`GET /api/v1/douyin/index/fetch_insight_get_rec`

<!-- Full path: /api/v1/douyin/index/fetch_insight_get_rec -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| report_id | string | ✅ | 报告ID/Report ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据当前报告 ID 获取相关推荐的其他报告
 - 通常用于报告详情页底部的"相关推荐"模块
 ### 参数:
 - report_id: 当前正在查看的报告 ID，从 fetch_report_search 或
    fetch_insight_recommend 获取
### 返回:
 - 相关推荐的报告列表（含 ID、标题、封面、发布时间等）

## fetch_insight_recommend

`GET /api/v1/douyin/index/fetch_insight_recommend`

<!-- Full path: /api/v1/douyin/index/fetch_insight_recommend -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取首页推荐的趋势报告列表
### 返回:
- 推荐报告列表（含报告ID、标题、封面、发布时间等）

## fetch_item_analysis_involved_vertical

`POST /api/v1/douyin/creator_v2/fetch_item_analysis_involved_vertical`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_analysis_involved_vertical -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定时间段内投稿作品涉及的垂类标签
 - 用于后续调用投稿分析接口时的参数
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - start_date: 开始日期，格式YYYYMMDD（必填）
 - end_date: 结束日期，格式YYYYMMDD（必填）
 - **注意：日期范围最多90天**
  ### 返回数据说明:
 - primary_verticals: 垂类标签列表
  - 返回该账号在指定时间段内发布的作品涉及的垂类
  - 例如：["动物", "美食", "旅游"]
 ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_audience_others

`POST /api/v1/douyin/creator_v2/fetch_item_audience_others`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_audience_others -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品的观众其他数据分析，包括受众分布和受众关注词
 - 了解观众是否为粉丝，以及观众关注的兴趣话题
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - item_id: 作品ID（必填）
  ### 返回数据说明:
 - **audience_distribution (受众分布)**:
  - fan_list: 粉丝占比列表
    - key: "1"=粉丝, "0"=非粉丝
    - value: 占比（0-1之间的小数）
 - **audience_keyword (受众关注词)**:
  - keyword_list: 观众关注的话题/关键词列表
    - keyword: 关键词内容
    - value: 该关键词的关注度占比
 ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_audience_portrait

`POST /api/v1/douyin/creator_v2/fetch_item_audience_portrait`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_audience_portrait -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品的观众数据分析
 - 了解观看作品的用户画像特征
 - 包含活跃分布、性别分布、地域分布、年龄分布等多维度数据
 - 帮助创作者精准定位目标受众，优化内容策略
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - item_id: 作品ID（必填）
  ### 返回数据说明:
 返回作品的观众画像数据，包括以下维度：
  **1. 活跃分布 (active)**:
 - key: 活跃时段标识（"2"=上午, "3"=下午, "4"=晚上, "-1"=其他）
 - value: 该时段的活跃用户占比（0-1之间的小数）
  **2. 性别分布 (gender)**:
 - ratio_list: 性别占比列表
  - key: "male"（男性）或 "female"（女性）
  - value: 该性别用户占比（0-1之间的小数）
- tgi_list: 性别TGI指数列表（Target Group Index，目标群体指数）
  - key: 性别标识
  - value: TGI值（100为平均水平，>100表示高于平均）
 **3. 地域分布 (province)**:
 - ratio_list: 省份占比列表
  - key: 省份名称（如"浙江"、"广东"、"北京"）
  - value: 该省份用户占比（0-1之间的小数）
- tgi_list: 省份TGI指数列表
  - key: 省份名称
  - value: TGI值（反映该地区用户的活跃度）
 **4. 年龄分布 (age)**:
 - ratio_list: 年龄段占比列表
  - key: 年龄段（"-18", "18-23", "24-30", "31-40", "41-50", "50-"）
  - value: 该年龄段用户占比（0-1之间的小数）
- tgi_list: 年龄段TGI指数列表
  - key: 年龄段
  - value: TGI值（反映该年龄段用户的偏好度）
 **5. 其他维度**:
 - career: 职业分布（可能为空）
 - city_level: 城市等级分布（包含ratio_list和tgi_list）
 - new_user: 新用户占比（可能为空）
  **TGI指数说明**:
 - TGI = 100: 该群体表现与平台平均水平一致
 - TGI > 100: 该群体在此作品中的占比高于平台平均，是核心受众
 - TGI < 100: 该群体在此作品中的占比低于平台平均
 - TGI越高，说明该群体对此类内容越感兴趣
  **注意**: 如果某些数据为空或占比为0，可能原因：
 - 作品刚发布，样本量不足
 - 该维度暂无数据或数据未达到统计阈值
 - 某些地区或年龄段的用户较少
  ### 数据价值:
 - **精准定位**: 了解核心受众群体特征
 - **内容优化**: 根据受众特点调整内容风格和主题
 - **发布时机**: 根据活跃时间优化发布时间
 - **地域策略**: 针对主要地域用户定制内容
 - **年龄适配**: 调整内容深度和表达方式
 - **性别偏好**: 理解不同性别用户的内容偏好
  ### 应用场景:
 1. **内容定位**: 根据主要受众群体调整内容方向
 2. **发布优化**: 在目标受众活跃时段发布作品
 3. **地域营销**: 针对主要地域用户进行本地化内容创作
 4. **年龄策略**: 根据年龄分布调整内容复杂度和话题
 5. **性别营销**: 平衡或侧重特定性别受众的内容设计
 6. **受众拓展**: 识别潜力受众群体，扩大影响力
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_danmaku_analysis

`POST /api/v1/douyin/creator_v2/fetch_item_danmaku_analysis`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_danmaku_analysis -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品的弹幕分析数据
 - 了解观众在视频各个时间点的弹幕互动情况
 - 帮助创作者识别视频中的热点片段和观众反应
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - item_id: 作品ID（必填）
  ### 返回数据说明:
 返回作品的弹幕分析数据，包括：
 - bullet_distribution: 弹幕分布数据
  - time_point: 时间点（秒）
  - count: 该时间点的弹幕数量
  - percentage: 该时间点弹幕占总弹幕的百分比
- hot_words: 热门弹幕词汇
  - word: 弹幕词汇
  - count: 出现次数
  - sentiment: 情感倾向（正面/负面/中性）
- total_count: 弹幕总数
 - peak_time: 弹幕高峰时间点
  **注意**: 如果返回空数据或弹幕数量为0，说明该作品目前没有弹幕数据，可能原因：
 - 作品刚发布，还没有观众发送弹幕
 - 作品类型不适合弹幕互动
 - 弹幕功能未开启
  ### 数据价值:
 - **热点识别**: 识别观众最感兴趣的视频片段
 - **情感分析**: 了解观众对内容的情感反应
 - **互动优化**: 在高弹幕区域优化内容呈现
 - **内容改进**: 根据弹幕反馈调整后续内容
  ### 应用场景:
 1. **内容优化**: 找出观众最喜欢的片段，在后续视频中强化类似内容
 2. **节奏调整**: 弹幕密集的时间点说明内容吸引人，可以延长类似内容时长
 3. **情感把控**: 通过弹幕情感分析了解观众真实反应
 4. **互动设计**: 在弹幕高峰处设计互动环节，提升参与度
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_filter_options

`GET /api/v1/douyin/index/fetch_item_filter_options`

<!-- Full path: /api/v1/douyin/index/fetch_item_filter_options -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频搜索 `fetch_item_query` 接口支持的所有筛选选项取值
 - 包含：垂类(categories)、时长(duration_types)、类型(label_types)、发布时间(date_types)
 - 调用 `fetch_item_query` 前可先查询本接口获取所需的 ID
 ### 返回:
 - categories:     垂类列表，每项包含 id / name / name_en，id 用于 category_id 参数
 - duration_types: 时长列表，每项包含 id / name / name_en，id 用于 duration_type 参数
 - label_types:    视频类型列表，每项包含 id / name / name_en，id 用于 label_type 参数
 - date_types:     发布时间列表，每项包含 id / name / name_en，id 用于 date_type 参数

## fetch_item_list

`POST /api/v1/douyin/creator_v2/fetch_item_list`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_list -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定时间范围内发布的所有投稿作品列表
 - 支持分页查询，每次最多返回100条数据
 - 数据更新说明：
  - **播放量、点赞量、评论量、分享量、收藏量实时更新**
  - **其他指标每小时更新一次**
- **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - start_time: 开始时间戳，单位毫秒（必填）
 - end_time: 结束时间戳，单位毫秒（必填）
 - count: 每页返回的数量，默认10，最多100（可选）
 - order_by: 排序方式，支持26种排序（可选，默认1）
 - fields: 需要返回的字段，默认 "metrics,review,visibility"（可选）
  - metrics: 流量指标（播放量、点赞量、评论量、分享量、收藏量等）
  - review: 审核状态
  - visibility: 可见性状态
- need_cooperation: 是否需要合作信息，默认true（可选）
 - need_long_article: 是否包含长图文，默认true（可选）
 - cursor: 分页游标，首次请求不传，后续分页使用返回的cursor（可选）
  ### 排序方式详解 (order_by):
  | 值 | 排序字段 | 排序方向 | 更新频率 | 说明 |
 |----|---------|---------|---------|------|
 | 1 | 发布时间 | 从新到旧 ↓ | - | 默认排序，最新发布的在前 |
 | 2 | 发布时间 | 从旧到新 ↑ | - | 最早发布的在前 |
 | 3 | 播放量 | 从高到低 ↓ | 实时 | 作品被观看的次数 |
 | 4 | 播放量 | 从低到高 ↑ | 实时 | 播放量最少的在前 |
 | 5 | 点赞量 | 从高到低 ↓ | 实时 | 作品获得点赞的次数 |
 | 6 | 点赞量 | 从低到高 ↑ | 实时 | 点赞量最少的在前 |
 | 7 | 评论量 | 从高到低 ↓ | 实时 | 作品获得评论的次数 |
 | 8 | 评论量 | 从低到高 ↑ | 实时 | 评论量最少的在前 |
 | 9 | 分享量 | 从高到低 ↓ | 实时 | 作品获得分享的次数 |
 | 10 | 分享量 | 从低到高 ↑ | 实时 | 分享量最少的在前 |
 | 11 | 收藏量 | 从高到低 ↓ | 实时 | 作品获得收藏的次数 |
 | 12 | 收藏量 | 从低到高 ↑ | 实时 | 收藏量最少的在前 |
 | 13 | 2s跳出率 | 从高到低 ↓ | 每小时 | 播放后2s内跳出的播放量/总播放量 |
 | 14 | 2s跳出率 | 从低到高 ↑ | 每小时 | 2s跳出率最低的在前 |
 | 15 | 5s完播率 | 从高到低 ↓ | 每小时 | 播放后超过5s的播放量/总播放量 |
 | 16 | 5s完播率 | 从低到高 ↑ | 每小时 | 5s完播率最低的在前 |
 | 17 | 完播率 | 从高到低 ↓ | 每小时 | 完整播完的播放量/总播放量 |
 | 18 | 完播率 | 从低到高 ↑ | 每小时 | 完播率最低的在前 |
 | 19 | 封面点击率 | 从高到低 ↓ | 每小时 | 作品封面的点击量/曝光量 |
 | 20 | 封面点击率 | 从低到高 ↑ | 每小时 | 封面点击率最低的在前 |
 | 21 | 平均播放时长 | 从高到低 ↓ | 每小时 | 视频被播放的平均时长 |
 | 22 | 平均播放时长 | 从低到高 ↑ | 每小时 | 平均播放时长最短的在前 |
 | 23 | 主页访问量 | 从高到低 ↓ | 每天 | 用户观看作品后访问主页的次数 |
 | 24 | 主页访问量 | 从低到高 ↑ | 每天 | 主页访问量最少的在前 |
 | 25 | 粉丝增量 | 从高到低 ↓ | 每小时 | 观众观看作品后关注作者的数量 |
 | 26 | 粉丝增量 | 从低到高 ↑ | 每小时 | 粉丝增量最少的在前 |
  ### 排序使用建议:
 - **寻找爆款**: 使用 order_by=3 (播放量↓) 或 order_by=5 (点赞量↓)
 - **优化内容**: 使用 order_by=13 (2s跳出率↓) 找出需要优化的作品
 - **提升完播**: 使用 order_by=17 (完播率↓) 分析高完播率作品
 - **涨粉分析**: 使用 order_by=25 (粉丝增量↓) 找出涨粉效果好的作品
 - **封面优化**: 使用 order_by=19 (封面点击率↓) 分析封面吸引力
  ### 返回:
 - 投稿作品列表数据，包含作品的详细指标信息
 - has_more: 是否还有更多数据
 - cursor: 下一页的游标，用于分页查询
 - items: 作品列表数组
  ### 使用流程:
 1. **第一次请求**：不传cursor参数，获取第一页数据
 2. **检查has_more**：如果为true，说明还有更多数据
 3. **分页请求**：使用返回的cursor值作为下次请求的cursor参数
 4. **重复步骤2-3**：直到has_more为false
  ### 功能限制:
 - 仅支持筛选：所选周期内，前100条作品的体裁
 - 如需导出更多数据，请使用 `/fetch_item_list_download` 接口（支持导出前1000条）
  ### 时间戳转换:
 - JavaScript: `new Date('2025-07-01').getTime()` -> 1719763200000
 - Python: `int(datetime(2025, 7, 1).timestamp() * 1000)` ->
1719763200000
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_list_download

`POST /api/v1/douyin/creator_v2/fetch_item_list_download`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_list_download -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 导出指定时间范围内前1000条投稿作品的详细数据
 - 支持按体裁类型筛选导出内容
 - **此接口用于批量导出数据，不适合实时查询**
 - **导出任务为异步处理，需要等待服务器生成文件**
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - min_cursor: 最小游标，即开始时间戳（毫秒）（必填）
 - max_cursor: 最大游标，即结束时间戳（毫秒）（必填）
 - type_filters: 体裁类型过滤列表，默认全选 [1,2,3,4,5,8]（可选）
  - **1**: 1分钟以内视频
  - **2**: 1-3分钟视频
  - **3**: 3-5分钟视频
  - **4**: 5分钟以上视频
  - **5**: 图文作品
  - **8**: 长图文作品
- need_long_article: 是否包含长图文，默认true（可选）
  ### 返回:
 - **直接返回Excel文件流**，浏览器会自动下载
 - 文件名：作品列表导出.xlsx
 - 文件格式：Excel (.xlsx)
 - Content-Type: application/vnd.ms-excel
  ### 使用流程:
 1. **发起导出请求**：提交时间范围和筛选条件
 2. **接收文件**：接口会直接返回Excel文件流
 3. **自动下载**：浏览器会自动触发文件下载
 4. **数据分析**：打开Excel文件进行数据分析
  ### 功能限制:
 - 仅支持导出：所选周期内，前1000条作品的数据
 - 支持按体裁类型筛选（可选择1-6种体裁的任意组合）
 - 不支持实时查询，适合批量数据分析场景
  ### 体裁类型说明:
 | 类型值 | 体裁名称 | 说明 | 使用场景 |
 |-------|---------|------|---------|
 | 1 | 1min以内视频 | 短视频 | 快速传播，高互动 |
 | 2 | 1-3min视频 | 中短视频 | 平衡内容与时长 |
 | 3 | 3-5min视频 | 中长视频 | 深度内容呈现 |
 | 4 | 5min+视频 | 长视频 | 专业内容，深度分析 |
 | 5 | 图文 | 图文作品 | 图片+文字形式 |
 | 8 | 长图文 | 长图文作品 | 深度图文内容 |
  ### 导出数据包含:
 - 作品基本信息（ID、标题、发布时间等）
 - 流量指标（播放量、点赞量、评论量、分享量、收藏量）
 - 审核状态
 - 可见性设置
 - 其他创作者相关数据
  ### 时间戳转换:
 - JavaScript: `new Date('2025-07-01').getTime()` -> 1719763200000
 - Python: `int(datetime(2025, 7, 1).timestamp() * 1000)` ->
1719763200000
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_overview_data

`POST /api/v1/douyin/creator_v2/fetch_item_overview_data`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_overview_data -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品总览数据，包括流量指标、审核状态、播放信息等
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - ids: 作品ID列表，多个ID用逗号分隔（例如: "7559536212910853422,7559536212910853423"）
 - fields: 需要返回的字段，默认为
"metrics,review,play_info,dou_plus,integrated_incentive,incentive_life,content_analysis"
  - 可选字段（用逗号分隔，可自行组合）:
    - metrics: 流量指标数据（播放量、点赞量、评论量等）
    - review: 审核状态信息
    - play_info: 播放相关信息
    - dou_plus: 抖+推广信息
    - integrated_incentive: 综合激励数据
    - incentive_life: 激励生命周期信息
    - content_analysis: 内容分析数据
 ### 返回:
 - 作品总览数据，根据 fields 参数返回对应的字段内容
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_play_source

`POST /api/v1/douyin/creator_v2/fetch_item_play_source`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_play_source -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品的流量来源统计数据
 - 流量来源统计了作品从不同途径播放的占比
 - **若暂时没有看到某个渠道，说明对应渠道暂时没有播放**
 - **作品刚发布推荐页流量占比可能偏低，请等待系统推流**
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - item_id: 作品ID（必填）
  ### 返回数据说明:
 - play_source: 流量来源列表，包含各渠道的播放占比
  - key: 流量来源渠道标识
  - value: 当前占比（0-1之间的小数，如0.85表示85%）
  - history_difference: 与历史数据的差异
  - app_id: 应用ID
 ### 流量来源渠道说明:
 - **homepage_hot**: 推荐页（系统推荐流量）
 - **familiar**: 朋友页（关注的人、好友推荐）
 - **search**: 搜索（用户主动搜索）
 - **homepage**: 个人主页（访问主页观看）
 - **message**: 消息页（通过消息入口）
 - **other**: 其他（其他途径）
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_query

`POST /api/v1/douyin/index/fetch_item_query`

<!-- Full path: /api/v1/douyin/index/fetch_item_query -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword |  |
| category_id | string |  | >- (default: '0') |  |
| date_type | integer |  | >- (default: 0) |  |
| label_type | integer |  | >- (default: 0) |  |
| duration_type | integer |  | >- (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索抖音指数视频库，支持垂类、时长、类型、发布时间四维筛选
 - 结果包含视频基础信息、播放/点赞/粉丝等核心数据
 ### 参数:
 - query: 搜索关键词（必填），例如 "美食"
 - category_id: 垂类ID（字符串），默认 "0"=全部
    - 常用示例：601=剧情, 602=明星, 603=综艺, 604=电影, 605=电视剧, 606=音乐,
      607=二次元, 608=游戏, 609=社会时政, 612=舞蹈, 615=科技, 617=母婴,
      619=生活家居, 628=美食, 629=旅行, 631=时尚, 633=体育, 635=汽车
    - 完整列表（共 36 项，含新增垂类）请调用 `fetch_item_filter_options`
- date_type: 发布时间筛选，默认 0=不限
    - 可选值：0=不限, 3=近3天, 7=近7天, 30=近一个月
- label_type: 视频类型（精选标签），默认 0=不限
    - 可选值：0=不限, 1=低粉爆款, 2=高完播率, 3=高涨粉率, 4=高点赞率
- duration_type: 时长筛选，默认 0=不限
    - 可选值：0=不限, 1=0-15秒, 6=15-60秒, 7=60-120秒, 8=120-180秒, 9=大于180秒
### 注意:
 - 所有筛选参数的完整合法取值可通过 `GET /fetch_item_filter_options` 动态获取，
  避免硬编码过期数据。
### 返回:
 - 视频列表，每项包含：itemId、itemTitle、视频封面、时长、发布时间、
  播放量、点赞数、评论数、分享数、作者ID、作者昵称、作者粉丝数等

## fetch_item_search_keyword

`POST /api/v1/douyin/creator_v2/fetch_item_search_keyword`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_search_keyword -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品的搜索关键词统计数据
 - 了解用户通过哪些搜索关键词找到并观看了该作品
 - 帮助创作者优化内容标题、标签和描述，提升搜索曝光
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - item_id: 作品ID（必填）
  ### 返回数据说明:
 返回用户搜索该作品时使用的关键词列表，包括：
 - keyword: 搜索关键词
 - count: 该关键词被搜索的次数
 - percentage: 该关键词占总搜索量的百分比
  **注意**: 如果返回空列表，说明该作品目前暂无搜索关键词数据，可能原因：
 - 作品刚发布，还没有用户通过搜索观看
 - 作品主要通过推荐、关注等非搜索渠道传播
 - 数据统计周期内没有搜索行为
  ### 数据价值:
 - **优化标题**: 根据热门关键词调整作品标题
 - **优化标签**: 添加相关的热门搜索词作为标签
 - **内容策划**: 了解用户兴趣点，制作更符合需求的内容
 - **SEO优化**: 提升作品在搜索结果中的排名
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_sug

`POST /api/v1/douyin/index/fetch_item_sug`

<!-- Full path: /api/v1/douyin/index/fetch_item_sug -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| query | string | ✅ | 搜索关键词/Search keyword |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取视频搜索的关键词自动补全建议
### 参数:
- query: 搜索关键词
### 返回:
- 匹配的关键词建议列表

## fetch_item_watch_trend

`POST /api/v1/douyin/creator_v2/fetch_item_watch_trend`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_watch_trend -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音作品的观看趋势分析数据
 - 了解用户在观看作品时的行为模式
 - 帮助创作者优化视频内容结构和节奏
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - item_id: 作品ID（必填）
 - analysis_type: 分析类型（可选，默认为1）
  - **1**: 留存分析 - 显示用户在各个时间点的留存情况
  - **2**: 点赞分析 - 显示用户在各个时间点的点赞情况
  - **7**: 跳出分析 - 显示用户在各个时间点的跳出情况
 ### 分析类型说明:
 - **留存分析 (analysis_type=1)**:
  - 展示观众在视频各时间点的留存比例
  - 留存率越高，说明该时间段内容越吸引人
  - **注意**: 播放量超过200后，数据更准确
  - 适合分析：哪些片段吸引观众持续观看
 - **点赞分析 (analysis_type=2)**:
  - 展示观众在视频各时间点的点赞比例
  - 点赞率高的时间点说明该片段特别受欢迎
  - 适合分析：哪些片段最能引发用户互动
 - **跳出分析 (analysis_type=7)**:
  - 展示观众在视频各时间点的跳出比例
  - 跳出率高的时间点可能存在内容问题
  - 适合分析：哪些片段导致观众离开
 ### 返回数据说明:
 - analysis_trend: 趋势分析数据
  - current_item: 当前作品的数据点列表
    - key: 时间点（格式：mm:ss，如 "00:05" 表示第5秒）
    - value: 该时间点的比例值（0-1之间的小数）
  - similar_author: 同类作者的平均数据（用于对比）
    - key: 时间点
    - value: 同类作者在该时间点的平均比例
 ### 数据价值:
 - **内容优化**: 识别观众流失的关键时间点
 - **节奏调整**: 优化视频的起承转合节奏
 - **对比分析**: 与同类作者对比，找出差距和优势
 - **A/B测试**: 测试不同版本的内容效果
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_knowledge_aweme

`GET /api/v1/douyin/web/fetch_knowledge_aweme`

<!-- Full path: /api/v1/douyin/web/fetch_knowledge_aweme -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer | ✅ | 每页数量/Number per page | 16 |
| refresh_index | integer |  | 翻页索引/Paging index (default: 1) |  |
| cookie | string |  | 用户自行提供的Cookie/User provided Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 知识作品
 ### 参数:
 - count: 每页数量，默认为16
 - refresh_index: 翻页索引，默认为1
 - cookie: 用户自行提供的Cookie，推荐使用自己的抖音Cookie，否则在翻页时可能会出现数据重复的问题

游客cookie获取接口：https://api.maxhub.io/api/v1/douyin/web/fetch_douyin_web_guest_cookie
  ### 返回:
 - 知识作品数据

## fetch_live_im_fetch

`GET /api/v1/douyin/web/fetch_live_im_fetch`

<!-- Full path: /api/v1/douyin/web/fetch_live_im_fetch -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间号/Live room id | 7382517534467115826 |
| user_unique_id | string | ✅ | 用户唯一ID/User unique ID | 7382524529011246630 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 抖音直播间弹幕参数获取
### 参数:
- room_id: 直播间号
- user_unique_id: 用户唯一ID
 ### 返回:
- 弹幕参数数据

## fetch_multi_video

`POST /api/v1/douyin/app/v3/fetch_multi_video`

<!-- Full path: /api/v1/douyin/app/v3/fetch_multi_video -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 ### 参数:
 - aweme_ids: 作品id列表，最多支持10个作品id。
 ### 返回:
 - 作品数据
 ### 备注:
 - 如果接口出现返回空的情况，请使用一样的参数去请求 Web 版本接口，具体响应状态码参考：
    - JSON PATH: $.data.filter_list[0].reason
    - 8：该内容因海外版权限制，暂时无法观看（短剧，电影片段等）
    - 8：视频不存在或已被删除
    - 5：该内容被标记为私人内容，没有公开展示权限
    - 10：该内容被标记为部分可见，仅作者选择的部分用户可见
    - 更多状态码请提交给我们的客户支持进行补充。

## fetch_multi_video

`POST /api/v1/douyin/app/v3/fetch_multi_video`

<!-- Full path: /api/v1/douyin/web/fetch_multi_video -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 若此接口失效，请使用APP接口替代。
 ### 参数:
 - aweme_ids: 作品id列表，最多支持50个作品id。
 ### 返回:
 - 作品数据

## fetch_multi_video_high_quality_play_url

`POST /api/v1/douyin/app/v3/fetch_multi_video_high_quality_play_url`

<!-- Full path: /api/v1/douyin/app/v3/fetch_multi_video_high_quality_play_url -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 批量获取视频的最高画质(原始上传画质)播放链接
 - 该接口会返回最高画质的播放链接，原始上传画质是指用户上传视频时的画质，通常最高画质视频无压缩码率并且文件头包含元数据。
 - 最高画质的视频链接无法从抖音APP或网页版直接获取，需要通过此接口获取。
 - 此接口非常适合用于批量获取高清无水印视频链接，适用于需要高质量视频的场景，如视频编辑、存档、训练模型等。
 - 使用并发请求，提高批量获取效率。
 - 最多支持50个视频ID。
 ### 参数:
 - aweme_ids: 作品id列表，用逗号分隔，例如: "123,456,789"，最多50个。
 ### 返回:
 - total: 总数
 - success_count: 成功数量
 - failed_count: 失败数量
 - videos: 视频列表，每个视频包含以下字段：
    - video_id: 作品id
    - original_video_url: 最高画质(原始上传画质)播放链接
    - file_size: 文件大小（字节）
    - file_size_in_mb: 文件大小（MB）
    - content_type: 内容类型
    - success: 是否成功
    - error: 错误信息（如果失败）
### 备注:
 - 由于数量较多，处理时间可能会稍长，请增加等待时间。

## fetch_multi_video_high_quality_play_url

`POST /api/v1/douyin/app/v3/fetch_multi_video_high_quality_play_url`

<!-- Full path: /api/v1/douyin/web/fetch_multi_video_high_quality_play_url -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 批量获取视频的最高画质(原始上传画质)播放链接
 - 该接口会返回最高画质的播放链接，原始上传画质是指用户上传视频时的画质，通常最高画质视频无压缩码率并且文件头包含元数据。
 - 最高画质的视频链接无法从抖音APP或网页版直接获取，需要通过此接口获取。
 - 此接口非常适合用于批量获取高清无水印视频链接，适用于需要高质量视频的场景，如视频编辑、存档、训练模型等。
 - 使用并发请求，提高批量获取效率。
 - 最多支持50个视频ID。
 ### 参数:
 - aweme_ids: 作品id列表，用逗号分隔，例如: "123,456,789"，最多50个。
 ### 返回:
 - total: 总数
 - success_count: 成功数量
 - failed_count: 失败数量
 - videos: 视频列表，每个视频包含以下字段：
    - video_id: 作品id
    - original_video_url: 最高画质(原始上传画质)播放链接
    - file_size: 文件大小（字节）
    - file_size_in_mb: 文件大小（MB）
    - content_type: 内容类型
    - success: 是否成功
    - error: 错误信息（如果失败）
### 备注:
 - 由于数量较多，处理时间可能会稍长，请增加等待时间。

## fetch_multi_video_statistics

`GET /api/v1/douyin/app/v3/fetch_multi_video_statistics`

<!-- Full path: /api/v1/douyin/app/v3/fetch_multi_video_statistics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_ids | string | ✅ | 作品id/Video id | 7448118827402972455,7126745726494821640 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据视频ID获取作品的统计数据，支持多个视频id，一次性最多支持50个视频。
 - 抖音大多数接口已经不再返回作品的播放数，只能通过此接口获取。
 - 价格为：0.025$一次。
 - 可以获取到的统计有：
    - 点赞数（digg_count）
    - 下载数（download_count）
    - 播放数（play_count）
    - 分享数（share_count）
### 参数:
 - aweme_ids: 作品id，支持多个视频id，用逗号隔开即可，不能超过50个，单个也可以，则无需逗号。
 ### 返回:
 - 作品统计数据

## fetch_multi_video_v2

`POST /api/v1/douyin/app/v3/fetch_multi_video_v2`

<!-- Full path: /api/v1/douyin/app/v3/fetch_multi_video_v2 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 ### 参数:
 - aweme_ids: 作品id列表，最多支持50个作品id。
 ### 返回:
 - 作品数据
 ### 备注:
 - 如果接口出现返回空的情况，请使用一样的参数去请求 Web 版本接口，具体响应状态码参考：
    - JSON PATH: $.data.filter_list[0].reason
    - 8：该内容因海外版权限制，暂时无法观看（短剧，电影片段等）
    - 8：视频不存在或已被删除
    - 5：该内容被标记为私人内容，没有公开展示权限
    - 10：该内容被标记为部分可见，仅作者选择的部分用户可见
    - 更多状态码请提交给我们的客户支持进行补充。

## fetch_music_aweme

`GET /api/v1/douyin/web/fetch_music_aweme`

<!-- Full path: /api/v1/douyin/web/fetch_music_aweme -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| count | integer | ✅ | 每页数量/Number per page | 16 |
| refresh_index | integer |  | 翻页索引/Paging index (default: 1) |  |
| cookie | string |  | 用户自行提供的Cookie/User provided Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 音乐作品
 ### 参数:
 - count: 每页数量，默认为16
 - refresh_index: 翻页索引，默认为1
 - cookie: 用户自行提供的Cookie，推荐使用自己的抖音Cookie，否则在翻页时可能会出现数据重复的问题

游客cookie获取接口：https://api.maxhub.io/api/v1/douyin/web/fetch_douyin_web_guest_cookie
  ### 返回:
 - 音乐作品数据

## fetch_music_detail

`GET /api/v1/douyin/app/v3/fetch_music_detail`

<!-- Full path: /api/v1/douyin/app/v3/fetch_music_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| music_id | string | ✅ | 音乐id/Music id | 7136850194742315016 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取指定音乐的详情数据
### 参数:
- music_id: 音乐id
### 返回:
- 音乐详情数据

## fetch_music_hot_search_list

`GET /api/v1/douyin/app/v3/fetch_music_hot_search_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_music_hot_search_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| chart_type | string |  | 榜单类型/Chart type (default: hot) | hot |
| cursor | string |  | 游标/Cursor (default: '0') | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音音乐热榜数据
 ### 参数:
 - chart_type: 榜单类型，默认值为'hot'，支持下面的值：
    - 'hot': 热门榜
    - 'trending': 飙升榜
    - 'original': 原创榜
- cursor: 游标，默认值为'0'，用于分页获取数据，每次请求后会返回下一个游标值，并且通过 `has_more`
字段指示是否有更多数据可供获取。
 ### 返回:
 - 音乐热搜榜数据

## fetch_music_search

`POST /api/v1/douyin/search/fetch_music_search`

<!-- Full path: /api/v1/douyin/search/fetch_music_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中音乐内容的搜索结果。
 - 支持关键词、排序方式、筛选条件等。
  ### 备注:
 - 本接口专注于音乐类内容搜索，不包含其他类型内容。
 - 初次请求时 `cursor` 传 0，`search_id` 传空字符串。
 - 返回内容包含音乐基本信息、作者信息、封面、播放地址、标签等。
  ### 参数:
 - keyword: 搜索关键词，例如 "游戏背景音乐"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（分页时使用）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "游戏背景音乐",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `music`: 音乐结果列表
  - `id_str`: 音乐ID（字符串格式）
  - `title`: 音乐标题
  - `author`: 音乐作者昵称
  - `album`: 所属专辑（如果有）
  - `play_url.url_list`: 音乐播放地址列表
  - `duration`: 音乐时长（秒）
  - `cover_thumb.url_list`: 缩略封面图片列表
  - `cover_medium.url_list`: 中尺寸封面图片列表
  - `cover_large.url_list`: 高清封面图片列表
  - `user_count`: 使用该音乐的作品数量
  - `is_original`: 是否原创音乐
  - `is_commerce_music`: 是否为商业授权音乐
  - `lyric_url`: 歌词文件链接（如果有）
  - `strong_beat_url.url_list`: 音乐节奏点文件链接
  - `tags`: 音乐标签
    - 如：主题（如游戏、Vlog）、情绪（如Funny）、风格（如8-bit, Electronic）
  - `artists`: 音乐关联的创作者列表（如果有）
    - `artist_name`: 艺人昵称
    - `uid`: 艺人UID
  - `cover_color_hsv`: 封面主色调HSV值
  - `can_background_play`: 是否支持后台播放

## fetch_music_video_list

`GET /api/v1/douyin/app/v3/fetch_music_video_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_music_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| music_id | string | ✅ | 音乐id/Music id | 7136850194742315016 |
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
 - count: 数量，请保持默认，否则会出现BUG。
 ### 返回:
 - 音乐视频列表数据

## fetch_one_video

`GET /api/v1/douyin/app/v3/fetch_one_video`

<!-- Full path: /api/v1/douyin/app/v3/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7448118827402972455 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据，支持图文、视频等。
 ### 参数:
 - aweme_id: 作品id
 ### 返回:
 - 作品数据
 ### 备注:
 - 如果接口出现返回空的情况，请使用一样的参数去请求 Web 版本接口，具体响应状态码参考：
    - JSON PATH: $.data.filter_list[0].reason
    - 8：该内容因海外版权限制，暂时无法观看（短剧，电影片段等）
    - 8：视频不存在或已被删除
    - 5：该内容被标记为私人内容，没有公开展示权限
    - 10：该内容被标记为部分可见，仅作者选择的部分用户可见
    - 更多状态码请提交给我们的客户支持进行补充。

## fetch_one_video

`GET /api/v1/douyin/app/v3/fetch_one_video`

<!-- Full path: /api/v1/douyin/web/fetch_one_video -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7372484719365098803 |
| need_anchor_info | boolean |  | 是否需要锚点信息/Whether anchor information is needed (default: false) | false |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据 V1，若此接口失效，请使用 `/fetch_one_video_v2` 接口，或使用APP接口。
 ### 参数:
 - aweme_id: 作品id
 - need_anchor_info:
是否需要锚点信息，默认为False，开启后会看到一些有关视频的锚点信息，如地理位置，商户信息，商品橱窗等，可能会增加接口响应时间。
 - 如果不需要锚点信息，建议保持默认值False，如果接口报错，可以尝试关闭此参数。
 ### 返回:
 - 作品数据

## fetch_one_video_by_share_url

`GET /api/v1/douyin/app/v3/fetch_one_video_by_share_url`

<!-- Full path: /api/v1/douyin/app/v3/fetch_one_video_by_share_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_url | string | ✅ | 分享链接/Share link | https://v.douyin.com/e3x2fjE/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据分享链接获取单个作品数据
 ### 参数:
 - share_url: 分享链接
 ### 返回:
 - 作品数据
 ### 备注:
 - 如果接口出现返回空的情况，请使用一样的参数去请求 Web 版本接口，具体响应状态码参考：
    - JSON PATH: $.data.filter_list[0].reason
    - 8：该内容因海外版权限制，暂时无法观看（短剧，电影片段等）
    - 8：视频不存在或已被删除
    - 5：该内容被标记为私人内容，没有公开展示权限
    - 10：该内容被标记为部分可见，仅作者选择的部分用户可见
    - 更多状态码请提交给我们的客户支持进行补充。

## fetch_one_video_by_share_url

`GET /api/v1/douyin/app/v3/fetch_one_video_by_share_url`

<!-- Full path: /api/v1/douyin/web/fetch_one_video_by_share_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_url | string | ✅ | 分享链接/Share link | https://v.douyin.com/e3x2fjE/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据分享链接获取单个作品数据 （本质上基于 `/fetch_one_video` 接口实现，建议有能力自行获取视频ID以提升接口响应速度）
 - 返回的视频画质比APP接口高一些，但是响应字段没有APP接口多。
 ### 参数:
 - share_url: 分享链接
 ### 返回:
 - 作品数据

## fetch_one_video_danmaku

`GET /api/v1/douyin/web/fetch_one_video_danmaku`

<!-- Full path: /api/v1/douyin/web/fetch_one_video_danmaku -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7355433624046472498 |
| duration | integer | ✅ | 视频总时长/Video total duration | 15134 |
| end_time | integer | ✅ | 结束时间/End time | 15133 |
| start_time | integer | ✅ | 开始时间/Start time | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个作品视频弹幕数据
### 参数:
- item_id: 作品id
- duration: 视频总时长
- end_time: 结束时间
- start_time: 开始时间
### 返回:
- 视频弹幕数据

## fetch_one_video_v2

`GET /api/v1/douyin/app/v3/fetch_one_video_v2`

<!-- Full path: /api/v1/douyin/app/v3/fetch_one_video_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7448118827402972455 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据，支持图文、视频等。
 ### 参数:
 - aweme_id: 作品id
 ### 返回:
 - 作品数据
 ### 备注:
 - 如果接口出现返回空的情况，请使用一样的参数去请求 Web 版本接口，具体响应状态码参考：
    - JSON PATH: $.data.filter_list[0].reason
    - 8：该内容因海外版权限制，暂时无法观看（短剧，电影片段等）
    - 8：视频不存在或已被删除
    - 5：该内容被标记为私人内容，没有公开展示权限
    - 10：该内容被标记为部分可见，仅作者选择的部分用户可见
    - 更多状态码请提交给我们的客户支持进行补充。

## fetch_one_video_v2

`GET /api/v1/douyin/app/v3/fetch_one_video_v2`

<!-- Full path: /api/v1/douyin/web/fetch_one_video_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7372484719365098803 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据 V2，若此接口失效，请使用 `/fetch_one_video` 接口，或使用APP接口。
 ### 参数:
 - aweme_id: 作品id
 ### 返回:
 - 作品数据

## fetch_one_video_v3

`GET /api/v1/douyin/app/v3/fetch_one_video_v3`

<!-- Full path: /api/v1/douyin/app/v3/fetch_one_video_v3 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品或文章ID/Video or Article ID | 7592116912205630761 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取单个作品数据，支持文章、图文、视频等。
 - V3版本的接口，解决了版权限制问题，可以获取更多受限内容，比如 V1，V2版本返回的Reason为8的内容和部分文章或短剧等。
 ### 参数:
 - aweme_id: 作品id
 ### 返回:
 - 作品数据

## fetch_product_review_score

`GET /api/v1/douyin/web/fetch_product_review_score`

<!-- Full path: /api/v1/douyin/web/fetch_product_review_score -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 3770337983790711029 |
| shop_id | string | ✅ | 店铺ID/Shop ID | 129508461 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

## fetch_related_posts

`GET /api/v1/douyin/web/fetch_related_posts`

<!-- Full path: /api/v1/douyin/web/fetch_related_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7393365489105358132 |
| refresh_index | integer |  | 翻页索引/Paging index (default: 1) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取相关作品推荐数据
 ### 参数:
 - aweme_id: 作品id
 - refresh_index: 翻页索引，默认为1，然后每次增加1用于翻页。
 - count: 数量，默认为20，建议保持不变。
 ### 返回:
 - 作品数据

## fetch_report_detail

`GET /api/v1/douyin/index/fetch_report_detail`

<!-- Full path: /api/v1/douyin/index/fetch_report_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| report_id | string | ✅ | '报告ID/Report ID. Example: 1081' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定趋势报告的完整详情
 - 包含报告标题、封面、发布时间、所属产品、正文内容、图片资源、PDF 下载链接等
 ### 参数:
 - report_id: 报告 ID（字符串），可从 fetch_report_search 或 fetch_insight_recommend
    返回结果中获取
### 返回:
 - 报告完整数据：title, cover, publish_time, business, content, images, pdf_url
等

## fetch_search_suggest

`POST /api/v1/douyin/search/fetch_search_suggest`

<!-- Full path: /api/v1/douyin/search/fetch_search_suggest -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中搜索关键词的联想推荐结果。
 - 根据用户输入的关键词，返回相关搜索词建议，用于提升搜索体验。
  ### 备注:
 - 通常用于实现搜索框实时推荐（如输入时下拉补全）。
 - 返回的推荐词经过抖音推荐系统内部打分排序。
  ### 参数:
 - keyword: 输入的关键词，如 "人工智能"
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "人工智能"
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `status_code`: 状态码（0 表示成功）
 - `status_msg`: 返回信息（一般为空）
 - `rid`: 请求ID
 - `sug_list[]`: 搜索建议列表
  - `content`: 推荐的搜索关键词（如 "人工智能ai软件免费版下载"）
  - `sug_type`: 建议类型（一般为空，预留字段）
  - `pos[]`: 匹配位置（标记关键词在原搜索词中的起止位置）
    - `begin`: 开始字符位置
    - `end`: 结束字符位置
  - `word_record`:
    - `group_id`: 推荐词组ID
    - `words_position`: 在本次推荐列表中的位置
    - `words_content`: 词内容（同 `content`）
    - `words_source`: 词来源（通常为 "sug"）
  - `extra_info`:
    - `client_server_extra`: 附加配置信息（JSON字符串）
    - `poi_id`: 关联POI ID（通常为空）
    - `search_params`: 搜索参数（带内部推荐得分）
- `words_query_record`:
  - `info`: 附加信息（通常为空）
  - `words_source`: 推荐来源
  - `query_id`: 推荐查询ID
- `extra`:
  - `now`: 当前服务器时间戳（毫秒）
  - `logid`: 日志ID
  - `fatal_item_ids`: 错误项列表（通常为空）
  - `search_request_id`: 搜索请求ID（通常为空）
- `log_pb`:
  - `impr_id`: 曝光日志ID
- `time_cost`:
  - `stream_inner`: 内部处理耗时（毫秒）
  - `server_engine_cost`: 搜索引擎处理耗时（毫秒）
- `cache_conf`:
  - `enable`: 是否命中缓存（布尔值）

## fetch_series_aweme

`GET /api/v1/douyin/web/fetch_series_aweme`

<!-- Full path: /api/v1/douyin/web/fetch_series_aweme -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| offset | integer | ✅ | 页码/Page number | 0 |
| count | integer | ✅ | 每页数量/Number per page | 16 |
| content_type | integer | ✅ | 短剧类型/Subtype | 0 |
| cookie | string |  | 用户自行提供的Cookie/User provided Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 短剧作品
 ### 参数:
 - offset: 页码，默认为0
 - count: 每页数量，默认为16
 - content_type: 子类型，默认为0
    - 0: 热榜
    - 101: 甜宠
    - 102: 搞笑
    - 104: 正能量
    - 105: 成长
    - 106: 悬疑
    - 109: 家庭
    - 110: 都市
    - 112: 奇幻
    - 113: 玄幻
    - 114: 职场
    - 115: 青春
    - 116: 古装
    - 117: 动作
    - 119: 逆袭
    - 124: 其他
- cookie: 用户自行提供的Cookie，推荐使用自己的抖音Cookie，否则在翻页时可能会出现数据重复的问题

游客cookie获取接口：https://api.maxhub.io/api/v1/douyin/web/fetch_douyin_web_guest_cookie
 ### 返回:
 - 短剧作品数据

## fetch_series_detail

`GET /api/v1/douyin/app/v3/fetch_series_detail`

<!-- Full path: /api/v1/douyin/app/v3/fetch_series_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| series_id | string | ✅ | 短剧id/Series id | 7592054624643713067 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取短剧详情信息
### 参数:
- series_id: 短剧id
### 返回:
- 短剧详情数据
### 备注:
- 该接口返回短剧的详细信息，包括：
    - 短剧名称、描述、封面
    - 作者信息
    - 总集数、更新状态
    - 播放量、收藏量等统计数据
    - 付费信息（如有）

## fetch_series_video_list

`GET /api/v1/douyin/app/v3/fetch_series_video_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_series_video_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| series_id | string | ✅ | 短剧id/Series id | 7592054624643713067 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取短剧视频列表
 ### 参数:
 - series_id: 短剧id
 - cursor: 游标，用于翻页，第一页为0，第二页通常为count的值（如15）。
 ### 返回:
 - 短剧视频列表数据
 ### 备注:
 - 该接口返回短剧中的所有视频列表
 - 响应中的 aweme_list 包含短剧的各集视频信息
 - has_more 字段表示是否还有更多数据

## fetch_user_collection_videos

`POST /api/v1/douyin/web/fetch_user_collection_videos`

<!-- Full path: /api/v1/douyin/web/fetch_user_collection_videos -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户收藏作品数据
 ### 参数:
 - cookie: 用户网页版抖音Cookie(此接口需要用户提供自己的Cookie)
 - max_cursor: 最大游标
 - count: 最大数量
 ### 返回:
 - 用户作品数据

## fetch_user_collects_videos

`GET /api/v1/douyin/web/fetch_user_collects_videos`

<!-- Full path: /api/v1/douyin/web/fetch_user_collects_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| collects_id | string | ✅ | 收藏夹id/Collection id |  |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| counts | integer |  | 每页数量/Number per page (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户收藏夹数据
### 参数:
- collects_id: 收藏夹id
- max_cursor: 最大游标
- count: 最大数量
### 返回:
- 用户作品数据

## fetch_user_like_videos

`GET /api/v1/douyin/app/v3/fetch_user_like_videos`

<!-- Full path: /api/v1/douyin/app/v3/fetch_user_like_videos -->

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

## fetch_user_like_videos

`POST /api/v1/douyin/app/v3/fetch_user_like_videos`

<!-- Full path: /api/v1/douyin/web/fetch_user_like_videos -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户喜欢作品数据
 ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_cursor: 最大游标
 - count: 最大数量
 - cookie: 用户网页版抖音Cookie(此接口需要用户提供自己的Cookie)
 ### 返回:
 - 用户作品数据

## fetch_user_live_videos

`GET /api/v1/douyin/web/fetch_user_live_videos`

<!-- Full path: /api/v1/douyin/web/fetch_user_live_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| webcast_id | string | ✅ | 直播间webcast_id/Room webcast_id | 376034101029 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户直播流数据
### 参数:
- webcast_id: 直播间 webcast_id
- 获取方法：
    - 假设你的直播间链接为：https://www.douyin.com/root/live/376034101029
    - 那么直播间webcast_id为：376034101029
    - webcast_id为直播间链接的最后一段数字，与room_id不同。
### 返回:
- 直播流数据

## fetch_user_live_videos_by_room_id_v2

`GET /api/v1/douyin/web/fetch_user_live_videos_by_room_id_v2`

<!-- Full path: /api/v1/douyin/web/fetch_user_live_videos_by_room_id_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| room_id | string | ✅ | 直播间room_id/Room room_id | 7462723839303093032 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定用户的直播流数据V2
 ### 参数:
 - room_id: 直播间room_id
 ### 返回:
 - 直播流数据
 ### 备注:
 modify_time字段是直播间的最后更新时间，也就相当于开播时间，如果下播也不会重置回0，而是一直保持最后的更新时间。

## fetch_user_live_videos_by_sec_uid

`GET /api/v1/douyin/web/fetch_user_live_videos_by_sec_uid`

<!-- Full path: /api/v1/douyin/web/fetch_user_live_videos_by_sec_uid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_uid | string | ✅ | 用户sec_uid/User sec_uid | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过sec_uid获取指定用户的直播流数据
 ### 参数:
 - sec_uid: 用户sec_uid，也叫 sec_user_id，可以在用户主页链接中找到。
 ### 返回:
 - 直播流数据

## fetch_user_mix_videos

`GET /api/v1/douyin/web/fetch_user_mix_videos`

<!-- Full path: /api/v1/douyin/web/fetch_user_mix_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| mix_id | string | ✅ | 合辑id/Mix id | 7348687990509553679 |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| counts | integer |  | 每页数量/Number per page (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取用户合辑作品数据
### 参数:
- mix_id: 合辑id
- max_cursor: 最大游标
- count: 最大数量
### 返回:
- 用户作品数据

## fetch_user_post_videos

`GET /api/v1/douyin/app/v3/fetch_user_post_videos`

<!-- Full path: /api/v1/douyin/app/v3/fetch_user_post_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 用户sec_user_id/User sec_user_id | MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE |
| max_cursor | integer |  | 最大游标/Maximum cursor (default: 0) |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| sort_type | integer |  | 排序类型/Sort type (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户主页作品数据
 ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_cursor: 最大游标，用于翻页，第一页为0，第二页为第一次响应中的max_cursor值。
 - count: 最大数量，不要超过20，建议保持不变。
 - sort_type: 排序类型，可选值如下：
    - `0`: 最新排序-默认
    - `1`: 最热排序
### 返回:
 - 用户作品数据

## fetch_user_post_videos

`GET /api/v1/douyin/app/v3/fetch_user_post_videos`

<!-- Full path: /api/v1/douyin/web/fetch_user_post_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sec_user_id | string | ✅ | 用户sec_user_id/User sec_user_id | MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE |
| max_cursor | string |  | 最大游标/Maximum cursor (default: '0') |  |
| count | integer |  | 每页数量/Number per page (default: 20) |  |
| filter_type | string |  | 过滤类型/Filter type (default: '0') |  |
| cookie | string |  | 用户网页版抖音Cookie/Your web version of Douyin Cookie |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户主页作品数据
 - 注意：请尽量使用APP的接口而不是WEB的接口，因为WEB的接口可能会被不稳定。
 ### 参数:
 - sec_user_id: 用户sec_user_id
 - max_cursor: 翻页游标，第一次请求传0，然后每次请求传上一次请求返回的max_cursor进行翻页。
 - count: 最大数量，建议不要超过20
 - filter_type: 过滤类型，可选参数如下：
    - 0: 默认排序
    - 3: 热度排序
- cookie: 用户网页版抖音Cookie(此接口可以接受用户提供自己的Cookie)
 ### 返回:
 - 用户作品数据

## fetch_user_series_list

`GET /api/v1/douyin/app/v3/fetch_user_series_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_user_series_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string |  | 用户id/User id (default: '') | 3010877781453635 |
| sec_user_id | string |  | 用户加密id/User sec id (default: '') | >- |
| cursor | integer |  | 游标/Cursor (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取用户的短剧合集列表
 ### 参数:
 - user_id: 用户id，与sec_user_id二选一即可
 - sec_user_id: 用户加密id，与user_id二选一即可
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 ### 返回:
 - 用户短剧合集列表数据
 ### 备注:
 - 该接口返回用户发布的所有短剧合集
 - 响应中的 series_id 可用于获取短剧详情和视频列表

## fetch_video_channel_result

`GET /api/v1/douyin/web/fetch_video_channel_result`

<!-- Full path: /api/v1/douyin/web/fetch_video_channel_result -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| tag_id | integer | ✅ | 标签id/Tag id | 300203 |
| count | integer |  | 数量/Number (default: 10) |  |
| refresh_index | integer |  | 刷新索引/Refresh index (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 抖音视频频道数据
- https://www.douyin.com/channel/300205
### 参数:
- tag_id: 标签id，从URL中获取
- count: 数量
- refresh_index: 刷新索引
### 返回:
- 视频频道数据

## fetch_video_comment_replies

`GET /api/v1/douyin/app/v3/fetch_video_comment_replies`

<!-- Full path: /api/v1/douyin/app/v3/fetch_video_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7354666303006723354 |
| comment_id | string | ✅ | 评论id/Comment id | 7354669356632638218 |
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
 - count: 数量，请保持默认，否则会出现BUG。
 ### 返回:
 - 评论回复数据

## fetch_video_comment_replies

`GET /api/v1/douyin/app/v3/fetch_video_comment_replies`

<!-- Full path: /api/v1/douyin/web/fetch_video_comment_replies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品id/Video id | 7354666303006723354 |
| comment_id | string | ✅ | 评论id/Comment id | 7354669356632638218 |
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
- cursor: 游标
- count: 数量
### 返回:
- 评论回复数据

## fetch_video_comments

`GET /api/v1/douyin/app/v3/fetch_video_comments`

<!-- Full path: /api/v1/douyin/app/v3/fetch_video_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7448118827402972455 |
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
 - count: 数量，请保持默认，否则会出现BUG。
 ### 返回:
 - 评论数据

## fetch_video_comments

`GET /api/v1/douyin/app/v3/fetch_video_comments`

<!-- Full path: /api/v1/douyin/web/fetch_video_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7372484719365098803 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取单个视频评论数据
### 参数:
- aweme_id: 作品id
- cursor: 游标
- count: 数量
### 返回:
- 评论数据

## fetch_video_danmaku_list

`GET /api/v1/douyin/creator/fetch_video_danmaku_list`

<!-- Full path: /api/v1/douyin/creator/fetch_video_danmaku_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| item_id | string | ✅ | 作品ID/Video item ID | 7545659154417896746 |
| count | integer |  | 每页数量/Items per page (default: 20) | 20 |
| offset | integer |  | 偏移量/Offset (starting position) (default: 0) | 0 |
| order_type | integer |  | 排序类型/Order type (1=时间排序, 2=其他排序) (default: 1) | 1 |
| is_blocked | boolean |  | 是否被屏蔽/Is blocked (default: false) | false |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取指定作品的弹幕列表，支持管理和筛选弹幕
 ### 参数:
 - item_id: 作品ID (必需参数，从作品链接或API获取)
 - count: 每页弹幕数量 (建议20，范围1-100)
 - offset: 偏移量 (分页使用，起始位置)
 - order_type: 排序类型 (1=时间排序, 2=其他排序)
 - is_blocked: 是否获取被屏蔽的弹幕 (false=正常弹幕, true=被屏蔽弹幕)
 ### 返回:
 - 作品弹幕列表数据

## fetch_video_high_quality_play_url

`GET /api/v1/douyin/app/v3/fetch_video_high_quality_play_url`

<!-- Full path: /api/v1/douyin/app/v3/fetch_video_high_quality_play_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string |  | 作品id/Video id | 7512756548356492544 |
| share_url | string |  | 可选，分享链接/Optional, share link | https://www.douyin.com/video/7512756548356492544 |
| region | string |  | >- | CN |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频的最高画质(原始上传画质)播放链接
 - 该接口会返回最高画质的播放链接，原始上传画质是指用户上传视频时的画质，通常最高画质视频无压缩码率并且文件头包含元数据。
 - 最高画质的视频链接无法从抖音APP或网页版直接获取，需要通过此接口获取。
 - 此接口非常适合用于获取高清无水印视频链接，适用于需要高质量视频的场景，如视频编辑、存档、训练模型等。
 - 一般情况都可以在线播放，如果不行，可以尝试使用IDM或浏览器下载后播放。
 ### 参数:
 - aweme_id: 作品id，优先使用aweme_id，如果没有则使用share_url。
 - share_url: 可选，分享链接，如果提供了作品id，则此参数可以不传。
 - region: 可选，请求出口地区（ISO 国家代码，如 "CN" / "US" / "HK"）。
    - 抖音服务器会根据请求 IP 返回对应区域的 CDN 域名，
      因此当用户位于**中国大陆**时建议传 `region="CN"` 以拿到国内 CDN 链接，
      下载速度会显著比海外 CDN 更快。
    - 不传则使用本服务出口 IP（通常是海外节点，返回海外 CDN）。
### 返回:
 - video_id： 作品id
 - original_video_url： 最高画质(原始上传画质)播放链接
 - video_data： 视频数据，包含视频的元数据，如时长、大小等。

## fetch_video_high_quality_play_url

`GET /api/v1/douyin/app/v3/fetch_video_high_quality_play_url`

<!-- Full path: /api/v1/douyin/web/fetch_video_high_quality_play_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string |  | 作品id/Video id | 7512756548356492544 |
| share_url | string |  | 可选，分享链接/Optional, share link | https://www.douyin.com/video/7512756548356492544 |
| region | string |  | >- | CN |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取视频的最高画质(原始上传画质)播放链接
 - 该接口会返回最高画质的播放链接，原始上传画质是指用户上传视频时的画质，通常最高画质视频无压缩码率并且文件头包含元数据。
 - 最高画质的视频链接无法从抖音APP或网页版直接获取，需要通过此接口获取。
 - 此接口非常适合用于获取高清无水印视频链接，适用于需要高质量视频的场景，如视频编辑、存档、训练模型等。
 - 一般情况都可以在线播放，如果不行，可以尝试使用IDM或浏览器下载后播放。
 ### 参数:
 - aweme_id: 作品id，优先使用aweme_id，如果没有则使用share_url。
 - share_url: 可选，分享链接，如果提供了作品id，则此参数可以不传。
 - region: 可选，请求出口地区（ISO 国家代码，如 "CN" / "US" / "HK"）。
    - 抖音服务器会根据请求 IP 返回对应区域的 CDN 域名，
      因此当用户位于**中国大陆**时建议传 `region="CN"` 以拿到国内 CDN 链接，
      下载速度会显著比海外 CDN 更快。
    - 不传则使用本服务出口 IP（通常是海外节点，返回海外 CDN）。
### 返回:
 - video_id： 作品id
 - original_video_url： 最高画质(原始上传画质)播放链接
 - video_data： 视频数据，包含视频的元数据，如时长、大小等。

## fetch_video_mix_detail

`GET /api/v1/douyin/app/v3/fetch_video_mix_detail`

<!-- Full path: /api/v1/douyin/app/v3/fetch_video_mix_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| mix_id | string | ✅ | 合集id/Mix id | 7302011174286002217 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音视频合集详情数据
### 参数:
- mix_id: 合集id
### 返回:
- 视频合集详情数据

## fetch_video_mix_post_list

`GET /api/v1/douyin/app/v3/fetch_video_mix_post_list`

<!-- Full path: /api/v1/douyin/app/v3/fetch_video_mix_post_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| mix_id | string | ✅ | 合集id/Mix id | 7302011174286002217 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Number (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音视频合集作品列表数据
 ### 参数:
 - mix_id: 合集id
 - cursor: 游标，用于翻页，第一页为0，第二页为第一次响应中的cursor值。
 - count: 数量，请保持默认，否则会出现BUG。
 ### 返回:
 - 视频合集作品列表数据

## fetch_video_search_v1

`POST /api/v1/douyin/search/fetch_video_search_v1`

<!-- Full path: /api/v1/douyin/search/fetch_video_search_v1 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中通过关键词搜索到的视频内容。
 - 专注于视频内容的搜索结果，不包含其他类型。
  ### 备注:
 - 初次请求时 `cursor` 传 0，`search_id` 传空字符串。
 - 返回的视频包含作者信息、播放地址、封面、互动数据等。
 - 同时返回一组关键词推荐 (`guide_search_words`) 用于引导用户继续搜索。
  ### 参数:
 - keyword: 搜索关键词，例如 "人工智能"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（分页时使用，从上一次响应获取）
 - backtrace: 翻页回溯标识（分页时使用，从上一次响应获取）
  #### 请求体示例：
 ```json
 payload = {
    "keyword": "人工智能",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": "",
    "backtrace": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `status_code`: 响应状态码（0表示成功）
 - `cursor`: 下一页的游标
 - `has_more`: 是否还有更多数据（1=有，0=没有）
 - `data[]`: 搜索到的视频内容列表
  - `type`: 结果类型（通常为 `1`）
  - `aweme_info`: 视频详细信息
    - 基本信息:
      - `aweme_id`: 视频ID
      - `desc`: 视频描述文字
      - `create_time`: 发布时间（时间戳）
    - 作者信息 (`author`):
      - `uid`: 用户ID
      - `nickname`: 昵称
      - `is_verified`: 是否认证
      - `region`: 地区，如 "CN"
      - `avatar_thumb.url_list`: 缩略头像列表
      - `follower_count`: 粉丝数
      - `enterprise_verify_reason`: 企业认证信息（如"央视新闻"）
    - 音乐信息 (`music`):
      - `id_str`: 音乐ID
      - `title`: 音乐标题
      - `author`: 音乐作者
      - `play_url.url_list`: 音乐播放链接
    - 视频播放信息 (`video`):
      - `play_addr.url_list`: 视频播放地址（高清）
      - `cover.url_list`: 视频封面
      - `dynamic_cover.url_list`: 动态封面
      - `origin_cover.url_list`: 原始封面
      - `ratio`: 视频分辨率，如 "720p"
      - `duration`: 视频时长（单位：毫秒）
      - `bit_rate[]`: 不同清晰度播放源
        - `gear_name`: 清晰度名称（如"540_2_2"）
        - `bit_rate`: 比特率
        - `play_addr.url_list`: 对应播放地址
    - 互动数据 (`statistics`):
      - `comment_count`: 评论数
      - `digg_count`: 点赞数
      - `share_count`: 分享数
      - `play_count`: 播放次数
    - 视频状态 (`status`):
      - `is_delete`: 是否删除
      - `is_private`: 是否私密
      - `allow_share`: 是否允许分享
      - `allow_comment`: 是否允许评论
    - 其他字段:
      - `share_url`: 视频分享外链
      - `user_digged`: 用户是否点赞（0=未点赞，1=已点赞）
 - `guide_search_words[]`: 推荐的搜索关键词
  - `id`: 推荐词ID
  - `word`: 推荐的关键词内容
  - `type`: 推荐类型（通常为 `recom`）
  - `query_id`: 推荐请求ID
 - `extra`:
  - `now`: 当前服务器时间戳（毫秒）
  - `logid`: 日志ID

## fetch_video_search_v2

`POST /api/v1/douyin/search/fetch_video_search_v2`

<!-- Full path: /api/v1/douyin/search/fetch_video_search_v2 -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音 App 中通过关键词搜索到的视频内容（V2版本接口）。
 - 相较于 V1，返回字段更加详细，包括作者资料、视频多清晰度播放源、标签列表等。
  ### 备注:
 - 初次请求时 `cursor` 传入0，`search_id`传空字符串。
 - 返回的视频内容丰富，可用于推荐展示、内容抓取、智能分析等应用场景。
  ### 参数:
 - keyword: 搜索关键词，如 "机器人"
 - cursor: 翻页游标（首次请求传 0，翻页时使用上次响应的 cursor）
 - sort_type: 排序方式
    - `0`: 综合排序
    - `1`: 最多点赞
    - `2`: 最新发布
- publish_time: 发布时间筛选
    - `0`: 不限
    - `1`: 最近一天
    - `7`: 最近一周
    - `180`: 最近半年
- filter_duration: 视频时长筛选
    - `0`: 不限
    - `0-1`: 1 分钟以内
    - `1-5`: 1-5 分钟
    - `5-10000`: 5 分钟以上
- content_type: 内容类型筛选
    - `0`: 不限
    - `1`: 视频
    - `2`: 图片
    - `3`: 文章
- search_id: 搜索ID（分页时使用，从上一次响应获取）
 - backtrace: 翻页回溯标识（分页时使用，从上一次响应获取）
  ### 请求体示例：
 ```json
 payload = {
    "keyword": "机器人",
    "cursor": 0,
    "sort_type": "0",
    "publish_time": "0",
    "filter_duration": "0",
    "content_type": "0",
    "search_id": "",
    "backtrace": ""
}
 ```
  ### 返回（部分常用字段，实际返回字段更多，一切以实际响应为准）:
 - `business_data[]`: 搜索返回的数据列表
  - `data_id`: 数据编号（字符串，如 "0"）
  - `type`: 数据类型（1=视频）
  - `data`:
    - `type`: 同上（1）
    - `aweme_info`: 视频详细信息
      - 基础信息:
        - `aweme_id`: 视频ID
        - `desc`: 视频描述
        - `create_time`: 发布时间（时间戳）
      - 作者信息 (`author`):
        - `uid`: 用户唯一ID
        - `short_id`: 用户短ID
        - `nickname`: 用户昵称
        - `signature`: 个性签名
        - `follower_count`: 粉丝数
        - `is_verified`: 是否认证
        - `region`: 地区，如 "CN"
        - `avatar_thumb.url_list`: 小头像URL列表
        - `avatar_medium.url_list`: 中头像URL列表
        - `avatar_larger.url_list`: 大头像URL列表
        - `enterprise_verify_reason`: 企业认证信息（如"店铺账号"）
      - 背景音乐 (`music`):
        - `id_str`: 音乐ID
        - `title`: 音乐标题
        - `author`: 音乐创作者昵称
        - `play_url.url_list`: 音乐播放链接列表
      - 视频播放信息 (`video`):
        - `play_addr.url_list`: 播放地址列表（支持高清播放）
        - `cover.url_list`: 封面图片列表
        - `dynamic_cover.url_list`: 动态封面列表
        - `origin_cover.url_list`: 原始封面列表
        - `duration`: 时长（毫秒）
        - `ratio`: 分辨率（如"720p"）
        - `bit_rate[]`: 多码率播放信息
          - `gear_name`: 清晰度名称（如"540_2_2"）
          - `bit_rate`: 码率（单位bps）
          - `play_addr.url_list`: 对应清晰度播放地址列表
      - 标签列表 (`cha_list[]`):
        - `cha_name`: 话题名（如 "#宇树科技"）
        - `cid`: 话题ID
        - `share_url`: 话题分享链接
      - 统计信息 (`statistics`):
        - `comment_count`: 评论数
        - `digg_count`: 点赞数
        - `share_count`: 分享数
        - `play_count`: 播放次数
        - `collect_count`: 收藏次数
      - 状态信息 (`status`):
        - `is_delete`: 是否被删除
        - `is_private`: 是否私密
        - `allow_share`: 是否允许分享
        - `allow_comment`: 是否允许评论
      - 其他字段:
        - `share_url`: 视频外链
        - `user_digged`: 当前用户是否点赞（0=否，1=是）
 - `cursor`: 翻页游标（用于下次请求）
 - `has_more`: 是否还有更多数据（1=有，0=无）

## fetch_video_statistics

`GET /api/v1/douyin/app/v3/fetch_video_statistics`

<!-- Full path: /api/v1/douyin/app/v3/fetch_video_statistics -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_ids | string | ✅ | 作品id/Video id | 7448118827402972455,7126745726494821640 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据视频ID获取作品的统计数据
 - 抖音大多数接口已经不再返回作品的播放数，只能通过此接口获取。
 - 可以获取到的统计有：
    - 点赞数（digg_count）
    - 下载数（download_count）
    - 播放数（play_count）
    - 分享数（share_count）
### 参数:
 - aweme_ids: 作品id，支持多个视频id，用逗号隔开即可，不能超过2个，单个也可以，则无需逗号。
 ### 返回:
 - 作品统计数据

## generate_a_bogus

`POST /api/v1/douyin/web/generate_a_bogus`

<!-- Full path: /api/v1/douyin/web/generate_a_bogus -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:

使用接口网址生成A-Bogus参数，提交的URL不能带有a_bogus参数，同时a_bogus参数与请求头中的User-Agent有关，需要一起提交和请求。
 ### 参数:
 - url: API链接，请去除url中的原本的a_boogus参数(如有)。
 - data: 请求载荷，只有在POST请求中才需要提交，GET请求中使用空字符串即可。
 - user_agent: user-agent，需要提交你请求头中的User-Agent，该值参与a_bogus参数的计算。
 - index_0: 加密明文列表的第一个值，无特殊要求，默认为0，不要随意修改。
 - index_1: 加密明文列表的第二个值，无特殊要求，默认为1，不要随意修改。
 - index_2: 加密明文列表的第三个值，无特殊要求，默认为14，不要随意修改。
 ### 返回:
 - A-Bogus参数

## generate_douyin_video_share_qrcode

`GET /api/v1/douyin/app/v3/generate_douyin_video_share_qrcode`

<!-- Full path: /api/v1/douyin/app/v3/generate_douyin_video_share_qrcode -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| object_id | string | ✅ | 作品id/Video id | 7348044435755846962 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成抖音视频分享二维码
### 参数:
- object_id: 作品id或作者uid
### 返回:
- 二维码数据

## generate_s_v_web_id

`GET /api/v1/douyin/web/generate_s_v_web_id`

<!-- Full path: /api/v1/douyin/web/generate_s_v_web_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成s_v_web_id
### 返回:
- s_v_web_id

## generate_ttwid

`GET /api/v1/douyin/web/generate_ttwid`

<!-- Full path: /api/v1/douyin/web/generate_ttwid -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_agent | string |  | '' (default: >-) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成ttwid
### 返回:
- ttwid

## generate_verify_fp

`GET /api/v1/douyin/web/generate_verify_fp`

<!-- Full path: /api/v1/douyin/web/generate_verify_fp -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成verify_fp
### 返回:
- verify_fp

## generate_wss_xb_signature

`GET /api/v1/douyin/web/generate_wss_xb_signature`

<!-- Full path: /api/v1/douyin/web/generate_wss_xb_signature -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_agent | string | ✅ | 用户浏览器代理/User browser agent | >- |
| room_id | string | ✅ | 房间号/Room ID | 7382517534467115826 |
| user_unique_id | string | ✅ | 用户唯一ID/User unique ID | 7382524529011246630 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成弹幕xb签名
 ### 参数:
 - user_agent: 用户浏览器代理
 - room_id: 房间号
 - user_unique_id: 用户唯一ID
 ### 返回:
 - 弹幕xb签名

## generate_x_bogus

`POST /api/v1/douyin/web/generate_x_bogus`

<!-- Full path: /api/v1/douyin/web/generate_x_bogus -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 使用接口网址生成X-Bogus参数
 ### 参数:
 - url: 接口网址

## get_all_aweme_id

`POST /api/v1/douyin/web/get_all_aweme_id`

<!-- Full path: /api/v1/douyin/web/get_all_aweme_id -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 提取列表作品id（最多支持20个链接）
 ### 参数:
 - url: 作品链接列表
 ### 返回:
 - 作品id列表

## get_author_show_items

`GET /api/v1/douyin/xingtu_v2/get_author_show_items`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_show_items -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| o_author_id | string | ✅ | 创作者ID/Creator author ID | 7589271892177518598 |
| platform_source | integer |  | 平台来源/Platform source (default: 1) | 1 |
| platform_channel | integer |  | 平台渠道/Platform channel (default: 1) | 1 |
| limit | integer |  | 返回数量/Result limit (default: 10) | 10 |
| only_assign | boolean |  | 仅看指派视频/Only show assigned videos (default: false) | false |
| flow_type | integer |  | 流量类型/Flow type (default: 0) | 0 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取创作者视频列表
 ### 参数:
 - o_author_id: 创作者ID
 - platform_source: 平台来源，默认1
 - platform_channel: 平台渠道，默认1
 - limit: 返回数量，默认10
 - only_assign: 仅看指派视频（只针对星图视频生效），默认False
 - flow_type: 流量类型，默认0
 ### 返回:
 - 创作者视频列表数据

## get_aweme_id

`GET /api/v1/douyin/web/get_aweme_id`

<!-- Full path: /api/v1/douyin/web/get_aweme_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | '' | https://www.douyin.com/video/7298145681699622182 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 提取单个作品id
### 参数:
- url: 作品链接
### 返回:
- 作品id

## get_ip_activity_detail

`GET /api/v1/douyin/xingtu_v2/get_ip_activity_detail`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_ip_activity_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | integer | ✅ | 活动ID，从get_ip_activity_list获取/Activity ID from get_ip_activity_list | 347 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取星图IP日历活动详情
### 参数:
- id: 活动ID，从`get_ip_activity_list`获取
### 返回:
- IP活动详情数据

## get_playlet_actor_rank_catalog

`POST /api/v1/douyin/xingtu_v2/get_playlet_actor_rank_catalog`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_playlet_actor_rank_catalog -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取短剧演员热榜分类列表
### 返回:
- 短剧演员热榜分类数据

## get_playlet_actor_rank_list

`GET /api/v1/douyin/xingtu_v2/get_playlet_actor_rank_list`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_playlet_actor_rank_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| category | string |  | 分类/Category (default: playlet_actor_list) | playlet_actor_list |
| name | string |  | 榜单名称/Ranking name (default: playlet_actor_composite_list) | playlet_actor_composite_list |
| qualifier | string |  | 达人类型，空字符串=不限/Actor type, empty=all (default: '') |  |
| period | integer |  | 统计周期，7=周榜，30=月榜/Period, 7=weekly, 30=monthly (default: 30) | 30 |
| date | string |  | 统计日期，格式YYYYMMDD/Date, format YYYYMMDD (default: '20251130') | 20251130 |
| limit | integer |  | 返回数量/Result limit (default: 100) | 100 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取短剧演员热榜数据
### 参数:
- category: 分类，默认`playlet_actor_list`
- name: 榜单名称，`playlet_actor_composite_list`=综合榜
- qualifier: 达人类型，空字符串=不限
- period: 统计周期，7=周榜，30=月榜
- date: 统计日期，格式YYYYMMDD
- limit: 返回数量，默认100
### 返回:
- 短剧演员热榜数据

## get_recommend_for_star_authors

`POST /api/v1/douyin/xingtu_v2/get_recommend_for_star_authors`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_recommend_for_star_authors -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取相似创作者推荐
### 参数:
- author_ids: 创作者ID列表
- similar_type: 相似类型
    - `comprehension`: 综合相似
    - `content`: 内容相似
    - `audience`: 用户相似
    - `commercial`: 商业能力相似
- page: 页码，默认1
- limit: 每页数量，默认12
### 返回:
- 相似创作者推荐数据

## kol_convert_video_display_v1

`GET /api/v1/douyin/xingtu/kol_convert_video_display_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_convert_video_display_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| detailType | string | ✅ | 详情类型/Detail Type | _1 |
| page | integer | ✅ | 页码/Page | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol转化视频展示V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- detailType: 详情类型, 支持以下参数:
    - _1 :相关视频数据(Video Data)
    - _2 :相关商品数据(Product Data)
### 返回:
 - kol转化视频展示

## kol_rec_videos_v1

`GET /api/v1/douyin/xingtu/kol_rec_videos_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_rec_videos_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol内容表现V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol内容表现

## kol_video_performance_v1

`GET /api/v1/douyin/xingtu/kol_video_performance_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_video_performance_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| onlyAssign | boolean | ✅ | 是否只显示分配作品/Whether to display only assigned works | false |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol视频表现V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- onlyAssign: 是否只显示分配作品，具体参数如下:
    - false : 显示全部，包括个人作品和分配作品，默认值。
    - true : 只显示来自星图的分配作品。
### 返回:
 - kol视频表现

## open_douyin_app_to_send_private_message

`GET /api/v1/douyin/app/v3/open_douyin_app_to_send_private_message`

<!-- Full path: /api/v1/douyin/app/v3/open_douyin_app_to_send_private_message -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| uid | string | ✅ | 用户id/User id | 96874812426 |
| sec_uid | string | ✅ | 用户sec_uid/User sec_uid | MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成抖音分享链接，唤起抖音APP，给指定用户发送私信。
  ### 参数:
 - uid: 用户id
 - sec_uid: 用户sec_uid
 - 注意: 请确保user_id和sec_uid都有值，否则无法发送私信给指定用户。
  ### 返回:
 - 分享链接

## open_douyin_app_to_video_detail

`GET /api/v1/douyin/app/v3/open_douyin_app_to_video_detail`

<!-- Full path: /api/v1/douyin/app/v3/open_douyin_app_to_video_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| aweme_id | string | ✅ | 作品id/Video id | 7348044435755846962 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 生成抖音分享链接，唤起抖音APP，跳转指定作品详情页。
  ### 参数:
 - aweme_id: 作品id
  ### 返回:
 - 分享链接

## register_device

`GET /api/v1/douyin/app/v3/register_device`

<!-- Full path: /api/v1/douyin/app/v3/register_device -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| proxy | string |  | 代理/Proxy (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 抖音APP注册设备，获取设备信息以及设备的Cookie信息。
  ### 参数:
 - proxy: 代理，要带http://或https://，仅支持http代理。
  - 格式: username:password@ip:port
 ### 返回:
 - 设备信息以及设备的Cookie信息。

---

See SKILL.md for cross-group orchestration patterns.