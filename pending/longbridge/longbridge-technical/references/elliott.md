# longbridge-elliott

艾略特波浪理论信号引擎：基于 Zigzag 摆动点识别，自动匹配五浪推动结构（1-2-3-4-5）与三浪调整结构（A-B-C），辅以斐波那契比率校验，输出当前波浪位置、目标价位与止损风险位。

> Simplified Chinese / Traditional Chinese / English.

## Workflow

1. 提取标的代码，标准化为 `<CODE>.<MARKET>` 格式。
2. 获取日线 OHLCV 数据（200 根 K 线）：
   ```bash
   longbridge kline <SYMBOL> --period day --format json   # run --help for available flags
   ```
3. **Zigzag 识别摆动点**（Python 实现，threshold 默认 5%）：
   ```python
   def zigzag(highs, lows, threshold=0.05):
       # 寻找局部高低点序列
       # 相邻同向点取极值合并，反向超过 threshold 才确认新摆动点
       ...
   ```
4. **匹配五浪推动结构**，需满足：
   - 波 3 不是最短浪（通常最长）
   - 波 4 不与波 1 价格区间重叠
   - 波 2 回撤不超过波 1 起点
5. **斐波那契校验**：
   - 波 2 回撤：0.382–0.618 × 波 1
   - 波 3 延伸：≥ 1.618 × 波 1（常见 1.618–2.618）
   - 波 4 回撤：0.236–0.382 × 波 3
   - 波 5 ≈ 波 1（容差 ±20%）
6. **匹配三浪调整结构** A-B-C（推动浪结束后出现）：
   - B 浪回撤：0.382–0.786 × A 浪
   - C 浪 ≈ A 浪（容差 ±20%）
7. 输出当前波浪位置、目标价位、止损位。

> 若不确定 CLI 参数，先运行 `longbridge kline --help` 查看最新参数。

## CLI

```bash
# 日线数据（主要数据源）
longbridge kline AAPL.US --period day --format json   # run --help for available flags

# 周线数据（辅助验证大级别波浪）
longbridge kline TSLA.US --period week --format json
```

## Output

以自然语言呈现，包含：

- **当前波浪位置**：如"5 浪推动中的第 3 浪上升段"、"ABC 调整中的 C 浪"
- **斐波那契关键位**：目标价位（扩展位）+ 支撑/阻力位
- **止损风险位**：结构失效价位
- **置信度说明**：斐波那契比率符合程度（完全符合/部分符合/仅供参考）
- **数据来源**：Longbridge Securities / 数据来源：长桥证券 / 數據來源：長橋證券

## Error handling

| 情形                            | 简体回复                                                                | 繁體回覆 / English                                                                                                      |
| ------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `command not found: longbridge` | 尝试 MCP fallback；否则请安装 longbridge-terminal                       | 嘗試 MCP fallback；否則請安裝 longbridge-terminal / Try MCP fallback; otherwise install longbridge-terminal             |
| stderr 含 `not logged in`       | 请运行 `longbridge auth login`                                          | 請運行 `longbridge auth login` / Run `longbridge auth login`                                                            |
| Zigzag 摆动点不足               | 建议切换更长周期（如周线），运行 `longbridge kline --help` 查看可用参数 | 建議切換更長週期，執行 `longbridge kline --help` / Switch to a longer period; run `longbridge kline --help` for options |
| 无法匹配任何波浪结构            | 当前数据暂无清晰波浪结构，建议等待更多确认                              | 當前數據暫無清晰波浪結構 / No clear wave structure yet, wait for more confirmation                                      |
| 其他 stderr                     | 原样返回错误，不静默重试                                                | 原樣返回錯誤 / Surface verbatim, never retry silently                                                                   |
| 其他 stderr                     | 原样透传，不静默重试                                                    |
