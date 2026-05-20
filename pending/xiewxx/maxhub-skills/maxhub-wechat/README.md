# WeChat Data Assistant

[中文文档](README_CN.md)

WeChat data assistant covering Channels (video) and Official Accounts (articles) with search, detail, comments, and more.

## Features

- **Channels** — fetch_channels_home, search_channels, search_channels_latest, fetch_channels_hot_topics, fetch_channels_user_search, fetch_channels_user_search_v2, fetch_channels_live_history, fetch_channels_comprehensive_search, fetch_channels_video_detail, fetch_channels_comments, fetch_channels_default_search
- **Official Accounts** — search_mp_account, search_mp_article, fetch_mp_article_list, fetch_mp_article_detail_html, fetch_mp_article_detail_json, fetch_mp_article_url, fetch_mp_article_comments, fetch_mp_article_comment_replies, fetch_mp_article_ad, fetch_mp_related_articles, fetch_mp_article_read_count, fetch_mp_long_url_to_short

## Install

```bash
npx clawhub install maxhub-wechat
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-wechat.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Channels | 视频号, 视频 |
| Official Accounts | 公众号, 文章 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
