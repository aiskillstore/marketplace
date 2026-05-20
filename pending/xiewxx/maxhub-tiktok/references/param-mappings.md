# Parameter Mappings / 参数映射

Platform: `tiktok` | Base URL: `https://www.aconfig.cn`

---

- `item_id` (string, required): 作品id/Video id — e.g. `7419966340443819295`

## check_live_room_online

- `room_id` (string, required): 直播间id/Live room id — e.g. `7358603858249009962`

## decrypt_strData

- `encrypted_data` (string, required): 加密后的strData字符串/Encrypted strData string — e.g. `>-`

## encrypt_strData

- `data` (string, required): >- — e.g. `>-`

## fetch_batch_check_live_alive

- `room_ids` (string, required): >- — e.g. `>-`

## fetch_check_live_alive

- `room_id` (string, required): 直播间ID/Live room ID — e.g. `7381444193462078214`

## fetch_comment_keywords

- `item_id` (string, required): 作品id/Video id — e.g. `7502551047378832671`

## fetch_creator_info

- `creator_uid` (string, required): 创作者uid/Creator uid — e.g. `6555451606845243393`

## fetch_creator_info_and_milestones

- `user_id` (string, required): 用户id/User id — e.g. `107955`

## fetch_creator_search_insights

- `offset` (integer, optional): 分页偏移量/Pagination offset — e.g. `0`
- `limit` (integer, optional): 每页数量/Number per page — e.g. `20`
- `tab` (string, optional): >- — e.g. `all`
- `language_filters` (string, optional): 语言过滤器，多个用逗号分隔/Language filters (id/de/en/es/fr/pt/vi/tr/ar/th/ja/ko) — e.g. `en`
- `category_filters` (string, optional): >-
- `creator_source` (string, optional): 创作者来源/Creator source — e.g. `general_search`
- `force_refresh` (boolean, optional): 是否强制刷新/Force refresh — e.g. `false`

## fetch_creator_search_insights_detail

- `query_id_str` (string, required): >- — e.g. `122991006`
- `time_range` (string, optional): >- — e.g. `past_30_days`
- `start_date` (integer, optional): >-
- `end_date` (integer, optional): >-
- `dimension_list` (string, optional): 维度列表，多个用逗号分隔/Dimension list (gender/age/country) — e.g. `gender,age,country`

## fetch_creator_search_insights_trend

- `query_id_str` (string, required): >- — e.g. `7555720035176562699`
- `from_tab_path` (string, optional): 来源标签路径/From tab path — e.g. `TRENDING,TOPICS`
- `query_analysis_required` (boolean, optional): 是否需要查询分析/Whether query analysis is required — e.g. `true`

## fetch_creator_search_insights_videos

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `headshots 2 2 3`
- `offset` (integer, optional): 分页偏移量/Pagination offset — e.g. `0`
- `count` (integer, optional): 每页数量/Number per page — e.g. `20`

## fetch_creator_showcase_product_list

- `kol_id` (string, required): 创作者的sec_user_id/Creator's sec_user_id — e.g. `>-`
- `count` (integer, optional): 数量/Number
- `next_scroll_param` (string, optional): 翻页参数/Page parameter

## fetch_explore_post

- `categoryType` (string, optional): 作品分类/Video category
- `count` (integer, optional): 每页数量/Number per page

## fetch_general_search

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `TikTok`
- `offset` (integer, optional): 翻页游标/Page cursor
- `search_id` (string, optional): 搜索id，翻页时需要提供/Search id, need to provide when paging
- `cookie` (string, optional): 用户cookie(按需提供)/User cookie(if needed)

## fetch_general_search_result

- `keyword` (string, required): 关键词/Keyword — e.g. `中华娘`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `sort_type` (integer, optional): 排序类型/Sort type — e.g. `0`
- `publish_time` (integer, optional): 发布时间/Publish time — e.g. `0`

## fetch_hashtag_detail

- `ch_id` (string, required): 话题id/Hashtag id — e.g. `7551`

## fetch_hashtag_search_result

- `keyword` (string, required): 关键词/Keyword — e.g. `Cat`
- `offset` (integer, optional): 偏移量/Offset
- `count` (integer, optional): 数量/Number

## fetch_hashtag_video_list

- `ch_id` (string, required): 话题id/Hashtag id — e.g. `7551`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_hot_selling_products_list

- `region` (string, optional): 地区代码/Region code — e.g. `US`
- `count` (integer, optional): 返回商品数量/Number of products to return — e.g. `100`

## fetch_live_daily_rank

