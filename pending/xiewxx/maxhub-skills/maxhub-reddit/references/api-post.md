# Post Data API / 帖子数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_community_highlights

`GET /api/v1/reddit/app/fetch_community_highlights`

<!-- Full path: /api/v1/reddit/app/fetch_community_highlights -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| subreddit_id | string | ✅ | '版块ID/Subreddit ID (format: t5_xxxxx)' |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP指定社区的精选亮点内容,包括热门帖子和重要公告
 ### 参数:
 - subreddit_id: 版块ID,格式为"t5_"开头,可从fetch_subreddit_info接口获取
 ### 返回:
 - 社区亮点JSON数据,包含:
  - 精选帖子列表
  - 置顶公告
  - 社区重要动态
  - 推荐内容
### 注意:
 - **APP接口的ID格式与Web接口不同，需要添加类型前缀**
 - 版块ID前缀: t5_ (例如: t5_2qh0u)

## fetch_post_comments

`GET /api/v1/reddit/app/fetch_post_comments`

<!-- Full path: /api/v1/reddit/app/fetch_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID |  |
| sort_type | string |  | >- (default: CONFIDENCE) |  |
| after | string |  | 分页参数/Pagination parameter for fetching next page (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取Reddit APP指定帖子下的评论
 ### 参数:
 - post_id: 帖子ID，格式如 "t3_XXXXXX"
 - sort_type: 排序方式，支持CONFIDENCE, NEW, TOP, HOT, CONTROVERSIAL, OLD,
RANDOM
 - after:
分页参数，获取下一页时使用，在commentForest里的最后一个评论节点中可以找到，例如$.data.postInfoById.commentForest.trees[-1].more.cursor
 ### 返回:
 - 指定帖子下的评论JSON数据
 ### 注意:
 - **APP接口的ID格式与Web接口不同，需要添加类型前缀**
 - 帖子ID前缀: t3_ (例如: t3_1ojnvca)

## fetch_post_details

`GET /api/v1/reddit/app/fetch_post_details`

<!-- Full path: /api/v1/reddit/app/fetch_post_details -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID (e.g., t3_1ojnh50) |  |
| include_comment_id | boolean |  | 是否包含特定评论ID/Include specific comment ID (default: false) |  |
| comment_id | string |  | 评论ID/Comment ID (when include_comment_id is True) (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

## 用途:
 - 根据帖子ID获取单个帖子详情
 - 可选择性包含特定评论的上下文
  ## 参数:
 - post_id: 帖子ID，格式如 "t3_XXXXXX"
 - include_comment_id: 是否包含特定评论ID，默认False
 - comment_id: 评论ID（当include_comment_id为True时使用），格式如 "t1_XXXXXX"
  ## 返回:
 - 包含帖子详细信息的数据，包括:
  - 帖子内容、标题、作者
  - 统计数据（点赞数、评论数等）
  - 版块信息
  - 奖励信息
  - 媒体资源
  - 推荐原因等
 ## 注意:
 - **APP接口的ID格式与Web接口不同，需要添加类型前缀**
 - 帖子ID前缀: t3_ (例如: t3_1ojnh50)
 - 评论ID前缀: t1_ (例如: t1_abcd123)
  ---

## fetch_post_details_batch

`GET /api/v1/reddit/app/fetch_post_details_batch`

<!-- Full path: /api/v1/reddit/app/fetch_post_details_batch -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_ids | string | ✅ | >- |  |
| include_comment_id | boolean |  | 是否包含特定评论ID/Include specific comment ID (default: false) |  |
| comment_id | string |  | 评论ID/Comment ID (when include_comment_id is True) (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

## 用途:
 - 根据帖子ID列表批量获取帖子详情
 - 支持最多5条帖子的批量查询
 - 可选择性包含特定评论的上下文
  ## 参数:
 - post_ids: 帖子ID列表，逗号分隔，格式如 "t3_XXXXXX,t3_YYYYYY"，最多支持5条
 - include_comment_id: 是否包含特定评论ID，默认False
 - comment_id: 评论ID（当include_comment_id为True时使用），格式如 "t1_XXXXXX"
  ## 返回:
 - 包含帖子详细信息的数据，包括:
  - 帖子内容、标题、作者
  - 统计数据（点赞数、评论数等）
  - 版块信息
  - 奖励信息
  - 媒体资源
  - 推荐原因等
 ## 注意:
 - 最多支持5条帖子的批量查询
 - 超过5条将返回错误
 - **APP接口的ID格式与Web接口不同，需要添加类型前缀**
 - 帖子ID前缀: t3_ (例如: t3_1ojnh50)
 - 评论ID前缀: t1_ (例如: t1_abcd123)
  ---

## fetch_post_details_batch_large

`GET /api/v1/reddit/app/fetch_post_details_batch_large`

<!-- Full path: /api/v1/reddit/app/fetch_post_details_batch_large -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_ids | string | ✅ | >- |  |
| include_comment_id | boolean |  | 是否包含特定评论ID/Include specific comment ID (default: false) |  |
| comment_id | string |  | 评论ID/Comment ID (when include_comment_id is True) (default: '') |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

## 用途:
 - 根据帖子ID列表大批量获取帖子详情
 - 支持最多30条帖子的批量查询
 - 可选择性包含特定评论的上下文
  ## 参数:
 - post_ids: 帖子ID列表，逗号分隔，格式如 "t3_XXXXXX,t3_YYYYYY,..."，最多支持30条
 - include_comment_id: 是否包含特定评论ID，默认False
 - comment_id: 评论ID（当include_comment_id为True时使用），格式如 "t1_XXXXXX"
  ## 返回:
 - 包含帖子详细信息的数据，包括:
  - 帖子内容、标题、作者
  - 统计数据（点赞数、评论数等）
  - 版块信息
  - 奖励信息
  - 媒体资源
  - 推荐原因等
 ## 注意:
 - 最多支持30条帖子的批量查询
 - 超过30条将返回错误
 - 大批量查询可能需要较长的响应时间
 - **APP接口的ID格式与Web接口不同，需要添加类型前缀**
 - 帖子ID前缀: t3_ (例如: t3_1ojnh50)
 - 评论ID前缀: t1_ (例如: t1_abcd123)
  ---

## fetch_subreddit_post_channels

`GET /api/v1/reddit/app/fetch_subreddit_post_channels`

<!-- Full path: /api/v1/reddit/app/fetch_subreddit_post_channels -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| subreddit_name | string |  | 版块名称/Subreddit name (default: pics) |  |
| sort | string |  | '排序方式/Sort method: HOT, NEW, TOP, CONTROVERSIAL, RISING' (default: HOT) |  |
| range | string |  | '时间范围/Time range: HOUR, DAY, WEEK, MONTH, YEAR, ALL' (default: DAY) |  |
| need_format | boolean |  | 是否需要清洗数据/Whether to clean and format the data (default: false) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取Reddit APP指定版块的帖子频道信息
### 参数:
- subreddit_name: 版块名称(不带r/前缀)
- sort: 排序方式，支持HOT, NEW, TOP, CONTROVERSIAL, RISING
- range: 时间范围，支持HOUR, DAY, WEEK, MONTH, YEAR, ALL
### 返回:
- 指定版块的帖子频道信息JSON数据

---

See SKILL.md for cross-group orchestration patterns.