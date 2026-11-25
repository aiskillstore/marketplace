# 风格库：三层体系（87 种）

> **开源体验版说明**：本文件是体验版节选。框架文字（定位、三层选择法、查找/新增/组合、大类与次选）完整保留；风格条目只收录 **20 条样本**的完整行（编号＋媒介＋写实度＋固定风格描述＋状态），其余 67 条仅在文末索引中列编号与中文名。**完整版**含全部 87 条的 Style 行、GPT Image 状态与 MJ / Imagine 两平台的逐条实测成绩及完整测试日志。

> 来源：内部测试包整理（42 种风格与三层体系）。**本库的定位（2026-10-21 先生定）：给 GPT Image 定制的风格库，专门筛适合 GPT 的风格。** 未测的标「未测试」，按 `style-test-kit.md` 一图定生死：**只判风格是否到位**（2026-10-21 晚先生改规矩：只测风格、不绑固定角色；此前按锚点判的 23 条「需加强」已全部转「可用」，锚点成绩保留在完整版测试日志作历史）——可用留在主表更新状态；不可用的拆出主表、移入文末「已拆出」区。风格描述只控制渲染方式，不得改动角色锁定字段。

## 三层选择法

1. **媒介层**：以风格表「媒介」列的实际取值为准——2D、2D手绘感、3D、传统手绘、传统版画、西方绘画、摄影、摄影工艺、数字影像、手工偶、手工、雕塑、印刷、玩具、题材风格。先定媒介、再在该媒介内找条目；媒介列里没有的分类就是库里没有，不许误报。
2. **写实度层**：写实 / 半写实 / 风格化 / 高度风格化。写实度会改变比例与五官处理，选定后同一角色全套资产不再切换。
3. **具体风格层**：从下表选一条，把「固定风格描述」原样附在提示词末尾 `Style: ...`。

选择建议：先按用途定媒介（视频→优先 3D/半写实/写实；表情包→风格化），再定写实度，最后选具体风格。系列角色共用同一条风格描述。选定的 Style 行若与硬约束（物种、母版规格）直接冲突，生产用途按 SKILL.md 步骤 ④「编译冲突规则」处理，不原样硬塞。

## 查找、新增与组合

**按名字找**：先定媒介层，再在表内按风格名（含英文名）找；找不到就是库里没有，不许拿近似条目顶替，说清"库里没有、最接近的是哪条、差在哪"。

**拿参考图找**：把参考图拆成三层（媒介是什么、写实度哪档、关键特征词是哪几个），与表内「固定风格描述」逐条比对；对得上的用那条，对不上走新增。逆推只定视觉配方，不能证明原作者用的软件、模型或工作流。

**新增一条风格**：从参考图或参考文档逆推出固定风格描述（英文短句，只写渲染、材质、光影，不写具体角色），按表格式入库、状态标「未测试」，再按 `style-test-kit.md` 实测回填。用这条路入的库：#43–#45（2026-10-21，源自先生发的参考图与《AI 视觉风格与提示词档案 V1.0》）。

**组合两种风格**：不整行相加，按层拆取——一条出「角色与材质」（题材、结构、材质），另一条出「摄影与情绪」（光影、色调、镜头、颗粒）。两条的写实度不得冲突；媒介互斥的（如水墨 × 3D 渲染）不组合。组合结果是新配置，不是库内现成条目；要长期复用就单独入库、单独实测（例：日系电影感人像的摄影 × 机械仿生人的角色 = 电影感机械人）。

## 大类与次选（2026-10-22 相似度审计重组，先生定）

审计规矩：全库审两遍——第一遍按视觉结果聚类，第二遍拿实测图逐簇复核；**实在太相似**的才归入大类作次选，有独立面孔的一律单列。编号全部保留（日志与提示词按编号引用），大类只是加在上面的一层，不改任何条目的 Style 行与状态。

**抽取规矩（组合抽用）**：顶层单元＝每个大类＋每个独立条目，等概率抽；抽到大类，再在其下次选里等概率随机随到一条。点名选风格时不受此限（可直接点大类里的任一次选）。

