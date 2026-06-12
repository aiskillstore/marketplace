---
name: zach-listing-health-checker
description: |
  以真实消费者视角检查亚马逊Listing健康状态。通过网页抓取模拟消费者浏览体验，
  检查页面可见性、价格、卖家信息、购物车、配送、类目节点、排名、差评等关键指标，
  并验证关键词搜索可见性。使用时机：新品上架后验收、日常巡检、排查Listing异常。
  触发词：/zach-listing-health-checker
benefits-from: []
user-invocable: true
allowed-tools: Read, Glob, Bash, Write, Edit, Grep
risk-level: low
---

## 前置建议

本公开版 Skill 是自包含的，不依赖任何私有工作区文件、内部参考库或品牌专属协议。

开始执行前，建议先通读本 Skill 自身的方法论部分，重点关注：

- 页面可访问性判断
- Buy Box / Add to Cart / 配送状态的异常标准
- 搜索可见性验证逻辑

如果你已经有自己的 Listing 诊断框架，可以作为补充背景使用；但本 Skill 的执行不依赖外部私有资料。

# Listing 健康检查器 — 完整方法论

## 1. 技能定位

### 核心理念

**通过 curl + BeautifulSoup 抓取亚马逊服务端渲染的 HTML，不借助任何 API 或第三方数据工具。**

原因：我们要验证的是"消费者打开亚马逊能看到什么"。任何 API 返回的数据都可能与前台页面不一致（缓存、区域差异、权限差异）。这个技能的价值就在于**所见即所得**。

亚马逊商品页面的核心数据（标题、价格、卖家、BSR、评论等）全部在服务端渲染的 HTML 中，无需 JavaScript 执行。curl 配合正确的浏览器 Headers 可稳定获取完整页面（~2.4MB HTML）。

### Script Directory

脚本位于 `skills/zach-listing-health-checker/scripts/`：
- **browser_utils.py** — 通用网页抓取模块（curl 封装、站点配置、反爬检测），其他 Skill 可复用
- **fetch_amazon_page.py** — 商品页面抓取，提取 9 项检查数据，输出 JSON
- **fetch_amazon_search.py** — 搜索结果页抓取，检查 ASIN 搜索可见性，输出 JSON

### 工作流位置

```
新品上架流程：
  zach-new-product-listing-writer → zach-launch-checklist-generator
      → 【zach-listing-health-checker：上架验收】
      → zach-ad-campaign-builder → 广告投放

日常运营：
  定期巡检 → 【zach-listing-health-checker】→ 发现问题 → 人工修复 → 复检
```

### 上下游

| 方向 | 技能 | 关系 |
|------|------|------|
| 上游 | zach-new-product-listing-writer | Listing 创建完成后需要验收 |
| 上游 | zach-launch-checklist-generator | 上架检查清单的执行环节之一 |
| 下游 | 人工修复 | 检查出问题后需要人工介入 |
| 下游 | 复检（再次调用本技能） | 修复后重新验证 |

---

## 2. 输入参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| ASIN | ✅ 是 | — | 10 位字母数字，通常以 B0 开头 |
| 站点代码 | 否 | US | 支持的站点见下方列表 |
| 卖家名称 | 否 | — | 用于校验 Sold By 是否正确 |
| 核心关键词 | 否 | — | 逗号分隔，用于搜索可见性验证 |

### 支持站点配置

| 站点代码 | 域名 | 默认邮编 | 货币 |
|----------|------|----------|------|
| US | amazon.com | 90001 | USD |
| UK / GB | amazon.co.uk | SW1A 1AA | GBP |
| DE | amazon.de | 10115 | EUR |
| FR | amazon.fr | 75001 | EUR |
| IT | amazon.it | 00100 | EUR |
| ES | amazon.es | 28001 | EUR |
| CA | amazon.ca | M5V 2T6 | CAD |
| JP | amazon.co.jp | 100-0001 | JPY |
| MX | amazon.com.mx | 06600 | MXN |
| AU | amazon.com.au | 2000 | AUD |

---

## 3. 检查项详细定义

### 3.1 页面可访问性

**检查内容**：页面是否正常渲染商品信息。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 页面包含商品标题、图片、价格等核心元素 |
| ❌ 异常 | 出现狗狗页面（Dog page）、404、"Looking for something?"、"Currently unavailable"、验证码页面 |

**常见异常场景**：
- ASIN 被下架 → 狗狗页面或 "Currently unavailable"
- ASIN 被合并到其他变体 → 自动跳转
- 区域限制 → "This item does not ship to your location"

### 3.2 价格与优惠

**检查内容**：当前售价、划线价、折扣、优惠券。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 有明确售价显示 |
| ⚠️ 需关注 | 价格与预期差异较大（需用户判断） |
| ❌ 异常 | 无价格显示、显示 "See price in cart"、或价格为 $0 |

