# Parameter Mappings / 参数映射

Platform: `wechat` | Base URL: `https://www.aconfig.cn`

---

## fetch_live_history

- `username` (string, required): 用户名/Username — e.g. `>-`

## fetch_mp_article_ad

- `url` (string, required): 文章链接/Article URL — e.g. `https://mp.weixin.qq.com/s/hrTDuwh0pWyJFYC93kKCrg`

## fetch_mp_article_comment_list

- `url` (string, required): 文章链接/Article URL — e.g. `https://mp.weixin.qq.com/s/Iv-xRzL7WzbL0dUUIgi3Nw`
- `comment_id` (string, optional): 评论ID/Comment ID
- `buffer` (string, optional): 偏移量/Offset

## fetch_mp_article_comment_reply_list

- `url` (string, optional): 文章链接/Article URL
- `comment_id` (string, required): 评论ID/Comment ID — e.g. `3601466901697855492`
- `content_id` (string, required): 内容ID/Content ID — e.g. `6387234930341970671`
- `offset` (string, optional): 偏移量/Offset

## fetch_mp_article_detail_html

- `url` (string, required): 文章链接/Article URL — e.g. `https://mp.weixin.qq.com/s/TSNQKkRpN1qbKsT7BvzqIw`

## fetch_mp_article_detail_json

- `url` (string, required): 文章链接/Article URL — e.g. `https://mp.weixin.qq.com/s/TSNQKkRpN1qbKsT7BvzqIw`

## fetch_mp_article_list

- `ghid` (string, required): 公众号ID/MP ID — e.g. `gh_a3d35d4c9d3f`
- `offset` (string, optional): 偏移量/Offset

## fetch_mp_article_read_count

- `url` (string, required): 文章链接/Article URL — e.g. `https://mp.weixin.qq.com/s/hrTDuwh0pWyJFYC93kKCrg`
- `comment_id` (string, required): 评论ID/Comment ID

## fetch_mp_article_url

- `sogou_url` (string, required): 搜狗链接/Sogou URL — e.g. `>-`

## fetch_mp_article_url_conversion

- `url` (string, required): 文章链接/Article URL — e.g. `>-`

## fetch_mp_related_articles

- `url` (string, required): 文章链接/Article URL — e.g. `https://mp.weixin.qq.com/s/Ko5V9jw9kwL8TO6Q7J3UqQ`

## fetch_search_article

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `人工智能`
- `offset` (integer, optional): 偏移量，从0开始，每页+20/Offset, starts with 0, plus 20 every page
- `sort_type` (string, optional): '排序方式: _0默认 / _2最新 / _4最热 (Sort: _0 default / _2 newest / _4 hottest)'

## fetch_search_channels

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `美食`
- `offset` (integer, optional): 偏移量，从0开始，每页+20/Offset, starts with 0, plus 20 every page
- `sort_type` (string, optional): '排序方式: _0默认 / _2最新 / _4最热 (Sort: _0 default / _2 newest / _4 hottest)'

## fetch_search_latest

- `keywords` (string, required): 搜索关键词/Search keywords — e.g. `美食`

## fetch_search_official_account

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `人民日报`
- `offset` (integer, optional): 偏移量，从0开始，每页+20/Offset, starts with 0, plus 20 every page
- `sort_type` (string, optional): '排序方式: _0默认 / _2最新 / _4最热 (Sort: _0 default / _2 newest / _4 hottest)'

## fetch_search_ordinary

- `keywords` (string, required): 搜索关键词/Search keywords — e.g. `美食`

## fetch_user_search

- `keywords` (string, required): 搜索关键词/Search keywords — e.g. `美食博主`
- `page` (integer, optional): 页码/Page number

## fetch_user_search_v2

- `keywords` (string, optional): 搜索关键词/Search keywords — e.g. `美食博主`
- `page` (integer, optional): 页码/Page number

## fetch_video_by_share_url

- `share_url` (string, required): 视频号分享URL/Share URL of the WeChat Channels video — e.g. `https://weixin.qq.com/sph/AwAMhHizXD`

## fetch_video_detail

- `id` (string, optional): 视频ID/Video ID — e.g. `14396973035218999573`
- `exportId` (string, optional): >-
