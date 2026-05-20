# Parameter Mappings / 参数映射

Platform: `linkedin` | Base URL: `https://www.aconfig.cn`

---

## get_ad_detail

- `ad_id` (string, required): 广告ID/Ad ID — e.g. `637671316`

## get_comment_replies

- `comment_urn` (string, required): 父评论URN/Parent comment URN — e.g. `>-`
- `post_urn` (string, optional): >- — e.g. `urn:li:activity:7193456789012345678`
- `count` (integer, optional): ''
- `pagination_token` (string, optional): 上一页响应里的 paginationToken

## get_comments_replies

- `post_id` (string, required): 帖子ID/Post ID — e.g. `7244804629786419202`
- `comment_id` (string, required): 评论ID/Comment ID
- `previous_replies_token` (string, required): 前一组回复的令牌/Previous replies token

## get_company_affiliated_pages

- `company_id` (string, required): 公司ID/Company ID — e.g. `1441`

## get_company_associated_member_insights

- `company_id` (string, required): 公司ID/Company ID — e.g. `1441`

## get_company_call_to_actions

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_competitors

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_employee_count_ranges

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_employees

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_company_grouped_locations

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_job_count

- `company_id` (string, required): 公司ID/Company ID — e.g. `783611`

## get_company_job_count

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_jobs

- `company_id` (string, required): 公司ID/Company ID — e.g. `783611`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `sort_by` (string, optional): '排序方式：recent(最新)或relevant(相关)/Sort by: recent or relevant'
- `date_posted` (string, optional): 发布时间过滤：anytime, past_month, past_week, past_24_hours
- `experience_level` (string, optional): >-
- `remote` (string, optional): 工作地点类型：onsite, remote, hybrid
- `job_type` (string, optional): >-
- `easy_apply` (string, optional): 是否易申请/Filter easy apply jobs
- `under_10_applicants` (string, optional): 是否少于10个申请者/Filter jobs with under 10 applicants
- `fair_chance_employer` (string, optional): 是否公平机会雇主/Filter fair chance employer jobs

## get_company_jobs

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_company_people

- `company_id` (string, required): 公司ID/Company ID — e.g. `1066442`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_company_posts

- `company_id` (string, required): 公司ID/Company ID — e.g. `10649600`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `sort_by` (string, optional): '排序方式：top(热门)或recent(最新)/Sort by: top or recent' — e.g. `top`

## get_company_posts

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_company_profile

- `company` (string, optional): 公司名称/Company name — e.g. `rapidapi`
- `company_id` (string, optional): 公司ID（额外消耗1次请求）/Company ID (+1 request)

## get_company_profile

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_similar_companies

- `universal_name` (string, required): 公司URL slug/Company slug — e.g. `microsoft`

## get_company_stock_quote

- `universal_name` (string, required): 公司URL slug（必须上市）/Public company slug — e.g. `microsoft`

## get_discovery_relevant_to_company

- `universal_name` (string, required): 公司URL slug/Company URL slug — e.g. `microsoft`
- `count` (integer, optional): ''
- `start` (integer, optional): ''
- `pagination_token` (string, optional): 保留兼容字段（当前不分页）/Reserved for future use

## get_discovery_relevant_to_user

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `count` (integer, optional): ''
- `start` (integer, optional): ''
- `pagination_token` (string, optional): 保留兼容字段（当前不分页）/Reserved for future use

## get_group_info

- `group_id` (string, required): 群组ID/Group ID

## get_group_posts

- `group_id` (string, required): 群组ID/Group ID
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_hashtag_feed

- `hashtag` (string, required): '话题文本，不带#/Hashtag text without #' — e.g. `ai`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_job_detail

- `job_id` (string, required): 职位ID/Job ID — e.g. `4172815660`
- `include_skills` (string, optional): 包含职位技能要求（额外消耗1次请求）/Include job skills (+1 request)

## get_job_detail

- `job_id` (string, required): LinkedIn职位数字ID/LinkedIn job numeric ID — e.g. `3902341234`

## get_post_comments

- `post_id` (string, required): 帖子ID/Post ID — e.g. `7244804629786419202`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `sort_order` (string, optional): >-
- `post_type` (string, optional): >-

## get_post_comments

- `post_urn` (string, required): 帖子URN/Post URN — e.g. `urn:li:activity:7193456789012345678`
- `start` (integer, optional): ''
- `count` (integer, optional): ''
- `sort_order` (string, optional): 评论排序：RELEVANCE / CHRON / REVERSE_CHRON / MEMBER_SETTING

## get_post_detail

- `post_id` (string, required): 帖子ID/Post ID — e.g. `7244804629786419202`

## get_post_detail

- `post_urn` (string, required): 帖子URN或数字ID/Post URN or numeric ID — e.g. `urn:li:activity:7193456789012345678`

