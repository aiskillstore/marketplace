# Parameter Mappings / 参数映射

Platform: `lemon8` | Base URL: `https://www.aconfig.cn`

---

## fetch_post_comment_list

- `group_id` (string, required): 作品的group_id/Post's group_id — e.g. `7361926875709129222`
- `item_id` (string, required): 作品的item_id/Post's item_id — e.g. `7361926875709129222`
- `media_id` (string, required): 作品的media_id/Post's media_id — e.g. `7428056850216862763`
- `offset` (string, optional): 翻页参数/Pagination parameter — e.g. `0`

## fetch_post_detail

- `item_id` (string, required): 作品ID/Post ID — e.g. `7361926875709129222`

## fetch_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `lemon8`
- `max_cursor` (string, optional): 翻页参数/Pagination parameter
- `filter_type` (string, optional): 搜索过滤类型/Search filter type
- `order_by` (string, optional): 搜索排序方式/Search sort type
- `search_tab` (string, optional): 搜索类型/Search type — e.g. `main`

## fetch_topic_info

- `forum_id` (string, required): 话题ID/Topic ID — e.g. `7174447913778593798`

## fetch_topic_post_list

- `category` (string, required): 话题分类 ID/Topic category ID — e.g. `590`
- `max_behot_time` (string, optional): 翻页参数/Pagination parameter
- `category_parameter` (string, required): 分类参数/Category parameter — e.g. `7174447913778593798`
- `hashtag_name` (string, required): Hashtag名称/Hashtag name — e.g. `lemon8christmas`
- `sort_type` (string, optional): 排序方式/Sort type

## fetch_user_follower_list

- `user_id` (string, required): 用户ID/User ID — e.g. `7428056850216862763`
- `cursor` (string, optional): 翻页参数/Pagination parameter

## fetch_user_following_list

- `user_id` (string, required): 用户ID/User ID — e.g. `7428056850216862763`
- `cursor` (string, optional): 翻页参数/Pagination parameter

## fetch_user_profile

- `user_id` (string, required): 用户ID/User ID — e.g. `7217844966059656197`

## get_item_id

- `share_text` (string, required): 分享链接/Share link — e.g. `https://v.lemon8-app.com/al/OghwFTppx`

## get_user_id

- `share_text` (string, required): 分享链接/Share link — e.g. `https://v.lemon8-app.com/al/OgZrsUppx`
