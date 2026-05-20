# PiPiXia Data Assistant

[中文文档](README_CN.md)

PiPiXia data assistant for posts, users, search, trending, comments, and topics.

## Features

- **Post & User** — fetch_single_video, fetch_post_statistics, fetch_post_comments, fetch_user_info, fetch_user_posts, fetch_user_following, fetch_user_followers
- **Search & Trending** — fetch_search, fetch_hot_search_board_list, fetch_hot_search_board_detail, fetch_hot_search_words, fetch_hashtag_detail, fetch_hashtag_posts, fetch_home_feed, fetch_home_short_drama
- **Tools** — generate_short_url, increase_post_view_count

## Install

```bash
npx clawhub install maxhub-pipixia
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-pipixia.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Post & User | 作品, 用户 |
| Search & Trending | 搜索, 热搜 |
| Tools | 短链接, 浏览 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
