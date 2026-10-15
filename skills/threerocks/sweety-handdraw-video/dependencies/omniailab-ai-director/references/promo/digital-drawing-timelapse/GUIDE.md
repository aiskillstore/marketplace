---
name: omniailab-promo-digital-drawing-timelapse
description: 数字绘画延时（15 秒） —— 宣传片线方向之一：一段提示词 ＋ 一张成品图，生成 15 秒数字绘画延时视频。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

> **在本 skill 中的位置**：一段提示词 ＋ 一张成品图，生成 15 秒数字绘画延时视频。由**宣传片线总调度** `references/PROMO GUIDE.md` 在判定为该方向后接入。
> **生成口径**：提示词编译完成后，统一在 **OmniAiLab 画布** 中选择 **MiniMax H3** 生成视频；图像与资产类提示词仍按主线层级执行（`references/LIRA GUIDE.md`／`references/STYLE GUIDE.md`／`references/ASSET-SYSTEM GUIDE.md`／`references/PROMPT-DOCTRINE GUIDE.md`）。
> **与主干的关系**：本文件是宣传片线的方向细则，**不改变 P0→P6 主干与确认门禁**；涉及资产、表演、情绪、站位与光学时照常调用主线对应层。
> **暂停点**：素材与文字确认 → 方向与风格确认 → 提示词确认 → 生成 → 验收；每一步都等创作者确认后再继续，**不得一次跑完**。
> **触发词**：手绘过程／手绘延时摄影／绘画过程视频／数字绘画过程／速涂视频

# 数字绘画延时（15 秒）

使用一张成品角色图或数字插画参考图，以及本 Skill 中固定的默认提示词，生成一条15秒角色绘画过程视频。默认使用 MiniMax H3；用户明确指定其他模型时先检查能力，兼容后遵循选择。生成失败先针对原因重试一次，随后切换其他兼容模型，不反复死磕同一模型。

第三步中的完整英文提示词是不可变的默认提示词。用户只输入 `/digital-drawing-timelapse` 并附上一张图、没有提供替换提示词时，自动使用这段提示词，并保持其内容不变。后续无论生成第几次，都不得根据生成次数、历史结果或会话记录修改默认提示词。

只有用户明确提供另一段完整视频提示词时，才允许在当前调用中临时覆盖默认提示词；替换提示词不会修改 Skill 中存储的默认提示词。

每次生成视频前，都必须通过卡片弹窗让用户选择并确认输出分辨率、画幅比例和音频处理方式。这些是执行参数，不是对固定提示词的修改。如果用户附带音频，应在同一张卡片中列为可选音轨，只有用户确认使用后才能合成。用户选择无音频时，生成无音频视频。

本 Skill 是直接生成路径。不读取、附加或使用原版过程视频、界面截图、第二张风格参考图、分镜、脚本、音频或其他创作素材。不额外添加界面重建规则、软件布局要求、缩略图限制、光标形态、镜头、音频或其他用户没有写入当前提示词的创作约束。

参考图不是首帧，而只用于约束提示词中要求的最终人物外观、比例、服装、发型、颜色、特殊特征和其他视觉内容。生成视频应在所选视频能力允许的范围内尽可能遵循用户提示词。

## 第一步：接收图片并确定提示词

必须有一张成品图参考。

直接使用用户提供的第一张图片作为参考图。不要把其他素材重新解释成界面或风格参考。如果缺少图片，应询问缺少的图片，不得自行编造。

提示词的确定方式是固定的：

- 用户只输入 `/digital-drawing-timelapse` 并附图、没有提供替换提示词时，自动使用第三步中的完整固定提示词。
- 每次生成都按该固定提示词的原意使用，不得改写、压缩、扩展、调序或追加约束。
- 不继承之前生成、历史结果、原版过程视频、界面截图或会话记录中的提示词修改。
- 只有用户明确提供新的完整提示词时，才在本次调用中覆盖默认提示词；不会更新 Skill 中的默认提示词。

参考图只用于固定提示词或用户明确替换提示词所描述的最终视觉目标。

## 第二步：确认执行参数

开始生成视频前，必须弹出一张卡片，让用户通过选项选择并确认：

- 输出分辨率，不预选默认值
- 输出画幅比例，可提供16:9建议但仍需用户确认
- 音频处理：无音频或合成音频
- 如果选择合成音频，并且存在音频附件，是否使用该音频作为音轨

