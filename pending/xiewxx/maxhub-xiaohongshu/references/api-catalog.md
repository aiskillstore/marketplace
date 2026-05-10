# 小红书（Xiaohongshu）API完整目录

> 共 78 个API，按能力域分类

## 数据采集（41个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取笔记详情/Fetch note detail | GET | `/api/v1/xiaohongshu/web_v3/fetch_note_detail` | note_id, xsec_token |
| 2 | 获取首页推荐/Fetch homepage feed | GET | `/api/v1/xiaohongshu/web_v3/fetch_homefeed` | - |
| 3 | 获取首页分类列表/Fetch homepage categories | GET | `/api/v1/xiaohongshu/web_v3/fetch_homefeed_categories` | - |
| 4 | 获取用户信息/Fetch user info | GET | `/api/v1/xiaohongshu/web_v3/fetch_user_info` | user_id |
| 5 | 获取用户笔记列表/Fetch user notes | GET | `/api/v1/xiaohongshu/web_v3/fetch_user_notes` | user_id |
| 6 | 获取图文笔记详情/Get image note detail | GET | `/api/v1/xiaohongshu/app_v2/get_image_note_detail` | - |
| 7 | 获取视频笔记详情/Get video note detail | GET | `/api/v1/xiaohongshu/app_v2/get_video_note_detail` | - |
| 8 | 获取用户信息/Get user info | GET | `/api/v1/xiaohongshu/app_v2/get_user_info` | - |
| 9 | 获取用户笔记列表/Get user posted notes | GET | `/api/v1/xiaohongshu/app_v2/get_user_posted_notes` | - |
| 10 | 获取商品详情/Get product detail | GET | `/api/v1/xiaohongshu/app_v2/get_product_detail` | sku_id |
| 11 | 获取商品推荐列表/Get product recommendations | GET | `/api/v1/xiaohongshu/app_v2/get_product_recommendations` | sku_id |
| 12 | 获取话题详情/Get topic info | GET | `/api/v1/xiaohongshu/app_v2/get_topic_info` | page_id |
| 13 | 获取话题笔记列表/Get topic feed | GET | `/api/v1/xiaohongshu/app_v2/get_topic_feed` | page_id |
| 14 | 获取笔记信息 V1/Get note info V1 | GET | `/api/v1/xiaohongshu/app/get_note_info` | - |
| 15 | 获取笔记信息 V2 (蒲公英商家后台)/Get note info V2 (Pu | GET | `/api/v1/xiaohongshu/app/get_note_info_v2` | - |
| 16 | [已弃用/Deprecated] 根据话题标签获取作品/Get notes by | GET | `/api/v1/xiaohongshu/app/get_notes_by_topic` | page_id, first_load_time |
| 17 | 获取用户信息/Get user info | GET | `/api/v1/xiaohongshu/app/get_user_info` | user_id |
| 18 | 获取用户作品列表/Get user notes | GET | `/api/v1/xiaohongshu/app/get_user_notes` | user_id |
| 19 | 获取商品详情/Get product detail | GET | `/api/v1/xiaohongshu/app/get_product_detail` | sku_id |
| 20 | 获取单一笔记和推荐笔记 V1 (已弃用)/Fetch one note and  | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes` | note_id |
| 21 | 获取单一笔记和推荐笔记 V2/Fetch one note and feed n | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v2` | note_id |
| 22 | 获取单一笔记和推荐笔记 V3/Fetch one note and feed n | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v3` | short_url |
| 23 | 获取小红书笔记图片/Fetch Xiaohongshu note image | GET | `/api/v1/xiaohongshu/web_v2/fetch_note_image` | note_id |
| 24 | 获取Web用户主页笔记/Fetch web user profile notes | GET | `/api/v1/xiaohongshu/web_v2/fetch_home_notes` | user_id |
| 25 | 获取App用户主页笔记/Fetch App user home notes | GET | `/api/v1/xiaohongshu/web_v2/fetch_home_notes_app` | user_id |
| 26 | 获取用户信息/Fetch user info | GET | `/api/v1/xiaohongshu/web_v2/fetch_user_info` | user_id |
| 27 | 获取App用户信息/Fetch App user info | GET | `/api/v1/xiaohongshu/web_v2/fetch_user_info_app` | user_id |
| 28 | 获取小红书商品列表/Fetch Xiaohongshu product list | GET | `/api/v1/xiaohongshu/web_v2/fetch_product_list` | user_id |
| 29 | 获取小红书热榜/Fetch Xiaohongshu hot list | GET | `/api/v1/xiaohongshu/web_v2/fetch_hot_list` | - |
| 30 | 获取首页推荐/Get home recommend | POST | `/api/v1/xiaohongshu/web/get_home_recommend` | - |
| 31 | 获取笔记信息 V2/Get note info V2 | GET | `/api/v1/xiaohongshu/web/get_note_info_v2` | - |
| 32 | 获取笔记信息 V4/Get note info V4 | GET | `/api/v1/xiaohongshu/web/get_note_info_v4` | - |
| 34 | 获取笔记信息 V7/Get note info V7 | GET | `/api/v1/xiaohongshu/web/get_note_info_v7` | - |
| 35 | 获取用户信息 V1/Get user info V1 | GET | `/api/v1/xiaohongshu/web/get_user_info` | user_id |
| 36 | 获取用户信息 V2/Get user info V2 | GET | `/api/v1/xiaohongshu/web/get_user_info_v2` | - |
| 37 | 获取用户的笔记 V2/Get user notes V2 | GET | `/api/v1/xiaohongshu/web/get_user_notes_v2` | user_id |
| 40 | 通过分享链接获取小红书的Note ID 和 xsec_token/Get Xia | GET | `/api/v1/xiaohongshu/web/get_note_id_and_xsec_token` | share_text |
| 41 | 获取小红书商品信息/Get Xiaohongshu product info | GET | `/api/v1/xiaohongshu/web/get_product_info` | - |

## 互动操作（17个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取笔记评论/Fetch note comments | GET | `/api/v1/xiaohongshu/web_v3/fetch_note_comments` | note_id, xsec_token |
| 2 | 获取子评论/Fetch sub comments | GET | `/api/v1/xiaohongshu/web_v3/fetch_sub_comments` | note_id, root_comment_id, xsec_token |
| 3 | 获取笔记评论列表/Get note comments | GET | `/api/v1/xiaohongshu/app_v2/get_note_comments` | - |
| 4 | 获取笔记二级评论列表/Get note sub comments | GET | `/api/v1/xiaohongshu/app_v2/get_note_sub_comments` | comment_id |
| 5 | 获取用户收藏笔记列表/Get user faved notes | GET | `/api/v1/xiaohongshu/app_v2/get_user_faved_notes` | - |
| 6 | 获取商品评论总览/Get product review overview | GET | `/api/v1/xiaohongshu/app_v2/get_product_review_overview` | sku_id |
| 7 | 获取商品评论列表/Get product reviews | GET | `/api/v1/xiaohongshu/app_v2/get_product_reviews` | sku_id |
| 8 | 获取笔记评论/Get note comments | GET | `/api/v1/xiaohongshu/app/get_note_comments` | note_id |
| 9 | 获取子评论/Get sub comments | GET | `/api/v1/xiaohongshu/app/get_sub_comments` | note_id, comment_id |
| 10 | 获取单一笔记和推荐笔记 V4 (互动量有延迟)/Fetch one note a | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v4` | note_id |
| 11 | 获取单一笔记和推荐笔记 V5 (互动量有缺失)/Fetch one note a | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v5` | note_id |
| 12 | 获取笔记评论/Fetch note comments | GET | `/api/v1/xiaohongshu/web_v2/fetch_note_comments` | note_id |
| 13 | 获取子评论/Fetch sub comments | GET | `/api/v1/xiaohongshu/web_v2/fetch_sub_comments` | note_id, comment_id |
| 14 | 获取用户粉丝列表/Fetch follower list | GET | `/api/v1/xiaohongshu/web_v2/fetch_follower_list` | user_id |
| 15 | 获取用户关注列表/Fetch following list | GET | `/api/v1/xiaohongshu/web_v2/fetch_following_list` | user_id |
| 16 | 获取笔记评论 V1/Get note comments V1 | GET | `/api/v1/xiaohongshu/web/get_note_comments` | note_id |
| 17 | 获取笔记评论回复 V1/Get note comment replies V1 | GET | `/api/v1/xiaohongshu/web/get_note_comment_replies` | note_id, comment_id |

## 搜索查询（15个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索笔记/Search notes | GET | `/api/v1/xiaohongshu/web_v3/fetch_search_notes` | keyword |
| 2 | 搜索用户/Search users | GET | `/api/v1/xiaohongshu/web_v3/fetch_search_users` | keyword |
| 3 | 获取搜索联想词/Fetch search suggestions | GET | `/api/v1/xiaohongshu/web_v3/fetch_search_suggest` | - |
| 4 | 搜索笔记/Search notes | GET | `/api/v1/xiaohongshu/app_v2/search_notes` | keyword |
| 5 | 搜索用户/Search users | GET | `/api/v1/xiaohongshu/app_v2/search_users` | keyword |
| 6 | 搜索图片/Search images | GET | `/api/v1/xiaohongshu/app_v2/search_images` | keyword |
| 7 | 搜索商品/Search products | GET | `/api/v1/xiaohongshu/app_v2/search_products` | keyword |
| 8 | 搜索群聊/Search groups | GET | `/api/v1/xiaohongshu/app_v2/search_groups` | keyword |
| 9 | 搜索笔记/Search notes | GET | `/api/v1/xiaohongshu/app/search_notes` | keyword, page |
| 10 | 搜索商品/Search products | GET | `/api/v1/xiaohongshu/app/search_products` | keyword, page |
| 11 | 获取搜索笔记/Fetch search notes | GET | `/api/v1/xiaohongshu/web_v2/fetch_search_notes` | keywords |
| 12 | 获取搜索用户/Fetch search users | GET | `/api/v1/xiaohongshu/web_v2/fetch_search_users` | keywords |
| 13 | 搜索笔记/Search notes | GET | `/api/v1/xiaohongshu/web/search_notes` | keyword |
| 14 | 搜索笔记 V3/Search notes V3 | GET | `/api/v1/xiaohongshu/web/search_notes_v3` | keyword |
| 15 | 搜索用户/Search users | GET | `/api/v1/xiaohongshu/web/search_users` | keyword |

## 数据分析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取热搜词/Fetch trending keywords | GET | `/api/v1/xiaohongshu/web_v3/fetch_trending` | - |

## 创作者/达人（2个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取创作者推荐灵感列表/Get creator inspiration feed | GET | `/api/v1/xiaohongshu/app_v2/get_creator_inspiration_feed` | - |
| 2 | 获取创作者热点灵感列表/Get creator hot inspiration  | GET | `/api/v1/xiaohongshu/app_v2/get_creator_hot_inspiration_feed` | - |

## 内容解析（2个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 提取分享链接信息/Extract share link info | GET | `/api/v1/xiaohongshu/app/extract_share_info` | share_link |
| 2 | 从分享链接中提取用户ID和xsec_token/Extract user ID  | GET | `/api/v1/xiaohongshu/app/get_user_id_and_xsec_token` | share_link |
