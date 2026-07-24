# QuantAll 实战手册

> 本文件是 QuantAll（全A解析）的使用经验积累文档。SKILL.md 负责"怎么装、有什么工具"，
> 本文档负责"怎么用好"——实战模式、代码示例、踩坑记录。
>
> **AI 使用建议**：执行复杂分析任务前先快速浏览本文档，了解常见模式和陷阱。

---

## 1. 快速上手（5 分钟）

### QuantAll 是什么

一台本地计算引擎。你（AI）写一段向量化 Python 代码，它就在全市场 5000+ 只股票上并行执行，
数秒内返回结果。**你不是在查询数据，你是在计算数据。**

### 你能做什么

| 你想要的 | 用什么工具 | 输出 |
|----------|-----------|------|
| 评估一个交易策略的收益 | `strategy_backtest` | 收益率/夏普/回撤/胜率 |
| 验证某个因子是否有效 | `factor_analysis` | IC均值/IR/多空差 |
| 找出符合条件的股票 | `select_by_code` | 股票列表 |
| 探索数据的多维关系 | `move_by_code` + `heat_map` | 热力图统计矩阵 |
| 标记事件/买点 | `new_layer_from_code` | 可视化短线 |

### 你的代码执行环境

```python
# 可用的变量
d          # dict[str, DataFrame] — 字段名 → 全市场面板数据（行=时间，列=股票）
col_attrs  # dict[str, Series]     — 股票属性（行业、市值等）

# 内置模块
np, pd     # numpy + pandas

# 内置函数
hold_until(buy, sell)  # 生成持仓矩阵（回测必须用这个！）
row_rank(df)           # 截面排名 → 百分位值 0~1
entry_check(window, conditions, mode="keep")  # 买入窗口条件检测
time_at(rq)            # 匹配指定时间
time_between(srq, erq) # 匹配时间区间
time_in(rqs)           # 匹配多个时间

# 复权价格（必须手动算！）
adj_close = d['close'] * d['adj_factor']
adj_high  = d['high']  * d['adj_factor']
adj_low   = d['low']   * d['adj_factor']
```

### 数据库数据传播规则

> **财报数据**（`stock_finance` 表）：会自动把公告日的数据**向后传播**（forward fill）到下一个公告日。也就是说，当你取任意日期的财报数据（如 ROE、营业收入），它会填充为最近一次公告的值——不会出现 NaN 空洞。
>
> **分红数据**（`dividend` 表）和**业绩预告数据**（`forecast` 表）：目前**只在公告日当天有数据，不会向后传播**。原因是"传播到哪个日期"存在技术细节难以确定（公告日和实际影响日之间的时间差不确定）。未来可能会增加相关操作，但目前这两张表取非公告日的数据就是 NaN。
>
> 含义：如果你在因子中使用分红率、预告净利润等字段，要意识到它们只存在于公告日期点上，不适合做连续的日频截面分析。

### 三条铁律

1. **禁止 import、for/while 循环、df.apply()、lambda、递归**
2. **禁止 axis=1（行方向计算）**——各股票停牌时间不对齐
3. **持仓矩阵必须用 `hold_until(buy, sell)`**，不能手写逆序 cumsum

---

## 2. strategy_backtest 四种视图详解

> **关键认知**：`strategy_backtest` 有四个 view 模式，它们**不是"选一个最好"的关系**，而是**从不同维度拆解同一个策略**。标准分析流程是 `summary → segments → detail → timeline`（逐步深入）。

### 四种视图对比

| view | 粒度 | 回答什么问题 | 后续分析 | 绘图方式 |
|------|------|-------------|----------|----------|
| **summary** | 每只股票 | "这个策略整体好不好？" | ✅ select/move/weight/heat_map | 5585条收益曲线叠加 |
| **segments** | 每次交易 | "买入前什么因子影响收益？" | ✅ 核心：分析因子与收益关系 | 持仓片段（起点=买入日） |
| **detail** | 每只股票 | "哪只股票表现最好/最差？" | ✅ 同 summary | 和 summary 同一张图 |
| **timeline** | 每日 | "每日净值走势？时间分布？" | ❌ **不支持二次分析** | 几条合成曲线（净值/排名/持仓比）

