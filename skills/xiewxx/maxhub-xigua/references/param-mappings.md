# Parameter Mappings / 参数映射

Platform: `xigua` | Base URL: `https://www.aconfig.cn`

---

## fetch_one_video

- `item_id` (string, required): 作品id/Video id — e.g. `7354954305222377999`

## fetch_one_video_play_url

- `item_id` (string, required): 作品id/Video id — e.g. `7354954305222377999`

## fetch_one_video_v2

- `item_id` (string, required): 作品id/Video id — e.g. `7354954305222377999`

## fetch_user_info

- `user_id` (string, required): 用户id/User id — e.g. `52712347586`

## fetch_user_post_list

- `user_id` (string, required): 用户id/User id — e.g. `1922379661976311`
- `max_behot_time` (string, optional): 最大行为时间/Maximum behavior time

## fetch_video_comment_list

- `item_id` (string, required): 作品id/Video id — e.g. `7354954305222377999`
- `offset` (integer, optional): 偏移量/Offset
- `count` (integer, optional): 数量/Count

## search_video

- `keyword` (string, required): 关键词/Keyword — e.g. `抖音`
- `offset` (integer, optional): 偏移量/Offset
- `order_type` (string, optional): 排序方式/Order type
- `min_duration` (integer, optional): 最小时长/Minimum duration
- `max_duration` (integer, optional): 最大时长/Maximum duration
