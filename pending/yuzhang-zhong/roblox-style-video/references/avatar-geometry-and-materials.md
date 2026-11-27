# Avatar Geometry, BrickColors, and Roblox World Signatures / 角色几何、官方色号与 Roblox 标志性视觉锚点

Short-form Roblox-style videos immediately read as **"authentic Roblox"** when they lock three things at once:
1. **Canonical Roblox Stud Proportions (`2×2×1` torso + four flush `1×2×1` limbs + `1.2×1.2×1.2` barrel-beveled head)**
2. **Solid Rectangular Block Hands (NOT Lego C-shaped claw hooks and NOT 5 human fingers)**
3. **Roblox World & UI Signatures (`SmoothPlastic` / `WoodPlanks` / `Neon` surfaces with zero raised circular Lego bumps + multi-part Roblox Studio props + `BillboardGui` overhead chat bubble + UGC hair/coils)**

When a prompt vaguely says "blocky toy character" or adds "C-shaped claw hands," diffusion models drift into **Lego minifigures** instead of Roblox. Use the exact geometric and material tokens below to lock the aesthetic.

## 1. Canonical Roblox Stud Anatomy (`R6` / `R15` / `Chibi-Blocky`)

| Body Part | Canonical Stud Size | Aspect Ratio | Geometry & Seam Rule |
| --- | --- | --- | --- |
| **Head (`SpecialMesh`)** | `1.2 × 1.2 × 1.2` studs | `1 : 1 : 1` | Classic Roblox barrel-cylinder with generous curved top and bottom fillets (`0.22` bevel radius); studless flat top; never a tall narrow tube |
| **Torso (`R6` / `R15`)** | `2.0 × 2.0 × 1.0` studs | `2 : 2 : 1` | Wide, flat-chested rectangular block with crisp `SmoothPlastic` chamfered edges (`0.06` stud bevel) |
| **Left & Right Arms** | `1.0 × 2.0 × 1.0` studs each | `1 : 2 : 1` | Solid rectangular blocks hanging **flush** against the left and right sides of the torso (`4.0` studs total shoulder span); bottom of the block IS the hand |
| **Left & Right Legs** | `1.0 × 2.0 × 1.0` studs each | `1 : 2 : 1` | Solid rectangular blocks sitting **flush side-by-side** directly beneath the `2.0`-stud torso (`1.0 + 1.0 = 2.0` studs total width, zero thigh gap, zero protruding shoe toes) |

## 2. Anatomy Lock Tokens / 核心部位防变形锁

### Head and Face Decal / 头部与2D面部贴图

- **Positive tokens (English)**: `1:1 classic Roblox barrel-cylinder head with deep rounded top and bottom bevels, smooth studless top, flat 2D screen-printed Roblox decal face, glossy black ink eyes, simple painted mouth line, zero 3D facial protrusion, no nose`
- **正向词 (中文)**: `1:1经典Roblox上下大圆角桶状圆柱头（头顶完全平滑无乐高颗粒），纯平2D丝网印刷贴图五官，高光墨点眼睛，简约绘制嘴型，无3D突起鼻子，无真实皮肤纹理`
- **Expression swaps (单镜头表情词)**:
  - `classic smile`: iconic Roblox `:)` two oval black eyes and curved smile line.
  - `shocked decal`: wide hollow ring eyes, open rectangular gasp mouth, painted sweat drop on temple.
  - `deadpan decal`: flat horizontal line eyes (`-_-`), tiny straight mouth line, zero emotion.
  - `crying decal`: streaming 2D blue waterfall tear strips painted on cheeks, wavy wailing mouth.
  - `smug / check-it decal`: asymmetrical raised brow line, sideways confident smirk.

### Hands and Limbs / 手部与四肢锁定（关键：区分 Roblox 实心方手与乐高 C 型钩爪）

- **Positive tokens (English)**: `canonical Roblox 2x2x1 rectangular torso, two 1x2x1 solid rectangular arm blocks flush at shoulders, two 1x2x1 rectangular leg blocks sitting flush side-by-side matching exact torso width, fingerless and clawless solid beveled rectangular block hands, no human fingers, no Lego C-shaped hook claws`
- **正向词 (中文)**: `纯正Roblox标准2x2x1倒角长方体躯干，两条1x2x1长方体方腿并拢紧贴且总宽度与躯干完全齐平，两条1x2x1一体式实心倒角方柱手臂紧贴躯干两侧，末端为平头倒角实心方块手部（严禁人类五指、严禁乐高C型钩子手），肩髋Motor6D机械转轴接缝清晰`

## 3. Four Surface Shaders / 四种高赞表面材质

| Shader ID | Visual Texture | Lighting Pairing | Prompt Tokens |
| --- | --- | --- | --- |
| `glossy-vinyl` | Blind-box collectible PVC/vinyl with crisp specular highlight and subtle subsurface scatter | Softbox key light + warm rim light + pastel GI bounce | `glossy blind-box vinyl toy material, smooth studless PVC surface, soft subsurface scattering, Octane render studio lighting` |
| `matte-abs` | Satin-matte injection-molded ABS plastic with 2mm chamfered edges | Clean three-point studio lighting, soft ambient occlusion in seams | `satin matte ABS plastic blocks, 2mm chamfered edges, studless smooth surfaces, clean ambient occlusion` |
| `clay-soft` | Soft-touch matte elastomer / polymer clay finish over rigid blocky geometry | Warm miniature tabletop lamp + shallow depth of field (`f/2.8` macro feel) | `soft-touch matte clay-plastic shader, warm miniature diorama lighting, tilt-shift shallow depth of field, tactile bevels` |
| `neon-cyber` | Glossy dark polycarbonate body with emissive neon trim and cyber visor | High-contrast neon rim lights + wet reflective floor grid | `glossy polycarbonate blocky armor, emissive neon edge strips, cyberpunk studio rim lighting, reflective floor` |

## 4. Curated Color Palettes / 爆款配色方案

| Palette Name | Head / Base | Primary Outfit | Secondary / Pants | Accent / Props |
| --- | --- | --- | --- | --- |
| **Classic Noob (经典新手)** | `#FACC15` (Warm Yellow) | `#2563EB` (Royal Blue) | `#65A30D` (Leaf Green) | `#F43F5E` (Cola Red) |
| **Cream Peach Blind-Box (奶油蜜桃)** | `#FEF3C7` (Warm Cream) | `#FDA4AF` (Pastel Rose) | `#F8FAFC` (Milk White) | `#38BDF8` (Sky Ribbon) |
| **Matcha Latte Desk (抹茶打工人)** | `#FEF9C3` (Soft Ivory) | `#86EFAC` (Matcha Green) | `#475569` (Slate Gray) | `#F59E0B` (Amber Coffee) |
| **Y2K Streetwear (千禧潮酷)** | `#FDE68A` (Light Gold) | `#1E293B` (Charcoal Puffer) | `#93C5FD` (Washed Denim) | `#A855F7` (Electric Purple) |

## 5. UGC Accessory Anchor Rules / 配饰防丢失法则

Video models drop small complex accessories across shots. Follow three rules:

1. Cap accessories at **two or three large-silhouette items** per character (for example: oversized cream headphones + fluffy cat-ear beanie + boxy mini backpack).
2. Describe accessories by **geometric primitive + material** (`thick rounded-rectangle matte white headphones` works better than `AirPods Max`).
3. Keep all accessories attached in the **3-View Turnaround Sheet** before generating individual shot keyframes.
