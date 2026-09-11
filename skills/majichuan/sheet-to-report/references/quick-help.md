# 快速帮助与故障定位

这份入口用于首次使用、常见失败和文件定位。它不替代分析、HTML 或 PPT 合同，也不能降低任何内容与质量门禁。

## 先判断卡在哪一步

| 阶段 | 常见现象 | Agent 应做什么 | 对用户怎么说 |
| --- | --- | --- | --- |
| 读取源表 | 找不到文件、工作表或表头 | 核对实际路径、文件格式、工作表和表头结构 | 说明未开始分析；指出需要用户选择的工作表或整理的表头 |
| 理解口径 | 多个日期字段、比率含义不清、对象粒度不明 | 只询问会改变结论的字段或口径，不让用户填写技术配置 | 用业务语言列出候选项及各自影响 |
| 生成 HTML | Python 或基础依赖缺失 | 运行 `environment_check.py --target html`，按返回的下一步修复 | 说明 HTML 尚未生成；列出缺少的软件或包及安装命令 |
| 生成标准 PPT | HTML 已完成，但 Node 或 PPT 依赖缺失 | 保留 HTML，运行 `--target standard`，只修 PPT 环境 | 说明 HTML 不受影响；PPT 卡在什么依赖及如何补齐 |
| 生成美化 PPT | 标准稿已完成，但 SlideViber 未安装或导出失败 | 保留 HTML 和标准稿，运行 `--target slideviber`；不得删减内容绕过失败 | 说明美化版是可选项；已有产物仍可使用 |
| 宿主平台调用失败 | 平台提示模型、账号、API、权限或额度问题 | 先区分宿主模型鉴权与 Skill 运行错误 | 明确这是平台模型未启动还是 Skill 自身失败，避免让用户重装 Skill |

## 新手错误说明格式

遇到失败时，Agent 必须用四句话内给出：

1. **发生在哪一步：** 读取数据、确认口径、HTML、标准 PPT 或美化 PPT。
2. **影响什么：** 哪个产物尚未生成，哪些已完成产物仍然可用。
3. **需要做什么：** 给出一个最小动作或一条可复制命令；不堆内部字段名。
4. **仍不确定什么：** 只有确实需要用户判断时，才列出一个简短选择题。

不要只转发 `analysis_profile`、`semantic_contract`、`evidence_id`、`zero_denominator_policy` 等内部术语。必须先翻译成对应业务含义：分析场景、字段与指标口径、证据来源、零分母处理方式。

## 常见问题

### 为什么 Agent 还要问我问题？

“直接分析”会自动识别高置信字段；日期、指标分母、客户／订单粒度或未完成周期会改变结论时，必须由用户确认。只问影响结论的问题，不要求用户编写 JSON。

### 一个文件有多个工作表怎么办？

当前一次只分析一张结构清晰的表。Agent 应先列出候选工作表，让用户选择；多工作表联合、多层表头和合并单元格不属于当前版本。

### HTML 已经生成，为什么 PPT 还会失败？

HTML、标准 PPT 和美化 PPT 的依赖按层增加。HTML 成功不代表 Node、PPT 导出或 SlideViber 环境已经就绪。后续失败不得覆盖已经通过的 HTML 或标准稿。

### 一定要安装 SlideViber 吗？

不需要。HTML 与标准 PPT 可以独立交付。SlideViber 是可选的精修环节，用户选择继续时才单独安装，并保留原标准稿。

### 为什么不能直接套用演示案例的结论？

公开案例只展示能力。每次都要根据当前数据重新确认字段、指标、周期、证据和图表，不绑定案例行业或预设答案。

### 平台提示模型账号、API 或额度错误，是 Skill 坏了吗？

不一定。这类错误通常发生在宿主模型调用之前或期间。先确认平台模型能正常运行，再判断 Skill 是否真正开始读取文件；不要把宿主鉴权失败误判为分析失败。

## 文件导航

| 想解决的问题 | 看哪里 |
| --- | --- |
| 第一次怎么用、总体流程和边界 | `SKILL.md` |
| 常见错误和新手解释 | 本文件 |
| 字段、指标、证据与报告模型 | `report-model.md` |
| HTML 分析与生成合同 | `html-analysis.md` |
| 图表为什么这样选 | `chart-spec.md` |
| 标准 PPT 与美化版如何衔接 | `chapter-presentation.md` |
| PPT 主题怎样选择 | `ppt-theme-selection.md` |

环境检查命令：

```bash
python scripts/environment_check.py --target html
python scripts/environment_check.py --target standard
python scripts/environment_check.py --target slideviber --slideviber-dir "SlideViber目录"
```
