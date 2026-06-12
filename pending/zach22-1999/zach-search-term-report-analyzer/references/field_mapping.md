# 搜索词报告字段映射

本文件用于把不同广告类型的搜索词报告，统一映射为 `zach-search-term-report-analyzer` 的内部分析字段。

适用范围：

- SP 搜索词报告
- SB 搜索词报告
- SD 搜索词报告

原则：

1. 优先使用官方原始字段
2. 字段名不同但语义一致时，映射到统一内部字段
3. 某字段缺失时按“有就用，没有就跳过”，但必须在报告中说明缺失项

---

## 1. 内部标准字段

| 内部字段 | 含义 | 是否核心 |
|----------|------|----------|
| `date` | 日期 | 是 |
| `brand` | 品牌 | 否 |
| `asin` | ASIN | 否 |
| `campaign_name` | 广告活动名称 | 否 |
| `ad_group_name` | 广告组名称 | 否 |
| `targeting` | 投放词 / 投放对象 | 否 |
| `match_type` | 匹配类型 | 否 |
| `search_term` | 客户搜索词 | 是 |
| `impressions` | 展示量 | 是 |
| `clicks` | 点击量 | 是 |
| `ctr` | 点击率 | 否 |
| `cpc` | 单次点击成本 | 否 |
| `spend` | 花费 | 是 |
| `orders` | 订单数 | 是 |
| `sales` | 销售额 | 否 |
| `cvr` | 转化率 | 是 |
| `acos` | ACOS | 否 |
| `roas` | ROAS | 否 |

---

## 2. 常见中文字段映射

| 原始字段 | 映射到 |
|----------|--------|
| `日期` | `date` |
| `广告活动名称` | `campaign_name` |
| `广告组名称` | `ad_group_name` |
| `投放` | `targeting` |
| `匹配类型` | `match_type` |
| `客户搜索词` | `search_term` |
| `展示量` | `impressions` |
| `点击量` | `clicks` |
| `点击率 (CTR)` / `点击率(CTR)` | `ctr` |
| `单次点击成本 (CPC)` / `单次点击成本(CPC)` | `cpc` |
| `花费` | `spend` |
| `7天总订单数(#)` | `orders` |
| `7天总销售额` | `sales` |
| `7天的转化率` | `cvr` |
| `广告投入产出比 (ACOS)` / `广告投入产出比(ACOS)` | `acos` |
| `总广告投资回报率 (ROAS)` / `总广告投资回报率(ROAS)` | `roas` |

---

## 3. 常见英文字段映射

| 原始字段 | 映射到 |
|----------|--------|
| `Date` | `date` |
| `Campaign Name` | `campaign_name` |
| `Ad Group Name` | `ad_group_name` |
| `Targeting` | `targeting` |
| `Match Type` | `match_type` |
| `Customer Search Term` / `Search Term` | `search_term` |
| `Impressions` | `impressions` |
| `Clicks` | `clicks` |
| `CTR` | `ctr` |
| `CPC` | `cpc` |
| `Spend` | `spend` |
| `Orders` | `orders` |
| `Sales` | `sales` |
| `CVR` | `cvr` |
| `ACOS` | `acos` |
| `ROAS` | `roas` |

---

## 4. 字段派生规则

若原始报表未直接提供以下字段，可按如下方式派生：

- `ctr = clicks / impressions`
- `cvr = orders / clicks`
- `acos = spend / sales`
- `roas = sales / spend`

派生前检查分母是否为 0。若为 0，不要硬算，保留为空并在报告中说明。

---

## 5. 多广告类型兼容策略

SP / SB / SD 搜索词报告字段相近，但不完全相同。兼容策略如下：

1. 只要能稳定识别 `search_term + clicks + spend + date`，就允许进入基础分析
2. 若缺少 `orders / sales / cvr`，允许仅做流量效率和异常观察，不做强转化结论
3. 若缺少 `asin`，尝试从广告活动名称、广告组名称、品牌命名中识别；仍无法识别则升级人工
4. 若缺少 `match_type`，允许继续分析，但要在报告中说明“未区分匹配类型”

---

## 6. ASIN 识别规则

优先级如下：

1. 直接使用报表内明确的 `ASIN` 字段
2. 从 `campaign_name` / `ad_group_name` 中提取类似 `B0...` 的 ASIN
3. 从品牌 + 活动命名约定中推测
4. 若一份报告中出现多个候选 ASIN，先列给用户确认，不直接混分析

---

## 7. 品牌识别规则

优先级如下：

1. 从文件所在路径或文件名识别品牌
2. 从活动命名识别品牌前缀
3. 从报表内 `brand` 字段或文件名中的 `brand-xxx` / `品牌-xxx` 片段识别
4. 若仍不明确，回显候选品牌，请用户确认或用 `--brand` 显式指定

---

## 8. 最低可分析门槛

进入正式分析前，至少要能稳定拿到：

- `date`
- `search_term`
- `clicks`
- `spend`

若连以上字段都无法稳定识别，则不要继续分析，直接返回 `NEEDS_CONTEXT` 或 `BLOCKED`。
