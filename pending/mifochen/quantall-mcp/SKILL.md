---
name: QuantAll-mcp
description: >
  QuantAll（全A解析）MCP —— 股市全市场向量化并行计算引擎，
  支持5000+股票因子计算、策略回测、因子IC分析及GPU多维可视化。13个工具。
  触发：回测/因子分析/选股/策略/IC分析等量化场景，或用户表述股市想法时AI主动计算验证。
  安装：SkillHub→venv→pip install quantall(清华源)→mcp.json→启动→⚠️重连MCP。
  更新：版本变更→pip install --upgrade quantall(清华源)→重启→⚠️重连MCP。
  常见坑：Git Bash用C:/、safe-delete冲突重建venv、import大小写QuantAll。
agent_created: true
license: MIT
---

# QuantAll（全A解析）MCP 技能

---

## 📦 安装与升级

### 快速安装（首次安装，AI 必读）

```
□ 1. 创建 venv：
   C:/Users/<用户>/.workbuddy/binaries/python/versions/3.13.12/python.exe -m venv <skill-dir>/scripts/.venv
□ 2. pip 安装（务必用清华源，45个包300MB+）：
   .venv/Scripts/python.exe -m pip install quantall -i https://pypi.tuna.tsinghua.edu.cn/simple
□ 3. 验证：.venv/Scripts/python.exe -c "from QuantAll import Start_main; print('OK')"
□ 4. 配置 ~/.workbuddy/mcp.json（见下方）
□ 5. 启动：.venv/Scripts/python.exe Start_QuantAll.py，检查 8686 端口
□ 6. ⚠️ 提醒用户：重连 MCP 连接器（或重启 WorkBuddy）
```

> ⚠️ **Git Bash 路径**：传参给 Python 必须用 `C:/` 前缀（非 `/c/`），否则双重转义导致找不到文件。
> ⚠️ **safe-delete 冲突**：WorkBuddy Python 运行时可能拦截 pip 文件覆盖，报 `SAFE_DELETE_FAIL_CLOSED`。解决：重建 venv（`rm -rf .venv && python -m venv .venv`）后重试，或用 `dangerouslyDisableSandbox: true`。
> ⚠️ **大小写**：`import QuantAll`（大写 Q、A），`import quantall` 会失败。
> ⚠️ **MCP 重连**：QuantAll 是 HTTP MCP，WorkBuddy 不会自动发现，必须手动信任或重启 WorkBuddy。
> ⚠️ **用户协议**：首次启动弹协议窗口，点击确认即"激活"（永久同意），功能无差异。

### 技能更新/升级（版本变更时，AI 必读）

> **核心规则**：技能包文件更新后，Python 库 `quantall` 也必须同步升级，否则新接口在旧库上会报错。

```
□ 1. 升级：.venv/Scripts/python.exe -m pip install --upgrade quantall -i https://pypi.tuna.tsinghua.edu.cn/simple
□ 2. 验证：.venv/Scripts/python.exe -c "import QuantAll; print(QuantAll.__version__)" 确认 >= requirements.txt 要求
□ 3. 重启 QuantAll 服务（先关旧进程再启动）
□ 4. ⚠️ 提醒用户重连 MCP
```

> safe-delete 冲突时：先 `pip uninstall quantall`，再 `pip install quantall`。
> 不确定是否需要升级时直接执行——`pip install --upgrade` 是幂等的。
> 版本检测：对比 `_meta.json` 的 version 与已安装库 `QuantAll.__version__`。

### MCP 配置

```json
{
  "mcpServers": {
    "全A解析": { "url": "http://127.0.0.1:8686/mcp", "disabled": false },
    "UpdateStock": {
      "command": "<skill-dir>/scripts/.venv/Scripts/python.exe",
      "args": ["<skill-dir>/scripts/UpdateStock_skill.py"],
      "disabled": false, "disabledTools": []
    }
  }
}
```

> UpdateStock 可选——QuantAll 独立运行，无需 UpdateStock。

### 桌面快捷方式（可选，AI 主动询问）

创建 `scripts/run.bat`（技能包不携带，需自行创建）：

```bat
@echo off
cd /d "%~dp0"
start "" .venv\Scripts\pythonw.exe Start_QuantAll.py %*
```

> `start ""` 空标题必须（路径含引号时）；`pythonw.exe` 无控制台窗口。再用 pywin32 创建桌面 `.lnk`。