卡片必须提供明确的“确认生成”操作。使用固定提示词原文，仅应用用户确认的执行参数。用户确认卡片前不得开始生成视频。固定默认提示词不需要重复确认。用户关闭、编辑卡片或留下任何必选项未确定时，保持等待，不得生成。

## 第三步：直接生成

只根据已确定的提示词和这一张参考图直接生成一条视频。

没有替换提示词时，已确定的提示词就是第三步中的固定默认提示词。不得进行单独的界面分析，不使用原版过程视频，不添加旧的界面规则，也不增加或删除任何创作指令。重复生成时默认提示词必须保持一致。

如果用户明确提供替换提示词，只在本次调用中使用它，不修改固定默认提示词。按照当前生效提示词保留时长、画幅、分辨率、音频、镜头、界面、光标行为、时间节点、风格和限制；当前提示词未指定画幅时默认16:9，未指定音频时默认关闭。

将成品图作为参考输入，而不是首帧关键帧。提示词仍然是绘画过程、界面、动效、镜头和最终展示的最高创作指令。

## 第四步：内部提示词模板

下面的英文提示词是不可变的默认生成提示词。用户只输入 `/digital-drawing-timelapse` 并附图、没有提供替换提示词时，自动完整使用它。不得追加、删除、改写或调序；无论生成次数多少都保持不变。只有用户明确提供替换提示词时，才在单次调用中使用替代版本。

```text
Create a 15-second fast-paced character creation timelapse inside a professional digital drawing and character design interface.

Use the provided character reference only as the final target for the character’s appearance, proportions, clothing, hairstyle, colors and distinctive features. The process must visibly start from a completely blank canvas and reconstruct the referenced character from scratch.

Show a visible mouse cursor actively controlling the entire creation process. Every major visual change should feel caused by cursor interaction with the UI.

0:00-0:02
Start on a blank white or neutral canvas inside a clean professional drawing interface. The cursor quickly creates the first loose construction lines, head shape, body proportions and basic pose using rough sketch strokes.

0:02-0:05
Accelerate into detailed sketching. The cursor rapidly defines the face, hair, anatomy, clothing silhouette, accessories and characteristic features of the referenced character. Use believable drawing gestures, short strokes, selections, transforms and occasional undo corrections.

0:05-0:08
The rough sketch becomes clean line art. The cursor switches tools, adjusts brush size and cleans the silhouette. Unnecessary construction lines disappear while precise facial details, clothing folds and small design elements are added.

0:08-0:11
Rapid coloring phase. The cursor selects regions and fills the character with the correct colors from the reference. Show quick palette selections, color picking, layer changes, clipping masks and brush passes. Add shadows, highlights and material details in fast succession.

0:11-0:13
Rendering and polish. The cursor adds final lighting, hair detail, skin shading, fabric texture, reflections and small accent details. Briefly zoom into important areas such as the face or costume while refining them, then zoom back out.

0:13-0:15
The interface clears unnecessary guides and panels. The finished character is shown fully rendered and closely matching the provided reference. End with the cursor making one final small adjustment, then stop on a clean full-character presentation.

STYLE:
High-speed digital art timelapse, polished professional character-design workflow, believable drawing software UI, smooth cursor movement, rapid but readable actions, clean layers and tool changes, no random text, no fake dialogue, no unrelated popups.

MOTION:
The entire 15 seconds should feel continuously productive. Avoid long pauses. Compress several minutes or hours of drawing into an energetic timelapse while keeping the progression clearly readable: blank canvas → rough sketch → clean line art → flat colors → shading → polished final character.

CAMERA:
Primarily screen-recording style with subtle digital zooms and pans following the cursor and active drawing area. Keep the UI stable and readable. Do not use cinematic cuts outside the software interface.

IMPORTANT:
The character must not appear instantly or through a single magical transformation. Every stage should visibly build upon the previous one through cursor-driven drawing, editing, coloring and rendering actions.
```

## 第五步：音频与输出规则

只返回一条生成视频及其准确文件名。除非用户另外要求，不生成方案文档、分镜、界面参考图、字幕文件或其他图片。

保留已确认的时长、分辨率和画幅。对于本模板，默认使用15秒和16:9，但不设置默认分辨率，分辨率必须每次明确选择并确认。默认关闭音频；用户明确确认后，才可使用附带音频作为合成音轨。没有明确确认时绝不使用音频附件。音频选择不能修改固定默认提示词。

如果生成失败，只针对错误原因进行有实质差异的修正，同时保留用户提示词和参考图。不得仅为了重试而添加新的创作约束。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
