#!/usr/bin/env node
/**
 * avatar_spec.mjs
 * Zero-dependency CLI generator for Roblox-style blocky character DNA cards,
 * multi-character Cast Lock sheets, Non-Human Blocky Pet companions, and
 * 3-view turnaround prompts (Midjourney / Flux / Jimeng / GPT-4o Image).
 */

import fs from "node:fs";
import path from "node:path";

export const DEFAULT_PERFORMANCE_DNA = {
  "chibi-plush": {
    defaultTemperament: "eager-expressive-blindbox",
    signatureGaze: "pupils-dart-to-trigger-before-head-turns",
    signatureGesture: "present-prop-forward-with-both-solid-block-hands",
    conflictReaction: "freeze-wide-eyed-then-lean-back",
    actingMomentEn: "hesitates between two choices with asymmetrical brows and pupils locked on the trigger prop",
    actingMomentZh: "高低眉犹豫不决、瞳孔死死盯住触发剧情的关键道具"
  },
  "classic-noob": {
    defaultTemperament: "unbothered-deadpan-opportunist",
    signatureGaze: "calm-peripheral-stare-amid-chaos",
    signatureGesture: "zero-telegraph-rigid-90-degree-action",
    conflictReaction: "complete-deadpan-emotional-immunity",
    actingMomentEn: "holds an unchanging Default Smile or Chill (-_-) face while calmly claiming the prize",
    actingMomentZh: "在混乱现场保持毫无波澜的默认微笑或死鱼眼淡定截胡"
  },
  "bacon-hair": {
    defaultTemperament: "earnest-panicked-rookie",
    signatureGaze: "double-take-at-unexpected-hazard",
    signatureGesture: "both-block-hands-raised-beside-head",
    conflictReaction: "stiff-step-back-then-frantic-scramble",
    actingMomentEn: "freezes mid-step with worried brows and pupils tracking the sudden hazard",
    actingMomentZh: "半步急停、八字眉惊恐紧盯突发危机"
  },
  "classic-guest": {
    defaultTemperament: "silent-observant-wildcard",
    signatureGaze: "direct-fourth-wall-camera-glance",
    signatureGesture: "single-crisp-right-arm-point",
    conflictReaction: "instant-180-pivot-exit",
    actingMomentEn: "points one solid block arm at incoming danger while glancing back at the camera",
    actingMomentZh: "单侧实心方臂直指远处危机并回头看镜头"
  },
  "builderman": {
    defaultTemperament: "overconfident-problem-solver",
    signatureGaze: "squinted-measure-of-target-distance",
    signatureGesture: "confident-forward-push-or-tool-raise",
    conflictReaction: "brief-smirk-before-physics-backfires",
    actingMomentEn: "leans forward with a confident asymmetrical smirk while bracing a camera-facing prop",
    actingMomentZh: "挑眉坏笑身体前倾、双侧方手朝镜头清晰抵住关键道具"
  },
  "ugc-streetwear": {
    defaultTemperament: "dramatic-main-character",
    signatureGaze: "confident-side-eye-over-shoulder",
    signatureGesture: "pose-strike-with-hip-tilt",
    conflictReaction: "dramatic-gasp-protecting-fit",
    actingMomentEn: "strikes an angled runway pose while side-eyeing a rival's outfit",
    actingMomentZh: "侧身定格时尚造型、挑眉斜睨身旁反差搭档"
  },
  "corporate-worker": {
    defaultTemperament: "caffeine-depleted-realist",
    signatureGaze: "slow-eyeball-shift-before-neck-pivot",
    signatureGesture: "protective-two-hand-mug-dock",
    conflictReaction: "90-degree-waist-hinge-desk-slump",
    actingMomentEn: "stares at an alarming screen notification with tired asymmetrical brows and coffee mug held camera-facing",
    actingMomentZh: "疲惫高低眉紧盯屏幕弹窗、胸前朝镜头稳稳端住咖啡杯"
  },
  "cozy-chef": {
    defaultTemperament: "proud-perfectionist-in-denial",
    signatureGaze: "proudly-tracks-dish-ignoring-smoke",
    signatureGesture: "two-hand-platter-presentation",
    conflictReaction: "holds-cheerful-smile-until-rigid-tip-over",
    actingMomentEn: "presents a smoking dish toward the lens with cheerful eyes locked on the viewer",
    actingMomentZh: "双手平托冒烟料理朝向镜头、眼神骄傲发亮制造反差喜感"
  },
  "obby-runner": {
    defaultTemperament: "hyper-focused-speedrunner",
    signatureGaze: "laser-locked-on-landing-edge",
    signatureGesture: "forward-lean-sprint-ready",
    conflictReaction: "silent-chill-stare-after-ragdoll-wipeout",
    actingMomentEn: "leans 10 degrees forward on platform edge with pupils locked on a tiny landing pad",
    actingMomentZh: "站在平台边缘前倾10度、瞳孔死锁前方极限落点"
  },
  "zombie-r6": {
    defaultTemperament: "single-minded-blocky-pursuer",
    signatureGaze: "unblinking-lock-on-nearest-snack-or-player",
    signatureGesture: "both-arms-locked-90-degrees-forward",
    conflictReaction: "tips-outward-as-one-rigid-statue",
    actingMomentEn: "reaches both stiff moss-green block arms forward with asymmetrical dazed eyes tracking the cart",
    actingMomentZh: "双侧绿方臂平举90度、大小眼呆滞锁定前方目标"
  }
};

