# 知乎数据助手

[English](README.md)

知乎数据查询助手。覆盖用户信息、搜索、专栏、问答、热榜、评论等全功能。

## 功能

- **用户数据** — fetch_user_info, fetch_user_following, fetch_user_followers, fetch_user_articles, fetch_user_included_articles, fetch_user_columns, fetch_user_follow_topics, fetch_user_follow_questions, fetch_user_follow_collections, fetch_recommend_followees
- **搜索与热榜** — fetch_search_suggest, fetch_search_recommend, fetch_preset_search, fetch_ai_search, fetch_article_search, fetch_user_search, fetch_topic_search, fetch_video_search, fetch_column_search, fetch_hot_list, fetch_hot_recommend, fetch_video_list
- **内容与问答** — fetch_column_articles, fetch_column_article_detail, fetch_article_relationship, fetch_comment_config, fetch_comment_v5, fetch_sub_comment_v5, fetch_question_answers

## 安装

```bash
npx clawhub install maxhub-zhihu
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-zhihu.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 用户数据 | 用户，资料 |
| 搜索与热榜 | 搜索，热榜 |
| 内容与问答 | 文章，专栏 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
