# Channels API / 视频号接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_comments

`POST /api/v1/wechat_channels/fetch_comments`

<!-- Full path: /api/v1/wechat_channels/fetch_comments -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信视频号视频评论
- 支持分页获取更多评论
### 参数:
- id: 视频ID
- lastBuffer: 分页参数，首次请求可为空
- comment_id: 评论ID，默认不传，传入则获取该评论下的子评论
### 返回:
- 视频评论列表

## fetch_default_search

`POST /api/v1/wechat_channels/fetch_default_search`

<!-- Full path: /api/v1/wechat_channels/fetch_default_search -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信视频号默认搜索结果
 - 支持分页获取更多结果
 ### 参数:
 - keywords: 搜索关键词
 - session_buffer:
    - 分页参数，首次请求可为空，后续使用响应中的 `last_buff` 进行分页请求
    - JSON Path： `$.data.last_buff`
### 返回:
 - 搜索结果列表，包含视频信息
  ### 重要提示:
 - 如果你访问响应返回的 `url` 字段，可能会发现无法正确打开视频页面，这是因为微信对视频号页面做了防盗链处理。
 - 解决方法是将 `url` 字段和 `url_token` 字段拼接成一个完整的
URL，然后在浏览器中打开。（注明：可以打开的意思是HTTP响应代码200，不代表视频能正常播放，因为视频文件是加密的）
 - 使用上面拼接好的链接通过任意 HTTP 客户端下载视频文件，下载后如果发现 MP4 文件无法正常播放，说明该视频文件是加密的。
请使用接口返回的 `decode_key` 字段和加密视频文件，通过下面的工具进行解密。
 - ⚠️ **视频文件加密说明**: 如果下载的 MP4 文件无法正常播放，说明该视频文件是加密的。请使用接口返回的 `decode_key`
字段和加密视频文件，通过此工具进行解密：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
 - ⚠️ **重要**: 微信接口每次请求都会返回新的加密文件链接和 `decode_key`，即使是同一个视频。请确保使用的
`decode_key` 与下载的加密视频文件是同一次 API 响应中获取的，否则解密将会失败。
 - JSON Path 和相关说明:
    - 获取翻页参数 `last_buff`: `$.data.last_buff`
    - 获取视频列表: `$.data.media_list[*]`
    - 获取视频 CDN 链接（不带Token）: `$.data.media_list[*].object_desc.media[0].url`
    - 获取视频 CDN 链接的 Token: `$.data.media_list[*].object_desc.media[0].url_token`
    - 拼接视频 CDN 的完整 URL 方式: `$.data.media_list[*].object_desc.media[0].url + $.data.media_list[*].object_desc.media[0].url_token`
    - 获取视频解密密钥（每次请求都不一样）: `$.data.media_list[*].object_desc.media[0].decode_key`
    - 在线解密工具: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
    - 可自行部署的解密 API（Docker一键部署）：https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

## fetch_home_page

`POST /api/v1/wechat_channels/fetch_home_page`

<!-- Full path: /api/v1/wechat_channels/fetch_home_page -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信视频号用户主页信息
 - 包含用户发布的视频列表
 - 支持分页获取更多视频
 ### 参数:
 - username: 用户名
 - last_buffer:
    - 分页参数，首次请求可为空，后续使用 `object_list` 最后一个 item 的 `last_buffer` 进行分页请求
    - JSON Path: `$.data.object_list[-1].last_buffer`
### 返回:
 - 用户主页信息和视频列表
  ### 重要提示:
 - 如果你访问响应返回的 `url` 字段，可能会发现无法正确打开视频页面，这是因为微信对视频号页面做了防盗链处理。
 - 解决方法是将 `url` 字段和 `url_token` 字段拼接成一个完整的
URL，然后在浏览器中打开。（注明：可以打开的意思是HTTP响应代码200，不代表视频能正常播放，因为视频文件是加密的）
 - 使用上面拼接好的链接通过任意 HTTP 客户端下载视频文件，下载后如果发现 MP4 文件无法正常播放，说明该视频文件是加密的。
请使用接口返回的 `decode_key` 字段和加密视频文件，通过下面的工具进行解密。
 - ⚠️ **视频文件加密说明**: 如果下载的 MP4 文件无法正常播放，说明该视频文件是加密的。请使用接口返回的 `decode_key`