export const ARCHETYPES = {
  "chibi-plush": {
    labelZh: "小红书爆款Plushie盲盒风小人",
    labelEn: "Roblox Plushie / Chibi-Blocky Avatar",
    defaultRig: "chibi-blocky",
    defaultMaterial: "glossy-vinyl",
    headColor: "Cool yellow #FDEA8D",
    primaryColor: "Pastel Pink #F4A2B8",
    secondaryColor: "Institutional white #F8F8F8",
    accentColor: "Cyan #00AAE4",
    outfitEn: "oversized pastel-pink blocky sweater on a 2x2x1 torso, flush 1x2x1 milk-white blocky legs with zero thigh gap",
    outfitZh: "蜜桃粉倒角方柱卫衣（2x2x1宽扁躯干）、并拢齐平的奶白色1x2x1方柱双腿（无分叉间隙）",
    accessoriesEn: "3D UGC fluffy bob hair with side bangs, cream cat-ear headphones on head, sky-blue boxy backpack",
    accessoriesZh: "3D立体刘海波波头UGC发型、头戴奶油白猫耳大耳机、天蓝色方盒双肩包",
    faceEn: "flat 2D screen-printed Roblox decal face with glossy ink eyes, star highlights, blush ovals, and a tiny cat smile (:3)",
    faceZh: "纯平2D丝网印刷五官贴图，带星光高点的墨点眼、椭圆粉腮红与猫猫嘴(:3)"
  },
  "classic-noob": {
    labelZh: "经典复古黄皮新手 (Official Noob)",
    labelEn: "Authentic Classic Roblox Noob (R6)",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    headColor: "Bright yellow #F5CD30",
    primaryColor: "Bright blue #0D69AC",
    secondaryColor: "Br. yellowish green #A4BD47",
    accentColor: "Bright red #C4281C (Bloxy Cola)",
    outfitEn: "untextured Bright blue (#0D69AC) 2x2x1 rectangular torso block, Bright yellow (#F5CD30) 1x2x1 solid rectangular arm blocks flush at sides, Br. yellowish green (#A4BD47) 1x2x1 rectangular leg blocks flush side-by-side",
    outfitZh: "经典亮蓝色(#0D69AC) 2x2x1长方体躯干、亮黄色(#F5CD30) 1x2x1实心方柱双臂紧贴两侧、黄绿色(#A4BD47) 1x2x1方柱双腿并拢齐平",
    accessoriesEn: "red cylindrical Bloxy Cola can docked flush against the right flat rectangular block hand",
    accessoriesZh: "右侧平头实心方块手刚性贴合一罐红色Bloxy Cola可乐罐",
    faceEn: "iconic classic Roblox Default Smile 2D decal face with two black oval eyes and a curved black line smile",
    faceZh: "标志性Roblox经典默认笑脸2D贴图（两个黑色椭圆眼点与上扬弧线嘴）"
  },
  "bacon-hair": {
    labelZh: "经典培根头新手 (Pal Hair / Bacon)",
    labelEn: "Iconic Roblox Bacon Hair Avatar",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    headColor: "Light stone grey #E5E4DF",
    primaryColor: "Dark stone grey #635F62",
    secondaryColor: "Black #1B2A35",
    accentColor: "Bright blue #0D69AC",
    outfitEn: "dark stone grey open blocky moto jacket over a bright blue inner shirt on a 2x2x1 torso, black 1x2x1 flush blocky jeans legs with white bottom trim",
    outfitZh: "深灰开襟机车方块夹克内搭蓝T恤（2x2x1躯干）、纯黑并拢齐平1x2x1方柱牛仔裤腿",
    accessoriesEn: "iconic brown strip-textured 3D Pal Hair (Bacon Hair) on top of the barrel-cylinder head",
    accessoriesZh: "头顶标志性棕褐色条状3D培根发型（Pal Hair / Bacon Hair）",
    faceEn: "classic Roblox 2D Default Smile decal printed flat on the light grey barrel-cylinder head",
    faceZh: "浅灰桶状圆角圆柱头正面印有经典Roblox 2D默认微笑贴图"
  },
  "classic-guest": {
    labelZh: "经典游客风形象 (Classic Guest Style)",
    labelEn: "Blocky Classic Guest Style (R6)",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    headColor: "Institutional white #F8F8F8",
    primaryColor: "Really black #111827",
    secondaryColor: "Black #1B2A35",
    accentColor: "Bright red #C4281C",
    outfitEn: "black 2x2x1 street jacket with a clean white geometric triangle emblem on the chest and white cuffs (zero brand logos), flush black 1x2x1 rectangular blocky pants",
    outfitZh: "纯黑2x2x1胸前印白色几何三角形徽章的夹克配白袖口（无任何品牌商标Logo）、纯黑并拢齐平1x2x1方柱长裤",
    accessoriesEn: "plain bright red sport baseball cap with curved front brim (unbranded, no logo) on the pale white 1:1 barrel head",
    accessoriesZh: "纯白1:1桶状圆角头上佩戴纯色无标亮红运动棒球帽",
    faceEn: "classic Roblox 2D Winning Grin (:D) decal with white top teeth bar",
    faceZh: "经典Roblox 2D露齿笑(:D)平面贴图"
  },
  "builderman": {
    labelZh: "经典工程安全帽建造者 (Builder Hard Hat)",
    labelEn: "Classic Builder Hard Hat Avatar (R6)",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    headColor: "Bright yellow #F5CD30",
    primaryColor: "Bright orange #F97316",
    secondaryColor: "Dark royal blue #1E3A8A",
    accentColor: "Bright yellow #FACC15 (Hard Hat)",
    outfitEn: "bright orange 2x2x1 zip hoodie with 3D hood, kangaroo pocket, and white drawstrings, dark royal-blue flush 1x2x1 blocky jeans",
    outfitZh: "亮橙色2x2x1拉链连帽卫衣（带立体兜帽、白抽绳与袋鼠兜）、深宝蓝并拢1x2x1方柱牛仔裤",
    accessoriesEn: "classic yellow ribbed construction hard hat on the yellow 1:1 barrel head",
    accessoriesZh: "黄色1:1桶状头上佩戴经典黄色工程安全帽",
    faceEn: "classic Roblox Check-It 2D smirk decal with angled brow",
    faceZh: "经典Roblox 2D挑眉坏笑(Check It)贴图"
  },
  "ugc-streetwear": {
    labelZh: "Y2K千禧穿搭潮人 (Dress-to-Impress)",
    labelEn: "Y2K UGC Streetwear Blocky Avatar",
    defaultRig: "r15",
    defaultMaterial: "glossy-vinyl",
    headColor: "Warm yellowish orange #F8D96D",
    primaryColor: "Really black #111827",
    secondaryColor: "Pastel blue #93C5FD",
    accentColor: "Alder / Electric Purple #A855F7",
    outfitEn: "cropped charcoal-black glossy puffer jacket with purple star badge on a 2x2x1 torso (zero brand logos), washed-denim 1x2x1 blocky legs sitting flush side-by-side",
    outfitZh: "炭黑高光短款方块羽绒服配紫色星星胸章（2x2x1躯干，无品牌商标）、水洗牛仔蓝并拢齐平1x2x1方柱裤腿",
    accessoriesEn: "3D pastel-pink layered UGC hair with cat-ear beanie, silver star sunglasses, purple boxy backpack",
    accessoriesZh: "3D粉色层次感UGC长发配猫耳针织帽、银色五角星墨镜、电光紫方盒双肩包",
    faceEn: "flat 2D painted Roblox Check-It / Smirk decal face with asymmetrical raised brow and confident sideways grin",
    faceZh: "纯平2D印刷Roblox经典挑眉坏笑(Check It / Smirk)贴图"
  },
  "corporate-worker": {
    labelZh: "破防早八打工人",
    labelEn: "Exhausted Office Worker Roblox Blocky",
    defaultRig: "chibi-blocky",
    defaultMaterial: "smooth-plastic",
    headColor: "Cool yellow #FDEA8D",
    primaryColor: "Mint #86EFAC (Matcha Cardigan)",
    secondaryColor: "Dark stone grey #475569",
    accentColor: "Bright red #F43F5E (Tie & Mug)",
    outfitEn: "matcha-green blocky cardigan over white shirt collar and red tie decal on a 2x2x1 torso, slate-grey 1x2x1 blocky trousers sitting flush side-by-side",
    outfitZh: "抹茶绿2x2x1方柱开衫内搭白衬衫领与红领带贴图、深灰并拢齐平1x2x1方柱西裤",
    accessoriesEn: "3D brown side-parted blocky hair, white headphones around neck, amber coffee mug docked flush to right flat block hand",
    accessoriesZh: "3D深棕偏分方块短发、颈挂白色方块耳机、右侧实心平头方块手刚性吸附琥珀咖啡杯",
    faceEn: "flat 2D screen-printed Roblox decal face with tired horizontal line eyes (-_-) or shocked hollow ring eyes",
    faceZh: "纯平2D印刷疲惫死鱼眼(-_-)或震惊圆圈眼贴图"
  },
  "cozy-chef": {
    labelZh: "治愈系微缩甜点师",
    labelEn: "Cozy Miniature Bakery Chef Blocky",
    defaultRig: "chibi-blocky",
    defaultMaterial: "clay-soft",
    headColor: "Cool yellow #FDEA8D",
    primaryColor: "Institutional white #FFFBEB",
    secondaryColor: "CGA brown #D97706 (Apron)",
    accentColor: "Carnation pink #FB7185",
    outfitEn: "butter-white blocky double-breasted chef coat on a 2x2x1 torso, caramel apron decal, flush 1x2x1 blocky legs",
    outfitZh: "奶油白双排扣2x2x1方柱厨师服、焦糖围裙贴图、并拢齐平1x2x1方柱双腿",
    accessoriesEn: "puffy rounded-blocky white chef toque hat, golden layered blocky croissant on pastel tray",
    accessoriesZh: "饱满圆角方块白色厨师高帽、马卡龙托盘上的多层金黄方块羊角包",
    faceEn: "flat 2D painted Roblox decal face with warm curved happy eyes (^^) and rosy oval cheek decals",
    faceZh: "纯平2D印刷弯弯笑眼(^^)与暖粉椭圆腮红贴图"
  },
  "obby-runner": {
    labelZh: "多巴胺跑酷闯关手 (Speedrunner)",
    labelEn: "Pastel Obby Parkour Speedrunner (R6)",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    headColor: "Bright yellow #F5CD30",
    primaryColor: "Cyan #00AAE4",
    secondaryColor: "Hot pink #FF55A3",
    accentColor: "Bright red #EF4444 (Speed Coil)",
    outfitEn: "sporty cyan 2x2x1 blocky jersey with a crisp white geometric triangle emblem on the chest (zero trademark logos), hot-pink 1x2x1 rectangular leg blocks sitting flush side-by-side",
    outfitZh: "亮青色2x2x1运动方柱球衣（胸前印白色几何三角形徽章，无任何品牌商标Logo）、亮粉色并拢齐平1x2x1长方体双腿",
    accessoriesEn: "plain bright-red sport visor cap (unbranded, no logo), glowing red Speed Coil wrapped around the right 1x2x1 solid rectangular arm block, twin white blocky jetpack",
    accessoriesZh: "头戴纯色无标红色运动遮阳帽、右侧1x2x1实心方柱手臂缠绕发光红色加速弹簧(Speed Coil)、背后白色双联方块喷气包",
    faceEn: "flat 2D screen-printed Roblox Winning/Energetic grin decal with determined wide eyes",
    faceZh: "纯平2D印刷专注大眼与活力露齿笑贴图（纯平面无3D深度）"
  },
  "zombie-r6": {
    labelZh: "经典绿皮方块丧尸 (Blocky R6 Zombie)",
    labelEn: "Classic Blocky R6 Zombie Mob",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    headColor: "Moss green #74A662",
    primaryColor: "Reddish brown #694028",
    secondaryColor: "Dark slate #334155",
    accentColor: "Lime #84CC16",
    outfitEn: "weathered brown 2x2x1 rectangular torso block with torn-hem flat decal, moss-green (#74A662) 1x2x1 solid rectangular arms held straight forward at 90-degree shoulder hinges, dark-slate 1x2x1 rectangular leg blocks flush side-by-side",
    outfitZh: "深棕2x2x1长方体破旧外衣躯干（平面破边贴图）、苔藓绿(#74A662) 1x2x1实心平头方柱双臂沿肩轴平举向前90度、深灰蓝1x2x1方柱双腿并拢齐平",
    accessoriesEn: "untextured moss-green 1:1 barrel head with zero hair or hats (clean silhouette for crowd scenes)",
    accessoriesZh: "无帽无发的纯苔藓绿1:1桶状圆角头部（适合多人丧尸群同框不乱）",
    faceEn: "flat 2D screen-printed Roblox zombie drool/dazed decal with asymmetrical hollow ring eyes and wavy line mouth",
    faceZh: "纯平2D印刷呆滞大小眼圆圈与波浪嘴贴图（无真实腐烂纹理或3D獠牙）"
  }
};

