# B站（Bilibili）API完整目录

> 共 41 个API，按能力域分类

## 数据采集（29个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个视频详情信息/Get single video data | GET | `/api/v1/bilibili/web/fetch_one_video` | bv_id |
| 2 | 获取单个视频详情信息V2/Get single video data V2 | GET | `/api/v1/bilibili/web/fetch_one_video_v2` | a_id, c_id |
| 3 | 获取单个视频详情信息V3/Get single video data V3 | GET | `/api/v1/bilibili/web/fetch_one_video_v3` | url |
| 4 | 获取单个视频详情/Get single video detail | GET | `/api/v1/bilibili/web/fetch_video_detail` | aid |
| 5 | 获取单个视频播放信息/Get single video play info | GET | `/api/v1/bilibili/web/fetch_video_play_info` | url |
| 6 | 获取视频字幕信息/Get video subtitle info | GET | `/api/v1/bilibili/web/fetch_video_subtitle` | a_id, c_id |
| 7 | 获取视频流地址/Get video playurl | GET | `/api/v1/bilibili/web/fetch_video_playurl` | bv_id, cid |
| 9 | 获取用户主页作品数据/Get user homepage video data | GET | `/api/v1/bilibili/web/fetch_user_post_videos` | uid |
| 10 | 获取用户所有收藏夹信息/Get user collection folders | GET | `/api/v1/bilibili/web/fetch_collect_folders` | uid |
| 11 | 获取指定收藏夹内视频数据/Gets video data from a coll | GET | `/api/v1/bilibili/web/fetch_user_collection_videos` | folder_id |
| 12 | 获取指定用户的信息/Get information of specified u | GET | `/api/v1/bilibili/web/fetch_user_profile` | uid |
| 13 | 获取综合热门视频信息/Get comprehensive popular vid | GET | `/api/v1/bilibili/web/fetch_com_popular` | - |
| 14 | 获取指定用户动态/Get dynamic information of spec | GET | `/api/v1/bilibili/web/fetch_user_dynamic` | uid |
| 15 | 获取动态详情/Get dynamic detail | GET | `/api/v1/bilibili/web/fetch_dynamic_detail` | dynamic_id |
| 16 | 获取动态详情v2/Get dynamic detail v2 | GET | `/api/v1/bilibili/web/fetch_dynamic_detail_v2` | dynamic_id |
| 17 | 获取视频实时弹幕/Get Video Danmaku | GET | `/api/v1/bilibili/web/fetch_video_danmaku` | cid |
| 18 | 获取指定直播间信息/Get information of specified l | GET | `/api/v1/bilibili/web/fetch_live_room_detail` | room_id |
| 19 | 获取直播间视频流/Get live video data of specifie | GET | `/api/v1/bilibili/web/fetch_live_videos` | room_id |
| 20 | 获取指定分区正在直播的主播/Get live streamers of spec | GET | `/api/v1/bilibili/web/fetch_live_streamers` | area_id |
| 21 | 获取所有直播分区列表/Get a list of all live areas | GET | `/api/v1/bilibili/web/fetch_all_live_areas` | - |
| 22 | 通过bv号获得视频分p信息/Get Video Parts By bvid | GET | `/api/v1/bilibili/web/fetch_video_parts` | bv_id |
| 23 | 获取单个视频详情信息/Get single video data | GET | `/api/v1/bilibili/app/fetch_one_video` | - |
| 24 | 获取用户投稿视频/Get user videos | GET | `/api/v1/bilibili/app/fetch_user_videos` | user_id |
| 25 | 获取用户信息/Get user info | GET | `/api/v1/bilibili/app/fetch_user_info` | user_id |
| 26 | 获取主页推荐视频流/Get home feed | GET | `/api/v1/bilibili/app/fetch_home_feed` | - |
| 27 | 获取热门推荐/Get popular feed | GET | `/api/v1/bilibili/app/fetch_popular_feed` | - |
| 28 | 获取影视推荐/Get cinema tab | GET | `/api/v1/bilibili/app/fetch_cinema_tab` | - |
| 29 | 获取番剧推荐/Get bangumi tab | GET | `/api/v1/bilibili/app/fetch_bangumi_tab` | - |

## 搜索查询（4个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取热门搜索信息/Get hot search data | GET | `/api/v1/bilibili/web/fetch_hot_search` | limit |
| 2 | 获取综合搜索信息/Get general search data | GET | `/api/v1/bilibili/web/fetch_general_search` | keyword, order, page, page_size |
| 3 | 综合搜索/search all | GET | `/api/v1/bilibili/app/fetch_search_all` | keyword |
| 4 | 分类搜索/ search by type | GET | `/api/v1/bilibili/app/fetch_search_by_type` | keyword |

## 数据分析（2个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取UP主状态统计/Get UP stat (total likes and v | GET | `/api/v1/bilibili/web/fetch_user_up_stat` | uid |
| 2 | 获取用户关系状态统计/Get user relation stat (follo | GET | `/api/v1/bilibili/web/fetch_user_relation_stat` | uid |

## 互动操作（4个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取指定视频的评论/Get comments on the specified  | GET | `/api/v1/bilibili/web/fetch_video_comments` | bv_id |
| 2 | 获取视频下指定评论的回复/Get reply to the specified  | GET | `/api/v1/bilibili/web/fetch_comment_reply` | bv_id, rpid |
| 3 | 获取视频评论列表/Get video comments | GET | `/api/v1/bilibili/app/fetch_video_comments` | - |
| 4 | 获取二级评论回复/Get reply detail | GET | `/api/v1/bilibili/app/fetch_reply_detail` | root |

## 工具服务（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 通过bv号获得视频aid号/Generate aid by bvid | GET | `/api/v1/bilibili/web/bv_to_aid` | bv_id |

## 内容解析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 提取用户ID/Extract user ID | GET | `/api/v1/bilibili/web/fetch_get_user_id` | share_link |

