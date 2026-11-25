# 完整示例：单角色从一句话到交接包

> 虚构演示，未真实出图。所有"验收结论"均为示例口径，用来示范每一步的产出长什么样；真实执行时结论必须来自看图（SKILL.md 第 7 节）。

## 0. 一句话想法（用户输入）

"想要一个民国女侦探，聪明冷静，穿风衣，短发，准备做短剧主角。"

拆解（步骤 ①）：
- 身份与处境：民国侦探社女侦探，独立接案
- 物种：人类
- 年龄气质：28 岁印象，冷静干练
- 核心识别点：波波头＋风衣＋放大镜吊坠（侦探身份可视化）
- 世界观：1930 年代上海，写实向
- 用途：短剧主角（视频）→ 媒介选 3D 写实或摄影写实；本例走 3D

## 1. 设计定位与自检简表（步骤 ③）

设计定位：1930 年代上海女侦探，靠波波头、卡其风衣和放大镜吊坠一眼立住。

身份锚点（1–3 个）：① 齐下巴波波头、中分、无刘海；② 卡其色双排扣风衣＋腰带；③ 黄铜放大镜吊坠（核心道具）。

| 维度 | 结果 | 说明 |
|---|---|---|
| 剪影 | ✅ | 波波头圆轮廓＋风衣下摆，全组唯一 |
| 比例 | ✅ | 约 7 头身，腿长偏长，站姿重心稳 |
| 脸 | ✅ | 鹅蛋脸、平直眉、眼尾微下垂显冷静，角色左颊（画面右侧）一颗小痣 |
| 发 | ✅ | 黑色波波头、齐下巴、中分、发尾内扣 |
| 服装层次 | ✅ | 白衬衫 → 深灰马甲 → 卡其风衣，腰带金属扣 |
| 材质 | ✅ | 风衣棉质斜纹、马甲毛呢、吊坠黄铜，三种分明 |
| 色板 | ✅ | 卡其 60% / 深灰 30% / 黄铜金 10% |
| 道具 | ✅ | 放大镜吊坠：黄铜圆框、短链、挂在马甲左胸口袋 |
| 不对称与记忆点 | ✅ | 吊坠只挂左侧；记忆点一句话："风衣上挂放大镜的女侦探" |
| 磨损与痕迹 | ✅ | 风衣下摆轻微磨边（常跑现场） |
| 世界观契合 | ✅ | 1930 年代上海，服装工艺符合年代 |
| 姿态与行为 | ✅ | 站姿笔直、下巴微收、目光平视（侦探的审视感） |

## 2. 风格选择（步骤 ④）

- 媒介层：3D
- 写实度层：写实
- 具体风格：style-library #16「3D写实游戏CG」
- 固定风格描述：`high-end realistic 3D game character render, PBR materials, detailed fabric and metal, cinematic studio lighting`
- 注：#16 在 style-library 中现行状态为「可用」（2026-10-21 实测），本例直接选用；若选的是「未测试」条目，按 SKILL.md 步骤 ④ 先跑小样再继续。

## 3. 母版提示词（步骤 ⑤）

```
[CHARACTER ANCHOR — 不可变，跨所有图逐字复用]
Shen Yizhen, a 28-year-old East Asian woman detective in 1930s Shanghai, tall and slender build, about 7-heads-tall proportions,
face: oval face, straight eyebrows, calm narrow eyes with slightly downturned outer corners, dark brown irises, a small mole on her left cheek, straight nose, natural lips, fair skin,
hair: black bob cut to the chin, center part, no bangs, inward-curled ends,
outfit: inner white cotton blouse / dark gray wool vest / khaki double-breasted trench coat with belt and metal buckle / dark gray straight trousers and black low-heel leather shoes,
signature: a brass magnifier pendant on a short chain, hanging from the left chest pocket of her vest; calm, observant temperament

[SHOT VARIABLE — 母版专用]
Full body, front view, neutral relaxed expression, mouth closed, arms slightly away from body,
even soft studio lighting, plain light gray seamless background, no text.

[STYLE]
Style: high-end realistic 3D game character render, PBR materials, detailed fabric and metal, cinematic studio lighting

[CONSTRAINTS]
no text, no watermark
```

