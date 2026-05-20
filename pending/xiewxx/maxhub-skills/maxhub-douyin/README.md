# Douyin Data Assistant

[中文文档](README_CN.md)

Comprehensive Douyin data assistant covering video, user, search, trending, creator, Xingtu KOL, and content index.

## Features

- **Video & Content** — fetch_one_video, fetch_one_video_v2, fetch_video_comments, fetch_video_comment_replies, fetch_user_post_videos, fetch_user_like_videos, fetch_video_danmaku, fetch_related_videos, batch_fetch_video_info
- **User Data** — fetch_user_info, fetch_user_followers, fetch_user_following, fetch_user_profile, batch_fetch_user_info
- **Search** — fetch_general_search_v2, fetch_video_search, fetch_user_search, fetch_hashtag_search, fetch_music_search, fetch_live_search, fetch_keyword_suggestions
- **Trending & Billboard** — fetch_hot_search, fetch_hot_total_list, fetch_video_hot_list, fetch_topic_hot_list, fetch_rising_hot_list, fetch_city_hot_list, fetch_hot_list_category
- **Creator Tools** — fetch_creator_hotspot, fetch_item_list, fetch_item_overview, fetch_item_audience, fetch_author_diagnosis, fetch_live_history, fetch_item_analysis_overview
- **Xingtu KOL** — search_kol, fetch_kol_base_info, fetch_kol_data_overview, fetch_kol_service_price, fetch_kol_fans_portrait, fetch_kol_audience_portrait, fetch_kol_video_performance, fetch_kol_xingtu_index
- **Content Index** — fetch_brand_index, fetch_hot_words, fetch_keyword_trend, fetch_daren_metrics, fetch_daren_fans, fetch_content_trend, fetch_search_trend, fetch_brand_trend_lines

## Install

```bash
npx clawhub install maxhub-douyin
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-douyin.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Video & Content | 视频, 作品 |
| User Data | 用户, 达人 |
| Search | 搜索, 搜 |
| Trending & Billboard | 热榜, 热搜 |
| Creator Tools | 创作者, 投稿 |
| Xingtu KOL | 星图, KOL |
| Content Index | 指数, 品牌 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
