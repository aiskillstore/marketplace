# Model Prompt Playbook / 七大主流视频生成模型纯净直播底片手册

Different AI video diffusion models interpret camera mounts, autofocus shifts, and multi-panel layouts differently. Always pair **First-Frame I2V (`首帧图生视频`)** with **Clean-Plate Prompts (`零文字纯净底片`)** and composite platform HUDs afterward.

## 1. Engine Comparison & Recommended Settings

| Engine | Best Mode | Clip Length | Camera & Rig Syntax | Recommended Settings |
| --- | --- | --- | --- | --- |
| **Kling (可灵 1.6 / 2.0)** | I2V (Master / High Quality) | 5s | Natural Chinese/English physical mount phrases (`固定24mm显示器摄像头`, `一臂距离18mm前置自拍跟走`) | Creativity `0.40–0.50`, Motion `Medium`, Negative prompt enabled |
| **Seedance / Jimeng (即梦视频)** | I2V / 首尾帧控制 | 4s–5s | Concise Chinese optical + focus clause (`35mm桌面固定机位，手掌托底触发微距自动对焦`) | Lock first frame (and loop end frame when needed); single physical action |
| **Hailuo MiniMax (海螺 Director)** | I2V-01-Director | 6s | Bracketed camera tags at prompt start: `[Static shot]`, `[Push in]`, `[Pull out, Shake]`, `[Tilt down]` | Use `[Static shot]` for webcams and `[Shake]` only on desk-slam / jump-scare beats |
| **Wan 2.6 (通义万相 14B)** | I2V / T2V | 5s | Explicit `9:16竖屏 + 机位焦段 + 补光眼神光 + 单步互动动作` | CFG `5.0–6.0`; always supply explicit negative prompt blocking UI text & extra fingers |
| **Sora** | I2V / Storyboard | 5s–10s | Physical capture simulation (`Physical Livestream Capture: 16mm chest-mounted action camera...`) | Lock rigid `Motor6D` hinges when using `--style roblox-blocky` |
| **Veo 3** | I2V / Native Audio T2V | 6s | Clean-plate visual prompt + `Live Audio:` clause (`close-mic lavalier voice, sizzling street stall, room acoustics`) | Never ask Veo to render on-screen chat text; let Veo generate close-mic room audio |
| **Runway Gen-4** | I2V | 5s | `Camera: [mount + lens]. Subject & Action: [single beat].` | Keep camera locked for `desktop-webcam` and `overhead-showcase-rig` |

## 2. Clean-Plate Prompt Formulas by Rig

### Formula A: Handheld IRL / Genre Selfie (`handheld-selfie-irl`)
- **English**:
  `18mm ultra-wide front-facing smartphone gimbal lens held at arm's length (60cm). Subject: [Style & Host Lock] extending right arm toward the lens, walking past [Environment]. Action: [Single Live Action]. Eye-line: direct 0° front-camera eye-contact with a quick 8° downward glance checking phone-screen chat. Lighting: [Neon / Daylight + Phone Screen Fill]. 9:16 vertical raw livestream camera plate, clean camera feed, zero burned-in UI text, zero watermarks.`
- **中文（可灵 / 即梦 / 万相）**:
  `9:16竖屏，18mm超广角手机前置云台一臂距离（60厘米）自拍机位。主体：[画风与主播设定]，右臂自然前伸持机边走边拍。单一动作：[单步互动动作]。眼神轴：0°直视前置镜头喊话，顺势向下偏8°扫一眼手机屏幕弹幕。补光：[环境光 + 手机屏幕冷白面部补光]。100%纯净无UI文字底片，严禁乱码弹幕与平台水印。`

### Formula B: Monitor Webcam & Desk Showcase (`desktop-webcam` / `overhead-showcase-rig`)
- **English**:
  `Locked 24mm monitor-top webcam (6° downward angle, deep f/4.5 room focus), matte-black condenser boom mic locked at lower-left edge. Subject: [Style & Host Lock] seated at studio desk with circular LED ring-light catchlights in the eyes. Action: [Single Action / Palm-Backed 18cm Autofocus Gesture]. Eye-line: switches from 15° off-axis chat-monitor glance back to 0° direct webcam lens. Clean raw camera feed, zero UI overlays.`

### Formula C: Dual-Track PiP Gameplay & 50/50 PK Split (`pip-facecam-rig` / `pk-cohost-split`)
- **Track A (Main 9:16 World/Game)**: Compile and render as a standalone full-screen `9:16` clip.
- **Track B (Corner Streamer Facecam)**: Compile as a locked `28mm` RGB bedroom close-up synced to the same 4 emotional beats (`smirk` → `focused lean-in` → `O_O shock` → `desk-slam meltdown`), then composite in rounded PiP frame via `render_preview.mjs` or `studio/index.html` / NLE.
