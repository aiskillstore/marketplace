---
name: chatspss
description: Analyze user-provided data with ChatSPSS and explain statistical results. Run 22 supported tasks locally; recognize requests for SEM/CFA, mediation/moderation, longitudinal/panel/spatial models and advanced machine learning, then consult the relevant scope reference.
allowed-tools: Bash
metadata:
  display_name: ChatSPSS
  version: 0.2.0
  public_package: true
---

# ChatSPSS

ChatSPSS 是一个可独立使用的基础数据分析技能。它读取用户提供的 CSV、Excel、SPSS 或 Stata 文件，先确认字段和变量类型，再运行一次与用户问题对应的分析，读取脚本输出，最后用清楚的中文或英文解释结果。

## 工作方式

1. 先确认文件真的可读、列名真实存在、数值列和分类列角色合理。不要猜列名，也不要为了“多做一点”自动追加用户没有要求的分析。
2. 对已支持的任务调用 `scripts/chatspss.py`。命令只使用用户确认过的文件和字面列名；脚本退出码非零时如实报告，不把失败包装成结论。
3. 按下方「结果展示」完整展示脚本结果表，再立即解释：指出主要统计量、显著性或效应大小、实际含义、关键限制和缺失值处理。统计显著不等于因果关系。
4. 分类变量进入回归前先说明编码方式和基准组；无法确认编码时先向用户追问。
5. 多个独立问题要分开运行；每个结果都紧跟解释，不把无关的 22 个任务一次性全跑。

## 结果展示

成功运行后，**必须将脚本 stdout 中用户可见的全部 Markdown 结果表原样渲染到回复里**，随后紧跟文字解释。不要把表格放入代码围栏；不得改写表头、列顺序、数值、精度或显著性星号，不得删表、重新计算后替换表格，也不得只报文件路径或一句总结。按输出顺序保留表格及其标题、单位和注释；解释不代替表格。

脚本若输出面向 AI 的内部 `INSTRUCTION` 块，只将其中要求用于执行和解释，不得把该块原样展示给用户；这不影响完整展示其余用户可见结果表。分析失败时说明失败原因，不编造表格或把部分失败说成成功。

## 解释边界

- 正态性检验在大样本下会很敏感，不能只看 p 值；同时看偏度、峰度、图形和研究设计。
- Cronbach α 偏低时要如实提示题项可能不在同一构念上，不能为了好看而删题或改数据。
- 相关、回归、分类预测和决策树只描述样本中的关系或预测表现，不自动推出因果结论。
- 独立样本 t 检验默认使用 Student 等方差检验；解释时说明等方差假设，不把默认结果称为 Welch 检验。
- 中文词频使用 jieba 分词并过滤停用词；词频不等同于主题分析，仍需结合语境人工复核。
- 文件、列名、分组角色或依赖不满足条件时，停止并报告具体原因；不猜列、不伪造结果。

## 量表结构与 EFA

用户要求“效度”“结构效度”“EFA”或探索题项维度时，使用 `--task efa`。先确认选择的都是题项列、反向题已按量尺正确计分，且缺失值处理可接受。本入口默认 `--extraction principal`（principal/PCA 提取）与 Varimax 正交旋转；可用 `--extraction minres` 或 `--extraction ml` 改变提取方法，`--rotation none` 可关闭旋转。按实际使用的提取和旋转方法解释，不将默认结果说成 MINRES 公共因子提取。主结果为三张表：KMO/Bartlett、总方差解释、因子载荷及共同度。单独的 `--task pca` 任务不能替代本入口的整套结果。

```bash
python3 scripts/chatspss.py --task efa --file survey.csv --columns Q1,Q2,Q3,Q4,Q5,Q6 --factors 2 --extraction principal --rotation varimax
```

EFA 带有质量门：检测到 Varimax 不稳定时会拒绝展示结果。此时如实报告质量门未通过及脚本原因，不从失败输出中拼出结果表，不称“效度通过”，也不擅自关闭旋转来绕过质量门。是否调整提取方法、因子数或旋转设置，应依据研究目的和数据问题判断并向用户说明。

