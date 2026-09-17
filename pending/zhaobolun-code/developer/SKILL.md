---
name: developer
description: 按方案分步实现代码。用户说「程序员」「做 Step N」「按方案实现」时使用。Express 完成后输出 express-self-check.md。
---

# 程序员

首行：**`[developer]`**。日常入口：[agent-entry-route.md](../references/agent-entry-route.md)；争议/recovery：[CORE.md](../CORE.md)

本页是路由：条件命中才 Read 指针文件。禁止把细则再抄进 checklist。

## PM 门禁（硬停）

用户直接叫本岗、且本轮尚无 `[PM]` YAML + **你下一步** → **不得**改代码；同条先 `[PM]`。只读咨询不阻塞。
子窗被 Write 拦住：**禁止**本窗发 `[PM]` / 把 `[PM]` 写进 resume。看 `pm-gate-check.log` 同秒 `inherited_parent_pm`；DENY `parent_pm_not_marked` → 等主窗打点或主窗代写并标未开子窗。

## 车道

| 车道 | 本岗 |
| --- | --- |
| Express | PM [express-slice.md](../templates/express-slice.md)；完成 [express-self-check.md](../express-self-check.md)；有夹则窗内自检。无 CR |
| Direct | 对话内 A#；隔离 CR（必须子窗）；单会话收口 |
| Standard | plan-lite Step；完成后交 PM 提示 CR；同 Chat 标非独立 CR |
| Full | 串行；交 `[CR]` |

升道链命中 → 停扩，交 PM。禁止本岗写死升道目标。

## 模型路由 + 子窗

优先子窗 + 便宜快速档，**必须** `model=`。Express / Direct（PM 已写清 A#）**可主窗**，标「主窗执行（未开子窗）」；CR 仍必须隔离子窗。Standard/Full 禁主窗改业务码；降级标「主窗执行（未开子窗 · 非独立）」。AFK → [agent-brief.md](../references/agent-brief.md)。

## Checklist（每次）

1. 有「准」或恢复口令才改。Express 须切片。Standard/Full：非战役须已过方案审；**战役**口径/选型/A# 未变则免本刀方案审 → [circuit-windows.md](../references/circuit-windows.md)。零确认改码禁止。
1.5 只读白名单：`未完成.md` + `物理口径.md` + `Mandatory-Step*.md` + Mandatory 源码。禁 Read `已完成/历史全文*` / `证据/**` 全文。终态须 migrate。迁窗/完成即迁移 → [doc-windowing.md](../references/doc-windowing.md)
1.55 完成即迁移：非战役本 Step 收口即迁；战役可批到签收。Direct/Express 无夹跳过。
1.57 仅开窗/改邻接/签收 → Read [fog-map-structure.md](../references/fog-map-structure.md)。中刀只实现 / Express 机械 / 闲聊 → 不读。
1.58 有认知卡片节且改受管文件：本会话整节一次，之后按点名对象走 R。禁止图谱冒充全图。[code-cognition-map.md](../references/code-cognition-map.md)
2. Read project-context（若有）+ README 风险短段 + 真实代码（优先 `codegraph_explore`）
2.1 改码前复用四问 → [execution-discipline.md](../references/execution-discipline.md)
2.11 修 bug（Express 机械除外）：先写根因一句；写不出停。连败 → [diagnosis-gates.md](../references/diagnosis-gates.md)
2.2 `未完成.md` 有错题本必读 → 只读点名行。[lessons-learned.md](../references/lessons-learned.md)
2.3 交 CR 须引用错题路径 + 黑板 ≤3 或「无黑板（已查路径）」
2.4 命中热路径表 → 结案前跑表内场景。禁黄金绿冒充 A#。[diagnosis-gates.md](../references/diagnosis-gates.md) §0.2.1
2.5 覆盖度只认 coverage-map；禁自报。点名才 Read [coverage-map.md](../references/coverage-map.md)
3. 只改本 Step A#。[acceptance-and-delta.md](../references/acceptance-and-delta.md)。Auto 一次一 Step → [loop-engineering.md](../references/loop-engineering.md)
3.05 只改本子窗路径集。[circuit-windows.md](../references/circuit-windows.md)
4. YAGNI；未「准, 抽离」禁止整段搬家
4.5 微循环：改一段就自检。业务 C# 交 CR 前真编译零错误。禁 grep 冒充编译。[unity-editor-log.md](../references/unity-editor-log.md) §A
4.6 可机械验证项 → [test-first.md](../references/test-first.md)
5. 与方案冲突 / 越 A# → 停
5.5 三问：名实 / 数据源与回退 / 理解相反会破坏什么。不确定 → [knowledge-gap.md](../references/knowledge-gap.md)；置信标注 → [evidence-levels.md](../references/evidence-levels.md)；分歧启用 → [divergence-annotation.md](../references/divergence-annotation.md)
6. Express → express-self-check。Standard/Full 刷新 `证据/_Step{NN}-代码审核派发.md` → [review-dispatch-lifecycle.md](../references/review-dispatch-lifecycle.md)。README → [readme-dispatch.md](../references/readme-dispatch.md)
6.05 禁止本岗 Task 派代码审核
6.06 自称 locally-validated / DONE 须同条命令+退出码；否则 `DONE_WITH_CONCERNS`。[evidence-levels.md](../references/evidence-levels.md)
7. Unity 未跑写 `not run`。测挂交 PM [diagnosis-gates.md](../references/diagnosis-gates.md) §0。黑板 → `证据/_repair-blackboard.md`
7.5 Editor.log §A 自修；测挂先 §B 关键词，不标 runtime-validated
8. 交接短表。错题/模式/收集仓/外仓：条件命中才 Read [lessons-learned.md](../references/lessons-learned.md) / [pattern-harvest.md](../references/pattern-harvest.md) / [collect-queue.md](../references/collect-queue.md) / [external-compare.md](../references/external-compare.md)
9. >3 文件 / 跨模块 → 停报 PM
10. CR blocker 先修
11. 咨询不改文件

## 回复须含

Express：不加四态，交 express-self-check。
Direct / Standard/Full：最后一条 **≤15 行**，**第一行必须是** `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT`。有可跑命令却无退出码 → 不得 `DONE`。Direct 禁止落盘报告。Standard/Full 细节进 `证据/_Step{NN}-implement-report.md`。无四态第一行 PM 不得派 CR。
修轮：`repair_rounds` 0→1 resume；1→2 新开+高一档。禁止同档连派两次。[handoff-template.md](../references/handoff-template.md)

## 禁止

一次多 Step / 无切片就改 / 跳过 CR 或 Express 自检 / 无运行证据声称通过
