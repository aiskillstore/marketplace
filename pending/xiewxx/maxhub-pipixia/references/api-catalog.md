# 皮皮虾（PiPiXia）API完整目录

> 共 17 个API，按能力域分类

## 数据采集（8个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取单个作品数据/Get single video data | GET | `/api/v1/pipixia/app/fetch_post_detail` | cell_id |
| 3 | 获取用户信息/Get user information | GET | `/api/v1/pipixia/app/fetch_user_info` | user_id |
| 4 | 获取用户作品列表/Get user post list | GET | `/api/v1/pipixia/app/fetch_user_post_list` | user_id |
| 5 | 获取首页推荐/Get home feed | GET | `/api/v1/pipixia/app/fetch_home_feed` | - |
| 6 | 获取话题详情/Get hashtag detail | GET | `/api/v1/pipixia/app/fetch_hashtag_detail` | hashtag_id |
| 7 | 获取话题作品列表/Get hashtag post list | GET | `/api/v1/pipixia/app/fetch_hashtag_post_list` | hashtag_id |
| 8 | 获取首页短剧推荐/Get home short drama feed | GET | `/api/v1/pipixia/app/fetch_home_short_drama_feed` | - |

## 数据分析（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取作品统计数据/Get post statistics | GET | `/api/v1/pipixia/app/fetch_post_statistics` | cell_id |

## 互动操作（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取用户粉丝列表/Get user follower list | GET | `/api/v1/pipixia/app/fetch_user_follower_list` | user_id |
| 2 | 获取用户关注列表/Get user following list | GET | `/api/v1/pipixia/app/fetch_user_following_list` | user_id |
| 3 | 获取作品评论列表/Get post comment list | GET | `/api/v1/pipixia/app/fetch_post_comment_list` | cell_id |

## 工具服务（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 生成短连接/Generate short URL | GET | `/api/v1/pipixia/app/fetch_short_url` | original_url |

## 搜索查询（4个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取热搜词条/Get hot search words | GET | `/api/v1/pipixia/app/fetch_hot_search_words` | - |
| 2 | 获取热搜榜单列表/Get hot search board list | GET | `/api/v1/pipixia/app/fetch_hot_search_board_list` | - |
| 3 | 获取热搜榜单详情/Get hot search board detail | GET | `/api/v1/pipixia/app/fetch_hot_search_board_detail` | block_type |
| 4 | 搜索接口/Search API | GET | `/api/v1/pipixia/app/fetch_search` | keyword |

