---
name: omniailab-promo-h3-visual-design-music-direction-library
description: 「风格化音乐与声音方向库｜H3 15 秒执行规则」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：当最终视频需要保留原声音、使用用户上传音频，或用户希望有与包装风格匹配的音乐时读取。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 风格化音乐与声音方向库｜H3 15 秒执行规则

当最终视频需要保留原声音、使用用户上传音频，或用户希望有与包装风格匹配的音乐时读取。这里的音乐不是理论描述，而是给 H3 的“声音材料 + 节奏节点 + 字体/镜头响应”规则。

## 1. 音乐模式先判定，不增加默认必问

```text
MUSIC_MODE = preserve_original_audio | style_generated_instrumental | use_uploaded_audio_as_rhythm_reference | no_music
```

- 上传视频且用户没有要求改音乐：`preserve_original_audio`；原对白、环境声、剪辑节奏优先。
- 上传视频并明确“加配乐”：`style_generated_instrumental`；对白和关键动作保持清楚，音乐只做非叙事性铺底。
- 上传音频作为参考：`use_uploaded_audio_as_rhythm_reference`；只读取 BPM、拍点、重音、停顿和能量曲线，不擅自复制未授权歌词或旋律。
- 图片/纯文字生成且用户没有声音素材：默认 `style_generated_instrumental`；生成无歌词、无品牌口号的短 instrumental bed。用户说不要音乐时使用 `no_music`。
- 产品、人物、Logo、场景的图片架空或 AI 重建属于新生成视频，不能写 `Audio: N/A`；默认按已确认风格生成器乐，并让 cue 驱动字体角色、图形载体和构图状态。
- 口播风：默认保留原声，不默认新增音乐；但默认生成 3–5 个分散的克制触感音效，服务观点大字、素材卡、轻推近和版式换位。用户明确“不要新增音效”时才关闭，所有新声音都在说话时让位。

## 1A. 简单划分

把所有音乐先按听感分成四类，还是放在这一个 reference 里：

- 开场钩子型：前 0.0–1.5 秒先给一个记忆点，负责“有头”。适合标题、第一眼主视觉、第一句字幕或第一次落位。
- 节拍推进型：1.5–10 秒维持清楚 groove，负责“中段往前走”。适合字体反复出现、版式换位、镜头微动和素材切换。
- 收束落板型：13.5–15 秒必须收干净，负责“有尾”。最后一拍要有落板、落点或收口感，不能只是在同一段 groove 上硬停。
- 留白口播型：对白/字幕优先，音乐只在重音、卡片、轻推近和最终收尾上配短音效，不让整条片被音乐盖住。

简单对应：

- 清新可爱风：开场钩子 + 轻推进 + 柔和落板
- 科技粒子风：扫描开场 + 精准推进 + 干净落板
- 炫酷艺术风：折射开场 + 事件推进 + 暗场落板
- 暗黑胶片故障风：低频压迫开场 + 硬切故障推进 + 封面落板
- 海报大字拼贴风：纸条开场 + 版面推进 + 纸感落板
- 口播包装风：留白开场 + 语音推进 + 轻触落板

## 2. 15 秒统一音乐时间轴

所有风格先遵循这一条，再套用风格专属声音：

```text
0.0–1.5s  HEAD / establish the stage and product; sparse sound, one clear hook, no full-impact hit.
1.5–5.0s  BODY 1 / one clear pulse or texture entry triggers the first Hero or camera move.
5.0–10.0s BODY 2 / one contrast or layer change supports the second angle, macro or Keyword.
10.0–13.5s PEAK / strongest but short accent aligns with the main readable Hero; leave a readable hold.
13.5–15.0s TAIL / final landing or落板；remove extra layers, let the final product and exact text settle; no advertising sting.
```

每个主要文字事件只绑定一个音乐触发点：`beat/downbeat/impact/texture swell/speech stress/gesture contact`。不要让每个字都跟着每个鼓点跳动。没有可靠音乐拍点时，按动作或明确时间点触发。

把音乐写成 `COMPOSITION CUE SCORE`，而不是只给一个 BPM：

```text
COMPOSITION CUE SCORE:
- cue 1 / establish: [time]；建立主体、Display A 骨架和第一个 Carrier。
- cue 2 / takeover: [time]；触发第一次全屏 Hero 或色场接管。
- cue 3 / space change: [time]；触发主体/文字前后景交换、面板扩张或镜头穿过字腔。
- cue 4 / contrast: [time]；Display B 或第二颜色状态接管。
- cue 5 / resolve: [time]；各层回收，Display A/主体稳定共存。
```

