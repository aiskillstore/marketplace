# zach-search-term-report-analyzer

> **作者**：Zach ｜ 公众号「Zach的进化笔记」
>
> Learn in public！把 Amazon Ads 搜索词报告变成可复核的否词、控成本、放量和 Listing 反馈清单。

Amazon Ads search term report analyzer.

它面向 SP / SB / SD 搜索词报告，帮助卖家回答四个问题：

1. 哪些词已经明显浪费预算，需要优先复核否词或控 bid
2. 哪些词高于当前 ASIN 基准，值得继续测试或放量
3. 哪些属性词、场景词代表真实用户语言，应该反馈给 Listing
4. 7 / 14 / 30 天窗口里，哪些词的 CVR、ACOS 或趋势正在变化

## 推荐安装方式：让 AI 帮你装

推荐在以下 IDE 中直接用自然语言安装：

- Claude Code
- Codex
- Cursor

把下面这句话直接发给你的 AI：

```text
帮我安装 `zach-search-term-report-analyzer` 这个 skill，来源仓库是 `amazon-skills`。直接装到当前工作区，并把依赖一起检查好。
```

手动安装仍然保留，但只作为降级方案：
[../../docs/manual-install.md](../../docs/manual-install.md)

## 快速开始

安装 Python 依赖：

```bash
python3 -m pip install -r skills/zach-search-term-report-analyzer/requirements.txt
```

先清洗报表：

```bash
python3 skills/zach-search-term-report-analyzer/scripts/clean_search_term_report.py \
  skills/zach-search-term-report-analyzer/examples/search-term-report-sample.csv
```

再生成分析结果：

```bash
python3 skills/zach-search-term-report-analyzer/scripts/analyze_search_term_decisions.py \
  skills/zach-search-term-report-analyzer/examples/search-term-report-sample.csv \
  --brand ExampleBrand \
  --asin B0PUBLIC01 \
  --target-acos 0.20 \
  --listing-context-file skills/zach-search-term-report-analyzer/examples/listing-context-sample.md \
  --skip-live-listing-fetch
```

默认输出到：

```text
outputs/search-term-report-analyzer/ExampleBrand/
```

## 输入

支持 Amazon Ads 官方导出的 CSV / XLSX / XLSM / XLS 报表。最低需要这些字段：

- `date`
- `search_term`
- `clicks`
- `spend`

如果报表中有订单、销售额、CVR、ACOS、ROAS，脚本会一起使用；如果缺失，会保留基础流量与花费分析，不强行推断转化结论。

## 输出

- Markdown 主报告
- CSV 明细表
- CSV 异常清单
- JSON 运行摘要

每个搜索词会得到：

- 分类：品牌词、竞品词、ASIN 型词、核心品类词、属性词、场景词、无关词或暂不确定
- 动作标签：放量、保持测试、控 bid、否词候选、观察、Listing 反馈或人工复核
- 置信度和解释

## 依赖

- Python 3.10+
- pandas
- beautifulsoup4
- openpyxl
- curl（用于默认 live Listing fetch）

`fetch_listing_context.py` 默认会尝试抓取 Amazon 前台页面。如果你只想跑确定性离线分析，使用 `--skip-live-listing-fetch` 并传入 `--listing-context-file`。

## 如果安装或运行出错，直接让 AI 帮你排查

把下面这段直接发给你的 AI，并把报错信息、截图或终端输出一起贴上：

```text
我已经安装了 `zach-search-term-report-analyzer`，但现在遇到了问题。请你直接帮我排查并尽量修复：

1. 先判断是 skill 文件缺失、Python 依赖缺失、报表字段不匹配、脚本路径错误、Amazon 页面抓取失败，还是当前 IDE 没有正确加载
2. 自动检查当前工作区里和 `zach-search-term-report-analyzer` 相关的文件、脚本、examples、references 和依赖
3. 如果可以自动修复，就直接修复
4. 修复后告诉我还需要重启 IDE、重新加载工作区，还是重新运行哪个命令
5. 最后给我一个最短的验证步骤，确认这个 skill 已经能用了
```

## 关于作者

关注「**Zach的进化笔记**」，获取 AI x 跨境电商的实战经验、工具和方法论：

<img src="../../assets/traffic/wechat-official-account.jpg" width="200" alt="公众号二维码" />

扫码加入交流群，一起交流 AI + 跨境电商的实战玩法：

<img src="../../assets/traffic/wechat-group.jpeg" width="200" alt="wechat-group" />
