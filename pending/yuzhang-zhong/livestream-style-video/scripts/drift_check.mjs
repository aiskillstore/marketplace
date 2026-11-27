#!/usr/bin/env node
/**
 * drift_check.mjs
 * Zero-dependency Unicode-safe 8-Gate Livestream POV & Style Anti-Drift Linter
 * and Prompt Rescue Rewriter.
 *
 * Enforces 8 deterministic quality gates:
 * 1. Physical Camera Rig Lock (blocks omniscient cinema crane/drone drift & missing rig anchors)
 * 2. Clean-Plate Anti-Gibberish UI Guard (blocks burned-in TikTok/Douyin/Twitch chat text in diffusion)
 * 3. Fourth-Wall & Eye-Line Presence (blocks passive third-person "ignores camera" acting)
 * 4. Livestream Optics & DOF Truth (blocks anamorphic cinema bars & background-obliterating f/1.2 blur)
 * 5. Orthogonal Style & Anatomy Lock (enforces Roblox fingerless/studless R6 rules, Voxel rules, or IRL hand truth)
 * 6. Multi-Feed PiP & PK Track Safety (blocks single-pass raw T2V dual-camera hallucination)
 * 7. Single-Action & Single-Rig Continuity Budget (Unicode-safe EN+ZH verb overload & mid-clip rig jump check)
 * 8. Brand & Platform Watermark Cleanliness (blocks official TikTok/Douyin/Twitch/YouTube/Roblox logos)
 */

import fs from "node:fs";
import path from "node:path";
import { normalizeLang, STYLE_ADAPTERS, RIG_PROFILES } from "./rig_spec.mjs";

export { normalizeLang };

export const VALID_ENGINES = new Set([
  "local3d",
  "kling",
  "seedance",
  "hailuo",
  "wan",
  "sora",
  "veo",
  "runway"
]);

export const ISSUE_PATCHES = {
  "cinematic-drift": {
    titleEn: "Detached Third-Person Cinematic Drift",
    titleZh: "跑偏成传统第三人称电影空镜（丧失直播感）",
    fixEn:
      "Lock a physical livestream capture device (e.g. locked 24mm monitor-top webcam or 18mm arm's-length front selfie smartphone), keep vertical 9:16 framing, and add direct 0° lens eye-contact plus a 15° chat-monitor glance.",
    fixZh:
      "正向锁死具体物理直播采集设备（如显示器顶端24mm固定摄像头或一臂距离18mm前置自拍手机），保持9:16竖屏构图，加入0°直视镜头喊话与15°偏轴扫视弹幕副屏动作。"
  },
  "gibberish-ui": {
    titleEn: "Burned-In Gibberish Livestream UI / Alien Chat Text",
    titleZh: "AI直出乱码弹幕与融化的直播间按钮",
    fixEn:
      "Remove all 'TikTok/Twitch UI, scrolling comments, floating hearts, viewer count' from the diffusion prompt; generate a 100% clean raw camera plate (`clean camera feed, zero UI overlays, no text`) and composite crisp HUD layers in post or via `render_preview.mjs`.",
    fixZh:
      "从视频生成提示词中彻底删除「直播间弹幕文字、礼物特效按钮、在线人数UI」描述；声明 `100%纯净无UI镜头底片，零文字水印`，在后期或用 `render_preview.mjs` 叠加高清无乱码直播HUD。"
  },
  "dead-fourth-wall": {
    titleEn: "Passive Fourth Wall (No Viewer / Chat Connection)",
    titleZh: "缺乏第四面墙破壁互动（像普通摆拍而非直播）",
    fixEn:
      "Insert an active live-stream micro-beat: host leans toward the lens, holds palm behind an item for autofocus showcase, or flicks eyes 15° off-axis to read a live comment before reacting back to 0°.",
    fixZh:
      "加入标志性直播微动作：身体向摄像头前倾互动、手掌托底递物触发微距对焦，或眼神偏转15°读一条弹幕后猛回0°主镜头反应。"
  },
  "pip-hallucination": {
    titleEn: "Melting Corner Facecam / Broken Split-Screen in Single-Pass T2V",
    titleZh: "单次文生视频导致右上角主播小窗漂移融化",
    fixEn:
      "Never ask raw T2V to invent two independent moving cameras at once. Generate Track A (9:16 gameplay/world) and Track B (locked RGB facecam) separately—or anchor with a First-Frame I2V split keyframe—and composite cleanly.",
    fixZh:
      "切勿让单次T2V同时凭空生成游戏主画面与角落主播小窗。将A轨主画面与B轨固定电竞房反应特写分轨独立生成（或使用首帧I2V锁定分屏边框），再无损合成。"
  },
  "mic-flip-drift": {
    titleEn: "Microphone / Studio Setup Flipping Sides Across Cuts",
    titleZh: "跨镜头麦克风左右乱跳或房间灯带变形",
    fixEn:
      "Generate a 3-state Livestream Setup Anchor Sheet (`rig_spec.mjs`) locking `boom-left` or `lavalier` and feed First-Frame I2V keyframes for every cut.",
    fixZh:
      "先用 `rig_spec.mjs` 生成三态直播间首帧参考卡锁死左置悬臂麦/领夹麦与RGB灯带位置，全片采用首帧I2V图生视频。"
  },
  "roblox-hand-lego-drift": {
    titleEn: "Roblox Streamer Growing Human Fingers or Lego Studs/Claws",
    titleZh: "Roblox主播长出真人五指、乐高C型钩爪或地面圆粒",
    fixEn:
      "Enforce canonical Roblox geometry: `2x2x1 rectangular torso, flush 1x2x1 blocky legs, fingerless and clawless solid 1x2x1 rectangular block hands, smooth studless 1:1 barrel head, flat 2D face decal, smooth SmoothPlastic/WoodPlanks surfaces (zero raised Lego studs)`.",
    fixZh:
      "强制锁定标准Roblox比例：`2x2x1躯干、并拢同宽1x2x1方腿、无手指无乐高C型爪的1x2x1实心平头方柱手、头顶无颗粒1:1桶状圆角头、纯平2D贴图五官、平滑无凸粒地板材质`。"
  },
  "action-overload": {
    titleEn: "Single-Clip Action Overload or Mid-Shot Rig Teleport",
    titleZh: "单镜动作超载或镜头中途瞬移换机位",
    fixEn:
      "Keep each 3.5–5s clip to ONE primary physical action and ONE consistent camera rig behavior; split multi-step sequences into separate cuts.",
    fixZh:
      "严守单镜单动作单机位预算：每支3.5–5秒片段仅执行1个核心动作与1种连续机位物理反馈，多步剧情拆分为独立分镜。"
  },
  "watermark-leak": {
    titleEn: "Platform Logo or Official Brand Watermark Leak",
    titleZh: "混入抖音/TikTok/Twitch/Roblox官方台标水印",
    fixEn:
      "Strip all official platform names/logos (`TikTok logo, Douyin watermark, Twitch badge, official Roblox tilted-square logo`) from positive prompts and move them to negative exclusions.",
    fixZh:
      "从正向提示词移除一切官方平台名称与台标描述，仅用通用几何直播角标并在负向词中明确排除品牌水印。"
  }
};

