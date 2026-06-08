# longbridge-smc

聪明钱概念（Smart Money Concepts / ICT）信号引擎：识别 BOS（Break of Structure 结构突破）、ChoCH（Change of Character 特性变化）、FVG（Fair Value Gap 公允价值缺口）、Order Block（订单块）、流动性抓取，综合判断机构资金偏向（多头/空头结构）。

## Requirements

> ⚠️ **额外依赖 / Extra dependency required**
>
> 此 skill 优先使用第三方 Python 库 **smartmoneyconcepts**，使用前建议安装：
>
> ```bash
> pip install smartmoneyconcepts
> ```
>
> 若未安装，LLM 自动回退到手动 Python 实现 BOS / ChoCH / FVG / Order Block 基础逻辑。
> This skill prefers the **smartmoneyconcepts** library: `pip install smartmoneyconcepts`. Falls back to manual implementation if unavailable.

> Simplified Chinese / Traditional Chinese / English.

## Workflow

1. 提取标的代码，标准化为 `<CODE>.<MARKET>` 格式。
2. 获取 OHLCV 数据（日线为主，建议同时拉 1 小时线用于多周期确认）：
   ```bash
   # 日线（主要结构判断）
   longbridge kline <SYMBOL> --period day --count 200 --format json
   # 1小时线（辅助精确入场区域，可选）
   longbridge kline <SYMBOL> --period 60m --count 400 --format json
   ```
3. 尝试使用 smartmoneyconcepts 库分析：
   ```python
   from smartmoneyconcepts import smc
   import pandas as pd
   # ohlcv: pd.DataFrame，列：open/high/low/close/volume
   bos_choch = smc.bos_choch(ohlcv)          # BOS / ChoCH
   fvg        = smc.fair_value_gaps(ohlcv)    # FVG 区间
   ob         = smc.ob(ohlcv)                 # 订单块
   ```
4. 若 smartmoneyconcepts 不可用，使用 Python 手动实现基础逻辑：
   - **BOS**：价格突破最近一个摆动高点（看涨 BOS）或摆动低点（看跌 BOS）
   - **ChoCH**：在下降趋势中首次突破摆动高点（多头 ChoCH），或在上升趋势中首次跌破摆动低点（空头 ChoCH）
   - **FVG**：连续三根 K 线中，第一根高点低于第三根低点（看涨 FVG），或第一根低点高于第三根高点（看跌 FVG）
   - **Order Block**：BOS/ChoCH 前最后一根方向相反的 K 线
5. 综合多信号判断机构偏向，输出多头结构或空头结构结论。

> 若环境未安装 smartmoneyconcepts，提示用户运行 `pip install smartmoneyconcepts`，或自动回退至手动实现。
> 若不确定 CLI 参数，先运行 `longbridge kline --help` 查看最新参数。

## CLI

```bash
# 日线数据（主要数据源）
longbridge kline AAPL.US --period day --count 200 --format json

# 1小时数据（辅助多周期确认，可选）
longbridge kline 700.HK --period 60m --count 400 --format json
```

## Output

以自然语言呈现，包含：

- **结构判断**：多头结构（Bullish Structure）/ 空头结构（Bearish Structure）
- **BOS / ChoCH 信号**：最近突破/变化位置、价格、日期
- **FVG 区间**：[FVG 低点, FVG 高点]、方向（看涨/看跌）、是否已被填充
- **订单块（Order Block）**：[OB 低点, OB 高点]、方向、强度评级
- **流动性区域**：近期高点（卖方流动性）/ 近期低点（买方流动性）
- **综合建议**：机构偏向 + 潜在入场区域 + 失效条件
- **数据来源**：Longbridge Securities / 数据来源：长桥证券 / 數據來源：長橋證券

## Error handling

| 情形                            | 简体回复                                                  | 繁體回覆 / English                                                                                                |
| ------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `command not found: longbridge` | 尝试 MCP fallback；否则请安装 longbridge-terminal         | 嘗試 MCP fallback；否則請安裝 longbridge-terminal / Try MCP fallback; otherwise install longbridge-terminal       |
| stderr 含 `not logged in`       | 请运行 `longbridge auth login`                            | 請運行 `longbridge auth login` / Run `longbridge auth login`                                                      |
| Python 缺少 smartmoneyconcepts  | 请运行 `pip install smartmoneyconcepts`；自动回退手动实现 | 請運行 `pip install smartmoneyconcepts` / Run `pip install smartmoneyconcepts`; fallback to manual implementation |
| smartmoneyconcepts API 不兼容   | 请运行 `pip install --upgrade smartmoneyconcepts`         | 請升級套件 / Run `pip install --upgrade smartmoneyconcepts`                                                       |
| 其他 stderr                     | 原样返回错误，不静默重试                                  | 原樣返回錯誤 / Surface verbatim, never retry silently                                                             |
| 数据量不足（K 线少于 50 根）    | 建议增大 `--count` 或切换更高周期                         |
| 其他 stderr                     | 原样透传，不静默重试                                      |
