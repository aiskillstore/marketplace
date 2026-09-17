---
name: module-readme
description: 维护模块 README 与版本记录。用户说「文档」「更新 README」时使用。
---

# 文档

首行：**`[docs]`**。日常入口：[agent-entry-route.md](../references/agent-entry-route.md)；争议/recovery：[CORE.md](../CORE.md)

## PM 门禁（硬停）

用户直接叫本岗、且**本轮尚无** `[PM]` YAML + **你下一步** 时：**不得**改 README；须同条先 `[PM]` 判车道并输出白话 **你下一步**，再切本岗。只读咨询（不改文件）→ 不阻塞。

## 车道

| 车道 | 本岗 |
| --- | --- |
| Express | 通常 skip；可选程序员一行版本 |
| Direct | 通常 `dev-one-liner`（程序员一行）；≥2 文件或结构改动 → `readme: docs` 本岗 |
| Standard/Full | PM 标 `readme: docs` 时**须**本岗；`dev-one-liner` 由程序员一行完成 |

## 模型路由 + 子窗

`readme: docs` 时本岗**必须子窗**（便宜快速模型）；禁止主窗切 `[docs]` 后直接改 README 结构。`dev-one-liner` 随实现子窗。细则 → [model-routing.md](../references/model-routing.md)。

## 何时须本岗（与 [readme-dispatch.md](../references/readme-dispatch.md) 一致）

满足**任一**即 `docs`：

- ≥2 个业务文件改动
- 新/改 public API
- 新增回归场景（须同步 project-context 索引）
- README 结构或「调试与回归」节须更新

仅 **1 文件、无新 API、无新回归** → `dev-one-liner`，程序员自更。

## Checklist

1. **须有 CR 结论**（Express=自检清单）且无 blocker；否则只写「待代码审核」
2. Read 真实代码 + **现有** README + `.cursor/project-context.md`（写前先检索，见 [execution-discipline.md](../references/execution-discipline.md) §复用四问）
2.1 **能少写/不写**：一行版本记录能说清则**不**扩结构/原理章；禁止复述已有运作原理
3. 版本记录含：目的、影响、CR 状态、验证状态、未验证风险（如 Standard 无图谱须写明影响面未图谱验证）
4. 新增回归场景 → 同步 `.cursor/project-context.md` 索引 + `.ai-gates/regression-index.yaml`
5. 不把 static-checked 写成 runtime-validated
6. 默认不改业务代码

## README 必含

概述、约束、文件结构、运作原理、调试/回归说明、版本迭代记录。

版本条目格式：`| 日期 | 版本 | feat/fix/refactor: 范围 — 原因与影响 |`

## 禁止

- CR 有 blocker 写最终完成 / 凭文件名猜测模块行为

细节 → [references/state-machine.md](../references/state-machine.md)
