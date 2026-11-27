# Model Prompt Playbook / 多模型图生视频与文生视频手册

Different AI video engines parse motion, camera trajectories, and style locks differently. A prompt written for Sora often overloads Kling or Hailuo. Use this playbook to format prompts for the user's chosen engine.

## 1. Universal Golden Rule: First-Frame I2V Beats Raw T2V

For multi-shot Roblox shorts, **First-Frame Image-to-Video (首帧图生视频 I2V)** is the primary production path:

1. Generate the **3-View Turnaround Sheet** first (`scripts/avatar_spec.mjs`).
2. Generate each shot's **First-Frame Static Keyframe** using an image model that supports reference character consistency (Midjourney `--cref`, Flux Redux/PuLID, Jimeng 角色参考, or GPT-4o Image).
3. Feed the verified static keyframe into the video engine with a **motion-only + geometry-lock prompt**. When the first frame already locks the outfit and 2D decal face, the video model spends its capacity on clean blocky motion instead of inventing anatomy.

## 2. Engine-Specific Syntax & Settings / 六大主流模型参数与语法

| Engine | Best Mode | Clip Length | Camera Control Syntax | Recommended Settings |
| --- | --- | --- | --- | --- |
| **Kling (可灵 1.6 / 2.0)** | I2V (High Quality / Master) | 5s | Natural language (`Camera slowly pushes in`, `镜头快速推近`) or Camera Control sliders | Creativity `0.4–0.5`, Motion scale `Medium`, Negative prompt enabled |
| **Seedance / Jimeng (即梦视频)** | I2V / 首尾帧控制 | 4s–5s | Direct Chinese rhythm & camera phrases (`固定机位微俯拍`, `镜头跟随轻微震动`) | Lock first frame (and end frame for loop shots); concise single-clause motion |
| **Hailuo MiniMax (海螺 I2V-01-Director)** | I2V-01-Director | 6s | Bracketed English commands: `[Push in]`, `[Pull out]`, `[Pan left]`, `[Tilt up]`, `[Shake]`, `[Static shot]` | Place `[Camera Command]` at the exact timestamp or opening of the prompt |
| **Wan 2.1 / Wan 2.6 (通义万相)** | I2V / T2V (14B) | 5s | Explicit lens + lighting + motion sentence (`Medium shot, slow dolly in, 3D blocky toy style`) | CFG `5.0–6.0`, strong negative prompt block required to block human hands |
| **Sora** | I2V / Storyboard | 5s–10s | Cinematic physical description (`Wide-angle 35mm macro lens, low-angle tracking shot`) | Specify rigid hinge physics so Sora does not apply soft-body deformation to limbs |
| **Runway Gen-3 / Gen-4** | I2V | 5s | `[Camera Moto]: Subject motion` structure (`Low angle static camera: The blocky character...`) | Structure prompt as `Camera: ... Subject: ... Scene: ...` |

## 3. Prompt Assembly Formula by Engine / 各模型提示词拼装公式

### Kling (可灵) Formula

- **Structure**: `[主体锚点 + 刚体关节声明] + [单一核心动作] + [表情贴图与配饰次级物理] + [运镜指令]`
- **Example (Chinese)**:
  `画面中的3D高光SmoothPlastic材质Roblox方块小人（1:1桶状圆角平滑头部、纯平2D印刷五官、无手指且无乐高C型爪的1x2x1实心平头方柱手、2x2x1躯干配并拢方腿），刚性Motor6D肩部关节快速向上抬起双臂抱头，脸部2D贴图呈现出瞳孔缩小的震惊表情，头顶毛绒猫耳针织帽随之轻微弹跳。木纹地板与多部件书桌道具清晰细腻，镜头快速推近至中近景，严禁出现人类手指或乐高圆粒凸起。`

### Seedance / Jimeng (即梦) Formula

- **Structure**: `[画风与材质锁定] + [镜头机位] + [干脆利落的单步动作] + [光影氛围]`
- **Example (Chinese)**:
  `高光SmoothPlastic材质Roblox方块小人，中景微俯拍镜头快速推近。小人保持2x2x1倒角方柱躯干与1x2x1实心平头方块手（无人类手指、无乐高C型爪），猛地向前倾倒扑在带键帽细节的微缩笔记本电脑键盘上，脸部2D贴图切换为流泪破防表情，桌面双铃闹钟与暖光台灯产生柔和塑料高光反射，动作干脆利落。`

### Hailuo MiniMax (海螺 Director) Formula

- **Structure**: `[Bracketed Camera Tag] + [Blocky Subject Lock] + [Single Hinged Action] + [Environment & Shader Tail]`
- **Example (English)**:
  `[Push in, Shake] A glossy SmoothPlastic Roblox-style blocky character with a 1:1 barrel-beveled cylindrical head, flat 2D painted face decal, and fingerless and clawless solid 1x2x1 rectangular block hands. The character rigidly slams its solid rectangular block hand onto a twin-bell red alarm clock with a white clock face on the wooden desk, causing the clock to bounce upward. Rigid Motor6D hinge joints, smooth studless floor and props (zero Lego bumps), studio lighting, no human fingers.`

### Wan 2.1 / 2.6 (通义万相) Formula

- **Structure**: `Positive Prompt (Style + Subject + Action + Camera)` + `Explicit Negative Prompt`
- **Positive Example**:
  `9:16竖屏，3D纯正Roblox Studio画风，SmoothPlastic平滑塑料材质的Roblox方块小人，1:1桶状圆角圆柱头，纯平2D印刷五官，无手指无乐高爪的1x2x1实心平头方柱手，刚性Motor6D铰链四肢。小人迈着干脆的方块步向前跳跃踏上带发光圆环的重生点平台，背上的立体方块书包轻微晃动，镜头低角度跟随平移，柔和天空盒轮廓光。`
- **Negative Example**:
  `人类手指，五指手掌，乐高C型夹爪手，乐高头顶与地面凸起圆颗粒，真实人类皮肤毛孔，3D高鼻梁，我的世界像素方块，面条状弯曲手臂，脚底打滑，画面模糊，多手多脚`

### Sora & Runway Formula

- **Structure**: `[Camera & Lens] + [Tactile Material & Rig Lock] + [Primary Physics Action] + [Constraint Tail]`
- **Example (English)**:
  `Camera: Medium close-up, 50mm macro lens, rapid dolly push-in. Subject: A stylized 3D Roblox R6/blocky figure made of satin-gloss SmoothPlastic, featuring a smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal, fingerless and clawless solid 1x2x1 rectangular block hands, and flush 1x2x1 blocky legs under a 2x2x1 torso. Action: The figure pivots its stiff right arm block at the shoulder hinge to slap a twin-bell red alarm clock on a wooden bedroom desk. Smooth flat architectural surfaces (zero raised circular Lego floor studs), rigid rectangular limbs.`
