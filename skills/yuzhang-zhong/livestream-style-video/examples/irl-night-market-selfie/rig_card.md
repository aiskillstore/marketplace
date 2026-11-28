<!-- lang: zh-en | rig: handheld-selfie-irl | style: realistic-irl -->
# 直播视角机位与画风设定卡 / Livestream POV Rig & Style DNA Card

| Dimension / 维度 | Locked Specification / 锁定参数 |
| --- | --- |
| **Host / 主播** | `Lin` |
| **Camera Rig / 直播机位** | `handheld-selfie-irl` — 手持自拍杆 / 口袋云台超广角户外移动直播机位 (Arm's-Length Ultra-Wide Handheld Selfie / Gimbal IRL Rig) |
| **Visual Style / 画风适配包** | `realistic-irl` — 写实真人 / 通用基础 AI 视频画风 (Photorealistic IRL / General AI Video) |
| **Optics & Mount / 镜头与架设** | 18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变<br>18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening |
| **Shake & Physics / 物理运动反馈** | 机位与主播伸出的持机手臂物理绑定：随步伐自然呼吸起伏，急转身带轻微水平倾角与自动曝光过渡 |
| **4th-Wall Eye-Line / 眼神互动轴** | 主播边走边直视手持前置镜头互动，偶而向下偏8°扫视手机屏幕下半区滚动弹幕 |
| **Microphone Lock / 麦克风方位锁** | `lavalier` — 衣领处夹持一枚紧凑型无线领夹麦克风发射器 |
| **Lighting / 直播补光方案** | `night-neon-irl` — 中景街头霓虹灯牌流光溢彩，一臂距离的手机屏幕冷白光自然照亮主播面部，真实夜间手机自动曝光质感 |
| **Style Invariants / 画风防崩几何锁** | 自然写实真人比例与真实皮肤微纹理，标准五指自然持握手机/麦克风/道具，真实衣物褶皱与手机/摄像头传感器动态范围<br>natural photorealistic human proportions and micro-skin texture, authentic five-finger hand anatomy with firm natural grip on phone/mic/props, real fabric folds, realistic smartphone/webcam sensor dynamic range |
| **HUD Strategy / 弹幕UI分层策略** | `clean-post-hud` — 在可灵/即梦/Sora/万相中生成100%无UI文字的纯净底片（严禁AI直出弹幕防乱码），再通过 `render_preview.mjs` 或剪辑软件无损叠加高清 LIVE 角标、在线人数、滚动弹幕与PK条。 |
| **Track Compositing / 分轨合成规范** | 单轨纯净底片原则：先生成无任何文字涂层的纯净镜头画面，后置叠加高清直播间角标与滚动弹幕。 |

## 三态首帧锚定提示词 / 3-State Setup Anchor Prompts

### English Setup Sheet Prompt (Midjourney / Flux / Sora / GPT-4o Image)

```text
9:16 Livestream Setup Reference Sheet (3-panel consistency anchor for host "Lin"): Panel 1 [0° Primary Live Frame]: 18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening, natural photorealistic human proportions and micro-skin texture, authentic five-finger hand anatomy with firm natural grip on phone/mic/props, real fabric folds, realistic smartphone/webcam sensor dynamic range, compact clip-on wireless lavalier microphone transmitter clipped to collar/lapel, vibrant night-street neon signage bokeh in mid-ground, cool-white smartphone screen glow illuminating the host's face from arm's length, natural night auto-ISO texture, direct eye-contact into the lens as if greeting live chat; Panel 2 [15° Chat-Read Glance]: exact same room, outfit, and mic position, eyes flicked 15 degrees off-axis reading a glowing secondary chat monitor with subtle smile; Panel 3 [Rig & Optical Side Diagram]: clean side-view showing camera mount distance, ring-light placement, and room background props. Clean raw camera feed, zero burned-in UI text, zero platform watermarks.
```

### 中文首帧直播间参考卡提示词 (即梦 / 可灵 / 通义万相)

```text
9:16 直播间跨镜头一致性三态锚定参考卡（主播「Lin」）：左格【0°主镜头直视态】：18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变，自然写实真人比例与真实皮肤微纹理，标准五指自然持握手机/麦克风/道具，真实衣物褶皱与手机/摄像头传感器动态范围，衣领处夹持一枚紧凑型无线领夹麦克风发射器，中景街头霓虹灯牌流光溢彩，一臂距离的手机屏幕冷白光自然照亮主播面部，真实夜间手机自动曝光质感，眼神0°直视镜头向直播间观众打招呼；中格【15°偏轴读弹幕态】：完全相同的房间陈设、穿搭与麦克风左右位置，视线偏转15°扫向副屏弹幕并露出实时反应；右格【机位与补光侧视锚点】：清晰交代摄像头架设距离、环形灯/霓虹光源方位与背景固定摆件。画面保持100%纯净无UI文字底片，零平台水印、零乱码弹幕。
```

## 负向防跑偏词 / Negative Prompts

- **EN Negative**: `waxy plastic AI doll skin, extra six fingers, fused fingers, floating wireless props, Hollywood 2.39:1 black letterbox bars, anamorphic blue cinema flares, burned-in gibberish TikTok UI text, floating omniscient crane camera, detached movie scene ignoring the lens, garbled AI-generated chat text, fake TikTok/Douyin/Twitch logo watermarks, microphone switching sides`
- **ZH Negative**: `塑料假人磨皮感，六指/多指畸形，道具悬空穿模，电影宽银幕黑边，变形宽银幕蓝光眩光，烘死在画面里的乱码直播间弹幕文字，上帝视角电影摇臂空镜，角色无视镜头演戏，AI直出乱码弹幕文字，虚假平台Logo水印，麦克风跨镜头左右跳位`
