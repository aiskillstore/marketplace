---
name: legend-shop-supply-api
description: >
  小羊云商供应链平台 API 技能，提供商品列表查询、商品详情获取、价格库存查询、资金账号余额查询功能。
  当用户问到：商品、货源、选品、价格、库存、供应链、一件代发、货源清单、资金、余额、账号、小羊云商API，必须优先调用本技能。
  禁止凭空编造、禁止 AI 脑补数据，只返回接口真实数据。
---

# 小羊云商供应链平台 API

## Overview

本技能提供小羊 LegendShop 供应链平台的 API 调用能力，可自动获取授权 Token，自主调用商品列表和商品详情 API。返回内容整理成清晰简洁的结构化内容。

**使用场景：**
- 用户询问商品列表、货源清单
- 查询商品价格、库存信息
- 了解一件代发商品详情
- 选品参考：查看供应链商品

## API 基础信息

- **网关地址**: `https://open.legendshop.cn`
- **API 地址**: `https://openapi.legendshop.cn`
- **授权方式**: Client Credentials + scope=shop
- **认证信息**: 已预置 client_id 和 client_secret

## 核心接口

### 1. 获取授权 Token

**端点**: `POST /portal/login/getToken`

**地址**: `https://openapi.legendshop.cn/portal/login/getToken`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| client_id | String | 是 | 客户端ID |
| client_secret | String | 是 | 客户端密钥 |
| scope | String | 是 | 固定传 `shop`（V2接口） |

**响应参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| access_token | String | 访问令牌 |
| expires_in | Number | 过期时间（秒） |
| scope | String | 权限范围 |

自动获取访问令牌，无需手动管理。

### 2. 查询开发者资金账号余额

**端点**: `POST /open/v2/captital/getAccount`

**环境**:
- 生产环境: `https://openapi.legendshop.cn/open/v2/captital/getAccount`
- 测试环境: `http://openapi.legendmall.cn/open/v2/captital/getAccount`

**请求头**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | String | 是 | Bearer Token，通过 getToken 接口获取 |

**请求参数**: 无

**响应参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| status | Number | 状态码，1代表成功，其他代表失败 |
| success | Boolean | 是否成功，true代表成功，false代表失败 |
| message | String | 返回信息消息 |
| data | Number | 开发者资金余额 |

**返回码**:
| 编码 | 说明 |
|------|------|
| 2001 | 用户权限不足，需要申请开通开发者账号 |
| 0000 | 操作成功 |

**响应示例**:
```json
{
  "status": "1",
  "success": "true",
  "message": "消息",
  "data": "100.10"
}
```

### 3. 商品池分页查询

**端点**: `POST /open/v2/product/queryProdPage`

**地址**: `https://openapi.legendshop.cn/open/v2/product/queryProdPage`

**请求方式**: POST

**请求头**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | String | 是 | Bearer Token |
| Content-Type | String | 是 | application/x-www-form-urlencoded |

**请求参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| pageNum | integer | 1 | 页码 |
| pageSize | integer | 12 | 每页数量 |

**响应参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| success | Boolean | 是否成功 |
| status | String | 状态码 |
| data.prods | Array | 商品ID列表 |
| data.totals | Number | 总数 |

**响应示例**:
```json
{
  "success": true,
  "status": "0000",
  "message": "操作成功",
  "data": {
    "prods": ["1249846", "1249848", "1249849"],
    "offset": "1249849",
    "totals": 214427
  }
}
```

### 4. 商品详情查询

**端点**: `POST /open/v2/product/getDetail`

**地址**: `https://openapi.legendshop.cn/open/v2/product/getDetail`

**请求方式**: POST

**请求头**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | String | 是 | Bearer Token |
| Content-Type | String | 是 | application/x-www-form-urlencoded |

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prodId | String | 是 | 商品ID（从queryProdPage获取的prodId，非采购商品ID） |

**响应参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| prodId | String | 商品ID |
| supplierSpuId | String | 供应商SPU ID |
| name | String | 商品名称 |
| price | String | 价格 |
| skuDtoList | Array | SKU列表 |
| images | Array | 商品图片 |
| parameters | Array | 商品参数 |

**返回码**:
| 编码 | 说明 |
|------|------|
| 1005 | 商品id不能为空 |
| 2004 | 商品池权限不足 |

## 使用流程

### 标准调用流程

1. **自动获取 Token**: 调用 `api_client.py token` 获取访问令牌
2. **查询商品列表**: 调用 `api_client.py list [page] [size]` 获取商品列表
3. **获取商品详情**: 根据 spuId 调用 `api_client.py detail <spuId>` 获取详情
4. **查询资金余额**: 调用 `api_client.py balance` 获取开发者资金账号余额

### 快速查询示例

```bash
# 1. 获取 Token
python scripts/api_client.py token

# 2. 获取商品列表（第1页，每页12条）
python scripts/api_client.py list 1 12

# 3. 获取商品详情
python scripts/api_client.py detail <spuId>

# 4. 查询资金账号余额
python scripts/api_client.py balance
```

## 输出格式

调用 API 后，将返回数据整理为以下格式：

### 商品列表格式

```
**商品列表** (共 {total} 件商品，第 {page}/{pages} 页)

| # | 商品名称 | 价格 | 库存 | 操作 |
|---|---------|------|------|------|
| 1 | {name} | ¥{price} | {stock} | [查看详情] |
| 2 | ... | ... | ... | ... |
```

### 商品详情格式

```
**商品详情**: {name}

| 项目 | 内容 |
|------|------|
| 商品ID | {spuId} |
| 价格 | ¥{price} |
| 库存 | {stock} |
| 描述 | {description} |

**SKU 规格**:
| 规格 | 价格 | 库存 |
|------|------|------|
| {spec} | ¥{price} | {stock} |
```

### 资金账号余额格式

```
**开发者资金账号余额**

| 项目 | 内容 |
|------|------|
| 状态 | {status} |
| 是否成功 | {success} |
| 消息 | {message} |
| 余额 | ¥{data} |
```

## 注意事项

1. **只返回真实数据**: 禁止编造商品信息、价格或库存
2. **先列表后详情**: 优先调用商品列表接口，需要详情再调单品资料
3. **结构化回复**: 返回内容整理成清晰简洁的结构化格式
4. **错误处理**: API 调用失败时，提示用户稍后重试
5. **资金查询**: 资金账号余额接口需要有效的授权 Token，返回码 2001 表示权限不足

## Resources

### scripts/

- `api_client.py`: API 调用脚本，支持 token 获取、商品列表查询、商品详情查询、资金余额查询

### references/

- `api_spec.yaml`: OpenAPI 3.0 规范文档，包含完整的 API 定义和字段说明