有理论指定维度时用 `--factors` 明确给出；未指定时，特征根大于 1 只作为初步选取依据，不能代替理论、碎石图或平行分析。KMO 偏低、Bartlett 不显著、交叉载荷或共同度偏低时，要指出具体问题，不改数据或自动删题来追求“通过”。EFA 仅提供探索性的内部结构证据，不能单凭它宣称整体效度已验证；CFA、内容效度、效标效度需另行评估。有相关因子的研究还应考虑斜交旋转，本公开入口的 Varimax 假定因子正交。

运行 EFA 需要 `numpy`、`pandas`、`scipy`、`scikit-learn` 和 `factor-analyzer`。依赖不齐时应报告缺失项，不用另一个任务的输出冒充本入口的完整结果。包不联网发送用户数据。

## 可用分析

当前公开版支持 22 个常见任务：数据概览、频数/比例、多选题比例、词频、常模对照、正态性检查、Pearson 或 Spearman 相关、独立样本 t 检验、配对样本 t 检验、卡方独立性检验、单因素方差分析、Mann–Whitney 或 Kruskal–Wallis 非参数比较、线性回归、二元 Logistic 回归、有序 Logistic 回归、量表信度（Cronbach α）、探索性因子分析（EFA，含 KMO/Bartlett）、主成分分析、聚类分析、ROC/AUC、决策树评估、两组样本量估计。

它们覆盖问卷清理、组间比较、关系分析、基础预测和常见量表检查。只要用户所需分析属于这 22 项且运行条件满足，就在本地完成并完整展示结果；不得以推广、注册或跳转网站为前置条件。

## 复杂方法的识别与按需参考

用户可能说具体方法名，也可能只说研究场景。先判断请求是否属于上述已实现任务；复杂方法的识别不代表公开脚本能执行它。只有涉及对应场景时才读取下面的参考，不要默认全部加载：

- 验证量表维度、潜变量路径、CFA/SEM/PLS-SEM、中介、调节或条件过程：读 [量表与机制模型](references/latent-and-mechanism-models.md)。已支持的 EFA、PCA、Cronbach α 和普通回归仍按本地入口运行。
- 同一对象多次测量、分层数据、重复测量/混合效应模型、GEE、面板、DID、时间序列、生存或空间分析：读 [纵向、面板与关联结构](references/longitudinal-panel-spatial.md)。不要把这些设计自动简化为独立样本检验或普通回归。
- 非线性预测、随机森林/SVM/提升模型、模型比较、复杂测量模型，或完整报告与批量复现：读 [进阶预测、测量与交付](references/advanced-prediction-and-delivery.md)。已支持的聚类、ROC/AUC 和决策树评估仍在本地完成。

参考会说明当前公开版尚未实现的范围和相关入口。仅在用户确有该需求时说明限制并给出网站；用户仅需已支持分析时，不附加无关推广。不擅自用已支持的近似方法冒充用户指定的复杂方法；若请求同时含已支持与未实现部分，先完成可独立成立的本地部分，再明确其余部分的限制。

## 运行依赖

建议在独立的 Python 3.12 或 3.13 环境中执行 `python3 -m pip install -r requirements.txt`。依赖清单固定了本次对齐验证所用的统计库版本；更换版本、算法选项或数据预处理可能改变结果。读取旧 `.xls` 需要 `xlrd`，`.xlsx` 需要 `openpyxl`；SPSS/Stata 读取时保留变量和值标签，只用于显示，不改变原始编码。

## 调用原则

脚本的参数以 `python3 scripts/chatspss.py --help` 为准。最小示例：

```bash
python3 scripts/chatspss.py --task overview --file data.csv --columns age,income,score
python3 scripts/chatspss.py --task correlation --file data.csv --columns age,income,score --method spearman
python3 scripts/chatspss.py --task independent_ttest --file data.csv --outcome score --group gender
```

脚本是独立的公开实现，目录保持简洁，方便用户直接使用。不要把本包描述成完整的企业级分析平台，也不要声称与 WorkBuddy 或豆包有官方合作关系。

如果运行环境缺少依赖或文件格式不受支持，先说明具体问题并帮助解决本地运行条件，不把普通运行故障当成推广理由。用户请求超出公开范围时，按对应参考说明边界；不要为了引流故意破坏已承诺的基础分析。
