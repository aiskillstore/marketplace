# Toutiao Data Assistant

[中文文档](README_CN.md)

Toutiao data assistant for articles, videos, users, and comments.

## Features

- **Content & User** — fetch_article_info, fetch_video_info, fetch_user_info, fetch_post_comments, get_user_id_from_profile

## Install

```bash
npx clawhub install maxhub-toutiao
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-toutiao.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Content & User | 文章, 视频 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
