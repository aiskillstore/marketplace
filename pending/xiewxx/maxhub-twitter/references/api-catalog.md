# Twitter（Twitter）API完整目录

> 共 13 个API，按能力域分类

## 数据采集（7个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个推文数据/Get single tweet data | GET | `/api/v1/twitter/web/fetch_tweet_detail` | tweet_id |
| 2 | 获取用户资料/Get user profile | GET | `/api/v1/twitter/web/fetch_user_profile` | - |
| 3 | 获取用户发帖/Get user post | GET | `/api/v1/twitter/web/fetch_user_post_tweet` | - |
| 4 | 获取用户推文回复/Get user tweet replies | GET | `/api/v1/twitter/web/fetch_user_tweet_replies` | screen_name |
| 5 | 获取用户高光推文/Get user highlights tweets | GET | `/api/v1/twitter/web/fetch_user_highlights_tweets` | userId |
| 6 | 获取用户媒体/Get user media | GET | `/api/v1/twitter/web/fetch_user_media` | screen_name |
| 7 | 转推用户列表/ReTweet User list | GET | `/api/v1/twitter/web/fetch_retweet_user_list` | tweet_id |

## 搜索查询（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索/Search | GET | `/api/v1/twitter/web/fetch_search_timeline` | keyword |

## 互动操作（4个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取评论/Get comments | GET | `/api/v1/twitter/web/fetch_post_comments` | tweet_id |
| 2 | 获取最新的推文评论/Get the latest tweet comments | GET | `/api/v1/twitter/web/fetch_latest_post_comments` | tweet_id |
| 3 | 用户关注/User Followings | GET | `/api/v1/twitter/web/fetch_user_followings` | screen_name |
| 4 | 用户粉丝/User Followers | GET | `/api/v1/twitter/web/fetch_user_followers` | screen_name |

## 数据分析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 趋势/Trending | GET | `/api/v1/twitter/web/fetch_trending` | - |