字段和加密视频文件，通过此工具进行解密：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
 - ⚠️ **重要**: 微信接口每次请求都会返回新的加密文件链接和 `decode_key`，即使是同一个视频。请确保使用的
`decode_key` 与下载的加密视频文件是同一次 API 响应中获取的，否则解密将会失败。
 - JSON Path 和相关说明:
    - 获取翻页参数 `last_buffer`: `$.data.object_list[-1].last_buffer`
    - 获取视频列表: `$.data.object_list[*]`
    - 获取视频 CDN 链接（不带Token）: `$.data.object_list[*].object_desc.media[0].url`
    - 获取视频 CDN 链接的 Token: `$.data.object_list[*].object_desc.media[0].url_token`
    - 拼接视频 CDN 的完整 URL 方式: `$.data.object_list[*].object_desc.media[0].url + $.data.object_list[*].object_desc.media[0].url_token`
    - 获取视频解密密钥（每次请求都不一样）: `$.data.object_list[*].object_desc.media[0].decode_key`
    - 在线解密工具: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
    - 可自行部署的解密 API（Docker一键部署）：https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

## fetch_hot_words

`GET /api/v1/wechat_channels/fetch_hot_words`

<!-- Full path: /api/v1/wechat_channels/fetch_hot_words -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信视频号当前热门话题
- 可用于发现热门内容和趋势
### 参数:
- 无需额外参数
### 返回:
- 热门话题列表

## fetch_live_history

`GET /api/v1/wechat_channels/fetch_live_history`

<!-- Full path: /api/v1/wechat_channels/fetch_live_history -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | 用户名/Username | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信视频号用户的直播回放列表
 ### 参数:
 - username: 用户名
 ### 返回:
 - 直播回放列表
  ### 重要提示:
 - 如果你访问响应返回的 `url` 字段，可能会发现无法正确打开视频页面，这是因为微信对视频号页面做了防盗链处理。
 - 解决方法是将 `url` 字段和 `url_token` 字段拼接成一个完整的
URL，然后在浏览器中打开。（注明：可以打开的意思是HTTP响应代码200，不代表视频能正常播放，因为视频文件是加密的）
 - 使用上面拼接好的链接通过任意 HTTP 客户端下载视频文件，下载后如果发现 MP4 文件无法正常播放，说明该视频文件是加密的。
请使用接口返回的 `decode_key` 字段和加密视频文件，通过下面的工具进行解密。
 - ⚠️ **视频文件加密说明**: 如果下载的 MP4 文件无法正常播放，说明该视频文件是加密的。请使用接口返回的 `decode_key`
字段和加密视频文件，通过此工具进行解密：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
 - ⚠️ **重要**: 微信接口每次请求都会返回新的加密文件链接和 `decode_key`，即使是同一个视频。请确保使用的
`decode_key` 与下载的加密视频文件是同一次 API 响应中获取的，否则解密将会失败。
 - JSON Path 和相关说明:
    - 获取直播回放列表: `$.data.live_list[*]`
    - 获取视频 CDN 链接（不带Token）: `$.data.live_list[*].media.url`
    - 获取视频 CDN 链接的 Token: `$.data.live_list[*].media.url_token`
    - 拼接视频 CDN 的完整 URL 方式: `$.data.live_list[*].media.url + $.data.live_list[*].media.url_token`
    - 获取视频解密密钥（每次请求都不一样）: `$.data.live_list[*].media.decode_key`
    - 在线解密工具: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
    - 可自行部署的解密 API（Docker一键部署）：https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

## fetch_mp_article_comment_list

