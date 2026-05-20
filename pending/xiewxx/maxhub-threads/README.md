# Threads Data Assistant

[中文文档](README_CN.md)

Threads data assistant for posts, user profiles, search, comments, and reposts.

## Features

- **Post & User** — fetch_post_detail, fetch_post_detail_v2, fetch_post_comments, fetch_user_info, fetch_user_info_by_id, fetch_user_posts, fetch_user_replies, fetch_user_reposts
- **Search** — search_recent, search_top, search_profiles

## Install

```bash
npx clawhub install maxhub-threads
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-threads.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Post & User | 帖子, 用户 |
| Search | 搜索, 搜 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
