# TikTok（TikTok）API完整目录

> 共 206 个API，按能力域分类

## 数据采集（102个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个作品数据/Get single video data | GET | `/api/v1/tiktok/web/fetch_post_detail` | itemId |
| 2 | 获取单个作品数据 V2/Get single video data V2 | GET | `/api/v1/tiktok/web/fetch_post_detail_v2` | itemId |
| 3 | 获取探索作品数据/Get explore video data | GET | `/api/v1/tiktok/web/fetch_explore_post` | - |
| 4 | 获取用户的个人信息/Get user profile | GET | `/api/v1/tiktok/web/fetch_user_profile` | - |
| 5 | 获取用户的作品列表/Get user posts | GET | `/api/v1/tiktok/web/fetch_user_post` | secUid |
| 6 | 获取用户的转发作品列表/Get user reposts | GET | `/api/v1/tiktok/web/fetch_user_repost` | secUid |
| 7 | 获取用户的播放列表/Get user play list | GET | `/api/v1/tiktok/web/fetch_user_play_list` | secUid |
| 8 | 获取用户的合辑列表/Get user mix list | GET | `/api/v1/tiktok/web/fetch_user_mix` | mixId |
| 9 | 获取用户的直播详情/Get user live details | GET | `/api/v1/tiktok/web/fetch_user_live_detail` | uniqueId |
| 10 | Tag详情/Tag Detail | GET | `/api/v1/tiktok/web/fetch_tag_detail` | tag_name |
| 11 | Tag作品/Tag Post | GET | `/api/v1/tiktok/web/fetch_tag_post` | challengeID |
| 12 | 首页推荐作品/Home Feed | POST | `/api/v1/tiktok/web/fetch_home_feed` | - |
| 13 | 加密strData/Encrypt strData | GET | `/api/v1/tiktok/web/encrypt_strData` | data |
| 14 | 解密strData/Decrypt strData | GET | `/api/v1/tiktok/web/decrypt_strData` | encrypted_data |
| 15 | 获取用户unique_id/Get user unique_id | GET | `/api/v1/tiktok/web/get_unique_id` | url |
| 16 | 获取列表unique_id/Get list unique_id | POST | `/api/v1/tiktok/web/get_all_unique_id` | - |
| 17 | TikTok直播间弹幕参数获取/tiktok live room danmaku | GET | `/api/v1/tiktok/web/fetch_live_im_fetch` | room_id |
| 18 | 直播间开播状态检测/Live room start status check | GET | `/api/v1/tiktok/web/fetch_check_live_alive` | room_id |
| 19 | 批量直播间开播状态检测/Batch live room start status | GET | `/api/v1/tiktok/web/fetch_batch_check_live_alive` | room_ids |
| 20 | 通过直播链接获取直播间信息/Get live room information  | GET | `/api/v1/tiktok/web/fetch_tiktok_live_data` | live_room_url |
| 21 | 获取直播间首页推荐列表/Get live room homepage recom | GET | `/api/v1/tiktok/web/fetch_live_recommend` | related_live_tag |
| 22 | 获取直播间礼物列表/Get live room gift list | GET | `/api/v1/tiktok/web/fetch_live_gift_list` | - |
| 26 | 根据Gift ID查询礼物名称/Get gift name by gift ID | POST | `/api/v1/tiktok/web/fetch_gift_name_by_id` | - |
| 27 | 批量查询Gift ID对应的礼物名称($0.025/次,建议50个)/Batch | POST | `/api/v1/tiktok/web/fetch_gift_names_by_ids` | - |
| 30 | 获取单个作品数据/Get single video data | GET | `/api/v1/tiktok/app/v3/fetch_one_video` | aweme_id |
| 31 | 获取单个作品数据 V2/Get single video data V2 | GET | `/api/v1/tiktok/app/v3/fetch_one_video_v2` | aweme_id |
| 32 | 获取单个作品数据 V3(支持国家参数)/Get single video dat | GET | `/api/v1/tiktok/app/v3/fetch_one_video_v3` | aweme_id |
| 33 | 批量获取视频信息/Batch Get Video Information | POST | `/api/v1/tiktok/app/v3/fetch_multi_video` | - |
| 34 | 批量获取视频信息 V2/Batch Get Video Information  | POST | `/api/v1/tiktok/app/v3/fetch_multi_video_v2` | - |
| 35 | 根据分享链接获取单个作品数据/Get single video data by  | GET | `/api/v1/tiktok/app/v3/fetch_one_video_by_share_url_v2` | share_url |
| 36 | 根据分享链接获取单个作品数据/Get single video data by  | GET | `/api/v1/tiktok/app/v3/fetch_one_video_by_share_url` | share_url |
| 37 | 使用用户名获取用户 user_id 和 sec_user_id/Get user | GET | `/api/v1/tiktok/app/v3/get_user_id_and_sec_user_id_by_username` | username |
| 38 | 获取指定用户的信息/Get information of specified u | GET | `/api/v1/tiktok/app/v3/handler_user_profile` | - |
| 39 | 获取指定 Webcast 用户的信息/Get information of sp | GET | `/api/v1/tiktok/app/v3/fetch_webcast_user_info` | - |
| 40 | 通过用户名获取用户账号国家地区/Get user account country | GET | `/api/v1/tiktok/app/v3/fetch_user_country_by_username` | username |
| 41 | 获取类似用户推荐/Similar User Recommendations | GET | `/api/v1/tiktok/app/v3/fetch_similar_user_recommendations` | sec_uid |
| 42 | 获取用户转发的作品数据/Get user repost video data | GET | `/api/v1/tiktok/app/v3/fetch_user_repost_videos` | user_id |
| 43 | 获取用户主页作品数据 V1/Get user homepage video da | GET | `/api/v1/tiktok/app/v3/fetch_user_post_videos` | - |
| 44 | 获取用户主页作品数据 V2/Get user homepage video da | GET | `/api/v1/tiktok/app/v3/fetch_user_post_videos_v2` | - |
| 45 | 获取用户主页作品数据 V3（精简数据-更快速）/Get user homepag | GET | `/api/v1/tiktok/app/v3/fetch_user_post_videos_v3` | - |
| 46 | 获取指定音乐的详情数据/Get details of specified mus | GET | `/api/v1/tiktok/app/v3/fetch_music_detail` | music_id |
| 47 | 获取指定音乐的视频列表数据/Get video list of specifie | GET | `/api/v1/tiktok/app/v3/fetch_music_video_list` | music_id |
| 48 | 获取指定话题的详情数据/Get details of specified has | GET | `/api/v1/tiktok/app/v3/fetch_hashtag_detail` | ch_id |
| 49 | 获取指定话题的作品数据/Get video list of specified  | GET | `/api/v1/tiktok/app/v3/fetch_hashtag_video_list` | ch_id |
| 50 | 获取指定直播间的数据/Get data of specified live ro | GET | `/api/v1/tiktok/app/v3/fetch_live_room_info` | room_id |
| 51 | 检测直播间是否在线/Check if live room is online | GET | `/api/v1/tiktok/app/v3/check_live_room_online` | room_id |
| 52 | 批量检测直播间是否在线/Batch check if live rooms ar | POST | `/api/v1/tiktok/app/v3/check_live_room_online_batch` | - |
| 53 | 获取分享短链接/Get share short link | GET | `/api/v1/tiktok/app/v3/fetch_share_short_link` | url |
| 54 | 获取分享二维码/Get share QR code | GET | `/api/v1/tiktok/app/v3/fetch_share_qr_code` | object_id |
| 55 | 通过分享链接获取店铺ID/Get Shop ID by Share Link | GET | `/api/v1/tiktok/app/v3/fetch_shop_id_by_share_link` | share_link |
| 56 | 通过分享链接获取商品ID/Get Product ID by Share Lin | GET | `/api/v1/tiktok/app/v3/fetch_product_id_by_share_link` | share_link |
| 57 | 获取商品详情数据（即将弃用，使用 fetch_product_detail_v2 | GET | `/api/v1/tiktok/app/v3/fetch_product_detail` | product_id |
| 58 | 获取商品详情数据V2/Get product detail data V2 | GET | `/api/v1/tiktok/app/v3/fetch_product_detail_v2` | product_id |
| 59 | 获取商品详情数据V3 / Get product detail data V3 | GET | `/api/v1/tiktok/app/v3/fetch_product_detail_v3` | product_id |
| 60 | 获取商品详情数据V4 / Get product detail data V4 | GET | `/api/v1/tiktok/app/v3/fetch_product_detail_v4` | product_id |
| 61 | 获取商品评价数据/Get product review data | GET | `/api/v1/tiktok/app/v3/fetch_product_review` | product_id |
| 62 | 获取商家主页Page列表数据/Get shop home page list d | GET | `/api/v1/tiktok/app/v3/fetch_shop_home_page_list` | seller_id |
| 63 | 获取商家主页数据/Get shop home page data | GET | `/api/v1/tiktok/app/v3/fetch_shop_home` | page_id, seller_id |
| 64 | 获取商家商品推荐数据/Get shop product recommend da | GET | `/api/v1/tiktok/app/v3/fetch_shop_product_recommend` | seller_id |
| 65 | 获取商家商品列表数据/Get shop product list data | GET | `/api/v1/tiktok/app/v3/fetch_shop_product_list` | seller_id |
| 66 | 获取商家商品列表数据 V2/Get shop product list data | GET | `/api/v1/tiktok/app/v3/fetch_shop_product_list_v2` | seller_id |
| 67 | 获取商家信息数据/Get shop information data | GET | `/api/v1/tiktok/app/v3/fetch_shop_info` | shop_id |
| 68 | 获取商家产品分类数据/Get shop product category dat | GET | `/api/v1/tiktok/app/v3/fetch_shop_product_category` | seller_id |
| 69 | 获取用户音乐列表数据/Get user music list data | GET | `/api/v1/tiktok/app/v3/fetch_user_music_list` | sec_uid |
| 70 | 获取内容翻译数据/Get content translation data | POST | `/api/v1/tiktok/app/v3/fetch_content_translate` | - |
| 71 | 获取主页视频推荐数据/Get home feed(recommend) vide | POST | `/api/v1/tiktok/app/v3/fetch_home_feed` | - |
| 73 | 获取直播间商品列表数据/Get live room product list d | GET | `/api/v1/tiktok/app/v3/fetch_live_room_product_list` | room_id, author_id |
| 74 | 获取直播间商品列表数据 V2 /Get live room product li | GET | `/api/v1/tiktok/app/v3/fetch_live_room_product_list_v2` | room_id, author_id |
| 77 | 获取单个广告详情/Get single ad detail | GET | `/api/v1/tiktok/ads/get_ads_detail` | ads_id |
| 78 | 获取关键词洞察数据/Get keyword insights data | GET | `/api/v1/tiktok/ads/get_keyword_insights` | - |
| 79 | 获取热门产品列表/Get top products list | GET | `/api/v1/tiktok/ads/get_top_products` | - |
| 80 | 获取热门标签列表/Get popular hashtags list | GET | `/api/v1/tiktok/ads/get_hashtag_list` | - |
| 81 | 获取关键词列表/Get keyword list | GET | `/api/v1/tiktok/ads/get_keyword_list` | - |
| 82 | 获取热门广告聚光灯/Get top ads spotlight | GET | `/api/v1/tiktok/ads/get_top_ads_spotlight` | - |
| 83 | 获取广告百分位数据/Get ad percentile data | GET | `/api/v1/tiktok/ads/get_ad_percentile` | material_id |
| 84 | 获取推荐广告/Get recommended ads | GET | `/api/v1/tiktok/ads/get_recommended_ads` | material_id |
| 85 | 获取关键词筛选器/Get keyword filters | GET | `/api/v1/tiktok/ads/get_keyword_filters` | - |
| 86 | 获取相关关键词/Get related keywords | GET | `/api/v1/tiktok/ads/get_related_keywords` | - |
| 87 | 获取关键词详细信息/Get keyword details | GET | `/api/v1/tiktok/ads/get_keyword_details` | - |
| 88 | 获取产品筛选器/Get product filters | GET | `/api/v1/tiktok/ads/get_product_filters` | - |
| 89 | 获取产品指标数据/Get product metrics | GET | `/api/v1/tiktok/ads/get_product_metrics` | id |
| 90 | 获取产品详细信息/Get product detail | GET | `/api/v1/tiktok/ads/get_product_detail` | id |
| 91 | 获取标签筛选器/Get hashtag filters | GET | `/api/v1/tiktok/ads/get_hashtag_filters` | - |
| 92 | 获取音乐筛选器/Get sound filters | GET | `/api/v1/tiktok/ads/get_sound_filters` | - |
| 93 | 获取音乐详情/Get sound detail | GET | `/api/v1/tiktok/ads/get_sound_detail` | clip_id |
| 94 | 获取音乐推荐/Get sound recommendations | GET | `/api/v1/tiktok/ads/get_sound_recommendations` | clip_id |
| 95 | 获取商品详情V1(桌面端-数据完整)/Get product detail V1 | GET | `/api/v1/tiktok/shop/web/fetch_product_detail` | product_id |
| 96 | 获取商品详情V2(移动端-数据少)/Get product detail V2  | GET | `/api/v1/tiktok/shop/web/fetch_product_detail_v2` | product_id |
| 97 | 获取商品详情V3(移动端-数据完整)/Get product detail V3 | GET | `/api/v1/tiktok/shop/web/fetch_product_detail_v3` | product_id |
| 98 | 获取商家商品列表V1/Get seller products list V1 | GET | `/api/v1/tiktok/shop/web/fetch_seller_products_list` | seller_id |
| 99 | 获取商家商品列表V2(移动端)/Get seller products list | GET | `/api/v1/tiktok/shop/web/fetch_seller_products_list_v2` | seller_id |
| 100 | 获取商品分类列表/Get product category list | GET | `/api/v1/tiktok/shop/web/fetch_products_category_list` | - |
| 101 | 根据分类ID获取商品列表/Get products by category ID | GET | `/api/v1/tiktok/shop/web/fetch_products_by_category_id` | category_id |
| 102 | 获取热卖商品列表/Get hot selling products list | GET | `/api/v1/tiktok/shop/web/fetch_hot_selling_products_list` | - |

