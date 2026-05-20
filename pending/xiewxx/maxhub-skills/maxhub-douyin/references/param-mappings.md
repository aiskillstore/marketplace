# Parameter Mappings / 参数映射

Platform: `douyin` | Base URL: `https://www.aconfig.cn`

---

- `item_id` (string, required): 作品id/Video id — e.g. `7197598285882789120`
- `cookie` (string, optional): 可选，默认使用游客Cookie/Optional, use guest Cookie by default

## author_content_hot_comment_keywords_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## author_hot_comment_tokens_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## douyin_live_room

- `live_room_url` (string, required): 直播间链接/Live room link — e.g. `https://live.douyin.com/834624950943`
- `danmaku_type` (string, required): 消息类型/Message type — e.g. `WebcastRoomMessage`

## encrypt_uid_to_sec_user_id

- `uid` (string, required): 用户uid(short_id)/User uid(short_id) — e.g. `1673937488185292`

## fetch_batch_user_profile_v1

- `sec_user_ids` (string, required): 用户sec_user_id列表，用逗号分隔/User sec_user_id list, separated by commas — e.g. `>-`

## fetch_batch_user_profile_v2

- `sec_user_ids` (string, required): 用户sec_user_id列表，用逗号分隔/User sec_user_id list, separated by commas — e.g. `>-`

## fetch_brand_cycles

- `brand_name` (string, required): 品牌名称/Brand name
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_brand_hot_search_list_detail

- `category_id` (integer, required): 分类id/Category id — e.g. `10`

## fetch_brand_initiative_rank_weekly

- `brand_name` (string, required): 品牌名称/Brand name
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_brand_lines

- `brand_name` (string, required): 品牌名称/Brand name
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_brand_radar_chart

- `brand_name` (string, required): 品牌名称/Brand name
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_brand_suggest

- `keyword` (string, required): 品牌名称关键词/Brand keyword

## fetch_brand_valid_info

- `keyword_list` (string, required): 品牌名称列表逗号分隔/Brand list comma separated

## fetch_cartoon_aweme

- `count` (integer, required): 每页数量/Number per page — e.g. `16`
- `refresh_index` (integer, optional): 翻页索引/Paging index
- `cookie` (string, optional): 用户自行提供的Cookie/User provided Cookie

## fetch_content_author_portrait

- `tag_id` (string, required): >-
- `period` (string, optional): '时间粒度/Period: week or month'
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_content_consume_trend

- `tag_id` (string, required): >-
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_content_consumer_portrait

- `tag_id` (string, required): >-
- `period` (string, optional): '时间粒度/Period: week or month'
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_content_creative_duration

- `tag_id` (string, required): >-
- `period` (string, optional): '时间粒度/Period: week=周, month=月'
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_content_creative_keyword_items

- `tag_id` (string, required): >-
- `period` (string, optional): '时间周期/Period: 1, 3, 7'
- `end_date` (string, required): >-
- `keyword` (string, required): >-

## fetch_content_creative_keywords

- `tag_id` (string, required): >-
- `period` (string, optional): '时间周期/Period: 1=近1天, 3=近3天, 7=近7天'
- `end_date` (string, required): >-

## fetch_content_creative_topic

- `tag_id` (string, required): >-
- `period` (string, optional): '时间周期/Period: 1, 3, 7'
- `end_date` (string, required): >-
- `rank_type` (string, optional): '排序类型/Rank type: index=指数排序, rise=飙升排序'

## fetch_content_interact_trend

- `tag_id` (string, required): >-
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_content_publish_trend

- `tag_id` (string, required): >-
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_creator_activity_detail

- `activity_id` (string, required): 活动ID/Activity ID — e.g. `7545335931785450534`

## fetch_creator_activity_list

- `start_time` (integer, required): 开始时间戳/Start timestamp — e.g. `1756656000`
- `end_time` (integer, required): 结束时间戳/End timestamp — e.g. `1759247999`

## fetch_creator_content_course

- `category_id` (integer, required): 分类ID/Category ID — e.g. `180`
- `order` (integer, optional): 排序方式/Order type (1=推荐排序, 2=最受欢迎, 3=最新上传) — e.g. `1`
- `limit` (integer, optional): 每页数量/Items per page — e.g. `24`
- `offset` (integer, optional): 偏移量/Offset (starting position) — e.g. `0`

## fetch_creator_hot_course

- `order` (integer, optional): 排序方式/Order type (1=推荐排序, 2=最受欢迎, 3=最新上传) — e.g. `1`
- `limit` (integer, optional): 每页数量/Items per page (建议24) — e.g. `24`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `category_id` (string, optional): |-

## fetch_creator_hot_music_billboard

