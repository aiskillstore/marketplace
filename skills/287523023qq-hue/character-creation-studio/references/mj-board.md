# Midjourney 板块（MJ 平台分支）

> **开源体验版说明**：本文件保留板块定位、测试框架、判定标准、主体锚定修法与通用规律等方法论内容；逐条成绩表仅收录 4 条样例行，各批「适配提示词」清单（Style 行汇编）与完整 55 条成绩表在完整版中。

本包双平台起于 GPT Image＋Midjourney：GPT Image 用主流程提示词，Midjourney 用本板块的改写框架。**判定共用检查维度**（只判风格、Style 行逐词核，见 `style-test-kit.md`），变的只是提示词语法；结论分级平台专用：MJ 三档（可驾驭／部分驾驭／驾驭不了），不映射 GPT 的二档状态、不回填风格库状态列。

## 为什么要另开板块

MJ 是关键词引擎，不解析 GPT 那种整句指令：隔离句、物种许可句、"no text"式祈使句对它无效或有害。所以同一条风格在 MJ 上要翻成"名词短语堆叠＋参数"。

## 定风格随机版框架（MJ）

```
character design sheet, one original character, full body, front view and three-quarter view side by side on one sheet, plain light gray background, <Style 行原文> --ar 3:2
```

- Style 行**原文照抄**风格库，不改写、不增减——两个平台测的是同一条风格。**#9 例外**：风格库里「#9 抽到按 #7 出图」是 GPT Image 专用别名规则；MJ 侧 #9 固定用原始美式卡通描述（保存于完整版 mj-board），两边不要串。
- 主体随机靠 MJ 自身：不写死主体细节，只给 "one original character"；克苏鲁等题材风格把 character 换成 creature。
- 风格自带底色时（如蓝晒、X 光、马赛克金底），删掉框架里的 "plain light gray background"，让 Style 行的底色说了算。
- 无隔离句概念：MJ 每次生成互相独立，不存在同会话污染，不用开新会话防污染。
- 判定补充：MJ 一次出 4 张网格——逐词核对整格，记"几张成立"（4/4 与 1/4 是两个分数，分开记）。
- 交付方式：MJ 每条固定出四宫格、数量改不了；每条挑风格最成立的一张放大成单图交付与展示，四宫格原图留档供判定成立数。

各批适配提示词就是「上框架＋逐条 Style 行原文」的清单，无额外改写，完整清单见完整版。

## MJ 成绩表（样例 4 条）

完整版含 55 条实测全表；**全账汇总：实测 55 条——可驾驭 52、部分驾驭 3、驾驭不了 0；另 32 条未测（非失败，提示词留档可续）**。

| # | 风格 | 网格核对（Style 行逐词） | 双视图格式 | 定论 |
|---|---|---|---|---|
| 1 | 日系动漫 | 细线条 ✓、大眼 ✓、平涂 ✓，带色板与多角度特写 | 4/4（专业设定图） | **可驾驭（满分级，MJ 主场）** |
| 13 | 扁平矢量 | 几何简化形状 ✓、无描边 ✓、有限配色 ✓、无渐变 ✓、边缘干净 ✓ | 4/4 | **可驾驭（满分级）** |
| 52 | 青花瓷 | 钴蓝釉下彩 ✓（4/4）、冰裂纹 ✓、陶瓷光泽 △（呈衣物纹样，与 GPT 同病） | 4/4（全是三视图设定图） | **可驾驭**（材质型通病在，但格式满分） |
| 53 | 木刻版画 | 刀刻排线 ✓（最佳格）、高对比 ✓；其余格漂移成漫画页/海报 | 0/4 | **部分驾驭**（风格只在最佳格成立，MJ 引力往日式漫画/海报拉） |

## 主体锚定修法（对「风格词吞角色」类条目的抢救实验，已实测验证）

病根：风格词在 MJ 语料里强绑定非角色题材时（如 batik＝布料产品图、ink wash＝山水画），风格词成了主体、角色被吞。修法：提示词里先把角色钉死（角色由该材料构成／角色为画面大幅主体），风格词降为角色的属性；自带场景引力的风格另加 `--no` 摁住题材词。

- 水墨锚定版示例（#23 在体验版风格库样本内，Style 行可查）：
  `character design sheet, one original character as the large main subject filling the frame, full body, front view and three-quarter view side by side on one sheet, traditional Chinese ink wash painting, expressive black ink brushwork, varying ink tones, generous empty space, rice paper texture --ar 3:2 --no landscape, mountains, trees, scenery`
- 蜡染锚定版同理：主体句改为 "one original character made entirely of batik cloth, humanoid figure with a cloth-patterned body"，后接蜡染 Style 行（完整版）与同一框架。

**抢救结果**：两例均救回——锚定后角色回到画面主体、风格逐词成立（蜡染的代价是角色呈无脸布形，测风格无碍，做正式角色时要另加面部要求）。结论：凡风格词在 MJ 里强绑定非角色题材的条目，MJ 版提示词一律先上主体锚定再附 Style 行。

## 通用规律（五批实测汇总提炼）

1. MJ 的风格还原力与 GPT 同级；动漫、CG、怪物设计类是强项。西式卡通与绘本类语料，MJ 明显比 GPT 厚——GPT 侧翻车甚至拆出的条目，MJ 侧有接住的实例。
2. **双视图格式跟风格的「题材引力」走**：服装/角色设计类格式满分；媒介/画种类媒介全中但构图容易海报化；插画/影片类引力会把设定图带成场景图——但风格本体仍可成立、人物不被吞，与「主体消失」（见主体锚定修法）是两回事。
3. 部分驾驭的典型病灶是「题材对、技法媒介没到位」：落成相近题材的现代插画，而不是所测风格本身。
4. 风格本身的还原度与 GPT 同级，但「设定图双视图」格式在 MJ 命中率不稳；测试阶段只判风格不受影响，角色生产阶段要另想办法（单图出图或参考图锁定）。
