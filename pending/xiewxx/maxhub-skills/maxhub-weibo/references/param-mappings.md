# Parameter Mappings / 参数映射

Platform: `weibo` | Base URL: `https://www.aconfig.cn`

---

## check_allow_comment_with_pic

- `id` (string, required): 微博ID/Weibo ID — e.g. `5092682368025584`

## fetch_advanced_search

- `q` (string, required): 搜索关键词/Search keyword — e.g. `yu7`
- `search_type` (string, optional): >- — e.g. `hot`
- `include_type` (string, optional): >- — e.g. `pic`
- `timescope` (string, optional): 时间范围/Time scope (custom:start:end) — e.g. `custom:2025-09-01-0:2025-09-08-23`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_ai_related_search

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `#微博奇遇记#`

## fetch_ai_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `#法国#`

## fetch_ai_smart_search

- `query` (string, required): 搜索关键词 — e.g. `人工智能`
- `page` (integer, optional): 页码 — e.g. `1`

## fetch_channel_feed

- `channel_name` (string, optional): 频道名称，不传则使用默认频道/Channel name, use default if not provided — e.g. `热门`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_city_list

- `normalized` (boolean, optional): 是否返回标准化结构（省份列表+城市数组）/Whether to return normalized structure

## fetch_comment_replies

- `cid` (string, required): 根评论ID/Root comment ID — e.g. `5100663573318494`
- `max_id` (string, optional): 翻页ID，默认0为第一页/Pagination ID, default 0 for first page — e.g. `0`

## fetch_home_recommend_feed

- `page` (string, optional): 页码，首页不传，第二页传2
- `count` (integer, optional): 每页数量 — e.g. `15`

## fetch_hot_ranking_timeline

- `ranking_type` (string, required): >- — e.g. `hour`
- `since_id` (string, optional): 分页标识，默认为0/Pagination identifier, default is 0 — e.g. `0`
- `max_id` (string, optional): 最大ID，默认为0/Max ID, default is 0 — e.g. `0`
- `count` (integer, optional): 获取数量，默认10/Count, default is 10 — e.g. `10`

## fetch_hot_search

- `category` (string, optional): >- — e.g. `realtimehot`
- `page` (integer, optional): 页码 — e.g. `1`
- `count` (integer, optional): 每页数量 — e.g. `20`
- `region_name` (string, optional): >- — e.g. `北京`

## fetch_pic_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `yu7`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_post_comments

- `post_id` (string, required): 微博ID/Post ID — e.g. `5100663548412324`
- `mid` (string, required): 微博MID/Post MID — e.g. `5100663548412324`
- `max_id` (string, optional): 翻页ID/Pagination ID
- `max_id_type` (integer, optional): 翻页ID类型/Pagination ID type — e.g. `0`

## fetch_post_comments

- `id` (string, required): 微博ID/Weibo ID — e.g. `5283919831764022`
- `count` (integer, optional): 评论数量/Number of comments — e.g. `10`
- `max_id` (string, optional): 页码/Page number

## fetch_post_detail

- `post_id` (string, required): 微博ID/Post ID — e.g. `5092682368025584`

## fetch_post_detail

- `id` (string, required): 作品id/Post id — e.g. `5092682368025584`
- `is_get_long_text` (string, optional): >- — e.g. `true`

## fetch_post_sub_comments

- `id` (string, required): 主评论ID/Comment ID — e.g. `5283574244704555`
- `count` (integer, optional): 子评论数量/Number of sub-comments — e.g. `10`
- `max_id` (string, optional): 分页标识/Page identifier

## fetch_realtime_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `yu7`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_search

- `keyword` (string, required): '搜索关键词，支持话题搜索如 #话题名#/Search keyword, supports hashtag like #topic#' — e.g. `游戏`
- `page` (integer, optional): >- — e.g. `1`
- `search_type` (string, optional): '搜索类型/Search type: 1=综合, 61=实时, 3=用户, 60=热门, 64=视频, 63=图片, 21=文章' — e.g. `1`
- `time_scope` (string, optional): '时间范围/Time scope: hour=一小时内, day=一天内, week=一周内, month=一个月内, null=不限'

## fetch_search_all

