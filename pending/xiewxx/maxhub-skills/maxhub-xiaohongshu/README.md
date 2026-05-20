# Xiaohongshu Data Assistant

[中文文档](README_CN.md)

Xiaohongshu data assistant with multi-version App/Web APIs for notes, users, search, products, comments, and topics.

## Features

- **Note Data** — fetch_note_info, fetch_note_detail, fetch_note_comments, fetch_note_sub_comments, fetch_note_image, fetch_one_note_feed
- **User Data** — fetch_user_info, fetch_user_notes, fetch_user_faved_notes, fetch_user_following, fetch_user_followers, extract_user_id_from_link
- **Search** — search_notes, search_users, search_products, fetch_search_suggestions, fetch_trending_keywords, fetch_home_feed
- **Product & Topic** — fetch_product_detail, fetch_product_reviews, fetch_product_review_overview, fetch_product_list, fetch_topic_info, fetch_topic_feed, fetch_hot_list

## Install

```bash
npx clawhub install maxhub-xiaohongshu
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-xiaohongshu.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Note Data | 笔记, 详情 |
| User Data | 用户, 资料 |
| Search | 搜索, 搜 |
| Product & Topic | 商品, 话题 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