## 数据分析（20个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取每日热门内容作品数据/Get daily trending video da | GET | `/api/v1/tiktok/web/fetch_trending_post` | - |
| 2 | 音乐排行榜/Music Chart List | GET | `/api/v1/tiktok/app/v3/fetch_music_chart_list` | - |
| 3 | 获取直播间排行榜数据/Get live room ranking list | GET | `/api/v1/tiktok/app/v3/fetch_live_ranking_list` | room_id, anchor_id |
| 4 | 获取直播每日榜单数据/Get live daily rank data | GET | `/api/v1/tiktok/app/v3/fetch_live_daily_rank` | - |
| 5 | 获取创作者直播概览/Get Creator Live Overview | POST | `/api/v1/tiktok/creator/get_live_analytics_summary` | - |
| 6 | 获取创作者视频概览/Get Creator Video Overview | POST | `/api/v1/tiktok/creator/get_video_analytics_summary` | - |
| 7 | 获取创作者视频列表分析/Get Creator Video List Analy | POST | `/api/v1/tiktok/creator/get_video_list_analytics` | - |
| 8 | 获取创作者商品列表分析/Get Creator Product List Ana | POST | `/api/v1/tiktok/creator/get_product_analytics_list` | - |
| 9 | 获取视频详细分段统计数据/Get Video Detailed Statisti | POST | `/api/v1/tiktok/creator/get_video_detailed_stats` | - |
| 10 | 获取视频与商品关联统计数据/Get Video-Product Associat | POST | `/api/v1/tiktok/creator/get_video_to_product_stats` | - |
| 11 | 获取视频受众分析数据/Get Video Audience Analysis D | POST | `/api/v1/tiktok/creator/get_video_audience_stats` | - |
| 12 | 获取作品的统计数据/Get video metrics | GET | `/api/v1/tiktok/analytics/fetch_video_metrics` | item_id |
| 13 | 检测视频虚假流量分析/Detect fake views in video | GET | `/api/v1/tiktok/analytics/detect_fake_views` | item_id |
| 14 | 获取视频评论关键词分析/Get comment keywords analysi | GET | `/api/v1/tiktok/analytics/fetch_comment_keywords` | item_id |
| 15 | 获取创作者信息和里程碑数据/Get creator info and miles | GET | `/api/v1/tiktok/analytics/fetch_creator_info_and_milestones` | user_id |
| 16 | 获取热门音乐排行榜/Get popular sound rankings | GET | `/api/v1/tiktok/ads/get_sound_rank_list` | - |
| 17 | 获取广告关键帧分析/Get ad keyframe analysis | GET | `/api/v1/tiktok/ads/get_ad_keyframe_analysis` | material_id |
| 18 | 获取广告互动分析/Get ad interactive analysis | GET | `/api/v1/tiktok/ads/get_ad_interactive_analysis` | material_id |
| 19 | 获取创意模式排行榜/Get creative pattern rankings | GET | `/api/v1/tiktok/ads/get_creative_patterns` | - |
| 20 | 获取流行趋势视频/Get popular trend videos | GET | `/api/v1/tiktok/ads/get_popular_trends` | - |