13–15 秒通常写 4–6 个 cue；6–8 秒写 2–3 个。一个 cue 可以让 Hero、Carrier 和灯光作为一组同步落位，但只有一个最强声音瞬态。最后一个 cue 必须对应 landing / 落板，而不是继续堆新的层。

## 3. 风格专属音乐配方

### 清新可爱风｜Fresh Cute

```text
Music profile: light 4/4 instrumental, 100–118 BPM, soft marimba or plucked mallet, muted hand clap, small bell sparkle, warm rounded bass, no lyrics.
Energy: low at intro → gentle lift at first Hero → one buoyant accent → soft release.
Cues: soft pluck establishes Display A and the rounded frame; one rounded clap triggers a full-frame Hero/color-state takeover; a short mallet run lets Display B/doodles become the next panel; tiny bell only when dots/starbursts touch the exact word; final warm bass note settles the type cast.
Mix: keep transient accents short; no dense hi-hats, no aggressive sidechain, no childish vocal syllables.
```

音乐与画面：产品落台/轻浮起对应一次柔和低频，圆点或贴纸回弹对应一次短拍，结束时让旋律尾音和文字一起回收。推荐使用 `softbox sweep + sticker pop`，不要叠加多种音效。

### 科技粒子风｜Tech Particle

```text
Music profile: precise 4/4 electronic instrumental, 110–128 BPM, tight kick, controlled sub pulse, short metallic tick, granular noise sweep, one cold synth tone, no lyrics.
Energy: restrained pulse at intro → denser pulse during orbit → one clean impact for particle convergence → immediate decay.
Cues: rim scan establishes the spatial plane; particle convergence hits one downbeat; a short high-frequency tick switches solid Display A to outline Display B; one cold impact opens the type/frame portal; all particles return before the resolve cue.
Mix: preserve product detail and dialogue; avoid continuous glitch noise, fake HUD beeps and wall-to-wall distortion.
```

音乐与画面：冷青轮廓光扫到真实部件时进入短促 tick，粒子聚成 Hero 时只给一次干净 impact；不要每个粒子都配一个声音。

### 炫酷艺术风｜Cool Art

```text
Music profile: fused editorial electronic, 112–124 BPM, filtered air, restrained foil/plastic flex, thin glass tick, clean dry beat, muted sub, one tile-click cluster, one metallic tape snap, one deep 3D block hit, one narrow scan zap and one dry fracture crack, no lyrics or chanting.
Energy: sparse refractive establish → clean rhythmic subject/type interaction → dense event impact → brief silence and dark scan climax → low sub/glass release.
Cues: 0.0–2.6 foil flex + glass tick reveals the fold/card; 2.6–6.0 clean beat + tile clicks merges the mosaic and curves Display B; 6.0–9.2 tape snap + one block hit folds type into the event poster; 9.2–12.1 brief silence → scan zap → fracture crack triggers the dark scan response; 12.1–15.0 sub tail + glass settle locks the fused poster.
Mix: play these cues sequentially, never simultaneously; every transient belongs to one visible fold, tile, type block, scan line or subject contact. No continuous glitch bed, wall-to-wall distortion, crowd chant, trailer boom or generic cinematic riser.
```

音乐与画面：声音跟随同一条“折痕 → 网格 → 字块 → 扫描 → 终版”链路；Hero 先完整可读，声音瞬态结束前所有故障、折射和像素错位回到稳定。

### 暗黑胶片故障风｜Dark Pop Glitch

```text
Music profile: dark-pop / cyber-grunge instrumental, 78–96 BPM half-time or 120–144 BPM trap feel, deep descending synth, distorted 808, tape hiss, close breath, film projector rattle, dry industrial metal hit, short reverse inhale, narrow scan zap, one exposure-flash hit, no lyrics except user-confirmed spoken line.
Energy: still pressure → first heavy scan tear → zine hard-cut attack → one red sub impact → empty low-frequency aftershock and cover landing.
Cues: 0.0–3.0 low synth descent + tape hiss establishes the still frame and readable wordmark; 3.0–6.0 distorted 808 + scan zap triggers one 2–4-frame tear and restores; 6.0–10.0 dry metal hit + film rattle supports 2–4-frame inserts; 10.0–13.0 strongest sub impact + exposure flash triggers red particle/registration shock; 13.0–15.0 music drops out to sub tail, then one dry camera/flash hit locks the magazine cover.
Mix: keep every glitch sound short and tied to a visible cut, scan, offset, particle burst or cover lock. No continuous glitch bed, EDM riser, crowd chant, trailer boom, neon synth arpeggio or random stutter.
```

音乐与画面：故障声不是氛围铺底，而是“触发器”。每次 scan zap、808、金属撞击或闪光命中一个明确视觉事件，事件结束时主体、Logo/字标和主标题都恢复清晰。若保留原视频声音，新增声音只在包装层低电平叠加。

