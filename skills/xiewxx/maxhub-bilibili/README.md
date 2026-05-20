# Bilibili Data Assistant

[中文文档](README_CN.md)

Bilibili video, user, comment, danmaku, and live data assistant with App and Web API support.

## Features

- **Video Data** — fetch_one_video, fetch_video_detail, fetch_video_playurl, fetch_video_comments, fetch_video_danmaku, fetch_video_subtitle, fetch_video_play_info, generate_aid_by_bvid, fetch_video_parts_by_bvid, fetch_vip_video_playurl
- **User Data** — fetch_user_info, fetch_user_profile, fetch_user_videos, fetch_user_followers, fetch_user_following, fetch_up_stat, fetch_user_relation_stat, extract_user_id, fetch_user_dynamic, fetch_user_collection_folders, fetch_collection_folder_data
- **Search** — fetch_general_search, fetch_hot_search, search_by_type
- **Comments & Interaction** — fetch_video_comments, fetch_comment_replies, fetch_dynamic_detail, fetch_dynamic_detail_v2
- **Live & Feed** — fetch_live_info, fetch_live_areas, fetch_live_streamers, fetch_live_video_data, fetch_home_feed, fetch_popular_feed, fetch_bangumi_tab, fetch_cinema_tab, fetch_comprehensive_popular

## Install

```bash
npx clawhub install maxhub-bilibili
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-bilibili.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Video Data | 视频, 详情 |
| User Data | 用户, UP主 |
| Search | 搜索, 搜 |
| Comments & Interaction | 评论, 回复 |
| Live & Feed | 直播, 推荐 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
