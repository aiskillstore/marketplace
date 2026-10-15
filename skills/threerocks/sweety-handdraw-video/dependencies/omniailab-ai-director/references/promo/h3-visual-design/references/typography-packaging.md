---
name: omniailab-promo-h3-visual-design-typography-packaging
description: 「字体、Logo 与口播包装」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：把用户素材转成“主体、字体、图形、空间、镜头、光影和声音共同编排”的 H3 视频提示词。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 字体、Logo 与口播包装

把用户素材转成“主体、字体、图形、空间、镜头、光影和声音共同编排”的 H3 视频提示词。目标是接近 AE 标题包装和动态海报，不是给原图做推进后放一个词，也不是自动生成品牌广告。

## 最高优先级：H3 逐字执行锁

1. 本路线由当前会话直接完成素材判断、设置确认和完整提示词工程；不创建用户可见的阶段计划，也不把创意写作交给下游写作者或能力资料。
2. 设置全部确认后生成唯一字符串 `final_h3_prompt`。它必须符合本路线的结构、字符预算和 Reference 规则；展示给用户的代码块内容就是实际送入 H3 的完整字符串。
3. 进入视频生成时只传递已经确认的模型、画幅、分辨率、时长、素材顺序和完整 `final_h3_prompt`；不得摘要、缩短、翻译、改写、重排、润色或追加文字。

4. 能力摘要只用于确认模型可用性、参考素材范围、时长、分辨率、音频和接口限制；不得重写、摘要、翻译、润色、重排或替换 `final_h3_prompt`。
5. 展示给用户的字符串与实际执行的 Prompt 必须字符级一致；若实际分辨率低于确认值，视为执行未按设置完成。只发送 brief、style summary、composition summary、主体摘要或原始需求让下游继续编写 Prompt，均视为失败。

文案先行硬锁：`text_mode=agent_curated` 时，`FACTS_FOR_COPY → SCENE_PACKAGING_COPY → COPY_TRACE → COPY_DECK → TEXT_WHITELIST` 是不可跳过的顺序。把介绍词当作 music skill 的歌词底稿，先有连续语义再拆屏幕文案；`COPY_DECK` 中任何无法回指介绍词里的事实锚点或概念发散段落，或只有“主体名＋上线/启动/在线”这类包装动作词，均视为文案失败，必须重写后才能生成指令。

### 口播包装的生成边界

1. 用户选择 `talking_head`，或需求命中口播包装、口播精剪、口播字幕包装、带动效的字幕包装后，最终视觉成片必须由视频生成完成并锁定 MiniMax H3；不得把字幕格式化、媒体拼接或普通字幕烧录结果当作包装成片交付。
2. 需要准确台词时，可在设置收齐后调用转写工具；转写结果只进入 `speech_facts`、`TEXT_WHITELIST`、重音和时间点，不负责生成视觉样式。
3. subtitle formatting 不参与口播包装视觉生成。media assembly 只能在 H3 已成功生成之后，用于恢复/混合原口播音轨、精确裁切时长或封装容器；不得用它烧录字幕、绘制卡片或替代 H3 生成。
4. 口播包装默认让 H3 同步生成克制触感音效，并要求原对白、口型和房间底噪保持在最前。用户明确“不要新增音效”时才关闭生成音效；需要字符级恢复原对白时，只在 H3 结果之后做确定性音轨处理。

口播视觉硬锁：`CAPTION_TRACK` 必须做“一条一条推进”的基础字幕，单次只呈现一个完整意群/一句话，长句可折成 1–2 行；禁止一次出现多句口播，也禁止全片固定一个底部圆角框。15 秒至少两次 65%–110% `KEYWORD_HERO_TRACK` 关键词包装动画、一次来源明确的素材弹窗/原片 crop/PiP `EVIDENCE_CARD_TRACK`、一次说话人缩到左上/右上角的 `SPEAKER_MINI_HEAD` 小窗版式、两次 2%–3% 合成层轻推近/视差，以及 3–5 个分别绑定关键词、卡片、版式换位的短触感音效。若最终 Prompt 没写出素材来源、卡片证明的台词、停留/退出方式或这些时间点，不得生成指令。