## get_post_detail_by_slug

- `slug` (string, required): 帖子URL slug尾段/Post URL slug suffix — e.g. `satya-nadella_ai-activity-7193456789012345678-AbCd`

## get_post_reactions

- `post_id` (string, required): 帖子ID/Post ID — e.g. `7244804629786419202`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `type` (string, optional): >-

## get_post_reactions

- `post_urn` (string, required): 帖子URN/Post URN — e.g. `urn:li:activity:7193456789012345678`
- `reaction_type` (string, optional): >- — e.g. `LIKE`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_post_reposts

- `post_id` (string, required): 帖子ID/Post ID — e.g. `7244804629786419202`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_about

- `urn` (string, required): >- — e.g. `ACoAAA8BYqEBCGLg_vT_ca6mMEqkpp9nVffJ3hc`

## get_user_bio

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_certifications

- `urn` (string, required): >- — e.g. `ACoAAARpiwIBp_SzoeHPlUfOvmtibe08Ea1iCh4`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_certifications

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_comments

- `urn` (string, required): >- — e.g. `ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_comments

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_user_contact

- `username` (string, required): LinkedIn用户名/LinkedIn username — e.g. `shubhangi-shrivastava-39161bb7`

## get_user_contact_info

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_educations

- `urn` (string, required): >- — e.g. `ACoAAARpiwIBp_SzoeHPlUfOvmtibe08Ea1iCh4`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_educations

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_experience

- `urn` (string, required): >- — e.g. `ACoAAAjpjWIBMh1iBR4OgSPK5GXetlQ6dYUT-qo`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_experiences

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_follower_and_connection

- `username` (string, required): LinkedIn用户名/LinkedIn username — e.g. `zoranmilosevic`

## get_user_follower_and_connection_count

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_honors

- `urn` (string, required): >- — e.g. `ACoAAC41xVEBx77koDz3k1eJ5E9t8UZ7g0IVGj4`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_honors

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_images

- `urn` (string, required): >- — e.g. `ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_images

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_user_interested_companies

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_user_interested_groups

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_user_interests_companies

- `urn` (string, required): >- — e.g. `ACoAAEDH77YBEVIYXAaEwTicp5CcB_hR7DfFL9o`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_interests_groups

- `urn` (string, required): >- — e.g. `ACoAAAjpjWIBMh1iBR4OgSPK5GXetlQ6dYUT-qo`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_posts

- `urn` (string, required): >- — e.g. `ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_posts

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `start` (integer, optional): 分页起始偏移/Start offset
- `count` (integer, optional): 每页数量（最大50）/Page size (max 50)

## get_user_profile

- `username` (string, required): LinkedIn用户名/LinkedIn username — e.g. `jack`
- `include_follower_and_connection` (string, optional): >-
- `include_experiences` (string, optional): 包含工作经历（额外消耗1次请求）/Include work experiences (+1 request)
- `include_skills` (string, optional): 包含技能（额外消耗1次请求）/Include skills (+1 request)
- `include_certifications` (string, optional): 包含认证（额外消耗1次请求）/Include certifications (+1 request)
- `include_publications` (string, optional): 包含出版物（额外消耗1次请求）/Include publications (+1 request)
- `include_educations` (string, optional): 包含教育背景（额外消耗1次请求）/Include educational background (+1 request)
- `include_volunteers` (string, optional): 包含志愿者经历（额外消耗1次请求）/Include volunteer experiences (+1 request)
- `include_honors` (string, optional): 包含荣誉奖项（额外消耗1次请求）/Include honors and awards (+1 request)
- `include_interests` (string, optional): 包含兴趣（额外消耗1次请求）/Include interests (+1 request)
- `include_bio` (string, optional): 包含个人简介（额外消耗1次请求）/Include bio/about (+1 request)

## get_user_profile

- `username` (string, required): LinkedIn用户名/LinkedIn username — e.g. `williamhgates`
- `include_follower_and_connection` (string, optional): 附带粉丝/连接数 (+1 request)/Include follower & connection count
- `include_experiences` (string, optional): 附带工作经历/Include work experiences
- `include_skills` (string, optional): 附带技能/Include skills
- `include_certifications` (string, optional): 附带认证/Include certifications
- `include_publications` (string, optional): 附带出版物/Include publications
- `include_educations` (string, optional): 附带教育背景/Include educations
- `include_volunteers` (string, optional): 附带志愿者经历/Include volunteer exp
- `include_honors` (string, optional): 附带荣誉奖项/Include honors
- `include_interests` (string, optional): 附带感兴趣的公司+群组/Include interests
- `include_bio` (string, optional): 附带简介/Include bio

## get_user_profile_cards

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_publications

- `urn` (string, required): >- — e.g. `ACoAAB8rG_UB7cstjC__gk5318uYsZOIVkyysi4`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_publications

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_reactions

- `urn` (string, required): >- — e.g. `ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_recent_activity

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_recommendations

