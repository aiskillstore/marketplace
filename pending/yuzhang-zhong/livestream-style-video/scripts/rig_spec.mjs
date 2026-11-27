#!/usr/bin/env node
/**
 * rig_spec.mjs
 * Zero-dependency CLI generator for Livestream Camera Rig + Orthogonal Visual Style DNA cards,
 * 3-state Streamer/Scene Setup Reference Prompts (0° Lens / 15° Chat-Read / Side Rig Layout),
 * Dual-Track PiP/PK Setup Specs, and Anti-Drift Negative Prompts.
 */

import fs from "node:fs";
import path from "node:path";

export const SUPPORTED_LANGS = new Set([
  "en",
  "zh",
  "zh-tw",
  "ja",
  "ko",
  "es",
  "fr",
  "de",
  "pt",
  "ru",
  "zh-en"
]);

export function normalizeLang(code = "en") {
  const clean = String(code || "en").toLowerCase().trim();
  if (clean === "zh-cn") return "zh";
  if (clean === "pt-br") return "pt";
  return SUPPORTED_LANGS.has(clean) ? clean : "en";
}

export const RIG_PROFILES = {
  "desktop-webcam": {
    labelEn: "Monitor-Top / Desk Ring-Light Webcam Rig",
    labelZh: "桌面固定广角摄像头 / 环形灯主播机位",
    lensEn: "24mm–28mm webcam optics, 5–8° slight downward monitor-top angle, deep f/4.5 room focus",
    lensZh: "24mm–28mm广角桌面摄像头光学，显示器顶端5°–8°微俯拍，f/4.5清晰房间景深（不虚化死背景）",
    physicsEn: "locked tripod/monitor mount; zero camera pan, subtle high-frequency desk-thump micro-vibration only on physical desk impact",
    physicsZh: "显示器/桌面支架刚性锁死，零推拉摇移，仅在拍桌瞬间产生真实高频桌面微震",
    eyeLineEn: "alternates between direct 0° webcam lens eye-contact and crisp 15° off-axis glance toward secondary chat monitor",
    eyeLineZh: "在0°直视主摄像头对视与15°偏轴扫视副屏弹幕之间自然切换",
    defaultLighting: "ring-rgb-studio",
    defaultMic: "boom-left"
  },
  "handheld-selfie-irl": {
    labelEn: "Arm's-Length Ultra-Wide Handheld Selfie / Gimbal IRL Rig",
    labelZh: "手持自拍杆 / 口袋云台超广角户外移动直播机位",
    lensEn: "18mm–20mm ultra-wide front-facing smartphone or pocket gimbal lens at arm's length (55–70cm), slight perspective foreshortening",
    lensZh: "18mm–20mm超广角手机前置/口袋云台一臂距离（55–70cm）自拍透视，带轻微近大远小畸变",
    physicsEn: "coupled to host's extended arm and footsteps: natural walking bob, slight horizon roll on sudden turns, brief auto-exposure shift across light zones",
    physicsZh: "机位与主播伸出的持机手臂物理绑定：随步伐自然呼吸起伏，急转身带轻微水平倾角与自动曝光过渡",
    eyeLineEn: "host looks directly into the held front lens while walking, occasionally glancing 8° down at the phone screen chat area",
    eyeLineZh: "主播边走边直视手持前置镜头互动，偶而向下偏8°扫视手机屏幕下半区滚动弹幕",
    defaultLighting: "night-neon-irl",
    defaultMic: "lavalier"
  },
  "pip-facecam-rig": {
    labelEn: "Dual-Track Gameplay / World Feed + Corner Streamer Facecam (PiP)",
    labelZh: "实况主画面 + 右上/左下主播反应小窗双轨机位 (PiP)",
    lensEn: "Track A (Main 9:16): active game/world camera; Track B (PiP Corner): locked 28mm RGB studio webcam close-up on streamer with headset",
    lensZh: "A轨（9:16主画面）：实况场景/游戏内镜头；B轨（角落画中画小窗）：28mm固定RGB电竞房主播特写机位",
    physicsEn: "strictly dual-track composited: generate Track A and Track B as clean independent plates (or locked I2V split) so PiP border never melts",
    physicsZh: "严格双轨分层生成后合成（或首帧锁定画中画边框I2V），杜绝单次文生视频导致小窗漂移融化",
    eyeLineEn: "streamer in PiP focuses intensely on main screen glow, snapping 0° into facecam during clutch wins or rage desk-slams",
    eyeLineZh: "小窗主播紧盯屏幕反光操作，在神操作或破防瞬间猛转0°怼脸直视摄像头",
    defaultLighting: "ring-rgb-studio",
    defaultMic: "headset-mic"
  },
  "overhead-showcase-rig": {
    labelEn: "45° Desk-Clamp / Beauty-Tech Autofocus Showcase Rig",
    labelZh: "桌面带货 / 开箱微距对焦手势展示机位",
    lensEn: "35mm clean desk-clamp camera with fast continuous autofocus (AF-C), ring-light circular specular reflections on held item",
    lensZh: "35mm俯拍/平视桌面夹持机位，快速连续自动对焦（AF-C），环形补光灯在展示物表面形成清晰圆环高光",
    physicsEn: "locked C-stand desk mount; subject brings product within 20cm of lens with flat palm behind it ('influencer autofocus gesture') shifting background softly",
    physicsZh: "桌面C型支架完全固定；主播将物品递至距镜头20cm处并以手掌托底触发网红微距对焦切换",
    eyeLineEn: "host alternates between inspecting the held object, pointing at details toward the lens, and checking off-screen iPad comment feed",
    eyeLineZh: "主播视线在手中展示物、0°主镜头指点细节与侧方平板弹幕屏之间精准切换",
    defaultLighting: "clean-beauty-softbox",
    defaultMic: "lavalier"
  },
  "chest-head-pov": {
    labelEn: "First-Person Chest / Head-Strap Action-Cam Live POV",
    labelZh: "第一人称胸挂 / 头戴运动相机探险直拍机位",
    lensEn: "16mm ultra-wide action-cam rectilinear/mild barrel lens, deep focus f/5.6, both hands of the streamer visible entering lower frame",
    lensZh: "16mm超广角运动相机第一视角，f/5.6大景深，主播双手从画面下沿自然伸入互动",
    physicsEn: "organic breathing rise-and-fall, crisp footstep shock, flashlight beam or held secondary chat-phone moving synchronously with torso/hands",
    physicsZh: "真实胸腔呼吸起伏与脚步震动反馈，右手手电筒光束或左手弹幕副机随身体同步晃动",
    eyeLineEn: "camera IS the streamer's eyes/chest: tilts down to check live chat on held smartphone in left hand, then whips up toward sound source",
    eyeLineZh: "镜头即主播本人视角：低头瞥一眼左手手机屏幕亮光，再猛地抬头对准前方异响源",
    defaultLighting: "flashlight-dim-exploration",
    defaultMic: "lavalier"
  },
  "pk-cohost-split": {
    labelEn: "50/50 Dual-Host Co-Stream / PK Versus Split-Screen Rig",
    labelZh: "双人连麦 PK 对称分屏直播机位",
    lensEn: "Two locked 24mm–28mm studio webcams framed in symmetric 50/50 split rooms with contrasting color temperatures (e.g. warm pink vs cool cyan)",
    lensZh: "上下或左右对称50/50双直播间固定28mm摄像头，两间房采用冷暖对比补光以强化连麦跨屏感",
    physicsEn: "both webcam frames remain locked independently; hosts lean toward the shared seam or slam desks in synchronized reaction",
    physicsZh: "两侧独立固定机位互不干扰，双方朝分屏中缝前倾喊话或同步破防后仰",
    eyeLineEn: "each host switches between 0° camera address and looking across/up-down toward the co-host's panel",
    eyeLineZh: "两位主播在0°直视各自观众与看向连麦对方分屏方向之间交替互动",
    defaultLighting: "ring-rgb-studio",
    defaultMic: "boom-left"
  },
  "cctv-obs-fixed": {
    labelEn: "High-Corner Fixed CCTV / 24x7 Room Slow-Live Cam",
    labelZh: "房间高处监控 / 24小时无人值守慢直播固定机位",
    lensEn: "20mm wide ceiling-corner security/OBS room cam at 25–30° downward pitch, infinite depth of field f/8, entire room geometry visible",
    lensZh: "20mm房间高角25°–30°俯视广角固定机位，f/8全景深覆盖全屋陈设",
    physicsEn: "100% bolted static frame; zero operator pan/zoom—all comedy or tension comes from characters/pets entering and exiting the fixed frame",
    physicsZh: "100%螺丝锁死静止画框，零人工运镜，张力完全来自角色/宠物闯入或离开固定画面",
    eyeLineEn: "mostly unguarded candid behavior until subject suddenly remembers the live cam is on and freezes looking up into the top corner lens",
    eyeLineZh: "前半程自然忘我状态，突发状况后猛然想起正在直播，抬头盯向墙角摄像头社死定格",
    defaultLighting: "warm-desk-lamp",
    defaultMic: "none"
  },
  "drone-follow-live": {
    labelEn: "Live Outdoor Follow-Gimbal / Broadcast Cameraman Rig",
    labelZh: "户外跟拍导播员 / 低空跟随直播机位",
    lensEn: "24mm stabilized handheld gimbal or low-altitude follow-drone 2–3m from host, live broadcast dynamic exposure",
    lensZh: "24mm跟拍云台或低空跟随无人机（距主播2–3米），现场纪实自动曝光",
    physicsEn: "realistic live cameraman lag: 0.2s framing catch-up when subject sprints or pivots unexpectedly, quick whip-reframe onto action",
    physicsZh: "真实直播摄影师跟拍延迟：主角突然冲刺或转身时镜头有0.2秒追焦滞后与快速甩镜重构图",
    eyeLineEn: "host talks over shoulder to the following camera operator while moving forward into the scene",
    eyeLineZh: "主播边向场景深处行进边回头朝跟拍镜头喊话解说",
    defaultLighting: "daylight-outdoor-autoexp",
    defaultMic: "lavalier"
  }
};

