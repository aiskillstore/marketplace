# LinkedIn Data Assistant

[中文文档](README_CN.md)

LinkedIn professional data assistant covering user profiles, companies, jobs, posts, comments, and ads with V1/V2 API support.

## Features

- **User Profile** — get_user_profile, fetch_user_experience, fetch_user_skills, fetch_user_educations, fetch_user_publications, fetch_user_certifications, fetch_user_recommendations, fetch_user_honors, fetch_user_volunteers, fetch_user_bio, fetch_user_contact_info, fetch_user_follower_count, fetch_user_profile_top_card
- **Company Data** — fetch_company_profile, fetch_company_people, fetch_company_posts, fetch_company_jobs, fetch_company_job_count, fetch_company_affiliated_pages, fetch_company_competitors, fetch_company_locations, fetch_company_cta_buttons, fetch_stock_quote
- **Search & Jobs** — search_people, search_users, search_jobs, search_posts, search_ads, fetch_job_detail
- **Content & Interaction** — fetch_post_detail, fetch_post_comments, fetch_post_reactions, fetch_post_reposts, fetch_user_posts, fetch_user_comments, fetch_user_reactions, fetch_hashtag_feed, fetch_comment_replies

## Install

```bash
npx clawhub install maxhub-linkedin
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-linkedin.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| User Profile | 用户, 资料 |
| Company Data | 公司, 企业 |
| Search & Jobs | 搜索, 职位 |
| Content & Interaction | 帖子, 评论 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
