---
name: omniailab-promo-anime-game-pv-audio-direction
description: 「二次元游戏 PV 音频方向」—— 二次元漫画 ／ 游戏 PV 方向细则：仅在 anime-game-pv 已触发后读取。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 二次元游戏 PV 音频方向

仅在 `anime-game-pv` 已触发后读取。声音必须进入同一条 Master Timeline；默认直接使用视频模型原生声音，独立 BGM 只处理用户明确提出的需求。

## 声音来源决策

1. **用户提供音频**：先用 audio metadata 和 music analysis 提取真实时长、段落、显著节拍、高潮、歌词/人声入口和情绪转折。用户未说明用途时，必须用 confirmation card 确认：参考音乐节奏、参考台词或人声、只分析节奏与情绪，或不使用该音频。只有前两项把真实音频交给选定的视频模型；第三项只把分析结果编入时间线并使用模型原生声音；第四项回到无用户音频路径。用户已明确用途时直接继承，不生成替代音乐。
2. **用户明确静音**：关闭音乐、对白、环境声和动作声。
3. **用户明确不加 BGM**：不生成音乐，只保留用户允许的原生环境声、动作声或对白。
4. **用户未提供音频**：默认使用视频模型原生声音，在 Prompt 中同时描述逐 Shot 声音事件、整体环境声和观众可听见的配乐发展。
5. **用户明确要求独立生成 BGM**：只有此时才生成独立音乐；生成后将它视为用户音频，重新检查当前能力，不把独立 BGM 作为默认步骤。

## 音频能力门

从当前能力摘要中确认所选视频模型和模式是否支持音频引用：

- 支持时，把真实音频路径放入对应 reference slot，并在 Prompt 中使用一致标签声明其用途；只有实际传入模型时，才能声称音频参与生成条件。
- 不支持时，用 confirmation card 让用户选择切换到支持音频引用的视频路径，或仅把分析结果作为时间/情绪参考并改用视频模型原生声音。不得静默降级，也不得承诺与未传入音频逐拍同步。
- 音频只是节奏参考时，Prompt 描述对应时间窗口和情绪变化，但不能写成“复制原音频”或“严格同步”。
- 用户没有提供音频而当前路径又不支持原生声音时，用 confirmation card 确认切换到支持原生声音的视频路径或接受静音；不得自动恢复为独立 BGM。

## 原生声音编译

每个 Logical Shot 写明与画面同步的对白、环境声、动作声或显式静音；全局再写环境声连续性和非剧情内配乐的发展。声音事件必须服务动作、转场和最终停留，不堆叠与画面无关的泛广告音乐。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