- `query` (string, required): 搜索关键词 — e.g. `NVIDIA`
- `page` (integer, optional): 页码 — e.g. `1`
- `search_type` (integer, optional): >- — e.g. `1`

## fetch_similar_search

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `#微博奇遇记#`

## fetch_status_comments

- `status_id` (string, required): 微博ID — e.g. `5258708168476831`
- `max_id` (string, optional): 翻页游标
- `sort_type` (string, optional): '排序类型: 0=按热度排序, 1=按时间排序' — e.g. `0`

## fetch_status_detail

- `status_id` (string, required): 微博ID — e.g. `5016922058656962`

## fetch_status_likes

- `status_id` (string, required): 微博ID — e.g. `5016922058656962`
- `attitude_type` (string, optional): '点赞类型: 0=全部, 1=点赞, 2=开心, 3=惊讶, 4=伤心, 5=愤怒, 6=打赏, 8=抱抱' — e.g. `0`

## fetch_status_reposts

- `status_id` (string, required): 微博ID — e.g. `5016922058656962`
- `max_id` (string, optional): 翻页游标

## fetch_topic_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `yu7`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_trend_top

- `containerid` (string, required): 频道容器ID/Channel container ID — e.g. `102803_ctg1_8999_-_ctg1_8999_home`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## fetch_user_album

- `uid` (string, required): 用户ID — e.g. `7648703289`
- `since_id` (string, optional): 翻页游标

## fetch_user_articles

- `uid` (string, required): 用户ID — e.g. `1725941200`
- `since_id` (string, optional): 翻页游标

## fetch_user_audios

- `uid` (string, required): 用户ID — e.g. `1725941200`
- `since_id` (string, optional): 翻页游标

## fetch_user_basic_info

- `uid` (string, required): 用户id/User id — e.g. `7277477906`

## fetch_user_fans

- `uid` (string, required): 用户ID/User ID — e.g. `1722594714`
- `page` (integer, optional): 页码/Page number — e.g. `0`

## fetch_user_following

- `uid` (string, required): 用户ID/User ID — e.g. `1722594714`
- `page` (integer, optional): 页码/Page number — e.g. `0`

## fetch_user_info

- `uid` (string, required): 用户ID — e.g. `7648703289`

## fetch_user_info

- `uid` (string, required): 用户ID/User ID — e.g. `2992978081`

## fetch_user_info

- `uid` (string, optional): 用户id/User id — e.g. `1722594714`
- `custom` (string, optional): 自定义微博用户名/Custom Weibo username — e.g. `shuqi`

## fetch_user_info_detail

- `uid` (string, required): 用户ID — e.g. `7648703289`

## fetch_user_original_posts

- `uid` (string, required): 用户id/User id — e.g. `7277477906`
- `page` (integer, optional): 页数/Page number — e.g. `1`
- `since_id` (string, optional): 翻页标识，用于获取下一页数据/Pagination identifier for getting next page data

## fetch_user_posts

- `uid` (string, required): 用户ID/User ID — e.g. `7277477906`
- `page` (integer, optional): 页码/Page number — e.g. `1`
- `since_id` (string, optional): 翻页ID，从上一页结果获取/Pagination ID from previous page

## fetch_user_posts

- `uid` (string, required): 用户id/User id — e.g. `7277477906`
- `page` (integer, optional): 页数/Page number — e.g. `1`
- `feature` (integer, optional): >- — e.g. `0`
- `since_id` (string, optional): 翻页标识，用于获取下一页数据/Pagination identifier for getting next page data

## fetch_user_profile_feed

- `uid` (string, required): 用户ID — e.g. `6580994757`
- `since_id` (string, optional): 翻页游标

## fetch_user_recommend_timeline

- `refresh` (integer, optional): 刷新类型，0=正常刷新，1=强制刷新/Refresh type, 0=normal refresh, 1=force refresh — e.g. `0`
- `group_id` (string, optional): 分组ID/Group ID — e.g. `102803`
- `containerid` (string, optional): 容器ID/Container ID — e.g. `102803`
- `extparam` (string, optional): 扩展参数/Extended parameters — e.g. `discover|new_feed`
- `max_id` (string, optional): 最大ID/Max ID — e.g. `0`
- `count` (integer, optional): 获取数量/Count — e.g. `10`

