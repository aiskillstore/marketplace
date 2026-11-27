#!/usr/bin/env node
/**
 * render_preview.mjs
 * Authentic 3D Minecraft Voxel & Nearest-Neighbor 16x16 / 8x8 Pixel-Texel Raymarcher.
 *
 * Implements canonical Minecraft pixel-grid proportions (1 pixel = 0.045 world units, 16px block = 0.72 units):
 * - Head:  Sharp 8x8x8 pixel cube + +0.5px 3D Outer Skin Layer (stepped pixel hair/bangs/helmet)
 * - Face:  Exact 8x8 integer texel grid (2x1 white sclera + 1x1 sliding pupil + 2x1 floating brows)
 * - Torso: 8x12x4 pixel rectangular prism with 8x12 nearest-neighbor tunic/armor texels
 * - Limbs: 4x12x4 (Steve Wide) or 3x12x4 (Alex Slim) rectangular prisms with flat 4x4 / 3x4 square hand ends
 * - Tools: True 16x16x1 extruded 3D pixel-art sprites (Diamond Pickaxe, Diamond Sword) with stepped 90° edges
 * - Blocks: 16x16x16 Grass Block, Diamond Ore, TNT Block, Crafting Table, and 14x14x14 Hinged Chest
 * - Mobs:  Canonical armless quadruped Creeper (8x8 black pixel face) & Pink Voxel Axolotl
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import zlib from "node:zlib";
import { execFileSync } from "node:child_process";
import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";
import { fileURLToPath } from "node:url";
import {
  PICKAXE_16,
  SWORD_16,
  DIAMOND_ITEM_16,
  HEART_16,
  lookupToolSpriteColor,
  lookupItemSpriteColor,
  texStone16,
  texStoneBricks16,
  texCobble16,
  texDirt16,
  texGrassTop16,
  texGrassSide16,
  texOakPlanks16,
  texDiamondOre16,
  hasMiningCrack,
  texTntTop16,
  texTntSide16,
  texCraftingTop16,
  texCraftingSide16,
  texPistonSide16,
  texPistonTopSticky16,
  texRedstoneLamp16,
  texDiamondBlock16,
  CREEPER_FACE_8,
  texCreeperSkin
} from "./mc_textures.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const mix = (a, b, t) => a + (b - a) * t;
const smoothstep = (e0, e1, x) => {
  const t = clamp((x - e0) / (e1 - e0), 0, 1);
  return t * t * (3 - 2 * t);
};

function v3(x = 0, y = 0, z = 0) {
  return { x, y, z };
}
const add3 = (a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
const sub3 = (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z });
const mul3 = (a, s) => ({ x: a.x * s, y: a.y * s, z: a.z * s });
const dot3 = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;
const len3 = (a) => Math.hypot(a.x, a.y, a.z);
const norm3 = (a) => {
  const l = len3(a) || 1;
  return { x: a.x / l, y: a.y / l, z: a.z / l };
};
const cross3 = (a, b) => ({
  x: a.y * b.z - a.z * b.y,
  y: a.z * b.x - a.x * b.z,
  z: a.x * b.y - a.y * b.x
});

function rotY(p, ang) {
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  return { x: c * p.x + s * p.z, y: p.y, z: -s * p.x + c * p.z };
}
function rotX(p, ang) {
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  return { x: p.x, y: c * p.y - s * p.z, z: s * p.y + c * p.z };
}
function rotZ(p, ang) {
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  return { x: c * p.x - s * p.y, y: s * p.x + c * p.y, z: p.z };
}

function sdBox(p, b) {
  const qx = Math.abs(p.x) - b.x;
  const qy = Math.abs(p.y) - b.y;
  const qz = Math.abs(p.z) - b.z;
  const ox = Math.max(qx, 0);
  const oy = Math.max(qy, 0);
  const oz = Math.max(qz, 0);
  return Math.hypot(ox, oy, oz) + Math.min(Math.max(qx, qy, qz), 0);
}

function sdRoundBox(p, b, r) {
  return sdBox(p, v3(b.x - r, b.y - r, b.z - r)) - r;
}

function sdRoundedCylinder(p, ra, rb, h) {
  const dx = Math.hypot(p.x, p.z) - ra + rb;
  const dy = Math.abs(p.y) - h + rb;
  const ox = Math.max(dx, 0);
  const oy = Math.max(dy, 0);
  return Math.min(Math.max(dx, dy), 0) + Math.hypot(ox, oy) - rb;
}

function sdLegoCClaw(p, scale = 1.0) {
  const q = mul3(p, 1 / scale);
  const qRot = rotX(q, Math.PI / 2);
  const dOuter = sdRoundedCylinder(qRot, 0.14, 0.025, 0.09);
  const dInner = sdRoundedCylinder(qRot, 0.07, 0.01, 0.16);
  const dSlot = sdRoundBox(sub3(q, v3(0, -0.10, 0)), v3(0.06, 0.10, 0.16), 0.01);
  return Math.max(dOuter, -Math.min(dInner, dSlot)) * scale;
}

// Deterministic hash for nearest-neighbor pixel texel variation
function texHash(ix, iy, iz = 0) {
  let n = (ix * 374761393 + iy * 668265263 + iz * 1442695041) | 0;
  n = ((n ^ (n >> 13)) * 1274126177) | 0;
  return ((n ^ (n >> 16)) >>> 0) / 4294967295;
}

function shadeTexel(rgb, delta) {
  return [
    clamp(rgb[0] + delta, 0, 255),
    clamp(rgb[1] + delta, 0, 255),
    clamp(rgb[2] + delta, 0, 255)
  ];
}

// ---------- 16x16 Extruded Pixel-Art Tool & Item Sprites ----------
const PICKAXE_SPRITE_16 = PICKAXE_16;
const SWORD_SPRITE_16 = SWORD_16;

export function evalVoxelSprite16x16(pLocal, spriteRows, pxSize = 0.026, halfThick = 0.016, mode = "tool") {
  const halfSpan = 8 * pxSize;
  const dBound = sdBox(pLocal, v3(halfSpan + pxSize, halfSpan + pxSize, halfThick + pxSize));
  if (dBound > 0.035) {
    return { d: dBound, color: [51, 224, 208], roughness: 0.2 };
  }

  const gx = clamp(Math.floor((pLocal.x + halfSpan) / pxSize), 0, 15);
  const gy = clamp(Math.floor((halfSpan - pLocal.y) / pxSize), 0, 15);
  const colorFn = mode === "item" ? lookupItemSpriteColor : lookupToolSpriteColor;

  let bestD = 1e9;
  let bestCol = [51, 224, 208];
  for (let dy = -1; dy <= 1; dy++) {
    const ry = gy + dy;
    if (ry < 0 || ry > 15) continue;
    const row = spriteRows[ry];
    for (let dx = -1; dx <= 1; dx++) {
      const rx = gx + dx;
      if (rx < 0 || rx > 15) continue;
      const ch = row[rx];
      if (ch === ".") continue;
      const cx = -halfSpan + (rx + 0.5) * pxSize;
      const cy = halfSpan - (ry + 0.5) * pxSize;
      const dp = sdBox(sub3(pLocal, v3(cx, cy, 0)), v3(pxSize * 0.5, pxSize * 0.5, halfThick));
      if (dp < bestD) {
        bestD = dp;
        bestCol = colorFn(ch) || bestCol;
      }
    }
  }
  if (bestD > 1e8) {
    const dz = Math.max(Math.abs(pLocal.z) - halfThick, 0);
    return { d: Math.hypot(pxSize * 1.25, dz), color: bestCol, roughness: 0.16 };
  }
  return { d: bestD, color: bestCol, roughness: 0.18 };
}

// Authentic 3D Iron-Framed Voxel Lantern (6x9x6 px + top cap + hanging loop)
export function evalLanternSDF(pWorld, pos = v3(0, 0, 0), scale = 1.0) {
  const p = mul3(sub3(pWorld, pos), 1 / scale);
  const dBound = len3(p) - 0.35;
  if (dBound > 0.25) return { d: dBound * scale, color: [51, 65, 85], roughness: 0.3, emissive: 0 };

  const dBody = sdBox(p, v3(0.088, 0.105, 0.088));
  const dCap = sdBox(sub3(p, v3(0, 0.125, 0)), v3(0.062, 0.022, 0.062));
  const dLoop = sdBox(sub3(p, v3(0, 0.162, 0)), v3(0.024, 0.022, 0.012));
  const dMin = Math.min(dBody, dCap, dLoop);

  if (dCap <= dBody || dLoop <= dBody) {
    return { d: dMin * scale, color: [58, 66, 78], roughness: 0.28, emissive: 0 };
  }
  // Iron cage frame along edges & bottom/top rims of lantern body
  const onEdgeX = Math.abs(p.x) > 0.066;
  const onEdgeY = Math.abs(p.y) > 0.082;
  const onEdgeZ = Math.abs(p.z) > 0.066;
  if ((onEdgeX && onEdgeZ) || onEdgeY) {
    return { d: dMin * scale, color: [52, 60, 72], roughness: 0.28, emissive: 0 };
  }
  // Glowing pixel flame core inside iron cage!
  const hot = Math.abs(p.x) < 0.035 && Math.abs(p.y) < 0.045 && Math.abs(p.z) < 0.035;
  return {
    d: dMin * scale,
    color: hot ? [255, 247, 194] : [245, 162, 36],
    roughness: 0.1,
    emissive: hot ? 0.95 : 0.78
  };
}

// Textured Minecraft Pixel Smoke Puff (multi-tone white/silver/slate voxel puff)
export function evalVoxelSmokePuff(pWorld, pos, halfSize = 0.11) {
  const p = sub3(pWorld, pos);
  const d = sdBox(p, v3(halfSize, halfSize, halfSize));
  if (d > 0.15) return { d, color: [241, 245, 249], roughness: 0.4, emissive: 0 };
  const ix = clamp(Math.floor(((p.x + halfSize) / (2 * halfSize)) * 4), 0, 3);
  const iy = clamp(Math.floor(((p.y + halfSize) / (2 * halfSize)) * 4), 0, 3);
  const iz = clamp(Math.floor(((p.z + halfSize) / (2 * halfSize)) * 4), 0, 3);
  const r = texHash(ix, iy, iz);
  const col = r < 0.25 ? [194, 204, 216] : r > 0.7 ? [252, 254, 255] : [228, 234, 242];
  return { d, color: col, roughness: 0.42, emissive: 0.16 };
}

// ---------- Official Mojang-Accurate 8x8 / 8x12 / 4x12 Character Pixel Maps ----------
const STEVE_PX = {
  H: [47, 32, 19],   // dark brown hair
  h: [60, 41, 24],   // mid brown hair
  k: [37, 25, 14],   // deep hair shadow
  S: [185, 134, 101],// warm tan skin
  s: [171, 122, 90], // shaded tan skin
  l: [198, 147, 113],// highlight tan skin
  d: [152, 104, 75], // ear / neck shadow skin
  W: [255, 255, 255],// eye sclera white
  P: [76, 61, 139],  // Steve indigo-violet pupil
  N: [136, 86, 61],  // 2x1 pixel nose
  B: [69, 37, 20],   // Steve classic U-beard dark brown
  b: [55, 29, 15],   // chin beard shadow
  M: [134, 77, 58],  // mouth center inside beard
  T: [0, 168, 175],  // Mojang Steve teal-cyan shirt
  t: [8, 151, 159],  // shaded teal-cyan fold
  C: [0, 182, 189],  // bright teal-cyan highlight
  c: [5, 124, 132],  // dark teal collar / hem shadow
  J: [61, 56, 156],  // Steve indigo-violet jeans
  j: [50, 46, 134],  // shaded jeans seam
  K: [72, 67, 172],  // jeans highlight
  G: [104, 104, 108],// Steve grey shoe upper
  g: [80, 80, 84]    // Steve dark grey shoe sole
};

const STEVE_HEAD_FRONT = [
  "HhHkHhHk", // iy=7 (top)
  "hHkHhkhH", // iy=6
  "HslSSlsH", // iy=5: iconic 1px sideburns at col 0 & 7!
  "sSlSSlSs", // iy=4: brow skin
  "sWPSSPWl", // iy=3: canonical white + indigo eyes!
  "sSsNNsSs", // iy=2: 2x1 brown pixel nose
  "ssBMMBss", // iy=1: U-beard sides + mouth center
  "dsbBBbsd"  // iy=0: iconic chin beard flush at bottom edge!
];

const STEVE_HEAD_SIDE = [
  "HhHkHhHk", // iy=7 (col 0 = front +Z, col 7 = back -Z)
  "hHkHhkhH", // iy=6
  "HhHkhHhk", // iy=5: sideburn across
  "SsHhHkHh", // iy=4: front 2px skin, stepped hair behind
  "SlsddhHk", // iy=3: front 3px skin, 2px ear, back 3px hair
  "SsSdshHk", // iy=2: ear base + back hairline
  "sSlSSssd", // iy=1: jawline skin
  "dsSsSssd"  // iy=0: bottom neck/jaw skin
];

const STEVE_HEAD_BACK = [
  "HhHkHhHk",
  "hHkHhkhH",
  "HkHhkhHh",
  "hkhHhHkH",
  "HhHkHhHk",
  "khHhHkHh",
  "dsSssSsd",
  "dssssssd"
];

const STEVE_TORSO_FRONT = [
  "tTcSScTt", // ty=11: open neck skin col 3,4
  "TTcsscTT", // ty=10: stepped V-collar skin col 3,4
  "tTTccTTt", // ty=9:  dark teal collar base
  "tTTTTTTt", // ty=8
  "tTCttCTt", // ty=7
  "tTTTTTTt", // ty=6
  "tTTttTTt", // ty=5
  "tTTTTTTt", // ty=4
  "tTTccTTt", // ty=3
  "tTTTTTTt", // ty=2
  "tcTttTct", // ty=1
  "JJJccTtT"  // ty=0: signature asymmetric untucked Steve shirt hem!
];

const ALEX_PX = {
  H: [213, 117, 54],  // ginger-orange hair
  h: [191, 97, 38],   // shaded ginger hair
  k: [226, 134, 72],  // highlight ginger hair
  S: [243, 199, 166], // pale ivory-peach skin
  s: [232, 184, 150], // shaded peach skin
  l: [249, 211, 182], // highlight peach skin
  W: [255, 255, 255], // sclera white
  P: [48, 123, 59],   // Alex emerald-green pupil
  M: [207, 125, 114], // Alex 2x1 soft coral-rose pixel mouth
  T: [126, 160, 78],  // olive-moss tunic
  t: [106, 138, 62],  // shaded olive tunic
  c: [84, 112, 46],   // dark olive fold
  B: [82, 58, 40],    // brown belt
  U: [148, 120, 76],  // belt buckle
  J: [108, 83, 64],   // brown trousers
  j: [90, 68, 52],    // shaded trousers
  G: [82, 70, 62],    // grey-brown boots
  g: [64, 54, 48]
};

const ALEX_HEAD_FRONT = [
  "HkHhHkHh", // iy=7
  "hHkHHkHh", // iy=6
  "HHhSSlsH", // iy=5: iconic Alex swept ginger bangs on left!
  "hSlSSlSs", // iy=4
  "sWPSSPWs", // iy=3: white + emerald green eyes
  "sSlSSlSs", // iy=2
  "ssSMMSss", // iy=1: delicate 2x1 coral-pink mouth
  "ssSSSSss"  // iy=0
];

const ALEX_TORSO_FRONT = [
  "tTcSShHt", // ty=11: ginger ponytail hanging over front-right shoulder!
  "TTcssHhT", // ty=10
  "tTTcckht", // ty=9
  "tTTTTtht", // ty=8
  "tTTttTHt", // ty=7: tip of ginger ponytail
  "tTTTTTTt", // ty=6
  "tTTttTTt", // ty=5
  "tTTTTTTt", // ty=4
  "BBBBUBBB", // ty=3: dark brown belt + buckle
  "cBBUBBBc", // ty=2
  "tTTttTTt", // ty=1
  "JJttttJJ"  // ty=0
];

const HOODIE_PX = {
  H: [64, 40, 28],    // espresso hair
  h: [82, 52, 36],
  S: [250, 216, 190], // soft cream-peach skin
  s: [238, 198, 170],
  W: [255, 255, 255],
  P: [45, 34, 48],    // dark berry anime skin eye
  R: [248, 150, 162], // cheek blush pixel
  M: [212, 128, 122],
  T: [122, 222, 162], // pastel matcha hoodie
  t: [98, 198, 140],
  c: [76, 172, 118],
  D: [248, 250, 252], // white hoodie drawstrings
  J: [125, 174, 238], // washed denim
  j: [104, 152, 218],
  G: [244, 246, 250], // white sneakers
  g: [203, 213, 225]
};

const HOODIE_HEAD_FRONT = [
  "HhHHhHHh", // iy=7
  "HHhHHhHH", // iy=6
  "HhSSShHh", // iy=5: cute parted espresso bangs
  "hSSSSSSh", // iy=4
  "SWPSSPWS", // iy=3: top of 2x2 cute skin eyes
  "RPPSSPPR", // iy=2: bottom of eyes + pink cheek blush at col 0 & 7
  "sSSMMSSs", // iy=1
  "sSSSSSSs"  // iy=0
];

const HOODIE_TORSO_FRONT = [
  "tTccccTt",
  "TTDttDTT", // white drawstrings at col 2 & 5!
  "tTDttDTt",
  "TTDttDTT",
  "tTDttDTt",
  "TTtTTtTT",
  "tTccccTt", // kangaroo pocket top
  "TcTTTTcT",
  "TcTTTTcT",
  "cccccccc", // ribbed hem
  "JJJJJJJJ",
  "jJJJJJJj"
];

function evalDynamicExpressionOverlay(ix, iy, expression, baseTheme) {
  if (expression === "smile") return null;
  const white = [255, 255, 255];
  const dark = [20, 24, 34];

  if (expression === "panic" || expression === "tears") {
    if ((ix === 2 || ix === 5) && iy <= 1) {
      return iy === 0 ? [56, 189, 248] : [125, 211, 252];
    }
  }
  if (expression === "shocked" || expression === "panic") {
    if ((iy === 3 || iy === 4) && (ix === 1 || ix === 2 || ix === 5 || ix === 6)) {
      if (iy === 3 && (ix === 2 || ix === 5)) return dark;
      return white;
    }
    if ((iy === 1 || iy === 2) && (ix === 3 || ix === 4)) return [36, 20, 22];
    return null;
  }
  if (expression === "deadpan") {
    if (iy === 4 && (ix === 1 || ix === 2 || ix === 5 || ix === 6)) {
      return baseTheme === "alex" ? [168, 82, 32] : [58, 38, 22];
    }
    if (iy === 3 && (ix === 1 || ix === 5)) return white;
    if (iy === 3 && (ix === 2 || ix === 6)) {
      return baseTheme === "alex" ? [48, 123, 59] : [76, 61, 139];
    }
    return null;
  }
  if (expression === "happy") {
    if (iy === 3 && (ix === 1 || ix === 2 || ix === 5 || ix === 6)) return [42, 32, 28];
    if (iy === 2 && (ix === 1 || ix === 6)) return [248, 142, 156];
    return null;
  }
  return null;
}

// ---------- Canonical 16x16x16 Voxel Block & Prop Evaluator ----------
function blendFlashWhite(col, active) {
  if (!active) return col;
  return [
    Math.round(mix(col[0], 255, 0.72)),
    Math.round(mix(col[1], 255, 0.72)),
    Math.round(mix(col[2], 255, 0.72))
  ];
}

export function evalMinecraftBlockSDF(pWorld, cfg = {}) {
  const {
    pos = v3(0, 0, 0),
    yaw = 0,
    scale = 1.0,
    type = "grass-block",
    cracks = 0,
    flashWhite = false,
    lidAngle = 0
  } = cfg;

  const p = mul3(rotY(sub3(pWorld, pos), -yaw), 1 / scale);
  const halfB = type === "chest-hinged" ? 0.315 : 0.36;
  const dBound = sdBox(p, v3(halfB + 0.06, halfB + 0.24, halfB + 0.06));
  if (dBound > 0.42) {
    return { d: dBound * scale, color: [110, 110, 114], roughness: 0.45, emissive: 0 };
  }

  if (type === "chest-hinged") {
    // 14x14x10 hollow golden-amber oak base + 14x4x14 upward-hinged lid + 2x4x1 beveled silver latch
    const dBaseOuter = sdBox(sub3(p, v3(0, -0.09, 0)), v3(0.315, 0.225, 0.315));
    const dHollow = sdBox(sub3(p, v3(0, 0.06, 0)), v3(0.252, 0.12, 0.252));
    const dBase = Math.max(dBaseOuter, -dHollow);

    const pPivot = sub3(p, v3(0, 0.135, -0.315));
    const pLidLocal = sub3(rotX(pPivot, lidAngle), v3(0, 0.09, 0.315));
    const dLid = sdBox(pLidLocal, v3(0.315, 0.09, 0.315));
    const pLatch = sub3(pLidLocal, v3(0, -0.075, 0.326));
    const dLatch = sdBox(pLatch, v3(0.042, 0.078, 0.018));

    const dChest = Math.min(dBase, dLid, dLatch);
    if (dLatch <= dBase && dLatch <= dLid) {
      const latchCol = pLatch.y > 0.02 ? [226, 232, 238] : pLatch.y < -0.03 ? [142, 148, 156] : [192, 198, 206];
      return { d: dChest * scale, color: latchCol, roughness: 0.22, emissive: 0.04 };
    }
    if (dLid <= dBase) {
      const lx = clamp(Math.floor(((pLidLocal.x + 0.315) / 0.63) * 14), 0, 13);
      const ly = clamp(Math.floor(((pLidLocal.y + 0.09) / 0.18) * 4), 0, 3);
      const lz = clamp(Math.floor(((pLidLocal.z + 0.315) / 0.63) * 14), 0, 13);
      const eX = lx === 0 || lx === 13 ? 1 : 0;
      const eY = ly === 0 || ly === 3 ? 1 : 0;
      const eZ = lz === 0 || lz === 13 ? 1 : 0;
      const isDarkSeam = ly === 0 || eX + eY + eZ >= 2;
      const n = (texHash(lx, ly + 10, lz) - 0.5) * 16;
      const col = isDarkSeam ? [38, 24, 12] : shadeTexel([214, 150, 56], n);
      return { d: dChest * scale, color: col, roughness: 0.42, emissive: 0.04 };
    }
    if (p.y > 0.02 && Math.abs(p.x) < 0.26 && Math.abs(p.z) < 0.26) {
      return { d: dChest * scale, color: [32, 20, 10], roughness: 0.5, emissive: 0 };
    }
    const bx = clamp(Math.floor(((p.x + 0.315) / 0.63) * 14), 0, 13);
    const by = clamp(Math.floor(((p.y + 0.315) / 0.45) * 10), 0, 9);
    const bz = clamp(Math.floor(((p.z + 0.315) / 0.63) * 14), 0, 13);
    const eX = bx === 0 || bx === 13 ? 1 : 0;
    const eY = by === 0 || by === 9 ? 1 : 0;
    const eZ = bz === 0 || bz === 13 ? 1 : 0;
    const isDarkRim = by === 9 || eX + eY + eZ >= 2;
    const n = (texHash(bx, by, bz) - 0.5) * 16;
    const col = isDarkRim ? [38, 24, 12] : shadeTexel([204, 140, 50], n);
    return { d: dChest * scale, color: col, roughness: 0.42, emissive: 0.04 };
  }

  if (type === "sticky-piston") {
    const ext = (cfg.extend ?? 0.35) * 0.36;
    const dBaseP = sdBox(sub3(p, v3(0, -0.09, 0)), v3(0.36, 0.27, 0.36));
    const dRod = sdBox(sub3(p, v3(0, 0.18 + ext * 0.5, 0)), v3(0.09, 0.10 + ext * 0.5, 0.09));
    const pHeadP = sub3(p, v3(0, 0.27 + ext, 0));
    const dHeadP = sdBox(pHeadP, v3(0.36, 0.09, 0.36));
    const dMinP = Math.min(dBaseP, dRod, dHeadP);

    const ux = clamp(Math.floor(((p.x + 0.36) / 0.72) * 16), 0, 15);
    const uz = clamp(Math.floor(((p.z + 0.36) / 0.72) * 16), 0, 15);

    if (dHeadP <= dBaseP && dHeadP <= dRod) {
      if (pHeadP.y > 0.078) {
        return { d: dMinP * scale, color: texPistonTopSticky16(ux, uz), roughness: 0.32, emissive: 0.04 };
      }
      const hy = clamp(12 + Math.floor(((pHeadP.y + 0.09) / 0.18) * 4), 12, 15);
      const fx = Math.abs(p.z) >= Math.abs(p.x) ? ux : uz;
      return { d: dMinP * scale, color: texPistonSide16(fx, hy), roughness: 0.42, emissive: 0 };
    }
    if (dRod <= dBaseP) {
      const ry = Math.floor((p.y + 1.0) / 0.045);
      return { d: dMinP * scale, color: ry % 2 === 0 ? [164, 124, 72] : [132, 98, 56], roughness: 0.4, emissive: 0 };
    }
    const by = clamp(Math.floor(((p.y + 0.36) / 0.54) * 12), 0, 11);
    const fx = Math.abs(p.z) >= Math.abs(p.x) ? ux : uz;
    return { d: dMinP * scale, color: texCobble16(fx, by), roughness: 0.46, emissive: 0 };
  }

  const dBox = sdBox(p, v3(halfB, halfB, halfB));
  const ux = clamp(Math.floor(((p.x + halfB) / (2 * halfB)) * 16), 0, 15);
  const uy = clamp(Math.floor(((p.y + halfB) / (2 * halfB)) * 16), 0, 15);
  const uz = clamp(Math.floor(((p.z + halfB) / (2 * halfB)) * 16), 0, 15);

  const ax = Math.abs(p.x);
  const ay = Math.abs(p.y);
  const az = Math.abs(p.z);
  const isTop = ay >= ax && ay >= az && p.y > 0;
  const isBot = ay >= ax && ay >= az && p.y <= 0;
  const fx = isTop || isBot ? ux : az >= ax ? ux : uz;
  const fy = isTop || isBot ? uz : uy;

  if (type === "grass-block") {
    const col = isTop ? texGrassTop16(ux, uz) : isBot ? texDirt16(ux, uz) : texGrassSide16(fx, uy);
    return { d: dBox * scale, color: col, roughness: 0.46, emissive: 0 };
  }

  if (type === "stone-block") {
    return { d: dBox * scale, color: texStone16(fx, fy), roughness: 0.48, emissive: 0 };
  }

  if (type === "cobble-block") {
    return { d: dBox * scale, color: texCobble16(fx, fy), roughness: 0.48, emissive: 0 };
  }

  if (type === "stone-bricks") {
    return { d: dBox * scale, color: texStoneBricks16(fx, fy), roughness: 0.46, emissive: 0 };
  }

  if (type === "oak-planks") {
    return { d: dBox * scale, color: texOakPlanks16(fx, fy), roughness: 0.44, emissive: 0 };
  }

  if (type === "diamond-ore") {
    if (cracks > 0 && hasMiningCrack(fx, fy, cracks)) {
      return { d: dBox * scale, color: [24, 26, 30], roughness: 0.5, emissive: 0 };
    }
    const ore = texDiamondOre16(fx, fy);
    return { d: dBox * scale, color: ore.col, roughness: ore.rough, emissive: ore.emissive };
  }

  if (type === "tnt-block") {
    const baseCol = isTop || isBot ? texTntTop16(ux, uz) : texTntSide16(fx, uy);
    return {
      d: dBox * scale,
      color: blendFlashWhite(baseCol, flashWhite),
      roughness: flashWhite ? 0.16 : 0.42,
      emissive: flashWhite ? 0.58 : 0
    };
  }

  if (type === "diamond-block") {
    return { d: dBox * scale, color: texDiamondBlock16(fx, fy), roughness: 0.18, emissive: 0.18 };
  }

  if (type === "redstone-lamp") {
    const lRes = texRedstoneLamp16(fx, fy, cfg.lit !== false);
    return { d: dBox * scale, color: lRes.col, roughness: lRes.rough, emissive: lRes.emissive };
  }

  // Default: "crafting-table"
  const cCol = isTop ? texCraftingTop16(ux, uz) : isBot ? texOakPlanks16(ux, uz) : texCraftingSide16(fx, uy);
  return { d: dBox * scale, color: cCol, roughness: 0.44, emissive: 0 };
}

// ---------- Canonical Quadruped Creeper Mob Evaluator ----------
export function evalCreeperSDF(pWorld, cfg = {}) {
  const {
    pos = v3(0, 0, 0),
    yaw = 0,
    headYaw = 0,
    swell = 1.0,
    flashWhite = false
  } = cfg;

  const p = mul3(rotY(sub3(pWorld, pos), -yaw), 1 / swell);
  const dBound = len3(p) - 1.35;
  if (dBound > 0.45) return { d: dBound * swell, color: [88, 168, 76], roughness: 0.44, emissive: 0 };

  const pHead = rotY(sub3(p, v3(0, 0.56, 0)), -headYaw);
  const dHead = sdBox(pHead, v3(0.18, 0.18, 0.18));
  const pBody = sub3(p, v3(0, 0.11, 0));
  const dBody = sdBox(pBody, v3(0.18, 0.27, 0.09));

  const dLegFL = sdBox(sub3(p, v3(-0.09, -0.295, 0.155)), v3(0.088, 0.135, 0.088));
  const dLegFR = sdBox(sub3(p, v3(0.09, -0.295, 0.155)), v3(0.088, 0.135, 0.088));
  const dLegBL = sdBox(sub3(p, v3(-0.09, -0.295, -0.155)), v3(0.088, 0.135, 0.088));
  const dLegBR = sdBox(sub3(p, v3(0.09, -0.295, -0.155)), v3(0.088, 0.135, 0.088));
  const dLegs = Math.min(dLegFL, dLegFR, dLegBL, dLegBR);

  const dMin = Math.min(dHead, dBody, dLegs);
  const gx = Math.floor((p.x + 2.0) / 0.045);
  const gy = Math.floor((p.y + 2.0) / 0.045);
  const gz = Math.floor((p.z + 2.0) / 0.045);
  let col = texCreeperSkin(gx, gy, gz);

  if (dHead <= dBody && dHead <= dLegs && pHead.z > 0.168) {
    const ix = clamp(Math.floor(((pHead.x + 0.18) / 0.36) * 8), 0, 7);
    const iy = clamp(Math.floor(((pHead.y + 0.18) / 0.36) * 8), 0, 7);
    if (CREEPER_FACE_8[7 - iy][ix] === "X") {
      col = [18, 22, 18];
    }
  }

  return {
    d: dMin * swell,
    color: blendFlashWhite(col, flashWhite),
    roughness: flashWhite ? 0.18 : 0.45,
    emissive: flashWhite ? 0.58 : 0
  };
}

// ---------- Canonical Pink Voxel Axolotl Pet Evaluator ----------
export function evalAxolotlSDF(pWorld, cfg = {}) {
  const { pos = v3(0, 0, 0), yaw = 0 } = cfg;
  const p = rotY(sub3(pWorld, pos), -yaw);
  const dBound = len3(p) - 0.72;
  if (dBound > 0.45) return { d: dBound, color: [248, 182, 214], roughness: 0.4, emissive: 0 };

  const pHead = sub3(p, v3(0, 0.03, 0.15));
  const dHead = sdBox(pHead, v3(0.15, 0.095, 0.11));
  const dBody = sdBox(sub3(p, v3(0, 0.0, -0.06)), v3(0.125, 0.078, 0.15));
  const dTailCore = sdBox(sub3(p, v3(0, 0.0, -0.28)), v3(0.022, 0.045, 0.11));
  const dTailFin = sdBox(sub3(p, v3(0, 0.005, -0.30)), v3(0.012, 0.078, 0.13));

  const dFeet = Math.min(
    sdBox(sub3(p, v3(-0.135, -0.085, 0.06)), v3(0.032, 0.048, 0.032)),
    sdBox(sub3(p, v3(0.135, -0.085, 0.06)), v3(0.032, 0.048, 0.032)),
    sdBox(sub3(p, v3(-0.135, -0.085, -0.12)), v3(0.032, 0.048, 0.032)),
    sdBox(sub3(p, v3(0.135, -0.085, -0.12)), v3(0.032, 0.048, 0.032))
  );

  const gillBoxes = [];
  for (const s of [-1, 1]) {
    gillBoxes.push(sdBox(sub3(pHead, v3(s * 0.185, 0.075, -0.02)), v3(0.045, 0.022, 0.014)));
    gillBoxes.push(sdBox(sub3(pHead, v3(s * 0.195, 0.015, -0.02)), v3(0.052, 0.022, 0.014)));
    gillBoxes.push(sdBox(sub3(pHead, v3(s * 0.180, -0.045, -0.02)), v3(0.042, 0.022, 0.014)));
    gillBoxes.push(sdBox(sub3(pHead, v3(s * 0.10, 0.125, -0.02)), v3(0.024, 0.035, 0.014)));
  }
  const dGills = Math.min(...gillBoxes);

  const dMin = Math.min(dHead, dBody, dTailCore, dTailFin, dFeet, dGills);
  if (dGills <= dHead && dGills <= dBody) {
    const tip = Math.abs(pHead.x) > 0.20 || pHead.y > 0.13;
    return { d: dMin, color: tip ? [244, 114, 182] : [219, 39, 119], roughness: 0.36, emissive: 0 };
  }
  if (dTailFin < dTailCore && dTailFin <= dBody) {
    return { d: dMin, color: [244, 114, 182], roughness: 0.36, emissive: 0 };
  }

  const gx = Math.floor((p.x + 1.0) / 0.038);
  const gy = Math.floor((p.y + 1.0) / 0.038);
  const gz = Math.floor((p.z + 1.0) / 0.038);
  const n = (texHash(gx, gy, gz) - 0.5) * 14;
  let col = shadeTexel([251, 194, 222], n);

  if (dHead <= dBody && pHead.z > 0.098) {
    const ix = clamp(Math.floor(((pHead.x + 0.15) / 0.30) * 8), 0, 7);
    const iy = clamp(Math.floor(((pHead.y + 0.095) / 0.19) * 5), 0, 4);
    if (iy === 2 && (ix === 1 || ix === 6)) col = [24, 24, 42];
    else if (iy === 1 && ix >= 3 && ix <= 4) col = [225, 92, 138];
    else if (iy === 2 && (ix === 0 || ix === 7)) col = [244, 114, 182];
  }
  return { d: dMin, color: col, roughness: 0.42, emissive: 0 };
}

// ---------- Canonical Tall Enderman Mob Evaluator ----------
export function evalEndermanSDF(pWorld, cfg = {}) {
  const { pos = v3(0, 0, 0), yaw = 0, jawOpen = 0, carriesGrass = true } = cfg;
  const p = rotY(sub3(pWorld, pos), -yaw);
  const dBound = len3(p) - 1.85;
  if (dBound > 0.45) return { d: dBound, color: [20, 20, 26], roughness: 0.42, emissive: 0 };

  const pHead = sub3(p, v3(0, 0.72 + jawOpen * 0.08, 0));
  const dHead = sdBox(pHead, v3(0.18, 0.18, 0.18));
  const dJaw = jawOpen > 0.05 ? sdBox(sub3(p, v3(0, 0.56, 0)), v3(0.178, 0.045, 0.178)) : 1e9;
  const dBody = sdBox(sub3(p, v3(0, 0.30, 0)), v3(0.16, 0.24, 0.08));

  const armAngle = carriesGrass ? 0.56 : -0.04;
  const pArmL = rotX(sub3(p, v3(-0.205, 0.50, 0)), armAngle);
  const pArmR = rotX(sub3(p, v3(0.205, 0.50, 0)), armAngle);
  const dArms = Math.min(
    sdBox(sub3(pArmL, v3(0, -0.34, 0)), v3(0.042, 0.36, 0.042)),
    sdBox(sub3(pArmR, v3(0, -0.34, 0)), v3(0.042, 0.36, 0.042))
  );
  const dLegs = Math.min(
    sdBox(sub3(p, v3(-0.08, -0.31, 0)), v3(0.044, 0.38, 0.044)),
    sdBox(sub3(p, v3(0.08, -0.31, 0)), v3(0.044, 0.38, 0.044))
  );

  let bestD = Math.min(dHead, dJaw, dBody, dArms, dLegs);
  const gx = Math.floor((p.x + 2.0) / 0.045);
  const gy = Math.floor((p.y + 2.0) / 0.045);
  const gz = Math.floor((p.z + 2.0) / 0.045);
  const n = (texHash(gx, gy, gz) - 0.5) * 10;
  let col = shadeTexel([22, 22, 28], n);
  let emissive = 0;

  if (dHead <= dBody && dHead <= dArms && pHead.z > 0.168) {
    const ix = clamp(Math.floor(((pHead.x + 0.18) / 0.36) * 8), 0, 7);
    const iy = clamp(Math.floor(((pHead.y + 0.18) / 0.36) * 8), 0, 7);
    if (iy === 3 && (ix <= 2 || ix >= 5)) {
      const isPupil = ix === 1 || ix === 6;
      col = isPupil ? [196, 28, 242] : [245, 192, 255];
      emissive = isPupil ? 0.72 : 0.88;
    }
  }

  if (carriesGrass) {
    const grass = evalMinecraftBlockSDF(p, {
      pos: v3(0, 0.06, 0.34),
      scale: 0.46,
      type: "grass-block"
    });
    if (grass.d < bestD) {
      return grass;
    }
  }

  return { d: bestD, color: col, roughness: 0.42, emissive };
}

// ---------- Canonical Minecraft Character SDF Evaluator ----------
export function evalMinecraftAvatarSDF(pWorld, cfg = {}) {
  const {
    pos = v3(0, 0, 0),
    yaw = 0,
    roll = 0,
    waistPitch = 0,
    headYaw = 0,
    headPitch = 0,
    armLPitch = -0.06,
    armRPitch = -0.35,
    legLPitch = 0,
    legRPitch = 0,
    expression = "smile",
    theme = "steve", // "steve" | "alex" | "knight" | "hoodie"
    heldItem = "pickaxe", // "pickaxe" | "sword" | "lantern" | "tnt-mini" | "none"
    hurtTint = false,
    driftMode = "none" // "none" | "human-fingers" | "blurry-noodle" | "roblox-lego"
  } = cfg;

  // "knight" wears 3D Diamond Armor OVER canonical Steve!
  const baseChar = theme === "alex" ? "alex" : theme === "hoodie" ? "hoodie" : "steve";
  const pxMap = baseChar === "alex" ? ALEX_PX : baseChar === "hoodie" ? HOODIE_PX : STEVE_PX;
  const isSlim = baseChar === "alex" || baseChar === "hoodie";

  let p = sub3(pWorld, pos);
  if (roll !== 0) {
    p = add3(rotZ(sub3(p, v3(0, -0.68, 0)), -roll), v3(0, -0.68, 0));
  }
  p = rotY(p, -yaw);

  const dBound = len3(p) - 1.95;
  if (dBound > 0.45) {
    return { d: dBound, color: [0, 0, 0], roughness: 0.4, emissive: 0 };
  }

  let bestD = 1e9;
  let bestCol = pxMap.T;
  let bestRough = 0.42;
  let bestEmissive = 0;

  const addPart = (d, col, rough = 0.42, emissive = 0) => {
    if (d < bestD) {
      bestD = d;
      bestCol = col;
      bestRough = rough;
      bestEmissive = emissive;
    }
  };

  const isBlurryOrToy = driftMode === "blurry-noodle" || driftMode === "roblox-lego";
  const bevel = driftMode === "none" ? 0.001 : 0.045;

  const pWaist = rotX(sub3(p, v3(0, -0.14, 0)), -waistPitch);
  const pUpper = add3(pWaist, v3(0, -0.14, 0));

  // 1. Canonical 8x12x4 Torso (centered at y = 0.13, spans y = -0.14 .. +0.40)
  const pTorso = sub3(pUpper, v3(0, 0.13, 0));
  const dTorso = bevel <= 0.002 ? sdBox(pTorso, v3(0.18, 0.27, 0.09)) : sdRoundBox(pTorso, v3(0.18, 0.27, 0.09), bevel);
  if (dTorso < bestD) {
    if (isBlurryOrToy) {
      addPart(dTorso, [6, 182, 212], 0.28);
    } else {
      const tx = clamp(Math.floor(((pTorso.x + 0.18) / 0.36) * 8), 0, 7);
      const ty = clamp(Math.floor(((pTorso.y + 0.27) / 0.54) * 12), 0, 11);
      const rowIdx = 11 - ty;
      const torsoFront =
        baseChar === "alex" ? ALEX_TORSO_FRONT : baseChar === "hoodie" ? HOODIE_TORSO_FRONT : STEVE_TORSO_FRONT;
      let ch = torsoFront[rowIdx][tx];
      if (pTorso.z <= 0.078) {
        // Back / sides of shirt (no front V-neck skin cutout)
        if (ch === "S" || ch === "s" || ch === "D" || ch === "U") ch = "T";
      }
      addPart(dTorso, pxMap[ch] || pxMap.T, 0.44);
    }
  }

  // +0.3px 3D Diamond Chestplate Shell over Steve when theme === "knight"
  if (theme === "knight" && driftMode === "none") {
    const dPlate = sdBox(sub3(pTorso, v3(0, 0.02, 0)), v3(0.194, 0.25, 0.104));
    if (dPlate < bestD) {
      const tx = clamp(Math.floor(((pTorso.x + 0.194) / 0.388) * 8), 0, 7);
      const ty = clamp(Math.floor(((pTorso.y + 0.23) / 0.50) * 11), 0, 10);
      // Authentic Diamond Chestplate V-neck cutout & pixel bevel trim
      const isNeckCut = pTorso.z > 0.08 && ty >= 9 && (tx === 3 || tx === 4);
      if (!isNeckCut) {
        const isTrim = tx === 0 || tx === 7 || ty === 0 || ty === 10 || (ty === 5 && (tx === 3 || tx === 4));
        const isShine = (tx === 1 || tx === 2) && (ty === 7 || ty === 8);
        const c = isTrim ? [18, 124, 128] : isShine ? [214, 252, 248] : (tx + ty) % 3 === 0 ? [52, 218, 204] : [74, 237, 217];
        addPart(dPlate, c, 0.16, 0.08);
      }
    }
  }

  // 2. Canonical 8x8x8 Cubic Head (centered at y = 0.58, spans y = +0.40 .. +0.76)
  const pHead = rotY(rotX(sub3(pUpper, v3(0, 0.58, 0)), -headPitch), -headYaw);
  let dHead;
  if (driftMode === "roblox-lego") {
    dHead = sdRoundedCylinder(pHead, 0.19, 0.065, 0.185);
    const dStud = sdRoundedCylinder(sub3(pHead, v3(0, 0.22, 0)), 0.10, 0.012, 0.05);
    if (dStud < bestD) addPart(dStud, [250, 204, 21], 0.18);
  } else {
    dHead = bevel <= 0.002 ? sdBox(pHead, v3(0.18, 0.18, 0.18)) : sdRoundBox(pHead, v3(0.18, 0.18, 0.18), bevel);
  }

  if (dHead < bestD) {
    const ix = clamp(Math.floor(((pHead.x + 0.18) / 0.36) * 8), 0, 7);
    const iy = clamp(Math.floor(((pHead.y + 0.18) / 0.36) * 8), 0, 7);
    const iz = clamp(Math.floor(((0.18 - pHead.z) / 0.36) * 8), 0, 7); // 0 = front (+Z), 7 = back (-Z)
    const rowIdx = 7 - iy;

    if (driftMode === "roblox-lego") {
      let c = [245, 205, 48];
      if (pHead.z > 0.15 && iy === 4 && (ix === 2 || ix === 5)) c = [20, 24, 32];
      if (pHead.z > 0.15 && iy === 2 && ix >= 2 && ix <= 5) c = [20, 24, 32];
      addPart(dHead, c, 0.22);
    } else if (driftMode === "blurry-noodle") {
      // Bilinear-blurred smudged face
      let c = [206, 150, 112];
      if (pHead.y > 0.08 || pHead.z < -0.14) c = [68, 44, 26];
      else if (pHead.z > 0.16 && Math.abs(Math.abs(pHead.x) - 0.07) < 0.035 && Math.abs(pHead.y - 0.01) < 0.025) c = [55, 52, 110];
      addPart(dHead, c, 0.35);
    } else {
      // Exact 6-face Mojang 8x8 pixel mapping!
      let hCol = pxMap.S;
      if (pHead.y > 0.172) {
        // Top of head (+Y): 8x8 pixel hair
        const ch = STEVE_HEAD_BACK[iz][ix];
        hCol = pxMap[ch === "d" || ch === "s" ? "H" : ch] || pxMap.H;
      } else if (pHead.y < -0.172) {
        // Underside of chin (-Y)
        hCol = pxMap.d || pxMap.s;
      } else if (pHead.z > 0.172) {
        // Front face (+Z)
        const frontMat =
          baseChar === "alex" ? ALEX_HEAD_FRONT : baseChar === "hoodie" ? HOODIE_HEAD_FRONT : STEVE_HEAD_FRONT;
        const dyn = evalDynamicExpressionOverlay(ix, iy, expression, baseChar);
        if (dyn) {
          hCol = dyn;
        } else {
          const ch = frontMat[rowIdx][ix];
          hCol = pxMap[ch] || pxMap.S;
        }
      } else if (pHead.z < -0.172) {
        // Back face (-Z)
        const ch = STEVE_HEAD_BACK[rowIdx][ix];
        hCol = pxMap[ch] || pxMap.H;
      } else {
        // Left & Right Side faces (±X): iconic stepped Minecraft sideburns + ear + jawline!
        const ch = STEVE_HEAD_SIDE[rowIdx][iz];
        hCol = pxMap[ch] || pxMap.S;
      }
      addPart(dHead, hCol, 0.42);
    }
  }

  // FAIL mode 1: 3D protruding human nose
  if (driftMode === "human-fingers") {
    const dNose = sdRoundBox(sub3(pHead, v3(0, -0.02, 0.21)), v3(0.038, 0.055, 0.065), 0.022);
    addPart(dNose, [224, 152, 116], 0.35);
  }

  // 3. Authentic 3D Outer Head Gear ONLY for Diamond Knight (3D Diamond Helmet) & Cozy Hoodie (3D Headphones)
  // (Canonical Vanilla Steve & Alex have flush 8x8x8 heads with NO protruding helmet slab!)
  if (driftMode === "none" && theme === "knight") {
    // True 3D Minecraft Diamond Helmet (+0.5px shell with open front face cutout + 2px nose-guard bar!)
    const dHelmOuter = sdBox(sub3(pHead, v3(0, 0.02, 0)), v3(0.204, 0.196, 0.204));
    const dHelmInner = sdBox(sub3(pHead, v3(0, -0.02, 0)), v3(0.181, 0.185, 0.181));
    // Carve front visor opening (x in [-0.145, +0.145], y < +0.055, z > 0.10), EXCEPT central 2px nose guard!
    const dVisorCut = sdBox(sub3(pHead, v3(0, -0.075, 0.16)), v3(0.142, 0.125, 0.08));
    const dNoseGuard = sdBox(sub3(pHead, v3(0, 0.025, 0.194)), v3(0.044, 0.045, 0.014));
    const dHelm = Math.min(Math.max(dHelmOuter, -dHelmInner, -dVisorCut), dNoseGuard);
    if (dHelm < bestD) {
      const hx = clamp(Math.floor(((pHead.x + 0.204) / 0.408) * 8), 0, 7);
      const hy = clamp(Math.floor(((pHead.y + 0.176) / 0.392) * 8), 0, 7);
      const isBorder = hy === 7 || hy === 0 || hx === 0 || hx === 7;
      const isShine = hy === 6 && (hx >= 1 && hx <= 3);
      const c = isBorder ? [18, 124, 128] : isShine ? [214, 252, 248] : [74, 237, 217];
      addPart(dHelm, c, 0.14, 0.10);
    }
  } else if (driftMode === "none" && theme === "hoodie") {
    const dCupL = sdBox(sub3(pHead, v3(-0.198, -0.01, 0.0)), v3(0.024, 0.068, 0.062));
    const dCupR = sdBox(sub3(pHead, v3(0.198, -0.01, 0.0)), v3(0.024, 0.068, 0.062));
    const dBand = sdBox(sub3(pHead, v3(0, 0.194, 0.0)), v3(0.198, 0.016, 0.036));
    addPart(Math.min(dCupL, dCupR, dBand), [248, 250, 252], 0.2);
  }

  // 4. Canonical 4x12x4 (Steve, halfW=0.09) or 3x12x4 (Alex, halfW=0.0675) Left & Right Arms
  // Exact Minecraft ModelPlayer pivot: 2px (0.09) below top of torso (y = 0.40 -> pivot y = 0.31), flush at x = ±(0.18 + armHalfW)
  const armHalfW = isSlim ? 0.0675 : 0.09;
  const shoulderX = 0.18 + armHalfW;

  for (const side of [-1, 1]) {
    const pitch = side < 0 ? armLPitch : armRPitch;
    const pShoulder = sub3(pUpper, v3(side * shoulderX, 0.31, 0));
    let pArm = rotX(pShoulder, -pitch);
    if (driftMode === "blurry-noodle") {
      pArm = v3(pArm.x + Math.sin(pArm.y * 7.5) * 0.065 * side, pArm.y, pArm.z);
    }
    const pArmBox = sub3(pArm, v3(0, -0.18, 0)); // spans y = -0.45 .. +0.09 -> top = 0.31 + 0.09 = +0.40 exact!
    const dArm = bevel <= 0.002 ? sdBox(pArmBox, v3(armHalfW, 0.27, 0.09)) : sdRoundBox(pArmBox, v3(armHalfW, 0.27, 0.09), bevel);
    if (dArm < bestD) {
      if (isBlurryOrToy) {
        const ay = clamp(Math.floor(((pArmBox.y + 0.27) / 0.54) * 12), 0, 11);
        addPart(dArm, ay >= 8 ? [6, 182, 212] : driftMode === "roblox-lego" ? [245, 205, 48] : [206, 150, 112], 0.28);
      } else {
        const ay = clamp(Math.floor(((pArmBox.y + 0.27) / 0.54) * 12), 0, 11);
        const ax = clamp(Math.floor(((pArmBox.x + armHalfW) / (2 * armHalfW)) * 4), 0, 3);
        const az = clamp(Math.floor(((pArmBox.z + 0.09) / 0.18) * 4), 0, 3);
        const nArm = (texHash(ax + side * 7, ay, az) - 0.5) * 12;
        // Official Steve has exact 4px sleeve (ay = 8..11) and 8px bare tan arm (ay = 0..7)!
        // Alex has 3px sleeve (ay = 9..11); Hoodie has long hoodie sleeve (ay = 2..11).
        const sleeveStart = baseChar === "hoodie" ? 2 : baseChar === "alex" ? 9 : 8;
        let armCol;
        if (ay >= sleeveStart) {
          armCol = shadeTexel(ay === sleeveStart ? pxMap.c : pxMap.T, nArm * 0.7);
        } else {
          armCol = shadeTexel(ay === 0 ? (pxMap.s || pxMap.S) : pxMap.S, nArm);
        }
        addPart(dArm, armCol, 0.44);
      }
    }

    // 3D Diamond Shoulder Pauldrons on top 5px of arms when theme === "knight"
    if (theme === "knight" && driftMode === "none") {
      const pPauldron = sub3(pArmBox, v3(0, 0.165, 0));
      const dPauldron = sdBox(pPauldron, v3(armHalfW + 0.014, 0.115, 0.104));
      if (dPauldron < bestD) {
        const py = clamp(Math.floor(((pPauldron.y + 0.115) / 0.23) * 5), 0, 4);
        const c = py === 0 || py === 4 ? [18, 124, 128] : py === 3 ? [214, 252, 248] : [74, 237, 217];
        addPart(dPauldron, c, 0.16, 0.08);
      }
    }

    // Drift failure hand modes
    const pHandEnd = sub3(pArm, v3(0, -0.47, 0));
    if (driftMode === "human-fingers") {
      for (let f = -2; f <= 2; f++) {
        const pf = sub3(pHandEnd, v3(f * 0.032, -0.055, 0));
        addPart(sdRoundBox(pf, v3(0.011, 0.055, 0.012), 0.005), pxMap.S, 0.35);
      }
    } else if (driftMode === "roblox-lego") {
      addPart(sdLegoCClaw(sub3(pArm, v3(0, -0.49, 0)), 0.85), [245, 205, 48], 0.2);
    } else if (driftMode === "blurry-noodle" && side === 1) {
      const pSmoothRod = rotX(sub3(pArm, v3(0, -0.39, 0.20)), -1.15);
      addPart(sdRoundedCylinder(pSmoothRod, 0.032, 0.015, 0.28), [186, 200, 218], 0.12);
    }

    // Authentic Extruded 16x16x1 Held Voxel Items (handle passes directly through center of Right 4x4 Hand!)
    if (driftMode === "none" && side === 1 && heldItem !== "none") {
      if (heldItem === "pickaxe" || heldItem === "sword") {
        // Right hand spans pArm.y = -0.45 .. -0.36; anchoring at (0, -0.40, 0.13) seats the oak handle right inside the 4x4 fist!
        const qGrip = sub3(pArm, v3(0.0, -0.40, 0.13));
        const pTool = rotY(rotX(qGrip, -0.28), Math.PI / 2);
        const sprite = heldItem === "sword" ? SWORD_SPRITE_16 : PICKAXE_SPRITE_16;
        const sp = evalVoxelSprite16x16(pTool, sprite, 0.025, 0.016, "tool");
        addPart(sp.d, sp.color, sp.roughness, 0.12);
      } else if (heldItem === "lantern") {
        // Hang lantern vertically downward directly from the bottom of the 4x4 hand (zero gap)!
        const pHandTip = rotX(sub3(pArm, v3(0, -0.43, 0.04)), pitch);
        const lan = evalLanternSDF(pHandTip, v3(0, -0.078, 0.0), 0.78);
        addPart(lan.d, lan.color, lan.roughness, lan.emissive);
      } else if (heldItem === "tnt-mini") {
        const tnt = evalMinecraftBlockSDF(pArm, {
          pos: v3(-0.14, -0.39, 0.22),
          scale: 0.48,
          type: "tnt-block"
        });
        addPart(tnt.d, tnt.color, tnt.roughness, tnt.emissive);
      }
    }
  }

  // 5. Canonical 4x12x4 Flush Left & Right Legs (x = ±0.09, spans y = -0.68 .. -0.14)
  for (const side of [-1, 1]) {
    const pitch = side < 0 ? legLPitch : legRPitch;
    const pHip = sub3(p, v3(side * 0.09, -0.14, 0));
    const pLeg = sub3(rotX(pHip, pitch), v3(0, -0.27, 0));
    const dLeg = bevel <= 0.002 ? sdBox(pLeg, v3(0.09, 0.27, 0.09)) : sdRoundBox(pLeg, v3(0.089, 0.27, 0.09), bevel);
    if (dLeg < bestD) {
      if (isBlurryOrToy) {
        addPart(dLeg, [59, 59, 143], 0.35);
      } else {
        const ly = clamp(Math.floor(((pLeg.y + 0.27) / 0.54) * 12), 0, 11);
        const lx = clamp(Math.floor(((pLeg.x + 0.09) / 0.18) * 4), 0, 3);
        const lz = clamp(Math.floor(((pLeg.z + 0.09) / 0.18) * 4), 0, 3);
        const nLeg = (texHash(lx + side * 11, ly, lz + 5) - 0.5) * 10;
        let legCol;
        if (ly === 0) legCol = pxMap.g;
        else if (ly === 1) legCol = pxMap.G;
        else if (baseChar === "steve" && theme !== "knight" && side === 1 && ly === 11 && pLeg.z > 0.07) {
          // Canonical Steve untucked cyan shirt corner hanging 1px onto right pant top!
          legCol = pxMap.c;
        } else {
          const isInnerSeam = (side === -1 && lx === 3) || (side === 1 && lx === 0);
          legCol = shadeTexel(isInnerSeam ? pxMap.j : pxMap.J, nLeg);
        }
        addPart(dLeg, legCol, 0.45);
      }
    }

    // 3D Diamond Leggings & Diamond Boots when theme === "knight"
    if (theme === "knight" && driftMode === "none") {
      const dGreave = sdBox(sub3(pLeg, v3(0, 0.02, 0)), v3(0.092, 0.24, 0.096));
      const dBoot = sdBox(sub3(pLeg, v3(0, -0.18, 0)), v3(0.098, 0.095, 0.102));
      const dArmorLeg = Math.min(dGreave, dBoot);
      if (dArmorLeg < bestD) {
        const ly = clamp(Math.floor(((pLeg.y + 0.27) / 0.54) * 12), 0, 11);
        const lx = clamp(Math.floor(((pLeg.x + 0.098) / 0.196) * 4), 0, 3);
        const isInner = (side === -1 && lx === 3) || (side === 1 && lx === 0);
        const isTrim = ly === 0 || ly === 3 || ly === 11 || isInner;
        const c = isTrim ? [18, 124, 128] : ly === 2 ? [214, 252, 248] : (lx + ly) % 2 === 0 ? [74, 237, 217] : [52, 216, 202];
        addPart(dArmorLeg, c, 0.18, 0.06);
      }
    }
  }

  if (hurtTint) {
    bestCol = [
      clamp(bestCol[0] * 0.45 + 245 * 0.55, 0, 255),
      clamp(bestCol[1] * 0.25 + 40 * 0.75, 0, 255),
      clamp(bestCol[2] * 0.25 + 40 * 0.75, 0, 255)
    ];
  }

  return { d: bestD, color: bestCol, roughness: bestRough, emissive: bestEmissive };
}

// ---------- Raymarcher & Minecraft BSL / Voxel Floor Shader ----------
export function render3DViewport(width, height, sceneFn, camCfg = {}) {
  const buf = new Uint8Array(width * height * 4);
  const ro = camCfg.ro || v3(0, 0.35, 2.65);
  const ta = camCfg.ta || v3(0, 0.08, 0);
  const fov = camCfg.fov || 1.92;
  const bgTop = camCfg.bgTop || [125, 211, 252];
  const bgBot = camCfg.bgBot || [224, 242, 254];
  const floorY = camCfg.floorY ?? -0.68;
  const floorType = camCfg.floorType || "grass"; // "grass" | "stone" | "oak"
  const warmLight = camCfg.warmLight ?? 0.0;

  const fw = norm3(sub3(ta, ro));
  const rt = norm3(cross3(fw, v3(0, 1, 0)));
  const up = cross3(rt, fw);

  const keyLight = norm3(v3(0.58, 0.82, 0.64));
  const fillLight = norm3(v3(-0.65, 0.35, 0.45));
  const rimLight = norm3(v3(-0.55, 0.52, -0.65));

  const calcNormal = (p, centerDist) => {
    const e = 0.0025;
    const d0 = centerDist ?? sceneFn(p).d;
    const dx = sceneFn(v3(p.x + e, p.y, p.z)).d - d0;
    const dy = sceneFn(v3(p.x, p.y + e, p.z)).d - d0;
    const dz = sceneFn(v3(p.x, p.y, p.z + e)).d - d0;
    return norm3(v3(dx, dy, dz));
  };

  const calcSoftShadow = (orig, dir) => {
    const h1 = sceneFn(add3(orig, mul3(dir, 0.09))).d;
    const h2 = sceneFn(add3(orig, mul3(dir, 0.24))).d;
    return clamp(0.52 + 0.48 * Math.min(h1 * 8.5, h2 * 4.5), 0.52, 1.0);
  };

  for (let py = 0; py < height; py++) {
    const ny = 1 - (2 * (py + 0.5)) / height;
    const vGrad = py / height;
    for (let px = 0; px < width; px++) {
      const nx = ((2 * (px + 0.5)) / width - 1) * (width / height);
      const rd = norm3(add3(add3(mul3(rt, nx), mul3(up, ny)), mul3(fw, fov)));

      let r = mix(bgTop[0], bgBot[0], vGrad);
      let g = mix(bgTop[1], bgBot[1], vGrad);
      let b = mix(bgTop[2], bgBot[2], vGrad);
      // Blocky Minecraft Sky Clouds when ray points upward in outdoor daytime scenes!
      if (rd.y > 0.06 && bgTop[2] > 180) {
        const tc = (2.1 - ro.y) / rd.y;
        if (tc > 0 && tc < 18) {
          const cp = add3(ro, mul3(rd, tc));
          const cx = Math.floor(cp.x / 0.85);
          const cz = Math.floor(cp.z / 0.85);
          if (texHash(cx, cz, 313) > 0.68) {
            const cFade = Math.exp(-0.018 * tc * tc);
            r = mix(r, 252, cFade * 0.85);
            g = mix(g, 254, cFade * 0.85);
            b = mix(b, 255, cFade * 0.85);
          }
        }
      }

      const ocx = ro.x;
      const ocy = ro.y - 0.05;
      const ocz = ro.z;
      const bSphere = ocx * rd.x + ocy * rd.y + ocz * rd.z;
      const cSphere = ocx * ocx + ocy * ocy + ocz * ocz - 2.35 * 2.35;
      const disc = bSphere * bSphere - cSphere;

      let t = disc > 0 ? Math.max(0.18, -bSphere - Math.sqrt(disc)) : 99.0;
      const tMax = disc > 0 ? Math.min(9.5, -bSphere + Math.sqrt(disc)) : 0.0;
      let hit = null;
      if (disc > 0 && tMax > 0.18) {
        for (let step = 0; step < 36; step++) {
          if (t > tMax) break;
          const pos = add3(ro, mul3(rd, t));
          const res = sceneFn(pos);
          if (res.d < 0.0028) {
            hit = { pos, res, t };
            break;
          }
          t += res.d;
        }
      }

      if (hit) {
        const N = calcNormal(hit.pos, hit.res.d);
        const V = mul3(rd, -1);
        const sh = dot3(N, keyLight) > 0 ? calcSoftShadow(add3(hit.pos, mul3(N, 0.012)), keyLight) : 0.52;
        // Authentic Minecraft directional block-face lighting (Top 1.0, Z 0.84, X 0.70) + BSL sun
        const mcFaceFactor = 0.74 + 0.18 * Math.abs(N.y) + 0.08 * Math.abs(N.z);
        const keyDiff = Math.max(0, dot3(N, keyLight)) * sh;
        const fillDiff = Math.max(0, dot3(N, fillLight)) * 0.25;
        const skyAmb = 0.38 + 0.14 * (0.5 + 0.5 * N.y);
        const aoSample = sceneFn(add3(hit.pos, mul3(N, 0.055))).d / 0.055;
        const ao = clamp(0.68 + 0.32 * aoSample, 0.62, 1.0);

        const emissive = hit.res.emissive || 0;
        const lighting = clamp((skyAmb + keyDiff * 0.58 + fillDiff) * mcFaceFactor * ao + emissive, 0, 1.45);

        const H = norm3(add3(keyLight, V));
        const rough = hit.res.roughness ?? 0.42;
        const specPow = rough < 0.22 ? 36 : 16;
        const specStrength = rough < 0.25 ? 0.32 * sh : 0.0;
        const spec = specStrength > 0 ? Math.pow(Math.max(0, dot3(N, H)), specPow) * specStrength : 0;

        const fresnel = rough < 0.25 ? Math.pow(1 - Math.max(0, dot3(N, V)), 3.0) : 0;
        const rim = fresnel * Math.max(0, dot3(N, rimLight)) * 0.18;

        const base = hit.res.color;
        r = clamp(base[0] * lighting + 255 * spec + 245 * rim + warmLight * 28, 0, 255);
        g = clamp(base[1] * lighting + 250 * spec + 245 * rim + warmLight * 16, 0, 255);
        b = clamp(base[2] * lighting + 240 * spec + 255 * rim, 0, 255);
      } else if (rd.y < -0.001 && floorY !== null) {
        const tf = (floorY - ro.y) / rd.y;
        if (tf > 0 && tf < 14.0) {
          const fp = add3(ro, mul3(rd, tf));
          // Exact 16x16 Vanilla Minecraft Floor Textures (1 block = 0.72 units, zero fake grid borders!)
          const blockSize = 0.72;
          const bx = Math.floor(fp.x / blockSize);
          const bz = Math.floor(fp.z / blockSize);
          const ux = clamp(Math.floor(((fp.x / blockSize - bx) + 1) % 1 * 16), 0, 15);
          const uz = clamp(Math.floor(((fp.z / blockSize - bz) + 1) % 1 * 16), 0, 15);
          const uxRot = (ux + Math.abs(bx * 5)) & 15;
          const uzRot = (uz + Math.abs(bz * 7)) & 15;

          let tileCol;
          if (floorType === "stone") {
            tileCol = ((bx + bz) & 3) === 0 ? texCobble16(ux, uz) : texStone16(uxRot, uzRot);
          } else if (floorType === "stone-bricks") {
            tileCol = texStoneBricks16(ux, uz);
          } else if (floorType === "oak") {
            tileCol = texOakPlanks16(ux, uz);
          } else {
            tileCol = texGrassTop16(uxRot, uzRot);
          }

          // Crisp Minecraft voxel sun shadow instead of blurry studio blob
          const floorShadow =
            Math.abs(fp.x) < 1.55 && Math.abs(fp.z) < 1.55
              ? calcSoftShadow(v3(fp.x, floorY + 0.02, fp.z), keyLight)
              : 1.0;
          const fade = Math.exp(-0.045 * tf * tf);
          r = mix(r, clamp(tileCol[0] * floorShadow + warmLight * 26, 0, 255), fade);
          g = mix(g, clamp(tileCol[1] * floorShadow + warmLight * 15, 0, 255), fade);
          b = mix(b, clamp(tileCol[2] * floorShadow, 0, 255), fade);
        }
      }

      const idx = (py * width + px) * 4;
      buf[idx] = r;
      buf[idx + 1] = g;
      buf[idx + 2] = b;
      buf[idx + 3] = 255;
    }
  }
  return buf;
}

// ---------- Pure Node PNG Encoder ----------
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

function pngChunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const typeBuf = Buffer.from(type, "ascii");
  const crcBuf = Buffer.alloc(4);
  crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([len, typeBuf, data, crcBuf]);
}

export function encodePNG(width, height, rgba) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;

  const stride = width * 4;
  const raw = Buffer.alloc((stride + 1) * height);
  for (let y = 0; y < height; y++) {
    const rowStart = y * (stride + 1);
    raw[rowStart] = 0;
    Buffer.from(rgba.buffer, rgba.byteOffset + y * stride, stride).copy(raw, rowStart + 1);
  }
  const idat = zlib.deflateSync(raw, { level: 6 });
  return Buffer.concat([
    signature,
    pngChunk("IHDR", ihdr),
    pngChunk("IDAT", idat),
    pngChunk("IEND", Buffer.alloc(0))
  ]);
}

// ---------- Scene Builders for the 6 Short-Video Cases ----------

// Cave Stone Wall Column + Angled Minecraft Wall Torch (placed far left/back so it NEVER overlaps tools!)
function evalCaveWallWithTorchSDF(pWorld, wallPos = v3(-0.88, -0.10, -0.78)) {
  const pillar = evalMinecraftBlockSDF(pWorld, {
    pos: wallPos,
    scale: 1.0,
    type: "cobble-block"
  });
  const topStone = evalMinecraftBlockSDF(pWorld, {
    pos: v3(wallPos.x, wallPos.y + 0.72, wallPos.z),
    scale: 1.0,
    type: "stone-block"
  });
  const pT = rotX(sub3(pWorld, v3(wallPos.x + 0.08, wallPos.y + 0.56, wallPos.z + 0.42)), -0.38);
  const dStick = sdBox(sub3(pT, v3(0, -0.05, 0)), v3(0.026, 0.13, 0.026));
  const dFlame = sdBox(sub3(pT, v3(0, 0.11, 0)), v3(0.036, 0.038, 0.036));
  let best = pillar.d < topStone.d ? pillar : topStone;
  if (dStick < best.d) best = { d: dStick, color: [146, 102, 52], roughness: 0.44, emissive: 0 };
  if (dFlame < best.d) best = { d: dFlame, color: [255, 224, 92], roughness: 0.08, emissive: 0.95 };
  return best;
}

// Case 01: Diamond Cave Creeper Ambush
export function buildDiamondCreeperScene(shotIndex, phase = 0.5) {
  const caveBgTop = [24, 34, 52];
  const caveBgBot = [45, 58, 82];

  if (shotIndex === 0) {
    // Shot 1: Steve swinging stepped 16x16x1 Diamond Pickaxe forward into glowing 16x16x16 Diamond Ore
    const swing = mix(-1.25, -0.58, Math.sin(phase * Math.PI));
    return {
      cam: {
        ro: v3(0.18, 0.34, 2.58 - phase * 0.12),
        ta: v3(0.02, 0.06, 0),
        fov: 1.92,
        bgTop: caveBgTop,
        bgBot: caveBgBot,
        floorY: -0.68,
        floorType: "stone",
        warmLight: 0.22
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.34, 0, -0.02),
          yaw: 0.48,
          armRPitch: swing,
          armLPitch: -0.18,
          expression: "smile",
          theme: "steve",
          heldItem: "pickaxe"
        });
        const ore = evalMinecraftBlockSDF(p, {
          pos: v3(0.36, -0.32, 0.12),
          yaw: -0.28,
          scale: 0.92,
          type: "diamond-ore",
          cracks: phase
        });
        const wall = evalCaveWallWithTorchSDF(p, v3(-0.92, -0.32, -0.78));
        let best = av.d < ore.d ? av : ore;
        if (wall.d < best.d) best = wall;
        return best;
      }
    };
  }

  if (shotIndex === 1) {
    // Shot 2: Ore shatters into spinning 16x16x1 Diamond Gem item, revealing green Creeper right behind it!
    const bob = Math.sin(phase * Math.PI * 2) * 0.05;
    return {
      cam: {
        ro: v3(0.0, 0.32, 2.68),
        ta: v3(0.0, 0.08, 0),
        fov: 1.92,
        bgTop: caveBgTop,
        bgBot: caveBgBot,
        floorY: -0.68,
        floorType: "stone",
        warmLight: 0.20
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.38, 0, 0.04),
          yaw: 0.36,
          armRPitch: -0.55,
          expression: "shocked",
          theme: "steve",
          heldItem: "pickaxe"
        });
        const creeper = evalCreeperSDF(p, {
          pos: v3(0.36, -0.25, -0.04),
          yaw: -0.35
        });
        const wall = evalCaveWallWithTorchSDF(p, v3(-0.95, -0.32, -0.82));
        const pDrop = rotY(sub3(p, v3(0.0, -0.16 + bob, 0.28)), phase * Math.PI * 2);
        const gem = evalVoxelSprite16x16(pDrop, DIAMOND_ITEM_16, 0.014, 0.014, "item");
        let best = av.d < creeper.d ? av : creeper;
        if (wall.d < best.d) best = wall;
        if (gem.d < best.d) best = { ...gem, emissive: 0.35 };
        return best;
      }
    };
  }

  if (shotIndex === 2) {
    // Shot 3: Creeper flashes white (with visible Creeper face!) and swells in boxy scale; Steve raises arms
    const isFlash = Math.sin(phase * Math.PI * 5) > 0;
    const swell = 1.0 + 0.14 * phase;
    return {
      cam: {
        ro: v3(0.0, 0.30, 2.75),
        ta: v3(0.0, 0.10, 0),
        fov: 1.92,
        bgTop: [45, 58, 78],
        bgBot: [71, 85, 105],
        floorY: -0.68,
        floorType: "stone"
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.36, 0, 0.05),
          yaw: 0.25,
          armLPitch: -2.25,
          armRPitch: -2.25,
          expression: "panic",
          theme: "steve",
          heldItem: "none"
        });
        const creeper = evalCreeperSDF(p, {
          pos: v3(0.34, -0.25, 0.04),
          yaw: -0.28,
          swell,
          flashWhite: isFlash
        });
        return av.d < creeper.d ? av : creeper;
      }
    };
  }

  // Shot 4: Textured Minecraft explosion smoke puffs + Steve in red-tinted hurt knockback + dropped pickaxe
  const spread = mix(0.14, 0.38, phase);
  return {
    cam: {
      ro: v3(0.0, 0.42, 2.78),
      ta: v3(0.0, 0.04, 0),
      fov: 1.92,
      bgTop: caveBgTop,
      bgBot: caveBgBot,
      floorY: -0.68,
      floorType: "stone",
      warmLight: 0.2
    },
    sceneFn: (p) => {
      const av = evalMinecraftAvatarSDF(p, {
        pos: v3(-0.42, -0.04, 0.04),
        yaw: 0.18,
        roll: -0.62,
        armLPitch: -1.45,
        armRPitch: -1.15,
        expression: "panic",
        theme: "steve",
        heldItem: "none",
        hurtTint: true
      });
      const pDroppedPick = rotY(rotZ(sub3(p, v3(-0.02, -0.44, 0.28)), 0.45), phase * Math.PI * 2);
      const pick = evalVoxelSprite16x16(pDroppedPick, PICKAXE_SPRITE_16, 0.024, 0.016, "tool");
      const sm1 = evalVoxelSmokePuff(p, v3(0.36 + spread * 0.25, 0.18 + spread * 0.2, 0), 0.12);
      const sm2 = evalVoxelSmokePuff(p, v3(0.22 - spread * 0.12, 0.34 + spread * 0.15, -0.10), 0.095);
      const sm3 = evalVoxelSmokePuff(p, v3(0.44, -0.10 + spread * 0.15, 0.14), 0.105);
      let best = av;
      if (pick.d < best.d) best = { ...pick, emissive: 0.15 };
      for (const sm of [sm1, sm2, sm3]) {
        if (sm.d < best.d) best = sm;
      }
      return best;
    }
  };
}

// Case 02: Cozy Isometric Voxel Cabin & Lantern Build
export function buildCozyLanternScene(shotIndex, phase = 0.5) {
  const skyTop = shotIndex >= 2 ? [49, 46, 129] : [125, 211, 252];
  const skyBot = shotIndex >= 2 ? [253, 186, 116] : [240, 249, 255];
  const warm = shotIndex >= 2 ? 0.55 : 0.0;

  if (shotIndex === 0) {
    // Shot 1: Alex snapping a 16x16x16 Crafting Table onto the grass/oak cabin corner
    const dropY = mix(0.08, -0.32, smoothstep(0, 0.65, phase));
    return {
      cam: {
        ro: v3(0.55, 0.52, 2.58),
        ta: v3(0.0, 0.04, 0),
        fov: 1.92,
        bgTop: skyTop,
        bgBot: skyBot,
        floorY: -0.68,
        floorType: "grass"
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.34, 0, -0.04),
          yaw: 0.45,
          armLPitch: -0.75,
          armRPitch: -0.85,
          expression: "smile",
          theme: "alex",
          heldItem: "none"
        });
        const table = evalMinecraftBlockSDF(p, {
          pos: v3(0.32, dropY, 0.10),
          yaw: -0.28,
          scale: 0.92,
          type: "crafting-table"
        });
        const wall = evalMinecraftBlockSDF(p, {
          pos: v3(0.58, -0.32, -0.62),
          yaw: -0.28,
          scale: 0.92,
          type: "oak-planks"
        });
        let best = av.d < table.d ? av : table;
        if (wall.d < best.d) best = wall;
        return best;
      }
    };
  }

  if (shotIndex === 1) {
    // Shot 2: Placing and opening a 14x14x14 hinged Chest with 3D silver pixel latch
    const lidOpen = mix(0.05, 0.58, smoothstep(0.15, 0.85, phase));
    return {
      cam: {
        ro: v3(-0.38, 0.46, 2.52),
        ta: v3(0.02, 0.04, 0.04),
        fov: 1.92,
        bgTop: skyTop,
        bgBot: skyBot,
        floorY: -0.68,
        floorType: "oak"
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.36, 0, -0.06),
          yaw: 0.48,
          armRPitch: -0.72,
          expression: "smile",
          theme: "alex",
          heldItem: "none"
        });
        const chest = evalMinecraftBlockSDF(p, {
          pos: v3(0.32, -0.36, 0.12),
          yaw: -0.32,
          scale: 0.94,
          type: "chest-hinged",
          lidAngle: lidOpen
        });
        return av.d < chest.d ? av : chest;
      }
    };
  }

  if (shotIndex === 2) {
    // Shot 3: Raising a 3D iron-framed glowing Voxel Lantern beside the Crafting Table
    return {
      cam: {
        ro: v3(0.20, 0.36, 2.52),
        ta: v3(0, 0.10, 0),
        fov: 1.94,
        bgTop: skyTop,
        bgBot: skyBot,
        floorY: -0.68,
        floorType: "oak",
        warmLight: warm
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.26, 0, 0),
          yaw: 0.32,
          armRPitch: -0.78,
          expression: "happy",
          theme: "alex",
          heldItem: "none"
        });
        const table = evalMinecraftBlockSDF(p, {
          pos: v3(0.38, -0.32, -0.04),
          yaw: -0.25,
          scale: 0.9,
          type: "crafting-table"
        });
        const topLantern = evalLanternSDF(p, v3(0.38, 0.148, -0.04), 0.9);
        let best = av.d < table.d ? av : table;
        if (topLantern.d < best.d) best = topLantern;
        return best;
      }
    };
  }

  // Shot 4: Cozy grass block diorama with Pink Voxel Axolotl & true 16x16x1 Pixel Heart sprite!
  const heartY = mix(0.22, 0.42, phase);
  return {
    cam: {
      ro: v3(0.42, 0.45, 2.58),
      ta: v3(0, 0.04, 0),
      fov: 1.92,
      bgTop: skyTop,
      bgBot: skyBot,
      floorY: -0.68,
      floorType: "grass",
      warmLight: warm
    },
    sceneFn: (p) => {
      const av = evalMinecraftAvatarSDF(p, {
        pos: v3(-0.32, 0, -0.04),
        yaw: 0.35,
        armRPitch: -0.62,
        expression: "happy",
        theme: "alex",
        heldItem: "lantern"
      });
      const axo = evalAxolotlSDF(p, {
        pos: v3(0.32, -0.54, 0.16),
        yaw: -0.45
      });
      const pHeart = rotY(sub3(p, v3(0.32, -0.28 + phase * 0.07, 0.16)), -0.35);
      const heart = evalVoxelSprite16x16(pHeart, HEART_16, 0.011, 0.010, "tool");
      let best = av.d < axo.d ? av : axo;
      if (heart.d < best.d) best = { ...heart, emissive: 0.35 };
      return best;
    }
  };
}

// Case 03: Pro Diamond Builder vs. Noob TNT Prank (Stone-Brick Fortress Floor!)
export function buildProVsNoobTntScene(shotIndex, phase = 0.5) {
  const bgTop = [147, 197, 253];
  const bgBot = [238, 246, 255];

  if (shotIndex === 0) {
    return {
      cam: {
        ro: v3(0, 0.30, 2.82),
        ta: v3(0, 0.06, 0),
        fov: 1.92,
        bgTop,
        bgBot,
        floorY: -0.68,
        floorType: "stone-bricks"
      },
      sceneFn: (p) => {
        const pro = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.38, 0, 0),
          yaw: 0.25,
          armRPitch: -0.68,
          expression: "smile",
          theme: "knight",
          heldItem: "sword"
        });
        const noob = evalMinecraftAvatarSDF(p, {
          pos: v3(0.38, 0, 0),
          yaw: -0.25,
          armLPitch: -0.75,
          armRPitch: -0.75,
          expression: "smile",
          theme: "steve",
          heldItem: "tnt-mini"
        });
        return pro.d < noob.d ? pro : noob;
      }
    };
  }

  if (shotIndex === 1) {
    return {
      cam: {
        ro: v3(0.08, 0.36, 2.85),
        ta: v3(0, 0.0, 0.08),
        fov: 1.92,
        bgTop,
        bgBot,
        floorY: -0.68,
        floorType: "stone-bricks"
      },
      sceneFn: (p) => {
        const pro = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.44, 0, -0.08),
          yaw: 0.35,
          armRPitch: -0.55,
          expression: "shocked",
          theme: "knight",
          heldItem: "sword"
        });
        const noob = evalMinecraftAvatarSDF(p, {
          pos: v3(0.44, 0, -0.08),
          yaw: -0.35,
          armLPitch: -0.85,
          armRPitch: -0.85,
          expression: "smile",
          theme: "steve",
          heldItem: "none"
        });
        const tnt = evalMinecraftBlockSDF(p, {
          pos: v3(0, -0.34, 0.24),
          yaw: 0.18,
          scale: 0.82,
          type: "tnt-block"
        });
        let best = pro.d < noob.d ? pro : noob;
        if (tnt.d < best.d) best = tnt;
        return best;
      }
    };
  }

  if (shotIndex === 2) {
    const isFlash = Math.sin(phase * Math.PI * 5) > 0;
    const swell = 0.84 + 0.15 * phase;
    return {
      cam: {
        ro: v3(0, 0.34, 2.88),
        ta: v3(0, 0.04, 0.08),
        fov: 1.92,
        bgTop: [254, 202, 202],
        bgBot: [254, 242, 242],
        floorY: -0.68,
        floorType: "stone-bricks"
      },
      sceneFn: (p) => {
        const pro = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.45, 0, -0.10),
          yaw: 0.3,
          waistPitch: -0.18,
          armLPitch: -2.15,
          armRPitch: -2.15,
          expression: "panic",
          theme: "knight",
          heldItem: "none"
        });
        const noob = evalMinecraftAvatarSDF(p, {
          pos: v3(0.45, 0, -0.10),
          yaw: -0.3,
          waistPitch: -0.18,
          armLPitch: -2.15,
          armRPitch: -2.15,
          expression: "panic",
          theme: "steve",
          heldItem: "none"
        });
        const tnt = evalMinecraftBlockSDF(p, {
          pos: v3(0, -0.30, 0.24),
          yaw: 0.18,
          scale: swell,
          type: "tnt-block",
          flashWhite: isFlash
        });
        let best = pro.d < noob.d ? pro : noob;
        if (tnt.d < best.d) best = tnt;
        return best;
      }
    };
  }

  return {
    cam: {
      ro: v3(0, 0.28, 2.80),
      ta: v3(0, 0.06, 0),
      fov: 1.92,
      bgTop: [148, 163, 184],
      bgBot: [226, 232, 240],
      floorY: -0.68,
      floorType: "stone-bricks"
    },
    sceneFn: (p) => {
      const pro = evalMinecraftAvatarSDF(p, {
        pos: v3(-0.38, 0, 0),
        yaw: 0.15,
        headYaw: -0.15,
        armLPitch: 0,
        armRPitch: 0,
        expression: "deadpan",
        theme: "knight",
        heldItem: "none"
      });
      const noob = evalMinecraftAvatarSDF(p, {
        pos: v3(0.38, 0, 0),
        yaw: -0.15,
        headYaw: 0.15,
        armLPitch: 0,
        armRPitch: 0,
        expression: "deadpan",
        theme: "steve",
        heldItem: "none"
      });
      const sm1 = evalVoxelSmokePuff(p, v3(0, -0.42, 0.22), 0.115);
      const sm2 = evalVoxelSmokePuff(p, v3(-0.18, -0.48, 0.28), 0.085);
      let best = pro.d < noob.d ? pro : noob;
      if (sm1.d < best.d) best = sm1;
      if (sm2.d < best.d) best = sm2;
      return best;
    }
  };
}

// Case 04: Redstone & Sticky Piston Chain ASMR (`Wan`)
export function buildRedstoneChainScene(shotIndex, phase = 0.5) {
  const darkTop = [22, 30, 46];
  const darkBot = [42, 54, 76];

  if (shotIndex === 0) {
    // Shot 1: Alex flipping lever / igniting glowing crimson redstone trail
    return {
      cam: {
        ro: v3(0.18, 0.42, 2.58),
        ta: v3(0, 0.02, 0),
        fov: 1.92,
        bgTop: darkTop,
        bgBot: darkBot,
        floorY: -0.68,
        floorType: "stone"
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.36, 0, -0.04),
          yaw: 0.42,
          armRPitch: -0.82,
          expression: "smile",
          theme: "alex",
          heldItem: "none"
        });
        const piston = evalMinecraftBlockSDF(p, {
          pos: v3(0.34, -0.32, 0.08),
          yaw: -0.25,
          scale: 0.88,
          type: "sticky-piston",
          extend: 0.05
        });
        // Authentic Redstone Dust cross + pixel wire + Redstone Torch on the stone floor!
        const dWireX = sdBox(sub3(p, v3(-0.02, -0.672, 0.16)), v3(0.28, 0.008, 0.026));
        const dWireZ = sdBox(sub3(p, v3(-0.16, -0.672, 0.16)), v3(0.026, 0.008, 0.11));
        const dTorchStick = sdBox(sub3(p, v3(-0.24, -0.59, 0.18)), v3(0.020, 0.08, 0.020));
        const dTorchHead = sdBox(sub3(p, v3(-0.24, -0.49, 0.18)), v3(0.026, 0.026, 0.026));
        let best = av.d < piston.d ? av : piston;
        const dWire = Math.min(dWireX, dWireZ);
        if (dWire < best.d) {
          const rx = Math.floor((p.x + 2.0) / 0.025);
          const rz = Math.floor((p.z + 2.0) / 0.025);
          const bright = ((rx * 7 + rz * 13) & 3) === 0;
          best = { d: dWire, color: bright ? [255, 72, 72] : [185, 20, 20], roughness: 0.25, emissive: 0.78 };
        }
        if (dTorchStick < best.d) best = { d: dTorchStick, color: [132, 94, 52], roughness: 0.55, emissive: 0 };
        if (dTorchHead < best.d) best = { d: dTorchHead, color: [255, 64, 64], roughness: 0.15, emissive: 0.92 };
        return best;
      }
    };
  }

  if (shotIndex === 1) {
    // Shot 2: Sticky piston extends its slime head, snapping a glowing Diamond Block upward
    const ext = smoothstep(0.1, 0.8, phase) * 0.65;
    return {
      cam: {
        ro: v3(0.35, 0.48, 2.55),
        ta: v3(0.05, 0.06, 0),
        fov: 1.92,
        bgTop: darkTop,
        bgBot: darkBot,
        floorY: -0.68,
        floorType: "stone"
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.42, 0, -0.06),
          yaw: 0.45,
          armRPitch: -0.55,
          expression: "smile",
          theme: "alex",
          heldItem: "none"
        });
        const piston = evalMinecraftBlockSDF(p, {
          pos: v3(0.28, -0.36, 0.08),
          yaw: -0.25,
          scale: 0.84,
          type: "sticky-piston",
          extend: ext
        });
        const dBlock = evalMinecraftBlockSDF(p, {
          pos: v3(0.28, 0.24 + ext * 0.28, 0.08),
          yaw: -0.25,
          scale: 0.72,
          type: "diamond-block"
        });
        let best = av.d < piston.d ? av : piston;
        if (dBlock.d < best.d) best = dBlock;
        return best;
      }
    };
  }

  if (shotIndex === 2) {
    // Shot 3: Redstone Lamps cascade open in warm amber glow
    return {
      cam: {
        ro: v3(-0.15, 0.38, 2.62),
        ta: v3(0, 0.08, 0),
        fov: 1.92,
        bgTop: [45, 38, 68],
        bgBot: [92, 64, 48],
        floorY: -0.68,
        floorType: "stone",
        warmLight: 0.55
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.38, 0, 0),
          yaw: 0.35,
          armRPitch: -0.75,
          expression: "happy",
          theme: "alex",
          heldItem: "none"
        });
        const lamp1 = evalMinecraftBlockSDF(p, { pos: v3(0.26, -0.32, 0.06), yaw: -0.2, scale: 0.82, type: "redstone-lamp", lit: true });
        const lamp2 = evalMinecraftBlockSDF(p, { pos: v3(0.26, 0.28, 0.06), yaw: -0.2, scale: 0.82, type: "redstone-lamp", lit: phase > 0.3 });
        let best = av.d < lamp1.d ? av : lamp1;
        if (lamp2.d < best.d) best = lamp2;
        return best;
      }
    };
  }

  // Shot 4: Diamond Block pedestal & glowing Lantern completion loop
  return {
    cam: {
      ro: v3(0.18, 0.40, 2.58),
      ta: v3(0, 0.06, 0),
      fov: 1.92,
      bgTop: darkTop,
      bgBot: [56, 72, 98],
      floorY: -0.68,
      floorType: "stone",
      warmLight: 0.35
    },
    sceneFn: (p) => {
      const av = evalMinecraftAvatarSDF(p, {
        pos: v3(-0.36, 0, 0),
        yaw: 0.3,
        armRPitch: -0.95,
        expression: "happy",
        theme: "alex",
        heldItem: "lantern"
      });
      const ped = evalMinecraftBlockSDF(p, { pos: v3(0.32, -0.32, 0.08), yaw: -0.3, scale: 0.86, type: "diamond-block" });
      return av.d < ped.d ? av : ped;
    }
  };
}

// Case 05: Enderman Midnight Grass Block Heist (`Sora`)
export function buildEndermanHeistScene(shotIndex, phase = 0.5) {
  const nightTop = [17, 24, 39];
  const nightBot = [49, 46, 129];

  if (shotIndex === 0) {
    // Shot 1: Steve on lawn while tall Enderman with glowing purple eyes appears behind him
    return {
      cam: {
        ro: v3(0, 0.34, 2.82),
        ta: v3(0, 0.12, 0),
        fov: 1.92,
        bgTop: nightTop,
        bgBot: nightBot,
        floorY: -0.68,
        floorType: "grass"
      },
      sceneFn: (p) => {
        const st = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.36, 0, 0.06),
          yaw: 0.22,
          armRPitch: -0.35,
          expression: "smile",
          theme: "steve",
          heldItem: "none"
        });
        const en = evalEndermanSDF(p, {
          pos: v3(0.36, 0.0, -0.06),
          yaw: -0.28,
          carriesGrass: false
        });
        return st.d < en.d ? st : en;
      }
    };
  }

  if (shotIndex === 1) {
    // Shot 2: Enderman plucks a 16x16x16 Grass Block up in its thin stick arms
    return {
      cam: {
        ro: v3(0.08, 0.36, 2.82),
        ta: v3(0, 0.10, 0),
        fov: 1.92,
        bgTop: nightTop,
        bgBot: nightBot,
        floorY: -0.68,
        floorType: "grass"
      },
      sceneFn: (p) => {
        const st = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.40, 0, 0.04),
          yaw: 0.42,
          armRPitch: -0.65,
          expression: "shocked",
          theme: "steve",
          heldItem: "none"
        });
        const en = evalEndermanSDF(p, {
          pos: v3(0.34, 0.0, 0.04),
          yaw: -0.35,
          carriesGrass: true
        });
        return st.d < en.d ? st : en;
      }
    };
  }

  if (shotIndex === 2) {
    // Shot 3: Eye contact! Enderman vibrates & opens cubic jaw while clutching the Grass Block
    const shake = Math.sin(phase * Math.PI * 8) * 0.03;
    return {
      cam: {
        ro: v3(0.0, 0.32, 2.75),
        ta: v3(0.04, 0.16, 0),
        fov: 1.92,
        bgTop: [46, 16, 101],
        bgBot: [88, 28, 135],
        floorY: -0.68,
        floorType: "grass"
      },
      sceneFn: (p) => {
        const st = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.40, 0, 0.06),
          yaw: 0.38,
          armLPitch: -2.1,
          armRPitch: -2.1,
          expression: "panic",
          theme: "steve",
          heldItem: "none"
        });
        const en = evalEndermanSDF(p, {
          pos: v3(0.32 + shake, 0.0, 0.04),
          yaw: -0.32,
          jawOpen: 0.75,
          carriesGrass: true
        });
        return st.d < en.d ? st : en;
      }
    };
  }

  // Shot 4: Purple portal cubes pop as Enderman teleports onto oak block holding Grass Block
  return {
    cam: {
      ro: v3(0, 0.42, 2.88),
      ta: v3(0, 0.14, 0),
      fov: 1.92,
      bgTop: nightTop,
      bgBot: nightBot,
      floorY: -0.68,
      floorType: "oak"
    },
    sceneFn: (p) => {
      const st = evalMinecraftAvatarSDF(p, {
        pos: v3(-0.38, 0, 0.06),
        yaw: 0.18,
        expression: "deadpan",
        theme: "steve",
        heldItem: "none"
      });
      const en = evalEndermanSDF(p, {
        pos: v3(0.34, 0.0, -0.04),
        yaw: -0.25,
        carriesGrass: true
      });
      // Authentic multi-speck Ender teleport pixel particles around Enderman
      const p1 = sdBox(sub3(p, v3(0.08, 0.34 + phase * 0.12, 0.18)), v3(0.018, 0.018, 0.018));
      const p2 = sdBox(sub3(p, v3(0.52, 0.52 - phase * 0.10, 0.12)), v3(0.015, 0.015, 0.015));
      const p3 = sdBox(sub3(p, v3(0.16, -0.12 + phase * 0.14, 0.24)), v3(0.014, 0.014, 0.014));
      const dPart = Math.min(p1, p2, p3);
      let best = st.d < en.d ? st : en;
      if (dPart < best.d) best = { d: dPart, color: [216, 114, 255], roughness: 0.1, emissive: 0.85 };
      return best;
    }
  };
}

// Case 06: Rainy Night Pink Voxel Axolotl Shelter (`Runway`)
export function buildAxolotlShelterScene(shotIndex, phase = 0.5) {
  const rainTop = [30, 58, 138];
  const rainBot = [96, 165, 250];
  const cozyTop = [67, 20, 7];
  const cozyBot = [251, 146, 60];

  if (shotIndex === 0) {
    // Shot 1: Pink Voxel Axolotl in blue pixel rain
    return {
      cam: {
        ro: v3(0.15, 0.12, 2.15),
        ta: v3(0, -0.35, 0),
        fov: 1.92,
        bgTop: rainTop,
        bgBot: rainBot,
        floorY: -0.68,
        floorType: "stone"
      },
      sceneFn: (p) => {
        const ax = evalAxolotlSDF(p, { pos: v3(0.0, -0.52, 0.08), yaw: 0.38 });
        const dRain1 = sdBox(sub3(p, v3(-0.28, -0.05 - phase * 0.25, 0.12)), v3(0.014, 0.08, 0.014));
        const dRain2 = sdBox(sub3(p, v3(0.28, 0.12 - phase * 0.25, -0.05)), v3(0.014, 0.08, 0.014));
        const dRain = Math.min(dRain1, dRain2);
        if (dRain < ax.d) return { d: dRain, color: [147, 197, 253], roughness: 0.1, emissive: 0.45 };
        return ax;
      }
    };
  }

  if (shotIndex === 1) {
    // Shot 2: Pastel 3D-Hoodie avatar lowers warm glowing Lantern beside the Axolotl
    return {
      cam: {
        ro: v3(0.22, 0.30, 2.55),
        ta: v3(0, 0.0, 0),
        fov: 1.92,
        bgTop: rainTop,
        bgBot: [147, 197, 253],
        floorY: -0.68,
        floorType: "stone",
        warmLight: 0.35
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.32, 0, 0),
          yaw: 0.38,
          waistPitch: 0.22,
          armRPitch: -0.95,
          expression: "smile",
          theme: "hoodie",
          heldItem: "lantern"
        });
        const ax = evalAxolotlSDF(p, { pos: v3(0.32, -0.54, 0.16), yaw: -0.45 });
        return av.d < ax.d ? av : ax;
      }
    };
  }

  if (shotIndex === 2) {
    // Shot 3: Warm oak cabin with glowing Redstone Lamp & happy Axolotl
    return {
      cam: {
        ro: v3(-0.18, 0.34, 2.52),
        ta: v3(0, 0.04, 0),
        fov: 1.92,
        bgTop: cozyTop,
        bgBot: cozyBot,
        floorY: -0.68,
        floorType: "oak",
        warmLight: 0.65
      },
      sceneFn: (p) => {
        const av = evalMinecraftAvatarSDF(p, {
          pos: v3(-0.34, 0, -0.04),
          yaw: 0.35,
          armRPitch: -0.65,
          expression: "happy",
          theme: "hoodie",
          heldItem: "none"
        });
        const ax = evalAxolotlSDF(p, { pos: v3(0.18, -0.54, 0.24), yaw: -0.42 });
        const lamp = evalMinecraftBlockSDF(p, { pos: v3(0.48, -0.32, -0.34), yaw: -0.2, scale: 0.78, type: "redstone-lamp", lit: true });
        let best = av.d < ax.d ? av : ax;
        if (lamp.d < best.d) best = lamp;
        return best;
      }
    };
  }

  // Shot 4: Cozy loop with floating pixel heart sprite above the Pink Axolotl
  return {
    cam: {
      ro: v3(0.28, 0.38, 2.55),
      ta: v3(0, 0.04, 0),
      fov: 1.92,
      bgTop: cozyTop,
      bgBot: cozyBot,
      floorY: -0.68,
      floorType: "oak",
      warmLight: 0.65
    },
    sceneFn: (p) => {
      const av = evalMinecraftAvatarSDF(p, {
        pos: v3(-0.30, 0, 0),
        yaw: 0.32,
        armRPitch: -0.75,
        expression: "happy",
        theme: "hoodie",
        heldItem: "lantern"
      });
      const ax = evalAxolotlSDF(p, { pos: v3(0.30, -0.54, 0.16), yaw: -0.42 });
      const pHeart = rotY(sub3(p, v3(0.30, -0.28 + phase * 0.07, 0.16)), -0.35);
      const heart = evalVoxelSprite16x16(pHeart, HEART_16, 0.011, 0.010, "tool");
      let best = av.d < ax.d ? av : ax;
      if (heart.d < best.d) best = { ...heart, emissive: 0.35 };
      return best;
    }
  };
}

export function buildRenderTasks() {
  const studioCam = {
    ro: v3(0, 0.22, 2.96),
    ta: v3(0, 0.05, 0),
    fov: 2.38,
    bgTop: [186, 230, 253],
    bgBot: [240, 249, 255],
    floorY: -0.68,
    floorType: "grass"
  };

  const objCam = {
    ro: v3(0, 0.36, 2.22),
    ta: v3(0, -0.12, 0),
    fov: 1.95,
    bgTop: [186, 230, 253],
    bgBot: [241, 245, 249],
    floorY: -0.68,
    floorType: "stone"
  };

  const tasks = [];

  // 1. 3-View Turnaround
  for (const [fname, yaw] of [
    ["turn_front.png", 0.0],
    ["turn_3q.png", 0.68],
    ["turn_side.png", 1.52]
  ]) {
    tasks.push({
      name: fname,
      w: 420,
      h: 520,
      run: () =>
        render3DViewport(
          420,
          520,
          (p) =>
            evalMinecraftAvatarSDF(p, {
              yaw,
              armRPitch: -0.68,
              theme: "steve",
              expression: "smile",
              heldItem: "pickaxe"
            }),
          studioCam
        )
    });
  }

  // 2. 4-Panel Voxel Blocks, Extruded Tools & Mobs Showcase
  tasks.push({
    name: "obj_1_ore_grass.png",
    w: 320,
    h: 420,
    run: () =>
      render3DViewport(
        320,
        420,
        (p) => {
          const b1 = evalMinecraftBlockSDF(p, { pos: v3(-0.36, -0.32, -0.04), yaw: 0.52, scale: 0.82, type: "grass-block" });
          const b2 = evalMinecraftBlockSDF(p, { pos: v3(0.36, -0.32, 0.08), yaw: -0.45, scale: 0.84, type: "diamond-ore" });
          return b1.d < b2.d ? b1 : b2;
        },
        objCam
      )
  });

  tasks.push({
    name: "obj_2_tnt_chest.png",
    w: 320,
    h: 420,
    run: () =>
      render3DViewport(
        320,
        420,
        (p) => {
          const b1 = evalMinecraftBlockSDF(p, { pos: v3(-0.37, -0.32, 0.04), yaw: 0.45, scale: 0.82, type: "tnt-block" });
          const b2 = evalMinecraftBlockSDF(p, {
            pos: v3(0.37, -0.36, 0.06),
            yaw: -0.42,
            scale: 0.88,
            type: "chest-hinged",
            lidAngle: 0.52
          });
          return b1.d < b2.d ? b1 : b2;
        },
        objCam
      )
  });

  tasks.push({
    name: "obj_3_extruded_tools.png",
    w: 320,
    h: 420,
    run: () =>
      render3DViewport(
        320,
        420,
        (p) => {
          const pPick = rotY(rotZ(sub3(p, v3(-0.28, -0.02, 0.08)), 0.15), 0.32);
          const pick = evalVoxelSprite16x16(pPick, PICKAXE_SPRITE_16, 0.036, 0.025);
          const pSword = rotY(rotZ(sub3(p, v3(0.30, -0.02, 0.08)), -0.15), -0.32);
          const sword = evalVoxelSprite16x16(pSword, SWORD_SPRITE_16, 0.036, 0.025);
          return pick.d < sword.d ? { ...pick, emissive: 0.15 } : { ...sword, emissive: 0.15 };
        },
        objCam
      )
  });

  tasks.push({
    name: "obj_4_creeper_axolotl.png",
    w: 320,
    h: 420,
    run: () =>
      render3DViewport(
        320,
        420,
        (p) => {
          const cr = evalCreeperSDF(p, { pos: v3(-0.24, -0.25, 0), yaw: 0.38 });
          const ax = evalAxolotlSDF(p, { pos: v3(0.34, -0.54, 0.22), yaw: -0.45 });
          return cr.d < ax.d ? cr : ax;
        },
        { ...objCam, ro: v3(0, 0.28, 2.28), ta: v3(0, 0.02, 0), floorType: "grass" }
      )
  });

  // 3. 4-Way Anti-Drift Comparison
  for (const [fname, dMode, expr] of [
    ["drift_1_fingers.png", "human-fingers", "shocked"],
    ["drift_2_blurry.png", "blurry-noodle", "deadpan"],
    ["drift_3_roblox_lego.png", "roblox-lego", "deadpan"],
    ["drift_4_locked.png", "none", "smile"]
  ]) {
    tasks.push({
      name: fname,
      w: 320,
      h: 420,
      run: () =>
        render3DViewport(
          320,
          420,
          (p) =>
            evalMinecraftAvatarSDF(p, {
              yaw: 0.36,
              armLPitch: -0.45,
              armRPitch: -0.68,
              driftMode: dMode,
              expression: expr,
              theme: "steve",
              heldItem: "pickaxe"
            }),
          { ...studioCam, ro: v3(0, 0.24, 2.88), ta: v3(0, 0.06, 0) }
        )
    });
  }

  // 4. Classic Minecraft Asset Library Thumbnails (6 Characters/Mobs + 8 Voxel Blocks/Items)
  const libCharCam = { ...studioCam, ro: v3(0, 0.24, 2.92), ta: v3(0, 0.06, 0) };
  const charPresets = [
    ["lib_char_steve.png", (p) => evalMinecraftAvatarSDF(p, { yaw: 0.42, armLPitch: 0.18, armRPitch: -0.62, legLPitch: -0.18, legRPitch: 0.18, theme: "steve", heldItem: "pickaxe" })],
    ["lib_char_alex.png", (p) => evalMinecraftAvatarSDF(p, { yaw: -0.40, armLPitch: -0.24, armRPitch: 0.24, legLPitch: 0.20, legRPitch: -0.20, theme: "alex", heldItem: "none" })],
    ["lib_char_knight.png", (p) => evalMinecraftAvatarSDF(p, { yaw: 0.40, armLPitch: 0.15, armRPitch: -0.62, theme: "knight", heldItem: "sword" })],
    ["lib_char_hoodie.png", (p) => evalMinecraftAvatarSDF(p, { yaw: -0.38, armLPitch: -0.22, armRPitch: 0.18, theme: "hoodie", expression: "smile", heldItem: "none" })],
    ["lib_mob_creeper.png", (p) => evalCreeperSDF(p, { pos: v3(0, -0.25, 0), yaw: 0.40 })],
    ["lib_mob_enderman.png", (p) => evalEndermanSDF(p, { pos: v3(0, -0.02, 0), yaw: -0.36, carriesGrass: true })]
  ];
  for (const [fname, fn] of charPresets) {
    tasks.push({ name: fname, w: 240, h: 300, run: () => render3DViewport(240, 300, fn, libCharCam) });
  }

  const singleObjCam = { ...objCam, ro: v3(0, 0.28, 1.82), ta: v3(0, -0.24, 0) };
  const objPresets = [
    ["lib_obj_grass.png", (p) => evalMinecraftBlockSDF(p, { pos: v3(0, -0.32, 0), yaw: 0.58, scale: 0.95, type: "grass-block" })],
    ["lib_obj_diamond_ore.png", (p) => evalMinecraftBlockSDF(p, { pos: v3(0, -0.32, 0), yaw: -0.52, scale: 0.95, type: "diamond-ore" })],
    ["lib_obj_tnt.png", (p) => evalMinecraftBlockSDF(p, { pos: v3(0, -0.32, 0), yaw: 0.52, scale: 0.95, type: "tnt-block" })],
    ["lib_obj_crafting_table.png", (p) => evalMinecraftBlockSDF(p, { pos: v3(0, -0.32, 0), yaw: -0.52, scale: 0.95, type: "crafting-table" })],
    ["lib_obj_chest.png", (p) => evalMinecraftBlockSDF(p, { pos: v3(0, -0.36, 0), yaw: -0.45, scale: 1.0, type: "chest-hinged", lidAngle: 0.52 })],
    ["lib_obj_piston.png", (p) => evalMinecraftBlockSDF(p, { pos: v3(0, -0.34, 0), yaw: 0.52, scale: 0.92, type: "sticky-piston", extend: 0.45 })],
    ["lib_obj_pickaxe.png", (p) => { const sp = evalVoxelSprite16x16(rotY(rotZ(sub3(p, v3(0, -0.18, 0.05)), 0.12), 0.28), PICKAXE_SPRITE_16, 0.042, 0.028); return { ...sp, emissive: 0.15 }; }],
    ["lib_obj_sword.png", (p) => { const sp = evalVoxelSprite16x16(rotY(rotZ(sub3(p, v3(0, -0.18, 0.05)), -0.12), -0.28), SWORD_SPRITE_16, 0.042, 0.028); return { ...sp, emissive: 0.15 }; }]
  ];
  for (const [fname, fn] of objPresets) {
    tasks.push({ name: fname, w: 220, h: 220, run: () => render3DViewport(220, 220, fn, singleObjCam) });
  }

  // 5. Keyframes & 24-frame animation loops for all 6 cases
  const suites = [
    ["creeper", buildDiamondCreeperScene],
    ["cozy", buildCozyLanternScene],
    ["tnt", buildProVsNoobTntScene],
    ["redstone", buildRedstoneChainScene],
    ["enderman", buildEndermanHeistScene],
    ["axolotl", buildAxolotlShelterScene]
  ];

  for (const [prefix, builder] of suites) {
    for (let s = 0; s < 4; s++) {
      tasks.push({
        name: `${prefix}_shot_${s}.png`,
        w: 360,
        h: 640,
        run: () => {
          const { cam, sceneFn } = builder(s, 0.55);
          return render3DViewport(360, 640, sceneFn, cam);
        }
      });
    }
    let frameIdx = 0;
    for (let s = 0; s < 4; s++) {
      for (let f = 0; f < 6; f++) {
        const phase = (f + 0.5) / 6;
        const idx = frameIdx++;
        tasks.push({
          name: `${prefix}_anim_${String(idx).padStart(2, "0")}.png`,
          w: 270,
          h: 480,
          run: () => {
            const { cam, sceneFn } = builder(s, phase);
            return render3DViewport(270, 480, sceneFn, cam);
          }
        });
      }
    }
  }

  // 6. Three 16-Frame Pure Voxel Block & Item Seamless Loops (280x220 each)
  for (let f = 0; f < 16; f++) {
    const phase = f / 16;
    const fStr = String(f).padStart(2, "0");

    // Loop A: Hinged Chest opening + popping spinning extruded 16x16x1 Diamond Pickaxe & Sword
    tasks.push({
      name: `objloop_chest_${fStr}.png`,
      w: 280,
      h: 220,
      run: () => {
        const openT = Math.sin(phase * Math.PI);
        const riseY = mix(-0.22, 0.32, smoothstep(0.08, 0.82, openT));
        const spin = phase * Math.PI * 2;
        return render3DViewport(
          280,
          220,
          (p) => {
            const chest = evalMinecraftBlockSDF(p, {
              pos: v3(0, -0.40, -0.04),
              yaw: -0.38,
              scale: 0.92,
              type: "chest-hinged",
              lidAngle: openT * 0.72
            });
            const pPick = rotY(rotZ(sub3(p, v3(-0.22 * openT, riseY, 0.18)), 0.18), spin);
            const pick = evalVoxelSprite16x16(pPick, PICKAXE_SPRITE_16, 0.025, 0.018);
            const pSword = rotY(rotZ(sub3(p, v3(0.22 * openT, riseY + 0.03, 0.18)), -0.18), -spin);
            const sword = evalVoxelSprite16x16(pSword, SWORD_SPRITE_16, 0.025, 0.018);
            let best = chest;
            if (openT > 0.14 && pick.d < best.d) best = { ...pick, emissive: 0.22 };
            if (openT > 0.14 && sword.d < best.d) best = { ...sword, emissive: 0.22 };
            return best;
          },
          {
            ro: v3(0.10, 0.34, 2.22),
            ta: v3(0, -0.02, 0),
            fov: 2.05,
            bgTop: [125, 211, 252],
            bgBot: [240, 249, 255],
            floorY: -0.68,
            floorType: "oak",
            warmLight: 0.25 * openT
          }
        );
      }
    });

    // Loop B: Sticky Piston pushing glowing 16x16x16 Diamond Ore to trigger Redstone Lamp
    tasks.push({
      name: `objloop_piston_${fStr}.png`,
      w: 280,
      h: 220,
      run: () => {
        const wave = Math.sin(phase * Math.PI);
        const ext = smoothstep(0.1, 0.85, wave) * 0.65;
        const lit = ext > 0.35;
        return render3DViewport(
          280,
          220,
          (p) => {
            const piston = evalMinecraftBlockSDF(p, {
              pos: v3(-0.34, -0.36, 0.04),
              yaw: 0.38,
              scale: 0.78,
              type: "sticky-piston",
              extend: ext
            });
            const ore = evalMinecraftBlockSDF(p, {
              pos: v3(-0.34, 0.18 + ext * 0.28, 0.04),
              yaw: 0.38,
              scale: 0.68,
              type: "diamond-ore"
            });
            const lamp = evalMinecraftBlockSDF(p, {
              pos: v3(0.36, -0.32, 0.04),
              yaw: -0.35,
              scale: 0.84,
              type: "redstone-lamp",
              lit
            });
            const dWire = sdBox(sub3(p, v3(0, -0.66, 0.24)), v3(0.38, 0.018, 0.045));
            let best = piston.d < ore.d ? piston : ore;
            if (lamp.d < best.d) best = lamp;
            if (dWire < best.d) {
              best = {
                d: dWire,
                color: lit ? [248, 58, 58] : [128, 28, 28],
                roughness: 0.2,
                emissive: lit ? 0.85 : 0.15
              };
            }
            return best;
          },
          {
            ro: v3(0, 0.38, 2.18),
            ta: v3(0, -0.06, 0),
            fov: 2.05,
            bgTop: [22, 30, 48],
            bgBot: lit ? [78, 56, 44] : [38, 48, 68],
            floorY: -0.68,
            floorType: "stone",
            warmLight: lit ? 0.45 : 0.0
          }
        );
      }
    });

    // Loop C: Primed 16x16x16 TNT Block flashing white, swelling, and bursting into cubic voxel smoke
    tasks.push({
      name: `objloop_tnt_${fStr}.png`,
      w: 280,
      h: 220,
      run: () => {
        const exploded = phase >= 0.68;
        const fuseP = clamp(phase / 0.68, 0, 1);
        const isFlash = !exploded && (f % 3 === 1 || f === 9 || f === 10);
        const swell = 0.92 + fuseP * 0.22;
        const burst = clamp((phase - 0.68) / 0.32, 0, 1);
        return render3DViewport(
          280,
          220,
          (p) => {
            if (!exploded) {
              return evalMinecraftBlockSDF(p, {
                pos: v3(0, -0.30, 0.04),
                yaw: 0.48 + fuseP * 0.12,
                scale: swell,
                type: "tnt-block",
                flashWhite: isFlash
              });
            }
            const rSpread = mix(0.14, 0.42, burst);
            const sSize = mix(0.14, 0.075, burst);
            const puffs = [
              evalVoxelSmokePuff(p, v3(-rSpread, -0.18 + burst * 0.22, 0.08), sSize),
              evalVoxelSmokePuff(p, v3(rSpread, -0.14 + burst * 0.26, -0.06), sSize * 0.9),
              evalVoxelSmokePuff(p, v3(0.04, 0.02 + burst * 0.30, 0.12), sSize * 1.05),
              evalVoxelSmokePuff(p, v3(-0.12, -0.38, -rSpread * 0.8), sSize * 0.85),
              evalVoxelSmokePuff(p, v3(0.18, -0.36, rSpread * 0.8), sSize * 0.85)
            ];
            let bestPuff = puffs[0];
            for (const pf of puffs) if (pf.d < bestPuff.d) bestPuff = pf;
            return bestPuff;
          },
          {
            ro: v3(0, 0.34, 2.08),
            ta: v3(0, -0.16, 0),
            fov: 2.05,
            bgTop: exploded && burst < 0.3 ? [127, 29, 29] : [30, 41, 59],
            bgBot: [51, 65, 85],
            floorY: -0.68,
            floorType: "stone"
          }
        );
      }
    });
  }

  return tasks;
}

export async function renderRawPanelSetParallel(tmpDir, force = false, filterPrefix = "") {
  fs.mkdirSync(tmpDir, { recursive: true });
  const allTasks = buildRenderTasks();
  const pendingIndices = [];
  for (let i = 0; i < allTasks.length; i++) {
    if (filterPrefix && !allTasks[i].name.startsWith(filterPrefix)) continue;
    const outPath = path.join(tmpDir, allTasks[i].name);
    if (force || !fs.existsSync(outPath) || fs.statSync(outPath).size <= 1000) {
      pendingIndices.push(i);
    }
  }
  if (pendingIndices.length === 0) return;

  const workerCount = Math.min(os.cpus().length || 4, 8, pendingIndices.length);
  const chunks = Array.from({ length: workerCount }, () => []);
  pendingIndices.forEach((taskIdx, i) => {
    chunks[i % workerCount].push(taskIdx);
  });

  const thisFile = fileURLToPath(import.meta.url);
  await Promise.all(
    chunks.map(
      (indices) =>
        new Promise((resolve, reject) => {
          const w = new Worker(thisFile, {
            workerData: { tmpDir, indices }
          });
          w.on("exit", (code) => {
            if (code === 0) resolve();
            else reject(new Error(`Render worker exited with code ${code}`));
          });
          w.on("error", reject);
        })
    )
  );
}

export function buildBoardsManifest(rawDir) {
  const showcaseDir = path.join(ROOT, "assets", "showcase");
  const libCharDir = path.join(ROOT, "assets", "library", "characters");
  const libObjDir = path.join(ROOT, "assets", "library", "objects");
  const creeperDir = path.join(ROOT, "examples", "diamond-creeper-ambush", "assets");
  const cozyDir = path.join(ROOT, "examples", "cozy-lantern-build", "assets");
  const tntDir = path.join(ROOT, "examples", "pro-builder-vs-noob-tnt", "assets");
  const redstoneDir = path.join(ROOT, "examples", "redstone-chain-asmr", "assets");
  const endermanDir = path.join(ROOT, "examples", "enderman-block-heist", "assets");
  const axolotlDir = path.join(ROOT, "examples", "axolotl-rainy-shelter", "assets");

  for (const d of [showcaseDir, libCharDir, libObjDir, creeperDir, cozyDir, tntDir, redstoneDir, endermanDir, axolotlDir]) {
    fs.mkdirSync(d, { recursive: true });
  }

  return {
    rootDir: ROOT,
    rawDir,
    turnaround: {
      outZh: path.join(showcaseDir, "steve_alex_turnaround_sheet.zh.png"),
      outEn: path.join(showcaseDir, "steve_alex_turnaround_sheet.en.png"),
      outDefault: [
        path.join(showcaseDir, "steve_alex_turnaround_sheet.png"),
        path.join(creeperDir, "steve_alex_turnaround_sheet.png")
      ],
      views: [
        { file: "turn_front.png", labelZh: "正面 0°", labelEn: "Front 0°" },
        { file: "turn_3q.png", labelZh: "斜侧 45°", labelEn: "3/4 View 45°" },
        { file: "turn_side.png", labelZh: "侧面 90°", labelEn: "Profile 90°" }
      ]
    },
    objects: {
      outZh: path.join(showcaseDir, "voxel_blocks_and_mobs_sheet.zh.png"),
      outEn: path.join(showcaseDir, "voxel_blocks_and_mobs_sheet.en.png"),
      outDefault: path.join(showcaseDir, "voxel_blocks_and_mobs_sheet.png"),
      panels: [
        { file: "obj_1_ore_grass.png", labelZh: "草方块 & 钻石矿", labelEn: "Grass & Diamond Ore", r: 16, g: 185, b: 129 },
        { file: "obj_2_tnt_chest.png", labelZh: "TNT & 储物箱", labelEn: "TNT & Hinged Chest", r: 245, g: 158, b: 11 },
        { file: "obj_3_extruded_tools.png", labelZh: "挤出像素镐 & 剑", labelEn: "16x16x1 Pickaxe & Sword", r: 14, g: 165, b: 233 },
        { file: "obj_4_creeper_axolotl.png", labelZh: "苦力怕 & 美西螈", labelEn: "Creeper & Pink Axolotl", r: 168, g: 85, b: 247 }
      ]
    },
    drift: {
      outZh: path.join(showcaseDir, "drift_rescue_comparison.zh.png"),
      outEn: path.join(showcaseDir, "drift_rescue_comparison.en.png"),
      outDefault: path.join(showcaseDir, "drift_rescue_comparison.png"),
      panels: [
        { file: "drift_1_fingers.png", labelZh: "× 真人手指 / 鼻子", labelEn: "× Human Fingers / Nose", r: 225, g: 29, b: 72 },
        { file: "drift_2_blurry.png", labelZh: "× 贴图糊化 / 圆棍", labelEn: "× Blurry / Round Rod", r: 217, g: 119, b: 6 },
        { file: "drift_3_roblox_lego.png", labelZh: "× 圆桶头 / 乐高爪", labelEn: "× Cylinder / Lego Claw", r: 124, g: 58, b: 237 },
        { file: "drift_4_locked.png", labelZh: "✓ 标准 Minecraft 像素", labelEn: "✓ Minecraft Voxel Lock", r: 5, g: 150, b: 105 }
      ]
    },
    library: {
      charSheetZh: path.join(showcaseDir, "classic_characters_lineup.zh.png"),
      charSheetEn: path.join(showcaseDir, "classic_characters_lineup.en.png"),
      charSheetDefault: path.join(showcaseDir, "classic_characters_lineup.png"),
      objSheetZh: path.join(showcaseDir, "classic_objects_atlas.zh.png"),
      objSheetEn: path.join(showcaseDir, "classic_objects_atlas.en.png"),
      objSheetDefault: path.join(showcaseDir, "classic_objects_atlas.png"),
      characters: [
        { raw: "lib_char_steve.png", out: path.join(libCharDir, "char_steve.png"), labelZh: "矿工 Steve", labelEn: "Classic Steve" },
        { raw: "lib_char_alex.png", out: path.join(libCharDir, "char_alex.png"), labelZh: "建筑师 Alex", labelEn: "Slim Alex" },
        { raw: "lib_char_knight.png", out: path.join(libCharDir, "char_knight.png"), labelZh: "钻石甲大佬", labelEn: "Diamond Knight" },
        { raw: "lib_char_hoodie.png", out: path.join(libCharDir, "char_hoodie.png"), labelZh: "3D卫衣小人", labelEn: "Cozy Hoodie" },
        { raw: "lib_mob_creeper.png", out: path.join(libCharDir, "mob_creeper.png"), labelZh: "苦力怕", labelEn: "Creeper" },
        { raw: "lib_mob_enderman.png", out: path.join(libCharDir, "mob_enderman.png"), labelZh: "抱草块末影人", labelEn: "Enderman" }
      ],
      objects: [
        { raw: "lib_obj_grass.png", out: path.join(libObjDir, "block_grass.png"), labelZh: "草方块", labelEn: "Grass Block" },
        { raw: "lib_obj_diamond_ore.png", out: path.join(libObjDir, "block_diamond_ore.png"), labelZh: "钻石矿石", labelEn: "Diamond Ore" },
        { raw: "lib_obj_tnt.png", out: path.join(libObjDir, "block_tnt.png"), labelZh: "TNT炸药", labelEn: "TNT Block" },
        { raw: "lib_obj_crafting_table.png", out: path.join(libObjDir, "block_crafting_table.png"), labelZh: "工作台", labelEn: "Crafting Table" },
        { raw: "lib_obj_chest.png", out: path.join(libObjDir, "prop_chest.png"), labelZh: "银锁储物箱", labelEn: "Hinged Chest" },
        { raw: "lib_obj_piston.png", out: path.join(libObjDir, "prop_piston.png"), labelZh: "粘性活塞", labelEn: "Sticky Piston" },
        { raw: "lib_obj_pickaxe.png", out: path.join(libObjDir, "item_diamond_pickaxe.png"), labelZh: "像素钻石镐", labelEn: "Diamond Pickaxe" },
        { raw: "lib_obj_sword.png", out: path.join(libObjDir, "item_diamond_sword.png"), labelZh: "像素钻石剑", labelEn: "Diamond Sword" }
      ]
    },
    heroReel: {
      gifPath: path.join(showcaseDir, "minecraft_shorts_reel.gif"),
      mp4Path: path.join(showcaseDir, "minecraft_shorts_reel.mp4"),
      sources: [
        path.join(creeperDir, "diamond_creeper_ambush.mp4"),
        path.join(cozyDir, "cozy_lantern_build.mp4"),
        path.join(tntDir, "pro_builder_vs_noob_tnt.mp4"),
        path.join(endermanDir, "enderman_block_heist.mp4")
      ]
    },
    objectLoops: [
      {
        prefix: "objloop_chest",
        gifPath: path.join(showcaseDir, "chest_loot_loop.gif"),
        mp4Path: path.join(showcaseDir, "chest_loot_loop.mp4")
      },
      {
        prefix: "objloop_piston",
        gifPath: path.join(showcaseDir, "piston_ore_loop.gif"),
        mp4Path: path.join(showcaseDir, "piston_ore_loop.mp4")
      },
      {
        prefix: "objloop_tnt",
        gifPath: path.join(showcaseDir, "tnt_blast_loop.gif"),
        mp4Path: path.join(showcaseDir, "tnt_blast_loop.mp4")
      }
    ],
    cases: [
      {
        prefix: "creeper",
        sheetZh: path.join(creeperDir, "storyboard_contact_sheet.zh.png"),
        sheetEn: path.join(creeperDir, "storyboard_contact_sheet.en.png"),
        sheetDefault: path.join(creeperDir, "storyboard_contact_sheet.png"),
        gifPath: path.join(creeperDir, "diamond_creeper_ambush.gif"),
        mp4Path: path.join(creeperDir, "diamond_creeper_ambush.mp4"),
        shots: [
          { labelZh: "01 · 挥镐敲钻石矿", labelEn: "01 · Mine Diamond Ore", chatZh: "出钻石了?!", chatEn: "Diamonds?!", bubbleX: 115, bubbleY: 36, savePath: path.join(creeperDir, "shot_01_mine.png") },
          { labelZh: "02 · 矿碎现苦力怕", labelEn: "02 · Creeper Reveal", chatZh: "嘶——", chatEn: "Tssss...", bubbleX: 212, bubbleY: 56, savePath: path.join(creeperDir, "shot_02_reveal.png") },
          { labelZh: "03 · 白光闪烁膨胀", labelEn: "03 · White Fuse Swell", chatZh: "快跑!!", chatEn: "RUN!!", bubbleX: 102, bubbleY: 36, savePath: path.join(creeperDir, "shot_03_swell.png") },
          { labelZh: "04 · 方块烟雾击飞", labelEn: "04 · Voxel Blast Loop", chatZh: "重生点见...", chatEn: "Respawn...", bubbleX: 142, bubbleY: 72, savePath: path.join(creeperDir, "shot_04_blast.png") }
        ]
      },
      {
        prefix: "cozy",
        sheetZh: path.join(cozyDir, "cozy_storyboard_sheet.zh.png"),
        sheetEn: path.join(cozyDir, "cozy_storyboard_sheet.en.png"),
        sheetDefault: path.join(cozyDir, "cozy_storyboard_sheet.png"),
        gifPath: path.join(cozyDir, "cozy_lantern_build.gif"),
        mp4Path: path.join(cozyDir, "cozy_lantern_build.mp4"),
        shots: [
          { labelZh: "01 · 放置工作台", labelEn: "01 · Snap Crafting Table", chatZh: "搭个小木屋!", chatEn: "Build time!", bubbleX: 116, bubbleY: 38 },
          { labelZh: "02 · 开启银锁木箱", labelEn: "02 · Open Hinged Chest", chatZh: "强迫症舒适", chatEn: "Crisp snap!", bubbleX: 118, bubbleY: 38 },
          { labelZh: "03 · 点亮BSL灯笼", labelEn: "03 · BSL Lantern Glow", chatZh: "开启光影!", chatEn: "Shader ON!", bubbleX: 132, bubbleY: 36 },
          { labelZh: "04 · 美西螈治愈循环", labelEn: "04 · Pink Axolotl Loop", chatZh: "今日份治愈", chatEn: "Cozy home", bubbleX: 122, bubbleY: 38 }
        ]
      },
      {
        prefix: "tnt",
        sheetZh: path.join(tntDir, "tnt_storyboard_sheet.zh.png"),
        sheetEn: path.join(tntDir, "tnt_storyboard_sheet.en.png"),
        sheetDefault: path.join(tntDir, "tnt_storyboard_sheet.png"),
        gifPath: path.join(tntDir, "pro_builder_vs_noob_tnt.gif"),
        mp4Path: path.join(tntDir, "pro_builder_vs_noob_tnt.mp4"),
        shots: [
          { labelZh: "01 · 大佬 vs 抱TNT萌新", labelEn: "01 · Pro vs. Noob TNT", chatZh: "别乱动!", chatEn: "Don't touch!", bubbleX: 102, bubbleY: 38 },
          { labelZh: "02 · 萌新拍下TNT", labelEn: "02 · Noob Places TNT", chatZh: "手滑了...", chatEn: "oops.", bubbleX: 215, bubbleY: 38 },
          { labelZh: "03 · TNT白光闪烁", labelEn: "03 · Primed TNT Flash", chatZh: "等一下?!", chatEn: "WAIT!", bubbleX: 160, bubbleY: 36 },
          { labelZh: "04 · 同步死鱼眼", labelEn: "04 · Deadpan Stare", chatZh: "已踢出服", chatEn: "Banned.", bubbleX: 160, bubbleY: 38 }
        ]
      },
      {
        prefix: "redstone",
        sheetZh: path.join(redstoneDir, "redstone_storyboard_sheet.zh.png"),
        sheetEn: path.join(redstoneDir, "redstone_storyboard_sheet.en.png"),
        sheetDefault: path.join(redstoneDir, "redstone_storyboard_sheet.png"),
        gifPath: path.join(redstoneDir, "redstone_chain_asmr.gif"),
        mp4Path: path.join(redstoneDir, "redstone_chain_asmr.mp4"),
        shots: [
          { labelZh: "01 · 点亮红石线路", labelEn: "01 · Ignite Redstone", chatZh: "通电!", chatEn: "Power ON!", bubbleX: 118, bubbleY: 38 },
          { labelZh: "02 · 活塞顶起钻石块", labelEn: "02 · Sticky Piston Push", chatZh: "丝滑卡扣", chatEn: "Snap!", bubbleX: 118, bubbleY: 38 },
          { labelZh: "03 · 红石灯逐格亮起", labelEn: "03 · Lamp Cascade", chatZh: "多米诺亮灯", chatEn: "Cascade!", bubbleX: 122, bubbleY: 38 },
          { labelZh: "04 · 钻石展台收尾", labelEn: "04 · Pedestal Loop", chatZh: "极度舒适", chatEn: "Clean loop", bubbleX: 122, bubbleY: 38 }
        ]
      },
      {
        prefix: "enderman",
        sheetZh: path.join(endermanDir, "enderman_storyboard_sheet.zh.png"),
        sheetEn: path.join(endermanDir, "enderman_storyboard_sheet.en.png"),
        sheetDefault: path.join(endermanDir, "enderman_storyboard_sheet.png"),
        gifPath: path.join(endermanDir, "enderman_block_heist.gif"),
        mp4Path: path.join(endermanDir, "enderman_block_heist.mp4"),
        shots: [
          { labelZh: "01 · 身后现末影人", labelEn: "01 · Enderman Behind", chatZh: "总觉得凉飕飕", chatEn: "Who's there?", bubbleX: 108, bubbleY: 38 },
          { labelZh: "02 · 顺走一块草方块", labelEn: "02 · Grass Block Heist", chatZh: "我的草坪?!", chatEn: "My lawn?!", bubbleX: 108, bubbleY: 38 },
          { labelZh: "03 · 对视张嘴震动", labelEn: "03 · Eye Contact Stare", chatZh: "别看眼睛!", chatEn: "Don't look!", bubbleX: 108, bubbleY: 38 },
          { labelZh: "04 · 瞬移抱块循环", labelEn: "04 · Teleport Loop", chatZh: "礼貌怪盗", chatEn: "Polite thief", bubbleX: 108, bubbleY: 38 }
        ]
      },
      {
        prefix: "axolotl",
        sheetZh: path.join(axolotlDir, "axolotl_storyboard_sheet.zh.png"),
        sheetEn: path.join(axolotlDir, "axolotl_storyboard_sheet.en.png"),
        sheetDefault: path.join(axolotlDir, "axolotl_storyboard_sheet.png"),
        gifPath: path.join(axolotlDir, "axolotl_rainy_shelter.gif"),
        mp4Path: path.join(axolotlDir, "axolotl_rainy_shelter.mp4"),
        shots: [
          { labelZh: "01 · 雨夜粉红美西螈", labelEn: "01 · Rainy Pink Axolotl", chatZh: "淋雨的小家伙", chatEn: "*shiver*", bubbleX: 160, bubbleY: 88 },
          { labelZh: "02 · 递出温暖灯笼", labelEn: "02 · Warm Lantern Offer", chatZh: "跟我回家吧", chatEn: "Come home", bubbleX: 118, bubbleY: 38 },
          { labelZh: "03 · 橡木屋红石暖灯", labelEn: "03 · Cozy Oak Shelter", chatZh: "暖和多了!", chatEn: "So warm!", bubbleX: 118, bubbleY: 38 },
          { labelZh: "04 · 爱心粒子循环", labelEn: "04 · Heart Particle Loop", chatZh: "晚安小方块", chatEn: "Cozy night", bubbleX: 122, bubbleY: 38 }
        ]
      }
    ]
  };
}

if (!isMainThread && workerData) {
  const { tmpDir, indices } = workerData;
  const tasks = buildRenderTasks();
  for (const idx of indices) {
    const t = tasks[idx];
    const buf = t.run();
    fs.writeFileSync(path.join(tmpDir, t.name), encodePNG(t.w, t.h, buf));
  }
  parentPort?.postMessage("done");
} else {
  const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
  if (isMain) {
    const force = process.argv.includes("--force");
    const loopsOnly = process.argv.includes("--loops-only");
    const rawDir = path.join(ROOT, "tmp", "raw_panels");
    console.log("Rendering 3D Minecraft voxel panels across worker threads...");
    await renderRawPanelSetParallel(rawDir, force, loopsOnly ? "objloop_" : "");
    const manifest = buildBoardsManifest(rawDir);
    manifest.loopsOnly = loopsOnly;
    const manifestPath = path.join(ROOT, "tmp", "boards_manifest.json");
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    console.log("Composing animated loops, hero reel, showcase boards, GIFs, and MP4s...");
    execFileSync(
      "powershell.exe",
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path.join(__dirname, "compose_boards.ps1"), "-ManifestPath", manifestPath],
      { stdio: "inherit" }
    );
  }
}
