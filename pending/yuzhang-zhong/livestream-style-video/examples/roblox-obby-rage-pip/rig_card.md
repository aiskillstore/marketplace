<!-- lang: zh-en | rig: pip-facecam-rig | style: roblox-blocky -->
# 直播视角机位与画风设定卡 / Livestream POV Rig & Style DNA Card

| Dimension / 维度 | Locked Specification / 锁定参数 |
| --- | --- |
| **Host / 主播** | `BloxyKai` |
| **Camera Rig / 直播机位** | `pip-facecam-rig` — 实况主画面 + 右上/左下主播反应小窗双轨机位 (PiP) (Dual-Track Gameplay / World Feed + Corner Streamer Facecam (PiP)) |
| **Visual Style / 画风适配包** | `roblox-blocky` — 纯正 Roblox R6 / 盲盒方块小人直播画风 (Canonical Roblox R6 / Chibi-Blocky Avatar Style) |
| **Optics & Mount / 镜头与架设** | A轨（9:16主画面）：实况场景/游戏内镜头；B轨（角落画中画小窗）：28mm固定RGB电竞房主播特写机位<br>Track A (Main 9:16): active game/world camera; Track B (PiP Corner): locked 28mm RGB studio webcam close-up on streamer with headset |
| **Shake & Physics / 物理运动反馈** | 严格双轨分层生成后合成（或首帧锁定画中画边框I2V），杜绝单次文生视频导致小窗漂移融化 |
| **4th-Wall Eye-Line / 眼神互动轴** | 小窗主播紧盯屏幕反光操作，在神操作或破防瞬间猛转0°怼脸直视摄像头 |
| **Microphone Lock / 麦克风方位锁** | `headset-mic` — 头戴式RGB电竞/监听大耳机，弯曲麦杆固定于左脸颊旁 |
| **Lighting / 直播补光方案** | `ring-rgb-studio` — 正面环形补光灯打出清晰圆环眼神光，屏幕冷光映亮桌面，背景墙点缀青色与品红RGB氛围灯带 |
| **Style Invariants / 画风防崩几何锁** | 纯正3D Roblox SmoothPlastic方块小人：标准2x2x1倒角长方体躯干、两条并拢同宽1x2x1方柱腿（无腿缝）、无人类五指且无乐高C型爪的1x2x1实心平头方柱手、头顶平滑无凸粒1:1桶状圆角头、纯平2D丝网印刷表情贴图（零3D鼻子凸起）、刚性Motor6D机械转轴关节、平滑无凸粒地板与多部件直播道具<br>authentic 3D Roblox SmoothPlastic avatar: canonical 2x2x1 chamfered rectangular torso, two flush 1x2x1 rectangular leg blocks matching exact torso width (zero thigh gap), fingerless and clawless solid 1x2x1 beveled rectangular block hands, smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal (zero 3D nose), rigid Motor6D mechanical hinge joints, smooth studless SmoothPlastic/WoodPlanks floors and multi-part streaming props |
| **HUD Strategy / 弹幕UI分层策略** | `clean-post-hud` — 在可灵/即梦/Sora/万相中生成100%无UI文字的纯净底片（严禁AI直出弹幕防乱码），再通过 `render_preview.mjs` 或剪辑软件无损叠加高清 LIVE 角标、在线人数、滚动弹幕与PK条。 |
| **Track Compositing / 分轨合成规范** | 双轨合成铁律（画中画PiP）：将 9:16 主场景/游戏画面 与 主播「BloxyKai」反应小窗 拆分为两条独立纯净视频轨分别生成，再通过后期或 render_preview.mjs 合成圆角画中画边框，彻底杜绝小窗变形漂移。 |

## 三态首帧锚定提示词 / 3-State Setup Anchor Prompts

### English Setup Sheet Prompt (Midjourney / Flux / Sora / GPT-4o Image)

