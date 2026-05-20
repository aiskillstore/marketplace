# Weibo Data Assistant

[中文文档](README_CN.md)

Comprehensive Weibo data assistant integrating App/Web/V2 APIs for posts, users, AI search, advanced search, trending, comments, and videos.

## Features

- **Post & Comment** — fetch_post_detail, fetch_post_comments, fetch_post_reposts, fetch_post_likes, fetch_sub_comments, fetch_single_post_data, fetch_comments
- **User Data** — fetch_user_info, fetch_user_detail, fetch_user_basic_info, fetch_user_timeline, fetch_user_original_posts, fetch_user_articles, fetch_user_videos, fetch_user_all_videos, fetch_user_following, fetch_user_followers, fetch_user_super_topics, user_search
- **Search** — comprehensive_search, search_weibo, ai_search, ai_search_extension, advanced_search, realtime_search, picture_search, video_search, topic_search, search_user_posts, user_search, fetch_similar_search, fetch_search_suggestions
- **Trending & Hot** — fetch_hot_search, fetch_hot_search_ranking, fetch_hot_search_complete, fetch_entertainment_ranking, fetch_social_ranking, fetch_life_ranking, fetch_hot_ranking_timeline
- **Video & Feed** — fetch_video_detail, fetch_video_featured_feed, fetch_home_recommend_feed, fetch_channel_feed, fetch_channel_trend, fetch_channel_config, fetch_video_collection_list, fetch_video_collection_detail, fetch_all_groups, check_image_comment_allowed

## Install

```bash
npx clawhub install maxhub-weibo
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-weibo.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Post & Comment | 微博详情, 评论, 转发 |
| User Data | 用户信息, 粉丝, 关注 |
| Search | AI搜索, 高级搜索, 图片搜索 |
| Trending | 热搜榜, 文娱榜, 社会榜 |
| Video & Feed | 视频详情, 频道, 推荐 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
