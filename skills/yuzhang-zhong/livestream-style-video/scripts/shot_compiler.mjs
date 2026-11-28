#!/usr/bin/env node
/**
 * shot_compiler.mjs
 * Zero-dependency Universal Plot-to-Livestream POV Storyboard & Multi-Engine Prompt Compiler.
 *
 * Supports:
 * 1. Built-in 8 flagship templates (5 General/Cross-Genre AI Video + 3 Roblox Livestream POV)
 * 2. Custom declarative episode specs (`--spec <episode.json>`)
 * 3. Arbitrary freeform story/plot translation (`--plot "<any story>" --style <id> --rig <id> --platform <id>`)
 * 4. Clean-Plate I2V/T2V prompt compilation for `local3d`, `kling`, `seedance`, `hailuo`, `wan`, `sora`, `veo`, `runway`
 * 5. Deterministic Post-HUD event timelines (`douyin`, `kuaishou`, `instagram`, `x`, `tiktok`, `clean`)
 */

import fs from "node:fs";
import path from "node:path";
import {
  RIG_PROFILES,
  STYLE_ADAPTERS,
  LIGHTING_PRESETS,
  buildRigSpec,
  normalizeLang
} from "./rig_spec.mjs";
import { resolvePlatformPreset, buildShotHudTimeline } from "./hud_presets.mjs";

export { normalizeLang };

export const ENGINE_PROFILES = {
  local3d: { nativeClipSeconds: 4.0, label: "Local 3D + Post-HUD Direct Video Engine (render_preview.mjs)" },
  kling: { nativeClipSeconds: 5.0, label: "Kling 2.0 I2V Clean-Plate (5s native -> trim to beat)" },
  seedance: { nativeClipSeconds: 5.0, label: "Seedance / Jimeng First+Last Frame I2V Clean-Plate" },
  hailuo: { nativeClipSeconds: 6.0, label: "Hailuo Director I2V ([Bracketed Camera] + Clean-Plate)" },
  wan: { nativeClipSeconds: 5.0, label: "Wan 2.6 14B I2V/T2V Clean-Plate" },
  sora: { nativeClipSeconds: 5.0, label: "Sora Physical Camera Rig I2V/T2V Clean-Plate" },
  veo: { nativeClipSeconds: 6.0, label: "Veo 3 Native Live-Audio + Clean-Plate Camera Rig" },
  runway: { nativeClipSeconds: 5.0, label: "Runway Gen-4 Camera-Locked I2V Clean-Plate" }
};