- `anchor_id` (string, optional): 主播id/Anchor id
- `room_id` (string, optional): 直播间id/Live room id
- `rank_type` (integer, optional): 榜单类型/Rank type
- `region_type` (integer, optional): 地区类型/Region type
- `gap_interval` (integer, optional): 时间间隔/Time interval
- `cookie` (string, optional): 用户自己的cookie/User's own cookie

## fetch_live_gift_list

- `room_id` (string, optional): 直播间ID，可选参数/Live room ID, optional parameter — e.g. `7381444193462078214`

## fetch_live_im_fetch

- `room_id` (string, required): 直播间号/Live room id — e.g. `7382517534467115826`
- `user_unique_id` (string, optional): 用户唯一ID/User unique ID — e.g. `7382524529011246630`
- `resp_content_type` (string, optional): '响应格式: protobuf 或 json / Response format: protobuf or json' — e.g. `protobuf`

## fetch_live_ranking_list

- `room_id` (string, required): 直播间id/Live room id — e.g. `7358603858249009962`
- `anchor_id` (string, required): 主播id/Anchor id — e.g. `7222941468722758702`

## fetch_live_recommend

- `related_live_tag` (string, required): 相关直播标签/Related live tag — e.g. `VALORANT`

## fetch_live_room_info

- `room_id` (string, required): 直播间id/Live room id — e.g. `7358603858249009962`

## fetch_live_room_product_list

- `room_id` (string, required): 直播间id/Live room id — e.g. `7420741353250507562`
- `author_id` (string, required): 主播id/Anchor id — e.g. `7408859677050274859`
- `page_size` (integer, optional): 数量/Number
- `offset` (integer, optional): 数量/Number
- `region` (string, optional): 地区/Region
- `cookie` (string, optional): 用户自己的cookie/User's own cookie

## fetch_live_room_product_list_v2

- `room_id` (string, required): 直播间id/Live room id — e.g. `7420741353250507562`
- `author_id` (string, required): 主播id/Anchor id — e.g. `7408859677050274859`
- `page_size` (integer, optional): 数量/Number
- `offset` (integer, optional): 数量/Number
- `region` (string, optional): 地区/Region
- `cookie` (string, optional): 用户自己的cookie/User's own cookie

## fetch_live_search_result

- `keyword` (string, required): 关键词/Keyword — e.g. `Cat`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `region` (string, optional): 地区/Region — e.g. `US`

## fetch_location_search

- `keyword` (string, required): 关键词/Keyword — e.g. `Shanghai`
- `offset` (integer, optional): 偏移量/Offset
- `count` (integer, optional): 数量/Number

## fetch_music_chart_list

- `scene` (integer, optional): '排行榜类型/Chart type (0: Top 50, 1: Viral 50)' — e.g. `0`
- `cursor` (integer, optional): 分页游标/Pagination cursor — e.g. `0`
- `count` (integer, optional): 每页数量/Number per page (max 50) — e.g. `50`

## fetch_music_detail

- `music_id` (string, required): 音乐id/Music id — e.g. `6943027371519772674`

## fetch_music_search_result

- `keyword` (string, required): 关键词/Keyword — e.g. `Cat`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `filter_by` (integer, optional): 过滤类型/Filter type — e.g. `0`
- `sort_type` (integer, optional): 排序类型/Sort type — e.g. `0`
- `region` (string, optional): 地区/Region — e.g. `US`

## fetch_music_video_list

- `music_id` (string, required): 音乐id/Music id — e.g. `6943027371519772674`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_one_video

- `aweme_id` (string, required): 作品id/Video id — e.g. `7350810998023949599`

## fetch_one_video_by_share_url_v2

- `share_url` (string, required): 分享链接/Share link — e.g. `https://www.tiktok.com/t/ZTFNEj8Hk/`

## fetch_one_video_v2

- `aweme_id` (string, required): 作品id/Video id — e.g. `7350810998023949599`

## fetch_one_video_v3

- `aweme_id` (string, required): 作品id/Video id — e.g. `7350810998023949599`
- `region` (string, optional): 国家代码/Country code — e.g. `US`

## fetch_post_comment

- `aweme_id` (string, required): 作品id/Video id — e.g. `7304809083817774382`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `count` (integer, optional): 每页数量/Number per page
- `current_region` (string, optional): 当前地区/Current region

## fetch_post_comment_reply

- `item_id` (string, required): 作品id/Video id — e.g. `7304809083817774382`
- `comment_id` (string, required): 评论id/Comment id — e.g. `7304877760886588191`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `count` (integer, optional): 每页数量/Number per page
- `current_region` (string, optional): 当前地区/Current region

