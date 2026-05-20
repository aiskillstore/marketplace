# LinkedIn 数据助手

[English](README.md)

LinkedIn 职场数据查询助手。覆盖用户资料、公司信息、职位搜索、帖子、评论、广告等全功能，支持V1/V2双版本API。

## 功能

- **用户资料** — get_user_profile, fetch_user_experience, fetch_user_skills, fetch_user_educations, fetch_user_publications, fetch_user_certifications, fetch_user_recommendations, fetch_user_honors, fetch_user_volunteers, fetch_user_bio, fetch_user_contact_info, fetch_user_follower_count, fetch_user_profile_top_card
- **公司数据** — fetch_company_profile, fetch_company_people, fetch_company_posts, fetch_company_jobs, fetch_company_job_count, fetch_company_affiliated_pages, fetch_company_competitors, fetch_company_locations, fetch_company_cta_buttons, fetch_stock_quote
- **搜索与职位** — search_people, search_users, search_jobs, search_posts, search_ads, fetch_job_detail
- **内容与互动** — fetch_post_detail, fetch_post_comments, fetch_post_reactions, fetch_post_reposts, fetch_user_posts, fetch_user_comments, fetch_user_reactions, fetch_hashtag_feed, fetch_comment_replies

## 安装

```bash
npx clawhub install maxhub-linkedin
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-linkedin.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 用户资料 | 用户，资料 |
| 公司数据 | 公司，企业 |
| 搜索与职位 | 搜索，职位 |
| 内容与互动 | 帖子，评论 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
