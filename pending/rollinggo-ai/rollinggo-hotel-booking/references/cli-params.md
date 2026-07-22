# CLI 命令完整参数规范

## 目录

- [hotel-tags](#hotel-tags) — 获取搜索标签
- [search-hotels](#search-hotels) — 搜索酒店
- [hotel-detail](#hotel-detail) — 酒店详情
- [price-confirm](#price-confirm) — 价格确认
- [book](#book) — 创建订单
- [orders](#orders) — 查询订单

---

## hotel-tags

获取所有可用的酒店筛选标签，用于构建搜索条件。

**输入**：无

**输出**：

| 字段 | 类型 | 说明 |
|------|------|------|
| tags | array | 标签列表 |
| tags[].name | string | 标签名称（用于 required-tag） |
| tags[].category | string | 标签分类（核心设施、服务与餐饮、景观与房型、特色卖点、交通与支付、品牌与评分、酒店类型、亲子家庭、价格相关、服务细节） |
| tags[].description | string | 标签描述 |

---

## search-hotels

根据地点、日期、标签等条件搜索酒店列表。

**输入**：

| CLI 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --origin-query | string | ✅ | 用户原始查询语句 |
| --place | string | ✅ | 地点名称（城市、景点、酒店名等） |
| --place-type | string | ✅ | 地点类型：城市/机场/景点/火车站/地铁站/酒店/区/县/详细地址 |
| --country-code | string | ❌ | 国家代码（如 CN） |
| --size | integer | ❌ | 返回数量，默认 5，最大 20 |
| --check-in-date | string | ❌ | 入住日期 YYYY-MM-DD |
| --stay-nights | integer | ❌ | 入住晚数，默认 1 |
| --adult-count | integer | ❌ | 每间房成人数，默认 2 |
| --star-ratings | string | ❌ | 星级范围，如 "4.5,5.0" |
| --distance-in-meter | integer | ❌ | 距离限制（米），景点类地点生效，默认 5000 |
| --preferred-brand | string | ❌ | 偏好品牌（模糊匹配） |
| --required-tag | string | ❌ | 必须标签（硬约束，未命中过滤） |
| --max-price-per-night | float | ❌ | 每晚最高价格（人民币） |

**输出**：

| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 搜索结果消息 |
| hotelInformationList | array | 酒店列表 |
| hotelInformationList[].hotelId | integer | 酒店 ID |
| hotelInformationList[].name | string | 酒店名称（含英文名） |
| hotelInformationList[].brand | string | 品牌（可为 null） |
| hotelInformationList[].address | string | 地址 |
| hotelInformationList[].destinationId | string | 目的地 ID |
| hotelInformationList[].latitude | float | 纬度 |
| hotelInformationList[].longitude | float | 经度 |
| hotelInformationList[].distanceInMeters | integer | 距目标地点距离（米） |
| hotelInformationList[].starRating | float | 星级 |
| hotelInformationList[].areaCode | string | 国家/地区代码 |
| hotelInformationList[].price.hasPrice | boolean | 是否有价格 |
| hotelInformationList[].price.currency | string | 币种 |
| hotelInformationList[].price.lowestPrice | float | 最低价格 |
| hotelInformationList[].price.message | string | 价格消息 |
| hotelInformationList[].imageUrl | string | 酒店图片 URL |
| hotelInformationList[].bookingUrl | string | 预订链接 |
| hotelInformationList[].description | string | 酒店描述（HTML 格式） |
| hotelInformationList[].hotelAmenities | array[string] | 酒店设施列表（含收费标注） |
| hotelInformationList[].tags | array[string] | 酒店标签 |

---

## hotel-detail

查询单个酒店的所有可售房型和实时价格。

**输入**：

| CLI 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --hotel-id | integer | 二选一 | 酒店 ID（优先） |
| --name | string | 二选一 | 酒店名称（模糊匹配） |
| --check-in-date | string | ❌ | 入住日期 YYYY-MM-DD |
| --check-out-date | string | ❌ | 离店日期 YYYY-MM-DD |
| --room-count | integer | ❌ | 房间数，默认 1 |
| --adult-count | integer | ❌ | 每间房成人数，默认 2 |
| --child-count | integer | ❌ | 每间房儿童数，默认 0 |
| --child-age | string | ❌ | 儿童年龄（逗号分隔） |
| --country-code | string | ❌ | 国家代码，默认 CN |
| --currency | string | ❌ | 币种，默认 CNY |

**输出**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| errorMessage | string | 错误信息（失败时） |
| hotelId | integer | 酒店 ID |
| name | string | 酒店名称（含英文） |
| nameEn | string | 酒店英文名 |
| checkIn | string | 入住日期 |
| checkOut | string | 离店日期 |
| bookingUrl | string | 预订链接 |
| roomRatePlans | array | 房型价格方案列表 |
| roomRatePlans[].roomTypeId | integer | 房型 ID |
| roomRatePlans[].roomName | string | 房型名称（英文） |
| roomRatePlans[].roomNameCn | string | 房型名称（中文） |
| roomRatePlans[].ratePlanId | string | 价格方案 ID（传入 price-confirm） |
| roomRatePlans[].ratePlanName | string | 价格方案名称 |
| roomRatePlans[].bedType | integer | 床型代码 |
| roomRatePlans[].bedTypeDescription | string | 床型描述（如"1 大床"、"2 单人床"） |
| roomRatePlans[].currency | string | 币种 |
| roomRatePlans[].totalPrice | float | 总价（含税） |
| roomRatePlans[].totalSalesRate | float | 每晚均价（可为 null） |
| roomRatePlans[].inventoryCount | integer | 剩余库存数（可为 null） |
| roomRatePlans[].isOnRequest | boolean | 是否需要人工确认（可为 null） |
| roomRatePlans[].cancellationPolicies | array | 取消政策列表 |
| roomRatePlans[].cancellationPolicies[].fromDate | string | 取消费用生效时间（ISO 8601） |
| roomRatePlans[].cancellationPolicies[].toDate | string | 截止时间（可为 null） |
| roomRatePlans[].cancellationPolicies[].amount | float | 取消费用金额 |
| roomRatePlans[].cancellationPolicies[].percent | integer | 取消费用百分比（可为 null） |
| roomRatePlans[].cancellationPolicies[].description | string | 取消政策描述（可为 null） |

---

## price-confirm

锁定选定房型的实时价格，获取预订参考号。referenceNo 有效期约 15-30 分钟，过期需重新调用。

**输入**：

| CLI 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --hotel-id | integer | ✅ | 酒店 ID |
| --rate-plan-id | string | ✅ | 价格方案 ID（从 hotel-detail 获取） |
| --rooms | integer | ✅ | 房间数量 |
| --check-in-date | string | ✅ | 入住日期 YYYY-MM-DD |
| --check-out-date | string | ✅ | 离店日期 YYYY-MM-DD |
| --adults | integer | ✅ | 每间房成人数 |
| --children | integer | ❌ | 每间房儿童数 |
| --child-age | string | ❌ | 儿童年龄（逗号分隔） |
| --nationality | string | ❌ | 国籍代码，默认 CN |
| --currency | string | ❌ | 币种，默认 CNY |

**输出**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| message | string | 结果消息 |
| priceDetailsInfo.referenceNo | string | 预订参考号（传入 book） |
| priceDetailsInfo.checkInDate | string | 入住日期 |
| priceDetailsInfo.checkOutDate | string | 离店日期 |
| priceDetailsInfo.hotelList | array | 酒店列表 |
| priceDetailsInfo.hotelList[].hotelName | string | 酒店名称 |
| priceDetailsInfo.hotelList[].totalPrice | float | 锁定总价 |
| priceDetailsInfo.hotelList[].ratePlanList | array | 房型价格方案列表 |
| priceDetailsInfo.hotelList[].ratePlanList[].roomName | string | 房型名称 |
| priceDetailsInfo.hotelList[].ratePlanList[].totalPrice | float | 总价 |
| priceDetailsInfo.hotelList[].ratePlanList[].averagePrice | float | 每晚均价 |
| priceDetailsInfo.hotelList[].ratePlanList[].priceList | array | 每日价格列表 |
| priceDetailsInfo.hotelList[].cancellationPolicyList | array | 取消政策 |

---

## book

使用 referenceNo 创建正式订单，返回支付链接。

**输入**：

| CLI 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --reference-no | string | ✅ | 预订参考号（从 price-confirm 获取） |
| --first-name | string | ✅ | 联系人名（拼音或英文） |
| --last-name | string | ✅ | 联系人姓（拼音或英文） |
| --email | string | ✅ | 联系邮箱 |
| --guests | string | ❌ | 客人信息 JSON（一般不需要，默认使用联系人信息） |

**输出**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| message | string | 结果消息（失败时含原因） |
| bookingResult.orderNo | string | 订单号 |
| bookingResult.paymentType | string | 支付类型（当前固定为 "URL"） |
| bookingResult.paymentUrl | string | 支付链接 |

---

## orders

查询当前用户的所有历史酒店订单。

**输入**：无

**输出**：

| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | 查询结果消息 |
| orderInfoList | array | 订单列表 |
| orderInfoList[].hotelBookingInfo.referenceNo | string | 预订参考号 |
| orderInfoList[].hotelBookingInfo.status | string | 订单状态码（"1"=待支付，"3"=已完成/已关闭） |
| orderInfoList[].hotelBookingInfo.mainOrderNo | string | 主订单号 |
| orderInfoList[].hotelBookingInfo.subOrderNo | string | 子订单号 |
| orderInfoList[].hotelBookingInfo.checkInDate | string | 入住日期 |
| orderInfoList[].hotelBookingInfo.checkOutDate | string | 离店日期 |
| orderInfoList[].hotelBookingInfo.numOfRooms | integer | 房间数 |
| orderInfoList[].hotelBookingInfo.nights | integer | 入住晚数 |
| orderInfoList[].hotelBookingInfo.totalPrice | float | 订单总价 |
| orderInfoList[].hotelBookingInfo.paymentStatus | string | 支付状态（CREATED=待支付，REFUNDED=已退款） |
| orderInfoList[].hotelBookingHotel.hotelName | string | 酒店名称 |
| orderInfoList[].hotelBookingHotel.hotelAddress | string | 酒店地址 |
| orderInfoList[].hotelBookingHotel.starRating | string | 星级 |
| orderInfoList[].hotelContact.firstName | string | 联系人名 |
| orderInfoList[].hotelContact.lastName | string | 联系人姓 |
| orderInfoList[].hotelContact.email | string | 联系邮箱 |
| orderInfoList[].hotelRatePlanInfo.roomName | string | 房型名称 |
| orderInfoList[].hotelRatePlanInfo.totalPrice | float | 总价 |
