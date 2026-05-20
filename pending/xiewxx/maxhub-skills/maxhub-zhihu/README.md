# Zhihu Data Assistant

[中文文档](README_CN.md)

Zhihu data assistant for user info, search, columns, Q&A, trending, and comments.

## Features

- **User Data** — fetch_user_info, fetch_user_following, fetch_user_followers, fetch_user_articles, fetch_user_included_articles, fetch_user_columns, fetch_user_follow_topics, fetch_user_follow_questions, fetch_user_follow_collections, fetch_recommend_followees
- **Search & Trending** — fetch_search_suggest, fetch_search_recommend, fetch_preset_search, fetch_ai_search, fetch_article_search, fetch_user_search, fetch_topic_search, fetch_video_search, fetch_column_search, fetch_hot_list, fetch_hot_recommend, fetch_video_list
- **Content & Q&A** — fetch_column_articles, fetch_column_article_detail, fetch_article_relationship, fetch_comment_config, fetch_comment_v5, fetch_sub_comment_v5, fetch_question_answers

## Install

```bash
npx clawhub install maxhub-zhihu
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-zhihu.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| User Data | 用户, 资料 |
| Search & Trending | 搜索, 热榜 |
| Content & Q&A | 文章, 专栏 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
