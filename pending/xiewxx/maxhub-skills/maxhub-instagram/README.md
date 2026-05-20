# Instagram Data Assistant

[中文文档](README_CN.md)

Instagram data assistant supporting V1/V2/V3 APIs for user info, posts, Reels, Stories, comments, search, hashtags, and locations.

## Features

- **User Data** — fetch_user_info, fetch_user_posts, fetch_user_followers, fetch_user_following, fetch_user_stories, fetch_user_reels, fetch_user_highlights, fetch_user_tagged_posts, fetch_user_about, fetch_user_brief_info, fetch_user_former_usernames
- **Post & Media** — fetch_post_info, fetch_post_comments, fetch_comment_replies, fetch_post_likes, fetch_highlight_stories, fetch_post_oembed
- **Search & Explore** — search_users, search_hashtags, search_locations, general_search, fetch_explore_feed, fetch_hashtag_posts, fetch_location_posts, fetch_location_info, fetch_nearby_content
- **Content Tools** — convert_media_id_shortcode, extract_shortcode, translate_comment, bulk_translate_comments, fetch_reels_feed, fetch_user_id_by_username

## Install

```bash
npx clawhub install maxhub-instagram
```

## Setup

1. Go to [www.aconfig.cn](https://www.aconfig.cn) to register and get your API Key
2. Configure: `openclaw config set skills.entries.maxhub-instagram.apiKey "<your-key>"` or `export MAXHUB_API_KEY="<your-key>"`

## Usage Examples

| Category | Example prompts |
|----------|----------------|
| User Data | 用户, 资料 |
| Post & Media | 帖子, 帖文 |
| Search & Explore | 搜索, 搜 |
| Content Tools | 翻译, 短码 |

Supports both **English** and **Chinese**.

## Links

- Website: [www.aconfig.cn](https://www.aconfig.cn)

---

Powered by [MaxHub](https://www.aconfig.cn)
