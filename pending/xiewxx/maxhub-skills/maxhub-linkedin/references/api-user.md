# User Data API / 用户数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_discovery_relevant_to_user

`GET /api/v1/linkedin/web_v2/get_discovery_relevant_to_user`

<!-- Full path: /api/v1/linkedin/web_v2/get_discovery_relevant_to_user -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |
| count | integer |  | '' (default: 12) |  |
| start | integer |  | '' (default: 0) |  |
| pagination_token | string |  | 保留兼容字段（当前不分页）/Reserved for future use |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 基于指定用户作为种子，返回 LinkedIn 推荐的相关人员列表。
 - 适合做"You may also know"/"行业人脉"扩展分析。
  ### 参数:
 - username: 已关注 / 想要参考的 LinkedIn 用户名（必填）
 - count / start / pagination_token: 兼容字段（当前不分页）
  ### 容错策略:
 - 如目标用户因隐私限制 / 地区限制不可见，**不会报错**，自动降级为基于当前账号的推荐结果
  ### 返回:
 - data.elements: 推荐人员数组，每个 profile 含姓名 / 头衔 / 头像 / 当前职位 / 推荐理由

## get_user_about

`GET /api/v1/linkedin/web/get_user_about`

<!-- Full path: /api/v1/linkedin/web/get_user_about -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAA8BYqEBCGLg_vT_ca6mMEqkpp9nVffJ3hc |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户简介/关于信息
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
  ### 返回:
 - 用户简介数据

## get_user_bio

`GET /api/v1/linkedin/web_v2/get_user_bio`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_bio -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 提取用户主页 About 段精简数据，已解析直接消费（不带 raw 包装层）。
 - 比 `get_user_profile` 更轻量；只需简介信息时用此端点。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.summary: 个人简介 / 自我介绍长文本
 - data.headline: 一句话 headline（如 "CEO at Microsoft"）
 - data.industry: 行业
 - data.location: 地理位置

## get_user_certifications

`GET /api/v1/linkedin/web/get_user_certifications`

<!-- Full path: /api/v1/linkedin/web/get_user_certifications -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAARpiwIBp_SzoeHPlUfOvmtibe08Ea1iCh4 |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户认证
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户认证列表数据

## get_user_certifications

`GET /api/v1/linkedin/web/get_user_certifications`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_certifications -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户证书与认证（主页 'Licenses & certifications' 折叠区）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.elements: 证书数组，每条含
  - name: 证书名称（如 "AWS Solutions Architect"）
  - issuing_organization: 颁发机构
  - issuing_organization_logo: 机构 logo
  - issue_date: 颁发日期
  - expiration_date: 失效日期（无则 null）
  - credential_id: 凭证编号
  - credential_url: 凭证查验链接

## get_user_comments

`GET /api/v1/linkedin/web/get_user_comments`

<!-- Full path: /api/v1/linkedin/web/get_user_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户的评论
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
 - pagination_token: 分页令牌（可选）
  ### 返回:
 - 用户评论列表数据

## get_user_contact

`GET /api/v1/linkedin/web/get_user_contact`

<!-- Full path: /api/v1/linkedin/web/get_user_contact -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/LinkedIn username | shubhangi-shrivastava-39161bb7 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn用户的联系信息
 ### 参数:
- username: LinkedIn用户名（必填）
 ### 返回:
- 用户联系信息数据

## get_user_contact_info

`GET /api/v1/linkedin/web_v2/get_user_contact_info`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_contact_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取用户主页 'Contact Info' 弹窗里的公开联系信息字段。
 - **只返回用户主动设为公开**的字段，不会绕过隐私设置。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.email: 邮箱
 - data.websites: 个人网站列表
 - data.twitter: Twitter handle
 - data.wechat: 微信号
 - data.phone: 电话
 - data.birthday: 出生日期
 - data.address: 公开地址
 - data.connectedAt: 与查询账号的连接时间（如有）
 - 字段未公开时对应值为 null

## get_user_educations

`GET /api/v1/linkedin/web/get_user_educations`

<!-- Full path: /api/v1/linkedin/web/get_user_educations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAARpiwIBp_SzoeHPlUfOvmtibe08Ea1iCh4 |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户教育背景
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户教育背景列表数据

## get_user_educations

`GET /api/v1/linkedin/web/get_user_educations`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_educations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户教育背景（主页 'Education' 折叠区）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.elements: 教育经历数组，每条含
  - school_name: 学校名称
  - school_logo: 学校 logo
  - degree: 学历（学士 / 硕士 / 博士 / MBA 等）
  - field_of_study: 专业 / 方向
  - start_date / end_date: 起止时间
  - grade: 成绩 / GPA（如填写）
  - description: 在校描述（项目 / 活动等）

