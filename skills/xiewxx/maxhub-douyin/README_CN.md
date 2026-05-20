# 抖音数据助手

[English](README.md)

抖音全场景数据查询助手。覆盖视频详情、用户数据、搜索、热榜、创作者工具、星图达人、内容指数等7大模块。

## 功能

- **视频与内容** — fetch_one_video, fetch_one_video_v2, fetch_video_comments, fetch_video_comment_replies, fetch_user_post_videos, fetch_user_like_videos, fetch_video_danmaku, fetch_related_videos, batch_fetch_video_info
- **用户数据** — fetch_user_info, fetch_user_followers, fetch_user_following, fetch_user_profile, batch_fetch_user_info
- **搜索** — fetch_general_search_v2, fetch_video_search, fetch_user_search, fetch_hashtag_search, fetch_music_search, fetch_live_search, fetch_keyword_suggestions
- **热榜与趋势** — fetch_hot_search, fetch_hot_total_list, fetch_video_hot_list, fetch_topic_hot_list, fetch_rising_hot_list, fetch_city_hot_list, fetch_hot_list_category
- **创作者工具** — fetch_creator_hotspot, fetch_item_list, fetch_item_overview, fetch_item_audience, fetch_author_diagnosis, fetch_live_history, fetch_item_analysis_overview
- **星图达人** — search_kol, fetch_kol_base_info, fetch_kol_data_overview, fetch_kol_service_price, fetch_kol_fans_portrait, fetch_kol_audience_portrait, fetch_kol_video_performance, fetch_kol_xingtu_index
- **内容指数** — fetch_brand_index, fetch_hot_words, fetch_keyword_trend, fetch_daren_metrics, fetch_daren_fans, fetch_content_trend, fetch_search_trend, fetch_brand_trend_lines

## 安装

```bash
npx clawhub install maxhub-douyin
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-douyin.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 视频与内容 | 视频，作品 |
| 用户数据 | 用户，达人 |
| 搜索 | 搜索，搜 |
| 热榜与趋势 | 热榜，热搜 |
| 创作者工具 | 创作者，投稿 |
| 星图达人 | 星图，KOL |
| 内容指数 | 指数，品牌 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
