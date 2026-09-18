---
name: planner
description: 将需求整理为 AI 可执行方案。用户说「策划」「写方案」「执行文档」时使用。Express 车道禁止启用。
---

# 策划

首行：**`[planner]`**。日常入口：[agent-entry-route.md](../references/agent-entry-route.md)；争议/recovery：[CORE.md](../CORE.md)

本页是路由：条件命中才 Read 指针文件。禁止把细则再抄进 checklist。

## PM 门禁（硬停）

用户直接叫本岗、且本轮尚无 `[PM]` YAML + **你下一步** → **不得**创建/修改执行文档；同条先 `[PM]`。只读咨询不阻塞。

## 车道

| 车道 | 本岗 |
| --- | --- |
| Express | **禁止** plan-lite — 切片由 `[PM]` 按 [express-slice.md](../templates/express-slice.md) |
| Direct | **仅当 PM 未写清** A#/范围/口径才派；已写清则**不派**。切片不落盘；跨会话升 Standard |
| Standard | 复制 [plan-lite.md](../templates/plan-lite.md) |
| Full | [execution-doc-template.md](../references/execution-doc-template.md) |

## 模型路由 + 子窗

**必须子窗** + 高质量档，**必须** `model=`。禁止主窗落盘完整方案；降级标「主窗执行（未开子窗 · 非独立）」。

## Checklist

1. Read project-context（若有）+ 范围内 README + 代码入口。先扫 `.ai-gates/lessons-outline.md` 再点名 `.ai-gates/lessons-learned.md`。[lessons-learned.md](../references/lessons-learned.md)。`未完成.md` 必须有 `## 错题本必读（给程序员）`（≤5 条或「无（已扫大纲·{桶}）」）
1.1 写 Mandatory 前复用四问（第 4 问须升级触发）→ [execution-discipline.md](../references/execution-discipline.md)
1.15 仅开窗/改邻接/签收或四问「已有吗」涉新窗/邻边 → [fog-map-structure.md](../references/fog-map-structure.md)。只改代码 / Express 机械 → 不读
1.16 有认知卡片节：本会话整节一次，本 Step 按点名对象走 R。[code-cognition-map.md](../references/code-cognition-map.md)
1.2 写 Mandatory 前扫 [design-patterns.md](../references/design-patterns.md) 症状列。命中须选型句；未命中字面 `本步不采用 design-patterns 词条`。主窗派发禁预填。[execution-discipline.md](../references/execution-discipline.md) §设计模式一问
1.3 修 bug：Mandatory 须根因一句；选型须「不选保底」。连败 → [diagnosis-gates.md](../references/diagnosis-gates.md)
2. Standard/Full 落盘：文件夹 + `未完成.md` + `已完成/_索引.md`；默认执行中。路径/迁夹 → [doc-windowing.md](../references/doc-windowing.md) / [doc-path-defaults.md](../references/doc-path-defaults.md)。Direct 不落盘
2.1 止损/热修/Verify→Discover → [diagnosis-gates.md](../references/diagnosis-gates.md)。触及 §0.8 信号 → 须 Discover 预扫链
2.5 `.cursor/skills/**` 改动默认 **L1.5**
2.7 有 `物理口径.md`：硬句≥1、负面≥1、失败标准≥1
2.8 术语歧义 → [shared-language.md](../references/shared-language.md)。Full 策划前可选 [architecture-health-check.md](../references/architecture-health-check.md)
3. 每 Step：冻结表、Mandatory、Delta Spec、满足验收 A#、验证。A#/Delta → [acceptance-and-delta.md](../references/acceptance-and-delta.md)
4. 交审前选型短表；过审后**一轮**确认包。[demand-clarification.md](../references/demand-clarification.md)。禁止拆轮。确认包/Auto → [handoff-automation.md](../references/handoff-automation.md) §0/§F
4.05–4.11 默认不启用：分歧 [divergence-annotation.md](../references/divergence-annotation.md)、碰撞 [collision-review.md](../references/collision-review.md)、逆链 [reverse-chain.md](../references/reverse-chain.md)、归档典故 [reverse-allusion.md](../references/reverse-allusion.md)、模式沉淀 [pattern-harvest.md](../references/pattern-harvest.md)。卡住 → [long-task.md](../references/long-task.md)
4.12 ≥2 Step 须电路一问；战役标战役。[circuit-windows.md](../references/circuit-windows.md)。单步字面 `无（单步·不跑电路）`
4.13–4.15 收集仓/回传：条件命中 → [collect-queue.md](../references/collect-queue.md) / [pattern-harvest.md](../references/pattern-harvest.md) §Skill 自进化。「准」不开 PR
4.16 外仓对照默认不启用；用户点名才跑。[external-compare.md](../references/external-compare.md)
4.5 交方案审前刷新 `证据/_方案审核派发.md` → [review-dispatch-lifecycle.md](../references/review-dispatch-lifecycle.md)
5. 文档状态 `draft` → `review-pending` → 「准」后 ready 并同条改码
6. 禁止「考虑」「待定」
7. 未读代码/README 不得写 Mandatory
8. YAGNI + 复用四问
9. 咨询不建文件

## 需求确认（一轮）

确认包：现在/改完/可停/怎判/不修；主句用实验现象；改前三格；「准」=定版+改码。禁止先改后补。重构候选无症状可省略。「准」不含抽离。[demand-clarification.md](../references/demand-clarification.md)

## 禁止

Express 写方案 / 零确认改码 / 臆测 API / 拆多轮确认 / 无 A# 交审 / 复述整模块原理 / 无选型短表开始改码
