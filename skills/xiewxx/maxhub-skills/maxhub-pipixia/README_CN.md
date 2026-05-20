# 皮皮虾数据助手

[English](README.md)

皮皮虾数据查询助手。覆盖作品详情、用户数据、搜索、热搜、评论、话题等全功能。

## 功能

- **作品与用户** — fetch_single_video, fetch_post_statistics, fetch_post_comments, fetch_user_info, fetch_user_posts, fetch_user_following, fetch_user_followers
- **搜索与热搜** — fetch_search, fetch_hot_search_board_list, fetch_hot_search_board_detail, fetch_hot_search_words, fetch_hashtag_detail, fetch_hashtag_posts, fetch_home_feed, fetch_home_short_drama
- **工具** — generate_short_url, increase_post_view_count

## 安装

```bash
npx clawhub install maxhub-pipixia
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-pipixia.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 作品与用户 | 作品，用户 |
| 搜索与热搜 | 搜索，热搜 |
| 工具 | 短链接，浏览 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