export const TEMPLATES = {
  "irl-night-market-selfie": {
    slug: "irl_night_market_selfie",
    category: "general-ai-video",
    titleZh: "夜市超广角自拍杆试吃翻车（通用写实 AI 视频）",
    titleEn: "Night-Market Ultra-Wide Selfie Skewer Fail (Realistic IRL)",
    style: "realistic-irl",
    rig: "handheld-selfie-irl",
    lighting: "night-neon-irl",
    platform: "douyin",
    host: "Lin",
    backdrop: "night_market",
    subjectEn:
      "a photorealistic young street-food streamer in a denim jacket with a clip-on wireless lavalier mic on the collar, extending right arm forward holding an 18mm ultra-wide front-facing smartphone gimbal at arm's length",
    subjectZh:
      "身穿牛仔夹克、领口夹着无线领夹麦的写实年轻美食主播，右臂向前伸出一臂距离持握18mm超广角手机前置云台自拍",
    shots: [
      {
        role: "Hook / 开播暴击点名弹幕",
        durationSec: 3.5,
        actionEn:
          "walks briskly past glowing night-market neon stalls while pointing with the free left hand at a smoking chili-oil skewer stall behind and grinning directly into the 0° held selfie lens",
        actionZh:
          "边走过霓虹闪烁的夜市摊位，边用空出的左手反指身后冒着红油热气的变态辣烤串摊，0°怼脸直视手持前置镜头放狠话",
        eyeLineEn: "direct 0° front-camera eye-contact, brief 8° downward flick checking live comment scroll on phone screen",
        eyeLineZh: "0°直视手机前置镜头互动，顺势向下偏8°扫一眼屏幕弹幕",
        cameraEn: "18mm ultra-wide arm's-length selfie tracking shot with natural walking bob and warm neon stall bokeh",
        cameraZh: "18mm一臂距离超广角自拍跟走机位，带自然步伐起伏与夜市霓虹灯牌散景",
        hailuoTag: "[Pull out, Shake]",
        sfxCue: "chime",
        sfx: "夜市鼎沸人声 + 领夹麦近讲人声 + 进场清脆提示音",
        caption: "弹幕说不敢挑战十倍辣？安排！",
        hudPopup: "join_toast"
      },
      {
        role: "Proof / 微距怼脸对焦实测",
        durationSec: 4.0,
        actionEn:
          "lifts a glistening red-chili skewer within 20cm of the smartphone lens with flat palm held behind it so continuous autofocus snaps sharply onto the sizzling spice crust",
        actionZh:
          "将裹满红油辣椒面的烤串递到距前置镜头20厘米处，左手掌平摊在烤串后方托底触发手机连续微距自动对焦",
        eyeLineEn: "glances between the close-up skewer and 0° lens to confirm autofocus lock",
        eyeLineZh: "视线在近景烤串与手机前置对焦框之间确认清晰度",
        cameraEn: "Arm's-length 18mm selfie frame with shallow macro autofocus pull onto foreground skewer",
        cameraZh: "手持前置超广角机位，焦点快速拉近锁死前景红油烤串（背景主播微虚）",
        hailuoTag: "[Static shot]",
        sfxCue: "boing",
        sfx: "滋滋烤油声 + 手机对焦滴滴声",
        caption: "家人们看这层辣椒籽，零滤镜直出！",
        hudPopup: "commerce_card"
      },
      {
        role: "Twist / 直播翻车瞬间破防",
        durationSec: 4.0,
        actionEn:
          "takes one confident bite of the chili skewer and instantly freezes mid-chew as cheeks flush red and handheld selfie arm trembles with panic",
        actionZh:
          "自信满满咬下一大口辣串，咀嚼半秒后整个人瞬间僵在原地，双颊泛红、持握自拍杆的右臂开始剧烈发抖",
        eyeLineEn: "wide watering eyes locked at 0° into the front lens in silent regret",
        eyeLineZh: "瞳孔地震泛起泪光，0°死死盯住前置摄像头陷入沉默",
        cameraEn: "Close arm's-length selfie framing with involuntary hand-tremor micro-shake",
        cameraZh: "近距前置怼脸构图，伴随主播手抖产生的真实高频微震",
        hailuoTag: "[Push in, Shake]",
        sfxCue: "buzz",
        sfx: "清脆咬合声 + 瞬间安静耳鸣音",
        caption: "等一下……好像不太对劲",
        hudPopup: "gift_combo"
      },
      {
        role: "Payoff / 狂灌冰饮看弹幕刷屏",
        durationSec: 3.5,
        actionEn:
          "tilts the selfie camera slightly upward while gulping an oversized iced lemon tea in desperation, eyes darting rapidly down to read the exploding chat stream",
        actionZh:
          "仰角举高自拍手机疯狂猛灌超大杯冰柠檬茶，眼神高频往下瞟向疯狂刷屏嘲笑的手机弹幕区",
        eyeLineEn: "rapid 8° downward chat-read flicks alternating with defeated 0° stare",
        eyeLineZh: "高频下瞥手机弹幕区后给出彻底服软的0°生无可恋眼神",
        cameraEn: "Slightly high-angle 18mm handheld selfie shot with neon lanterns overhead",
        cameraZh: "微俯拍18mm手持前置机位，头顶夜市灯笼入画收尾",
        hailuoTag: "[Tilt down, Static shot]",
        sfxCue: "win",
        sfx: "吨吨猛喝冰块碰撞声 + 礼物连击清脆叮声",
        caption: "榜一别刷火箭了先帮我叫救护车",
        hudPopup: "gift_combo_peak"
      }
    ]
  },

  "desk-unboxing-autofocus": {
    slug: "desk_unboxing_autofocus",
    category: "general-ai-video",
    titleZh: "桌面带货微距开箱弹飞事故（通用写实 AI 视频）",
    titleEn: "Desk-Clamp Gadget Unboxing Spring Pop Fail (Realistic IRL)",
    style: "realistic-irl",
    rig: "overhead-showcase-rig",
    lighting: "clean-beauty-softbox",
    platform: "kuaishou",
    host: "Kaya",
    backdrop: "unboxing_desk",
    subjectEn:
      "a photorealistic tech livestream host in a crisp oatmeal knit sweater seated behind a clean studio desk with circular LED ring-light catchlights in the eyes and a left-mounted matte-black boom mic",
    subjectZh:
      "身穿燕麦色针织衫的写实数码测评主播坐在整洁直播台后，瞳孔映出清晰圆形环形灯眼神光，画面左下角固定伸入哑光黑悬臂麦",
    shots: [
      {
        role: "Hook / 倒计时开箱钩子",
        durationSec: 3.5,
        actionEn:
          "taps a sealed matte-silver mystery gadget cube on the desk twice and leans toward the 35mm desk-clamp lens with raised eyebrows",
        actionZh:
          "双手在直播台面轻敲两下密封哑光银色机关盲盒，身体向35mm桌面夹持摄像头前倾挑眉互动",
        eyeLineEn: "0° direct lens eye-contact followed by a quick 15° glance to side iPad comment feed",
        eyeLineZh: "0°直视主镜头互动，迅速向右侧15°平板弹幕屏扫一眼",
        cameraEn: "Locked 35mm slightly high-angle desk-clamp livestream camera, crisp f/4 studio clarity",
        cameraZh: "固定35mm微俯角桌面夹持直播机位，f/4通透高显色直播间画质",
        hailuoTag: "[Static shot]",
        sfxCue: "clack",
        sfx: "清脆指节敲盒声 + 直播间上链接提示音",
        caption: "全网断货的解压机关盒，今天直播间实测！",
        hudPopup: "join_toast"
      },
      {
        role: "Proof / 网红手掌托底对焦",
        durationSec: 4.0,
        actionEn:
          "holds the metallic gadget cube 18cm from the camera lens with left palm flat behind it so autofocus locks onto the engraved red release button",
        actionZh:
          "右手将金属机关盒举到距镜头18厘米处，左手五指并拢平摊在盒子后方做网红托底对焦手势，焦点瞬间锁死盒顶红色按钮",
        eyeLineEn: "peeks around the held box into 0° lens to verify focus sharpness",
        eyeLineZh: "从展示盒旁探头直视0°镜头确认微距对焦清晰",
        cameraEn: "Locked 35mm desk-clamp shot with smooth continuous AF-C focus shift from face to foreground cube",
        cameraZh: "固定桌面机位触发平滑连续自动对焦（AF-C由人脸切至前景金属盒）",
        hailuoTag: "[Push in]",
        sfxCue: "chime",
        sfx: "镜头马达轻响 + 金属质感摩挲声",
        caption: "看这做工细节，手掌托底给大家看清楚",
        hudPopup: "commerce_card"
      },
      {
        role: "Twist / 弹簧机关意外炸开",
        durationSec: 4.0,
        actionEn:
          "presses the red button on the desk and a harmless colorful foam mascot pops upward out of the cube, bumping the boom mic foam and startling the host backward into the chair",
        actionZh:
          "放回桌面按下红钮瞬间，盒内彩色海绵玩偶猛地弹簧弹出擦碰悬臂麦防喷棉，吓得主播整个人往后仰倒在电竞椅背上",
        eyeLineEn: "wide startled eyes tracking the upward pop before snapping 0° to webcam",
        eyeLineZh: "惊恐瞪眼追随弹起玩偶，随即猛看向0°摄像头确认刚刚全播出去",
        cameraEn: "Locked desk-clamp camera with authentic brief desk-vibration micro-shake on pop",
        cameraZh: "固定桌面支架机位，伴随桌面弹开瞬间的真实支架高频微震",
        hailuoTag: "[Shake, Static shot]",
        sfxCue: "boing",
        sfx: "弹簧嘭声 + 麦克风防喷棉轻擦低频声",
        caption: "卧槽！！厂家没说弹力这么猛啊！！",
        hudPopup: "gift_combo"
      },
      {
        role: "Payoff / 憋笑指副屏弹幕",
        durationSec: 3.5,
        actionEn:
          "catches the fallen foam mascot on the desk, bursts out laughing while pointing right hand toward the off-axis chat monitor",
        actionZh:
          "一把按住落回桌面的海绵玩偶，破功憋不住大笑并用右手指着侧方15°弹幕副屏跟观众互怼",
        eyeLineEn: "switches between 15° chat-monitor laugh and 0° direct webcam grin",
        eyeLineZh: "在15°盯弹幕爆笑与0°回看主镜头之间自然切换",
        cameraEn: "Locked 35mm studio desk framing matching Shot 1 for clean loop",
        cameraZh: "固定35mm直播台构图完美回扣第一镜",
        hailuoTag: "[Static shot]",
        sfxCue: "win",
        sfx: "真实憋笑声 + 键盘敲击截屏声",
        caption: "谁在刷『主播工伤』出来挨打！",
        hudPopup: "gift_combo_peak"
      }
    ]
  },

  "midnight-corridor-fpv-live": {
    slug: "midnight_corridor_fpv_live",
    category: "general-ai-video",
    titleZh: "深夜旧楼第一人称双持探险直播（悬疑剧情转直播）",
    titleEn: "Midnight Corridor First-Person Flashlight & Chat-Phone Live",
    style: "realistic-irl",
    rig: "chest-head-pov",
    lighting: "flashlight-dim-exploration",
    platform: "instagram",
    host: "ren.urban",
    backdrop: "dim_corridor",
    subjectEn:
      "first-person 16mm chest/head-mounted live action-camera perspective of an urban explorer; left hand visible in lower-left holding a glowing smartphone displaying dark-mode chat light, right hand sweeping a tactical LED flashlight",
    subjectZh:
      "佩戴16mm超广角胸挂/头戴直播相机的第一人称视角；画面左下伸出左手举着泛冷蓝微光的副机看弹幕，右下伸出右手持战术强光手电筒扫射",
    shots: [
      {
        role: "Hook / 第一视角双持开场",
        durationSec: 3.5,
        actionEn:
          "takes two slow cautious footsteps down a peeling-paint vintage hallway while tilting the left-hand chat phone briefly toward the chest lens and sweeping the right-hand flashlight onto Room 404's brass plate",
        actionZh:
          "在墙皮斑驳的复古走廊缓慢迈出两步，左手微倾副机屏幕确认直播信号正常，右手强光手电筒精准打在尽头404铜牌木门上",
        eyeLineEn: "first-person POV tilts slightly toward left-hand phone glow then locks onto the door ahead",
        eyeLineZh: "第一人称镜头微低瞥一眼左手副机亮光，随即抬起锁死前方木门",
        cameraEn: "16mm ultra-wide first-person chest-cam POV with authentic breathing sway and crisp f/5.6 depth",
        cameraZh: "16mm超广角第一人称运动直播机位，带真实呼吸起伏与脚步微震",
        hailuoTag: "[Push in]",
        sfxCue: "chime",
        sfx: "空旷走廊脚步回声 + 呼吸收音 + 弹幕提示轻响",
        caption: "Chat told me to check the 4th floor... nobody's here right?",
        hudPopup: "join_toast"
      },
      {
        role: "Proof / 停步回应弹幕质疑",
        durationSec: 4.0,
        actionEn:
          "pauses outside the wooden door and waves the right hand openly through the flashlight beam in front of the lens to prove there are no hidden wires",
        actionZh:
          "停在木门两米外，伸出右手在镜头前穿过手电筒光束晃动示意，向直播间证明现场绝无剧本机关",
        eyeLineEn: "visible right hand gestures directly in front of the 16mm POV lens",
        eyeLineZh: "右手直接在16mm第一视角镜头前比划互动",
        cameraEn: "16mm first-person POV stationary with subtle heartbeat micro-sway",
        cameraZh: "16mm第一视角驻足构图，保留细微手持呼吸感",
        hailuoTag: "[Static shot]",
        sfxCue: "clack",
        sfx: "衣物摩擦声 + 压低声音耳语收音",
        caption: "See? Zero strings, door is bolted from outside.",
        hudPopup: "qa_pinned"
      },
      {
        role: "Twist / 门缝自开与壁灯闪烁",
        durationSec: 4.0,
        actionEn:
          "the overhead corridor bulb flickers twice and the heavy wooden door creaks open 15 centimeters by itself while the right-hand flashlight beam trembles violently",
        actionZh:
          "头顶走廊廊灯突然闪烁两下，沉重木门无风自动吱呀推开15厘米黑缝，画面右下右手持握的手电筒光斑剧烈颤抖",
        eyeLineEn: "POV freezes dead on the widening dark door gap as left hand clutches phone tighter",
        eyeLineZh: "第一视角死死定格在缓缓张开的门缝黑影，左手猛地攥紧副机",
        cameraEn: "16mm first-person POV stepping half a pace backward with startled jolt",
        cameraZh: "16mm第一视角倒退半步产生急促惊吓顿挫感",
        hailuoTag: "[Pull out, Shake]",
        sfxCue: "buzz",
        sfx: "电流滋啦闪灯声 + 老旧门轴刺耳吱呀声",
        caption: "WAIT DID YOU GUYS HEAR THAT?!",
        hudPopup: "gift_combo"
      },
      {
        role: "Payoff / 掉头狂奔手电乱晃",
        durationSec: 3.5,
        actionEn:
          "whips 180 degrees around toward the stairwell exit in one urgent pivot as both hands pump into the lower frame sprinting out",
        actionZh:
          "第一视角猛地180度急转身朝安全出口楼梯间冲刺，双手交替甩入画面下沿伴随手电筒光束上下剧烈扫动",
        eyeLineEn: "urgent POV whip-pan locking onto bright exit sign ahead",
        eyeLineZh: "急促甩镜锁定前方绿色安全出口亮光",
        cameraEn: "16mm action-cam sprint POV with authentic running bob",
        cameraZh: "16mm运动相机冲刺第一视角，真实跑步颠簸收尾",
        hailuoTag: "[Pan right, Shake]",
        sfxCue: "siren",
        sfx: "急促冲刺脚步声 + 麦克风风噪破音",
        caption: "NOPE STREAM OVER WE ARE LEAVING!!",
        hudPopup: "gift_combo_peak"
      }
    ]
  },

  "late-night-study-webcam": {
    slug: "late_night_study_webcam",
    category: "general-ai-video",
    titleZh: "深夜赶工固定摄像头橘猫踩键盘（陪伴慢直播反转）",
    titleEn: "Late-Night Desk Webcam Study Stream Tabby Cat Chaos",
    style: "realistic-irl",
    rig: "desktop-webcam",
    lighting: "warm-desk-lamp",
    platform: "x",
    host: "dev_mika",
    backdrop: "study_room",
    subjectEn:
      "a photorealistic creator in oversized glasses and a charcoal hoodie seated at a warm-lit study desk with a glowing mechanical keyboard, left boom mic, and cyan LED shelf rim light behind",
    subjectZh:
      "戴大框眼镜穿深灰连帽卫衣的写实创作者坐在暖光书桌前，面前摆着背光机械键盘与左置悬臂麦，背后书架透出青色氛围灯带",
    shots: [
      {
        role: "Hook / 深夜陪伴读弹幕打卡",
        durationSec: 3.5,
        actionEn:
          "types steadily on the glowing mechanical keyboard, then flicks eyes 15° right to read a viewer message and gives a quiet encouraging thumbs-up to the 0° monitor-top webcam",
        actionZh:
          "双手在背光机械键盘上专注敲字，视线向右侧15°副屏扫过一条弹幕后，对着显示器上方0°摄像头安静比出大拇指回应",
        eyeLineEn: "clean 15° chat-monitor read shifting to warm 0° webcam eye-contact",
        eyeLineZh: "标准15°偏轴读弹幕后切回0°主摄像头对视点头",
        cameraEn: "Locked 24mm monitor-top webcam at 6° downward tilt, deep room focus",
        cameraZh: "锁死在显示器顶端的24mm广角摄像头（6°微俯拍，背景书架清晰）",
        hailuoTag: "[Static shot]",
        sfxCue: "clack",
        sfx: "清脆机械键盘麻将音 + 深夜安静底噪",
        caption: "2:00 AM co-working stream — finishing the final slide deck",
        hudPopup: "join_toast"
      },
      {
        role: "Proof / 举马克杯镜头前叹气",
        durationSec: 4.0,
        actionEn:
          "raises a ceramic coffee mug toward the webcam in a sleepy toast while behind the chair a ginger tabby cat's ears quietly pop above the desk edge",
        actionZh:
          "略显困倦地举起陶瓷咖啡杯朝摄像头隔空碰杯，而书桌右后方一对橘猫耳朵悄无声息探出桌沿",
        eyeLineEn: "host looks 0° at webcam, completely unaware of the cat ears behind; chat notices first",
        eyeLineZh: "主播0°直视镜头喝咖啡浑然不觉，戏剧反差让弹幕率先发现猫耳朵",
        cameraEn: "Identical locked 24mm monitor-top webcam frame",
        cameraZh: "保持完全一致的24mm固定显示器机位",
        hailuoTag: "[Static shot]",
        sfxCue: "chime",
        sfx: "轻放瓷杯声 + 细微猫咪呼噜声",
        caption: "One last cup of coffee and we deploy...",
        hudPopup: "join_toast"
      },
      {
        role: "Twist / 橘猫飞扑一脚踩发送",
        durationSec: 4.0,
        actionEn:
          "the plump ginger tabby cat leaps squarely onto the glowing mechanical keyboard, scattering sticky notes and pressing Enter with both front paws",
        actionZh:
          "圆润橘猫猛地一跃精准降落在背光机械键盘正中央，震飞两张便利贴并两只猫爪结结实实踩下回车键",
        eyeLineEn: "host's glasses reflect bright screen flash as eyes widen at the keyboard",
        eyeLineZh: "镜片映出屏幕弹窗白光，主播瞳孔瞬间放大低头盯向猫爪",
        cameraEn: "Locked monitor-top webcam shaking briefly from the cat landing on the desk",
        cameraZh: "显示器摄像头因橘猫砸中桌面产生真实上下微震",
        hailuoTag: "[Shake, Static shot]",
        sfxCue: "drop",
        sfx: "猫咪落地闷响 + 键盘乱按连响 + 系统发送提示音",
        caption: "NO WAIT THAT WAS THE PRODUCTION BRANCH—",
        hudPopup: "gift_combo"
      },
      {
        role: "Payoff / 人猫同步盯摄像头社死",
        durationSec: 3.5,
        actionEn:
          "both the frozen creator with hands on head and the sitting ginger cat slowly look straight up into the 0° monitor-top webcam together",
        actionZh:
          "双手抱头石化的主播与端坐在键盘上的橘猫同步缓慢抬头，一齐0°死死盯住显示器顶端的直播摄像头",
        eyeLineEn: "synchronized 0° direct lens stare from both human host and tabby cat",
        eyeLineZh: "一人一猫双双0°直视主摄像头定格",
        cameraEn: "Locked 24mm monitor-top webcam frame",
        cameraZh: "24mm固定桌面摄像头定格收尾",
        hailuoTag: "[Static shot]",
        sfxCue: "win",
        sfx: "无辜猫叫一声 (Meow~) + 满屏飘心音效",
        caption: "Chat... please tell me nobody clipped that.",
        hudPopup: "gift_combo_peak"
      }
    ]
  },

  "wuxia-sword-flight-live": {
    slug: "wuxia_sword_flight_live",
    category: "general-ai-video",
    titleZh: "仙侠御剑飞行早高峰户外直播（任意架空剧情转直播）",
    titleEn: "Wuxia Flying-Sword Cloud Commute Selfie Live (Genre Plot -> Live POV)",
    style: "cinematic-genre-adapt",
    rig: "handheld-selfie-irl",
    lighting: "daylight-outdoor-autoexp",
    platform: "douyin",
    host: "青云小师兄",
    backdrop: "cloud_sea",
    subjectEn:
      "a windswept young wuxia swordsman in flowing azure-and-white robes standing atop a hovering jade-bronze flying sword high above a golden sea of clouds, extending right arm to hold a glowing jade-tablet selfie cam at 18mm ultra-wide angle",
    subjectZh:
      "身穿青白流云道袍的年轻剑修脚踏悬浮青铜古剑穿梭于金色云海之上，右臂伸直一臂距离举着发光玉简自拍法器呈18mm超广角直拍",
    shots: [
      {
        role: "Hook / 云海早高峰开播吐槽",
        durationSec: 3.5,
        actionEn:
          "holds robe hair ribbon against strong high-altitude wind while shouting cheerfully into the 0° held jade selfie lens as sunlit mountain peaks whip past below",
        actionZh:
          "左手按住被高空罡风吹乱的发带，对着一臂外0°玉简前置镜头大声喊话吐槽御剑早高峰，脚下金顶群峰飞速掠过",
        eyeLineEn: "0° direct lens grin with windswept hair across forehead",
        eyeLineZh: "迎风眯眼0°直视手持自拍法器镜头",
        cameraEn: "18mm ultra-wide arm's-length selfie POV tilted slightly down to show cloud sea",
        cameraZh: "18mm超广角一臂自拍微俯视角，完整带入脚下翻涌云海",
        hailuoTag: "[Pull out, Shake]",
        sfxCue: "chime",
        sfx: "高空呼啸风噪收音 + 剑鸣嗡音 + 开播叮声",
        caption: "御剑直播间家人们早！今天三环剑道又堵了！",
        hudPopup: "join_toast"
      },
      {
        role: "Proof / 下摇镜头展示脚下飞剑",
        durationSec: 4.0,
        actionEn:
          "tilts the held selfie cam downward to show embroidered boots balanced on the glowing rune-carved flying sword blade skimming a rainbow cloud bank",
        actionZh:
          "手腕下压将自拍镜头摇向脚底，怼近展示靴底稳稳踩着的符文发光飞剑剑身正贴着彩虹云层掠过",
        eyeLineEn: "camera tilts down from face to boots and sword runes, then tilts back up to 0° wink",
        eyeLineZh: "镜头由脸部实拍下摇至脚底剑身再摇回0°眨眼自证",
        cameraEn: "Continuous handheld 18mm selfie tilt-down and recovery with sunlit lens auto-exposure",
        cameraZh: "手持前置一臂机位俯仰实拍，穿过云层阳光产生真实自动曝光收缩",
        hailuoTag: "[Tilt down]",
        sfxCue: "boing",
        sfx: "清越破空剑气声 + 衣袂猎猎风声",
        caption: "新换的二阶青霜剑，百公里仅耗两块灵石！",
        hudPopup: "commerce_card"
      },
      {
        role: "Twist / 仙鹤超车抢镜惊险颠簸",
        durationSec: 4.0,
        actionEn:
          "a giant white spirit crane swoops right behind the swordsman's shoulder photobombing the selfie frame and buffeting the flying sword with a gust that makes the host wobble",
        actionZh:
          "一只巨大白羽仙鹤突然从剑修右肩后方贴脸超车闯入自拍画面，翅膀卷起的气流震得脚下飞剑左右摇晃、主播险些站不稳",
        eyeLineEn: "glances at selfie screen spotting the crane behind, then whips head back in shock",
        eyeLineZh: "从自拍屏幕里瞥见身后仙鹤贴脸，猛扭头惊呼稳住身形",
        cameraEn: "18mm handheld selfie frame jolting 12° with turbulence roll",
        cameraZh: "18mm手持前置画面随气流颠簸产生12°真实倾斜晃动",
        hailuoTag: "[Shake, Pan left]",
        sfxCue: "siren",
        sfx: "清亮鹤唳声 + 翅膀扑扇强风声",
        caption: "卧槽哪门派的仙鹤？！变道不打转向符啊！",
        hudPopup: "gift_combo"
      },
      {
        role: "Payoff / 发髻吹歪看弹幕破防",
        durationSec: 3.5,
        actionEn:
          "regains balance on the hovering sword with crooked hair-bun and stares deadpan into the 0° selfie lens while smoothing messy bangs",
        actionZh:
          "重新稳住悬停飞剑但头顶道冠已被吹歪，一边用左手扒拉凌乱刘海一边生无可恋0°盯住自拍屏幕满屏哈哈弹幕",
        eyeLineEn: "8° downward read of laughing danmaku then deadpan 0° lens stare",
        eyeLineZh: "低头扫一眼满屏嘲笑弹幕，抬眼0°死鱼眼凝视镜头",
        cameraEn: "Stabilized arm's-length 18mm cloud-sea selfie shot",
        cameraZh: "恢复平稳的云海一臂超广角自拍构图",
        hailuoTag: "[Static shot]",
        sfxCue: "win",
        sfx: "乌鸦飞过音效 + 满屏礼物连击叮声",
        caption: "扣『剑修科目三』的道友踢出直播间了啊！",
        hudPopup: "gift_combo_peak"
      }
    ]
  },

  "roblox-obby-rage-pip": {
    slug: "roblox_obby_rage_pip",
    category: "roblox-livestream",
    titleZh: "Roblox 天空跑酷实况 + 右上主播小窗破防拍桌（双轨 PiP 样本）",
    titleEn: "Roblox Sky-Obby Speedrun + PiP Streamer Desk-Slam Rage",
    style: "roblox-blocky",
    rig: "pip-facecam-rig",
    lighting: "ring-rgb-studio",
    platform: "tiktok",
    host: "BloxyKai",
    backdrop: "obby_sky",
    subjectEn:
      "dual-track Roblox SmoothPlastic livestream: Track A shows an R6 blocky obby runner (2x2x1 torso, flush 1x2x1 legs, fingerless solid block hands, 1:1 barrel head) leaping across neon sky pads; Track B PiP corner shows a chibi-blocky streamer wearing cat-ear RGB headset and boom mic in a neon bedroom",
    subjectZh:
      "双轨合成Roblox SmoothPlastic实况直播：A轨主画面为标准R6方块跑酷小人（2x2x1躯干、并拢1x2x1方腿、无手指无乐高爪实心方手、1:1桶状头）跨越天空霓虹跳台；B轨右上画中画小窗为戴猫耳RGB耳机与悬臂麦的方块主播反应特写",
    shots: [
      {
        role: "Hook / 终点前立Flag挑衅弹幕",
        durationSec: 3.5,
        actionEn:
          "the R6 obby avatar stands poised on a floating pink SmoothPlastic sky pad as the PiP headset streamer grins smugly into the 0° facecam raising one solid 1x2x1 block hand",
        actionZh:
          "A轨跑酷方块小人在粉色高空平台上蓄势待发，B轨小窗方块主播对着0°摄像头露出挑眉坏笑贴图并高举1x2x1实心平头方手立Flag",
        facecamPromptEn:
          "Locked 28mm RGB bedroom webcam close-up: Roblox chibi-blocky streamer in cat-ear headset with Check-It smirk 2D decal raises solid 1x2x1 fingerless block hand confidently toward 0° lens",
        facecamPromptZh:
          "28mm固定RGB电竞房摄像头特写：戴猫耳耳机的Roblox方块主播呈现挑眉坏笑2D贴图，朝0°镜头自信举起1x2x1无手指实心方手",
        eyeLineEn: "PiP streamer locks 0° smug eye-contact with webcam before glancing at game monitor",
        eyeLineZh: "小窗主播先0°自信怼脸看镜头，再转回紧盯游戏屏幕",
        cameraEn: "Dual-track composited: Track A high-angle 3/4 sky obby follow; Track B locked 28mm corner webcam",
        cameraZh: "A/B双轨独立生成合成：A轨高空跑酷斜俯跟拍；B轨右上圆角固定电竞房反应窗",
        hailuoTag: "[Push in]",
        chatEn: "WORLD RECORD!",
        sfxCue: "chime",
        sfx: "清脆键盘敲击声 + 跑酷准备提示音",
        caption: "Watch chat — zero-death Stage 99 speedrun!",
        hudPopup: "join_toast",
        actors: [
          { castId: "runner", fromPos: [-0.45, 0.0, 0], toPos: [-0.25, 0.0, 0], yaw: 0.45, pose: "wave", expression: "smirk", theme: "obby", backProp: "jetpack" }
        ]
      },
      {
        role: "Proof / 连跳加速冲刺终点",
        durationSec: 4.0,
        actionEn:
          "the R6 runner performs a crisp Motor6D leap across the sky gap toward the glowing emerald finish pad while the PiP streamer leans close to the glowing monitor",
        actionZh:
          "A轨R6小人迈开刚性Motor6D方腿干脆跃过云端深渊冲向翠绿终点台，B轨小窗主播身体前倾紧贴显示器蓝光屏住呼吸",
        facecamPromptEn:
          "Locked 28mm RGB webcam: Roblox blocky streamer leans forward toward cool monitor glow, flat 2D decal showing intense focused eyes and a painted blue sweat drop",
        facecamPromptZh:
          "28mm固定摄像头：Roblox方块主播前倾贴近屏幕冷光，纯平2D贴图呈现专注眼神与一滴蓝色印刷汗珠",
        eyeLineEn: "focused forward screen gaze with blue monitor reflection on smooth 1:1 barrel head",
        eyeLineZh: "专注紧盯主屏幕，平滑1:1桶状头映出显示器蓝光",
        cameraEn: "Dual-track composited: Track A dynamic side-tracking jump arc; Track B locked corner facecam",
        cameraZh: "双轨合成：A轨侧面平移捕捉跳跃抛物线；B轨锁死反应小窗",
        hailuoTag: "[Pan right]",
        chatEn: "SO CLOSE!!",
        sfxCue: "boing",
        sfx: "经典Roblox弹簧跳跃音 + 极速敲空格键声",
        caption: "One last jump to the checkpoint!!",
        hudPopup: "commerce_card",
        actors: [
          { castId: "runner", fromPos: [-0.38, 0.05, 0], toPos: [0.28, 0.34, 0], yaw: 0.48, pose: "jump", expression: "grin", theme: "obby", backProp: "jetpack" }
        ]
      },
      {
        role: "Twist / 脚尖擦碰红砖瞬间归零",
        durationSec: 4.0,
        actionEn:
          "the R6 runner's flush 1x2x1 blocky foot clips the glowing neon-red Killbrick strip right in front of the flag, triggering an instant rigid plank tumble",
        actionZh:
          "就在距离终点旗半步处，A轨小人并拢的1x2x1方腿脚尖擦碰到发光红砖(Killbrick)，全身瞬间保持刚体直挺挺侧翻坠落",
        facecamPromptEn:
          "Locked 28mm RGB webcam with impact shake: Roblox blocky streamer switches to wide hollow shocked ring eyes (O_O) 2D decal as red screen flash illuminates the desk",
        facecamPromptZh:
          "28mm固定摄像头微震：屏幕红光映亮桌面，小窗方块主播2D贴图瞬间切换为空心白圈震惊眼(O_O)",
        eyeLineEn: "PiP streamer freezes in 0_0 disbelief then snaps head 15° toward exploding chat",
        eyeLineZh: "小窗主播O_O石化后猛转15°看向刷满问号的弹幕屏",
        cameraEn: "Dual-track composited: Track A close impact shot with red highlight flash; Track B startled recoil",
        cameraZh: "双轨合成：A轨红砖碰撞微震特写；B轨主播后仰震惊",
        hailuoTag: "[Shake, Static shot]",
        chatEn: "NOOOO!!",
        sfxCue: "buzz",
        sfx: "经典Oof闷响 + 失败蜂鸣音",
        caption: "BRO MY TOE BARELY TOUCHED THE RED BRICK?!",
        hudPopup: "gift_combo",
        actors: [
          { castId: "runner", fromPos: [0.18, 0.0, 0], toPos: [0.32, -0.35, 0], yaw: 0.35, pose: "plank_fall", expression: "shocked", theme: "obby", backProp: "jetpack" }
        ]
      },
      {
        role: "Payoff / 双手刚性拍桌瀑布泪收尾",
        durationSec: 3.5,
        actionEn:
          "while the R6 avatar respawns stiffly back at Stage 1, the PiP blocky streamer pivots both solid 1x2x1 rectangular arms down to slam the desk with streaming 2D waterfall tears",
        actionZh:
          "A轨小人刚性复活回第1关起点，B轨小窗方块主播双侧1x2x1实心方臂沿肩轴猛拍书桌，脸部浮现蓝色2D瀑布流泪贴图",
        facecamPromptEn:
          "Locked 28mm RGB webcam shaking from desk slam: Roblox blocky streamer slams both fingerless solid 1x2x1 block hands flat on the desk, 2D decal streaming blue waterfall tear strips and X_X dizzy eyes",
        facecamPromptZh:
          "28mm摄像头随拍桌剧烈微震：方块主播双侧无手指1x2x1实心方手平拍桌面，2D贴图挂满蓝色瀑布宽条眼泪",
        eyeLineEn: "0° direct webcam meltdown stare while chat spams Stage 1 jokes",
        eyeLineZh: "0°对着摄像头彻底破防流泪",
        cameraEn: "Dual-track composited: Track A wide Stage 1 reset; Track B desk-slam shake close-up",
        cameraZh: "双轨合成：A轨回到起点构成循环；B轨拍桌破防收尾",
        hailuoTag: "[Shake, Pull out]",
        chatEn: "STAGE 1...",
        sfxCue: "clack",
        sfx: "清脆塑料拍桌声 + 满屏礼物飘屏叮声",
        caption: "Back to Stage 1... goodnight chat 💀",
        hudPopup: "gift_combo_peak",
        actors: [
          { castId: "runner", fromPos: [-0.45, 0.0, 0], toPos: [-0.45, 0.0, 0], yaw: 0.0, pose: "faceplant", expression: "tears", theme: "obby", backProp: "jetpack" }
        ]
      }
    ]
  },

  "roblox-doors-irl-selfie": {
    slug: "roblox_doors_irl_selfie",
    category: "roblox-livestream",
    titleZh: "Roblox 惊悚走廊自拍杆直拍 · 身后白眼突脸（Roblox IRL 样本）",
    titleEn: "Roblox DOORS Corridor Handheld Selfie-Stick Live Scare",
    style: "roblox-blocky",
    rig: "handheld-selfie-irl",
    lighting: "flashlight-dim-exploration",
    platform: "instagram",
    host: "momo_rblx",
    backdrop: "hotel_corridor",
    subjectEn:
      "an authentic Roblox SmoothPlastic R6/chibi-blocky streamer in a sky-blue hoodie (2x2x1 torso, flush 1x2x1 legs, fingerless and clawless solid 1x2x1 block hands, smooth studless 1:1 barrel head, flat 2D decal face) holding a blocky selfie-stick smartphone forward in its right block hand",
    subjectZh:
      "穿天蓝连帽卫衣的纯正Roblox SmoothPlastic方块小人主播（2x2x1躯干、并拢1x2x1方腿、无手指无乐高爪1x2x1实心平头方手、1:1平滑桶状头、2D平面五官），右侧实心方手刚性贴合举着方块自拍杆手机前置直拍",
    shots: [
      {
        role: "Hook / 050号门前压低声音开播",
        durationSec: 3.5,
        actionEn:
          "walks cautiously on smooth dark-wood hotel planks holding the selfie stick forward while pointing its left solid 1x2x1 block hand back at brass-plaqued Door 050",
        actionZh:
          "踩在平滑无凸粒的深色酒店木地板上举着自拍杆慢走，左侧1x2x1实心方手反指身后的050号黄铜牌木门向观众小声解说",
        eyeLineEn: "0° direct stare into the held blocky selfie phone with nervous 2D sweat-drop decal",
        eyeLineZh: "带着2D蓝色汗珠贴图0°紧盯手持自拍手机镜头",
        cameraEn: "18mm ultra-wide arm's-length blocky selfie-stick perspective down the dim hotel corridor",
        cameraZh: "18mm超广角方块自拍杆一臂前置视角，纵深带入幽暗酒店走廊",
        hailuoTag: "[Pull out]",
        chatEn: "DOOR 050...",
        sfxCue: "chime",
        sfx: "木地板塑料踏步声 + 低沉走廊环境音",
        caption: "Chat dared me to stream Door 050 solo... totally fine!",
        hudPopup: "join_toast",
        actors: [
          { castId: "momo", fromPos: [0.0, 0, 0.25], toPos: [0.05, 0, 0.35], yaw: 0.15, pose: "walk", expression: "smirk", theme: "commuter", handPropL: "flashlight" }
        ]
      },
      {
        role: "Proof / 壁灯骤闪盯着弹幕发愣",
        durationSec: 4.0,
        actionEn:
          "stops mid-corridor as the warm brass wall sconces flicker twice; the blocky avatar tilts its 1:1 head down 8° reading frantic chat warnings on its phone screen",
        actionZh:
          "走到走廊中央时两侧黄铜壁灯突然明灭闪烁两下，方块小人微低1:1桶状脑袋阅读手机屏幕上疯狂刷出的『快躲柜子』弹幕",
        eyeLineEn: "8° downward read of glowing phone screen before snapping back to 0° lens",
        eyeLineZh: "低头8°读手机弹幕亮光，随后疑惑抬眼看向0°前置镜头",
        cameraEn: "Handheld selfie-stick close medium shot with flickering warm-to-red corridor wall light",
        cameraZh: "手持自拍杆中近景，走廊壁灯呈现暖黄转暗红闪烁光效",
        hailuoTag: "[Static shot]",
        chatEn: "WHY HIDE??",
        sfxCue: "buzz",
        sfx: "灯泡电流滋啦闪烁声 + 密集弹幕弹出音",
        caption: "Wait why is everyone spamming HIDE right now??",
        hudPopup: "qa_pinned",
        actors: [
          { castId: "momo", fromPos: [0.05, 0, 0.35], toPos: [0.05, 0, 0.35], yaw: 0.0, pose: "idle", expression: "deadpan", theme: "commuter", handPropL: "flashlight" }
        ]
      },
      {
        role: "Twist / 前置镜头拍到身后白眼",
        durationSec: 4.0,
        actionEn:
          "in the wide selfie background directly over the avatar's left shoulder, a pair of glowing white blocky eyes materializes in the dark hallway; the avatar spots it in the selfie preview and switches to O_O ring eyes",
        actionZh:
          "超广角自拍画面左肩正后方的黑暗走廊里悄然亮起一对发光白色方块眼；小人从自拍预览屏里看清身后异状，2D贴图瞬间变成空心白圈震惊眼(O_O)",
        eyeLineEn: "spots monster via the 0° front-camera screen reflection before rigidly rotating head",
        eyeLineZh: "直接通过前置自拍屏看清身后白眼，无需先转头即完成恐怖直播高潮",
        cameraEn: "18mm selfie-stick over-shoulder depth revealing dark figure behind host with sudden jolt shake",
        cameraZh: "18mm超广角自拍前置纵深构图，清晰拍到主播肩膀后方发光白眼并伴随手抖震动",
        hailuoTag: "[Push in, Shake]",
        chatEn: "BEHIND YOU!!",
        sfxCue: "siren",
        sfx: "低频恐怖重低音骤响 + 塑料关节急抖声",
        caption: "IT'S IN THE SELFIE CAM!! IT'S RIGHT BEHIND ME!!",
        hudPopup: "gift_combo",
        actors: [
          { castId: "momo", fromPos: [0.05, 0, 0.38], toPos: [0.08, 0.06, 0.42], yaw: -0.1, pose: "recoil", expression: "shocked", theme: "commuter", handPropL: "flashlight" },
          { castId: "shadow", fromPos: [-0.38, 0.08, -0.55], toPos: [-0.28, 0.08, -0.35], yaw: 0.2, pose: "idle", expression: "shocked", theme: "guest" }
        ]
      },
      {
        role: "Payoff / 刚性冲进木衣柜留缝直拍",
        durationSec: 3.5,
        actionEn:
          "sprints two rigid Motor6D strides into the slatted wooden wardrobe and pulls the doors shut, peering out through the narrow wooden slats with the selfie light illuminating streaming 2D tears",
        actionZh:
          "迈开两步干脆刚性的Motor6D方腿冲进百叶木衣柜猛地关门，仅剩手机自拍冷光在柜内照亮满脸2D瀑布流泪贴图",
        eyeLineEn: "whispering 0° extreme close-up inside dark closet lit only by phone screen",
        eyeLineZh: "衣柜内仅靠手机屏幕冷光照明的0°贴脸耳语特写",
        cameraEn: "Extreme close-up selfie cam inside slatted closet with rhythmic red light passing outside",
        cameraZh: "百叶木柜内贴脸前置大特写，柜门缝隙外掠过暗红光影",
        hailuoTag: "[Shake, Static shot]",
        chatEn: "SAFE...?",
        sfxCue: "clack",
        sfx: "木柜门砰然合拢声 + 压抑呼吸声",
        caption: "Nobody breathe... chat stop sending loud gifts!!",
        hudPopup: "gift_combo_peak",
        actors: [
          { castId: "momo", fromPos: [0.0, 0, 0.45], toPos: [0.0, 0, 0.48], yaw: 0.0, pose: "idle", expression: "tears", theme: "commuter" }
        ]
      }
    ]
  },

  "roblox-pet-hatch-pk": {
    slug: "roblox_pet_hatch_pk",
    category: "roblox-livestream",
    titleZh: "Roblox 双人连麦 PK 抽蛋开箱 · 氪金潮人 vs 黄皮新手出金（50/50 分屏样本）",
    titleEn: "Roblox Dual-Host PK Split-Screen Mystery Egg Hatch (Pro vs Noob)",
    style: "roblox-blocky",
    rig: "pk-cohost-split",
    lighting: "ring-rgb-studio",
    platform: "kuaishou",
    host: "Y2K_Queen",
    cohost: "ClassicNoob",
    backdrop: "adoption_plaza",
    subjectEn:
      "50/50 vertical co-host PK split-screen Roblox SmoothPlastic livestream: Left room shows a glossy Y2K streetwear blocky streamer in pink neon studio; Right room shows an untextured yellow-head blue-torso Classic R6 Noob in a plain starter room—both with solid fingerless 1x2x1 block hands and 2D face decals",
    subjectZh:
      "左右对称50/50双人连麦PK分屏Roblox直播：左屏粉色霓虹直播间为戴星形墨镜的Y2K潮牌方块主播，右屏简陋木屋为经典黄头蓝衣绿腿R6新手小人（均为无手指1x2x1实心平头方手与纯平2D五官贴图）",
    shots: [
      {
        role: "Hook / 双人连麦PK亮出宠物蛋",
        durationSec: 3.5,
        pkScoreRatio: 0.78,
        actionEn:
          "across the locked 50/50 webcam split, the Left Y2K streamer boasts beside a golden VIP egg while the Right Classic Noob sits stiffly beside a plain spotted starter egg",
        actionZh:
          "对称50/50连麦分屏中，左屏潮人主播拍着胸前金色VIP盲盒蛋向镜头炫耀（PK条遥遥领先），右屏黄皮新手木讷端坐在普通斑点新手蛋后",
        eyeLineEn: "Left host smirks 0° at lens; Right Noob keeps unchanging Default Smile staring straight ahead",
        eyeLineZh: "左屏自信挑眉0°看镜头；右屏新手保持永恒不变的默认微笑2D贴图",
        cameraEn: "Locked 50/50 dual-webcam split-screen (warm magenta studio left vs plain daylight room right)",
        cameraZh: "双直播间锁死28mm对称分屏（左暖粉霓虹房 vs 右极简新手房）",
        hailuoTag: "[Static shot]",
        chatEn: "EZ PK WIN!",
        sfxCue: "chime",
        sfx: "PK开局战鼓声 + 连麦接通提示音",
        caption: "PK赌注：谁孵出稀有度低谁当场改名叫小丑！",
        hudPopup: "join_toast",
        actors: [
          { castId: "y2k", fromPos: [-0.58, 0, 0.05], toPos: [-0.58, 0, 0.05], yaw: 0.22, pose: "cheer", expression: "smirk", theme: "y2k", handPropR: "mystery_egg" },
          { castId: "noob", fromPos: [0.58, 0, 0.05], toPos: [0.58, 0, 0.05], yaw: -0.18, pose: "idle", expression: "smile", theme: "noob", handPropL: "mystery_egg" }
        ]
      },
      {
        role: "Proof / 双方同步刚性拍蛋开裂",
        durationSec: 4.0,
        pkScoreRatio: 0.65,
        actionEn:
          "both blocky hosts pivot their solid 1x2x1 rectangular right arms down in unison to tap their Mystery Eggs on the desks as bright geometric cracks appear",
        actionZh:
          "左右分屏两位方块主播同步挥落1x2x1实心平头右方臂轻拍桌面宠物蛋，两枚方块蛋壳同时亮起几何裂纹发光线",
        eyeLineEn: "both hosts lean slightly toward their webcam lenses watching the glowing cracks",
        eyeLineZh: "双方同时前倾盯住桌面发光裂纹等待开奖",
        cameraEn: "Locked 50/50 dual-webcam split-screen with glowing egg light spill on both hosts",
        cameraZh: "对称50/50固定双机位，桌面盲盒蛋裂纹强光映亮双方桶状下巴",
        hailuoTag: "[Push in]",
        chatEn: "CRACKING!!",
        sfxCue: "clack",
        sfx: "双声道清脆敲蛋壳声 + 蓄力上升合成音",
        caption: "三、二、一，同时开蛋见证奇迹！！",
        hudPopup: "commerce_card",
        actors: [
          { castId: "y2k", fromPos: [-0.58, 0, 0.05], toPos: [-0.58, 0, 0.05], yaw: 0.22, pose: "slam", expression: "grin", theme: "y2k" },
          { castId: "noob", fromPos: [0.58, 0, 0.05], toPos: [0.58, 0, 0.05], yaw: -0.18, pose: "slam", expression: "smile", theme: "noob" }
        ]
      },
      {
        role: "Twist / 新手欧皇爆出传说霓虹神龙",
        durationSec: 4.0,
        pkScoreRatio: 0.16,
        actionEn:
          "Left Y2K streamer's golden egg pops into a tiny plain gray blocky pebble, while Right Noob's starter egg erupts into a floating cyan-and-gold blocky Mythic Neon Dragon!",
        actionZh:
          "左屏金色蛋噗地变成一块灰色普通方块鹅卵石，而右屏新手的普通蛋轰然金光炸裂，腾空浮现一只青金双色几何方块传说神龙（PK血条瞬间反杀拉满）！",
        eyeLineEn: "Left host jaw-drops with O_O ring eyes staring across split seam; Right Noob keeps exact same Default Smile",
        eyeLineZh: "左屏潮人O_O震惊扭头隔着分屏线死盯右屏神龙；右屏新手表情纹丝不动依然默认微笑",
        cameraEn: "Locked 50/50 split-screen with golden mythic rim light flooding Right Noob's room",
        cameraZh: "对称50/50分屏，右屏瞬间被金色传说神宠光效填满",
        hailuoTag: "[Shake, Static shot]",
        chatEn: "0.01% MYTHIC?!",
        sfxCue: "win",
        sfx: "左屏滑稽漏气音 vs 右屏史诗传说出金号角声",
        caption: "0.01%全服神宠被黄皮新手一发入魂？！PK条直接反杀！",
        hudPopup: "gift_combo",
        actors: [
          { castId: "y2k", fromPos: [-0.58, 0, 0.05], toPos: [-0.58, 0, 0.05], yaw: 0.55, pose: "recoil", expression: "shocked", theme: "y2k" },
          { castId: "noob", fromPos: [0.58, 0, 0.05], toPos: [0.58, 0, 0.05], yaw: -0.15, pose: "cheer", expression: "smile", theme: "noob" }
        ],
        props: [
          { type: "neon_dragon", pos: [0.58, 0.42, 0.35], moveTo: [0.58, 0.56, 0.35] }
        ]
      },
      {
        role: "Payoff / 左屏刚体栽倒 vs 右屏淡定喝可乐",
        durationSec: 3.5,
        pkScoreRatio: 0.08,
        actionEn:
          "Left Y2K streamer tips 90 degrees forward onto the studio desk in defeat, while Right Classic Noob calmly raises a red Bloxy Cola can to the webcam beside the hovering blocky dragon",
        actionZh:
          "左屏潮人主播沿腰部转轴90度刚体扑倒在直播台破防痛哭，右屏黄皮新手在悬浮方块神龙陪伴下淡定举起红色Bloxy Cola可乐罐向观众致意",
        eyeLineEn: "Left X_X faceplant; Right calm 0° Default Smile toast to chat",
        eyeLineZh: "左屏X_X扑街定格；右屏0°举罐淡定敬礼",
        cameraEn: "Locked 50/50 dual-webcam split-screen payoff",
        cameraZh: "50/50双机位强烈反差收尾",
        hailuoTag: "[Static shot]",
        chatEn: "GG NOOB WINS",
        sfxCue: "win",
        sfx: "汽水拉开清脆滋声 + PK胜利欢呼音效",
        caption: "氪金大佬当场自闭，老铁们把『欧皇』打在公屏！",
        hudPopup: "gift_combo_peak",
        actors: [
          { castId: "y2k", fromPos: [-0.58, 0, 0.05], toPos: [-0.58, 0, 0.05], yaw: 0.0, pose: "faceplant", expression: "dizzy", theme: "y2k" },
          { castId: "noob", fromPos: [0.58, 0, 0.05], toPos: [0.58, 0, 0.05], yaw: 0.0, pose: "idle", expression: "smile", theme: "noob", handPropR: "cola" }
        ],
        props: [
          { type: "neon_dragon", pos: [0.58, 0.54, 0.35], moveTo: [0.58, 0.48, 0.35] }
        ]
      }
    ]
  }
};