- `billboard_tag` (integer, optional): 榜单标签/Billboard tag (0=全部，具体分类值可通过配置接口获取) — e.g. `0`
- `order_key` (integer, optional): 排序键/Order key (1=播放最高, 2=点赞最多, 4=热度最高, 5=投稿最多) — e.g. `1`
- `time_filter` (integer, optional): 时间筛选/Time filter (1=24小时, 2=7天, 3=30天) — e.g. `1`

## fetch_creator_hot_props_billboard

- `billboard_tag` (integer, optional): >-
- `order_key` (integer, optional): >-
- `time_filter` (integer, optional): >-

## fetch_creator_hot_spot_billboard

- `billboard_tag` (string, optional): >-
- `hot_search_type` (integer, optional): >-
- `city_code` (string, optional): >-

## fetch_creator_hot_topic_billboard

- `billboard_tag` (integer, optional): >-
- `order_key` (integer, optional): >-
- `time_filter` (integer, optional): >-

## fetch_creator_material_center_billboard

- `billboard_tag` (integer, optional): >-
- `order_key` (integer, optional): >-
- `time_filter` (integer, optional): >-

## fetch_creator_material_center_related

- `query_id` (string, required): 查询ID/Query ID (话题ID/热点ID，从其他榜单接口获取) — e.g. `2488260`
- `billboard_type` (integer, optional): 榜单类型/Billboard type (2=热点, 3=话题, 4=道具, 5=音乐) — e.g. `2`
- `limit` (integer, optional): 每页数量/Items per page — e.g. `20`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`

## fetch_daren_compare_users_stable

- `user_list` (string, required): 达人抖音 uid 列表，逗号分隔，最多5个 / Daren uid list, comma separated, max 5
- `days` (string, optional): '天数/Days: 7 or 30'

## fetch_daren_great_item_mile_info

- `user_id` (string, required): '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212'

## fetch_daren_great_user_fans_info

- `user_id` (string, required): '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212'

## fetch_daren_great_user_top_video

- `user_id` (string, required): '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212'
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD

## fetch_daren_similar_users

- `user_id` (string, required): '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212'

## fetch_daren_sug_great_user_list

- `keyword` (string, required): 搜索关键词/Search keyword
- `total` (string, optional): 返回数量/Return count

## fetch_douyin_web_guest_cookie

- `user_agent` (string, required): 用户浏览器代理/User browser agent — e.g. `>-`

## fetch_encrypt_user_id

- `uid` (string, required): '抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212'

## fetch_food_aweme

- `count` (integer, required): 每页数量/Number per page — e.g. `16`
- `refresh_index` (integer, optional): 翻页索引/Paging index
- `cookie` (string, optional): 用户自行提供的Cookie/User provided Cookie

## fetch_game_aweme

- `count` (integer, required): 每页数量/Number per page — e.g. `16`
- `refresh_index` (integer, optional): 翻页索引/Paging index
- `cookie` (string, optional): 用户自行提供的Cookie/User provided Cookie

## fetch_hashtag_detail

- `ch_id` (integer, required): 话题id/Hashtag id — e.g. `1575791821492238`

## fetch_hashtag_video_list

- `ch_id` (string, required): 话题id/Hashtag id — e.g. `1575791821492238`
- `cursor` (integer, optional): 游标/Cursor
- `sort_type` (integer, optional): 排序类型/Sort type
- `count` (integer, optional): 数量/Number

## fetch_home_feed

- `count` (integer, optional): 数量/Number
- `refresh_index` (integer, optional): 翻页索引/Paging index

## fetch_hot_account_fans_interest_account_list

- `sec_uid` (string, required): 用户sec_id — e.g. `MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4`

## fetch_hot_account_fans_interest_search_list

- `sec_uid` (string, required): 用户sec_id — e.g. `MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4`

## fetch_hot_account_fans_interest_topic_list

- `sec_uid` (string, required): 用户sec_id — e.g. `MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4`

## fetch_hot_account_fans_portrait_list

- `sec_uid` (string, required): 用户sec_id — e.g. `MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4`
- `option` (integer, optional): >- — e.g. `1`

## fetch_hot_account_item_analysis_list

- `sec_uid` (string, required): 用户sec_id — e.g. `MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4`

## fetch_hot_account_search_list

- `keyword` (string, required): 搜索的用户名或抖音号 — e.g. `rmrbxmt`
- `cursor` (integer, required): 游标，默认空 — e.g. `0`

## fetch_hot_account_trends_list

- `sec_uid` (string, required): 用户sec_id — e.g. `MS4wLjABAAAA8U_l6rBzmy7bcy6xOJel4v0RzoR_wfAubGPeJimN__4`
- `option` (integer, optional): 选项，2 新增点赞量 3 新增作品量 4 新增评论量 5 新增分享量
- `date_window` (integer, optional): 时间窗口，1 按小时 2 按天 — e.g. `24`

## fetch_hot_calendar_detail

- `calendar_id` (string, required): 活动id — e.g. `1720`

## fetch_hot_category_list

- `billboard_type` (string, required): 榜单类型 — e.g. `rise`
- `snapshot_time` (string, optional): 快照时间 格式yyyyMMddHHmmss
- `start_date` (string, optional): 快照开始时间 格式yyyyMMdd
- `end_date` (string, optional): 快照结束时间 格式yyyyMMdd
- `keyword` (string, optional): 热点搜索词

## fetch_hot_challenge_list

- `page` (integer, required): 页码 — e.g. `1`
- `page_size` (integer, required): 每页数量 — e.g. `10`
- `keyword` (string, optional): 热点搜索词

## fetch_hot_city_list

- `page` (integer, required): 页码 — e.g. `1`
- `page_size` (integer, required): 每页数量 — e.g. `10`
- `order` (string, required): 排序方式
- `city_code` (string, optional): 城市编码，从城市列表获取，空为全部
- `sentence_tag` (string, optional): 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部
- `keyword` (string, optional): 热点搜索词

## fetch_hot_comment_word_list

- `aweme_id` (string, required): 作品id — e.g. `7456035425539329340`

## fetch_hot_item_trends_list

- `aweme_id` (string, optional): 作品id
- `option` (integer, optional): 选项，7 点赞量 8 分享量 9 评论量
- `date_window` (integer, optional): 时间窗口，1 按小时 2 按天

## fetch_hot_rise_list

- `page` (integer, required): 页码 — e.g. `1`
- `page_size` (integer, required): 每页数量 — e.g. `10`
- `order` (string, required): 排序方式 — e.g. `rank`
- `sentence_tag` (string, optional): 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部
- `keyword` (string, optional): 热点搜索词

## fetch_hot_search_list

- `board_type` (string, optional): 榜单类型/Board type
- `board_sub_type` (string, optional): 榜单子类型/Board sub type

## fetch_hot_total_hot_word_detail_list

- `keyword` (string, required): 搜索关键字
- `word_id` (string, required): 内容词id
- `query_day` (integer, required): 查询日期，格式为YYYYMMDD，需为当日 — e.g. `20250105`

## fetch_hot_total_list

- `page` (integer, required): 页码 — e.g. `1`
- `page_size` (integer, required): 每页数量 — e.g. `10`
- `type` (string, required): 快照类型 snapshot 按时刻查看 range 按时间范围
- `snapshot_time` (string, optional): 快照时间 格式yyyyMMddHHmmss
- `start_date` (string, optional): 快照开始时间 格式yyyyMMdd
- `end_date` (string, optional): 快照结束时间 格式yyyyMMdd
- `sentence_tag` (string, optional): 热点分类标签，从热点榜分类获取，多个分类用逗号分隔，空为全部
- `keyword` (string, optional): 热点搜索词

## fetch_hot_user_portrait_list

- `aweme_id` (string, required): 作品id — e.g. `7456035425539329340`
- `option` (integer, optional): 选项，1 手机价格分布 2 性别分布 3 年龄分布 4 地域分布-省份 5 地域分布-城市 6 城市等级 7 手机品牌分布

## fetch_hot_words

- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_insight_get_rec

- `report_id` (string, required): 报告ID/Report ID

## fetch_item_query

- `query` (string, required): 搜索关键词/Search keyword
- `category_id` (string, optional): >-
- `date_type` (integer, optional): >-
- `label_type` (integer, optional): >-
- `duration_type` (integer, optional): >-

## fetch_item_sug

- `query` (string, required): 搜索关键词/Search keyword

## fetch_keyword_valid_date

- `keyword_list` (string, required): 关键词列表，逗号分隔/Keyword list, comma separated

## fetch_knowledge_aweme

- `count` (integer, required): 每页数量/Number per page — e.g. `16`
- `refresh_index` (integer, optional): 翻页索引/Paging index
- `cookie` (string, optional): 用户自行提供的Cookie/User provided Cookie

## fetch_live_gift_ranking

- `room_id` (string, required): 直播间room_id/Room room_id — e.g. `7356585666190461731`
- `rank_type` (integer, optional): 排行类型/Leaderboard type

## fetch_live_im_fetch

- `room_id` (string, required): 直播间号/Live room id — e.g. `7382517534467115826`
- `user_unique_id` (string, required): 用户唯一ID/User unique ID — e.g. `7382524529011246630`

## fetch_live_room_product_result

- `room_id` (string, required): 直播间room_id/Room room_id — e.g. `7360830184578091776`
- `author_id` (string, required): 作者id/Author id — e.g. `1714858898241277`
- `offset` (integer, optional): 偏移量/Offset
- `limit` (integer, optional): 数量/Number

## fetch_mission_task_list

- `cursor` (integer, optional): 游标/Cursor (分页) — e.g. `0`
- `limit` (integer, optional): 每页数量/Items per page — e.g. `24`
- `mission_type` (integer, optional): 任务类型/Mission type — e.g. `1`
- `tab_scene` (integer, optional): 场景类型/Scene type (1=可投稿, 2=可报名, 3=好物测评) — e.g. `1`
- `industry_lv1` (integer, optional): 一级行业/Primary industry (-1=全部) — e.g. `1913`
- `industry_lv2` (integer, optional): 二级行业/Secondary industry (-1=全部) — e.g. `191301`
- `platform_channel` (string, optional): 平台渠道/Platform channel (1=抖音视频, 2=抖音直播, 3=抖音图文) — e.g. `1`
- `pay_type` (string, optional): >- — e.g. `4`
- `greater_than_cost_progress` (string, optional): 成本进度/Cost progress (20=高于20%, 50=高于50%, 80=高于80%) — e.g. `20`
- `publish_time_start` (string, optional): 发布开始时间/Publish start time (时间戳) — e.g. `1757097636`
- `quick_selector_scene` (string, optional): 快速选择场景/Quick selector (1=高收益, 4=保底收入, 5=合作过)
- `keyword` (string, optional): 关键词/Keyword (任务名称或ID)

## fetch_multi_keyword_hot_trend

- `keyword_list` (string, required): 关键词列表，逗号分隔/Keyword list, comma separated
- `start_date` (string, required): 开始日期/Start date, YYYYMMDD
- `end_date` (string, required): 结束日期/End date, YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'
- `region` (string, optional): 地区列表，逗号分隔/Region list, comma separated

## fetch_multi_keyword_interpretation

- `keyword_list` (string, required): 关键词列表，逗号分隔/Keyword list, comma separated
- `start_date` (string, required): 开始日期/Start date, YYYYMMDD
- `end_date` (string, required): 结束日期/End date, YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'
- `region` (string, optional): 地区列表，逗号分隔/Region list, comma separated

## fetch_multi_video_statistics

- `aweme_ids` (string, required): 作品id/Video id — e.g. `7448118827402972455,7126745726494821640`

## fetch_music_aweme

- `count` (integer, required): 每页数量/Number per page — e.g. `16`
- `refresh_index` (integer, optional): 翻页索引/Paging index
- `cookie` (string, optional): 用户自行提供的Cookie/User provided Cookie

## fetch_music_detail

- `music_id` (string, required): 音乐id/Music id — e.g. `7136850194742315016`

## fetch_music_hot_search_list

- `chart_type` (string, optional): 榜单类型/Chart type — e.g. `hot`
- `cursor` (string, optional): 游标/Cursor — e.g. `0`

## fetch_music_video_list

- `music_id` (string, required): 音乐id/Music id — e.g. `7136850194742315016`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_one_video

- `aweme_id` (string, required): 作品id/Video id — e.g. `7448118827402972455`

## fetch_one_video

- `aweme_id` (string, required): 作品id/Video id — e.g. `7372484719365098803`
- `need_anchor_info` (boolean, optional): 是否需要锚点信息/Whether anchor information is needed — e.g. `false`

## fetch_one_video_by_share_url

- `share_url` (string, required): 分享链接/Share link — e.g. `https://v.douyin.com/e3x2fjE/`

