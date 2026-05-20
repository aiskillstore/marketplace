# Parameter Mappings / 参数映射

Platform: `xiaohongshu` | Base URL: `https://www.aconfig.cn`

---

## extract_share_info

- `share_link` (string, required): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## fetch_feed_notes_v2

- `note_id` (string, required): 笔记ID/Note ID — e.g. `66c9cc31000000001f03a4bc`

## fetch_feed_notes_v3

- `short_url` (string, required): 短链/Short URL — e.g. `http://xhslink.com/a/tyoREa3ciaAeb`

## fetch_feed_notes_v4

- `note_id` (string, required): 笔记ID/Note ID — e.g. `66c9cc31000000001f03a4bc`

## fetch_feed_notes_v5

- `note_id` (string, required): 笔记ID/Note ID — e.g. `66c9cc31000000001f03a4bc`

## fetch_follower_list

- `user_id` (string, required): 用户ID/User ID — e.g. `604a28420000000001005211`
- `cursor` (string, optional): 游标/Cursor

## fetch_following_list

- `user_id` (string, required): 用户ID/User ID — e.g. `604a28420000000001005211`
- `cursor` (string, optional): 游标/Cursor

## fetch_home_notes

- `user_id` (string, required): 用户ID/User ID — e.g. `5e3a8ee700000000010070c6`
- `cursor` (string, optional): 游标/Cursor

## fetch_home_notes_app

- `user_id` (string, required): 用户ID/User ID — e.g. `5e3a8ee700000000010070c6`
- `cursor` (string, optional): 游标/Cursor

## fetch_homefeed

- `num` (integer, optional): 返回数量，最大40/Number of results, max 40 — e.g. `20`
- `cursor_score` (string, optional): 翻页游标/Pagination cursor
- `category` (string, optional): 分类频道ID/Category channel ID — e.g. `homefeed_recommend`
- `need_filter_image` (boolean, optional): 仅图文/Image notes only

## fetch_note_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `651ccaa9000000001f03d7f7`
- `cursor` (string, optional): 游标/Cursor

## fetch_note_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `69f0817d000000002301ca13`
- `cursor` (string, optional): 游标/Cursor
- `xsec_token` (string, required): >- — e.g. `ABkUO3R6tKvwMzj0Y3pFBbab4YWPXwLhp7gfbNpfYY8Bg=`

## fetch_note_detail

- `note_id` (string, required): 笔记ID/Note ID — e.g. `697ee7f5000000001a0225c1`
- `xsec_token` (string, required): >- — e.g. `ABkR6BvFSbUES4IbFcbjZrtCRa3FSqpqsa1KjFLyurW8U=`

## fetch_note_image

- `note_id` (string, required): 笔记ID/Note ID — e.g. `66c9cc31000000001f03a4bc`

## fetch_product_list

- `user_id` (string, required): 用户ID/User ID — e.g. `627e35aa00000000210275ae`
- `page` (string, optional): 页码/Page number

## fetch_search_notes

- `keywords` (string, required): 搜索关键词/Search keywords — e.g. `口红`
- `page` (integer, optional): 页码/Page number
- `sort_type` (string, optional): 排序方式/Sort type
- `note_type` (string, optional): 笔记类型/Note type

## fetch_search_notes

- `keyword` (string, required): 搜索关键词/Search keywords — e.g. `口红`
- `page` (integer, optional): 页码/Page number
- `sort` (string, optional): 排序方式/Sort type
- `note_type` (integer, optional): 笔记类型/Note type

## fetch_search_suggest

- `keyword` (string, optional): 关键词 (可为空)/Keyword (optional) — e.g. `口红`

## fetch_search_users

- `keywords` (string, required): 搜索关键词/Search keywords — e.g. `口红`
- `page` (integer, optional): 页码/Page number

## fetch_search_users

- `keyword` (string, required): 搜索关键词/Search keywords — e.g. `口红`
- `page` (integer, optional): 页码/Page number