### summary 输出结构

```json
{
  "分析的股票数量": <N>,
  "时间范围": "<start> 至 <end>",
  "盈利比率-%": <百分比>,
  "跑赢基准比率-%": <百分比>,
  "全局买入比": <比率>,
  "全局持仓比": <比率>,
  "统计分析": {
    "总收益率-%": { 平均值, 中位数, 最大值, 最小值, 标准差, 25%分位, 75%分位 },
    "年化收益率-%": { ... },
    "最大回撤-%": { ... },
    "夏普率": { ... },
    "胜率-%": { ... },
    "盈亏比": { ... },
    "基准收益率(自身)-%": { ... }
  }
}
```

> **如何使用 summary**：先看中位收益率和夏普率判断策略是否有价值，再看盈利比率和跑赢基准比率判断策略相对 buy&hold 的表现。分布偏度（均值 vs 中位数）可以判断是否少数牛股拉高均值。

### segments 输出结构 + 绘图逻辑

```json
{
  "持仓片断总数": <N>,
  "平均收益-%": <平均>,
  "最大收益-%": <最大值>,
  "最小收益-%": <最小值>,
  "平均持仓时间": <天数>,
  "最长持仓时间": <天数>,
  "最短持仓时间": <天数>
}
```

**图形绘制方式**：

```
segments 模式不是单只股票画一条线，而是把每段"买入→卖出"独立画成一条线。

- 起点：每段买入日，坐标 (0, 1.0) —— 买入时收益为 1x（基准）
- 终点：每段卖出日，坐标 (持仓天数, 卖出收益倍数)
- X 轴：持仓天数（从 0 到 offset_days 或实际卖出天数）
- Y 轴：收益倍数（1.0 = 买入点，向上 = 盈利，向下 = 亏损）
- 红色：盈利片段（Y>1）
- 绿色/青色：亏损片段（Y<1）
- 一只股票多段持仓 → 被拆分成多条独立线段
```

**后续分析方法（每个片段的买入时间是关键日期）**：
- `select_by_code`：按收益倍数筛选，或按持仓天数筛选——返回**片段维度**统计（权重=卖价/买价，非股票维度累计收益）
- **核心设计**：segments 的真正价值不是看收益本身，而是分析"**买入前**的各种参数和因子对最终收益的影响"——把买入时的市值/换手率/估值等用 move_by_code 映射到坐标轴，再用 heat_map 做交叉分析
- `move_by_code`：把买入时的因子值映射到 X/Y 轴（如买入时市盈率→X，买入时成交量→Y）
- `weight_by_code`：调整权重（如按持仓天数加权）
- `heat_map`：因子×收益的二维分布矩阵

#### detail 输出结构

```json
{
  "总收益率-%":    { "000001": <值>, "000002": <值>, ... },  // 每只股票逐一展开
  "年化收益率-%":  { "000001": <值>, "000002": <值>, ... },
  // 与 summary.statistics 的指标一一对应，但按股票逐一展开
}
```

**⚠️ 重要警告**：
- detail 返回数据量极大（全市场 × 多个指标），可能远超 AI 上下文窗口
- **禁止直接向用户展示原始 detail 数据**——等于没展示
- **正确做法**：AI 读取后自行分析（排序、筛选 Top/Bottom、找规律），只汇报结论
- 推荐用法：筛选表现最好和最差的各 10 只 → 分析共性/原因

#### timeline

**绘制内容**：不画持仓片段，而是绘制 **5 条合成曲线**：

