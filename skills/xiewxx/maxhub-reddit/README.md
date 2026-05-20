# Reddit Data Assistant

[中文文档](README_CN.md)

Reddit data assistant for posts, subreddits, users, search, comments, and feeds.

## Features

- **Post Data** — fetch_single_post, fetch_batch_posts, fetch_large_batch_posts, fetch_post_comments, fetch_comment_replies
- **Subreddit** — fetch_subreddit_info, fetch_subreddit_feed, fetch_subreddit_rules, fetch_subreddit_settings, fetch_subreddit_channels, fetch_community_highlights, check_subreddit_muted
- **User & Search** — fetch_user_profile, fetch_user_posts, fetch_user_comments, fetch_user_active_subreddits, fetch_user_trophies, fetch_trending_searches, fetch_dynamic_search, fetch_search_typeahead, fetch_home_feed, fetch_popular_feed, fetch_news_feed, fetch_games_feed

## Install

```bash
npx clawhub install maxhub-reddit
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-reddit.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Post Data | 帖子, 详情 |
| Subreddit | 版块, 社区 |
| User & Search | 用户, 搜索 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
