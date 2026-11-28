# Short-Video Beats, Camera, and Audio / 短视频节奏、运镜与音效卡点

Viral Roblox-style shorts on Douyin, Xiaohongshu, and TikTok rely on tight physical timing, miniature toy cinematography, and crisp sound design. Use these rules when structuring storyboards.

## 1. The 3-Zone Retention Structure / 竖屏短视频三段式留存结构

| Zone | Time Window (15s Short) | Retention Goal | Visual & Motion Rule |
| --- | --- | --- | --- |
| **Zone 1 · Hook (黄金前3秒)** | `0.0s–3.5s` | Stop the scroll immediately | Start mid-action or mid-crisis: extreme close-up on a shocked 2D decal face, sudden whip-pan, or a rigid blocky ragdoll impact. Never waste 3 seconds on an empty room. |
| **Zone 2 · Escalation (节奏推进)** | `3.5s–11.5s` (2 shots) | Build comedic contrast or tension | Cut every `3.5s–4.0s`. Alternate shot scale (`Close-Up -> Medium Full -> Low-Angle Close-Up`). Keep one clear physical verb per clip. |
| **Zone 3 · Payoff / Loop (反转或无缝循环)** | `11.5s–15.0s` | Trigger replay, shares, or comments | End with a deadpan freeze-frame, a dramatic spotlight shift, or a final pose that matches Shot 1 Frame 1 so the video loops seamlessly. |

## 2. Miniature Toy Cinematography / 盲盒微缩感摄影灯光法则

Why do top Roblox AI videos look like expensive collectibles rather than flat game screen recordings? Because they prompt **miniature studio photography** instead of game-engine rendering:

1. **Lens & Depth of Field (微距浅景深)**:
   Use `50mm macro lens, shallow depth of field (f/2.8), soft bokeh background, miniature tabletop diorama scale`. This blurs background clutter and makes the beveled plastic character pop in 9:16 mobile viewing.
2. **Three-Point Toy Lighting (三点潮玩布光)**:
   - **Key light**: `warm softbox key light at 45 degrees creating a crisp oval specular highlight on the cylindrical head`.
   - **Rim light**: `bright cyan or warm amber rim light separating the chamfered torso edges from the background`.
   - **Global Illumination**: `soft pastel bounce light in the crevices between the blocky arms and torso`.
3. **9:16 Safe Zones (竖屏安全区构图)**:
   Keep the character's head and 2D face decal within the **central 50% vertical band** (`y: 25% to 75%`). The top 15% and bottom 25% of a 9:16 screen are covered by platform UI, captions, and account icons on Douyin, Xiaohongshu, and TikTok.

## 3. High-Impact Camera Moves for Blocky Avatars / 高表现力运镜词库

| Camera Move | English Prompt Token | 中文运镜提示词 | Best Moment |
| --- | --- | --- | --- |
| **Snap Zoom / Crash Push** | `Rapid dolly push-in to extreme close-up on the 2D decal face` | `镜头极速推近至脸部2D贴图大特写` | Hook (`0–3s`) or sudden realization |
| **Low-Angle Hero Tilt** | `Low-angle hero shot tilting upward with dramatic rim light` | `低角度仰拍缓慢上摇，强边缘轮廓光` | Outfit reveal or comical overconfidence |
| **Isometric Diorama Pan** | `45-degree high-angle isometric view panning smoothly across the miniature room` | `45度微缩模型俯视机位平滑横移` | Miniature tycoon / cozy café / desk setup |
| **Handheld Impact Shake** | `Subtle camera shake on impact as the blocky figure lands` | `方块小人落地瞬间镜头轻微震动反馈` | Slapstick fall, alarm slam, obby jump |
| **Deadpan Lock-Off** | `Locked-off static tripod medium shot, zero camera movement` | `完全固定的三脚架中景机位，衬托僵硬滑稽动作` | Awkward silence or R6 ragdoll flop |

## 4. Sound Effects & Caption Beats / 经典音效与字幕卡点

Pair each visual beat with tactile toy and retro game audio cues in post-production:

- **Plastic Clack (`清脆SmoothPlastic碰撞声`)**: when solid 1x2x1 block hands tap a desk, cup, or keyboard.
- **Classic "Oof" / Comic Thud (`经典闷响/摔倒声`)**: when an R6/chibi avatar tips over rigidly at 90 degrees.
- **Cartoon Boing (`弹簧Q弹声`)**: when oversized UGC cat ears, backpack, or springy hats bounce after a jump.
- **Vinyl Squeak (`轻微橡胶摩擦声`)**: when the cylindrical head rotates 45 degrees in deadpan silence.
- **Record Scratch + Bass Drop (`黑胶急停+重低音`)**: at the `11.5s` payoff twist or outfit swap cut.

## 5. Instant-Acting Grammar (`v1.7.0`) / 瞬间表演语法（眼神、眉型与道具关系）

Locking Roblox proportions solves *"does it look like Roblox?"*; viral retention also requires *"what is the character thinking in 0.5 seconds without reading captions?"*. Upgrade every beat from static role labels to **purposeful instant acting**:

1. **One Story Instant (`beatIntent` + `audienceRead`)**:
   Combine motion and decal into one causal reaction—e.g. *"spots the last empty seat while realizing the rival commuter noticed it too (`audienceRead`: both are about to sprint)"*.
2. **1st-Class Gaze & Asymmetrical Brows (`performance.gazeTarget` + `eyebrows`)**:
   Bind `gazeTarget` to a concrete `prop.id` or `castId` (`pupils tracking "empty_seat"`). Pair with `left-up-right-down` / `right-up-left-down` / `furrowed` / `worried` eyebrows and decoupled head/body orientation (e.g., torso leaning forward ready to run while pupils dart sideways at the rival).
3. **Camera-Facing Hand-Prop Interaction (`interaction`)**:
   Restrict prop actions to `hold | present | tap | slam | point | drop | receive`, always specifying `hand` (`right` | `left` | `both`), `contact` (`flush-flat`), and `visibility: "camera-facing"` so neither torso nor secondary actors occlude the key prop at mobile thumbnail scale.