## fetch_user_search

- `query` (string, optional): 搜索关键词/Query（提供则视为“全部”搜索；留空则仅应用高级筛选参数） — e.g. `yu7`
- `page` (integer, optional): 页码/Page — e.g. `1`
- `region` (string, optional): 地区编码，从 /city_list 获取/Region code from /city_list — e.g. `custom:11:1`
- `auth` (string, optional): 认证类型 org_vip(机构)/per_vip(个人)/ord(普通)/Auth type — e.g. `org_vip`
- `gender` (string, optional): 性别 man / women / Gender — e.g. `man`
- `age` (string, optional): 年龄段 18y/22y/29y/39y/40y / Age bucket — e.g. `22y`
- `nickname` (string, optional): 昵称筛选/Nickname filter — e.g. `张三`
- `tag` (string, optional): 标签筛选/Tag filter — e.g. `摄影`
- `school` (string, optional): 学校筛选/School filter — e.g. `清华大学`
- `work` (string, optional): 公司筛选/Company filter — e.g. `字节跳动`

## fetch_user_super_topics

- `uid` (string, required): 用户ID — e.g. `7648703289`
- `page` (integer, optional): 页码 — e.g. `1`

## fetch_user_timeline

- `uid` (string, required): 用户ID — e.g. `7648703289`
- `page` (integer, optional): 页码 — e.g. `1`
- `filter_type` (string, optional): 筛选类型 — e.g. `all`
- `month` (string, optional): 时间筛选(YYYYMMDD格式) — e.g. `20251010`

## fetch_user_video_collection_detail

- `cid` (string, required): 收藏夹ID/Collection ID — e.g. `4883992307236954`
- `cursor` (string, optional): 分页游标/Pagination cursor
- `tab_code` (integer, optional): '排序方式：0=默认，1=最热，2=最新/Sort type: 0=default, 1=hottest, 2=latest' — e.g. `0`

## fetch_user_video_collection_list

- `uid` (string, required): 用户ID/User ID — e.g. `7277477906`

## fetch_user_video_list

- `uid` (string, required): 用户ID/User ID — e.g. `7277477906`
- `cursor` (string, optional): 分页游标/Pagination cursor — e.g. `0`

## fetch_user_videos

- `uid` (string, required): 用户ID — e.g. `7648703289`
- `since_id` (string, optional): 翻页游标

## fetch_video_detail

- `mid` (string, required): 视频微博ID — e.g. `5242977759006596`

## fetch_video_featured_feed

- `page` (string, optional): 页码，首页不传，第二页传2

## fetch_video_search

- `query` (string, required): 搜索关键词/Search keyword — e.g. `yu7`
- `mode` (string, optional): 搜索模式：hot=热门 / all=全部 — e.g. `hot`
- `page` (integer, optional): 页码/Page number — e.g. `1`

## search_user_posts

- `uid` (string, required): 用户ID/User ID — e.g. `7277477906`
- `q` (string, optional): 搜索关键词/Search keyword
- `page` (integer, optional): 页数/Page number — e.g. `1`
- `starttime` (string, optional): 开始时间戳/Start timestamp — e.g. `1772294400`
- `endtime` (string, optional): 结束时间戳/End timestamp — e.g. `1772294400`
- `hasori` (integer, optional): 是否包含原创微博，1=包含，0=不包含/Include original posts, 1=include, 0=exclude — e.g. `1`
- `hasret` (integer, optional): 是否包含转发微博，1=包含，0=不包含/Include retweets, 1=include, 0=exclude — e.g. `1`
- `hastext` (integer, optional): 是否包含文字微博，1=包含，0=不包含/Include text posts, 1=include, 0=exclude — e.g. `1`
- `haspic` (integer, optional): 是否包含图片微博，1=包含，0=不包含/Include image posts, 1=include, 0=exclude — e.g. `1`
- `hasvideo` (integer, optional): 是否包含视频微博，1=包含，0=不包含/Include video posts, 1=include, 0=exclude — e.g. `1`
- `hasmusic` (integer, optional): 是否包含音乐微博，1=包含，0=不包含/Include music posts, 1=include, 0=exclude — e.g. `1`
