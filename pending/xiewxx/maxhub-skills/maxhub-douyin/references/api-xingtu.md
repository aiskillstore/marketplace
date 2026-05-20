# Xingtu API / 星图接口

Base URL: `https://www.aconfig.cn`
Auth: `Authorization: Bearer $MAXHUB_API_KEY`

---
## fetch_product_coupon

`GET /api/v1/douyin/web/fetch_product_coupon`

<!-- Full path: /api/v1/douyin/web/fetch_product_coupon -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| product_id | string | ✅ | 商品ID/Product ID | 3770337983790711029 |
| shop_id | string | ✅ | 店铺ID/Shop ID | 129508461 |
| price | string | ✅ | 价格/Price | 1490 |
| author_id | string | ✅ | 作者ID/Author ID | 3109048548866375 |
| sec_user_id | string | ✅ | 作者ID/Secure Author ID | >- |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

获取商品优惠券相关信息

## fetch_share_info_by_share_code

`GET /api/v1/douyin/app/v3/fetch_share_info_by_share_code`

<!-- Full path: /api/v1/douyin/app/v3/fetch_share_info_by_share_code -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| share_code | string | ✅ | 分享口令/Share code | 8:/ h@O.kP 05/21 【生意场上，装逼就是节省沟通成本】长按复制打开抖音，即可阅读文章 ︽︽2QnCB9aIZZ29︽︽ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 根据分享口令获取分享信息，比如抖音文章的分享口令提取分享人信息和文章ID等然后再去请求单一作品数据接口获取文章内容。
 ### 参数:
 - share_code: 分享口令
 ### 返回:
 - 分享信息，包含分享人信息和文章ID等

## generate_douyin_short_url

`GET /api/v1/douyin/app/v3/generate_douyin_short_url`

<!-- Full path: /api/v1/douyin/app/v3/generate_douyin_short_url -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| url | string | ✅ | 抖音链接/Douyin link | https://www.douyin.com/passport/web/logout/ |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成抖音短链接
### 参数:
- url: 抖音链接
### 返回:
- 短链接数据

## generate_real_msToken

`GET /api/v1/douyin/web/generate_real_msToken`

<!-- Full path: /api/v1/douyin/web/generate_real_msToken -->

### Parameters

No parameters required.

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 生成真实msToken
### 返回:
- msToken

## get_xingtu_kolid_by_unique_id

`GET /api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`

<!-- Full path: /api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| unique_id | string | ✅ | 抖音号/Douyin User unique_id | m6640150 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
- 通过抖音号获取游客星图kolid
### 参数:
- unique_id: 抖音号, 可以从接口以下接口获取：
    - `/api/v1/douyin/web/handler_user_profile`
    - `/api/v1/douyin/web/handler_user_profile_v2`
    - `/api/v1/douyin/web/handler_user_profile_v3`
    - `/api/v1/douyin/app/v3/handler_user_profile`
### 返回:
- 游客星图kolid

## kol_base_info_v1

`GET /api/v1/douyin/xingtu/kol_base_info_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_base_info_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| platformChannel | string | ✅ | 平台渠道/Platform Channel | _1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol基本信息V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- platformChannel:
    - 平台渠道，支持以下参数:
    - _1 :抖音短视频(Video)
    - _10 :抖音直播(Live)
### 返回:
 - kol基本信息

## kol_cp_info_v1

`GET /api/v1/douyin/xingtu/kol_cp_info_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_cp_info_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol性价比能力分析V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
### 返回:
 - kol性价比能力分析

## kol_service_price_v1

`GET /api/v1/douyin/xingtu/kol_service_price_v1`

<!-- Full path: /api/v1/douyin/xingtu/kol_service_price_v1 -->

### Parameters

| Parameter | Type | Required | Description | Example |
|---|---|---|---|---|
| kolId | string | ✅ | 用户的kolId/User kolId | 7048929565493690398 |
| platformChannel | string | ✅ | 平台渠道/Platform Channel | _1 |

### Response

Standard MaxHub response: `{code, message, message_zh, data, cache_url}`

### Description

### 用途:
 - 获取kol服务报价V1
 - 该接口数据使用企业账号进行请求，收费较贵。
 ### 参数:
 - kolId: 用户的kolId, 可以从接口以下接口获取：
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_uid`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_sec_user_id`
    - `/api/v1/douyin/xingtu/get_xingtu_kolid_by_unique_id`
- platformChannel:
    - 平台渠道，支持以下参数:
    - _1: 抖音短视频(Video)
    - _10: 抖音直播(Live)
### 返回:
 kol服务报价

---

See SKILL.md for cross-group orchestration patterns.