| 曲线 | 颜色 | 含义 |
|------|------|------|
| **每日平均收益** | 🔴 红色 | 每天策略持仓的平均收益百分比 |
| **平均收益排名** | 🟡 黄色 | 每天策略收益在全体股票中的排名均值 |
| **持平股数/总股数** | 🔵 青色 | 当天持平（没变动）的股票占比 |
| **买入股数/总股数** | ⚪ 白色 | 当天发出买入信号的股票占比 |
| **卖出股数/总股数** | 🟣 紫色 | 当天发出卖出信号的股票占比 |

**标题栏显示 5 条线的均值**，格式如：`收益%分布:X.XX 收益排序分布:X.XX 持仓比:X.XX 买点比:X.XX 卖点比:X.XX`

**核心用途**：观察时间分布规律——哪些时间段收益好、哪些时间段回撤大、market timing 是否有效。

**⚠️ 不支持二次分析**：timeline 是"只读"视图，不能用 `select_by_code`、`move_by_code`、`weight_by_code`、`heat_map` 等工具做进一步操作。看完就完了，想深入分析需要切到其他 view。

### 四视图使用决策树

```
跑 strategy_backtest
  │
  ├─ view=summary → 总收益中位数为正？夏普>0.5？
  │   ├─ 否 → 策略不行，换一个
  │   └─ 是 → 继续
  │
  ├─ view=segments → 买入前因子对收益有什么影响？
  │   核心操作：move_by_code（映射因子）+ heat_map（交叉分析）
  │
  ├─ view=detail → AI 内部分析 Top/Bottom 股票
  │   给用户：Top 10 股票名称+收益、Bottom 10、行业分布规律
  │   ⚠️ 绝不直接展示原始数据
  │
  └─ view=timeline → 查看时间分布规律
      └─ ⚠️ 只读视图，不支持二次分析。看完切其他 view
```

### 从 summary 图开始的后续分析

`strategy_backtest`（view=summary）执行后，软件端会绘制全市场持仓收益叠加图。这张图不是终点，而是后续深入分析的**起点**。

#### 用 `select_by_code` 筛选图上数据

`select_by_code` 可以对 summary 图上的所有股票进行条件筛选。**它不只是筛选器——天生自带统计功能**。返回结果中直接包含：

```json
{
  "全局平均": <数值>,          // 选中股票的平均权重（默认=回测最终收益）
  "有效数量": <N>,             // 实际命中的股票数
  "权重名称": "<指标名>",      // 当前权重指标名称
  "Y轴统计": [...],            // 如果有 move_by_code，按 Y 轴分 bin
  "Y轴细分": [...],            // bin 边界
  "Y轴缩放": <值>
}
```

> 💡 **核心认知**：不用先 `select_by_code` 再 `heat_map`，select_by_code 本身就返回 `全局平均`——你可以直接知道"这批股票的均值是多少"。

常见筛选维度：

- **属性**：`col_attrs['所在城市']`、`col_attrs['所属行业']`（Series，直接对比）
- **关键日**：用 `time_at` 取某一天的数值（如某日涨幅大的股票）→ bool DataFrame → 广播成全维度 DataFrame

> ⚠️ **使用某一天数值的正确方法**：`select_by_code` 等工具要求 `out` 是与 `d['close']` 同维度的 DataFrame，不能直接用某天的 Series。**正确做法**是用 `time_at` 生成 bool DataFrame，把目标日数值广播到全维度——全程向量化，无需循环（`for` 循环在 exec 环境中本就禁止）：
> ```python
> # 筛选某日涨幅>阈值的股票（向量化方法）
> ret = (d['close'] * d['adj_factor']).pct_change()
> # 1. time_at 获取 bool DataFrame，True→1，False→NaN
> mask = time_at('目标日期').astype(float)
> mask = mask.where(mask > 0, np.nan)
> # 2. 乘上对应因子的数值（目标日有值，其余为 NaN）
> day_ret = mask * ret
> # 3. 向前向后填充 NaN（把目标日数值传播到所有日期）
> day_ret = day_ret.ffill().bfill()
> # 4. 添加条件
> out = day_ret > 阈值
> ```

