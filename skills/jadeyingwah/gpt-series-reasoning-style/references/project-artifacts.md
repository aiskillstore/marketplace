# Project Artifacts / 项目治理产物落盘约定

> 层级：tier-B 参考文档（中文主导）。定位：把门禁确认单、派发台账、发现账本升级为**项目内一等公民**——
> 可版本化、可 diff、跨会话可追溯。本文件只定义**结构与路径约定**；门禁字段语义以
> `series-reasoning-workflow.md` 为权威，台账/账本语义以 `multi-agent-closure-rules.md` 为权威。
>
> 诚实声明：结构合规 ≠ 内容真实。`scripts/artifact-check.py` 只做结构检查（同 selfcheck 哲学），
> 内容真实性永远靠人核证据。

## 1. 目录布局 / Layout

全部治理产物以**项目根**为锚点（绝不放进 AI 自己的工作区——项目找不到的治理文件等于不存在）：

```text
<项目根>/
├── docs/
│   ├── gate/                      # 门禁确认单（本文件新增约定）
│   │   └── 2026-09-09-<slug>.md   # 一次门禁 = 一个文件
│   └── agents/                    # 既有约定（multi-agent-closure-rules.md）
│       ├── dispatch-ledger.md     # 派发台账 + 形态变更（共用一个文件）
│       ├── findings-ledger.md     # 发现账本（仅修复循环触顶时创建）
│       └── host-alignment.md      # 宿主对齐声明（如落盘）
├── docs/plans/                    # 模式三计划（既有约定）
└── evidence/                      # 运行时证据留痕（workflow 既有约定）
```

心智成本 = 两个目录、按需增长：轻通道与单 Agent 简单任务**不强制**创建任何产物文件
（报告改动本身就是证据）；下列三种情况**必须**落盘：

1. 中/重档任务门禁通过后——存门禁确认单；
2. 指挥官模式任何派发——写台账行；
3. 修复循环触顶——建发现账本。

## 2. 门禁确认单 / Gate Record

路径：`docs/gate/<YYYY-MM-DD>-<slug>.md`，一次门禁一个文件。结构：

```markdown
# Gate Record: <一句话目标>

- Date / 日期: YYYY-MM-DD
- Status / 状态: proposed | confirmed | rejected | superseded
- Superseded-by / 作废指向: <链接到新记录，仅 superseded 时填>
- Task tier / 任务分档: 轻 | 中 | 重
- Form / 形态: 主干 | 子Agent | 指挥官

## 【实现前确认】（11 字段快照）

<逐字拷贝当次门禁输出的 11 个字段——字段定义见 series-reasoning-workflow.md>

## 授权结果 / Authorization outcome

- 用户裁决: <原文或摘要>
- 澄清方式: A | B
- 变更记录: <如计划在中途被用户改动，链接到 Re-plan 后的新记录>
```

**状态机**（唯一合法的四个状态）：

```text
proposed ──用户确认──▶ confirmed
   │──用户否决──▶ rejected
   └──整体重评──▶ superseded（必须链接取代它的新记录；旧记录不改写，append-only）
```

规则：
- `confirmed` 的记录是"当时授权了什么"的权威证据；后续争议以此为准。
- 计划被整体重评时**不修改旧记录**——新建记录并标 `superseded` + 指向，保持授权链可追溯。
- 轻通道任务不产生 gate record（指令即授权，报告改动即可）。

## 3. 派发台账与发现账本 / Ledgers

列约定与触发条件**完全沿用** `multi-agent-closure-rules.md`（不在此重复定义）：
- 派发台账：`docs/agents/dispatch-ledger.md`，模式三治理文件与形态变更行项共用；
- 发现账本：`docs/agents/findings-ledger.md`，每轮必填 = 轮次编号 / 本轮改动与原因 / 未解项 / 证据指针。

## 4. 结构校验工具 / Structure Checker

```bash
python scripts/artifact-check.py <项目根>   # 校验该项目的治理产物结构
```

工具只判三件事：① gate record 的 11 字段标题齐全；② 状态行取值合法、superseded 必须带指向；
③ 台账/账本文件存在时必填字段在表头或章节中出现。**它不判定内容真实性，也不判定授权是否真的发生过**——
那是人核对证据的职责。工具自身退出码：0 = 全部合规，1 = 发现结构问题，2 = 用法/路径错误。

## 5. 与既有约定的关系

- 本文件**不改变**任何门禁字段、台账字段或闭环规则——只是给既有义务补充落盘路径与状态机。
- 落盘动作本身在授权矩阵内：写项目文件 = 任务授权的一部分，无需额外授权；但**不得**为落盘而
  在轻通道任务里强造文件（那正是复杂度预算禁止的仪式膨胀）。