| 大类 | 次选成员（编号） | 归类理由（一句） |
|---|---|---|
| 写实系 | #16 3D写实游戏CG、#20 照片级写实、#21 电影感、#22 超写实数字绘画 | 终点都是逼真，媒介之别在成图上常常分不出来 |
| 日系动画系 | #1 日系动漫、#2 赛璐璐、#4 日系水彩、#10 吉卜力风、#11 新海诚风 | 同一动画家族：赛璐璐是其上色法、吉卜力/新海诚是其流派、水彩是其质感变体 |
| 西方古典绘画系 | #29 油画、#30 文艺复兴、#31 巴洛克、#32 前拉斐尔派 | 后三者本就是油画的不同时代面孔 |
| 日本版画系 | #26 浮世绘、#27 新版画 | 新版画是浮世绘的直系后代 |
| 块面3D系 | #18 低多边形、#57 体素 | 都是几何块面建模，方块与三角面之别 |
| 数字厚涂系 | #3 厚涂、#40 游戏原画/概念设定 | 游戏原画的底子就是厚涂数字绘画，设定图形态下难分 |
| 器物材质系（材质型） | #52 青花瓷、#63 景泰蓝、#64 大漆漆画 | 实测同病：只换表面材质、不换人物渲染媒介（见完整版测试日志 #64 挂起记录）；作次选随到，不占独立位 |
| 美式漫画系 | #7 美漫、#9 美式卡通（次选） | GPT 实测未执行 #9 自身描述（输出回落日系动漫，见完整版测试日志 #9 节）；因与 #7 同属美式漫画家族，按归位决定作 #7 的别名次选：**抽中或点到 #9 时用 #7 的固定描述出图**（此别名规则仅限 GPT Image；MJ 侧 #9 用完整版 mj-board 保存的原始描述与成绩）。模型更新后可重测 #9 自身描述 |

未归类＝独立条目（63 条；其中 #12 童话绘本维持拆出、不进抽）：各自有独立面孔，抽取时与大类同级等概率。**全库可抽口径：主表 85 条＋#9 归位次选（按 #7 出图），共 86 个可抽结果；#12 不可抽。**2026-10-22 晚新增 #68–#77 共 10 条（当晚已全部开放型实测可用）暂全列独立；其中 #72 胶片摄影（近写实系）、#75 洛可可（近西方古典绘画系）是否归入大类作次选，待先生拍板。2026-10-23 再新增 #78–#87 共 10 条（铜版蚀刻/水粉/粉彩/年画/琳派/钩织玩偶/折纸/红外摄影/湿版摄影/全息镭射），该批已于当日全部实测完毕：10 条全数可用、并入独立条目（带 △ 者 3 条：#79 水粉、#81 年画、#85 红外，明细见完整版测试日志批次小结）；近邻备查结案：折纸与 #73 纸模（整纸折叠棱面 vs 裁切分层拼贴）、蚀刻与 #53 木刻（凹版细线 vs 凸版粗块）均实测分得开，维持独立，不归次选。复核时**拒绝合并**的近邻（备查）：水墨/工笔（国画两大分支）、剪纸/皮影（红平剪影 vs 透光关节偶）、敦煌/唐卡/埃及壁画（文化身份各自成立）、民俗偶/毛毡偶/黏土/手办（材料质感天差地别）、赛博/蒸汽/原子朋克与蒸汽波（时代符号各异）、印象派/表现主义/立体主义/波普/新艺术（现代流派各自标志性强）。

## 风格表（体验版样本 20 条）