## fetch_sub_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `673c894c0000000007033f92`
- `comment_id` (string, required): 评论ID/Comment ID — e.g. `673ecdfc000000001503bf8b`
- `cursor` (string, optional): 游标/Cursor

## fetch_sub_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `69f08d5f00000000350397ba`
- `root_comment_id` (string, required): 父评论ID/Root comment ID — e.g. `69f09736000000002803832e`
- `num` (integer, optional): 数量/Number
- `cursor` (string, optional): 游标/Cursor
- `xsec_token` (string, required): >- — e.g. `ABkUO3R6tKvwMzj0Y3pFBbaUK6gBt3Yj1Br95ogIzuXyI=`

## fetch_user_info

- `user_id` (string, required): 用户ID/User ID — e.g. `5e3a8ee700000000010070c6`

## fetch_user_info

- `user_id` (string, required): 用户ID/User ID — e.g. `5e3a8ee700000000010070c6`

## fetch_user_info_app

- `user_id` (string, required): 用户ID/User ID — e.g. `5e3a8ee700000000010070c6`

## fetch_user_notes

- `user_id` (string, required): 用户ID/User ID — e.g. `5e3a8ee700000000010070c6`
- `cursor` (string, optional): 游标/Cursor
- `num` (integer, optional): 数量/Number — e.g. `30`

## get_creator_hot_inspiration_feed

- `cursor` (string, optional): 分页游标，首次请求留空/Pagination cursor, leave empty for first request

## get_creator_inspiration_feed

- `cursor` (string, optional): 分页游标，首次请求留空/Pagination cursor, leave empty for first request
- `tab` (integer, optional): 标签类型/Tab type — e.g. `0`
- `source` (string, optional): 来源/Source — e.g. `creator_center`

## get_image_note_detail

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `697c0eee000000000a03c308`
- `share_text` (string, optional): 分享链接/Share link — e.g. `http://xhslink.com/o/8GqargIxrko`

## get_note_comment_replies

- `note_id` (string, required): 笔记ID/Note ID — e.g. `6683b283000000001f0052bf`
- `comment_id` (string, required): 评论ID/Comment ID — e.g. `6683ec5b000000000303b91a`
- `lastCursor` (string, optional): 上一页的游标/Last cursor

## get_note_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `677d1909000000002002a892`
- `start` (string, optional): 翻页游标/Pagination cursor — e.g. `682b0133000000001c03618d`
- `sort_strategy` (integer, optional): '排序策略：1-默认排序，2-最新评论/Sort strategy: 1-default, 2-latest' — e.g. `1`

## get_note_comments

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `697c0eee000000000a03c308`
- `share_text` (string, optional): 分享链接/Share link — e.g. `http://xhslink.com/o/8GqargIxrko`
- `cursor` (string, optional): 分页游标，首次请求留空/Pagination cursor, leave empty for first request
- `index` (integer, optional): 评论索引，首次请求传0/Comment index, pass 0 for first request — e.g. `0`
- `pageArea` (string, optional): '折叠状态: UNFOLDED(默认-展开), FOLDED(折叠)' — e.g. `UNFOLDED`
- `sort_strategy` (string, optional): '排序策略/Sort strategy: default, latest_v2, like_count' — e.g. `latest_v2`

## get_note_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `6683b283000000001f0052bf`
- `lastCursor` (string, optional): 上一页的游标/Last cursor

## get_note_id_and_xsec_token

- `share_text` (string, required): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## get_note_info

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `665f95200000000006005624`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## get_note_info_v2

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `665f95200000000006005624`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## get_note_info_v2

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `665f95200000000006005624`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## get_note_info_v4

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `665f95200000000006005624`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## get_note_info_v7

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `665f95200000000006005624`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`

## get_note_sub_comments

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `699916e6000000001d0253da`
- `share_text` (string, optional): 分享链接/Share link — e.g. `http://xhslink.com/o/8GqargIxrko`
- `comment_id` (string, required): 父评论ID/Parent comment ID — e.g. `699fb9930000000008030db6`
- `cursor` (string, optional): >-
- `index` (integer, optional): >- — e.g. `1`

