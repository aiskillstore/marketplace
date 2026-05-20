# Parameter Mappings / 参数映射

Platform: `zhihu` | Base URL: `https://www.aconfig.cn`

---

## fetch_ai_search

- `message_content` (string, required): 搜索内容/Search Content

## fetch_ai_search_result

- `message_id` (string, required): 消息ID/Message ID

## fetch_column_article_detail

- `article_id` (string, required): 文章ID/Article ID

## fetch_column_articles

- `column_id` (string, required): 专栏ID/Column ID
- `limit` (string, optional): 每页文章数量/Number of articles per page
- `offset` (string, optional): 偏移量/Offset

## fetch_column_comment_config

- `article_id` (string, required): 文章ID/Article ID

## fetch_column_recommend

- `article_id` (string, required): 文章ID/Article ID
- `limit` (string, optional): 每页专栏数量/Number of columns per page
- `offset` (string, optional): 偏移量/Offset

## fetch_column_relationship

- `article_id` (string, required): 文章ID/Article ID

## fetch_column_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页专栏数量/Number of columns per page
- `search_hash_id` (string, optional): 搜索哈希ID/Search Hash ID

## fetch_comment_v5

- `answer_id` (string, required): 回答ID/Answer ID
- `order_by` (string, optional): 排序/Sort
- `limit` (string, optional): 每页评论数量/Number of comments per page
- `offset` (string, optional): 偏移量/Offset

## fetch_ebook_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页电子书数量/Number of ebooks per page
- `search_hash_id` (string, optional): 搜索哈希ID/Search Hash ID

## fetch_hot_list

- `limit` (string, optional): 每页文章数量/Number of articles per page
- `desktop` (string, optional): 是否为桌面端/Is it a desktop

## fetch_hot_recommend

- `offset` (string, optional): 偏移量/Offset
- `page_number` (string, optional): 页码/Page Number
- `session_token` (string, optional): 会话令牌/Session Token

## fetch_salt_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页内容数量/Number of contents per page
- `search_hash_id` (string, optional): 搜索哈希ID/Search Hash ID

## fetch_scholar_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页论文数量/Number of papers per page

## fetch_search_suggest

- `keyword` (string, required): 搜索关键词/Search Keywords

## fetch_sub_comment_v5

- `comment_id` (string, required): 评论ID/Comment ID
- `order_by` (string, optional): 排序/Sort
- `limit` (string, optional): 每页评论数量/Number of comments per page
- `offset` (string, optional): 偏移量/Offset

## fetch_topic_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页话题数量/Number of topics per page

## fetch_user_articles

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页文章数量/Number of articles per page
- `sort_type` (string, optional): 排序类型/Sort Type

## fetch_user_follow_collections

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页收藏数量/Number of collections per page

## fetch_user_follow_columns

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页专栏数量/Number of columns per page

## fetch_user_follow_questions

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页问题数量/Number of questions per page

## fetch_user_follow_topics

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页话题数量/Number of topics per page

## fetch_user_followees

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页用户数量/Number of users per page

## fetch_user_followers

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页用户数量/Number of users per page

## fetch_user_included_articles

- `user_url_token` (string, required): 用户ID/User ID
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页文章数量/Number of articles per page

## fetch_user_info

- `user_url_token` (string, required): 用户ID/User ID

## fetch_user_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页用户数量/Number of users per page

## fetch_video_list

- `offset` (string, optional): 偏移量/Offset
- `limit` (string, optional): 每页视频数量/Number of videos per page

## fetch_video_search_v3

- `keyword` (string, required): 搜索关键词/Search Keywords
- `limit` (string, optional): 每页视频数量/Number of videos per page
- `offset` (string, optional): 偏移量/Offset
- `search_hash_id` (string, optional): 搜索哈希ID/Search Hash ID
