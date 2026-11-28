#!/usr/bin/env node
/**
 * shot_compiler.mjs
 * Zero-dependency CLI storyboard planner and spec compiler for 9:16 Roblox-style
 * blocky short videos — supporting both direct local 3D video rendering (`local3d`)
 * and optional external I2V engines (`kling`, `seedance`, `hailuo`, `wan`, `sora`, `runway`).
 */

import fs from "node:fs";
import path from "node:path";
import { buildAvatarSpec, buildCastSpec } from "./avatar_spec.mjs";

export const ACTING_ANCHORS = {
  "punchy-celebration": {
    en: "punchy toy-comedy celebration beat, one immediately readable triumph instant, pupils tracking the prize, asymmetrical raised brows, blocky torso contrast against stubby solid limbs, readable without dialogue",
    zh: "高张力玩具喜剧庆祝瞬间：只表达单一清晰胜利读点，瞳孔明确锁定战利品，眉毛高低上扬，方躯干与短粗实心方肢形成反差，遮住对白也能秒懂"
  },
  "deadpan-misunderstanding": {
    en: "deadpan toy-comedy contrast still, one immediately readable silent gag, flat horizontal Chill (-_-) calm beside chaos, pupils tracking the absurd trigger, entire joke readable without dialogue",
    zh: "冷面玩具喜剧反差定格：混乱旁保持死鱼眼(-_-)绝对淡定，瞳孔明确追踪荒诞触发源，只传达单一反差读点，无需字幕即可看懂笑点"
  },
  "guilty-glance": {
    en: "guilty toy-comedy micro-acting beat, torso oriented away while pupils dart sideways to track the incriminating prop, asymmetrical eyebrows (one lowered, one raised), instant subtext without dialogue",
    zh: "心虚偷瞄喜剧瞬间：身体朝向一侧而瞳孔斜向追踪关键道具，眉毛一高一低不对称，半秒读出角色小心思"
  },
  "overconfident-reveal": {
    en: "overconfident toy-comedy setup beat, forward-leaning 2x2x1 torso, smug asymmetrical Check-It brow, key prop presented cleanly on the camera-facing plane, readable without dialogue",
    zh: "自信亮牌玩具喜剧瞬间：2x2x1躯干前倾，挑眉坏笑，关键道具在朝向镜头的无遮挡平面清晰展示，遮住台词也能读懂"
  },
  "competitive-hesitation": {
    en: "punchy toy-comedy decision instant, one immediately readable beat, pupils tracking the contested target, asymmetrical eyebrows, forward-leaning torso with feet still planted, readable without dialogue",
    zh: "玩具喜剧抉择蓄力瞬间：只表达单一清晰动机，瞳孔死盯争夺目标，高低眉不对称，身体前倾但双脚未动，半秒读懂下一秒要冲刺"
  },
  "frozen-realization": {
    en: "punchy toy-comedy reaction still, one immediately readable shock beat, rigid torso recoiled 10 degrees, wide O_O ring eyes with pupils locked on the cause of disaster, readable without dialogue",
    zh: "玩具喜剧石化反应瞬间：刚性躯干后仰10度，震惊圆圈眼(O_O)瞳孔死锁翻车源头，遮住对白也能一眼读懂崩溃原因"
  }
};

export const VALID_INTERACTION_INTENTS = new Set(["hold", "present", "tap", "slam", "point", "drop", "receive"]);

const ENGINE_PROFILES = {
  local3d: { nativeClipSeconds: 4.0, label: "Local 3D Direct Video Engine (render_preview.mjs)" },
  kling: { nativeClipSeconds: 5.0, label: "Kling I2V (5s native -> trim to beat)" },
  seedance: { nativeClipSeconds: 5.0, label: "Seedance / Jimeng First+Last Frame I2V" },
  hailuo: { nativeClipSeconds: 6.0, label: "Hailuo Director I2V (6s native -> trim to beat)" },
  wan: { nativeClipSeconds: 5.0, label: "Wan 2.6 I2V (5s native -> trim to beat)" },
  sora: { nativeClipSeconds: 5.0, label: "Sora Rigid-Physics I2V (5s native -> trim to beat)" },
  runway: { nativeClipSeconds: 5.0, label: "Runway Gen-4 I2V (5s native -> trim to beat)" }
};

