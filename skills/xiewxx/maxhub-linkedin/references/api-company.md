# Company Data API / 公司数据接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## get_company_affiliated_pages

`GET /api/v1/linkedin/web/get_company_affiliated_pages`

<!-- Full path: /api/v1/linkedin/web/get_company_affiliated_pages -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company_id | string | ✅ | 公司ID/Company ID | 1441 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn公司的关联页面
 ### 参数:
- company_id: 公司ID（必填）
 ### 返回:
- 公司关联页面数据

## get_company_associated_member_insights

`GET /api/v1/linkedin/web/get_company_associated_member_insights`

<!-- Full path: /api/v1/linkedin/web/get_company_associated_member_insights -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company_id | string | ✅ | 公司ID/Company ID | 1441 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn公司的关联成员洞察数据
 ### 参数:
- company_id: 公司ID（必填）
 ### 返回:
- 公司关联成员洞察数据

## get_company_call_to_actions

`GET /api/v1/linkedin/web_v2/get_company_call_to_actions`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_call_to_actions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 返回公司主页右上角的 Call-to-Action 按钮配置。
- 用于了解公司主推的转化路径（注册 / 咨询 / 访问官网等）。
 ### 参数:
- universal_name: 公司 URL slug（必填）
 ### 返回:
- data.elements: CTA 按钮数组，每条含
  - cta_type: 按钮类型（visit_website / sign_up / learn_more / contact_us / view_jobs / etc）
  - label: 按钮文案
  - url: 点击后跳转的 URL
  - is_external: 是否站外链接

## get_company_competitors

`GET /api/v1/linkedin/web_v2/get_company_competitors`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_competitors -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回 LinkedIn 推算的竞争对手列表，基于行业 / 规模 / 主营业务的近义匹配。
 - 相对客观，适合做行业图谱 / 竞品分析。
 - 与 `get_company_similar_companies` 区别：competitors 是平台业务匹配，similar
是用户行为聚合。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
  ### 返回:
 - data.elements: 竞争对手数组，每条含
  - 公司名称 / logo / 行业 / 员工规模
  - 总部地点 / 简介
  - 与查询公司的相似度评分（如有）

## get_company_employee_count_ranges

`GET /api/v1/linkedin/web_v2/get_company_employee_count_ranges`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_employee_count_ranges -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回公司员工数量按多个维度的分布统计（在 LinkedIn 'Insights' 页面可视化展示）。
 - 适合做公司画像 / 组织规模分析。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
  ### 返回:
 - data.by_location: 按地点分组（含每个地点的员工数）
 - data.by_function: 按职能分组（工程 / 销售 / 市场等）
 - data.by_department: 按部门分组
 - data.by_seniority: 按资历分组（initial / senior / VP / 高管 等）
 - data.by_business_line: 按业务线分组（如有）
 - 每个维度可能因公司规模较小而无数据

## get_company_employees

`GET /api/v1/linkedin/web_v2/get_company_employees`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_employees -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 列出指定公司的员工，按 LinkedIn 默认相关性排序。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50，默认 10）
  ### 限制:
 - 受 LinkedIn 全局搜索结果上限影响：每家公司通常可拉取 < 1000 条
 - 仅返回可被搜索的员工（公开 + 1°/2°/3° connection）
  ### 返回:
 - data.elements: 员工数组，每条含
  - name: 姓名
  - public_identifier: URL slug（用于后续调 get_user_*）
  - headline: 一句话头衔
  - profile_picture: 头像 URL
  - location: 地点
  - current_position: 当前职位

## get_company_grouped_locations

`GET /api/v1/linkedin/web_v2/get_company_grouped_locations`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_grouped_locations -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回公司全部办公地点，按地理分组（公司主页 'Locations' 标签数据）。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
  ### 返回:
 - data.locations: 按 country / state / city 分组的地点数组
 - 每个地点含
  - line1 / line2: 详细街道地址
  - city / state / country / postal_code
  - latitude / longitude: 经纬度（如有）
  - is_headquarters: 是否总部
  - description: 地点描述（如有，含此办公室主营业务）

## get_company_job_count

`GET /api/v1/linkedin/web/get_company_job_count`

<!-- Full path: /api/v1/linkedin/web/get_company_job_count -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company_id | string | ✅ | 公司ID/Company ID | 783611 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn公司职位数量
 ### 参数:
- company_id: 公司ID（必填）
 ### 返回:
- 公司职位数量数据

## get_company_job_count

`GET /api/v1/linkedin/web/get_company_job_count`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_job_count -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 仅返回公司当前在招职位的总数（轻量调用，比 `get_company_jobs` 节省请求成本）。
 - 需要具体列表请用 `get_company_jobs`。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
  ### 返回:
 - data.job_count: 在招职位总数（整数）

## get_company_jobs

`GET /api/v1/linkedin/web/get_company_jobs`

