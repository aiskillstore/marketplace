#!/usr/bin/env node
/**
 * drift_check.mjs
 * Zero-dependency rule-based linter and rescue rewriter for Minecraft-style AI video prompts.
 * Flags human fingers, smooth/round non-voxel tools, blurry bilinear textures,
 * Roblox cylinder / Lego stud contamination, action overload, and rubbery limb deformation.
 */

import { fileURLToPath } from "node:url";

const ISSUE_PATCHES = {
  "human-fingers": {
    titleZh: "长出人类五指 (Human Finger Growth)",
    fixEn:
      "fingerless and clawless flat 4x4 square pixel-block hand ends on 4x12x4 rectangular prism arms, zero human fingers, no knuckles",
    fixZh:
      "末端为4x4平头正方形像素截面的长方体手臂，严禁长出人类五指或手部关节"
  },
  "smooth-tools": {
    titleZh: "钻石剑/镐变成圆滑金属棍或写实刀刃 (Smooth Non-Voxel Tool Drift)",
    fixEn:
      "holding an extruded 16x16x1 3D pixel-art Minecraft tool with stepped 90-degree staircase voxel edges at a 45-degree angle, no smooth cylindrical metal rod or curved blade",
    fixZh:
      "握持16x16x1像素挤出厚度的锯齿直角立体像素工具（阶梯状90度像素边缘，严禁圆棍镐柄或平滑弧形金属剑刃）"
  },
  "blurry-texels": {
    titleZh: "16x16像素方格被涂抹成模糊渐变或泥塑 (Blurry Bilinear Texture Smudge)",
    fixEn:
      "crisp unfiltered 16x16 nearest-neighbor pixel-art block textures, sharp pixel grid edges, zero bilinear blur, no smooth clay gradients",
    fixZh:
      "清晰无模糊的16x16邻近采样像素网格贴图，像素色块边界分明，严禁双线性插值模糊或光滑泥塑渐变"
  },
  "roblox-lego-drift": {
    titleZh: "串味成Roblox圆桶头或乐高头顶圆粒/C型爪 (Roblox Cylinder / Lego Stud Drift)",
    fixEn:
      "sharp 90-degree 1:1:1 cubic 8x8x8 Minecraft head with studless flat top and +0.5px 3D outer hair layer, no Roblox cylindrical barrel head, no Lego top studs or C-shaped claw hooks",
    fixZh:
      "90度锋利直角1:1:1的8x8x8像素正方体头部（平顶无颗粒+0.5px悬浮3D立体刘海层），严禁Roblox桶状圆柱头、乐高头顶圆凸粒或乐高C型夹爪手"
  },
  "face-morph": {
    titleZh: "8x8像素平面脸凸起长出真人鼻子/嘴唇 (3D Human Face Morphing)",
    fixEn:
      "flat 8x8 nearest-neighbor pixel face with Fresh Animations 2x1 sliding pixel eyes and floating 2x1 pixel eyebrows, zero 3D protruding human nose",
    fixZh:
      "纯平8x8邻近像素五官贴图（2x1可动像素眼与2x1悬浮像素眉毛），零3D鼻子凸起，无真实人类面部骨骼"
  },
  "noodle-limbs": {
    titleZh: "4x12x4方柱四肢像面条一样软化弯曲 (Rubbery Noodle Limbs)",
    fixEn:
      "rigid 4x12x4 rectangular prism arms and legs with mechanical shoulder/hip pivots and clean 90-degree blocky bends, no rubbery limb deformation",
    fixZh:
      "刚性4x12x4长方体方柱四肢，仅在肩髋转轴摆动或做利落90度方块折弯，严禁橡胶面条状弯曲"
  },
  "outfit-drift": {
    titleZh: "切镜头后外层皮肤或方块纹理变形 (Cross-Shot Pixel & Skin Drift)",
    fixEn:
      "Switch from raw T2V to First-Frame I2V anchored by a 3-view 64x64 skin turnaround sheet and isometric block card",
    fixZh:
      "从纯文生视频(T2V)切换为首帧图生视频(I2V)，先用角色三视图与16x16x16方块设定卡固定首帧"
  },
  "overload": {
    titleZh: "单镜头动作过多导致穿模卡死 (Single-Clip Action Overload)",
    fixEn:
      "Split sequential verbs so each 4-5s video clip executes only ONE primary voxel action and ONE camera move",
    fixZh:
      "遵循单镜头单动作铁律：将多个连续动词拆分为独立的3.5~4秒分镜，每镜只保留1个核心动作"
  }
};

