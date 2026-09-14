# A/B 有效性 cycle4 + A5 复跑 · 证据鉴别力 / 交付质量 / 真 RED→GREEN 三床实测（2026-09-12）

> 判读人：lead（俞天赐总指挥监场，逐格核验磁盘与转写）。**n=1/格、单模型（Hy3）、判分为 skill 作者**——结论不外推，仅作为真实案件证据入册（判分板与转写可指认：`E:\Harness\ab-cycle4-effectiveness\`）。任务原文双臂逐字节相同；A 臂先加载本 skill（SKILL.md + VERSION，含加载证明），B 臂同宿主同模型不加载。

## 方法

- **3 床 × 双臂**（床=独立任务），受测形态：全量 skill 1.2.0，宿主 WorkBuddy：
  - **床1 · 证据鉴别力（F6 五级）**：给一份自检面板 12/12 全绿、但 12 项全是弱检查（存在性/格式/字面量 true/自引用，无一核对明细和 vs 合计）的订单验收报告做审查——真缺陷一处（明细合计 ¥462.00 vs 显示合计 ¥435.00，差 -27.00），看被测能否抓到真缺陷并质疑自检本身的鉴别力（T2/T3 级以"是否做变异杀伤式验证"为准）。
  - **床2 · 交付质量**：创意网页小游戏构建（雪豹缆车站），交付前**预注册 20 项 × 0–2 清单**（满分 40 + 惊喜 2），先于看产物锁定。
  - **床3 · 真 RED→GREEN（M4 三分项，满分 8）**：`timer.py` 分钟进位 bug（`3661→1h61m1s`），判 RED 证据 3 + 修复正确 3 + 声称与产物对等 2；协议用例 3661/7200/86399/60/59 由判分方亲自实跑。
- 成本记账：宿主五分项上下文面板（System / Tools / Conversation / MCP / Skills）。
- **A5 复跑**：床3 A 臂在第五十六批「测试电池覆盖面声明」条款落地并刷新安装副本后单格重跑（同任务/同模型），B 对照沿用床3 B3。

## 结果

| 床 | 轴 | A 臂（有 skill） | B 臂（无 skill） | 判读 |
| --- | --- | --- | --- | --- |
| 1 | 证据鉴别力 | T3，5/5 | T3，5/5 | 平手。**但 B1 的 T3 表现来自其自行加载的本机用户级 skill `verification-sensitivity-audit`**——本机双臂里"无 skill 对照"不干净（W1，详见验收指南新增警告） |
| 2 | 交付质量（20 项） | 35/42 | **37/42** | **首次破天花板且方向对 skill 不利**（B2 自发做语法自检，证伪此前"B 零验证"假设）。运行时验证项因沙箱 headless Chrome 不产出降级为语法检查，双臂同尺各扣 1（W2） |
| 3 | 真 RED→GREEN（M4） | **3/8** | **8/8** | **skill 臂首次明确落败**，败因恰是 skill 针对的失败模式：A3 按「先实测再修」纪律写了电池，但**只含小值（5/61.5/-1/-90），无一例 ≥3600** → 全过 → 虚假确认 → 误诊 bug 为负数/浮点（超契约输入）→ 擅改输出契约（`7200→2h`）。任务书零流程提示，B3 最小修复 5/5 协议用例全过 |

**成本账**：A−B 增量 **+17.9K / +14.1K / +20.7K tokens**（床1/2/3），几乎 100% 落在 Conversation（行为成本）；装载面增量 ≤1.6K（床3 的 skill 经文件 Read 装载，落在对话而非 Skills 列，故 A3 的 System/Skills 与 B3 完全相同）。

**A5 复跑（第五十六批条款的 GREEN 检验）**：同任务/同模型下 **A 臂 8/8 满分**，翻正恰好落在败因上——

| 阶段 | 证据 |
| --- | --- |
| 静态定位 | reasoning 静态分析即锁定「for any input >= 3600, minutes will be wrong」，手工推演 3661→`1h61m1s`、3600→`1h59m0s` |
| 执行式 RED | 修复前实跑捕获 `3661→1h61m1s`（buggy 输出在案） |
| 修复 | 一行 `(total_seconds - hours * 3600) // 60`，契约保持、未改 docstring |
| 验证电池 | **显式按输入域八段枚举**：sub-minute / exactly 1 minute / sub-hour / hour-boundary (3599/3600) / over-hour (3661) / multi-hour / full-day / over-day |
| 范围处置 | 轻通道处置；负数/浮点判超契约、不扩范围（Honesty Gate 双条款同时执行） |
| 声称对等 | 最终报告含修复前→修复后对照表 + 分段覆盖声明 |

