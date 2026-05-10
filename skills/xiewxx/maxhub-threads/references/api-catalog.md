# Threads（Threads）API完整目录

> 共 11 个API，按能力域分类

## 数据采集（7个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取用户信息/Get user info | GET | `/api/v1/threads/web/fetch_user_info` | username |
| 2 | 根据用户ID获取用户信息/Get user info by ID | GET | `/api/v1/threads/web/fetch_user_info_by_id` | user_id |
| 3 | 获取用户帖子列表/Get user posts | GET | `/api/v1/threads/web/fetch_user_posts` | user_id |
| 4 | 获取用户转发列表/Get user reposts | GET | `/api/v1/threads/web/fetch_user_reposts` | user_id |
| 5 | 获取用户回复列表/Get user replies | GET | `/api/v1/threads/web/fetch_user_replies` | user_id |
| 6 | 获取帖子详情/Get post detail | GET | `/api/v1/threads/web/fetch_post_detail` | post_id |
| 7 | 获取帖子详情 V2(支持链接)/Get post detail V2(suppo | GET | `/api/v1/threads/web/fetch_post_detail_v2` | - |

## 互动操作（1个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取帖子评论/Get post comments | GET | `/api/v1/threads/web/fetch_post_comments` | post_id |

## 搜索查询（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索热门内容/Search top content | GET | `/api/v1/threads/web/search_top` | query |
| 2 | 搜索最新内容/Search recent content | GET | `/api/v1/threads/web/search_recent` | query |
| 3 | 搜索用户档案/Search profiles | GET | `/api/v1/threads/web/search_profiles` | query |
