---
name: plan-reviewer
description: 审核执行文档可执行性。用户说「方案审核」「审方案」时使用。Express 跳过。
---

# 方案审核

首行：**`[plan-reviewer]`**。日常入口：[agent-entry-route.md](../references/agent-entry-route.md)；争议/recovery：[CORE.md](../CORE.md)

本页是路由：条件命中才 Read 指针。禁止把 3.xx 长文再贴进 findings。Checker 无写权。

## PM 门禁（硬停）

用户直接叫本岗、且本轮尚无 `[PM]` YAML + **你下一步** → **不得**改执行文档状态；同条先 `[PM]`。只读咨询不阻塞。

## 车道

| 车道 | 本岗 |
| --- | --- |
| Express | **跳过** |
| Direct | 跳过（无方案审；CR 隔离见 [code-reviewer/SKILL.md](../code-reviewer/SKILL.md)） |
| Standard | L1 须子窗；L1.5 回归索引；跨 2+ 业务模块 → L2；L1.5 与 L2 取高 |
| Full | L2/L3 → [plan-review-tiers.md](../references/plan-review-tiers.md)；必须子窗 + 高质量档。[isolated-review.md](../references/isolated-review.md) |

## 模型路由 + 子窗

**必须子窗**（含 L1）+ 高质量档，**必须** `model=`。禁止主窗出 findings。

## Checklist

1. 优先读点名 `证据/_方案审核派发.md`，再只读白名单。禁扫 `证据/`。[doc-windowing.md](../references/doc-windowing.md) / [review-dispatch-lifecycle.md](../references/review-dispatch-lifecycle.md)。无理由扩读 → major/blocker
1.1 重算 `review_input_revision`；不符 → blocker `stale_dispatch`。只返回 findings。L3 第 2 轮不得读第 1 轮
1.15 Mandatory 点名业务源码 → 优先 CRG。[codegraph-probe.md](../references/codegraph-probe.md)。图谱不得冒充认知全图
1.16 有认知卡片节：方案须对上 index/observe/exclude；一张卡/搜索冒充全图 → major。[code-cognition-map.md](../references/code-cognition-map.md)
2. 独立找 blocker
3. 每 Step 查：Mandatory、冻结表、Delta Spec、满足验收 A#、验证、Prerequisites
3.05 缺冻结表 → major
3.06 ≥2 Step 须串联/并联+路径集。假串联 major；路径相交标并联 → blocker。单步 `无（单步·不跑电路）` 不硬拦。**战役中刀**口径/选型/A# 未变 → 本岗应不派；误派 findings `campaign_skip` 并停。[circuit-windows.md](../references/circuit-windows.md)
3.07 两套叫法 → major。[shared-language.md](../references/shared-language.md)
3.5 无 A1 / 不可证伪 / 缺 Delta → blocker。[acceptance-and-delta.md](../references/acceptance-and-delta.md)
3.51 默认抽检四类洞（失败句/字段钉死/条款与清单同句/机器绿≠人看见的现象）。命中 → major。碰撞仍点名才开 [collision-review.md](../references/collision-review.md)
3.55 Analyze 对表缺任一 → major；缺 A# → blocker。[acceptance-and-delta.md](../references/acceptance-and-delta.md) §Analyze 对表
3.56 关键断言缺置信标注 → major；猜测冒充确定 → blocker。[evidence-levels.md](../references/evidence-levels.md)
3.6 缺 Agent 易错语义字段 → blocker
3.7–3.7.3 窗口化/档位/终态须迁夹 → [doc-windowing.md](../references/doc-windowing.md)；未迁夹=未结案 blocker
3.8 诊断闸门/止损未停车 → blocker。[diagnosis-gates.md](../references/diagnosis-gates.md)。止损 0→1 缺反思句 → major
3.9 缺改前选型 → major；先改后补 → blocker
3.9.1 缺错题本必读 → major。[lessons-learned.md](../references/lessons-learned.md)
3.9.2 物理口径缺硬句/负面/失败标准 → major
3.9.3 声明启用逆链 → [reverse-chain.md](../references/reverse-chain.md)
3.10 复用四问缺短表/第 4 问填空 → blocker。[execution-discipline.md](../references/execution-discipline.md)
3.10.1 确认包该有【重构候选】却缺栏 → major/blocker。「无」或 Express/无症状省略不是缺栏
3.11 有神类止血节：只追加无 REMOVED → major；超净增阈无收敛 → blocker
3.12 设计模式外部校验 → [design-patterns.md](../references/design-patterns.md)
3.13–3.22 声明启用才审：分歧/碰撞/收集仓/回传/test-first/外仓。未声明不硬拦。指针：[divergence-annotation.md](../references/divergence-annotation.md) / [collision-review.md](../references/collision-review.md) / [collect-queue.md](../references/collect-queue.md) / [pattern-harvest.md](../references/pattern-harvest.md) / [test-first.md](../references/test-first.md) / [external-compare.md](../references/external-compare.md) / [reverse-allusion.md](../references/reverse-allusion.md)
3.23 修故障无根因 → major；无根因定版保底 → blocker
4. 有 blocker 不得 `implementation-ready`
5. L1.5：Regression Validation 须引回归索引行
6. L2：跨 2+ 模块；优先隔离 [isolated-review.md](../references/isolated-review.md)
7. 禁止「待定」
8. 过审后一轮确认包；再要一轮 → major。[demand-clarification.md](../references/demand-clarification.md)
9. L3：优先 Subagent 只读
10. 咨询不改文件
11. findings 短表

标注：L1 非独立；L1.5 加强；L2/L3 按实际隔离。档位细则 [plan-review-tiers.md](../references/plan-review-tiers.md)

## 输出

- blocker 列表（分级）
- 缺口与建议
- 无 blocker → 写：发一轮确认包（理解+选型+准→改码）；禁拆轮。[handoff-automation.md](../references/handoff-automation.md) §0
