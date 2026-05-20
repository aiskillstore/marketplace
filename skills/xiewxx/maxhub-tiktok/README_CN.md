# TikTok 数据助手

[English](README.md)

TikTok 全场景数据查询助手。覆盖视频详情、用户数据、搜索、广告、创作者工具、电商、互动等7大模块，支持App和Web双端API。

## 功能

- **视频与内容** — fetch_one_video, fetch_one_video_v2, fetch_one_video_v3, fetch_video_comments, fetch_video_comment_replies, fetch_user_posts, fetch_user_likes, fetch_user_reposts, fetch_user_favorites, fetch_explore_videos, fetch_daily_trending, fetch_home_feed, batch_fetch_video_info
- **用户数据** — fetch_user_info, fetch_user_profile, fetch_user_followers, fetch_user_following, fetch_user_live_details, get_user_id_by_username, fetch_similar_users
- **搜索** — fetch_general_search, search_video, search_user, search_live, search_keyword_suggest, fetch_trending_search_words
- **广告与分析** — search_ads, search_creators, fetch_ad_detail, fetch_ad_analysis, fetch_product_detail, fetch_product_metrics, fetch_keyword_insights, fetch_popular_hashtags, fetch_popular_sounds, fetch_creator_analytics, detect_fake_views, fetch_comment_keywords
- **创作者与电商** — fetch_creator_account_info, fetch_creator_video_overview, fetch_showcase_products, fetch_shop_info, fetch_shop_products, fetch_product_detail, fetch_product_reviews, search_products, fetch_live_room_data, fetch_live_products
- **互动操作** — like, follow, post_comment, reply_comment, collect, forward
- **签名与工具** — generate_xbogus, generate_ttwid, generate_msToken, generate_web_id, register_device, encrypt_strdata, decrypt_strdata, fetch_guest_cookie

## 安装

```bash
npx clawhub install maxhub-tiktok
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-tiktok.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 视频与内容 | 视频，作品 |
| 用户数据 | 用户，达人 |
| 搜索 | 搜索，搜 |
| 广告与分析 | 广告，分析 |
| 创作者与电商 | 创作者，电商 |
| 互动操作 | 点赞，关注 |
| 签名与工具 | 签名，加密 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
