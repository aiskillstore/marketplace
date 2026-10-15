---
name: omniailab-promo-h3-visual-design
description: 动态视觉设计（字体包装／追踪视觉／手绘融合） —— 宣传片线方向之一：动态字体与空间包装、主体追踪框与拓扑图形、真人实拍与二维手绘互动三条路线的动态视觉短片。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

> **在本 skill 中的位置**：动态字体与空间包装、主体追踪框与拓扑图形、真人实拍与二维手绘互动三条路线的动态视觉短片。由**宣传片线总调度** `references/PROMO GUIDE.md` 在判定为该方向后接入。
> **生成口径**：提示词编译完成后，统一在 **OmniAiLab 画布** 中选择 **MiniMax H3** 生成视频；图像与资产类提示词仍按主线层级执行（`references/LIRA GUIDE.md`／`references/STYLE GUIDE.md`／`references/ASSET-SYSTEM GUIDE.md`／`references/PROMPT-DOCTRINE GUIDE.md`）。
> **与主干的关系**：本文件是宣传片线的方向细则，**不改变 P0→P6 主干与确认门禁**；涉及资产、表演、情绪、站位与光学时照常调用主线对应层。
> **暂停点**：素材与文字确认 → 方向与风格确认 → 提示词确认 → 生成 → 验收；每一步都等创作者确认后再继续，**不得一次跑完**。
> **触发词**：H3动态设计／动态字体／字体包装／主体追踪图形／追踪视觉／手绘实拍融合／视频视觉包装

# 动态视觉设计（字体包装／追踪视觉／手绘融合）

将本 Skill 作为薄路由入口。主文件只判断视觉技法，不承载任何具体风格配方；确定路线后按需读取对应 reference，由该 reference 完成设置、Prompt、生成和交付规则。

## 1. 路线选择

| 主导意图 | 路线 | 必读 reference |
| --- | --- | --- |
| 给人物、产品、Logo、场景、口播或原片加入动态字体、标题、卡片、图形、字幕或 合成感包装 | `typography-packaging` | [typography-packaging.md](references/typography-packaging.md) |
| 制作 TD / 实时视觉工具 / CV 调试视觉、追踪框、拓扑线、数字 ID、局部负片或“AI 看见的世界” | `td-cv-tracking` | [td-cv-tracking.md](references/td-cv-tracking.md) |
| 制作真人生活空间与二维手绘、涂鸦、蜡笔、粉笔动画融合的视频 | `handdrawn-live-action` | [handdrawn-live-action.md](references/handdrawn-live-action.md) |

明确出现 实时视觉与追踪 或手绘融合意图时优先进入对应路线；其余动态字体、Logo、口播和素材包装进入 `typography-packaging`。不要因为“炫酷”“特效”“视觉感”这类弱信号猜路线，缺少决定性信息时只询问一次用户想使用哪种表现技法。

一个任务默认只读取一条路线。用户明确要求组合两种技法时，先确定主路线，再只补读另一条相关 reference；不得预读全部路线或把三套规则拼进同一 Prompt。

## 2. 顶层边界

以下意图不进入本 Skill：

| 用户意图 | 去向 |
| --- | --- |
| 音乐、歌词、Rap、Fashion 表演或节拍分镜主导的完整 MV | `cool-music-video` |
| 品牌、产品卖点或商业叙事主导的广告 | `brand-ad` 或 `ad-tvc` |
| 角色觉醒、战斗、世界观或抽卡活动主导的二次元游戏 PV | `anime-game-pv` |
| 以参考视频证据分析和逐镜复刻为目标 | `video-deconstruct` |
| KOC / UGC 真人种草、测评、开箱或带货 | `koc-video` |
| 纯转写、SRT/ASS、字幕翻译或无动效字幕烧录 | 通用字幕/后期能力 |

判断依据是用户要交付的核心结果，不按单个关键词抢占其它完整品类 Skill。

## 3. 共同执行约束

1. 由 执行层 直接执行，不创建 阶段执行计划，不派 规划器 或 执行器 重新设计。
2. 只读取所选路线明确要求的 references；路线 reference 是具体问询、Prompt 结构、生成方式和完成条件的真相源。
3. 只使用真实存在的附件、画布节点和用户事实；不得虚构素材路径、品牌、文字、人物身份或参考关系。
4. 保留用户明确指定的模型、时长、画幅、主体、文案和声音要求；只询问会阻塞所选路线的缺失信息。
5. 路线生成最终 Prompt 后，展示内容、送入生成的内容与实际送入 H3 的内容必须一致；不得让下游摘要、翻译或二次改写。
6. 具体路线的硬规则优先于本入口的通用规则；路线未通过自身完成检查时不得交付。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