`GET /api/v1/wechat_mp/web/fetch_mp_article_comment_list`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_comment_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | https://mp.weixin.qq.com/s/Iv-xRzL7WzbL0dUUIgi3Nw |
| comment_id | string |  | 评论ID/Comment ID (default: '') |  |
| buffer | string |  | 偏移量/Offset (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信公众号文章评论列表
 ### 参数:
 - url: 文章链接
 - comment_id: 评论ID，可以不传获取评论用的id，默认传空字符串
 - buffer: 偏移量，第一次传空字符串，后续传上次返回的buffer值
 ### 返回:
 - 评论列表

## fetch_mp_article_comment_reply_list

`GET /api/v1/wechat_mp/web/fetch_mp_article_comment_reply_list`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_comment_reply_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string |  | 文章链接/Article URL (default: https://mp.weixin.qq.com/s/Ko5V9jw9kwL8TO6Q7J3UqQ) |  |
| comment_id | string | ✅ | 评论ID/Comment ID | 3601466901697855492 |
| content_id | string | ✅ | 内容ID/Content ID | 6387234930341970671 |
| offset | string |  | 偏移量/Offset (default: '0') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取微信公众号文章评论回复列表
### 参数:
- url: 文章链接
- comment_id: 评论ID
- content_id: 内容ID
- offset: 偏移量
### 返回:
- 评论回复列表

## fetch_mp_article_detail_html

`GET /api/v1/wechat_mp/web/fetch_mp_article_detail_html`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_detail_html -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | https://mp.weixin.qq.com/s/TSNQKkRpN1qbKsT7BvzqIw |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:

获取微信公众号文章详情的HTML，如果你需要获取详细的JSON格式数据，请使用`/api/v1/wechat_mp/web/fetch_mp_article_detail_json`接口
 ### 参数:
 - url: 文章链接
 ### 返回:
 - 文章详情的HTML

## fetch_mp_article_detail_json

`GET /api/v1/wechat_mp/web/fetch_mp_article_detail_json`

<!-- Full path: /api/v1/wechat_mp/web/fetch_mp_article_detail_json -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 文章链接/Article URL | https://mp.weixin.qq.com/s/TSNQKkRpN1qbKsT7BvzqIw |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信公众号文章详情的JSON格式数据

 ### 参数:
 - url: 文章链接
 ### 返回:
 - 文章详情的HTML

## fetch_search_article

`GET /api/v1/wechat_mp/web/fetch_search_article`

<!-- Full path: /api/v1/wechat_mp/web/fetch_search_article -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 人工智能 |
| offset | integer |  | 偏移量，从0开始，每页+20/Offset, starts with 0, plus 20 every page (default: 0) |  |
| sort_type | string |  | '排序方式: _0默认 / _2最新 / _4最热 (Sort: _0 default / _2 newest / _4 hottest)' (default: _0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过关键词搜索微信公众号文章
 ### 参数:
 - keyword: 搜索关键词
 - offset: 偏移量，从0开始，每页+20
 - sort_type: 排序方式，可选 `_0`(默认) / `_2`(最新) / `_4`(最热)
 ### 返回:
 - 匹配的公众号文章列表
  ### 重要提示 / 资源限制:
 - 此接口资源有限，单次请求可能出现瞬时失败。
 - 建议在客户端实现 **3–5 次重试** 逻辑以获得更高的成功率，重试之间可加入短暂随机退避。

## fetch_search_channels

`GET /api/v1/wechat_channels/fetch_search_channels`

<!-- Full path: /api/v1/wechat_channels/fetch_search_channels -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 美食 |
| offset | integer |  | 偏移量，从0开始，每页+20/Offset, starts with 0, plus 20 every page (default: 0) |  |
| sort_type | string |  | '排序方式: _0默认 / _2最新 / _4最热 (Sort: _0 default / _2 newest / _4 hottest)' (default: _0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过关键词搜索微信视频号
 ### 参数:
 - keyword: 搜索关键词
 - offset: 偏移量，从0开始，每页+20
 - sort_type: 排序方式，可选 `_0`(默认) / `_2`(最新) / `_4`(最热)
 ### 返回:
 - 匹配的视频号搜索结果
  ### 重要提示 / 资源限制:
 - 此接口资源有限，单次请求可能出现瞬时失败。
 - 建议在客户端实现 **3–5 次重试** 逻辑以获得更高的成功率，重试之间可加入短暂随机退避。

## fetch_search_latest

`GET /api/v1/wechat_channels/fetch_search_latest`

<!-- Full path: /api/v1/wechat_channels/fetch_search_latest -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keywords | 美食 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信视频号最新视频搜索结果
 - 按时间倒序排列
 ### 参数:
 - keywords: 搜索关键词
 ### 返回:
 - 最新视频搜索结果列表
  ### 重要提示:
 - 如果你访问响应返回的 `url` 字段，可能会发现无法正确打开视频页面，这是因为微信对视频号页面做了防盗链处理。
 - 解决方法是将 `url` 字段和 `url_token` 字段拼接成一个完整的
URL，然后在浏览器中打开。（注明：可以打开的意思是HTTP响应代码200，不代表视频能正常播放，因为视频文件是加密的）
 - 使用上面拼接好的链接通过任意 HTTP 客户端下载视频文件，下载后如果发现 MP4 文件无法正常播放，说明该视频文件是加密的。
请使用接口返回的 `decode_key` 字段和加密视频文件，通过下面的工具进行解密。
 - ⚠️ **视频文件加密说明**: 如果下载的 MP4 文件无法正常播放，说明该视频文件是加密的。请使用接口返回的 `decode_key`
字段和加密视频文件，通过此工具进行解密：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
 - ⚠️ **重要**: 微信接口每次请求都会返回新的加密文件链接和 `decode_key`，即使是同一个视频。请确保使用的
`decode_key` 与下载的加密视频文件是同一次 API 响应中获取的，否则解密将会失败。
 - JSON Path 和相关说明:
    - 获取视频列表: `$.data.object_list[*]`
    - 获取视频 CDN 链接（不带Token）: `$.data.object_list[*].object_desc.media[0].url`
    - 获取视频 CDN 链接的 Token: `$.data.object_list[*].object_desc.media[0].url_token`
    - 拼接视频 CDN 的完整 URL 方式: `$.data.object_list[*].object_desc.media[0].url + $.data.object_list[*].object_desc.media[0].url_token`
    - 获取视频解密密钥（每次请求都不一样）: `$.data.object_list[*].object_desc.media[0].decode_key`
    - 在线解密工具: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
    - 可自行部署的解密 API（Docker一键部署）：https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

## fetch_search_official_account

`GET /api/v1/wechat_mp/web/fetch_search_official_account`

<!-- Full path: /api/v1/wechat_mp/web/fetch_search_official_account -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | 人民日报 |
| offset | integer |  | 偏移量，从0开始，每页+20/Offset, starts with 0, plus 20 every page (default: 0) |  |
| sort_type | string |  | '排序方式: _0默认 / _2最新 / _4最热 (Sort: _0 default / _2 newest / _4 hottest)' (default: _0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过关键词搜索微信公众号账号
 ### 参数:
 - keyword: 搜索关键词
 - offset: 偏移量，从0开始，每页+20
 - sort_type: 排序方式，可选 `_0`(默认) / `_2`(最新) / `_4`(最热)
 ### 返回:
 - 匹配的公众号列表
  ### 重要提示 / 资源限制:
 - 此接口资源有限，单次请求可能出现瞬时失败。
 - 建议在客户端实现 **3–5 次重试** 逻辑以获得更高的成功率，重试之间可加入短暂随机退避。

## fetch_search_ordinary

`GET /api/v1/wechat_channels/fetch_search_ordinary`

<!-- Full path: /api/v1/wechat_channels/fetch_search_ordinary -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keywords | 美食 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信视频号综合搜索结果
 - 按相关性排序
 ### 参数:
 - keywords: 搜索关键词
 ### 返回:
 - 综合搜索结果列表
  ### 重要提示:
 - 如果你访问响应返回的 `url` 字段，可能会发现无法正确打开视频页面，这是因为微信对视频号页面做了防盗链处理。
 - 解决方法是将 `url` 字段和 `url_token` 字段拼接成一个完整的
URL，然后在浏览器中打开。（注明：可以打开的意思是HTTP响应代码200，不代表视频能正常播放，因为视频文件是加密的）
 - 使用上面拼接好的链接通过任意 HTTP 客户端下载视频文件，下载后如果发现 MP4 文件无法正常播放，说明该视频文件是加密的。
请使用接口返回的 `decode_key` 字段和加密视频文件，通过下面的工具进行解密。
 - ⚠️ **视频文件加密说明**: 如果下载的 MP4 文件无法正常播放，说明该视频文件是加密的。请使用接口返回的 `decode_key`
字段和加密视频文件，通过此工具进行解密：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
 - ⚠️ **重要**: 微信接口每次请求都会返回新的加密文件链接和 `decode_key`，即使是同一个视频。请确保使用的
`decode_key` 与下载的加密视频文件是同一次 API 响应中获取的，否则解密将会失败。
 - JSON Path 和相关说明:
    - 获取视频列表: `$.data.object_list[*]`
    - 获取视频 CDN 链接（不带Token）: `$.data.object_list[*].object_desc.media[0].url`
    - 获取视频 CDN 链接的 Token: `$.data.object_list[*].object_desc.media[0].url_token`
    - 拼接视频 CDN 的完整 URL 方式: `$.data.object_list[*].object_desc.media[0].url + $.data.object_list[*].object_desc.media[0].url_token`
    - 获取视频解密密钥（每次请求都不一样）: `$.data.object_list[*].object_desc.media[0].decode_key`
    - 在线解密工具: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
    - 可自行部署的解密 API（Docker一键部署）：https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

## fetch_user_search

`GET /api/v1/wechat_channels/fetch_user_search`

<!-- Full path: /api/v1/wechat_channels/fetch_user_search -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keywords | 美食博主 |
| page | integer |  | 页码/Page number (default: 1) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索微信视频号用户
- 按关键词查找相关用户
### 参数:
- keywords: 搜索关键词
- page: 页码，从1开始
### 返回:
- 用户搜索结果列表

## fetch_user_search_v2

`GET /api/v1/wechat_channels/fetch_user_search_v2`

<!-- Full path: /api/v1/wechat_channels/fetch_user_search_v2 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string |  | 搜索关键词/Search keywords (default: '') | 美食博主 |
| page | integer |  | 页码/Page number (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索微信视频号用户
- 按关键词查找相关用户
### 参数:
- keywords: 搜索关键词
- page: 页码，默认为0
### 返回:
- 用户搜索结果列表

## fetch_video_by_share_url

`GET /api/v1/wechat_channels/fetch_video_by_share_url`

<!-- Full path: /api/v1/wechat_channels/fetch_video_by_share_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_url | string | ✅ | 视频号分享URL/Share URL of the WeChat Channels video | https://weixin.qq.com/sph/AwAMhHizXD |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 通过视频号分享URL获取视频详情
 - 适用于从浏览器或微信中拿到的分享链接，例如 `https://weixin.qq.com/sph/AwAMhHizXD`
  ### 参数:
 - share_url: 视频号分享URL（必填）
  ### 返回:
 - 视频详细信息（结构同 fetch_video_detail）

## fetch_video_detail

`GET /api/v1/wechat_channels/fetch_video_detail`

<!-- Full path: /api/v1/wechat_channels/fetch_video_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| id | string |  | 视频ID/Video ID (default: '') | 14396973035218999573 |
| exportId | string |  | >- (default: '') |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取微信视频号视频详细信息
 - 可通过视频ID或导出ID获取
 ### 参数:
 - id: 视频ID（二选一）
 - exportId: 导出ID（会过期，二选一，使用时可不传id）
 ### 返回:
 - 视频详细信息
  ### 重要提示:
 - 如果你访问响应返回的 `url` 字段，可能会发现无法正确打开视频页面，这是因为微信对视频号页面做了防盗链处理。
 - 解决方法是将 `url` 字段和 `url_token` 字段拼接成一个完整的
URL，然后在浏览器中打开。（注明：可以打开的意思是HTTP响应代码200，不代表视频能正常播放，因为视频文件是加密的）
 - 使用上面拼接好的链接通过任意 HTTP 客户端下载视频文件，下载后如果发现 MP4 文件无法正常播放，说明该视频文件是加密的。
请使用接口返回的 `decode_key` 字段和加密视频文件，通过下面的工具进行解密。
 - ⚠️ **视频文件加密说明**: 如果下载的 MP4 文件无法正常播放，说明该视频文件是加密的。请使用接口返回的 `decode_key`
字段和加密视频文件，通过此工具进行解密：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
 - ⚠️ **重要**: 微信接口每次请求都会返回新的加密文件链接和 `decode_key`，即使是同一个视频。请确保使用的
`decode_key` 与下载的加密视频文件是同一次 API 响应中获取的，否则解密将会失败。
 - JSON Path 和相关说明:
    - 获取视频 CDN 链接（不带Token）: `$.data.object_desc.media[0].url`
    - 获取视频 CDN 链接的 Token: `$.data.object_desc.media[0].url_token`
    - 拼接视频 CDN 的完整 URL 方式: `$.data.object_desc.media[0].url + $.data.object_desc.media[0].url_token`
    - 获取视频解密密钥（每次请求都不一样）: `$.data.object_desc.media[0].decode_key`
    - 在线解密工具: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
    - 可自行部署的解密 API（Docker一键部署）：https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

---

See SKILL.md for cross-group orchestration patterns.