## get_product_detail

- `sku_id` (string, required): 商品skuId/Product SKU ID — e.g. `68be7cbc8c331700011f89d1`

## get_product_detail

- `sku_id` (string, required): 商品SKU ID/Product SKU ID — e.g. `669ddd44e05f3700011067ed`
- `source` (string, optional): 来源/Source — e.g. `mall_search`
- `pre_page` (string, optional): 前置页面/Previous page — e.g. `mall_search`

## get_product_info

- `share_text` (string, optional): 分享链接/Share link
- `item_id` (string, optional): 商品ID/Item ID — e.g. `65fc2e6d6b92310001d24efb`
- `xsec_token` (string, optional): X-Sec-Token — e.g. `XBC6LTqeaEDeJETMoXo436Eg-74GxFemVnNHeONYobv7k=`

## get_product_recommendations

- `sku_id` (string, required): 商品SKU ID/Product SKU ID — e.g. `669ddd44e05f3700011067ed`
- `cursor_score` (string, optional): 分页游标，首次请求留空/Pagination cursor, leave empty for first request
- `region` (string, optional): 地区/Region — e.g. `US`

## get_product_review_overview

- `sku_id` (string, required): 商品SKU ID/Product SKU ID — e.g. `669ddd44e05f3700011067ed`
- `tab` (integer, optional): 标签类型/Tab type — e.g. `2`

## get_product_reviews

- `sku_id` (string, required): 商品SKU ID/Product SKU ID — e.g. `669ddd44e05f3700011067ed`
- `page` (integer, optional): 页码，从0开始/Page number, start from 0 — e.g. `0`
- `sort_strategy_type` (integer, optional): '排序策略：0=综合排序, 1=最新排序/Sort strategy: 0=general, 1=latest' — e.g. `0`
- `share_pics_only` (integer, optional): '仅看有图评论：0=否, 1=是/Show reviews with images only: 0=no, 1=yes' — e.g. `0`
- `from_page` (string, optional): 来源页面/From page — e.g. `score_page`

## get_sub_comments

- `note_id` (string, required): 笔记ID/Note ID — e.g. `677d1909000000002002a892`
- `comment_id` (string, required): 一级评论ID/Parent comment ID — e.g. `677f67e400000000220013f3`
- `start` (string, optional): 翻页游标/Pagination cursor — e.g. `6806642d000000001f01991b`

## get_topic_feed

- `page_id` (string, required): 话题页面ID/Topic page ID — e.g. `5c1cc866febed9000184b7c1`
- `sort` (string, optional): '排序方式/Sort: trend(最热), time(最新)' — e.g. `trend`
- `cursor_score` (string, optional): 分页游标分数，翻页时传入/Pagination cursor score for next page
- `last_note_id` (string, optional): 上一页最后一条笔记ID，翻页时传入/Last note ID from previous page
- `last_note_ct` (string, optional): 上一页最后一条笔记创建时间，翻页时传入/Last note create time from previous page
- `session_id` (string, optional): 会话ID，翻页时保持一致/Session ID, keep consistent for pagination
- `first_load_time` (string, optional): 首次加载时间戳，翻页时保持一致/First load timestamp, keep consistent for pagination
- `source` (string, optional): 来源/Source — e.g. `normal`

## get_topic_info

- `page_id` (string, required): 话题页面ID/Topic page ID — e.g. `5c1cc866febed9000184b7c1`
- `source` (string, optional): 来源/Source — e.g. `normal`
- `note_id` (string, optional): >-

## get_topic_notes