<!-- Full path: /api/v1/linkedin/web/get_company_jobs -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company_id | string | ✅ | 公司ID/Company ID | 783611 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| sort_by | string |  | '排序方式：recent(最新)或relevant(相关)/Sort by: recent or relevant' |  |
| date_posted | string |  | 发布时间过滤：anytime, past_month, past_week, past_24_hours |  |
| experience_level | string |  | >- |  |
| remote | string |  | 工作地点类型：onsite, remote, hybrid |  |
| job_type | string |  | >- |  |
| easy_apply | string |  | 是否易申请/Filter easy apply jobs |  |
| under_10_applicants | string |  | 是否少于10个申请者/Filter jobs with under 10 applicants |  |
| fair_chance_employer | string |  | 是否公平机会雇主/Filter fair chance employer jobs |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn公司职位列表
  ### 参数:
 - company_id: 公司ID（必填）
 - page: 页码（可选），默认为1
 - sort_by: 排序方式（可选）：recent(最新), relevant(相关)
 - date_posted: 发布时间过滤（可选）：anytime, past_month, past_week, past_24_hours
 - experience_level: 经验级别（可选）：internship, entry_level, associate,
mid_senior, director, executive
 - remote: 工作地点类型（可选）：onsite, remote, hybrid
 - job_type: 工作类型（可选）：full_time, part_time, contract, temporary,
volunteer, internship, other
 - easy_apply: 是否易申请（可选）
 - under_10_applicants: 是否少于10个申请者（可选）
 - fair_chance_employer: 是否公平机会雇主（可选）
  ### 返回:
 - 公司职位列表数据

## get_company_jobs

`GET /api/v1/linkedin/web/get_company_jobs`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_jobs -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取公司在招职位列表（公司主页 'Jobs' 标签）。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 职位数组，每条含
  - job_id: 职位数字 ID（用于后续调 get_job_detail）
  - title: 职位标题
  - location: 工作地点（含 remote 标记）
  - posted_at: 发布时间
  - company_name / company_logo: 公司信息
  - easy_apply: 是否支持一键投递
  - applicants_count: 已申请人数
- data.metadata: 分页信息

## get_company_people

`GET /api/v1/linkedin/web/get_company_people`

<!-- Full path: /api/v1/linkedin/web/get_company_people -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company_id | string | ✅ | 公司ID/Company ID | 1066442 |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn公司员工列表
 ### 参数:
- company_id: 公司ID（必填）
- page: 页码（可选），默认为1
 ### 返回:
- 公司员工列表数据

## get_company_posts

`GET /api/v1/linkedin/web/get_company_posts`

<!-- Full path: /api/v1/linkedin/web/get_company_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company_id | string | ✅ | 公司ID/Company ID | 10649600 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| sort_by | string |  | '排序方式：top(热门)或recent(最新)/Sort by: top or recent' (default: top) | top |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn公司发布的帖子
 ### 参数:
- company_id: 公司ID（必填）
- page: 页码（可选），默认为1
- sort_by: 排序方式（可选），默认为top
    - top: 热门帖子
    - recent: 最新帖子
 ### 返回:
- 公司帖子列表数据

## get_company_posts

`GET /api/v1/linkedin/web/get_company_posts`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取公司主页 'Posts' 标签的内容流（公司账号发布的官方动态、分享、视频、文章）。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 公司帖子数组，每条含
  - 文本内容 / 媒体附件
  - 发布时间 / 互动统计（点赞 / 评论 / 转发 / 浏览数）
  - 文章分享时含原文标题 / URL / 缩略图
- data.metadata: 分页信息

## get_company_profile

`GET /api/v1/linkedin/web/get_company_profile`

<!-- Full path: /api/v1/linkedin/web/get_company_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| company | string |  | 公司名称/Company name | rapidapi |
| company_id | string |  | 公司ID（额外消耗1次请求）/Company ID (+1 request) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn公司资料信息
 ### 参数:
- company: 公司名称（可选）
- company_id: 公司ID（可选，额外消耗1次请求）
 ### 注意:
- company和company_id至少需要提供一个
 ### 返回:
- 公司资料数据

## get_company_profile

`GET /api/v1/linkedin/web/get_company_profile`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取公司主页核心资料数据。
  ### 参数:
 - universal_name: 公司 URL slug，从 LinkedIn URL `/company/<slug>/` 复制（必填）
  ### 返回:
 - data.name: 公司名称
 - data.universal_name: URL slug
 - data.description: 公司简介
 - data.website: 官网 URL
 - data.industry: 所属行业
 - data.employee_count_range: 员工规模区间（如 "1001-5000"）
 - data.followers_count: 关注数
 - data.headquarters: 总部地址
 - data.specialties: 业务专长 / 主营领域列表
 - data.logo: logo（多种尺寸）
 - data.cover: 封面图
 - data.founded_year: 成立年份
 - data.company_type: 公司类型（公开 / 私营 / 非营利等）