export const STYLE_ADAPTERS = {
  "realistic-irl": {
    labelEn: "Photorealistic IRL / General AI Video",
    labelZh: "写实真人 / 通用基础 AI 视频画风",
    geometryLockEn:
      "natural photorealistic human proportions and micro-skin texture, authentic five-finger hand anatomy with firm natural grip on phone/mic/props, real fabric folds, realistic smartphone/webcam sensor dynamic range",
    geometryLockZh:
      "自然写实真人比例与真实皮肤微纹理，标准五指自然持握手机/麦克风/道具，真实衣物褶皱与手机/摄像头传感器动态范围",
    antiDriftNegativeEn:
      "waxy plastic AI doll skin, extra six fingers, fused fingers, floating wireless props, Hollywood 2.39:1 black letterbox bars, anamorphic blue cinema flares, burned-in gibberish TikTok UI text",
    antiDriftNegativeZh:
      "塑料假人磨皮感，六指/多指畸形，道具悬空穿模，电影宽银幕黑边，变形宽银幕蓝光眩光，烘死在画面里的乱码直播间弹幕文字"
  },
  "roblox-blocky": {
    labelEn: "Canonical Roblox R6 / Chibi-Blocky Avatar Style",
    labelZh: "纯正 Roblox R6 / 盲盒方块小人直播画风",
    geometryLockEn:
      "authentic 3D Roblox SmoothPlastic avatar: canonical 2x2x1 chamfered rectangular torso, two flush 1x2x1 rectangular leg blocks matching exact torso width (zero thigh gap), fingerless and clawless solid 1x2x1 beveled rectangular block hands, smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal (zero 3D nose), rigid Motor6D mechanical hinge joints, smooth studless SmoothPlastic/WoodPlanks floors and multi-part streaming props",
    geometryLockZh:
      "纯正3D Roblox SmoothPlastic方块小人：标准2x2x1倒角长方体躯干、两条并拢同宽1x2x1方柱腿（无腿缝）、无人类五指且无乐高C型爪的1x2x1实心平头方柱手、头顶平滑无凸粒1:1桶状圆角头、纯平2D丝网印刷表情贴图（零3D鼻子凸起）、刚性Motor6D机械转轴关节、平滑无凸粒地板与多部件直播道具",
    antiDriftNegativeEn:
      "human fingers, five-finger hands, Lego C-shaped claw hooks, raised circular Lego floor/head studs, Minecraft sharp 8x8x8 pixel voxel head, 3D protruding human nose, rubbery noodle limbs, official Roblox tilted-square logo, burned-in gibberish UI text",
    antiDriftNegativeZh:
      "人类五指，乐高C型夹爪手，乐高头顶与地面凸起圆颗粒，我的世界直角像素方头，3D真人鼻梁，面条状软体弯曲手臂，官方Roblox倾斜方框商标，画面内烘死的乱码弹幕UI"
  },
  "anime-vtuber": {
    labelEn: "2D Cel-Shaded Anime / Live2D & 3D VTuber Style",
    labelZh: "二次元赛璐璐 / Live2D 虚拟主播画风",
    geometryLockEn:
      "crisp cel-shaded 2D/2.5D anime streamer aesthetic, clean ink linework, expressive anime iris catchlights, bouncy hair physics synced to head-tracking sway, clean anime streaming room or Live2D bust framing",
    geometryLockZh:
      "清爽二次元赛璐璐/2.5D虚拟主播画风，干净线稿与高光瞳孔眼神光，随头部面捕摆动自然弹跳的发丝物理，整洁二次元直播间背景",
    antiDriftNegativeEn:
      "uncanny semi-realistic 3D face, photorealistic skin pores, smudged line-art, extra fingers, garbled floating chat text",
    antiDriftNegativeZh:
      "恐怖谷半写实3D脸，写实毛孔，线稿糊化崩坏，多指畸形，乱码漂浮弹幕文字"
  },
  "stylized-3d": {
    labelEn: "Tactile Blind-Box Vinyl / Pixar-Grade 3D Stylized",
    labelZh: "潮玩盲盒皮克斯级 3D 卡通画风",
    geometryLockEn:
      "tactile subsurface-scattered matte vinyl & plush 3D stylized character, appealing 3-head chibi-stylized proportions, clean four/five-finger stylized hands, miniature studio streaming desk props with soft global illumination",
    geometryLockZh:
      "细腻微透光哑光潮玩/皮克斯级3D卡通角色，讨喜三头身比例，干净利落的卡通手部造型，精致微缩直播台道具与柔和全局光照",
    antiDriftNegativeEn:
      "uncanny photorealistic human face, sharp voxel cubes, Lego studs, muddy textures, burned-in gibberish UI overlays",
    antiDriftNegativeZh:
      "写实真人恐怖谷脸，像素马赛克方块，乐高圆粒，脏污贴图，乱码UI水印"
  },
  "voxel-sandbox": {
    labelEn: "Crisp 8x8x8 / 16x16x16 Voxel Sandbox Style",
    labelZh: "硬朗 8×8×8 / 16×16×16 体素像素沙盒直播画风",
    geometryLockEn:
      "canonical voxel character with sharp 1:1:1 cubic 8x8x8 head, 8x12x4 torso, fingerless flat 4x4 square pixel-block hands, unfiltered nearest-neighbor 16x16 pixel block textures, +0.5px 3D headset/hoodie outer skin layer, and extruded pixel mic/tools",
    geometryLockZh:
      "标准体素小人（直角8x8x8立方头、8x12x4躯干、无手指4x4平头像素方手、+0.5px立体耳机卫衣外层皮肤、清晰邻近采样16x16像素贴图与立体像素麦克风道具）",
    antiDriftNegativeEn:
      "human fingers, bilinear blurry textures, rounded Roblox cylindrical head, Lego studs or C-claws, smooth round metal rods, burned-in gibberish UI",
    antiDriftNegativeZh:
      "人类五指，双线性模糊贴图，圆角桶状头，乐高圆粒或C型爪，光滑圆棍道具，乱码弹幕UI"
  },
  "cinematic-genre-adapt": {
    labelEn: "Cross-Genre / Period / Fantasy / Sci-Fi Diegetic Livestream",
    labelZh: "古风仙侠 / 科幻 / 奇幻 / 悬疑架空剧情跨次元直播化",
    geometryLockEn:
      "high-detail genre costume and world architecture (wuxia cloud peaks, medieval dungeon, or cyberpunk rooftop) shot strictly through an intimate first-person selfie/visor/talisman live lens—preserving raw handheld immediacy, wind-whipped hair, direct viewer address, and unscripted live timing rather than detached movie framing",
    geometryLockZh:
      "高细节类型片服化道与宏大场景（仙侠云海、古堡地牢或赛博天台），但严格通过贴脸自拍法器/战术面罩/手持直拍镜头呈现——保留迎风碎发、怼脸向观众喊话与突发抓拍的野生直播临场感，拒绝疏离的传统电影旁观机位",
    antiDriftNegativeEn:
      "detached third-person movie trailer shot, widescreen 2.39:1 cinema bars, actors ignoring camera, slow-motion epic crane sweep, burned-in gibberish UI text",
    antiDriftNegativeZh:
      "疏离的第三人称电影预告片空镜，宽银幕上下黑边，角色无视镜头演戏，慢动作史诗摇臂大远景，画面内烘死的乱码UI"
  }
};