| # | 风格 | 媒介 | 写实度 | 固定风格描述 | GPT Image 状态 |
|---|---|---|---|---|---|
| 1 | 日系动漫 (Anime style) | 2D | 风格化 | Japanese anime style, clean thin lineart, large expressive eyes, simplified anatomy, soft flat coloring with light gradients | 可用（2026-10-21 实测） |
| 2 | 赛璐璐 (Cel shading) | 2D | 风格化 | cel-shaded anime illustration, crisp black outlines, flat color fills, two-tone hard-edged shadows, sharp highlight shapes | 可用（2026-10-21 实测） |
| 6 | Q版 (Chibi) | 2D | 高度风格化 | chibi style, 2.5-head-tall proportions, oversized head, tiny body, cute rounded shapes, simple bold colors | 可用（2026-10-21 实测） |
| 7 | 美漫 (American comic book style) | 2D | 风格化 | American comic book style, bold inked outlines, dynamic anatomy, halftone dot shading, saturated flat colors | 可用（2026-10-21 实测） |
| 12 | 童话绘本 (Fairy tale picture book) | — | — | children's picture book illustration, gouache and colored pencil texture, warm soft palette, gentle storybook charm | 已拆出（2026-10-21 实测不可用，详见文末「已拆出」区） |
| 13 | 扁平矢量 (Flat vector illustration) | 2D | 高度风格化 | flat vector illustration, geometric simplified shapes, no outlines, limited palette, no gradients, clean edges | 可用（2026-10-21 实测） |
| 14 | 像素艺术 (Pixel art) | 2D | 高度风格化 | 16-bit pixel art sprite, limited color palette, crisp visible pixels, no anti-aliasing, retro game character | 可用（2026-10-21 实测） |
| 16 | 3D写实游戏CG (Realistic 3D game CG) | 3D | 写实 | high-end realistic 3D game character render, PBR materials, detailed fabric and metal, cinematic studio lighting | 可用（2026-10-21 实测） |
| 19 | 手办/潮玩 (Collectible figure / designer toy) | 3D | 风格化 | PVC anime figure product photo, glossy painted plastic, small display base, studio lighting | 可用（2026-10-21 实测） |
| 20 | 照片级写实 (Photorealistic) | 摄影 | 写实 | photorealistic photograph, real human, natural skin texture, 85mm lens, softbox studio lighting, sharp focus | 可用（2026-10-21 实测） |
| 23 | 水墨 (Chinese ink wash painting) | 传统手绘 | 风格化 | traditional Chinese ink wash painting, expressive black ink brushwork, varying ink tones, generous empty space, rice paper texture | 可用（2026-10-21 实测） |
| 24 | 工笔 (Gongbi) | 传统手绘 | 半写实 | Chinese gongbi painting, fine meticulous ink outlines, layered mineral colors, flat decorative rendering, silk texture | 可用（2026-10-21 实测） |
| 25 | 敦煌壁画 (Dunhuang mural) | 传统手绘 | 风格化 | Dunhuang cave mural style, flowing ribbons, mineral pigments of ochre malachite and lapis, weathered plaster texture | 可用（2026-10-21 实测） |
| 26 | 浮世绘 (Ukiyo-e) | 传统版画 | 风格化 | Japanese ukiyo-e woodblock print, bold contour lines, flat color areas, Prussian blue accents, washi paper grain | 可用（2026-10-21 实测） |
| 38 | 蒸汽朋克 (Steampunk) | 题材风格 | 半写实 | steampunk aesthetic, Victorian clothing, brass gears and leather, warm sepia palette | 可用（2026-10-21 实测） |
| 52 | 青花瓷 (Blue-and-white porcelain) | 传统手绘 | 风格化 | blue-and-white porcelain painting, cobalt blue on glossy white ceramic glaze, hand-painted brush shading, fine crackle texture, ceramic sheen | 可用（2026-10-21 实测） |
| 53 | 木刻版画 (Woodcut print) | 传统手绘 | 高度风格化 | woodcut print, bold black-and-white carved blocks, visible knife-cut hatching, high-contrast ink texture, rough woodgrain edges | 可用（2026-10-22 实测） |
| 69 | 装饰艺术 (Art Deco) | 西方绘画 | 风格化 | Art Deco illustration, bold geometric symmetry, gold and black palette, sunburst and chevron motifs, elegant streamlined figures | 可用（2026-10-22 实测） |
| 73 | 纸模 (Papercraft) | 手工 | 风格化 | layered papercraft sculpture, folded and cut paper construction, visible paper edges and layered depth, soft shadows between layers, handmade paper diorama look | 可用（2026-10-22 实测） |
| 76 | 孔版印刷 (Risograph) | 印刷 | 高度风格化 | risograph print, fluorescent spot colors, grainy overprint texture, slight ink misregistration, matte paper zine aesthetic | 可用（2026-10-22 实测） |