**记录字段**：
- 当前售价
- 划线价（List Price / Was Price）
- 折扣百分比
- 优惠券（Coupon）金额或百分比
- 是否有"Subscribe & Save"折扣

### 3.3 卖家信息（Buy Box）

**检查内容**：Sold by 和 Ships from 信息。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | Sold by 显示为用户指定的卖家名称 |
| ❌ 异常 | Sold by 不是指定卖家（Buy Box 被抢） |
| ⚠️ 需关注 | 用户未指定卖家，仅记录当前信息 |

**记录字段**：
- Sold by：卖家名称
- Ships from：发货方（Amazon / 卖家名 / 第三方）
- 是否为 FBA（Ships from Amazon）

### 3.4 购物车状态

**检查内容**：是否有 Add to Cart / Buy Now 按钮。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 同时显示 Add to Cart 和 Buy Now |
| ⚠️ 需关注 | 只有 Add to Cart 没有 Buy Now，或显示 "See All Buying Options" |
| ❌ 异常 | 无购买按钮，或显示 "Currently unavailable" |

### 3.5 配送信息

**检查内容**：预计送达时间和 Prime 状态。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 有明确的预计送达日期，且在 7 天以内 |
| ⚠️ 需关注 | 配送时间 7-14 天 |
| ❌ 异常 | 配送时间超过 14 天、或无配送信息 |

**记录字段**：
- 预计送达日期
- 是否有 Prime 标识
- 配送费用（免费/具体金额）

### 3.6 类目与节点

**检查内容**：
1. 搜索栏旁的大类（department selector）
2. 面包屑导航中的销售节点路径（通常在主图上方）

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 能正常显示类目信息 |
| ⚠️ 需人工确认 | 类目信息显示正常，但需人工确认是否为期望的节点 |

**记录字段**：
- 搜索栏大类名称
- 面包屑完整路径（如 `Musical Instruments › Electronic Music, DJ & Karaoke › Karaoke Equipment › Systems › Portable Systems`）

> 注意：类目节点的"正确性"需要人工判断，技能只负责抓取和展示，不做自动判断。

### 3.7 BSR 排名

**检查内容**：Best Sellers Rank 在各层级类目中的排名。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 有 BSR 排名数据 |
| ⚠️ 需关注 | 排名显著下跌（需历史对比） |
| ❌ 异常 | 无 BSR 排名（可能表示商品未正常入库或类目异常） |

**记录字段**：
- 每个层级的类目名称 + 排名数字
- 示例：`#152 in Musical Instruments` → `#3 in Portable Karaoke Systems`

### 3.8 差评监控

**检查内容**：首页评论中的差评（1-3 星）数量和内容。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 首页 0 条差评 |
| ⚠️ 需关注 | 首页 1-2 条差评 |
| ❌ 异常 | 首页 3 条及以上差评 |

**记录字段**：
- 总评分（星级）
- 总评论数
- 首页差评条数
- 每条差评的：星级、标题、简要内容、日期
- 差评趋势判断：首次检查标注「首次检查，无历史对比基线」；有历史报告时对比差评数变化

### 3.9 搜索可见性

**检查内容**：用核心关键词搜索后，商品是否出现在搜索结果首页。

| 状态 | 判断条件 |
|------|----------|
| ✅ 正常 | 在首页自然位找到 |
| ⚠️ 需关注 | 仅在广告位找到，自然位未找到 |
| ❌ 异常 | 首页完全未找到（可能被压制或搜索不可见） |

**关键操作**：
- 搜索时确保选择 "All Departments"，不要被限定在某个子类目
- 区分自然位（Organic）和广告位（Sponsored）
- 记录具体位置编号

---

## 4. 执行步骤（详细）

### Step 1：参数解析与准备

1. 从用户输入中提取 ASIN、站点代码、卖家名称、核心关键词
2. 验证 ASIN 格式（10 位字母数字）
3. 根据站点代码查找域名和默认邮编
4. 如果用户未提供站点代码，默认使用 US
5. 构建商品页面 URL：`https://{domain}/dp/{ASIN}`

### Step 2：抓取商品页面

运行 `fetch_amazon_page.py` 脚本抓取商品页面并提取结构化数据：

```bash
python3 skills/zach-listing-health-checker/scripts/fetch_amazon_page.py {ASIN} --site {站点代码}
```

脚本输出 JSON，包含以下字段：
- `page_status`：页面状态（ok / dog_page / unavailable / captcha / fetch_failed）
- `title`：商品标题
- `price`：当前售价、划线价、折扣、优惠券
- `seller`：sold_by、ships_from
- `cart`：add_to_cart、buy_now、see_all_buying_options
- `delivery`：配送文本、Prime 标识
- `category`：搜索栏大类、面包屑路径
- `bsr`：各层级排名和类目
- `ratings`：评分星级、评论总数
- `reviews_on_page`：首页评论详情（星级、标题、日期、内容、是否差评）
- `variants`：变体信息
- `stock`：库存状态
- `anomalies`：异常提示列表

