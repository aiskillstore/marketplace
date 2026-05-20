# 微信数据助手

[English](README.md)

微信数据查询助手。覆盖视频号和公众号两大模块，支持搜索、视频详情、评论、文章、用户等全功能。

## 功能

- **视频号** — fetch_channels_home, search_channels, search_channels_latest, fetch_channels_hot_topics, fetch_channels_user_search, fetch_channels_user_search_v2, fetch_channels_live_history, fetch_channels_comprehensive_search, fetch_channels_video_detail, fetch_channels_comments, fetch_channels_default_search
- **公众号** — search_mp_account, search_mp_article, fetch_mp_article_list, fetch_mp_article_detail_html, fetch_mp_article_detail_json, fetch_mp_article_url, fetch_mp_article_comments, fetch_mp_article_comment_replies, fetch_mp_article_ad, fetch_mp_related_articles, fetch_mp_article_read_count, fetch_mp_long_url_to_short

## 安装

```bash
npx clawhub install maxhub-wechat
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-wechat.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 视频号 | 视频号，视频 |
| 公众号 | 公众号，文章 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
