# YouTube（YouTube）API完整目录

> 共 44 个API，按能力域分类

## 数据采集（27个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取视频信息 V1/Get video information V1 | GET | `/api/v1/youtube/web/get_video_info` | video_id |
| 2 | 获取视频信息 V2/Get video information V2 | GET | `/api/v1/youtube/web/get_video_info_v2` | video_id |
| 3 | 获取视频详情 V3/Get video information V3 | GET | `/api/v1/youtube/web/get_video_info_v3` | video_id |
| 4 | 获取视频字幕/Get video subtitles | GET | `/api/v1/youtube/web/get_video_subtitles` | subtitle_url |
| 5 | 获取频道描述信息/Get channel description | GET | `/api/v1/youtube/web/get_channel_description` | - |
| 6 | 获取推荐视频/Get related videos | GET | `/api/v1/youtube/web/get_relate_video` | video_id |
| 7 | 获取频道ID/Get channel ID | GET | `/api/v1/youtube/web/get_channel_id` | channel_name |
| 8 | 从频道URL获取频道ID V2/Get channel ID from URL  | GET | `/api/v1/youtube/web/get_channel_id_v2` | channel_url |
| 9 | 从频道ID获取频道URL/Get channel URL from channe | GET | `/api/v1/youtube/web/get_channel_url` | channel_id |
| 10 | 获取频道信息/Get channel information | GET | `/api/v1/youtube/web/get_channel_info` | channel_id |
| 11 | 获取频道视频 V1（即将过时，优先使用 V2）/Get channel vide | GET | `/api/v1/youtube/web/get_channel_videos` | channel_id |
| 12 | 获取频道视频 V2/Get channel videos V2 | GET | `/api/v1/youtube/web/get_channel_videos_v2` | channel_id |
| 13 | 获取频道视频 V3/Get channel videos V3 | GET | `/api/v1/youtube/web/get_channel_videos_v3` | channel_id |
| 14 | 获取频道短视频/Get channel short videos | GET | `/api/v1/youtube/web/get_channel_short_videos` | channel_id |
| 15 | 获取视频详情 /Get video information | GET | `/api/v1/youtube/web_v2/get_video_info` | video_id |
| 16 | 获取频道描述信息/Get channel description | GET | `/api/v1/youtube/web_v2/get_channel_description` | - |
| 17 | 从频道URL获取频道ID /Get channel ID from URL | GET | `/api/v1/youtube/web_v2/get_channel_id` | channel_url |
| 18 | 从频道ID获取频道URL/Get channel URL from channe | GET | `/api/v1/youtube/web_v2/get_channel_url` | channel_id |
| 19 | 获取频道视频 /Get channel videos | GET | `/api/v1/youtube/web_v2/get_channel_videos` | channel_id |
| 20 | 获取视频流信息/Get video streams info | GET | `/api/v1/youtube/web_v2/get_video_streams` | - |
| 21 | 获取视频流信息 V2/Get video streams info V2 | GET | `/api/v1/youtube/web_v2/get_video_streams_v2` | - |
| 22 | 获取已签名的视频流URL/Get signed video stream URL | GET | `/api/v1/youtube/web_v2/get_signed_stream_url` | itag |
| 23 | 获取视频字幕/Get video captions | GET | `/api/v1/youtube/web_v2/get_video_captions` | - |
| 24 | 获取视频相似内容/Get related videos | GET | `/api/v1/youtube/web_v2/get_related_videos` | - |
| 25 | 获取频道短视频列表/Get channel shorts | GET | `/api/v1/youtube/web_v2/get_channel_shorts` | - |
| 26 | 获取频道帖子列表/Get channel community posts | GET | `/api/v1/youtube/web_v2/get_channel_community_posts` | channel_id |
| 27 | 获取帖子详情/Get post detail | GET | `/api/v1/youtube/web_v2/get_post_detail` | post_id |

## 互动操作（6个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取视频评论/Get video comments | GET | `/api/v1/youtube/web/get_video_comments` | video_id |
| 2 | 获取视频二级评论/Get video sub comments | GET | `/api/v1/youtube/web/get_video_comment_replies` | continuation_token |
| 3 | 获取视频评论/Get video comments | GET | `/api/v1/youtube/web_v2/get_video_comments` | video_id |
| 4 | 获取视频二级评论/Get video sub comments | GET | `/api/v1/youtube/web_v2/get_video_comment_replies` | continuation_token |
| 5 | 获取帖子评论/Get post comments | GET | `/api/v1/youtube/web_v2/get_post_comments` | - |
| 6 | 获取帖子评论回复/Get post comment replies | GET | `/api/v1/youtube/web_v2/get_post_comment_replies` | continuation_token |

## 搜索查询（10个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索视频/Search video | GET | `/api/v1/youtube/web/search_video` | search_query |
| 2 | 综合搜索（支持过滤条件）/General search with filters | GET | `/api/v1/youtube/web/get_general_search` | search_query |
| 3 | YouTube Shorts短视频搜索/YouTube Shorts searc | GET | `/api/v1/youtube/web/get_shorts_search` | search_query |
| 4 | 搜索频道/Search channel | GET | `/api/v1/youtube/web/search_channel` | channel_id, search_query |
| 5 | 综合搜索（原始数据，推荐使用V2）/General search (raw da | GET | `/api/v1/youtube/web_v2/get_general_search` | search_query |
| 6 | 综合搜索V2/General search V2 | GET | `/api/v1/youtube/web_v2/get_general_search_v2` | - |
| 7 | Shorts搜索（原始数据，推荐使用V2）/Shorts search (raw | GET | `/api/v1/youtube/web_v2/get_shorts_search` | search_query |
| 8 | Shorts搜索V2/Shorts search V2 | GET | `/api/v1/youtube/web_v2/get_shorts_search_v2` | - |
| 9 | 获取搜索推荐词/Get search suggestions | GET | `/api/v1/youtube/web_v2/get_search_suggestions` | keyword |
| 10 | 搜索频道/Search channels | GET | `/api/v1/youtube/web_v2/search_channels` | - |

## 数据分析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取趋势视频/Get trending videos | GET | `/api/v1/youtube/web/get_trending_videos` | - |
