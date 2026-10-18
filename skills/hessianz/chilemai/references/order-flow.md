# 四种场景的完整调用序

以「杭州 · 西湖 · 减脂 · 预算 40」为例，把 Phase 1~5 落成具体的工具调用。
示例中的 `storeCode=3330257`、`beCode` 等均来自真实返回值，实际使用时会变化。

---

## 场景 A · 到店自取（beType=1）

最常用。用户想去店里拿了就走。

```
1. query-nearby-stores
   { "beType": 1, "searchType": 2, "city": "杭州市", "keyword": "西湖" }
   → 取距离最近且在营业的门店
   → storeCode = "3330257"   ⚠️ beType=1 不产出 beCode

2. query-meals
   { "storeCode": "3330257", "orderType": 1, "beType": 1 }
   → data.meals{code: {name, currentPrice}}   取 productCode

3. list-nutrition-foods
   { }
   → 存 nutrition.txt，跑 scripts/chilemai.py match / plan 核实匹配与整餐营养

4. query-store-coupons
   { "storeCode": "3330257", "orderType": 1, "beType": 1 }

5. calculate-price
   { "storeCode": "3330257", "orderType": 1, "beType": 1,
     "items": [ { "productCode": "1406", "quantity": 1 },
                { "productCode": "4437", "quantity": 1 } ] }
   → 价格单位是分；记下 data.takeWayList[].code

6. 【给用户看门店、餐品规格与份数、整餐营养、优惠及官方实付，等确认】

7. create-order
   { "storeCode": "3330257", "orderType": 1, "beType": 1,
     "takeWayCode": "<上一步 takeWayList[].code>",
     "items": [ ... 同上 ... ] }
   → 返回支付链接

8. 【用户支付】→ query-order { "orderId": "..." }
```

**易错点**：第 7 步的 `beCode` 一定不要出现。

---

## 场景 B · 得来速车道（beType=5）

和场景 A 几乎一样，只有两点不同：

- 门店查询用 `beType=5`，返回值**带 `beCode`**，后续每次调用都要带上
- 取餐方式通过 `takeWayCode` 表达

```
1. query-nearby-stores { "beType": 5, "searchType": 2, "city": "杭州市", "keyword": "西湖" }
   → 同时记下 storeCode 与 beCode
2. query-meals { "storeCode": "...", "orderType": 1, "beType": 5, "beCode": "..." }
3. list-nutrition-foods { }
4. calculate-price { "storeCode": "...", "orderType": 1, "beType": 5, "beCode": "...", "items": [...] }
5. 【确认】
6. create-order { ..., "beCode": "...", "takeWayCode": "..." }
```

---

## 场景 C · 麦乐送外送（beType=2）

需要配送地址。地址不存在时先建。

```
1. delivery-query-addresses { }
   → 有地址 → 记下 addressId
   → 无地址 → delivery-create-address
        { "city": "杭州市", "contactName": "李明", "gender": "先生",
          "phone": "18616646686", "address": "清竹园9号楼", "addressDetail": "2单元508" }

2. delivery-query-stores { "addressId": "<上一步>", "beType": 2 }
   → storeCode + beCode

3. query-meals { "storeCode": "...", "orderType": 2, "beType": 2, "beCode": "..." }

4. list-nutrition-foods { } → 脚本筛选（外送餐品与到店可能有差异）

5. calculate-price { "storeCode": "...", "orderType": 2, "beType": 2, "beCode": "...", "items": [...] }
   → 按官方实付总额核对预算，包含适用的配送/打包等费用；orderType=2 **不需要** takeWayCode

6. 【确认】

7. create-order { "storeCode": "...", "orderType": 2, "beType": 2, "beCode": "...",
                  "addressId": "...", "items": [...], "remark": "无接触配送" }
```

**易错点**：外送不能传 `takeWayCode`；`remark`（≤ 50 字）只在外送场景引导填写。

---

## 场景 D · 企业团餐（beType=6）

团餐多了"预算 + 人数"和"助餐服务"两个变量。

```
1. delivery-query-addresses { } → addressId（同上）

2. 【先问两个数】预算总额与人数 → 人均预算

3. delivery-query-stores { "addressId": "...", "beType": 6 } → storeCode + beCode

4. query-meals { "storeCode": "...", "orderType": 2, "beType": 6, "beCode": "..." }

5. query-promotions { "storeCode": "...", "orderType": 2, "beType": 6, "beCode": "..." }
   → 满减 / 满折规则（promotionType 31=满额减、33=订单折扣）

6. query-meal-assistance { "storeCode": "...", "orderType": 2, "beType": 6, "beCode": "..." }
   → 取 gmServiceCode（算价前必做）

7. calculate-price { ..., "beType": 6, "beCode": "...", "gmServiceCode": "...", "items": [...] }
   → 组合时要能把总价压进预算，同时尽量不重复小食

8. 【确认】

9. create-order { ..., "beType": 6, "beCode": "...", "gmServiceCode": "...", "addressId": "..." }
```

团餐搭配的经验口径（来自 MCP 工具说明）：

| 人均预算 | 建议结构 |
| --- | --- |
| 20 元以下 | 小食 |
| 20–30 元 | 汉堡 + 小食，或汉堡 + 饮料 |
| 30–40 元 | 汉堡 + 薯条/小食 + 饮料 |
| 40–50 元 | 汉堡 + 薯条 + 小食 + 饮料 |
| 50 元以上 | 丰富组合，优先不重复小食 |

---

## 预约场景（四种场景都可能叠加）

用户说"明天中午 12 点送到 / 我 8 点去取"时：

1. 门店查询时完整展示 `reservationTimeOptions`（**漏一条用户就选不了那个时段**），
   `today=true` 的日期标星号
2. 从选项里挑出对应时段，得到 `reservationDate`（`yyyy-MM-dd HH:mm`）
3. 后续 `query-meals` / `calculate-price` / `create-order` **都带上** `reservationDate`
4. 即时单**不要**传这个参数

---

## 拿到订单之后

- `create-order` 返回支付链接 → 交给用户扫码或跳麦当劳 APP
- 用户回"支付完成 / 支付失败" → `query-order` 核对最新状态，**不要凭猜测说已支付**
- 用户要取消 → `cancel-order`，问清原因码
- 用户问配送进度 → `query-order`

## 确认后的变更与创建失败

- 用户确认针对具体的门店、场景、地址/时间、餐品规格与数量、优惠和官方实付总额。
  换店、换餐、换规格、优惠失效或金额变化后重新算价，展示变化并重新确认，再创建订单。
- `create-order` 返回明确的失败信息时，按错误修正；涉及上述内容变化仍需重新确认。
- 超时、断连或返回结果无法判断是否成功时，**不直接重试创建**。
  已有 `orderId` 用 `query-order` 核查；没有则用 `order-list` 检查本次时间段、门店、金额与餐品对应的订单。
  有候选时再查详情确认，不凭“最新一单”认领。确认已创建则返回已有支付入口。
- 暂未查到订单不等于确定未创建。无法确认时告诉用户“创建结果待核查”，
  请用户在官方订单页核实；状态未澄清前不新建第二单。后续重建也需用户明确确认。
