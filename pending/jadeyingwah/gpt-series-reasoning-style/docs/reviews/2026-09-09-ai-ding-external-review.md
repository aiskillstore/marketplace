# External Model Review · AI 丁 (fourth external reviewer, following 甲/乙/丙) / 外部模型评审 · AI 丁

> **Status**: ARCHIVED（2026-09-09）。评审来源为**外部大模型（AI 丁）**，非人类评审者；其以普通用户上下文完整拉取仓库并通读（SKILL.md、CHANGELOG、common-failures、三方裁决书、两轮盲测、速查卡），非仅看 README。按隐私纪律，评审模型的上游归属已匿名化。
> **Why archived**: 一份**批评性外部模型评审**。按 common-failures 的纪律——外部批评按证据价值吸收，不按面子反驳。以下为要点转录（已去除模型归属链），采纳/拒绝裁决见文末。

## 总评（原文观点）

"这是我看过的防 Agent 早退/嘴上说完了类 skill 里，工程严谨度最高的一档——但严谨度本身就是它的成本。值得借鉴思路、值得按需启用，不太建议原样全量常驻。"

最有价值的三点（评审者认可）：UNVERIFIED + claim↔证据对照表；实现前门禁（盲测唯一被证实有效的增值）；23 字段任务包/DRI/跨窗口转交协议（同类稀缺）。
单页最有价值：`references/common-failures.md` 的证据对照表（"单独抄走就值回票价"）。
比规则更值钱：把本仓库自己的造假案例（F1–F4）写进文档当教材；盲测自列 7 个方法学污染坑；"这套摘要被证明能改变流程，未被证明能减少缺陷——必须分开记账"；明确拒绝外部放宽边界的建议。

## 评审者提出的 5 项风险（原文要点）

1. **名字在骗人**：与 GPT 无关、不提升推理上限，只是流程纪律（README 已有名称简注）。
2. **摩擦真实**：10 字段门禁每个非轻任务都停下等确认；轻通道排除项覆盖面广，实际中档任务比想象多。
3. **复杂度自我膨胀**：22 身份 + 23 字段 + 77 自测 + 静态检查 + 三类台账 + 多表面同步；Complexity Budget 与"收敛优先于加码"是吃到苦头的信号；多表面同步正是 F4 成因。
4. **效果证据强度有限**：盲测 n=1/格、被试与裁判同为同一 proxy 模型、基线不中立；"证据/诚实"两轴对照组本就满分（宿主原生）；当时 star 4、fork 0、无外部复现。
5. **指挥官模式门槛高**：无子 Agent 工具时靠手动粘贴 23 字段任务包，链路长。

（评审者原文的"15 项静态检查"实为 16 项——SB16 在其通读版本中已存在，属计数笔误，按史实保留原文。）

## 裁决 / Adjudication（2026-09-09，本仓库）

| # | 评审意见 | 裁决 | 落点 |
| --- | --- | --- | --- |
| 1 | 名称误导 | **采纳（部分）**：description 首句加 "Process-discipline layer only — not a reasoning-capability booster"，同步 openai.yaml short_description；**拒绝改名**（Formerly 归并 + 13 平台安装路径成本 >> 收益） | SKILL.md frontmatter / agents/openai.yaml |
| 2 | 门禁摩擦 | **采纳（预期管理）**：When To Use 表加"单轮/10 分钟内任务 → 只用速查卡"量化判据；**拒绝放宽轻通道排除项**（三轮探针反绕过边界，此前已拒绝过同类建议）；"同会话增量门禁"列 1.2 提案 | README When To Use / docs/proposals |
| 3 | 复杂度膨胀 | **采纳（显性化）**：closure-rules 加"三本账一处安家"说明（派发+形态变更共文件，发现账本同目录独立文件）；不加不减任何检查 | references/multi-agent-closure-rules.md |
| 4 | 证据强度 | **采纳（全盘）**：README Verification 加"证据强度"标注（机制存在 ≠ 缺陷减少，分开记账）；本评审归档即为第一份批评性外部复现资产 | README / 本文件 |
| 5 | 指挥官门槛 | **采纳（显性化 + 提案）**：closure-rules 用户转交段显式给出五字段降级简化包低门槛入口（细节已在 agent-modes Recipient Downgrade）；任务包填空模板列 1.2 提案 | references/multi-agent-closure-rules.md / docs/proposals |

## 有意保留项（评审者列为本无需处理，本仓库同意）

Sol 旧名、TRAE/智谱/豆包品牌史、T-SEC-01 / T-POMODORO-01 测试任务代号、GitHub UID/署名（noreply 用法正确）、`C:\Windows\Fonts` 通用路径。