## get_user_experience

`GET /api/v1/linkedin/web/get_user_experience`

<!-- Full path: /api/v1/linkedin/web/get_user_experience -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAAjpjWIBMh1iBR4OgSPK5GXetlQ6dYUT-qo |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户工作经历
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户工作经历列表数据

## get_user_experiences

`GET /api/v1/linkedin/web_v2/get_user_experiences`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_experiences -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户工作经历列表（主页 'Experience' 折叠区）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.elements: 工作经历数组，每条含
  - 公司名称 / 公司 LinkedIn 链接 / 公司 logo
  - 职位标题 / 雇佣类型（全职/兼职/合同/实习）
  - 起止时间 / 是否至今在职
  - 工作描述 / 地点
  - 关联技能（如有）

## get_user_follower_and_connection

`GET /api/v1/linkedin/web/get_user_follower_and_connection`

<!-- Full path: /api/v1/linkedin/web/get_user_follower_and_connection -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/LinkedIn username | zoranmilosevic |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn用户粉丝和连接数
 ### 参数:
- username: LinkedIn用户名（必填）
 ### 返回:
- 用户粉丝和连接数数据

## get_user_honors

`GET /api/v1/linkedin/web/get_user_honors`

<!-- Full path: /api/v1/linkedin/web/get_user_honors -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAC41xVEBx77koDz3k1eJ5E9t8UZ7g0IVGj4 |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户荣誉奖项
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户荣誉奖项列表数据

## get_user_honors

`GET /api/v1/linkedin/web/get_user_honors`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_honors -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户荣誉与奖项（主页 'Honors & awards' 折叠区）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.elements: 奖项数组，每条含
  - title: 奖项名称
  - issuer: 颁发方
  - issue_date: 颁发日期
  - description: 奖项描述
  - associated_with: 关联的工作经历或教育（如有）

## get_user_images

`GET /api/v1/linkedin/web/get_user_images`

<!-- Full path: /api/v1/linkedin/web/get_user_images -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户发布的图片
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
 - pagination_token: 分页令牌（可选）
  ### 返回:
 - 用户图片列表数据

## get_user_interested_groups

`GET /api/v1/linkedin/web_v2/get_user_interested_groups`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_interested_groups -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户主动关注的 LinkedIn Groups 列表。
 - **受目标用户隐私设置影响**：如目标用户隐藏了关注列表，会返回 403。
  ### 参数:
 - username: LinkedIn 用户名（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 群组数组，每条含群组名称 / logo / 成员数 / 群组 URL / 简介
 - data.metadata: 分页信息

## get_user_interests_groups

`GET /api/v1/linkedin/web/get_user_interests_groups`

<!-- Full path: /api/v1/linkedin/web/get_user_interests_groups -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAAjpjWIBMh1iBR4OgSPK5GXetlQ6dYUT-qo |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户感兴趣的群组
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户感兴趣的群组列表数据

## get_user_publications

`GET /api/v1/linkedin/web/get_user_publications`

<!-- Full path: /api/v1/linkedin/web/get_user_publications -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAB8rG_UB7cstjC__gk5318uYsZOIVkyysi4 |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户出版物
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户出版物列表数据

## get_user_publications

`GET /api/v1/linkedin/web/get_user_publications`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_publications -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户出版物 / 学术论文列表（主页 'Publications' 折叠区）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.elements: 出版物数组，每条含
  - title: 标题
  - venue: 期刊 / 会议 / 出版方
  - publication_date: 发表日期
  - url: 出版物链接
  - description: 摘要 / 简介
  - co_authors: 合著者列表

## get_user_reactions

`GET /api/v1/linkedin/web/get_user_reactions`

<!-- Full path: /api/v1/linkedin/web/get_user_reactions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户的点赞/反应记录
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
 - pagination_token: 分页令牌（可选）
  ### 返回:
 - 用户点赞/反应数据

## get_user_recent_activity

`GET /api/v1/linkedin/web_v2/get_user_recent_activity`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_recent_activity -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回主页 'Activity' 折叠区的最新动态聚合预览（最近 N 条 posts / comments / reactions
的混合摘要）。
 - 用于在主页快速展示用户近期活跃度；**不是**完整列表（完整列表请用 get_user_posts /
get_user_comments）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.elements: 最近活动数组，每条含
  - activity_type: posts / comments / reactions
  - content: 帖子或评论摘要
  - timestamp: 活动时间
  - target_post: 被评论 / 被点赞的原帖（comments / reactions 类型才有）
- data.total_count: 用户公开活动总数

## get_user_recommendations

`GET /api/v1/linkedin/web/get_user_recommendations`

