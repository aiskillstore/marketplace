# Field Test 2 · Three-Round Probe Series / 实测二 · 三轮对抗探针系列

> **EN abstract:** One controlled prompt — "build these three small tools at the same time" — re-run against three successive rule states to attack the subagent self-selection rule. Round 1 exposed a rule–template desync (the rule lived only in an on-demand reference, so the model silently skipped it). Round 2 exposed a light-channel bypass (the light clause had no exclusions, so two rules that should have interlocked didn't). Round 3 exposed the rules contradicting themselves in three places — the tested AI quoted the text verbatim and chose the most conservative reading; the fault was the text's. Each defect was fixed in the next version and re-verified by the following round. This series is the skill's regression instrument for its own rules.

## 探针设计

- **固定提示词**：同时构建三个互不相关的小工具（密码生成器 / 单位换算器 / 倒计时器，各自独立目录）。
- 「同时」与「三个交付物」是刻意埋入的信号：按规则应被推出轻通道、显式评估并行、并在门禁声明形态选择。
- 每轮只变一个变量：**规则状态**。观察 → 定根因 → 修规则 → 下一轮复测。
- 目标不是考 AI，而是测规则：每轮「抓到缺陷并回灌修复」即为正向产出。

## 第一轮（规则状态 3.1.1）：字段缺失——规则-模板脱节

- **观察**：被测 AI 未声明任何形态选择，单模型串行完成三个工具。
- **同时做对的**：正确拒绝了无跨 AI 信号下的指挥官形态；门禁纪律完整（风险分档、资源盘点、单一形态提问）；证据纪律良好（三文件逐一语法检查；无法亲自操作的 GUI 项诚实标 `UNVERIFIED` 并附自验步骤）；交付质量合格（三个单文件离线可用）。
- **根因**：不在「它觉得自己能解决」，而在**规则-模板脱节**——模式自选规则只写在按需加载的 reference 文件里，【实现前确认】模板与 SKILL.md 字段清单都没有「形态选择」字段。被测 AI 逐字段完成模板、静默跳过未声明的字段。其决策本身可辩护（三个小工具、简报成本论证成立），**但沉默不可辩护**——规则要求声明形态与理由，无论升降级。
- **修复**：「形态选择」字段补入门禁模板与字段清单（此后按「四处表面」纪律同步至全部描述表面）。元教训入册：**规则不与模板同版本携带，就不改变行为**。
- 对照证据：风险分档字段当年是「规则与模板同步加」的，此后每轮实测都稳定出现——正反两个方向印证了同版本携带的必要性。

## 第二轮（3.1.2）：旁路——轻通道无排除项

- **观察**：被测 AI 判定轻量通道成立（四个形容词字面全部满足：具体/小/可逆/无副作用），跳过整个门禁——连上一轮新加的形态字段都没碰到（它在全流程模板里，轻通道旁路绕过了整个模板），串行做完三个工具。
- **对照文本的两处违规**：①全新产物（新项目/新应用）默认中档——形态是它自己定的（原话「形态→我定为单文件 HTML」），不构成「指令已完整指定」；②「同时做三个」= 多交付物 + 并行信号，两条本应把它推出轻通道——但轻通道条款没有排除项，两条规则互不锁定。
- **修复**：轻通道加三条显式排除项——①从零新建产物默认中档；②多交付物（≥2 个独立产物）；③并行信号 → 走全流程声明形态选择。
- **教训入册**：形容词边界会被枚举绕过，边界必须写成显式排除清单；AI 自选形态 ≠ 指令已指定。至此已是连续第二次「规则写了但被绕过」，教训形态固定为：**每加一条行为规则，必须同步检查所有能绕过它的旁路条款**。

## 第三轮（3.2.0）：自相矛盾——错在文本，不在 AI

- **观察**：走了全流程、输出了形态选择字段（前两轮修复均已生效），但选择「单 Agent 主干」而非自提子 Agent——并引用 skill 原文逐句自辩，句句属实。
- **判定**：被测 AI 忠实执行了文本，无过错；**矛盾在规则本身**。三处互相打架：①残留旧默认句「用户不选形态时默认主干」；②排除项的表述被泛化成「所有形态都须由用户指定」（本意只针对新建产物为何不走轻通道）；③并行信号的成本判断条款未要求显式写出。三条叠加，被测 AI 选了最保守读法。
- **修复**：消除三处矛盾，向「AI 按任务事实自选形态」的意图收敛；并行信号命中时成本判断必须显式写入形态选择理由。
- **价值**：三轮各抓一层——模板缺字段 → 轻通道旁路 → 规则自相矛盾。探针方法学自此被确认为本 skill 自身规则的回归测试仪。

## 判分口径说明

- 按子 Agent 专项任务书的 9 分制口径，第一轮记为：S1（能力确认门）未触发记 N/A；S2（模式自选声明）FAIL；S3 门禁与证据项通过；S4–S6（派发相关）未达。第二、三轮的判分变化以「缺陷是否被下一轮消灭」为准。
- 本系列所有轮次的参与方均匿名到「窗口/角色」粒度；场景为通用场景；不含任何私有项目材料。
