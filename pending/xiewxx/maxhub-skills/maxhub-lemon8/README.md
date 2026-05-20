# Lemon8 Data Assistant

[中文文档](README_CN.md)

Lemon8 content data assistant covering search, discover, posts, users, comments, topics, and trending.

## Features

- **Search & Discover** — fetch_search, fetch_discover_content, fetch_discover_banners, fetch_hot_search_keywords, fetch_editor_picks
- **Post & User** — fetch_post_info, fetch_post_comments, fetch_user_info, fetch_user_following, fetch_user_fans, fetch_topic_info, fetch_topic_posts
- **Link Tools** — fetch_post_id_by_link, fetch_user_id_by_link, fetch_post_ids_batch, fetch_user_ids_batch

## Install

```bash
npx clawhub install maxhub-lemon8
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-lemon8.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Search & Discover | 搜索, 发现 |
| Post & User | 帖子, 用户 |
| Link Tools | 分享, 链接 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
