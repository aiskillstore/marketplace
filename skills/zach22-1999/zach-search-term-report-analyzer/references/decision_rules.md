# 搜索词决策规则

本文件定义 `zach-search-term-report-analyzer` 的核心判断规则。
目标不是生成泛泛而谈的分析，而是把广告搜索词报告转成可执行的决策输出：

- 否词候选
- 放量候选
- 潜力属性词 / 场景词
- 观察名单
- 需人工复核项

---

## 1. 适用范围

适用于以下广告搜索词报告：

- SP 搜索词报告
- SB 搜索词报告
- SD 搜索词报告

默认以**单个 ASIN**为分析单位。如果一份报告中包含多个 ASIN，先识别候选 ASIN，由用户确认分析对象后再继续。

---

## 2. 核心原则

### 2.1 先回到产品维度，再看搜索词

不要把整份报告里的所有词直接混在一起比较。先识别：

- 品牌
- ASIN
- 报告类型
- 主要广告组合 / 广告活动 / 广告组命名

若同一 ASIN 对应多个广告活动，允许合并分析；若涉及多个不同产品，默认拆开。

### 2.2 基准使用该 ASIN 自身的广告 CVR

默认基准不是全店平均、也不是全报告平均，而是：

`ASIN广告CVR基准 = 当前分析窗口内该 ASIN 的总订单数 / 总点击量`

用于判断：

- 某搜索词是否高于平均
- 某搜索词是否接近平均
- 某搜索词是否明显低于平均

### 2.3 不单指标拍板

不能只因某词 CVR 低，就直接建议否定。至少联合看：

- 点击量
- 花费
- ACOS
- CVR
- 时间窗趋势
- 相关性
- 词类别（品牌词 / 竞品词 / 属性词 / 场景词 / 无关词）

---

## 3. 指标定义

若报告原始字段名不同，统一映射到以下内部指标：

- `impressions`：展示量
- `clicks`：点击量
- `ctr`：点击率
- `cpc`：单次点击成本
- `spend`：花费
- `orders`：订单数
- `sales`：销售额
- `cvr`：订单数 / 点击量
- `acos`：花费 / 销售额
- `roas`：销售额 / 花费

若原报表已给出 `CVR / ACOS / ROAS`，优先复算校验；若缺字段，按“有就用，没有就跳过”。

补充约定：

- 搜索词进入聚合前，应先做标准化清洗，去掉隐藏字符、异常空格和大小写差异
- 同一搜索词的脏字符变体应尽量合并到同一个标准搜索词再分析

---

## 4. 可配置阈值

以下阈值不要硬写在主流程里，集中在这里配置。

```yaml
min_clicks_for_judgement: 8
min_clicks_for_priority: 15
min_clicks_for_scale_up: 12
min_clicks_for_listing_feedback: 10
min_spend_for_attention: 10
high_spend_without_orders: 15
near_avg_cvr_band: 0.15
high_cvr_band: 0.20
low_cvr_band: 0.20
trend_change_band: 0.20
max_target_acos_multiple_for_scale_up: 1.15
very_high_target_acos_multiple: 1.50
```

解释：

- `min_clicks_for_judgement`
  - 点击量低于这个值时，不做强结论，默认进入观察或人工复核。
- `min_clicks_for_priority`
  - 点击量高于这个值时，优先进入处理名单。
- `min_clicks_for_scale_up`
  - 即使某词表现优秀，也建议达到这个点击量后再进入更明确的放量。
- `min_clicks_for_listing_feedback`
  - 属性词 / 场景词至少达到这个点击量后，再优先反馈给 Listing / 投放策略。
- `min_spend_for_attention`
  - 即使点击不高，但花费已明显发生，也要进入关注。
- `high_spend_without_orders`
  - 当某词已经明显花费但仍 0 单时，即使 ACOS 因无销售额而缺失，也应优先进入控成本。
- `near_avg_cvr_band`
  - 当词的 CVR 与 ASIN 基准 CVR 的差距在 ±15% 内，视为“接近平均”。
- `high_cvr_band`
  - 当词的 CVR 高于 ASIN 基准 CVR 20% 以上，视为“明显高于平均”。
- `low_cvr_band`
  - 当词的 CVR 低于 ASIN 基准 CVR 20% 以上，视为“明显低于平均”。
- `trend_change_band`
  - 7 / 14 / 30 天窗口之间的核心指标变化超过 20% 时，视为趋势显著变化。
- `max_target_acos_multiple_for_scale_up`
  - 即使某词 CVR 很高，只要 ACOS 明显高于目标，也不要直接放量。
- `very_high_target_acos_multiple`
  - 当 ACOS 远高于目标时，优先进入控 bid / 降成本，而不是继续观察。

---

## 5. 搜索词分类规则