> ⚠️ **select_by_code 不回测数据过滤**：`select_by_code` 只影响 GUI 图层显示，不会过滤 `strategy_backtest` 的股票范围。想只测某个子集 → 需要其他方式（或观察 select_by_code + heat_map 的统计结果）。

#### 用 `move_by_code` 和 `weight_by_code` 控制绘图

Summary 图的坐标和权重是可以调整的：
- **平移（move_by_code）**：把其他维度映射到 X 或 Y 轴，实现多维视图。例如把市值映射到 X 轴，看市值与收益的关系
- **权重（weight_by_code）**：默认按最终收益加权，一般不需要修改。但你可以按自定义规则加权（如按持仓天数加权）

> 同样注意：平移/权重输出必须是和 `d['close']` 同维度的 DataFrame。若需用某一天数值，同样用 `time_at` + 填充广播（见上方方法），不要用 `for` 循环复制

#### 做内力图（热力图分析）

筛选出子集后，可以进一步做**内力图**（多维热力图）：

```
select_by_code（筛选子集）
  → move_by_code(x)（映射维度，如市值）
  → move_by_code(y)（映射维度，如换手率）
  → weight_by_code（可选：调整权重）
  → heat_map（获取二维统计矩阵）
  → 分析矩阵密度分布
```

#### 操作链：从 summary 到深度分析

```
strategy_backtest(summary) → 画全市场图
  ↓
select_by_code（筛选行业/城市/关键日）
  ↓
  ├─ 再跑 strategy_backtest（只测筛选子集）→ detail/segments 看明细
  ├─ 或 move_by_code + weight_by_code → 调整绘图维度
  ├─ 或 new_layer_from_code → 标记新事件
  └─ 或 heat_map → 内力图做多维交叉分析
```

---

## 3. factor_analysis 三项模式详解

> **核心认知**：`factor_analysis` 有三个 mode，和 `strategy_backtest` 的 view 一样，是从不同维度评估因子有效性。

### 三种模式对比

| mode | MCP 返回 | 软件端绘图 | 后续分析 | 核心用途 |
|------|---------|-----------|----------|---------|
| **summary** | 聚合统计（IC均值/IR/正占比/多空差） | 散点图：X=收益排序，Y=因子排序，红=高收益，绿=低收益 | **支持** `move_by_code` + `heat_map` + `select_by_code` | **第一步必跑**，判断因子是否有效 |
| **daily** | 每日IC时间序列 + 每日前/后10%IC | 时序曲线图：X=时间，Y=IC值，三条曲线（蓝=每日IC/红=前10%/绿=后10%） | **不支持**（只读视图） | 看IC时序稳定性、时段特征 |
| **scatter** | 同 summary 的聚合统计 | 时序散点图：X=时间（按天排列，每天因子排序缩放到0-0.8）+ 因子排序，Y=因子排序，红=高收益，绿=低收益 | **支持** 在时间维度上进一步分析 | 观察因子-收益关系随时间的演变，局部放大可做切片分析 |

> **关键区别**：
> - `summary` 是**全局截面**散点——所有(日期,股票)混在一起，看整体因子-收益关系
> - `scatter` 是**时序截面**散点——每个时间切片（一天）独立排列，能看到垂直条纹（不同日期的IC强度差异），局部放大可分析特定时段
> - `daily` 是**纯时序曲线**——只看IC随时间的变化，不支持二次分析
> 
> `scatter` 和 `summary` 返回同样的聚合统计数据，但绘图方式不同、后续分析能力不同。`daily` 是只读视图。

### daily 模式返回格式

```json
{
  "每日IC信息": "                每日IC  每日前10%IC  每日后10%IC\nYYYY-MM-DD -0.XXXXX -0.XXXXX -0.XXXXX\n..."
}
```

- **每日IC**：每天的 Rank IC（Spearman 秩相关）
- **每日前10%IC**：因子值最高 10% 股票的 IC 贡献
- **每日后10%IC**：因子值最低 10% 股票的 IC 贡献
- **最后 `feature_days` 行全为 NaN**——因为没有足够未来数据计算

### 实战用法

