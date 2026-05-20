# Threads 数据助手

[English](README.md)

Threads 数据查询助手。覆盖帖子详情、用户资料、搜索、评论、转发等全功能。

## 功能

- **帖子与用户** — fetch_post_detail, fetch_post_detail_v2, fetch_post_comments, fetch_user_info, fetch_user_info_by_id, fetch_user_posts, fetch_user_replies, fetch_user_reposts
- **搜索** — search_recent, search_top, search_profiles

## 安装

```bash
npx clawhub install maxhub-threads
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-threads.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 帖子与用户 | 帖子，用户 |
| 搜索 | 搜索，搜 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