export const TEMPLATES = {
  "daily-meltdown": {
    titleZh: "周一早八闹钟破防记",
    titleEn: "Monday 8 AM Alarm Meltdown",
    defaultRig: "chibi-blocky",
    defaultMaterial: "glossy-vinyl",
    subjectEn: "a 2.4-head chibi blocky Roblox-style figure with a smooth studless cream 1:1 barrel head, flat 2D screen-printed face decal, fingerless and clawless solid 1x2x1 rectangular block hands, and a pastel matcha hoodie",
    subjectZh: "2.4头身SmoothPlastic材质Roblox方块小人（平滑无颗粒1:1桶状圆柱头、纯平2D丝网印刷五官贴图、1x2x1实心平头倒角方柱手、穿抹茶绿倒角方柱卫衣）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "pops its cylindrical blocky head rapidly up from behind a vibrating miniature twin-bell red alarm clock on the wooden desk",
        actionZh: "从木书桌剧烈震动的双铃红色微缩闹钟后方猛地探出桶状方块脑袋",
        faceEn: "wide hollow ring eyes (O_O) and an open rectangular gasp mouth painted flat on the face decal",
        faceZh: "脸部2D贴图呈现空心圆圈震惊眼(O_O)与长方形张嘴倒吸凉气表情",
        cameraEn: "Extreme close-up, rapid dolly push-in with subtle impact shake",
        cameraZh: "大特写机位极速推近，伴随闹钟震动的轻微镜头抖动",
        hailuoTag: "[Push in, Shake]",
        sfx: "刺耳电子闹钟声 + 塑料弹跳音",
        caption: "早八人的痛，谁懂？"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "pivots its rigid right 1x2x1 rectangular arm downward at the shoulder hinge so the flat block hand slams squarely onto the red alarm clock",
        actionZh: "右侧刚性方柱手臂沿肩部转轴干脆挥落，用1x2x1实心平头方柱手底面刚性拍扁闹钟",
        faceEn: "grumpy squinted line eyes (-_-) and a tiny wavy frown decal",
        faceZh: "2D贴图切换为起床气眯眯眼(-_-)与波浪小撇嘴",
        cameraEn: "Medium side-angle macro shot, 50mm f/2.8 shallow depth of field",
        cameraZh: "中景侧面微距机位，50mm f/2.8浅景深",
        hailuoTag: "[Static shot]",
        sfx: "清脆塑料拍击声 (Clack!)",
        caption: "再睡五分钟…就五分钟"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "sits stiffly before a glowing miniature laptop with recessed keycaps as blue 2D waterfall tear strips appear down its cheeks",
        actionZh: "笔直僵硬地坐在带键帽细节的发光微缩笔记本电脑前，脸颊两侧浮现蓝色2D瀑布流泪贴图条",
        faceEn: "streaming blue painted tear bands and a wailing rectangular mouth decal",
        faceZh: "双颊蓝色印刷宽面条眼泪贴图与委屈长方嘴",
        cameraEn: "Over-the-shoulder dolly arc to front medium close-up under cool screen light",
        cameraZh: "越肩镜头平滑环绕至正面中近景",
        hailuoTag: "[Pan right, Push in]",
        sfx: "密集消息提示音 + 委屈气泡音",
        caption: "打开电脑：99+ 未读消息"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "tilts its rigid 2x2x1 rectangular torso forward 90 degrees at the waist hinge and face-plants flat onto the laptop keyboard with a slight plastic bounce",
        actionZh: "2x2x1长方体躯干沿腰部机械转轴直挺挺向前折弯90度，平滑桶状脑袋啪地平拍在键盘上并轻微回弹",
        faceEn: "crossed KO dizzy eyes (X_X) painted flat on the head",
        faceZh: "2D贴图定格为眩晕叉叉眼(X_X)",
        cameraEn: "High-angle isometric lock-off shot matching the desk geometry of Shot 1",
        cameraZh: "45度高角度微缩模型固定俯拍，衔接第一镜桌面构图",
        hailuoTag: "[Tilt down, Static shot]",
        sfx: "经典闷响 (Oof!) + 键盘塑料声",
        caption: "已老实，申请重启人生"
      }
    ]
  },
  "duo-comedy": {
    titleZh: "精致潮人与黄皮新手的闺蜜反差",
    titleEn: "Fashion UGC vs Classic Noob Bestie Contrast",
    defaultRig: "r15",
    defaultMaterial: "matte-abs",
    subjectEn: "two contrasting Roblox-style blocky figures: on the left, a glossy Y2K streetwear blocky avatar with star sunglasses and purple backpack; on the right, a classic yellow-head blue-torso R6 Noob, both with fingerless and clawless solid 1x2x1 rectangular block hands",
    subjectZh: "同框反差双人Roblox方块小人：左侧为戴星星墨镜背紫色方盒包的Y2K潮牌方块小人，右侧为经典黄头蓝衣绿腿R6刚性新手小人（均为1x2x1实心平头方柱手与2D印刷五官）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "strike contrasting poses side by side: the Y2K avatar poses with solid 1x2x1 block hands on hips while the Classic Noob stands stiff like a wooden plank",
        actionZh: "并排反差亮相：左侧潮人小人1x2x1实心方柱手抵腰摆造型，右侧经典黄皮新手像木板一样笔直僵立",
        faceEn: "left avatar has a confident Check-It smirk decal; right Noob has the unchanging Default Smile decal",
        faceZh: "左侧自信挑眉坏笑2D贴图，右侧永恒不变的经典默认微笑贴图",
        cameraEn: "Fast snap-zoom into a two-shot medium framing on a smooth plaza stage",
        cameraZh: "中景双人同框极速推镜，平整广场地砖舞台背景",
        hailuoTag: "[Push in]",
        sfx: "时尚快门声 + 滑稽木鱼声",
        caption: "出门逛街：精修闺蜜 vs 我"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "the Y2K avatar performs a crisp 180-degree spin and accidentally bumps the Classic Noob with its boxy purple backpack",
        actionZh: "左侧潮人小人原地干脆转身180度，背上的紫色微缩方盒背包撞上右侧新手小人",
        faceEn: "left avatar winks; right Noob keeps the exact same blank smile while getting bumped",
        faceZh: "左侧眨眼贴图，右侧被撞瞬间依然保持一模一样的默认微笑",
        cameraEn: "Low-angle tracking shot capturing the backpack collision",
        cameraZh: "低角度微仰拍平移捕捉方块背包碰撞瞬间",
        hailuoTag: "[Pan left]",
        sfx: "清脆塑料撞击声 (Bonk!)",
        caption: "试图配合演出的我"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "the Classic Noob tips sideways at a rigid 45-degree angle as one unsegmented assembly without bending knees or elbows",
        actionZh: "右侧经典新手小人不弯膝盖不弯手肘，全身保持刚体呈45度直挺挺向侧方倾倒",
        faceEn: "unchanging painted smile on the Noob; shocked hollow ring eyes on the Y2K avatar",
        faceZh: "倾倒的新手依旧保持默认微笑，潮人小人切换为震惊圆圈眼贴图",
        cameraEn: "Medium wide static tripod shot with subtle impact shake",
        cameraZh: "中全景固定机位配合轻微震动反馈",
        hailuoTag: "[Shake, Static shot]",
        sfx: "经典倒地闷响 + 弹簧音",
        caption: "物理引擎：直接罢工"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "both blocky avatars slowly rotate only their 1:1 cylindrical heads 45 degrees to stare directly into the camera lens",
        actionZh: "两个方块小人身体完全静止，仅1:1桶状脑袋同时缓慢转动45度盯向镜头",
        faceEn: "synchronized deadpan horizontal line eyes (-_-) on both avatars",
        faceZh: "两人同步切换为沉默死鱼眼(-_-)2D贴图",
        cameraEn: "Slow dolly pull-back to the opening two-shot composition",
        cameraZh: "镜头缓慢拉远回到开场双人构图",
        hailuoTag: "[Pull out]",
        sfx: "轻微塑料转轴声 + 乌鸦飞过",
        caption: "确认过眼神，是亲闺蜜"
      }
    ]
  },
  "obby-storytime": {
    titleZh: "多巴胺天空跑酷闯关剧场",
    titleEn: "Pastel Sky Obby Parkour Storytime",
    defaultRig: "r6",
    defaultMaterial: "matte-abs",
    subjectEn: "a classic R6 Roblox-style blocky speedrunner with a smooth yellow 1:1 barrel head, cyan blocky jersey with white triangle emblem, red Speed Coil around right 1x2x1 solid arm, and fingerless flat block hands",
    subjectZh: "经典R6刚性比例Roblox跑酷方块小人（平滑亮黄1:1桶状头、印白色三角徽章的青色运动方柱上衣、右臂缠绕红色Speed Coil加速弹簧、1x2x1实心平头方柱手）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "leaps with stiff swinging 1x2x1 rectangular arms and legs across two floating pastel-pink beveled SmoothPlastic platforms high above fluffy blocky clouds",
        actionZh: "摆动笔直的1x2x1方柱四肢，在云海之上的两块马卡龙粉平滑倒角浮台间干脆跃过",
        faceEn: "determined wide 2D ink eyes and energetic open grin decal",
        faceZh: "专注大眼与活力露齿笑2D贴图",
        cameraEn: "Dynamic third-person follow camera closely trailing the blocky runner",
        cameraZh: "第三人称跟随镜头紧贴小人后方高速推进",
        hailuoTag: "[Push in, Tilt up]",
        sfx: "清脆跳跃弹簧音 (Boing!)",
        caption: "千万别往脚下看！"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "hops rhythmically across three rotating mint-green cylindrical rollers without bending its unsegmented R6 knees",
        actionZh: "保持膝盖笔直的R6刚体姿态，在三个旋转的薄荷绿圆柱滚筒上连续跳步通过",
        faceEn: "focused eyes with a single painted sweat drop on the temple",
        faceZh: "眼神紧盯前方，额角带一滴2D汗珠贴图",
        cameraEn: "Side-profile tracking shot moving parallel to the floating obstacle course",
        cameraZh: "侧面平行跟拍镜头展现浮空闯关纵深",
        hailuoTag: "[Pan right]",
        sfx: "连续塑料踏步清脆哒哒声",
        caption: "这波操作打几分？"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "skids to a halt at the edge of a translucent glass pad right before a glowing red Neon Killbrick bar, swinging stiff blocky arms for balance",
        actionZh: "在发光红色Neon激光砖前的半透明玻璃浮台边缘急停，双侧笔直方柱手臂摆动维持平衡",
        faceEn: "wide panicked ring eyes (O_O) and wavy mouth decal",
        faceZh: "惊慌圆圈眼(O_O)与波浪嘴2D贴图",
        cameraEn: "High-angle crane shot looking down into the cloud abyss",
        cameraZh: "高角度俯拍展现脚下云海深渊反差",
        hailuoTag: "[Tilt down]",
        sfx: "急刹车音效 + 警报声",
        caption: "差点踩上红砖激光！"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "leaps cleanly over the red Neon bar and lands squarely on the cyan-ring stage pad in the exact starting pose of Shot 1",
        actionZh: "干脆跃过红色激光砖，稳稳降落在发光青环终点浮台上，姿态与第一镜完全重合",
        faceEn: "cheerful Winning Grin (:D) victory decal",
        faceZh: "开心露齿大笑(:D)胜利贴图",
        cameraEn: "Return to third-person follow framing for seamless loop replay",
        cameraZh: "机位平滑归位至开场第三人称视角实现无缝循环",
        hailuoTag: "[Push in]",
        sfx: "通关叮咚音效 (Ding!)",
        caption: "丝滑过关，无缝循环"
      }
    ]
  },
  "mini-tycoon": {
    titleZh: "治愈系微缩羊角包咖啡馆",
    titleEn: "Cozy Miniature Croissant Café Tycoon",
    defaultRig: "chibi-blocky",
    defaultMaterial: "clay-soft",
    subjectEn: "a 2.4-head chibi blocky bakery chef with a puffy white blocky chef hat, caramel apron, flat 2D happy face decal, and fingerless solid 1x2x1 rectangular block hands",
    subjectZh: "2.4头身柔感塑料Roblox甜点师方块小人（戴圆角方块白厨师帽、焦糖棕围裙、纯平2D弯弯笑眼贴图、1x2x1实心平头方柱手）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "pops cheerfully up behind a sunlit wooden bakery counter beside a mint espresso machine and pastry case",
        actionZh: "在配有薄荷绿意式咖啡机与玻璃甜点柜的阳光木质吧台后方轻快弹起亮相",
        faceEn: "warm curved happy eyes (^^) and rosy cheek decals",
        faceZh: "弯弯笑眼(^^)配暖粉腮红2D贴图",
        cameraEn: "45-degree isometric macro view pushing gently toward the counter",
        cameraZh: "45度微缩模型微距俯拍轻推吧台",
        hailuoTag: "[Push in]",
        sfx: "治愈风铃声 + 烤箱叮声",
        caption: "欢迎光临微缩方块烘焙屋"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "docks a golden layered blocky croissant cleanly onto a pastel pink tray using its solid 1x2x1 rectangular block hands",
        actionZh: "用1x2x1实心平头方柱手将多层金黄方块羊角包稳稳摆入粉色托盘中",
        faceEn: "focused cute tongue-blep decal on the smooth cylindrical head",
        faceZh: "专注可爱的微吐舌头2D贴图",
        cameraEn: "Extreme macro close-up on the solid 1x2x1 rectangular block hands, flaky golden croissant, and espresso machine",
        cameraZh: "1x2x1实心平头方柱手、多层金黄羊角包与意式咖啡机的微距特写",
        hailuoTag: "[Static shot]",
        sfx: "清脆卡扣声 (Snap!)",
        caption: "强迫症极度舒适的摆盘"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "slides a sleeved hot latte cup smoothly across the cream counter with the flat face of its right 1x2x1 block hand",
        actionZh: "用右侧1x2x1实心方手平面推着带隔热套的热拿铁杯沿吧台稳稳滑出",
        faceEn: "sparkling star-eyed happy decal",
        faceZh: "闪亮星星眼开心2D贴图",
        cameraEn: "Side-profile counter tracking shot following the sliding latte cup",
        cameraZh: "沿吧台侧面平行跟拍拿铁杯滑行轨迹",
        hailuoTag: "[Pan left]",
        sfx: "杯底轻滑声 + 气泡音",
        caption: "今日份开心已出品"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "waves one stiff 1x2x1 rectangular arm happily as three glossy golden coin discs pop upward above the counter",
        actionZh: "单侧1x2x1刚性方柱手臂轻快挥动，吧台上方弹起三枚高光金色圆饼金币",
        faceEn: "beaming Winning Grin (:D) decal under warm pendant lamps",
        faceZh: "暖光吊灯下的治愈露齿笑(:D)2D贴图",
        cameraEn: "Gentle pull-back to the opening 45-degree isometric bakery view",
        cameraZh: "镜头轻柔拉回开场45度烘焙屋全景实现循环",
        hailuoTag: "[Pull out]",
        sfx: "清脆金币收集音 (Coin Chime!)",
        caption: "金币+999，明天继续营业"
      }
    ]
  },
  "outfit-drop": {
    titleZh: "T台卡点潮玩变装秀",
    titleEn: "Runway Beat-Drop UGC Outfit Transition",
    defaultRig: "r15",
    defaultMaterial: "glossy-vinyl",
    subjectEn: "an R15 Roblox-style blocky fashion avatar with a smooth 1:1 barrel head, flat 2D decal face, mechanical elbow/knee hinges, and fingerless solid 1x2x1 rectangular block hands on a glowing runway podium",
    subjectZh: "站在发光T台上的R15分段刚性Roblox穿搭方块小人（平滑1:1桶状头、纯平2D印刷五官、机械肘膝铰链、1x2x1实心平头方柱手）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "stands shyly in a plain matte-gray blocky base outfit under an unlit 5-star scoreboard arch, tilting its head down",
        actionZh: "身穿朴素浅灰基础款方块装站在未点亮的五星拱门T台上，桶状脑袋微垂",
        faceEn: "deadpan Chill (-_-) decal with a single shy sweat drop",
        faceZh: "害羞汗珠配死鱼眼(-_-)2D贴图",
        cameraEn: "High-angle medium shot pushing down toward the podium",
        cameraZh: "高角度中景缓慢下推营造蓄力感",
        hailuoTag: "[Push in, Tilt down]",
        sfx: "倒计时心跳节拍声",
        caption: "变装前：0星灰模小方块"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "leaps straight upward with rigid blocky legs spinning 360 degrees into a burst of neon star light",
        actionZh: "双侧方柱腿干脆发力垂直起跳并原地旋转360度切入霓虹光环",
        faceEn: "wide shocked O_O decal right before the beat drop",
        faceZh: "迎接重音卡点的圆圈眼2D贴图",
        cameraEn: "Rapid upward tilt following the spin jump",
        cameraZh: "随起跳快速上摇",
        hailuoTag: "[Tilt up]",
        sfx: "合成器升调蓄力音 (Riser)",
        caption: "3、2、1，准备卡点！"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "lands firmly on the glowing pink podium now dressed in a pink Y2K hoodie, twin pigtails, and a 5-point gold crown as all 5 overhead stars light up gold",
        actionZh: "重音落地瞬间完成换装：身穿粉色Y2K卫衣、双马尾配五尖金皇冠踏亮粉色T台，头顶五颗金星全亮",
        faceEn: "confident Check-It smirk decal",
        faceZh: "自信挑眉坏笑2D贴图",
        cameraEn: "Low-angle hero shot with impact shake and cyan/pink neon arch burst",
        cameraZh: "低角度仰拍英雄机位配霓虹拱门光效爆发",
        hailuoTag: "[Shake, Tilt up]",
        sfx: "重低音卡点爆发 (Bass Drop!)",
        caption: "五星神装已就位"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "strikes a crisp runway victory pose holding a pink boba cup docked flush to its right 1x2x1 solid block hand",
        actionZh: "右侧1x2x1实心平头方柱手刚性吸附粉色波霸奶茶杯定格T台胜利亮相",
        faceEn: "cool idol smile decal",
        faceZh: "酷飒微笑2D贴图",
        cameraEn: "Smooth 30-degree orbit around the glossy podium",
        cameraZh: "围绕高光T台平滑环绕30度",
        hailuoTag: "[Pan right]",
        sfx: "连续快门闪光声",
        caption: "这套穿搭给几星？"
      }
    ]
  },
  "meme-slapstick": {
    titleZh: "黑暗料理与刚体倒地梗图",
    titleEn: "Burnt Pizza Deadpan R6 Ragdoll Slapstick",
    defaultRig: "r6",
    defaultMaterial: "glossy-vinyl",
    subjectEn: "a classic R6 blocky bakery chef wearing a white toque hat and cream coat with fingerless solid 1x2x1 rectangular block hands in a checker-tile brick-oven kitchen",
    subjectZh: "棋盘格地砖砖炉厨房里头戴白色厨师高帽的R6刚性方块小人（1x2x1实心平头方柱手、纯平2D默认微笑贴图）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "proudly presents a smoking, completely charred pitch-black blocky pizza on a silver platter docked between both 1x2x1 block hands",
        actionZh: "双侧1x2x1实心平头方手稳稳端着银色圆托盘，上面冒着方块灰烟的披萨已烤得乌黑焦炭",
        faceEn: "cheerful unchanging Default Smile :) decal despite the disaster",
        faceZh: "面对灾难现场依然保持毫无波澜的经典2D默认微笑贴图",
        cameraEn: "Fast crash-zoom from medium shot to close-up",
        cameraZh: "从中景极速推至特写",
        hailuoTag: "[Push in]",
        sfx: "欢快小号突然走调",
        caption: "耗时三小时的诚意大作"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "stands completely motionless as the kitchen lights cut out into slate shadow under a single harsh top spotlight",
        actionZh: "全身保持绝对静止，厨房灯光骤暗仅剩一束冷白顶光直打在微笑桶状头上",
        faceEn: "exact same painted Default Smile :) staring forward",
        faceZh: "冷光阴影下一模一样的2D印刷微笑",
        cameraEn: "Locked-off frontal close-up, zero camera motion",
        cameraZh: "正脸特写死死固定机位",
        hailuoTag: "[Static shot]",
        sfx: "拉电闸咔哒声 + 低音弦乐",
        caption: "空气突然安静"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "the chef's right 1x2x1 rectangular arm block detaches cleanly at the Motor6D shoulder seam and clatters flat onto the counter beside the burnt pizza",
        actionZh: "小人右侧1x2x1方柱手臂沿Motor6D肩部接缝干脆脱落，啪嗒平掉在焦黑披萨旁的台面上",
        faceEn: "still smiling without blinking",
        faceZh: "依然眨都不眨地保持默认微笑贴图",
        cameraEn: "Medium shot tilting slightly down toward the detached arm block",
        cameraZh: "中景微下摇对准掉落台面的方柱手臂",
        hailuoTag: "[Tilt down]",
        sfx: "清脆部件散落声 (Clatter!)",
        caption: "心态与胳膊一起崩了"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "tips sideways at a strict 90-degree angle onto the checker-tile floor as one rigid statue without bending a single joint",
        actionZh: "全身不弯曲任何关节，像完整雕像一样呈90度直挺挺向侧面拍倒在棋盘格地板上",
        faceEn: "sideways Default Smile :) decal facing the lens from the floor",
        faceZh: "倒在地板上依然侧脸对镜头微笑",
        cameraEn: "Wide locked-off kitchen shot with tiny floor-impact shake",
        cameraZh: "厨房全景固定机位配轻微落地震动",
        hailuoTag: "[Shake, Static shot]",
        sfx: "经典闷响 (Oof!)",
        caption: "厨神生涯，到此为止"
      }
    ]
  },
  "disaster-survival": {
    titleZh: "自然灾害模拟器：高塔龙卷风",
    titleEn: "Natural Disaster Survival: Tornado Tower",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    subjectEn: "an authentic R6 blocky Classic Guest-style avatar wearing a plain unbranded red baseball cap and black jacket with a white geometric triangle chest emblem and flush 1x2x1 blocky legs (zero brand logos)",
    subjectZh: "头戴纯色无标红棒球帽、身穿黑底白色几何三角形胸章2x2x1夹克与并拢1x2x1方柱长裤的R6游客风小人（无任何品牌商标Logo）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "stands atop a multi-pillar green and wooden observation watchtower with yellow guardrails, pointing rigidly at a swirling dark-gray tornado funnel whipping flying planks across the grass island",
        actionZh: "站在带黄色护栏与木梁支架的绿色瞭望高塔顶端，抬起右侧1x2x1实心方柱手指向远处卷着木板碎片的深灰龙卷风漏斗",
        faceEn: "wide white shocked ring eyes (O_O) and open gasp mouth decal",
        faceZh: "震惊白圈眼(O_O)与张嘴倒吸凉气2D贴图",
        cameraEn: "Low-angle dramatic push-in with wind camera shake",
        cameraZh: "低角度仰拍极速推近伴随狂风震动",
        hailuoTag: "[Push in, Shake]",
        sfx: "警报蜂鸣声 + 呼啸风声",
        caption: "警报：黑色龙卷风来袭！"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "braces both flat solid 1x2x1 block hands squarely against the yellow guardrail bar as loose green tower planks rip upward into the vortex",
        actionZh: "双侧1x2x1实心平头方块手底面死死抵住黄色护栏横杆，塔顶松动木板被狂风卷向高空",
        faceEn: "upturned panicked brows and clenched teeth decal",
        faceZh: "慌张八字眉与咬牙2D贴图",
        cameraEn: "Medium tracking orbit around the swaying watchtower",
        cameraZh: "围绕摇晃塔顶的中景环绕跟拍",
        hailuoTag: "[Pan right, Shake]",
        sfx: "木板掀飞声 + 强风音",
        caption: "塔顶要塌了！抓紧！"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "hops desperately with unbent R6 legs onto the narrow surviving central deck pillar as outer planks fall away",
        actionZh: "保持R6直腿刚体姿态猛地跳向中间唯一幸存的窄方柱平台",
        faceEn: "streaming cyan waterfall tear bands decal",
        faceZh: "双颊青蓝瀑布流泪2D贴图",
        cameraEn: "High-angle crane shot looking down at the narrow surviving platform",
        cameraZh: "高角度俯拍孤立窄平台",
        hailuoTag: "[Tilt down]",
        sfx: "连续弹簧跳跃声",
        caption: "只剩最后一块平台了！"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "raises one rigid 1x2x1 arm straight up in victory on the lone tower platform under sudden clear blue sky",
        actionZh: "天空瞬间放晴，小人站在孤柱顶端高举单侧1x2x1刚性方臂庆祝存活",
        faceEn: "classic Winning Grin (:D) decal",
        faceZh: "经典露齿大笑(:D)贴图",
        cameraEn: "Smooth pull-back to wide grass island framing",
        cameraZh: "平稳拉远展示晴空孤塔全景",
        hailuoTag: "[Pull out]",
        sfx: "通关胜利欢呼音效",
        caption: "成功存活！毫发无损"
      }
    ]
  },
  "brookhaven-chase": {
    titleZh: "小镇警匪街头追逐",
    titleEn: "Brookhaven Street Police Chase",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    subjectEn: "two authentic Roblox R6 avatars on a smooth striped asphalt street: a Classic Noob sprinting ahead with a green money duffel docked to its right block hand and an R6 Police Officer in a navy cap and gold star badge chasing behind",
    subjectZh: "平整黄虚线柏油路上的双人R6追逐：前方经典黄皮新手右方手刚性吸附绿色钱袋狂奔，后方戴深蓝警帽佩金星警徽的R6警官紧追不舍",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "the yellow R6 Noob sprints down the striped asphalt street with a green cash duffel docked to its right 1x2x1 block hand while a police cruiser flashes red/blue sirens behind",
        actionZh: "经典黄皮R6新手右侧1x2x1实心方手吸附绿色钱袋冲上柏油马路，后方巡逻警车红蓝警灯交替闪烁",
        faceEn: "mischievous Check-It smirk decal on the Noob",
        faceZh: "黄皮新手印着挑眉坏笑(Check It)贴图",
        cameraEn: "Low front tracking shot pulling backward ahead of the runner",
        cameraZh: "贴地正前方倒退跟拍奔跑镜头",
        hailuoTag: "[Pull out, Shake]",
        sfx: "急促警笛声 (Wee-Woo!)",
        caption: "刚抢完小镇银行就遇熟人"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "the navy-uniformed R6 Police Officer swings stiff 1x2x1 arms and legs rapidly in pursuit along the sidewalk curb",
        actionZh: "身穿深蓝制服的R6警官沿路缘石高速摆动1x2x1笔直方肢全力追赶",
        faceEn: "angry Bloxxer scowling brow decal on the officer",
        faceZh: "警官满脸严肃的愤怒皱眉2D贴图",
        cameraEn: "Side-profile parallel speed pan along the street",
        cameraZh: "沿街道侧面高速平行横移跟拍",
        hailuoTag: "[Pan left]",
        sfx: "密集塑料脚步声 + 警哨声",
        caption: "前面那个黄方块站住！"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "the Noob trips over a red-and-yellow curbside fire hydrant and launches into a stiff horizontal R6 plank dive as the cash bag pops upward",
        actionZh: "黄皮新手绊到路边红黄消防栓，整个人保持笔直刚体呈水平飞扑出去，绿色钱袋高高抛起",
        faceEn: "wide shocked O_O ring eyes decal",
        faceZh: "瞬间切换为震惊白圈眼(O_O)贴图",
        cameraEn: "Medium close-up with impact shake",
        cameraZh: "中近景碰撞震动",
        hailuoTag: "[Shake]",
        sfx: "滑稽绊倒弹簧音 + Oof!",
        caption: "消防栓平地摔物理起飞"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "steel prison bars drop into the foreground as the officer stands calmly beside the sideways-toppled Noob",
        actionZh: "前景落下钢制铁窗栏杆，警官淡定站在侧翻倒地的新手旁",
        faceEn: "deadpan Chill (-_-) face decal on the Noob",
        faceZh: "倒地新手切换为安详死鱼眼(-_-)贴图",
        cameraEn: "Locked-off frontal two-shot",
        cameraZh: "正面双人定格固定镜头",
        hailuoTag: "[Static shot]",
        sfx: "铁门咔嚓落锁声",
        caption: "小镇一日游到此结束"
      }
    ]
  },
  "doors-horror": {
    titleZh: "惊悚酒店手电筒走廊",
    titleEn: "Doors Hotel Flashlight Hallway",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    subjectEn: "an authentic R6 blocky avatar in a sky-blue hoodie with a dark-slate flashlight docked forward from its right 1x2x1 solid rectangular arm inside a red-carpeted wooden hotel corridor",
    subjectZh: "红金地毯木质酒店走廊中，身穿天蓝连帽卫衣、右侧1x2x1实心方柱手朝前刚性吸附金属手电筒的R6主角小人",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "steps cautiously down the red hotel carpet sweeping its bright yellow flashlight beam onto wooden Door 050 with a brass plaque",
        actionZh: "沿酒店红毯迈着僵硬小步靠近挂有黄铜牌的050号木门，手电筒扫出明亮黄光",
        faceEn: "deadpan nervous horizontal eyes decal",
        faceZh: "紧张微眯一字眼2D贴图",
        cameraEn: "Over-the-shoulder slow push-in down the corridor",
        cameraZh: "越肩机位顺走廊缓慢推近",
        hailuoTag: "[Push in]",
        sfx: "木地板吱呀声 + 低频心跳",
        caption: "第50号门…千万别闪灯"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "freezes mid-step as the warm brass wall sconce violently flickers twice and plunges the corridor into dark slate shadow",
        actionZh: "墙上黄铜壁灯滋啦爆闪两下骤然熄灭，小人全身僵直停在半步姿态",
        faceEn: "wide white shocked ring eyes (O_O) decal",
        faceZh: "瞳孔骤缩的惊恐白圈眼(O_O)贴图",
        cameraEn: "Frontal medium close-up lit by flashlight bounce",
        cameraZh: "手电筒反光照亮的正面中近景",
        hailuoTag: "[Static shot]",
        sfx: "灯泡电流爆闪声",
        caption: "完了，灯真的闪了？！"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "rotates only its 1:1 barrel head 65 degrees backward as a dark sphere entity with two glowing white eyes materializes behind",
        actionZh: "身体静止不动，仅1:1桶状圆角头缓慢向后转动65度，身后黑暗浮现带两颗惨白发光眼的黑影",
        faceEn: "open silent gasp mouth decal",
        faceZh: "无声张嘴惊恐2D贴图",
        cameraEn: "Medium close-up rack-focus revealing the glowing eyes behind",
        cameraZh: "凸显身后发光白眼的中近景变焦",
        hailuoTag: "[Push in, Shake]",
        sfx: "深渊低吼渐强音",
        caption: "别回头！快躲衣柜！"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "pivots 180 degrees and steps stiffly into the louvered wooden wardrobe closet on the right",
        actionZh: "180度干脆转身，直挺挺闪进右侧百叶木衣柜中",
        faceEn: "wide eyes peeking from closet",
        faceZh: "衣柜前急促躲藏贴图",
        cameraEn: "Fast pan to the wooden louvered closet",
        cameraZh: "快速摇镜对准百叶木衣柜",
        hailuoTag: "[Pan right, Shake]",
        sfx: "木柜门砰响声",
        caption: "极限躲柜，险些重开"
      }
    ]
  },
  "sword-duel": {
    titleZh: "十字路口经典长剑对决",
    titleEn: "Crossroads Linked Sword 1v1 Duel",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    subjectEn: "two classic R6 blocky fighters on a smooth slate bridge between stone castle battlements over glowing molten lava: Builder Hard Hat in orange hoodie vs. Classic Noob, each with a silver Linked Sword (golden crossguard, blue grip) docked to its flat 1x2x1 block hand",
    subjectZh: "熔岩河上方平滑石桥与城堡垛口间的双人R6对决：戴黄安全帽穿橙卫衣的建造者 vs 经典黄皮新手，均在1x2x1实心平头方手上刚性吸附金护手蓝握柄的银色十字长剑",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "both R6 fighters raise their metallic Linked Swords (with golden crossguards and blue grips) upright between stone castle battlements on opposite ends of a SmoothPlastic slate bridge over glowing molten orange lava",
        actionZh: "滚烫熔岩河上方的平滑石桥与城堡垛口之间，两名R6剑客同时高举金护手蓝握柄的金属十字长剑摆出迎战姿态",
        faceEn: "confident smirk on Builder; determined grin on Noob",
        faceZh: "安全帽小人挑眉自信笑，黄皮新手露齿战意贴图",
        cameraEn: "Wide side-profile fighting framing pushing in",
        cameraZh: "横版格斗式侧面全景推镜",
        hailuoTag: "[Push in]",
        sfx: "经典拔剑金属音 (Unsheathe!)",
        caption: "经典十字剑1v1，谁赢？"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "both R6 avatars leap forward in a stiff double-jump and clash Linked Swords mid-air with a bright golden spark burst",
        actionZh: "两人同时刚体跃起空中拼刀，两把十字长剑交击迸出耀眼金色十字火花",
        faceEn: "intense angry Bloxxer brows on both fighters",
        faceZh: "双方同步切换为愤怒皱眉2D贴图",
        cameraEn: "Low-angle hero shot tilting upward into the mid-air clash",
        cameraZh: "低角度仰拍定格半空交剑火花",
        hailuoTag: "[Tilt up, Shake]",
        sfx: "清脆金属交击声 (Clang!)",
        caption: "空中拼刀！火花拉满"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "Builder lands a spin-slash that knocks the Noob sliding backward to the very edge of the slate bridge",
        actionZh: "安全帽小人落地横劈将黄皮新手击退滑行至石桥悬崖最边缘",
        faceEn: "shocked O_O decal on the Noob teetering at the ledge",
        faceZh: "黄皮新手边缘摇晃呈现震惊白圈眼(O_O)贴图",
        cameraEn: "Dynamic tracking pan to the bridge ledge",
        cameraZh: "高速横移跟拍至石桥悬崖边",
        hailuoTag: "[Pan right]",
        sfx: "重击声 + 碎石坠落音",
        caption: "差一毫米掉岩浆！"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "both fighters put away their swords and raise red Bloxy Cola cans docked to their flat block hands in a friendly truce toast",
        actionZh: "两人突然收剑停手，默契举起吸附在平头方手上的红色汽水罐碰杯言和",
        faceEn: "synchronized cheerful Default Smile :) decals",
        faceZh: "两人同步恢复经典默认微笑(:))贴图",
        cameraEn: "Pull-out to balanced two-shot on the slate bridge",
        cameraZh: "拉远定格在石桥友谊双人构图",
        hailuoTag: "[Pull out]",
        sfx: "汽水开罐声 (Tss-Ahhh!)",
        caption: "打累了，先干一罐汽水"
      }
    ]
  },
  "school-panic": {
    titleZh: "考场发卷大脑宕机记",
    titleEn: "Classroom Pop-Quiz Brain Meltdown",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    subjectEn: "an authentic R6 Bacon Hair student avatar seated at a wooden classroom desk with stacked textbooks and a printed exam sheet in front of a green chalkboard and red wall clock",
    subjectZh: "黑板与红框挂钟前、坐在摆有课本与试卷的木课桌后的3D棕发培根头R6学生小人",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "stares confidently down at the crisp white exam paper on the wooden desk while the red classroom wall clock ticks behind",
        actionZh: "自信低头看向木课桌上的白色试卷，身后黑板旁红框挂钟滴答走字",
        faceEn: "confident Default Smile :) decal before reading Question 1",
        faceZh: "看题前信心满满的默认微笑贴图",
        cameraEn: "High-angle close-up tilting from the exam sheet up to the face",
        cameraZh: "从桌面试卷上摇至脸部特写",
        hailuoTag: "[Tilt up]",
        sfx: "试卷拍桌声 + 秒针滴答声",
        caption: "考前：这把稳拿满分"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "raises both solid 1x2x1 blocky hands to the sides of its barrel head as yellow alert blocks pop up on each side",
        actionZh: "看清第一题瞬间，双侧1x2x1实心方柱手猛地抱住桶状脑袋，两侧弹出黄色惊叹方块",
        faceEn: "wide white shocked ring eyes (O_O) decal",
        faceZh: "瞳孔地震的震惊白圈眼(O_O)贴图",
        cameraEn: "Fast crash-zoom into the panicked 2D decal face",
        cameraZh: "极速推镜聚焦慌张2D贴图脸",
        hailuoTag: "[Push in, Shake]",
        sfx: "系统报错音效",
        caption: "第一题：完全没见过？！"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "scribbles rapidly across the exam sheet with a yellow blocky pencil docked to its right 1x2x1 solid block hand",
        actionZh: "右侧1x2x1实心方手吸附黄色方块铅笔在试卷上高速左右疾书",
        faceEn: "angry focused Bloxxer brows decal",
        faceZh: "咬牙奋笔疾书皱眉贴图",
        cameraEn: "Side desk macro shot with frantic vibration",
        cameraZh: "课桌侧面微距配合高频微震",
        hailuoTag: "[Shake]",
        sfx: "高速沙沙写字声 + 倒计时铃",
        caption: "不管了，先把解字写满"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "slumps stiffly backward against the chair with both 1x2x1 arms hanging straight down as the bell rings",
        actionZh: "下课铃响，小人全身刚体向后靠倒在椅背上，两条方柱手臂笔直垂落",
        faceEn: "crossed KO dizzy eyes (X_X) decal",
        faceZh: "大脑宕机的叉叉眼(X_X)贴图",
        cameraEn: "Slow overhead pull-back above the desk",
        cameraZh: "课桌上方俯拍缓慢拉远",
        hailuoTag: "[Pull out]",
        sfx: "下课铃声 + 放空风声",
        caption: "交卷那一刻，重获平静"
      }
    ]
  },
  "red-light-game": {
    titleZh: "一二三木头人极限急停",
    titleEn: "Red Light Green Light Freeze Challenge",
    defaultRig: "r6",
    defaultMaterial: "smooth-plastic",
    subjectEn: "two spaced R6 blocky runners (Cyan Obby Speedrunner with white triangle jersey on left, Classic Yellow Noob on right) racing across a smooth sandy arena with a traffic signal pole behind and a red-white checkered finish line ahead",
    subjectZh: "红绿灯信号杆前、沙地赛场上保持安全间距并排冲向红白格终点线的两名R6参赛者（左为印白三角徽章的青衣跑酷手，右为经典黄皮新手）",
    shots: [
      {
        role: "Hook / 黄金前3秒",
        actionEn: "both R6 avatars sprint joyfully forward across the sandy court while the center traffic signal glows bright green",
        actionZh: "信号杆亮起绿灯，两名R6方块小人在沙地赛场上迈开笔直方腿欢快向前冲刺",
        faceEn: "excited Winning Grin (:D) decals on both runners",
        faceZh: "两人脸上均印着兴奋露齿笑(:D)贴图",
        cameraEn: "Wide frontal tracking shot moving ahead of both runners",
        cameraZh: "双人正前方平行后退跟拍",
        hailuoTag: "[Pan right]",
        sfx: "轻快口令声 + 沙地踏步音",
        caption: "绿灯冲刺！终点就在眼前"
      },
      {
        role: "Escalation 1 / 动作推进",
        actionEn: "the traffic signal switches to crimson red and both R6 avatars freeze instantly mid-stride balanced on one 1x2x1 blocky leg",
        actionZh: "信号灯骤变红灯，两个小人瞬间在半步金鸡独立单方腿姿态死死定格",
        faceEn: "wide frozen shocked O_O ring eyes",
        faceZh: "不敢眨眼的震惊白圈眼(O_O)贴图",
        cameraEn: "Snap-zoom into the frozen one-legged R6 pose",
        cameraZh: "急推镜头定格滑稽单腿僵直造型",
        hailuoTag: "[Push in]",
        sfx: "刺耳红灯急停蜂鸣声 (BZZT!)",
        caption: "红灯！！连呼吸都停了"
      },
      {
        role: "Escalation 2 / 情绪升级",
        actionEn: "the Classic Noob wobbles 5 degrees sideways as one rigid plank while trying to hold balance beside the frozen Cyan runner",
        actionZh: "右侧黄皮新手单腿重心不稳整体轻微歪晃5度，左侧青衣小人死死屏住不动",
        faceEn: "panicked O_O eyes on both avatars",
        faceZh: "双人紧张圆圈眼对峙贴图",
        cameraEn: "Medium two-shot under tense red arena lighting",
        cameraZh: "红光氛围下的双人中景紧张定格",
        hailuoTag: "[Static shot]",
        sfx: "紧绷弦乐拔高 + 塑料嘎吱微响",
        caption: "兄弟你别晃啊！！"
      },
      {
        role: "Payoff & Loop / 反转收尾",
        actionEn: "the signal switches back to bright green and both R6 avatars dive forward at 42 degrees across the checkered finish line together",
        actionZh: "绿灯重新亮起，两人同时向前刚体前倾飞扑压过红白格子终点线",
        faceEn: "cheerful Winning Grin (:D) victory decals",
        faceZh: "劫后余生的胜利露齿大笑(:D)贴图",
        cameraEn: "High-angle finish-line celebration shot",
        cameraZh: "终点线高角度俯拍庆祝镜头",
        hailuoTag: "[Tilt down]",
        sfx: "通关礼花砰响声 + 欢呼声",
        caption: "压线过关！全员存活"
      }
    ]
  }
};

