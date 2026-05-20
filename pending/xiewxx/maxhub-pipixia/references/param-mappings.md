# Parameter Mappings / 参数映射

Platform: `pipixia` | Base URL: `https://www.aconfig.cn`

---

## fetch_hashtag_detail

- `hashtag_id` (string, required): 话题id/Hashtag id — e.g. `129559`

## fetch_hashtag_post_list

- `hashtag_id` (string, required): 话题id/Hashtag id — e.g. `129559`
- `cursor` (string, optional): 翻页游标/Page cursor — e.g. `0`
- `feed_count` (string, optional): 翻页数量/Page count — e.g. `0`
- `hashtag_request_type` (string, optional): 话题请求类型/Hashtag request type — e.g. `0`
- `hashtag_sort_type` (string, optional): 话题排序类型/Hashtag sort type — e.g. `3`

## fetch_home_feed

- `cursor` (string, optional): 翻页游标/Page cursor — e.g. `0`

## fetch_home_short_drama_feed

- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_hot_search_board_detail

- `block_type` (integer, required): 榜单类型/Board type — e.g. `12`

- `cell_type` (integer, optional): 作品类型/Video type — e.g. `1`

## fetch_post_comment_list

- `cell_id` (string, required): 作品id/Video id — e.g. `7411193113223371043`
- `cell_type` (integer, optional): 作品类型/Video type — e.g. `1`
- `offset` (string, optional): 翻页游标/Page cursor — e.g. `0`

## fetch_post_detail

- `cell_id` (string, required): 作品id/Video id — e.g. `7411193113223371043`
- `cell_type` (integer, optional): 作品类型/Video type — e.g. `1`

## fetch_post_statistics

- `cell_id` (string, required): 作品id/Video id — e.g. `7411193113223371043`

## fetch_search

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `皮皮虾`
- `offset` (string, optional): 翻页游标/Page cursor — e.g. `0`
- `search_type` (string, optional): 搜索类型/Search type — e.g. `1`

## fetch_short_url

- `original_url` (string, required): 原始链接/Original URL — e.g. `https://h5.pipix.com/item/7385813877985909043`

## fetch_user_follower_list

- `user_id` (string, required): 用户id/User id — e.g. `1310254082831248`
- `cursor` (string, optional): 翻页游标/Page cursor — e.g. `0`

## fetch_user_following_list

- `user_id` (string, required): 用户id/User id — e.g. `1310254082831248`
- `cursor` (string, optional): 翻页游标/Page cursor — e.g. `0`

## fetch_user_info

- `user_id` (string, required): 用户id/User id — e.g. `1020401`

## fetch_user_post_list

- `user_id` (string, required): 用户id/User id — e.g. `1310254082831248`
- `cursor` (string, optional): 翻页游标/Page cursor — e.g. `0`
- `feed_count` (string, optional): 翻页数量/Page count — e.g. `0`