- `page_id` (string, required): 话题标签ID/Topic tag ID — e.g. `5c014b045b29cb0001ead530`
- `first_load_time` (string, required): 首次请求时间戳（毫秒）/First load timestamp (ms) — e.g. `1744978179304`
- `sort` (string, optional): '排序方式：hot-综合，time-最新，trend-最热/Sort: hot, time, trend' — e.g. `hot`
- `last_note_ct` (string, optional): 最后一条笔记create_time（翻页用）/Last note create_time (pagination)
- `last_note_id` (string, optional): 最后一条笔记ID（翻页用）/Last note ID (pagination)
- `cursor_score` (string, optional): 游标分数（翻页用）/Cursor score (pagination)
- `session_id` (string, optional): 会话ID，由服务端生成（翻页用）/Session ID, server-generated (pagination)

## get_user_faved_notes

- `user_id` (string, optional): 用户ID/User ID — e.g. `5a8cf39111be10466d285d6b`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/a/EZ4M9TwMA6c3`
- `cursor` (string, optional): >-

## get_user_id_and_xsec_token

- `share_link` (string, required): 用户分享链接/User share link — e.g. `https://xhslink.com/m/Ap1vXtgAixh`

## get_user_info

- `user_id` (string, required): 用户ID/User ID — e.g. `5c2f338a000000000701e1c6`

## get_user_info

- `user_id` (string, optional): 用户ID/User ID — e.g. `61b46d790000000010008153`
- `share_text` (string, optional): 分享链接/Share link — e.g. `https://xhslink.com/m/3ZSCJZAMz0a`

## get_user_info

- `user_id` (string, required): 用户ID/User ID — e.g. `5f4a10070000000001006fc7`

## get_user_info_v2

- `user_id` (string, optional): 用户ID/User ID — e.g. `5f4a10070000000001006fc7`
- `share_text` (string, optional): 分享文本或链接/Share text or link — e.g. `>-`

## get_user_notes

- `user_id` (string, required): 用户ID/User ID — e.g. `5c57e6a4000000001802a013`
- `cursor` (string, optional): 翻页游标/Pagination cursor — e.g. `67ee399f000000001c02f36f`

## get_user_notes_v2

- `user_id` (string, required): 用户ID/User ID — e.g. `5f4a10070000000001006fc7`
- `lastCursor` (string, optional): 上一页的游标/Last cursor

## get_user_posted_notes

- `user_id` (string, optional): 用户ID/User ID — e.g. `61b46d790000000010008153`
- `share_text` (string, optional): 分享链接/Share link — e.g. `http://xhslink.com/o/8GqargIxrko`
- `cursor` (string, optional): 分页游标，首次请求留空/Pagination cursor, leave empty for first request

## get_video_note_detail

- `note_id` (string, optional): 笔记ID/Note ID — e.g. `697c0eee000000000a03c308`
- `share_text` (string, optional): 分享链接/Share link — e.g. `http://xhslink.com/o/8GqargIxrko`

## get_visitor_cookie

- `proxy` (string, optional): 代理/Proxy

## search_groups

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `上海`
- `page_no` (integer, optional): 页码，从0开始/Page number, start from 0 — e.g. `0`
- `search_id` (string, optional): 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination
- `source` (string, optional): 来源/Source — e.g. `unifiedSearchGroup`
- `is_recommend` (integer, optional): '是否推荐：0=否, 1=是/Is recommend: 0=no, 1=yes' — e.g. `0`

## search_images

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `壁纸`
- `page` (integer, optional): 页码，从1开始/Page number, start from 1 — e.g. `1`
- `search_id` (string, optional): 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination
- `search_session_id` (string, optional): 搜索会话ID，翻页时传入首次搜索返回的值/Search session ID for pagination
- `word_request_id` (string, optional): 词请求ID，翻页时传入首次搜索返回的值/Word request ID for pagination
- `source` (string, optional): 来源/Source — e.g. `explore_feed`

