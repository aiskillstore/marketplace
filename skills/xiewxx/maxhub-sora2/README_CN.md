# Sora2 数据助手

[English](README.md)

Sora2 视频平台数据查询助手。覆盖作品详情、用户数据、搜索、评论、Cameo等全功能。

## 功能

- **作品与用户** — fetch_single_post, fetch_post_comments, fetch_comment_replies, fetch_post_remix_list, fetch_none_watermark_download, fetch_user_profile, fetch_user_posts, fetch_user_following, fetch_user_followers, fetch_feed, search_users
- **Cameo出镜秀** — fetch_cameo_leaderboard, fetch_user_cameo_list
- **工具** — upload_image

## 安装

```bash
npx clawhub install maxhub-sora2
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-sora2.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 作品与用户 | 作品，用户 |
| Cameo出镜秀 | Cameo，出镜秀 |
| 工具 | 上传，图片 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
