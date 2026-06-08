# Pre-Earnings Preview

The **pre-earnings** mode of `longbridge-earnings`: help an investor prepare for an
**upcoming** earnings release by surfacing prior guidance, recent events, the last call's
Q&A, and the key things to watch — so they don't have to dig through filings and transcripts
by hand.

> **Output**: an inline preview summary by default. Only if the user explicitly asks for a
> written file ("完整前瞻 / full preview") produce a single **Markdown** file —
> Markdown tables + Unicode `█` bars, no DOCX, no Python, no images — mirroring the
> post-earnings full-report style.

> **Response language**: match the user's input language (Simplified / Traditional / English).
> File names, ticker symbols, CLI commands, and metric abbreviations (EPS, YoY, CapEx…) always
> stay in English.

## Data Sources

Priority: **CLI (primary) → Web Search (supplement)**.

Before using any CLI command, run `longbridge <command> --help` to check the exact argument
format — the CLI is updated frequently and flags may change. Do not assume flag names.

**CLI docs**: https://open.longbridge.com/zh-CN/docs/cli/
**MCP fallback**: if the `longbridge` CLI is unavailable, the same data is reachable through MCP
(`claude mcp add --transport http longbridge https://mcp.longbridge.com`) — discover available
tools from the MCP server's tool list at runtime; do not rely on hardcoded tool names.

| Data Needed                 | CLI Entry Point                                            |
| --------------------------- | ---------------------------------------------------------- |
| Prior filings & guidance    | `longbridge filing --help`                                 |
| Financial statements        | `longbridge financial-report --help`                       |
| Analyst consensus estimates | `longbridge consensus --help`                              |
| EPS estimates & revisions   | `longbridge forecast-eps --help`                           |
| Operating history           | `longbridge operating --help`                              |
| Quote & valuation           | `longbridge quote --help` / `longbridge calc-index --help` |
| Price trend                 | `longbridge kline --help`                                  |
| Capital flow & positioning  | `longbridge capital --help`                                |
| Analyst ratings             | `longbridge institution-rating --help`                     |
| News & events               | `longbridge news --help`                                   |

**JSON output handling**: when parsing CLI JSON with Python or jq, save to a temp file first
(`longbridge <cmd> > /tmp/data.json`), then read it — the CLI may append version-notification
lines to stdout that break direct piping.

Web Search supplements: earnings call transcripts, options-implied move, whisper numbers,
recent industry events not yet in the CLI.

## Functional Modules

### Module A — Prior Quarter Guidance vs. Actual

Extract from the most recent earnings filing and call:

- **Guidance fulfillment**: the key metric is always **management's own prior guidance vs. the
  actual result** — not YoY, not consensus vs. actual. What did management guide for Q[N-1] at
  the end of Q[N-2], and how did the Q[N-1] actual compare?
- **Management outlook**: macro/sector views, strategic priorities, capital allocation.
- **Performance summary**: for each guided metric, the beat/miss amount and direction.

Table columns for 【一】:

```
指标 | 管理层此前指引（上上季电话会） | 上季实际值 | 与指引偏差 | 评估
```

- Col 2 = management's own guidance range/midpoint, NOT market consensus
- Col 3 = actual reported value
- Col 4 = (actual − guidance midpoint) / guidance midpoint, with sign
- Col 5 = 超预期 / 基本符合 / 不及预期

If management gave no quantitative guidance (e.g. exploration-stage companies), use operational
milestone commitment vs. actual progress instead. Use `longbridge filing --help` to locate prior
filings; for transcripts not in the CLI, web-search "[company] Q[X] earnings call transcript".

### Module B — Recent Events Tracking

Surface events since the prior release relevant to this quarter, categorized by **Macro/policy**,
**Industry**, **Company**, **Market sentiment**. Each event: timestamp, source, relevance to the
upcoming earnings. Use `longbridge news --help` and `longbridge institution-rating --help`; web
search for events not yet indexed.

