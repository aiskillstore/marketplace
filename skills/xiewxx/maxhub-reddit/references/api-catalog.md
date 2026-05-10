# Reddit（Reddit）API完整目录

> 共 24 个API，按能力域分类

## 数据采集（18个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取Reddit APP首页推荐内容/Fetch Reddit APP Home | GET | `/api/v1/reddit/app/fetch_home_feed` | - |
| 2 | 获取Reddit APP流行推荐内容/Fetch Reddit APP Popu | GET | `/api/v1/reddit/app/fetch_popular_feed` | - |
| 3 | 获取Reddit APP游戏推荐内容/Fetch Reddit APP Game | GET | `/api/v1/reddit/app/fetch_games_feed` | - |
| 4 | 获取Reddit APP资讯推荐内容/Fetch Reddit APP News | GET | `/api/v1/reddit/app/fetch_news_feed` | - |
| 5 | 获取单个Reddit帖子详情/Fetch Single Reddit Post  | GET | `/api/v1/reddit/app/fetch_post_details` | post_id |
| 6 | 批量获取Reddit帖子详情(最多5条)/Fetch Reddit Post D | GET | `/api/v1/reddit/app/fetch_post_details_batch` | post_ids |
| 7 | 大批量获取Reddit帖子详情(最多30条)/Fetch Reddit Post | GET | `/api/v1/reddit/app/fetch_post_details_batch_large` | post_ids |
| 8 | 获取Reddit APP版块规则样式信息/Fetch Reddit APP Su | GET | `/api/v1/reddit/app/fetch_subreddit_style` | - |
| 9 | 获取Reddit APP版块帖子频道信息/Fetch Reddit APP Su | GET | `/api/v1/reddit/app/fetch_subreddit_post_channels` | - |
| 10 | 获取Reddit APP版块信息/Fetch Reddit APP Subred | GET | `/api/v1/reddit/app/fetch_subreddit_info` | - |
| 11 | 获取Reddit APP版块设置/Fetch Reddit APP Subred | GET | `/api/v1/reddit/app/fetch_subreddit_settings` | subreddit_id |
| 12 | 获取Reddit APP社区亮点/Fetch Reddit APP Commun | GET | `/api/v1/reddit/app/fetch_community_highlights` | subreddit_id |
| 13 | 获取Reddit APP用户资料信息/Fetch Reddit APP User | GET | `/api/v1/reddit/app/fetch_user_profile` | username |
| 14 | 获取用户活跃的社区列表/Fetch User's Active Subreddi | GET | `/api/v1/reddit/app/fetch_user_active_subreddits` | username |
| 15 | 获取用户发布的帖子列表/Fetch User Posts | GET | `/api/v1/reddit/app/fetch_user_posts` | username |
| 16 | 获取Reddit APP版块Feed内容/Fetch Reddit APP Su | GET | `/api/v1/reddit/app/fetch_subreddit_feed` | subreddit_name |
| 17 | 检查版块是否静音/Check if Subreddit is Muted | GET | `/api/v1/reddit/app/check_subreddit_muted` | subreddit_id |
| 18 | 获取用户公开奖杯/Fetch User Public Trophies | GET | `/api/v1/reddit/app/fetch_user_trophies` | username |

## 互动操作（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取Reddit APP帖子评论/Fetch Reddit APP Post C | GET | `/api/v1/reddit/app/fetch_post_comments` | post_id |
| 2 | 获取Reddit APP评论回复（二级评论）/Fetch Reddit APP  | GET | `/api/v1/reddit/app/fetch_comment_replies` | post_id, cursor |
| 3 | 获取用户评论列表/Fetch User Comments | GET | `/api/v1/reddit/app/fetch_user_comments` | username |

## 搜索查询（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取Reddit APP搜索自动补全建议/Fetch Reddit APP Se | GET | `/api/v1/reddit/app/fetch_search_typeahead` | query |
| 2 | 获取Reddit APP动态搜索结果/Fetch Reddit APP Dyna | GET | `/api/v1/reddit/app/fetch_dynamic_search` | query |
| 3 | 获取Reddit APP今日热门搜索/Fetch Reddit APP Tren | GET | `/api/v1/reddit/app/fetch_trending_searches` | - |