/**
 * Strip negated spans so "zero burned-in TikTok UI, no human fingers, 无乱码弹幕"
 * are recognized as protective negations rather than positive violations.
 */
export function stripNegatedSpans(text = "") {
  let cleaned = String(text);
  const enNegPatterns = [
    /\b(?:zero|no|without|never|free of|avoid|excluding)\s+[^.,;()\n]{1,95}/gi
  ];
  const zhNegPatterns = [
    /(?:严禁(?:出现)?|禁止(?:出现)?|不出现|不含|无|零|拒绝|避免|杜绝|去除|排除)[^，。；、（）()\n]{1,42}/g
  ];
  for (const re of [...enNegPatterns, ...zhNegPatterns]) {
    cleaned = cleaned.replace(re, " ");
  }
  return cleaned;
}

function detectImplicitStyle(text, explicitStyle = "") {
  if (explicitStyle && STYLE_ADAPTERS[explicitStyle]) return explicitStyle;
  if (/roblox|\br6\b|\br15\b|方块小人|smoothplastic|bloxy/i.test(text)) return "roblox-blocky";
  if (/minecraft|voxel|体素|我的世界|8x8x8|16x16x16/i.test(text)) return "voxel-sandbox";
  if (/vtuber|live2d|cel[- ]shaded|虚拟主播|二次元/i.test(text)) return "anime-vtuber";
  if (/blind[- ]box|vinyl|潮玩|盲盒|pixar/i.test(text)) return "stylized-3d";
  if (/wuxia|御剑|仙侠|古风|cyberpunk|赛博|medieval|骑士|巨龙/i.test(text)) return "cinematic-genre-adapt";
  return "realistic-irl";
}

function countActionOverload(posText) {
  const enSeqMatches = posText.match(
    /\b(?:and then|then|afterwards|subsequently|next,\s*(?:he|she|it|they|the)|before finally)\b/gi
  ) || [];
  const zhSeqMatches = posText.match(/(?:然后|接着|随后|紧接着|再转身|最后又|先.*再.*接着)/g) || [];
  return enSeqMatches.length + zhSeqMatches.length;
}

