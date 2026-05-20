# Parameter Mappings / 参数映射

Platform: `twitter` | Base URL: `https://www.aconfig.cn`

---

## fetch_latest_post_comments

- `tweet_id` (string, required): 推文ID/Tweet ID — e.g. `1808168603721650364`
- `cursor` (string, optional): 游标/Cursor

## fetch_post_comments

- `tweet_id` (string, required): 推文ID/Tweet ID — e.g. `1835124037934367098`
- `cursor` (string, optional): 游标/Cursor

## fetch_retweet_user_list

- `tweet_id` (string, required): 推文ID/Tweet ID — e.g. `1835124037934367098`
- `cursor` (string, optional): 游标/Cursor

## fetch_search_timeline

- `keyword` (string, required): 搜索关键字/Search Keyword — e.g. `Elon Musk`
- `search_type` (string, optional): 搜索类型/Search Type — e.g. `Top`
- `cursor` (string, optional): 游标/Cursor

## fetch_trending

- `country` (string, optional): 国家/Country — e.g. `UnitedStates`

## fetch_tweet_detail

- `tweet_id` (string, required): 推文ID/Tweet ID — e.g. `1808168603721650364`

## fetch_user_followers

- `screen_name` (string, required): 用户名/Screen Name — e.g. `elonmusk`
- `cursor` (string, optional): 游标/Cursor

## fetch_user_followings

- `screen_name` (string, required): 用户名/Screen Name — e.g. `elonmusk`
- `cursor` (string, optional): 游标/Cursor

## fetch_user_media

- `screen_name` (string, required): 用户名/Screen Name — e.g. `elonmusk`
- `rest_id` (integer, optional): 用户ID/User ID — e.g. `44196397`
- `cursor` (string, optional): 翻页游标/Page Cursor

## fetch_user_post_tweet

- `screen_name` (string, optional): 用户名/Screen Name — e.g. `elonmusk`
- `rest_id` (integer, optional): 用户ID/User ID — e.g. `44196397`
- `cursor` (string, optional): 游标/Cursor

## fetch_user_profile

- `screen_name` (string, optional): 用户名/Screen Name — e.g. `elonmusk`
- `rest_id` (integer, optional): >- — e.g. `44196397`

## fetch_user_tweet_replies

- `screen_name` (string, required): 用户名/Screen Name — e.g. `elonmusk`
- `cursor` (string, optional): 游标/Cursor
