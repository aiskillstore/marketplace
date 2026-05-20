# Kuaishou Data Assistant

[中文文档](README_CN.md)

Kuaishou data assistant with App and Web API support for video, user, search, trending, live, and comments.

## Features

- **Video Data** — fetch_one_video, fetch_one_video_v2, fetch_video_comments, fetch_video_sub_comments, fetch_user_videos, fetch_user_hot_posts, fetch_video_by_url
- **User Data** — fetch_user_info, fetch_user_id, search_user, fetch_user_collect, fetch_user_live_info
- **Search & Trending** — comprehensive_search, search_video, fetch_hot_list, fetch_hot_categories, fetch_brand_top_list, fetch_live_top_list, fetch_shopping_top_list
- **Live & Tools** — fetch_user_live_replay, generate_share_link, generate_share_short_url

## Install

```bash
npx clawhub install maxhub-kuaishou
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-kuaishou.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Video Data | 视频, 作品 |
| User Data | 用户, 资料 |
| Search & Trending | 搜索, 热榜 |
| Live & Tools | 直播, 分享 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
