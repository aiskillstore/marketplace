# Bilibili 数据助手

[English](README.md)

B站视频、用户、评论、弹幕、直播数据查询助手。支持App和Web双端API。

## 功能

- **视频数据** — fetch_one_video, fetch_video_detail, fetch_video_playurl, fetch_video_comments, fetch_video_danmaku, fetch_video_subtitle, fetch_video_play_info, generate_aid_by_bvid, fetch_video_parts_by_bvid, fetch_vip_video_playurl
- **用户数据** — fetch_user_info, fetch_user_profile, fetch_user_videos, fetch_user_followers, fetch_user_following, fetch_up_stat, fetch_user_relation_stat, extract_user_id, fetch_user_dynamic, fetch_user_collection_folders, fetch_collection_folder_data
- **搜索** — fetch_general_search, fetch_hot_search, search_by_type
- **评论互动** — fetch_video_comments, fetch_comment_replies, fetch_dynamic_detail, fetch_dynamic_detail_v2
- **直播与推荐** — fetch_live_info, fetch_live_areas, fetch_live_streamers, fetch_live_video_data, fetch_home_feed, fetch_popular_feed, fetch_bangumi_tab, fetch_cinema_tab, fetch_comprehensive_popular

## 安装

```bash
npx clawhub install maxhub-bilibili
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-bilibili.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 视频数据 | 视频，详情 |
| 用户数据 | 用户，UP主 |
| 搜索 | 搜索，搜 |
| 评论互动 | 评论，回复 |
| 直播与推荐 | 直播，推荐 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