## fetch_post_detail

- `itemId` (string, required): 作品id/Video id — e.g. `7339393672959757570`

## fetch_post_detail_v2

- `itemId` (string, required): 作品id/Video id — e.g. `7339393672959757570`

## fetch_product_detail

- `product_id` (string, required): 商品id/Product id — e.g. `1729385239712731370`

## fetch_product_detail

- `product_id` (string, required): 商品ID/Product ID — e.g. `1729556436942358002`
- `seller_id` (string, optional): 卖家ID(可选)/Seller ID (optional) — e.g. `7494629757824764402`
- `region` (string, optional): 地区代码/Region code — e.g. `MY`

## fetch_product_detail_v2

- `product_id` (string, required): 商品id/Product id — e.g. `1729385239712731370`

## fetch_product_detail_v2

- `product_id` (string, required): 商品ID/Product ID — e.g. `1729556436942358002`
- `seller_id` (string, optional): 卖家ID(可选)/Seller ID (optional) — e.g. `7494629757824764402`
- `region` (string, optional): 地区代码/Region code — e.g. `MY`

## fetch_product_detail_v3

- `product_id` (string, required): 商品id / Product ID — e.g. `1729385239712731370`
- `region` (string, optional): 商品的国家/地区代码/ Country/region code of the product — e.g. `US`

## fetch_product_detail_v3

- `product_id` (string, required): 商品ID/Product ID — e.g. `1732108663255959373`
- `region` (string, optional): 地区代码/Region code — e.g. `SG`

## fetch_product_detail_v4

- `product_id` (string, required): 商品id / Product ID — e.g. `1729385239712731370`
- `region` (string, optional): 商品的国家/地区代码/ Country/region code of the product — e.g. `US`

## fetch_product_id_by_share_link

- `share_link` (string, required): 分享链接/Share link — e.g. `https://www.tiktok.com/t/ZT98v9dPs6aEC-qHWeW/`

## fetch_product_review

- `product_id` (string, required): 商品id/Product id — e.g. `1729448812983194615`
- `cursor` (integer, optional): 游标/Cursor
- `size` (integer, optional): 数量/Number
- `filter_id` (integer, optional): 筛选条件/Filter condition
- `sort_type` (integer, optional): 排序条件/Sorting conditions

## fetch_product_reviews_v2

- `product_id` (string, required): 商品ID/Product ID — e.g. `1729556436942358002`
- `page_start` (integer, optional): 起始页码/Page start — e.g. `1`
- `sort_rule` (integer, optional): 排序规则/Sort rule — e.g. `2`
- `filter_type` (integer, optional): '筛选类型/Filter type: 1=默认, 2=有图片/视频, 3=真实购买' — e.g. `1`
- `filter_value` (integer, optional): '星级筛选/Star filter: 6=全部, 5-1=对应星级' — e.g. `6`
- `region` (string, optional): 地区代码/Region code — e.g. `MY`

## fetch_product_search

- `keyword` (string, required): 关键词/Keyword — e.g. `Cat Toy`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number
- `sort_type` (integer, optional): 商品排序条件/Product sorting conditions
- `customer_review_four_star` (boolean, optional): 四星以上评价/Four-star or more reviews
- `have_discount` (boolean, optional): 有优惠/Having discount
- `min_price` (string, optional): 最低价格/Minimum price
- `max_price` (string, optional): 最高价格/Maximum price

## fetch_products_by_category_id

- `category_id` (integer, required): 分类ID/Category ID — e.g. `963976`
- `offset` (integer, optional): 翻页偏移量/Offset for pagination — e.g. `0`
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_products_category_list

- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_search_keyword_suggest

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `TikTok`

## fetch_search_live

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `TikTok`
- `count` (integer, optional): 每页数量/Number per page
- `offset` (integer, optional): 翻页游标/Page cursor
- `search_id` (string, optional): 搜索id，翻页时需要提供/Search id, need to provide when paging
- `cookie` (string, optional): 用户cookie(按需提供)/User cookie(if needed)

## fetch_search_photo

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `TikTok`
- `count` (integer, optional): 每页数量/Number per page
- `offset` (integer, optional): 翻页游标/Page offset
- `search_id` (string, optional): 搜索id，翻页时需要提供/Search id, need to provide when paging
- `cookie` (string, optional): 用户cookie(按需提供)/User cookie(if needed)

## fetch_search_products_list