## 1. 两阶段读取

设置问询前只使用本文件，不预读 Reference。用户完成全部设置后、编写每一条最终 Prompt 之前，用 reference reading 即时读取且只读取一次：

- [h3-execution-grammar.md](h3-execution-grammar.md)：中文生成指令结构、文案、构图状态、时间轴、全局检查和 7000 字硬上限。
- [subject-packaging-system.md](subject-packaging-system.md)：本次主体、空间模式、口播或原片权限。
- [typography-system-library.md](typography-system-library.md)：字体角色、配色、图形组件、空间关系和动态语法。
- [music-direction-library.md](music-direction-library.md)：所选风格的音乐材料与 cue。
- 仅一份已确认的主风格：
  - 清新可爱风 → [style-fresh-cute.md](style-fresh-cute.md)
  - 科技粒子风 → [style-tech-particle.md](style-tech-particle.md)
  - 炫酷艺术风 → [style-cool-art.md](style-cool-art.md)
  - 暗黑胶片故障风 / dark-pop 故障 / cyber-grunge / 地下音乐杂志 / 黑红 Logo 发布片 → [style-dark-pop-glitch.md](style-dark-pop-glitch.md)
  - 海报大字拼贴风 / 复古拼贴海报 / 拼贴剪纸 → [style-poster-collage.md](style-poster-collage.md)，命中“复古拼贴剪纸”时只启用其中 1A 增强路由
  - 口播包装风 → 使用已读取的 [subject-packaging-system.md](subject-packaging-system.md) 口播分支，不重复读取文件

即使同一 session 早先读过，也不得依赖旧读取结果或记忆摘要；用户改选设置后重新执行这一组读取。不要新增同义 Reference。

## 2. 先建立事实，不替用户做设置

```text
INPUT_FACTS = {
  source_type: video | image | text | mixed,
  source_assets: [真实附件名或素材 ID],
  subject_type: product | person | logo | scene | mixed | unknown,
  logo_layout_type: pure_logo | logo_with_cover_anchor | not_logo | unknown,
  identity_facts: [素材中真实可见、必须保持的轮廓/结构/材质/颜色/脸/字形/空间],
  speech_facts: [准确语句、重音、停顿；无则 none],
  reference_ratio: [只展示，不代替成片画幅],
  has_audio: yes | no | unknown
}

PACKAGING_SETUP = {
  video_use_mode: creative_rework | preserve_original | not_applicable | awaiting,
  subject_mode: product_hero_stage | person_editorial_stage | logo_motion_stage | scene_rebuild_stage | mixed_stage | preserve_original_packaging | awaiting,
  space_mode: preserve_source_space | rebuild_editorial_space | hybrid_local_set | awaiting,
  output_ratio: 16:9 | 4:3 | 1:1 | 3:4 | 9:16 | 21:9 | awaiting,
  resolution: 2K,
  duration: 5s | 10s | 15s | user_value | awaiting,
  style: fresh_cute | tech_particle | cool_art | dark_pop_glitch | poster_collage | talking_head | awaiting,
  text_mode: agent_curated | exact_user_text | awaiting,
  text_language: agent_recommended | Chinese | English | Mixed | awaiting,
  text_whitelist: [准确文字] | awaiting,
  caption_mode: auto_exact_transcript | user_transcript | keyword_only | no_caption | not_applicable,
  music_mode: preserve_original_audio | style_generated_instrumental | user_audio_reference | no_music
}
```

`reference_ratio`、素材气质和文件名都不能自动写入 `output_ratio` 或 `style`。`logo_layout_type` 只由参考图/视频自动判断并回显，不作为问询卡片的新问题。

## 3. 一张前置设置卡收齐项目

缺少设置时显示同一张卡，已确认字段直接回显，不重复问。

进入本路线后，第一次 confirmation card 必须一次收齐所有仍为 `awaiting` 的独立设置。设置卡由本路线负责，优先于 执行层 的通用成片信息问询。禁止先单独询问时长、比例，禁止把时长与比例拼成 `5秒 9:16`、`8秒 16:9` 一类组合选项，也禁止在设置未收齐时开始素材分析、模型能力查询或生成。

