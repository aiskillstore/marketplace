# Voxel Geometry, Blocks, Mobs, and Shaders / 角色像素比例、方块道具、生物与光影规范

Short-form Minecraft-style videos immediately read as **"authentic Minecraft"** when they lock four things at once:
1. **Canonical Pixel-Grid Character Anatomy (`8×8×8` head + `8×12×4` torso + `4×12×4` Steve / `3×12×4` Alex limbs + `+0.5px` 3D outer skin layer)**
2. **Flat Square `4×4` / `3×4` Hand Ends + Extruded `16×16×1` Pixel-Art Held Tools (NOT human fingers, NOT Lego C-claws, and NOT smooth round metal blades)**
3. **Crisp Nearest-Neighbor `16×16` & `8×8` Pixel Texels (zero bilinear blur, sharp 90-degree cubic corners)**
4. **Canonical Voxel Blocks & Mobs (`16×16×16` Grass Block / Diamond Ore / TNT, `14×14×14` Hinged Chest, Quadruped Creeper, Tall Enderman)**

When a prompt vaguely says "blocky character with a pickaxe," diffusion models drift into **Roblox cylindrical heads**, **Lego studs and C-claws**, or **blurry clay characters holding smooth cylindrical tools**. Use the exact geometric and texel tokens below to lock the aesthetic.

## 1. Canonical Minecraft Character Pixel Anatomy (`64×64` Skin Standard)

In Minecraft, `1 full block = 16 × 16 × 16 pixels = 1.0 meter`. A standard player character stands `32 pixels` (`2.0 blocks` / `1.8m` in-game hitbox) tall:

| Body Part | Pixel Size (`W × H × D`) | Block Ratio | Geometry & Layer Rule |
| --- | --- | --- | --- |
| **Head (Base Cube)** | `8 × 8 × 8` px | `0.5 × 0.5 × 0.5` blocks (`1:1:1`) | Sharp 90-degree cube with an `8×8` nearest-neighbor pixel face; flat studless top; never a rounded Roblox cylinder |
| **Head Outer Layer (`Hat`)** | `8.8 × 8.8 × 8.8` px (`+0.5px` inflation) | Floating 3D shell | Raised 3D pixel bangs, hoodie hood, crown, headphones, or Diamond Helmet casting a crisp 1px step shadow |
| **Torso (`Body` + `Jacket`)** | `8 × 12 × 4` px (`+0.25px` outer jacket) | `0.5 × 0.75 × 0.25` blocks (`2:3:1`) | Rectangular prism torso with crisp `8×12` pixel shirt/armor grid |
| **Arms (`Classic Wide` / Steve)** | `4 × 12 × 4` px each | `0.25 × 0.75 × 0.25` blocks (`1:3:1`) | Flush against torso sides (`16px` total shoulder span); ends in a flat `4×4` pixel square hand |
| **Arms (`Slim` / Alex)** | `3 × 12 × 4` px each | `0.1875 × 0.75 × 0.25` blocks | Slimmer `3px` wide rectangular prism arms (`14px` total shoulder span); ends in a flat `3×4` square hand |
| **Left & Right Legs** | `4 × 12 × 4` px each | `0.25 × 0.75 × 0.25` blocks (`1:3:1`) | Two rectangular prisms sitting **flush side-by-side** directly beneath the `8px` torso (`4 + 4 = 8px` total width, zero thigh gap) |

## 2. Expressive Pixel Face & Hand Lock Tokens / 面部像素与平头方手锁定

### `8×8` Pixel Face & *Fresh Animations* Rig