---

## 架构概述

- **QuantAll**（HTTP MCP，8686 端口）：独立的本地计算引擎，因子计算/回测/IC分析/可视化。**完全免费**。
- **UpdateStock**（stdio MCP，可选）：数据库管理，需 tushare API key。
- 两者共用同一个 DuckDB 数据库，路径通过 `scripts/DB_setting.json` 管理。
- **核心定位**：QuantAll 只需本地数据库即可工作，UpdateStock 不是必需依赖。

### 数据库方案

| 方案 | 说明 |
|------|------|
| A. 内置 Test.duckdb | pip 包自带，仅沪深300近两年基础行情，仅供测试。**pip 更新会覆盖**。 |
| B. UpdateStock 创建 | 需 tushare：完整版(2000+积分)全市场全表 / 精简版(200积分免费)仅 OHLCV |
| C. 自有数据库 | 修改 `DB_setting.json` 的 `db_path` 直连，可调整 `data/db_translate.json` 字段翻译 |

> QuantAll 只是计算引擎，数据库里有什么字段就能算什么。字段名经 `db_translate.json` 翻译层映射为中文。

### UpdateStock 工具表

| 工具 | 用途 |
|------|------|
| `ping` | 健康检查 |
| `Creat_DB` | 创建数据库 |
| `Update_Stock_Data` | 全量更新（需 tushare 2000+） |
| `Update_Stock_Data_easy` | 增量更新（需 tushare 200，免费） |
| `get_stock` / `get_adj_stock` | 查询行情（非复权/前复权） |
| `Start_QuantAll` | 启动 QuantAll |
| `Set_QuantAll_DataBase` | 设置数据库路径和天数 |

---

## Python Exec 环境规范

所有需要 `code` 参数的工具共享相同的 exec 环境。

| 变量 | 类型 | 说明 |
|------|------|------|
| `d` | dict[str, DataFrame] | key=字段名，value=面板数据（行=时间，列=股票） |
| `col_attrs` | dict[str, Series] | 股票属性（行业、市值等） |
| `np`, `pd` | module | numpy, pandas |

**默认字段**（d 中）：`close`, `open`, `high`, `low`, `vol`, `amount`, `adj_factor`
> 复权价格：`adj_close = d['close'] * d['adj_factor']`，high/low 同理

**股票属性**（col_attrs 中）：`股票代码`, `股票名称`, `所属行业`, `所在省份`, `交易所`, `所属概念` 等

**约束**：
- **禁止**：import / for/while 循环 / df.apply() / lambda / 递归 / axis=1 行方向计算
- **必须**：所有运算向量化，代码最后一行设 `out = ...`

---

## QuantAll 工具总览

| 工具 | 说明 | 核心输出 |
|------|------|----------|
| `ping` | 健康检查 | "pong" |
| `available_data` | 查看可用字段 | 字段名列表 |
| `strategy_backtest` | 策略回测 | 收益/夏普/回撤/胜率 |
| `factor_analysis` | 单因子IC分析 | IC均值/IR/正占比/多空差 |
| `batch_factor_analysis` | 批量因子IC分析 | list（每因子IC/IR） |
| `save_factor_result` | 保存因子结果 | 保存到数据库 |
| `new_layer_from_code` | 创建图层标记 | bool → 可视化短线 |
| `select_by_code` | 筛选股票（集合运算） | bool → 选中集合 |
| `move_by_code` | 坐标平移映射 | 数值 → 热力图 |
| `weight_by_code` | 权重设置 | 数值 → 加权统计 |
| `heat_map` | 热力图统计 | 矩阵统计 |
| `get_user_selection` | 获取用户选中 | 股票代码列表 |
| `MCP_Close` | 关闭服务 ⚠️ | 无 |

> **关键机制**：不支持并行调用（串行执行）；select_by_code 只影响 GUI 图层不影响回测数据；每股因子必须除以 close。

---

### strategy_backtest — 策略回测

用代码生成持仓矩阵（bool DataFrame），自动计算绩效。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | string | 必填 | 策略名称 |
| `code` | string | 必填 | `out = bool DataFrame`（True=持仓） |
| `use_price` | enum | `close` | `close`/`next_open`（严格回测用 next_open） |
| `view` | enum | `summary` | `summary`/`detail`/`segments`/`timeline` |
| `offset_days` | int | `0` | 跳过头部 N 天（避开预热期） |
| `open_commission` | float | `0.00025` | 买入手续费 |
| `close_commission` | float | `0.00075` | 卖出手续费 |