function printHelp() {
  console.log(`Usage: node scripts/drift_check.mjs --prompt "<prompt text>" [options]

Run deterministic PASS/WARN/FAIL checks on a Minecraft-style AI video prompt and output a rescued rewrite.

Options:
  --prompt <text>    Draft prompt to inspect (required unless --issue is given)
  --engine <id>      Target engine: kling | seedance | hailuo | wan | sora | runway (default: kling)
  --mode <id>        Workflow mode: i2v | t2v (default: i2v)
  --issue <code>     Optional observed failure code: human-fingers | smooth-tools |
                     blurry-texels | roblox-lego-drift | face-morph | noodle-limbs |
                     outfit-drift | overload
  --lang <code>      Output language: en | zh | zh-tw | ja | ko | es | fr | de | pt | ru | zh-en (default: en)
  --json             Output structured JSON
  --help             Show this help message`);
}

const SUPPORTED_LANGS = new Set(["en", "zh", "zh-tw", "ja", "ko", "es", "fr", "de", "pt", "ru", "zh-en"]);

function normalizeLang(code = "en") {
  const clean = String(code || "en").toLowerCase().trim();
  if (clean === "zh-cn") return "zh";
  if (clean === "pt-br") return "pt";
  return SUPPORTED_LANGS.has(clean) ? clean : "en";
}

const DRIFT_HEADERS = {
  en: "Minecraft Prompt Anti-Drift Report",
  zh: "Minecraft 提示词防串味体检报告",
  "zh-tw": "Minecraft 提示詞防串味體檢報告",
  ja: "Minecraft プロンプト崩れ検査レポート",
  ko: "Minecraft 프롬프트 왜곡 점검 리포트",
  es: "Informe Anti-Deriva de Prompt Minecraft",
  fr: "Rapport Anti-Dérive du Prompt Minecraft",
  de: "Minecraft-Prompt-Drift-Prüfbericht",
  pt: "Relatório Anti-Desvio de Prompt Minecraft",
  ru: "Отчёт проверки промпта Minecraft на искажения",
  "zh-en": "Minecraft Prompt Anti-Drift Report / 防串味报告"
};

export function parseArgs(argv) {
  const opts = {
    prompt: "",
    engine: "kling",
    mode: "i2v",
    issue: "",
    lang: "en",
    json: false,
    help: false
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--json") opts.json = true;
    else if (arg === "--prompt" && argv[i + 1]) opts.prompt = argv[++i];
    else if (arg === "--engine" && argv[i + 1]) opts.engine = argv[++i].toLowerCase();
    else if (arg === "--mode" && argv[i + 1]) opts.mode = argv[++i].toLowerCase();
    else if (arg === "--issue" && argv[i + 1]) opts.issue = argv[++i].toLowerCase();
    else if (arg === "--lang" && argv[i + 1]) opts.lang = normalizeLang(argv[++i]);
  }
  return opts;
}

