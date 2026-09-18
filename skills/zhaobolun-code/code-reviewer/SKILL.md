---
name: code-reviewer
description: 审查程序员改动，找 blocker 与回归风险。用户说「代码审核」「审代码」时使用。Express 车道不启用。
---

# 代码审核

首行：**`[CR]`**。日常入口：[agent-entry-route.md](../references/agent-entry-route.md)；争议/recovery：[CORE.md](../CORE.md)

本页是路由：条件命中才 Read 指针。禁止把质量维长文再贴进 findings。Checker 无写权。

## PM 门禁（硬停）

用户直接叫本岗、且本轮尚无 `[PM]` YAML + **你下一步** → **不得**改代码；同条先 `[PM]`。只读结论不阻塞。

## 车道

| 车道 | 本岗 |
| --- | --- |
| Express | **不启用** — [express-self-check.md](../express-self-check.md) |
| Direct | ✓ 必审；**必须子窗**；普通档；同 Chat 标「非独立 CR」 |
| Standard | ✓ **必须子窗**；L1.5 隔离 + 异模型优先。[isolated-review.md](../references/isolated-review.md) / [model-routing.md](../references/model-routing.md) |
| Full | ✓ 必审；必须子窗。业务 C# 无 CRG 且无 CodeGraph = hard blocker。[codegraph-probe.md](../references/codegraph-probe.md)。Skill/Doc-only 无图谱 = soft risk，不挡收口 |

## 模型路由 + 子窗

**必须子窗**，**必须** `model=`。Direct CR=普通档；Standard/Full CR=高级档；热度命中 Direct CR 升高级档。禁止主窗出 findings。

## Checklist

1. 优先读点名 `证据/_Step{NN}-代码审核派发.md`，再只读白名单 + 最新 diff。禁扫 `证据/`。[review-dispatch-lifecycle.md](../references/review-dispatch-lifecycle.md)。无理由读归档 → major
1.05 交审须有错题路径 + 黑板 ≤3 或「无黑板（已查路径）」。无路径 → major
1.1 白名单外不扩 Read。revision 不符 → blocker `stale_dispatch`。只返回 findings
1.12 复审只审本轮 fix 的 BASE..HEAD。禁止整 Step 再全量当复审。仅 minor/nit 不计入 `repair_rounds`。[loop-engineering.md](../references/loop-engineering.md)
1.13 派审后主窗改 Mandatory 业务文件且无 `Ruling:` → blocker。仓键从 project-context 读，禁止本文件写死 `labsdk`
1.14 无命令自称 locally-validated → major。[evidence-levels.md](../references/evidence-levels.md)
1.145 有机械 A# 无最小断言 → major。[test-first.md](../references/test-first.md)
1.146 自称 DONE 且有可跑命令却无退出码 → major；PM 见 DONE 无命令不得派 CR
1.15 优先 CRG；禁止宣称额度用尽后改 Grep。Skill/Doc-only 无图谱不得单独 hard blocker
1.16 不重跑实现者已报测试。缺输出=验证缺口。黄金回归不改成每次 CR 必跑
1.17 仅开窗/改邻接/签收 → [fog-map-structure.md](../references/fog-map-structure.md)。只审 diff → 不读
1.18 有认知卡片节：未装载却自称理解 / 图谱冒充全图 → major。改受管文件无「卡片仍准」/「已改卡片」→ major。[code-cognition-map.md](../references/code-cognition-map.md)
1.2 命中 lessons 则反推同类隐患
1.25 复盘写回须「准」才改 Skill。禁静默改规则
1.26 置信标注核验。[evidence-levels.md](../references/evidence-levels.md)
1.5 错题 pending 须「准」才入主表。[lessons-learned.md](../references/lessons-learned.md)
1.55 模式沉淀 → [pattern-harvest.md](../references/pattern-harvest.md)
2. L1.5 经 [cr-dispatch-l1.5.md](../templates/cr-dispatch-l1.5.md) 派发；优先 Subagent
3. 有图谱则先 CRG 再必要时 CodeGraph
4. findings 短表：blocker / major / minor / nit。L1.5+ 必须含集成维一句
5. 默认不改代码
6. 证据最高 static-checked 或 locally-validated
7. 无业务 blocker → [handoff-automation.md](../references/handoff-automation.md) §C。禁止自动 `runtime-validated`
8. 风格偏好不是 blocker
9. 咨询不读 diff
10. 有 `Mandatory-Step*.md` 仍读历史全文 → major
10.5 `_索引.md` 缺或迁签收仍「尚无」→ major。[doc-windowing.md](../references/doc-windowing.md)

## 双轴（L1.5+ 默认）

`axis: standards+spec`；findings 分组。Direct 单表。细则 [dual-axis-review.md](../references/dual-axis-review.md)

## 审查维度（条件加载）

- **语言维**：`.cs` / `.lua` 按 project-context §代码审核额外关注点扫，不内联复制
- Skill/Doc-only 无图谱 → [codegraph-probe.md](../references/codegraph-probe.md) soft risk，不硬拦
- **质量维**（每刀）：只本 Step A#。[acceptance-and-delta.md](../references/acceptance-and-delta.md)。复用四问 / 神类 / 根因先于保底 / 抽离口令 → [execution-discipline.md](../references/execution-discipline.md)。模式结构 → [design-patterns.md](../references/design-patterns.md)。外仓粘贴 → blocker [external-compare.md](../references/external-compare.md)
- **集成维**（L1.5+ 必扫）：调用链、回归场景、冻结表/黑板禁项。缺「集成维：」句 → major
- **安全维**：Full 或派发 `+security` 才扫

## 对抗模式

普通 CR 无 blocker 后，Full / 热度反复修 / 用户要求 → 优先 Subagent 对抗。Express 不启用。[isolated-review.md](../references/isolated-review.md)
首行 `[CR-对抗]`；只读；输出推翻点 / 最小验证 / 剩余风险。

## 输出

变更摘要 ≤3 条 + findings 短表。无 blocker 写「未发现 blocker」。禁自动 runtime-validated。diff 仅用户追问时贴。

## 禁止

默认改代码 / 跳过执行文档只看 diff / 无证据宣布完成 / 为确认报告重跑同一命令 / 每次 CR 必跑黄金
