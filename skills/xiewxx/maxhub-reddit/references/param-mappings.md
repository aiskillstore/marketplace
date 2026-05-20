# Parameter Mappings / 参数映射

Platform: `reddit` | Base URL: `https://www.aconfig.cn`

---

## fetch_comment_replies

- `post_id` (string, required): 帖子ID/Post ID (e.g., t3_1qmup73)
- `cursor` (string, required): >-
- `sort_type` (string, optional): >-
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_community_highlights

- `subreddit_id` (string, required): '版块ID/Subreddit ID (format: t5_xxxxx)'
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_games_feed

- `sort` (string, optional): '排序方式/Sort method: NEW, HOT, TOP, RISING'
- `time` (string, optional): '时间范围/Time range: ALL, HOUR, DAY, WEEK, MONTH, YEAR'
- `after` (string, optional): 分页参数/Pagination parameter
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_home_feed

- `sort` (string, optional): '排序方式/Sort method: HOT, NEW, TOP, BEST, CONTROVERSIAL'
- `filter_posts` (array, optional): 过滤掉指定的帖子ID列表/Filter out specified post IDs
- `after` (string, optional): 分页参数/Pagination parameter for fetching next page
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_news_feed

- `subtopic_ids` (array, optional): 子话题ID列表/Subtopic IDs list
- `after` (string, optional): 分页参数/Pagination parameter
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_popular_feed

- `sort` (string, optional): '排序方式/Sort method: BEST, HOT, NEW, TOP, CONTROVERSIAL, RISING'
- `time` (string, optional): '时间范围/Time range: ALL, HOUR, DAY, WEEK, MONTH, YEAR'
- `filter_posts` (array, optional): 过滤帖子ID列表/Filter post IDs
- `after` (string, optional): 分页参数/Pagination parameter
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_post_comments

- `post_id` (string, required): 帖子ID/Post ID
- `sort_type` (string, optional): >-
- `after` (string, optional): 分页参数/Pagination parameter for fetching next page
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_post_details

- `post_id` (string, required): 帖子ID/Post ID (e.g., t3_1ojnh50)
- `include_comment_id` (boolean, optional): 是否包含特定评论ID/Include specific comment ID
- `comment_id` (string, optional): 评论ID/Comment ID (when include_comment_id is True)
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_post_details_batch

- `post_ids` (string, required): >-
- `include_comment_id` (boolean, optional): 是否包含特定评论ID/Include specific comment ID
- `comment_id` (string, optional): 评论ID/Comment ID (when include_comment_id is True)
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_post_details_batch_large

- `post_ids` (string, required): >-
- `include_comment_id` (boolean, optional): 是否包含特定评论ID/Include specific comment ID
- `comment_id` (string, optional): 评论ID/Comment ID (when include_comment_id is True)
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_subreddit_post_channels

- `subreddit_name` (string, optional): 版块名称/Subreddit name
- `sort` (string, optional): '排序方式/Sort method: HOT, NEW, TOP, CONTROVERSIAL, RISING'
- `range` (string, optional): '时间范围/Time range: HOUR, DAY, WEEK, MONTH, YEAR, ALL'
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_subreddit_style

- `subreddit_name` (string, optional): 版块名称/Subreddit name
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data

## fetch_user_profile

- `username` (string, required): 用户名/Username
- `need_format` (boolean, optional): 是否需要清洗数据/Whether to clean and format the data