export function inspectPrompt(rawOpts = {}) {
  const prompt = (rawOpts.prompt || "").trim();
  const lower = prompt.toLowerCase();
  const mode = rawOpts.mode === "t2v" ? "t2v" : "i2v";
  const engine = rawOpts.engine || "kling";
  const issue = rawOpts.issue && ISSUE_PATCHES[rawOpts.issue] ? rawOpts.issue : "";

  const checks = [];

  // 1. Hand & Extruded 16x16x1 Tool Geometry Gate
  const hasSquareHandLock =
    /flat.*4x4|flat.*3x4|square.*hand|4x12x4.*arm|3x12x4.*arm|fingerless.*square|平头正方形|平头方手|4x4平头/.test(lower);
  const mentionsRiskyHands =
    /\b(fingers|five fingers|human hands|手指|五指)\b/.test(lower) &&
    !/no human fingers|zero human fingers|fingerless|无人类五指|严禁.*手指/.test(lower);
  const mentionsSmoothTool =
    /\b(round metal|smooth sword|cylindrical rod|realistic blade|圆棍|圆滑金属)\b/.test(lower) &&
    !/no smooth|never a smooth|严禁圆/.test(lower);
  const mentionsToolWithoutExtrusion =
    /\b(sword|pickaxe|axe|shovel|torch|钻石剑|钻石镐|火把)\b/.test(lower) &&
    !/16x16x1|2x10x2|extruded|stepped|像素挤出|锯齿像素/.test(lower);

  if (mentionsRiskyHands || mentionsSmoothTool || issue === "human-fingers" || issue === "smooth-tools") {
    checks.push({
      gate: "Hand & Extruded Tool Lock / 平头方手与16x16x1像素道具锁",
      status: "FAIL",
      reasonEn:
        "Prompt triggers human fingers or smooth non-voxel tools without locking `flat 4x4 square pixel-block hand ends` and `extruded 16x16x1 stepped pixel-art tool`.",
      reasonZh:
        "提示词易触发真人五指或圆滑写实武器，缺少「4x4平头正方形像素手」与「16x16x1阶梯锯齿立体像素工具」锁定。"
    });
  } else if (!hasSquareHandLock || mentionsToolWithoutExtrusion) {
    checks.push({
      gate: "Hand & Extruded Tool Lock / 平头方手与16x16x1像素道具锁",
      status: "WARN",
      reasonEn:
        "Add `fingerless flat 4x4 square pixel-block hands` and `extruded 16x16x1 pixel-art tool with stepped 90-degree voxel edges`.",
      reasonZh:
        "建议补充「4x4平头正方形像素手截面」与「16x16x1像素挤出厚度锯齿直角工具」，防止长手指或工具圆滑化。"
    });
  } else {
    checks.push({
      gate: "Hand & Extruded Tool Lock / 平头方手与16x16x1像素道具锁",
      status: "PASS",
      reasonEn: "Flat square pixel hands and extruded 16x16x1 voxel item geometry locked.",
      reasonZh: "已锁定平头正方形像素手与16x16x1立体像素工具几何结构。"
    });
  }

  // 2. 8x8 Cubic Head & Pixel Face Gate
  const hasCubicHeadLock =
    /8x8x8.*head|8x8.*pixel face|2x1.*pixel eye|8x8x8.*立方体头|8x8.*像素脸|8x8.*像素五官/.test(lower);
  if (
    issue === "face-morph" ||
    (!hasCubicHeadLock && /\b(boy|girl|man|woman|talking|smiling|crying|男孩|女孩|说话|大笑|哭泣)\b/.test(lower))
  ) {
    checks.push({
      gate: "8x8 Pixel Face & 3D Skin Layer Lock / 8x8像素脸与0.5px外层皮肤锁",
      status: issue === "face-morph" ? "FAIL" : "WARN",
      reasonEn:
        "Human-gendered or emotional words without `sharp 8x8x8 cubic head, flat 8x8 pixel face, +0.5px 3D outer hair layer, zero 3D nose` risk morphing into a human face.",
      reasonZh:
        "包含拟人或情绪词但未锁定「8x8x8直角立方体头 + 纯平8x8像素五官 + 0.5px悬浮3D立体刘海层」，易长出3D真人鼻梁。"
    });
  } else if (!hasCubicHeadLock) {
    checks.push({
      gate: "8x8 Pixel Face & 3D Skin Layer Lock / 8x8像素脸与0.5px外层皮肤锁",
      status: "WARN",
      reasonEn: "Add `sharp 8x8x8 cubic head, flat 8x8 pixel face, +0.5px 3D outer skin layer`.",
      reasonZh: "建议补充「8x8x8直角立方体头、纯平8x8像素五官、+0.5px外层3D皮肤壳」。"
    });
  } else {
    checks.push({
      gate: "8x8 Pixel Face & 3D Skin Layer Lock / 8x8像素脸与0.5px外层皮肤锁",
      status: "PASS",
      reasonEn: "8x8x8 cubic head and 8x8 pixel face grid locked.",
      reasonZh: "已锁定8x8x8直角立方体头与8x8像素面部网格。"
    });
  }

  // 3. Nearest-Neighbor 16x16 Texel & Anti-Roblox/Lego Guard
  const hasTexelLock =
    /16x16|nearest-neighbor|sharp 90-degree|unfiltered.*pixel|邻近采样|16x16像素|90度锋利直角/.test(lower);
  const mentionsRobloxOrLego =
    /\b(cylindrical head|barrel head|c-shaped claw|lego stud|圆桶头|圆柱头|c型爪|乐高颗粒)\b/.test(lower) &&
    !/no roblox|no lego|无roblox|无乐高|严禁roblox|严禁乐高/.test(lower);

  if (issue === "blurry-texels" || issue === "roblox-lego-drift" || mentionsRobloxOrLego) {
    checks.push({
      gate: "16x16 Nearest-Neighbor & Anti-Roblox/Lego Guard / 像素防糊化与防串味锁",
      status: "FAIL",
      reasonEn:
        "Detected blurry texel risk or Roblox/Lego contamination. Must lock `crisp unfiltered 16x16 nearest-neighbor pixel textures, sharp 90-degree cubic corners`.",
      reasonZh:
        "检测到贴图糊化或Roblox圆头/乐高颗粒串味风险，必须声明「清晰无模糊16x16邻近采样像素贴图与90度锋利直角正方体」。"
    });
  } else if (!hasTexelLock) {
    checks.push({
      gate: "16x16 Nearest-Neighbor & Anti-Roblox/Lego Guard / 像素防糊化与防串味锁",
      status: "WARN",
      reasonEn:
        "Missing `crisp 16x16 nearest-neighbor pixel-art textures, sharp 90-degree voxel corners`; model may blur block textures or round off cube edges.",
      reasonZh:
        "缺少「清晰16x16邻近像素贴图、90度直角体素边缘」描述，模型可能将像素块涂抹模糊或圆角化。"
    });
  } else {
    checks.push({
      gate: "16x16 Nearest-Neighbor & Anti-Roblox/Lego Guard / 像素防糊化与防串味锁",
      status: "PASS",
      reasonEn: "16x16 nearest-neighbor pixel grid and 90-degree cubic corners locked.",
      reasonZh: "已锁定16x16邻近像素网格与90度直角正方体边界。"
    });
  }

  // 4. Single-Action Clip Budget Gate
  const chainConnectors = (
    prompt.match(/\b(then|after that|and then|next|suddenly|while also|接着|然后|随后|再|紧接着|一边.*一边)\b/gi) || []
  ).length;
  const verbMatches = (
    prompt.match(
      /\b(walks?|runs?|jumps?|mines?|breaks?|places?|builds?|fights?|swings?|opens?|turns?|explodes?|走|跑|跳|挖|敲碎|放置|建造|战斗|挥动|打开|转身|爆炸)\b/gi
    ) || []
  ).length;

  if (issue === "overload" || chainConnectors >= 2 || verbMatches >= 3) {
    checks.push({
      gate: "Single-Action Clip Budget / 单镜头动作容量",
      status: "FAIL",
      reasonEn: `Detected multi-step action chain (${verbMatches} verbs, ${chainConnectors} connectors). Keep each 4-5s clip to ONE primary voxel action.`,
      reasonZh: `检测到单镜头动作超载（识别到 ${verbMatches} 个动作词、${chainConnectors} 处先后连接词）。请拆分为独立分镜，每镜仅保留 1 个核心动作。`
    });
  } else if (chainConnectors === 1 || verbMatches === 2) {
    checks.push({
      gate: "Single-Action Clip Budget / 单镜头动作容量",
      status: "WARN",
      reasonEn: "Two-part action detected; keep the second part as a simple pixel particle pop or eye shift.",
      reasonZh: "包含两段动作，建议将后半段简化为正方形像素粒子迸发或8x8像素眼神变化。"
    });
  } else {
    checks.push({
      gate: "Single-Action Clip Budget / 单镜头动作容量",
      status: "PASS",
      reasonEn: "Action density fits cleanly inside a single 4-5s generation clip.",
      reasonZh: "单镜头动作密度合理，适合4~5秒高质量生成。"
    });
  }

  // 5. Rigid Voxel Hinge & I2V Anchor Gate
  const hasRigidityLock =
    /rigid|hinge|pivot|rectangular prism|blocky bend|刚性|转轴|长方体|方块折弯/.test(lower);
  if (issue === "noodle-limbs" || issue === "outfit-drift") {
    checks.push({
      gate: "Rigid Voxel Hinge & I2V Anchor / 刚性像素转轴与首帧锚定",
      status: "FAIL",
      reasonEn: ISSUE_PATCHES[issue].fixEn,
      reasonZh: ISSUE_PATCHES[issue].fixZh
    });
  } else if (mode === "t2v" || !hasRigidityLock) {
    checks.push({
      gate: "Rigid Voxel Hinge & I2V Anchor / 刚性像素转轴与首帧锚定",
      status: "WARN",
      reasonEn:
        mode === "t2v"
          ? "Raw T2V risks pixel grid smudging across cuts; prefer First-Frame I2V with `rigid rectangular prism limbs`."
          : "Add `rigid 4x12x4 rectangular prism limbs with mechanical shoulder/hip pivots`.",
      reasonZh:
        mode === "t2v"
          ? "当前为纯文生视频(T2V)，多镜头易导致像素贴图变形；建议改用首帧I2V并声明「刚性长方体转轴四肢」。"
          : "建议补充「刚性长方体方柱四肢与肩髋机械转轴」，防止手臂像面条一样弯曲。"
    });
  } else {
    checks.push({
      gate: "Rigid Voxel Hinge & I2V Anchor / 刚性像素转轴与首帧锚定",
      status: "PASS",
      reasonEn: "Rigid voxel hinge physics and I2V workflow locked.",
      reasonZh: "已锁定刚性体素转轴物理与首帧I2V工作流。"
    });
  }

  const hasFail = checks.some((c) => c.status === "FAIL");
  const hasWarn = checks.some((c) => c.status === "WARN");
  const overallStatus = hasFail ? "FAIL" : hasWarn ? "WARN" : "PASS";

  // Build rescued prompt
  const cleanedEn = prompt
    .replace(/\bwith five fingers\b/gi, "with fingerless flat 4x4 square pixel-block hand ends")
    .replace(/\bround metal sword\b/gi, "extruded 16x16x1 stepped pixel-art diamond sword")
    .replace(/\b(and then|then)\b.*/i, "");

  const rescuedPromptEn = [
    `[${engine.toUpperCase()} I2V]`,
    "An authentic Minecraft voxel character with a sharp 90-degree 8x8x8 cubic head, +0.5px raised 3D outer hair layer, flat 8x8 nearest-neighbor pixel face (2x1 sliding pixel eyes, zero 3D nose), 8x12x4 rectangular prism torso, and rigid 4x12x4 rectangular prism limbs ending in fingerless and clawless flat 4x4 square pixel-block hands.",
    cleanedEn ? `Core single action: ${cleanedEn.trim()}.` : "Core single action: swings an extruded 16x16x1 stepped pixel-art diamond pickaxe into a 16x16x16 diamond ore block.",
    "Crisp unfiltered 16x16 nearest-neighbor pixel textures, Minecraft BSL shader sunlight and warm block light, cubic pixel particles, no human fingers, no blurry bilinear textures, no Roblox cylinder head, no Lego studs."
  ].join(" ");

  const rescuedPromptZh = [
    `【${engine.toUpperCase()} 首帧I2V救场版】`,
    "纯正《我的世界》像素方块小人（90度锋利直角8x8x8像素立方体头、+0.5px外层悬浮3D立体刘海层、纯平8x8邻近像素五官贴图、8x12x4长方体躯干、刚性4x12x4长方体四肢配无手指无钩爪的4x4平头正方形像素手截面），握持16x16x1阶梯锯齿立体像素工具。",
    "单镜头仅执行 1 个核心刚性转轴动作并迸发正方形像素粒子；全程保持清晰无模糊的16x16邻近采样像素网格与BSL体积光影，严禁出现人类五指、圆滑金属武器、贴图模糊、Roblox圆桶头或乐高头顶颗粒。"
  ].join("");

  return {
    overallStatus,
    engine,
    mode,
    issue: issue || null,
    originalPrompt: prompt,
    checks,
    rescuedPromptEn,
    rescuedPromptZh
  };
}