## fetch_one_video_by_share_url

- `share_url` (string, required): 分享链接/Share link — e.g. `https://v.douyin.com/e3x2fjE/`

## fetch_one_video_danmaku

- `item_id` (string, required): 作品id/Video id — e.g. `7355433624046472498`
- `duration` (integer, required): 视频总时长/Video total duration — e.g. `15134`
- `end_time` (integer, required): 结束时间/End time — e.g. `15133`
- `start_time` (integer, required): 开始时间/Start time — e.g. `0`

## fetch_one_video_v2

- `aweme_id` (string, required): 作品id/Video id — e.g. `7448118827402972455`

## fetch_one_video_v2

- `aweme_id` (string, required): 作品id/Video id — e.g. `7372484719365098803`

## fetch_one_video_v3

- `aweme_id` (string, required): 作品或文章ID/Video or Article ID — e.g. `7592116912205630761`

## fetch_portrait

- `keyword` (string, required): 关键词/Keyword
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_product_coupon

- `product_id` (string, required): 商品ID/Product ID — e.g. `3770337983790711029`
- `shop_id` (string, required): 店铺ID/Shop ID — e.g. `129508461`
- `price` (string, required): 价格/Price — e.g. `1490`
- `author_id` (string, required): 作者ID/Author ID — e.g. `3109048548866375`
- `sec_user_id` (string, required): 作者ID/Secure Author ID — e.g. `>-`

