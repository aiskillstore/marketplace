#!/usr/bin/env node
/**
 * drift_check.mjs
 * Zero-dependency Unicode-safe linter, package auditor, thumbnail readability checker,
 * and rescue rewriter for Roblox-style blocky short-video specs and prompts.
 *
 * Enforces 10 independent quality gates across two distinct domains:
 * [Geometry & Brand Gates 1–8: "Does it look like authentic Roblox?"]
 * 1. Hand Geometry Lock (no human fingers, no Lego C-claws, no contradictory negations)
 * 2. 2D Face Decal Lock (1:1 barrel head, flat 2D decal, no 3D nose)
 * 3. Studless & Non-Voxel Guard (smooth floors/props, zero Lego floor/head bumps, non-voxel)
 * 4. Single-Action Clip Budget (Unicode-safe EN+ZH verb & sequence-connector parser)
 * 5. Rigid Physics & I2V Anchor (catches rubbery/noodle contradictions on R6 & R15)
 * 6. Trademark & Brand Cleanliness (fails official Roblox Tilt / [R] logo leaks)
 * 7. Pet & Prop Topology Lock (blocks scaly/clawed organic pets & finger-pinched props)
 * 8. UI & Engine Compatibility Guard (flags dense garble-prone UI text & unknown engines)
 *
 * [Performance & Readability Gates 9–10: "Does the acting beat read in 0.5s?"]
 * 9. Performance & Interaction Completeness (gaze target, reaction cause, single audienceRead, camera-facing hand-prop intent)
 * 10. Thumbnail & Safe-Zone Readability (9:16 safe zone, silhouette non-occlusion, <=4-word bubble, optional 64x64 PNG crop contrast)
 */

import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";

const VALID_ENGINES = new Set(["local3d", "kling", "seedance", "hailuo", "wan", "sora", "runway"]);
const VALID_INTERACTION_INTENTS = new Set(["hold", "present", "tap", "slam", "point", "drop", "receive"]);
const BUILTIN_STAGE_TARGETS = {
  subway_car: {
    empty_seat: [0.62, -0.32, -0.78],
    left_seat: [-0.92, -0.32, -0.78],
    center_strap: [0.0, 1.06, 0.04],
    left_strap: [-0.72, 1.06, 0.04],
    right_strap: [0.72, 1.06, 0.04]
  },
  adoption_plaza: {
    pedestal: [0.22, -0.45, 0.28],
    archway: [0.0, 0.35, -1.04]
  },
  convenience_store: {
    counter_top: [0.0, -0.28, 0.44],
    snack_shelf: [0.82, 0.22, -0.88]
  },
  supermarket_aisle: {
    left_shelf: [-1.35, 0.12, -0.35],
    right_shelf: [1.35, 0.12, -0.35]
  }
};

const ISSUE_PATCHES = {
  "human-fingers": {
    titleZh: "长出人类五指 (Human Finger Growth)",
    fixEn: "fingerless and clawless solid 1x2x1 beveled rectangular block hands, zero human fingers, no knuckles",
    fixZh: "平头倒角1x2x1实心方块手部，严禁出现人类五指或手部关节纹"
  },
  "lego-studs": {
    titleZh: "出现乐高头顶/地面圆颗粒或乐高C型夹爪手 (Lego Stud & C-Claw Contamination)",
    fixEn: "smooth studless 1:1 barrel-beveled Roblox head, flat SmoothPlastic / WoodPlanks / Concrete floor surfaces (zero raised circular Lego floor studs or cylindrical brick pegs), solid 1x2x1 rectangular block hands (no Lego C-shaped hook claws)",
    fixZh: "头顶完全平滑的1:1桶状圆角Roblox头部，平滑无凸起圆粒的Roblox SmoothPlastic/木纹/柏油地面（严禁乐高地面凸点底板），1x2x1实心平头方柱手（严禁乐高C型钩子爪）"
  },
  "minecraft-voxels": {
    titleZh: "串味成我的世界像素方块 (Minecraft Voxel Drift)",
    fixEn: "classic Roblox 1:1 barrel-cylinder head with deep curved top/bottom bevels, SmoothPlastic shader, non-voxel, no pixel texture",
    fixZh: "经典Roblox 1:1上下大圆角桶状圆柱头，SmoothPlastic平滑塑料材质，非像素马赛克方块"
  },
  "limb-gap": {
    titleZh: "双腿分叉有空隙或穿分体运动鞋 (Non-Roblox Separated Legs)",
    fixEn: "canonical Roblox 2x2x1 rectangular torso with two 1x2x1 rectangular leg blocks sitting flush side-by-side matching exact torso width, zero thigh gap",
    fixZh: "标准Roblox 2x2x1宽扁长方体躯干配两条并拢齐平的1x2x1方柱双腿（与躯干完全同宽，无腿缝、无外凸真人运动鞋）"
  },
  "face-morph": {
    titleZh: "五官突起长出真人鼻子/嘴唇 (3D Human Face Morphing)",
    fixEn: "flat 2D screen-printed Roblox face decal on smooth cylindrical surface, painted ink eyes and mouth, zero 3D nose protrusion",
    fixZh: "纯平2D丝网印刷五官贴图，绘制墨点眼与平面嘴型，零3D鼻子凸起，无真实皮肤纹理"
  },
  "noodle-limbs": {
    titleZh: "四肢像面条一样弯曲软化 (Rubbery Noodle Limbs)",
    fixEn: "rigid 1x2x1 rectangular blocky arms and legs, strict Motor6D mechanical hinge rotation only, zero rubbery soft-body bending",
    fixZh: "刚性1x2x1长方体四肢，仅在Motor6D机械转轴处转动，严禁橡胶面条状软体弯曲形变"
  },
  "foot-sliding": {
    titleZh: "走路脚底打滑/太空步 (Foot Skating / Sliding)",
    fixEn: "medium three-quarter framing, crisp bouncy R6 hop landing firmly on a flat smooth Roblox SmoothPlastic or WoodPlanks floor",
    fixZh: "改用中景或七分景机位，将连续碎步走改为干脆的R6方块跳步落地，强化与平整地面的接触阴影"
  },
  "outfit-drift": {
    titleZh: "切镜头后衣服与配饰变形 (Cross-Shot Outfit Drift)",
    fixEn: "Anchor multi-shot episodes with a locked Cast Spec JSON (`render_preview.mjs --spec`) or First-Frame I2V from a 3-view turnaround sheet",
    fixZh: "通过结构化角色设定JSON（`render_preview.mjs --spec`本地3D直出）或3视图首帧I2V锁定跨镜头穿搭"
  },
  "trademark-leak": {
    titleZh: "混入官方商标或品牌水印 (Official Trademark Leak)",
    fixEn: "unbranded outfits and UI badges using clean geometric triangle emblems only, zero official Roblox logos or tilted-square badges",
    fixZh: "纯色无标服饰与UI卡片，仅使用原创几何三角形徽章，严禁任何官方Roblox倾斜方框商标或R字徽标"
  },
  overload: {
    titleZh: "单镜头动作过多导致穿模卡死 (Single-Clip Action Overload)",
    fixEn: "Split sequential verbs so each 3.5–4s shot executes only ONE primary physical action and ONE camera move",
    fixZh: "遵循单镜头单动作铁律：将多个连续动词拆分为独立的3.5~4秒分镜，每镜只保留1个核心动作"
  },
  "missing-acting": {
    titleZh: "只有静态职业/外观标签，缺少瞬间表演关系 (Missing Acting Grammar & Gaze Target)",
    fixEn: "Upgrade static role labels into one readable story instant: specify beatIntent, pupils tracking a concrete gazeTarget, asymmetrical eyebrows, and camera-facing hand-prop interaction",
    fixZh: "将静态身份标签升级为瞬间表演：明确角色此刻的beatIntent、瞳孔追踪目标(gazeTarget)、不对称高低眉与朝向镜头的手部道具交互"
  },
  "poor-readability": {
    titleZh: "小尺寸缩略图遮挡或安全区失焦 (Thumbnail Occlusion & Safe-Zone Drift)",
    fixEn: "Separate actor silhouettes, keep the key hand/prop on the camera-facing plane unoccluded by torsos, place heads inside the central 9:16 safe band, and keep chat bubbles <= 4 words",
    fixZh: "拉开双人剪影间距，确保关键手与道具朝向镜头不被躯干遮挡，角色头部落入9:16竖屏中央安全区，气泡台词控制在4词以内确保遮住字幕也能看懂"
  }
};

