# Parameter Mappings / 参数映射

Platform: `youtube` | Base URL: `https://www.aconfig.cn`

---

## get_channel_community_posts

- `channel_id` (string, required): 频道ID/Channel ID — e.g. `UCkRfArvrzheW2E7b6SVT7vQ`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `continuation_token` (string, optional): 分页token，用于获取下一页/Pagination token for next page
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_channel_description

- `channel_id` (string, optional): >- — e.g. `UCeu6U67OzJhV1KwBansH3Dg`
- `continuation_token` (string, optional): >-
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_channel_id

- `channel_name` (string, required): 频道名称/Channel name — e.g. `LinusTechTips`

## get_channel_id

- `channel_url` (string, required): >- — e.g. `https://www.youtube.com/@CozyCraftYT`

## get_channel_id_v2

- `channel_url` (string, required): >- — e.g. `https://www.youtube.com/@CozyCraftYT`

## get_channel_info

- `channel_id` (string, required): 频道ID/Channel ID — e.g. `UCXuqSBlHAE6Xw-yeJA0Tunw`

## get_channel_short_videos

- `channel_id` (string, required): 频道ID/Channel ID — e.g. `UCXuqSBlHAE6Xw-yeJA0Tunw`
- `continuation_token` (string, optional): 翻页令牌/Pagination token

## get_channel_shorts

- `channel_id` (string, optional): 频道ID/Channel ID (e.g., UCuAXFkgsw1L7xaCfnd5JJOw) — e.g. `UCuAXFkgsw1L7xaCfnd5JJOw`
- `channel_url` (string, optional): >- — e.g. `https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw`
- `continuation_token` (string, optional): 分页token/Pagination token
- `need_format` (boolean, optional): 是否格式化数据/Whether to format data

## get_channel_url

- `channel_id` (string, required): 频道ID/Channel ID (格式如：UCeu6U67OzJhV1KwBansH3Dg) — e.g. `UCeu6U67OzJhV1KwBansH3Dg`

## get_channel_url

- `channel_id` (string, required): 频道ID/Channel ID (格式如：UCeu6U67OzJhV1KwBansH3Dg) — e.g. `UCeu6U67OzJhV1KwBansH3Dg`

## get_channel_videos

- `channel_id` (string, required): 频道ID/Channel ID — e.g. `UCJHBJ7F-nAIlMGolm0Hu4vg`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `continuation_token` (string, optional): 分页token，用于获取下一页/Pagination token for next page
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_channel_videos_v2

- `channel_id` (string, required): 频道ID/Channel ID — e.g. `UCXuqSBlHAE6Xw-yeJA0Tunw`
- `lang` (string, optional): 视频结果语言代码/Video result language code — e.g. `en-US`
- `sortBy` (string, optional): 排序方式/Sort by — e.g. `newest`
- `contentType` (string, optional): 内容类型/Content type — e.g. `videos`
- `nextToken` (string, optional): 翻页令牌/Pagination token

## get_general_search

- `search_query` (string, required): 搜索关键字/Search keyword — e.g. `Python编程`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code
- `country_code` (string, optional): 国家代码（如US, CN等）/Country code
- `time_zone` (string, optional): 时区（如America/Los_Angeles, Asia/Shanghai等）/Time zone
- `upload_time` (string, optional): 上传时间过滤 | Upload time filter
- `duration` (string, optional): 视频时长过滤 | Duration filter
- `content_type` (string, optional): 内容类型过滤 | Content type filter
- `feature` (string, optional): 特征过滤 | Feature filter
- `sort_by` (string, optional): 排序方式 | Sort by
- `continuation_token` (string, optional): 翻页令牌/Pagination token

## get_general_search_v2

- `keyword` (string, optional): 搜索关键词（首次请求必填）/Search keyword (required for first request) — e.g. `Python tutorial`
- `continuation_token` (string, optional): 分页token，用于获取下一页/Continuation token for next page
- `upload_date` (string, optional): 上传时间过滤/Upload date filter
- `type` (string, optional): 类型过滤/Type filter
- `duration` (string, optional): '时长过滤/Duration filter: short (<4min), medium (4-20min), long (>20min)'
- `features` (string, optional): >-
- `sort_by` (string, optional): 排序方式/Sort by

## get_post_comment_replies

- `continuation_token` (string, required): >-
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_post_comments

- `post_id` (string, optional): 帖子ID（首次请求时必填）/Post ID (required for first request) — e.g. `UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy`
- `continuation_token` (string, optional): >-
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_post_detail

- `post_id` (string, required): 帖子ID/Post ID — e.g. `UgkxiCSRfD6g7SPlWGPDa3vbP7aIsytXRkvy`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_relate_video

- `video_id` (string, required): 视频ID/Video ID — e.g. `LuIL5JATZsc`
- `continuation_token` (string, optional): 翻页令牌/Pagination token

## get_related_videos

- `video_id` (string, optional): 视频ID/Video ID — e.g. `dQw4w9WgXcQ`
- `video_url` (string, optional): 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) — e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `need_format` (boolean, optional): >-

## get_search_suggestions

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `Rick Astley`
- `language` (string, optional): 语言代码/Language code (e.g., en, zh-cn, ja) — e.g. `en`
- `region` (string, optional): 地区代码/Region code (e.g., US, SG, CN, JP) — e.g. `US`

## get_shorts_search