<!-- Full path: /api/v1/linkedin/web/get_user_recommendations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAC3iNKcB3qbWJrP7K5Z3i89AF5c1snr8bhc |
| page | string |  | 页码/Page number (default: 1) | 1 |
| type | string |  | '推荐类型：received(收到的)或given(给出的)/Type: received or given' (default: received) | received |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户的推荐信
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
 - type: 推荐类型（可选），默认为received
    - received: 收到的推荐信
    - given: 给出的推荐信
- pagination_token: 分页令牌（可选）
  ### 返回:
 - 用户推荐信列表数据

## get_user_recommendations

`GET /api/v1/linkedin/web/get_user_recommendations`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_recommendations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |
| direction | string |  | received(收到的) / given(写出的) (default: received) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取用户主页 'Recommendations' 折叠区里的推荐信内容。
  ### 参数:
 - username: LinkedIn 用户名（必填）
 - direction: `received`（收到的）或 `given`（写出的），默认 received
  ### 返回:
 - data.elements: 推荐信数组，每条含推荐人姓名 / 头像 / 头衔 / 推荐文本 / 推荐时间 / 与被推荐者的关系
 - 响应包含 received 与 given 两组数据，调用方按 direction 字段筛选

## get_user_skills

`GET /api/v1/linkedin/web/get_user_skills`

<!-- Full path: /api/v1/linkedin/web/get_user_skills -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAACkphDcBDruPBdXiAnqyc834jkTkd_4kRnU |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户技能
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户技能列表数据

## get_user_skills

`GET /api/v1/linkedin/web/get_user_skills`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_skills -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 返回用户技能列表（主页 'Skills' 折叠区）。
 ### 参数:
- username: LinkedIn 用户名（必填）
 ### 返回:
- data.elements: 技能数组，每条含
  - name: 技能名称（如 "Python", "Cloud Computing"）
  - endorsement_count: 其他用户对此技能的认可数
  - top_endorsers: 顶部认可者列表（部分技能有）

## get_user_top_card_supplementary

`GET /api/v1/linkedin/web_v2/get_user_top_card_supplementary`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_top_card_supplementary -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回顶部卡片之外的次级展示数据（UI 标签和徽章），用于完善展示。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.open_to_work: 'Open to work' 横幅信息（求职意向 / 期望职位 / 期望地点）
 - data.hiring: 'Hiring' 标签（如有，含正在招聘的职位）
 - data.premium_badge: Premium 会员标记
 - data.creator_mode: 创作者模式徽章
 - data.influencer: LinkedIn Influencer 标记（顶级用户）
 - data.verification: 是否已验证

## get_user_videos

`GET /api/v1/linkedin/web/get_user_videos`

<!-- Full path: /api/v1/linkedin/web/get_user_videos -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户发布的视频
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
 - pagination_token: 分页令牌（可选）
  ### 返回:
 - 用户视频列表数据

## get_user_volunteers

`GET /api/v1/linkedin/web/get_user_volunteers`

<!-- Full path: /api/v1/linkedin/web/get_user_volunteers -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAABCtiL8B26nfi3Nbpo_AM8ngg4LeClT1Wh8 |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户的志愿者经历
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户志愿者经历数据

## search_users

`GET /api/v1/linkedin/web_v2/search_users`

<!-- Full path: /api/v1/linkedin/web_v2/search_users -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keyword | python developer |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 10) |  |
| geo_urn | string |  | 地理位置URN/Geo URN | urn:li:geo:103644278 |
| industry_urn | string |  | 行业URN/Industry URN | urn:li:industry:4 |
| current_company_urn | string |  | 当前公司URN/Current company URN | urn:li:fsd_company:1035 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按关键词 + 可选过滤器搜索 LinkedIn 用户。
 - 过滤器以 LinkedIn URN 形式提供，从 LinkedIn 搜索 URL 的 query string 复制即可。
  ### 参数:
 - keywords: 搜索关键词（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50，默认 10）
 - geo_urn: 地理位置 URN（如 `urn:li:geo:103644278` = United States）
 - industry_urn: 行业 URN（如 `urn:li:industry:4` = Computer Software）
 - current_company_urn: 当前公司 URN（如 `urn:li:fsd_company:1035` = Microsoft）
  ### 返回:
 - data.elements: 用户搜索结果数组，每条含
  - public_identifier: URL slug（用于后续调 get_user_*）
  - full_name: 全名
  - headline: 一句话头衔
  - profile_picture: 头像 URL
  - location: 地点
  - current_position: 当前职位（公司 + 标题）
- data.metadata: 分页信息 + 总命中数

---

See SKILL.md for cross-group orchestration patterns.