# Reddit 数据助手

[English](README.md)

Reddit 数据查询助手。覆盖帖子详情、版块、用户、搜索、评论、推荐等全功能。

## 功能

- **帖子数据** — fetch_single_post, fetch_batch_posts, fetch_large_batch_posts, fetch_post_comments, fetch_comment_replies
- **版块** — fetch_subreddit_info, fetch_subreddit_feed, fetch_subreddit_rules, fetch_subreddit_settings, fetch_subreddit_channels, fetch_community_highlights, check_subreddit_muted
- **用户与搜索** — fetch_user_profile, fetch_user_posts, fetch_user_comments, fetch_user_active_subreddits, fetch_user_trophies, fetch_trending_searches, fetch_dynamic_search, fetch_search_typeahead, fetch_home_feed, fetch_popular_feed, fetch_news_feed, fetch_games_feed

## 安装

```bash
npx clawhub install maxhub-reddit
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-reddit.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 帖子数据 | 帖子，详情 |
| 版块 | 版块，社区 |
| 用户与搜索 | 用户，搜索 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