const NEGATIVE_GUARD =
  "official Roblox logo, tilted square Roblox trademark emblem, Roblox R badge, brand logos, watermarks, human fingers, five-fingered hand, Lego C-shaped claw hands, Lego hook hands, Lego top head studs, raised circular Lego floor studs, studded Lego baseplate, cylindrical brick pegs, Minecraft sharp voxel cube head, featureless blank single-box props, separated thin legs with thigh gap, protruding human sneakers, realistic human face, 3D protruding nose, skin pores, rubbery noodle limbs, soft-body limb bending, foot sliding, morphing clothes";

const NEGATIVE_GUARD_ZH =
  "官方Roblox商标Logo，倾斜方框标志，R字品牌徽标，任何品牌水印，人类五指，真实人手，乐高C型夹爪手，乐高钩子手，乐高头顶圆柱凸起颗粒，乐高地面凸起圆粒，乐高积木凸点底板，我的世界直角像素方块头，简陋无细节纯色单一方块道具，双腿分叉有空隙，外凸真人运动鞋，真实人类面部骨骼，3D凸起高鼻梁，皮肤毛孔，橡胶面条状软体弯曲四肢，脚底打滑，服装中途变形";

function printHelp() {
  console.log(`Usage:
  node scripts/shot_compiler.mjs --template <id> [options]
  node scripts/shot_compiler.mjs --spec <episode.json> [options]

Compile a 9:16 Roblox-style short-video storyboard from a built-in template OR a custom JSON episode spec.

Options:
  --spec <file>      Custom episode JSON file (supports custom cast[], props, and arbitrary shot counts!)
  --template <id>    Built-in template: ${Object.keys(TEMPLATES).join(" | ")} (default: daily-meltdown)
  --duration <sec>   Target duration: 15 | 30 | 45 (default: 15; 30s/45s expand into 8/12 UNIQUE beats)
  --engine <id>      Target engine: local3d | kling | seedance | hailuo | wan | sora | runway (default: local3d)
  --rig <id>         Override rig: chibi-blocky | r6 | r15
  --loop             Emit explicit last-frame prompts and loop Shot N back to Shot 1 Start-Frame
  --aspect <ratio>   Aspect ratio: 9:16 | 16:9 | 1:1 (default: 9:16)
  --topic <string>   Optional custom topic subtitle
  --lang <code>      Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en (default: en)
  --out <path>       Write UTF-8 output directly to file (prevents Windows PowerShell UTF-16 BOM issues)
  --json             Output structured JSON
  --help             Show this help message`);
}

