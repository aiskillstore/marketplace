# Model Prompt Playbook / 多模型图生视频与文生视频手册

Different AI video engines interpret voxel edges, pixel-art textures, and rigid block motion differently. A prompt that lacks nearest-neighbor texture locks will cause video models to blur `16×16` pixel blocks into smooth clay or add human fingers when holding a pickaxe. Use this playbook to format prompts for the user's chosen engine.

## 1. Universal Golden Rule: First-Frame I2V Protects Pixel Grids

For multi-shot Minecraft shorts (both character skits and isometric block builds), **First-Frame Image-to-Video (首帧图生视频 I2V)** is the primary production path:

1. Generate the **3-View Character Turnaround & Voxel Object Sheet** first (`scripts/voxel_spec.mjs`).
2. Generate each shot's **First-Frame Static Keyframe** using an image model that preserves sharp pixel grids (`Midjourney --cref`, `Flux`, `Jimeng 即梦角色/构图参考`, or `GPT-4o Image`).
3. Feed the pixel-locked static keyframe into the video engine with a **single-action motion + rigid voxel constraint prompt**. Because the first frame already establishes the `8×8` pixel face, `+0.5px` 3D hair layer, and `16×16×1` stepped pickaxe, the video model focuses on clean hinge motion and cubic particle effects instead of blurring textures.

## 2. Engine-Specific Syntax & Settings / 六大主流模型参数与语法

| Engine | Best Mode | Clip Length | Camera Control Syntax | Recommended Settings |
| --- | --- | --- | --- | --- |
| **Kling (可灵 1.6 / 2.0)** | I2V (High Quality / Master) | 5s | Natural language (`Camera slowly pushes in`, `镜头快速推近并轻微震动`) or Camera Sliders | Creativity `0.35–0.45` (keep low to preserve `16×16` pixel grid), Negative prompt enabled |
| **Seedance / Jimeng (即梦视频)** | I2V / 首尾帧控制 | 4s–5s | Direct Chinese rhythm & camera phrases (`45度等距微缩俯拍`, `镜头特写快速推近`) | Lock first frame (and end frame for block-build loops); emphasize `清晰16x16像素贴图` |
| **Hailuo MiniMax (海螺 I2V-01-Director)** | I2V-01-Director | 6s | Bracketed English commands: `[Push in]`, `[Pull out]`, `[Pan left]`, `[Tilt up]`, `[Shake]`, `[Static shot]` | Place `[Camera Command]` at the opening of the prompt; specify `stepped voxel edges` |
| **Wan 2.1 / Wan 2.6 (通义万相)** | I2V / T2V (14B) | 5s | Explicit lens + shader + voxel sentence (`9:16 vertical, Minecraft BSL shader, crisp 16x16 pixel blocks`) | CFG `5.5–6.5`, strong negative prompt required to block human hands and Roblox cylinders |
| **Sora** | I2V / Storyboard | 5s–10s | Physical voxel description (`Macro 50mm isometric lens, rigid cubic voxel physics`) | Explicitly state `unfiltered nearest-neighbor 16x16 pixel textures` and `cubic particle burst` |
| **Runway Gen-3 / Gen-4** | I2V | 5s | `Camera: ... Subject: ... Action: ...` structured prompt | Keep camera speed moderate so `16×16` pixel grids do not smear into motion blur |

## 3. Prompt Assembly Formula by Engine / 各模型提示词拼装公式

### Kling (可灵) Formula

- **Structure**: `[像素比例与外层皮肤锁定] + [单一刚体动作与方块交互] + [像素表情与立方体粒子物理] + [运镜与防糊化尾缀]`
- **Example (Chinese)**:
  `画面中的Minecraft我的世界标准像素方块小人（1:1:1锋利直角8x8x8像素立方体头、0.5px悬浮3D立体刘海层、8x12x4长方体躯干、4x12x4平头正方形截面手臂），右侧刚性方柱手臂沿肩部转轴有力挥落手中的16x16x1锯齿像素钻石镐，敲碎前方的发光青色16x16x16钻石矿石方块，迸发出数颗正方形像素碎屑与旋转的微型像素钻石掉落物。镜头快速推近并伴随敲击瞬间轻微震动，BSL光影火把暖光，保持清晰16x16邻近像素网格，严禁出现人类五指、贴图模糊或Roblox圆桶头。`

### Seedance / Jimeng (即梦) Formula

- **Structure**: `[MC光影画风与16x16像素锁定] + [机位视角] + [干脆利落的方块拼搭/挥动动作] + [立方体光影反馈]`
- **Example (Chinese)**:
  `Minecraft BSL体积光影画风，清晰无模糊的16x16像素贴图，45度等距微缩模型俯拍镜头轻柔推近。穿森系围裙的Alex像素小人（3x12x4细手臂、平头方形手截面）将一盏16x16像素发光火把干脆地安插在橡木工作台方块上，金黄色方块暖光瞬间照亮周围的草方块与粉色美西螈，动作干脆有定格积木感。`

### Hailuo MiniMax (海螺 Director) Formula

- **Structure**: `[Bracketed Camera Tag] + [Voxel Character & Block Lock] + [Single Hinged Action] + [Nearest-Neighbor Shader Tail]`
- **Example (English)**:
  `[Push in, Shake] An authentic Minecraft voxel character with a sharp 8x8x8 cubic head, raised 0.5px 3D hair layer, 8x12x4 torso, and flat 4x4 square hand ends holding a stepped 16x16x1 pixel-art diamond pickaxe. Behind the miner, a green armless quadrupedal Minecraft Creeper mob flashes bright white and swells in boxy scale. Crisp nearest-neighbor 16x16 pixel textures, BSL shader cave torchlight, rigid shoulder hinges, no human fingers, no blurry textures.`

### Wan 2.1 / 2.6 (通义万相) Formula

- **Structure**: `Positive Prompt (Shader + Voxel Proportions + Block Action + Camera)` + `Explicit Negative Prompt`
- **Positive Example**:
  `9:16竖屏，Minecraft官方宣传片Bare Bones配BSL光影画风，8x8x8直角立方体像素头，Fresh Animations可动2x1像素眼睛，4x12x4平头方柱四肢，清晰16x16像素贴图。小人将一块印有TNT字样的红白16x16x16像素炸药块啪地拍在石砖地面上，TNT方块开始白光闪烁膨胀，镜头中近景快速拉远，高对比度像素光影。`
- **Negative Example**:
  `人类手指，五指手掌，真实人类皮肤，3D高鼻梁，Roblox圆柱桶状头，乐高头顶圆颗粒，乐高C型夹爪手，圆滑金属镐子，贴图模糊涂抹，面条状弯曲四肢，画面糊化`

### Sora & Runway Formula

- **Structure**: `[Camera & Lens] + [Voxel Grid & Texel Lock] + [Primary Block/Character Physics] + [Constraint Tail]`
- **Example (English)**:
  `Camera: Medium close-up, 45-degree isometric macro lens, slow dolly push-in. Subject: A canonical Minecraft voxel character (8x8x8 cubic head with +0.5px 3D outer hair shell, 8x12x4 torso, 4x12x4 rectangular prism limbs with flat 4x4 square hand ends) standing beside a 14x14x14 hinged oak chest with a silver 2x4 pixel front latch. Action: The hinged top lid of the voxel chest pivots open 75 degrees, emitting warm golden square pixel particles onto the character's 8x8 pixel face. All surfaces retain crisp nearest-neighbor 16x16 pixel-art textures without bilinear blurring or soft-body limb bending.`
