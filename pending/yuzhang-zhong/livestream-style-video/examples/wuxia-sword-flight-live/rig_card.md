<!-- lang: zh-en | rig: handheld-selfie-irl | style: cinematic-genre-adapt -->
# 直播视角机位与画风设定卡 / Livestream POV Rig & Style DNA Card

| Dimension / 维度 | Locked Specification / 锁定参数 |
| --- | --- |
| **Host / 主播** | `青云小师兄` |
| **Camera Rig / 直播机位** | `handheld-selfie-irl` — 手持自拍杆 / 口袋云台超广角户外移动直播机位 (Arm's-Length Ultra-Wide Handheld Selfie / Gimbal IRL Rig) |
| **Visual Style / 画风适配包** | `cinematic-genre-adapt` — 古风仙侠 / 科幻 / 奇幻 / 悬疑架空剧情跨次元直播化 (Cross-Genre / Period / Fantasy / Sci-Fi Diegetic Livestream) |
| **Optics & Mount / 镜头与架设** | 18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变<br>18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening |
| **Shake & Physics / 物理运动反馈** | 机位与主播伸出的持机手臂物理绑定：随步伐自然呼吸起伏，急转身带轻微水平倾角与自动曝光过渡 |
| **4th-Wall Eye-Line / 眼神互动轴** | 主播边走边直视手持前置镜头互动，偶而向下偏8°扫视手机屏幕下半区滚动弹幕 |
| **Microphone Lock / 麦克风方位锁** | `lavalier` — 衣领处夹持一枚紧凑型无线领夹麦克风发射器 |
| **Lighting / 直播补光方案** | `daylight-outdoor-autoexp` — 通透自然日光勾勒迎风轮廓，真实运动相机/手机直出自动曝光高光过渡 |
| **Style Invariants / 画风防崩几何锁** | 高细节类型片服化道与宏大场景（仙侠云海、古堡地牢或赛博天台），但严格通过贴脸自拍法器/战术面罩/手持直拍镜头呈现——保留迎风碎发、怼脸向观众喊话与突发抓拍的野生直播临场感，拒绝疏离的传统电影旁观机位<br>high-detail genre costume and world architecture (wuxia cloud peaks, medieval dungeon, or cyberpunk rooftop) shot strictly through an intimate first-person selfie/visor/talisman live lens—preserving raw handheld immediacy, wind-whipped hair, direct viewer address, and unscripted live timing rather than detached movie framing |
| **HUD Strategy / 弹幕UI分层策略** | `clean-post-hud` — 在可灵/即梦/Sora/万相中生成100%无UI文字的纯净底片（严禁AI直出弹幕防乱码），再通过 `render_preview.mjs` 或剪辑软件无损叠加高清 LIVE 角标、在线人数、滚动弹幕与PK条。 |
| **Track Compositing / 分轨合成规范** | 单轨纯净底片原则：先生成无任何文字涂层的纯净镜头画面，后置叠加高清直播间角标与滚动弹幕。 |

## 三态首帧锚定提示词 / 3-State Setup Anchor Prompts

### English Setup Sheet Prompt (Midjourney / Flux / Sora / GPT-4o Image)

```text
9:16 Livestream Setup Reference Sheet (3-panel consistency anchor for host "青云小师兄"): Panel 1 [0° Primary Live Frame]: 18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening, high-detail genre costume and world architecture (wuxia cloud peaks, medieval dungeon, or cyberpunk rooftop) shot strictly through an intimate first-person selfie/visor/talisman live lens—preserving raw handheld immediacy, wind-whipped hair, direct viewer address, and unscripted live timing rather than detached movie framing, compact clip-on wireless lavalier microphone transmitter clipped to collar/lapel, crisp natural daylight rim-lighting windblown silhouettes, authentic action-cam auto-exposure highlight roll-off, direct eye-contact into the lens as if greeting live chat; Panel 2 [15° Chat-Read Glance]: exact same room, outfit, and mic position, eyes flicked 15 degrees off-axis reading a glowing secondary chat monitor with subtle smile; Panel 3 [Rig & Optical Side Diagram]: clean side-view showing camera mount distance, ring-light placement, and room background props. Clean raw camera feed, zero burned-in UI text, zero platform watermarks.
```

### 中文首帧直播间参考卡提示词 (即梦 / 可灵 / 通义万相)

```text
9:16 直播间跨镜头一致性三态锚定参考卡（主播「青云小师兄」）：左格【0°主镜头直视态】：18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变，高细节类型片服化道与宏大场景（仙侠云海、古堡地牢或赛博天台），但严格通过贴脸自拍法器/战术面罩/手持直拍镜头呈现——保留迎风碎发、怼脸向观众喊话与突发抓拍的野生直播临场感，拒绝疏离的传统电影旁观机位，衣领处夹持一枚紧凑型无线领夹麦克风发射器，通透自然日光勾勒迎风轮廓，真实运动相机/手机直出自动曝光高光过渡，眼神0°直视镜头向直播间观众打招呼；中格【15°偏轴读弹幕态】：完全相同的房间陈设、穿搭与麦克风左右位置，视线偏转15°扫向副屏弹幕并露出实时反应；右格【机位与补光侧视锚点】：清晰交代摄像头架设距离、环形灯/霓虹光源方位与背景固定摆件。画面保持100%纯净无UI文字底片，零平台水印、零乱码弹幕。
```

## 负向防跑偏词 / Negative Prompts

- **EN Negative**: `detached third-person movie trailer shot, widescreen 2.39:1 cinema bars, actors ignoring camera, slow-motion epic crane sweep, burned-in gibberish UI text, floating omniscient crane camera, detached movie scene ignoring the lens, garbled AI-generated chat text, fake TikTok/Douyin/Twitch logo watermarks, microphone switching sides`
- **ZH Negative**: `疏离的第三人称电影预告片空镜，宽银幕上下黑边，角色无视镜头演戏，慢动作史诗摇臂大远景，画面内烘死的乱码UI，上帝视角电影摇臂空镜，角色无视镜头演戏，AI直出乱码弹幕文字，虚假平台Logo水印，麦克风跨镜头左右跳位`