每个搜索词至少要落一个主标签，可多打辅助标签。

### 5.1 主标签

- `brand_term`：品牌词
- `competitor_term`：竞品词
- `asin_term`：ASIN 串号词
- `core_category_term`：核心品类词
- `attribute_term`：属性词
- `scenario_term`：场景词
- `irrelevant_term`：无关词
- `uncertain_term`：暂不确定

### 5.2 分类优先级

优先级从高到低：

1. `brand_term`
2. `competitor_term`
3. `asin_term`
4. `irrelevant_term`
5. `attribute_term`
6. `scenario_term`
7. `core_category_term`
8. `uncertain_term`

### 5.3 v1 的边界

v1 可以做：

- 识别并标记品牌词
- 识别并标记竞品词
- 标记属性词、场景词、无关词候选
- 识别并标记 ASIN 串号词
- 对常见品牌 typo 做保守归并

v1 不强制做：

- 深度竞品品牌库构建
- 自动打开多个竞品 Listing 做复杂判断

遇到边界不清时，标为 `uncertain_term` 并升级人工。

---

## 6. 决策输出标签

每个搜索词最终至少输出一个动作标签：

- `scale_up`
  - 建议放量、提高出价、转精准或重点保留
- `hold_test`
  - 当前不要激进处理，继续测试或小幅调 bid
- `reduce_bid`
  - 词相关，但成本效率偏差，先控 bid
- `negative_candidate`
  - 进入否词候选
- `observe`
  - 数据不足或趋势不稳，先观察
- `listing_feedback`
  - 应反馈给 Listing / 素材 / 产品认知
- `manual_review`
  - 需要人工复核，不自动下结论

---

## 7. 主决策规则

### 7.1 放量候选规则

满足以下条件时，优先标记为 `scale_up`：

- `clicks >= min_clicks_for_judgement`
- 更稳妥时优先要求 `clicks >= min_clicks_for_scale_up`
- `cvr >= ASIN广告CVR基准 * (1 + high_cvr_band)`
- 不属于 `irrelevant_term`
- 不属于需要保守处理的例外项
- ACOS 没有明显高于目标 ACOS

附加加分条件：

- 7 天 CVR 高于 14 / 30 天
- ACOS 低于目标 ACOS
- 点击量持续增长
- 属于属性词或场景词，且词义与产品卖点一致

输出说明应写清：

- 为什么该词高于基准
- 建议是放量、转精准、单独建组，还是先维持再观察

### 7.2 接近平均词规则

当满足以下条件时，标记为 `hold_test` 或 `reduce_bid`：

- `clicks >= min_clicks_for_judgement`
- `ASIN广告CVR基准 * (1 - near_avg_cvr_band) <= cvr <= ASIN广告CVR基准 * (1 + near_avg_cvr_band)`

这时继续看 ACOS：

- 若 `acos > 目标ACOS`
  - 标记 `reduce_bid`
  - 说明：词不一定差，但成本压力偏高，先降 bid 控成本
- 若 `acos <= 目标ACOS`
  - 标记 `hold_test`
  - 说明：词效能接近平均，可保持或小幅提 bid 测试放量空间

### 7.3 明显低效词规则

满足以下条件时，优先考虑 `negative_candidate` 或 `manual_review`：

- `clicks >= min_clicks_for_judgement` 或 `spend >= min_spend_for_attention`
- `cvr <= ASIN广告CVR基准 * (1 - low_cvr_band)`
- ACOS 明显偏高或持续无单
- 词义与产品不强相关，或已出现明显浪费信号

但以下情况不要直接否：

- `brand_term`
- `competitor_term`
- 新品期
- 点击量过低、数据不足
- 明显可能是 Listing 承接问题而非流量问题

默认顺序：

1. 先看是否属于例外项
2. 再看是否无关
3. 再决定是 `negative_candidate`、`reduce_bid`、`observe` 还是 `manual_review`

补充：

- 若某词 `0 单 + 高点击 / 高花费`，即使 ACOS 因无销售额而缺失，也应优先考虑进入 `reduce_bid`
- 对属性词 / 场景词，不要因为短期转化弱就完全丢掉；可同时给出“控成本”和“反馈 Listing”的双重视角

### 7.4 点击优先级规则

同等条件下，优先处理高点击词。

排序优先级建议：

1. 高点击 + 高花费 + 低效率词
2. 高点击 + 高效率词
3. 上升中的属性词 / 场景词
4. 低点击但花费异常词
5. 低点击低花费观察词

---

## 8. 时间窗规则

默认至少输出：

- 近 7 天
- 近 14 天
- 近 30 天

### 8.1 趋势变好

以下情况可标记为“趋势变好”：

- 7 天 CVR 明显高于 30 天
- 7 天 ACOS 明显低于 30 天
- 点击量稳定或上升
- 订单效率同步改善

