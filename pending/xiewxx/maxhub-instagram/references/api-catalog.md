# Instagram（Instagram）API完整目录

> 共 88 个API，按能力域分类

## 数据采集（62个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | Shortcode转Media ID/Convert shortcode to  | GET | `/api/v1/instagram/v1/shortcode_to_media_id` | shortcode |
| 2 | Media ID转Shortcode/Convert media ID to s | GET | `/api/v1/instagram/v1/media_id_to_shortcode` | media_id |
| 3 | 用户ID转用户信息/Get user info by user ID | GET | `/api/v1/instagram/v1/user_id_to_username` | user_id |
| 4 | 根据用户名获取用户数据/Get user data by username | GET | `/api/v1/instagram/v1/fetch_user_info_by_username` | username |
| 5 | 根据用户名获取用户数据V2/Get user data by username  | GET | `/api/v1/instagram/v1/fetch_user_info_by_username_v2` | username |
| 6 | 根据用户名获取用户数据V3/Get user data by username  | GET | `/api/v1/instagram/v1/fetch_user_info_by_username_v3` | username |
| 7 | 根据用户ID获取用户数据/Get user data by user ID | GET | `/api/v1/instagram/v1/fetch_user_info_by_id` | user_id |
| 8 | 根据用户ID获取用户数据V2/Get user data by user ID  | GET | `/api/v1/instagram/v1/fetch_user_info_by_id_v2` | user_id |
| 9 | 获取用户的About信息/Get user about info | GET | `/api/v1/instagram/v1/fetch_user_about_info` | user_id |
| 10 | 获取用户帖子列表/Get user posts list | GET | `/api/v1/instagram/v1/fetch_user_posts` | user_id |
| 11 | 获取用户帖子列表V2/Get user posts list V2 | GET | `/api/v1/instagram/v1/fetch_user_posts_v2` | user_id |
| 12 | 获取用户Reels列表/Get user Reels list | GET | `/api/v1/instagram/v1/fetch_user_reels` | user_id |
| 13 | 获取用户转发列表/Get user reposts list | GET | `/api/v1/instagram/v1/fetch_user_reposts` | user_id |
| 14 | 获取用户被标记的帖子/Get user tagged posts | GET | `/api/v1/instagram/v1/fetch_user_tagged_posts` | user_id |
| 15 | 获取相关用户推荐/Get related profiles | GET | `/api/v1/instagram/v1/fetch_related_profiles` | user_id |
| 16 | 通过URL获取帖子详情/Get post by URL | GET | `/api/v1/instagram/v1/fetch_post_by_url` | post_url |
| 17 | 通过URL获取帖子详情 V2/Get post by URL V2 | GET | `/api/v1/instagram/v1/fetch_post_by_url_v2` | post_url |
| 18 | 通过ID获取帖子详情/Get post by ID | GET | `/api/v1/instagram/v1/fetch_post_by_id` | post_id |
| 19 | 获取使用特定音乐的帖子/Get posts using specific mus | GET | `/api/v1/instagram/v1/fetch_music_posts` | - |
| 20 | 获取话题标签下的帖子/Get posts by hashtag | GET | `/api/v1/instagram/v1/fetch_hashtag_posts` | hashtag |
| 21 | 获取地点信息/Get location info | GET | `/api/v1/instagram/v1/fetch_location_info` | location_id |
| 22 | 获取地点下的帖子/Get posts by location | GET | `/api/v1/instagram/v1/fetch_location_posts` | location_id |
| 23 | 获取国家城市列表/Get cities by country | GET | `/api/v1/instagram/v1/fetch_cities` | country_code |
| 24 | 获取城市地点列表/Get locations by city | GET | `/api/v1/instagram/v1/fetch_locations` | city_id |
| 25 | 获取探索页面分类/Get explore page sections | GET | `/api/v1/instagram/v1/fetch_explore_sections` | - |
| 26 | 获取分类下的帖子/Get posts by section | GET | `/api/v1/instagram/v1/fetch_section_posts` | section_id |
| 27 | Shortcode转Media ID/Convert shortcode to  | GET | `/api/v1/instagram/v2/shortcode_to_media_id` | shortcode |
| 28 | Media ID转Shortcode/Convert media ID to s | GET | `/api/v1/instagram/v2/media_id_to_shortcode` | media_id |
| 29 | 用户ID转用户信息/Get user info by user ID | GET | `/api/v1/instagram/v2/user_id_to_username` | user_id |
| 30 | 获取用户信息/Get user info | GET | `/api/v1/instagram/v2/fetch_user_info` | - |
| 31 | 获取用户帖子/Get user posts | GET | `/api/v1/instagram/v2/fetch_user_posts` | - |
| 32 | 获取用户Reels/Get user reels | GET | `/api/v1/instagram/v2/fetch_user_reels` | - |
| 33 | 获取用户故事/Get user stories | GET | `/api/v1/instagram/v2/fetch_user_stories` | - |
| 34 | 获取用户精选/Get user highlights | GET | `/api/v1/instagram/v2/fetch_user_highlights` | - |
| 35 | 获取精选故事详情/Get highlight stories | GET | `/api/v1/instagram/v2/fetch_highlight_stories` | highlight_id |
| 36 | 获取用户被标记的帖子/Get user tagged posts | GET | `/api/v1/instagram/v2/fetch_user_tagged_posts` | - |
| 37 | 获取相似用户/Get similar users | GET | `/api/v1/instagram/v2/fetch_similar_users` | - |
| 38 | 获取帖子详情/Get post info | GET | `/api/v1/instagram/v2/fetch_post_info` | code_or_url |
| 39 | 获取音乐帖子/Get music posts | GET | `/api/v1/instagram/v2/fetch_music_posts` | audio_canonical_id |
| 40 | 获取地点帖子/Get location posts | GET | `/api/v1/instagram/v2/fetch_location_posts` | location_id |
| 41 | 获取话题帖子/Get hashtag posts | GET | `/api/v1/instagram/v2/fetch_hashtag_posts` | keyword |
| 42 | 通过用户名获取用户ID/Get user ID by username | GET | `/api/v1/instagram/v3/get_user_id_by_username` | username |
| 43 | 获取用户信息/Get user profile | GET | `/api/v1/instagram/v3/get_user_profile` | - |
| 44 | 获取用户短详情/Get user brief info | GET | `/api/v1/instagram/v3/get_user_brief` | user_id, username |
| 45 | 获取用户帖子列表/Get user posts | GET | `/api/v1/instagram/v3/get_user_posts` | username |
| 46 | 获取用户被标记的帖子/Get user tagged posts | GET | `/api/v1/instagram/v3/get_user_tagged_posts` | - |
| 47 | 获取用户Reels列表/Get user reels | GET | `/api/v1/instagram/v3/get_user_reels` | - |
| 48 | 获取用户精选Highlights列表/Get user highlights | GET | `/api/v1/instagram/v3/get_user_highlights` | - |
| 49 | 获取Highlight精选详情/Get highlight stories | GET | `/api/v1/instagram/v3/get_highlight_stories` | highlight_id |
| 50 | 获取用户账户简介/Get user about info | GET | `/api/v1/instagram/v3/get_user_about` | - |
| 51 | 获取用户曾用用户名/Get user former usernames | GET | `/api/v1/instagram/v3/get_user_former_usernames` | - |
| 52 | 获取用户Stories（快拍）/Get user stories | GET | `/api/v1/instagram/v3/get_user_stories` | - |
| 53 | 获取Reels推荐列表/Get recommended Reels feed | GET | `/api/v1/instagram/v3/get_recommended_reels` | - |
| 54 | 获取帖子详情/Get post info (media_id or URL) | GET | `/api/v1/instagram/v3/get_post_info` | media_id |
| 55 | 获取帖子详情(code)/Get post info by shortcode | GET | `/api/v1/instagram/v3/get_post_info_by_code` | code |
| 56 | 获取帖子oEmbed内嵌信息/Get post oEmbed info | GET | `/api/v1/instagram/v3/get_post_oembed` | url |
| 57 | 获取探索页推荐帖子/Get explore feed | GET | `/api/v1/instagram/v3/get_explore` | - |
| 58 | 获取地点详情/Get location info | GET | `/api/v1/instagram/v3/get_location_info` | location_id |
| 59 | 获取地点相关帖子/Get location posts | GET | `/api/v1/instagram/v3/get_location_posts` | location_id |
| 60 | 获取地点附近内容/Get nearby location content | GET | `/api/v1/instagram/v3/get_location_nearby` | location_id |
| 61 | 短码转媒体ID/Convert shortcode to media ID | GET | `/api/v1/instagram/v3/shortcode_to_media_id` | shortcode |
| 62 | 媒体ID转短码/Convert media ID to shortcode | GET | `/api/v1/instagram/v3/media_id_to_shortcode` | media_id |