/**
 * Auto-infer best camera rig, style adapter, lighting, and HUD platform from an arbitrary user plot string
 * when not explicitly overridden on the CLI.
 */
export function inferLivestreamConfigFromPlot(plotText = "", overrides = {}) {
  const p = String(plotText || "");
  let style = overrides.style && STYLE_ADAPTERS[overrides.style] ? overrides.style : "";
  if (!style) {
    if (/roblox|\br6\b|\br15\b|方块小人|obby|doors|bloxy/i.test(p)) style = "roblox-blocky";
    else if (/minecraft|voxel|我的世界|体素|苦力怕|红石/i.test(p)) style = "voxel-sandbox";
    else if (/vtuber|虚拟主播|live2d|二次元|动漫/i.test(p)) style = "anime-vtuber";
    else if (/盲盒|潮玩|黏土|皮克斯|vinyl|chibi/i.test(p)) style = "stylized-3d";
    else if (/仙侠|御剑|古装|武侠|骑士|巨龙|太空|赛博|末日|魔法|wuxia|medieval|dragon|cyberpunk|spaceship/i.test(p))
      style = "cinematic-genre-adapt";
    else style = "realistic-irl";
  }

  let rig = overrides.rig && RIG_PROFILES[overrides.rig] ? overrides.rig : "";
  if (!rig) {
    if (/连麦|\bpk\b|对决PK|双人分屏|versus\s+stream/i.test(p)) rig = "pk-cohost-split";
    else if (/实况|打游戏|跑酷|通关|speedrun|gameplay|画中画|pip/i.test(p)) rig = "pip-facecam-rig";
    else if (/开箱|测评|带货|美妆|试色|做饭|手工|unbox|review|cooking|asmr/i.test(p)) rig = "overhead-showcase-rig";
    else if (/监控|无人|24小时|超市夜班|cctv|security\s+cam/i.test(p)) rig = "cctv-obs-fixed";
    else if (/鬼屋|走廊|探险|密室|废墟|手电筒|haunted|corridor|abandoned/i.test(p)) rig = "chest-head-pov";
    else if (/街头|户外|夜市|御剑|旅行|爬山|屋顶|street|outdoor|rooftop|flight/i.test(p)) rig = "handheld-selfie-irl";
    else rig = "desktop-webcam";
  }

  const rigDef = RIG_PROFILES[rig] || RIG_PROFILES["desktop-webcam"];
  const lighting =
    overrides.lighting && LIGHTING_PRESETS[overrides.lighting]
      ? overrides.lighting
      : rigDef.defaultLighting;

  let platform = overrides.platform || "";
  if (!platform) {
    const hasZh = /[\u4e00-\u9fff]/.test(p);
    platform = hasZh ? (rig === "pk-cohost-split" ? "kuaishou" : "douyin") : "tiktok";
  }

  return { style, rig, lighting, platform: resolvePlatformPreset(platform).id };
}

