# Sora2（Sora2）API完整目录

> 共 17 个API，按能力域分类

## 数据采集（8个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单一作品详情/Fetch single post detail | GET | `/api/v1/sora2/get_post_detail` | - |
| 2 | 获取作品的 Remix 列表/Fetch post remix list | GET | `/api/v1/sora2/get_post_remix_list` | - |
| 3 | 获取用户信息档案/Fetch user profile | GET | `/api/v1/sora2/get_user_profile` | user_id |
| 4 | 获取用户发布的帖子列表/Fetch user posts | GET | `/api/v1/sora2/get_user_posts` | user_id |
| 5 | 获取用户Cameo出镜秀列表/Fetch user cameo appearan | GET | `/api/v1/sora2/get_user_cameo_appearances` | user_id |
| 6 | 获取Feed流（热门/推荐视频）/Fetch feed | GET | `/api/v1/sora2/get_feed` | - |
| 7 | 上传图片获取media_id/Upload image to get media | POST | `/api/v1/sora2/upload_image` | - |
| 8 | [已弃用/Deprecated] 查询任务状态/Get task status | GET | `/api/v1/sora2/get_task_status` | task_id |

## 内容解析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取无水印视频下载信息/Fetch none watermark video d | GET | `/api/v1/sora2/get_video_download_info` | - |

## 互动操作（4个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取作品一级评论/Fetch post comments | GET | `/api/v1/sora2/get_post_comments` | post_id |
| 2 | 获取评论的回复/Fetch comment replies | GET | `/api/v1/sora2/get_comment_replies` | comment_id |
| 3 | 获取用户粉丝列表/Fetch user followers | GET | `/api/v1/sora2/get_user_followers` | user_id |
| 4 | 获取用户关注列表/Fetch user following | GET | `/api/v1/sora2/get_user_following` | user_id |

## 创作者/达人（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取 Cameo 出镜秀达人排行榜/Fetch Cameo leaderboar | GET | `/api/v1/sora2/get_cameo_leaderboard` | - |

## 搜索查询（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索用户/Search users | GET | `/api/v1/sora2/search_users` | username |

## 工具服务（2个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | [已弃用/Deprecated] 文本/图片生成视频/Create video  | POST | `/api/v1/sora2/create_video` | - |
| 2 | [已弃用/Deprecated] 获取任务生成的作品详情（无水印版本）/Get  | GET | `/api/v1/sora2/get_task_detail` | - |