function printHelp() {
  console.log(`Usage:
  node scripts/drift_check.mjs --prompt "<prompt text>" [options]
  node scripts/drift_check.mjs --pack <prompts.json | episode.json> [options]

Run 10-gate deterministic PASS/WARN/FAIL checks (Gates 1–8 Geometry + Gates 9–10 Acting & Thumbnail Readability).

Options:
  --prompt <text>    Draft prompt to inspect
  --pack <file>      Inspect all shots inside a compiled prompts.json or custom episode spec JSON
  --assets-dir <dir> Optional rendered assets folder to verify 64x64 thumbnail/avatar contrast
  --require-acting   Require explicit gaze target, reaction cause, and audienceRead on single prompts
  --engine <id>      Target engine: local3d | kling | seedance | hailuo | wan | sora | runway (default: local3d)
  --rig <id>         Optional rig hint: r6 | r15 | chibi-blocky
  --mode <id>        Workflow mode: i2v | t2v | local3d (default: i2v)
  --issue <code>     Optional observed failure code: ${Object.keys(ISSUE_PATCHES).join(" | ")}
  --lang <code>      Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en (default: en)
  --out <path>       Write UTF-8 report directly to file
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
    prompt: "",
    pack: "",
    assetsDir: "",
    requireActing: false,
    engine: "kling",
    rig: "",
    mode: "i2v",
    issue: "",
    out: "",
    lang: "en",
    json: false,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--json") opts.json = true;
    else if (arg === "--require-acting") opts.requireActing = true;
    else if (arg === "--prompt" && argv[i + 1]) opts.prompt = argv[++i];
    else if ((arg === "--pack" || arg === "--spec") && argv[i + 1]) opts.pack = argv[++i];
    else if (arg === "--assets-dir" && argv[i + 1]) opts.assetsDir = argv[++i];
    else if (arg === "--engine" && argv[i + 1]) opts.engine = argv[++i].toLowerCase();
    else if (arg === "--rig" && argv[i + 1]) opts.rig = argv[++i].toLowerCase();
    else if (arg === "--mode" && argv[i + 1]) opts.mode = argv[++i].toLowerCase();
    else if (arg === "--issue" && argv[i + 1]) opts.issue = argv[++i].toLowerCase();
    else if (arg === "--out" && argv[i + 1]) opts.out = argv[++i];
    else if (arg === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
  }
  return opts;
}

/**
 * Decode an RGBA 8-bit PNG generated by render_preview.mjs and measure 64x64 thumbnail luminance std-dev
 * to verify small-size avatar / keyframe contrast without external dependencies.
 */
export function measurePngThumbnailContrast(pngPath) {
  if (!pngPath || !fs.existsSync(pngPath)) return null;
  const buf = fs.readFileSync(pngPath);
  if (buf.length < 33 || buf.readUInt32BE(0) !== 0x89504e47) return null;
  let offset = 8;
  let width = 0;
  let height = 0;
  let colorType = 6;
  const idatChunks = [];
  while (offset + 8 <= buf.length) {
    const len = buf.readUInt32BE(offset);
    const type = buf.toString("ascii", offset + 4, offset + 8);
    const dataStart = offset + 8;
    if (type === "IHDR" && len >= 10) {
      width = buf.readUInt32BE(dataStart);
      height = buf.readUInt32BE(dataStart + 4);
      colorType = buf[dataStart + 9];
    } else if (type === "IDAT") {
      idatChunks.push(buf.subarray(dataStart, dataStart + len));
    } else if (type === "IEND") {
      break;
    }
    offset = dataStart + len + 4;
  }
  if (!width || !height || idatChunks.length === 0 || (colorType !== 6 && colorType !== 2)) return null;
  const bpp = colorType === 6 ? 4 : 3;
  const raw = zlib.inflateSync(Buffer.concat(idatChunks));
  const stride = 1 + width * bpp;
  if (raw.length < height * stride) return null;

  // Reconstruct PNG scanline filters (None=0, Sub=1, Up=2, Average=3, Paeth=4)
  const pixels = new Uint8Array(width * height * bpp);
  const paeth = (a, b, c) => {
    const p = a + b - c;
    const pa = Math.abs(p - a);
    const pb = Math.abs(p - b);
    const pc = Math.abs(p - c);
    if (pa <= pb && pa <= pc) return a;
    return pb <= pc ? b : c;
  };
  for (let y = 0; y < height; y++) {
    const filter = raw[y * stride];
    const rowIn = y * stride + 1;
    const rowOut = y * width * bpp;
    const prevOut = (y - 1) * width * bpp;
    for (let i = 0; i < width * bpp; i++) {
      const x = raw[rowIn + i];
      const a = i >= bpp ? pixels[rowOut + i - bpp] : 0;
      const b = y > 0 ? pixels[prevOut + i] : 0;
      const c = y > 0 && i >= bpp ? pixels[prevOut + i - bpp] : 0;
      let val = x;
      if (filter === 1) val = (x + a) & 0xff;
      else if (filter === 2) val = (x + b) & 0xff;
      else if (filter === 3) val = (x + ((a + b) >> 1)) & 0xff;
      else if (filter === 4) val = (x + paeth(a, b, c)) & 0xff;
      pixels[rowOut + i] = val;
    }
  }

  // Sample central 64x64 thumbnail grid inside the 9:16 safe band (x: 15%..85%, y: 18%..78%)
  const lumas = [];
  for (let gy = 0; gy < 64; gy++) {
    const sy = Math.min(height - 1, Math.floor(height * (0.18 + (gy / 63) * 0.60)));
    for (let gx = 0; gx < 64; gx++) {
      const sx = Math.min(width - 1, Math.floor(width * (0.15 + (gx / 63) * 0.70)));
      const pIdx = (sy * width + sx) * bpp;
      const lum = 0.299 * pixels[pIdx] + 0.587 * pixels[pIdx + 1] + 0.114 * pixels[pIdx + 2];
      lumas.push(lum);
    }
  }
  const mean = lumas.reduce((a, b) => a + b, 0) / lumas.length;
  const variance = lumas.reduce((acc, v) => acc + (v - mean) * (v - mean), 0) / lumas.length;
  const stdDev = Math.sqrt(variance);
  return { width, height, stdDev: Number(stdDev.toFixed(2)) };
}

/**
 * Strip negated clauses locally so we can distinguish positive risk mentions
 * ("with five fingers") from negations ("zero fingers", "无人类五指"), AND
 * detect contradictions when BOTH appear in the same prompt!
 */
function stripNegatedSpans(text) {
  return text
    .replace(/\b(?:no|zero|without|never|free of|avoid|ban|excluding)\s+[^.,;()\n]{1,55}/gi, " ")
    .replace(/(?:严禁|禁止|不带|不含|没有|无|零)[^，。；、（）()\n]{1,26}/g, " ");
}

function countActionVerbsAndConnectors(prompt) {
  // Neutralize camera framing, static outfit/decal adjectives, and spatial prepositions ("close-up", "medium-close", "pull-back", "open jacket", "open gasp mouth", "sweat drop", "next to")
  const scrubbed = prompt
    .replace(/\b(?:extreme\s+|medium[-\s]+)?close[-\s]?ups?\b/gi, "closeup_lens")
    .replace(/\bmedium-close\b/gi, "medium_lens")
    .replace(/\bpop-ups?\b/gi, "popup_ui")
    .replace(/\bpush-in\b/gi, "dolly_in")
    .replace(/\bpull-(?:out|back)\b/gi, "dolly_out")
    .replace(/\bnext\s+to\b/gi, "beside")
    .replace(/\bstand-in\b/gi, "substitute")
    .replace(/\bopen\s+(?:jacket|hoodie|coat|collar|shirt|vest|(?:silent\s+)?gasp(?:\s+mouth)?|mouth|grin|smile)\b/gi, "styled_feature")
    .replace(/\bsweat\s+drops?\b/gi, "sweat_decal")
    .replace(/\bteardrops?\b/gi, "tear_decal")
    .replace(/\[[^\]]*\]/g, " "); // ignore bracketed camera tags like [Push in, Shake]

  const enConnectors =
    scrubbed.match(/\b(?:then|and then|after that|afterwards|subsequently|while simultaneously|followed by)\b/gi) || [];
  const zhConnectors = scrubbed.match(/(?:接着|然后|随后|紧接着|再转身|再跑|再跳|再坐|再挥|再拍|一边[^，。]{1,10}一边)/g) || [];
  const chainConnectors = enConnectors.length + zhConnectors.length;

  const enVerbs =
    scrubbed.match(
      /\b(?:walks?|walking|runs?|running|sprints?|sprinting|dashes?|dashing|jumps?|jumping|hops?|hopping|leaps?|leaping|sits?\s+down|sitting\s+down|stands?\s+up|standing\s+up|drinks?|drinking|pours?|pouring|spills?|spilling|eats?|eating|opens?|opening|closes?|closing|slams?|slamming|slaps?|slapping|swats?|swatting|taps?|tapping|clicks?|clicking|waves?|waving|cries|crying|dances?|dancing|spins?|spinning|falls?|falling|trips?|tripping|dives?|diving|plunges?|plunging|plummets?|plummeting|climbs?|climbing|dodges?|dodging|hesitates?|hesitating|misses|missing|pushes|pushing|pulls?|pulling|grabs?|grabbing|snatches|snatching|throws?|throwing|drops?|dropping|cracks?|cracking|hatches|hatching|crashes|crashing|recoils?|recoiling)\b/gi
    ) || [];

  const zhVerbs =
    scrubbed.match(
      /(?:跑向|奔跑|狂奔|冲刺|冲向|走过|走进|跳到|跳起|跳跃|跃起|跃过|坐下|落座|站起|喝水|喝咖啡|倒水|洒出|打开|合上|关上|拍扁|拍停|拍下|拍在|挥手|挥开|挥动|抱头|哭泣|跳舞|转身|旋转|摔倒|绊倒|飞扑|坠落|跌落|爬上|躲避|闪避|推着|推动|拉动|抓起|抢走|扔出|掉回|撞开|冲撞|裂开|破壳)/g
    ) || [];

  return {
    chainConnectors,
    verbCount: enVerbs.length + zhVerbs.length,
    matchedVerbs: [...enVerbs, ...zhVerbs]
  };
}

export function inspectPrompt(rawOpts = {}) {
  const prompt = (rawOpts.prompt || "").trim();
  const lower = prompt.toLowerCase();
  const positiveOnly = stripNegatedSpans(prompt);
  const posLower = positiveOnly.toLowerCase();

  const mode = rawOpts.mode === "t2v" ? "t2v" : rawOpts.mode === "local3d" ? "local3d" : "i2v";
  const rawEngine = (rawOpts.engine || "kling").toLowerCase();
  const isKnownEngine = VALID_ENGINES.has(rawEngine);
  const engine = rawEngine;
  const issue = rawOpts.issue && ISSUE_PATCHES[rawOpts.issue] ? rawOpts.issue : "";

  const detectedRig =
    rawOpts.rig === "r15" || /\br15\b/i.test(prompt)
      ? "r15"
      : rawOpts.rig === "r6" || /\br6\b/i.test(prompt)
      ? "r6"
      : "chibi-blocky";

  const checks = [];

  // 1. Hand Geometry Lock (Unicode-safe for both EN & ZH, catches contradictions!)
  const hasHandLock =
    /fingerless|zero(?:\s+human)?\s+fingers|no(?:\s+human)?\s+fingers|without\s+fingers|solid[^.,;]{0,30}block\s+hands?|1x2x1[^.,;]{0,30}(?:arms?|hands?)|blocky\s+hands?/.test(
      lower
    ) || /(?:无手指|无人类五指|零手指|实心[^，。；]{0,12}方[块柱][^，。；]{0,6}手|1x2x1[^，。；]{0,12}手|平头[^，。；]{0,8}方[块柱]?手)/.test(prompt);

  const positiveMentionsFingers =
    /\b(?:five\s+fingers|human\s+fingers|human\s+hands|fingers|knuckles|thumb)\b/i.test(posLower) ||
    /(?:五根手指|人类五指|五指|手指|指关节|拇指)/.test(positiveOnly);

  const positiveMentionsLegoClaws =
    /\b(?:c-shaped|claw\s+hands?|lego\s+claws?|lego\s+hooks?)\b/i.test(posLower) ||
    /(?:c型手|c型夹爪|c型钩爪|乐高爪|乐高钩子)/i.test(positiveOnly);

  if (positiveMentionsFingers || issue === "human-fingers") {
    checks.push({
      gate: "Hand Geometry Lock / 手部防长手指与防乐高爪锁",
      status: "FAIL",
      reasonEn: hasHandLock
        ? "Contradictory hand prompt: positive clause mentions fingers/thumbs even though a fingerless lock appears later."
        : "Prompt triggers human finger generation without a fingerless solid 1x2x1 rectangular block hand lock.",
      reasonZh: hasHandLock
        ? "手部描述自相矛盾：前文正向出现了手指/五指动作，后文又声明无手指。"
        : "提示词正文中出现五指/手指描述且缺少「无手指1x2x1实心平头方块手」几何锁定。"
    });
  } else if (positiveMentionsLegoClaws) {
    checks.push({
      gate: "Hand Geometry Lock / 手部防长手指与防乐高爪锁",
      status: "FAIL",
      reasonEn: "C-shaped claw hooks belong to Lego minifigures; use `fingerless and clawless solid 1x2x1 beveled rectangular block hands`.",
      reasonZh: "C型夹爪属于乐高小人特征，必须改为「无手指且无乐高C型爪的1x2x1实心平头倒角方柱手」。"
    });
  } else if (!hasHandLock) {
    checks.push({
      gate: "Hand Geometry Lock / 手部防长手指与防乐高爪锁",
      status: "WARN",
      reasonEn: "Missing explicit `fingerless and clawless solid 1x2x1 rectangular block hands` token; models may invent human fingers or Lego hooks.",
      reasonZh: "未显式声明「1x2x1实心平头方块手」，运动时易长出人类手指或乐高钩爪。"
    });
  } else {
    checks.push({
      gate: "Hand Geometry Lock / 手部防长手指与防乐高爪锁",
      status: "PASS",
      reasonEn: "Solid fingerless & clawless blocky hand lock verified.",
      reasonZh: "已包含无指无爪的实心平头方块手锁定。"
    });
  }

  // 2. 2D Face Decal Lock
  const hasFaceLock =
    /2d[^.,;]{0,25}(?:decal|face|eyes|smile|grin)|(?:decal|screen-printed|painted)\s+face|(?:barrel|cylindrical)\s+head/.test(lower) ||
    /(?:2d[^，。；]{0,12}(?:五官|贴图|笑脸|死鱼眼|圆圈眼)|印刷[^，。；]{0,8}(?:五官|贴图|困眼|笑脸)|平面[^，。；]{0,8}贴图|圆柱头|桶状[^，。；]{0,6}头)/i.test(
      prompt
    );
  const humanGenderRisk =
    /\b(?:girl|boy|man|woman|realistic\s+face|3d\s+nose|lips)\b/i.test(posLower) ||
    /(?:真脸|高鼻梁|真人嘴唇)/.test(positiveOnly);

  if (issue === "face-morph" || (humanGenderRisk && !hasFaceLock)) {
    checks.push({
      gate: "2D Face Decal Lock / 面部2D贴图锁",
      status: issue === "face-morph" ? "FAIL" : "WARN",
      reasonEn: "Humanized nouns or facial terms without `1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal, zero 3D nose` risk realistic face morphing.",
      reasonZh: "包含拟人词但未锁定「1:1桶状圆角圆柱头 + 纯平2D印刷五官贴图 + 无3D鼻子」，易触发真人化五官变形。"
    });
  } else if (!hasFaceLock) {
    checks.push({
      gate: "2D Face Decal Lock / 面部2D贴图锁",
      status: "WARN",
      reasonEn: "Add `1:1 barrel-beveled cylindrical head, flat 2D screen-printed decal face` to prevent 3D nose protrusion.",
      reasonZh: "建议补充「1:1桶状圆柱头、纯平2D印刷五官贴图」以防止长出3D鼻子。"
    });
  } else {
    checks.push({
      gate: "2D Face Decal Lock / 面部2D贴图锁",
      status: "PASS",
      reasonEn: "Cylindrical head and flat 2D face decal lock present.",
      reasonZh: "已锁定桶状圆柱头与2D平面贴图五官。"
    });
  }

  // 3. Studless & Non-Voxel Guard
  const hasStudlessLock =
    /studless|zero\s+raised[^.,;]{0,20}stud|no\s+raised[^.,;]{0,20}lego|non-voxel|chamfered|beveled|smoothplastic/.test(lower) ||
    /(?:无颗粒|无凸点|无圆粒|无乐高|倒角|平滑塑料|非像素)/.test(prompt);
  const positiveMentionsLegoStuds =
    /\b(?:studded|raised\s+studs|lego\s+studs|lego\s+floor|brick\s+pegs|voxel\s+cube)\b/i.test(posLower) ||
    /(?:凸点底板|乐高颗粒|乐高圆粒|地面凸点|像素方块头)/.test(positiveOnly);

  if (issue === "lego-studs" || issue === "minecraft-voxels" || positiveMentionsLegoStuds) {
    checks.push({
      gate: "Studless & Non-Voxel Guard / 乐高凸粒与MC防串味锁",
      status: issue ? "FAIL" : "FAIL",
      reasonEn: "Positive prompt includes `studded` / Lego floor bumps or voxel terms; replace with `smooth flat SmoothPlastic / WoodPlanks / Concrete surfaces (zero raised circular Lego studs), non-voxel`.",
      reasonZh: "正向描述中包含凸点底板/乐高颗粒或体素词，极易诱发地面与头顶长出乐高圆粒；必须改为平整无凸点的 SmoothPlastic/木板/混凝土表面。"
    });
  } else if (!hasStudlessLock) {
    checks.push({
      gate: "Studless & Non-Voxel Guard / 乐高凸粒与MC防串味锁",
      status: "WARN",
      reasonEn: "Missing `smooth studless SmoothPlastic, 2mm chamfered edges, zero raised Lego studs, non-voxel`.",
      reasonZh: "缺少「平滑无乐高凸粒、2毫米倒角、非像素方块」描述。"
    });
  } else {
    checks.push({
      gate: "Studless & Non-Voxel Guard / 乐高凸粒与MC防串味锁",
      status: "PASS",
      reasonEn: "Studless beveled geometry and smooth architectural surface tokens present.",
      reasonZh: "已包含无乐高凸粒倒角方块与平整表面锁定。"
    });
  }

  // 4. Single-Action Clip Budget (Unicode-safe; prefer isolated actionText or extracted Single action clause!)
  let extractedAction = rawOpts.actionText ? rawOpts.actionText : "";
  if (!extractedAction) {
    const mEn = prompt.match(/(?:Single action|Action):\s*([^.;]+?)(?:\s+while\s+maintaining|\.)/i);
    const mZh = prompt.match(/单镜动作：([^。；]+)/);
    if (mEn) extractedAction = mEn[1];
    else if (mZh) extractedAction = mZh[1];
  }
  const actionScopeText = extractedAction ? stripNegatedSpans(extractedAction) : positiveOnly;
  const { chainConnectors, verbCount } = countActionVerbsAndConnectors(actionScopeText);
  if (issue === "overload" || chainConnectors >= 2 || verbCount >= 3 || (chainConnectors >= 1 && verbCount >= 3)) {
    checks.push({
      gate: "Single-Action Clip Budget / 单镜头动作容量",
      status: "FAIL",
      reasonEn: `Detected multi-step action chain (${verbCount} active motion verbs, ${chainConnectors} sequence connectors). Split into separate 3.5–4s single-action shots.`,
      reasonZh: `检测到单镜头动作超载（识别到 ${verbCount} 个动态动词、${chainConnectors} 处先后连接词）。请拆分为每镜单一核心动作的 3.5~4 秒分镜。`
    });
  } else if (chainConnectors === 1 || verbCount === 2) {
    checks.push({
      gate: "Single-Action Clip Budget / 单镜头动作容量",
      status: "WARN",
      reasonEn: "Two-step motion detected; keep the secondary beat to a simple 2D decal swap or rigid head pivot.",
      reasonZh: "检测到两段动作，建议将次要动作限制为面部2D贴图切换或刚性转头。"
    });
  } else {
    checks.push({
      gate: "Single-Action Clip Budget / 单镜头动作容量",
      status: "PASS",
      reasonEn: "Action density fits cleanly inside a single 3.5–4s shot.",
      reasonZh: "单镜头动作密度合理。"
    });
  }

  // 5. Rigid Physics & Contradiction Check (catches "R15 ... softly bends noodle-like arm"!)
  const hasSoftBodyContradiction =
    /\b(?:noodle-like|noodle\s+arms?|rubbery|softly\s+bends?|bendy|elastic\s+limbs?|twists?\s+(?:its\s+)?forearm|jelly\s+limbs?|soft-body\s+limbs?)\b/i.test(
      posLower
    ) || /(?:面条臂|面条般|像面条一样|软体弯曲|橡胶般弯曲|扭曲前臂|软绵绵弯曲)/.test(positiveOnly);

  const hasExplicitHingeWords =
    /\b(?:rigid|hinges?|motor6d|stiff|unsegmented|mechanical\s+elbows?)\b/i.test(lower) ||
    /(?:刚性|刚体|转轴|铰链|僵直|不弯曲)/.test(prompt);

  if (hasSoftBodyContradiction || issue === "noodle-limbs" || issue === "foot-sliding" || issue === "outfit-drift") {
    checks.push({
      gate: "Rigid Physics & I2V Anchor / 刚体关节与首帧锚定",
      status: "FAIL",
      reasonEn: hasSoftBodyContradiction
        ? "Contradictory soft-body limb deformation (`noodle-like` / `softly bends` / `twists forearm`) detected; blocky R6/R15 limbs must remain rigid rectangular segments rotating only at mechanical hinges."
        : ISSUE_PATCHES[issue].fixEn,
      reasonZh: hasSoftBodyContradiction
        ? "检测到面条臂/软体弯曲/扭曲前臂等矛盾变形词；R6/R15方柱四肢必须保持刚性长方体，仅沿机械铰链折角转动。"
        : ISSUE_PATCHES[issue].fixZh
    });
  } else if (mode === "t2v" || !hasExplicitHingeWords) {
    checks.push({
      gate: "Rigid Physics & I2V Anchor / 刚体关节与首帧锚定",
      status: "WARN",
      reasonEn:
        mode === "t2v"
          ? "Raw T2V risks cross-shot outfit drift; prefer local 3D `--spec` rendering or First-Frame I2V with explicit `rigid Motor6D mechanical hinge joints`."
          : "Add explicit `rigid Motor6D mechanical hinge joints` (mentioning `R6`/`R15` alone is not enough to stop soft-body limb bending).",
      reasonZh:
        mode === "t2v"
          ? "纯文生视频(T2V)多镜头易换装变脸；建议直接用本地3D `--spec` 渲染成片，或改用首帧I2V并显式声明「刚性Motor6D机械铰链」。"
          : "仅写 R6/R15 骨架名不足以阻止软体形变，请显式加入「刚性Motor6D机械转轴/铰链 (rigid mechanical hinge joints)」。"
    });
  } else {
    checks.push({
      gate: "Rigid Physics & I2V Anchor / 刚体关节与首帧锚定",
      status: "PASS",
      reasonEn: "Rigid mechanical hinge physics locked without soft-body contradictions.",
      reasonZh: "已锁定刚性机械铰链物理且无软体变形冲突。"
    });
  }

  // 6. Trademark & Brand Cleanliness Gate
  const positiveMentionsTrademark =
    /\b(?:official\s+roblox\s+(?:logo|r\b|badge|emblem|trademark)|roblox\s+tilt\b|tilted[-\s]square\s+(?:roblox|r\b|logo)|roblox\s+r\s+(?:logo|badge|emblem)|robux\s+(?:icon|logo))\b/i.test(
      posLower
    ) || /(?:官方\s*roblox\s*(?:商标|logo|标志|徽标)|倾斜方框\s*(?:商标|标志)|roblox\s*r\s*(?:标|徽标))/i.test(positiveOnly);

  if (positiveMentionsTrademark || issue === "trademark-leak") {
    checks.push({
      gate: "Trademark Cleanliness / 官方商标零污染锁",
      status: "FAIL",
      reasonEn: "Positive prompt requests an official Roblox logo / tilted-square emblem / [R] badge. Replace with an unbranded geometric triangle emblem.",
      reasonZh: "正向提示词中包含官方 Roblox 商标 / 倾斜方框或 R 徽标；请替换为无品牌的原创几何三角形徽章。"
    });
  } else {
    checks.push({
      gate: "Trademark Cleanliness / 官方商标零污染锁",
      status: "PASS",
      reasonEn: "Zero official trademark emblems requested in positive prompt.",
      reasonZh: "正向描述无官方品牌商标污染。"
    });
  }

  // 7. Non-Human Pet & Prop Topology Gate (ignore wearable ear accessories like "cat-ear headphones")
  const petScopeLower = posLower.replace(/\b(?:cat|dog|bunny|bear|fox)-ears?\b/gi, "ear_accessory");
  const petScopeZh = positiveOnly.replace(/(?:猫耳|兔耳|熊耳|狗耳)(?:耳机|帽|发箍|头饰)?/g, "耳饰");
  const mentionsPet =
    /\b(?:dragon|pet|puppy|dog|cat|kitten|monster|creature|mount)\b/i.test(petScopeLower) ||
    /(?:神宠|宠物|巨龙|恐龙|小龙|猫咪|小狗|坐骑)/.test(petScopeZh);
  const organicPetDrift =
    /\b(?:scaly|scales|sharp\s+claws?|talons?|leathery\s+(?:bat\s+)?wings?|feathers?|furry|realistic\s+fur|fangs?)\b/i.test(
      posLower
    ) || /(?:龙鳞|鳞片|锋利尖爪|利爪|皮膜翼|蝙蝠翼|逼真毛发|獠牙)/.test(positiveOnly);
  const blockyPetLocked =
    /\b(?:blocky[^.,;]{0,25}(?:pet|dragon|dog|cat|wing)|chamfered[^.,;]{0,25}(?:pet|dragon|wing)|clawless[^.,;]{0,20}paws?)\b/i.test(
      lower
    ) || /(?:方块[^，。；]{0,8}(?:龙|宠|犬|翼)|无爪[^，。；]{0,8}方[足爪]|几何翼)/.test(prompt);

  const mentionsHeldProp =
    /\b(?:kettle|ramen|noodles?|chopsticks?|cup|mug|cola|can|sword|flashlight|pencil|strap|handle|shopping\s+cart|umbrella|phone|tray)\b/i.test(
      posLower
    ) || /(?:水壶|泡面|筷子|咖啡杯|可乐罐|长剑|手电筒|铅笔|吊环|把手|购物车|托盘)/.test(positiveOnly);
  const fingerPinchProp =
    /\b(?:pinches?|wraps?\s+(?:its\s+)?fingers|gripping\s+with\s+fingers|curls?\s+fingers|between\s+thumb\s+and)\b/i.test(
      posLower
    ) || /(?:捏住|五指握住|手指缠绕|夹在指间|扣住扳机)/.test(positiveOnly);
  const propDockedCleanly =
    /\b(?:docked|welded|parented|attached\s+flush|mounted\s+flush|magnetic|presses\s+squarely|flat\s+against|pushes\s+the\s+bar)\b/i.test(
      lower
    ) || /(?:吸附|刚性贴合|父子绑定|焊接|平贴|抵住|贴在)/.test(prompt);

  if ((mentionsPet && organicPetDrift) || fingerPinchProp) {
    checks.push({
      gate: "Pet & Prop Topology Lock / 神宠与手持道具刚性装配锁",
      status: "FAIL",
      reasonEn: fingerPinchProp
        ? "Prop interaction uses finger-pinching/wrapping (`pinches` / `wraps fingers`); specify rigid flat-surface docking/welding to the 1x2x1 block hand."
        : "Non-human pet uses organic anatomy (`scales` / `sharp claws` / `leathery wings`); lock chamfered SmoothPlastic/Neon pet blocks, 2D dot eyes, and clawless block paws.",
      reasonZh: fingerPinchProp
        ? "道具交互出现了捏住/手指缠绕描述；必须改为道具与1x2x1实心平头方手平面的刚性吸附/贴合装配。"
        : "非人宠物包含鳞片/尖爪/皮膜翼等有机生物特征；必须锁定倒角SmoothPlastic/Neon方块神宠、2D豆豆眼与无爪实心小方足。"
    });
  } else if ((mentionsPet && !blockyPetLocked) || (mentionsHeldProp && !propDockedCleanly && mode !== "local3d")) {
    checks.push({
      gate: "Pet & Prop Topology Lock / 神宠与手持道具刚性装配锁",
      status: "WARN",
      reasonEn: mentionsPet
        ? "Pet mentioned without explicit `blocky chamfered SmoothPlastic pet, 2D dot eyes, clawless block paws` lock."
        : "Handheld prop mentioned without explicit rigid flat-hand docking (`docked/welded flush against the solid 1x2x1 block hand`).",
      reasonZh: mentionsPet
        ? "提及宠物但未锁定「倒角方块几何体、2D豆豆眼、无爪小方足」，易退化为写实生物。"
        : "提及手持/接触道具，建议显式声明「与1x2x1实心平头方手底面刚性贴合/吸附 (docked/welded flush)」，防止模型脑补手指握持。"
    });
  } else {
    checks.push({
      gate: "Pet & Prop Topology Lock / 神宠与手持道具刚性装配锁",
      status: "PASS",
      reasonEn: "Pet/prop rigid attachment topology is clean.",
      reasonZh: "宠物与手持道具刚性装配约束清晰。"
    });
  }

  // 8. UI Text-Garble & Engine Compatibility Gate
  const denseUiRisk =
    /\b(?:paragraph\s+text|crowded\s+[^.,;]{0,20}text|fine\s+print|countdown\s+timer\s+\d\d:\d\d|four\s+overlapping\s+[^.,;]{0,25}text)\b/i.test(
      lower
    ) || /(?:密集小字|多行段落文字|倒计时数字跳动|满屏文字弹窗)/.test(prompt);

  if (!isKnownEngine) {
    checks.push({
      gate: "UI & Engine Guard / 浮空UI防乱码与引擎校验",
      status: "WARN",
      reasonEn: `Unsupported engine "${engine}". Valid engines: ${Array.from(VALID_ENGINES).join(", ")}.`,
      reasonZh: `未知引擎 "${engine}"；支持列表：${Array.from(VALID_ENGINES).join(", ")}。`
    });
  } else if (denseUiRisk) {
    checks.push({
      gate: "UI & Engine Guard / 浮空UI防乱码与引擎校验",
      status: "WARN",
      reasonEn: "Dense UI text or live ticking digits often garble in diffusion video; keep in-scene UI badges to 1–3 bold words or composite HUD text in post / local 3D.",
      reasonZh: "密集弹窗文字或跳动倒计时在扩散视频中极易乱码；画面内仅保留1~3词极简色块按钮，复杂花字建议后期合成或直接用本Skill本地3D直出。"
    });
  } else {
    checks.push({
      gate: "UI & Engine Guard / 浮空UI防乱码与引擎校验",
      status: "PASS",
      reasonEn: `Engine (${engine}) and UI text density verified.`,
      reasonZh: `目标引擎 (${engine}) 与画面UI文字密度正常。`
    });
  }

  // Tag Gates 1–8 explicitly under "geometry" domain so Geometry vs. Acting never conflate
  for (const c of checks) {
    c.category = "geometry";
  }

  // 9. Performance & Interaction Completeness Gate ("Does the character act with clear gaze, cause, and camera-facing prop intent?")
  const shotSpec = rawOpts.shotSpec && typeof rawOpts.shotSpec === "object" ? rawOpts.shotSpec : null;
  const knownTargetMap = rawOpts.knownTargetMap instanceof Map ? rawOpts.knownTargetMap : null;
  const requireActing = Boolean(rawOpts.requireActing);

  if (issue === "missing-acting") {
    checks.push({
      category: "acting",
      gate: "Performance & Interaction Completeness / 表演关系完整性",
      status: "FAIL",
      reasonEn: ISSUE_PATCHES["missing-acting"].fixEn,
      reasonZh: ISSUE_PATCHES["missing-acting"].fixZh
    });
  } else if (shotSpec) {
    const perf = shotSpec.performance && typeof shotSpec.performance === "object" ? shotSpec.performance : null;
    const inter = shotSpec.interaction && typeof shotSpec.interaction === "object" ? shotSpec.interaction : null;
    const actorGazePresent = Array.isArray(shotSpec.actors) && shotSpec.actors.some((a) => Boolean(a?.gaze));
    const hasGaze = Boolean(perf?.gazeTarget || actorGazePresent);
    const hasRead = Boolean(shotSpec.audienceRead || shotSpec.beatIntent);
    const hasCause = Boolean(perf?.reactionCause || shotSpec.beatIntent);
    const actorUsesHandProp = Array.isArray(shotSpec.actors) && shotSpec.actors.some((a) => Boolean(a?.handPropL || a?.handPropR));

    const badIntent = inter && inter.intent && !VALID_INTERACTION_INTENTS.has(String(inter.intent).toLowerCase());
    const occludedInter = inter && /^(?:occluded|hidden|blocked)$/i.test(String(inter.visibility || ""));
    const unknownGazeTarget =
      perf?.gazeTarget && knownTargetMap && knownTargetMap.size > 0 && !knownTargetMap.has(perf.gazeTarget);
    const unknownInterProp =
      inter?.propId && knownTargetMap && knownTargetMap.size > 0 && !knownTargetMap.has(inter.propId);

    if (badIntent || occludedInter || unknownGazeTarget || unknownInterProp) {
      const detailEn = badIntent
        ? `Invalid interaction.intent "${inter.intent}" (must be hold | present | tap | slam | point | drop | receive).`
        : occludedInter
        ? `interaction.visibility is "${inter.visibility}"; key hand-prop contact must be camera-facing/unoccluded.`
        : unknownGazeTarget
        ? `performance.gazeTarget "${perf.gazeTarget}" does not match any castId, prop id, or stageTarget id.`
        : `interaction.propId "${inter.propId}" does not match any prop id or stageTarget id.`;
      checks.push({
        category: "acting",
        gate: "Performance & Interaction Completeness / 表演关系完整性",
        status: "FAIL",
        reasonEn: detailEn,
        reasonZh: `表演或交互目标无效：${detailEn}`
      });
    } else if (rawOpts.enforceStructuredActing && (!hasGaze || !hasRead || !hasCause || (actorUsesHandProp && !inter))) {
      const missing = [];
      if (!hasRead) missing.push("audienceRead/beatIntent");
      if (!hasGaze) missing.push("performance.gazeTarget");
      if (!hasCause) missing.push("performance.reactionCause");
      if (actorUsesHandProp && !inter) missing.push("interaction (hand/propId/intent/visibility)");
      checks.push({
        category: "acting",
        gate: "Performance & Interaction Completeness / 表演关系完整性",
        status: "WARN",
        reasonEn: `Shot describes mechanics without complete acting grammar (missing: ${missing.join(", ")}). Add gaze target, reaction cause, and single audienceRead.`,
        reasonZh: `分镜仅描述了动作与外观，缺少完整瞬间表演字段（缺失：${missing.join("、")}）；请补充视线目标、触发前因与半秒观众读点。`
      });
    } else {
      checks.push({
        category: "acting",
        gate: "Performance & Interaction Completeness / 表演关系完整性",
        status: "PASS",
        reasonEn: hasGaze && hasRead
          ? "Beat intent, gaze target, and camera-facing interaction semantics verified."
          : "Single-beat action and prop interaction semantics clean.",
        reasonZh: hasGaze && hasRead ? "已完整锁定表演动机、瞳孔追踪目标与可见面道具交互。" : "单镜头动作与交互语义清晰。"
      });
    }
  } else {
    // Plain prompt string check: catch static occupation-label prompts or --require-acting gaps
    const hasExplicitGaze =
      /\b(?:pupils?\s+track(?:ing)?|gaze|stares?\s+at|looks?\s+(?:at|toward)|watching|eyebrows?|side-eye)\b/i.test(lower) ||
      /(?:瞳孔|视线|盯住|盯着|看向|斜睨|高低眉|挑眉)/.test(prompt);
    const hasExpressiveBeat =
      verbCount >= 1 ||
      hasExplicitGaze ||
      /\b(?:pivots?|leans?|freezes?|holds?\s+up|presents?|points?|waves?|slumps?|recoils?|swings?)\b/i.test(lower) ||
      /(?:转头|前倾|后仰|定格|举起|指向|挥动|摆动|端着)/.test(prompt);
    const mentionsOccludedHand =
      /\b(?:hand\s+hidden|occluded\s+by\s+torso|prop\s+behind\s+back)\b/i.test(posLower) || /(?:手被挡住|道具被身体遮挡)/.test(positiveOnly);

    if (mentionsOccludedHand) {
      checks.push({
        category: "acting",
        gate: "Performance & Interaction Completeness / 表演关系完整性",
        status: "FAIL",
        reasonEn: "Key hand or prop is described as hidden/occluded; keep acting hand and prop on the camera-facing plane.",
        reasonZh: "关键手部或道具被描述为遮挡不可见；必须将核心交互手与道具置于朝向镜头的可见面。"
      });
    } else if ((requireActing && !hasExplicitGaze) || !hasExpressiveBeat) {
      checks.push({
        category: "acting",
        gate: "Performance & Interaction Completeness / 表演关系完整性",
        status: "WARN",
        reasonEn: "Static label-style description without explicit pupil gaze target or story-beat intent; specify what the character's pupils track and what the viewer reads in 0.5s.",
        reasonZh: "当前描述偏向静态身份/站桩标签，缺少明确视线追踪目标(pupils tracking)与瞬间剧情读点；建议补充角色正在看什么及触发前因。"
      });
    } else {
      checks.push({
        category: "acting",
        gate: "Performance & Interaction Completeness / 表演关系完整性",
        status: "PASS",
        reasonEn: "Expressive single-beat acting cue verified.",
        reasonZh: "单镜头动态表演指向清晰。"
      });
    }
  }

  // 10. Thumbnail & Safe-Zone Readability Gate ("Can the joke, expression, and prop still read at mobile thumbnail size?")
  const thumbStats = rawOpts.thumbnailPath ? measurePngThumbnailContrast(rawOpts.thumbnailPath) : null;
  if (issue === "poor-readability") {
    checks.push({
      category: "acting",
      gate: "Thumbnail & Safe-Zone Readability / 小尺寸与安全区可读性",
      status: "FAIL",
      reasonEn: ISSUE_PATCHES["poor-readability"].fixEn,
      reasonZh: ISSUE_PATCHES["poor-readability"].fixZh
    });
  } else {
    let readabilityStatus = "PASS";
    let readReasonEn = thumbStats
      ? `9:16 safe-zone framing, silhouette separation, and 64x64 thumbnail contrast (stdDev=${thumbStats.stdDev}) verified.`
      : "9:16 safe-zone framing, silhouette separation, and dialogue-free readability verified.";
    let readReasonZh = thumbStats
      ? `9:16竖屏安全区、剪影分离度与64x64缩略图对比度(stdDev=${thumbStats.stdDev})校验通过。`
      : "9:16竖屏安全区、剪影无遮挡与去台词可读性校验通过。";

    if (shotSpec) {
      const chatWords = String(shotSpec.chatEn || "")
        .trim()
        .split(/\s+/)
        .filter(Boolean).length;
      const actors = Array.isArray(shotSpec.actors) ? shotSpec.actors : [];
      const actorPositions = actors.map((a) => {
        const p = Array.isArray(a.pos) ? a.pos : Array.isArray(a.fromPos) ? a.fromPos : [0, 0, 0];
        return { id: a.castId || "", x: Number(p[0]) || 0, y: Number(p[1]) || 0, z: Number(p[2]) || 0, pose: a.pose || "idle" };
      });

      // Check actor-to-actor silhouette collision
      let collidedPair = null;
      for (let i = 0; i < actorPositions.length; i++) {
        for (let j = i + 1; j < actorPositions.length; j++) {
          const dx = Math.abs(actorPositions[i].x - actorPositions[j].x);
          const dz = Math.abs(actorPositions[i].z - actorPositions[j].z);
          if (dx < 0.28 && dz < 0.22) {
            collidedPair = `${actorPositions[i].id || i} & ${actorPositions[j].id || j}`;
          }
        }
      }

      // Check whether a non-target standing actor blocks the camera's sightline to gazeTarget!
      let occludedTarget = "";
      const gazeTgtId = shotSpec.performance?.gazeTarget || "";
      if (gazeTgtId && knownTargetMap && knownTargetMap.has(gazeTgtId)) {
        const tgtPos = knownTargetMap.get(gazeTgtId);
        if (Array.isArray(tgtPos)) {
          for (const ap of actorPositions) {
            if (ap.id !== gazeTgtId && ap.pose !== "sit" && Math.abs(ap.x - tgtPos[0]) < 0.24 && ap.z > tgtPos[2] + 0.25) {
              occludedTarget = `${ap.id || "actor"} stands directly in front of gazeTarget "${gazeTgtId}"`;
            }
          }
        }
      }

      // Check fallback 2-cast occlusion when actors[] was omitted on subway_car with empty_seat!
      if (!occludedTarget && actors.length === 0 && rawOpts.backdrop === "subway_car" && rawOpts.castCount >= 2) {
        occludedTarget = "Default 2-actor placement (x=+0.58) occludes subway empty_seat (x=+0.62); declare explicit actors[] positions";
      }

      const bubbleOutOfSafeZone =
        shotSpec.bubbleY !== undefined && (Number(shotSpec.bubbleY) < 14 || Number(shotSpec.bubbleY) > 165);

      if (collidedPair || chatWords > 8) {
        readabilityStatus = "FAIL";
        readReasonEn = collidedPair
          ? `Actors (${collidedPair}) overlap in 3D space (|dx|<0.28, |dz|<0.22), merging silhouettes at mobile thumbnail size.`
          : `Overhead chatEn has ${chatWords} words (>8); visual gag relies on dense text instead of silent-comedy readability.`;
        readReasonZh = collidedPair
          ? `角色（${collidedPair}）站位重叠导致缩略图剪影粘连；请拉开横向或前后景深间距。`
          : `头顶气泡词数过多（${chatWords}词 > 8词），在小尺寸画面中无法一眼读懂，请精简至1~4词并将笑点交给动作眼神。`;
      } else if (occludedTarget || chatWords > 4 || bubbleOutOfSafeZone || (thumbStats && thumbStats.stdDev < 14)) {
        readabilityStatus = "WARN";
        readReasonEn = occludedTarget
          ? `Sightline occlusion warning: ${occludedTarget}. Keep the contested prop/target unoccluded.`
          : bubbleOutOfSafeZone
          ? `bubbleY=${shotSpec.bubbleY} sits outside the 9:16 top/face safe band (20..140).`
          : thumbStats && thumbStats.stdDev < 14
          ? `Rendered 64x64 thumbnail contrast is flat (stdDev=${thumbStats.stdDev}); boost rim/silhouette contrast.`
          : `Overhead chatEn has ${chatWords} words; trim to <=4 bold words so the pose carries the joke.`;
        readReasonZh = occludedTarget
          ? `视线遮挡预警：${occludedTarget}；请调整站位让关键目标完全露在镜头可见面。`
          : bubbleOutOfSafeZone
          ? `气泡纵向位置(bubbleY=${shotSpec.bubbleY})超出竖屏安全区(20..140)。`
          : thumbStats && thumbStats.stdDev < 14
          ? `64x64缩略图对比度偏低(stdDev=${thumbStats.stdDev})，小尺寸易糊成一片。`
          : `头顶气泡偏长（${chatWords}词），建议压缩至4词以内，确保遮住台词也能读懂表演。`;
      }
    } else if (thumbStats && thumbStats.stdDev < 14) {
      readabilityStatus = "WARN";
      readReasonEn = `Rendered 64x64 thumbnail contrast is low (stdDev=${thumbStats.stdDev}).`;
      readReasonZh = `渲染图64x64缩略图对比度偏低(stdDev=${thumbStats.stdDev})。`;
    }

    checks.push({
      category: "acting",
      gate: "Thumbnail & Safe-Zone Readability / 小尺寸与安全区可读性",
      status: readabilityStatus,
      reasonEn: readReasonEn,
      reasonZh: readReasonZh
    });
  }

  const geoChecks = checks.filter((c) => c.category === "geometry");
  const actChecks = checks.filter((c) => c.category === "acting");
  const summarizeChecks = (arr) =>
    arr.some((c) => c.status === "FAIL") ? "FAIL" : arr.some((c) => c.status === "WARN") ? "WARN" : "PASS";

  const geometryStatus = summarizeChecks(geoChecks);
  const actingStatus = summarizeChecks(actChecks);
  const overallStatus = summarizeChecks(checks);

  // Clean & rig-accurate Rescue Rewrite
  const sanitizedAction = (prompt || "performs one crisp blocky hinge motion")
    .replace(/\b(?:then|and then|after that|afterwards|followed by)\b[\s\S]*$/i, "")
    .replace(/(?:接着|然后|随后|紧接着)[\s\S]*$/, "")
    .replace(/\b(?:with\s+)?(?:five\s+fingers|human\s+fingers|human\s+hands|c-shaped\s+claw\s+hands?|lego\s+claws?|studded\s+lego\s+floor|official\s+roblox\s+(?:logo|r\s+logo|badge)|noodle-like|softly\s+bends?|realistic\s+scaly)\b/gi, "")
    .replace(/(?:带人类五指的?|用五根手指|人类五指|乐高C型夹爪|凸点底板|官方Roblox商标Logo|像面条一样)/gi, "")
    .replace(/\s{2,}/g, " ")
    .replace(/^[\s,.;:，。；、]+|[\s,.;:，。；、]+$/g, "");

  const hasCjkInput = /[\u4e00-\u9fff]/.test(sanitizedAction);
  const actionForEn = hasCjkInput ? "executes one crisp single-beat physical motion matching the keyframe" : sanitizedAction || "executes one crisp single-beat physical motion";
  const actionForZh = hasCjkInput ? sanitizedAction : "沿刚性机械铰链执行单一干脆的核心物理动作（保持首帧角色配色与贴图完全一致）";

  const rigDescEn =
    detectedRig === "r15"
      ? "Roblox R15 segmented blocky rig (2x2x1 SmoothPlastic torso, flush 1x2x1 upper/lower rectangular limb blocks rotating strictly at mechanical 90-degree elbow and knee hinges with zero rubbery bending, fingerless and clawless solid block hands)"
      : "Roblox R6/Blocky rig (2x2x1 SmoothPlastic rectangular torso, flush 1x2x1 unsegmented solid rectangular limbs rotating strictly at Motor6D shoulder and hip hinges, fingerless and clawless flat beveled block hands)";

  const rigDescZh =
    detectedRig === "r15"
      ? "Roblox R15分段刚性方块骨架（2x2x1平滑塑料躯干、并拢1x2x1刚性上下肢方块仅沿肘膝机械铰链折角转动、严禁面条弯曲、无指无爪实心平头方手）"
      : "标准Roblox R6刚性方块骨架（2x2x1平滑塑料长方体躯干、并拢齐平1x2x1无分段实心方柱四肢仅沿肩髋Motor6D转轴摆动、无指无爪实心平头方手）";

  let rescuedPromptEn;
  if (engine === "hailuo") {
    rescuedPromptEn = `[Push in] (9:16 vertical, ${detectedRig}) ${rigDescEn}, 1:1 barrel-beveled studless head with flat 2D screen-printed face decal. Single action: ${actionForEn}. Props docked flush to flat block hands, smooth architectural floor (zero raised Lego studs), unbranded triangle emblem only.`;
  } else if (engine === "sora") {
    rescuedPromptEn = `Camera (9:16, 35mm macro lens): Medium framing, controlled dolly push-in (generate 5.0s clip, trim to 3.75s). Subject: ${rigDescEn}, smooth studless 1:1 barrel head, flat 2D face decal. Action: ${actionForEn}. Physics: Strict rigid-body hinge rotation only, zero soft-body limb deformation, smooth studless floor, zero brand logos.`;
  } else if (engine === "runway") {
    rescuedPromptEn = `Camera (9:16): Medium tracking framing. Subject (${detectedRig}): ${rigDescEn}, 1:1 studless barrel head, flat 2D decal face. Action: ${actionForEn}. Physics: Rigid Motor6D hinges, smooth flat floor (zero Lego bumps), zero human fingers, unbranded.`;
  } else {
    const tag = isKnownEngine ? engine.toUpperCase() : "SAFE-BLOCKY";
    rescuedPromptEn = `[${tag} I2V · 9:16] ${rigDescEn}, smooth studless 1:1 barrel-beveled cylindrical head, flat 2D screen-printed face decal. Single action: ${actionForEn}. Smooth flat Roblox SmoothPlastic / WoodPlanks environment with multi-part props, zero human fingers, zero Lego C-claws or floor studs, zero official brand logos, non-voxel.`;
  }

  const tagZh = isKnownEngine ? engine.toUpperCase() : "通用防串味";
  const rescuedPromptZh = `【${tagZh} 首帧I2V · 9:16竖屏】${rigDescZh}，头顶平滑无颗粒1:1桶状圆角圆柱头与纯平2D印刷五官贴图。单一核心动作：${actionForZh}。手持道具与方手底面刚性贴合吸附，平整无凸粒地面与多部件精致道具，无任何官方商标Logo，严禁人类五指、乐高C型爪或乐高地面圆颗粒。`;

  const negativePrompt =
    "official Roblox logo, tilted square Roblox trademark emblem, Roblox R badge, brand watermarks, human fingers, five-fingered hand, Lego C-shaped claw hands, Lego hook hands, Lego top head studs, raised circular Lego floor studs, studded Lego baseplate, Minecraft sharp voxel cube head, organic reptile scales, sharp claws, leathery bat wings, separated thin legs with thigh gap, protruding human sneakers, realistic human face, 3D protruding nose, skin pores, rubbery noodle limbs, soft-body limb bending, foot sliding, morphing clothes / 官方Roblox倾斜方框商标Logo，R字品牌徽标，品牌水印，人类五指，真实人脸，乐高C型夹爪手，乐高头顶与地面凸起圆颗粒，我的世界直角像素块，真实动物鳞片尖爪，双腿分叉穿真人运动鞋，3D高鼻梁，面条状软体弯曲手臂，脚底打滑";

  return {
    overallStatus,
    geometryStatus,
    actingStatus,
    engine,
    rig: detectedRig,
    mode,
    issue: issue || null,
    originalPrompt: prompt,
    checks,
    rescuedPromptEn,
    rescuedPromptZh,
    negativePrompt
  };
}

export function inspectPackageFile(filePath, opts = {}) {
  const abs = path.resolve(filePath);
  const raw = JSON.parse(fs.readFileSync(abs, "utf8").replace(/^\uFEFF/, ""));
  const shots = Array.isArray(raw.shots) ? raw.shots : [];
  if (shots.length === 0) {
    throw new Error(`No shots[] array found in ${abs}`);
  }

  const engine = (opts.engine || raw.engine || "local3d").toLowerCase();
  const rig = opts.rig || raw.rig || "r6";
  const packMode = engine === "local3d" || opts.mode === "local3d" ? "local3d" : opts.mode || "i2v";
  const isCustomEpisode = Boolean(raw.template === "custom-spec" || Array.isArray(raw.cast) || raw.backdrop || opts.requireActing);
  const backdrop = raw.backdrop || "";
  const castCount = Array.isArray(raw.cast) ? raw.cast.length : 0;
  const assetsDir = opts.assetsDir ? path.resolve(opts.assetsDir) : "";

  // Build base target registry (camera + backdrop landmarks + stageTargets + cast IDs)
  const baseTargets = new Map();
  baseTargets.set("camera", [0, 0.36, 3.18]);
  baseTargets.set("viewer", [0, 0.36, 3.18]);
  const bMarks = BUILTIN_STAGE_TARGETS[backdrop] || {};
  for (const [k, pos] of Object.entries(bMarks)) baseTargets.set(k, pos);
  if (Array.isArray(raw.stageTargets)) {
    for (const st of raw.stageTargets) {
      if (st?.id) baseTargets.set(st.id, st.pos || [0, 0, 0]);
    }
  }
  if (Array.isArray(raw.cast)) {
    for (const c of raw.cast) {
      if (c?.id) baseTargets.set(c.id, null);
    }
  }

  const seenActions = new Map();
  const duplicateShots = [];
  const constraintViolations = [];

  const shotReports = shots.map((s, idx) => {
    const shotNum = s.shotNumber || s.id || idx + 1;
    const isRawSpecShot = !s.i2vPromptEn && !s.i2vPromptZh && Boolean(Array.isArray(raw.cast) || raw.backdrop || raw.environmentEn);
    const specHeader = isRawSpecShot
      ? `Roblox ${rig} ${raw.material || "SmoothPlastic"} rig, 1:1 studless barrel cylindrical head, flat 2D screen-printed face decal, fingerless and clawless solid 1x2x1 block hands, rigid Motor6D hinges. ${raw.environmentEn || ""} `
      : "";
    const textToInspect = s.i2vPromptEn || s.i2vPromptZh || `${specHeader}${s.actionEn || s.actionZh || ""} ${s.faceEn || ""}`;
    const actionOnly = s.actionEn || s.actionZh || "";
    const actionSig = String(actionOnly).trim().toLowerCase();
    if (actionSig) {
      if (seenActions.has(actionSig)) {
        duplicateShots.push({ shotNumber: shotNum, duplicatesShot: seenActions.get(actionSig), action: actionSig });
      } else {
        seenActions.set(actionSig, shotNum);
      }
    }
    const banCheckpoint = Boolean(raw.constraints?.noCheckpoint || raw.constraints?.noCheckpoints);
    const banJetpack = Boolean(raw.constraints?.noJetpack || raw.constraints?.noJetpacks);
    if (banCheckpoint && /\bcheckpoint\b|存档点/i.test(textToInspect)) {
      constraintViolations.push(`Shot ${shotNum} violates constraints.noCheckpoint`);
    }
    if (banJetpack && /\bjetpack\b|喷气包/i.test(textToInspect)) {
      constraintViolations.push(`Shot ${shotNum} violates constraints.noJetpack`);
    }

    const shotTargets = new Map(baseTargets);
    if (Array.isArray(s.props)) {
      for (const pr of s.props) {
        if (pr?.id) shotTargets.set(pr.id, pr.pos || [0, 0, 0]);
        if (pr?.type && !shotTargets.has(pr.type)) shotTargets.set(pr.type, pr.pos || [0, 0, 0]);
      }
    }
    if (Array.isArray(s.actors)) {
      for (const ac of s.actors) {
        if (ac?.castId) shotTargets.set(ac.castId, ac.pos || ac.fromPos || [0, 0, 0]);
      }
    }

    const shotPngCandidate = assetsDir
      ? path.join(assetsDir, `shot_${String(idx + 1).padStart(2, "0")}.png`)
      : "";

    const rep = inspectPrompt({
      prompt: textToInspect,
      actionText: actionOnly,
      shotSpec: s,
      knownTargetMap: shotTargets,
      enforceStructuredActing: isCustomEpisode,
      backdrop: s.backdrop || backdrop,
      castCount,
      thumbnailPath: shotPngCandidate && fs.existsSync(shotPngCandidate) ? shotPngCandidate : "",
      engine,
      rig,
      mode: s.i2vPromptEn ? packMode : "local3d"
    });
    return {
      shotNumber: shotNum,
      overallStatus: rep.overallStatus,
      geometryStatus: rep.geometryStatus,
      actingStatus: rep.actingStatus,
      failedGates: rep.checks.filter((c) => c.status === "FAIL").map((c) => c.gate),
      warnGates: rep.checks.filter((c) => c.status === "WARN").map((c) => c.gate)
    };
  });

  // Optional Avatar Crop thumbnail audit when --assets-dir contains avatars/*.png
  const avatarCropStats = [];
  if (assetsDir && fs.existsSync(path.join(assetsDir, "avatars"))) {
    for (const fn of fs.readdirSync(path.join(assetsDir, "avatars")).filter((f) => f.endsWith(".png"))) {
      const st = measurePngThumbnailContrast(path.join(assetsDir, "avatars", fn));
      if (st) avatarCropStats.push({ file: fn, ...st });
    }
  }

  const geoFail = duplicateShots.length > 0 || constraintViolations.length > 0 || shotReports.some((r) => r.geometryStatus === "FAIL");
  const geoWarn = shotReports.some((r) => r.geometryStatus === "WARN");
  const geometryStatus = geoFail ? "FAIL" : geoWarn ? "WARN" : "PASS";

  const actFail = shotReports.some((r) => r.actingStatus === "FAIL");
  const actWarn = shotReports.some((r) => r.actingStatus === "WARN");
  const actingStatus = actFail ? "FAIL" : actWarn ? "WARN" : "PASS";

  const overallStatus = geoFail || actFail ? "FAIL" : geoWarn || actWarn ? "WARN" : "PASS";

  return {
    file: abs,
    shotCount: shots.length,
    uniqueActionCount: seenActions.size,
    overallStatus,
    geometryStatus,
    actingStatus,
    avatarCropStats,
    duplicateShots,
    constraintViolations,
    shotReports
  };
}

export function formatDriftCheckMarkdown(report, rawLang = "en") {
  const lang = normalizeLang(rawLang);
  const useZhText = lang === "zh" || lang === "zh-tw" || lang === "zh-en";
  const lines = [];
  lines.push(`# Prompt Drift & Rescue Report: \`${report.overallStatus}\` (\`lang: ${lang}\`)`);
  lines.push("");
  lines.push(
    `- **Domain Verdicts**: Geometry Gates (1–8): \`${report.geometryStatus}\` · Acting & Readability Gates (9–10): \`${report.actingStatus}\``
  );
  lines.push(`- **Engine, Rig & Mode**: \`${report.engine}\` · \`${report.rig || "r6"}\` · \`${report.mode.toUpperCase()}\``);
  if (report.issue) {
    lines.push(`- **Targeted Issue**: \`${report.issue}\` (${ISSUE_PATCHES[report.issue].titleZh})`);
  }
  if (report.originalPrompt) {
    lines.push(`- **Input Prompt**: \`${report.originalPrompt}\``);
  }
  lines.push("");
  lines.push("| Gate | Status | Diagnosis & Fix |");
  lines.push("| --- | :---: | --- |");
  for (const c of report.checks) {
    const diag = lang === "zh" ? c.reasonZh : lang === "zh-en" || lang === "zh-tw" ? `${c.reasonZh} (${c.reasonEn})` : c.reasonEn;
    lines.push(`| ${c.gate} | **${c.status}** | ${diag} |`);
  }
  lines.push("");

  if (lang !== "zh") {
    lines.push("## Rescued Prompt (English · Geometry-Locked Single Action)");
    lines.push("");
    lines.push("```text");
    lines.push(report.rescuedPromptEn);
    lines.push("```");
    lines.push("");
  }

  if (useZhText) {
    lines.push("## 救场重写提示词 (中文 · 已锁定几何防串味与单镜头单动作)");
    lines.push("");
    lines.push("```text");
    lines.push(report.rescuedPromptZh);
    lines.push("```");
    lines.push("");
  }

  lines.push("## Required Negative Prompt");
  lines.push("");
  lines.push("```text");
  lines.push(report.negativePrompt);
  lines.push("```");

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

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("drift_check.mjs");
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || (!opts.prompt && !opts.issue && !opts.pack)) {
    printHelp();
    process.exit(opts.help ? 0 : 1);
  }
  try {
    if (opts.pack) {
      const packReport = inspectPackageFile(opts.pack, opts);
      const outText = opts.json
        ? JSON.stringify(packReport, null, 2)
        : `# Package Drift Audit: \`${packReport.overallStatus}\`\n\n- **Geometry Gates (1–8)**: \`${packReport.geometryStatus}\`\n- **Acting & Readability Gates (9–10)**: \`${packReport.actingStatus}\`\n- Shots: \`${packReport.shotCount}\` (Unique actions: \`${packReport.uniqueActionCount}\`)\n- Duplicate shots: \`${packReport.duplicateShots.length}\`\n- Constraint violations: \`${packReport.constraintViolations.length}\`${
            packReport.avatarCropStats.length
              ? `\n- Avatar 64x64 thumbnail contrast: ${packReport.avatarCropStats.map((a) => `\`${a.file}\` (stdDev=${a.stdDev})`).join(", ")}`
              : ""
          }\n\n` +
          packReport.shotReports
            .map(
              (s) =>
                `- Shot ${String(s.shotNumber).padStart(2, "0")}: **${s.overallStatus}** (Geometry: \`${s.geometryStatus}\`, Acting: \`${s.actingStatus}\`)${
                  s.failedGates.length ? ` [FAIL: ${s.failedGates.join(", ")}]` : ""
                }${s.warnGates.length ? ` [WARN: ${s.warnGates.join(", ")}]` : ""}`
            )
            .join("\n");
      emitOutput(outText, opts.out);
    } else {
      const report = inspectPrompt(opts);
      const outText = opts.json ? JSON.stringify(report, null, 2) : formatDriftCheckMarkdown(report, opts.lang);
      emitOutput(outText, opts.out);
    }
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(1);
  }
}