- `search_word` (string, required): 搜索关键词/Search keyword — e.g. `labubu`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `page_token` (string, optional): 分页标记/Page token
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_search_products_list_v2

- `search_word` (string, required): 搜索关键词/Search keyword — e.g. `labubu`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `page_token` (string, optional): 分页标记/Page token
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_search_user

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `TikTok`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `search_id` (string, optional): 搜索id，翻页时需要提供/Search id, need to provide when paging
- `cookie` (string, optional): 用户cookie(按需提供)/User cookie(if needed)

## fetch_search_video

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `TikTok`
- `count` (integer, optional): 每页数量/Number per page
- `offset` (integer, optional): 翻页游标/Page cursor
- `search_id` (string, optional): 搜索id，翻页时需要提供/Search id, need to provide when paging
- `cookie` (string, optional): 用户cookie(按需提供)/User cookie(if needed)

## fetch_search_word_suggestion

- `search_word` (string, required): 搜索关键词/Search keyword — e.g. `labubu`
- `lang` (string, optional): 语言/Language — e.g. `en-US`
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_search_word_suggestion_v2

- `search_word` (string, required): 搜索关键词/Search keyword — e.g. `labubu`
- `lang` (string, optional): 语言/Language — e.g. `en-US`
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_seller_products_list

- `seller_id` (string, required): 卖家ID/Seller ID — e.g. `7495150558072178725`
- `search_params` (string, optional): 搜索参数(用于分页)/Search params (for pagination) — e.g. `>-`
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_seller_products_list_v2

- `seller_id` (string, required): 卖家ID/Seller ID — e.g. `7495150558072178725`
- `searchParams` (string, optional): 搜索参数/Search params
- `region` (string, optional): 地区代码/Region code — e.g. `US`

## fetch_share_qr_code

- `object_id` (string, required): 对象id/Object id — e.g. `6762244951259661318`
- `schema_type` (integer, optional): 模式类型/Schema type

## fetch_share_short_link

- `url` (string, required): 分享链接/Share link — e.g. `https://www.tiktok.com/passport/web/logout/`

## fetch_shop_home

- `page_id` (string, required): 爬取的商家主页Page id/Page id of the crawled shop home page — e.g. `7314705727611930410`
- `seller_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `8646929864612614278`

## fetch_shop_home_page_list

- `seller_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `8646929864612614278`

## fetch_shop_id_by_share_link

- `share_link` (string, required): 分享链接/Share link — e.g. `https://vt.tiktok.com/ZT2AHoGsE/`

## fetch_shop_info

- `shop_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `8646942781241463007`

## fetch_shop_product_category

- `seller_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `7495294980909468039`

## fetch_shop_product_list

- `seller_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `8646929864612614278`
- `scroll_params` (string, optional): 滚动参数，用于加载更多商品数据/Scroll parameter, used to load more product data
- `page_size` (integer, optional): 每页数量/Number per page
- `sort_field` (integer, optional): 排序字段/Sorting field
- `sort_order` (integer, optional): 排序方式/Sorting method

## fetch_shop_product_list_v2

- `seller_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `8646929864612614278`
- `scroll_params` (string, optional): 滚动参数，用于加载更多商品数据/Scroll parameter, used to load more product data
- `page_size` (integer, optional): 每页数量/Number per page
- `sort_field` (integer, optional): 排序字段/Sorting field
- `sort_order` (integer, optional): 排序方式/Sorting method

## fetch_shop_product_recommend

- `seller_id` (string, required): 商家id,店铺id/Seller id, shop id — e.g. `8646929864612614278`
- `scroll_param` (string, optional): 滚动参数，用于加载更多商品数据/Scroll parameter, used to load more product data
- `page_size` (integer, optional): 每页数量/Number per page

## fetch_similar_user_recommendations

- `sec_uid` (string, required): 用户sec_uid/User sec_uid — e.g. `>-`
- `page_token` (string, optional): 分页标记/Page token

## fetch_tag_detail

- `tag_name` (string, required): Tag名称/Tag name — e.g. `tiktok`

## fetch_tag_post

- `challengeID` (string, required): Tag ID — e.g. `7551`
- `count` (integer, optional): 每页数量/Number per page
- `cursor` (integer, optional): 翻页游标/Page cursor

## fetch_tiktok_live_data

- `live_room_url` (string, required): 直播间链接/Live room link — e.g. `https://www.tiktok.com/@.caseoh_daily/live`

## fetch_tiktok_web_guest_cookie

- `user_agent` (string, required): 用户浏览器代理/User browser agent — e.g. `>-`

## fetch_user_collect