| view | 返回 | 后续分析 | 用途 |
|------|------|----------|------|
| `summary` | 聚合统计 | ✅ select/move/heat_map | **第一步必跑**，判断策略价值 |
| `segments` | 聚合统计 | ✅ 因子分析 | 分析买入前因子对收益影响 |
| `detail` | 逐股票指标 | ✅ | AI 内部分析 Top/Bottom（返回~140万字符，**禁止直接展示**） |
| `timeline` | 每日序列 | ❌ 只读 | 观察时间分布 |

> 持仓矩阵**必须用 `hold_until(buy, sell)`** 生成。

```python
DeferExecuteTool(toolName="mcp__全A解析__strategy_backtest", params={
  "name": "双均线交叉",
  "code": "adj_close = d['close'] * d['adj_factor']\nma5 = adj_close.rolling(5).mean()\nma20 = adj_close.rolling(20).mean()\nbuy = (ma5 > ma20) & (ma5.shift(1) <= ma20.shift(1))\nsell = (ma5 < ma20) & (ma5.shift(1) >= ma20.shift(1))\nout = hold_until(buy, sell)",
  "use_price": "next_open", "offset_days": 20, "view": "summary"
})
```

### factor_analysis — 因子分析

评估因子与未来收益的 Spearman 秩相关（Rank IC）。标准流程：`summary → daily → scatter`。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | string | 必填 | 因子名称 |
| `code` | string | 必填 | `out = 数值 DataFrame` |
| `feature_days` | int | `1` | 评估未来第 N 天收益 |
| `mode` | enum | `summary` | `summary`/`daily`/`scatter` |

| mode | 返回 | 后续分析 | 用途 |
|------|------|----------|------|
| `summary` | IC均值/IR/正占比/多空差 | ✅ move/heat_map/select | **第一步**，判断因子有效性 |
| `daily` | 每日IC时序 | ❌ 只读 | 看IC时序稳定性 |
| `scatter` | 同summary聚合 | ✅ | 观察因子-收益关系随时间演变 |

> |IC_IR| > 0.3 视为有效。单因子不需手动 `row_rank()`，复合因子需手动 rank 后组合。
> **每股因子必须除以 close**：`out = d['每股收益'] / d['close']`（E/P比率），否则无预测力。比率类/增长率类不需要除。

### batch_factor_analysis — 批量因子分析

| 参数 | 说明 |
|------|------|
| `factor_dict` | dict[str,str]，因子名称→代码字典 |
| `feature_days` | int，未来第N天收益 |

返回 list，每个元素与 factor_analysis summary 结构一致。排名规则同 factor_analysis。

### save_factor_result — 保存因子结果

| 参数 | 说明 |
|------|------|
| `result` | factor_analysis 或 batch_factor_analysis 的返回值 |
| `note` | 备注 |

---

### 可视化分析管道

`new_layer_from_code` 是视觉探索入口，标记 (股票, 日期) 散点后通过平移/权重/筛选/热力图深度分析。

**管道**：`new_layer_from_code → move_by_code(x/y) → weight_by_code(可选) → select_by_code(可选) → heat_map`

软件只维护**一个活动图层**，新的 `new_layer` 替换旧的。`strategy_backtest` 和 `factor_analysis(scatter)` 也会创建图层。

#### new_layer_from_code

| 参数 | 说明 |
|------|------|
| `name` | 图层名称 |
| `code` | `out = bool DataFrame`（True 位置绘制短线） |

> move/weight/select 代码中可用 `.shift(N)` 取标记日前数据，`.shift(-N)` 取标记日后数据（如未来收益）。

#### move_by_code

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `code` | 必填 | `out = 数值 DataFrame`，映射到 X/Y 轴 |
| `direction` | `y` | `x` 或 `y`（双向独立，同方向覆盖） |
| `to_percentile` | `true` | 转排名值(0~1)消除量纲 |
| `optimized_display` | `false` | 散点超10万时建议开启 |

> 返回完整热力图数据（无需单独调 heat_map）。`to_percentile=false` 时分布不均是正常现象（金融数据天然偏态）。

#### weight_by_code

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `code` | 必填 | `out = 数值 DataFrame` |
| `to_percentile` | `true` | 转排名值 |