export const LIGHTING_PRESETS = {
  "ring-rgb-studio": {
    labelEn: "Circular Ring-Light Key + Cyan/Magenta RGB Wall Rim",
    labelZh: "环形补光灯主光（圆形眼神光）+ 青品双色 RGB 电竞背景轮廓光",
    promptEn: "front circular LED ring-light creating crisp ring catchlights in the eyes, cool monitor glow on desk, cyan and magenta RGB neon strip accents on back wall",
    promptZh: "正面环形补光灯打出清晰圆环眼神光，屏幕冷光映亮桌面，背景墙点缀青色与品红RGB氛围灯带"
  },
  "night-neon-irl": {
    labelEn: "Night Street Neon Spill + Phone Screen Face Fill",
    labelZh: "夜市/街头霓虹环境光 + 手机屏幕近距冷白面部补光",
    promptEn: "vibrant night-street neon signage bokeh in mid-ground, cool-white smartphone screen glow illuminating the host's face from arm's length, natural night auto-ISO texture",
    promptZh: "中景街头霓虹灯牌流光溢彩，一臂距离的手机屏幕冷白光自然照亮主播面部，真实夜间手机自动曝光质感"
  },
  "warm-desk-lamp": {
    labelEn: "Cozy Late-Night Warm Desk Lamp + Cool Monitor Spill",
    labelZh: "深夜暖黄护眼台灯 + 显示器冷蓝屏幕反光",
    promptEn: "warm 3000K architectural desk lamp pool paired with cool 6500K monitor screen glow across keyboard and hands, quiet cozy late-night room atmosphere",
    promptZh: "3000K暖黄台灯光晕搭配6500K显示器冷蓝屏幕光洒在键盘与手部，静谧深夜陪伴直播氛围"
  },
  "clean-beauty-softbox": {
    labelEn: "High-CRI Dual Softbox E-Commerce / Unboxing Lighting",
    labelZh: "高显色双柔光箱带货 / 微距开箱透亮布光",
    promptEn: "bright high-CRI dual studio softbox + ring-light illumination, crisp specular highlights on product packaging, clean clutter-free studio counter",
    promptZh: "高显色度双柔光箱配合环形灯通透布光，商品材质高光锐利清晰，干净整洁直播台面"
  },
  "flashlight-dim-exploration": {
    labelEn: "Handheld Flashlight Cone + Dim Corridor Practical Sconces",
    labelZh: "手持强光手电筒光束 + 幽暗走廊闪烁壁灯",
    promptEn: "tight volumetric handheld flashlight beam cutting through dim ambient corridor shadows, faint blue smartphone chat-screen spill on left hand",
    promptZh: "凝聚的手持强光手电筒光束切开幽暗走廊阴影，左手弹幕手机屏幕泛出微弱冷蓝光"
  },
  "daylight-outdoor-autoexp": {
    labelEn: "Crisp Outdoor Daylight / Cloud-Sea Sunlight with Live Auto-Exposure",
    labelZh: "户外自然日光 / 云海天光 + 运动直播实时自动曝光",
    promptEn: "crisp natural daylight rim-lighting windblown silhouettes, authentic action-cam auto-exposure highlight roll-off",
    promptZh: "通透自然日光勾勒迎风轮廓，真实运动相机/手机直出自动曝光高光过渡"
  }
};