/**
 * Translate ANY freeform storyline/plot into a structured 4-beat (15s) or 8-beat (30s)
 * Livestream Perspective spec, preserving the user's concrete plot elements while injecting
 * authentic camera rig physics, 0°/15° fourth-wall eye-lines, and unscripted live timing.
 */
export function translatePlotToLivestreamSpec(plotText, options = {}) {
  const cleanPlot = String(plotText || "Creator tests a mysterious gadget live on desk").trim();
  const { style, rig, lighting, platform } = inferLivestreamConfigFromPlot(cleanPlot, options);
  const styleDef = STYLE_ADAPTERS[style];
  const rigDef = RIG_PROFILES[rig];
  const isZhPlot = /[\u4e00-\u9fff]/.test(cleanPlot);
  const host = options.host || (style === "roblox-blocky" ? "Momo" : isZhPlot ? "阿泽" : "Alex");

  const slug =
    options.slug ||
    cleanPlot
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 32) ||
    "custom_livestream_pov";

  const subjectEn =
    style === "roblox-blocky"
      ? `an authentic 3D Roblox SmoothPlastic avatar ("${host}", 2x2x1 rectangular torso, flush 1x2x1 blocky legs, fingerless and clawless solid 1x2x1 rectangular block hands, smooth studless 1:1 barrel head, flat 2D face decal)`
      : `a ${styleDef.labelEn} livestream host ("${host}") framed via ${rigDef.labelEn} (${styleDef.geometryLockEn})`;

  const subjectZh =
    style === "roblox-blocky"
      ? `纯正3D Roblox SmoothPlastic方块主播「${host}」（2x2x1长方体躯干、并拢同宽1x2x1方腿、无手指无乐高C型爪的1x2x1实心平头方手、平滑无颗粒1:1桶状头、纯平2D贴图脸）`
      : `采用【${rigDef.labelZh}】直拍的【${styleDef.labelZh}】主播「${host}」（${styleDef.geometryLockZh}）`;

  const plotSummaryEn = isZhPlot ? `live scenario "${cleanPlot}"` : cleanPlot;
  const plotSummaryZh = cleanPlot;

  const baseFourShots = [
    {
      role: "Hook / 开播暴击立Flag",
      durationSec: 3.5,
      actionEn: `opens the live broadcast right inside the world of ${plotSummaryEn}, leaning toward the 0° live lens to greet viewers and point out the setup`,
      actionZh: `在「${plotSummaryZh}」现场直接开播，身体朝0°直播镜头前倾打招呼并抬手向弹幕展示当前处境`,
      eyeLineEn: "direct 0° lens eye-contact with a quick 15° glance toward the live chat feed",
      eyeLineZh: "0°直视主镜头立Flag互动，顺势偏转15°扫一眼实时滚动的弹幕",
      cameraEn: `${rigDef.lensEn}, crisp opening framing`,
      cameraZh: `${rigDef.lensZh}，极具临场感的开播第一镜`,
      hailuoTag: "[Push in]",
      chatEn: "WE ARE LIVE!",
      sfxCue: "chime",
      sfx: "开播提示音 + 近距离真实收音环境声",
      caption: isZhPlot ? `直播实测：${plotSummaryZh}！` : `Chat, we are actually doing this live: ${cleanPlot}!`,
      hudPopup: "join_toast"
    },
    {
      role: "Proof / 怼脸实测与细节推进",
      durationSec: 4.0,
      actionEn: `brings the key prop or scene detail of ${plotSummaryEn} close toward the lens for live inspection while narrating to skeptical chat`,
      actionZh: `围绕「${plotSummaryZh}」将关键道具或现场细节凑近直播镜头自证，边操作边回应弹幕质疑`,
      eyeLineEn: "alternates between the close-up action and 0° camera confirmation",
      eyeLineZh: "视线在近景操作物与0°直播镜头之间来回确认对焦",
      cameraEn: `${rigDef.lensEn}, continuous live autofocus and physical mount truth`,
      cameraZh: `${rigDef.lensZh}，真实连续自动对焦与物理支架反馈`,
      hailuoTag: "[Static shot]",
      chatEn: "LOOK CLOSE!",
      sfxCue: "clack",
      sfx: "近场操作细节声 + 弹幕快速刷屏轻响",
      caption: isZhPlot ? "零剪辑零剧本，镜头拉近给家人们看清楚！" : "Zero cuts, zero script — look right at the lens!",
      hudPopup: "commerce_card"
    },
    {
      role: "Twist / 突发直播事故与剧情高潮",
      durationSec: 4.0,
      actionEn: `at the climax of ${plotSummaryEn}, an unscripted live twist erupts right on camera, jolting the rig as the host freezes in live shock`,
      actionZh: `「${plotSummaryZh}」推进到最高潮时突发意外反转，物理直播机位随之产生真实震动，主播当场瞳孔地震定格`,
      eyeLineEn: "startled snap toward the live anomaly then wide-eyed 0° stare back at camera",
      eyeLineZh: "猛地看向突发异变方向，随即瞪大双眼0°回看镜头确认全被播了出去",
      cameraEn: `${rigDef.lensEn} with authentic startled micro-shake (${rigDef.physicsEn})`,
      cameraZh: `${rigDef.lensZh}，触发真实物理惊吓微震（${rigDef.physicsZh}）`,
      hailuoTag: "[Shake, Pull out]",
      chatEn: "WAIT WHAT?!",
      sfxCue: "buzz",
      sfx: "突发碰撞/异响声 + 麦克风瞬态收音反馈",
      caption: isZhPlot ? "等一下？？这不在计划里啊！！" : "WAIT A SECOND THAT WAS NOT SUPPOSED TO HAPPEN?!",
      hudPopup: "gift_combo"
    },
    {
      role: "Payoff / 满屏问号看弹幕破防定格",
      durationSec: 3.5,
      actionEn: `amid the aftermath of ${plotSummaryEn}, the host stares speechlessly between the exploding 15° chat screen and the 0° live lens for a viral clip-that freeze`,
      actionZh: `在「${plotSummaryZh}」翻车余波中，主播在15°刷爆问号的弹幕屏与0°主摄像头之间无语凝视，定格成神级直播切片结尾`,
      eyeLineEn: "15° frantic chat-screen read locking into deadpan 0° lens freeze",
      eyeLineZh: "先偏15°看满屏哈哈弹幕，再转回0°生无可恋盯住镜头收尾",
      cameraEn: `${rigDef.lensEn}, holding steady for clip-worthy reaction payoff`,
      cameraZh: `${rigDef.lensZh}，稳定接住主播破防微表情形成循环点`,
      hailuoTag: "[Static shot]",
      chatEn: "CLIP THAT!!",
      sfxCue: "win",
      sfx: "礼物连击刷屏叮声 + 憋笑叹气收音",
      caption: isZhPlot ? "录屏的兄弟手下留情，直播间要炸了…" : "Chat please stop clipping this 💀💀",
      hudPopup: "gift_combo_peak"
    }
  ];

  return {
    slug,
    category: style === "roblox-blocky" ? "roblox-livestream" : "general-ai-video",
    titleZh: isZhPlot ? `直播视角：${cleanPlot}` : `直播视角改编：${cleanPlot}`,
    titleEn: `Livestream POV: ${cleanPlot}`,
    style,
    rig,
    lighting,
    platform,
    host,
    backdrop: style === "roblox-blocky" ? "studio" : "study_room",
    subjectEn,
    subjectZh,
    shots: baseFourShots
  };
}