## fetch_product_review_list

- `product_id` (string, required): 商品ID/Product ID — e.g. `3770337983790711029`
- `shop_id` (string, required): 店铺ID/Shop ID — e.g. `129508461`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Count
- `sort_type` (integer, optional): '排序类型 (0: 默认排序, 1: 最新排序)/Sort Type (0: Default, 1: Latest)'

## fetch_product_review_score

- `product_id` (string, required): 商品ID/Product ID — e.g. `3770337983790711029`
- `shop_id` (string, required): 店铺ID/Shop ID — e.g. `129508461`

## fetch_product_sku_list

- `product_id` (string, required): 商品ID/Product ID — e.g. `3770337983790711029`
- `author_id` (string, required): 作者ID/Author ID — e.g. `3109048548866375`

## fetch_related_posts

- `aweme_id` (string, required): 作品id/Video id — e.g. `7393365489105358132`
- `refresh_index` (integer, optional): 翻页索引/Paging index
- `count` (integer, optional): 数量/Number

## fetch_relation_word

- `keyword` (string, required): 关键词/Keyword
- `start_date` (string, required): 开始日期（周一）/Start date (Monday) YYYYMMDD
- `end_date` (string, required): 结束日期（必须为周日）/End date (must be Sunday) YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_report_detail

