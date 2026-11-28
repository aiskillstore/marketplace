# Rescue and Anti-Drift Guide / 翻车诊断与防串味救场指南

When an AI video clip ruins the Roblox aesthetic, the cause is almost always one of eight predictable failure modes. Use the diagnostic table and patches below to fix the prompt or workflow in one iteration.

## 1. Quick Diagnostic Matrix / 八大翻车症状速查表

| Issue Code | Symptom / 翻车表现 | Root Cause / 根本原因 | Immediate Fix / 核心修复手段 |
| --- | --- | --- | --- |
| `human-fingers` | 小人手臂末端长出人类五指或关节纹 | 模型将 "hands" 默认映射为真人手部 | 强制替换 `hands` 为 `fingerless and clawless solid 1x2x1 beveled rectangular block hands`，负向排除 `five fingers, human hands` |
| `lego-studs` | 头顶或地面长出乐高圆颗粒，或手部变成乐高C型钩爪 | 误用了 "C-shaped claw hands"、"studded floor" 或 "brick toy" 触发乐高先验 | **严禁使用乐高C型爪与地面凸点！** 正向声明 `solid 1x2x1 rectangular block arms, smooth studless barrel-beveled Roblox head, flat SmoothPlastic / WoodPlanks floor (zero raised circular Lego studs)`，负向排除 `Lego top studs, raised circular floor studs, Lego C-shaped claw hands` |
| `minecraft-voxels` | 头部与身体变成直角锋利方块且带像素马赛克贴图 | 模型混淆了 Roblox 与 Minecraft | 正向声明 `classic Roblox 1:1 barrel-cylinder head with deep curved top/bottom bevels, SmoothPlastic shader`，负向排除 `Minecraft voxel, pixel art` |
| `limb-gap` | 双腿之间有明显空隙、穿了分体运动鞋，不像 Roblox 方腿 | 未声明 Roblox 标志性的 `2×2×1` 躯干与并拢 `1×2×1` 双腿比例 | 正向声明 `canonical Roblox 2x2x1 rectangular torso with two 1x2x1 rectangular leg blocks sitting flush side-by-side matching exact torso width` |
| `face-morph` | 说话或做表情时五官凸起长出真人鼻子与牙齿 | 动态幅度过大触发真人面部骨骼先验 | 正向锁定 `flat 2D screen-printed decal face, painted ink eyes and mouth, zero 3D nose`，调低运动幅度 |
| `noodle-limbs` | 走路或挥手时手臂像橡胶面条一样弯曲 | 视频模型默认使用软体连续骨骼形变 | 声明 `rigid Motor6D mechanical hinge joints at shoulders and hips only, stiff 1x2x1 rectangular limbs, no rubbery bending` |
| `outfit-drift` | 切镜头后衣服颜色、帽子或发型变了 | 直接使用 T2V 文生视频，缺少视觉锚点 | 切换为 **首帧 I2V 工作流**：先用三视图固定角色参考，生成每个镜头的首帧图再转视频 |
| `overload` | 5秒内动作混乱、穿模或后半段静止卡死 | 单条提示词塞入了 3 个以上连续动词 | 遵循 **单镜头单动作铁律**：将 `走过去->坐下->喝咖啡->哭泣` 拆分为 3 个独立 3.5 秒分镜 |

## 2. Before & After Prompt Rescue Examples / 救场前后对比实例

### Case A: Fixing Humanization & Finger Growth (`human-fingers` + `face-morph`)

- **Broken Prompt (翻车原词)**:
  `A cute Roblox girl holding an iced coffee cup with both hands and smiling happily at the camera.`
- **Why it fails**: "girl", "both hands", and "smiling" trigger human finger generation and 3D human cheek/lip deformation.
- **Rescued Prompt (救场修复词)**:
  `A 3D SmoothPlastic Roblox-style chibi blocky figure with a smooth studless 1:1 barrel-beveled head and flat 2D screen-printed decal face showing starry eyes and a painted curved smile. Its fingerless and clawless solid 1x2x1 beveled rectangular block hands hold the sides of a miniature translucent iced coffee cup with a dome lid and straw. Rigid rectangular arms pivot slightly upward at the shoulder hinges. Soft studio lighting, zero human fingers, zero Lego C-claws, no 3D human nose.`

### Case B: Fixing Action Overload (`overload`)

- **Broken Prompt (翻车原词)**:
  `The Roblox worker walks into the office, sits at the desk, opens the laptop, and slams his head on the keyboard in despair.`
- **Why it fails**: Four distinct actions inside a single 5-second clip cause limb merging and desk clipping.
- **Rescued Split (拆分为两个高完成度镜头)**:
  - **Shot A (3.5s)**: `Medium shot. A blocky Roblox office worker already seated at a miniature desk pivots its rigid rectangular arms to flip open a glowing blocky laptop; its 2D decal face freezes in a wide-eyed shocked expression.`
  - **Shot B (3.5s)**: `Close-up high-angle shot. The blocky worker tilts its rigid rectangular torso forward 90 degrees at the waist hinge, slamming its smooth cylindrical yellow head flat onto the miniature plastic keyboard with a slight bounce.`

### Case C: Fixing Lego & Minecraft Contamination (`lego-studs` + `minecraft-voxels`)

- **Broken Prompt (翻车原词)**:
  `A blocky plastic toy character jumping across floating blocks in the sky.`
### Case D: Non-Human Blocky Companions & Rigid Prop Docking (`Pet & Prop Topology Lock`)

- **Blocky Pet / Creature Rule**: When adding pets, dragons, dogs, or monsters, lock `chamfered Roblox SmoothPlastic + Neon geometric primitives, flat 2D dot eyes, stubby clawless rectangular block paws, rigid hinged wing/tail plates (zero reptile scales, zero sharp claws/talons, zero realistic fur or leathery bat wings)`. Use `node scripts/avatar_spec.mjs --companion neon-dragon` to generate a ready-to-use Pet DNA block.
- **Handheld Prop Docking Rule**: Blocky `1x2x1` arms have no fingers or claws, so never write `pinches`, `wraps fingers`, or `holds between thumb and index`. Always state that the prop (`kettle`, `ramen cup`, `Bloxy Cola`, `Linked Sword`, `flashlight`, `overhead subway strap`) is **docked / welded / parented flush against the flat bottom or front face of the solid `1x2x1` rectangular block hand**.

### Case E: Upgrading Static Labels into Readable Acting (`Gates 9 & 10`)

- **`missing-acting` (Gate 9 · Performance & Interaction Completeness)**: Even when Gates 1–8 (`geometryStatus: PASS`) hold, a shot falls flat if it only states a static role/prop label (`"A witch holding two potions"`). Always specify:
  1. `beatIntent` & single `audienceRead` (the joke readable without dialogue);
  2. `performance.gazeTarget` (`pupils tracking ...`) + `reactionCause` + `eyebrows`;
  3. `interaction` (`hand`, `propId`, controlled `intent` in `hold|present|tap|slam|point|drop|receive`, and `visibility: "camera-facing"`).
- **`poor-readability` (Gate 10 · Thumbnail & Safe-Zone Readability)**: Keep actor silhouettes separated (`|dx| >= 0.28` or depth-staggered), never park a standing actor in front of `gazeTarget`, keep `chatEn` to `<= 4` words, and pass `--assets-dir <dir>` to verify `64×64` thumbnail/avatar contrast. See [`examples/subway-acting-versus-baseline/`](../examples/subway-acting-versus-baseline/) for a controlled single-variable comparison.