## 其余 67 条索引（完整版含全部 Style 行与三平台实测成绩）

以下条目在完整版中均有完整行（固定风格描述＋GPT 状态）及 MJ / Imagine 逐条成绩；体验版仅列编号与中文名，供了解库的覆盖面。

| # | 风格 | # | 风格 | # | 风格 |
|---|---|---|---|---|---|
| 3 | 厚涂 | 4 | 日系水彩 | 5 | 韩系插画 |
| 8 | 日漫黑白 | 9 | 美式卡通 | 10 | 吉卜力风 |
| 11 | 新海诚风 | 15 | 3D卡通渲染 | 17 | 黏土风 |
| 18 | 低多边形 | 21 | 电影感 | 22 | 超写实数字绘画 |
| 27 | 新版画 | 28 | 印度细密画 | 29 | 油画 |
| 30 | 文艺复兴 | 31 | 巴洛克 | 32 | 前拉斐尔派 |
| 33 | 新艺术运动 | 34 | 印象派 | 35 | 表现主义 |
| 36 | 波普艺术 | 37 | 赛博朋克 | 39 | 暗黑奇幻 |
| 40 | 游戏原画/概念设定 | 41 | 哥特 | 42 | 铅笔素描 |
| 43 | 民俗偶 | 44 | 毛毡偶 | 45 | 机械仿生人 |
| 46 | 扁平时尚插画 | 47 | 克苏鲁怪诞 | 48 | 剪纸 |
| 49 | 皮影 | 50 | 刺绣 | 51 | 彩窗玻璃 |
| 54 | 埃及壁画 | 55 | 立体主义 | 56 | 蒸汽波 |
| 57 | 体素 | 58 | 唐卡 | 59 | 马赛克 |
| 60 | 故障艺术 | 61 | 原子朋克 | 62 | 蜡染 |
| 63 | 景泰蓝 | 64 | 大漆漆画 | 65 | 蓝晒法 |
| 66 | X光透视 | 67 | 石雕像 | 68 | 超现实主义 |
| 70 | 清晰线条 | 71 | 太阳朋克 | 72 | 胶片摄影 |
| 74 | 生物机械 | 75 | 洛可可 | 77 | 积木玩具 |
| 78 | 铜版蚀刻 | 79 | 水粉 | 80 | 粉彩 |
| 81 | 年画 | 82 | 琳派 | 83 | 钩织玩偶 |
| 84 | 折纸 | 85 | 红外摄影 | 86 | 湿版摄影 |
| 87 | 全息镭射 |  |  |  |  |

## 测试方法
测试主体、提示词、判定与回填规则见 `style-test-kit.md`；每种风格出 1 张定结论（标准型双视图，或开放型双视图），只记录风格是否到位。测完把状态改为「可用」，不可用的拆到下面「已拆出」区。

## 已拆出：不适合 GPT 的风格

测出「不可用」的风格移到这里保管，不删除；模型版本更新后可重测，测过移回主表。

| 原编号 | 风格 | 拆出日期 | 原因 |
|---|---|---|---|
| 12 | 童话绘本 (Fairy tale picture book) | 2026-10-21 | 绘本体未成立：仅水粉/彩铅颗粒质感落地，人物仍是成熟动漫脸＋写实比例，整体像动漫设定图加颗粒滤镜（锚点全过，纯风格没对） |

注：#9 美式卡通原在此列，2026-10-22 晚经先生定甲案正式归位「美式漫画系」次选（见上方大类节），已移出本区；其 GPT 不执行自身描述的实测记录保留在完整版测试日志 #9 节。
