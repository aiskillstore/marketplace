# zach-sif-cvr-threshold-analyzer

> **作者**：Zach ｜ 公众号「Zach的进化笔记」
>
> Learn in public！把 ASIN 360 业务报表和 SIF 自然排名数据变成可盯盘的 CVR 风险线。

Amazon CVR and organic-rank threshold analyzer.

它帮助卖家回答一个很具体的问题：

1. 站外放量之后，CVR 低到什么区间会增加自然排名波动风险
2. 哪条线适合日常观察，哪条线适合暂停或收缩放量前复核
3. 广告 CVR 是否也在同时变差，说明问题可能不只是站外流量稀释
4. 核心词和稳定词的自然位波动，是否与业务报表里的低 CVR 同步出现

## 推荐安装方式：让 AI 帮你装

推荐在以下 IDE 中直接用自然语言安装：

- Claude Code
- Codex
- Cursor

把下面这句话直接发给你的 AI：

```text
帮我安装 `zach-sif-cvr-threshold-analyzer` 这个 skill，来源仓库是 `amazon-skills`。直接装到当前工作区，并把依赖一起检查好。
```

手动安装仍然保留，但只作为降级方案：
[../../docs/manual-install.md](../../docs/manual-install.md)

## 快速开始

先用仓库自带样例跑通：

```bash
python3 skills/zach-sif-cvr-threshold-analyzer/scripts/analyze_cvr_rank_threshold.py \
  --business-report skills/zach-sif-cvr-threshold-analyzer/examples/business-report-sample.csv \
  --sif-cache skills/zach-sif-cvr-threshold-analyzer/examples/sif-daily-keyword-sample.json \
  --asin B0PUBLIC01 \
  --brand ExampleBrand \
  --site US \
  --launch-date 2026-01-05 \
  --core-keywords "portable espresso maker,travel coffee maker" \
  --analysis-date 2026-01-20
```

默认输出到：

```text
outputs/zach-sif-cvr-threshold-analyzer/ExampleBrand/
```

## 真实使用方式

1. 从领星 ASIN 360 导出目标 ASIN 的日级业务报表。
2. 让你的 AI/IDE 调用你自己的 SIF MCP，拉取同一日期窗口的日级关键词自然排名明细，并保存为 JSON。
3. 用 `--business-report` 指向业务报表，用 `--sif-cache` 指向 SIF JSON，再运行脚本。

示例：

```bash
python3 skills/zach-sif-cvr-threshold-analyzer/scripts/analyze_cvr_rank_threshold.py \
  --business-report /path/to/asin-360-business-report.csv \
  --sif-cache /path/to/your-sif-daily-keyword-cache.json \
  --asin B0XXXXXXXX \
  --brand YourBrand \
  --site US \
  --launch-date 2026-01-05 \
  --core-keywords "main keyword,model keyword"
```

## 输入

业务报表最低需要：

- 日期
- ASIN
- Session
- 整体 CVR

推荐同时提供：

- 广告 CVR
- 自然 CVR
- 广告点击
- 广告订单
- 自然订单
- 销量
- 订单量

SIF JSON 需要按日期保存关键词明细，至少包含：

- `keyword`
- 自然排名变化信息，例如 `pchangeReason.nfInfo.change`
- 可选的 `scoreRatio` / `score`，用于自动筛选核心词和稳定词

## 输出

- Markdown 主报告
- CSV 日级面板
- CSV 阈值候选
- JSON 稳定词篮子

报告会输出：

- 观察线
- 危险线
- 广告 CVR 确认线
- 命中率、召回率、Lift
- 核心词和稳定词自然位波动事件
- 需要人工复核的关注事项

## 依赖

- Python 3.9+
- 可选：openpyxl，用于更稳地读取 `.xlsx` / `.xlsm`

CSV 不需要额外依赖。没有 openpyxl 时，脚本会尝试使用内置的轻量 XLSX 读取器。

## 如果安装或运行出错，直接让 AI 帮你排查

把下面这段直接发给你的 AI，并把报错信息、截图或终端输出一起贴上：

```text
我已经安装了 `zach-sif-cvr-threshold-analyzer`，但现在遇到了问题。请你直接帮我排查并尽量修复：

1. 先判断是 skill 文件缺失、业务报表字段不匹配、SIF JSON 结构不匹配、脚本路径错误，还是当前 IDE 没有正确加载
2. 自动检查当前工作区里和 `zach-sif-cvr-threshold-analyzer` 相关的文件、脚本、examples、references 和输出目录
3. 如果可以自动修复，就直接修复
4. 修复后告诉我还需要重启 IDE、重新加载工作区，还是重新运行哪个命令
5. 最后给我一个最短的验证步骤，确认这个 skill 已经能用了
```

## 关于作者

关注「**Zach的进化笔记**」，获取 AI x 跨境电商的实战经验、工具和方法论：

<img src="../../assets/traffic/wechat-official-account.jpg" width="200" alt="公众号二维码" />

扫码加入交流群，一起交流 AI + 跨境电商的实战玩法：

<img src="../../assets/traffic/wechat-group.jpeg" width="200" alt="wechat-group" />
