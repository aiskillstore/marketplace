# 头条（Toutiao）API完整目录

> 共 7 个API，按能力域分类

## 数据采集（6个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取指定文章的信息/Get information of specified a | GET | `/api/v1/toutiao/web/get_article_info` | aweme_id |
| 2 | 获取指定视频的信息/Get information of specified v | GET | `/api/v1/toutiao/web/get_video_info` | aweme_id |
| 3 | 获取指定文章的信息/Get information of specified a | GET | `/api/v1/toutiao/app/get_article_info` | group_id |
| 4 | 获取指定视频的信息/Get information of specified v | GET | `/api/v1/toutiao/app/get_video_info` | group_id |
| 5 | 获取指定用户的信息/Get information of specified u | GET | `/api/v1/toutiao/app/get_user_info` | user_id |
| 6 | 从头条用户主页获取用户user_id/Get user_id from user | GET | `/api/v1/toutiao/app/get_user_id` | user_profile_url |

## 互动操作（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取指定作品的评论/Get comments of specified post | GET | `/api/v1/toutiao/app/get_comments` | group_id, offset |

