---
name: omniailab-promo-case-ui-motion-01
description: ui-motion 成品样例：社交头像 App 界面动效的成品提示词与“动作顺序即信息结构”拆解。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 社交头像 App UI 动效（UI 动效 ｜ 竖屏 ｜ 15 秒内）

**对应子技能**：`references/promo/ui-motion/GUIDE.md`（UI 动效与产品演示方向，含品牌分析／动效脚本规范／QA 清单／8 套风格）
**生成**：OmniAiLab 画布 · **MiniMax H3**
**成片**：源表内 `社交头像AppUI动效.mp4`（约 11.4 MB，未随仓库分发）
**源记录**：`recvwkOJ4GsPEx`

## 一、成品提示词（原文，可直接改用）

```text
做UI动画，创作社交头像App。柔蓝薰衣草渐变与玻璃面板中，可爱3D头像从PROFILE卡探出并微笑、挥手、眨眼；拖拽旋转查看造型，点击统计展开关注、粉丝、经验与徽章，再进入OUTFIT、COLOR、ACCESSORIES、STYLE编辑器切换服装、配饰和颜色，最后将头像、卡片与按钮拆成可触控旋转的三维层并落版“CREATE YOUR AVATAR”。禁平面角色、战斗、武器、随机漂窗和被动展示。
```

## 二、这条为什么这么写（UI 动效的四段式）

1. **品牌视觉先定调**："**柔蓝薰衣草渐变与玻璃面板**中"——UI 动效第一条永远是**界面视觉语言**（配色＋材质），
   它决定后面所有交互的观感；这里用了当前最主流的"渐变＋玻璃拟态"。
2. **交互链路按用户动作顺序写**：
   **3D 头像从 PROFILE 卡探出（微笑／挥手／眨眼）→ 拖拽旋转查看造型 → 点击统计展开（关注／粉丝／经验／徽章）
   → 进入 OUTFIT／COLOR／ACCESSORIES／STYLE 编辑器切换 → 拆成可触控旋转的三维层 → 落版**。
   这是 UI 动效最该照抄的地方：**提示词里写的是"用户做了什么、界面如何响应"，不是"画面长什么样"**——
   因为 UI 动效的本质是**交互演示**，动作顺序就是信息结构。
3. **落版给明确文案**："落版 `CREATE YOUR AVATAR`"。
   > 画面内出现可读文字（按钮／标签／落版标题）时，按本 skill 主线口径，**这类含文字的画面优先用 `image2.5` 出首帧**
   > （中文与排版能力最强），再交给 MiniMax H3 做运动，成功率更高。
4. **末句给"禁"清单**："禁平面角色、战斗、武器、随机漂窗和被动展示"——
   把**常见跑偏方向一次性堵掉**。同前面几条：这几句在**需求侧**很好用，
   进入生成提示词时应改为正向表述（例如"角色为立体 3D 形象"代替"禁平面角色"）。

## 三、怎么用

- **要做**：App／产品的 UI 动效、功能演示、编辑器类产品的交互展示。
- **怎么改**：换品牌视觉（配色＋材质）→ **保留"动作顺序即信息结构"的写法**，把动作换成你的产品真实交互路径 →
  落版文案换成你的 CTA → 参数移到画布。
- **配合**：`references/promo/ui-motion/` 的品牌分析与动效脚本规范；含文字的界面帧走主线 `image2.5`。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