## get_company_similar_companies

`GET /api/v1/linkedin/web_v2/get_company_similar_companies`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_similar_companies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回 LinkedIn 在公司主页底部展示的 'People also viewed' 板块数据。
 - 基于"查看过此公司的用户"行为聚合得出，反映用户视角下的相似公司。
 - 与 `get_company_competitors` 区别：similar 偏用户行为聚合，competitors 偏行业 / 业务匹配。
  ### 参数:
 - universal_name: 公司 URL slug（必填）
  ### 返回:
 - data.elements: 相似公司数组，每条含公司名 / logo / 行业 / 员工数 / 公司主页 URL

## get_company_stock_quote

`GET /api/v1/linkedin/web_v2/get_company_stock_quote`

<!-- Full path: /api/v1/linkedin/web_v2/get_company_stock_quote -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug（必须上市）/Public company slug | microsoft |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回上市公司的股价相关数据（仅对**公开上市**公司有效）。
 - 私营公司 / 未上市公司将返回 null。
  ### 参数:
 - universal_name: 公司 URL slug（必须是上市公司）
  ### 返回:
 - data.symbol: 股票代码（如 "MSFT"）
 - data.exchange: 交易所（如 "NASDAQ"）
 - data.price: 当前股价
 - data.change: 涨跌额
 - data.change_pct: 涨跌幅百分比
 - data.market_cap: 市值
 - data.currency: 计价货币（USD / EUR 等）
 - data.last_updated: 最后更新时间

## get_discovery_relevant_to_company

`GET /api/v1/linkedin/web_v2/get_discovery_relevant_to_company`

<!-- Full path: /api/v1/linkedin/web_v2/get_discovery_relevant_to_company -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| universal_name | string | ✅ | 公司URL slug/Company URL slug | microsoft |
| count | integer |  | '' (default: 12) |  |
| start | integer |  | '' (default: 0) |  |
| pagination_token | string |  | 保留兼容字段（当前不分页）/Reserved for future use |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 基于指定公司作为种子，返回 LinkedIn 推荐的相关人员 + 公司列表。
 - 适合做"扩展关注"/"行业图谱"分析。
  ### 参数:
 - universal_name: 公司 URL slug（如 microsoft，必填）
 - count: 兼容字段（当前 LinkedIn 一次返回固定约 7 条，不实际分页）
 - start: 兼容字段
 - pagination_token: 兼容字段
  ### 返回:
 - data.elements: 推荐实体数组，混合人员（profile）+ 公司（company）两种类型
 - 每个 profile 含姓名 / 头衔 / 头像 / 当前职位 / 推荐理由
 - 每个 company 含公司名 / logo / 行业 / 员工数 / 推荐理由

## get_group_info

`GET /api/v1/linkedin/web/get_group_info`

<!-- Full path: /api/v1/linkedin/web/get_group_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| group_id | string | ✅ | 群组ID/Group ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn群组的基本信息
 ### 参数:
- group_id: 群组ID（必填）
 ### 返回:
- 群组信息数据

## get_group_posts

`GET /api/v1/linkedin/web/get_group_posts`

<!-- Full path: /api/v1/linkedin/web/get_group_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| group_id | string | ✅ | 群组ID/Group ID |  |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn群组的帖子
 ### 参数:
- group_id: 群组ID（必填）
- page: 页码（可选），默认为1
 ### 返回:
- 群组帖子数据

## get_hashtag_feed

`GET /api/v1/linkedin/web_v2/get_hashtag_feed`

<!-- Full path: /api/v1/linkedin/web_v2/get_hashtag_feed -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| hashtag | string | ✅ | '话题文本，不带#/Hashtag text without #' | ai |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按话题（hashtag）拉取最近的帖子流。
 - 等价于在 LinkedIn 浏览 `/feed/hashtag/?keywords=<hashtag>`。
  ### 参数:
 - hashtag: 话题文本，**不带 `#` 前缀**（如 `ai`、`machinelearning`）
 - start: 分页起始偏移
 - count: 每页数量（1-50，默认 10）
  ### 返回:
 - data.elements: 帖子数组，每条含
  - 作者信息（姓名 / 头像 / 头衔）
  - 内容文本（含 hashtag 高亮位置）
  - 媒体附件
  - 互动统计 / 发布时间
- data.metadata: 分页信息 + hashtag 元数据（关注此话题的人数等）

## get_job_detail

`GET /api/v1/linkedin/web/get_job_detail`

<!-- Full path: /api/v1/linkedin/web/get_job_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| job_id | string | ✅ | 职位ID/Job ID | 4172815660 |
| include_skills | string |  | 包含职位技能要求（额外消耗1次请求）/Include job skills (+1 request) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn职位详情
 ### 参数:
- job_id: 职位ID（必填）
- include_skills: 包含职位技能要求（可选，额外消耗1次请求）
 ### 返回:
- 职位详情数据

## get_job_detail

`GET /api/v1/linkedin/web/get_job_detail`

<!-- Full path: /api/v1/linkedin/web_v2/get_job_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| job_id | string | ✅ | LinkedIn职位数字ID/LinkedIn job numeric ID | 3902341234 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按 jobId 拉取完整职位详情。
  ### 参数:
 - job_id: LinkedIn 职位数字 ID（从 LinkedIn URL `/jobs/view/<id>/` 复制）
  ### 返回:
 - data.title: 职位标题
 - data.description: 职位详情描述（HTML 或纯文本）
 - data.company: 招聘公司信息（名称 / logo / 主页 URL）
 - data.location: 工作地点（含 remote 标记）
 - data.posted_at: 发布时间
 - data.applicants_count: 已申请人数
 - data.salary_range: 薪资范围（如有，含 currency / period）
 - data.employment_type: 雇佣类型（全职 / 兼职 / 合同 / 实习）
 - data.experience_level: 经验要求（入门 / 中级 / 高级 等）
 - data.required_skills: 技能要求列表
 - data.how_you_fit: 你的匹配度分析（含 connection 中是否有此公司员工）
 - data.easy_apply: 是否支持一键投递
 - data.apply_url: 申请链接（外部站点投递时）

## get_post_comments

`GET /api/v1/linkedin/web/get_post_comments`

<!-- Full path: /api/v1/linkedin/web/get_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 7244804629786419202 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| sort_order | string |  | >- |  |
| post_type | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn帖子的评论
  ### 参数:
 - post_id: 帖子ID（必填）
 - page: 页码（可选），默认为1
 - sort_order: 排序方式（可选），可选值：relevance, recent，默认relevance
 - post_type: 帖子类型（可选），可选值：activity, ugc，默认activity
  ### 返回:
 - 帖子评论数据

## get_post_comments

`GET /api/v1/linkedin/web/get_post_comments`

<!-- Full path: /api/v1/linkedin/web_v2/get_post_comments -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_urn | string | ✅ | 帖子URN/Post URN | urn:li:activity:7193456789012345678 |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 10) |  |
| sort_order | string |  | 评论排序：RELEVANCE / CHRON / REVERSE_CHRON / MEMBER_SETTING (default: RELEVANCE) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取一条帖子下的**顶层**评论列表（不含回复，回复请用 `get_comment_replies`）。
  ### 参数:
 - post_urn: 帖子 URN（接受多种形式，同 `get_post_detail`）
 - start: 分页起始偏移
 - count: 每页数量（1-50，默认 10）
 - sort_order: 评论排序方式
  - `RELEVANCE`（默认）：相关性优先
  - `CHRON`：时间正序（最早在前）
  - `REVERSE_CHRON`：时间倒序（最新在前）
  - `MEMBER_SETTING`：跟随用户偏好设置
 ### 返回:
 - data.elements: 评论数组，每条含
  - comment_urn: 评论 URN（用于后续调 `get_comment_replies`）
  - author: 评论者信息（姓名 / 头像 / 头衔）
  - text: 评论文本
  - posted_at: 评论时间
  - reactions_count: 评论本身的点赞数
  - replies_count: 回复数（>0 时可调 `get_comment_replies`）
- data.metadata: 分页信息

## get_post_detail

`GET /api/v1/linkedin/web/get_post_detail`

<!-- Full path: /api/v1/linkedin/web/get_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 7244804629786419202 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn帖子的详情
 ### 参数:
- post_id: 帖子ID（必填）
 ### 返回:
- 帖子详情数据

## get_post_detail

`GET /api/v1/linkedin/web/get_post_detail`

<!-- Full path: /api/v1/linkedin/web_v2/get_post_detail -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_urn | string | ✅ | 帖子URN或数字ID/Post URN or numeric ID | urn:li:activity:7193456789012345678 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按 post URN 拉取单条帖子的完整数据。
  ### 参数:
 - post_urn: 帖子 URN，接受多种形式（自动归一化）：
  - `urn:li:activity:7193456789012345678`（标准）
  - `urn:li:share:1234567890` / `urn:li:ugcPost:9876543210`
  - `activity:7193456789012345678`（可省略 `urn:li:` 前缀）
  - `7193456789012345678`（纯数字，自动加 `urn:li:activity:` 前缀）
 ### 返回:
 - data.author: 作者信息（姓名 / 头像 / 头衔 / 主页 URL）
 - data.content: 帖子文本（含 mention / hashtag 高亮位置）
 - data.media: 媒体附件（图片 / 视频 / 文档 URL，含多种尺寸）
 - data.engagement: 互动统计（点赞 / 评论 / 转发 / 浏览数）
 - data.published_at: 发布时间戳
 - data.reshare_chain: 转发链路（若是转发帖子，含原帖完整信息）
 - data.is_edited: 是否被编辑过