export const HUD_MODES = {
  "clean-post-hud": {
    labelEn: "Clean Diffusion Plate + Deterministic Post-Composited Live HUD (Recommended)",
    labelZh: "纯净无字生成底片 + 后置确定性直播间 HUD 叠加（强烈推荐）",
    ruleEn:
      "Generate 100% UI-free raw video frames in Kling/Seedance/Sora/Wan (`clean camera feed, zero text/HUD`), then overlay crisp localized LIVE badge, viewer counter, scrolling chat pills, and PiP/PK frames via `render_preview.mjs` or video editor.",
    ruleZh:
      "在可灵/即梦/Sora/万相中生成100%无UI文字的纯净底片（严禁AI直出弹幕防乱码），再通过 `render_preview.mjs` 或剪辑软件无损叠加高清 LIVE 角标、在线人数、滚动弹幕与PK条。"
  },
  "minimal-diegetic": {
    labelEn: "Minimal Diegetic World Cues Only (<=3 ASCII Words)",
    labelZh: "极简场景内原生提示（仅限 <=3 词英文气泡或纯图标）",
    ruleEn:
      "Keep screen borders clean; allow at most a crisp 1–3 word ASCII speech bubble (e.g. Roblox `BillboardGui` `'CHAT?!'`) or physical Tally REC red LED.",
    ruleZh:
      "保持画框四周净空，仅允许场景内红点录制灯或不超过3个英文单词的头顶气泡（如 Roblox `BillboardGui`）。"
  },
  "raw-clean": {
    labelEn: "100% Raw Camera Feed Only (Zero Overlay)",
    labelZh: "纯裸机直出底片（不叠加任何直播间浮层）",
    ruleEn: "Pure physical webcam/selfie camera feed relying solely on framing, eye-contact, and audio for livestream feel.",
    ruleZh: "完全依靠机位光学、眼神对视与收音麦传达直播感，不添加任何UI浮层。"
  }
};