中文说明：锚点块把脸、发、四层服装、吊坠位置（角色左胸）逐字写死；母版变量块只放构图与光线——平光、浅灰底、无戏剧光，避免把阴影烤进身份。

## 4. 母版候选与选定（步骤 ⑥，示例口径）

出 4 张候选后对照自检表验收：
- 候选 1：痣跑到右脸 → 淘汰（可数/位置特征错）
- 候选 2：全对，吊坠链子略长 → **选定**（小瑕疵不影响身份，后续在锁定记录里写明链长以母版为准）
- 候选 3：风衣变单排扣 → 淘汰
- 候选 4：波波头变长发 → 淘汰

选定后母版不再重生成，后续全部从它派生。

## 5. 锁定记录（步骤 ⑦）

```
角色名 / 版本号：沈亦真 v1        母版文件：00_master.png
身份一句话：1930 年代上海女侦探，冷静干练，独立接案
物种与身体比例：人类女性，约 7 头身，身高印象偏高，体型纤细
脸：鹅蛋脸、平直眉、眼尾微下垂、深棕瞳、角色左颊（画面右侧）一颗小痣、直鼻、自然唇、肤色偏白
发：黑色波波头、齐下巴、中分、无刘海、发尾内扣
服装层次与配色：白棉衬衫 → 深灰毛呢马甲 → 卡其双排扣风衣（腰带金属扣）→ 深灰直筒裤、黑低跟皮鞋
配件位置：黄铜放大镜吊坠挂马甲左胸口袋（角色自身左侧）
核心道具：放大镜吊坠（黄铜圆框＋短链，链长以母版为准）
可数特征：风衣双排扣 ×8、痣 ×1（角色左颊（画面右侧））
风格描述：#16 3D写实游戏CG — high-end realistic 3D game character render, PBR materials, detailed fabric and metal, cinematic studio lighting
不可变字段：脸、发、体型、四层服装结构与配色、吊坠位置与材质
本次允许变化：按派生资产规格逐项放行（角度/表情/姿态光线/服装层）
尚未展示 / 推定区域：背面风衣开衩样式未确认，派生背面时用低复杂度推定并标注
已知弱点：（待派生后回填）
变更日志：v1 建立
```

## 6. 派生资产提示词示例：全身三视图（步骤 ⑦）

锚点块与母版逐字相同，只换变量块：

```
[SHOT VARIABLE — 三视图]
Character turnaround sheet, three full-body views side by side on one canvas: front view (0°), side view (90°, character's left side facing viewer), back view (180°), same scale, A-pose, plain light gray background, even soft lighting, no text.
```

其余派生（头部图、表情板、细节板、定妆照）同理：锚点不动、每次只换一个维度，规格见 asset-derivation.md，出图后逐张对照锁定记录验收。

## 7. identity_line（交接包，步骤 ⑧）

```
Shen Yizhen, a 28-year-old East Asian woman detective in 1930s Shanghai, tall and slender, oval face with straight eyebrows, calm downturned eyes, dark brown irises, a small mole on her left cheek, black chin-length bob with center part, wearing a white blouse, dark gray wool vest and a khaki double-breasted trench coat with belt, a brass magnifier pendant hanging from her left vest pocket.
```

（约 70 词，落在 40–80 词要求内。）

## 8. 交接包清单（步骤 ⑧）

```
shen-yizhen_v1/
  00_master.png            母版（已选定，候选 2）
  01_turnaround.png        全身三视图
  02_head.png              头部图（头身分离·头）
  03_expressions.png       表情板
  04_details.png           吊坠、风衣扣、色板
  05_portrait.png          定妆照
  lock_record.md           上面第 5 节
  identity_line.txt        上面第 7 节
```

交接说明（附 lock_record 末尾）：
- 推荐首帧：00_master.png 或 05_portrait.png 作身份参考
- 禁止变化清单：发长与分缝、痣的位置、风衣排扣数、吊坠位置（角色左侧）
- 已知弱点：（派生验收后回填，如"侧面痣不可见属正常，不要在侧面图上补痣"）
