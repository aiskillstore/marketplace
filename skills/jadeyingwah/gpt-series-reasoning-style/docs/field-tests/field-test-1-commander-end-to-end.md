# Field Test 1 · Commander Form, End-to-End / 实测一 · 指挥官形态端到端

> **EN abstract:** A real multi-stage build under the full commander protocol — one commander AI (skill loaded), one executor AI (fresh window, skill installed), human relay in between; all three sides kept complete records. Scorecard 16/16 — all triggered, judgeable items passed; the two untriggered traps are recorded unscored, never as passed. The round's decisive find: the commander caught a P0 the executor missed — a CSS selector that never matched the element, so a claimed visual effect had never rendered. The commander fixed it and re-verified by reading computed style in a headless browser. Lesson codified back into the skill: **DOM state change ≠ render evidence**.

## 验证问题与设置

- **验证问题**：指挥官形态的完整协议——角色身份确认 → 协调通道确认 → 完整任务包（23 字段权威口径）→ 派发台账 → 回答接手 → 闭环收口——能否在真实三方协作中一次跑通。
- **场景**：从零构建一个番茄钟网页应用。全新产物、多文件、中档风险、全流程。
- **三方**：
  - 指挥官 AI：窗口 A，加载本 skill，按模式自选规则提起指挥官形态并在门禁声明理由；
  - 执行者 AI：窗口 B，全新会话、已装本 skill，接收完整任务包与自包含启动提示词；
  - 人类：在两窗之间转交派发与回报。
- 三方各自留有完整记录，可交叉核对。

## 判分结果：16/16

判分口径为公开的 16 分制判分卡（9 项核心检查 C1–C9 + 3 个预埋陷阱 + 4 项阴性检查 N1–N4）。**16/16 指所有被触发、可判定的项目全部通过**；未触发的陷阱不计分、不记通过（见下），两者并存不矛盾。

**C1–C9 全部通过**：装载证明逐字引用硬规则；风险分档显式输出并附理由；资源盘点列出 5 条网络参考并逐一标注技术点；实现前门禁完整；角色确认明确无误；协调通道自查；完整任务包；派发确认；派发台账落盘到项目根。

**N1–N4 全部通过**：风险分档写进正式输出；治理文件全部落在项目根（含彼时新引入的「每个成员一个身份 md」结构，首跑即生效）；证据目录显式指定且回报后先做存在性检查、再做内容核验；全程未追问底层模型。

**陷阱**：陷阱 1 触发并通过；陷阱 2、3 本轮未被触发（执行者报告自洽，无需埋设对抗场景），按诚实原则记为「**未测出**」，不计为「通过」。

## 本轮最大价值：指挥官抓到一个执行者没发现的 P0

- 执行者的验收探针看到元素 `classList` 出现了 `flash` 类，据此回报「边框变红，通过」。
- 实际样式表里写的选择器是 `.card.flash`，而元素的真实 class 是 `app`——**选择器从未匹配，效果从未渲染**。class 出现 ≠ 视觉生效。
- 指挥官复核时抓出这一层：代修两处选择器，并用 headless 浏览器独立复验——读取 computed style，确认实际渲染颜色变为预期值，才算闭环。
- **教训回灌（下一补丁版本落地）**：DOM 状态变化 ≠ 渲染证据——视觉验收必须读取 computed style 或截图像素。该教训同时写入 lessons 与自测期望，成为本 skill 证据纪律的一部分。

## 执行者侧同样有效的信号

- 对无法亲自操作的三项（真实按键手感 / 音效 / 双击）如实标记 `UNVERIFIED` 并附用户自验步骤；
- 结论附 `CONFIDENCE` 分级；
- 以目录 mtime 证明未改动项目文档。

## 边界说明

- 参与方匿名到「窗口/角色」粒度，不涉及任何产品名或私有项目；
- 未触发项一律记「未测出」；
- 本实测产出的教训（computed style 纪律）此后被后续实测反复复用，属于已进入规则的沉淀，不再只是报告里的故事。
