# Creator API / 创作者接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_all_area

`GET /api/v1/douyin/index/fetch_all_area`

<!-- Full path: /api/v1/douyin/index/fetch_all_area -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音指数支持的所有地区列表
 ### 返回:
 - 省份和城市的层级结构列表，可用于关键词指数的地区筛选参数

## fetch_author_diagnosis

`POST /api/v1/douyin/creator_v2/fetch_author_diagnosis`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_author_diagnosis -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者账号的诊断数据和优化建议
 - 自动分析最近一周（从当天起往前7天）的账号表现
 - 提供完播率、互动指数等关键指标的评估和改进建议
 - 帮助创作者了解账号健康度，优化内容策略
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
 - **无需指定时间范围，系统自动获取最近7天数据**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
  ### 数据更新时间:
 - **更新周期**: 次日12点更新昨日作品数据
 - **示例**: 2025年10月10日的作品数据会在2025年10月11日12点更新
 - **时间范围**: 自动获取最近一周的数据（从当天起往前7天）
 - **首次使用**: 获取权限后次日起生产数据
  ### 数据指标含义:
  **名词定义**:
 - **同类创作者**: 具有相似创作领域或粉丝量级的创作者
 - **时间粒度**: 时间粒度是数据更新计算的周期
 - **抖音精选**: 包含精选APP+抖音电脑端+抖音APP_精选Tab的数据表现
  **账号诊断类指标**:
 - **投稿数**: 根据统计周期内发布的作品个数得出
 - **互动指数**: 作品的观看、点赞、评论、转发的综合得分
 - **视频播放量**: 作品被观看的次数
 - **视频完播率**: 作品完整播放次数的占比
  - 每日完播率：当日完播浏览量与总浏览量的比值
  - 每十分钟级完播率：累计完播浏览量与累计浏览量的比值
- **粉丝净增量**: 账号净增粉丝数，通过涨粉数减去掉粉数得出
  ### 返回数据说明:
 返回账号诊断数据，包括以下五个核心维度：
  **1. 互动指数 (Interact)**:
 - **OwnValue**: 账号自身的互动指数值（观看、点赞、评论、转发的综合得分）
 - **SimilarCount**: 同类创作者总数
 - **AuthorRank**: 账号在自身历史数据中的排名百分位（0-1之间，越大表示当前表现越好）
 - **SimilarRank**: 账号在同类创作者中的排名百分位（0-1之间，越大表示排名越靠前）
 - **SimilarValue**: 同类创作者的平均互动指数值
 - **解读**: AuthorRank=0.26表示当前互动指数超过了自己历史26%的时期
 - **解读**: SimilarRank=0.52表示在同类创作者中排名超过52%
  **2. 粉丝净增量 (NewFans)**:
 - **OwnValue**: 统计周期内账号净增粉丝数（涨粉数 - 掉粉数）
 - **SimilarCount**: 同类创作者总数
 - **AuthorRank**: 账号在自身历史涨粉数据中的排名百分位
 - **SimilarRank**: 账号在同类创作者中的涨粉排名百分位
 - **SimilarValue**: 同类创作者的平均粉丝净增量
 - **解读**: OwnValue=2表示本周期净增2个粉丝
  **3. 视频播放量 (PlayCnt)**:
 - **OwnValue**: 统计周期内作品被观看的总次数
 - **SimilarCount**: 同类创作者总数
 - **AuthorRank**: 账号在自身历史播放量中的排名百分位
 - **SimilarRank**: 账号在同类创作者中的播放量排名百分位
 - **SimilarValue**: 同类创作者的平均播放量
 - **解读**: OwnValue=192表示本周期总播放量为192次
  **4. 视频完播率 (PlayFinishRatio)**:
 - **OwnValue**: 作品完整播放次数的占比（0-1之间的小数）
 - **SimilarCount**: 同类创作者总数
 - **AuthorRank**: 账号在自身历史完播率中的排名百分位
 - **SimilarRank**: 账号在同类创作者中的完播率排名百分位
 - **SimilarValue**: 同类创作者的平均完播率
 - **解读**: OwnValue=0.15表示完播率为15%
 - **提升建议**: "想要作品吸引人，前3秒钟是关键，可以多分析同行业热门作品的人设、镜头技巧和音乐"
  **5. 投稿活跃度 (PublishActivation)**:
 - **OwnValue**: 统计周期内发布的作品个数
 - **SimilarCount**: 同类创作者总数
 - **AuthorRank**: 账号在自身历史投稿数据中的排名百分位
 - **SimilarRank**: 账号在同类创作者中的投稿活跃度排名百分位
 - **SimilarValue**: 同类创作者的平均投稿数
 - **解读**: OwnValue=2表示本周期发布了2个作品
  ### 返回数据结构示例:
 ```json
 {
    "code": 0,
    "data": {
        "Interact": {
            "OwnValue": 0.0052,
            "SimilarCount": 1494654282,
            "AuthorRank": 0.2633,
            "SimilarRank": 0.5169,
            "SimilarValue": 0.0909
        },
        "NewFans": {
            "OwnValue": 2,
            "AuthorRank": 0.7924,
            "SimilarRank": 0.6343
        },
        "PlayCnt": {
            "OwnValue": 192,
            "AuthorRank": 0.8427,
            "SimilarRank": 0.5132
        },
        "PlayFinishRatio": {
            "OwnValue": 0.1545,
            "AuthorRank": 0.3851,
            "SimilarRank": 0.5086
        },
        "PublishActivation": {
            "OwnValue": 2,
            "AuthorRank": 0.7345,
            "SimilarRank": 0.5675
        }
    }
}
 ```
  ### 数据解读技巧:
 - **OwnValue**: 查看实际数值，了解账号当前表现
 - **AuthorRank**: 与自己过去比较，数值越高说明当前状态越好
 - **SimilarRank**: 与同行比较，数值越高说明在同类创作者中排名越靠前
 - **建议**: AuthorRank和SimilarRank都低于0.5时需要重点优化该项指标
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_creator_material_center_config

