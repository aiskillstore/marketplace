# YouTube Data Assistant

[中文文档](README_CN.md)

YouTube data assistant with Web/V2 APIs for video, channel, search, comments, subtitles, and Shorts.

## Features

- **Video Data** — fetch_video_info, fetch_video_info_v2, fetch_video_info_v3, fetch_video_streams, fetch_video_streams_v2, fetch_video_subtitles, fetch_video_captions, fetch_related_videos, fetch_trending_videos
- **Channel Data** — fetch_channel_info, fetch_channel_description, fetch_channel_videos, fetch_channel_videos_v2, fetch_channel_videos_v3, fetch_channel_shorts, fetch_channel_community_posts, get_channel_id, get_channel_id_from_url
- **Search** — general_search, general_search_v2, search_video, search_channel, shorts_search, shorts_search_v2, fetch_search_suggestions
- **Comments** — fetch_video_comments, fetch_video_sub_comments, fetch_post_comments, fetch_post_comment_replies

## Install

```bash
npx clawhub install maxhub-youtube
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-youtube.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| Video Data | 视频, 详情 |
| Channel Data | 频道, 信息 |
| Search | 搜索, 搜 |
| Comments | 评论, 回复 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