/**
 * Expand a 4-shot base storyboard to 8 unique shots (for 30s) or 12 unique shots (for 45s)
 * with zero duplicate action strings so every single clip has its own distinct single-action beat.
 */
function expandShotsToCount(baseShots, targetShotCount, baseTemplate) {
  if (baseShots.length >= targetShotCount) {
    return baseShots.slice(0, targetShotCount);
  }
  const expanded = [];
  for (let i = 0; i < baseShots.length; i++) {
    const s = baseShots[i];
    expanded.push({ ...s, durationSec: 3.75 });
    if (expanded.length < targetShotCount) {
      expanded.push({
        ...s,
        role: `${s.role.split("/")[0].trim()} Reaction Beat ${i + 1} / 弹幕实时反馈镜`,
        durationSec: 3.75,
        actionEn: `following beat ${i + 1}, ${baseTemplate.host || "the host"} glances 15° off-axis at the surging live chat reaction and leans closer to the lens to respond in real time (beat-${i + 1} reaction cut)`,
        actionZh: `承接第${i + 1}拍动作，主播「${baseTemplate.host || "Alex"}」偏转15°扫视暴涨的实时弹幕区，随即凑近0°镜头做出即时嘴硬回应（第${i + 1}组互动反应切镜）`,
        hailuoTag: "[Static shot]",
        hudPopup: i % 2 === 0 ? "join_toast" : "gift_combo"
      });
    }
  }
  while (expanded.length < targetShotCount) {
    const idx = expanded.length + 1;
    expanded.push({
      ...baseShots[baseShots.length - 1],
      role: `Encore Live Beat ${idx} / 下播前返场互动`,
      durationSec: 3.75,
      actionEn: `waves toward the 0° live lens during encore beat ${idx} while thanking top gifters before cutting the stream`,
      actionZh: `在第${idx}拍返场互动中朝0°直播镜头挥手感谢榜一礼物并准备光速下播`,
      hailuoTag: "[Pull out]"
    });
  }
  return expanded.slice(0, targetShotCount);
}

