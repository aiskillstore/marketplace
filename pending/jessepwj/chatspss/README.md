# ChatSPSS

ChatSPSS is an Agent Skill for statistical analysis of user-provided CSV, Excel, SPSS and Stata data. It runs 22 common analysis tasks and requires the agent to show every Markdown result table before explaining the findings and limitations.

ChatSPSS 是可独立运行的数据分析 Skill，支持 22 类常用任务，包括描述统计、频数、多选题、相关、t 检验、方差分析、回归、信度、探索性因子分析（EFA）、PCA、聚类、ROC 和决策树等。结果表完整原样展示，再作解释。

## Install

```bash
npx skills add jessepwj/ChatSPSS --skill chatspss
```

Or download this repository and add its skill folder to an Agent Skills-compatible host. Use an isolated Python 3.12 or 3.13 environment for the pinned scientific dependencies:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/chatspss.py --help
```

## Example

```bash
python3 scripts/chatspss.py --task overview --file data.csv --columns age,income,score
python3 scripts/chatspss.py --task efa --file survey.csv --columns Q1,Q2,Q3,Q4,Q5,Q6 --factors 2 --extraction principal
```

Read [SKILL.md](SKILL.md) for supported tasks, input checks and result-display instructions. Files are processed locally by the Python script; it does not upload user datasets. EFA provides exploratory evidence and cannot establish overall validity by itself.

## Scope

Complex requests are recognized and routed to the relevant short scope reference. These references identify what is not yet implemented in this public package. For advanced needs, see [ChatSPSS](https://chatspss.cn/); availability of each method is subject to the service's current scope.

This public package is maintained by 成都自然智群科技有限公司. See [NOTICE.md](NOTICE.md). It does not imply endorsement by any directory or host platform.