`GET /api/v1/douyin/creator/fetch_creator_material_center_config`

<!-- Full path: /api/v1/douyin/creator/fetch_creator_material_center_config -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取抖音创作者中心配置信息
### 返回:
- 创作者中心配置数据

## fetch_daren_great_item_mile_info

`POST /api/v1/douyin/index/fetch_daren_great_item_mile_info`

<!-- Full path: /api/v1/douyin/index/fetch_daren_great_item_mile_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| user_id | string | ✅ | '达人抖音 uid (纯数字) / Douyin uid (numeric). Example: 3100268042915212' |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取达人核心指标数据
 ### 参数:
 - user_id: 达人抖音 uid（纯数字，如 "3100268042915212"）
 ### 返回:
 - 粉丝数、获赞数、作品数、互动率等核心指标

## fetch_industry_category_config

`GET /api/v1/douyin/creator/fetch_industry_category_config`

<!-- Full path: /api/v1/douyin/creator/fetch_industry_category_config -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者平台的行业分类配置
 - 返回所有可用的行业分类层级结构
 - **建议在调用商单任务列表接口前先调用此接口获取完整的行业分类信息**
  ### 重要说明:
 - 此接口已优化为Redis缓存，首次调用后数据将缓存30天
 - 缓存键: `douyin_creator:industry_categories`
 - 数据结构包含一级行业和二级行业的完整映射关系
  ### 数据结构:
 ```json
 {
    "status_code": 0,
    "status_msg": "success",
    "data": {
        "industry_categories": [
            {"key": "-1", "label": "全部"},
            {"key": 1901, "label": "3C及电器"},
            {"key": 1913, "label": "游戏"},
            ...
        ],
        "industry_subcategories": {
            1913: [
                {"key": "-1", "label": "全部"},
                {"key": 191301, "label": "休闲游戏"},
                {"key": 191302, "label": "棋牌桌游"},
                ...
            ],
            ...
        }
    }
}
 ```
  ### 在商单任务筛选中的使用:
 1. **获取全部行业任务**: `industry_lv1=-1` (此时industry_lv2无需设置)
 2. **获取特定一级行业**: `industry_lv1=1913` (游戏行业)
 3. **获取特定二级行业**: `industry_lv1=1913&industry_lv2=191301` (游戏-休闲游戏)
  ### 性能优化:
 - 首次调用时从本地JSON文件读取并缓存到Redis
 - 后续调用直接从Redis缓存读取，大幅提升响应速度
 - 缓存有效期30天，确保数据时效性
  ### 返回:
 - 返回完整的行业分类树结构
 - 包含32个一级行业分类和对应的二级行业分类
 - 每个分类包含分类ID(key)和名称(label)

