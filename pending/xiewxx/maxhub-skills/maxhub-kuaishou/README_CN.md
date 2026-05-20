# 快手数据助手

[English](README.md)

快手全场景数据查询助手。支持App和Web双端API，覆盖视频详情、用户数据、搜索、热榜、直播、评论等全功能。

## 功能

- **视频数据** — fetch_one_video, fetch_one_video_v2, fetch_video_comments, fetch_video_sub_comments, fetch_user_videos, fetch_user_hot_posts, fetch_video_by_url
- **用户数据** — fetch_user_info, fetch_user_id, search_user, fetch_user_collect, fetch_user_live_info
- **搜索与热榜** — comprehensive_search, search_video, fetch_hot_list, fetch_hot_categories, fetch_brand_top_list, fetch_live_top_list, fetch_shopping_top_list
- **直播与工具** — fetch_user_live_replay, generate_share_link, generate_share_short_url

## 安装

```bash
npx clawhub install maxhub-kuaishou
```

## 配置

1. 前往 [www.aconfig.cn](https://www.aconfig.cn) 注册并获取 API Key
2. 配置：`openclaw config set skills.entries.maxhub-kuaishou.apiKey "<你的-key>"` 或 `export MAXHUB_API_KEY="<你的-key>"`

## 使用示例

| 分类 | 示例指令 |
|------|----------|
| 视频数据 | 视频，作品 |
| 用户数据 | 用户，资料 |
| 搜索与热榜 | 搜索，热榜 |
| 直播与工具 | 直播，分享 |

支持 **中文** 和 **英文** 双语。

## 链接

- 官网：[www.aconfig.cn](https://www.aconfig.cn)

---

由 [MaxHub](https://www.aconfig.cn) 提供技术支持