export const FACE_OVERRIDES = {
  smile: {
    en: "iconic classic Roblox Default Smile 2D decal face (:)) with two black oval ink eyes and a curved black smile arc",
    zh: "经典Roblox 2D默认微笑(:))平面贴图（两颗黑色椭圆墨点眼与上扬弧线嘴）"
  },
  deadpan: {
    en: "flat 2D screen-printed Roblox Chill (-_-) deadpan decal with horizontal line eyes and a tiny flat mouth line",
    zh: "纯平2D丝网印刷Roblox经典死鱼眼(Chill -_-)贴图（水平一字眼与短平嘴线）"
  },
  smirk: {
    en: "flat 2D painted Roblox Check-It smirk decal with one angled brow and confident sideways grin",
    zh: "纯平2D印刷Roblox经典挑眉坏笑(Check It)贴图"
  },
  grin: {
    en: "classic Roblox 2D Winning Grin (:D) decal with oval ink eyes and open D-shaped mouth with white top teeth bar",
    zh: "经典Roblox 2D露齿大笑(:D)平面贴图（带白色上排牙条）"
  },
  shocked: {
    en: "flat 2D screen-printed Roblox Shocked (O_O) decal with wide white sclera rings, tiny black pupils, and open gasp mouth",
    zh: "纯平2D印刷震惊白圈眼(O_O)配张嘴倒吸凉气贴图"
  },
  tears: {
    en: "flat 2D screen-printed Roblox Crying (T_T) decal with worried brows and cyan waterfall tear strips painted down both cheeks",
    zh: "纯平2D印刷八字委屈眉与双颊青蓝色瀑布流泪条带(T_T)贴图"
  },
  angry: {
    en: "flat 2D screen-printed Roblox Angry Bloxxer (>_<) decal with V-angled scowling brows and clenched frown",
    zh: "纯平2D印刷愤怒V字皱眉(>_<)与抿嘴贴图"
  },
  dizzy: {
    en: "flat 2D screen-printed Roblox KO Dizzy (X_X) decal with crossed eyes and stunned flat mouth",
    zh: "纯平2D印刷眩晕叉叉眼(X_X)宕机贴图"
  },
  sleepy: {
    en: "flat 2D screen-printed half-lidded sleepy commuter eyes decal with tiny yawn dot mouth",
    zh: "纯平2D印刷半睁困倦死鱼眼配迷你哈欠点状嘴贴图"
  }
};