## fetch_item_analysis_item_performance

`POST /api/v1/douyin/creator_v2/fetch_item_analysis_item_performance`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_analysis_item_performance -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取投稿作品的表现数据，包括播放量、点赞量、评论量、分享量等指标
 - 分析不同体裁和垂类的内容表现
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
 - **建议先调用 fetch_item_analysis_involved_vertical 接口获取垂类标签**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - start_date: 开始日期，格式YYYYMMDD（必填）
 - end_date: 结束日期，格式YYYYMMDD（必填）
 - genres: 体裁类型列表（可选，默认包含所有体裁）
  - 1: 1分钟以内视频
  - 2: 1-3分钟视频
  - 3: 3-5分钟视频
  - 4: 5分钟以上视频
  - 5: 图文
  - 8: 长图文
- primary_verticals: 垂类标签列表（必填，从 fetch_item_analysis_involved_vertical
接口获取）
 - metric_type: 指标类型（可选，默认为1）
  - 1: 播放量 (Views)
  - 2: 点赞量 (Likes)
  - 3: 评论量 (Comments)
  - 4: 分享量 (Shares)
- **注意：日期范围最多90天**
  ### 返回数据说明:
 - 包含所选指标在不同体裁和垂类下的表现数据
 - 趋势分析、对比数据等
 - 帮助了解内容在各个维度的表现
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_item_analysis_overview

`POST /api/v1/douyin/creator_v2/fetch_item_analysis_overview`

<!-- Full path: /api/v1/douyin/creator_v2/fetch_item_analysis_overview -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取账号投稿作品的综合分析数据
 - 包括不同体裁、垂类的投稿表现统计
 - **此接口需要用户提供有效的抖音创作者平台Cookie**
> ⚠️ **Security Notice / 安全提示**
> - This endpoint requires your platform session Cookie, which is a sensitive credential equivalent to a login session.
> - **Only provide your Cookie if you fully trust the service provider.**
> - Prefer using scoped OAuth/API tokens over full browser cookies when available.
> - Use a separate test account rather than your primary account.
> - Rotate or revoke your Cookie after use if possible.
> - 此端点需要您的平台会话 Cookie，这是等同于登录会话的敏感凭据。
> - **仅在完全信任服务提供商的情况下提供 Cookie。**
> - 尽可能使用范围限定的 OAuth/API 令牌而非完整浏览器 Cookie。
> - 使用独立的测试账号而非主账号。
> - 使用后尽可能轮换或撤销 Cookie。
 - **使用 POST 方法，Cookie 在请求体中传输，更安全**
 - **建议先调用 fetch_item_analysis_involved_vertical 接口获取垂类标签**
  ### 请求体参数:
 - cookie: 用户的抖音创作者平台Cookie（必填，在请求体中传输）
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
> 📋 **Data Handling Disclosure / 数据处理披露**
> - Your Cookie/session data will be transmitted to a third-party API service (`https://www.aconfig.cn`) for processing.
> - The service provider processes your data solely to fulfill the API request and does not store your credentials beyond the request lifecycle.
> - For details, refer to the service provider's privacy policy and terms of service.
> - 您的 Cookie/会话数据将传输至第三方 API 服务进行处理。
> - 服务提供商仅处理您的数据以完成 API 请求，不会在请求生命周期之外存储您的凭据。
> - 详见服务提供商的隐私政策和服务条款。
 - start_date: 开始日期，格式YYYYMMDD（必填）
 - end_date: 结束日期，格式YYYYMMDD（必填）
 - genres: 体裁类型列表（可选，默认包含所有体裁）
  - 1: 1分钟以内视频
  - 2: 1-3分钟视频
  - 3: 3-5分钟视频
  - 4: 5分钟以上视频
  - 5: 图文
  - 8: 长图文