设置卡前先用一行回显已知事实：

```text
素材=[真实素材]｜视频使用=[二创/锁定/图片输入不适用]｜参考比例=[素材比例，仅供参考，不作为成片比例]｜Logo构图=[纯Logo/Logo+封面锚点/不适用]
```

图片输入直接记录 `video_use_mode=not_applicable`，不把它做成待选问题；检测到视频时，把“视频使用方式”加入同一张 confirmation card。

问询路由只保留这些规则：无素材也无描述时先让用户选择上传图片、上传视频或输入内容；视频使用方式与空间处理分开判断；锁定原片时强制 `preserve_source_space`；图片仍须确认空间处理，主体类型只调整推荐项顺序；参考比例只回显，不提供“自适应”；`Agent 推荐`仍需用户确认；用户选择必现文字但未提供原文时，下一次只追问准确文字。

### 设置卡固定结构

第一次确认卡只收齐尚未明确的决定，每项单选且推荐项放第一位，用户仍可输入自定义答案。依次确认：画面保留原环境、重建包装空间或局部混合；主体围绕产品、人物、Logo 或场景组织；最终画幅；5、10 或 15 秒时长；主包装风格；可读文字由用户提供还是由 Agent 基于事实提案；以及屏幕文字语言。若输入包含视频，再补问沿用视频做二创还是锁定原片只做包装。已明确的字段直接回显，不重复询问。

主体包装的推荐项根据 `subject_type` 排到第一位，但不能替用户自动确认。文字控制默认推荐“输入必现文字”；用户选择“输入必现文字”后仍未给出文字时，下一次只追问准确文字；不重复整张卡。文字语言仍要确认，但它只决定排版角色：必现文字必须逐字保留，不得为了混排强行翻译、补写或替换。选择“Agent 自动搭配”时，必须先写 `SCENE_PACKAGING_COPY` 再拆 `TEXT_WHITELIST`，并允许用户继续改文字。选择“Agent 推荐”后，先根据主体、观看场景和文案长度给出一句推荐理由，再写入 `text_language`。

设置回显应包含素材、视频使用方式、画面处理、主体包装、画幅、分辨率、时长、风格、文字、字幕和音乐选择。

字段仍为 `awaiting` 时继续同一张卡，不生成生成指令 Prompt。

## 4. 设置确认后的唯一执行链

1. 按第 1 节即时读取五类 Reference，不使用同一 session 的旧摘要。
2. 按 `h3-execution-grammar.md` 先列 `FACTS_FOR_COPY`，再写 `SCENE_PACKAGING_COPY`（一段连贯、可读懂的产品/场景介绍词），然后用 `COPY_TRACE` 逐条从介绍词拆出 `COPY_DECK / TEXT_WHITELIST`，完成语言检查和字符预算；不能直接从主体名、风格名、字体动作或材质词拼关键词，介绍词也不要求整段全部上屏。
3. 按 `subject-packaging-system.md` 锁定主体身份、空间权限和本次主体最低交付；产品必须建立 `PRODUCT_PROTECTED_LAYER`。
4. 按 `typography-system-library.md` 选择可见字体骨架与 2–4 个动作机制；再套当前风格 Reference 的独有材质、状态和锁定块。
5. 按 `music-direction-library.md` 写音乐模式、声音材料和逐状态 cue。
6. 严格使用 `h3-execution-grammar.md` 的唯一 Prompt 模板和全局检查，再执行当前主体与风格的专属检查。

## 5. 唯一生成指令

最终只输出一个使用 `working_language`、目标 5600–6200、绝不超过 7000 字符的 `final_h3_prompt`。长度按实际字符串逐字符计数，包含空格、标点、换行和素材标记；超过 7000 或无法可靠计数时禁止展示和执行。自动压缩顺序：先删重复形容词 → 合并重复身份/负面边界 → 合并相邻状态的同义句；保留准确文字、时间点、字体角色、素材来源、空间关系、动作链和必要检查。展示给用户的 Prompt 与实际视频生成使用的字符串必须逐字一致；分辨率默认使用 2K 并检查结果；所有设置未确认、Reference 未即时读取或任一全局/主体/风格检查未通过时，不得执行。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
