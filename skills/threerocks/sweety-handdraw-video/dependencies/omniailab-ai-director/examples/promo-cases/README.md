---
name: omniailab-promo-cases
description: 宣传片线成品样例库索引——7 条真实 MiniMax H3 成片的原话输入/成品提示词与“记录→子技能→文件”一一对应表。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

---
name: omniailab-promo-cases
description: 宣传片线成品样例库索引——7 条真实 MiniMax H3 成片的原话输入/成品提示词与“记录→子技能→文件”一一对应表。
version: 2.0.35
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 宣传片线 · 成品样例库（真实生产记录）

**这一层是什么**：把真实跑过的 7 条 MiniMax H3 成片，连**当时的原话输入／成品提示词**一起存下来。
规范在 `references/promo/`，**可照抄的成品在这一层**。所有样例均在 **OmniAiLab 画布 · MiniMax H3** 上生成。

> **一句话用法**：动笔写某个方向的提示词之前，**先来这里看一眼有没有近似样例**——照它的骨架改，比从零写快得多，也更不容易漏掉该方向的关键约束。

## 一、记录 → 子技能 → 文件（一一对应）

| 源表 # | 标题 | 影片类型 | 当时选的子技能 | 样例文件 | 提示词形态 |
|---|---|---|---|---|---|
| 23 | AURELIS 香水品牌短广告 | TVC | `brand-ad` | [`brand-ad/01_香水品牌短广告.md`](brand-ad/01_香水品牌短广告.md) | 原话输入（需求侧） |
| 24 | 高端护肤精华短广告 | TVC | `brand-ad` | [`brand-ad/02_护肤精华短广告.md`](brand-ad/02_护肤精华短广告.md) | 原话输入（需求侧） |
| 25 | 口红短广告 | TVC | `brand-ad` | [`brand-ad/03_口红短广告.md`](brand-ad/03_口红短广告.md) | 原话输入（需求侧） |
| 26 | 多口味果汁横屏短广告 | TVC | `brand-ad` | [`brand-ad/04_多口味果汁短广告.md`](brand-ad/04_多口味果汁短广告.md) | 原话输入（需求侧） |
| 27 | Omni AiLab 霓虹 CG 标题片 | 标题片 | `h3-visual-design` | [`h3-visual-design/01_霓虹CG标题片.md`](h3-visual-design/01_霓虹CG标题片.md) | **成品提示词**（可直接投喂） |
| 28 | 地下空间舞者追踪动效 | TD 动效 | `touchdesigner-workflow` → 归入 `h3-visual-design` | [`h3-visual-design/02_地下空间舞者追踪动效.md`](h3-visual-design/02_地下空间舞者追踪动效.md) | **成品提示词**（可直接投喂） |
| 29 | 社交头像 App UI 动效 | UI 动效 | `ui-motion` | [`ui-motion/01_社交头像AppUI动效.md`](ui-motion/01_社交头像AppUI动效.md) | **成品提示词**（可直接投喂） |

**关于第 28 条**：源记录当时选的是 `touchdesigner-workflow`（属"本地软件连接器类"，本 skill **未并入该目录**，只保留指路），
其规范内容归入 `references/promo/h3-visual-design/`（追踪视觉分支：`td-cv-tracking.md`、`td-visual-attributes.md`），故样例也落在该目录下。

## 二、按你要做的事取用

| 你要做 | 直接翻 |
|---|---|
| 15 秒内、单一产品、靠材质与光说话的 **TVC** | `brand-ad/01`（玻璃与光线）、`02`（材质与微观水膜） |
| 美妆／快消类，要**动作节拍**（升起→打开→环绕→定版） | `brand-ad/03` |
| 快消多口味／多 SKU 的**合集收尾** | `brand-ad/04` |
| CG 三维字标／**片头标题序列** | `h3-visual-design/01`（含完整 15 秒时间结构，可直接当骨架） |
| **追踪视觉／舞蹈类动效** | `h3-visual-design/02` |
| App／产品 **UI 动效**（含交互链路） | `ui-motion/01` |

## 三、三条硬提醒（照抄前必读）

1. **参数必须逐条改**：样例里的时长／画幅／分辨率是**当时那条片**的，换片必须改；本 skill 的既有口径是**参数只落在画布，不写进提示词正文**。
2. **品牌资产必须换干净**：样例里的品牌名、产品名、瓶型、Logo 文案、落版文字全是案例专有，**换片必换，不得残留**。
3. **注意提示词形态**：
   - 4 条 `brand-ad` 存的是**当时的原话输入**（需求侧一句话），成品提示词由该方向按 `references/promo/brand-ad/GUIDE.md` 的流程编译；
   - 3 条视觉／UI 类存的是**可直接投喂的成品提示词**；
   - 成品提示词样例里保留了若干"不要…"句式，那是原作者当时的写法。**按本 skill `references/PROMPT-DOCTRINE GUIDE.md` 的十一条铁律，否定式应改写为末段的正向锁定后再投喂**（写"不要旗子"容易把旗子召回来）。各文件已逐条标注。

## 四、成片在哪

7 条成片（每条 5–17 MB，共约 87 MB）都在源 Base 表内，**未随仓库分发**（控制仓库体量）。
表：`ZWyIbhfi7an84KsNDnpcywUbn5b` ／ `tblMY8xSafIUiaa2` ／ 视图 `vewYjWpvy8`。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
