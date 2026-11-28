<!-- lang: zh-en | rig: handheld-selfie-irl | style: roblox-blocky -->
# 直播视角机位与画风设定卡 / Livestream POV Rig & Style DNA Card

| Dimension / 维度 | Locked Specification / 锁定参数 |
| --- | --- |
| **Host / 主播** | `momo_rblx` |
| **Camera Rig / 直播机位** | `handheld-selfie-irl` — 手持自拍杆 / 口袋云台超广角户外移动直播机位 (Arm's-Length Ultra-Wide Handheld Selfie / Gimbal IRL Rig) |
| **Visual Style / 画风适配包** | `roblox-blocky` — 纯正 Roblox R6 / 盲盒方块小人直播画风 (Canonical Roblox R6 / Chibi-Blocky Avatar Style) |
| **Optics & Mount / 镜头与架设** | 18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变<br>18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening |
| **Shake & Physics / 物理运动反馈** | 机位与主播伸出的持机手臂物理绑定：随步伐自然呼吸起伏，急转身带轻微水平倾角与自动曝光过渡 |
| **4th-Wall Eye-Line / 眼神互动轴** | 主播边走边直视手持前置镜头互动，偶而向下偏8°扫视手机屏幕下半区滚动弹幕 |
| **Microphone Lock / 麦克风方位锁** | `lavalier` — 衣领处夹持一枚紧凑型无线领夹麦克风发射器 |
| **Lighting / 直播补光方案** | `flashlight-dim-exploration` — 凝聚的手持强光手电筒光束切开幽暗走廊阴影，左手弹幕手机屏幕泛出微弱冷蓝光 |
| **Style Invariants / 画风防崩几何锁** | 纯正3D Roblox SmoothPlastic方块小人：标准2x2x1倒角长方体躯干、两条并拢同宽1x2x1方柱腿（无腿缝）、无人类五指且无乐高C型爪的1x2x1实心平头方柱手、头顶平滑无凸粒1:1桶状圆角头、纯平2D丝网印刷表情贴图（零3D鼻子凸起）、刚性Motor6D机械转轴关节、平滑无凸粒地板与多部件直播道具<br>authentic 3D Roblox SmoothPlastic avatar: canonical 2x2x1 chamfered rectangular torso, two flush 1x2x1 rectangular leg blocks matching exact torso width (zero thigh gap), fingerless and clawless solid 1x2x1 beveled rectangular block hands, smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal (zero 3D nose), rigid Motor6D mechanical hinge joints, smooth studless SmoothPlastic/WoodPlanks floors and multi-part streaming props |
| **HUD Strategy / 弹幕UI分层策略** | `clean-post-hud` — 在可灵/即梦/Sora/万相中生成100%无UI文字的纯净底片（严禁AI直出弹幕防乱码），再通过 `render_preview.mjs` 或剪辑软件无损叠加高清 LIVE 角标、在线人数、滚动弹幕与PK条。 |
| **Track Compositing / 分轨合成规范** | 单轨纯净底片原则：先生成无任何文字涂层的纯净镜头画面，后置叠加高清直播间角标与滚动弹幕。 |

## 三态首帧锚定提示词 / 3-State Setup Anchor Prompts

### English Setup Sheet Prompt (Midjourney / Flux / Sora / GPT-4o Image)

```text
9:16 Livestream Setup Reference Sheet (3-panel consistency anchor for host "momo_rblx"): Panel 1 [0° Primary Live Frame]: 18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening, authentic 3D Roblox SmoothPlastic avatar: canonical 2x2x1 chamfered rectangular torso, two flush 1x2x1 rectangular leg blocks matching exact torso width (zero thigh gap), fingerless and clawless solid 1x2x1 beveled rectangular block hands, smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal (zero 3D nose), rigid Motor6D mechanical hinge joints, smooth studless SmoothPlastic/WoodPlanks floors and multi-part streaming props [Roblox Rig Variant: CHIBI-BLOCKY — 2x2x1 torso + flush 1x2x1 limbs + fingerless/clawless solid block hands + 1:1 barrel head + flat 2D face decal], compact clip-on wireless lavalier microphone transmitter clipped to collar/lapel, tight volumetric handheld flashlight beam cutting through dim ambient corridor shadows, faint blue smartphone chat-screen spill on left hand, direct eye-contact into the lens as if greeting live chat; Panel 2 [15° Chat-Read Glance]: exact same room, outfit, and mic position, eyes flicked 15 degrees off-axis reading a glowing secondary chat monitor with subtle smile; Panel 3 [Rig & Optical Side Diagram]: clean side-view showing camera mount distance, ring-light placement, and room background props. Clean raw camera feed, zero burned-in UI text, zero platform watermarks.
```

### 中文首帧直播间参考卡提示词 (即梦 / 可灵 / 通义万相)

```text
9:16 直播间跨镜头一致性三态锚定参考卡（主播「momo_rblx」）：左格【0°主镜头直视态】：18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变，纯正3D Roblox SmoothPlastic方块小人：标准2x2x1倒角长方体躯干、两条并拢同宽1x2x1方柱腿（无腿缝）、无人类五指且无乐高C型爪的1x2x1实心平头方柱手、头顶平滑无凸粒1:1桶状圆角头、纯平2D丝网印刷表情贴图（零3D鼻子凸起）、刚性Motor6D机械转轴关节、平滑无凸粒地板与多部件直播道具【Roblox骨架变体：CHIBI-BLOCKY — 2x2x1躯干 + 并拢同宽1x2x1方腿 + 无手指无乐高爪实心方手 + 1:1平滑桶状头 + 2D平面贴图脸】，衣领处夹持一枚紧凑型无线领夹麦克风发射器，凝聚的手持强光手电筒光束切开幽暗走廊阴影，左手弹幕手机屏幕泛出微弱冷蓝光，眼神0°直视镜头向直播间观众打招呼；中格【15°偏轴读弹幕态】：完全相同的房间陈设、穿搭与麦克风左右位置，视线偏转15°扫向副屏弹幕并露出实时反应；右格【机位与补光侧视锚点】：清晰交代摄像头架设距离、环形灯/霓虹光源方位与背景固定摆件。画面保持100%纯净无UI文字底片，零平台水印、零乱码弹幕。
```

## 负向防跑偏词 / Negative Prompts

- **EN Negative**: `human fingers, five-finger hands, Lego C-shaped claw hooks, raised circular Lego floor/head studs, Minecraft sharp 8x8x8 pixel voxel head, 3D protruding human nose, rubbery noodle limbs, official Roblox tilted-square logo, burned-in gibberish UI text, floating omniscient crane camera, detached movie scene ignoring the lens, garbled AI-generated chat text, fake TikTok/Douyin/Twitch logo watermarks, microphone switching sides`
- **ZH Negative**: `人类五指，乐高C型夹爪手，乐高头顶与地面凸起圆颗粒，我的世界直角像素方头，3D真人鼻梁，面条状软体弯曲手臂，官方Roblox倾斜方框商标，画面内烘死的乱码弹幕UI，上帝视角电影摇臂空镜，角色无视镜头演戏，AI直出乱码弹幕文字，虚假平台Logo水印，麦克风跨镜头左右跳位`