## 搜索查询（12个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索用户/话题/地点/Search users/hashtags/places | GET | `/api/v1/instagram/v1/fetch_search` | query |
| 2 | 搜索用户/Search users | GET | `/api/v1/instagram/v2/search_users` | keyword |
| 3 | 综合搜索/General search | GET | `/api/v1/instagram/v2/general_search` | keyword |
| 4 | 搜索Reels/Search reels | GET | `/api/v1/instagram/v2/search_reels` | keyword |
| 5 | 搜索音乐/Search music | GET | `/api/v1/instagram/v2/search_music` | keyword |
| 6 | 搜索话题标签/Search hashtags | GET | `/api/v1/instagram/v2/search_hashtags` | keyword |
| 7 | 搜索地点/Search locations | GET | `/api/v1/instagram/v2/search_locations` | keyword |
| 8 | 根据坐标搜索地点/Search locations by coordinates | GET | `/api/v1/instagram/v2/search_by_coordinates` | latitude, longitude |
| 9 | 搜索用户/Search users | GET | `/api/v1/instagram/v3/search_users` | query |
| 10 | 搜索话题标签/Search hashtags | GET | `/api/v1/instagram/v3/search_hashtags` | query |
| 11 | 搜索地点/Search places | GET | `/api/v1/instagram/v3/search_places` | query |
| 12 | 综合搜索（支持分页）/General search (with paginati | GET | `/api/v1/instagram/v3/general_search` | query |

## 互动操作（13个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取帖子评论列表V2/Get post comments V2 | GET | `/api/v1/instagram/v1/fetch_post_comments_v2` | media_id |
| 2 | 获取评论的子评论列表/Get comment replies | GET | `/api/v1/instagram/v1/fetch_comment_replies` | media_id, comment_id |
| 3 | 获取用户粉丝/Get user followers | GET | `/api/v1/instagram/v2/fetch_user_followers` | - |
| 4 | 获取用户关注/Get user following | GET | `/api/v1/instagram/v2/fetch_user_following` | - |
| 5 | 获取帖子点赞列表/Get post likes | GET | `/api/v1/instagram/v2/fetch_post_likes` | code_or_url |
| 6 | 获取帖子评论/Get post comments | GET | `/api/v1/instagram/v2/fetch_post_comments` | code_or_url |
| 7 | 获取评论回复/Get comment replies | GET | `/api/v1/instagram/v2/fetch_comment_replies` | code_or_url, comment_id |
| 8 | 获取帖子评论/Get post comments | GET | `/api/v1/instagram/v3/get_post_comments` | code |
| 9 | 获取评论的子评论/回复/Get comment replies | GET | `/api/v1/instagram/v3/get_comment_replies` | media_id, comment_id |
| 10 | 翻译评论/帖子文本/Translate comment or caption | GET | `/api/v1/instagram/v3/translate_comment` | comment_id |
| 11 | 批量翻译评论/Bulk translate comments | GET | `/api/v1/instagram/v3/bulk_translate_comments` | comment_ids |
| 12 | 获取用户关注列表/Get user following list | GET | `/api/v1/instagram/v3/get_user_following` | - |
| 13 | 获取用户粉丝列表/Get user followers list | GET | `/api/v1/instagram/v3/get_user_followers` | - |

## 内容解析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 从URL提取短码/Extract shortcode from URL | GET | `/api/v1/instagram/v3/extract_shortcode` | url |