```python
# 单因子分析
factor_analysis(name="换手率", code="out = d['换手率']", feature_days=20, mode="summary")

# 复合因子（各自排名后等权组合）
factor_analysis(
    name="低换手小市值",
    code="turnover_rank = row_rank(d['换手率'])\nsize_rank = row_rank(d['总市值'])\nout = (1 - turnover_rank) + (1 - size_rank)",
    feature_days=20,
    mode="summary"
)

# 动量因子
factor_analysis(
    name="20日动量",
    code="adj_close = d['close'] * d['adj_factor']\nout = adj_close.pct_change(20)",
    feature_days=20,
    mode="daily"  # 看 IC 时序稳定性
)
```

> ⚠️ **注意**：`factor_analysis` 内部已自动做排名转换（Spearman Rank IC），代码中不需要手动 `row_rank()`。但如果要组合多个因子，需要手动 rank 后再组合（确保量纲一致）。

### 因子分析涉及的关键指标

| 指标 | 含义 | 使用建议 |
|------|------|---------|
| IC均值 | 因子值与未来收益的 Spearman 秩相关系数均值 | 绝对值越大越好，正=因子值越高收益越高 |
| IC_IR | IC均值 / IC标准差 | 衡量因子的风险调整后预测力，通常 \|IR\|>0.3 视为有效 |
| IC正占比 | IC>0 的天数比例 | 偏离50%越多越好 |
| 多空差 | 因子值最高组 vs 最低组的收益差 | 衡量因子区分度 |
| feature_days | 评估未来第 N 天的收益 | 长周期（20d）通常比短周期（5d）IC更强 |

### 因子分析 decision tree

```
跑 factor_analysis
  │
  ├─ mode=summary → |IC_IR| > 0.3？IC正占比偏离50%？
  │   ├─ 否 → 因子无效，换一个
  │   └─ 是 → 继续
  │
  ├─ mode=daily → IC 时序稳定？有没有长期同符号？
  │   如果频繁正负翻转 → 因子不稳定，时效性强
  │   ⚠️ 只读视图，不支持二次分析
  │
  └─ mode=scatter → 查看时序截面分布（软件端可视化）
      全局看垂直条纹（时间维度IC差异），局部放大做切片分析
      支持 move_by_code / heat_map 在时间维度上进一步挖掘
```

---

## 4. 三大场景操作手册

### 场景一：用户有明确需求

用户直接要求回测、因子分析、选股等。

**标准流程**：
```
ping → available_data（确认字段存在）→ 写 code → 执行工具 → summary 快评 → 按需深入
```

**常见模式**：

```python
# 回测需求 → strategy_backtest（先 summary，再 detail/timeline）
adj_close = d['close'] * d['adj_factor']
ma5  = adj_close.rolling(5).mean()
ma20 = adj_close.rolling(20).mean()
buy  = (ma5 > ma20) & (ma5.shift(1) <= ma20.shift(1))
sell = (ma5 < ma20) & (ma5.shift(1) >= ma20.shift(1))
out  = hold_until(buy, sell)
```

```python
# 因子分析 → factor_analysis
out = d['换手率']  # 简单因子直接输出字段
# 或复合因子：
m_rank = row_rank((d['close'] * d['adj_factor']).pct_change(20))
s_rank = row_rank(d['总市值'])
out = 0.6 * m_rank + 0.4 * (1 - s_rank)
```

### 场景二：用户模糊表述想法

用户没说"回测"或"因子分析"，但表达了与股市相关的直觉或疑问。

**关键原则**：把"模糊想法"翻译成"可计算的量化问题"。

**判断清单**（用户说什么 → 你可以算什么）：

