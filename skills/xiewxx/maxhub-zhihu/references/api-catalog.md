# 知乎（Zhihu）API完整目录

> 共 34 个API，按能力域分类

## 数据采集（11个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取知乎专栏文章列表/Get Zhihu Column Articles | GET | `/api/v1/zhihu/web/fetch_column_articles` | column_id |
| 2 | 获取知乎专栏文章详情/Get Zhihu Column Article Deta | GET | `/api/v1/zhihu/web/fetch_column_article_detail` | article_id |
| 3 | 获取知乎相似专栏推荐/Get Zhihu Similar Column Reco | GET | `/api/v1/zhihu/web/fetch_column_recommend` | article_id |
| 4 | 获取知乎专栏文章互动关系/Get Zhihu Column Article Re | GET | `/api/v1/zhihu/web/fetch_column_relationship` | article_id |
| 5 | 获取知乎首页推荐/Get Zhihu Hot Recommend | GET | `/api/v1/zhihu/web/fetch_hot_recommend` | - |
| 6 | 获取知乎首页热榜/Get Zhihu Hot List | GET | `/api/v1/zhihu/web/fetch_hot_list` | - |
| 7 | 获取知乎首页视频榜/Get Zhihu Video List | GET | `/api/v1/zhihu/web/fetch_video_list` | - |
| 8 | 获取知乎用户信息/Get Zhihu User Info | GET | `/api/v1/zhihu/web/fetch_user_info` | user_url_token |
| 9 | 获取知乎用户的文章列表/Get Zhihu User Articles | GET | `/api/v1/zhihu/web/fetch_user_articles` | user_url_token |
| 10 | 获取知乎用户的被收录文章列表/Get Zhihu User Included A | GET | `/api/v1/zhihu/web/fetch_user_included_articles` | user_url_token |
| 11 | 获取知乎问题回答列表/Get Zhihu Question Answers | GET | `/api/v1/zhihu/web/fetch_question_answers` | question_id |

## 互动操作（10个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取知乎专栏评论区配置/Get Zhihu Column Comment Con | GET | `/api/v1/zhihu/web/fetch_column_comment_config` | article_id |
| 2 | 获取知乎评论区V5/Get Zhihu Comment V5 | GET | `/api/v1/zhihu/web/fetch_comment_v5` | answer_id |
| 3 | 获取知乎子评论区V5/Get Zhihu Sub Comment V5 | GET | `/api/v1/zhihu/web/fetch_sub_comment_v5` | comment_id |
| 4 | 获取知乎用户关注列表/Get Zhihu User Following | GET | `/api/v1/zhihu/web/fetch_user_followees` | user_url_token |
| 5 | 获取知乎用户粉丝列表/Get Zhihu User Followers | GET | `/api/v1/zhihu/web/fetch_user_followers` | user_url_token |
| 6 | 获取知乎用户订阅的专栏/Get Zhihu User Columns | GET | `/api/v1/zhihu/web/fetch_user_follow_columns` | user_url_token |
| 7 | 获取知乎用户关注的问题/Get Zhihu User Follow Questi | GET | `/api/v1/zhihu/web/fetch_user_follow_questions` | user_url_token |
| 8 | 获取知乎用户关注的收藏/Get Zhihu User Follow Collec | GET | `/api/v1/zhihu/web/fetch_user_follow_collections` | user_url_token |
| 9 | 获取知乎用户关注的话题/Get Zhihu User Follow Topics | GET | `/api/v1/zhihu/web/fetch_user_follow_topics` | user_url_token |
| 10 | 获取知乎推荐关注列表/Get Zhihu Recommend Followees | GET | `/api/v1/zhihu/web/fetch_recommend_followees` | - |

## 搜索查询（13个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取知乎文章搜索V3/Get Zhihu Article Search V3 | GET | `/api/v1/zhihu/web/fetch_article_search_v3` | keyword |
| 2 | 获取知乎用户搜索V3/Get Zhihu User Search V3 | GET | `/api/v1/zhihu/web/fetch_user_search_v3` | keyword |
| 3 | 获取知乎话题搜索V3/Get Zhihu Topic Search V3 | GET | `/api/v1/zhihu/web/fetch_topic_search_v3` | keyword |
| 4 | 获取知乎论文搜索V3/Get Zhihu Scholar Search V3 | POST | `/api/v1/zhihu/web/fetch_scholar_search_v3` | keyword |
| 5 | 获取知乎AI搜索/Get Zhihu AI Search | GET | `/api/v1/zhihu/web/fetch_ai_search` | message_content |
| 6 | 获取知乎AI搜索结果/Get Zhihu AI Search Result | GET | `/api/v1/zhihu/web/fetch_ai_search_result` | message_id |
| 7 | 获取知乎视频搜索V3/Get Zhihu Video Search V3 | GET | `/api/v1/zhihu/web/fetch_video_search_v3` | keyword |
| 8 | 获取知乎专栏搜索V3/Get Zhihu Column Search V3 | GET | `/api/v1/zhihu/web/fetch_column_search_v3` | keyword |
| 9 | 获取知乎盐选内容搜索V3/Get Zhihu Salt Search V3 | GET | `/api/v1/zhihu/web/fetch_salt_search_v3` | keyword |
| 10 | 获取知乎电子书搜索V3/Get Zhihu Ebook Search V3 | GET | `/api/v1/zhihu/web/fetch_ebook_search_v3` | keyword |
| 11 | 获取知乎搜索预设词/Get Zhihu Preset Search | GET | `/api/v1/zhihu/web/fetch_preset_search` | - |
| 12 | 获取知乎搜索发现/Get Zhihu Search Recommend | GET | `/api/v1/zhihu/web/fetch_search_recommend` | - |
| 13 | 知乎搜索预测词/Get Zhihu Search Suggest | GET | `/api/v1/zhihu/web/fetch_search_suggest` | keyword |
