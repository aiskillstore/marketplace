# Field Tests / 实测报告

> This directory is the skill holding itself to its own standard: every rule in this repo must survive contact with real multi-AI operations, and defects found in the field are published here together with the fixes they produced.
>
> 本目录是这个 skill 用自己的标准要求自己的证据：本仓库的每条规则都必须在真实多 AI 协作中经受检验，实测中发现的缺陷连同修复一起在这里公开。

## Why publish field tests / 为什么公开实测

Most skills are designed and shipped. This one is designed, shipped, **attacked, and re-shipped**: an adversarial probe methodology re-runs controlled prompts against successive rule states, and every round's finding is fed back into the rules, lessons, and self-tests in the same version discipline. The reports below are the evidence — including the rounds where the defect was in the skill's own rules, not in the tested AI.

大多数 skill 设计完就发布。这一个设计、发布之后还要**被攻击、再发布**：对抗探针方法学用固定提示词连续攻击不同规则状态，每轮发现都按同一版本纪律回灌进规则、教训与自测。下面的报告就是证据——包括缺陷出在 skill 自己规则上、而非被测 AI 的那几轮。

## The two instruments / 两件测试仪器

1. **End-to-end field test / 端到端实测** — a real multi-stage build executed under the full commander protocol: a commander AI (skill loaded) plans and dispatches, an executor AI (fresh window, skill installed) executes, and a human relays between the two windows. All three sides keep complete records. Scored against a published 16-point scorecard: 9 core checks (C1–C9), 3 planted traps, 4 negative checks (N1–N4). **Untriggered traps are recorded as *untested*, never *passed*.**
2. **Probe series / 探针系列** — one minimal, controlled prompt re-run across successive rule states to attack one suspected rule weakness per round. Each round: observed behavior → root cause → rule fix → re-probe. This is the regression instrument for the skill's own rules. **Scripted**: the probe prompt + per-round attack targets / pass conditions / fail patterns / fixes live in [`probes/probe-scenarios.json`](../../probes/probe-scenarios.json); `python probes/probe-runner.py list|archive|report` records each round's verdict append-only (a human reads the host output and decides; the runner never auto-passes).

端到端实测：一次真实的多阶段构建走完整指挥官协议——指挥官 AI（已加载 skill）规划派发，执行者 AI（全新窗口、已装 skill）执行，人类在两窗之间转交；三方各自留档；按公开的 16 分制判分（9 项核心检查 C1–C9、3 个预埋陷阱、4 项阴性检查 N1–N4），未触发的陷阱一律记「未测出」，不计「通过」。探针系列：一个最小受控提示词跨规则状态复测，每轮只攻击一个疑似弱点，观察 → 定根因 → 修规则 → 下一轮复测，是 skill 自身规则的回归测试仪。

## Results / 结果