- **Positive tokens (English)**: `sharp 1:1:1 cubic 8x8x8 Minecraft head, crisp nearest-neighbor 8x8 pixel face texture, Fresh Animations style expressive 2x1 white sclera pixel eyes with sliding 1x1 pupils and floating 2x1 pixel eyebrows, raised 0.5px 3D outer skin hair bangs layer, zero 3D human nose, no rounded Roblox cylinder head`
- **正向词 (中文)**: `1:1:1锋利直角8x8x8像素立方体头部，清晰无模糊的8x8邻近采样像素五官贴图，Fresh Animations风格可动2x1像素眼白配1x1滑动像素瞳孔与2x1悬浮像素眉毛，外层悬浮0.5像素厚度的3D立体刘海/帽兜皮肤层，零3D突起真人鼻梁，严禁Roblox圆桶头`
- **Expression swaps (单镜头像素表情词)**:
  - `default pixel smile`: classic `2×1` pixel eyes (`white + blue/brown/green pupil pixel`) with a `2×1` warm pixel mouth.
  - `shocked pixel eyes`: oversized `2×2` hollow square pixel eyes with tiny centered `1×1` pupil texels and a `2×2` dark square open mouth.
  - `deadpan / side-eye`: flat `2×1` half-closed horizontal pixel eyelids (`-_-`) with pupils shifted to the corner texel.
  - `panic waterfall tears`: vertical `1×4` cyan/blue pixel tear strips streaming down columns `x=2` and `x=5` of the `8×8` face grid.

### Flat `4×4` / `3×4` Square Hands & Extruded `16×16×1` Held Tools

- **Positive tokens (English)**: `flat square 4x4 pixel-block hand ends, fingerless and clawless rectangular prism arms, holding an extruded 16x16x1 pixel-art tool with stepped 90-degree voxel edges at a 45-degree grip angle, no human fingers, no Lego C-shaped claws, no smooth cylindrical metal shaft`
- **正向词 (中文)**: `末端为4x4平头正方形像素截面的长方体手臂（无人类五指、无乐高C型钩爪），以45度角握持16x16x1像素挤出厚度的锯齿直角像素工具（严禁圆润光滑金属杆或真人手指握持）`

## 3. Canonical Voxel Blocks, Sub-Block Props & Mobs / 核心方块、道具与生物几何表

| Voxel Object / Mob | Canonical Grid Size | Signature Visual Details | Prompt Lock Tokens |
| --- | --- | --- | --- |
| **Grass Block (`草方块`)** | `16 × 16 × 16` px (`1m³`) | Lush green `16×16` top pixel grid + jagged `2–5px` green grass side overhang over brown dirt texels | `canonical 16x16x16 Minecraft grass block with crisp green top texels, stepped pixel grass side overlay, and rich brown dirt pixel grid` |
| **Diamond Ore (`钻石矿石`)** | `16 × 16 × 16` px (`1m³`) | Grey cobblestone/stone `16×16` pixel matrix embedded with glowing `#4AEDD9` cyan diamond pixel clusters | `16x16x16 stone voxel block embedded with glowing cyan #4AEDD9 pixel clusters of Minecraft diamond ore` |
| **TNT Block (`TNT炸药块`)** | `16 × 16 × 16` px (`1m³`) | Red/orange vertical dynamite stick texels + white center band (`4px` tall) printed with black pixel `TNT` letters + top fuse | `16x16x16 Minecraft TNT voxel block with red dynamite pixel stripes, white center band reading TNT in pixel font, and top grey pixel fuse` |
| **Crafting Table (`工作台`)** | `16 × 16 × 16` px (`1m³`) | `3×3` crafting grid pixel top + pixelated saw and hammer tools hanging on oak plank side faces | `16x16x16 Minecraft crafting table block with 3x3 top grid texels and pixelated saw and hammer side textures` |
| **Hinged Chest (`储物箱`)** | `14 × 14 × 14` px (`0.875m³`) | Slightly inset from full block; oak-brown pixel sides with dark horizontal lid seam at `y=10px` and a `2×4` silver `#CBD5E1` front pixel latch | `14x14x14 Minecraft wooden chest with hinged top lid seam and protruding 3D silver 2x4 pixel lock latch on the front` |
| **Torch / Lantern (`火把/灯笼`)** | `2 × 10 × 2` px / `6 × 9 × 6` px | Pixelated oak stick topped with a `2×2×2` emissive orange-gold voxel flame and cubic smoke particles | `2x10x2 pixel wooden torch with glowing 2x2x2 emissive amber voxel flame and floating square pixel particles` |
| **Diamond Pickaxe / Sword (`钻石镐/剑`)** | `16 × 16 × 1` px sprite | Diagonal brown oak pixel handle + stepped cyan `#4AEDD9` diamond pixel head/blade extruded `1px` thick | `extruded 16x16x1 3D pixel-art Minecraft diamond pickaxe with stepped 90-degree cyan voxel edges and pixel wood handle` |
| **Creeper (`苦力怕`)** | `8×8×8` head, `8×12×4` body, four `4×6×4` legs | **ZERO arms**; mottled green `16×16` leaf-camo texels; iconic `8×8` black pixel eyes and sad mouth; flashes solid white before exploding | `canonical armless Minecraft Creeper mob with 8x8x8 cubic head, iconic black pixel frowning mouth and eyes, 8x12x4 body, and four short 4x6x4 legs` |
| **Enderman (`末影人`)** | `8×8×8` head, `8×12×4` torso, `2×30×2` limbs | Jet-black `#111827` voxel body, long thin `2×30×2` stick arms/legs, glowing magenta `#D946EF` `3×1` pixel eyes, floating purple portal particles | `tall jet-black Minecraft Enderman with 8x8x8 cube head, glowing purple 3x1 pixel eyes, long thin 2x30x2 stick arms carrying a 16x16x16 grass block` |
| **Pink Axolotl (`粉美西螈`)** | `8×5×10` body, `3D` pixel gills | Pastel pink `#F472B6` voxel body, three 3D pixel gill fronds on each side of head, flat pixel tail | `cute pastel-pink Minecraft voxel axolotl with 3D pixel external gill fronds and tiny dark pixel eyes` |