| 用户的模糊表述 | 可量化的分析 | 用什么工具 |
|-------------|------------|-----------|
| "XX 之后一般会涨还是跌？" | 事件发生后 N 日收益的统计 | `strategy_backtest` |
| "XX 是不是影响收益？" | 因子 IC 分析 | `factor_analysis` |
| "哪些股票最近 XX？" | 条件筛选 | `select_by_code` + `new_layer_from_code` |
| "XX 和 YY 有什么关系？" | 双因子多维分析 | `move_by_code` × 2 + `heat_map` |
| "最近 X 类型的股票表现如何？" | 筛选 + 最近 N 日涨跌幅 | `select_by_code` + `move_by_code` |

**标准流程**：
```
理解用户意图 → 翻译成可量化问题 → available_data（确认有对应字段）
→ 写 code → 执行 → 读结果 → 用数据回答（而非"网上说..."）
```

### 场景三：AI 自主挖掘机会

你主动设计分析假设，利用 QuantAll 的技术闭环验证。

**技术闭环**：
```
假设 → code → QuantAll 执行 → 读返回数据 → 形成结论 → 可能迭代
```

**可以做的事情**：
- 扫描多个因子的 IC，找出近期有效的因子
- 测试常见技术指标在过去 N 年的胜率
- 组合多因子看看有没有协同效应
- 按行业分组分析因子表现差异

**注意事项**：
- 每个假设用独立的工具调用，不要一次跑太多
- 先 `available_data` 确认字段可用
- 把结论和原始数据一起呈现给用户（提供不确定性范围，不要过度自信）
- 结论里标注用的是哪个参数、哪个时间段

---

## 5. 代码模式库

### 穿越信号

```python
# 上穿阈值
cross_up   = (val > threshold) & (val.shift(1) <= threshold)

# 下穿阈值
cross_down = (val < threshold) & (val.shift(1) >= threshold)

# DataFrame vs DataFrame 金叉/死叉（两边都要 shift！）
golden_cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
dead_cross   = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))
```

### 技术指标实现

```python
# RSI (14)
adj_close = d['close'] * d['adj_factor']
delta = adj_close.diff()
gain  = delta.clip(lower=0).rolling(14).mean()
loss  = (-delta.clip(upper=0)).rolling(14).mean()
rsi   = 100 - 100 / (1 + gain / loss)

# KDJ
adj_close = d['close'] * d['adj_factor']
low_c  = d['low']  * d['adj_factor']
high_c = d['high'] * d['adj_factor']
low9   = low_c.rolling(9).min()
high9  = high_c.rolling(9).max()
rsv    = (adj_close - low9) / (high9 - low9) * 100
k_val  = rsv.ewm(com=2, adjust=False).mean()
d_val  = k_val.ewm(com=2, adjust=False).mean()
j_val  = 3 * k_val - 2 * d_val

# 波动率
ret    = (d['close'] * d['adj_factor']).pct_change()
vol_20 = ret.rolling(20).std()

# 成交量放量
vol_ma_20   = d['vol'].rolling(20).mean()
volume_spike = d['vol'] > vol_ma_20 * 2
```

### 持仓矩阵生成（必须用 hold_until）

```python
# 标准双信号
buy  = ...  # bool DataFrame
sell = ...  # bool DataFrame
out  = hold_until(buy, sell)

# 多卖点（多个卖出条件自动 OR 合并）
out = hold_until(buy, [sell1, sell2, sell3])
```

### 多因子组合

```python
# 各自排名 → 加权组合
f1_rank = row_rank(d['因子1'])
f2_rank = row_rank(d['因子2'])
f3_rank = row_rank(1 - d['因子3'])  # 反向因子用 1 - rank
out = 0.5 * f1_rank + 0.3 * f2_rank + 0.2 * f3_rank
```

---

## 6. 常见错误和解决方案

### E1：axis=1 行方向计算

**症状**：代码里用了 `axis=1` 的聚合或排序
**原因**：各股票停牌时间不同，行不对齐
**解决**：所有计算按列方向（axis=0 / 默认），不要跨股票比较同一行

### E2：忘记复权

**症状**：回测结果看起来不对
**原因**：直接用 `d['close']` 而没用 `d['close'] * d['adj_factor']`
**解决**：所有价格运算前先手动乘 adj_factor