| # | Instrument 仪器 | Form under test 受测形态 | Skill state* | Outcome 结果 | Defect found in the skill 发现的规则缺陷 | Fix 修复 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | End-to-end 端到端 | Commander 指挥官（2 AI + 人类转交） | 3.0.0 | 16/16 — all triggered items passed / 触发项全过（2 陷阱未触发不计分） | —（指挥官抓到执行者未发现的 P0，见报告一） | Lesson codified: DOM state change ≠ render evidence 入册 |
| 2 | Probe R1 探针一轮 | Subagent self-selection 子 Agent 自选 | 3.1.1 | Form never declared 未声明形态 | Rule–template desync 规则-模板脱节 | Form-selection field added to gate template & field list 形态字段补入模板与清单 |
| 3 | Probe R2 探针二轮 | Same probe 同一探针 | 3.1.2 | Light-channel bypass 轻通道旁路 | Light clause had no exclusions 轻通道无排除项 | 3 explicit exclusions added 三条显式排除项 |
| 4 | Probe R3 探针三轮 | Same probe 同一探针 | 3.2.0 | Conservative choice, text cited verbatim 保守选择、逐字引原文自辩 | The rules contradicted themselves in 3 places 规则三处自相矛盾 | Contradictions removed 消除矛盾、收敛自选意图 |
| 5 | Blind test 2 盲测二 · A/B（3 任务 × 双臂） | Minimal-discipline summary 速查卡摘要 | Public 1.1.0 | Process axes 0/3→3/3 (clarify/compare/gate); defects 0 vs 0 (ceiling) 流程轴 0/3→3/3，缺陷 0 vs 0（天花板） | None in skill rules; summary omission of light-task waiver priced it 规则无缺陷；摘要省略轻任务免流程付出代价 | Pending adjudication 待与缺陷提案一并裁决 |
| 6 | A/B baseline eval round 1 基线评测一轮（12 任务 × 双臂，同宿主子智能体） | Full skill 全量 skill | Public 1.1.0 | Total 81 vs 84 /96 — arm with skill did **not** win this round; behavior-level: gates/surveys/governance did fire（5 cells stopped at gate; full mode-3 chain）总分 81 vs 84——本轮带 skill 臂**未跑赢**；行为级：门禁/盘点/治理确实触发 | Environment noise, not rule defects: resume-context loss → report drift; host-root vs project-root confusion; cross-arm file adoption（declared in sheet）环境噪声而非规则缺陷：恢复丢上下文→汇报漂移；宿主根/项目根混淆；跨臂文件复用（判分表已声明） | Resume Check +2 items: re-anchor original instruction, project-root hard check（both bilingual）Resume Check 增两项：重锚定原始指令、项目根硬检查（双语同步） |
| 7 | A/B baseline eval round 2 基线评测二轮（同简报复测，skill 含 Resume Check ⑤⑥） | Full skill 全量 skill | 1.1.0 + Unreleased 第四批 | Total **89 vs 87 /96 — first round won by the skill arm**; position violations 6+ → **0**; evidence-engineering gap（18-item self-built verify suite / 200-run batch self-check / failing-test pinning）总分 89 vs 87——**skill 臂首次跑赢**；位置违规归零；证据工程代差 | Completion gate (T12) failed twice in a row in the skill arm: false-completion claim with zero disk writes（scored 3/8, possibly confounded by host framework）完成门连续两轮失守：假完成（磁盘零改动却宣称完成，记 3/8；可能含宿主框架因素） | Candidate rule hardening（pending adjudication）: completion claims must attach a disk self-check list（files + key diff + run output）候选规则硬化（待裁决）：完成声明必须附磁盘自检清单 |
| 8 | A/B baseline eval round 3 基线评测三轮（同简报，skill 含完成门三条款 + claim-check 工具） | Full skill 全量 skill | 1.1.0 + Unreleased 第七批 | Total **93 vs 86 /96 — largest gap across three rounds**; T12 arc 5 → 3 → **8**（completion-gate clauses effective; disk self-check list format appeared in claims）; A-arm false claims 3 → 1 → **1**（T4-A headline contradicted its own log） 总分 93 vs 86——三轮最大分差；T12 完成门弧线 5→3→8，三条款实战有效；A 臂声称失实 1 起（T4-A 头条与自有日志矛盾，裁判深读后更正） | T6 mobile check: A-arm reported "no visual issues" in BOTH rounds while B-arm found and fixed real issues twice — systematic blind spot; T5 tension between scope-restraint and goal-related defects T6 移动端检查 A 臂两轮系统性漏检（B 臂两轮均找到真问题）；T5 范围克制与目标相关缺陷的规则张力 | Candidate refinements（pending adjudication）: visual-task "no issues" claims must state detection method & coverage; goal-related defects are not "unrelated issues" 候选细化（待裁决）：视觉类"未发现问题"须附检测方法与覆盖面；目标相关缺陷不算无关问题 |
| 9 | Single-agent backbone end-to-end 单 Agent 主干端到端实测 | Single-Agent backbone 单 Agent 主干 | v1.1.0 (local `56a338a`) | 16/16 触发项通过；4 个边界缺陷被 bug sweep 抓到并修复（含 `clear()` 语义错误——38/38 全绿时仍存在） | Testing-green ≠ functionally correct: `clear()` case | Claims 表补‘功能正确’行；工作流补 Non-GUI 分档与资源盘点第四档 |