## 4. Four Minecraft Visual & Shader Styles / 四种高赞光影与渲染画风

| Shader ID | Visual Signature | Best Short-Video Genre | Prompt Tokens |
| --- | --- | --- | --- |
| `bsl-sunlight` | **BSL / Complementary Shaders**: warm volumetric god-rays, soft block-edge shadows, glowing torches/ores, gentle water reflection while keeping `16×16` pixel texels razor-sharp | Cozy builds, survival stories, Xiaohongshu aesthetic shorts | `Minecraft BSL / Complementary Shaders aesthetic, warm volumetric sunlight god-rays, soft voxel contact shadows, emissive torch and ore glow, crisp nearest-neighbor 16x16 pixel textures` |
| `bare-bones-trailer` | **Official Minecraft Trailer / Bare Bones + Fresh Animations**: simplified ultra-clean `16×16` color blocks, subtle edge bevel highlight, bouncy expressive pixel eyes and brows | Comedy skits, duo contrast, fast-paced TikTok/Douyin memes | `Official Minecraft Trailer and Bare Bones texture pack aesthetic, vibrant clean 16x16 pixel blocks, Fresh Animations expressive pixel eyes and brows, bright studio global illumination` |
| `vanilla-crisp` | **Classic Vanilla Java Edition**: authentic unweighted `16×16` pixel textures, crisp step-shaded block faces (`100%` top, `80%` north/south, `60%` east/west), classic skybox | Nostalgic gameplay skits, speedrun parodies, Noob vs. Pro | `authentic Vanilla Minecraft Java Edition look, crisp unfiltered 16x16 nearest-neighbor pixel textures, directional block face shading, classic blocky clouds` |
| `rtx-emissive` | **Minecraft RTX / Ray-Traced Cave**: dark deepslate cave contrast lit entirely by glowing cyan Diamond Ore (`#4AEDD9`), Redstone (`#EF4444`), and warm Amber Lanterns (`#F59E0B`) | Cave mining hooks, Redstone ASMR, Enderman encounters | `Minecraft RTX path-traced voxel lighting, emissive glowing cyan diamond ore and warm amber torch light bouncing across crisp 16x16 deepslate pixel blocks` |