- `report_id` (string, required): '报告ID/Report ID. Example: 1081'

## fetch_report_search

- `current_page` (string, optional): 页码/Page number
- `page_size` (string, optional): 每页数量/Page size
- `type` (string, optional): >-
- `business` (string, optional): >-
- `report_time` (string, optional): 发布年份列表，逗号分隔/Year list, comma separated. e.g. 2024,2023
- `search` (string, optional): 报告关键词搜索/Search keyword
- `category` (string, optional): >-

## fetch_series_aweme

- `offset` (integer, required): 页码/Page number — e.g. `0`
- `count` (integer, required): 每页数量/Number per page — e.g. `16`
- `content_type` (integer, required): 短剧类型/Subtype — e.g. `0`
- `cookie` (string, optional): 用户自行提供的Cookie/User provided Cookie

## fetch_series_detail

- `series_id` (string, required): 短剧id/Series id — e.g. `7592054624643713067`

## fetch_series_video_list

- `series_id` (string, required): 短剧id/Series id — e.g. `7592054624643713067`
- `cursor` (integer, optional): 游标/Cursor

## fetch_share_info_by_share_code

- `share_code` (string, required): 分享口令/Share code — e.g. `8:/ h@O.kP 05/21 【生意场上，装逼就是节省沟通成本】长按复制打开抖音，即可阅读文章 ︽︽2QnCB9aIZZ29︽︽`

## fetch_topic_query

- `keyword` (string, required): 话题关键词/Topic keyword
- `start_date` (string, required): 开始日期/Start date YYYYMMDD
- `end_date` (string, required): 结束日期/End date YYYYMMDD
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_topic_suggest

- `keyword` (string, required): 话题关键词/Topic keyword
- `app_name` (string, optional): '平台/Platform: aweme(抖音), toutiao(头条)'

## fetch_user_collects_videos

- `collects_id` (string, required): 收藏夹id/Collection id
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `counts` (integer, optional): 每页数量/Number per page

## fetch_user_fans_list

- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id
- `max_time` (string, optional): 最大时间戳/Maximum timestamp
- `count` (integer, optional): 数量/Number

## fetch_user_fans_list

- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id
- `max_time` (string, optional): 最大时间戳/Maximum timestamp
- `count` (integer, optional): 数量/Number
- `source_type` (integer, optional): 来源类型/Source type

## fetch_user_following_list

- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id
- `max_time` (string, optional): 最大时间戳/Maximum timestamp
- `count` (integer, optional): 数量/Number
- `source_type` (integer, optional): 来源类型/Source type

## fetch_user_like_videos

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `>-`
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `counts` (integer, optional): 每页数量/Number per page

## fetch_user_live_info_by_uid

- `uid` (string, required): 用户UID/User UID — e.g. `3081254195702747`

## fetch_user_live_videos

- `webcast_id` (string, required): 直播间webcast_id/Room webcast_id — e.g. `376034101029`

## fetch_user_live_videos_by_room_id_v2

- `room_id` (string, required): 直播间room_id/Room room_id — e.g. `7462723839303093032`

## fetch_user_live_videos_by_sec_uid

- `sec_uid` (string, required): 用户sec_uid/User sec_uid — e.g. `>-`

## fetch_user_mix_videos

- `mix_id` (string, required): 合辑id/Mix id — e.g. `7348687990509553679`
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `counts` (integer, optional): 每页数量/Number per page

## fetch_user_post_videos

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE`
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `count` (integer, optional): 每页数量/Number per page
- `sort_type` (integer, optional): 排序类型/Sort type

## fetch_user_post_videos

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE`
- `max_cursor` (string, optional): 最大游标/Maximum cursor
- `count` (integer, optional): 每页数量/Number per page
- `filter_type` (string, optional): 过滤类型/Filter type
- `cookie` (string, optional): 用户网页版抖音Cookie/Your web version of Douyin Cookie