- `cookie` (string, required): 用户cookie/User cookie — e.g. `Your_Cookie`
- `secUid` (string, required): 用户secUid/User secUid — e.g. `Your_SecUid`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `count` (integer, optional): 每页数量/Number per page
- `coverFormat` (integer, optional): 封面格式/Cover format

## fetch_user_country_by_username

- `username` (string, required): 用户名/Username — e.g. `tiktok`

## fetch_user_fans

- `secUid` (string, required): 用户secUid/User secUid — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `count` (integer, optional): 每页数量/Number per page
- `maxCursor` (integer, optional): 最大游标/Max cursor
- `minCursor` (integer, optional): 最小游标/Min cursor

## fetch_user_follow

- `secUid` (string, required): 用户secUid/User secUid — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `count` (integer, optional): 每页数量/Number per page
- `maxCursor` (integer, optional): 最大游标/Max cursor
- `minCursor` (integer, optional): 最小游标/Min cursor

## fetch_user_follower_list

- `user_id` (string, optional): 用户ID/User ID (与sec_user_id二选一/One of user_id and sec_user_id) — e.g. `7486586574684881927`
- `sec_user_id` (string, optional): >- — e.g. `>-`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `min_time` (integer, optional): 最小时间，用于翻页/Minimum time for paging — e.g. `0`
- `page_token` (string, optional): 翻页token/Page token

## fetch_user_following_list

- `user_id` (string, optional): 用户ID/User ID (与sec_user_id二选一/One of user_id and sec_user_id) — e.g. `7486586574684881927`
- `sec_user_id` (string, optional): >- — e.g. `>-`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `min_time` (integer, optional): 最小时间，用于翻页/Minimum time for paging — e.g. `0`
- `page_token` (string, optional): 翻页token/Page token

## fetch_user_like

- `secUid` (string, required): 用户secUid/User secUid — e.g. `>-`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `count` (integer, optional): 每页数量/Number per page
- `coverFormat` (integer, optional): 封面格式/Cover format
- `post_item_list_request_type` (integer, optional): 排序方式/Sort type

## fetch_user_like_videos

- `sec_user_id` (string, required): 用户sec_user_id/User sec_user_id — e.g. `>-`
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `counts` (integer, optional): 每页数量/Number per page

## fetch_user_live_detail

- `uniqueId` (string, required): 用户uniqueId/User uniqueId — e.g. `tiktok`

## fetch_user_mix

- `mixId` (string, required): 合辑id/Mix id — e.g. `7101538765474106158`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `count` (integer, optional): 每页数量/Number per page

## fetch_user_music_list

- `sec_uid` (string, required): 用户sec_uid/User sec_uid — e.g. `>-`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_user_play_list

- `secUid` (string, required): 用户secUid/User secUid — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `cursor` (integer, optional): 翻页游标/Page cursor
- `count` (integer, optional): 每页数量/Number per page

## fetch_user_post

- `secUid` (string, required): 用户secUid/User secUid — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `cursor` (integer, optional): 翻页游标/Page cursor — e.g. `0`
- `count` (integer, optional): 每页数量/Number per page — e.g. `20`
- `coverFormat` (integer, optional): 封面格式/Cover format — e.g. `2`
- `post_item_list_request_type` (integer, optional): 排序方式/Sort type — e.g. `0`

## fetch_user_post_videos

- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `unique_id` (string, optional): 用户unique_id/User unique_id
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `count` (integer, optional): 每页数量/Number per page
- `sort_type` (integer, optional): 排序类型/Sort type

## fetch_user_post_videos_v2

- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `unique_id` (string, optional): 用户unique_id/User unique_id
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `count` (integer, optional): 每页数量/Number per page
- `sort_type` (integer, optional): 排序类型/Sort type

## fetch_user_post_videos_v3

- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `unique_id` (string, optional): 用户unique_id/User unique_id
- `max_cursor` (integer, optional): 最大游标/Maximum cursor
- `count` (integer, optional): 每页数量/Number per page
- `sort_type` (integer, optional): 排序类型/Sort type

## fetch_user_profile

- `uniqueId` (string, optional): 用户uniqueId/User uniqueId — e.g. `tiktok`
- `secUid` (string, optional): 用户secUid/User secUid

## fetch_user_repost

- `secUid` (string, required): 用户secUid/User secUid — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `cursor` (integer, optional): 翻页游标/Page cursor — e.g. `0`
- `count` (integer, optional): 每页数量/Number per page — e.g. `20`
- `coverFormat` (integer, optional): 封面格式/Cover format — e.g. `2`