## 搜索查询（32个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取每日趋势搜索关键词/Get daily trending search wo | GET | `/api/v1/tiktok/web/fetch_trending_searchwords` | - |
| 2 | 获取综合搜索列表/Get general search list | GET | `/api/v1/tiktok/web/fetch_general_search` | keyword |
| 3 | 搜索关键字推荐/Search keyword suggest | GET | `/api/v1/tiktok/web/fetch_search_keyword_suggest` | keyword |
| 4 | 搜索用户/Search user | GET | `/api/v1/tiktok/web/fetch_search_user` | keyword |
| 5 | 搜索视频/Search video | GET | `/api/v1/tiktok/web/fetch_search_video` | keyword |
| 6 | 搜索直播/Search live | GET | `/api/v1/tiktok/web/fetch_search_live` | keyword |
| 7 | 搜索照片/Search photo | GET | `/api/v1/tiktok/web/fetch_search_photo` | keyword |
| 8 | 获取指定关键词的综合搜索结果/Get comprehensive search  | GET | `/api/v1/tiktok/app/v3/fetch_general_search_result` | keyword |
| 9 | 获取指定关键词的视频搜索结果/Get video search results  | GET | `/api/v1/tiktok/app/v3/fetch_video_search_result` | keyword |
| 10 | 获取指定关键词的用户搜索结果/Get user search results o | GET | `/api/v1/tiktok/app/v3/fetch_user_search_result` | keyword |
| 11 | 获取指定关键词的音乐搜索结果/Get music search results  | GET | `/api/v1/tiktok/app/v3/fetch_music_search_result` | keyword |
| 12 | 获取指定关键词的话题搜索结果/Get hashtag search result | GET | `/api/v1/tiktok/app/v3/fetch_hashtag_search_result` | keyword |
| 13 | 获取指定关键词的直播搜索结果/Get live search results o | GET | `/api/v1/tiktok/app/v3/fetch_live_search_result` | keyword |
| 14 | 获取地点搜索结果/Get location search results | GET | `/api/v1/tiktok/app/v3/fetch_location_search` | keyword |
| 15 | 创作者搜索洞察/Creator Search Insights | GET | `/api/v1/tiktok/app/v3/fetch_creator_search_insights` | - |
| 16 | 创作者搜索洞察详情/Creator Search Insights Detail | GET | `/api/v1/tiktok/app/v3/fetch_creator_search_insights_detail` | query_id_str |
| 17 | 创作者搜索洞察趋势/Creator Search Insights Trend | GET | `/api/v1/tiktok/app/v3/fetch_creator_search_insights_trend` | query_id_str |
| 18 | 创作者搜索洞察相关视频/Creator Search Insights Vide | GET | `/api/v1/tiktok/app/v3/fetch_creator_search_insights_videos` | keyword |
| 19 | 搜索粉丝列表/Search follower list | GET | `/api/v1/tiktok/app/v3/search_follower_list` | user_id, keyword |
| 20 | 搜索关注列表/Search following list | GET | `/api/v1/tiktok/app/v3/search_following_list` | user_id, keyword |
| 21 | 获取商品搜索结果/Get product search results | GET | `/api/v1/tiktok/app/v3/fetch_product_search` | keyword |
| 22 | 生成TikTok分享链接，唤起TikTok APP，跳转指定关键词搜索结果/Ge | GET | `/api/v1/tiktok/app/v3/open_tiktok_app_to_keyword_search` | keyword |
| 23 | 搜索广告/Search ads | GET | `/api/v1/tiktok/ads/search_ads` | - |
| 24 | 获取查询建议/Get query suggestions | GET | `/api/v1/tiktok/ads/get_query_suggestions` | - |
| 25 | 搜索音乐提示/Search sound hints | GET | `/api/v1/tiktok/ads/search_sound_hint` | keyword |
| 26 | 搜索音乐/Search sounds | GET | `/api/v1/tiktok/ads/search_sound` | keyword |
| 27 | 搜索创作者/Search creators | GET | `/api/v1/tiktok/ads/search_creators` | keyword |
| 28 | 获取搜索关键词建议V1/Get search keyword suggestio | GET | `/api/v1/tiktok/shop/web/fetch_search_word_suggestion` | search_word |
| 29 | 获取搜索关键词建议V2(移动端)/Get search keyword sugg | GET | `/api/v1/tiktok/shop/web/fetch_search_word_suggestion_v2` | search_word |
| 30 | 搜索商品列表V1/Search products list V1 | GET | `/api/v1/tiktok/shop/web/fetch_search_products_list` | search_word |
| 31 | 搜索商品列表V2(移动端)/Search products list V2 (M | GET | `/api/v1/tiktok/shop/web/fetch_search_products_list_v2` | search_word |
| 32 | 搜索商品列表V3/Search products list V3 | GET | `/api/v1/tiktok/shop/web/fetch_search_products_list_v3` | keyword |

## 互动操作（20个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取用户的点赞列表/Get user likes | GET | `/api/v1/tiktok/web/fetch_user_like` | secUid |
| 2 | 获取用户的收藏列表/Get user favorites | GET | `/api/v1/tiktok/web/fetch_user_collect` | cookie, secUid |
| 3 | 获取作品的评论列表/Get video comments | GET | `/api/v1/tiktok/web/fetch_post_comment` | aweme_id |
| 4 | 获取作品的评论回复列表/Get video comment replies | GET | `/api/v1/tiktok/web/fetch_post_comment_reply` | item_id, comment_id |
| 5 | 获取用户的粉丝列表/Get user followers | GET | `/api/v1/tiktok/web/fetch_user_fans` | secUid |
| 6 | 获取用户的关注列表/Get user followings | GET | `/api/v1/tiktok/web/fetch_user_follow` | secUid |
| 7 | 获取用户喜欢作品数据/Get user like video data | GET | `/api/v1/tiktok/app/v3/fetch_user_like_videos` | sec_user_id |
| 8 | 获取单个视频评论数据/Get single video comments dat | GET | `/api/v1/tiktok/app/v3/fetch_video_comments` | aweme_id |
| 9 | 获取指定视频的评论回复数据/Get comment replies data o | GET | `/api/v1/tiktok/app/v3/fetch_video_comment_replies` | item_id, comment_id |
| 10 | 获取指定用户的粉丝列表数据/Get follower list of speci | GET | `/api/v1/tiktok/app/v3/fetch_user_follower_list` | - |
| 11 | 获取指定用户的关注列表数据/Get following list of spec | GET | `/api/v1/tiktok/app/v3/fetch_user_following_list` | - |
| 12 | 获取商品评论V1/Get product reviews V1 | GET | `/api/v1/tiktok/shop/web/fetch_product_reviews_v1` | product_id |
| 13 | 获取商品评论V2/Get product reviews V2 | GET | `/api/v1/tiktok/shop/web/fetch_product_reviews_v2` | product_id |
| 14 | 申请使用TikTok交互API权限（Scope）/Apply for TikTo | GET | `/api/v1/tiktok/interaction/apply` | api_key, invite_code |
| 15 | 发送评论/Post comment | POST | `/api/v1/tiktok/interaction/post_comment` | - |
| 16 | 回复评论/Reply to comment | POST | `/api/v1/tiktok/interaction/reply_comment` | - |
| 17 | 点赞/Like | POST | `/api/v1/tiktok/interaction/like` | - |
| 18 | 关注/Follow | POST | `/api/v1/tiktok/interaction/follow` | - |
| 19 | 收藏/Collect | POST | `/api/v1/tiktok/interaction/collect` | - |
| 20 | 转发/Forward | POST | `/api/v1/tiktok/interaction/forward` | - |

## 工具服务（13个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 5 | 生成 XBogus/Generate XBogus | POST | `/api/v1/tiktok/web/generate_xbogus` | - |
| 10 | 生成哈希ID/Generate hashed ID | GET | `/api/v1/tiktok/web/generate_hashed_id` | email |
| 11 | 生成TikTok分享链接，唤起TikTok APP，跳转指定作品详情页/Gene | GET | `/api/v1/tiktok/app/v3/open_tiktok_app_to_video_detail` | aweme_id |
| 12 | 生成TikTok分享链接，唤起TikTok APP，跳转指定用户主页/Gener | GET | `/api/v1/tiktok/app/v3/open_tiktok_app_to_user_profile` | uid |
| 13 | 生成TikTok分享链接，唤起TikTok APP，给指定用户发送私信/Gene | GET | `/api/v1/tiktok/app/v3/open_tiktok_app_to_send_private_message` | uid |

## 内容解析（7个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 提取用户user_id/Extract user user_id | GET | `/api/v1/tiktok/web/get_user_id` | url |
| 2 | 提取用户sec_user_id/Extract user sec_user_id | GET | `/api/v1/tiktok/web/get_sec_user_id` | url |
| 3 | 提取列表用户sec_user_id/Extract list user sec_ | POST | `/api/v1/tiktok/web/get_all_sec_user_id` | - |
| 4 | 提取单个作品id/Extract single video id | GET | `/api/v1/tiktok/web/get_aweme_id` | url |
| 5 | 提取列表作品id/Extract list video id | POST | `/api/v1/tiktok/web/get_all_aweme_id` | - |
| 6 | 提取直播间弹幕/Extract live room danmaku | GET | `/api/v1/tiktok/web/tiktok_live_room` | live_room_url, danmaku_type |
| 7 | 根据直播间链接提取直播间ID/Extract live room ID from | GET | `/api/v1/tiktok/web/get_live_room_id` | live_room_url |

## 创作者/达人（12个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取带货创作者信息/Get shopping creator informati | GET | `/api/v1/tiktok/app/v3/fetch_creator_info` | creator_uid |
| 2 | 获取创作者橱窗商品列表/Get creator showcase product | GET | `/api/v1/tiktok/app/v3/fetch_creator_showcase_product_list` | kol_id |
| 3 | 获取创作者账号健康状态/Get Creator Account Health S | POST | `/api/v1/tiktok/creator/get_account_health_status` | - |
| 4 | 获取创作者账号违规记录列表/Get Creator Account Violat | POST | `/api/v1/tiktok/creator/get_account_violation_list` | - |
| 5 | 获取创作者账号概览/Get Creator Account Overview | POST | `/api/v1/tiktok/creator/get_account_insights_overview` | - |
| 6 | 获取创作者账号信息/Get Creator Account Info | POST | `/api/v1/tiktok/creator/get_creator_account_info` | - |
| 7 | 获取橱窗商品列表/Get Showcase Product List | POST | `/api/v1/tiktok/creator/get_showcase_product_list` | - |
| 8 | 获取视频关联商品列表/Get Video Associated Product  | POST | `/api/v1/tiktok/creator/get_video_associated_product_list` | - |
| 9 | 获取同款商品关联视频/Get Product Related Videos | POST | `/api/v1/tiktok/creator/get_product_related_videos` | - |
| 10 | 获取标签创作者信息/Get hashtag creator info | GET | `/api/v1/tiktok/ads/get_hashtag_creator` | hashtag |
| 11 | 获取创作者筛选器/Get creator filters | GET | `/api/v1/tiktok/ads/get_creator_filters` | - |
| 12 | 获取创作者列表/Get creator list | GET | `/api/v1/tiktok/ads/get_creator_list` | - |
