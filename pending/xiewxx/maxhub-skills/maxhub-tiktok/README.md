# TikTok Data Assistant

[中文文档](README_CN.md)

TikTok comprehensive data assistant covering video, user, search, ads, creator, shop, and interaction with App and Web API support.

## Features

- **Video & Content** — fetch_one_video, fetch_one_video_v2, fetch_one_video_v3, fetch_video_comments, fetch_video_comment_replies, fetch_user_posts, fetch_user_likes, fetch_user_reposts, fetch_user_favorites, fetch_explore_videos, fetch_daily_trending, fetch_home_feed, batch_fetch_video_info
- **User Data** — fetch_user_info, fetch_user_profile, fetch_user_followers, fetch_user_following, fetch_user_live_details, get_user_id_by_username, fetch_similar_users
- **Search** — fetch_general_search, search_video, search_user, search_live, search_keyword_suggest, fetch_trending_search_words
- **Ads & Analytics** — search_ads, search_creators, fetch_ad_detail, fetch_ad_analysis, fetch_product_detail, fetch_product_metrics, fetch_keyword_insights, fetch_popular_hashtags, fetch_popular_sounds, fetch_creator_analytics, detect_fake_views, fetch_comment_keywords
- **Creator & Shop** — fetch_creator_account_info, fetch_creator_video_overview, fetch_showcase_products, fetch_shop_info, fetch_shop_products, fetch_product_detail, fetch_product_reviews, search_products, fetch_live_room_data, fetch_live_products
- **Interaction** — like, follow, post_comment, reply_comment, collect, forward
- **Crypto & Tools** — generate_xbogus, generate_ttwid, generate_msToken, generate_web_id, register_device, encrypt_strdata, decrypt_strdata, fetch_guest_cookie

## Install

```bash
npx clawhub install maxhub-tiktok
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-tiktok.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Video & Content | 视频, 作品 |
| User Data | 用户, 达人 |
| Search | 搜索, 搜 |
| Ads & Analytics | 广告, 分析 |
| Creator & Shop | 创作者, 电商 |
| Interaction | 点赞, 关注 |
| Crypto & Tools | 签名, 加密 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
