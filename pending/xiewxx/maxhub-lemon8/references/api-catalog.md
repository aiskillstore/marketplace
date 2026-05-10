# Lemon8（Lemon8）API完整目录

> 共 16 个API，按能力域分类

## 数据采集（11个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取指定用户的信息/Get information of specified u | GET | `/api/v1/lemon8/app/fetch_user_profile` | user_id |
| 2 | 获取指定作品的信息/Get information of specified p | GET | `/api/v1/lemon8/app/fetch_post_detail` | item_id |
| 3 | 获取发现页Banner/Get banners of discover page | GET | `/api/v1/lemon8/app/fetch_discover_banners` | - |
| 4 | 获取发现页主体内容/Get main content of discover p | GET | `/api/v1/lemon8/app/fetch_discover_tab` | - |
| 5 | 获取发现页的 Editor's Picks/Get Editor's Picks | GET | `/api/v1/lemon8/app/fetch_discover_tab_information_tabs` | - |
| 6 | 获取话题信息/Get topic information | GET | `/api/v1/lemon8/app/fetch_topic_info` | forum_id |
| 7 | 获取话题作品列表/Get topic post list | GET | `/api/v1/lemon8/app/fetch_topic_post_list` | category, category_parameter, hashtag_name |
| 8 | 通过分享链接获取作品ID/Get post ID through sharing | GET | `/api/v1/lemon8/app/get_item_id` | share_text |
| 9 | 通过分享链接获取用户ID/Get user ID through sharing | GET | `/api/v1/lemon8/app/get_user_id` | share_text |
| 10 | 通过分享链接批量获取作品ID/Get post IDs in batch thr | POST | `/api/v1/lemon8/app/get_item_ids` | - |
| 11 | 通过分享链接批量获取用户ID/Get user IDs in batch thr | POST | `/api/v1/lemon8/app/get_user_ids` | - |

## 互动操作（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取指定用户的粉丝列表/Get fans list of specified u | GET | `/api/v1/lemon8/app/fetch_user_follower_list` | user_id |
| 2 | 获取指定用户的关注列表/Get following list of specif | GET | `/api/v1/lemon8/app/fetch_user_following_list` | user_id |
| 3 | 获取指定作品的评论列表/Get comments list of specifi | GET | `/api/v1/lemon8/app/fetch_post_comment_list` | group_id, item_id, media_id |

## 搜索查询（2个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取热搜关键词/Get hot search keywords | GET | `/api/v1/lemon8/app/fetch_hot_search_keywords` | - |
| 2 | 搜索接口/Search API | GET | `/api/v1/lemon8/app/fetch_search` | query |