## get_post_detail_by_slug

`GET /api/v1/linkedin/web_v2/get_post_detail_by_slug`

<!-- Full path: /api/v1/linkedin/web_v2/get_post_detail_by_slug -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| slug | string | ✅ | 帖子URL slug尾段/Post URL slug suffix | satya-nadella_ai-activity-7193456789012345678-AbCd |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按 LinkedIn 分享链接的 URL slug 直接拉取帖子，**无需先解析数字 ID**。
 - 适合从 LinkedIn 推广链接 / 用户分享文本里抓帖子。
  ### 参数:
 - slug: 分享链接 `/posts/<slug>` 的尾段
  - 形如 `<author-slug>_<topic>-activity-<id>-<hash>`
  - 整段从 LinkedIn URL 复制即可
 ### 返回:
 - 同 `get_post_detail`：完整 normalized 帖子数据

## get_post_reactions

`GET /api/v1/linkedin/web/get_post_reactions`

<!-- Full path: /api/v1/linkedin/web/get_post_reactions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 7244804629786419202 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| type | string |  | >- (default: all) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn帖子的点赞/反应记录
  ### 参数:
 - post_id: 帖子ID（必填）
 - page: 页码（可选），默认为1
 - type: 反应类型（可选），可选值：all, like, praise, empathy, appreciation,
interest，默认all
  ### 返回:
 - 帖子反应数据

## get_post_reactions

`GET /api/v1/linkedin/web/get_post_reactions`

<!-- Full path: /api/v1/linkedin/web_v2/get_post_reactions -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_urn | string | ✅ | 帖子URN/Post URN | urn:li:activity:7193456789012345678 |
| reaction_type | string |  | >- | LIKE |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 10) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按反应类型拉取点赞 / 反应过帖子的用户列表。
  ### 参数:
 - post_urn: 帖子 URN（接受多种形式，同 `get_post_detail`）
 - reaction_type: 反应类型，留空则 LinkedIn 默认 LIKE
  - `LIKE`：👍 赞
  - `PRAISE`：👏 鼓掌
  - `EMPATHY`：🤝 关怀
  - `INTEREST`：💡 思考
  - `APPRECIATION`：🙌 支持
  - `MAYBE`：🤔 好奇
  - `ENTERTAINMENT`：😄 趣味
- start: 分页起始偏移
 - count: 每页数量（1-50，默认 10）
  ### 返回:
 - data.elements: 用户数组，每条含
  - public_identifier: URL slug
  - full_name: 全名
  - headline: 一句话头衔
  - profile_picture: 头像 URL
  - reaction_type: 该用户使用的反应类型
- data.metadata: 分页信息

## get_post_reposts

`GET /api/v1/linkedin/web/get_post_reposts`

<!-- Full path: /api/v1/linkedin/web/get_post_reposts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| post_id | string | ✅ | 帖子ID/Post ID | 7244804629786419202 |
| page | string |  | 页码/Page number (default: 1) | 1 |
| pagination_token | string |  | 分页令牌/Pagination token |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取LinkedIn帖子的转发记录
 ### 参数:
- post_id: 帖子ID（必填）
- page: 页码（可选），默认为1
- pagination_token: 分页令牌（可选）
 ### 返回:
- 帖子转发数据

## get_user_comments

`GET /api/v1/linkedin/web/get_user_comments`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_comments -->

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
 - 拉取**用户在他人帖子下发表的评论**列表（用户主页 'Activity → Comments' 标签）。
 - 注意：这**不是**某条帖子的评论列表，那个用 `get_post_comments`。
  ### 参数:
 - username: LinkedIn 用户名（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 评论数组，每条含被评论的原帖摘要 / 评论文本 / 时间戳 / 在原帖中的位置
 - data.metadata: 分页信息

## get_user_follower_and_connection_count

`GET /api/v1/linkedin/web_v2/get_user_follower_and_connection_count`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_follower_and_connection_count -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户主页右上角的两个统计数字：粉丝数 + 一度连接数。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.follower_count: 关注此用户的人数
 - data.connection_count: 一度好友数量（private profile 隐藏时返回 -1）

## get_user_images

`GET /api/v1/linkedin/web/get_user_images`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_images -->

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
 - 拉取用户主页 'Posts → Images' 标签内容（仅图片类型的帖子）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 图片帖子数组，每条含图片 URL（多张时为数组）/ 文案 / 互动统计

## get_user_interested_companies

`GET /api/v1/linkedin/web_v2/get_user_interested_companies`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_interested_companies -->

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
 - 返回用户主动关注的公司列表（同 `get_user_interested_groups`，但实体类型为公司）。
 - 受目标用户隐私设置影响。
  ### 参数:
 - username: LinkedIn 用户名（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 公司数组，每条含公司名称 / logo / 行业 / 员工数 / 公司主页 URL / 简介
 - data.metadata: 分页信息