function formatEngineCleanPromptEn(engine, rigSpec, base, shot) {
  const cleanTail =
    "9:16 vertical raw livestream camera plate, clean camera feed, zero burned-in UI text, zero scrolling comments, zero platform watermarks.";
  const core = `${rigSpec.rig.lensEn}. Subject: ${base.subjectEn}. Action: ${shot.actionEn}. Eye-line: ${shot.eyeLineEn}. Camera physics: ${shot.cameraEn}. Lighting: ${rigSpec.lighting.promptEn}. ${cleanTail}`;

  switch (engine) {
    case "hailuo":
      return `${shot.hailuoTag || "[Static shot]"} ${core}`;
    case "runway":
      return `Camera: ${shot.cameraEn} (${rigSpec.rig.lensEn}). Subject & Action: ${base.subjectEn} ${shot.actionEn}. ${shot.eyeLineEn}. ${cleanTail}`;
    case "sora":
      return `Physical Livestream Capture (${rigSpec.rig.labelEn}): ${core}`;
    case "veo":
      return `${core} Live Audio: ${shot.sfx || "close-mic streamer voice and room ambience"}.`;
    default:
      return core;
  }
}

function formatEngineCleanPromptZh(engine, rigSpec, base, shot) {
  const engineTag =
    engine === "kling"
      ? "【可灵I2V纯净直播底片】"
      : engine === "seedance"
      ? "【即梦I2V首尾帧纯净底片】"
      : engine === "wan"
      ? "【万相2.6竖屏直播底片】"
      : `【${engine.toUpperCase()} 直播视角纯净底片】`;

  return `${engineTag}9:16竖屏，${rigSpec.rig.lensZh}。主体：${base.subjectZh}。单一动作：${shot.actionZh}。互动眼神轴：${shot.eyeLineZh}。机位反馈：${shot.cameraZh}。补光：${rigSpec.lighting.promptZh}。100%纯净无UI文字底片（严禁AI直出滚动弹幕文字、礼物按钮或平台台标水印，所有直播边框由后置HUD叠加）。`;
}

