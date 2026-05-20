# Parameter Mappings / 参数映射

Platform: `sora2` | Base URL: `https://www.aconfig.cn`

---

## get_cameo_leaderboard

- `cursor` (string, optional): 翻页参数（可选）/Cursor for pagination (optional)

## get_comment_replies

- `comment_id` (string, required): 一级评论ID/First-level comment ID — e.g. `68e659c5a37081919618c57baf499d0c`
- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response

## get_feed

- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response
- `eager_views` (string, optional): >- — e.g. `{"views":[]}`

## get_post_comments

- `post_id` (string, required): 作品ID/Post ID — e.g. `s_68e647d78e5081918cdeaf27e7edc735`
- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response

## get_post_detail

- `post_id` (string, optional): 作品ID（可选）/Post ID (optional) — e.g. `s_68e853d2ad448191b3c81e830f53c3a2`
- `post_url` (string, optional): 作品链接（可选）/Post URL (optional) — e.g. `https://sora.chatgpt.com/p/s_68e853d2ad448191b3c81e830f53c3a2`

## get_post_remix_list

- `post_id` (string, optional): 作品ID（可选）/Post ID (optional) — e.g. `s_690acc0f4fcc8191ab5a75a96b6b6caf`
- `post_url` (string, optional): 作品链接（可选）/Post URL (optional) — e.g. `https://sora.chatgpt.com/p/s_690acc0f4fcc8191ab5a75a96b6b6caf`
- `cursor` (string, optional): 翻页参数（可选）/Cursor for pagination (optional)

## get_user_cameo_appearances

- `user_id` (string, required): 用户ID/User ID — e.g. `user-xiCyLclE6KJcdTXyvVq3Ontc`
- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response

## get_user_followers

- `user_id` (string, required): 用户ID/User ID — e.g. `user-xiCyLclE6KJcdTXyvVq3Ontc`
- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response

## get_user_following

- `user_id` (string, required): 用户ID/User ID — e.g. `user-BOXD64QrAyZVybLCeXTqJWm3`
- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response

## get_user_posts

- `user_id` (string, required): 用户ID/User ID — e.g. `user-xiCyLclE6KJcdTXyvVq3Ontc`
- `cursor` (string, optional): 翻页参数，从上一次响应中获取/Pagination cursor from previous response

## get_user_profile

- `user_id` (string, required): 用户ID/User ID — e.g. `user-xiCyLclE6KJcdTXyvVq3Ontc`

## get_video_download_info

- `post_id` (string, optional): 作品ID（可选）/Post ID (optional) — e.g. `s_68e853d2ad448191b3c81e830f53c3a2`
- `post_url` (string, optional): 作品链接（可选）/Post URL (optional) — e.g. `https://sora.chatgpt.com/p/s_68e853d2ad448191b3c81e830f53c3a2`

## search_users

- `username` (string, required): 搜索关键词（用户名）/Search keyword (username) — e.g. `sam`