export const COMPANIONS = {
  "neon-dragon": {
    nameEn: "Blocky Neon Dragon Pet",
    nameZh: "浮空霓虹方块龙神宠",
    specEn:
      "floating Roblox Adopt-Me-style blocky neon dragon companion built strictly from chamfered SmoothPlastic and emissive Neon primitives: pearl-white beveled boxy head and snout, flat 2D black dot eyes, stubby glowing cyan prism horns, four tiny clawless solid rectangular block paws, and twin flat beveled translucent cyan-violet geometric wing plates hinging rigidly at the back (zero reptile scales, zero sharp claws/talons, zero leathery bat wings, non-voxel)",
    specZh:
      "浮空Roblox领养风霓虹方块龙神宠（完全由倒角SmoothPlastic与自发光Neon几何块拼成：珍珠白圆角方头方吻部、纯平2D黑豆眼、发光青色短棱柱角、四只无爪实心迷你小方足、背部刚性铰链扇动的扁平半透明青紫几何翼板；严禁真实爬行动物鳞片、尖爪或蝙蝠皮膜翼，非像素体素）"
  },
  "blocky-shiba": {
    nameEn: "Blocky Shiba Dog Pet",
    nameZh: "圆角方块柴犬宠物",
    specEn:
      "compact Roblox-style blocky Shiba Inu companion made of satin-gloss SmoothPlastic: chamfered warm-amber cube head with cream muzzle decal, flat 2D shiny dot eyes, triangular beveled prism ears, boxy 2:1 rectangular body, curled blocky tail, and four stubby clawless rectangular block legs (zero realistic fur strands, zero wet animal nose, non-voxel)",
    specZh:
      "微缩Roblox风圆角方块柴犬宠物（SmoothPlastic平滑塑料材质：暖橘色大倒角方头印奶油色吻部贴图、纯平2D黑豆眼、三角棱柱立耳、倒角长方体躯干配卷曲方块尾、四条无爪短方柱腿；严禁真实动物毛发丝与湿鼻头）"
  },
  "floating-slime": {
    nameEn: "Glossy Blocky Slime Cube Pet",
    nameZh: "半透明果冻方块史莱姆宠",
    specEn:
      "hovering translucent mint-cyan Roblox Glass/SmoothPlastic chamfered cube pet with rounded 4mm bevels, flat 2D starry kawaii eyes printed on front face, and tiny solid star core inside (zero organic tentacles or liquid splatter)",
    specZh:
      "悬浮半透明薄荷青倒角方块果冻宠（大圆角平滑几何体、正面纯平2D星星萌眼贴图、内部悬浮发光几何星核；无液体飞溅或有机触手）"
  },
  "cyber-drone": {
    nameEn: "Blocky Cyber Camera Drone",
    nameZh: "微缩方块跟拍无人机",
    specEn:
      "miniature white-and-cyan SmoothPlastic boxy hovering drone companion with a flat 2D winking visor decal screen and two rigid blocky thruster pods (zero ब्रांड/brand logos)",
    specZh:
      "微缩白青配色SmoothPlastic倒角方盒悬浮无人机跟宠，正面带纯平2D眨眼电子表情屏与双侧刚性方块推进器（无品牌Logo）"
  }
};

export const RIGS = {
  "chibi-blocky": {
    label: "Chibi-Blocky / Plushie UGC (Canonical flush blocky limbs + 3D UGC hair / 萌系Plushie齐平方块骨架)",
    geometryEn:
      "canonical Roblox blocky proportions (1:1 classic Roblox barrel-cylinder head with deep curved top and bottom bevels, 2x2x1 rectangular torso block, two 1x2x1 rectangular leg blocks sitting flush side-by-side matching exact torso width with zero thigh gap, two 1x2x1 solid rectangular arm blocks flush at shoulders, fingerless and clawless solid beveled rectangular block hands)",
    geometryZh:
      "纯正Roblox标准方块比例（1:1上下大圆角桶状圆柱头，2x2x1宽扁倒角长方体躯干，两条1x2x1方柱腿并拢紧贴且总宽度与躯干完全齐平无分叉，两条1x2x1一体式实心方柱手臂紧贴肩侧，平头倒角实心方块手部【严禁人类五指、严禁乐高C型钩爪】）"
  },
  r6: {
    label: "Classic R6 (6-part canonical 2x2x1 & 1x2x1 stud rig / 经典R6六部件标准Stud比例骨架)",
    geometryEn:
      "authentic Roblox R6 6-part rigid blocky rig built on exact stud ratios (1.2x1.2x1.2 barrel-beveled cylindrical head, 2x2x1 rectangular torso, two 1x2x1 unsegmented straight rectangular arm blocks flush at sides, two 1x2x1 unsegmented straight rectangular leg blocks flush side-by-side matching torso width, strict Motor6D shoulder/hip hinge pivots only, fingerless and clawless solid flat block hands)",
    geometryZh:
      "正统Roblox R6六部件刚性Stud比例骨架（1.2x1.2x1.2上下圆角桶状圆柱头，2x2x1长方体躯干，两条1x2x1无肘膝分段的笔直实心方柱手臂紧贴两侧，两条1x2x1笔直方柱双腿并拢齐平与躯干同宽，仅肩髋Motor6D机械转轴可动，平头实心方块手【无人类手指、无乐高C型爪】）"
  },
  r15: {
    label: "Expressive R15 (15-part segmented rigid blocky rig / R15分段机械铰链标准方块骨架)",
    geometryEn:
      "Roblox R15 segmented blocky rig retaining canonical 2x2x1 torso and flush 1x2x1 rectangular limb silhouette with crisp rigid upper/lower arm and leg blocks rotating strictly at mechanical elbow and knee hinges (zero rubbery noodle bending or forearm twisting), 1:1 barrel-beveled cylindrical head, fingerless and clawless solid rectangular block hands",
    geometryZh:
      "Roblox R15分段刚性方块骨架（保持2x2x1躯干与并拢齐平1x2x1方柱四肢轮廓，上臂/前臂保持笔直刚性方块并仅沿机械肘膝铰链做折角转动【严禁面条状软体弯曲或扭曲】，1:1桶状圆角圆柱头，无手指且无乐高C型爪的实心平头方块手）"
  }
};

