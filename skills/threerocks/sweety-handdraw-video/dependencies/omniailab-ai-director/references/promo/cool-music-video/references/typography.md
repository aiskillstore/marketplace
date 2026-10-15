---
name: omniailab-promo-cool-music-video-typography
description: 「复古潮流拼贴字体参考」—— 酷感音乐短片（15 秒横屏） 方向细则：动态字体默认使用准确英文，并且要像海报、纸张、墙面或前景实体一样参与表演。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 复古潮流拼贴字体参考

动态字体默认使用准确英文，并且要像海报、纸张、墙面或前景实体一样参与表演。`working_language` 不改变本 Skill 的 English-only 屏幕包装；只有用户明确指定某段准确原文必须上屏时，才保留用户原文。字体 reference 只借字形骨架、尺度、材质、字距和运动机制，不要求模型安装真实字体。

## 字体路线

### 主字族：Ultra-black condensed grotesk

- ALL CAPS，700–900 weight，极窄字宽，tight 或 negative tracking。
- 平直切角、矩形 counters、厚重黑块，适合 `Hero type` 和压屏词。
- 可做横向压缩、纵向拉伸、纵排、越界裁切、人物前后景遮挡。
- 材质优先油墨、复印纸、半色调和硬阴影；不要干净白色 CG 3D 字。

### 主字族备选：Heavy newspaper serif / slab display

- 仅在用户参考明显偏报刊、老海报或粗衬线时使用；粗细对比和硬朗衬线形成复古编辑感。
- 字体可跨照片接缝、纸片边缘和倾斜画框；先完整可读，再被撕纸或套印切开。

### 辅字族：窄体 neutral sans / monospaced technical / marker accent

- 一次项目最多选一个辅字族。
- 只用于 Lyric type、边注、括号、箭头或少量编号；不生成密集伪 UI、小报副标题或随机数字。
- marker accent 要像真实手写英文批注：略不规则基线、轻微笔画变化、清楚可读，不做卡通涂鸦。

## 每镜字体字段

每个镜头用以下顺序描述，不能压缩成“加大字”：

1. `Exact text`：默认来自本项目已确认的英文视觉词；可由歌词、片名、人物状态或情绪翻译/提炼而来。用户明确指定准确原文必须上屏时保留原文。最终 prompt 只写实际文字，不写白名单元数据。
2. `Role / scale`：Hero 30–150% 画幅；Action 12–40%；Lyric 沿边缘或人物轮廓；Texture 仅使用已确认英文字符碎片。
3. `Anatomy`：字族、ALL CAPS/大小写、字宽、字重、端点、counters、tracking、leading。
4. `Material / color`：油墨、纸、网点、胶带、玻璃或现场墙面；写准确主色和阴影色。
5. `Depth`：前景实体字、中景人物遮挡、背景墙面贴附、接缝跨层或纯文字黑场；需要透视时写消失点。
6. `Layout`：越界块字、纵排、横压缩、非规则分栏、负空间孤字、遮罩挖空、镜像或跨缝连接。
7. `Choreography`：进入 → 清晰可读 → 由 vocal/snare/hi-hat/808 或动作触发变形 → 遮挡/穿越 → 恢复或退场。

## 全片层级节奏

- 开头建立一个清晰 Hero type，让模型知道主字族是什么。
- 中段轮换 Action type、纵排词、人物前后景穿插和复印残影。
- 高潮可用非规则分栏、双色套印、字块压屏或 0.2–0.5 秒纯文字黑场。
- 结尾回收同一主字族和色盘；不要突然切换成无关的科技 UI 或品牌 Logo。
- 文字始终先给短暂可读时刻，再变形；不要从头到尾生成乱码。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