## fetch_user_profile_by_short_id

- `short_id` (string, required): 用户Short ID/User Short ID — e.g. `114131058`

## fetch_user_profile_by_uid

- `uid` (string, required): 用户UID/User UID — e.g. `68141954464`

## fetch_user_search

- `user_name` (string, required): 用户名/Username (支持抖音号和抖音昵称) — e.g. `Y`

## fetch_user_series_list

- `user_id` (string, optional): 用户id/User id — e.g. `3010877781453635`
- `sec_user_id` (string, optional): 用户加密id/User sec id — e.g. `>-`
- `cursor` (integer, optional): 游标/Cursor

## fetch_video_channel_result

- `tag_id` (integer, required): 标签id/Tag id — e.g. `300203`
- `count` (integer, optional): 数量/Number
- `refresh_index` (integer, optional): 刷新索引/Refresh index

## fetch_video_comment_replies

- `item_id` (string, required): 作品id/Video id — e.g. `7354666303006723354`
- `comment_id` (string, required): 评论id/Comment id — e.g. `7354669356632638218`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_comment_replies

- `item_id` (string, required): 作品id/Video id — e.g. `7354666303006723354`
- `comment_id` (string, required): 评论id/Comment id — e.g. `7354669356632638218`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_comments

- `aweme_id` (string, required): 作品id/Video id — e.g. `7448118827402972455`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_comments

- `aweme_id` (string, required): 作品id/Video id — e.g. `7372484719365098803`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_danmaku_list

- `item_id` (string, required): 作品ID/Video item ID — e.g. `7545659154417896746`
- `count` (integer, optional): 每页数量/Items per page — e.g. `20`
- `offset` (integer, optional): 偏移量/Offset (starting position) — e.g. `0`
- `order_type` (integer, optional): 排序类型/Order type (1=时间排序, 2=其他排序) — e.g. `1`
- `is_blocked` (boolean, optional): 是否被屏蔽/Is blocked — e.g. `false`

## fetch_video_high_quality_play_url

- `aweme_id` (string, optional): 作品id/Video id — e.g. `7512756548356492544`
- `share_url` (string, optional): 可选，分享链接/Optional, share link — e.g. `https://www.douyin.com/video/7512756548356492544`
- `region` (string, optional): >- — e.g. `CN`

## fetch_video_high_quality_play_url

- `aweme_id` (string, optional): 作品id/Video id — e.g. `7512756548356492544`
- `share_url` (string, optional): 可选，分享链接/Optional, share link — e.g. `https://www.douyin.com/video/7512756548356492544`
- `region` (string, optional): >- — e.g. `CN`

## fetch_video_mix_detail

- `mix_id` (string, required): 合集id/Mix id — e.g. `7302011174286002217`

## fetch_video_mix_post_list

- `mix_id` (string, required): 合集id/Mix id — e.g. `7302011174286002217`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_statistics

- `aweme_ids` (string, required): 作品id/Video id — e.g. `7448118827402972455,7126745726494821640`

## generate_douyin_short_url

- `url` (string, required): 抖音链接/Douyin link — e.g. `https://www.douyin.com/passport/web/logout/`

## generate_douyin_video_share_qrcode

- `object_id` (string, required): 作品id/Video id — e.g. `7348044435755846962`

## generate_ttwid

- `user_agent` (string, optional): ''

## generate_wss_xb_signature

- `user_agent` (string, required): 用户浏览器代理/User browser agent — e.g. `>-`
- `room_id` (string, required): 房间号/Room ID — e.g. `7382517534467115826`
- `user_unique_id` (string, required): 用户唯一ID/User unique ID — e.g. `7382524529011246630`

## get_author_base_info

- `o_author_id` (string, required): 创作者ID/Creator author ID — e.g. `7589271892177518598`
- `platform_source` (integer, optional): 平台来源/Platform source — e.g. `1`
- `platform_channel` (integer, optional): 平台渠道/Platform channel — e.g. `1`
- `recommend` (boolean, optional): 是否返回推荐信息/Whether to return recommendation info — e.g. `true`
- `need_sec_uid` (boolean, optional): 是否返回sec_uid/Whether to return sec_uid — e.g. `true`
- `need_linkage_info` (boolean, optional): 是否返回联动信息/Whether to return linkage info — e.g. `true`

## get_author_business_card_info

- `o_author_id` (string, required): 创作者ID/Creator author ID — e.g. `7589271892177518598`

## get_author_content_hot_keywords

- `author_id` (string, required): 创作者ID/Creator author ID — e.g. `7589271892177518598`
- `keyword_type` (integer, optional): 热词类型/Keyword type — e.g. `0`

