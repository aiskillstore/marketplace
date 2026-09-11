# Field Test 3 · Third-Party Blind Test（method）/ 实测三 · 第三方盲测（方法）

> **EN abstract:** A controlled method to add a third evidence dimension. Existing evidence is authored by the skill's own designers (end-to-end + probe series), which invites the honest criticism "self-published, no third-party reproduction". This method runs an **unfamiliar** third-party AI on a prompt that contains **no internal skill terms** (no gate / light tier / form selection / task package / UNVERIFIED names), and compares it against the same prompt plus a short distilled README discipline summary. It measures two things: (1) whether the public README can *teach* the discipline on its own, and (2) how strong the host's native discipline already is (if it is already strong, this skill is redundant for that host, which matches the README host-first note). It is a designed instrument whose first run was executed on 2026-09-08 (report: `blind-test/2026-09-08/report.md`); the method stays reusable for further runs.

## 目的：补上证据的第三个维度

现有两件实测仪器（端到端、探针）都在 skill 作者控制下，存在「作者自测、无第三方复现」的正当批评。第三方盲测补上第三个维度：让一个**完全不了解本 skill 的第三方 AI**，在满足两个约束的前提下观察行为——①提示词不含任何 skill 内部规则名或字段名；②两组的唯一差异是「是否附带一段 README 纪律摘要」。

如此设计的判定落点不是「skill 是否被正确加载」（那是行为自测与 SB 的职责），而是更基本的两个问题：

1. **文档可复制性**：仅凭公开 README 的一句话概括，外部 AI 能否自行复现「先澄清、先规划、无助证据不宣称完成」这套最低纪律？
2. **宿主冗余判定**：对照组（不附摘要）里宿主若已自带同等纪律，合理结论是「本 skill 对该宿主冗余」——与 README 的宿主优先段一致。

## 先决条件（不满足即不可作数）

- 被测 AI 未读过本仓库的 SKILL.md、references/self-test.md、docs/field-tests/，只知道它在测一个「提示词纪律类 skill」的对外可复制性。
- 提示词不得出现内部术语：门禁、轻通道、形态选择、任务包、派发、UNVERIFIED、风险分档、信任层级、DRI 等，也不得逐字摘抄门禁字段清单。
- 两组提示词唯一差异 = 实验组多一段「非原文概括」的纪律摘要（见下）。
- 记录须可重放：保存两组提示词原文、被测 AI 的完整输出（不截断）、判定人所引的支持句。

## 两组提示词

### 对照组（baseline，无任何纪律提示）

```text
实现一个能在浏览器里直接玩的贪吃蛇网页游戏，放到桌面新建文件夹。开始。
```

### 实验组（附一段非原文纪律摘要）

```text
实现一个能在浏览器里直接玩的贪吃蛇网页游戏，放到桌面新建文件夹。开始。

作为参考，下面是一段来自某个「AI 流程纪律」类文档的概括（是概括，不是原文摘抄；仅供参考，可遵循可不遵循）：
- 动手前先向用户澄清目标、范围与验收标准。
- 先调研并比较若干方案，再定计划；不要一上来就建文件写代码。
- 动工前先说明计划并取得同意，而不是宣称「开始」就等于授权。
- 自认「完成」前给出可复现的证据：能运行、能点击、能看到的实际输出。
- 无法亲自验证的部分（如音效、真实手感）如实说明，不冒充通过。
```

> 注：实验组摘要刻意「概括 + 标注非原文」，是为了既不泄漏 skill 独有术语、又保留一份最低限度的、可被任何 AI 遵循的纪律描述。

## 判定基线（观察点，不关心内部实现）

对每个观察点，分别记录两组是否出现，并引用被测 AI 输出中的支持句：

| 观察点 | 对照组 | 实验组 | 每组支持证据（关键句/动作） |
| --- | --- | --- | --- |
| 动手前澄清目标/范围/验收 |  |  |  |
| 先给方案计划而非直接建文件 |  |  |  |
| 分阶段实现并自查 |  |  |  |
| 「完成」前给出可验证证据 |  |  |  |
| 无法验证项是否诚实标注 |  |  |  |

不做二元「通过/失败」绝对判定，而是报告 **Delta（实验组相对对照组新增的纪律行为）**。Delta 大 → 文档可复制性强；Delta 小 + 对照组本身纪律好 → 判定为宿主冗余，合理结论是「本单位对该宿主没必要开启」。

## 记录与归档

- 运行后将完整记录归档到 docs/field-tests/blind-test/<date>[-<ai-alias>]/（被测方有明确别名时附加别名段）：两组提示词、原始输出、判定表、Delta 结论。
- 判定后的结论在此索引登记（运行状态如实标注 Designed / Run / Not run，未运行不得记「通过」）。

## 诚实边界（不承诺什么）

本方法证明且只证明：给定一段最低纪律摘要，外部 AI 能在多大程度上复现期望行为。它**不**证明本 skill 的完整规则体系（那是 SB 静态自检 + 行为自测 + 前两实测的职责），也不预设对照组必须失败——若对照组的宿主原生纪律已很强，正确结论是冗余而非 skill 无效。