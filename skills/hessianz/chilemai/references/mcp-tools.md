# MCP 工具速查

本文件是「吃了麦」会用到的麦当劳 MCP 工具清单与**最容易传错的参数规则**。
工具全名以 `mcd-mcp` 为准；Server 地址 `https://mcp.mcd.cn`（streamable HTTP）。

## 一、先记住这张表：beType / orderType / beCode

这是全部踩坑的来源。**传错直接报错，或拿到错误门店的数据。**

| 场景 | beType | orderType | beCode | 门店来自 | storeCode 从哪拿 |
| --- | ---: | ---: | --- | --- | --- |
| 到店自取 | 1 | 1 | **不传**（传了报错） | `query-nearby-stores` | 同上 |
| 得来速车道 | 5 | 1 | **必传** | `query-nearby-stores` | 同上 |
| 麦乐送外送 | 2 | 2 | **必传** | `delivery-query-stores` | 同上 |
| 企业团餐 | 6 | 2 | **必传** | `delivery-query-stores` | 同上 |

补充规则：

- `takeWayCode`：仅 `orderType=1`（到店自取 / 得来速）需要，取值来自
  `calculate-price` 返回的 `data.takeWayList[].code`
- `addressId`：仅 `orderType=2` 需要，来自 `delivery-query-addresses`
- `reservationDate`：只有**预约**场景才传（格式 `yyyy-MM-dd HH:mm`），即时单不要传
- `gmServiceCode`：仅企业团餐（`beType=6`），来自 `query-meal-assistance`

## 二、工具分组

### 1. 门店

| 工具 | 用途 | 关键参数 |
| --- | --- | --- |
| `query-nearby-stores` | 到店 / 得来速门店 | `beType`、`searchType`(1 收藏 / 2 按位置)、`city`、`keyword` |
| `delivery-query-addresses` | 外送地址列表 | 无 |
| `delivery-create-address` | 新建配送地址 | `city`、`contactName`、`phone`、`address`、`addressDetail`、`gender` |
| `delivery-query-stores` | 某地址可配送门店 | `addressId`、`beType`(2 或 6) |

`searchType=2` 时 `city` 与 `keyword` **都必填**。`searchType=1` 读收藏，
用户指定收藏店时使用；用户要求离当前位置最近时，直接按已确认的 city + keyword 搜索，
不要用收藏店代替最近门店。

### 2. 餐品与营养

| 工具 | 用途 | 关键参数 |
| --- | --- | --- |
| `query-meals` | 在售餐品与价格 | `storeCode`、`orderType`、`beType`、(`beCode`)、`reservationDate` |
| `query-meal-detail` | 餐品组成 / 可特调项 | `storeCode`、`orderType`、`beType`、`code` |
| `list-nutrition-foods` | 营养数据（无需门店） | 无 |

`query-meals` 返回结构：`data.categories[]`（分类 + 餐品 code 列表）与
`data.meals{code: {name, currentPrice, originalPrice, ...}}`。**下单用的 `productCode`
就是这里的 `code`。**

`list-nutrition-foods` 的 `data` 是**自定义文本格式，不是 JSON**：

```
[160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
  猪柳麦满分,null,1288,308,16,16,24,781,213
```

用 `scripts/chilemai.py` 解析，别手撕。

### 3. 价格与优惠

| 工具 | 用途 | 关键参数 |
| --- | --- | --- |
| `calculate-price` | 算含优惠价格 | `storeCode`、`orderType`、`beType`、`items[]` |
| `available-coupons` | 可领取的券 | 无 |
| `auto-bind-coupons` | 一键领取全部可领券 | 无 |
| `query-my-coupons` | 卡包里的券（**不校验可用性**） | `page`、`pageSize` |
| `query-store-coupons` | 指定门店 + 订单类型**真正可用**的券 | `storeCode`、`orderType`、`beType`、(`beCode`) |
| `query-promotions` | 团餐满减 / 满折规则 | 仅 `beType=6` |

⚠️ `calculate-price` 与 `create-order` 的价格字段单位是**分**，展示前 ÷100。

⚠️ 判断"这张券能不能用"必须走 `query-store-coupons`；`query-my-coupons`
只表示用户**拥有**这张券。

### 4. 下单与订单

| 工具 | 用途 | 关键参数 |
| --- | --- | --- |
| `query-meal-assistance` | 团餐助餐服务（算价前） | `storeCode`、`beType=6` |
| `create-order` | 创建订单 | 见下方 |
| `query-order` | 查订单详情 / 支付后核对 | `orderId` |
| `order-list` | 历史订单 | 无 |
| `cancel-order` | 取消订单 | `orderId`、`cancelReasonCode` |

`cancel-order` 的 `cancelReasonCode` 取值：`1` 改主意了、`2` 重复下单、
`3` 点错了/点多了、`4` 地址电话填错了、`5` 送达时间选错了、`-1` 其它。

### 5. 会员（可选）

`query-my-account`（积分）、`campaign-calendar`（活动日历）、`now-time-info`（当前时间）、
`mall-*`（积分商城）、`draw-lottery` / `query-my-prizes`（抽奖与奖品）。

`now-time-info` 在需要判断"今天/明天"来匹配早餐、夜宵时段时有用。

## 三、下单必需参数清单

`create-order` 前逐项核对：

- [ ] `storeCode`
- [ ] `orderType` 与 `beType` 配对正确（见第一节表）
- [ ] `beCode`：到店自取**不传**，其余三种**必传**
- [ ] `takeWayCode`：`orderType=1` 必传，来自 `calculate-price`
- [ ] `addressId`：`orderType=2` 必传
- [ ] `items[]`：每项 `productCode` + `quantity`；用券再加 `couponId` / `couponCode`
- [ ] 用户已确认方案与价格

## 四、错误对照

| 现象 | 大概率原因 |
| --- | --- |
| 到店自取报错 | 多传了 `beCode` |
| 得来速/外送/团餐报错 | 漏传 `beCode` |
| 价格算出来是 0 或异常 | `productCode` 不是 `query-meals` 返回的 `code` |
| 门店查不到 | `searchType=2` 少了 `city` 或 `keyword` |
| 券不生效 | 用了 `query-my-coupons` 的券但没验 `query-store-coupons` |
| 预约失败 | `reservationTimeOptions` 里的时段没完整展示给用户，或漏传 `reservationDate` |