## get_author_hot_comment_tokens

- `author_id` (string, required): 创作者ID/Creator author ID — e.g. `7589271892177518598`
- `num` (integer, optional): 返回热词数量/Number of hot tokens — e.g. `10`
- `without_emoji` (boolean, optional): 是否排除emoji/Whether to exclude emoji — e.g. `true`

## get_author_local_info

- `o_author_id` (string, required): 创作者ID/Creator author ID — e.g. `7146074596666507300`
- `platform_source` (integer, optional): 平台来源/Platform source — e.g. `1`
- `platform_channel` (integer, optional): 平台渠道/Platform channel — e.g. `1`
- `time_range` (integer, optional): 时间范围(天)/Time range in days — e.g. `30`

## get_author_market_fields

- `market_scene` (integer, optional): 市场场景，1=默认场景/Market scene, 1=default — e.g. `1`

## get_author_show_items

- `o_author_id` (string, required): 创作者ID/Creator author ID — e.g. `7589271892177518598`
- `platform_source` (integer, optional): 平台来源/Platform source — e.g. `1`
- `platform_channel` (integer, optional): 平台渠道/Platform channel — e.g. `1`
- `limit` (integer, optional): 返回数量/Result limit — e.g. `10`
- `only_assign` (boolean, optional): 仅看指派视频/Only show assigned videos — e.g. `false`
- `flow_type` (integer, optional): 流量类型/Flow type — e.g. `0`

## get_author_spread_info

- `o_author_id` (string, required): 创作者ID/Creator author ID — e.g. `7589271892177518598`
- `platform_source` (integer, optional): 平台来源/Platform source — e.g. `1`
- `platform_channel` (integer, optional): 平台渠道/Platform channel — e.g. `1`
- `type` (integer, optional): 视频类型，1=个人视频/Video type, 1=personal video — e.g. `1`
- `flow_type` (integer, optional): 流量类型/Flow type — e.g. `0`
- `only_assign` (boolean, optional): 仅看指派视频/Only assigned videos — e.g. `false`
- `range` (integer, optional): 时间范围，2=近30天，3=近90天/Time range, 2=last 30 days, 3=last 90 days — e.g. `2`

## get_aweme_id

- `url` (string, required): '' — e.g. `https://www.douyin.com/video/7298145681699622182`

## get_demander_mcn_list

- `mcn_name` (string, optional): MCN机构名称，支持模糊搜索/MCN name, supports fuzzy search
- `page` (integer, optional): 页码/Page number — e.g. `1`
- `limit` (integer, optional): 每页数量/Page size — e.g. `20`
- `order_by` (string, optional): 排序方式/Sort by — e.g. `platform_scores`

## get_excellent_case_category_list

- `platform_source` (integer, optional): 平台来源/Platform source — e.g. `1`

## get_ip_activity_detail

- `id` (integer, required): 活动ID，从get_ip_activity_list获取/Activity ID from get_ip_activity_list — e.g. `347`

## get_playlet_actor_rank_list

- `category` (string, optional): 分类/Category — e.g. `playlet_actor_list`
- `name` (string, optional): 榜单名称/Ranking name — e.g. `playlet_actor_composite_list`
- `qualifier` (string, optional): 达人类型，空字符串=不限/Actor type, empty=all
- `period` (integer, optional): 统计周期，7=周榜，30=月榜/Period, 7=weekly, 30=monthly — e.g. `30`
- `date` (string, optional): 统计日期，格式YYYYMMDD/Date, format YYYYMMDD — e.g. `20251130`
- `limit` (integer, optional): 返回数量/Result limit — e.g. `100`

## get_ranking_list_catalog

- `codes` (string, optional): 分类代码，默认为空字符串/Classification codes, default is empty string
- `biz_scene` (string, optional): 业务场景/Business scene — e.g. `douyin_flow_split_video_author_ranks`

## get_ranking_list_data

- `code` (integer, optional): 榜单类型代码/Ranking type code — e.g. `1`
- `qualifier` (string, optional): 榜单分类ID，从get_ranking_list_catalog获取/Category qualifier_id — e.g. `1901`
- `version` (string, optional): 版本/Version — e.g. `flow_split`
- `period` (integer, optional): 统计周期，7=周榜，30=月榜/Period, 7=weekly, 30=monthly — e.g. `30`
- `date` (string, optional): 统计日期，格式YYYYMMDD/Date, format YYYYMMDD — e.g. `20260131`
- `limit` (integer, optional): 返回数量/Result limit — e.g. `100`

## get_resource_list

- `resource_id` (integer, required): 资源ID/Resource ID — e.g. `1052`

## get_sec_user_id

- `url` (string, required): '' — e.g. `>-`

## get_sign_image

