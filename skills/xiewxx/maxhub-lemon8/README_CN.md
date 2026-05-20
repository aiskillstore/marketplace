# Lemon8 数据助手

[English](README.md)

Lemon8 内容数据查询助手。覆盖搜索、发现页、帖子详情、用户信息、评论、话题、热搜等全功能。

## 功能

- **搜索与发现** — fetch_search, fetch_discover_content, fetch_discover_banners, fetch_hot_search_keywords, fetch_editor_picks
- **帖子与用户** — fetch_post_info, fetch_post_comments, fetch_user_info, fetch_user_following, fetch_user_fans, fetch_topic_info, fetch_topic_posts
- **链接工具** — fetch_post_id_by_link, fetch_user_id_by_link, fetch_post_ids_batch, fetch_user_ids_batch

## 安装

```bash
npx clawhub install maxhub-lemon8
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-lemon8.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 搜索与发现 | 搜索，发现 |
| 帖子与用户 | 帖子，用户 |
| 链接工具 | 分享，链接 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