## get_user_interests_companies

`GET /api/v1/linkedin/web/get_user_interests_companies`

<!-- Full path: /api/v1/linkedin/web/get_user_interests_companies -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| urn | string | ✅ | >- | ACoAAEDH77YBEVIYXAaEwTicp5CcB_hR7DfFL9o |
| page | string |  | 页码/Page number (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户感兴趣的公司
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
  ### 返回:
 - 用户感兴趣的公司列表数据

## get_user_posts

`GET /api/v1/linkedin/web/get_user_posts`

<!-- Full path: /api/v1/linkedin/web/get_user_posts -->

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
 - 获取LinkedIn用户发布的帖子
  ### 参数:
 - urn: 用户URN（必填），可通过get_user_profile接口获取
 - page: 页码（可选），默认为1
 - pagination_token: 分页令牌（可选）
  ### 返回:
 - 用户帖子列表数据

## get_user_posts

`GET /api/v1/linkedin/web/get_user_posts`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |
| start | integer |  | 分页起始偏移/Start offset (default: 0) |  |
| count | integer |  | 每页数量（最大50）/Page size (max 50) (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 拉取 LinkedIn 用户主页 'Posts' 标签按时间倒序的帖子流。
 - 返回所有 mediaType 的完整数据：纯文本 / 图片 / 视频 / 文档 / 文章分享 / 转发等。
  ### 参数:
 - username: LinkedIn 用户名（URL slug，必填）
 - start: 分页起始偏移（默认 0）
 - count: 每页数量（1-50，默认 20）
  ### 返回:
 - data.elements: 帖子数组，每条含作者信息 / 文本内容 / 媒体附件 / 互动统计（点赞 / 评论 / 转发数）/ 发布时间戳
/ 转发链路
 - data.metadata: 分页元数据（含下一页 paginationToken）

## get_user_profile

`GET /api/v1/linkedin/web/get_user_profile`

<!-- Full path: /api/v1/linkedin/web/get_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/LinkedIn username | jack |
| include_follower_and_connection | string |  | >- |  |
| include_experiences | string |  | 包含工作经历（额外消耗1次请求）/Include work experiences (+1 request) |  |
| include_skills | string |  | 包含技能（额外消耗1次请求）/Include skills (+1 request) |  |
| include_certifications | string |  | 包含认证（额外消耗1次请求）/Include certifications (+1 request) |  |
| include_publications | string |  | 包含出版物（额外消耗1次请求）/Include publications (+1 request) |  |
| include_educations | string |  | 包含教育背景（额外消耗1次请求）/Include educational background (+1 request) |  |
| include_volunteers | string |  | 包含志愿者经历（额外消耗1次请求）/Include volunteer experiences (+1 request) |  |
| include_honors | string |  | 包含荣誉奖项（额外消耗1次请求）/Include honors and awards (+1 request) |  |
| include_interests | string |  | 包含兴趣（额外消耗1次请求）/Include interests (+1 request) |  |
| include_bio | string |  | 包含个人简介（额外消耗1次请求）/Include bio/about (+1 request) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取LinkedIn用户资料信息
  ### 参数:
 - username:
LinkedIn用户名（必填），可以从个人资料URL中获取，例如：https://www.linkedin.com/in/jack 则用户名为
jack
 - include_follower_and_connection: 包含粉丝和连接数（可选，额外消耗1次请求）
 - include_experiences: 包含工作经历（可选，额外消耗1次请求）
 - include_skills: 包含技能（可选，额外消耗1次请求）
 - include_certifications: 包含认证（可选，额外消耗1次请求）
 - include_publications: 包含出版物（可选，额外消耗1次请求）
 - include_educations: 包含教育背景（可选，额外消耗1次请求）
 - include_volunteers: 包含志愿者经历（可选，额外消耗1次请求）
 - include_honors: 包含荣誉奖项（可选，额外消耗1次请求）
 - include_interests: 包含兴趣（可选，额外消耗1次请求）
 - include_bio: 包含个人简介（可选，额外消耗1次请求）
  ### 返回:
 - 用户资料数据，包含：
    - id: 用户ID
    - urn: 用户URN
    - public_identifier: 公开标识符
    - first_name: 名
    - last_name: 姓
    - full_name: 全名
    - headline: 头衔/职位描述
    - is_premium: 是否高级会员
    - is_open_to_work: 是否开放工作机会
    - is_hiring: 是否在招聘
    - location: 位置信息
    - cover: 封面图片
    - 以及根据参数选择的其他信息

## get_user_profile

`GET /api/v1/linkedin/web/get_user_profile`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_profile -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/LinkedIn username | williamhgates |
| include_follower_and_connection | string |  | 附带粉丝/连接数 (+1 request)/Include follower & connection count |  |
| include_experiences | string |  | 附带工作经历/Include work experiences |  |
| include_skills | string |  | 附带技能/Include skills |  |
| include_certifications | string |  | 附带认证/Include certifications |  |
| include_publications | string |  | 附带出版物/Include publications |  |
| include_educations | string |  | 附带教育背景/Include educations |  |
| include_volunteers | string |  | 附带志愿者经历/Include volunteer exp |  |
| include_honors | string |  | 附带荣誉奖项/Include honors |  |
| include_interests | string |  | 附带感兴趣的公司+群组/Include interests |  |
| include_bio | string |  | 附带简介/Include bio |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取 LinkedIn 用户主页核心字段（firstName / lastName / headline / industry /
location / 头像 / 封面）。
 - 可选 `include_*` 标志附带子节数据，每个 include 增加约 1-2 秒延迟（**串行**拉取）。
 - 失败的子节以 `{key: {"error": "..."}}` 形式返回，主数据不受影响。
  ### 参数:
 - username: LinkedIn URL slug（如 williamhgates）
 - include_*: 附带各类子节（见参数描述）
  ### 返回:
 - data.profile：主资料对象
 - data.<include_key>：每个 include 对应一个子节数据块
 - data.raw：原始 normalized 响应（调试用）

## get_user_profile_cards

`GET /api/v1/linkedin/web_v2/get_user_profile_cards`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_profile_cards -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 一次返回用户主页**所有**可折叠子节的完整原始数据。
 - 适合需要批量解析多个子节的场景；只需单个子节请用对应专用端点（更轻量）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 覆盖子节:
 - 关于 / 工作经历 / 教育背景 / 认证 / 技能 / 推荐位（Featured）
 - 出版物 / 荣誉奖项 / 志愿者经历 / 推荐信 / 项目 / 语言 / 兴趣
  ### 返回:
 - data.included[]: 所有 section card 数组，每张 card 含 `sectionType` 字段标识类别
 - 调用方按 `sectionType` 在 `data.included[]` 自取
 - 如只需某 section 精简结果，请用对应专用端点（get_user_experiences / get_user_educations
等）

## get_user_top_card

`GET /api/v1/linkedin/web_v2/get_user_top_card`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_top_card -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| username | string | ✅ | LinkedIn用户名/Username | williamhgates |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 返回用户主页头图区的**完整**展示数据。
 - 比 `get_user_bio` 更全面 —— 含视觉资源（背景图 / 头像）+ 关系数据（mutual connections）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
  ### 返回:
 - data.cover_image: 主页背景图 URL
 - data.profile_picture: 头像 URL（多种尺寸）
 - data.full_name: 全名
 - data.headline: 一句话头衔
 - data.current_position: 当前职位（公司 + 标题）
 - data.education: 顶部展示的教育经历
 - data.location: 地理位置
 - data.connection_count: 一度连接数
 - data.follower_count: 粉丝数
 - data.mutual_connections: 与查询账号的共同好友（如有）
 - data.is_premium / is_open_to_work / is_hiring: 状态标记

## get_user_videos

`GET /api/v1/linkedin/web/get_user_videos`

<!-- Full path: /api/v1/linkedin/web_v2/get_user_videos -->

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
 - 拉取用户主页 'Posts → Videos' 标签内容（仅视频类型的帖子）。
  ### 参数:
 - username: LinkedIn 用户名（必填）
 - start: 分页起始偏移
 - count: 每页数量（1-50）
  ### 返回:
 - data.elements: 视频帖子数组，每条含视频地址 / 缩略图 / 时长 / 文案 / 互动统计

## search_jobs

`GET /api/v1/linkedin/web/search_jobs`

<!-- Full path: /api/v1/linkedin/web/search_jobs -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | backend |
| page | string |  | 页码/Page number (default: 1) | 1 |
| sort_by | string |  | '排序方式：recent(最新)或relevant(相关)/Sort by: recent or relevant' |  |
| date_posted | string |  | 发布时间过滤：anytime, past_month, past_week, past_24_hours |  |
| geocode | string |  | 地理位置代码，可通过Search Geocode Location获取/Geocode for location | 103644278 |
| company | string |  | 公司ID过滤/Company ID filter (e.g., 1441 for Google) | 1441 |
| experience_level | string |  | >- |  |
| remote | string |  | 工作地点类型：onsite, remote, hybrid |  |
| job_type | string |  | >- |  |
| easy_apply | string |  | 是否易申请/Filter easy apply jobs |  |
| has_verifications | string |  | 是否有公司认证/Filter jobs with company verifications |  |
| under_10_applicants | string |  | 是否少于10个申请者/Filter jobs with under 10 applicants |  |
| fair_chance_employer | string |  | 是否公平机会雇主/Filter fair chance employer jobs |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索LinkedIn职位
  ### 参数:
 - keyword: 搜索关键词（必填）
 - page: 页码（可选），默认为1
 - sort_by: 排序方式（可选）：recent(最新), relevant(相关)
 - date_posted: 发布时间过滤（可选）：anytime, past_month, past_week, past_24_hours
 - geocode: 地理位置代码（可选）
 - company: 公司ID过滤（可选）
 - experience_level: 经验级别（可选）：internship, entry_level, associate,
mid_senior, director, executive
 - remote: 工作地点类型（可选）：onsite, remote, hybrid
 - job_type: 工作类型（可选）：full_time, part_time, contract, temporary,
volunteer, internship, other
 - easy_apply: 是否易申请（可选）
 - has_verifications: 是否有公司认证（可选）
 - under_10_applicants: 是否少于10个申请者（可选）
 - fair_chance_employer: 是否公平机会雇主（可选）
  ### 返回:
 - 职位搜索结果列表数据

## search_jobs

`GET /api/v1/linkedin/web/search_jobs`

<!-- Full path: /api/v1/linkedin/web_v2/search_jobs -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keywords | string | ✅ | 搜索关键词/Search keyword | machine learning engineer |
| location | string |  | 地点（自由文本）/Location (free text) | San Francisco Bay Area |
| start | integer |  | '' (default: 0) |  |
| count | integer |  | '' (default: 20) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 按关键词 + 地点搜索 LinkedIn 职位。
  ### 参数:
 - keywords: 搜索关键词（必填，如 "machine learning engineer"）
 - location: 地点（自由文本，如 "San Francisco Bay Area"，可省略）
 - start: 分页起始偏移
 - count: 每页数量（1-50，默认 20）
  ### 返回:
 - data.elements: 职位搜索结果数组，每条含
  - job_id: 职位数字 ID（用于后续调 `get_job_detail`）
  - title: 职位标题
  - company_name / company_logo: 公司信息
  - location: 工作地点（含 remote 标记）
  - posted_at: 发布时间
  - easy_apply: 是否支持一键投递
  - applicants_count: 已申请人数
  - salary_range: 薪资范围（如显示）
- data.metadata: 分页信息 + 总命中数

## search_people

`GET /api/v1/linkedin/web/search_people`

<!-- Full path: /api/v1/linkedin/web/search_people -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| name | string |  | 搜索关键词/Search keyword for people | john |
| first_name | string |  | 名/First name | john |
| last_name | string |  | 姓/Last name | oliver |
| title | string |  | 职位/Title | manager |
| company | string |  | 公司/Company |  |
| school | string |  | 学校/School |  |
| page | string |  | 页码/Page number (default: 1) | 1 |
| geocode_location | string |  | 地理位置代码/Geocode for location (e.g., 103644278 for United States) | 103644278 |
| current_company | string |  | 当前公司ID/Current company ID |  |
| profile_language | string |  | 个人资料语言/Profile language |  |
| industry | string |  | 行业ID/Industry ID |  |
| service_category | string |  | 服务类别ID/Service category ID |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 搜索LinkedIn用户
 ### 参数:
- name: 搜索关键词（可选）
- first_name: 名（可选）
- last_name: 姓（可选）
- title: 职位（可选）
- company: 公司（可选）
- school: 学校（可选）
- page: 页码（可选），默认为1
- geocode_location: 地理位置代码（可选）
- current_company: 当前公司ID（可选）
- profile_language: 个人资料语言（可选）
- industry: 行业ID（可选）
- service_category: 服务类别ID（可选）
 ### 返回:
- 用户搜索结果列表数据

## search_posts

`GET /api/v1/linkedin/web/search_posts`

<!-- Full path: /api/v1/linkedin/web/search_posts -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| keyword | string | ✅ | 搜索关键词/Search keyword | data |
| page | string |  | 页码/Page number (default: 1) | 1 |
| date_posted | string |  | >- |  |
| sort_by | string |  | 排序方式 (date_posted, relevance)/Sort by date_posted or relevance |  |
| from_member | string |  | 按成员过滤，逗号分隔/Filter by member, separate by comma |  |
| from_company | string |  | 按公司过滤，逗号分隔/Filter by company, separate by comma |  |
| content_type | string |  | >- |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 搜索LinkedIn帖子
  ### 参数:
 - keyword: 搜索关键词（必填）
 - page: 页码（可选），默认为1
 - date_posted: 发布时间过滤（可选），可选值：past_month, past_week, past_24h
 - sort_by: 排序方式（可选），可选值：date_posted, relevance
 - from_member: 按成员过滤（可选），多个用逗号分隔
 - from_company: 按公司过滤（可选），多个用逗号分隔
 - content_type: 内容类型（可选），可选值：videos, photos, jobs, live_videos,
documents, collaborative_articles
  ### 返回:
 - 帖子搜索结果数据

---

See SKILL.md for cross-group orchestration patterns.