```text
9:16 Livestream Setup Reference Sheet (3-panel consistency anchor for host "BloxyKai"): Panel 1 [0° Primary Live Frame]: Track A (Main 9:16): active game/world camera; Track B (PiP Corner): locked 28mm RGB studio webcam close-up on streamer with headset, authentic 3D Roblox SmoothPlastic avatar: canonical 2x2x1 chamfered rectangular torso, two flush 1x2x1 rectangular leg blocks matching exact torso width (zero thigh gap), fingerless and clawless solid 1x2x1 beveled rectangular block hands, smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal (zero 3D nose), rigid Motor6D mechanical hinge joints, smooth studless SmoothPlastic/WoodPlanks floors and multi-part streaming props [Roblox Rig Variant: CHIBI-BLOCKY — 2x2x1 torso + flush 1x2x1 limbs + fingerless/clawless solid block hands + 1:1 barrel head + flat 2D face decal], over-ear RGB gaming/studio headset with curved boom mic positioned near left cheek, front circular LED ring-light creating crisp ring catchlights in the eyes, cool monitor glow on desk, cyan and magenta RGB neon strip accents on back wall, direct eye-contact into the lens as if greeting live chat; Panel 2 [15° Chat-Read Glance]: exact same room, outfit, and mic position, eyes flicked 15 degrees off-axis reading a glowing secondary chat monitor with subtle smile; Panel 3 [Rig & Optical Side Diagram]: clean side-view showing camera mount distance, ring-light placement, and room background props. Clean raw camera feed, zero burned-in UI text, zero platform watermarks.
```

### 中文首帧直播间参考卡提示词 (即梦 / 可灵 / 通义万相)

```text
9:16 直播间跨镜头一致性三态锚定参考卡（主播「BloxyKai」）：左格【0°主镜头直视态】：A轨（9:16主画面）：实况场景/游戏内镜头；B轨（角落画中画小窗）：28mm固定RGB电竞房主播特写机位，纯正3D Roblox SmoothPlastic方块小人：标准2x2x1倒角长方体躯干、两条并拢同宽1x2x1方柱腿（无腿缝）、无人类五指且无乐高C型爪的1x2x1实心平头方柱手、头顶平滑无凸粒1:1桶状圆角头、纯平2D丝网印刷表情贴图（零3D鼻子凸起）、刚性Motor6D机械转轴关节、平滑无凸粒地板与多部件直播道具【Roblox骨架变体：CHIBI-BLOCKY — 2x2x1躯干 + 并拢同宽1x2x1方腿 + 无手指无乐高爪实心方手 + 1:1平滑桶状头 + 2D平面贴图脸】，头戴式RGB电竞/监听大耳机，弯曲麦杆固定于左脸颊旁，正面环形补光灯打出清晰圆环眼神光，屏幕冷光映亮桌面，背景墙点缀青色与品红RGB氛围灯带，眼神0°直视镜头向直播间观众打招呼；中格【15°偏轴读弹幕态】：完全相同的房间陈设、穿搭与麦克风左右位置，视线偏转15°扫向副屏弹幕并露出实时反应；右格【机位与补光侧视锚点】：清晰交代摄像头架设距离、环形灯/霓虹光源方位与背景固定摆件。画面保持100%纯净无UI文字底片，零平台水印、零乱码弹幕。
```

## 负向防跑偏词 / Negative Prompts

- **EN Negative**: `human fingers, five-finger hands, Lego C-shaped claw hooks, raised circular Lego floor/head studs, Minecraft sharp 8x8x8 pixel voxel head, 3D protruding human nose, rubbery noodle limbs, official Roblox tilted-square logo, burned-in gibberish UI text, floating omniscient crane camera, detached movie scene ignoring the lens, garbled AI-generated chat text, fake TikTok/Douyin/Twitch logo watermarks, microphone switching sides`
- **ZH Negative**: `人类五指，乐高C型夹爪手，乐高头顶与地面凸起圆颗粒，我的世界直角像素方头，3D真人鼻梁，面条状软体弯曲手臂，官方Roblox倾斜方框商标，画面内烘死的乱码弹幕UI，上帝视角电影摇臂空镜，角色无视镜头演戏，AI直出乱码弹幕文字，虚假平台Logo水印，麦克风跨镜头左右跳位`