- `uri` (string, required): 图片的uri/Image URI — e.g. `tos-cn-i-0813c000-ce/oMKzDA3A9QGAuebfsDIAwlDoAfCFEEzSEw8FQZ`
- `durationTS` (integer, optional): 有效期时长（秒）/Duration in seconds — e.g. `86400`
- `format` (string, optional): 图片格式/Image format — e.g. `webp`

## get_user_profile_qrcode

- `core_user_id` (string, optional): 用户核心ID(与sec_uid二选一)/User core ID (pick one with sec_uid) — e.g. `1113181577281568`
- `sec_uid` (string, optional): >-

## get_webcast_id

- `url` (string, required): '' — e.g. `https://live.douyin.com/775841227732`

## get_xingtu_kolid_by_sec_user_id

- `sec_user_id` (string, required): 抖音用户sec_user_id/Douyin User sec_user_id — e.g. `MS4wLjABAAAAoxwUZouIdKL6sZ8EB96KDjkrhfBMS1KbCgsMJR1kIUs`

## get_xingtu_kolid_by_uid

- `uid` (string, required): 抖音用户ID/Douyin User ID — e.g. `70452002324`

## get_xingtu_kolid_by_unique_id

- `unique_id` (string, required): 抖音号/Douyin User unique_id — e.g. `m6640150`

## handler_user_profile

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `>-`

## handler_user_profile

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `>-`

## handler_user_profile_v2

- `unique_id` (string, required): 用户unique_id/User unique_id — e.g. `TheChief`

## handler_user_profile_v3

- `uid` (string, required): 用户uid(short_id)/User uid(short_id) — e.g. `1673937488185292`

## handler_user_profile_v4

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `>-`

## kol_audience_portrait_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## kol_base_info_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `platformChannel` (string, required): 平台渠道/Platform Channel — e.g. `_1`

## kol_conversion_ability_analysis_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `_range` (string, required): 时间范围/Time Range — e.g. `_1`

## kol_convert_video_display_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `detailType` (string, required): 详情类型/Detail Type — e.g. `_1`
- `page` (integer, required): 页码/Page — e.g. `1`

## kol_cp_info_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## kol_daily_fans_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `startDate` (string, required): 开始日期/Start Date — e.g. `2024-12-01`
- `endDate` (string, required): 结束日期/End Date — e.g. `2025-01-01`

## kol_data_overview_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `_type` (string, required): 类型/Type — e.g. `_1`
- `_range` (string, required): 范围/Range — e.g. `_2`
- `flowType` (integer, required): 流量类型/Flow Type — e.g. `1`
- `onlyAssign` (boolean, optional): 是否指派/Whether assigned (optional)

## kol_fans_portrait_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `fansType` (string, optional): 粉丝类型/Fans Type — e.g. `_1`

## kol_link_struct_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## kol_rec_videos_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## kol_service_price_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `platformChannel` (string, required): 平台渠道/Platform Channel — e.g. `_1`

## kol_touch_distribution_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## kol_video_performance_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`
- `onlyAssign` (boolean, required): 是否只显示分配作品/Whether to display only assigned works — e.g. `false`

## kol_xingtu_index_v1

- `kolId` (string, required): 用户的kolId/User kolId — e.g. `7048929565493690398`

## open_douyin_app_to_keyword_search

- `keyword` (string, required): 关键词/Keyword — e.g. `雷军`

## open_douyin_app_to_send_private_message

- `uid` (string, required): 用户id/User id — e.g. `96874812426`
- `sec_uid` (string, required): 用户sec_uid/User sec_uid — e.g. `MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70`

## open_douyin_app_to_user_profile

- `uid` (string, required): 用户id/User id — e.g. `96874812426`
- `sec_uid` (string, required): 用户sec_uid/User sec_uid — e.g. `MS4wLjABAAAA9y04iBlVdeMQqTJbqsQZKb-tqWqWW29jPVJqideHT70`

## open_douyin_app_to_video_detail

- `aweme_id` (string, required): 作品id/Video id — e.g. `7348044435755846962`

## register_device

- `proxy` (string, optional): 代理/Proxy

## search_kol_v1

- `keyword` (string, required): 关键词/Keyword — e.g. `抖音`
- `platformSource` (string, required): 平台来源/Platform Source — e.g. `_1`
- `page` (integer, required): 页码/Page — e.g. `1`

## search_kol_v2

- `keyword` (string, required): 关键词/Keyword — e.g. `美妆`
- `followerRange` (string, optional): 粉丝范围(可选)/Follower Range (optional), 例如 10-100 表示10万-100万粉丝 — e.g. `10-100`
- `contentTag` (string, optional): 内容标签(可选)/Content Tag (optional), 例如 tag-1 或 tag_level_two-7 — e.g. `tag-1`

## webcast_id_2_room_id

- `webcast_id` (string, required): 直播间号/Webcast id — e.g. `775841227732`
