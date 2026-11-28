<!-- lang: zh-en | rig: chest-head-pov | style: realistic-irl -->
# 直播视角机位与画风设定卡 / Livestream POV Rig & Style DNA Card

| Dimension / 维度 | Locked Specification / 锁定参数 |
| --- | --- |
| **Host / 主播** | `ren.urban` |
| **Camera Rig / 直播机位** | `chest-head-pov` — 第一人称胸挂 / 头戴运动相机探险直拍机位 (First-Person Chest / Head-Strap Action-Cam Live POV) |
| **Visual Style / 画风适配包** | `realistic-irl` — 写实真人 / 通用基础 AI 视频画风 (Photorealistic IRL / General AI Video) |
| **Optics & Mount / 镜头与架设** | 16mm超广角运动相机第一视角，f/5.6大景深，主播双手从画面下沿自然伸入互动<br>16mm ultra-wide action-cam rectilinear/mild barrel lens, deep focus f/5.6, both hands of the streamer visible entering lower frame |
| **Shake & Physics / 物理运动反馈** | 真实胸腔呼吸起伏与脚步震动反馈，右手手电筒光束或左手弹幕副机随身体同步晃动 |
| **4th-Wall Eye-Line / 眼神互动轴** | 镜头即主播本人视角：低头瞥一眼左手手机屏幕亮光，再猛地抬头对准前方异响源 |
| **Microphone Lock / 麦克风方位锁** | `lavalier` — 衣领处夹持一枚紧凑型无线领夹麦克风发射器 |
| **Lighting / 直播补光方案** | `flashlight-dim-exploration` — 凝聚的手持强光手电筒光束切开幽暗走廊阴影，左手弹幕手机屏幕泛出微弱冷蓝光 |
| **Style Invariants / 画风防崩几何锁** | 自然写实真人比例与真实皮肤微纹理，标准五指自然持握手机/麦克风/道具，真实衣物褶皱与手机/摄像头传感器动态范围<br>natural photorealistic human proportions and micro-skin texture, authentic five-finger hand anatomy with firm natural grip on phone/mic/props, real fabric folds, realistic smartphone/webcam sensor dynamic range |
| **HUD Strategy / 弹幕UI分层策略** | `clean-post-hud` — 在可灵/即梦/Sora/万相中生成100%无UI文字的纯净底片（严禁AI直出弹幕防乱码），再通过 `render_preview.mjs` 或剪辑软件无损叠加高清 LIVE 角标、在线人数、滚动弹幕与PK条。 |
| **Track Compositing / 分轨合成规范** | 单轨纯净底片原则：先生成无任何文字涂层的纯净镜头画面，后置叠加高清直播间角标与滚动弹幕。 |

## 三态首帧锚定提示词 / 3-State Setup Anchor Prompts

### English Setup Sheet Prompt (Midjourney / Flux / Sora / GPT-4o Image)

```text
9:16 Livestream Setup Reference Sheet (3-panel consistency anchor for host "ren.urban"): Panel 1 [0° Primary Live Frame]: 16mm ultra-wide action-cam rectilinear/mild barrel lens, deep focus f/5.6, both hands of the streamer visible entering lower frame, natural photorealistic human proportions and micro-skin texture, authentic five-finger hand anatomy with firm natural grip on phone/mic/props, real fabric folds, realistic smartphone/webcam sensor dynamic range, compact clip-on wireless lavalier microphone transmitter clipped to collar/lapel, tight volumetric handheld flashlight beam cutting through dim ambient corridor shadows, faint blue smartphone chat-screen spill on left hand, direct eye-contact into the lens as if greeting live chat; Panel 2 [15° Chat-Read Glance]: exact same room, outfit, and mic position, eyes flicked 15 degrees off-axis reading a glowing secondary chat monitor with subtle smile; Panel 3 [Rig & Optical Side Diagram]: clean side-view showing camera mount distance, ring-light placement, and room background props. Clean raw camera feed, zero burned-in UI text, zero platform watermarks.
```

### 中文首帧直播间参考卡提示词 (即梦 / 可灵 / 通义万相)

```text
9:16 直播间跨镜头一致性三态锚定参考卡（主播「ren.urban」）：左格【0°主镜头直视态】：16mm超广角运动相机第一视角，f/5.6大景深，主播双手从画面下沿自然伸入互动，自然写实真人比例与真实皮肤微纹理，标准五指自然持握手机/麦克风/道具，真实衣物褶皱与手机/摄像头传感器动态范围，衣领处夹持一枚紧凑型无线领夹麦克风发射器，凝聚的手持强光手电筒光束切开幽暗走廊阴影，左手弹幕手机屏幕泛出微弱冷蓝光，眼神0°直视镜头向直播间观众打招呼；中格【15°偏轴读弹幕态】：完全相同的房间陈设、穿搭与麦克风左右位置，视线偏转15°扫向副屏弹幕并露出实时反应；右格【机位与补光侧视锚点】：清晰交代摄像头架设距离、环形灯/霓虹光源方位与背景固定摆件。画面保持100%纯净无UI文字底片，零平台水印、零乱码弹幕。
```

## 负向防跑偏词 / Negative Prompts

- **EN Negative**: `waxy plastic AI doll skin, extra six fingers, fused fingers, floating wireless props, Hollywood 2.39:1 black letterbox bars, anamorphic blue cinema flares, burned-in gibberish TikTok UI text, floating omniscient crane camera, detached movie scene ignoring the lens, garbled AI-generated chat text, fake TikTok/Douyin/Twitch logo watermarks, microphone switching sides`
- **ZH Negative**: `塑料假人磨皮感，六指/多指畸形，道具悬空穿模，电影宽银幕黑边，变形宽银幕蓝光眩光，烘死在画面里的乱码直播间弹幕文字，上帝视角电影摇臂空镜，角色无视镜头演戏，AI直出乱码弹幕文字，虚假平台Logo水印，麦克风跨镜头左右跳位`
