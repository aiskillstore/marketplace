# YouTube 数据助手

[English](README.md)

YouTube 全场景数据查询助手。支持Web/V2双版本API，覆盖视频详情、频道数据、搜索、评论、字幕、Shorts等全功能。

## 功能

- **视频数据** — fetch_video_info, fetch_video_info_v2, fetch_video_info_v3, fetch_video_streams, fetch_video_streams_v2, fetch_video_subtitles, fetch_video_captions, fetch_related_videos, fetch_trending_videos
- **频道数据** — fetch_channel_info, fetch_channel_description, fetch_channel_videos, fetch_channel_videos_v2, fetch_channel_videos_v3, fetch_channel_shorts, fetch_channel_community_posts, get_channel_id, get_channel_id_from_url
- **搜索** — general_search, general_search_v2, search_video, search_channel, shorts_search, shorts_search_v2, fetch_search_suggestions
- **评论** — fetch_video_comments, fetch_video_sub_comments, fetch_post_comments, fetch_post_comment_replies

## 安装

```bash
npx clawhub install maxhub-youtube
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-youtube.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 视频数据 | 视频，详情 |
| 频道数据 | 频道，信息 |
| 搜索 | 搜索，搜 |
| 评论 | 评论，回复 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
