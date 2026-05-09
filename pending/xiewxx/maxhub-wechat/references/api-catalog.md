# 微信（WeChat）API完整目录

> 共 20 个API，按能力域分类

## 数据采集（12个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取微信公众号文章详情的JSON/Get Wechat MP Article D | GET | `/api/v1/wechat_mp/web/fetch_mp_article_detail_json` | url |
| 2 | 获取微信公众号文章详情的HTML/Get Wechat MP Article D | GET | `/api/v1/wechat_mp/web/fetch_mp_article_detail_html` | url |
| 3 | 获取微信公众号文章列表/Get Wechat MP Article List | GET | `/api/v1/wechat_mp/web/fetch_mp_article_list` | ghid |
| 4 | 获取微信公众号文章阅读量/Get Wechat MP Article Read  | GET | `/api/v1/wechat_mp/web/fetch_mp_article_read_count` | url, comment_id |
| 5 | 获取微信公众号文章永久链接/Get Wechat MP Article URL | GET | `/api/v1/wechat_mp/web/fetch_mp_article_url` | sogou_url |
| 6 | 获取微信公众号广告/Get Wechat MP Article Ad | GET | `/api/v1/wechat_mp/web/fetch_mp_article_ad` | url |
| 7 | 获取微信公众号长链接转短链接/Get Wechat MP Long URL to | GET | `/api/v1/wechat_mp/web/fetch_mp_article_url_conversion` | url |
| 8 | 获取微信公众号关联文章/Get Wechat MP Related Articl | GET | `/api/v1/wechat_mp/web/fetch_mp_related_articles` | url |
| 9 | 微信视频号视频详情/WeChat Channels Video Detail | GET | `/api/v1/wechat_channels/fetch_video_detail` | - |
| 10 | 微信视频号主页/WeChat Channels Home Page | POST | `/api/v1/wechat_channels/fetch_home_page` | - |
| 11 | 微信视频号直播回放/WeChat Channels Live History | GET | `/api/v1/wechat_channels/fetch_live_history` | username |
| 12 | 微信视频号热门话题/WeChat Channels Hot Topics | GET | `/api/v1/wechat_channels/fetch_hot_words` | - |

## 互动操作（3个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取微信公众号文章评论列表/Get Wechat MP Article Comm | GET | `/api/v1/wechat_mp/web/fetch_mp_article_comment_list` | url |
| 2 | 获取微信公众号文章评论回复列表/Get Wechat MP Article Co | GET | `/api/v1/wechat_mp/web/fetch_mp_article_comment_reply_list` | comment_id, content_id |
| 3 | 微信视频号评论/WeChat Channels Comments | POST | `/api/v1/wechat_channels/fetch_comments` | - |

## 搜索查询（5个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 微信视频号默认搜索/WeChat Channels Default Search | POST | `/api/v1/wechat_channels/fetch_default_search` | - |
| 2 | 微信视频号搜索最新视频/WeChat Channels Search Lates | GET | `/api/v1/wechat_channels/fetch_search_latest` | keywords |
| 3 | 微信视频号综合搜索/WeChat Channels Comprehensive  | GET | `/api/v1/wechat_channels/fetch_search_ordinary` | keywords |
| 4 | 微信视频号用户搜索/WeChat Channels User Search | GET | `/api/v1/wechat_channels/fetch_user_search` | keywords |
| 5 | 微信视频号用户搜索V2/WeChat Channels User Search  | GET | `/api/v1/wechat_channels/fetch_user_search_v2` | - |

