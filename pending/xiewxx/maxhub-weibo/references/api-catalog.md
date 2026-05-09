# 微博（Weibo）API完整目录

> 共 64 个API，按能力域分类

## 数据采集（31个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取频道配置列表/Get channel config list | GET | `/api/v1/weibo/web/fetch_config_list` | - |
| 2 | 根据频道名称获取热门内容/Get channel feed by name | GET | `/api/v1/weibo/web/fetch_channel_feed` | - |
| 3 | 获取用户信息/Get user information | GET | `/api/v1/weibo/web/fetch_user_info` | uid |
| 4 | 获取用户微博列表/Get user posts | GET | `/api/v1/weibo/web/fetch_user_posts` | uid |
| 5 | 获取微博详情/Get post detail | GET | `/api/v1/weibo/web/fetch_post_detail` | post_id |
| 6 | 获取单个作品数据/Get single post data | GET | `/api/v1/weibo/web_v2/fetch_post_detail` | id |
| 7 | 获取用户信息/Get user information | GET | `/api/v1/weibo/web_v2/fetch_user_info` | - |
| 8 | 获取用户基本信息/Get user basic information | GET | `/api/v1/weibo/web_v2/fetch_user_basic_info` | uid |
| 9 | 获取微博用户文章数据/Get Weibo user posts | GET | `/api/v1/weibo/web_v2/fetch_user_posts` | uid |
| 10 | 获取微博用户原创微博数据/Get Weibo user original pos | GET | `/api/v1/weibo/web_v2/fetch_user_original_posts` | uid |
| 11 | 获取用户微博视频收藏夹列表/Get user video collection  | GET | `/api/v1/weibo/web_v2/fetch_user_video_collection_list` | uid |
| 12 | 获取用户微博视频收藏夹详情/Get user video collection  | GET | `/api/v1/weibo/web_v2/fetch_user_video_collection_detail` | cid |
| 13 | 获取微博用户全部视频/Get user all videos | GET | `/api/v1/weibo/web_v2/fetch_user_video_list` | uid |
| 14 | 获取用户粉丝列表/Get user fans list | GET | `/api/v1/weibo/web_v2/fetch_user_fans` | uid |
| 15 | 获取所有分组信息/Get all groups information | GET | `/api/v1/weibo/web_v2/fetch_all_groups` | - |
| 16 | 获取微博主页推荐时间轴/Get user recommend timeline | GET | `/api/v1/weibo/web_v2/fetch_user_recommend_timeline` | - |
| 17 | 地区省市映射/Region City List | GET | `/api/v1/weibo/web_v2/fetch_city_list` | - |
| 18 | 获取用户信息/Get user information | GET | `/api/v1/weibo/app/fetch_user_info` | uid |
| 19 | 获取用户详细信息/Get user detail information | GET | `/api/v1/weibo/app/fetch_user_info_detail` | uid |
| 20 | 获取用户发布的微博/Get user timeline | GET | `/api/v1/weibo/app/fetch_user_timeline` | uid |
| 21 | 获取用户视频列表/Get user videos | GET | `/api/v1/weibo/app/fetch_user_videos` | uid |
| 22 | 获取用户参与的超话列表/Get user super topics | GET | `/api/v1/weibo/app/fetch_user_super_topics` | uid |
| 23 | 获取用户相册/Get user album | GET | `/api/v1/weibo/app/fetch_user_album` | uid |
| 24 | 获取用户文章列表/Get user articles | GET | `/api/v1/weibo/app/fetch_user_articles` | uid |
| 25 | 获取用户音频列表/Get user audios | GET | `/api/v1/weibo/app/fetch_user_audios` | uid |
| 26 | 获取用户主页动态/Get user profile feed | GET | `/api/v1/weibo/app/fetch_user_profile_feed` | uid |
| 27 | 获取微博详情/Get post detail | GET | `/api/v1/weibo/app/fetch_status_detail` | status_id |
| 28 | 获取微博转发列表/Get post reposts | GET | `/api/v1/weibo/app/fetch_status_reposts` | status_id |
| 29 | 获取视频详情/Get video detail | GET | `/api/v1/weibo/app/fetch_video_detail` | mid |
| 30 | 获取短视频精选Feed流/Get video featured feed | GET | `/api/v1/weibo/app/fetch_video_featured_feed` | - |
| 31 | 获取首页推荐Feed流/Get home recommend feed | GET | `/api/v1/weibo/app/fetch_home_recommend_feed` | - |

