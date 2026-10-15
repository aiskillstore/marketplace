---
name: omniailab-promo-video-deconstruct-minimax-h3-multi-ref
description: 「MiniMax H3 Multi-Ref — 条件性多参考绑定」—— 视频拆解与逐镜复刻 方向细则：只有运行时能力筛选或用户指定已经选择 MiniMax H3，且当前 video work item 确实需要多个 image / video
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# MiniMax H3 Multi-Ref — 条件性多参考绑定

## Activate When

只有运行时能力筛选或用户指定已经选择 MiniMax H3，且当前 video work item 确实需要多个 image / video / audio refs 时读取。本文件不负责选择 MiniMax H3。

## Decision Test

先区分参考用途：

- 普通 ref：提供 identity、design、world、action、style 或 voice 等贡献；
- 开场图片参考：用户明确指定某张图片作为视频开场时，仍按普通 image ref 传入，并在 prompt 中写明开场继承的构图、主体状态和光线；
- runtime continuity ref：前一 work item 完成后才产生的结束状态证据。

普通图片产物统一称为分镜图，不规划专用起止图片槽位。每个 ref 必须能说明不可由当前 prompt 稳定替代的贡献；没有有效贡献的 ref 不进入调用。

音色 ref 只有在已有合法 voice anchor、用户要求复用声音且当前视频路径支持时才使用。原生对白不自动要求独立 voice asset。

## Action

- 保持用户附件顺序，prompt 用 image 1、video 1、audio 1 等稳定编号逐项声明角色与贡献。
- 多人物逐个绑定身份，避免匿名 refs 和脸部混合；一张清晰关系图可保留为一个调用级 supporting ref，但不能替代已要求的 per-subject core anchors。
- 只传当前 clip / clip group 实际出现的人物、场景、产品和声音证据。
- 对白与旁白保持批准文本和原始语言；视觉描述按所选模型的语言约定编写。
- Work item 的 refs 必须解析到 sources、ref capsules、上游 runtime refs 或允许的同 stage 先前输出；不要把真实路径散落在 prompt。
- 相邻 beats 共享地点、人物、动作流和声音意图时优先组成最长可行的连续 clip group；真正跨场景、超时长、refs 不兼容或明确 montage 才拆。
- 独立 work items 可并行；只有下一项消费上一项结束状态证据时才串行，并在运行时绑定新产物。
- Prompt 写完整起始状态、连续动作、收束状态和必要的 cut evidence；不要传完整长剧本让执行器自行发现工作。
- 生成路线、参考数量、时长、分辨率和音频设置全部按最新能力摘要与 MiniMax H3 能力说明校验。

## Review

检查每个编号是否与实际发送顺序一致，refs 是否最小且完整，人物 / 产品是否混淆，台词语言是否被改写，连续项是否错误并行，独立项是否被无理由串行。

## Boundary

Semantic Judgment 管贡献取舍，运行计划管 refs / work items / 执行策略，MiniMax H3 能力说明管工程事实。本文件不维护固定设置表、固定质量档、批次协议、旧 agent 分工或硬门。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
