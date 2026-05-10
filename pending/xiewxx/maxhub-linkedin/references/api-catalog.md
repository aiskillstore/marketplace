# LinkedIn（LinkedIn）API完整目录

> 共 68 个API，按能力域分类

## 数据采集（56个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取用户资料/Get user profile | GET | `/api/v1/linkedin/web/get_user_profile` | username |
| 2 | 获取用户帖子/Get user posts | GET | `/api/v1/linkedin/web/get_user_posts` | urn |
| 3 | 获取用户联系信息/Get user contact information | GET | `/api/v1/linkedin/web/get_user_contact` | username |
| 4 | 获取用户推荐信/Get user recommendations | GET | `/api/v1/linkedin/web/get_user_recommendations` | urn |
| 5 | 获取用户视频/Get user videos | GET | `/api/v1/linkedin/web/get_user_videos` | urn |
| 6 | 获取用户图片/Get user images | GET | `/api/v1/linkedin/web/get_user_images` | urn |
| 7 | 获取公司资料/Get company profile | GET | `/api/v1/linkedin/web/get_company_profile` | - |
| 8 | 获取公司员工/Get company people | GET | `/api/v1/linkedin/web/get_company_people` | company_id |
| 9 | 获取公司帖子/Get company posts | GET | `/api/v1/linkedin/web/get_company_posts` | company_id |
| 10 | 获取公司职位/Get company jobs | GET | `/api/v1/linkedin/web/get_company_jobs` | company_id |
| 11 | 获取公司职位数量/Get company job count | GET | `/api/v1/linkedin/web/get_company_job_count` | company_id |
| 12 | 获取用户简介/Get user about | GET | `/api/v1/linkedin/web/get_user_about` | urn |
| 13 | 获取用户工作经历/Get user experience | GET | `/api/v1/linkedin/web/get_user_experience` | urn |
| 14 | 获取用户技能/Get user skills | GET | `/api/v1/linkedin/web/get_user_skills` | urn |
| 15 | 获取用户教育背景/Get user educations | GET | `/api/v1/linkedin/web/get_user_educations` | urn |
| 16 | 获取用户出版物/Get user publications | GET | `/api/v1/linkedin/web/get_user_publications` | urn |
| 17 | 获取用户认证/Get user certifications | GET | `/api/v1/linkedin/web/get_user_certifications` | urn |
| 18 | 获取用户荣誉奖项/Get user honors | GET | `/api/v1/linkedin/web/get_user_honors` | urn |
| 19 | 获取用户感兴趣的群组/Get user interests groups | GET | `/api/v1/linkedin/web/get_user_interests_groups` | urn |
| 20 | 获取用户感兴趣的公司/Get user interests companies | GET | `/api/v1/linkedin/web/get_user_interests_companies` | urn |
| 21 | 获取职位详情/Get job detail | GET | `/api/v1/linkedin/web/get_job_detail` | job_id |
| 22 | 获取用户主页基础信息（可选附带子节）/Get user profile (opt | GET | `/api/v1/linkedin/web_v2/get_user_profile` | username |
| 23 | 获取用户帖子（动态标签）/Get user posts | GET | `/api/v1/linkedin/web_v2/get_user_posts` | username |
| 24 | 获取用户公开联系信息/Get contact info | GET | `/api/v1/linkedin/web_v2/get_user_contact_info` | username |
| 25 | 获取用户推荐信/Get recommendations | GET | `/api/v1/linkedin/web_v2/get_user_recommendations` | username |
| 26 | 获取用户视频帖子/Get user videos | GET | `/api/v1/linkedin/web_v2/get_user_videos` | username |
| 27 | 获取用户图片帖子/Get user images | GET | `/api/v1/linkedin/web_v2/get_user_images` | username |
| 28 | 获取用户简介摘要/Get user bio | GET | `/api/v1/linkedin/web_v2/get_user_bio` | username |
| 29 | 获取用户主页全部卡片原始结构/Get full profile cards | GET | `/api/v1/linkedin/web_v2/get_user_profile_cards` | username |
| 30 | 获取用户工作经历/Get experiences | GET | `/api/v1/linkedin/web_v2/get_user_experiences` | username |
| 31 | 获取用户技能/Get skills | GET | `/api/v1/linkedin/web_v2/get_user_skills` | username |
| 32 | 获取用户教育背景/Get educations | GET | `/api/v1/linkedin/web_v2/get_user_educations` | username |
| 33 | 获取用户出版物/Get publications | GET | `/api/v1/linkedin/web_v2/get_user_publications` | username |
| 34 | 获取用户认证/Get certifications | GET | `/api/v1/linkedin/web_v2/get_user_certifications` | username |
| 35 | 获取用户荣誉奖项/Get honors | GET | `/api/v1/linkedin/web_v2/get_user_honors` | username |
| 36 | 获取用户主页顶部卡片/Get profile top card | GET | `/api/v1/linkedin/web_v2/get_user_top_card` | username |
| 37 | 获取用户主页顶部卡片补充信息/Get top card supplementar | GET | `/api/v1/linkedin/web_v2/get_user_top_card_supplementary` | username |
| 38 | 获取用户近期动态聚合/Get recent activity summary | GET | `/api/v1/linkedin/web_v2/get_user_recent_activity` | username |
| 39 | 发现："基于公司 X"的相关推荐/Discovery relevant to c | GET | `/api/v1/linkedin/web_v2/get_discovery_relevant_to_company` | universal_name |
| 40 | 发现："基于用户 X"的相关推荐/Discovery relevant to u | GET | `/api/v1/linkedin/web_v2/get_discovery_relevant_to_user` | username |
| 41 | 获取公司主页资料/Get company profile | GET | `/api/v1/linkedin/web_v2/get_company_profile` | universal_name |
| 42 | 获取公司员工列表/Get employees | GET | `/api/v1/linkedin/web_v2/get_company_employees` | universal_name |
| 43 | 获取公司主页帖子流/Get company posts | GET | `/api/v1/linkedin/web_v2/get_company_posts` | universal_name |
| 44 | 获取公司在招职位列表/Get company jobs | GET | `/api/v1/linkedin/web_v2/get_company_jobs` | universal_name |
| 45 | 获取公司在招职位总数/Get job count | GET | `/api/v1/linkedin/web_v2/get_company_job_count` | universal_name |
| 46 | 获取相似公司（People also viewed）/Get similar c | GET | `/api/v1/linkedin/web_v2/get_company_similar_companies` | universal_name |
| 47 | 获取公司竞争对手/Get competitors | GET | `/api/v1/linkedin/web_v2/get_company_competitors` | universal_name |
| 48 | 获取上市公司股价/Get stock quote | GET | `/api/v1/linkedin/web_v2/get_company_stock_quote` | universal_name |
| 49 | 获取公司主页 CTA 按钮配置/Get CTA buttons | GET | `/api/v1/linkedin/web_v2/get_company_call_to_actions` | universal_name |
| 50 | 获取公司员工数量范围（各 segment）/Get employee count | GET | `/api/v1/linkedin/web_v2/get_company_employee_count_ranges` | universal_name |
| 51 | 获取公司全部办公地点（按地理分组）/Get grouped locations | GET | `/api/v1/linkedin/web_v2/get_company_grouped_locations` | universal_name |
| 52 | 获取单条帖子详情（按 post URN）/Get post detail by  | GET | `/api/v1/linkedin/web_v2/get_post_detail` | post_urn |
| 53 | 按 URL slug 获取帖子/Get post by URL slug | GET | `/api/v1/linkedin/web_v2/get_post_detail_by_slug` | slug |
| 54 | 获取帖子点赞/反应人列表/Get post reactions | GET | `/api/v1/linkedin/web_v2/get_post_reactions` | post_urn |
| 55 | 按 hashtag 获取话题动态流/Get hashtag feed | GET | `/api/v1/linkedin/web_v2/get_hashtag_feed` | hashtag |
| 56 | 获取职位详情/Get job detail | GET | `/api/v1/linkedin/web_v2/get_job_detail` | job_id |

## 互动操作（8个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 获取用户评论/Get user comments | GET | `/api/v1/linkedin/web/get_user_comments` | urn |
| 2 | 获取用户粉丝和连接数/Get user follower and connect | GET | `/api/v1/linkedin/web/get_user_follower_and_connection` | username |
| 3 | 获取用户评论（在他人帖子下的评论）/Get user comments | GET | `/api/v1/linkedin/web_v2/get_user_comments` | username |
| 4 | 获取用户粉丝/连接数/Get follower & connection cou | GET | `/api/v1/linkedin/web_v2/get_user_follower_and_connection_count` | username |
| 5 | 获取用户关注的群组/Get followed groups | GET | `/api/v1/linkedin/web_v2/get_user_interested_groups` | username |
| 6 | 获取用户关注的公司/Get followed companies | GET | `/api/v1/linkedin/web_v2/get_user_interested_companies` | username |
| 7 | 获取帖子顶层评论/Get post top-level comments | GET | `/api/v1/linkedin/web_v2/get_post_comments` | post_urn |
| 8 | 获取评论的回复/Get comment replies | GET | `/api/v1/linkedin/web_v2/get_comment_replies` | comment_urn |

## 搜索查询（4个API）

| # | 名称 | 方法 | 路径 | 必填参数 |
|---|------|------|------|----------|
| 1 | 搜索职位/Search jobs | GET | `/api/v1/linkedin/web/search_jobs` | keyword |
| 2 | 搜索用户/Search people | GET | `/api/v1/linkedin/web/search_people` | - |
| 3 | 搜索用户/Search users | GET | `/api/v1/linkedin/web_v2/search_users` | keywords |
| 4 | 搜索职位/Search jobs | GET | `/api/v1/linkedin/web_v2/search_jobs` | keywords |
