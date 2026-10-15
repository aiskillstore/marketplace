---
name: omniailab-print-films
description: 电影印片风格预设（R01–R02）。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 电影印片风格

仅在用户指定 Kodak 2383、Fujifilm 3513、输入 `Rxx`、要求印片菜单或需要影院发行拷贝质感时读取本文件。

印片风格描述最终呈现阶段的对比、黑位、高光、色彩分离和密度。它可以单独使用，也可以叠加在拍摄胶片之后。

## 预设

### R01 Kodak VISION Color Print Film 2383

- 视觉特征：浓郁稳定的黑位、扎实影院对比、中性高光、清晰色彩分离、饱满但受控的色彩密度。
- 画面效果：增强明暗结构与投影拷贝质感，人物肤色保持自然，高光具有清晰层次。
- 适用：剧情电影、城市夜景、商业电影质感、需要厚实黑位与经典影院色彩的场景。
- 提示词表达：`Kodak 2383 电影印片质感，浓郁黑位，中性高光，清晰色彩分离，扎实而受控的影院对比`

### R02 Fujicolor Positive Film ETERNA-CP 3513DI

- 视觉特征：清晰色彩分离、平衡中性灰、受控对比、通透色彩、富士电影正片的发行拷贝质感。
- 画面效果：保持阴影层次和色彩辨识度，整体呈现洁净、细腻、具有银幕感的最终色彩。
- 适用：人物剧情、东方城市、自然环境、需要细腻色彩层次与平衡对比的场景。
- 提示词表达：`Fujicolor ETERNA-CP 3513DI 电影正片质感，清晰色彩分离，平衡中性灰，受控对比，细腻通透的影院拷贝色彩`

## 组合方式

- 单独选择印片时，直接描述最终色彩与对比，无需补充拍摄底片名称。
- 与 `Cxx` 组合时，将 `Cxx` 视为基础成像响应，将 `Rxx` 视为最终印片呈现。
- `S1` 轻微调整黑位与色彩密度，`S2` 呈现自然影院印片效果，`S3` 强化印片对比与色彩分离。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
