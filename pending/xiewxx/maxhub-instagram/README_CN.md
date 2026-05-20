# Instagram 数据助手

[English](README.md)

Instagram 全场景数据查询助手。支持V1/V2/V3三个版本API，覆盖用户信息、帖子、Reels、Stories、评论、搜索、话题、地点等全功能。

## 功能

- **用户数据** — fetch_user_info, fetch_user_posts, fetch_user_followers, fetch_user_following, fetch_user_stories, fetch_user_reels, fetch_user_highlights, fetch_user_tagged_posts, fetch_user_about, fetch_user_brief_info, fetch_user_former_usernames
- **帖子与媒体** — fetch_post_info, fetch_post_comments, fetch_comment_replies, fetch_post_likes, fetch_highlight_stories, fetch_post_oembed
- **搜索与发现** — search_users, search_hashtags, search_locations, general_search, fetch_explore_feed, fetch_hashtag_posts, fetch_location_posts, fetch_location_info, fetch_nearby_content
- **内容工具** — convert_media_id_shortcode, extract_shortcode, translate_comment, bulk_translate_comments, fetch_reels_feed, fetch_user_id_by_username

## 安装

```bash
npx clawhub install maxhub-instagram
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-instagram.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 用户数据 | 用户，资料 |
| 帖子与媒体 | 帖子，帖文 |
| 搜索与发现 | 搜索，搜 |
| 内容工具 | 翻译，短码 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
