# 小红书数据助手

[English](README.md)

小红书全场景数据查询助手。支持App和Web多版本API，覆盖笔记详情、用户数据、搜索、商品、评论、话题等全功能。

## 功能

- **笔记数据** — fetch_note_info, fetch_note_detail, fetch_note_comments, fetch_note_sub_comments, fetch_note_image, fetch_one_note_feed
- **用户数据** — fetch_user_info, fetch_user_notes, fetch_user_faved_notes, fetch_user_following, fetch_user_followers, extract_user_id_from_link
- **搜索** — search_notes, search_users, search_products, fetch_search_suggestions, fetch_trending_keywords, fetch_home_feed
- **商品与话题** — fetch_product_detail, fetch_product_reviews, fetch_product_review_overview, fetch_product_list, fetch_topic_info, fetch_topic_feed, fetch_hot_list

## 安装

```bash
npx clawhub install maxhub-xiaohongshu
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-xiaohongshu.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 笔记数据 | 笔记，详情 |
| 用户数据 | 用户，资料 |
| 搜索 | 搜索，搜 |
| 商品与话题 | 商品，话题 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