export const MATERIALS = {
  "smooth-plastic": {
    label: "Roblox SmoothPlastic + Flat Square-Seam Baseplate (官方SmoothPlastic平滑塑料与无凸点方格底板)",
    shaderEn:
      "authentic Roblox Studio SmoothPlastic shader with crisp 2mm edge bevels on the avatar, standing on a flat matte Roblox SmoothPlastic / WoodPlanks / Concrete surface with subtle recessed square grid seams (zero raised circular Lego floor studs or pegs), clean ambient occlusion and bright skybox lighting",
    shaderZh:
      "纯正Roblox Studio SmoothPlastic平滑塑料材质（角色身体带2毫米利落倒角高光），脚踩平整无圆粒凸起的Roblox平滑地板或木地板（严禁乐高地面凸点颗粒），清晰环境光遮蔽与明亮天空盒布光"
  },
  "glossy-vinyl": {
    label: "Glossy Blind-Box SmoothPlastic (高光潮玩级SmoothPlastic材质)",
    shaderEn:
      "glossy collectible Roblox SmoothPlastic & PVC shader, smooth studless character and floor surfaces (zero raised Lego pegs), crisp specular highlights, subtle subsurface scattering under three-point studio lighting",
    shaderZh:
      "高光潮玩级Roblox SmoothPlastic材质，角色与地面完全平滑无乐高凸起圆粒，清脆高光反射与次表面散射，配合三点摄影棚布光"
  },
  "matte-abs": {
    label: "Satin Matte SmoothPlastic (绸感哑光SmoothPlastic材质)",
    shaderEn:
      "satin matte Roblox SmoothPlastic blocks, 2mm chamfered edges, studless character body and smooth flat set pieces, clean ambient occlusion in Motor6D joint seams, studio lighting",
    shaderZh:
      "绸感哑光Roblox SmoothPlastic方块材质，2毫米精密倒角边缘，平滑无颗粒布景道具，Motor6D关节接缝柔和环境光遮蔽"
  },
  "clay-soft": {
    label: "Soft Miniature Diorama Plastic (微缩柔感模型塑料材质)",
    shaderEn:
      "soft-touch matte diorama shader over canonical Roblox 2x2x1/1x2x1 blocky geometry with multi-part miniature Roblox Studio props, warm tabletop lighting, 50mm f/2.8 shallow depth of field",
    shaderZh:
      "标准Roblox 2x2x1/1x2x1方块几何体配微缩柔感哑光材质与精致多部件Roblox道具，暖调桌面布光，50mm微距浅景深"
  },
  "neon-cyber": {
    label: "Roblox Neon + ForceField Cyber Shader (Roblox自发光Neon与高光材质)",
    shaderEn:
      "Roblox SmoothPlastic dark shell paired with glowing Roblox Neon material accents, high-contrast cyan and magenta rim lighting, sleek smooth reflective floor (zero raised Lego studs)",
    shaderZh:
      "深色Roblox SmoothPlastic方块外壳配高亮度Roblox Neon自发光材质边条，高反差轮廓光与平滑微反射地面（无乐高凸起圆粒）"
  }
};

export const NEGATIVE_PROMPT_EN =
  "official Roblox logo, tilted square Roblox trademark emblem, Roblox R badge, brand logos, watermarks, human fingers, five fingers, realistic human hands, knuckles, Lego C-shaped claw hands, Lego hook hands, Lego top head studs, raised circular Lego floor studs, cylindrical Lego brick pegs, studded Lego baseplate, Minecraft sharp voxel cube head, 8x8 pixel texture, featureless blank single-box props, separated thin legs with thigh gap, protruding human sneakers, realistic human face, 3D protruding nose, skin pores, rubbery noodle limbs, blurry decal";

export const NEGATIVE_PROMPT_ZH =
  "官方Roblox商标Logo，倾斜方框标志，R字品牌徽标，任何品牌水印，人类五指，真实人手，乐高C型夹爪手，乐高钩子手，乐高头顶圆柱凸起颗粒，乐高地面凸起圆粒，乐高积木凸点底板，我的世界直角像素方块头，无细节简陋纯色单一方块道具，双腿分叉有空隙，凸出真人运动鞋，真实人类面部骨骼，3D凸起高鼻梁，皮肤毛孔，橡胶面条状弯曲四肢，五官贴图模糊";

function printHelp() {
  console.log(`Usage: node scripts/avatar_spec.mjs [options]

Generate a geometry-locked Roblox-style Character DNA card, multi-character Cast Lock sheet,
optional Non-Human Blocky Pet DNA, and 3-view turnaround prompts.

Options:
  --archetype <id>         Character preset: ${Object.keys(ARCHETYPES).join(" | ")} (default: chibi-plush)
  --rig <id>               Rig proportion: chibi-blocky | r6 | r15 (default: preset default)
  --material <id>          Surface shader: ${Object.keys(MATERIALS).join(" | ")}
  --face <id>              Override 2D face decal: ${Object.keys(FACE_OVERRIDES).join(" | ")}
  --name <string>          Character name (default: "Bloxy")
  --accessory <str>        Extra English UGC accessory to append
  --accessory-zh <str>     Extra Chinese UGC accessory to append (falls back to --accessory)
  --replace-accessory <s > Replace preset's default accessories completely (removes jetpacks/mugs)
  --no-accessories         Strip all default accessories/held gear for a bare base rig
  --temperament <str>      Performance DNA default temperament (e.g., "guilty-comic")
  --signature-gaze <str>   Performance DNA gaze habit (e.g., "side-eye-before-acting")
  --signature-gesture <s>  Performance DNA hand/body habit (e.g., "present-prop-camera-facing")
  --conflict-reaction <s>  Performance DNA reaction under pressure (e.g., "freeze-then-overcompensate")
  --acting-moment <str>    Signature one-beat acting moment for Cast Acting Sheets
  --companion <id>         Attach a Blocky Pet DNA card: ${Object.keys(COMPANIONS).join(" | ")}
  --cast <list>            Multi-character cast lock, e.g. "classic-noob:Noob:r6,builderman:Builder:r6,zombie-r6:Zombies:r6"
  --lang <code>            Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en (default: en)
  --out <path>             Write UTF-8 output directly to file (avoids Windows PowerShell UTF-16 '>' corruption)
  --json                   Output structured JSON
  --help                   Show this help message`);
}

const SUPPORTED_LANGS = new Set(["en", "zh", "zh-tw", "ja", "ko", "es", "fr", "de", "pt", "ru", "zh-en"]);

export function normalizeLang(code = "en") {
  const clean = String(code || "en").toLowerCase().trim();
  if (clean === "zh-cn") return "zh";
  if (clean === "pt-br") return "pt";
  return SUPPORTED_LANGS.has(clean) ? clean : "en";
}

const AVATAR_HEADERS = {
  en: { title: "Character DNA Card", field: "Field", spec: "Specification", neg: "Anti-Drift Negative Prompt" },
  zh: { title: "角色设定卡", field: "字段", spec: "锁定参数", neg: "负向防串味词" },
  "zh-tw": { title: "角色設定卡", field: "欄位", spec: "鎖定參數", neg: "負向防串味詞" },
  ja: { title: "キャラクターDNAカード", field: "項目", spec: "固定パラメータ", neg: "スタイル崩れ防止ネガティブプロンプト" },
  ko: { title: "캐릭터 DNA 카드", field: "항목", spec: "고정 사양", neg: "스타일 왜곡 방지 네거티브 프롬프트" },
  es: { title: "Ficha ADN del Personaje", field: "Campo", spec: "Especificación", neg: "Prompt Negativo Anti-Deriva" },
  fr: { title: "Fiche ADN du Personnage", field: "Champ", spec: "Spécification", neg: "Prompt Négatif Anti-Dérive" },
  de: { title: "Charakter-DNA-Karte", field: "Feld", spec: "Spezifikation", neg: "Negativ-Prompt gegen Stilabweichung" },
  pt: { title: "Ficha de DNA do Personagem", field: "Campo", spec: "Especificação", neg: "Prompt Negativo Anti-Desvio" },
  ru: { title: "Карта ДНК персонажа", field: "Поле", spec: "Спецификация", neg: "Негативный промпт против искажений" },
  "zh-en": { title: "Character DNA Card / 角色设定卡", field: "Field / 字段", spec: "Specification / 锁定参数", neg: "Anti-Drift Negative Prompt / 负向防串味词" }
};

