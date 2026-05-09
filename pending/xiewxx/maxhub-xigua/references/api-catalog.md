# 西瓜视频（Xigua）API完整目录

> 共 7 个API，按能力域分类

## 数据采集（5个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个作品数据/Get single video data | GET | `/api/v1/xigua/app/v2/fetch_one_video` | item_id |
| 2 | 获取单个作品数据 V2/Get single video data V2 | GET | `/api/v1/xigua/app/v2/fetch_one_video_v2` | item_id |
| 3 | 获取单个作品的播放链接/Get single video play URL | GET | `/api/v1/xigua/app/v2/fetch_one_video_play_url` | item_id |
| 4 | 个人信息/Personal information | GET | `/api/v1/xigua/app/v2/fetch_user_info` | user_id |
| 5 | 获取个人作品列表/Get user post list | GET | `/api/v1/xigua/app/v2/fetch_user_post_list` | user_id |

## 互动操作（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 视频评论列表/Video comment list | GET | `/api/v1/xigua/app/v2/fetch_video_comment_list` | item_id |

## 搜索查询（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索视频/Search video | GET | `/api/v1/xigua/app/v2/search_video` | keyword |

