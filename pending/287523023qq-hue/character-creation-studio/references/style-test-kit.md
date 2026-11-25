# 风格测试包（GPT Image 实测用）

本文件是给 style-library 里标「未测试」的风格定状态的工具：固定提示词结构、固定判定标准，每种风格只换 Style 一行，测完回填 style-library 的状态列。测试默认**双视图**（正面＋四分之三）；亦可走**开放型**：只锁 Style 行、主体按 subject-draw 的随机规矩交给模型，画布**默认仍用双视图**（同一主体两视角，验风格一致性）；仅主体与风格强绑定、单体即足定论时可用单图（如 #47 克苏鲁怪诞，属特例）。判定都只看风格。三视图与头部转面是角色生产（锁定派生）阶段的资产，不用于测风格（2026-10-21 先生定）。

**现行规矩（2026-10-21 晚先生改定）：只测风格，不绑角色。** 测试只判一件事——GPT 能不能把这种风格画到位。判定只有两档：可用 / 不可用（拆出）。角色锚点保不保得住，不属于风格测试；真要拿某风格做锁定角色时，在实际使用中按 acceptance-checklist 验收。

此前（2026-10-21 白天）曾用固定测试角色 Lin Che 连锚点一起测，45 种的成绩记在完整版测试日志（style-test-log）；其中 23 条「需加强描述」（风格已到位、仅锚点不过）已按新规矩全部转「可用」，原补强句作废，锚点成绩保留在完整版日志作历史参考。

## 1. 测试主体与提示词（全程统一）

主体只定"一个年轻女性角色"，不定长相、不定服装——服装与整体形象由 Style 行决定，这样测的才是风格本身。

```
[SUBJECT — 所有风格共用]
A young East Asian woman, full body, two views of the same character side by side on one canvas: front view and three-quarter view, same scale, standing relaxed, arms slightly away from body, even soft studio lighting, plain light gray seamless background, no text.

[STYLE]
Style: <从 style-library 复制目标风格的固定描述>

[CONSTRAINTS]
no text, no watermark
```

例外：Style 行自带背景设定的，构图句的背景改为 simple plain background，让风格的背景处理显出来。

**开放型模板**（只锁风格、主体随机；用户指定时，或风格与主体强绑定时用）：主体不写死，框架与标准型同为双视图，另加默认隔离句（用户点名延续上一版时去掉）：

```
Create a completely new character unrelated to any previous image in this conversation; do not reuse earlier faces, hairstyles, outfits or props.
The character may be human or any other species — creature, android, spirit, plant, machine, or something never seen before; choose freely.
A single original character, full body, two views of the same character side by side on one canvas: front view and three-quarter view, same scale, standing relaxed, even soft studio lighting, plain light gray seamless background, no text.

Style: <从 style-library 复制目标风格的固定描述>

no text, no watermark
```

收图约定（2026-10-21 先生定）：先生只发图、不标注风格名；Muse 自行对照 style-library 辨认对应编号与 Style 行再审；认不准时先说候选、勿硬判。**输入核验（2026-10-23 外审补）**：辨认只用于定位，定论前必须拿本批**实际送测清单**核对——认出的风格若不在送测清单内，说明模型把送测风格回落/串成了别的风格，按送测的那条判（通常记没执行），不许改按认出的风格记成功。

## 2. 测试流程（每种风格一轮）

1. 每种风格只出 **1 张**定结论（一图定生死）：标准型用统一主体模板、只换 Style 行；开放型用开放模板（主体随机、带隔离句），同一批内框架不变。
2. 按第 3 节判定，当场定结论。
3. 回填：可用留在 style-library 主表更新状态；不可用的**拆出主表**，移入 style-library 文末「已拆出：不适合 GPT 的风格」区，注明日期与原因。记录出图模型版本；记录里涉及单侧特征时一律双写（角色侧＋画面侧），与锁定记录同一口径，不许只记画面左右。另注意：GPT 在同一对话内会被既往出图污染（2026-10-21 已验证：#49/#54 在旧对话里主体雷同旧测试角色、提示词并无锚点；换新对话测 #50/#57，主体完全不同）——污染源是**固定锚点角色在同一对话反复出图**：用固定角色测，角色测完或换角色就开新对话；**开放型随机主体不积累固定模板，同一对话连续抽不用换**（2026-10-22 先生定）。发现主体雷同时，先分清是不是固定角色攒的污染，再决定要不要重跑。

## 3. 判定标准（只看风格）

- **判定对象**永远是实际送测的那条 Style 行，不是审查者从成图认出的风格（见收图约定「输入核验」）。
- **风格到位**：渲染方式、线条、材质、色调与 Style 行一致，不是"有点像"；两个视角风格一致。
- **画面成立**：主体完整、没有大面积崩坏（五官肢体糊成一团、结构散架）；崩坏到看不出风格的，按风格没立住算。
- 不看脸像不像、痣在不在、服装道具合不合某个角色——那是角色验收，不是风格测试。

## 4. 状态判定

- **可用**：风格到位、画面成立。
- **不可用**：风格没对（不到位，或回落成别的风格）→ 拆出主表。不可用不是删除；模型版本更新后可重测，测过可移回。

## 5. 记录格式（测完贴回 style-library 状态列或测试日志）

```
风格 #N <名称>｜日期｜模型版本｜结论：可用/不可用
成绩：风格哪几项对上了 / 没对上
```

## 6. 批量节奏

风格一次测不完，按用途优先级分批；每批测完立即回填状态列，不攒着——没回填的测试等于没测。

## 历史约定（仅用于解读 2026-10-21 前的锚点测试记录）

- 旧测试角色：Lin Che（24 岁东亚女性，高马尾＋齐刘海、左眼下痣、白内衬/黑劲装盘扣/深灰腰带/黑裤布鞋四层、左腰佩深色木鞘长剑、菱格纹缠柄），锚点逐字文本见完整版测试日志与提示词文件。
- 痣的核对（旧协议）：锚点 "a small mole below the left eye" 以画面左侧（角色右颊）为标准落点；颗数不对或落在画面右记脸不过。旧日志里的"双痣""落点反"均按此判。
- 鞋的核对（旧协议）：实物/写实类里布鞋被画成浅色模制大底、形似运动鞋/皮鞋的，属风格化呈现，不判服装错（#19–#22 据此判可用）。
- 旧协议的补强句（已作废）：记在各条旧日志里，仅作历史，不再执行补强重测。

## 平台分支：Midjourney（2026-10-22 新增）

MJ 测试不走本包的 GPT 提示词，改走 `mj-board.md` 的 MJ 框架与适配规矩；与本包共用的是检查维度（只判风格、Style 行逐词核，另记网格成立数）。结论分级平台专用：GPT 二档（可用／不可用），MJ 三档（可驾驭／部分驾驭／驾驭不了），两边**不互相映射、不回填对方状态列**；MJ 的「部分驾驭」＝可选用但有明确弱点，选用时按 mj-board 成绩表注明的弱点避让。GPT 与 MJ 的成绩分开记：GPT 成绩记在测试日志（完整版附带）与风格库状态列，MJ 成绩记在 mj-board.md 的成绩表（完整版）。