## 数据分析（5个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取频道热门趋势/Get channel trend top | GET | `/api/v1/weibo/web/fetch_trend_top` | containerid |
| 2 | 获取微博热门榜单时间轴/Get hot ranking timeline | GET | `/api/v1/weibo/web_v2/fetch_hot_ranking_timeline` | ranking_type |
| 3 | 获取微博文娱榜单/Get Weibo entertainment ranking | GET | `/api/v1/weibo/web_v2/fetch_entertainment_ranking` | - |
| 4 | 获取微博生活榜单/Get Weibo life ranking | GET | `/api/v1/weibo/web_v2/fetch_life_ranking` | - |
| 5 | 获取微博社会榜单/Get Weibo social ranking | GET | `/api/v1/weibo/web_v2/fetch_social_ranking` | - |

## 互动操作（8个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取微博评论/Get post comments | GET | `/api/v1/weibo/web/fetch_post_comments` | post_id, mid |
| 2 | 获取评论子评论/Get comment replies | GET | `/api/v1/weibo/web/fetch_comment_replies` | cid |
| 3 | 检查微博是否允许带图评论/Check if Weibo allows image | GET | `/api/v1/weibo/web_v2/check_allow_comment_with_pic` | id |
| 4 | 获取微博评论/Get Weibo comments | GET | `/api/v1/weibo/web_v2/fetch_post_comments` | id |
| 5 | 获取微博子评论/Get Weibo sub-comments | GET | `/api/v1/weibo/web_v2/fetch_post_sub_comments` | id |
| 6 | 获取用户关注列表/Get user following list | GET | `/api/v1/weibo/web_v2/fetch_user_following` | uid |
| 7 | 获取微博评论/Get post comments | GET | `/api/v1/weibo/app/fetch_status_comments` | status_id |
| 8 | 获取微博点赞列表/Get post likes | GET | `/api/v1/weibo/app/fetch_status_likes` | status_id |

## 搜索查询（20个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索微博/Search Weibo | GET | `/api/v1/weibo/web/fetch_search` | keyword |
| 2 | 获取热搜榜/Get hot search ranking | GET | `/api/v1/weibo/web/fetch_hot_search` | - |
| 3 | 获取搜索页热搜词/Get search page hot topics | GET | `/api/v1/weibo/web/fetch_search_topics` | - |
| 4 | 搜索用户微博/Search user posts | GET | `/api/v1/weibo/web_v2/search_user_posts` | uid |
| 5 | 获取微博热搜词条(10条)/Get Weibo hot search index | GET | `/api/v1/weibo/web_v2/fetch_hot_search_index` | - |
| 6 | 获取微博完整热搜榜单(50条)/Get Weibo complete hot s | GET | `/api/v1/weibo/web_v2/fetch_hot_search_summary` | - |
| 7 | 获取微博热搜榜单/Get Weibo hot search ranking | GET | `/api/v1/weibo/web_v2/fetch_hot_search` | - |
| 8 | 获取微博相似搜索词推荐/Get Weibo similar search rec | GET | `/api/v1/weibo/web_v2/fetch_similar_search` | keyword |
| 9 | 微博智能搜索/Weibo AI Search | GET | `/api/v1/weibo/web_v2/fetch_ai_search` | query |
| 10 | 微博AI搜索内容扩展/Weibo AI Search Content Exten | GET | `/api/v1/weibo/web_v2/fetch_ai_related_search` | keyword |
| 11 | 微博高级搜索/Weibo Advanced Search | GET | `/api/v1/weibo/web_v2/fetch_advanced_search` | q |
| 12 | 实时搜索/Weibo Realtime Search | GET | `/api/v1/weibo/web_v2/fetch_realtime_search` | query |
| 13 | 用户搜索/User search | GET | `/api/v1/weibo/web_v2/fetch_user_search` | - |
| 14 | 视频搜索（热门/全部）/Weibo video search (hot/all) | GET | `/api/v1/weibo/web_v2/fetch_video_search` | query |
| 15 | 图片搜索/Weibo picture search | GET | `/api/v1/weibo/web_v2/fetch_pic_search` | query |
| 16 | 话题搜索/Weibo topic search | GET | `/api/v1/weibo/web_v2/fetch_topic_search` | query |
| 17 | 综合搜索/Comprehensive search | GET | `/api/v1/weibo/app/fetch_search_all` | query |
| 18 | AI智搜/AI Smart Search | GET | `/api/v1/weibo/app/fetch_ai_smart_search` | query |
| 19 | 获取热搜榜/Get hot search | GET | `/api/v1/weibo/app/fetch_hot_search` | - |
| 20 | 获取热搜分类列表/Get hot search categories | GET | `/api/v1/weibo/app/fetch_hot_search_categories` | - |