- `search_query` (string, required): 搜索关键字/Search keyword — e.g. `Python编程`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `en-US`
- `country_code` (string, optional): 国家代码（如US, CN等）/Country code — e.g. `US`
- `time_zone` (string, optional): 时区（如America/Los_Angeles, Asia/Shanghai等）/Time zone — e.g. `America/Los_Angeles`
- `upload_time` (string, optional): 上传时间过滤 | Upload time filter for Shorts
- `sort_by` (string, optional): 排序方式 | Sort by for Shorts
- `continuation_token` (string, optional): 翻页令牌/Pagination token
- `filter_mixed_content` (boolean, optional): >- — e.g. `true`

## get_shorts_search_v2

- `keyword` (string, optional): 搜索关键词（首次请求必填）/Search keyword (required for first request) — e.g. `coding tips`
- `continuation_token` (string, optional): 分页token，用于获取下一页/Continuation token for next page
- `upload_date` (string, optional): 上传时间过滤/Upload date filter
- `sort_by` (string, optional): 排序方式/Sort by

## get_signed_stream_url

- `video_id` (string, optional): 视频ID/Video ID — e.g. `dQw4w9WgXcQ`
- `video_url` (string, optional): 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) — e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `itag` (integer, required): >- — e.g. `18`

## get_trending_videos

- `language_code` (string, optional): 语言代码/Language code
- `country_code` (string, optional): 国家代码/Country code
- `section` (string, optional): 类型/Section

## get_video_captions

- `video_id` (string, optional): 视频ID/Video ID — e.g. `dQw4w9WgXcQ`
- `video_url` (string, optional): 视频URL/Video URL — e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `language_code` (string, optional): >- — e.g. `en`
- `format` (string, optional): 字幕格式/Caption format — e.g. `srt`

## get_video_captions_v2

- `video_id` (string, optional): 视频ID/Video ID — e.g. `MWvpXswLFxA`
- `video_url` (string, optional): 视频URL/Video URL — e.g. `https://www.youtube.com/watch?v=MWvpXswLFxA`
- `language_code` (string, optional): >- — e.g. `en`
- `format` (string, optional): 字幕格式/Caption format — e.g. `srt`

## get_video_comment_replies

- `continuation_token` (string, required): >-
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_video_comments

- `video_id` (string, required): 视频ID/Video ID — e.g. `LuIL5JATZsc`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `country_code` (string, optional): 国家代码（如US, JP等）/Country code — e.g. `US`
- `sort_by` (string, optional): 排序方式 | Sort by
- `continuation_token` (string, optional): 翻页令牌/Pagination token
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_video_info

- `video_id` (string, required): 视频ID/Video ID — e.g. `LuIL5JATZsc`
- `url_access` (string, optional): URL访问模式：normal（包含音视频URL）| blocked（不包含音视频URL） / URL access mode
- `lang` (string, optional): 语言代码（IETF标签），默认en-US / Language code — e.g. `zh-CN`
- `videos` (string, optional): >-
- `audios` (string, optional): >-
- `subtitles` (boolean, optional): 是否获取字幕 / Include subtitles
- `related` (boolean, optional): 是否获取相关视频 / Include related content

## get_video_info

- `video_id` (string, required): 视频ID/Video ID — e.g. `oaSNBz4qMQY`
- `language_code` (string, optional): 语言代码（如zh-CN, en-US等）/Language code — e.g. `zh-CN`
- `need_format` (boolean, optional): 是否需要清洗数据，提取关键内容，移除冗余数据/Whether to clean and format the data

## get_video_info_v2

- `video_id` (string, required): 视频ID/Video ID — e.g. `LuIL5JATZsc`

## get_video_streams

- `video_id` (string, optional): 视频ID/Video ID — e.g. `dQw4w9WgXcQ`
- `video_url` (string, optional): 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) — e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

## get_video_streams_v2

- `video_id` (string, optional): 视频ID/Video ID — e.g. `dQw4w9WgXcQ`
- `video_url` (string, optional): 视频URL/Video URL (如果提供video_id则忽略此参数/Ignored if video_id is provided) — e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

## get_video_subtitles

- `subtitle_url` (string, required): 字幕URL（需先调用获取视频详情接口） / Subtitle URL from video details — e.g. `https://www.youtube.com/api/timedtext?v=...`
- `format` (string, optional): 字幕格式：srt/xml/vtt/txt / Subtitle format
- `fix_overlap` (boolean, optional): 修复重叠字幕（默认开启） / Fix overlapping subtitles
- `target_lang` (string, optional): 目标语言代码（留空保持原语言） / Target language code — e.g. `zh-CN`

## search_channel

- `channel_id` (string, required): 频道ID/Channel ID — e.g. `UCXuqSBlHAE6Xw-yeJA0Tunw`
- `search_query` (string, required): 搜索关键字/Search keyword — e.g. `AMD`
- `language_code` (string, optional): 语言代码/Language code
- `country_code` (string, optional): 国家代码/Country code
- `continuation_token` (string, optional): 翻页令牌/Pagination token

## search_channels

- `keyword` (string, optional): 搜索关键词/Search keyword — e.g. `Rick Astley`
- `continuation_token` (string, optional): 分页token/Pagination token
- `need_format` (boolean, optional): 是否格式化数据/Whether to format data

## search_video

- `search_query` (string, required): 搜索关键字/Search keyword — e.g. `Minecraft`
- `language_code` (string, optional): 语言代码/Language code
- `order_by` (string, optional): 排序方式/Order by
- `country_code` (string, optional): 国家代码/Country code
- `continuation_token` (string, optional): 翻页令牌/Pagination token
