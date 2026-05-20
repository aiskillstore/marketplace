# Subreddit API / 版块接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_games_feed

`GET /api/v1/reddit/app/fetch_games_feed`

<!-- Full path: /api/v1/reddit/app/fetch_games_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sort | string |  | '排序方式/Sort method: NEW, HOT, TOP, RISING' (default: NEW) |  |
| time | string |  | '时间范围/Time range: ALL, HOUR, DAY, WEEK, MONTH, YEAR' (default: ALL) |  |
| after | string |  | 分页参数/Pagination parameter (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP游戏相关的推荐内容,展示游戏社区的热门帖子
 ### 参数:
 - sort: 排序方式,可选: NEW(最新), HOT(热门), TOP(顶级), RISING(上升中)
 - time: 时间范围,可选: ALL(全部时间), HOUR(一小时), DAY(一天), WEEK(一周), MONTH(一个月),
YEAR(一年)
 - after: 分页参数,获取下一页时使用
 ### 返回:
 - 游戏推荐内容JSON数据,包含:
  - 游戏相关帖子列表
  - 游戏社区讨论
  - 游戏新闻和更新

## fetch_home_feed

`GET /api/v1/reddit/app/fetch_home_feed`

<!-- Full path: /api/v1/reddit/app/fetch_home_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sort | string |  | '排序方式/Sort method: HOT, NEW, TOP, BEST, CONTROVERSIAL' (default: BEST) |  |
| filter_posts | array |  | 过滤掉指定的帖子ID列表/Filter out specified post IDs (default: []) |  |
| after | string |  | 分页参数/Pagination parameter for fetching next page (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP首页推荐内容
 ### 参数:
 - sort: 排序方式，支持HOT, NEW, TOP, BEST, CONTROVERSIAL
 - filter_posts: 过滤掉指定的帖子ID列表，用于排除已获取的帖子，避免重复获取
 - after: 分页参数，获取下一页时使用
 ### 返回:
 - Reddit APP首页推荐内容的JSON数据

## fetch_news_feed

`GET /api/v1/reddit/app/fetch_news_feed`

<!-- Full path: /api/v1/reddit/app/fetch_news_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| subtopic_ids | array |  | 子话题ID列表/Subtopic IDs list |  |
| after | string |  | 分页参数/Pagination parameter (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP新闻资讯推荐内容,展示最新的新闻和时事讨论
 ### 参数:
 - subtopic_ids: 子话题ID列表,默认["all"]表示所有新闻类别
 - after: 分页参数,获取下一页时使用
 ### 返回:
 - 新闻推荐内容JSON数据,包含:
  - 新闻帖子列表
  - 时事讨论
  - 热点话题
  - 新闻来源和链接

## fetch_popular_feed

`GET /api/v1/reddit/app/fetch_popular_feed`

<!-- Full path: /api/v1/reddit/app/fetch_popular_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| sort | string |  | '排序方式/Sort method: BEST, HOT, NEW, TOP, CONTROVERSIAL, RISING' (default: BEST) |  |
| time | string |  | '时间范围/Time range: ALL, HOUR, DAY, WEEK, MONTH, YEAR' (default: ALL) |  |
| filter_posts | array |  | 过滤帖子ID列表/Filter post IDs (default: []) |  |
| after | string |  | 分页参数/Pagination parameter (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP流行/热门推荐内容,展示全站最受欢迎的帖子
 ### 参数:
 - sort: 排序方式,可选: BEST(最佳), HOT(热门), NEW(最新), TOP(顶级),
CONTROVERSIAL(有争议), RISING(上升中)
 - time: 时间范围,可选: ALL(全部时间), HOUR(一小时), DAY(一天), WEEK(一周), MONTH(一个月),
YEAR(一年)
 - filter_posts: 过滤掉指定的帖子ID列表,用于避免重复获取
 - after: 分页参数,获取下一页时使用
 ### 返回:
 - 流行推荐内容JSON数据,包含:
  - 热门帖子列表
  - 帖子详细信息(标题、内容、点赞数、评论数等)
  - 分页信息(after参数用于下一页)

## fetch_subreddit_style

`GET /api/v1/reddit/app/fetch_subreddit_style`

<!-- Full path: /api/v1/reddit/app/fetch_subreddit_style -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| subreddit_name | string |  | 版块名称/Subreddit name (default: pics) |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Reddit APP指定版块的规则和样式信息
### 参数:
- subreddit_name: 版块名称(不带r/前缀)
### 返回:
- 指定版块的规则和样式信息JSON数据

---

See SKILL.md for cross-group orchestration patterns.