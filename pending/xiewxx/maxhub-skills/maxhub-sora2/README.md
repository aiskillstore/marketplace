# Sora2 Data Assistant

[中文文档](README_CN.md)

Sora2 video platform data assistant for posts, users, search, comments, and Cameo features.

## Features

- **Post & User** — fetch_single_post, fetch_post_comments, fetch_comment_replies, fetch_post_remix_list, fetch_none_watermark_download, fetch_user_profile, fetch_user_posts, fetch_user_following, fetch_user_followers, fetch_feed, search_users
- **Cameo** — fetch_cameo_leaderboard, fetch_user_cameo_list
- **Tools** — upload_image

## Install

```bash
npx clawhub install maxhub-sora2
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-sora2.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Post & User | 作品, 用户 |
| Cameo | Cameo, 出镜秀 |
| Tools | 上传, 图片 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