export function parseArgs(argv) {
  const opts = {
    archetype: "chibi-plush",
    rig: "",
    material: "",
    face: "",
    name: "Bloxy",
    accessory: "",
    accessoryZh: "",
    replaceAccessory: "",
    replaceAccessoryZh: "",
    noAccessories: false,
    temperament: "",
    signatureGaze: "",
    signatureGesture: "",
    conflictReaction: "",
    actingMoment: "",
    companion: "",
    cast: "",
    out: "",
    strict: false,
    lang: "en",
    json: false,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--json") opts.json = true;
    else if (arg === "--strict") opts.strict = true;
    else if (arg === "--no-accessories") opts.noAccessories = true;
    else if (arg === "--archetype" && argv[i + 1]) opts.archetype = argv[++i];
    else if (arg === "--rig" && argv[i + 1]) opts.rig = argv[++i];
    else if (arg === "--material" && argv[i + 1]) opts.material = argv[++i];
    else if (arg === "--face" && argv[i + 1]) opts.face = argv[++i].toLowerCase();
    else if (arg === "--name" && argv[i + 1]) opts.name = argv[++i];
    else if (arg === "--accessory" && argv[i + 1]) opts.accessory = argv[++i];
    else if (arg === "--accessory-zh" && argv[i + 1]) opts.accessoryZh = argv[++i];
    else if (arg === "--replace-accessory" && argv[i + 1]) opts.replaceAccessory = argv[++i];
    else if (arg === "--replace-accessory-zh" && argv[i + 1]) opts.replaceAccessoryZh = argv[++i];
    else if (arg === "--temperament" && argv[i + 1]) opts.temperament = argv[++i];
    else if (arg === "--signature-gaze" && argv[i + 1]) opts.signatureGaze = argv[++i];
    else if (arg === "--signature-gesture" && argv[i + 1]) opts.signatureGesture = argv[++i];
    else if (arg === "--conflict-reaction" && argv[i + 1]) opts.conflictReaction = argv[++i];
    else if (arg === "--acting-moment" && argv[i + 1]) opts.actingMoment = argv[++i];
    else if (arg === "--companion" && argv[i + 1]) opts.companion = argv[++i].toLowerCase();
    else if (arg === "--cast" && argv[i + 1]) opts.cast = argv[++i];
    else if (arg === "--out" && argv[i + 1]) opts.out = argv[++i];
    else if (arg === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
  }
  return opts;
}

export function buildAvatarSpec(rawOpts = {}) {
  const visIn = rawOpts.visualDNA && typeof rawOpts.visualDNA === "object" ? rawOpts.visualDNA : {};
  const perfIn = rawOpts.performanceDNA && typeof rawOpts.performanceDNA === "object" ? rawOpts.performanceDNA : {};
  const mergedArchetype = visIn.archetype || rawOpts.archetype;
  const mergedRig = visIn.rig || rawOpts.rig;
  const mergedMaterial = visIn.material || rawOpts.material;
  const mergedFace = visIn.face || rawOpts.face;

  if (rawOpts.strict) {
    if (mergedArchetype && !ARCHETYPES[mergedArchetype]) {
      throw new Error(`Unknown --archetype "${mergedArchetype}". Valid presets: ${Object.keys(ARCHETYPES).join(", ")}`);
    }
    if (mergedRig && !RIGS[mergedRig]) {
      throw new Error(`Unknown --rig "${mergedRig}". Valid rigs: ${Object.keys(RIGS).join(", ")}`);
    }
    if (mergedMaterial && !MATERIALS[mergedMaterial]) {
      throw new Error(`Unknown --material "${mergedMaterial}". Valid materials: ${Object.keys(MATERIALS).join(", ")}`);
    }
    if (mergedFace && !FACE_OVERRIDES[mergedFace]) {
      throw new Error(`Unknown --face "${mergedFace}". Valid faces: ${Object.keys(FACE_OVERRIDES).join(", ")}`);
    }
    if (rawOpts.companion && !COMPANIONS[rawOpts.companion]) {
      throw new Error(`Unknown --companion "${rawOpts.companion}". Valid companions: ${Object.keys(COMPANIONS).join(", ")}`);
    }
  }

  const archetypeKey = ARCHETYPES[mergedArchetype] ? mergedArchetype : "chibi-plush";
  const preset = ARCHETYPES[archetypeKey];
  const rigKey = RIGS[mergedRig] ? mergedRig : preset.defaultRig;
  const materialKey = MATERIALS[mergedMaterial] ? mergedMaterial : preset.defaultMaterial;
  const rig = RIGS[rigKey];
  const material = MATERIALS[materialKey];
  const name = rawOpts.name || "Bloxy";

  const faceOverride = mergedFace && FACE_OVERRIDES[mergedFace] ? FACE_OVERRIDES[mergedFace] : null;
  const faceEn = faceOverride ? faceOverride.en : preset.faceEn;
  const faceZh = faceOverride ? faceOverride.zh : preset.faceZh;

  const noAcc = Boolean(visIn.noAccessories ?? rawOpts.noAccessories);
  let accessoriesEn;
  let accessoriesZh;
  if (noAcc) {
    accessoriesEn = "none (clean bare silhouette, zero held props or back gear)";
    accessoriesZh = "无额外配饰与手持物（干净基础轮廓）";
  } else if (rawOpts.replaceAccessory) {
    accessoriesEn = rawOpts.replaceAccessory;
    accessoriesZh = rawOpts.replaceAccessoryZh || rawOpts.replaceAccessory;
  } else {
    const extraEn = rawOpts.accessory ? `, ${rawOpts.accessory}` : "";
    const extraZh = rawOpts.accessoryZh ? `、${rawOpts.accessoryZh}` : rawOpts.accessory ? `、${rawOpts.accessory}` : "";
    accessoriesEn = `${preset.accessoriesEn}${extraEn}`;
    accessoriesZh = `${preset.accessoriesZh}${extraZh}`;
  }

  const defaultPerf = DEFAULT_PERFORMANCE_DNA[archetypeKey] || DEFAULT_PERFORMANCE_DNA["chibi-plush"];
  const performanceDNA = {
    defaultTemperament: perfIn.defaultTemperament || rawOpts.temperament || defaultPerf.defaultTemperament,
    signatureGaze: perfIn.signatureGaze || rawOpts.signatureGaze || defaultPerf.signatureGaze,
    signatureGesture: perfIn.signatureGesture || rawOpts.signatureGesture || defaultPerf.signatureGesture,
    conflictReaction: perfIn.conflictReaction || rawOpts.conflictReaction || defaultPerf.conflictReaction,
    actingMomentEn: perfIn.actingMomentEn || rawOpts.actingMoment || defaultPerf.actingMomentEn,
    actingMomentZh: perfIn.actingMomentZh || rawOpts.actingMoment || defaultPerf.actingMomentZh
  };

  const companionObj = rawOpts.companion && COMPANIONS[rawOpts.companion] ? COMPANIONS[rawOpts.companion] : null;
  const companionPromptEn = companionObj ? ` Companion pet lock: ${companionObj.specEn}.` : "";
  const companionPromptZh = companionObj ? ` 随行方块宠物锁定：${companionObj.specZh}。` : "";

  const turnaroundPromptEn = [
    `Character turnaround reference sheet of "${name}", a Roblox-style 3D blocky figure shown in three full-body views side by side: front view, 45-degree three-quarter view, and side profile view.`,
    `Geometry lock: ${rig.geometryEn}, studless top head, zero Lego pegs, non-voxel.`,
    `Face lock: ${faceEn}, no 3D human nose.`,
    `Outfit & UGC accessories: ${preset.outfitEn}; accessories: ${accessoriesEn}.${companionPromptEn}`,
    `Material & lighting: ${material.shaderEn}, standing on a clean neutral warm-gray studio cyclorama background, 8k product render, consistent scale across all three views, zero brand logos.`
  ].join(" ");

  const turnaroundPromptZh = [
    `角色三视图设定卡（"${name}"），同一个Roblox风格3D方块小人并排展示全身正面视图、45度斜侧面视图与正侧面视图。`,
    `几何锁定：${rig.geometryZh}，头顶平滑无乐高凸起颗粒，非我的世界像素方块。`,
    `面部锁定：${faceZh}，严禁3D凸起真人鼻子。`,
    `穿搭与UGC配饰：${preset.outfitZh}；配饰：${accessoriesZh}。${companionPromptZh}`,
    `材质与布光：${material.shaderZh}，纯色浅暖灰摄影棚无缝背景，三视图身高比例与衣着细节完全一致，严禁任何官方商标Logo。`
  ].join("");

  const petNegEn = companionObj ? ", organic animal fur, reptile scales, sharp claws, talons, leathery bat wings, wet snout" : "";
  const petNegZh = companionObj ? "，真实动物毛发，爬行鳞片，锋利尖爪，蝙蝠皮膜翼，湿鼻头" : "";

  const palette = {
    head: preset.headColor,
    primary: preset.primaryColor,
    secondary: preset.secondaryColor,
    accent: preset.accentColor
  };
  const locks = {
    headAndFaceEn: faceEn,
    headAndFaceZh: faceZh,
    handsEn: "Fingerless and clawless solid 1x2x1 beveled rectangular block hands (zero human fingers, zero Lego C-shaped hooks)",
    handsZh: "平头倒角1x2x1实心方块手（严禁人类五指、严禁乐高C型钩子手）",
    outfitEn: preset.outfitEn,
    outfitZh: preset.outfitZh,
    accessoriesEn,
    accessoriesZh
  };

  return {
    name,
    archetype: archetypeKey,
    archetypeLabel: `${preset.labelZh} / ${preset.labelEn}`,
    rig: rigKey,
    rigLabel: rig.label,
    material: materialKey,
    materialLabel: material.label,
    face: mergedFace || "preset-default",
    visualDNA: {
      archetype: archetypeKey,
      rig: rigKey,
      material: materialKey,
      face: mergedFace || "preset-default",
      palette,
      locks
    },
    performanceDNA,
    companion: companionObj
      ? {
          id: rawOpts.companion,
          nameEn: companionObj.nameEn,
          nameZh: companionObj.nameZh,
          specEn: companionObj.specEn,
          specZh: companionObj.specZh
        }
      : null,
    palette,
    locks,
    shotAnchorEn: `${name} (${rigKey} blocky figure: ${preset.outfitEn}; ${faceEn}; accessories: ${accessoriesEn}; acting temperament: ${performanceDNA.defaultTemperament})`,
    shotAnchorZh: `${name}（${rigKey}方块小人：${preset.outfitZh}；${faceZh}；配饰：${accessoriesZh}；表演性格：${performanceDNA.defaultTemperament}）`,
    turnaroundPromptEn,
    turnaroundPromptZh,
    negativePromptEn: `${NEGATIVE_PROMPT_EN}${petNegEn}`,
    negativePromptZh: `${NEGATIVE_PROMPT_ZH}${petNegZh}`
  };
}

export function buildCastSpec(castDescriptor = "", sharedOpts = {}) {
  let members;
  if (Array.isArray(castDescriptor)) {
    if (castDescriptor.length === 0) {
      throw new Error(`Cast list must contain at least one character`);
    }
    members = castDescriptor.map((item, idx) => {
      const id = item.id || `cast_${idx + 1}`;
      const spec = buildAvatarSpec({
        ...sharedOpts,
        ...item,
        name: item.name || id
      });
      return { id, ...spec };
    });
  } else {
    const entries = String(castDescriptor)
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (entries.length === 0) {
      throw new Error(`--cast requires at least one entry in "archetype:Name[:rig[:face[:actingMoment]]]" format`);
    }
    members = entries.map((item, idx) => {
      const [archRaw, nameRaw, rigRaw, faceRaw, momentRaw] = item.split(":").map((x) => x.trim());
      const id = `cast_${idx + 1}_${(nameRaw || archRaw || `actor${idx + 1}`).toLowerCase().replace(/[^a-z0-9]+/g, "_")}`;
      const spec = buildAvatarSpec({
        archetype: archRaw || "classic-noob",
        name: nameRaw || `Actor${idx + 1}`,
        rig: rigRaw || sharedOpts.rig || "",
        material: sharedOpts.material || "",
        face: faceRaw || "",
        actingMoment: momentRaw || "",
        strict: sharedOpts.strict
      });
      return { id, ...spec };
    });
  }

  const cols = Math.min(4, Math.max(2, Math.ceil(Math.sqrt(members.length))));
  const rows = Math.ceil(members.length / cols);
  const panelListEn = members
    .map(
      (m, idx) =>
        `Panel ${idx + 1} (${m.name} · ${m.rig}): ${m.locks.outfitEn}, ${m.locks.accessoriesEn} — Instant acting beat: ${m.performanceDNA.actingMomentEn} (${m.performanceDNA.signatureGaze}, camera-facing solid 1x2x1 block hands)`
    )
    .join("; ");
  const panelListZh = members
    .map(
      (m, idx) =>
        `第${idx + 1}格（${m.name} · ${m.rig}）：${m.locks.outfitZh}，${m.locks.accessoriesZh} —— 标志性瞬间表演：${m.performanceDNA.actingMomentZh}（${m.performanceDNA.signatureGaze}，平头方手朝向镜头无遮挡）`
    )
    .join("；");

  const actingSheetPromptEn = `Unified ${cols}x${rows} Cast Acting Reference Sheet on one shared neutral warm-gray studio board showing ${members.length} distinct Roblox-style blocky characters under identical SmoothPlastic lighting and scale. Punchy toy-comedy reaction stills, one immediately readable story beat per cell, pupils tracking the trigger object, expressive asymmetrical eyebrows, canonical 2x2x1 torsos with flush 1x2x1 solid rectangular limbs, fingerless and clawless block hands, 1:1 studless barrel heads, readable without dialogue: ${panelListEn}. Zero official brand logos, zero Lego studs or C-claws, non-voxel.`;
  const actingSheetPromptZh = `同图统一角色瞬间表演设定板（${cols}x${rows}宫格，浅暖灰摄影棚底板，同一套SmoothPlastic布光与比例）：喜剧玩具插画式反应定格，每格不是静态站桩标签，而是“身份+瞬间表演”，瞳孔明确追踪触发反应的物件，眉毛允许高低不对称，遮住对白也能半秒读懂剧情：${panelListZh}。保持标准2x2x1躯干配并拢1x2x1实心平头方肢、1:1无颗粒桶状头、无官方商标Logo、无人类五指或乐高C型爪。`;

  return {
    castCount: members.length,
    gridLayout: `${cols}x${rows}`,
    members,
    combinedShotLockEn: members.map((m) => `[${m.id}] ${m.shotAnchorEn}`).join(" | "),
    combinedShotLockZh: members.map((m) => `[${m.id}] ${m.shotAnchorZh}`).join("；"),
    actingSheetPromptEn,
    actingSheetPromptZh,
    negativePromptEn: NEGATIVE_PROMPT_EN + ", character outfit swap, palette swap between characters, identity drift, static T-pose mannequin",
    negativePromptZh: NEGATIVE_PROMPT_ZH + "，角色衣服互换，双人串色，跨镜头换脸，呆板无眼神站桩"
  };
}

export function formatAvatarSpecMarkdown(spec, rawLang = "en") {
  const lang = normalizeLang(rawLang);
  const h = AVATAR_HEADERS[lang] || AVATAR_HEADERS.en;
  const useZhText = lang === "zh" || lang === "zh-tw" || lang === "zh-en";
  const lines = [];
  lines.push(`# ${h.title}: ${spec.name} (\`lang: ${lang}\`)`);
  lines.push("");
  lines.push(`| ${h.field} | ${h.spec} |`);
  lines.push("| --- | --- |");
  lines.push(`| Archetype | \`${spec.archetype}\` (${spec.archetypeLabel}) |`);
  lines.push(`| Rig | \`${spec.rig}\` (${spec.rigLabel}) |`);
  lines.push(`| Material | \`${spec.material}\` (${spec.materialLabel}) |`);
  lines.push(`| Hand Lock | ${useZhText ? `${spec.locks.handsZh} / ${spec.locks.handsEn}` : spec.locks.handsEn} |`);
  lines.push(`| Face Lock | ${useZhText ? spec.locks.headAndFaceZh : spec.locks.headAndFaceEn} |`);
  lines.push(`| Outfit | ${useZhText ? spec.locks.outfitZh : spec.locks.outfitEn} |`);
  lines.push(`| UGC Accessories | ${useZhText ? spec.locks.accessoriesZh : spec.locks.accessoriesEn} |`);
  if (spec.companion) {
    lines.push(
      `| Blocky Companion Pet | \`${spec.companion.id}\` — ${useZhText ? spec.companion.specZh : spec.companion.specEn} |`
    );
  }
  lines.push(`| Color Palette | Head \`${spec.palette.head}\` · Primary \`${spec.palette.primary}\` · Secondary \`${spec.palette.secondary}\` · Accent \`${spec.palette.accent}\` |`);
  lines.push("");

  lines.push(useZhText ? "## Performance DNA / 表演习惯与情绪语言锁" : "## Performance DNA (Acting & Attention Lock)");
  lines.push("");
  lines.push(`| ${h.field} | ${h.spec} |`);
  lines.push("| --- | --- |");
  lines.push(`| Default Temperament | \`${spec.performanceDNA.defaultTemperament}\` |`);
  lines.push(`| Signature Gaze | \`${spec.performanceDNA.signatureGaze}\` |`);
  lines.push(`| Signature Gesture | \`${spec.performanceDNA.signatureGesture}\` |`);
  lines.push(`| Conflict Reaction | \`${spec.performanceDNA.conflictReaction}\` |`);
  lines.push(
    `| Signature Acting Beat | ${useZhText ? spec.performanceDNA.actingMomentZh : spec.performanceDNA.actingMomentEn} |`
  );
  lines.push("");

  if (lang !== "zh") {
    lines.push("## 3-View Turnaround Image Prompt (English · Midjourney / Flux / GPT-4o)");
    lines.push("");
    lines.push("```text");
    lines.push(spec.turnaroundPromptEn);
    lines.push("```");
    lines.push("");
  }

  if (useZhText) {
    lines.push("## 角色三视图生成提示词 (中文 · 即梦 / 可灵参考图 / 万相)");
    lines.push("");
    lines.push("```text");
    lines.push(spec.turnaroundPromptZh);
    lines.push("```");
    lines.push("");
  }

  lines.push(`## ${h.neg}`);
  lines.push("");
  lines.push("```text");
  lines.push(lang === "zh" ? spec.negativePromptZh : useZhText ? `${spec.negativePromptEn}\n${spec.negativePromptZh}` : spec.negativePromptEn);
  lines.push("```");

  return lines.join("\n");
}

export function formatCastSpecMarkdown(castPack, rawLang = "en") {
  const lang = normalizeLang(rawLang);
  const useZhText = lang === "zh" || lang === "zh-tw" || lang === "zh-en";
  const lines = [];
  lines.push(`# Multi-Character Cast Lock Sheet (\`lang: ${lang}\`, \`${castPack.castCount}\` roles)`);
  lines.push("");
  lines.push("| Cast ID | Name | Archetype & Rig | Visual & Performance DNA Lock |");
  lines.push("| --- | --- | --- | --- |");
  for (const m of castPack.members) {
    const moment = useZhText ? m.performanceDNA.actingMomentZh : m.performanceDNA.actingMomentEn;
    lines.push(
      `| \`${m.id}\` | **${m.name}** | \`${m.archetype}\` · \`${m.rig}\` | ${useZhText ? m.shotAnchorZh : m.shotAnchorEn} · *Acting*: ${moment} |`
    );
  }
  lines.push("");
  lines.push("## 1. Cast Acting Sheet Prompt (Optional Shared-Canvas Exploration Board)");
  lines.push("");
  lines.push("> Director reference board (`" + castPack.gridLayout + "`): generates the whole cast's signature acting moments in one unified style pass. Inspect & crop individual avatars afterward rather than treating full-grid pixels as ground-truth hand topology.");
  lines.push("");
  lines.push("```text");
  lines.push(useZhText && lang === "zh" ? castPack.actingSheetPromptZh : castPack.actingSheetPromptEn);
  lines.push("```");
  lines.push("");
  lines.push("## 2. Individual Geometry Turnaround Sheets (3-View Proportion Locks)");
  lines.push("");
  for (const m of castPack.members) {
    lines.push(`### \`${m.id}\` · ${m.name}`);
    lines.push("```text");
    lines.push(useZhText && lang === "zh" ? m.turnaroundPromptZh : m.turnaroundPromptEn);
    lines.push("```");
    lines.push("");
  }
  return lines.join("\n");
}

function emitOutput(text, outPath) {
  if (outPath) {
    const abs = path.resolve(outPath);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, text.endsWith("\n") ? text : `${text}\n`, "utf8");
  } else {
    console.log(text);
  }
}

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("avatar_spec.mjs");
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    process.exit(0);
  }
  try {
    opts.strict = true;
    if (opts.cast) {
      const castPack = buildCastSpec(opts.cast, opts);
      const outText = opts.json ? JSON.stringify(castPack, null, 2) : formatCastSpecMarkdown(castPack, opts.lang);
      emitOutput(outText, opts.out);
    } else {
      const spec = buildAvatarSpec(opts);
      const outText = opts.json ? JSON.stringify(spec, null, 2) : formatAvatarSpecMarkdown(spec, opts.lang);
      emitOutput(outText, opts.out);
    }
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(1);
  }
}