- primary_verticals: 垂类标签列表（必填，从 fetch_item_analysis_involved_vertical
接口获取）
 - **注意：日期范围最多90天**
  ### 返回数据说明:
 - 包含不同体裁和垂类的投稿数据分析
 - 播放量、点赞量、评论量、分享量等指标
 - 不同体裁的内容表现对比
  ### Cookie 获取方式:
 1. 登录抖音创作者平台 (https://creator.douyin.com)
 2. 打开浏览器开发者工具（F12）
 3. 切换到 Network 标签
 4. 刷新页面或进行操作
 5. 找到任意请求，复制 Cookie 请求头的值

## fetch_mission_task_list

`GET /api/v1/douyin/creator/fetch_mission_task_list`

<!-- Full path: /api/v1/douyin/creator/fetch_mission_task_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| cursor | integer |  | 游标/Cursor (分页) (default: 0) | 0 |
| limit | integer |  | 每页数量/Items per page (default: 24) | 24 |
| mission_type | integer |  | 任务类型/Mission type (default: 1) | 1 |
| tab_scene | integer |  | 场景类型/Scene type (1=可投稿, 2=可报名, 3=好物测评) (default: 1) | 1 |
| industry_lv1 | integer |  | 一级行业/Primary industry (-1=全部) (default: -1) | 1913 |
| industry_lv2 | integer |  | 二级行业/Secondary industry (-1=全部) (default: -1) | 191301 |
| platform_channel | string |  | 平台渠道/Platform channel (1=抖音视频, 2=抖音直播, 3=抖音图文) | 1 |
| pay_type | string |  | >- | 4 |
| greater_than_cost_progress | string |  | 成本进度/Cost progress (20=高于20%, 50=高于50%, 80=高于80%) | 20 |
| publish_time_start | string |  | 发布开始时间/Publish start time (时间戳) | 1757097636 |
| quick_selector_scene | string |  | 快速选择场景/Quick selector (1=高收益, 4=保底收入, 5=合作过) |  |
| keyword | string |  | 关键词/Keyword (任务名称或ID) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取抖音创作者平台的商单任务列表
 - 支持多种筛选条件，包括行业分类、付费类型、平台渠道等
  ### 重要参数使用说明:
 #### 行业分类组合规则:
 - **industry_lv1=-1 (全部)**: 当选择全部一级行业时，industry_lv2参数将被忽略，无需设置
 - **industry_lv1=具体值**: 当选择具体一级行业时，可配合industry_lv2进行二级筛选
    - industry_lv2=-1: 该一级行业下的所有二级分类
    - industry_lv2=具体值: 该一级行业下的具体二级分类
 #### 可选参数 (选择"全部"时无需传入):
 - **platform_channel**: 不传入表示全部平台渠道
 - **pay_type**: 不传入表示全部付费类型
 - **greater_than_cost_progress**: 不传入表示不限制成本进度
 - **publish_time_start**: 不传入表示不限制发布时间
 - **quick_selector_scene**: 不传入表示不使用快速筛选
 - **keyword**: 不传入表示不进行关键词搜索
  ### 参数详解:
 - cursor: 游标，用于分页，0表示第一页
 - limit: 每页返回的任务数量，建议24
 - mission_type: 任务类型，通常为1
 - tab_scene: 场景类型
    - 1: 可投稿 (可以直接投稿的任务)
    - 2: 可报名 (需要报名审核的任务)
    - 3: 好物测评 (商品测评类任务)
- industry_lv1/lv2: 行业分类 (建议先调用fetch_industry_category_config获取完整分类)
    - -1: 全部行业
    - 具体数值: 对应具体行业类别 (如1913=游戏, 1903=食品饮料)
- platform_channel: 平台渠道 (可选)
    - 1: 抖音视频
    - 2: 抖音直播
    - 3: 抖音图文
- pay_type: 付费类型 (可选)
    - 1: 视频等级 (按粉丝量等级定价)
    - 2: 自定义 (商家自定义价格)
    - 3: 按转化付费 (按转化效果付费)
    - 4: 按有效播放量 (按播放量付费)
    - 5: 按销售量 (按商品销售量付费)
    - 9: 按核销量 (按核销数量付费)
    - 14: 按付费分佣 (按分佣比例付费)
- greater_than_cost_progress: 成本进度筛选 (可选)
    - 20: 高于20%成本进度的任务
    - 50: 高于50%成本进度的任务
    - 80: 高于80%成本进度的任务
- publish_time_start: 发布开始时间过滤 (可选，时间戳格式)
 - quick_selector_scene: 快速筛选场景 (可选)
    - 1: 高收益任务
    - 4: 保底收入任务
    - 5: 曾经合作过的商家
- keyword: 关键词搜索 (可选，支持任务名称或任务ID)
  ### 使用示例:
 ```
 # 获取全部行业的可投稿任务
 GET /fetch_mission_task_list?industry_lv1=-1&tab_scene=1
  # 获取游戏行业休闲游戏分类的按播放量付费任务
 GET
/fetch_mission_task_list?industry_lv1=1913&industry_lv2=191301&pay_type=4
  # 获取高收益的抖音视频任务
 GET /fetch_mission_task_list?platform_channel=1&quick_selector_scene=1
 ```
  ### 返回:
 - 返回符合条件的商单任务列表
 - 包含任务详情、报酬信息、要求等

## fetch_product_review_list

`GET /api/v1/douyin/web/fetch_product_review_list`

<!-- Full path: /api/v1/douyin/web/fetch_product_review_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 3770337983790711029 |
| shop_id | string | ✅ | 店铺ID/Shop ID | 129508461 |
| cursor | integer |  | 游标/Cursor (default: 0) |  |
| count | integer |  | 数量/Count (default: 20) |  |
| sort_type | integer |  | '排序类型 (0: 默认排序, 1: 最新排序)/Sort Type (0: Default, 1: Latest)' (default: 0) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

## fetch_product_sku_list

`GET /api/v1/douyin/web/fetch_product_sku_list`

<!-- Full path: /api/v1/douyin/web/fetch_product_sku_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 3770337983790711029 |
| author_id | string | ✅ | 作者ID/Author ID | 3109048548866375 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

## get_author_base_info

`GET /api/v1/douyin/xingtu_v2/get_author_base_info`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_base_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| o_author_id | string | ✅ | 创作者ID/Creator author ID | 7589271892177518598 |
| platform_source | integer |  | 平台来源/Platform source (default: 1) | 1 |
| platform_channel | integer |  | 平台渠道/Platform channel (default: 1) | 1 |
| recommend | boolean |  | 是否返回推荐信息/Whether to return recommendation info (default: true) | true |
| need_sec_uid | boolean |  | 是否返回sec_uid/Whether to return sec_uid (default: true) | true |
| need_linkage_info | boolean |  | 是否返回联动信息/Whether to return linkage info (default: true) | true |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作者基本信息
### 参数:
- o_author_id: 创作者ID
- platform_source: 平台来源，默认1
- platform_channel: 平台渠道，默认1
- recommend: 是否返回推荐信息，默认True
- need_sec_uid: 是否返回sec_uid，默认True
- need_linkage_info: 是否返回联动信息，默认True
### 返回:
- 创作者基本信息数据

## get_author_business_card_info

`GET /api/v1/douyin/xingtu_v2/get_author_business_card_info`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_business_card_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| o_author_id | string | ✅ | 创作者ID/Creator author ID | 7589271892177518598 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作者商业卡片信息
### 参数:
- o_author_id: 创作者ID
### 返回:
- 创作者商业卡片信息数据

## get_author_local_info

`GET /api/v1/douyin/xingtu_v2/get_author_local_info`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_local_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| o_author_id | string | ✅ | 创作者ID/Creator author ID | 7146074596666507300 |
| platform_source | integer |  | 平台来源/Platform source (default: 1) | 1 |
| platform_channel | integer |  | 平台渠道/Platform channel (default: 1) | 1 |
| time_range | integer |  | 时间范围(天)/Time range in days (default: 30) | 30 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作者位置信息
### 参数:
- o_author_id: 创作者ID
- platform_source: 平台来源，默认1
- platform_channel: 平台渠道，默认1
- time_range: 时间范围(天)，默认30
### 返回:
- 创作者位置信息数据

## get_author_spread_info

`GET /api/v1/douyin/xingtu_v2/get_author_spread_info`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_author_spread_info -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| o_author_id | string | ✅ | 创作者ID/Creator author ID | 7589271892177518598 |
| platform_source | integer |  | 平台来源/Platform source (default: 1) | 1 |
| platform_channel | integer |  | 平台渠道/Platform channel (default: 1) | 1 |
| type | integer |  | 视频类型，1=个人视频/Video type, 1=personal video (default: 1) | 1 |
| flow_type | integer |  | 流量类型/Flow type (default: 0) | 0 |
| only_assign | boolean |  | 仅看指派视频/Only assigned videos (default: false) | false |
| range | integer |  | 时间范围，2=近30天，3=近90天/Time range, 2=last 30 days, 3=last 90 days (default: 2) | 2 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取创作者商业能力的传播价值信息
### 参数:
- o_author_id: 创作者ID
- platform_source: 平台来源，默认1
- platform_channel: 平台渠道，默认1
- type: 视频类型，1=个人视频
- flow_type: 流量类型，默认0
- only_assign: 仅看指派视频，默认False
- range: 时间范围，2=近30天，3=近90天
### 返回:
- 创作者传播价值数据

## get_excellent_case_category_list

`GET /api/v1/douyin/xingtu_v2/get_excellent_case_category_list`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_excellent_case_category_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| platform_source | integer |  | 平台来源/Platform source (default: 1) | 1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取连接用户漏斗中的优秀行业分类列表
### 参数:
- platform_source: 平台来源，默认1
### 返回:
- 优秀行业分类列表数据

## get_resource_list

`GET /api/v1/douyin/xingtu_v2/get_resource_list`

<!-- Full path: /api/v1/douyin/xingtu_v2/get_resource_list -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| resource_id | integer | ✅ | 资源ID/Resource ID | 1052 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 获取营销活动案例列表
### 参数:
- resource_id: 资源ID
### 返回:
- 营销活动案例数据

## kol_audience_portrait_v1

`GET /api/v1/douyin/xingtu/kol_audience_portrait_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_audience_portrait_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol观众画像V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol观众画像

## kol_conversion_ability_analysis_v1

`GET /api/v1/douyin/xingtu/kol_conversion_ability_analysis_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_conversion_ability_analysis_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| _range | string | ✅ | 时间范围/Time Range | _1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol转化能力分析V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- _range: 时间范围, 支持以下参数:
    - _1 :近7天(last 7 days)
    - _2 :30天(last 30 days)
    - _3 :90天(last 90 days)
### 返回:
 - kol转化能力分析

## kol_data_overview_v1

`GET /api/v1/douyin/xingtu/kol_data_overview_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_data_overview_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| _type | string | ✅ | 类型/Type | _1 |
| _range | string | ✅ | 范围/Range | _2 |
| flowType | integer | ✅ | 流量类型/Flow Type | 1 |
| onlyAssign | boolean |  | 是否指派/Whether assigned (optional) |  |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol数据概览V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- _type: 类型, 支持以下参数:
    - _1 :个人视频(personal video)
    - _2 :星图视频(xingtu video)
- _range: 范围, 支持以下参数:
    - _2 :近30天(last 30 days)
    - _3 :近90天(last 90 days)
- flowType: 流量类型, 支持以下参数:
    - 1 : 默认(default)
- onlyAssign (可选): 是否指派，具体参数如下:
    - 不传递 : 使用API默认行为
    - false : 全部数据
    - true : 仅指派数据
### 返回:
 - kol数据概览

---

See SKILL.md for cross-group orchestration patterns.