### E3：手写逆序 cumsum 而非 hold_until

**症状**：持仓矩阵逻辑错误，出现"空仓但没卖"、"持仓但没买"
**原因**：逆序 fill/cumsum 的逻辑容易出错
**解决**：全部改用 `hold_until(buy, sell)`

### E4：穿越信号两边忘记 shift

**症状**：信号在当天产生而非次日
**原因**：DataFrame 交叉时只 shift 了一边
**解决**：两边都 shift：`(A > B) & (A.shift(1) <= B.shift(1))`

### E5：字段名不存在

**症状**：代码引用了不存在的字段
**解决**：先调用 `available_data` 确认字段名。数据库内原始字段名与 AI 看到的名称中间有 `db_translate.json` 翻译层

### E6：factor_analysis 中重复 row_rank

**症状**：因子分析不需要自己调 row_rank
**原因**：`factor_analysis` 内部已自动做排名转换
**解决**：`out = d['字段名']` 即可，不需要 `out = row_rank(d['字段名'])`

### E7：并行调用返回 "有其它任务在执行"

**症状**：同时对 QuantAll 发多个工具调用，后面的返回 `"有其它任务在执行，稍后再试"`
**原因**：QuantAll 是单线程执行引擎，不支持并发
**解决**：所有 QuantAll 工具调用必须**串行**——上一个返回后才发下一个。同一策略的不同 view 也要一个一个跑。

### E8：timeline/factor_analysis pandas 3.0.3 兼容性问题（✅ 已修复）

**症状1**：`strategy_backtest(view="timeline")` 返回 `"异常：call stack is not deep enough"`
**症状2**：`factor_analysis` 报 `Argument 'f_days' has incorrect type (expected str, got int)` 或 `feature_days` 参数不生效
**根因**：**pandas 3.0.3 兼容性问题**。QuantAll 早期代码基于 pandas 2.* 开发，pandas 3.0+ 中部分行为变更（`str` 类型不再是 `object`、部分日期处理行为变更、`inplace` 参数废弃、类型签名更严格等）。
**解决**：更新代码兼容 pandas 3.0.3。`factor_analysis` 三种 mode（summary/daily/scatter）和不同 `feature_days` 值均已验证正常。
**⚠️ 重要提醒**：后续如果遇到任何 QuantAll 工具执行异常（非语法错误类），**可能是 pandas 3.0.3 兼容性问题**，应提醒用户检查。

### E9：`select_by_code` / `move_by_code` / `weight_by_code` 传入 Series 报错

**症状**：用了 `col_attrs['所属行业']` 或某个 Series 作为这些工具的 `out`，执行失败
**原因**：这些工具要求 `out` 是**DataFrame**（行=时间，列=股票），和 `d['close']` 维度一致。`col_attrs` 返回的是 Series（一个值对应一只股票），维度不匹配
**解决**：把 Series 复制成全量 DataFrame：
```python
# 错误：out 是 Series
code = "out = col_attrs['所属行业'] == '银行'"

# 正确：复制到和 d['close'] 同维度
s = (col_attrs['所属行业'] == '银行').astype(bool)
out = d['close'].notna().copy()  # 先创建同维度模板
for col in out.columns:
    out[col] = s[col]
```

### E10：`select_by_code` 筛选文本属性时报错

**症状**：`col_attrs['所属行业']` 是文本字符串，直接比较报错或执行失败
**原因**：exec 环境对文本操作有限制，或行业名称含中文/特殊字符
**解决**：文本属性可以直接用 `.get(col, '') == '目标值'` 做字符串比较。如果失败，先查有哪些可用值。

### E11：select_by_code 选了子集，回测仍然跑全市场

**症状**：先 `select_by_code` 筛了某个子集，再 `strategy_backtest`，结果仍是全市场。
**原因**：`select_by_code` 只影响 GUI 图层的选中状态，不过滤 `strategy_backtest` 的数据范围。
**解决**：用 `select_by_code` + `heat_map` / `move_by_code` 的组合来分析子集，或直接用 `select_by_code` 的 `全局平均` 对比。不要期望 select 能过滤回测数据。

