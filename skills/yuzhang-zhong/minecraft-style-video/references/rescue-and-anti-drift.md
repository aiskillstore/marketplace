# Rescue and Anti-Drift Guide / 翻车诊断与防串味救场指南

When an AI video clip ruins the Minecraft aesthetic, the cause is almost always one of eight predictable failure modes. Use the diagnostic table and patches below to fix the prompt or workflow in one iteration.

## 1. Quick Diagnostic Matrix / 八大翻车症状速查表

| Issue Code | Symptom / 翻车表现 | Root Cause / 根本原因 | Immediate Fix / 核心修复手段 |
| --- | --- | --- | --- |
| `human-fingers` | 小人握剑/握镐时手臂末端长出五根真人手指 | 模型将 "holding a pickaxe/sword" 默认映射为真人手握持 | 强制声明 `flat 4x4 square pixel-block hand ends, fingerless and clawless rectangular prism arms`，负向排除 `five fingers, human hands` |
| `blurry-texels` | 方块与衣服上的 `16×16` 像素格被涂抹成模糊渐变或光滑泥塑 | 未声明邻近采样像素网格，模型启用了平滑纹理先验 | 正向锁定 `crisp unfiltered 16x16 nearest-neighbor pixel-art textures, sharp pixel grid edges, zero bilinear blur` |
| `roblox-lego-drift` | 脑袋变成 Roblox 圆桶圆柱头，或长出乐高圆凸粒与 C 型夹爪手 | 模型混淆了 Minecraft、Roblox 与 Lego 三种积木画风 | 正向声明 `sharp 90-degree 1:1:1 cubic 8x8x8 Minecraft head, studless flat top`，负向排除 `Roblox cylindrical barrel head, Lego top studs, Lego C-shaped claws` |
| `smooth-tools` | 钻石镐、钻石剑或火把变成了圆滑金属棍与写实刀刃 | 未说明 Minecraft 道具是 `16×16×1` 像素图挤出模型 | 正向声明 `extruded 16x16x1 pixel-art tool with stepped 90-degree staircase voxel edges`，负向排除 `smooth cylindrical rod, realistic curved metal blade` |
| `face-morph` | 做表情或说话时，`8×8` 平面脸凸起长出真人鼻梁、嘴唇或圆眼球 | 情绪词触发了 3D 真人面部网格形变 | 正向锁定 `flat 8x8 pixel-grid face with 2x1 sliding pixel eyes and floating 2x1 pixel brows, zero 3D nose protrusion` |
| `noodle-limbs` | 跑步或挥镐时，`4×12×4` 方柱手臂像面条一样弯曲成弧线 | 视频模型默认使用连续软体骨骼形变 | 声明 `rigid 4x12x4 rectangular prism limbs with mechanical shoulder/hip pivots and clean 90-degree blocky bends, no rubbery bending` |
| `outfit-drift` | 切镜头后皮肤外层发型、盔甲或方块纹理变样 | 直接使用纯文生视频 (T2V)，缺少像素网格锚点 | 切换为 **首帧 I2V 工作流**：先用角色三视图与方块设定卡固定首帧图片，再送入视频模型 |
| `overload` | 5秒内同时挖矿、转身、拔剑、砍怪导致穿模卡死 | 单条提示词塞入了 3 个以上连续动词 | 遵循 **单镜头单动作铁律**：将多步动作拆分为独立的 3.5 秒分镜，每镜仅保留 1 个核心动作 |

## 2. Before & After Prompt Rescue Examples / 救场前后对比实例

### Case A: Fixing Human Fingers & Smooth Sword (`human-fingers` + `smooth-tools`)

- **Broken Prompt (翻车原词)**:
  `A cute Minecraft character holding a glowing diamond sword in his hand and smiling at the camera.`
- **Why it fails**: "in his hand", "glowing diamond sword", and "smiling" cause the model to generate five human fingers gripping a smooth cylindrical fantasy sword and a 3D human nose.
- **Rescued Prompt (救场修复词)**:
  `An authentic Minecraft voxel character with a sharp 90-degree 8x8x8 cubic head, +0.5px raised 3D outer hair layer, 8x12x4 rectangular prism torso, and fingerless flat 4x4 square pixel-block hand ends. The right 4x12x4 blocky arm holds an extruded 16x16x1 pixel-art diamond sword with stepped 90-degree cyan voxel blade edges at a 45-degree angle. Flat 8x8 pixel face with 2x1 pixel eyes, crisp nearest-neighbor 16x16 pixel textures, BSL shader sunlight, no human fingers, no smooth metal blade, no 3D human nose.`

### Case B: Fixing Roblox/Lego Drift & Blurry Blocks (`roblox-lego-drift` + `blurry-texels`)

- **Broken Prompt (翻车原词)**:
  `A blocky toy character placing a grass block on the ground.`
- **Why it fails**: "blocky toy character" triggers Roblox barrel heads or Lego studs with smooth plastic surfaces.
- **Rescued Prompt (救场修复词)**:
  `A canonical Minecraft Alex voxel builder (sharp 8x8x8 cubic head, slim 3x12x4 rectangular prism arms with flat 3x4 square ends) pivots her shoulder hinge to place a 16x16x16 Minecraft grass block onto an oak plank floor. The grass block displays crisp unfiltered 16x16 nearest-neighbor green top texels, stepped pixel grass side overhang, and brown dirt pixels. Zero bilinear blur, no Roblox cylindrical head, no Lego studs or C-shaped claws.`

### Case C: Fixing Action Overload (`overload`)

- **Broken Prompt (翻车原词)**:
  `Steve mines the diamond ore, picks up the diamond, turns around, sees a Creeper, and runs away before it explodes.`
- **Rescued Split (拆分为高完成度独立镜头)**:
  - **Shot A (3.5s)**: `Medium close-up. Minecraft Steve swings his extruded 16x16x1 pixel-art diamond pickaxe into a glowing 16x16x16 cyan diamond ore block; the block shatters into square pixel particles, revealing a green armless Minecraft Creeper standing directly behind it.`
  - **Shot B (3.5s)**: `Medium two-shot with subtle camera shake. The green Minecraft Creeper flashes bright white and swells in boxy scale while Steve's 8x8 pixel eyes widen into hollow squares and his rigid 4x12x4 arms pivot upward in panic.`