export function inspectPrompt(options = {}) {
  const rawPrompt = String(options.prompt || "").trim();
  const engine = String(options.engine || "kling").toLowerCase().trim();
  const mode = String(options.mode || "i2v").toLowerCase().trim();
  const rigHint = String(options.rig || "").toLowerCase().trim();
  const styleId = detectImplicitStyle(rawPrompt, String(options.style || "").toLowerCase().trim());
  const posText = stripNegatedSpans(rawPrompt);

  const checks = [];
  const detectedIssues = new Set();
  if (options.issue && ISSUE_PATCHES[options.issue]) {
    detectedIssues.add(options.issue);
  }

  // Gate 1: Physical Camera Rig Lock
  const cinemaDriftRe =
    /\b(?:omniscient|crane shot|crane sweep|jib sweep|hollywood trailer|cinematic aerial sweep|sweeping crane)\b|(?:上帝视角|全知视角|电影摇臂|史诗大远景|航拍大全景摇臂)/i;
  const hasRigAnchorRe =
    /\b(?:webcam|selfie|arm's[- ]length|front[- ]facing|gimbal|action[- ]cam|chest[- ]mount|head[- ]strap|first[- ]person|pov|desk[- ]clamp|ring[- ]light|cctv|fixed corner cam|split[- ]screen|facecam|monitor[- ]top)\b|(?:摄像头|自拍杆|前置镜头|手持云台|一臂距离|运动相机|胸挂|第一人称|第一视角|直播机位|环形灯|俯拍支架|监控机位|连麦分屏|画中画|副屏)/i;

  if (cinemaDriftRe.test(posText)) {
    checks.push({
      gate: "1. Physical Camera Rig Lock / 物理直播机位锚点",
      status: "FAIL",
      detailEn: "Detected detached omniscient cinema crane/aerial phrasing that destroys livestream presence.",
      detailZh: "检测到上帝全知视角/电影摇臂大远景描述，会彻底破坏直播机位临场感。"
    });
    detectedIssues.add("cinematic-drift");
  } else if (!hasRigAnchorRe.test(rawPrompt)) {
    checks.push({
      gate: "1. Physical Camera Rig Lock / 物理直播机位锚点",
      status: "WARN",
      detailEn: "No explicit livestream camera mount (webcam, selfie smartphone, desk-clamp, chest POV, or CCTV) declared.",
      detailZh: "未显式声明物理直播机位（桌面摄像头、手持前置自拍、俯拍支架、胸挂POV或固定监控）。"
    });
    detectedIssues.add("cinematic-drift");
  } else {
    checks.push({
      gate: "1. Physical Camera Rig Lock / 物理直播机位锚点",
      status: "PASS",
      detailEn: "Concrete physical livestream capture rig anchored.",
      detailZh: "已锁定明确的物理直播采集机位。"
    });
  }

  // Gate 2: Clean-Plate Anti-Gibberish UI Guard
  const burnedUiRe =
    /\b(?:scrolling\s+(?:tiktok|twitch|live)?\s*(?:comments|chat)|floating\s+(?:chat\s+messages|comments|ui\s+buttons)|tiktok\s+live\s+interface|twitch\s+chat\s+overlay|gift\s+animation\s+banner|viewer\s+count\s+text\s+on\s+screen)\b|(?:滚动弹幕文字|飘过弹幕字样|直播间UI界面|抖音直播界面|快手直播间文字|礼物特效横幅|屏幕右上角在线人数文字|点赞飘心按钮)/i;
  if (burnedUiRe.test(posText)) {
    checks.push({
      gate: "2. Clean-Plate Anti-Gibberish UI Guard / 纯净底片防乱码UI锁",
      status: "FAIL",
      detailEn: "Positive prompt asks diffusion model to render scrolling UI text/buttons, causing garbled alien glyphs.",
      detailZh: "正向提示词要求扩散模型直出滚动弹幕文字或直播间按钮，会导致严重外星乱码与画面融化。"
    });
    detectedIssues.add("gibberish-ui");
  } else {
    checks.push({
      gate: "2. Clean-Plate Anti-Gibberish UI Guard / 纯净底片防乱码UI锁",
      status: "PASS",
      detailEn: "Raw plate kept free of burned-in scrolling UI text.",
      detailZh: "生成底片保持无乱码UI净空，适合后置叠加高清直播HUD。"
    });
  }

  // Gate 3: Fourth-Wall & Eye-Line Presence
  const passiveCinemaRe =
    /\b(?:(?:ignores?|ignored|ignoring)\s+the\s+(?:camera|lens)|unaware\s+of\s+(?:the\s+)?(?:camera|lens)|fourth\s+wall\s+intact)\b|(?:无视镜头|完全不看镜头演戏|浑然不觉镜头存在)/i;
  const liveEngagementRe =
    /(?:eye[- ]contact|0°|15°|8°|looks?\s+(?:directly\s+|straight\s+)?(?:into|at|up\s+into)\s+(?:the\s+)?(?:camera|lens|webcam|facecam|front\s+lens)|(?:into|toward|at)\s+(?:the|their)\s+(?:front|live|webcam|selfie|held|camera)\s+(?:lens|lenses|cam|screen)|leans?\s+close\s+to\s+the\s+glowing\s+monitor|staring\s+across\s+split\s+seam|chat[- ](?:monitor|screen|feed|phone)|autofocus\s+(?:gesture|lock|pull|shift)|palm\s+(?:flat\s+)?behind|visible\s+(?:left|right)?\s*hands?|in\s+front\s+of\s+the\s+(?:16mm\s+pov\s+)?lens|both\s+hands\s+pump\s+into\s+the\s+lower\s+frame|pov\s+(?:tilts|freezes|whip)|talking\s+to\s+chat|selfie\s+(?:preview|screen)|toast\s+to\s+chat|overhead\s+corner\s+lens|直视镜头|眼神对视|扫视副屏|看弹幕|弹幕屏|怼脸展示|手掌托底|双手伸入画面|朝镜头喊话|抬头看监控)/i;

  if (passiveCinemaRe.test(posText) && rigHint !== "cctv-obs-fixed") {
    checks.push({
      gate: "3. Fourth-Wall & Eye-Line Presence / 第四面墙互动与眼神轴",
      status: "FAIL",
      detailEn: "Prompt explicitly instructs subject to ignore the camera outside a CCTV rig.",
      detailZh: "非监控机位下明确要求角色无视镜头，丧失直播互动感。"
    });
    detectedIssues.add("dead-fourth-wall");
  } else if (!liveEngagementRe.test(rawPrompt) && rigHint !== "cctv-obs-fixed") {
    checks.push({
      gate: "3. Fourth-Wall & Eye-Line Presence / 第四面墙互动与眼神轴",
      status: "WARN",
      detailEn: "Add 0° lens eye-contact, 15° chat-screen glance, palm-backed autofocus gesture, or first-person visible hands.",
      detailZh: "建议补充0°镜头对视、15°扫弹幕眼神、手掌托底对焦手势或第一人称入画双手。"
    });
    detectedIssues.add("dead-fourth-wall");
  } else {
    checks.push({
      gate: "3. Fourth-Wall & Eye-Line Presence / 第四面墙互动与眼神轴",
      status: "PASS",
      detailEn: "Active fourth-wall lens address, chat glance, or first-person hand presence verified.",
      detailZh: "已具备第四面墙镜头互动、读弹幕眼神轴或第一视角手部锚点。"
    });
  }

  // Gate 4: Livestream Optics & Lighting Truth
  const cinemaOpticsRe =
    /\b(?:anamorphic\s+2\.39|2\.39:1\s+letterbox|f\/1\.2\s+creamy\s+bokeh|35mm\s+kodak\s+film\s+grain|cinematic\s+widescreen\s+bars)\b|(?:宽银幕黑边|2\.39:1电影画幅|f\/1\.2刀锐奶化背景全虚|胶片颗粒电影调色)/i;
  if (cinemaOpticsRe.test(posText)) {
    checks.push({
      gate: "4. Livestream Optics & Lighting Truth / 直播光学景深与补光",
      status: "FAIL",
      detailEn: "Cinema letterbox / anamorphic / f/1.2 bokeh conflicts with authentic 9:16 webcam/smartphone livestream optics.",
      detailZh: "电影宽银幕黑边/变形镜头/f1.2全虚化与真实9:16直播摄像头/手机光学冲突。"
    });
    detectedIssues.add("cinematic-drift");
  } else {
    checks.push({
      gate: "4. Livestream Optics & Lighting Truth / 直播光学景深与补光",
      status: "PASS",
      detailEn: "Optics compatible with 9:16 livestream sensor & lighting.",
      detailZh: "光学景深与9:16直播补光特征匹配。"
    });
  }

  // Gate 5: Orthogonal Style & Anatomy Lock
  let styleGate = {
    gate: `5. Style & Anatomy Lock (${styleId}) / 画风几何与手部防串味锁`,
    status: "PASS",
    detailEn: `Style pack '${styleId}' constraints satisfied.`,
    detailZh: `画风适配包「${styleId}」几何约束检查通过。`
  };
  if (styleId === "roblox-blocky") {
    const badRobloxRe =
      /\b(?:five\s+fingers|human\s+fingers|fingered\s+hands|pinches\s+with\s+thumb|lego\s+c[- ]?(?:shaped\s+)?claw|studded\s+floor|raised\s+lego\s+studs|minecraft\s+voxel|noodle[- ]like\s+arm|rubbery\s+limb|realistic\s+3d\s+nose)\b|(?:五根手指|人类五指|五指紧握|拇指捏住|乐高C型爪|乐高圆粒|凸点地板|我的世界像素|面条般弯曲|软体橡胶手臂|高挺真人鼻梁)/i;
    // Also detect contradiction: declaring fingerless AND five fingers
    const rawContradiction =
      /(?:zero\s+fingers|fingerless|无人类五指|无手指)/i.test(rawPrompt) &&
      /\b(?:with\s+five\s+fingers|wraps?\s+its\s+fingers)\b|(?:用五根手指|五指抓握)/i.test(posText);
    if (badRobloxRe.test(posText) || rawContradiction) {
      styleGate = {
        gate: `5. Style & Anatomy Lock (${styleId}) / 画风几何与手部防串味锁`,
        status: "FAIL",
        detailEn: "Roblox style violation: detected human fingers, Lego studs/C-claws, voxel drift, or rubbery limbs.",
        detailZh: "Roblox画风违规：检测到人类五指、乐高C型爪/地面凸粒、像素方头或面条软体四肢。"
      };
      detectedIssues.add("roblox-hand-lego-drift");
    } else if (!/(?:1x2x1|block\s+hands|fingerless|实心.*方.*手|无手指)/i.test(rawPrompt)) {
      styleGate = {
        gate: `5. Style & Anatomy Lock (${styleId}) / 画风几何与手部防串味锁`,
        status: "WARN",
        detailEn: "Roblox prompt should explicitly lock solid 1x2x1 fingerless/clawless block hands and 2D decal face.",
        detailZh: "Roblox直播提示词建议显式锁死1x2x1无手指无乐高爪实心方手与纯平2D贴图五官。"
      };
      detectedIssues.add("roblox-hand-lego-drift");
    }
  } else if (styleId === "voxel-sandbox") {
    if (/\b(?:five\s+fingers|human\s+fingers|smooth\s+cylindrical\s+head)\b|(?:五根手指|人类五指|圆润桶状头)/i.test(posText)) {
      styleGate = {
        gate: `5. Style & Anatomy Lock (${styleId}) / 画风几何与手部防串味锁`,
        status: "FAIL",
        detailEn: "Voxel style violation: detected human fingers or rounded non-cubic head.",
        detailZh: "体素画风违规：检测到人类五指或非立方体圆头。"
      };
    }
  } else if (styleId === "realistic-irl") {
    if (/\b(?:six\s+fingers|plastic\s+doll\s+skin)\b|(?:六根手指|塑料假人皮肤)/i.test(posText)) {
      styleGate = {
        gate: `5. Style & Anatomy Lock (${styleId}) / 画风几何与手部防串味锁`,
        status: "FAIL",
        detailEn: "Realistic IRL violation: uncanny skin or malformed hand token in positive prompt.",
        detailZh: "写实真人违规：正向提示词包含塑料假人或畸形手部描述。"
      };
    }
  }
  checks.push(styleGate);

  // Gate 6: Multi-Feed PiP & PK Track Safety
  const asksSinglePassPiP =
    /\b(?:picture[- ]in[- ]picture|corner\s+facecam\s+box|small\s+webcam\s+overlay\s+in\s+the\s+corner)\b|(?:右上角画中画小窗|角落叠着主播小窗|左下角悬浮小窗)/i.test(
      posText
    );
  const hasDualTrackSafety =
    /\b(?:dual[- ]track|track\s+a|track\s+b|composited\s+separately|locked\s+first[- ]frame\s+split)\b|(?:双轨合成|分轨独立生成|首帧锚定分屏)/i.test(
      rawPrompt
    ) || engine === "local3d" || mode === "local3d";

  if (asksSinglePassPiP && mode === "t2v" && !hasDualTrackSafety) {
    checks.push({
      gate: "6. Multi-Feed PiP & PK Track Safety / 画中画与连麦分轨安全",
      status: "FAIL",
      detailEn: "Raw single-pass T2V cannot stably animate both a moving world and a corner PiP facecam without melting borders; split into Track A + Track B.",
      detailZh: "单次裸跑T2V同时生成动态主场景与角落主播画中画会导致边框融化漂移，请拆分为A/B双轨生成后合成。"
    });
    detectedIssues.add("pip-hallucination");
  } else {
    checks.push({
      gate: "6. Multi-Feed PiP & PK Track Safety / 画中画与连麦分轨安全",
      status: "PASS",
      detailEn: "Single-camera or dual-track safe compositing strategy confirmed.",
      detailZh: "机位轨道策略安全，无单次T2V画中画融化风险。"
    });
  }

  // Gate 7: Single-Action & Single-Rig Continuity Budget
  const seqCount = countActionOverload(posText);
  const rigTeleport =
    /(?:desktop\s+webcam|显示器固定摄像头)/i.test(posText) &&
    /(?:aerial\s+drone|outdoor\s+sprint\s+down\s+the\s+street|冲出大楼在街头狂奔跟拍)/i.test(posText);

  if (seqCount >= 2 || rigTeleport) {
    checks.push({
      gate: "7. Single-Action & Rig Budget / 单镜单动作与机位连续性预算",
      status: "FAIL",
      detailEn: rigTeleport
        ? "Mid-clip camera rig teleportation detected (cannot jump from locked desk webcam to outdoor follow cam in one clip)."
        : `Detected ${seqCount + 1}+ chained sequential actions in a single 4–5s clip; split into separate cuts.`,
      detailZh: rigTeleport
        ? "检测到单镜头中途瞬移切换物理机位（桌面固定摄像头无法在同一镜内变成街头航拍跟拍）。"
        : `单条4–5秒提示词串联了过多连续动作（检测到 ${seqCount} 处时序串联词），请拆分为独立分镜。`
    });
    detectedIssues.add("action-overload");
  } else {
    checks.push({
      gate: "7. Single-Action & Rig Budget / 单镜单动作与机位连续性预算",
      status: "PASS",
      detailEn: "Clip stays within single primary action and continuous camera rig budget.",
      detailZh: "符合单镜头单一核心动作与连续机位预算。"
    });
  }

  // Gate 8: Brand & Platform Watermark Cleanliness
  const brandLeakRe =
    /\b(?:official\s+tiktok\s+logo|douyin\s+logo\s+watermark|twitch\s+purple\s+glitch\s+logo|youtube\s+official\s+logo|official\s+roblox\s+(?:tilted[- ]square|\[r\]|logo))\b|(?:官方抖音台标|抖音Logo水印|快手官方水印|Twitch官方图标|官方Roblox倾斜方框商标|Roblox官方R标)/i;
  const engineValid = VALID_ENGINES.has(engine);

  if (brandLeakRe.test(posText) || !engineValid) {
    checks.push({
      gate: "8. Brand Watermark & Engine Guard / 平台商标净空与引擎校验",
      status: "FAIL",
      detailEn: !engineValid
        ? `Unsupported video engine '${engine}'. Use: ${Array.from(VALID_ENGINES).join(", ")}.`
        : "Detected official platform/brand logo or watermark in positive prompt.",
      detailZh: !engineValid
        ? `不支持的目标视频引擎「${engine}」。可选：${Array.from(VALID_ENGINES).join(", ")}。`
        : "正向提示词混入官方直播平台台标或品牌商标描述。"
    });
    if (!engineValid) detectedIssues.add("cinematic-drift");
    else detectedIssues.add("watermark-leak");
  } else {
    checks.push({
      gate: "8. Brand Watermark & Engine Guard / 平台商标净空与引擎校验",
      status: "PASS",
      detailEn: `Brand-clean prompt verified for engine '${engine}'.`,
      detailZh: `无官方平台台标污染，目标引擎「${engine}」语法兼容。`
    });
  }

  const hasFail = checks.some((c) => c.status === "FAIL");
  const hasWarn = checks.some((c) => c.status === "WARN");
  const overallStatus = hasFail ? "FAIL" : hasWarn ? "WARN" : "PASS";

  // Build rescued prompt suggestion when issues exist
  const styleAdapter = STYLE_ADAPTERS[styleId] || STYLE_ADAPTERS["realistic-irl"];
  const defaultRig = RIG_PROFILES[rigHint] || RIG_PROFILES["desktop-webcam"];
  const patches = Array.from(detectedIssues).map((code) => ({
    code,
    ...(ISSUE_PATCHES[code] || ISSUE_PATCHES["cinematic-drift"])
  }));

  const rescuedPromptEn =
    overallStatus === "PASS"
      ? rawPrompt
      : [
          `[9:16 Livestream Clean Plate · ${defaultRig.labelEn}]`,
          `${defaultRig.lensEn}.`,
          `${styleAdapter.geometryLockEn}.`,
          `Subject addresses the 0° live lens directly, glances 15° off-axis at the chat monitor, and performs ONE crisp action within the locked camera rig.`,
          `Clean raw camera feed, zero burned-in UI text, zero platform watermarks.`
        ].join(" ");

  const rescuedPromptZh =
    overallStatus === "PASS"
      ? rawPrompt
      : [
          `【9:16 直播视角纯净底片 · ${defaultRig.labelZh}】`,
          `${defaultRig.lensZh}。`,
          `${styleAdapter.geometryLockZh}。`,
          `主播0°直视镜头互动并自然偏轴15°瞥一眼副屏弹幕，在连续物理机位内仅执行1个干净利落的核心动作。`,
          `100%纯净无UI文字底片，严禁乱码弹幕与平台水印。`
        ].join("");

  return {
    overallStatus,
    engine,
    mode,
    styleId,
    rigHint: rigHint || "auto",
    checks,
    patches,
    rescuedPromptEn,
    rescuedPromptZh,
    negativePromptEn: `${styleAdapter.antiDriftNegativeEn}, floating omniscient crane shot, burned-in gibberish chat text, official platform watermarks`,
    negativePromptZh: `${styleAdapter.antiDriftNegativeZh}，上帝视角电影摇臂，AI直出乱码弹幕，官方平台台标水印`
  };
}

export function inspectPackageFile(filePath, options = {}) {
  const abs = path.resolve(filePath);
  const raw = JSON.parse(fs.readFileSync(abs, "utf8").replace(/^\uFEFF/, ""));
  const shots = Array.isArray(raw.shots) ? raw.shots : [];
  const engine = options.engine || raw.engine || "local3d";
  const style = options.style || raw.style || "realistic-irl";
  const rig = options.rig || raw.rig || "desktop-webcam";
  const mode = options.mode || (engine === "local3d" ? "local3d" : "i2v");

  const shotReports = shots.map((sh, idx) => {
    const promptCandidate =
      sh.i2vPromptEn ||
      sh.cleanPlatePromptEn ||
      [
        `9:16 ${rig} livestream camera (${RIG_PROFILES[rig]?.lensEn || "webcam lens"}):`,
        STYLE_ADAPTERS[style]?.geometryLockEn || "",
        sh.actionEn || "",
        sh.eyeLineEn || "direct 0-degree lens eye-contact and 15-degree chat-monitor glance",
        sh.cameraEn || "",
        "clean raw camera feed, zero burned-in UI text"
      ].join(" ");
    const rep = inspectPrompt({
      prompt: promptCandidate,
      engine,
      mode,
      style: sh.style || style,
      rig: sh.rig || rig
    });
    return {
      shotIndex: idx + 1,
      role: sh.role || `Shot ${idx + 1}`,
      actionKey: (sh.actionEn || sh.i2vPromptEn || "").trim().toLowerCase(),
      ...rep
    };
  });

  const uniqueActionCount = new Set(shotReports.map((r) => r.actionKey).filter(Boolean)).size;
  const duplicateShots = shots.length > 0 && uniqueActionCount < shots.length;
  const anyFail = shotReports.some((r) => r.overallStatus === "FAIL") || duplicateShots;
  const anyWarn = shotReports.some((r) => r.overallStatus === "WARN");

  return {
    file: abs,
    shotCount: shots.length,
    uniqueActionCount,
    duplicateShots,
    overallStatus: anyFail ? "FAIL" : anyWarn ? "WARN" : "PASS",
    shotReports
  };
}

export function formatDriftCheckMarkdown(report, lang = "en") {
  const code = normalizeLang(lang);
  const includeZh = code === "zh" || code === "zh-tw" || code === "zh-en";

  if (Array.isArray(report.shotReports)) {
    const lines = [
      `<!-- lang: ${code} | status: ${report.overallStatus} -->`,
      `# Livestream POV Package Audit (${report.overallStatus})`,
      "",
      `- **Shots Audited**: \`${report.shotCount}\` (Unique Beats: \`${report.uniqueActionCount}\`${report.duplicateShots ? " — DUPLICATE DETECTED!" : ""})`,
      "",
      "| Shot | Role | Status | Failed / Warned Gates |",
      "| :---: | --- | :---: | --- |"
    ];
    for (const sr of report.shotReports) {
      const nonPass = sr.checks.filter((c) => c.status !== "PASS").map((c) => `${c.status}: ${c.gate}`).join("; ") || "All 8 gates PASS";
      lines.push(`| ${String(sr.shotIndex).padStart(2, "0")} | ${sr.role} | **${sr.overallStatus}** | ${nonPass} |`);
    }
    lines.push("");
    return lines.join("\n");
  }

  const lines = [
    `<!-- lang: ${code} | status: ${report.overallStatus} | style: ${report.styleId} -->`,
    `# Livestream POV 8-Gate Anti-Drift Report: **${report.overallStatus}**`,
    "",
    `- **Engine**: \`${report.engine}\` · **Mode**: \`${report.mode}\` · **Style Lock**: \`${report.styleId}\``,
    "",
    "| Gate | Status | Diagnostic |",
    "| --- | :---: | --- |"
  ];

  for (const c of report.checks) {
    lines.push(`| ${c.gate} | **${c.status}** | ${includeZh ? `${c.detailZh}<br>${c.detailEn}` : c.detailEn} |`);
  }

  if (report.patches.length > 0) {
    lines.push("", "## Recommended Rescue Patches / 修复补丁", "");
    for (const p of report.patches) {
      lines.push(`- **\`${p.code}\` (${includeZh ? p.titleZh : p.titleEn})**: ${includeZh ? p.fixZh : p.fixEn}`);
    }
    lines.push(
      "",
      "## Rescued Clean-Plate Prompt / 修补后提示词",
      "",
      "```text",
      includeZh ? `${report.rescuedPromptZh}\n\n${report.rescuedPromptEn}` : report.rescuedPromptEn,
      "```",
      "",
      "- **Negative**: `" + (includeZh ? report.negativePromptZh : report.negativePromptEn) + "`"
    );
  }
  lines.push("");
  return lines.join("\n");
}

function parseArgs(argv) {
  const opts = {
    prompt: "",
    pack: "",
    engine: "kling",
    style: "",
    rig: "",
    mode: "i2v",
    issue: "",
    lang: "en",
    out: "",
    json: false,
    help: false
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") opts.help = true;
    else if (a === "--json") opts.json = true;
    else if (a === "--prompt" && argv[i + 1]) opts.prompt = argv[++i];
    else if ((a === "--pack" || a === "--spec") && argv[i + 1]) opts.pack = argv[++i];
    else if (a === "--engine" && argv[i + 1]) opts.engine = argv[++i].toLowerCase().trim();
    else if (a === "--style" && argv[i + 1]) opts.style = argv[++i].toLowerCase().trim();
    else if (a === "--rig" && argv[i + 1]) opts.rig = argv[++i].toLowerCase().trim();
    else if (a === "--mode" && argv[i + 1]) opts.mode = argv[++i].toLowerCase().trim();
    else if (a === "--issue" && argv[i + 1]) opts.issue = argv[++i].toLowerCase().trim();
    else if (a === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
    else if (a === "--out" && argv[i + 1]) opts.out = argv[++i];
  }
  return opts;
}

function printHelp() {
  console.log(`Usage:
  node scripts/drift_check.mjs --prompt "<prompt text>" [options]
  node scripts/drift_check.mjs --pack <prompts.json | episode.json> [options]

Run 8-gate deterministic PASS/WARN/FAIL checks on a Livestream POV video prompt or full episode package.

Options:
  --prompt <text>    Draft prompt to inspect
  --pack <file>      Inspect all shots inside a compiled prompts.json or custom episode spec JSON
  --engine <id>      Target engine: local3d | kling | seedance | hailuo | wan | sora | veo | runway
  --style <id>       Optional style lock: realistic-irl | roblox-blocky | anime-vtuber | stylized-3d | voxel-sandbox | cinematic-genre-adapt
  --rig <id>         Optional rig hint: desktop-webcam | handheld-selfie-irl | pip-facecam-rig | overhead-showcase-rig | chest-head-pov | pk-cohost-split | cctv-obs-fixed | drone-follow-live
  --mode <id>        Workflow mode: i2v | t2v | local3d (default: i2v)
  --issue <code>     Optional observed failure code: ${Object.keys(ISSUE_PATCHES).join(" | ")}
  --lang <code>      Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en
  --out <path>       Write UTF-8 report directly to file
  --json             Output structured JSON
  --help             Show this help message`);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("drift_check.mjs");
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || (!opts.prompt && !opts.pack)) {
    printHelp();
    process.exit(opts.help ? 0 : 1);
  }
  const report = opts.pack ? inspectPackageFile(opts.pack, opts) : inspectPrompt(opts);
  const outText = opts.json ? JSON.stringify(report, null, 2) + "\n" : formatDriftCheckMarkdown(report, opts.lang);
  if (opts.out) {
    const abs = path.resolve(opts.out);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, outText, "utf8");
    console.log(`Wrote drift report (${report.overallStatus}) to ${abs}`);
  } else {
    process.stdout.write(outText);
  }
}