### E12：stock_factor 表部分字段读取异常（⚠️ 已部分解决）

**症状**：`d['换手率']`、`d['市盈率TTM']` 等 `stock_factor` 表中的字段在 `move_by_code` 中报读取异常。
**解决**：`factor_analysis` 中可以正常使用这些字段（`d['换手率']`、`d['市盈率TTM']`、`d['市净率']`、`d['ROE']`、`d['股息率TTM']`、`d['总市值']` 等均实测正常）。`move_by_code` 场景下的兼容性待进一步验证。基础价量字段（`close`/`vol`/`amount`/`adj_factor`）始终稳定可用。

---

## 7. 热力图分析方法论

热力图是 QuantAll 的核心可视化工具，通过 `move_by_code` + `weight_by_code` + `heat_map` 三件套实现多维分析。

### 基本流程

```
new_layer_from_code（标记事件/选股）
→ move_by_code(direction="x")（设置 X 轴维度）
→ move_by_code(direction="y")（设置 Y 轴维度）
→ weight_by_code（可选：设置权重）
→ heat_map（读取热力图统计）
→ 分析矩阵数据，形成结论
```

### 典型用法

```
# 分析"因子 A × 因子 B"的多维关系
1. new_layer_from_code：标记所有感兴趣的事件/买点
2. move_by_code(x)：映射维度 A
3. move_by_code(y)：映射维度 B
4. heat_map：得到 A×B 的二维分布矩阵

# 分析"维度 × 收益率"的关系
1. new_layer_from_code：标记所有买入事件
2. move_by_code(x)：放量倍数 = d['vol'] / vol_ma20
3. move_by_code(y)：未来 N 日收益率
4. heat_map：得到放量×收益的二维分布矩阵
```

### heat_map 返回数据格式

```
matrix[i][j]: i=Y轴行, j=X轴列, origin=bottom-left
```

---

## 8. 进阶技巧

### 多步骤串联

不要试图在一个 code 里做所有事。用多个工具串联：

```
select_by_code（初筛）→ new_layer_from_code（标记）→ move_by_code（分析）
→ heat_map（统计）→ 如果发现规律 → strategy_backtest（验证）
```

### 迭代分析

同一个问题可以多轮迭代：

```
第一轮：factor_analysis(mode=summary) → 看 IC 概览
第二轮：factor_analysis(mode=daily)   → 看 IC 时序稳定性
第三轮：factor_analysis(mode=scatter) → 看截面分布
第四轮：move_by_code + heat_map       → 多维交叉验证
```

### 善用 offset_days

`strategy_backtest` 的 `offset_days` 跳过指标预热期，避免开头的 NaN 干扰：

```python
# MA20 至少需要 20 天数据才稳定
strategy_backtest(name="MA策略", code=..., offset_days=20, view="summary")
```

### 严格回测 vs 收盘操作

- `use_price="close"`：当日收盘价成交（实战可用性偏低）
- `use_price="next_open"`：次日开盘成交（推荐，更贴近实盘）

量价分析用 close 没问题，但策略回测优先用 next_open。

---

## 附录：工具速查

| 工具 | 一句话 | code 输出类型 |
|------|--------|--------------|
| `strategy_backtest` | 策略回测 | bool（持仓矩阵） |
| `factor_analysis` | 因子有效性评估 | 数值（因子值） |
| `new_layer_from_code` | 创建标记图层 | bool（True=标记） |
| `select_by_code` | 筛选股票 | bool（True=选中） |
| `move_by_code` | 坐标轴映射 | 数值（控制位置） |
| `weight_by_code` | 统计权重 | 数值（控制权重） |
| `heat_map` | 热力图统计 | 不需要 code |
| `available_data` | 查看可用字段 | 不需要 code |
| `ping` | 健康检查 | 不需要 code |
| `get_user_selection` | 用户当前选中 | 不需要 code |