const SUPPORTED_LANGS = new Set(["en", "zh", "zh-tw", "ja", "ko", "es", "fr", "de", "pt", "ru", "zh-en"]);

export function normalizeLang(code = "en") {
  const clean = String(code || "en").toLowerCase().trim();
  if (clean === "zh-cn") return "zh";
  if (clean === "pt-br") return "pt";
  return SUPPORTED_LANGS.has(clean) ? clean : "en";
}

export function parseArgs(argv) {
  const opts = {
    spec: "",
    template: "daily-meltdown",
    templateExplicit: false,
    duration: 15,
    durationExplicit: false,
    engine: "kling",
    rig: "",
    loop: false,
    strict: false,
    aspect: "9:16",
    topic: "",
    out: "",
    lang: "en",
    json: false,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--json") opts.json = true;
    else if (arg === "--loop") opts.loop = true;
    else if (arg === "--strict") opts.strict = true;
    else if ((arg === "--spec" || arg === "--input" || arg === "--shots-file") && argv[i + 1]) opts.spec = argv[++i];
    else if (arg === "--template" && argv[i + 1]) {
      opts.template = argv[++i];
      opts.templateExplicit = true;
    } else if (arg === "--duration" && argv[i + 1]) {
      opts.duration = Number(argv[++i]);
      opts.durationExplicit = true;
    } else if (arg === "--engine" && argv[i + 1]) opts.engine = argv[++i].toLowerCase();
    else if (arg === "--rig" && argv[i + 1]) opts.rig = argv[++i].toLowerCase();
    else if (arg === "--aspect" && argv[i + 1]) opts.aspect = argv[++i];
    else if (arg === "--topic" && argv[i + 1]) opts.topic = argv[++i];
    else if (arg === "--out" && argv[i + 1]) opts.out = argv[++i];
    else if (arg === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
  }
  return opts;
}

/**
 * Expand a 4-shot template into 8 or 12 UNIQUE progressive beats without modulo-recycling
 * or firing checkpoints/payoffs prematurely in the middle of the episode!
 */
function expandTemplateBeats(baseShots, targetShotCount) {
  if (targetShotCount === baseShots.length) {
    return baseShots.map((s) => ({ ...s }));
  }
  const [s1, s2, s3, s4] = baseShots;
  if (targetShotCount === 8) {
    return [
      { ...s1, role: "01 · Hook Opening / 黄金开场" },
      {
        role: "02 · Hook Reaction / 悬念放大",
        actionEn: `holds its rigid blocky stance and pivots its 1:1 cylindrical head sharply to lock onto the obstacle ahead (${s1.actionEn.slice(0, 48)}...)`,
        actionZh: `定住刚性方块身姿并干脆转动1:1桶状头聚焦前方目标，承接开场悬念`,
        faceEn: s1.faceEn,
        faceZh: s1.faceZh,
        cameraEn: "Tight medium close-up rack-focus from the character's 2D face decal to the target ahead",
        cameraZh: "紧凑中近景焦点从2D贴图脸切向前方目标",
        hailuoTag: "[Push in]",
        sfx: "紧张提示音 (Ping!)",
        caption: s1.caption
      },
      { ...s2, role: "03 · Rising Action A / 动作推进" },
      {
        role: "04 · Midpoint Shift / 中段变奏",
        actionEn: "pauses for half a beat on flat blocky feet to steady its balance as lighting and camera perspective shift across the set",
        actionZh: "双侧平底方腿稳稳踏住平整地面微顿半拍稳住重心，切入中段视角转换",
        faceEn: s2.faceEn,
        faceZh: s2.faceZh,
        cameraEn: "Low-angle 45-degree side tracking shot emphasizing rigid 2x2x1/1x2x1 silhouette",
        cameraZh: "45度低角度侧面跟拍凸显标准方块比例轮廓",
        hailuoTag: "[Pan right]",
        sfx: "清脆塑料踏步定音",
        caption: "稳住节奏，继续推进！"
      },
      { ...s3, role: "05 · Escalation Peak / 危机升级" },
      {
        role: "06 · Climax Hold / 极限拉扯",
        actionEn: "leans its rigid 2x2x1 rectangular torso 15 degrees at the waist hinge on the brink of tipping while stiff 1x2x1 arms counterbalance",
        actionZh: "2x2x1刚性躯干沿腰部转轴前倾15度处于失衡边缘，双侧笔直方臂反向摆动拉住重心",
        faceEn: s3.faceEn,
        faceZh: s3.faceZh,
        cameraEn: "Extreme close-up Dutch-tilt tension framing with subtle camera vibration",
        cameraZh: "微倾斜大特写配合紧张微震",
        hailuoTag: "[Shake, Static shot]",
        sfx: "心跳加速鼓点",
        caption: "千钧一发！！"
      },
      {
        role: "07 · Climax Release / 终局触发",
        actionEn: "commits to one decisive rigid Motor6D hinge movement into the final beat transition",
        actionZh: "沿Motor6D机械转轴做出最后一记干脆果断的刚性动作切入终局",
        faceEn: s4.faceEn,
        faceZh: s4.faceZh,
        cameraEn: "Wide dynamic follow shot bridging into the final payoff framing",
        cameraZh: "全景动态跟拍衔接收尾机位",
        hailuoTag: "[Tilt down]",
        sfx: "转折重音音效 (Whoosh!)",
        caption: "最后一搏！"
      },
      { ...s4, role: "08 · Final Payoff & Loop / 终局反转" }
    ];
  }

  // 12-shot 45s progressive arc (guaranteed 12 distinct actions, payoff only on Shot 12)
  const eight = expandTemplateBeats(baseShots, 8);
  return [
    eight[0],
    eight[1],
    {
      role: "03 · World & Prop Reveal / 场景道具亮牌",
      actionEn: "steps one crisp R6 stride forward into the main set zone, aligning its flat block hand with the primary scene prop",
      actionZh: "向前迈出一步干脆的R6方块步进入核心场景区，平头方手对准关键道具",
      faceEn: s1.faceEn,
      faceZh: s1.faceZh,
      cameraEn: "Wide architectural establishing tracking shot across smooth studless surfaces",
      cameraZh: "展现平整无凸粒场景与多部件道具的全景横移",
      hailuoTag: "[Pan left]",
      sfx: "环境氛围音切入",
      caption: "正式进入主战场"
    },
    { ...eight[2], role: "04 · First Attempt / 初次出手" },
    { ...eight[3], role: "05 · Midpoint Check / 中盘定格" },
    {
      role: "06 · Unexpected Complication / 突发阻碍",
      actionEn: "recoils half a stud backward as one rigid assembly when an unexpected obstacle shifts in front of it",
      actionZh: "前方突发阻碍变化，小人整体保持刚体后仰半格距离",
      faceEn: "wide hollow shocked ring eyes (O_O) decal",
      faceZh: "震惊白圈眼(O_O)2D贴图",
      cameraEn: "Snap push-in onto the obstacle and shocked 2D decal face",
      cameraZh: "急推聚焦阻碍物与震惊2D贴图脸",
      hailuoTag: "[Push in, Shake]",
      sfx: "突发警报音",
      caption: "等等，情况不对？！"
    },
    { ...eight[4], role: "07 · Crisis Escalation / 危机爆发" },
    { ...eight[5], role: "08 · Brink of Failure / 悬崖边缘" },
    {
      role: "09 · Deadpan Micro-Beat / 暴风眼沉默",
      actionEn: "freezes completely motionless for two seconds while only the background hazard or lighting shifts around its glossy head",
      actionZh: "全身死死静止两秒不动，仅周围光影在平滑桶状头表面流转",
      faceEn: "deadpan horizontal Chill (-_-) line eyes decal",
      faceZh: "极致反差的沉默死鱼眼(-_-)贴图",
      cameraEn: "Locked-off frontal close-up, zero camera motion",
      cameraZh: "零运镜正脸特写定格",
      hailuoTag: "[Static shot]",
      sfx: "空气突然安静",
      caption: "大脑飞速运转中…"
    },
    { ...eight[6], role: "10 · Final Commit / 绝地动作" },
    {
      role: "11 · Impact Settlement / 落地余波",
      actionEn: "absorbs the final landing with a tiny rigid plastic bounce on the smooth floor without bending knees or elbows",
      actionZh: "落回平整地面产生一下轻微刚性塑料回弹，全程不弯膝肘",
      faceEn: s4.faceEn,
      faceZh: s4.faceZh,
      cameraEn: "Medium-wide tripod shot capturing the clean rigid landing",
      cameraZh: "中全景固定机位捕捉刚体落地",
      hailuoTag: "[Static shot]",
      sfx: "清脆塑料落地声",
      caption: "尘埃落定！"
    },
    { ...eight[7], role: "12 · Final Payoff & Loop / 终局收尾" }
  ];
}

function composeActingDirectives(shot = {}) {
  const anchorKey = shot.actingAnchor && ACTING_ANCHORS[shot.actingAnchor] ? shot.actingAnchor : "";
  const anchor = anchorKey ? ACTING_ANCHORS[anchorKey] : null;
  const perf = shot.performance && typeof shot.performance === "object" ? shot.performance : {};
  const inter = shot.interaction && typeof shot.interaction === "object" ? shot.interaction : null;

  const momentPartsEn = [];
  const momentPartsZh = [];
  if (shot.beatIntent) momentPartsEn.push(`Beat intent: ${shot.beatIntent}`);
  if (shot.beatIntentZh || shot.beatIntent) momentPartsZh.push(`表演动机：${shot.beatIntentZh || shot.beatIntent}`);
  if (shot.audienceRead) momentPartsEn.push(`Instant audience read: ${shot.audienceRead}`);
  if (shot.audienceReadZh || shot.audienceRead) momentPartsZh.push(`半秒观众读点：${shot.audienceReadZh || shot.audienceRead}`);
  if (anchor) {
    momentPartsEn.push(`Acting anchor (${anchorKey}): ${anchor.en}`);
    momentPartsZh.push(`表演参考（${anchorKey}）：${anchor.zh}`);
  }

  const attnPartsEn = [];
  const attnPartsZh = [];
  if (perf.gazeTarget) {
    attnPartsEn.push(`pupils tracking "${perf.gazeTarget}"`);
    attnPartsZh.push(`瞳孔明确追踪「${perf.gazeTarget}」`);
  }
  if (perf.reactionCause) {
    attnPartsEn.push(`triggered by ${perf.reactionCause}`);
    attnPartsZh.push(`前因触发：${perf.reactionCauseZh || perf.reactionCause}`);
  }
  if (perf.eyebrows) {
    attnPartsEn.push(`eyebrows: ${perf.eyebrows}`);
    attnPartsZh.push(`眉型：${perf.eyebrows}`);
  }
  if (perf.bodyAttitude) {
    attnPartsEn.push(`body attitude: ${perf.bodyAttitude}`);
    attnPartsZh.push(`体态重心：${perf.bodyAttitude}`);
  }

  let interactionEn = "";
  let interactionZh = "";
  if (inter && inter.propId) {
    const hand = inter.hand || "right";
    const intent = inter.intent || "hold";
    const contact = inter.contact || "flush-flat";
    const vis = inter.visibility || "camera-facing";
    interactionEn = `Hand-prop interaction: ${hand} fingerless solid 1x2x1 block hand executes "${intent}" on "${inter.propId}" (${contact} contact, ${vis} plane, never occluded by torso).`;
    interactionZh = `手与道具关系：${hand}侧无指1x2x1实心平头方手对「${inter.propId}」执行「${intent}」（${contact}刚性接触，处于${vis}镜头可见面，严禁被身体遮挡）。`;
  }

  const leadPrefixEn = [
    momentPartsEn.length > 0 ? `${momentPartsEn.join(" | ")}.` : "",
    attnPartsEn.length > 0 ? `Attention & gaze: ${attnPartsEn.join(", ")}.` : "",
    interactionEn
  ]
    .filter(Boolean)
    .join(" ");

  const leadPrefixZh = [
    momentPartsZh.length > 0 ? `${momentPartsZh.join("｜")}。` : "",
    attnPartsZh.length > 0 ? `注意力与视线：${attnPartsZh.join("，")}。` : "",
    interactionZh
  ]
    .filter(Boolean)
    .join("");

  return { leadPrefixEn, leadPrefixZh };
}

function formatEnginePrompt(shot, subjectEn, subjectZh, envEn, envZh, engine, aspect, rig, isLoopFinal, shot1StartEn, shot1StartZh) {
  const { leadPrefixEn, leadPrefixZh } = composeActingDirectives(shot);
  const actEn = leadPrefixEn ? `${leadPrefixEn} ` : "";
  const actZh = leadPrefixZh ? `${leadPrefixZh}` : "";

  const rigTailEn =
    rig === "r15"
      ? "Roblox R15 segmented blocky rig (2x2x1 torso, flush 1x2x1 rigid limb segments rotating strictly at mechanical 90-degree elbow/knee hinges, zero soft-body noodle bending, fingerless and clawless flat beveled block hands)"
      : "Canonical Roblox 2x2x1 torso and flush 1x2x1 unsegmented solid rectangular limbs (Motor6D rigid shoulder/hip hinges only, zero soft-body deformation, fingerless and clawless flat beveled block hands)";
  const rigTailZh =
    rig === "r15"
      ? "Roblox R15分段刚性方块骨架（2x2x1躯干配并拢齐平1x2x1上下肢刚性方块，仅沿肘膝机械铰链折角转动、严禁面条弯曲，无指无爪平头方手）"
      : "纯正Roblox 2x2x1长方体躯干配并拢齐平1x2x1无分段实心平头方柱四肢（仅肩髋Motor6D刚性转轴、零软体形变、无人类五指与乐高C型爪）";

  const worldTailEn = `${rigTailEn}, 1:1 studless barrel-beveled cylindrical head with flat 2D screen-printed face decal, ${
    envEn || "smooth Roblox SmoothPlastic / WoodPlanks / Concrete surfaces (zero raised circular Lego floor studs) with detailed multi-part props"
  }, unbranded geometric triangle emblems only.`;
  const worldTailZh = `${rigTailZh}，1:1平滑无颗粒桶状圆角头配纯平2D印刷五官贴图，${
    envZh || "平整无圆粒凸起的Roblox SmoothPlastic/木板/混凝土表面（严禁乐高地面凸点）与多部件精致道具"
  }，无任何官方品牌商标。`;

  let i2vPromptEn = "";
  let i2vPromptZh = "";

  // Prompt priority order: 1. Beat Moment & Gaze -> 2. Hand-Prop Interaction -> 3. Cast Anchor -> 4. Single Action & Camera -> 5. Geometry/World Guard
  switch (engine) {
    case "local3d":
      i2vPromptEn = `[Local 3D Render · ${aspect}] ${actEn}Cast: ${subjectEn}. Single action: ${shot.actionEn}. Decal: ${shot.faceEn}. Camera: ${shot.cameraEn}. ${worldTailEn}`;
      i2vPromptZh = `【本地3D直出渲染 · ${aspect}】${actZh}角色：${subjectZh}。单镜动作：${shot.actionZh}。贴图：${shot.faceZh}。运镜：${shot.cameraZh}。${worldTailZh}`;
      break;
    case "hailuo":
      i2vPromptEn = `${shot.hailuoTag || "[Static shot]"} (${aspect} vertical, ${rig} rig) ${actEn}Featuring ${subjectEn}. Single action: ${shot.actionEn}, showing ${shot.faceEn}. Props docked flush to flat block hands. ${worldTailEn}`;
      i2vPromptZh = `${shot.hailuoTag || "[Static shot]"}（${aspect}竖屏，${rig}骨架）${actZh}主体为${subjectZh}。单镜动作：${shot.actionZh}，面部呈现${shot.faceZh}。手持物与实心方手底面刚性吸附。${worldTailZh}`;
      break;
    case "seedance":
      i2vPromptEn = `[Seedance First+Last Frame I2V · ${aspect}] ${actEn}${shot.cameraEn}. ${subjectEn}. Single action: ${shot.actionEn} with crisp Motor6D timing; ${shot.faceEn}. ${worldTailEn}`;
      i2vPromptZh = `【即梦/Seedance首尾帧I2V · ${aspect}】${actZh}${shot.cameraZh}。${subjectZh}。单镜动作：${shot.actionZh}，${shot.faceZh}。动作干脆有刚体节奏感，${worldTailZh}`;
      break;
    case "wan":
      i2vPromptEn = `${aspect} vertical 3D Roblox SmoothPlastic render. ${actEn}${shot.cameraEn}. Subject: ${subjectEn}. Single action: ${shot.actionEn}. Expression: ${shot.faceEn}. ${worldTailEn}`;
      i2vPromptZh = `${aspect}竖屏3D纯正Roblox渲染。${actZh}${shot.cameraZh}。主体：${subjectZh}。单镜动作：${shot.actionZh}，${shot.faceZh}。${worldTailZh}`;
      break;
    case "sora":
      i2vPromptEn = `Camera (${aspect}, 35mm macro lens): ${shot.cameraEn}. ${actEn}Subject (${rig}): ${subjectEn}. Action: ${shot.actionEn} while maintaining ${shot.faceEn}. Physics: Strict rigid-body Motor6D hinge rotation, zero soft-body limb deformation, props welded flush to flat block hands. ${worldTailEn}`;
      i2vPromptZh = `机位与镜头（${aspect}，35mm微距镜头）：${shot.cameraZh}。${actZh}主体（${rig}）：${subjectZh}。单镜动作：${shot.actionZh}，保持${shot.faceZh}。物理约束：严格刚体铰链转动、零软体弯曲变形、道具刚性贴合平头方手。${worldTailZh}`;
      break;
    case "runway":
      i2vPromptEn = `Camera (${aspect}): ${shot.cameraEn}. ${actEn}Subject (${rig}): ${subjectEn}. Action: ${shot.actionEn} while maintaining ${shot.faceEn}. Physics: ${worldTailEn}`;
      i2vPromptZh = `机位（${aspect}）：${shot.cameraZh}。${actZh}主体（${rig}）：${subjectZh}。单镜动作：${shot.actionZh}，${shot.faceZh}。物理约束：${worldTailZh}`;
      break;
    case "kling":
    default:
      i2vPromptEn = `[Kling I2V · ${aspect}] ${actEn}${subjectEn}. Single action: ${shot.actionEn}. Facial decal: ${shot.faceEn}. Camera: ${shot.cameraEn}. ${worldTailEn}`;
      i2vPromptZh = `【可灵I2V · ${aspect}】${actZh}${subjectZh}。单镜动作：${shot.actionZh}，${shot.faceZh}。运镜：${shot.cameraZh}。${worldTailZh}`;
      break;
  }

  const firstFramePromptEn =
    shot.firstFrameEn ||
    `${aspect} vertical keyframe still. ${actEn}${shot.cameraEn}. ${subjectEn} positioned at the start of the beat (${shot.actionEn}), displaying ${shot.faceEn}. ${worldTailEn}`;
  const firstFramePromptZh =
    shot.firstFrameZh ||
    `${aspect}竖屏首帧关键帧静帧。${actZh}${shot.cameraZh}。${subjectZh}处于动作起始位（${shot.actionZh}），面部呈现${shot.faceZh}。${worldTailZh}`;

  const lastFramePromptEn = isLoopFinal
    ? `[LOOP LOCK = REUSE SHOT 01 FIRST FRAME] ${shot1StartEn}`
    : shot.endFrameEn ||
      `${aspect} vertical end-frame still after completing single action (${shot.actionEn}), holding ${shot.faceEn}. ${worldTailEn}`;
  const lastFramePromptZh = isLoopFinal
    ? `【无缝循环尾帧 = 直接复用镜头01首帧】${shot1StartZh}`
    : shot.endFrameZh ||
      `${aspect}竖屏动作完成定格尾帧（完成：${shot.actionZh}），面部定格为${shot.faceZh}。${worldTailZh}`;

  return {
    firstFramePromptEn,
    firstFramePromptZh,
    lastFramePromptEn,
    lastFramePromptZh,
    i2vPromptEn,
    i2vPromptZh
  };
}

const THEME3D_TO_ARCHETYPE = {
  noob: "classic-noob",
  bacon: "bacon-hair",
  guest: "classic-guest",
  builderman: "builderman",
  zombie: "zombie-r6",
  chef: "cozy-chef",
  obby: "obby-runner",
  y2k: "ugc-streetwear",
  theo: "corporate-worker",
  commuter: "chibi-plush",
  clerk: "corporate-worker"
};

function buildCastLocksFromSpec(castArray = [], defaultRig = "r6", defaultMaterial = "smooth-plastic") {
  return castArray.map((c, idx) => {
    const id = c.id || `actor_${idx + 1}`;
    const vis = c.visualDNA && typeof c.visualDNA === "object" ? c.visualDNA : {};
    const themeHint = String(vis.theme3d || c.theme3d || c.theme || "").toLowerCase();
    const rawArch = vis.archetype || c.archetype;
    const resolvedArchetype =
      rawArch && rawArch !== "classic-noob"
        ? rawArch
        : THEME3D_TO_ARCHETYPE[themeHint] || rawArch || "classic-noob";
    const built = buildAvatarSpec({
      archetype: resolvedArchetype,
      name: c.name || id,
      rig: vis.rig || c.rig || defaultRig,
      material: vis.material || c.material || defaultMaterial,
      face: vis.face || c.face || "",
      accessory: vis.accessory || c.accessory || "",
      accessoryZh: vis.accessoryZh || c.accessoryZh || "",
      replaceAccessory: vis.replaceAccessory || c.replaceAccessory || "",
      replaceAccessoryZh: vis.replaceAccessoryZh || c.replaceAccessoryZh || "",
      noAccessories: Boolean(vis.noAccessories ?? c.noAccessories),
      companion: vis.companion || c.companion || "",
      visualDNA: c.visualDNA,
      performanceDNA: c.performanceDNA
    });
    return {
      id,
      name: built.name,
      rig: built.rig,
      archetype: built.archetype,
      visualDNA: built.visualDNA,
      performanceDNA: built.performanceDNA,
      shotAnchorEn: c.customDescEn || built.shotAnchorEn,
      shotAnchorZh: c.customDescZh || built.shotAnchorZh,
      turnaroundPromptEn: built.turnaroundPromptEn,
      turnaroundPromptZh: built.turnaroundPromptZh
    };
  });
}

export function compileStoryboard(rawOpts = {}) {
  const engineRaw = (rawOpts.engine || "kling").toLowerCase();
  if (rawOpts.strict && !ENGINE_PROFILES[engineRaw]) {
    throw new Error(`Unsupported --engine "${rawOpts.engine}". Valid engines: ${Object.keys(ENGINE_PROFILES).join(", ")}`);
  }
  const engine = ENGINE_PROFILES[engineRaw] ? engineRaw : "kling";
  const engineProfile = ENGINE_PROFILES[engine];
  const aspect = rawOpts.aspect || "9:16";

  // Branch A: Custom JSON Spec (--spec <file.json> or inline specObject)
  if (rawOpts.spec || rawOpts.specObject) {
    const specData =
      rawOpts.specObject ||
      JSON.parse(fs.readFileSync(path.resolve(rawOpts.spec), "utf8").replace(/^\uFEFF/, ""));
    if (!Array.isArray(specData.shots) || specData.shots.length === 0) {
      throw new Error(`Custom spec must contain a non-empty shots[] array`);
    }

    const rig = rawOpts.rig || specData.rig || "r6";
    const material = specData.material || "smooth-plastic";
    const isLoop = Boolean(rawOpts.loop || specData.loop);
    const castLocks = Array.isArray(specData.cast) && specData.cast.length > 0
      ? buildCastLocksFromSpec(specData.cast, rig, material)
      : [];
    const castMap = new Map(castLocks.map((c) => [c.id, c]));

    const defaultSubjEn =
      specData.subjectEn ||
      (castLocks.length > 0
        ? castLocks.map((c) => c.shotAnchorEn).join("; ")
        : "an authentic Roblox R6/blocky figure with fingerless solid 1x2x1 block hands");
    const defaultSubjZh =
      specData.subjectZh ||
      (castLocks.length > 0
        ? castLocks.map((c) => c.shotAnchorZh).join("；")
        : "标准Roblox R6/方块小人（无指无爪1x2x1实心平头方柱手）");

    let cursorSec = 0;
    const totalCustomSec = specData.shots.reduce((acc, s) => acc + (Number(s.durationSec) || 0), 0);
    const totalDuration = Number(specData.durationSeconds) || (totalCustomSec > 0 ? totalCustomSec : 15);
    const defaultSlot = totalDuration / specData.shots.length;

    let shot1StartEn = "";
    let shot1StartZh = "";
    const compiledShots = specData.shots.map((s, idx) => {
      const dur = Number(s.durationSec) || defaultSlot;
      const startSec = cursorSec;
      const endSec = idx === specData.shots.length - 1 ? totalDuration : cursorSec + dur;
      cursorSec = endSec;

      const activeCast =
        Array.isArray(s.castIds) && s.castIds.length > 0 && castMap.size > 0
          ? s.castIds.map((id) => castMap.get(id)).filter(Boolean)
          : castLocks;

      const subjEn = activeCast.length > 0 ? activeCast.map((c) => c.shotAnchorEn).join("; ") : defaultSubjEn;
      const subjZh = activeCast.length > 0 ? activeCast.map((c) => c.shotAnchorZh).join("；") : defaultSubjZh;

      const isFinalShot = idx === specData.shots.length - 1;
      const prompts = formatEnginePrompt(
        {
          beatIntent: s.beatIntent || "",
          beatIntentZh: s.beatIntentZh || "",
          audienceRead: s.audienceRead || "",
          audienceReadZh: s.audienceReadZh || "",
          actingAnchor: s.actingAnchor || "",
          performance: s.performance || null,
          interaction: s.interaction || null,
          actionEn: s.actionEn || "performs one crisp rigid blocky motion",
          actionZh: s.actionZh || s.actionEn || "执行单一刚性方块动作",
          faceEn: s.faceEn || "flat 2D Default Smile decal",
          faceZh: s.faceZh || s.faceEn || "纯平2D默认微笑贴图",
          cameraEn: s.cameraEn || "Medium 9:16 framing, steady camera",
          cameraZh: s.cameraZh || s.cameraEn || "竖屏中景稳定机位",
          hailuoTag: s.hailuoTag || "[Static shot]",
          firstFrameEn: s.firstFrameEn,
          firstFrameZh: s.firstFrameZh,
          endFrameEn: s.endFrameEn,
          endFrameZh: s.endFrameZh
        },
        subjEn,
        subjZh,
        specData.environmentEn,
        specData.environmentZh,
        engine,
        aspect,
        rig,
        isLoop && isFinalShot,
        shot1StartEn,
        shot1StartZh
      );
      if (idx === 0) {
        shot1StartEn = prompts.firstFramePromptEn;
        shot1StartZh = prompts.firstFramePromptZh;
      }

      const fmtOld = `${startSec.toFixed(1)}s–${endSec.toFixed(1)}s`;
      const fmtExact = `${startSec.toFixed(2)}s–${endSec.toFixed(2)}s`;

      return {
        shotNumber: idx + 1,
        timeWindow: fmtOld,
        exactTimeWindow: fmtExact,
        editorialDurationSec: Number((endSec - startSec).toFixed(2)),
        nativeGenerateSeconds: engineProfile.nativeClipSeconds,
        editorialTrimWindow: `0.00s–${(endSec - startSec).toFixed(2)}s (from ${engineProfile.nativeClipSeconds.toFixed(1)}s source clip)`,
        role: s.role || `Shot ${idx + 1}`,
        castIds: activeCast.map((c) => c.id),
        beatIntent: s.beatIntent || "",
        beatIntentZh: s.beatIntentZh || "",
        audienceRead: s.audienceRead || "",
        audienceReadZh: s.audienceReadZh || "",
        actingAnchor: s.actingAnchor || "",
        performance: s.performance || null,
        interaction: s.interaction || null,
        actors: s.actors || null,
        props: s.props || null,
        camera: s.camera || null,
        actionZh: s.actionZh || s.actionEn,
        actionEn: s.actionEn,
        faceZh: s.faceZh || s.faceEn,
        faceEn: s.faceEn,
        cameraZh: s.cameraZh || s.cameraEn,
        cameraEn: s.cameraEn,
        chatEn: s.chatEn || "",
        sfx: s.sfx || "Plastic clack",
        caption: s.caption || "",
        ...prompts,
        negativePromptEn: NEGATIVE_GUARD,
        negativePromptZh: NEGATIVE_GUARD_ZH
      };
    });

    const castActingPack =
      Array.isArray(specData.cast) && specData.cast.length > 0
        ? buildCastSpec(
            specData.cast.map((c, idx) => {
              const vis = c.visualDNA && typeof c.visualDNA === "object" ? c.visualDNA : {};
              const themeHint = String(vis.theme3d || c.theme3d || c.theme || "").toLowerCase();
              const rawArch = vis.archetype || c.archetype;
              const resolvedArchetype =
                rawArch && rawArch !== "classic-noob" ? rawArch : THEME3D_TO_ARCHETYPE[themeHint] || rawArch || "classic-noob";
              return { ...c, id: c.id || `actor_${idx + 1}`, archetype: resolvedArchetype };
            }),
            { rig, material }
          )
        : null;

    return {
      template: "custom-spec",
      title: `${specData.titleZh || specData.titleEn || "Custom Episode"} / ${specData.titleEn || specData.titleZh || "Custom Episode"}`,
      engine,
      engineLabel: engineProfile.label,
      nativeClipSeconds: engineProfile.nativeClipSeconds,
      rig,
      material,
      aspect,
      loop: isLoop,
      constraints: specData.constraints || {},
      stageTargets: specData.stageTargets || [],
      cast: castLocks,
      castActingSheetPromptEn: castActingPack ? castActingPack.actingSheetPromptEn : "",
      castActingSheetPromptZh: castActingPack ? castActingPack.actingSheetPromptZh : "",
      durationSeconds: totalDuration,
      shotCount: compiledShots.length,
      workflowMode: engine === "local3d" ? "Direct Local 3D Render (render_preview.mjs --spec)" : "First-Frame I2V (首帧图生视频)",
      shots: compiledShots
    };
  }

  // Branch B: Built-in Template
  if (rawOpts.strict) {
    if (rawOpts.templateExplicit && !TEMPLATES[rawOpts.template]) {
      throw new Error(`Unknown --template "${rawOpts.template}". Valid templates: ${Object.keys(TEMPLATES).join(", ")} (or pass --spec <custom.json>)`);
    }
    if (rawOpts.durationExplicit && ![15, 30, 45].includes(Number(rawOpts.duration))) {
      throw new Error(`Unsupported --duration "${rawOpts.duration}". Valid durations: 15, 30, 45 (or pass custom durations via --spec <custom.json>)`);
    }
  }

  const templateKey = TEMPLATES[rawOpts.template] ? rawOpts.template : "daily-meltdown";
  const tpl = TEMPLATES[templateKey];
  const duration = [15, 30, 45].includes(Number(rawOpts.duration)) ? Number(rawOpts.duration) : 15;
  const rig = rawOpts.rig || tpl.defaultRig;
  const isLoop = Boolean(rawOpts.loop || engine === "seedance");
  const topicNote = rawOpts.topic ? ` (${rawOpts.topic})` : "";

  const targetShotCount = duration === 15 ? 4 : duration === 30 ? 8 : 12;
  const expandedBeats = expandTemplateBeats(tpl.shots, targetShotCount);
  const slotSeconds = duration / targetShotCount;

  let shot1StartEn = "";
  let shot1StartZh = "";
  const compiledShots = [];
  for (let i = 0; i < targetShotCount; i++) {
    const sourceShot = expandedBeats[i];
    const startNum = i * slotSeconds;
    const endNum = i === targetShotCount - 1 ? duration : (i + 1) * slotSeconds;
    const isFinalShot = i === targetShotCount - 1;

    const prompts = formatEnginePrompt(
      sourceShot,
      tpl.subjectEn,
      tpl.subjectZh,
      "",
      "",
      engine,
      aspect,
      rig,
      isLoop && isFinalShot,
      shot1StartEn,
      shot1StartZh
    );
    if (i === 0) {
      shot1StartEn = prompts.firstFramePromptEn;
      shot1StartZh = prompts.firstFramePromptZh;
    }

    compiledShots.push({
      shotNumber: i + 1,
      timeWindow: `${startNum.toFixed(1)}s–${endNum.toFixed(1)}s`,
      exactTimeWindow: `${startNum.toFixed(2)}s–${endNum.toFixed(2)}s`,
      editorialDurationSec: Number((endNum - startNum).toFixed(2)),
      nativeGenerateSeconds: engineProfile.nativeClipSeconds,
      editorialTrimWindow: `0.00s–${(endNum - startNum).toFixed(2)}s (from ${engineProfile.nativeClipSeconds.toFixed(1)}s source clip)`,
      role: sourceShot.role,
      actionZh: sourceShot.actionZh,
      actionEn: sourceShot.actionEn,
      faceZh: sourceShot.faceZh,
      faceEn: sourceShot.faceEn,
      cameraZh: sourceShot.cameraZh,
      cameraEn: sourceShot.cameraEn,
      sfx: sourceShot.sfx,
      caption: sourceShot.caption,
      ...prompts,
      negativePromptEn: NEGATIVE_GUARD,
      negativePromptZh: NEGATIVE_GUARD_ZH
    });
  }

  return {
    template: templateKey,
    title: `${tpl.titleZh} / ${tpl.titleEn}${topicNote}`,
    engine,
    engineLabel: engineProfile.label,
    nativeClipSeconds: engineProfile.nativeClipSeconds,
    rig,
    material: tpl.defaultMaterial,
    aspect,
    loop: isLoop,
    durationSeconds: duration,
    shotCount: compiledShots.length,
    workflowMode: engine === "local3d" ? "Direct Local 3D Render (render_preview.mjs)" : "First-Frame I2V (首帧图生视频)",
    shots: compiledShots
  };
}

export function formatStoryboardMarkdown(plan, rawLang = "en") {
  const lang = normalizeLang(rawLang);
  const useZhText = lang === "zh" || lang === "zh-tw" || lang === "zh-en";
  const showLastFrame = Boolean(plan.loop || plan.engine === "seedance");
  const lines = [];
  lines.push(`# 9:16 Storyboard & Prompt Pack: ${plan.title} (\`lang: ${lang}\`)`);
  lines.push("");
  lines.push(`- **Source**: \`${plan.template}\``);
  lines.push(`- **Target Engine**: \`${plan.engine}\` — ${plan.engineLabel}`);
  lines.push(`- **Rig & Material**: \`${plan.rig}\` · \`${plan.material}\``);
  lines.push(
    `- **Format & Timing**: \`${plan.aspect}\` · \`${plan.durationSeconds}s\` (\`${plan.shotCount}\` unique shots; generate \`${plan.nativeClipSeconds.toFixed(1)}s\` source clips and trim to exact beat windows)`
  );
  if (Array.isArray(plan.cast) && plan.cast.length > 0) {
    lines.push(`- **Locked Cast (${plan.cast.length})**: ${plan.cast.map((c) => `\`${c.id}\` (${c.name} · ${c.rig})`).join(", ")}`);
  }
  lines.push("");
  if (plan.castActingSheetPromptEn) {
    lines.push("## Optional Cast Acting Reference Sheet (Shared-Canvas Exploration)");
    lines.push("");
    lines.push("```text");
    lines.push(useZhText && lang === "zh" ? plan.castActingSheetPromptZh : plan.castActingSheetPromptEn);
    lines.push("```");
    lines.push("");
  }
  lines.push("## Beat Sheet Overview");
  lines.push("");
  lines.push("| Shot | Exact Window | Beat Role | Instant Read & Gaze | Single Action | Camera | SFX & Caption |");
  lines.push("| --- | --- | --- | --- | --- | --- | --- |");

  for (const s of plan.shots) {
    const actionText = useZhText ? s.actionZh : s.actionEn;
    const cameraText = useZhText ? s.cameraZh : s.cameraEn;
    const readText = useZhText
      ? s.audienceReadZh || s.audienceRead || s.beatIntentZh || s.beatIntent || "—"
      : s.audienceRead || s.beatIntent || "—";
    const gazeTag = s.performance?.gazeTarget ? ` (\`gaze -> ${s.performance.gazeTarget}\`)` : "";
    lines.push(
      `| ${String(s.shotNumber).padStart(2, "0")} | ${s.exactTimeWindow} | ${s.role} | ${readText}${gazeTag} | ${actionText} | ${cameraText} | ${s.sfx} · 「${s.caption}」 |`
    );
  }
  lines.push("");
  lines.push("## Compiled Shot Prompts");
  lines.push("");

  for (const s of plan.shots) {
    lines.push(`### Shot ${String(s.shotNumber).padStart(2, "0")} (${s.exactTimeWindow} · ${s.editorialTrimWindow}) · ${s.role}`);
    lines.push("");
    if (s.beatIntent || s.audienceRead || s.performance?.gazeTarget || s.interaction?.propId) {
      const gazeNote = s.performance?.gazeTarget ? ` · Gaze: \`${s.performance.gazeTarget}\`` : "";
      const browNote = s.performance?.eyebrows ? ` · Brows: \`${s.performance.eyebrows}\`` : "";
      const interNote = s.interaction?.propId
        ? ` · Interaction: \`${s.interaction.hand || "right"}:${s.interaction.intent || "hold"} -> ${s.interaction.propId} (${s.interaction.visibility || "camera-facing"})\``
        : "";
      lines.push(
        `- **Acting Grammar**: ${useZhText ? s.audienceReadZh || s.audienceRead || s.beatIntentZh || s.beatIntent : s.audienceRead || s.beatIntent}${gazeNote}${browNote}${interNote}`
      );
    }
    if (lang !== "zh") {
      lines.push(`- **First-Frame Image Prompt (EN)**: \`${s.firstFramePromptEn}\``);
      if (showLastFrame) {
        lines.push(`- **Last-Frame / Loop Anchor (EN)**: \`${s.lastFramePromptEn}\``);
      }
      lines.push(`- **Motion Prompt (${plan.engine} · EN)**: \`${s.i2vPromptEn}\``);
    }
    if (useZhText) {
      lines.push(`- **首帧静帧提示词 (ZH)**: \`${s.firstFramePromptZh}\``);
      if (showLastFrame) {
        lines.push(`- **尾帧/循环锚点提示词 (ZH)**: \`${s.lastFramePromptZh}\``);
      }
      lines.push(`- **动态提示词 (${plan.engine} · ZH)**: \`${s.i2vPromptZh}\``);
    }
    lines.push(`- **Negative Prompt**: \`${lang === "zh" ? s.negativePromptZh : s.negativePromptEn}\``);
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

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("shot_compiler.mjs");
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    process.exit(0);
  }
  try {
    opts.strict = true;
    const plan = compileStoryboard(opts);
    const outText = opts.json ? JSON.stringify(plan, null, 2) : formatStoryboardMarkdown(plan, opts.lang);
    emitOutput(outText, opts.out);
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(1);
  }
}
