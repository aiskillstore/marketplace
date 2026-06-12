---
name: zach-sif-cvr-threshold-analyzer
description: |
  基于领星 ASIN 360 或同类日业务报表，以及用户自己 SIF MCP 导出的日级关键词自然排名 JSON，回测 CVR 与核心词/稳定词自然排名波动的关系，并输出观察线、危险线、广告 CVR 确认线。
  使用时机：站外放量、达人投放、联盟投放或内容种草后，需要判断 CVR 低到什么区间会增加自然排名波动风险。
  触发词：/zach-sif-cvr-threshold-analyzer
benefits-from: []
user-invocable: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
risk-level: medium
---

## 前置建议

本公开版 Skill 是自包含的，不依赖作者的本地工作区、店铺配置或私有数据源。

开始执行前，建议先读取本 Skill 自带材料：

- `references/input_schema.md` — 领星 ASIN 360 业务报表字段和兼容别名
- `references/threshold_method.md` — 阈值、命中率、召回率、Lift 的计算口径
- `scripts/analyze_cvr_rank_threshold.py` — 离线阈值分析脚本
- `examples/business-report-sample.csv` — 脱敏业务报表示例
- `examples/sif-daily-keyword-sample.json` — 脱敏 SIF 日级关键词排名缓存示例

## 定位

这个 Skill 用来回答一个具体问题：

> 站外放量期间，如果 ASIN 的整体 CVR 或广告 CVR 低于某个区间，是否更容易引发核心词或长期稳定词的自然排名波动？

它不是站外归因工具，也不会替用户修改广告、预算、价格、Coupon 或 Listing。它只把业务报表里的转化数据，与 SIF 日级关键词自然排名数据对齐，给运营一个可盯盘的风险阈值。

## 输入参数

| 参数 | 必须 | 默认值 | 说明 |
|------|------|--------|------|
| 业务报告 | 是 | - | `.csv` / `.xlsx` / `.xlsm`，优先使用领星 ASIN 360 日级 ASIN 业务数据 |
| ASIN | 是 | - | 目标 ASIN |
| SIF 缓存 | 是 | 自动查找输出目录内默认缓存名 | 用户自己的 SIF MCP/tooling 导出的日级关键词 JSON |
| 站点 | 否 | `US` | 用于输出标识 |
| 品牌 | 否 | `UnknownBrand` | 只用于输出目录和报告标题 |
| 投放开始日期 | 否 | 空 | 用于 pre/post 标记和稳定词筛选 |
| 核心关键词 | 否 | SIF 分数自动筛选 | 推荐人工传入 2-6 个核心大词或型号词 |
| 输出目录 | 否 | `outputs/zach-sif-cvr-threshold-analyzer/{brand}/` | 报告与 CSV 输出位置 |

## 执行流程

### Step 1: 准备业务报表

1. 从领星 ASIN 360 导出目标 ASIN 的日级业务报表，至少包含日期、ASIN、Session、整体 CVR。
2. 如果字段名不同，按 `references/input_schema.md` 做映射。
3. 如果报表内有多个 ASIN，必须用 `--asin` 指定单个目标，不要混合分析。

### Step 2: 准备 SIF 日级关键词缓存

让用户当前 IDE / Agent 调用用户自己的 SIF MCP，按日期获取目标 ASIN 的关键词流量和自然排名明细，并保存为 JSON。

缓存建议结构：

```json
{
  "source": "user-provided SIF cache",
  "daily": {
    "2026-01-01": {
      "details": [
        {
          "keyword": "example keyword",
          "scoreRatio": 0.02,
          "pchangeReason": {
            "nfInfo": {"change": "10_16"},
            "spInfo": {"change": "1_2"}
          }
        }
      ]
    }
  }
}
```

脚本只读取本地 JSON，不会直接访问任何作者私有服务。

### Step 3: 运行阈值分析

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

### Step 4: 解释排名波动事件

脚本自己定义“排名波动事件”，不是直接读取 SIF 的结论字段：

- 核心词自然位在 0/1/2 天窗口内下滑 5 位以上；
- 或核心词从 P1 掉出；
- 或稳定词篮子中 30% 以上关键词同步下滑。

稳定词篮子从投放前窗口自动筛选：

- 出现天数足够；
- 自然位中位数在 P1 范围内；
- SIF 有稳定流量贡献。

### Step 5: 输出三条线

1. **观察线**：优先高召回率，宁可早提醒，适合日常盯盘。
2. **危险线**：优先高命中率和 Lift，适合暂停或收缩站外放量前复核。
3. **广告 CVR 确认线**：只做辅助确认，用来判断广告流量是否也在低效承接。

如果样本不支持某条线，必须写“未找到足够稳健的阈值”，不要强行给伪精确数字。

## 输出文件清单

默认输出到：

```text
outputs/zach-sif-cvr-threshold-analyzer/{brand}/
```

| 文件 | 格式 | 命名 |
|------|------|------|
| 主报告 | `.md` | `{YYYY-MM-DD}_{site}_{asin}_CVR自然排名阈值分析.md` |
| 日级面板 | `.csv` | `{YYYY-MM-DD}_{site}_{asin}_CVR排名阈值_日级面板.csv` |
| 阈值候选 | `.csv` | `{YYYY-MM-DD}_{site}_{asin}_CVR排名阈值_候选阈值.csv` |
| 稳定词篮子 | `.json` | `{YYYY-MM-DD}_{site}_{asin}_CVR排名阈值_稳定词篮子.json` |

## 风险与边界

- **本 Skill 不做**：
  - 不直接修改广告预算、出价、否词、价格、Coupon 或 Listing
  - 不上传用户报表
  - 不沉淀真实店铺数据
  - 不把阈值解释成 Amazon 官方算法阈值
- **需要人工复核**：
  - 样本少于 21 天
  - 业务报告日期不连续或关键字段缺失
  - SIF 关键日期缺失
  - 观察线 / 危险线给出的动作涉及预算、价格或促销调整
  - 核心关键词没有人工确认
- **risk-level = medium**：
  - 本 Skill 会给出运营动作建议，但任何预算、价格、投放或页面执行都需要用户确认后手动完成。

## 完成后

报告完成状态：

- **DONE** — 业务报告、SIF 缓存、阈值报告和 CSV 面板全部完成
- **DONE_WITH_CONCERNS** — 已生成，但存在样本较小、SIF 缺日或某条阈值不稳健
- **BLOCKED** — 核心字段缺失、文件不可读、ASIN 无法确定或 SIF 缓存缺失
- **NEEDS_CONTEXT** — 需要用户补充 ASIN、业务报告、投放开始日期或核心关键词

告知用户：

1. 分析对象：品牌、ASIN、站点、日期窗口
2. 三条线：观察线、危险线、广告 CVR 确认线
3. 文件路径：主报告、日级面板、候选阈值和稳定词篮子