## fetch_user_repost_videos

- `user_id` (integer, required): 用户id/User id — e.g. `107955`
- `offset` (integer, optional): 偏移量/Offset
- `count` (integer, optional): 数量/Number

## fetch_user_search_result

- `keyword` (string, required): 关键词/Keyword — e.g. `Cat`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `user_search_follower_count` (string, optional): 根据粉丝数排序/Sort by number of followers
- `user_search_profile_type` (string, optional): 根据账号类型排序/Sort by account type
- `user_search_other_pref` (string, optional): 根据其他偏好排序/Sort by other preferences

## fetch_video_comment_replies

- `item_id` (string, required): 作品id/Video id — e.g. `7326156045968067873`
- `comment_id` (string, required): 评论id/Comment id — e.g. `7327061675382260482`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_comments

- `aweme_id` (string, required): 作品id/Video id — e.g. `7326156045968067873`
- `cursor` (integer, optional): 游标/Cursor
- `count` (integer, optional): 数量/Number

## fetch_video_metrics

- `item_id` (string, required): 作品id/Video id — e.g. `7502551047378832671`

## fetch_video_search_result

- `keyword` (string, required): 关键词/Keyword — e.g. `中华娘`
- `offset` (integer, optional): 偏移量/Offset — e.g. `0`
- `count` (integer, optional): 数量/Number — e.g. `20`
- `sort_type` (integer, optional): 排序类型/Sort type — e.g. `0`
- `publish_time` (integer, optional): 发布时间/Publish time — e.g. `0`
- `region` (string, optional): 地区/Region — e.g. `US`

## fetch_webcast_user_info

- `user_id` (string, optional): 用户uid （可选，纯数字）/User uid (optional, pure number)
- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`

## generate_fingerprint

- `browser_type` (string, optional): ''

## generate_hashed_id

- `email` (string, required): 邮箱地址/Email address — e.g. `test@example.com`

## generate_real_msToken

- `random_strData` (boolean, optional): ''
- `browser_type` (string, optional): ''

## generate_ttwid

- `user_agent` (string, optional): ''

## generate_webid

- `cookie` (string, optional): ''
- `user_agent` (string, optional): ''
- `url` (string, optional): ''
- `referer` (string, optional): ''
- `user_unique_id` (string, optional): ''
- `app_id` (integer, optional): ''

## generate_wss_xb_signature

- `user_agent` (string, optional): 用户浏览器代理（可选）/User browser agent (optional) — e.g. `>-`

## get_ad_interactive_analysis

- `material_id` (string, required): 广告素材ID/Ad material ID — e.g. `7213258221116751874`
- `metric_type` (string, optional): 分析类型/Analysis type (ctr, cvr, clicks, conversion, remain)
- `period_type` (integer, optional): 时间范围(天)/Period type (days)

## get_ad_keyframe_analysis

- `material_id` (string, required): 广告素材ID/Ad material ID — e.g. `7213258221116751874`
- `metric` (string, optional): >-

## get_ad_percentile

- `material_id` (string, required): 广告素材ID/Ad material ID — e.g. `7213258221116751874`
- `metric` (string, optional): >-
- `period_type` (integer, optional): 时间范围(天)/Time period (days)

## get_ads_detail

- `ads_id` (string, required): 广告ID/Ad ID — e.g. `7131673574381518849`

## get_aweme_id

- `url` (string, required): 作品链接/Video link — e.g. `https://www.tiktok.com/@owlcitymusic/video/7218694761253735723`

## get_creative_patterns

- `first_industry_id` (string, optional): 一级行业ID/First industry ID
- `period_type` (string, optional): 时间周期类型/Period type (week, month)
- `order_field` (string, optional): 排序字段/Order field (ctr, play_over_rate)
- `order_type` (string, optional): 排序方式/Sort order (desc, asc)
- `week` (string, optional): 特定周（可选）/Specific week (optional)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page

## get_creator_list

- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `sort_by` (string, optional): 排序方式/Sort by (follower, engagement, avg_views)
- `creator_country` (string, optional): 创作者国家/Creator country
- `audience_country` (string, optional): 受众国家/Audience country
- `audience_count` (integer, optional): 受众数量筛选/Audience count filter
- `keyword` (string, optional): 关键词/Keyword

## get_hashtag_creator

- `hashtag` (string, required): '标签名称，不包含#符号/Hashtag name (without # symbol)' — e.g. `blowup`

## get_hashtag_list

- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `period` (integer, optional): 时间范围（天）/Time period (days)
- `country_code` (string, optional): 国家代码/Country code
- `sort_by` (string, optional): 排序方式/Sort by (popular, new)
- `industry_id` (string, optional): 行业ID/Industry ID
- `filter_by` (string, optional): 筛选条件/Filter (new_on_board)

## get_keyword_details

- `keyword` (string, optional): 关键词（可选）/Keyword (optional)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `period` (integer, optional): 时间范围（天）/Time period (days)
- `country_code` (string, optional): 国家代码/Country code
- `order_by` (string, optional): 排序字段/Sort field
- `order_type` (string, optional): 排序方式/Sort order (desc, asc)
- `industry` (string, optional): 行业ID/Industry ID
- `objective` (string, optional): 广告目标/Ad objective
- `keyword_type` (string, optional): 关键词类型/Keyword type

## get_keyword_insights

- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `period` (integer, optional): 时间段（天）/Time period (days, 7/30/120/180)
- `country_code` (string, optional): 国家代码/Country code
- `order_by` (string, optional): 排序字段/Sort field (post, ctr, click_rate, etc.)
- `order_type` (string, optional): 排序方式/Sort order (desc, asc)
- `industry` (string, optional): 行业ID/Industry ID
- `objective` (string, optional): 广告目标/Ad objective
- `keyword_type` (string, optional): 关键词类型/Keyword type
- `keyword` (string, optional): 关键词/Keyword

## get_keyword_list

- `keyword` (string, optional): 关键词/Keyword
- `period` (integer, optional): 时间范围（天）/Time period (days)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `country_code` (string, optional): 国家代码/Country code
- `industry` (string, optional): 行业ID列表，逗号分隔/Industry IDs, comma separated

## get_live_room_id

- `live_room_url` (string, required): 直播间链接/Live room link — e.g. `https://www.tiktok.com/@maksukaracun/live`

## get_popular_trends

- `period` (integer, optional): 时间范围（天）/Time period (days)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `order_by` (string, optional): 排序字段/Order by (vv, like, comment, repost)
- `country_code` (string, optional): 国家代码/Country code

## get_product_detail

- `id` (string, required): 产品类目ID/Product category ID — e.g. `601583`
- `last` (integer, optional): 最近天数/Last days
- `ecom_type` (string, optional): 电商类型/E-commerce type
- `period_type` (string, optional): 时间类型/Period type
- `country_code` (string, optional): 国家代码/Country code

## get_product_metrics

- `id` (string, required): 产品类目ID/Product category ID — e.g. `601583`
- `last` (integer, optional): 最近天数/Last days
- `metrics` (string, optional): 指标类型，逗号分隔/Metrics types, comma separated
- `ecom_type` (string, optional): 电商类型/E-commerce type
- `period_type` (string, optional): 时间类型/Period type
- `country_code` (string, optional): 国家代码/Country code

## get_query_suggestions

- `count` (integer, optional): 建议数量/Suggestion count
- `scenario` (integer, optional): 场景类型/Scenario type

## get_recommended_ads

- `material_id` (string, required): 广告素材ID/Ad material ID — e.g. `7213258221116751874`
- `industry` (string, optional): 行业ID/Industry ID
- `country_code` (string, optional): 国家代码/Country code

## get_related_keywords

- `keyword` (string, optional): 目标关键词/Target keyword
- `period` (integer, optional): 时间段（天）/Time period (days, 7/30/120)
- `country_code` (string, optional): 国家/地区代码/Country code
- `rank_type` (string, optional): '排名类型/Rank type (popular: 热门, breakout: 突破性)'
- `content_type` (string, optional): 内容类型/Content type (keyword, hashtag)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page

## get_sec_user_id

- `url` (string, required): 用户主页链接/User homepage link — e.g. `https://www.tiktok.com/@tiktok`

## get_sound_detail

- `clip_id` (string, required): 音乐ID/Sound clip ID — e.g. `7251810329461147649`
- `period` (integer, optional): 时间范围（天）/Time period (days)
- `country_code` (string, optional): 国家代码/Country code

## get_sound_filters

- `rank_type` (string, optional): 排行类型/Rank type (popular, surging)

## get_sound_rank_list

- `period` (integer, optional): 时间范围（天）/Time period (days)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `rank_type` (string, optional): 排行类型/Rank type (popular, surging)
- `new_on_board` (boolean, optional): 是否只看新上榜/Only new on board
- `commercial_music` (boolean, optional): 是否商业音乐/Commercial music only
- `country_code` (string, optional): 国家代码/Country code