新权重替换旧权重（不叠加），影响 heat_map 加权统计。不改变有效数量。

#### select_by_code

| 参数 | 说明 |
|------|------|
| `mode` | `A`(新选)/`AB`(∩)/`A+B`(∪)/`A-B`/`B-A`/`A+B-AB`(对称差) |
| `code` | `out = bool DataFrame` |

筛选后自动重新统计所有维度。select 不影响回测数据范围。

#### heat_map

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `mode` | `auto` | `auto`(10等分)/`percent`(排名范围)/`value`(数值范围) |
| `x_range`, `y_range` | — | 范围（percent/value 模式） |

> matrix[i][j]: i=Y行, j=X列, origin=bottom-left。move/weight/select 返回中已含默认 10×10 矩阵，heat_map 用于自定义范围缩放。

#### get_user_selection

获取用户在 GUI 端框选的散点。返回：`primary_code`, `top_100`(前100只), `select_count`, `total_count`。

> GUI 交互：右键拖拽方向决定操作——红=重选、绿=清空、紫=加、青=减。选中≤20个绘制K线图，>20个绘制热力统计图。

---

## 核心函数

| 函数 | 说明 |
|------|------|
| `hold_until(buy, sell)` | 生成持仓矩阵（回测必须用），sell 可传 list 自动 OR 合并 |
| `entry_check(window, conditions, mode)` | 买入窗口条件检测，mode: keep/discard/left/right/start/end/next |
| `row_rank(df, split=[])` | 横截面排名→百分位(0~1)，split 可分组排名 |
| `get_time()` | 返回时间整数 |
| `time_at(rq)` | 匹配时间（负数=倒数第N天） |
| `time_between(srq, erq)` | 匹配时间区间（左闭右开） |
| `time_in(rqs)` | 匹配多个指定时间 |

---

## 策略代码模板

### 双均线交叉

```python
adj_close = d['close'] * d['adj_factor']
ma5 = adj_close.rolling(5).mean()
ma20 = adj_close.rolling(20).mean()
buy = (ma5 > ma20) & (ma5.shift(1) <= ma20.shift(1))
sell = (ma5 < ma20) & (ma5.shift(1) >= ma20.shift(1))
out = hold_until(buy, sell)
```

### 市值+动量复合因子

```python
adj_close = d['close'] * d['adj_factor']
momentum = adj_close.pct_change(20)
m_rank = row_rank(momentum)
size_rank = row_rank(d['总市值'])
out = 0.7 * m_rank + 0.3 * (1 - size_rank)
```

> 更多模板（RSI、放量突破、KDJ等）参见 `references/quantall_playbook.md`。

---

## 典型工作流程

**回测**：ping → available_data → strategy_backtest(summary) → 深挖 detail/segments
**因子分析**：available_data → factor_analysis(summary) → daily/scatter → batch → save
**可视化探索**：new_layer → move(x/y) → weight(可选) → select(可选) → heat_map

> **AI 行为底线**：先 ping 确认服务 → 先 available_data 确认字段 → 代码向量化 → 先 summary 后 detail → 客观呈现
> **实战经验文档**：`references/quantall_playbook.md` 含详细模式、代码模板、踩坑记录。复杂任务前建议先读。

---

## 注意事项

- 持仓生成必须用 `hold_until`，禁止手写逆序 cumsum
- 穿越信号：上穿 `(val > t) & (val.shift(1) <= t)`，两边都 shift
- 复权价格必须手动算：`adj_close = d['close'] * d['adj_factor']`
- 每股因子必须除以 close（非复权价），比率类/增长率类不需要
- 禁止 axis=1（行方向计算），各股票时间不对齐
- 严格回测推荐 `use_price="next_open"` + `offset_days`
- 手续费默认买入万2.5、卖出万7.5（含印花税）
- `row_rank` 返回百分位值(0~1)
- MCP_Close 仅明确不再需要时调用
- 不支持并行工具调用，所有调用串行

## 版本历史

- **v1.0** — 首版发布，13个工具，配套 playbook 实战手册。PyPI 在线安装，包内置 Test.duckdb。
- **v1.0.1** — 新增「技能更新/升级流程」：版本变更时必须 `pip install --upgrade quantall`。`requirements.txt` 更新为 `>=1.0.1`。SKILL.md 精简至 500 行以内，详细用法移至 playbook。
