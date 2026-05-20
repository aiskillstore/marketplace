# Parameter Mappings / 参数映射

Platform: `instagram` | Base URL: `https://www.aconfig.cn`

---

## fetch_cities

- `country_code` (string, required): 国家代码（如US、CN、JP）/Country code (e.g. US, CN, JP) — e.g. `US`
- `page` (integer, optional): 页码/Page number

## fetch_comment_replies

- `media_id` (string, required): 帖子ID（媒体ID）/Post ID (Media ID) — e.g. `3766120364183949816`
- `comment_id` (string, required): 父评论ID/Parent comment ID — e.g. `17871667485468098`
- `min_id` (string, optional): >-

## fetch_comment_replies

- `code_or_url` (string, required): 帖子Shortcode或URL/Post shortcode or URL — e.g. `DRhvwVLAHAG`
- `comment_id` (string, required): 评论ID/Comment ID — e.g. `18067775592012345`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_hashtag_posts

- `hashtag` (string, required): '话题标签名称（不含#号）/Hashtag name (without #)' — e.g. `cat`
- `end_cursor` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_hashtag_posts

- `keyword` (string, required): '话题关键词（不含#号）/Hashtag keyword (without #)' — e.g. `cat`
- `feed_type` (string, optional): >-
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_highlight_stories

- `highlight_id` (string, required): 精选ID/Highlight ID — e.g. `17895069621772257`

## fetch_location_info

- `location_id` (string, required): 地点ID/Location ID — e.g. `703457703`

## fetch_location_posts

- `location_id` (string, required): 地点ID/Location ID — e.g. `703457703`
- `tab` (string, optional): '排序方式：ranked(热门)/recent(最新)/Sorting: ranked(top)/recent(latest)'
- `end_cursor` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_location_posts

- `location_id` (string, required): 地点ID/Location ID — e.g. `331004901`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_locations

- `city_id` (string, required): 城市ID（从fetch_cities获取）/City ID (from fetch_cities) — e.g. `c2791472`
- `page` (integer, optional): 页码/Page number

## fetch_music_posts

- `music_id` (string, optional): 音乐ID/Music ID — e.g. `564058920086577`
- `music_url` (string, optional): 音乐URL（与music_id二选一）/Music URL (alternative to music_id) — e.g. `https://www.instagram.com/reels/audio/564058920086577`
- `max_id` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_music_posts

- `audio_canonical_id` (string, required): 音频ID/Audio ID — e.g. `564058920086577`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_post_by_id

- `post_id` (string, required): 帖子ID/Post ID — e.g. `3742637871112032100`

## fetch_post_by_url

- `post_url` (string, required): 帖子URL/Post URL — e.g. `https://www.instagram.com/p/DPwhVB-jo9k/`

## fetch_post_by_url_v2

- `post_url` (string, required): 帖子URL/Post URL — e.g. `https://www.instagram.com/p/DPwhVB-jo9k/`

## fetch_post_comments

- `code_or_url` (string, required): 帖子Shortcode或URL/Post shortcode or URL — e.g. `DRhvwVLAHAG`
- `sort_by` (string, optional): '排序方式: recent(最新) 或 popular(热门)/Sort by: recent or popular' — e.g. `recent`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_post_comments_v2

- `media_id` (string, required): 帖子ID（媒体ID）/Post ID (Media ID) — e.g. `3766120364183949816`
- `sort_order` (string, optional): '排序方式：popular(热门)/recent(最新)/Sorting: popular/recent' — e.g. `recent`
- `min_id` (string, optional): >-

## fetch_post_info

- `code_or_url` (string, required): 帖子Shortcode或URL/Post shortcode or URL — e.g. `DRhvwVLAHAG`

## fetch_post_likes

- `code_or_url` (string, required): 帖子Shortcode或URL/Post shortcode or URL — e.g. `DRhvwVLAHAG`
- `end_cursor` (string, optional): 分页游标/Pagination cursor

## fetch_related_profiles

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`

## fetch_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `taylorswift`
- `select` (string, optional): >-

## fetch_section_posts

- `section_id` (string, required): >- — e.g. `10156104410190727`
- `count` (integer, optional): 每页数量/Count per page
- `max_id` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_similar_users

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`

## fetch_user_followers

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_user_following

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_user_highlights

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`

## fetch_user_info

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`

## fetch_user_info_by_id

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`

## fetch_user_posts

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`
- `count` (integer, optional): 每页数量/Count per page
- `max_id` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_user_posts

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_user_posts_v2

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`
- `count` (integer, optional): 每页数量/Count per page
- `end_cursor` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_user_reels

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`
- `count` (integer, optional): 每页数量/Count per page
- `max_id` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_user_reels

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`
- `pagination_token` (string, optional): 分页token/Pagination token

## fetch_user_reposts

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`
- `max_id` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_user_stories

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`

## fetch_user_tagged_posts

- `user_id` (string, required): Instagram用户ID/Instagram user ID — e.g. `25025320`
- `count` (integer, optional): 每页数量/Count per page
- `end_cursor` (string, optional): 分页游标，用于获取下一页/Pagination cursor for next page

## fetch_user_tagged_posts

- `username` (string, optional): 用户名/Username — e.g. `instagram`
- `user_id` (string, optional): 用户ID/User ID — e.g. `18527`
- `pagination_token` (string, optional): 分页token/Pagination token

## general_search

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `cat`
- `pagination_token` (string, optional): 分页token/Pagination token

## general_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `justin`
- `next_max_id` (string, optional): >-
- `rank_token` (string, optional): >-
- `enable_metadata` (boolean, optional): 是否启用元数据/Enable metadata

## get_comment_replies

- `media_id` (string, required): 帖子媒体ID/Post media ID — e.g. `3829530490739515971`
- `comment_id` (string, required): 父评论ID/Parent comment ID — e.g. `18065937092249736`
- `min_id` (string, optional): >-

## get_highlight_stories

- `highlight_id` (string, required): '精选ID/Highlight ID (格式/format: highlight:xxx)' — e.g. `highlight:18064916456320419`
- `reel_ids` (string, optional): >-
- `first` (integer, optional): 每页数量/Items per page
- `last` (integer, optional): 获取最后N条/Get last N items

## get_post_comments

- `code` (string, required): 帖子短代码/Post shortcode (e.g., DUajw4YkorV) — e.g. `DUajw4YkorV`
- `min_id` (string, optional): >-
- `sort_order` (string, optional): >-

## get_post_info

- `media_id` (string, optional): 帖子媒体ID/Post media ID（与 url 二选一） — e.g. `3850699893338385742`
- `url` (string, optional): 帖子URL/Post URL（与 media_id 二选一；支持 /p/、/reel/、/reels/、/tv/ 形式） — e.g. `https://www.instagram.com/p/DUajw4YkorV/`