### 8.2 趋势变坏

以下情况可标记为“趋势变坏”：

- 7 天 CVR 明显低于 30 天
- 7 天 ACOS 明显高于 30 天
- 点击量上升但转化不跟
- 花费上升但订单无改善

### 8.3 趋势不稳

以下情况标记为 `observe`：

- 7 / 14 / 30 天结论互相打架
- 样本量太低
- 某时间窗数据异常缺失
- 大促、节假日等特殊周期导致波动失真

补充：

- 趋势判断不要只看 CVR，也要结合 ACOS 是否同步变好 / 变坏

---

## 9. 例外规则

### 9.1 新品期

如果当前 ASIN 处于新品期：

- 不要用成熟品的稳定阈值直接判断
- 对低效词更偏 `observe` 或 `manual_review`
- 对潜力词更偏“测试中放量”，而不是直接重仓

### 9.2 品牌词

品牌词即使 CVR 很高，也不自动进入“重点放量”。
要单独标记 `brand_term`，并说明：

- 它可能主要承担品牌防守或品牌承接
- 不一定代表真实泛品类需求扩张

### 9.3 竞品词

竞品词即使 CVR 一般，也不自动进入否词。
默认先标记 `competitor_term`，并说明：

- 这是竞品争夺词
- 是否继续投放需要更高层策略判断
- v1 只做标记和提醒，不做深度竞品归因

### 9.4 数据不足

若满足任一条件：

- `clicks < min_clicks_for_judgement`
- `spend < min_spend_for_attention`
- 时间窗数据不完整

则默认标记为 `observe` 或 `manual_review`，不下强结论。

### 9.5 ASIN 型搜索词

如果搜索词本身包含明显的 `B0...` ASIN 串号：

- 单独标记为 `asin_term`
- 不自动进入放量或否词
- 默认优先 `manual_review`
- 说明需要人工判断这是品牌承接、竞品流量，还是特殊投放信号

---

## 10. 异常归因规则

当词表现差时，不要只输出“CVR低”。至少尝试归因到以下之一：

- `irrelevant_traffic`
  - 词本身与产品不够相关
- `poor_listing_alignment`
  - 词相关，但 Listing 承接不够
- `pricing_or_conversion_issue`
  - 可能是价格、评价、竞争环境影响转化
- `mixed_signal`
  - 数据不够一致，无法明确归因
- `manual_review_needed`
  - 必须看 Listing 才能进一步判断

若需要看 Listing 才能继续判断，应明确写：

“该词已触发人工复核，建议先查看对应 ASIN 的 Listing、核心卖点、功能和适用场景，再决定是否否定或调整投放。”

---

## 11. 属性词 / 场景词规则

对于 `attribute_term` 或 `scenario_term`，不要只输出广告动作，还要判断是否进入 `listing_feedback`。

优先进入 `listing_feedback` 的条件：

- 近 7 天或 14 天点击量上升
- 词义与产品真实卖点相关
- 当前 Listing 中未明显覆盖该属性 / 场景
- 不是明显无关流量

输出时建议拆成两条：

- 广告侧建议
- Listing / 内容侧建议

---

## 12. 置信度层

除动作标签外，建议额外给出 `high / medium / low` 三级置信度。

置信度应至少参考：

- 点击量是否足够
- 是否已有订单样本
- 7 / 14 / 30 天是否都能形成有效窗口
- 词分类是否明确
- 趋势是否稳定

规则目标：

- `low`：不直接给强动作，优先 `observe / listing_feedback / manual_review`
- `medium`：可给轻动作，如 `hold_test / reduce_bid`
- `high`：可给更明确的 `scale_up / reduce_bid / negative_candidate`

---

## 13. 输出优先级

最终报告中的顺序建议：

1. `negative_candidate`
2. `scale_up`
3. `reduce_bid`
4. `listing_feedback`
5. `observe`
6. `manual_review`

原因：

- 先处理浪费
- 再处理机会
- 再处理需要协同的认知反馈
- 最后放观察和人工复核

---

## 14. 升级人工条件

以下情况直接标记 `manual_review`：

- 报告中无法稳定识别 ASIN
- 多个产品混在一起且用户未确认分析对象
- 品牌词 / 竞品词策略含糊，无法自动下结论
- 需要结合 Listing 才能判断相关性
- 字段缺失导致核心指标无法计算
- 时间窗信号互相冲突，无法形成稳定结论

---

## 15. v1 不做的事

v1 明确不做：

- 自动代替用户做最终预算决策
- 深度竞品品牌库建设
- 自动抓竞品 Listing 并做完整竞品画像
- 在没有明确字段时强行给 ACOS / CVR 结论
- 把用户真实销售数据沉淀进 skill 包