const MIC_LABELS = {
  "boom-left": {
    en: "matte-black condenser boom microphone arm entering cleanly from the lower-left edge with foam pop filter (locked to screen-left across all shots)",
    zh: "哑光黑悬臂电容麦克风配防喷棉从画面左下角伸入（全片跨镜头严格锁死左侧，严禁左右乱跳）"
  },
  "boom-right": {
    en: "matte-black condenser boom microphone arm entering cleanly from the lower-right edge with shock mount (locked to screen-right across all shots)",
    zh: "哑光黑悬臂电容麦克风从画面右下角伸入（全片跨镜头严格锁死右侧）"
  },
  lavalier: {
    en: "compact clip-on wireless lavalier microphone transmitter clipped to collar/lapel",
    zh: "衣领处夹持一枚紧凑型无线领夹麦克风发射器"
  },
  "headset-mic": {
    en: "over-ear RGB gaming/studio headset with curved boom mic positioned near left cheek",
    zh: "头戴式RGB电竞/监听大耳机，弯曲麦杆固定于左脸颊旁"
  },
  none: {
    en: "built-in ambient camera mic (no visible microphone prop)",
    zh: "机身内置收音（画面内不出现外置麦克风道具）"
  }
};

export function parseArgs(argv) {
  const opts = {
    rig: "desktop-webcam",
    style: "realistic-irl",
    lighting: "",
    hud: "clean-post-hud",
    host: "Alex",
    cohost: "Momo",
    mic: "",
    robloxRig: "chibi-blocky",
    lang: "en",
    out: "",
    json: false,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") opts.help = true;
    else if (a === "--json") opts.json = true;
    else if (a === "--rig" && argv[i + 1]) opts.rig = argv[++i].toLowerCase().trim();
    else if (a === "--style" && argv[i + 1]) opts.style = argv[++i].toLowerCase().trim();
    else if (a === "--lighting" && argv[i + 1]) opts.lighting = argv[++i].toLowerCase().trim();
    else if (a === "--hud" && argv[i + 1]) opts.hud = argv[++i].toLowerCase().trim();
    else if (a === "--host" && argv[i + 1]) opts.host = argv[++i].trim();
    else if (a === "--cohost" && argv[i + 1]) opts.cohost = argv[++i].trim();
    else if (a === "--mic" && argv[i + 1]) opts.mic = argv[++i].toLowerCase().trim();
    else if (a === "--roblox-rig" && argv[i + 1]) opts.robloxRig = argv[++i].toLowerCase().trim();
    else if (a === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
    else if (a === "--out" && argv[i + 1]) opts.out = argv[++i];
  }
  return opts;
}

export function buildRigSpec(input = {}) {
  const rigId = RIG_PROFILES[input.rig] ? input.rig : "desktop-webcam";
  const styleId = STYLE_ADAPTERS[input.style] ? input.style : "realistic-irl";
  const rig = RIG_PROFILES[rigId];
  const style = STYLE_ADAPTERS[styleId];

  const lightingId = LIGHTING_PRESETS[input.lighting] ? input.lighting : rig.defaultLighting;
  const lighting = LIGHTING_PRESETS[lightingId];

  const hudId = HUD_MODES[input.hud] ? input.hud : "clean-post-hud";
  const hud = HUD_MODES[hudId];

  const micId = MIC_LABELS[input.mic] ? input.mic : rig.defaultMic;
  const mic = MIC_LABELS[micId];

  const hostName = input.host || "Alex";
  const cohostName = input.cohost || "Momo";
  const robloxRig = ["r6", "chibi-blocky", "r15"].includes(input.robloxRig) ? input.robloxRig : "chibi-blocky";

  const robloxSubNoteEn =
    styleId === "roblox-blocky"
      ? ` [Roblox Rig Variant: ${robloxRig.toUpperCase()} — 2x2x1 torso + flush 1x2x1 limbs + fingerless/clawless solid block hands + 1:1 barrel head + flat 2D face decal]`
      : "";
  const robloxSubNoteZh =
    styleId === "roblox-blocky"
      ? `【Roblox骨架变体：${robloxRig.toUpperCase()} — 2x2x1躯干 + 并拢同宽1x2x1方腿 + 无手指无乐高爪实心方手 + 1:1平滑桶状头 + 2D平面贴图脸】`
      : "";

  const setupAnchorPromptEn = [
    `9:16 Livestream Setup Reference Sheet (3-panel consistency anchor for host "${hostName}"):`,
    `Panel 1 [0° Primary Live Frame]: ${rig.lensEn}, ${style.geometryLockEn}${robloxSubNoteEn}, ${mic.en}, ${lighting.promptEn}, direct eye-contact into the lens as if greeting live chat;`,
    `Panel 2 [15° Chat-Read Glance]: exact same room, outfit, and mic position, eyes flicked 15 degrees off-axis reading a glowing secondary chat monitor with subtle smile;`,
    `Panel 3 [Rig & Optical Side Diagram]: clean side-view showing camera mount distance, ring-light placement, and room background props.`,
    `Clean raw camera feed, zero burned-in UI text, zero platform watermarks.`
  ].join(" ");

  const setupAnchorPromptZh = [
    `9:16 直播间跨镜头一致性三态锚定参考卡（主播「${hostName}」）：`,
    `左格【0°主镜头直视态】：${rig.lensZh}，${style.geometryLockZh}${robloxSubNoteZh}，${mic.zh}，${lighting.promptZh}，眼神0°直视镜头向直播间观众打招呼；`,
    `中格【15°偏轴读弹幕态】：完全相同的房间陈设、穿搭与麦克风左右位置，视线偏转15°扫向副屏弹幕并露出实时反应；`,
    `右格【机位与补光侧视锚点】：清晰交代摄像头架设距离、环形灯/霓虹光源方位与背景固定摆件。`,
    `画面保持100%纯净无UI文字底片，零平台水印、零乱码弹幕。`
  ].join("");

  const dualTrackNoteEn =
    rigId === "pip-facecam-rig"
      ? `Dual-Track Rule (PiP): Render Main 9:16 World/Gameplay Feed and "${hostName}" Corner Facecam as TWO separate clean plates, then composite the rounded PiP box in post (or ` +
        "`render_preview.mjs`) so the facecam frame never warps."
      : rigId === "pk-cohost-split"
      ? `Dual-Track Rule (PK Split): Render Host A ("${hostName}", warm key) and Host B ("${cohostName}", cool cyan key) as locked webcam plates or a First-Frame I2V anchored 50/50 split before adding the VS PK score bar.`
      : "Single-Track Clean Plate: Generate raw camera feed first, then composite optional LIVE badge and scrolling chat HUD cleanly.";

  const dualTrackNoteZh =
    rigId === "pip-facecam-rig"
      ? `双轨合成铁律（画中画PiP）：将 9:16 主场景/游戏画面 与 主播「${hostName}」反应小窗 拆分为两条独立纯净视频轨分别生成，再通过后期或 render_preview.mjs 合成圆角画中画边框，彻底杜绝小窗变形漂移。`
      : rigId === "pk-cohost-split"
      ? `双轨合成铁律（连麦PK分屏）：分别锁定左/上房主播「${hostName}」（暖色补光）与右/下房主播「${cohostName}」（冷青补光）固定机位底片，合成对称50/50分屏后再叠加PK血条与VS标识。`
      : "单轨纯净底片原则：先生成无任何文字涂层的纯净镜头画面，后置叠加高清直播间角标与滚动弹幕。";

  const negativePromptEn = `${style.antiDriftNegativeEn}, floating omniscient crane camera, detached movie scene ignoring the lens, garbled AI-generated chat text, fake TikTok/Douyin/Twitch logo watermarks, microphone switching sides`;
  const negativePromptZh = `${style.antiDriftNegativeZh}，上帝视角电影摇臂空镜，角色无视镜头演戏，AI直出乱码弹幕文字，虚假平台Logo水印，麦克风跨镜头左右跳位`;

  return {
    rigId,
    styleId,
    lightingId,
    hudId,
    micId,
    hostName,
    cohostName,
    robloxRig,
    rig,
    style,
    lighting,
    hud,
    mic,
    dualTrackNoteEn,
    dualTrackNoteZh,
    setupAnchorPromptEn,
    setupAnchorPromptZh,
    negativePromptEn,
    negativePromptZh
  };
}

const HEADINGS = {
  en: { title: "Livestream POV Rig & Style DNA Card", anchors: "3-State Setup Anchor Prompts", neg: "Anti-Drift Negative Prompts" },
  zh: { title: "直播视角机位与画风 DNA 设定卡", anchors: "直播间三态一致性首帧参考词", neg: "防跑偏负向提示词" },
  "zh-tw": { title: "直播視角機位與畫風 DNA 設定卡", anchors: "直播間三態一致性首幀參考詞", neg: "防跑偏負向提示詞" },
  ja: { title: "ライブ配信POVカメラ＆スタイル設定カード", anchors: "3状態セットアップ参照プロンプト", neg: "ドリフト防止ネガティブプロンプト" },
  ko: { title: "라이브 방송 POV 카메라 & 스타일 DNA 카드", anchors: "3상태 셋업 기준 프롬프트", neg: "드리프트 방지 네거티브 프롬프트" },
  es: { title: "Tarjeta ADN de Cámara Livestream POV y Estilo", anchors: "Prompts de Referencia en 3 Estados", neg: "Prompts Negativos Anti-Deriva" },
  fr: { title: "Carte ADN Caméra Livestream POV & Style", anchors: "Prompts d'Ancrage en 3 États", neg: "Prompts Négatifs Anti-Dérive" },
  de: { title: "Livestream-POV-Kamera- & Stil-DNA-Karte", anchors: "3-Zustands-Setup-Referenzprompts", neg: "Anti-Drift-Negativprompts" },
  pt: { title: "Cartão DNA de Câmera Livestream POV e Estilo", anchors: "Prompts de Referência em 3 Estados", neg: "Prompts Negativos Anti-Desvio" },
  ru: { title: "ДНК-карта ракурса стрима и визуального стиля", anchors: "Референс-промпты 3 состояний сцены", neg: "Негативные анти-дрейф промпты" },
  "zh-en": { title: "直播视角机位与画风设定卡 / Livestream POV Rig & Style DNA Card", anchors: "三态首帧锚定提示词 / 3-State Setup Anchor Prompts", neg: "负向防跑偏词 / Negative Prompts" }
};

export function formatRigSpecMarkdown(spec, lang = "en") {
  const code = normalizeLang(lang);
  const h = HEADINGS[code] || HEADINGS.en;
  const includeZh = code === "zh" || code === "zh-tw" || code === "zh-en";

  const lines = [
    `<!-- lang: ${code} | rig: ${spec.rigId} | style: ${spec.styleId} -->`,
    `# ${h.title}`,
    "",
    "| Dimension / 维度 | Locked Specification / 锁定参数 |",
    "| --- | --- |",
    `| **Host / 主播** | \`${spec.hostName}\`${spec.rigId === "pk-cohost-split" ? ` vs \`${spec.cohostName}\`` : ""} |`,
    `| **Camera Rig / 直播机位** | \`${spec.rigId}\` — ${includeZh ? `${spec.rig.labelZh} (${spec.rig.labelEn})` : spec.rig.labelEn} |`,
    `| **Visual Style / 画风适配包** | \`${spec.styleId}\` — ${includeZh ? `${spec.style.labelZh} (${spec.style.labelEn})` : spec.style.labelEn} |`,
    `| **Optics & Mount / 镜头与架设** | ${includeZh ? `${spec.rig.lensZh}<br>${spec.rig.lensEn}` : spec.rig.lensEn} |`,
    `| **Shake & Physics / 物理运动反馈** | ${includeZh ? spec.rig.physicsZh : spec.rig.physicsEn} |`,
    `| **4th-Wall Eye-Line / 眼神互动轴** | ${includeZh ? spec.rig.eyeLineZh : spec.rig.eyeLineEn} |`,
    `| **Microphone Lock / 麦克风方位锁** | \`${spec.micId}\` — ${includeZh ? spec.mic.zh : spec.mic.en} |`,
    `| **Lighting / 直播补光方案** | \`${spec.lightingId}\` — ${includeZh ? spec.lighting.promptZh : spec.lighting.promptEn} |`,
    `| **Style Invariants / 画风防崩几何锁** | ${includeZh ? `${spec.style.geometryLockZh}<br>${spec.style.geometryLockEn}` : spec.style.geometryLockEn} |`,
    `| **HUD Strategy / 弹幕UI分层策略** | \`${spec.hudId}\` — ${includeZh ? spec.hud.ruleZh : spec.hud.ruleEn} |`,
    `| **Track Compositing / 分轨合成规范** | ${includeZh ? spec.dualTrackNoteZh : spec.dualTrackNoteEn} |`,
    "",
    `## ${h.anchors}`,
    "",
    "### English Setup Sheet Prompt (Midjourney / Flux / Sora / GPT-4o Image)",
    "",
    "```text",
    spec.setupAnchorPromptEn,
    "```",
    "",
    "### 中文首帧直播间参考卡提示词 (即梦 / 可灵 / 通义万相)",
    "",
    "```text",
    spec.setupAnchorPromptZh,
    "```",
    "",
    `## ${h.neg}`,
    "",
    "- **EN Negative**: `" + spec.negativePromptEn + "`",
    "- **ZH Negative**: `" + spec.negativePromptZh + "`",
    ""
  ];
  return lines.join("\n");
}