export function compileStoryboard(options = {}) {
  const engine = ENGINE_PROFILES[options.engine] ? options.engine : "kling";
  let base;

  if (options.specObject) {
    base = { ...options.specObject };
  } else if (options.spec) {
    const abs = path.resolve(options.spec);
    base = JSON.parse(fs.readFileSync(abs, "utf8").replace(/^\uFEFF/, ""));
  } else if (options.plot) {
    base = translatePlotToLivestreamSpec(options.plot, options);
  } else {
    const tplKey = TEMPLATES[options.template] ? options.template : "irl-night-market-selfie";
    base = structuredClone(TEMPLATES[tplKey]);
  }

  const style = options.style && STYLE_ADAPTERS[options.style] ? options.style : base.style || "realistic-irl";
  const rig = options.rig && RIG_PROFILES[options.rig] ? options.rig : base.rig || "desktop-webcam";
  const lighting =
    options.lighting && LIGHTING_PRESETS[options.lighting]
      ? options.lighting
      : base.lighting || RIG_PROFILES[rig].defaultLighting;
  const platformPreset = resolvePlatformPreset(options.platform || base.platform || "douyin");

  const rigSpec = buildRigSpec({
    rig,
    style,
    lighting,
    hud: platformPreset.id === "clean" ? "raw-clean" : "clean-post-hud",
    host: options.host || base.host || "Alex",
    cohost: options.cohost || base.cohost || "Momo",
    robloxRig: options.robloxRig || base.robloxRig || "chibi-blocky"
  });

  const durationSec = Number(options.duration || base.durationSeconds || 15);
  const targetShotCount = durationSec >= 45 ? 12 : durationSec >= 30 ? 8 : (base.shots?.length || 4);
  const rawShots = expandShotsToCount(base.shots || [], targetShotCount, base);

  const sumRaw = rawShots.reduce((a, s) => a + (Number(s.durationSec) || 3.75), 0);
  const scale = durationSec / sumRaw;

  let cursor = 0;
  const compiledShots = rawShots.map((sh, idx) => {
    const d = Number(((Number(sh.durationSec) || 3.75) * scale).toFixed(2));
    const start = cursor;
    const end = idx === rawShots.length - 1 ? durationSec : Number((cursor + d).toFixed(2));
    cursor = end;

    const subjectAnchorEn =
      base.subjectEn ||
      `${rigSpec.style.labelEn} streamer "${rigSpec.hostName}" (${rigSpec.style.geometryLockEn})`;
    const subjectAnchorZh =
      base.subjectZh ||
      `${rigSpec.style.labelZh}主播「${rigSpec.hostName}」（${rigSpec.style.geometryLockZh}）`;

    const baseWithSubject = { ...base, subjectEn: subjectAnchorEn, subjectZh: subjectAnchorZh };

    const firstFramePromptEn = `9:16 vertical static keyframe, ${rigSpec.rig.lensEn}: ${subjectAnchorEn}, mid-setup before ${sh.actionEn}. ${rigSpec.lighting.promptEn}. Crisp room/world background, clean raw camera feed, zero UI text or watermarks.`;
    const firstFramePromptZh = `9:16竖屏首帧静态锚定图，${rigSpec.rig.lensZh}：${subjectAnchorZh}，处于「${sh.actionZh}」起始构图。${rigSpec.lighting.promptZh}。100%纯净无UI文字底片，零乱码弹幕，零水印。`;

    const i2vPromptEn = formatEngineCleanPromptEn(engine, rigSpec, baseWithSubject, sh);
    const i2vPromptZh = formatEngineCleanPromptZh(engine, rigSpec, baseWithSubject, sh);

    const hudOverlay = buildShotHudTimeline(sh, idx, rawShots.length, platformPreset.id, base.slug || "");

    return {
      shotNumber: idx + 1,
      role: sh.role || `Shot ${idx + 1}`,
      durationSec: Number((end - start).toFixed(2)),
      timeWindow: `${start.toFixed(1)}s–${end.toFixed(1)}s`,
      exactTimeWindow: `${start.toFixed(2)}s–${end.toFixed(2)}s`,
      actionEn: sh.actionEn,
      actionZh: sh.actionZh,
      eyeLineEn: sh.eyeLineEn || rigSpec.rig.eyeLineEn,
      eyeLineZh: sh.eyeLineZh || rigSpec.rig.eyeLineZh,
      cameraEn: sh.cameraEn || rigSpec.rig.lensEn,
      cameraZh: sh.cameraZh || rigSpec.rig.lensZh,
      hailuoTag: sh.hailuoTag || "[Static shot]",
      firstFramePromptEn,
      firstFramePromptZh,
      i2vPromptEn,
      i2vPromptZh,
      trackBFacecamPromptEn: sh.facecamPromptEn || null,
      trackBFacecamPromptZh: sh.facecamPromptZh || null,
      negativePromptEn: rigSpec.negativePromptEn,
      negativePromptZh: rigSpec.negativePromptZh,
      sfxCue: sh.sfxCue || "chime",
      sfx: sh.sfx || "近场收音 + 弹幕提示音",
      caption: sh.caption || "",
      chatEn: sh.chatEn || "",
      hudOverlay,
      actors: sh.actors || null,
      props: sh.props || null,
      pkScoreRatio: sh.pkScoreRatio
    };
  });

  return {
    slug: base.slug || "livestream_episode",
    titleEn: base.titleEn || "Livestream POV Short",
    titleZh: base.titleZh || "直播视角短片",
    category: base.category || (style === "roblox-blocky" ? "roblox-livestream" : "general-ai-video"),
    engine,
    engineLabel: ENGINE_PROFILES[engine].label,
    style,
    rig,
    lighting,
    platform: platformPreset.id,
    platformLabelEn: platformPreset.labelEn,
    platformLabelZh: platformPreset.labelZh,
    aspect: "9:16",
    durationSeconds: durationSec,
    shotCount: compiledShots.length,
    host: rigSpec.hostName,
    cohost: rigSpec.cohostName,
    backdrop: base.backdrop || "study_room",
    dualTrackNoteEn: rigSpec.dualTrackNoteEn,
    dualTrackNoteZh: rigSpec.dualTrackNoteZh,
    setupAnchorPromptEn: rigSpec.setupAnchorPromptEn,
    setupAnchorPromptZh: rigSpec.setupAnchorPromptZh,
    shots: compiledShots
  };
}

