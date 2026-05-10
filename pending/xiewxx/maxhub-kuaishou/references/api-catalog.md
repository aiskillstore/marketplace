# 快手（Kuaishou）API完整目录

> 共 33 个API，按能力域分类

## 数据采集（23个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个作品数据 V1/Get single video data V1 | GET | `/api/v1/kuaishou/web/fetch_one_video` | share_text |
| 2 | 获取单个作品数据 V2/Get single video data V2 | GET | `/api/v1/kuaishou/web/fetch_one_video_v2` | photo_id |
| 3 | 链接获取作品数据/Fetch single video by URL | GET | `/api/v1/kuaishou/web/fetch_one_video_by_url` | url |
| 4 | 获取用户信息/Fetch user info | GET | `/api/v1/kuaishou/web/fetch_user_info` | user_id |
| 5 | 获取用户发布作品/Fetch user posts | GET | `/api/v1/kuaishou/web/fetch_user_post` | user_id |
| 6 | 获取用户直播回放/Fetch user live replay | GET | `/api/v1/kuaishou/web/fetch_user_live_replay` | user_id |
| 7 | 获取用户收藏作品/Fetch user collect | GET | `/api/v1/kuaishou/web/fetch_user_collect` | user_id |
| 8 | 获取快手热榜 V1/Fetch Kuaishou Hot List V1 | GET | `/api/v1/kuaishou/web/fetch_kuaishou_hot_list_v1` | - |
| 9 | 获取快手热榜 V2/Fetch Kuaishou Hot List V2 | GET | `/api/v1/kuaishou/web/fetch_kuaishou_hot_list_v2` | - |
| 10 | 获取用户ID/Fetch user ID | GET | `/api/v1/kuaishou/web/fetch_get_user_id` | share_link |
| 11 | 视频详情V1/Video detailsV1 | GET | `/api/v1/kuaishou/app/fetch_one_video` | photo_id |
| 12 | 根据链接获取单个作品数据/Fetch single video by URL | GET | `/api/v1/kuaishou/app/fetch_one_video_by_url` | share_text |
| 13 | 获取单个用户数据V2/Get single user data V2 | GET | `/api/v1/kuaishou/app/fetch_one_user_v2` | user_id |
| 14 | 获取用户直播信息/Get user live info | GET | `/api/v1/kuaishou/app/fetch_user_live_info` | user_id |
| 15 | 获取用户热门作品数据/Get user hot post data | GET | `/api/v1/kuaishou/app/fetch_user_hot_post` | user_id |
| 16 | 用户视频列表V2/User video list V2 | GET | `/api/v1/kuaishou/app/fetch_user_post_v2` | user_id |
| 17 | 快手热榜分类/Kuaishou hot categories | GET | `/api/v1/kuaishou/app/fetch_hot_board_categories` | - |
| 18 | 快手热榜详情/Kuaishou hot board detail | GET | `/api/v1/kuaishou/app/fetch_hot_board_detail` | - |
| 19 | 快手直播榜单/Kuaishou live top list | GET | `/api/v1/kuaishou/app/fetch_live_top_list` | - |
| 20 | 快手购物榜单/Kuaishou shopping top list | GET | `/api/v1/kuaishou/app/fetch_shopping_top_list` | - |
| 21 | 快手品牌榜单/Kuaishou brand top list | GET | `/api/v1/kuaishou/app/fetch_brand_top_list` | - |
| 22 | 获取魔法表情使用人数/Fetch magic face usage count | GET | `/api/v1/kuaishou/app/fetch_magic_face_usage` | magic_face_id |
| 23 | 获取魔法表情热门视频/Fetch magic face hot videos | GET | `/api/v1/kuaishou/app/fetch_magic_face_hot` | magic_face_id |

## 互动操作（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取作品一级评论/Fetch video comments | GET | `/api/v1/kuaishou/web/fetch_one_video_comment` | photo_id |
| 2 | 获取作品二级评论/Fetch video sub comments | GET | `/api/v1/kuaishou/web/fetch_one_video_sub_comment` | photo_id, root_comment_id |
| 3 | 获取单个作品评论数据/Get single video comment data | GET | `/api/v1/kuaishou/app/fetch_one_video_comment` | photo_id |

## 工具服务（2个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 生成分享短连接/Generate share short URL | GET | `/api/v1/kuaishou/web/generate_share_short_url` | photo_id |
| 2 | 生成快手分享链接/Generate Kuaishou share link | GET | `/api/v1/kuaishou/app/generate_kuaishou_share_link` | shareObjectId |

## 搜索查询（5个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 快手批量视频查询接口/Kuaishou batch video query AP | GET | `/api/v1/kuaishou/app/fetch_videos_batch` | photo_ids |
| 2 | 综合搜索/Comprehensive search | GET | `/api/v1/kuaishou/app/search_comprehensive` | keyword |
| 3 | 搜索视频V2/Search video V2 | GET | `/api/v1/kuaishou/app/search_video_v2` | keyword |
| 4 | 搜索用户V2/Search user V2 | GET | `/api/v1/kuaishou/app/search_user_v2` | keyword |
| 5 | 快手热搜人物榜单/Kuaishou hot search person boar | GET | `/api/v1/kuaishou/app/fetch_hot_search_person` | - |