function printHelp() {
  console.log(`Usage:
  node scripts/rig_spec.mjs [options]

Build a Livestream POV Camera Rig + Orthogonal Visual Style DNA card and 3-state setup anchor prompt.

Options:
  --rig <id>          Camera rig: ${Object.keys(RIG_PROFILES).join(" | ")} (default: desktop-webcam)
  --style <id>        Style pack: ${Object.keys(STYLE_ADAPTERS).join(" | ")} (default: realistic-irl)
  --lighting <id>     Lighting preset: ${Object.keys(LIGHTING_PRESETS).join(" | ")}
  --hud <id>          HUD mode: ${Object.keys(HUD_MODES).join(" | ")} (default: clean-post-hud)
  --host <name>       Primary streamer/host name (default: Alex)
  --cohost <name>     Co-host name for pk-cohost-split (default: Momo)
  --mic <id>          Mic lock: boom-left | boom-right | lavalier | headset-mic | none
  --roblox-rig <id>   When --style roblox-blocky: r6 | chibi-blocky | r15 (default: chibi-blocky)
  --lang <code>       Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en
  --out <path>        Write UTF-8 output directly to file
  --json              Emit structured JSON instead of Markdown
  --help              Show this help message`);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("rig_spec.mjs");
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    process.exit(0);
  }
  const spec = buildRigSpec(opts);
  const outText = opts.json ? JSON.stringify(spec, null, 2) + "\n" : formatRigSpecMarkdown(spec, opts.lang);
  if (opts.out) {
    const abs = path.resolve(opts.out);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, outText, "utf8");
    console.log(`Wrote rig spec to ${abs}`);
  } else {
    process.stdout.write(outText);
  }
}
