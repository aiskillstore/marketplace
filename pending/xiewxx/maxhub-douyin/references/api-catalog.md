# 抖音（Douyin）API完整目录

> 共 290 个API，按能力域分类

## 数据采集（70个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个作品数据/Get single video data | GET | `/api/v1/douyin/web/fetch_one_video` | aweme_id |
| 2 | 获取单个作品数据 V2/Get single video data V2 | GET | `/api/v1/douyin/web/fetch_one_video_v2` | aweme_id |
| 3 | 根据分享链接获取单个作品数据/Get single video data by  | GET | `/api/v1/douyin/web/fetch_one_video_by_share_url` | share_url |
| 4 | 获取视频的最高画质播放链接/Get the highest quality pl | GET | `/api/v1/douyin/web/fetch_video_high_quality_play_url` | - |
| 5 | 批量获取视频的最高画质播放链接/Batch get the highest qu | POST | `/api/v1/douyin/web/fetch_multi_video_high_quality_play_url` | - |
| 6 | 批量获取视频信息/Batch Get Video Information | POST | `/api/v1/douyin/web/fetch_multi_video` | - |
| 7 | 获取单个作品视频弹幕数据/Get single video danmaku da | GET | `/api/v1/douyin/web/fetch_one_video_danmaku` | item_id, duration, end_time, start_time |
| 8 | 获取首页推荐数据/Get home feed data | GET | `/api/v1/douyin/web/fetch_home_feed` | - |
| 9 | 获取相关作品推荐数据/Get related posts recommendat | GET | `/api/v1/douyin/web/fetch_related_posts` | aweme_id |
| 10 | 获取用户主页作品数据/Get user homepage video data | GET | `/api/v1/douyin/web/fetch_user_post_videos` | sec_user_id |
| 11 | 获取用户收藏作品数据/Get user collection video dat | POST | `/api/v1/douyin/web/fetch_user_collection_videos` | - |
| 12 | 获取用户收藏夹/Get user collection | POST | `/api/v1/douyin/web/fetch_user_collects` | - |
| 13 | 获取用户收藏夹数据/Get user collection data | GET | `/api/v1/douyin/web/fetch_user_collects_videos` | collects_id |
| 14 | 获取用户合辑作品数据/Get user mix video data | GET | `/api/v1/douyin/web/fetch_user_mix_videos` | mix_id |
| 15 | 获取用户直播流数据/Get user live video data | GET | `/api/v1/douyin/web/fetch_user_live_videos` | webcast_id |
| 16 | 通过sec_uid获取指定用户的直播流数据/Get live video dat | GET | `/api/v1/douyin/web/fetch_user_live_videos_by_sec_uid` | sec_uid |
| 17 | 通过room_id获取指定用户的直播流数据 V1/Get live video  | GET | `/api/v1/douyin/web/fetch_user_live_videos_by_room_id` | room_id |
| 18 | 通过room_id获取指定用户的直播流数据 V2/Gets the live s | GET | `/api/v1/douyin/web/fetch_user_live_videos_by_room_id_v2` | room_id |
| 19 | 抖音直播间商品信息/Douyin live room product infor | GET | `/api/v1/douyin/web/fetch_live_room_product_result` | room_id, author_id |
| 20 | 获取商品详情/Get product detail | GET | `/api/v1/douyin/web/fetch_product_detail` | product_id |
| 21 | 获取商品SKU列表/Get product SKU list | GET | `/api/v1/douyin/web/fetch_product_sku_list` | product_id, author_id |
| 22 | 获取商品优惠券信息/Get product coupon information | GET | `/api/v1/douyin/web/fetch_product_coupon` | product_id, shop_id, price, author_id, sec_user_id |
| 23 | 获取商品评价评分/Get product review score | GET | `/api/v1/douyin/web/fetch_product_review_score` | product_id, shop_id |
| 24 | 获取商品评价列表/Get product review list | GET | `/api/v1/douyin/web/fetch_product_review_list` | product_id, shop_id |
| 25 | 使用UID获取用户信息/Get user information by UID | GET | `/api/v1/douyin/web/fetch_user_profile_by_uid` | uid |
| 26 | 获取批量用户信息(最多10个)/Get batch user profile ( | GET | `/api/v1/douyin/web/fetch_batch_user_profile_v1` | sec_user_ids |
| 27 | 获取批量用户信息(最多50个)/Get batch user profile ( | GET | `/api/v1/douyin/web/fetch_batch_user_profile_v2` | sec_user_ids |
| 28 | 使用UID获取用户开播信息/Get user live information  | GET | `/api/v1/douyin/web/fetch_user_live_info_by_uid` | uid |
| 29 | 使用Short ID获取用户信息/Get user information by | GET | `/api/v1/douyin/web/fetch_user_profile_by_short_id` | short_id |
| 30 | 生成短链接 | GET | `/api/v1/douyin/web/handler_shorten_url` | target_url |
| 31 | 使用sec_user_id获取指定用户的信息/Get information o | GET | `/api/v1/douyin/web/handler_user_profile` | sec_user_id |
| 32 | 使用unique_id（抖音号）获取指定用户的信息/Get informatio | GET | `/api/v1/douyin/web/handler_user_profile_v2` | unique_id |
| 33 | 加密用户uid到sec_user_id/Encrypt user uid to  | GET | `/api/v1/douyin/web/encrypt_uid_to_sec_user_id` | uid |
| 34 | 根据抖音uid获取指定用户的信息/Get information of spec | GET | `/api/v1/douyin/web/handler_user_profile_v3` | uid |
| 35 | 根据sec_user_id获取指定用户的信息（性别，年龄，直播等级、牌子）/Ge | GET | `/api/v1/douyin/web/handler_user_profile_v4` | sec_user_id |
| 36 | 获取用户粉丝列表/Get user fans list | GET | `/api/v1/douyin/web/fetch_user_fans_list` | - |
| 37 | 话题作品/Challenge Posts | POST | `/api/v1/douyin/web/fetch_challenge_posts` | - |
| 38 | 抖音视频频道数据/Douyin video channel data | GET | `/api/v1/douyin/web/fetch_video_channel_result` | tag_id |
| 40 | 直播间号转房间号/Webcast id to room id | GET | `/api/v1/douyin/web/webcast_id_2_room_id` | webcast_id |
| 41 | 抖音直播间弹幕参数获取/Douyin live room danmaku par | GET | `/api/v1/douyin/web/fetch_live_im_fetch` | room_id, user_unique_id |
| 42 | 短剧作品/Series Video | GET | `/api/v1/douyin/web/fetch_series_aweme` | offset, count, content_type |
| 43 | 知识作品推荐/Knowledge Video | GET | `/api/v1/douyin/web/fetch_knowledge_aweme` | count |
| 44 | 游戏作品推荐/Game Video | GET | `/api/v1/douyin/web/fetch_game_aweme` | count |
| 45 | 二次元作品推荐/Anime Video | GET | `/api/v1/douyin/web/fetch_cartoon_aweme` | count |
| 46 | 音乐作品推荐/Music Video | GET | `/api/v1/douyin/web/fetch_music_aweme` | count |
| 47 | 美食作品推荐/Food Video | GET | `/api/v1/douyin/web/fetch_food_aweme` | count |
| 48 | 获取单个作品数据/Get single video data | GET | `/api/v1/douyin/app/v3/fetch_one_video` | aweme_id |
| 49 | 获取单个作品数据 V2/Get single video data V2 | GET | `/api/v1/douyin/app/v3/fetch_one_video_v2` | aweme_id |
| 50 | 获取单个作品数据 V3 (无版权限制)/Get single video dat | GET | `/api/v1/douyin/app/v3/fetch_one_video_v3` | aweme_id |
| 51 | 根据分享口令获取分享信息/Get share info by share cod | GET | `/api/v1/douyin/app/v3/fetch_share_info_by_share_code` | share_code |
| 52 | 批量获取视频信息 V1/Batch Get Video Information  | POST | `/api/v1/douyin/app/v3/fetch_multi_video` | - |
| 53 | 批量获取视频信息 V2/Batch Get Video Information  | POST | `/api/v1/douyin/app/v3/fetch_multi_video_v2` | - |
| 54 | 根据分享链接获取单个作品数据/Get single video data by  | GET | `/api/v1/douyin/app/v3/fetch_one_video_by_share_url` | share_url |
| 55 | 获取视频的最高画质播放链接/Get the highest quality pl | GET | `/api/v1/douyin/app/v3/fetch_video_high_quality_play_url` | - |
| 56 | 批量获取视频的最高画质播放链接/Batch get the highest qu | POST | `/api/v1/douyin/app/v3/fetch_multi_video_high_quality_play_url` | - |
| 58 | 获取指定用户的信息/Get information of specified u | GET | `/api/v1/douyin/app/v3/handler_user_profile` | sec_user_id |
| 59 | 获取用户粉丝列表/Get user fans list | GET | `/api/v1/douyin/app/v3/fetch_user_fans_list` | - |
| 60 | 获取用户主页作品数据/Get user homepage video data | GET | `/api/v1/douyin/app/v3/fetch_user_post_videos` | sec_user_id |
| 61 | 获取抖音视频合集详情数据/Get Douyin video mix detail | GET | `/api/v1/douyin/app/v3/fetch_video_mix_detail` | mix_id |
| 62 | 获取抖音视频合集作品列表数据/Get Douyin video mix post | GET | `/api/v1/douyin/app/v3/fetch_video_mix_post_list` | mix_id |
| 63 | 获取用户短剧合集列表/Get user series list | GET | `/api/v1/douyin/app/v3/fetch_user_series_list` | - |
| 64 | 获取短剧视频列表/Get series video list | GET | `/api/v1/douyin/app/v3/fetch_series_video_list` | series_id |
| 65 | 获取短剧详情信息/Get series detail | GET | `/api/v1/douyin/app/v3/fetch_series_detail` | series_id |
| 66 | 获取指定音乐的详情数据/Get details of specified mus | GET | `/api/v1/douyin/app/v3/fetch_music_detail` | music_id |
| 67 | 获取指定音乐的视频列表数据/Get video list of specifie | GET | `/api/v1/douyin/app/v3/fetch_music_video_list` | music_id |
| 68 | 获取指定话题的详情数据/Get details of specified has | GET | `/api/v1/douyin/app/v3/fetch_hashtag_detail` | ch_id |
| 69 | 获取指定话题的作品数据/Get video list of specified  | GET | `/api/v1/douyin/app/v3/fetch_hashtag_video_list` | ch_id |

## 互动操作（8个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取用户喜欢作品数据/Get user like video data | POST | `/api/v1/douyin/web/fetch_user_like_videos` | - |
| 2 | 获取用户关注列表/Get user following list | GET | `/api/v1/douyin/web/fetch_user_following_list` | - |
| 3 | 获取单个视频评论数据/Get single video comments dat | GET | `/api/v1/douyin/web/fetch_video_comments` | aweme_id |
| 4 | 获取指定视频的评论回复数据/Get comment replies data o | GET | `/api/v1/douyin/web/fetch_video_comment_replies` | item_id, comment_id |
| 5 | 获取用户关注列表 (弃用，使用 /api/v1/douyin/web/fetch | GET | `/api/v1/douyin/app/v3/fetch_user_following_list` | - |
| 6 | 获取用户喜欢作品数据/Get user like video data | GET | `/api/v1/douyin/app/v3/fetch_user_like_videos` | sec_user_id |
| 7 | 获取单个视频评论数据/Get single video comments dat | GET | `/api/v1/douyin/app/v3/fetch_video_comments` | aweme_id |
| 8 | 获取指定视频的评论回复数据/Get comment replies data o | GET | `/api/v1/douyin/app/v3/fetch_video_comment_replies` | item_id, comment_id |

## 数据分析（88个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取直播间送礼用户排行榜/Get live room gift user ran | GET | `/api/v1/douyin/web/fetch_live_gift_ranking` | room_id |
| 2 | 根据视频ID获取作品的统计数据（点赞数、下载数、播放数、分享数）/Get the | GET | `/api/v1/douyin/app/v3/fetch_video_statistics` | aweme_ids |
| 3 | 根据视频ID批量获取作品的统计数据（点赞数、下载数、播放数、分享数）/Get t | GET | `/api/v1/douyin/app/v3/fetch_multi_video_statistics` | aweme_ids |
| 4 | 获取创作者中心热门视频榜单/Get creator material cente | GET | `/api/v1/douyin/creator/fetch_creator_material_center_billboard` | - |
| 5 | 获取创作者中心创作热点/Get creator hot spot billboa | GET | `/api/v1/douyin/creator/fetch_creator_hot_spot_billboard` | - |
| 6 | 获取创作者热门话题榜单/Get creator hot topic billbo | GET | `/api/v1/douyin/creator/fetch_creator_hot_topic_billboard` | - |
| 7 | 获取创作者热门道具榜单/Get creator hot props billbo | GET | `/api/v1/douyin/creator/fetch_creator_hot_props_billboard` | - |
| 8 | 获取创作者热门挑战榜单/Get creator hot challenge bi | GET | `/api/v1/douyin/creator/fetch_creator_hot_challenge_billboard` | - |
| 9 | 获取创作者热门音乐榜单/Get creator hot music billbo | GET | `/api/v1/douyin/creator/fetch_creator_hot_music_billboard` | - |
| 10 | 获取作品流量来源统计/Fetch item play source statis | POST | `/api/v1/douyin/creator_v2/fetch_item_play_source` | - |
| 11 | 获取作品观看趋势分析/Fetch item watch trend analys | POST | `/api/v1/douyin/creator_v2/fetch_item_watch_trend` | - |
| 12 | 获取作品弹幕分析/Fetch item bullet analysis | POST | `/api/v1/douyin/creator_v2/fetch_item_danmaku_analysis` | - |
| 13 | 获取作品观众数据分析/Fetch item audience portrait | POST | `/api/v1/douyin/creator_v2/fetch_item_audience_portrait` | - |
| 14 | 获取作品观众其他数据分析/Fetch item audience others  | POST | `/api/v1/douyin/creator_v2/fetch_item_audience_others` | - |
| 15 | 获取投稿分析概览/Fetch item analysis overview | POST | `/api/v1/douyin/creator_v2/fetch_item_analysis_overview` | - |
| 16 | 获取所有有效日期/Get all valid dates | GET | `/api/v1/douyin/index/fetch_all_valid_date` | - |
| 17 | 获取关联分析有效日期/Get valid date for relation | GET | `/api/v1/douyin/index/fetch_valid_date_for_relation` | - |
| 18 | 获取所有地区列表/Get all area list | GET | `/api/v1/douyin/index/fetch_all_area` | - |
| 19 | 获取实时热点排行/Get current hot topics | GET | `/api/v1/douyin/index/fetch_current_hot_topic` | - |
| 20 | 获取热门关键词/Get hot words | GET | `/api/v1/douyin/index/fetch_hot_words` | - |
| 21 | 获取关键词有效日期/Get keyword valid date | POST | `/api/v1/douyin/index/fetch_keyword_valid_date` | keyword_list |
| 22 | 获取多关键词热度趋势/Get multi-keyword hot trend | POST | `/api/v1/douyin/index/fetch_multi_keyword_hot_trend` | keyword_list, start_date, end_date |
| 23 | 获取多关键词解读/Get multi-keyword interpretatio | POST | `/api/v1/douyin/index/fetch_multi_keyword_interpretation` | keyword_list, start_date, end_date |
| 24 | 获取关联词分析/Get relation word analysis | POST | `/api/v1/douyin/index/fetch_relation_word` | keyword, start_date, end_date |
| 25 | 获取人群画像/Get crowd portrait | POST | `/api/v1/douyin/index/fetch_portrait` | keyword, start_date, end_date |
| 26 | 获取用户订阅关键词/Get user subscribed keywords | POST | `/api/v1/douyin/index/fetch_get_user_sub_word` | - |
| 27 | 抖音 uid 转加密 user_id/Encrypt Douyin uid to | GET | `/api/v1/douyin/index/fetch_encrypt_user_id` | uid |
| 28 | 达人趋势对比/Daren compare users | POST | `/api/v1/douyin/index/fetch_daren_compare_users_stable` | user_list |
| 29 | 获取相似达人/Get similar daren | POST | `/api/v1/douyin/index/fetch_daren_similar_users` | user_id |
| 30 | 获取达人视频/Get daren top videos | POST | `/api/v1/douyin/index/fetch_daren_great_user_top_video` | user_id, start_date, end_date |
| 31 | 获取达人核心指标/Get daren core metrics | POST | `/api/v1/douyin/index/fetch_daren_great_item_mile_info` | user_id |
| 32 | 获取达人粉丝分析/Get daren fans analysis | POST | `/api/v1/douyin/index/fetch_daren_great_user_fans_info` | user_id |
| 33 | 获取品牌指数/Get brand index | POST | `/api/v1/douyin/index/fetch_brand_valid_info` | keyword_list |
| 34 | 获取品牌雷达图/Get brand radar chart | POST | `/api/v1/douyin/index/fetch_brand_radar_chart` | brand_name, start_date, end_date |
| 35 | 获取品牌趋势线/Get brand trend lines | POST | `/api/v1/douyin/index/fetch_brand_lines` | brand_name, start_date, end_date |
| 36 | 获取品牌周期数据/Get brand cycles | POST | `/api/v1/douyin/index/fetch_brand_cycles` | brand_name, start_date, end_date |
| 37 | 获取品牌主动排行周榜/Get brand initiative rank wee | POST | `/api/v1/douyin/index/fetch_brand_initiative_rank_weekly` | brand_name, start_date, end_date |
| 38 | 创作指南有效日期/Get content valid date | GET | `/api/v1/douyin/index/fetch_content_valid_date` | - |
| 39 | 热门视频时间范围/Brand hot videos time scope | POST | `/api/v1/douyin/index/fetch_brand_hot_videos_time_scope` | - |
| 40 | 创作热门关键词/Content creative keywords | POST | `/api/v1/douyin/index/fetch_content_creative_keywords` | tag_id, end_date |
| 41 | 关键词相关视频/Creative keyword related items | POST | `/api/v1/douyin/index/fetch_content_creative_keyword_items` | tag_id, end_date, keyword |
| 42 | 创作热门话题/Content creative topic | POST | `/api/v1/douyin/index/fetch_content_creative_topic` | tag_id, end_date |
| 43 | 内容发布趋势/Content publish trend | GET | `/api/v1/douyin/index/fetch_content_publish_trend` | tag_id, start_date, end_date |
| 44 | 创作时长分布/Content creative duration | POST | `/api/v1/douyin/index/fetch_content_creative_duration` | tag_id, end_date |
| 45 | 创作者画像/Content author portrait | POST | `/api/v1/douyin/index/fetch_content_author_portrait` | tag_id, end_date |
| 46 | 消费者画像/Content consumer portrait | POST | `/api/v1/douyin/index/fetch_content_consumer_portrait` | tag_id, end_date |
| 47 | 互动趋势/Content interact trend | POST | `/api/v1/douyin/index/fetch_content_interact_trend` | tag_id, start_date, end_date |
| 48 | 消费趋势/Content consume trend | POST | `/api/v1/douyin/index/fetch_content_consume_trend` | tag_id, start_date, end_date |
| 49 | 获取推荐报告/Get recommended insight reports | GET | `/api/v1/douyin/index/fetch_insight_recommend` | - |
| 50 | 获取报告详情/Get report detail | GET | `/api/v1/douyin/index/fetch_report_detail` | report_id |
| 51 | 获取报告相关推荐/Get related insight recommendat | GET | `/api/v1/douyin/index/fetch_insight_get_rec` | report_id |
| 52 | 获取中国城市列表/Fetch Chinese city list | GET | `/api/v1/douyin/billboard/fetch_city_list` | - |
| 53 | 获取垂类内容标签/Fetch vertical content tags | GET | `/api/v1/douyin/billboard/fetch_content_tag` | - |
| 54 | 获取热点榜分类/Fetch hot list category | GET | `/api/v1/douyin/billboard/fetch_hot_category_list` | billboard_type |
| 55 | 获取上升热点榜/Fetch rising hot list | GET | `/api/v1/douyin/billboard/fetch_hot_rise_list` | page, page_size, order |
| 56 | 获取同城热点榜/Fetch city hot list | GET | `/api/v1/douyin/billboard/fetch_hot_city_list` | page, page_size, order |
| 57 | 获取挑战热榜/Fetch hot challenge list | GET | `/api/v1/douyin/billboard/fetch_hot_challenge_list` | page, page_size |
| 58 | 获取热点总榜/Fetch total hot list | GET | `/api/v1/douyin/billboard/fetch_hot_total_list` | page, page_size, type |
| 59 | 获取活动日历/Fetch activity calendar | POST | `/api/v1/douyin/billboard/fetch_hot_calendar_list` | - |
| 60 | 获取活动日历详情/Fetch activity calendar detail | GET | `/api/v1/douyin/billboard/fetch_hot_calendar_detail` | calendar_id |
| 61 | 获取作品点赞观众画像-仅限热门榜/Fetch work like audienc | GET | `/api/v1/douyin/billboard/fetch_hot_user_portrait_list` | aweme_id |
| 62 | 获取作品评论分析-词云权重/Fetch work comment analysi | GET | `/api/v1/douyin/billboard/fetch_hot_comment_word_list` | aweme_id |
| 63 | 获取作品数据趋势/Fetch post data trend | GET | `/api/v1/douyin/billboard/fetch_hot_item_trends_list` | - |
| 64 | 获取热门账号/Fetch hot account list | POST | `/api/v1/douyin/billboard/fetch_hot_account_list` | - |
| 65 | 获取账号粉丝数据趋势/Fetch account fan data trend | GET | `/api/v1/douyin/billboard/fetch_hot_account_trends_list` | sec_uid |
| 66 | 获取账号作品分析-上周/Fetch account work analysis  | GET | `/api/v1/douyin/billboard/fetch_hot_account_item_analysis_list` | sec_uid |
| 67 | 获取粉丝画像/Fetch fan portrait | GET | `/api/v1/douyin/billboard/fetch_hot_account_fans_portrait_list` | sec_uid |
| 68 | 获取粉丝兴趣作者 20个用户/Fetch fan interest author | GET | `/api/v1/douyin/billboard/fetch_hot_account_fans_interest_account_list` | sec_uid |
| 69 | 获取粉丝近3天感兴趣的话题 10个话题/Fetch fan interest t | GET | `/api/v1/douyin/billboard/fetch_hot_account_fans_interest_topic_list` | sec_uid |
| 70 | 获取视频热榜/Fetch video hot list | POST | `/api/v1/douyin/billboard/fetch_hot_total_video_list` | - |
| 71 | 获取低粉爆款榜/Fetch low fan explosion list | POST | `/api/v1/douyin/billboard/fetch_hot_total_low_fan_list` | - |
| 72 | 获取高完播率榜/Fetch high completion rate list | POST | `/api/v1/douyin/billboard/fetch_hot_total_high_play_list` | - |
| 73 | 获取高点赞率榜/Fetch high like rate list | POST | `/api/v1/douyin/billboard/fetch_hot_total_high_like_list` | - |
| 74 | 获取高涨粉率榜/Fetch high fan rate list | POST | `/api/v1/douyin/billboard/fetch_hot_total_high_fan_list` | - |
| 75 | 获取话题热榜/Fetch topic hot list | POST | `/api/v1/douyin/billboard/fetch_hot_total_topic_list` | - |
| 76 | 获取热度飙升的话题榜/Fetch topic list with rising  | POST | `/api/v1/douyin/billboard/fetch_hot_total_high_topic_list` | - |
| 77 | 获取全部热门内容词/Fetch all hot content words | POST | `/api/v1/douyin/billboard/fetch_hot_total_hot_word_list` | - |
| 78 | 获取内容词详情/Fetch content word details | GET | `/api/v1/douyin/billboard/fetch_hot_total_hot_word_detail_list` | keyword, word_id, query_day |
| 79 | 获取kol转化能力分析V1/Get kol Conversion Ability | GET | `/api/v1/douyin/xingtu/kol_conversion_ability_analysis_v1` | kolId, _range |
| 80 | 获取kol星图指数V1/Get kol Xingtu Index V1 | GET | `/api/v1/douyin/xingtu/kol_xingtu_index_v1` | kolId |
| 81 | 获取kol性价比能力分析V1/Get kol Cp Info V1 | GET | `/api/v1/douyin/xingtu/kol_cp_info_v1` | kolId |
| 82 | 获取kol热词分析评论V1/Get Author Hot Comment Tok | GET | `/api/v1/douyin/xingtu/author_hot_comment_tokens_v1` | kolId |
| 83 | 获取kol热词分析内容V1/Get Author Content Hot Com | GET | `/api/v1/douyin/xingtu/author_content_hot_comment_keywords_v1` | kolId |
| 84 | 获取星图热榜分类/Get Ranking List Catalog | GET | `/api/v1/douyin/xingtu_v2/get_ranking_list_catalog` | - |
| 85 | 获取星图达人商业榜数据/Get Ranking List Data | GET | `/api/v1/douyin/xingtu_v2/get_ranking_list_data` | - |
| 86 | 获取短剧演员热榜分类/Get Playlet Actor Rank Catalo | POST | `/api/v1/douyin/xingtu_v2/get_playlet_actor_rank_catalog` | - |
| 87 | 获取短剧演员热榜/Get Playlet Actor Rank List | GET | `/api/v1/douyin/xingtu_v2/get_playlet_actor_rank_list` | - |
| 88 | 获取内容趋势指南/Get Content Trend Guide | GET | `/api/v1/douyin/xingtu_v2/get_content_trend_guide` | - |

## 搜索查询（59个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | [已弃用/Deprecated] 获取指定关键词的综合搜索结果/Get comp | GET | `/api/v1/douyin/web/fetch_general_search_result` | keyword |
| 2 | [已弃用/Deprecated] 获取指定关键词的视频搜索结果/Get vide | GET | `/api/v1/douyin/web/fetch_video_search_result` | keyword |
| 3 | 获取指定关键词的视频搜索结果 V2 （废弃，替代接口请参考下方文档）/Get v | GET | `/api/v1/douyin/web/fetch_video_search_result_v2` | keyword |
| 4 | 获取指定关键词的用户搜索结果(废弃，替代接口请参考下方文档)/Get user  | GET | `/api/v1/douyin/web/fetch_user_search_result` | keyword |
| 5 | 获取指定关键词的用户搜索结果 V2 (已弃用，替代接口请参考下方文档)/Get  | GET | `/api/v1/douyin/web/fetch_user_search_result_v2` | keyword |
| 6 | 获取指定关键词的用户搜索结果 V3 (已弃用，替代接口请参考下方文档)/Get  | GET | `/api/v1/douyin/web/fetch_user_search_result_v3` | keyword |
| 7 | [已弃用/Deprecated] 获取指定关键词的直播搜索结果/Get live | GET | `/api/v1/douyin/web/fetch_live_search_result` | keyword |
| 8 | [已弃用/Deprecated] 搜索话题/Search Challenge | POST | `/api/v1/douyin/web/fetch_search_challenge` | - |
| 9 | 获取抖音热榜数据/Get Douyin hot search results | GET | `/api/v1/douyin/web/fetch_hot_search_result` | - |
| 10 | 查询抖音用户基本信息/Query Douyin user basic infor | POST | `/api/v1/douyin/web/fetch_query_user` | - |
| 11 | 获取指定关键词的综合搜索结果（弃用，替代接口见下方文档说明）/Get compr | GET | `/api/v1/douyin/app/v3/fetch_general_search_result` | keyword |
| 12 | 获取指定关键词的视频搜索结果（弃用，替代接口见下方文档说明）/Get video | GET | `/api/v1/douyin/app/v3/fetch_video_search_result` | keyword |
| 13 | 获取指定关键词的视频搜索结果 V2 （弃用，替代接口见下方文档说明）/Get v | GET | `/api/v1/douyin/app/v3/fetch_video_search_result_v2` | keyword |
| 14 | 获取指定关键词的用户搜索结果（弃用，替代接口见下方文档说明）/Get user  | GET | `/api/v1/douyin/app/v3/fetch_user_search_result` | keyword |
| 15 | 获取指定关键词的直播搜索结果（弃用，替代接口见下方文档说明）/Get live  | GET | `/api/v1/douyin/app/v3/fetch_live_search_result` | keyword |
| 16 | 获取指定关键词的音乐搜索结果（弃用，替代接口见下方文档说明）/Get music | GET | `/api/v1/douyin/app/v3/fetch_music_search_result` | keyword |
| 17 | 获取指定关键词的话题搜索结果（弃用，替代接口见下方文档说明）/Get hasht | GET | `/api/v1/douyin/app/v3/fetch_hashtag_search_result` | keyword |
| 18 | 获取抖音热搜榜数据/Get Douyin hot search list dat | GET | `/api/v1/douyin/app/v3/fetch_hot_search_list` | - |
| 19 | 获取抖音直播热搜榜数据/Get Douyin live hot search l | GET | `/api/v1/douyin/app/v3/fetch_live_hot_search_list` | - |
| 20 | 获取抖音音乐榜数据/Get Douyin music hot search li | GET | `/api/v1/douyin/app/v3/fetch_music_hot_search_list` | - |
| 21 | 获取抖音品牌热榜分类数据/Get Douyin brand hot search | GET | `/api/v1/douyin/app/v3/fetch_brand_hot_search_list` | - |
| 22 | 获取抖音品牌热榜具体分类数据/Get Douyin brand hot sear | GET | `/api/v1/douyin/app/v3/fetch_brand_hot_search_list_detail` | category_id |
| 23 | 生成抖音分享链接，唤起抖音APP，跳转指定关键词搜索结果/Generate Do | GET | `/api/v1/douyin/app/v3/open_douyin_app_to_keyword_search` | keyword |
| 24 | 搜索用户/Search users | GET | `/api/v1/douyin/creator/fetch_user_search` | user_name |
| 25 | 获取作品搜索关键词统计/Fetch item search keywords s | POST | `/api/v1/douyin/creator_v2/fetch_item_search_keyword` | - |
| 26 | 达人搜索建议/Daren search suggest | POST | `/api/v1/douyin/index/fetch_daren_sug_great_user_list` | keyword |
| 27 | 获取视频搜索筛选选项/Get video search filter optio | GET | `/api/v1/douyin/index/fetch_item_filter_options` | - |
| 28 | 视频搜索建议/Video search suggest | POST | `/api/v1/douyin/index/fetch_item_sug` | query |
| 29 | 视频搜索结果/Video search results | POST | `/api/v1/douyin/index/fetch_item_query` | query |
| 30 | 品牌搜索建议/Brand search suggest | POST | `/api/v1/douyin/index/fetch_brand_suggest` | keyword |
| 31 | 话题搜索建议/Topic search suggest | POST | `/api/v1/douyin/index/fetch_topic_suggest` | keyword |
| 32 | 话题搜索结果/Topic search results | POST | `/api/v1/douyin/index/fetch_topic_query` | keyword, start_date, end_date |
| 33 | 搜索趋势报告/Search trend reports | POST | `/api/v1/douyin/index/fetch_report_search` | - |
| 34 | 获取综合搜索 V1/Fetch general search V1 | POST | `/api/v1/douyin/search/fetch_general_search_v1` | - |
| 35 | 获取综合搜索 V2/Fetch general search V2 | POST | `/api/v1/douyin/search/fetch_general_search_v2` | - |
| 36 | 获取搜索关键词推荐/Fetch search keyword suggestio | POST | `/api/v1/douyin/search/fetch_search_suggest` | - |
| 37 | 获取视频搜索 V1/Fetch video search V1 | POST | `/api/v1/douyin/search/fetch_video_search_v1` | - |
| 38 | 获取视频搜索 V2/Fetch video search V2 | POST | `/api/v1/douyin/search/fetch_video_search_v2` | - |
| 39 | 获取多重搜索/Fetch multi-type search | POST | `/api/v1/douyin/search/fetch_multi_search` | - |
| 40 | 获取用户搜索/Fetch user search | POST | `/api/v1/douyin/search/fetch_user_search` | - |
| 41 | 获取用户搜索 V2/Fetch user search V2 | POST | `/api/v1/douyin/search/fetch_user_search_v2` | - |
| 42 | 获取图片搜索/Fetch image search | POST | `/api/v1/douyin/search/fetch_image_search` | - |
| 43 | 获取图文搜索 V3/Fetch image-text search V3 | POST | `/api/v1/douyin/search/fetch_image_search_v3` | - |
| 44 | 获取直播搜索 V1/Fetch live search V1 | POST | `/api/v1/douyin/search/fetch_live_search_v1` | - |
| 45 | 获取话题搜索 V1/Fetch hashtag search V1 | POST | `/api/v1/douyin/search/fetch_challenge_search_v1` | - |
| 46 | 获取话题搜索 V2/Fetch hashtag search V2 | POST | `/api/v1/douyin/search/fetch_challenge_search_v2` | - |
| 47 | 获取话题推荐搜索/Fetch hashtag suggestions | POST | `/api/v1/douyin/search/fetch_challenge_suggest` | - |
| 48 | 获取经验搜索/Fetch experience search | POST | `/api/v1/douyin/search/fetch_experience_search` | - |
| 49 | 获取音乐搜索/Fetch music search | POST | `/api/v1/douyin/search/fetch_music_search` | - |
| 50 | 获取讨论搜索/Fetch discussion search | POST | `/api/v1/douyin/search/fetch_discuss_search` | - |
| 51 | 获取学校搜索/Fetch school search | POST | `/api/v1/douyin/search/fetch_school_search` | - |
| 52 | 获取图像识别搜索/Fetch vision search (image-base | POST | `/api/v1/douyin/search/fetch_vision_search` | - |
| 53 | 搜索用户名或抖音号/Fetch account search list | GET | `/api/v1/douyin/billboard/fetch_hot_account_search_list` | keyword, cursor |
| 54 | 获取粉丝近3天搜索词 10个搜索词/Fetch fan interest sea | GET | `/api/v1/douyin/billboard/fetch_hot_account_fans_interest_search_list` | sec_uid |
| 55 | 获取搜索热榜/Fetch search hot list | POST | `/api/v1/douyin/billboard/fetch_hot_total_search_list` | - |
| 56 | 获取热度飙升的搜索榜/Fetch search list with rising | POST | `/api/v1/douyin/billboard/fetch_hot_total_high_search_list` | - |
| 57 | 关键词搜索kol V1/Search Kol V1 | GET | `/api/v1/douyin/xingtu/search_kol_v1` | keyword, platformSource, page |
| 58 | 高级搜索kol V2/Search Kol Advanced V2 | GET | `/api/v1/douyin/xingtu/search_kol_v2` | keyword |
| 59 | 搜索MCN机构列表/Get Demander MCN List | GET | `/api/v1/douyin/xingtu_v2/get_demander_mcn_list` | - |

## 工具服务（12个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 8 | 生成抖音短链接/Generate Douyin short link | GET | `/api/v1/douyin/app/v3/generate_douyin_short_url` | url |
| 9 | 生成抖音视频分享二维码/Generate Douyin video share  | GET | `/api/v1/douyin/app/v3/generate_douyin_video_share_qrcode` | object_id |
| 10 | 生成抖音分享链接，唤起抖音APP，跳转指定作品详情页/Generate Douy | GET | `/api/v1/douyin/app/v3/open_douyin_app_to_video_detail` | aweme_id |
| 11 | 生成抖音分享链接，唤起抖音APP，跳转指定用户主页/Generate Douyi | GET | `/api/v1/douyin/app/v3/open_douyin_app_to_user_profile` | uid, sec_uid |
| 12 | 生成抖音分享链接，唤起抖音APP，给指定用户发送私信/Generate Douy | GET | `/api/v1/douyin/app/v3/open_douyin_app_to_send_private_message` | uid, sec_uid |

## 内容解析（7个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 提取单个用户id/Extract single user id | GET | `/api/v1/douyin/web/get_sec_user_id` | url |
| 2 | 提取列表用户id/Extract list user id | POST | `/api/v1/douyin/web/get_all_sec_user_id` | - |
| 3 | 提取单个作品id/Extract single video id | GET | `/api/v1/douyin/web/get_aweme_id` | url |
| 4 | 提取列表作品id/Extract list video id | POST | `/api/v1/douyin/web/get_all_aweme_id` | - |
| 5 | 提取直播间号/Extract webcast id | GET | `/api/v1/douyin/web/get_webcast_id` | url |
| 6 | 提取列表直播间号/Extract list webcast id | POST | `/api/v1/douyin/web/get_all_webcast_id` | - |
| 7 | 提取直播间弹幕/Extract live room danmaku | GET | `/api/v1/douyin/web/douyin_live_room` | live_room_url, danmaku_type |

## 创作者/达人（46个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取创作者活动列表/Get creator activity list | GET | `/api/v1/douyin/creator/fetch_creator_activity_list` | start_time, end_time |
| 2 | 获取创作者活动详情/Get creator activity detail | GET | `/api/v1/douyin/creator/fetch_creator_activity_detail` | activity_id |
| 3 | 获取创作者中心配置/Get creator material center co | GET | `/api/v1/douyin/creator/fetch_creator_material_center_config` | - |
| 4 | 获取创作者热门课程/Get creator hot course | GET | `/api/v1/douyin/creator/fetch_creator_hot_course` | - |
| 5 | 获取创作者内容创作合集分类/Get creator content creati | GET | `/api/v1/douyin/creator/fetch_creator_content_category` | - |
| 6 | 获取创作者内容创作课程/Get creator content creation | GET | `/api/v1/douyin/creator/fetch_creator_content_course` | category_id |
| 7 | 获取作品弹幕列表/Get video danmaku list | GET | `/api/v1/douyin/creator/fetch_video_danmaku_list` | item_id |
| 8 | 获取商单任务列表/Get mission task list | GET | `/api/v1/douyin/creator/fetch_mission_task_list` | - |
| 9 | 获取行业分类配置/Get industry category config | GET | `/api/v1/douyin/creator/fetch_industry_category_config` | - |
| 10 | 获取作品总览数据/Fetch item overview data | POST | `/api/v1/douyin/creator_v2/fetch_item_overview_data` | - |
| 11 | 获取作品垂类标签/Fetch item analysis involved ve | POST | `/api/v1/douyin/creator_v2/fetch_item_analysis_involved_vertical` | - |
| 12 | 获取投稿表现数据/Fetch item analysis item perfor | POST | `/api/v1/douyin/creator_v2/fetch_item_analysis_item_performance` | - |
| 13 | 获取投稿作品列表/Fetch item list | POST | `/api/v1/douyin/creator_v2/fetch_item_list` | - |
| 14 | 导出投稿作品列表/Download item list | POST | `/api/v1/douyin/creator_v2/fetch_item_list_download` | - |
| 15 | 获取直播场次历史记录/Fetch live room history list | POST | `/api/v1/douyin/creator_v2/fetch_live_room_history_list` | - |
| 16 | 获取创作者账号诊断/Fetch author diagnosis | POST | `/api/v1/douyin/creator_v2/fetch_author_diagnosis` | - |
| 17 | 获取加密图片解析/Get Sign Image | GET | `/api/v1/douyin/xingtu/get_sign_image` | uri |
| 18 | 根据抖音用户ID获取游客星图kolid/Get XingTu kolid by  | GET | `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid` | uid |
| 19 | 根据抖音sec_user_id获取游客星图kolid/Get XingTu ko | GET | `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id` | sec_user_id |
| 20 | 根据抖音号获取游客星图kolid/Get XingTu kolid by Dou | GET | `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id` | unique_id |
| 21 | 获取kol基本信息V1/Get kol Base Info V1 | GET | `/api/v1/douyin/xingtu/kol_base_info_v1` | kolId, platformChannel |
| 22 | 获取kol观众画像V1/Get kol Audience Portrait V1 | GET | `/api/v1/douyin/xingtu/kol_audience_portrait_v1` | kolId |
| 23 | 获取kol粉丝画像V1/Get kol Fans Portrait V1 | GET | `/api/v1/douyin/xingtu/kol_fans_portrait_v1` | kolId |
| 24 | 获取kol服务报价V1/Get kol Service Price V1 | GET | `/api/v1/douyin/xingtu/kol_service_price_v1` | kolId, platformChannel |
| 25 | 获取kol数据概览V1/Get kol Data Overview V1 | GET | `/api/v1/douyin/xingtu/kol_data_overview_v1` | kolId, _type, _range, flowType |
| 26 | 获取kol视频表现V1/Get kol Video Performance V1 | GET | `/api/v1/douyin/xingtu/kol_video_performance_v1` | kolId, onlyAssign |
| 27 | 获取kol转化视频展示V1/Get kol Convert Video Disp | GET | `/api/v1/douyin/xingtu/kol_convert_video_display_v1` | kolId, detailType, page |
| 28 | 获取kol连接用户V1/Get kol Link Struct V1 | GET | `/api/v1/douyin/xingtu/kol_link_struct_v1` | kolId |
| 29 | 获取kol连接用户来源V1/Get kol Touch Distribution | GET | `/api/v1/douyin/xingtu/kol_touch_distribution_v1` | kolId |
| 30 | 获取kol内容表现V1/Get kol Rec Videos V1 | GET | `/api/v1/douyin/xingtu/kol_rec_videos_v1` | kolId |
| 31 | 获取kol粉丝趋势V1/Get kol Daily Fans V1 | GET | `/api/v1/douyin/xingtu/kol_daily_fans_v1` | kolId, startDate, endDate |
| 32 | 获取达人广场筛选字段/Get Author Market Fields | GET | `/api/v1/douyin/xingtu_v2/get_author_market_fields` | - |
| 33 | 获取创作者基本信息/Get Author Base Info | GET | `/api/v1/douyin/xingtu_v2/get_author_base_info` | o_author_id |
| 34 | 获取创作者商业卡片信息/Get Author Business Card Inf | GET | `/api/v1/douyin/xingtu_v2/get_author_business_card_info` | o_author_id |
| 35 | 获取创作者位置信息/Get Author Local Info | GET | `/api/v1/douyin/xingtu_v2/get_author_local_info` | o_author_id |
| 36 | 获取创作者视频列表/Get Author Show Items | GET | `/api/v1/douyin/xingtu_v2/get_author_show_items` | o_author_id |
| 37 | 获取创作者评论热词/Get Author Hot Comment Tokens | GET | `/api/v1/douyin/xingtu_v2/get_author_hot_comment_tokens` | author_id |
| 38 | 获取创作者内容热词/Get Author Content Hot Keyword | GET | `/api/v1/douyin/xingtu_v2/get_author_content_hot_keywords` | author_id |
| 39 | 获取相似创作者推荐/Get Recommend Similar Star Aut | POST | `/api/v1/douyin/xingtu_v2/get_recommend_for_star_authors` | - |
| 40 | 获取优秀行业分类列表/Get Excellent Case Category L | GET | `/api/v1/douyin/xingtu_v2/get_excellent_case_category_list` | - |
| 41 | 获取创作者传播价值/Get Author Spread Info | GET | `/api/v1/douyin/xingtu_v2/get_author_spread_info` | o_author_id |
| 42 | 获取用户主页二维码/Get User Profile QRCode | GET | `/api/v1/douyin/xingtu_v2/get_user_profile_qrcode` | - |
| 43 | 获取星图IP日历行业列表/Get IP Activity Industry Li | GET | `/api/v1/douyin/xingtu_v2/get_ip_activity_industry_list` | - |
| 44 | 获取星图IP日历活动列表/Get IP Activity List | POST | `/api/v1/douyin/xingtu_v2/get_ip_activity_list` | - |
| 45 | 获取星图IP活动详情/Get IP Activity Detail | GET | `/api/v1/douyin/xingtu_v2/get_ip_activity_detail` | id |
| 46 | 获取营销活动案例/Get Resource List | GET | `/api/v1/douyin/xingtu_v2/get_resource_list` | resource_id |

