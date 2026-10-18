# MCP 集成说明

本文档说明「吃了麦？」实际使用的麦当劳 MCP Server、Tool、调用流程，以及它带来的业务价值。

## 一、MCP Server

| 项 | 值 |
| --- | --- |
| 名称 | `mcd-mcp` |
| 传输方式 | `streamablehttp` |
| 端点 | `https://mcp.mcd.cn` |
| 鉴权 | `Authorization: Bearer <MCD_MCP_TOKEN>`（请求头） |
| 服务标识 | `serverInfo.name = "mcd-mcp"`，`version = 1.0.0` |
| 协议版本 | `2025-03-26` |

脱敏配置见 [`mcp-config.example.json`](mcp-config.example.json)，仅含环境变量占位符 `MCD_MCP_TOKEN`。

## 二、实际使用的 Tool

### 核心链路（每次点餐都会用到）

| Tool | 作用 | 在本项目中的用法 |
| --- | --- | --- |
| `query-nearby-stores` | 查可点餐门店 | 到店/得来速场景；按当前 city+keyword 搜最近营业门店，用户指定收藏店时才查收藏 |
| `query-meals` | 在售餐品与价格 | 拿 `productCode` 与实时价格，作为下单的基础数据 |
| `list-nutrition-foods` | 餐品营养数据 | 拿热量/蛋白/脂肪/碳水/钠/钙，做营养目标筛选 |
| `calculate-price` | 算含优惠价格 | 确认最终价格，并取 `takeWayList[].code` 供下单用 |
| `create-order` | 创建订单 | 用户确认后下单，返回支付入口 |
| `query-order` | 查订单状态 | 用户反馈支付完成后核对真实状态 |

### 场景扩展

| Tool | 作用 | 触发条件 |
| --- | --- | --- |
| `delivery-query-addresses` | 外送地址簿 | 用户选择麦乐送/团餐 |
| `delivery-create-address` | 新建配送地址 | 地址簿为空 |
| `delivery-query-stores` | 按地址查可配送门店 | 外送/团餐场景取 storeCode + beCode |
| `query-meal-detail` | 核实套餐组成、规格与份数 | 套餐比较与营养汇总前，不能只根据名称猜组成 |
| `query-meal-assistance` | 团餐助餐服务 | 团餐算价前取 `gmServiceCode` |
| `query-promotions` | 团餐满减/满折规则 | 团餐搭配时优化总价 |

### 省钱链路

| Tool | 作用 | 说明 |
| --- | --- | --- |
| `available-coupons` | 当前可领取的券 | 用于发现优惠 |
| `auto-bind-coupons` | 一键领取全部可领券 | 用户说"便宜的"时先领券 |
| `query-store-coupons` | 指定门店 + 订单类型**真正可用**的券 | 判断可用性的唯一依据 |
| `query-my-coupons` | 卡包拥有券 | 只做展示，**不承诺可用于当前订单** |

### 辅助

| Tool | 作用 |
| --- | --- |
| `now-time-info` | 取服务器时间，用于匹配早餐/夜宵时段与"今天/明天" |
| `query-my-account` / `campaign-calendar` | 积分与活动日历（可选） |
| `order-list` / `cancel-order` | 历史订单与取消 |

## 三、调用流程

```
用户输入
  │
  ├─ Phase 1 解析意图 ──────────────── 目标 goal / 约束 / 场景 beType / 位置
  │
  ├─ Phase 2 锁定门店 ──────────────── query-nearby-stores          (到店/得来速)
  │                                    delivery-query-addresses
  │                                    → delivery-query-stores      (外送/团餐)
  │                                  产出 storeCode (+ beCode)
  │
  ├─ Phase 3 拉全数据 ──────────────── query-meals                  (在售餐品+价格)
  │                                    list-nutrition-foods         (营养)
  │                                    ↓ scripts/chilemai.py
  │                                    match  → 菜单 × 营养 名称对齐
  │
  ├─ Phase 4 组方案 ────────────────── scripts/chilemai.py plan     (整餐营养校验)
  │                                    query-meal-detail            (套餐需核实组成)
  │                                    available-coupons / auto-bind-coupons
  │                                    query-store-coupons          (本店可用券)
  │                                    calculate-price              (含优惠价 + takeWayCode)
  │
  └─ Phase 5 下单 ──────────────────── 【用户确认】
                                       create-order → 支付入口
                                       query-order  → 支付后核对
```

各场景的完整参数序见 [`references/order-flow.md`](references/order-flow.md)。

## 四、集成中的关键技术点

这些处理决定了推荐是否可信。

### 1. 营养数据不是 JSON，必须解析

`list-nutrition-foods` 返回的 `data` 是自定义文本：

```
[160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
  猪柳麦满分,null,1288,308,16,16,24,781,213
```

我们写了 `scripts/chilemai.py` 做解析（仅标准库），并把解析后的数据用于筛选与排序。
不解析就没法做任何定量比较。

### 2. 菜单与营养库的名称不一致

`query-meals` 里叫 `纯牛奶(盒装)`，营养库里叫 `纯牛奶（盒装）`——全角与半角括号的差别。
直接对名会漏掉大量餐品。脚本先做标点归一化，只有唯一精确匹配才返回可合计的营养值。
互为前缀只产生待确认候选，不再取第一条命中记录推定杯型或份量；同名营养行冲突也列为待确认。

### 3. 套餐不能用单品的营养数值

菜单里的「巨无霸三件套」在营养库中只能匹配到单品「巨无霸」（513 kcal）。
但三件套还包含薯条与饮料，真实热量显著更高。如果把 513 kcal 当作这顿饭的热量报给
正在控热量的用户，就是**自信地答错**。

因此脚本把匹配结果分成三类，且 `plan` 不自动纳入套餐：

| 分类 | 含义 |
| --- | --- |
| 精确对齐 | 归一化后唯一同名；单品可用，套餐仍需核实组成与口径 |
| 待确认（JSON 键 `alias`） | 仅返回候选名称与原因，不返回营养数值 |
| 未对齐 | 营养未知，不用于严格营养目标达标判断 |

套餐用 `query-meal-detail` 查清实际组成、规格和份数后逐项核实并汇总。
组成或必要营养缺失时明确无法核算总营养。

### 4. 参数传递有强约束

`beType` / `orderType` / `beCode` 三者必须配对，传错会直接报错或拿到错误门店的数据：

| 场景 | beType | orderType | beCode |
| --- | ---: | ---: | --- |
| 到店自取 | 1 | 1 | **不传**（传了报错） |
| 得来速 | 5 | 1 | **必传** |
| 麦乐送 | 2 | 2 | **必传** |
| 企业团餐 | 6 | 2 | **必传** |

此外：`takeWayCode` 仅 `orderType=1` 需要；算价与下单返回的价格字段单位是**分**。
这些规则被固化进 [`references/mcp-tools.md`](references/mcp-tools.md) 供每次调用前核对。

### 5. 整餐约束与价格校验

`plan` 枚举 1–3 份可信单品组合，至少含一份主食，按数量合计营养并检查整餐目标，
避免单品蛋白门槛提前排除有效组合。配餐、饮品可选，默认推荐少量方案。
菜单价格单位需明确传 `--price-unit yuan|fen`，输出的 `menu_subtotal_cents` 仅是菜单估价，
不是实付承诺。优惠比较与最终预算判断统一走 `calculate-price`，包含适用的配送等费用。
无候选只说明当前数据覆盖和搜索范围没有匹配，不擅自放宽约束。

用户确认绑定具体方案和官方实付金额。确认后变更需重新算价并确认；创建结果不明时，
先查已有订单，不自动重试创建。处理细节见 `references/order-flow.md`。

## 五、业务价值

| 维度 | 没有 MCP 时 | 用了 MCP 之后 |
| --- | --- | --- |
| **菜单** | 网上找的静态菜单，可能已下架 | 当前门店**在售**餐品与实时价格 |
| **营养** | 靠记住"巨无霸大概 500 卡" | 官方营养表逐项比对，可按目标筛选 |
| **门店** | 自己搜地图再判断营业状态 | 按距离 + 营业状态直接给出最近门店 |
| **优惠** | 到店才发现有券没用 | 先领券、再校验本店可用性、对比券后价 |
| **下单** | 得自己打开 APP 重新找一遍 | 决策结果直接变成订单与支付入口 |

一句话：**把"吃什么"从一次跨 App 的手工劳动，变成一句对话。**

## 六、诚实边界

- 营养库覆盖约 160 条餐品，部分新品（如「龙焰鸡腿堡」系列）暂无营养数据，
  脚本会把它们列为"未对齐"，不纳入严格营养目标计算，**不编造数值**
- `query-my-coupons` 返回的券不保证可用于当前门店，可用性判定统一走 `query-store-coupons`
- 价格、供应状态以麦当劳官方渠道的实时结果为准
