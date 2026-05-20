# Parameter Mappings / 参数映射

Platform: `bilibili` | Base URL: `https://www.aconfig.cn`

---

## bv_to_aid

- `bv_id` (string, required): 作品id/Video id — e.g. `BV1M1421t7hT`

## fetch_collect_folders

- `uid` (string, required): 用户UID — e.g. `178360345`

## fetch_com_popular

- `pn` (integer, optional): 页码/Page number

## fetch_comment_reply

- `bv_id` (string, required): 作品id/Video id — e.g. `BV1M1421t7hT`
- `pn` (integer, optional): 页码/Page number
- `rpid` (string, required): 回复id/Reply id — e.g. `237109455120`

## fetch_dynamic_detail

- `dynamic_id` (string, required): 动态id/Dynamic id — e.g. `1172584638000922630`

## fetch_dynamic_detail_v2

- `dynamic_id` (string, required): 动态id/Dynamic id — e.g. `1172584638000922630`

## fetch_general_search

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `火影忍者`
- `order` (string, required): 排序方式/Order method — e.g. `totalrank`
- `page` (integer, required): 页码/Page number — e.g. `1`
- `page_size` (integer, required): 每页数量/Number per page — e.g. `42`
- `duration` (integer, optional): 时长筛选/Duration filter
- `pubtime_begin_s` (integer, optional): 开始日期/Start date (10-digit timestamp)
- `pubtime_end_s` (integer, optional): 结束日期/End date (10-digit timestamp)

## fetch_get_user_id

- `share_link` (string, required): 用户分享链接/User share link — e.g. `https://b23.tv/1ZuB5NC`

## fetch_home_feed

- `idx` (integer, optional): 页面索引/Page index
- `flush` (integer, optional): 刷新标记/Flush flag (0=普通加载, 1=刷新)
- `pull` (boolean, optional): 是否下拉刷新/Pull to refresh

## fetch_hot_search

- `limit` (string, required): 返回数量/Return number — e.g. `10`

## fetch_live_room_detail

- `room_id` (string, required): 直播间ID/Live room ID — e.g. `22816111`

## fetch_live_streamers

- `area_id` (string, required): 直播分区id/Live area ID — e.g. `9`
- `pn` (integer, optional): 页码/Page number

## fetch_live_videos

- `room_id` (string, required): 直播间ID/Live room ID — e.g. `1815229528`

## fetch_one_video

- `av_id` (string, optional): AV号/AV ID — e.g. `115568241811221`
- `bv_id` (string, optional): BV号/BV ID — e.g. `BV18SCrBGE9E`

## fetch_one_video

- `bv_id` (string, required): 作品id/Video id — e.g. `BV1M1421t7hT`

## fetch_one_video_v2

- `a_id` (string, required): 作品id/Video id — e.g. `114006081739452`
- `c_id` (string, required): 作品cid/Video cid — e.g. `28400484458`

## fetch_one_video_v3

- `url` (string, required): 视频链接/Video URL — e.g. `https://www.bilibili.com/video/BV1S5uKzzE4r`

## fetch_popular_feed

- `idx` (integer, optional): 页面索引/Page index
- `last_param` (string, optional): 上一页最后一个视频ID/Last video ID

## fetch_reply_detail

- `root` (string, required): 一级评论ID/Root comment ID — e.g. `241743663521`
- `av_id` (string, optional): AV号/AV ID — e.g. `113100682434775`
- `bv_id` (string, optional): BV号/BV ID — e.g. `BV18SCrBGE9E`
- `next_offset` (integer, optional): 下一页游标/Next page cursor
- `ps` (integer, optional): 每页数量/Page size

## fetch_search_all

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `原神`
- `page` (integer, optional): 页码/Page number
- `page_size` (integer, optional): 每页数量/Page size
- `order` (integer, optional): 排序方式/Sort order (0=综合排序)

## fetch_search_by_type

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `原神`
- `search_type` (string, optional): 搜索类型/Search type (video/bangumi/pgc/live/article/user)
- `page` (integer, optional): 页码/Page number
- `page_size` (integer, optional): 每页数量/Page size
- `order` (integer, optional): 排序方式/Sort order (0=综合, 1=最新, 2=播放量, 3=弹幕数)

## fetch_user_collection_videos

- `folder_id` (string, required): 收藏夹id/collection folder id — e.g. `1756059545`
- `pn` (integer, optional): 页码/Page number

## fetch_user_dynamic

- `uid` (string, required): 用户UID — e.g. `16015678`
- `offset` (string, optional): 开始索引/offset — e.g. `953154282154098691`

## fetch_user_info

- `user_id` (string, required): 用户ID/User ID — e.g. `203680252`

## fetch_user_post_videos

- `uid` (string, required): 用户UID — e.g. `178360345`
- `pn` (integer, optional): 页码/Page number
- `order` (string, optional): 排序方式/Order method

## fetch_user_profile

- `uid` (string, required): 用户UID — e.g. `178360345`

## fetch_user_relation_stat

- `uid` (string, required): 用户UID/User UID — e.g. `178360345`

## fetch_user_up_stat

- `uid` (string, required): 用户UID/User UID — e.g. `178360345`

## fetch_user_videos

- `user_id` (string, required): 用户ID/User ID — e.g. `203680252`
- `post_filter` (string, optional): 过滤类型/Filter type (archive/season/contribute)
- `page` (integer, optional): 页码/Page number
- `ps` (integer, optional): 每页数量/Page size

## fetch_video_comments

- `av_id` (string, optional): AV号/AV ID — e.g. `115568241811221`
- `bv_id` (string, optional): BV号/BV ID — e.g. `BV18SCrBGE9E`
- `mode` (integer, optional): 排序模式/Sort mode (3=热门/hot, 2=时间/time)
- `next_offset` (integer, optional): 分页游标/Pagination cursor

## fetch_video_comments

- `bv_id` (string, required): 作品id/Video id — e.g. `BV1M1421t7hT`
- `pn` (integer, optional): 页码/Page number

## fetch_video_danmaku

- `cid` (string, required): 作品cid/Video cid — e.g. `1639235405`

## fetch_video_detail

- `aid` (string, required): 作品id/Video id — e.g. `114902186396822`

## fetch_video_parts

- `bv_id` (string, required): 作品id/Video id — e.g. `BV1vf421i7hV`

## fetch_video_play_info

- `url` (string, required): 视频链接/Video URL — e.g. `https://www.bilibili.com/video/BV1S5uKzzE4r`

## fetch_video_playurl

- `bv_id` (string, required): 作品id/Video id — e.g. `BV1y7411Q7Eq`
- `cid` (string, required): 作品cid/Video cid — e.g. `171776208`

## fetch_video_subtitle

- `a_id` (string, required): 作品id/Video id — e.g. `114006081739452`
- `c_id` (string, required): 作品cid/Video cid — e.g. `28400484458`