### 海报大字拼贴风｜Poster Collage

```text
Music profile: tactile 4/4 instrumental, 90–108 BPM, dry drum break, muted bass, paper rustle, typewriter or print-click texture, one brass/wood hit, no lyrics.
Energy: measured tabletop rhythm → layered print accents → one strong collage snap → quiet paper release.
Cues: paper strip/panel assembly follows a short drum fill; full-frame Display A landing makes one dry thump; a small brush/brass hit introduces Display B; registration shift uses a tiny click; one panel expands on the strongest collage snap; final paper/frame retracts on the last bar.
Mix: keep paper and print textures local and quiet; avoid cinematic orchestra, generic riser and continuous vinyl crackle.
```

音乐与画面：纸条从已有纸缝滑出时用短 drum fill，套印偏移只用一次 click，撕纸边回收时让纸张摩擦声自然消失。音乐不能把产品变成平面插画。

### 口播包装风｜Talking Head

```text
Music profile: no new music by default. If the user explicitly asks for music, use an optional low-density instrumental bed at 80–100 BPM with soft pad or muted pluck, no competing melody, no lyrics and no vocal chops.
Sound palette: choose 3–5 total cues from soft tick / paper flick / muted thump / air swipe / restrained UI click. Keep every transient short, tactile and quieter than speech.
Energy: stable under the voice; one accent only at a real spoken stress, card arrival, editorial punch-in, layout swap, mini-head corner inset or visible gesture; leave clean breathing gaps.
Cues: each of the two or more Keyword Heroes must have one audible muted thump/click 0.05–0.12s before the speech stress; Evidence Card must have one paper flick or restrained UI click; the mini-head corner inset may use one short air swipe or soft tick; 2%–3% punch-in may use one short air swipe; frame/divider settle may use one soft tick. Write the exact event→time→cue map and do not score every word.
Mix: dialogue and original room tone stay in front; duck all non-diegetic sound under important words, preserve the original voice character, and do not add an advertising sting.
```

如果是锁定原片，原音乐与对白不改，只在包装层上叠加 3–5 个低电平短音效；如果是二创但保留原声，新增音乐只在空白段落轻轻铺底。字幕、观点大字、卡片、轻推近和版式换位必须由真实语音时间点驱动，而不是由音乐强行切断口型。用户明确不要新增音效时，不添加任何非原声瞬态。

## 4. 声音到字体/镜头的可执行映射

```text
MUSIC_CUE_MAP:
- cue_source: [downbeat / snare / impact / texture swell / speech stress / gesture contact]
- time: [exact time]
- camera_response: [one camera change or preserve original camera]
- product_response: [one visible product/light response or N/A]
- type_response: [Display A/B/Utility/Marks 的组合进入、尺度、切片、描边或扫描]
- carrier_response: [frame/panel/strip/grid/color field 的进入或接管]
- reset: [exact time or musical decay where all extra layers settle]
```

正确示例：

```text
At 3.6s, one dry kick lands with the product's 3/4 turn. The Hero "[TEXT]" is already fully readable; compress its width by 10% once, hold the complete spelling, then restore by 4.2s. The kick tail fades; no second type event starts.
```

错误示例：

- “配一段很燃的音乐，让所有字跟着节奏炸开。”
- “随机加入鼓点、音效和电子噪声。”
- “每个粒子都配一个声音。”

## 5. 最终 Prompt 音乐块

```text
MUSIC / AUDIO:
Mode: [preserve_original_audio / style_generated_instrumental / use_uploaded_audio_as_rhythm_reference / no_music].
Profile: [style-specific BPM range, meter, instruments/textures, energy curve, no lyrics].
15-second cues: 0.0–1.5 [intro]; 1.5–5.0 [first cue]; 5.0–10.0 [second cue]; 10.0–13.5 [Hero cue]; 13.5–15.0 [release].
Sync: bind each major type/camera event to one cue_source and exact time. Keep dialogue, room tone and product detail audible. No invented lyrics, brand sting, CTA or random sound effects.
```

口播在 `Mode=preserve_original_audio` 下追加：`Editorial SFX MAP: [exact time] → [Keyword Hero / Evidence Card / editorial punch-in / layout swap] → [soft tick / paper flick / muted thump / air swipe / restrained UI click] → [dialogue ducking and recovery]`. 全片 3–5 个可听见的低电平短音效，其中两个必须对应不同 Keyword Hero，一个对应 Evidence Card；对白至少高出每个 cue 一个清晰混音层，不做逐字音效。

如果没有音乐或用户明确不需要，写：`MUSIC_MODE=no_music. Non-diegetic music: N/A. Do not add background music.`

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