## search_notes

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `猫粮`
- `page` (integer, required): 页码（从1开始）/Page number (start from 1) — e.g. `1`
- `search_id` (string, optional): 搜索ID，翻页时使用/Search ID for pagination — e.g. `2egvdsiowvfm9thbt260w`
- `session_id` (string, optional): 会话ID，翻页时使用/Session ID for pagination — e.g. `2egvdt4sl2b7rnfg8zk00`
- `sort_type` (string, optional): 排序方式/Sort type — e.g. `general`
- `filter_note_type` (string, optional): 笔记类型筛选：不限、视频笔记、普通笔记/Note type filter — e.g. `不限`
- `filter_note_time` (string, optional): 发布时间筛选：不限、一天内、一周内、半年内/Time filter — e.g. `不限`

## search_notes

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `美食推荐`
- `page` (integer, optional): 页码，从1开始/Page number, start from 1 — e.g. `1`
- `sort_type` (string, optional): 排序方式/Sort type — e.g. `general`
- `note_type` (string, optional): '笔记类型/Note type: 不限, 视频笔记, 普通笔记, 直播笔记' — e.g. `不限`
- `time_filter` (string, optional): '发布时间筛选/Time filter: 不限, 一天内, 一周内, 半年内' — e.g. `不限`
- `search_id` (string, optional): 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination
- `search_session_id` (string, optional): 搜索会话ID，翻页时传入首次搜索返回的值/Search session ID for pagination
- `source` (string, optional): 来源/Source — e.g. `explore_feed`
- `ai_mode` (integer, optional): 'AI模式：0=关闭, 1=开启/AI mode: 0=off, 1=on' — e.g. `0`

## search_notes

- `keyword` (string, required): 搜索关键词/Keyword — e.g. `美食`
- `page` (integer, optional): 页码/Page — e.g. `1`
- `sort` (string, optional): 排序方式/Sort — e.g. `general`
- `noteType` (string, optional): 笔记类型/Note type — e.g. `_0`
- `noteTime` (string, optional): 发布时间/Release time

## search_notes_v3

- `keyword` (string, required): 搜索关键词/Keyword — e.g. `美食`
- `page` (integer, optional): 页码/Page — e.g. `1`
- `sort` (string, optional): 排序方式/Sort — e.g. `general`
- `noteType` (string, optional): 笔记类型/Note type — e.g. `_0`
- `noteTime` (string, optional): 发布时间/Release time

## search_products

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `充电宝`
- `page` (integer, required): 页码（从1开始）/Page number (start from 1) — e.g. `1`
- `search_id` (string, optional): 搜索ID，翻页时使用/Search ID for pagination
- `session_id` (string, optional): 会话ID，翻页时使用/Session ID for pagination
- `sort` (string, optional): >- — e.g. `sales_qty`
- `scope` (string, optional): '搜索范围：purchased-买过的店、following-关注的店/Scope: purchased, following' — e.g. `purchased`
- `service_guarantee` (string, optional): 物流权益，多选用英文逗号分割/Service guarantee, comma separated — e.g. `24小时发货,七天无理由`
- `min_price` (string, optional): 最低价/Min price — e.g. `1`
- `max_price` (string, optional): 最高价/Max price — e.g. `100`
- `super_promotion` (string, optional): 标签ID/Promotion tag ID — e.g. `695fb0a330425100017ff555`

## search_products

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `手机壳`
- `page` (integer, optional): 页码，从1开始/Page number, start from 1 — e.g. `1`
- `search_id` (string, optional): 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination
- `source` (string, optional): 来源/Source — e.g. `explore_feed`

## search_users

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `美食博主`
- `page` (integer, optional): 页码，从1开始/Page number, start from 1 — e.g. `1`
- `search_id` (string, optional): 搜索ID，翻页时传入首次搜索返回的值/Search ID for pagination
- `source` (string, optional): 来源/Source — e.g. `explore_feed`

## search_users

- `keyword` (string, required): 搜索关键词/Keyword — e.g. `美食`
- `page` (integer, optional): 页码/Page — e.g. `1`