### Step 3：解析检查结果

将脚本返回的 JSON 数据逐项对照第 3 节的判断标准，为每个检查项标记状态：
- ✅ 正常
- ⚠️ 需关注
- ❌ 异常

对于脚本未能提取的字段（值为空或缺失），标注为「⚠️ 未能获取」，不做推测。

### Step 4：搜索可见性检查

⛔ **仅在用户提供了核心关键词时执行本步骤。**

对每个核心关键词，运行 `fetch_amazon_search.py` 脚本：

```bash
python3 skills/zach-listing-health-checker/scripts/fetch_amazon_search.py "{keyword}" {ASIN} --site {站点代码}
```

脚本输出 JSON，包含：
- `target_found`：目标 ASIN 是否在首页
- `target_position`：位置编号
- `target_type`：organic（自然位）或 sponsored（广告位）
- `search_department`：搜索范围
- `first_page_results`：首页所有结果列表（含 ASIN、标题、位置、类型）
- `captcha`：是否被验证码拦截

根据第 3.9 节的判断标准标记搜索可见性状态。

**注意**：多个 ASIN 搜索同一关键词时，只需抓取一次搜索结果页，在结果中查找所有目标 ASIN。

### Step 5：生成健康检查报告

按照第 5 节的报告模板，将所有检查结果整理为 Markdown 报告。

**总体评估逻辑**：
- 🟢 全部通过：所有 9 项均为 ✅
- 🟡 需关注：有 ⚠️ 但无 ❌
- 🔴 有异常：有任何一项 ❌

### Step 6：保存报告

将报告保存到：
```
outputs/listing-health-check/{品牌名或ASIN}/{YYYY-MM-DD}_{ASIN}_健康检查报告.md
```

如果无法从页面确定品牌名，使用卖家名称或 ASIN 作为目录名。

### Step 7：输出摘要

在终端向用户输出：
1. 总体评估状态（🟢/🟡/🔴）
2. 异常项和需关注项的简要列表
3. 报告文件的保存路径

---

## 5. 输出报告模板

```markdown
---
created: YYYY-MM-DD HH:MM
topic: {ASIN} Listing 健康检查
type: 健康检查报告
data_sources: 亚马逊官网页面抓取（curl + BeautifulSoup）
---

# {ASIN} Listing 健康检查报告

> 检查时间：YYYY-MM-DD HH:MM
> 站点：{站点代码} ({域名}) | 邮编：{邮编}
> 商品标题：{完整标题}

## 总体评估

| 状态 | 说明 |
|------|------|
| 🟢 / 🟡 / 🔴 | {一句话总结，如"链接健康，所有指标正常"} |

通过：X/9 | 需关注：X | 异常：X

---

## 逐项检查结果

### 1. ✅/❌ 页面可访问性
- **状态**：正常 / 异常
- **详情**：{具体描述}

### 2. ✅/⚠️/❌ 价格与优惠
- **当前售价**：${XX.XX}
- **划线价**：${XX.XX} / 无
- **折扣**：{X% off} / 无
- **优惠券**：{金额或百分比} / 无
- **Subscribe & Save**：{折扣} / 无

### 3. ✅/❌ 卖家信息（Buy Box）
- **Sold by**：{卖家名}
- **Ships from**：{发货方}
- **期望卖家**：{用户指定} → ✅ 匹配 / ❌ 不匹配 / 未指定

### 4. ✅/⚠️/❌ 购物车状态
- **Add to Cart**：有 / 无
- **Buy Now**：有 / 无
- **Buy Box 持有**：是 / 否

### 5. ✅/⚠️/❌ 配送信息
- **预计送达**：{日期}
- **Prime**：是 / 否
- **配送费**：{免费 / 金额}
- **判断**：正常（≤7天）/ 偏慢（7-14天）/ 异常（>14天）

### 6. ✅/⚠️ 类目与节点
- **搜索栏大类**：{大类名称}
- **面包屑路径**：{完整路径}
- **提示**：请人工确认节点是否为期望类目

### 7. ✅/⚠️/❌ BSR 排名

| 层级 | 类目 | 排名 |
|------|------|------|
| 大类 | {类目名} | #{排名} |
| 子类1 | {类目名} | #{排名} |
| 子类2 | {类目名} | #{排名} |

### 8. ✅/⚠️/❌ 差评监控
- **总评分**：{X.X} 星（{X,XXX} 条评论）
- **首页差评数**：{X} 条
- **差评趋势**：首次检查，无历史对比基线 / 较上次 {增加/减少} {X} 条

差评详情：

| 星级 | 标题 | 日期 | 内容摘要 |
|------|------|------|----------|
| ⭐{X} | {标题} | {日期} | {内容} |

### 9. ✅/⚠️/❌ 搜索可见性

| 关键词 | 搜索范围 | 是否找到 | 位置 | 类型 |
|--------|----------|----------|------|------|
| {keyword1} | All Departments | 是/否 | #{位置} | 自然/广告 |
| {keyword2} | {范围} | {结果} | {位置} | {类型} |

---

## 问题清单与行动建议

| 优先级 | 问题 | 建议操作 |
|--------|------|----------|
| 🔴 高 | {问题描述} | {具体建议} |
| 🟡 中 | {问题描述} | {具体建议} |

---

## 原始数据快照

> 以下为脚本抓取的原始关键信息，供核对。

{保留核心原始数据，便于日后审计}
```