function formatReportMarkdown(rep, rawLang) {
  const lang = normalizeLang(rawLang);
  const useZh = lang === "zh" || lang === "zh-tw" || lang === "zh-en";
  const useEn = lang !== "zh";
  const hdr = DRIFT_HEADERS[lang] || DRIFT_HEADERS.en;
  const lines = [];
  lines.push(`# ${hdr} (${rep.overallStatus})`);
  lines.push("");
  lines.push(`- **Engine**: \`${rep.engine}\` · **Mode**: \`${rep.mode.toUpperCase()}\``);
  if (rep.originalPrompt) {
    lines.push(`- **Original Prompt**: \`${rep.originalPrompt}\``);
  }
  lines.push("");
  lines.push("| Gate | Status | Diagnosis |");
  lines.push("| --- | :---: | --- |");
  for (const c of rep.checks) {
    const diag = lang === "zh" || lang === "zh-tw" ? c.reasonZh : lang === "zh-en" ? `${c.reasonZh} (${c.reasonEn})` : c.reasonEn;
    lines.push(`| ${c.gate} | **${c.status}** | ${diag} |`);
  }
  lines.push("");
  if (useEn) {
    lines.push("## Rescued Prompt (EN)");
    lines.push("```text");
    lines.push(rep.rescuedPromptEn);
    lines.push("```");
    lines.push("");
  }
  if (useZh) {
    lines.push("## 救场重写提示词 (ZH)");
    lines.push("```text");
    lines.push(rep.rescuedPromptZh);
    lines.push("```");
  }
  return lines.join("\n");
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || (!opts.prompt && !opts.issue)) {
    printHelp();
    process.exit(opts.help ? 0 : 1);
  }
  const rep = inspectPrompt(opts);
  if (opts.json) {
    console.log(JSON.stringify(rep, null, 2));
  } else {
    console.log(formatReportMarkdown(rep, opts.lang));
  }
}
