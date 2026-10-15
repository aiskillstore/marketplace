---
name: omniailab-promo-brand-ad-adsqa-target-answers
description: 「AdsQA 目标答案与证据卡」—— 品牌广告与 TVC（官方） 方向细则：当用户只给出模糊的情绪、受众或“高级感”要求，或成片需要更强的说服力时读取。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# AdsQA 目标答案与证据卡

当用户只给出模糊的情绪、受众或“高级感”要求，或成片需要更强的说服力时读取。本卡把广告目标转成可观察的画面与声音证据；它不是评分表，不替代产品事实、来源核验或 brand-ad 的路线边界。

## 目标答案表

为每个项目写一条因果答案，说明观众看完广告后应该理解什么：

| answer_id | 维度 | 必填内容 |
| --- | --- | --- |
| answer_visual | 视觉概念 | 主体关系、视觉符号、产品证据，以及必须被看见的变化 |
| answer_emotion | 情绪 | 情绪起点、转折、终点，以及每次转折由什么画面 / 声音触发 |
| answer_theme | 主题 / 核心信息 | 片尾留下的一句话，以及它怎样由产品事实支撑 |
| answer_persuasion | 说服策略 | 演示、对比、转化、权威、社会情境或其它可信理由 |
| answer_audience | 受众 | 对谁说、他们的生活张力或愿望，以及应该产生什么识别 |

每条答案追加：

```text
required_evidence: 必须在画面或声音中出现的证据
failure_if_missing: 证据缺失时观众会误解什么
priority: must-have | important | optional
```

没有可观察证据的答案不得进入最终 H3 Prompt；不要用抽象形容词或隐藏 brief 代替证据。

## 视觉推理卡

每个关键帧或 sequence 至少写一张精简卡：

```text
Visual Reasoning Card
- answer_ids_supported: 该画面证明哪些目标答案
- unresolved_state: 当前仍未解决的关系或问题
- viewer_position: 观众站在哪里，能看到 / 不知道什么
- gaze_flow: 视线进入 -> 受阻 / 减速 -> 焦点落点 -> 离开
- composition_pressure: 一个主导空间机制
- space_roles: 前景 / 中景 / 后景各自承担什么
- primary_action: 一个主要动作
- secondary_clue: 一个具体的前因或后果线索
- light_sources: 物理光源、方向、时间和明暗区域
- lock_constraints: 产品身份、材质和连续性红线
```

拒绝“漂亮但没有证据”的 moodboard；每张图 / 每个镜头都必须能回答至少一个目标答案，并且有明确的产品动作或声音结果。

## 答案到成片映射

在生成前确认中展示：`answer_id -> required_evidence -> sequence / shot -> product proof -> sound / copy`。多 sequence 任务让每个 sequence 承担一个主答案，所有片段共享同一产品锚点、视觉方向和 Voice Continuity Lock。旁白应表达完整叙事，只有确认的记忆点进入原生艺术字，不把每句旁白变成字幕。

## 自检

生成后逐项问：

1. 观众不看隐藏 brief，能否仅凭画面、声音和确认文案回答五个问题？
2. 产品是否参与因果关系，而不是只在结尾出现？
3. 情绪变化、说服证据、旁白重音、动作和艺术字是否在同一节拍闭合？
4. 是否出现未核验主张、随机身份、伪 Logo、无证据的风格词或跨段声音断裂？

任一答案无法被证据支持时，先回写答案表 / 视觉推理卡，再重编译受影响的 sequence；不得靠后期叠字或补旁白掩盖缺口。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