---

## 6. 数据诚信规则

本技能严格遵守以下数据原则：

1. **数据来源唯一**：所有信息来自亚马逊官网页面抓取（curl + BeautifulSoup），不使用 Sorftime MCP 或其他任何第三方数据工具。
2. **不推测未获取信息**：脚本无法提取的字段，标注为「⚠️ 未能获取」，绝不编造。
3. **标注数据时效**：报告中明确标注检查时间，说明"结果仅代表检查时刻的页面快照"。
4. **区分事实与判断**：
   - 页面抓取到的原始信息 = 📊 数据事实
   - 基于检查结果给出的建议 = 💡 分析推断
5. **差评趋势需历史对比**：首次检查只记录快照，不做"是否新增差评"的判断；有历史报告时才做对比。

---

## 7. 局限性与应对

| 局限 | 说明 | 应对方式 |
|------|------|----------|
| JS 动态内容 | curl 获取服务端渲染 HTML，JS 动态加载的内容可能缺失 | 如关键信息缺失，标注「⚠️ 可能因动态加载未获取」 |
| 反爬机制 | 亚马逊可能返回验证码或简化页面 | 脚本自动检测验证码，报告中标注「❌ 被亚马逊拦截，建议手动检查」 |
| 地域差异 | 未实际设置邮编，可能影响价格和配送显示 | 在报告中说明使用的邮编和站点 |
| 搜索个性化 | 搜索结果受算法影响 | 注明"搜索结果为特定时刻快照，实际可能因用户画像不同而异" |
| 单次快照 | 无法检测"突然新增差评"等时序变化 | 建议定期执行并对比历史报告 |

---

## 8. 使用场景

### 场景 1：新品上架验收

```
/zach-listing-health-checker B0XXXXXXXXX US MyBrand "main keyword, secondary keyword"
```

上架 24-48 小时后执行，重点关注：
- 页面是否正常
- Buy Box 是否在自己手上
- 搜索关键词是否可见

### 场景 2：日常巡检

```
/zach-listing-health-checker B0XXXXXXXXX
```

每周例行检查，重点关注：
- 差评数量变化
- Buy Box 是否丢失
- 价格是否正确

### 场景 3：异常排查

```
帮我检查 B0XXXXXXXXX，最近销量突然下降，看看链接有没有问题
```

侧重排查：
- 是否被压制（搜索不可见）
- Buy Box 是否被抢
- 是否有新差评爆发

### 场景 4：批量检查（多 ASIN）

用户提供多个 ASIN 时，逐个执行完整检查流程，最后输出汇总表。

---

## 9. 与其他技能的数据流

```
本技能不消费其他技能的输出，也不产出供其他技能消费的数据。
它是一个独立的"健康巡检"工具，输出人可读的诊断报告。

唯一的"数据流"是历史报告对比：
  本次报告 ↔ 上次报告（同一 ASIN）→ 差评趋势判断
```

---

## 10. 依赖环境

- **Python 3**：运行抓取脚本
- **beautifulsoup4**：HTML 解析（`pip install beautifulsoup4`）
- **curl**：系统自带，用于 HTTP 请求
- **Bash 工具**：用于执行 Python 脚本
- **Write 工具**：用于保存报告文件
- **Read 工具**：用于读取历史报告（差评趋势对比）
- **Glob 工具**：用于查找历史报告文件

无需 Sorftime MCP、无需外部 API。脚本均位于 `skills/zach-listing-health-checker/scripts/` 目录。

## 风险与边界
- **risk-level: low** — 纯分析/信息收集，只读取公开前台页面，不涉及任何账号操作

## 上游 / 下游
- **上游**：无（直接输入 ASIN 或 URL）
- **下游**：`zach-listing-rufus-optimizer`（内容诊断）、`zach-asin-sales-anomaly-analyzer`（异常排查）

## 完成后
报告完成状态：DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT
