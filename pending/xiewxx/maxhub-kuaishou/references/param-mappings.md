# Parameter Mappings / 参数映射

Platform: `kuaishou` | Base URL: `https://www.aconfig.cn`

---

## fetch_get_user_id

- `share_link` (string, required): '' — e.g. `https://v.kuaishou.com/KcdKDwFp`

## fetch_kuaishou_hot_list_v2

- `board_type` (string, optional): '' — e.g. `1`

## fetch_one_video

- `photo_id` (string, required): '' — e.g. `3xhpk3xcf6e4iac`

## fetch_one_video_by_url

- `share_text` (string, required): '' — e.g. `https://v.kuaishou.com/cNYP0Z`

## fetch_one_video_comment

- `photo_id` (string, required): '' — e.g. `3x7gxp2zhgjv832`
- `pcursor` (string, optional): ''

## fetch_user_info

- `user_id` (string, required): '' — e.g. `3xz63mn6fngqtiq`

## fetch_videos_batch

- `photo_ids` (string, required): >- — e.g. `5228960823332207296,5196309727975443273,5222486898325987583`

## search_comprehensive

- `keyword` (string, required): '' — e.g. `汽车之家`
- `pcursor` (string, optional): ''
- `sort_type` (string, optional): '可选值: all(综合排序), newest(最新发布), most_likes(最多点赞)'
- `publish_time` (string, optional): '可选值: all(全部), one_day(近一日), one_week(近一周), one_month(近一月)'
- `duration` (string, optional): >-
- `search_scope` (string, optional): '可选值: all(全部)'