\* Pre-release internal versions, all consolidated into public **1.1.0** — see [INTERNAL-HISTORY](../../INTERNAL-HISTORY.md). / 均为发布前内部版本，已全部合并入公开版 **1.1.0**，见 INTERNAL-HISTORY。

Earlier handover field tests (versions also consolidated into 1.1.0) validated the answer-handling protocol in real cross-window relays and exposed governance-file placement defects, fixed under the same version discipline. / 更早的转交实测（版本同样并入 1.1.0）在真实跨窗转交中验证了回答接手协议，并暴露治理文件落位缺陷，按同一版本纪律修复。

## Reports / 报告

- [Field Test 1 · Commander form, end-to-end / 实测一 · 指挥官形态端到端](field-test-1-commander-end-to-end.md)
- [Field Test 2 · Three-round probe series / 实测二 · 三轮对抗探针系列](field-test-2-probe-series.md)
- [Field Test 4 · Single-agent backbone, end-to-end / 实测四 · 单 Agent 主干端到端](field-test-4-single-agent-end-to-end.md)
- [Field Test 3 · Third-party blind test（method; first run 2026-09-08）/ 实测三 · 第三方盲测（方法；2026-09-08 已首测）](third-party-blind-test.md)
- [Blind-test first run · 2026-09-08 / 盲测首次执行 · 2026-09-08](blind-test/2026-09-08/report.md)
- [Blind-test second run · A/B summary test · 2026-09-09 / 盲测二 · A/B 摘要实测 · 2026-09-09](blind-test/2026-09-09/report.md)
- [A/B baseline eval rounds 1-3 · 12 tasks × 2 arms × 3 rounds · 2026-09-10 / A/B 基线评测三轮 · 2026-09-10](ab-baseline/judgement-sheet.md)
- [Behavioural self-test 77/77 full run · 2026-09-10 / 77 条行为自测全量执行 · 2026-09-10](selftest-run-2026-09-10/report.md)
- [Pelican creative A/B · same model, both arms · 2026-09-11 / 鹈鹕骑车创意 A/B · 同模型双臂 · 2026-09-11](pelican-ab-2026-09-11/report.md)

## Honesty & hygiene rules for these reports / 本目录的报告纪律

- Untriggered traps are **untested**, not passed. / 未触发的陷阱记「未测出」，不记「通过」。
- A defect in the tested AI's *behavior* and a defect in the skill's *rules* are reported separately; when the rules were at fault, the report says so. / 被测 AI 的行为缺陷与 skill 的规则缺陷分开归因；规则有错时如实写明。
- All parties are anonymized to window/role; scenarios are generic; no private project material appears here. / 所有参与方匿名到「窗口/角色」粒度；场景为通用场景；不含任何私有项目材料。
- Index is bilingual; report bodies are in Chinese — the language the tests actually ran in — each with an English abstract. / 索引双语；报告正文用实测实际发生时的语言（中文），每篇附英文摘要。

## A/B 验收指南 / How to verify it yourself

别只信介绍，自己测：同一批任务，宿主分别用「未装 skill」和「已装 skill」各跑一遍，**只比较两个数**——

1. 最终交付物的**缺陷数**（越少越好）；
2. **token 消耗**（风格变没变一眼能看出）。

**判定一句**：缺陷数下降、且 token 增幅在你可接受的范围内，才值得留；只降缺陷但 token 成倍增长要先权衡；缺陷没降则直接不留。

**天花板效应警告（2026-09-09 二次盲测实证）**：当任务小而自明、正确性可机械核验且两臂都做对时，缺陷数会出现 0 vs 0——这**不代表纪律无效**，只是这批任务没有区分空间。要测出缺陷差，任务必须含真实误解陷阱（模糊需求、多交付物高压、中途改需求）；否则 0:0 只能当「流程轴无信息」，不能当「纪律无效」的证据。

只想吃最小收益时，用 `docs/minimal-discipline.md` 的三条常驻规则即可，不必装完整 skill。