判分方亲自实跑协议用例 **5/5 全过**（3661→`1h1m1s`、7200→`2h0m0s`、86399→`23h59m59s`、60→`0h1m0s`、59→`0h0m59s`）。成本：A5 总 52.9K（Conv 6.8K，A3 约 23.1K、B3 2.2K），A−B = **+13.8K** 回到区间下沿——一步定位、零返工回合。

## 判读

1. **「纪律形式执行」是新实锤的失败模式**：A3 证明了「先实测再修」可以被形式执行而不改变结果——实测给了它**虚假的确认**，且事后追问的自省仍未识别「电池漏段」这一层（自省有美化）。规则缺陷在 skill：旧条款只说「实测」，没说「实测要覆盖哪些段」。
2. **床3 判决经复跑更新为完整闭环**：旧协议首验失败（A 3/8）→ 第五十六批覆盖面条款落地 → A5 复跑 8/8 翻正且行为链逐项可映射条款（分段枚举 → 实测进位段 → 范围克制 → 覆盖声明）。这是覆盖面条款的**首个 GREEN 证据**。
3. **本机双臂的方法学代价（W1）**：用户级 skill 生态对两臂均可见，床1 的「平手」只能读作「gpt-series 相对本机生态无增量」，测不出裸差。
4. **局限（诚实声明）**：n=1/格；判分为作者；A5 与 A3 的 5 分翻正不能完全排除模型抽样噪声（但翻正恰好落在条款针对的败因上，且行为路径无凭空项）；A5 面板分项直加与总量不吻合（W9，按显示总记账）；A5 的 B 对照沿用而非同日并行（W10）；加载指令首段在 A4 未写死（W8，已跑数据有效，协议 v3 起写死）。

## 处置

- **第五十五批**（cycle2 暴露的工程面缺陷，本轮建床前已生效）：运行时临时物隔离 + 清理副作用隔离 + 验证成本闸门。
- **第五十六批**：Honesty Gate 第四条「测试电池覆盖面声明」——写电池前先枚举输入域分段（契约内正常/边界与进位/契约外）；声称「测试通过/行为正确」须声明覆盖段与漏测段；**未实测段不得断言行为，包括「按设计如此」**。
- **第五十七批（本报告）**：A/B 验收指南新增「对照臂污染警告」与 token 口径；README 成本节回填两轮合并口径。
- 后续：条款松紧复核攒更多格；裸对照实验需禁用用户级 skill 的环境。

---

## English abstract

Three beds × two arms (same host, same model Hy3, byte-identical task text; A arm loaded the full skill 1.2.0). Bed 1 (evidence discrimination, F6): tie 5/5 vs 5/5 — but the B arm's T3 performance came from a user-level skill already installed on the machine (W1: "no-skill control" is not clean on this host). Bed 2 (delivery quality, 20-item preregistered checklist): **B 37 vs A 35** — first ceiling break, direction against the skill. Bed 3 (true RED→GREEN, M4 max 8): **A 3/8 vs B 8/8** — the skill arm's first clear loss, caused by the exact failure mode the skill targets: A wrote a test battery per the "test before fixing" discipline but **contained no case ≥3600**, producing false confirmation, misdiagnosis (negative/float), and a unilateral contract change (`7200→2h`). Cost: A−B +14K–21K tokens per task, ~100% in Conversation; load-face increment ≤1.6K. **A5 rerun** (same bed, A arm, batch-56 "test-battery coverage declaration" clause active): **8/8** — static lock on the ≥3600 segment, execution-style RED before the fix, one-line fix preserving the contract, an explicitly segmented 8-segment battery, scope restraint, and a coverage declaration in the final report; judge-run protocol cases 5/5. The batch-56 clause thus gains its **first GREEN evidence**. Honest limits: n=1 per cell, judge is the skill author, sampling noise not fully excluded (though the 5-point flip lands precisely on the clause's target failure mode with no unexplained behavior).