- `urn` (string, required): >- — e.g. `ACoAAC3iNKcB3qbWJrP7K5Z3i89AF5c1snr8bhc`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `type` (string, optional): '推荐类型：received(收到的)或given(给出的)/Type: received or given' — e.g. `received`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_recommendations

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `direction` (string, optional): received(收到的) / given(写出的)

## get_user_skills

- `urn` (string, required): >- — e.g. `ACoAACkphDcBDruPBdXiAnqyc834jkTkd_4kRnU`
- `page` (string, optional): 页码/Page number — e.g. `1`

## get_user_skills

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_top_card

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_top_card_supplementary

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`

## get_user_videos

- `urn` (string, required): >- — e.g. `ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `pagination_token` (string, optional): 分页令牌/Pagination token

## get_user_videos

- `username` (string, required): LinkedIn用户名/Username — e.g. `williamhgates`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## get_user_volunteers

- `urn` (string, required): >- — e.g. `ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8`
- `page` (string, optional): 页码/Page number — e.g. `1`

## search_ads

- `keyword` (string, optional): >- — e.g. `data`
- `advertiser_name` (string, optional): 广告主名称/Advertiser name
- `country` (string, optional): 国家代码过滤/Country code filter — e.g. `US`
- `date` (string, optional): >-
- `pagination_token` (string, optional): 分页令牌/Pagination token

## search_jobs

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `backend`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `sort_by` (string, optional): '排序方式：recent(最新)或relevant(相关)/Sort by: recent or relevant'
- `date_posted` (string, optional): 发布时间过滤：anytime, past_month, past_week, past_24_hours
- `geocode` (string, optional): 地理位置代码，可通过Search Geocode Location获取/Geocode for location — e.g. `103644278`
- `company` (string, optional): 公司ID过滤/Company ID filter (e.g., 1441 for Google) — e.g. `1441`
- `experience_level` (string, optional): >-
- `remote` (string, optional): 工作地点类型：onsite, remote, hybrid
- `job_type` (string, optional): >-
- `easy_apply` (string, optional): 是否易申请/Filter easy apply jobs
- `has_verifications` (string, optional): 是否有公司认证/Filter jobs with company verifications
- `under_10_applicants` (string, optional): 是否少于10个申请者/Filter jobs with under 10 applicants
- `fair_chance_employer` (string, optional): 是否公平机会雇主/Filter fair chance employer jobs

## search_jobs

- `keywords` (string, required): 搜索关键词/Search keyword — e.g. `machine learning engineer`
- `location` (string, optional): 地点（自由文本）/Location (free text) — e.g. `San Francisco Bay Area`
- `start` (integer, optional): ''
- `count` (integer, optional): ''

## search_location

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `san francisco`

## search_people

- `name` (string, optional): 搜索关键词/Search keyword for people — e.g. `john`
- `first_name` (string, optional): 名/First name — e.g. `john`
- `last_name` (string, optional): 姓/Last name — e.g. `oliver`
- `title` (string, optional): 职位/Title — e.g. `manager`
- `company` (string, optional): 公司/Company
- `school` (string, optional): 学校/School
- `page` (string, optional): 页码/Page number — e.g. `1`
- `geocode_location` (string, optional): 地理位置代码/Geocode for location (e.g., 103644278 for United States) — e.g. `103644278`
- `current_company` (string, optional): 当前公司ID/Current company ID
- `profile_language` (string, optional): 个人资料语言/Profile language
- `industry` (string, optional): 行业ID/Industry ID
- `service_category` (string, optional): 服务类别ID/Service category ID

## search_posts

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `data`
- `page` (string, optional): 页码/Page number — e.g. `1`
- `date_posted` (string, optional): >-
- `sort_by` (string, optional): 排序方式 (date_posted, relevance)/Sort by date_posted or relevance
- `from_member` (string, optional): 按成员过滤，逗号分隔/Filter by member, separate by comma
- `from_company` (string, optional): 按公司过滤，逗号分隔/Filter by company, separate by comma
- `content_type` (string, optional): >-

## search_schools

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `stanford`
- `page` (string, optional): 页码/Page number — e.g. `1`

## search_suggestion_industry

- `keyword` (string, required): 搜索关键词/Search keyword — e.g. `software`

## search_users

- `keywords` (string, required): 搜索关键词/Search keyword — e.g. `python developer`
- `start` (integer, optional): ''
- `count` (integer, optional): ''
- `geo_urn` (string, optional): 地理位置URN/Geo URN — e.g. `urn:li:geo:103644278`
- `industry_urn` (string, optional): 行业URN/Industry URN — e.g. `urn:li:industry:4`
- `current_company_urn` (string, optional): 当前公司URN/Current company URN — e.g. `urn:li:fsd_company:1035`