## get_post_info_by_code

- `code` (string, required): 帖子短代码/Post shortcode — e.g. `DUajw4YkorV`

## get_post_oembed

- `url` (string, required): Instagram帖子的完整URL/Full URL of Instagram post — e.g. `https://www.instagram.com/reel/DUlObENDmJD`
- `hidecaption` (boolean, optional): 是否隐藏帖子文本/Whether to hide caption
- `maxwidth` (integer, optional): 最大宽度（像素）/Max width in pixels

## get_recommended_reels

- `first` (integer, optional): 获取数量/Number of reels to fetch
- `after` (string, optional): >-

## get_user_about

- `user_id` (string, optional): 用户ID/User ID — e.g. `791258468`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`

## get_user_brief

- `user_id` (string, required): 用户ID/User ID — e.g. `791258468`
- `username` (string, required): 用户名/Username — e.g. `99brasil`

## get_user_former_usernames

- `user_id` (string, optional): 用户ID/User ID — e.g. `17841403122371231`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`

## get_user_highlights

- `user_id` (string, optional): 用户ID/User ID — e.g. `58208242181`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`
- `first` (integer, optional): 每页数量/Number of highlights per page
- `after` (string, optional): 向后翻页游标/Forward pagination cursor
- `before` (string, optional): 向前翻页游标/Backward pagination cursor
- `last` (integer, optional): 向前翻页时每页数量/Number of highlights per page (backward)

## get_user_id_by_username

- `username` (string, required): 用户名/Username — e.g. `liensue.talks`

## get_user_posts

- `username` (string, required): Instagram 用户名（不含 @）/Instagram username (without @) — e.g. `99brasil`
- `first` (integer, optional): 向后翻页时每页数量/Number of posts per page (forward)
- `after` (string, optional): 向后翻页游标（end_cursor）/Forward pagination cursor (end_cursor)
- `before` (string, optional): 向前翻页游标（start_cursor）/Backward pagination cursor (start_cursor)
- `last` (integer, optional): 向前翻页时每页数量/Number of posts per page (backward)
- `count` (integer, optional): 首次请求数量/Number of posts for first request

## get_user_profile

- `user_id` (string, optional): 用户ID/User ID — e.g. `58208242181`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`

## get_user_reels

- `user_id` (string, optional): 用户ID/User ID — e.g. `58208242181`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`
- `first` (integer, optional): 向后翻页时每页数量/Number of reels per page (forward)
- `after` (string, optional): 向后翻页游标（end_cursor）/Forward pagination cursor (end_cursor)
- `before` (string, optional): 向前翻页游标（start_cursor）/Backward pagination cursor (start_cursor)
- `last` (integer, optional): 向前翻页时每页数量/Number of reels per page (backward)
- `page_size` (integer, optional): 每页视频数量/Videos per page

## get_user_stories

- `user_id` (string, optional): 用户ID/User ID — e.g. `58208242181`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`

## get_user_tagged_posts

- `user_id` (string, optional): 用户ID/User ID — e.g. `58208242181`
- `username` (string, optional): 用户名（与user_id二选一）/Username (alternative to user_id) — e.g. `instagram`
- `first` (integer, optional): 向后翻页时每页数量/Number of posts per page (forward)
- `after` (string, optional): 向后翻页游标（end_cursor）/Forward pagination cursor (end_cursor)
- `before` (string, optional): 向前翻页游标（start_cursor）/Backward pagination cursor (start_cursor)
- `last` (integer, optional): 向前翻页时每页数量/Number of posts per page (backward)
- `count` (integer, optional): 首次请求数量/Number of posts for first request

## media_id_to_shortcode

- `media_id` (string, required): 帖子Media ID/Post media ID — e.g. `3774507992167247878`

## search_by_coordinates

- `latitude` (number, required): 纬度/Latitude — e.g. `40.7`
- `longitude` (number, required): 经度/Longitude — e.g. `-74`

## search_hashtags

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `cat`

## search_hashtags

- `query` (string, required): 搜索关键词/Search keyword — e.g. `fashion`
- `rank_token` (string, optional): >-

## search_locations

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `paris`

## search_music

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `happy`

## search_reels

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `cat`
- `pagination_token` (string, optional): 分页token/Pagination token

## search_users

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `instagram`

## search_users

- `query` (string, required): 搜索关键词/Search keyword — e.g. `justin`
- `rank_token` (string, optional): >-

## shortcode_to_media_id

- `shortcode` (string, required): 帖子Shortcode/Post shortcode — e.g. `DRhvwVLAHAG`

## user_id_to_username

- `user_id` (string, required): 用户ID/User ID — e.g. `18527`