### Module C — Prior Earnings Call Q&A Summary

From the prior call transcript: **high-frequency analyst questions** (margins, segment growth,
capex…), **management's response** (key judgment, not verbatim), and **verification significance**
(which Q&A topics this quarter's results will answer). Source: web search for the transcript.

### Module D — Key Focus Framework for This Quarter

Synthesize A–C into an actionable preview:

- **Guidance fulfillment checklist**: each prior quantitative guidance item → the specific data
  point to check.
- **Beat / miss risk factors**: what could surprise in either direction.
- **3–5 key questions to watch**: plain language, combining institutional focus with the user's
  holding thesis.
- **Risk flags**: tail risks from prior management warnings + recent external events.

### Module E — Historical Guidance Fulfillment Tracking

Pull 4–8 quarters to establish management's track record: guidance-vs-actual table by quarter;
bias pattern (consistently conservative or optimistic?); metric reliability (tight vs. wide
historical deviation); and a **credibility assessment for the current guidance**. Use
`longbridge financial-report --help`, `longbridge operating --help`, `longbridge consensus --help`.

### Module F — Market Consensus vs. Management Guidance

Identify expectation gaps: current consensus for key metrics; comparison with management guidance
(above / below / within range); historical consensus accuracy; and **expectation-gap alerts**
flagging significant divergences as upside or downside risk. Use `longbridge consensus --help`
and `longbridge forecast-eps --help`.

## Output — Inline Preview Summary

Use exactly this structure. Skip any section with no data with a one-line note
(e.g. "暂无电话会记录，跳过"). Do not rename, reorder, or add sections.

```
📊 [公司名称（股票代码）] 财报前瞻摘要
财报发布日期：{日期} | 分析日期：{今天}
════════════════════════════════════════

【一】上期业绩指引回顾
▸ [指标]：管理层指引 {区间/中值} → 实际 {值}（{超预期/不及预期 +X%}）
  ※ 必须是管理层自身指引 vs. 实际，不是共识 vs. 实际，不是 YoY 对比
▸ ...

【二】管理层展望要点
▸ ...

【三】上期电话会 | 分析师核心 Q&A
Q1：[问题]
  ↳ 管理层答复：[结论]
  ↳ 本次关注：[需验证的指标]

【四】近期重要事件
▸ [日期] [来源] 事件描述 → 关联性：...

【五】历史指引兑现规律
▸ 收入指引：过去 N 季平均偏差 {方向} {幅度}
▸ EPS 指引：兑现率 {%}，平均偏差 {值}
▸ 本次指引可信度：{评估}

【六】市场一致预期 vs 管理层指引
  指标      市场预期   管理层指引   偏差
  收入      ...        ...          ...
  EPS       ...        ...          ...
▸ 预期差提示：...

【七】本次财报核心关注点
① ...
② ...
③ ...

【八】风险提示
⚠ ...

---
⚡ 数据来源：Longbridge CLI + Web Search | 仅供参考，不构成投资建议
```

## Output — Optional Markdown File

Only when the user explicitly asks for a written preview: produce a single file
`[SYMBOL]_Q[N]_[YEAR]_Earnings_Preview.md` covering the same eight sections, using Markdown
tables and Unicode `█` bars for any "charts". **No DOCX, no Python scripts, no image files** —
identical in spirit to the post-earnings full report.

## Error handling

| Situation                               | Response                                                                                                   |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Shell `command not found: longbridge`   | Fall back to MCP if configured; otherwise tell the user to install longbridge-terminal, then give a web-search-only preview with a clear label. |
| stderr `not logged in` / `unauthorized` | Tell the user to run `longbridge auth login`; can still proceed with web search for public data.           |
| Company has **already reported**        | Switch to the post-earnings path of this skill (lite summary card / full report) instead.                  |
| No CLI data + no web results            | State which modules have gaps; still deliver the available modules — never produce a blank preview.        |
| Other stderr                            | Surface verbatim — never silently retry.                                                                   |
