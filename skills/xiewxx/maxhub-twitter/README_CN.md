# Twitter/X 数据助手

[English](README.md)

Twitter/X 数据查询助手。覆盖推文详情、用户资料、搜索、评论、趋势等全功能。

## 功能

- **推文数据** — fetch_single_tweet, fetch_tweet_comments, fetch_comments, fetch_retweet_users
- **用户数据** — fetch_user_profile, fetch_user_posts, fetch_user_media, fetch_user_replies, fetch_user_highlights, fetch_user_followings, fetch_user_followers
- **搜索与趋势** — search, fetch_trending

## 安装

```bash
npx clawhub install maxhub-twitter
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-twitter.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 推文数据 | 推文，详情 |
| 用户数据 | 用户，资料 |
| 搜索与趋势 | 搜索，趋势 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