export function formatStoryboardMarkdown(plan, lang = "en") {
  const code = normalizeLang(lang);
  const includeZh = code === "zh" || code === "zh-tw" || code === "zh-en";

  const lines = [
    `<!-- lang: ${code} | engine: ${plan.engine} | rig: ${plan.rig} | style: ${plan.style} | platform: ${plan.platform} -->`,
    `# ${includeZh ? `${plan.titleZh} / ${plan.titleEn}` : plan.titleEn}`,
    "",
    `- **Aspect & Duration**: \`${plan.aspect}\` · \`${plan.durationSeconds}s\` (\`${plan.shotCount}\` non-repeating live beats)`,
    `- **Camera Rig**: \`${plan.rig}\` · **Style Pack**: \`${plan.style}\` · **Engine**: \`${plan.engine}\` (${plan.engineLabel})`,
    `- **Post-HUD Chrome Preset**: \`${plan.platform}\` — ${includeZh ? plan.platformLabelZh : plan.platformLabelEn}`,
    `- **Compositing Strategy**: ${includeZh ? plan.dualTrackNoteZh : plan.dualTrackNoteEn}`,
    "",
    "## Beat-by-Beat Livestream Storyboard / 分镜与弹幕时间轴",
    "",
    "| # | Window | Live Beat Role | Physical Action & 4th-Wall Eye-Line | Post-HUD Popup & Audio |",
    "| :---: | :---: | --- | --- | --- |"
  ];

  for (const s of plan.shots) {
    const act = includeZh ? `${s.actionZh}<br>*眼神轴*：${s.eyeLineZh}` : `${s.actionEn}<br>*Eye-line*: ${s.eyeLineEn}`;
    const hudSummary = s.hudOverlay.enabled
      ? `\`${s.hudOverlay.platform}\` · \`${s.hudOverlay.activePopup}\` · 👥 ${s.hudOverlay.viewerCount.toLocaleString()}<br>🔊 ${s.sfx}`
      : `Raw Clean Plate<br>🔊 ${s.sfx}`;
    lines.push(`| ${String(s.shotNumber).padStart(2, "0")} | \`${s.timeWindow}\` | ${s.role} | ${act} | ${hudSummary} |`);
  }

  lines.push("", "## Clean-Plate Shot Prompts / 逐镜无乱码纯净底片提示词", "");
  for (const s of plan.shots) {
    lines.push(`### Shot ${String(s.shotNumber).padStart(2, "0")} (\`${s.exactTimeWindow}\`) — ${s.role}`, "");
    lines.push("- **First-Frame Anchor (EN)**: `" + s.firstFramePromptEn + "`");
    if (includeZh) {
      lines.push("- **首帧静态锚定词 (ZH)**: `" + s.firstFramePromptZh + "`");
    }
    lines.push("- **Clean-Plate Motion Prompt (EN)**: `" + s.i2vPromptEn + "`");
    if (includeZh) {
      lines.push("- **视频动态生成词 (ZH)**: `" + s.i2vPromptZh + "`");
    }
    if (s.trackBFacecamPromptEn) {
      lines.push("- **Track-B Corner Facecam Prompt (EN)**: `" + s.trackBFacecamPromptEn + "`");
      if (includeZh && s.trackBFacecamPromptZh) {
        lines.push("- **B轨右上主播反应小窗提示词 (ZH)**: `" + s.trackBFacecamPromptZh + "`");
      }
    }
    lines.push("- **Negative Anti-Drift**: `" + (includeZh ? s.negativePromptZh : s.negativePromptEn) + "`");
    if (s.caption) {
      lines.push(`- **Post-HUD Caption / 直播花字**: "${s.caption}"`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

function parseArgs(argv) {
  const opts = {
    template: "irl-night-market-selfie",
    spec: "",
    plot: "",
    style: "",
    rig: "",
    lighting: "",
    platform: "",
    host: "",
    cohost: "",
    robloxRig: "",
    duration: 15,
    engine: "kling",
    lang: "en",
    out: "",
    json: false,
    help: false
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") opts.help = true;
    else if (a === "--json") opts.json = true;
    else if (a === "--template" && argv[i + 1]) opts.template = argv[++i].toLowerCase().trim();
    else if (a === "--spec" && argv[i + 1]) opts.spec = argv[++i];
    else if (a === "--plot" && argv[i + 1]) opts.plot = argv[++i];
    else if (a === "--style" && argv[i + 1]) opts.style = argv[++i].toLowerCase().trim();
    else if (a === "--rig" && argv[i + 1]) opts.rig = argv[++i].toLowerCase().trim();
    else if (a === "--lighting" && argv[i + 1]) opts.lighting = argv[++i].toLowerCase().trim();
    else if (a === "--platform" && argv[i + 1]) opts.platform = argv[++i].toLowerCase().trim();
    else if (a === "--host" && argv[i + 1]) opts.host = argv[++i].trim();
    else if (a === "--cohost" && argv[i + 1]) opts.cohost = argv[++i].trim();
    else if (a === "--roblox-rig" && argv[i + 1]) opts.robloxRig = argv[++i].toLowerCase().trim();
    else if (a === "--duration" && argv[i + 1]) opts.duration = Number(argv[++i]) || 15;
    else if (a === "--engine" && argv[i + 1]) opts.engine = argv[++i].toLowerCase().trim();
    else if (a === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
    else if (a === "--out" && argv[i + 1]) opts.out = argv[++i];
  }
  return opts;
}

function printHelp() {
  console.log(`Usage:
  node scripts/shot_compiler.mjs --plot "<any story/plot>" [--style <id>] [--rig <id>] [--platform <id>] [options]
  node scripts/shot_compiler.mjs --template <id> [options]
  node scripts/shot_compiler.mjs --spec <episode.json> [options]

Compile any visual style and storyline into a 9:16 Livestream POV storyboard, clean-plate I2V/T2V prompts,
and multi-platform HUD timeline (Douyin, Kuaishou, Instagram Live, X Live, TikTok Live).

Built-in Templates:
  General / Cross-Genre AI Video:
    irl-night-market-selfie | desk-unboxing-autofocus | midnight-corridor-fpv-live |
    late-night-study-webcam | wuxia-sword-flight-live
  Roblox Livestream POV:
    roblox-obby-rage-pip    | roblox-doors-irl-selfie | roblox-pet-hatch-pk

Options:
  --plot <text>       Translate any freeform Chinese/English plot into a 4/8-shot livestream storyboard
  --template <id>     Built-in template ID (default: irl-night-market-selfie)
  --spec <file>       Custom declarative episode spec JSON
  --style <id>        Style override: realistic-irl | roblox-blocky | anime-vtuber | stylized-3d | voxel-sandbox | cinematic-genre-adapt
  --rig <id>          Rig override: desktop-webcam | handheld-selfie-irl | pip-facecam-rig | overhead-showcase-rig | chest-head-pov | pk-cohost-split | cctv-obs-fixed | drone-follow-live
  --platform <id>     Post-HUD preset: douyin | kuaishou | instagram | x | tiktok | clean
  --duration <sec>    Target duration: 15 (4 shots) | 30 (8 shots) | 45 (12 shots)
  --engine <id>       Engine: local3d | kling | seedance | hailuo | wan | sora | veo | runway
  --lang <code>       Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en
  --out <path>        Write UTF-8 output directly to file
  --json              Emit structured JSON (ready for drift_check.mjs and render_preview.mjs)
  --help              Show this help message`);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("shot_compiler.mjs");
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    process.exit(0);
  }
  const plan = compileStoryboard(opts);
  const outText = opts.json ? JSON.stringify(plan, null, 2) + "\n" : formatStoryboardMarkdown(plan, opts.lang);
  if (opts.out) {
    const abs = path.resolve(opts.out);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, outText, "utf8");
    console.log(`Wrote compiled storyboard (${plan.shotCount} shots, ${plan.platform} HUD) to ${abs}`);
  } else {
    process.stdout.write(outText);
  }
}