## get_sound_recommendations

- `clip_id` (string, required): 参考音乐ID/Reference sound clip ID — e.g. `7156826385225353217`
- `limit` (integer, optional): 推荐数量/Number of recommendations

## get_top_ads_spotlight

- `industry` (string, optional): 行业ID/Industry ID
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page

## get_top_products

- `last` (integer, optional): 最近天数/Last days
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `country_code` (string, optional): 国家代码/Country code
- `first_ecom_category_id` (string, optional): 电商类目ID，多个用逗号分隔/E-commerce category IDs, comma separated
- `ecom_type` (string, optional): 电商类型/E-commerce type (l3)
- `period_type` (string, optional): 时间类型/Period type (last)
- `order_by` (string, optional): 排序字段/Sort field (post, ctr, cvr)
- `order_type` (string, optional): 排序方式/Sort order (desc, asc)

## get_unique_id

- `url` (string, required): 用户主页链接/User homepage link — e.g. `https://www.tiktok.com/@tiktok`

## get_user_id

- `url` (string, required): 用户主页链接/User homepage link — e.g. `https://www.tiktok.com/@tiktok`

## get_user_id_and_sec_user_id_by_username

- `username` (string, required): 用户名/Username — e.g. `tiktok`

## handler_user_profile

- `user_id` (string, optional): 用户uid （可选，纯数字）/User uid (optional, pure number)
- `sec_user_id` (string, optional): 用户sec_user_id/User sec_user_id — e.g. `MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM`
- `unique_id` (string, optional): 用户unique_id （用户名）/User unique_id (username)

## open_tiktok_app_to_keyword_search

- `keyword` (string, required): 关键词/Keyword — e.g. `Evil0ctal`

## open_tiktok_app_to_send_private_message

- `uid` (string, required): 用户id/User id — e.g. `7059867056504407087`

## open_tiktok_app_to_user_profile

- `uid` (string, required): 用户id/User id — e.g. `7059867056504407087`

## open_tiktok_app_to_video_detail

- `aweme_id` (string, required): 作品id/Video id — e.g. `7440436579409153311`

## search_ads

- `objective` (integer, optional): 广告目标类型/Ad objective (1:流量 2:应用安装 3:转化 4:视频浏览 5:触达 6:潜在客户 7:产品销售)
- `like` (integer, optional): 表现排名/Performance rank (1:前1-20% 2:前21-40% 3:前41-60% 4:前61-80%)
- `period` (integer, optional): 时间段/Time period (days)
- `industry` (string, optional): 行业ID/Industry ID
- `keyword` (string, optional): 搜索关键词/Search keyword
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `order_by` (string, optional): 排序方式/Sort by (for_you, likes)
- `country_code` (string, optional): 国家代码/Country code
- `ad_format` (integer, optional): 广告格式/Ad format (1:视频)
- `ad_language` (string, optional): 广告语言/Ad language
- `search_id` (string, optional): 搜索ID（可选）/Search ID (optional)

## search_creators

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `jo`
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `sort_by` (string, optional): 排序方式/Sort by (follower, avg_views)
- `creator_country` (string, optional): 创作者国家/Creator country

## search_follower_list

- `user_id` (string, required): 用户ID/User ID — e.g. `7540849481009988663`
- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `a`

## search_following_list

- `user_id` (string, required): 用户ID/User ID — e.g. `7540849481009988663`
- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `a`

## search_sound

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `taylor swift`
- `period` (integer, optional): 时间范围（天）/Time period (days)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `rank_type` (string, optional): 排行类型/Rank type (popular, surging)
- `new_on_board` (boolean, optional): 是否只看新上榜/Only new on board
- `commercial_music` (boolean, optional): 是否商业音乐/Commercial music only
- `country_code` (string, optional): 国家代码/Country code

## search_sound_hint

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `taylor swift`
- `period` (integer, optional): 时间范围（天）/Time period (days)
- `page` (integer, optional): 页码/Page number
- `limit` (integer, optional): 每页数量/Items per page
- `rank_type` (string, optional): 排行类型/Rank type (popular, surging)
- `country_code` (string, optional): 国家代码/Country code
- `filter_by_checked` (boolean, optional): 是否只看已验证/Only verified
- `commercial_music` (boolean, optional): 是否商业音乐/Commercial music only

## tiktok_live_room

- `live_room_url` (string, required): 直播间链接/Live room link — e.g. `https://www.tiktok.com/@mpl.id.official/live`
- `danmaku_type` (string, required): 消息类型/Message type — e.g. `WebcastChatMessage`
