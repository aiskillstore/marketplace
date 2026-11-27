# Rescue and Anti-Drift Guide / 直播视角翻车诊断与防跑偏救场指南

When an AI-generated clip loses its livestream feel, melts UI text, or breaks character geometry, map the symptom to one of the **eight deterministic failure codes** below (`node scripts/drift_check.mjs --issue <code>`).

## 1. Eight-Symptom Diagnostic Matrix / 八大翻车速查表

| Issue Code | Observed Symptom / 翻车表现 | Root Cause / 根本原因 | Immediate Fix / 核心修复补丁 |
| --- | --- | --- | --- |
| `cinematic-drift` | 画面变成电影预告片摇臂远景或带上下黑边，毫无直播感 | 仅写了 `"livestream"`，未锁死物理摄像头焦段与支架位置 | 正向锁死具体采集设备（`locked 24mm monitor-top webcam` 或 `18mm arm's-length front selfie cam`），负向排除 `crane shot, 2.39:1 letterbox, f/1.2 bokeh` |
| `gibberish-ui` | 画面左下角出现外星乱码弹幕文字、融化的红心按钮或假台标 | 在扩散提示词里写了 `"TikTok live UI, scrolling comments"` | **彻底移除提示词内一切UI与弹幕文字描述**；声明 `clean raw camera feed, zero burned-in UI text`，用 `render_preview.mjs` 或 `studio/` 后置叠加无损HUD |
| `dead-fourth-wall` | 角色自顾自演戏完全不看镜头，像偷拍电影片段 | 缺少第四面墙互动动作与读弹幕眼神轴 | 插入 `0° direct lens eye-contact`、`15° off-axis chat-monitor glance` 或 `palm-backed 18cm autofocus showcase gesture` |
| `pip-hallucination` | 右上角主播小窗边框像果冻一样变形漂移，或大小窗动作串位 | 用单次裸跑 `T2V` 同时生成动态游戏画面与角落画中画 | 拆分为 **A轨（9:16主场景）+ B轨（固定28mm电竞房反应特写）** 独立生成后再合成圆角画中画 |
| `mic-flip-drift` | 切镜头后左下角的悬臂麦克风跑到右边，或背景灯带变色 | 跨镜头缺少首帧视觉锚点 | 先用 `rig_spec.mjs` 生成三态直播间参考卡锁死 `boom-left` 与RGB灯带色温，全片改用 **首帧 I2V** |
| `roblox-hand-lego-drift` | Roblox主播长出人类五指、乐高C型钩爪或地面长出乐高圆粒 | `"streamer holding mic/phone"` 触发真人手部或乐高先验 | 强制锁定 `2x2x1 torso, flush 1x2x1 legs, fingerless and clawless solid 1x2x1 rectangular block hands, smooth studless 1:1 barrel head, flat 2D decal face` |
| `action-overload` | 5秒内塞入4个连续动作导致肢体穿模，或中途从室内瞬移到街头 | 单镜动词超载或违背物理机位连续性 | 严守 **单镜单动作单机位预算**：每镜3.5–5秒仅执行1个核心动作，多步反转拆为4镜 |
| `watermark-leak` | 角落出现模糊变形的抖音/TikTok/Twitch/Roblox官方图标 | 正向词提到了具体平台名称触发训练集中带水印脏数据 | 正向词改用中性光学描述（`vertical 9:16 live camera plate`），将官方商标全部移入负向词 |

## 2. Before & After Rescue Examples / 救场前后对比实例

### Case 1: Rescuing Gibberish UI + Cinematic Drift (`gibberish-ui` + `cinematic-drift`)
- **Broken Prompt**:
  `A girl livestreaming on TikTok Live at a night market with scrolling comments, floating hearts, and viewer count in the corner, cinematic 85mm bokeh.`
- **Rescued Clean-Plate Prompt**:
  `9:16 vertical raw livestream camera plate, 18mm ultra-wide front-facing smartphone gimbal held at arm's length. Photorealistic street-food streamer in a denim jacket with a collar wireless lavalier mic extends her right arm toward the lens while holding a sizzling chili skewer 20cm from the camera with her flat left palm behind it to trigger macro autofocus. Direct 0° eye-contact into the front lens followed by a quick 8° downward glance at the phone screen, vibrant night-market neon stall spill and cool screen glow on face, clean camera feed, zero burned-in UI text, zero platform watermarks.`
- **Post-HUD Step**: Composite crisp `douyin` or `tiktok` chrome, `[钻粉 Lv.16]` danmaku, and `讲解中 ¥39.9` shopping card via `render_preview.mjs --platform douyin` or `studio/index.html`.

### Case 2: Rescuing Roblox PiP Gamer Melt (`pip-hallucination` + `roblox-hand-lego-drift`)
- **Broken Prompt (T2V)**:
  `Roblox streamer with headphones gripping mouse with five fingers in corner facecam while his character jumps obby blocks and falls.`
- **Rescued Dual-Track Split**:
  - **Track A (`9:16` Main Feed)**: `SmoothPlastic Roblox R6 runner (2x2x1 torso, flush 1x2x1 blocky legs, fingerless and clawless solid 1x2x1 block hands, 1:1 studless barrel head) clips a glowing red Killbrick before the finish flag and tumbles as a rigid plank.`
  - **Track B (`28mm` Locked Facecam)**: `Locked 28mm RGB bedroom webcam close-up with desk-slam shake: Roblox chibi-blocky streamer in cat-ear headset pivots both rigid 1x2x1 fingerless solid block arms down to slam the desk, flat 2D decal streaming blue waterfall tears.`
