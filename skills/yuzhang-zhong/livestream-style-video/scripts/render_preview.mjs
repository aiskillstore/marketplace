#!/usr/bin/env node
/**
 * render_preview.mjs
 * Zero-npm-dependency 3D SDF Livestream Scene + Multi-Platform Chrome/HUD Video Engine.
 *
 * Supports:
 * - Stylized Realistic IRL & Cross-Genre Streamer Rigs (18mm selfie, 24mm monitor webcam,
 *   35mm autofocus desk-clamp, 16mm first-person dual-hand POV, Wuxia flying-sword selfie)
 * - Canonical Roblox R6 / Chibi-Blocky Streamer Rigs (2x2x1 torso, flush 1x2x1 limbs,
 *   fingerless/clawless solid block hands, 1:1 barrel head, flat 2D decals, PiP facecam & 50/50 PK split)
 * - Multi-platform clean-room HUD presets via scripts/compose_hud.py (douyin, kuaishou, instagram, x, tiktok, clean)
 * - Synthesized multi-shot live WAV audio + GIF + H.264 MP4 export
 */

import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { execFileSync, spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { TEMPLATES, compileStoryboard } from "./shot_compiler.mjs";
import { buildShotHudTimeline, resolvePlatformPreset } from "./hud_presets.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const mix = (a, b, t) => a + (b - a) * t;
const smoothstep = (e0, e1, x) => {
  const t = clamp((x - e0) / (e1 - e0), 0, 1);
  return t * t * (3 - 2 * t);
};

const v3 = (x = 0, y = 0, z = 0) => ({ x, y, z });
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
  const c = Math.cos(ang), s = Math.sin(ang);
  return { x: c * p.x + s * p.z, y: p.y, z: -s * p.x + c * p.z };
}
function rotX(p, ang) {
  const c = Math.cos(ang), s = Math.sin(ang);
  return { x: p.x, y: c * p.y - s * p.z, z: s * p.y + c * p.z };
}
function rotZ(p, ang) {
  const c = Math.cos(ang), s = Math.sin(ang);
  return { x: c * p.x - s * p.y, y: s * p.x + c * p.y, z: p.z };
}

function sdRoundBox(p, b, r) {
  const qx = Math.abs(p.x) - b.x + r;
  const qy = Math.abs(p.y) - b.y + r;
  const qz = Math.abs(p.z) - b.z + r;
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0), Math.max(qz, 0)) + Math.min(Math.max(qx, qy, qz), 0) - r;
}

function sdRoundedCylinder(p, ra, rb, h) {
  const dx = Math.hypot(p.x, p.z) - ra + rb;
  const dy = Math.abs(p.y) - h + rb;
  return Math.min(Math.max(dx, dy), 0) + Math.hypot(Math.max(dx, 0), Math.max(dy, 0)) - rb;
}

function sdSphere(p, r) {
  return len3(p) - r;
}

function sdCapsule(p, a, b, r) {
  const pa = sub3(p, a), ba = sub3(b, a);
  const h = clamp(dot3(pa, ba) / (dot3(ba, ba) || 1e-6), 0, 1);
  return len3(sub3(pa, mul3(ba, h))) - r;
}

class SceneHit {
  constructor() {
    this.d = 1e9;
    this.color = [128, 128, 128];
    this.roughness = 0.35;
    this.id = 0;
  }
  add(d, color, roughness = 0.35, id = 1) {
    if (d < this.d) {
      this.d = d;
      this.color = color;
      this.roughness = roughness;
      this.id = id;
    }
    return this;
  }
  merge(other) {
    if (other && other.d < this.d) {
      this.d = other.d;
      this.color = other.color;
      this.roughness = other.roughness;
      this.id = other.id;
    }
    return this;
  }
}

// ---------- PNG Encoder (Zero Dependencies) ----------
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
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
  const stride = width * 4;
  const raw = Buffer.alloc((stride + 1) * height);
  for (let y = 0; y < height; y++) {
    const rowStart = y * (stride + 1);
    raw[rowStart] = 0;
    Buffer.from(rgba.buffer, rgba.byteOffset + y * stride, stride).copy(raw, rowStart + 1);
  }
  const idat = zlib.deflateSync(raw, { level: 6 });
  return Buffer.concat([signature, pngChunk("IHDR", ihdr), pngChunk("IDAT", idat), pngChunk("IEND", Buffer.alloc(0))]);
}

// ---------- 2D Face Evaluator (Ring-Light Catchlights + Expressions) ----------
function evalExpressiveFace(u, v, expression = "smile", ringLight = true, blushRed = false) {
  if (Math.abs(u) > 0.45 || Math.abs(v) > 0.45) return null;
  const ink = [15, 23, 42];
  const white = [255, 255, 255];
  const tear = [96, 195, 255];
  const ex = Math.abs(u) - 0.13;
  const ey = v - 0.08;

  if (blushRed && Math.hypot(Math.abs(u) - 0.22, v + 0.02) < 0.085) {
    return [244, 63, 94];
  }
  if (expression === "tears" && Math.abs(ex) < 0.038 && v < 0.03 && v > -0.35) {
    return tear;
  }

  // Eyes
  if (expression === "dizzy") {
    if (Math.abs(ex) < 0.06 && Math.abs(ey) < 0.06 && (Math.abs(ex - ey) < 0.018 || Math.abs(ex + ey) < 0.018)) {
      return ink;
    }
  } else if (expression === "deadpan") {
    if (Math.abs(ex) < 0.065 && Math.abs(ey) < 0.016) return ink;
  } else if (expression === "shocked") {
    const r = Math.hypot(ex, ey);
    if (r < 0.068 && r > 0.042) return ink;
    if (r <= 0.042 && r > 0.016) return white;
    if (r <= 0.016) return ink;
  } else {
    const r = Math.hypot(ex, ey * 0.85);
    if (r < 0.056) {
      if (ringLight && r > 0.024 && r < 0.040) return white;
      if (!ringLight && Math.hypot(ex + 0.015, ey - 0.018) < 0.018) return white;
      return ink;
    }
  }

  // Mouth
  const my = v + 0.12;
  if (expression === "shocked" || expression === "tears") {
    if (Math.abs(u) < 0.075 && Math.abs(my) < 0.048) {
      return my < -0.015 ? [244, 114, 182] : [76, 18, 28];
    }
  } else if (expression === "deadpan" || expression === "dizzy") {
    if (Math.abs(u) < 0.08 && Math.abs(my) < 0.015) return ink;
  } else if (expression === "smirk") {
    const curve = (u - 0.02) * 0.28;
    if (Math.abs(u) < 0.09 && Math.abs(my - curve) < 0.017) return ink;
  } else {
    const arc = u * u * 1.9 - 0.02;
    if (Math.abs(u) < 0.10 && Math.abs(my - arc) < 0.018) return ink;
  }
  return null;
}

// ---------- Stylized Realistic / Genre Human Streamer SDF ----------
function evalHumanStreamerSDF(p, cfg = {}) {
  const hit = new SceneHit();
  const pos = cfg.pos || v3(0, 0, 0);
  let q = sub3(p, pos);
  if (len3(q) - 1.55 > hit.d) return hit;

  if (cfg.yaw) q = rotY(q, cfg.yaw);
  if (cfg.waistPitch) {
    const pivot = v3(0, -0.25, 0);
    q = add3(rotX(sub3(q, pivot), cfg.waistPitch), pivot);
  }

  const skin = cfg.flushed ? [252, 165, 165] : [253, 220, 192];
  const topCol = cfg.topColor || [37, 99, 235];
  const innerShirt = [248, 250, 252];
  const hairCol = cfg.hairColor || [24, 32, 48];

  // Organic Neck + Natural Sloped Human Torso + Open Jacket Collar & Lavalier Mic
  hit.add(sdRoundedCylinder(sub3(q, v3(0, 0.25, -0.01)), 0.085, 0.02, 0.09), skin, 0.34, 2);
  const pt = sub3(q, v3(0, -0.14, 0));
  const dTorso = sdRoundBox(pt, v3(0.28, 0.34, 0.16), 0.14);
  if (dTorso < hit.d) {
    let cCol = topCol;
    if (pt.z > 0.11 && Math.abs(pt.x) < 0.085 && pt.y > -0.18) cCol = innerShirt;
    hit.add(dTorso, cCol, 0.42, 2);
  }
  if (cfg.lavalier !== false) {
    hit.add(sdRoundBox(sub3(pt, v3(0.09, 0.24, 0.15)), v3(0.026, 0.036, 0.022), 0.008), [15, 23, 42], 0.22, 3);
  }

  // Organic Ellipsoid Human Head + Ears + Hair + Ring-Light Catchlights
  let ph = sub3(q, v3(0, 0.50, 0));
  if (cfg.headYaw) ph = rotY(ph, cfg.headYaw);
  if (cfg.headPitch) ph = rotX(ph, cfg.headPitch);

  const pe = v3(ph.x / 0.205, ph.y / 0.245, ph.z / 0.205);
  const dHead = (len3(pe) - 1.0) * 0.205;
  if (dHead < hit.d) {
    let hCol = skin;
    if (ph.z > 0.12) {
      const decal = evalExpressiveFace(ph.x / 0.40, ph.y / 0.46, cfg.expression || "smile", true, Boolean(cfg.flushed));
      if (decal) hCol = decal;
    }
    hit.add(dHead, hCol, 0.32, 4);
  }
  hit.add(sdSphere(sub3(ph, v3(-0.20, -0.01, 0)), 0.045), skin, 0.34, 4);
  hit.add(sdSphere(sub3(ph, v3(0.20, -0.01, 0)), 0.045), skin, 0.34, 4);

  // Volumetric hair crown + side locks
  const pHair = v3(ph.x / 0.22, (ph.y - 0.06) / 0.22, (ph.z + 0.025) / 0.22);
  const dHair = (len3(pHair) - 1.0) * 0.22;
  if (ph.y > 0.07 || ph.z < -0.01 || Math.abs(ph.x) > 0.165) {
    hit.add(dHair, hairCol, 0.44, 5);
  }
  if (cfg.wuxiaBun) {
    const bunTilt = cfg.crookedBun ? 0.38 : 0.0;
    const pb = rotZ(sub3(ph, v3(cfg.crookedBun ? 0.06 : 0, 0.29, -0.02)), bunTilt);
    hit.add(sdRoundedCylinder(pb, 0.075, 0.02, 0.065), hairCol, 0.35, 5);
    hit.add(sdRoundedCylinder(sub3(pb, v3(0, -0.02, 0)), 0.085, 0.01, 0.022), [56, 189, 248], 0.18, 5);
  }
  if (cfg.glasses) {
    const glL = Math.max(sdRoundBox(sub3(ph, v3(-0.08, 0.04, 0.20)), v3(0.062, 0.045, 0.012), 0.012), -sdRoundBox(sub3(ph, v3(-0.08, 0.04, 0.20)), v3(0.046, 0.030, 0.02), 0.008));
    const glR = Math.max(sdRoundBox(sub3(ph, v3(0.08, 0.04, 0.20)), v3(0.062, 0.045, 0.012), 0.012), -sdRoundBox(sub3(ph, v3(0.08, 0.04, 0.20)), v3(0.046, 0.030, 0.02), 0.008));
    hit.add(Math.min(glL, glR), [15, 23, 42], 0.16, 6);
  }

  // Arms
  const armLPitch = cfg.armLPitch ?? -0.25;
  const armRPitch = cfg.armRPitch ?? -0.25;
  const paL = rotX(sub3(q, v3(-0.38, 0.16, 0)), armLPitch);
  hit.add(sdCapsule(paL, v3(0, 0, 0), v3(0, -0.42, 0), 0.085), topCol, 0.38, 7);
  hit.add(sdSphere(sub3(paL, v3(0, -0.45, 0)), 0.075), skin, 0.32, 7);

  const paR = rotX(sub3(q, v3(0.38, 0.16, 0)), armRPitch);
  hit.add(sdCapsule(paR, v3(0, 0, 0), v3(0, -0.42, 0), 0.085), topCol, 0.38, 7);
  hit.add(sdSphere(sub3(paR, v3(0, -0.45, 0)), 0.075), skin, 0.32, 7);

  // Legs (for full-body shots like Wuxia sword flight)
  if (cfg.showLegs) {
    hit.add(sdCapsule(q, v3(-0.14, -0.42, 0), v3(-0.16, -0.92, 0), 0.095), [226, 232, 240], 0.42, 8);
    hit.add(sdCapsule(q, v3(0.14, -0.42, 0), v3(0.16, -0.92, 0), 0.095), [226, 232, 240], 0.42, 8);
  }
  return hit;
}

// ---------- Canonical Roblox R6 / Chibi-Blocky Avatar SDF ----------
// Strictly enforces 2x2x1 torso + flush 1x2x1 solid rectangular limbs + fingerless/clawless block hands + 1:1 barrel head
function evalRobloxAvatarSDF(p, cfg = {}) {
  const hit = new SceneHit();
  const pos = cfg.pos || v3(0, 0, 0);
  let q = sub3(p, pos);
  if (len3(q) - 1.65 > hit.d) return hit;

  if (cfg.yaw) q = rotY(q, cfg.yaw);
  if (cfg.roll) q = rotZ(q, cfg.roll);
  if (cfg.waistPitch) {
    const wPivot = v3(0, -0.18, 0);
    q = add3(rotX(sub3(q, wPivot), cfg.waistPitch), wPivot);
  }

  const theme = cfg.theme || "obby";
  const palettes = {
    noob: { head: [245, 205, 48], torso: [13, 105, 172], arms: [245, 205, 48], legs: [164, 189, 71], headset: false },
    obby: { head: [253, 234, 141], torso: [14, 165, 233], arms: [253, 234, 141], legs: [30, 41, 59], headset: true },
    y2k: { head: [248, 217, 109], torso: [236, 72, 153], arms: [24, 24, 27], legs: [147, 197, 253], headset: true },
    commuter: { head: [253, 234, 141], torso: [56, 189, 248], arms: [56, 189, 248], legs: [51, 65, 85], headset: false },
    shadow: { head: [15, 23, 42], torso: [15, 23, 42], arms: [15, 23, 42], legs: [15, 23, 42], headset: false }
  };
  const pal = palettes[theme] || palettes.obby;

  // Canonical 2x2x1 Torso (0.34 * 2 = 0.68 wide, 0.68 tall, 0.34 deep; half-extents: 0.34, 0.34, 0.17)
  const pt = sub3(q, v3(0, 0.0, 0));
  const dTorso = sdRoundBox(pt, v3(0.34, 0.34, 0.17), 0.026);
  if (dTorso < hit.d) {
    let tCol = pal.torso;
    // Trademark-free geometric triangle chest emblem
    if (pt.z > 0.145 && pt.y > -0.10 && pt.y < 0.14 && Math.abs(pt.x) < (0.14 - pt.y) * 0.52) {
      tCol = [248, 250, 252];
    }
    hit.add(dTorso, tCol, 0.24, 10);
  }

  // Canonical 1:1 Barrel-Beveled Cylindrical Head (studless smooth top + flat 2D decal)
  let ph = sub3(q, v3(0, 0.56, 0));
  if (cfg.headYaw) ph = rotY(ph, cfg.headYaw);
  const dHead = sdRoundedCylinder(ph, 0.215, 0.055, 0.215);
  if (dHead < hit.d) {
    let hCol = pal.head;
    if (theme === "shadow") {
      if (ph.z > 0.14 && Math.abs(Math.abs(ph.x) - 0.065) < 0.032 && Math.abs(ph.y - 0.03) < 0.028) {
        hCol = [255, 255, 255];
      }
      hit.add(dHead, hCol, hCol[0] === 255 ? 0.02 : 0.45, 11);
    } else {
      if (ph.z > 0.14) {
        const dec = evalExpressiveFace(ph.x / 0.42, ph.y / 0.42, cfg.expression || "smile", false, false);
        if (dec) hCol = dec;
      }
      hit.add(dHead, hCol, 0.22, 11);
    }
  }

  // Optional Cat-Ear RGB Headset (arch over top of head in XY plane!)
  if (pal.headset || cfg.headset) {
    const pArch = rotX(sub3(ph, v3(0, 0.04, 0)), Math.PI / 2);
    if (ph.y > 0.0) {
      const dBand = Math.max(
        sdRoundedCylinder(pArch, 0.255, 0.015, 0.035),
        -sdRoundedCylinder(pArch, 0.218, 0.01, 0.06)
      );
      hit.add(dBand, [168, 85, 247], 0.18, 12);
    }
    hit.add(sdRoundBox(sub3(ph, v3(-0.14, 0.27, 0)), v3(0.038, 0.042, 0.025), 0.008), [244, 114, 182], 0.14, 12);
    hit.add(sdRoundBox(sub3(ph, v3(0.14, 0.27, 0)), v3(0.038, 0.042, 0.025), 0.008), [244, 114, 182], 0.14, 12);
    hit.add(sdRoundBox(sub3(ph, v3(-0.235, 0.02, 0)), v3(0.035, 0.075, 0.065), 0.015), [56, 189, 248], 0.12, 12);
    hit.add(sdRoundBox(sub3(ph, v3(0.235, 0.02, 0)), v3(0.035, 0.075, 0.065), 0.015), [56, 189, 248], 0.12, 12);
  }

  // Flush 1x2x1 Solid Block Arms (zero human fingers, zero Lego C-claws)
  const armLPitch = cfg.armLPitch ?? 0.0;
  const armRPitch = cfg.armRPitch ?? 0.0;
  const paL = rotX(sub3(q, v3(-0.51, 0.24, 0)), armLPitch);
  hit.add(sdRoundBox(sub3(paL, v3(0, -0.24, 0)), v3(0.165, 0.34, 0.165), 0.022), pal.arms, 0.24, 13);

  const paR = rotX(sub3(q, v3(0.51, 0.24, 0)), armRPitch);
  hit.add(sdRoundBox(sub3(paR, v3(0, -0.24, 0)), v3(0.165, 0.34, 0.165), 0.022), pal.arms, 0.24, 13);

  if (cfg.selfieStick) {
    hit.add(sdCapsule(paR, v3(0, -0.54, 0.05), v3(-0.18, -0.35, 0.72), 0.022), [148, 163, 184], 0.20, 14);
    hit.add(sdRoundBox(sub3(paR, v3(-0.18, -0.32, 0.76)), v3(0.085, 0.145, 0.018), 0.01), [56, 189, 248], 0.06, 14);
  }
  if (cfg.colaCan) {
    hit.add(sdRoundedCylinder(sub3(paR, v3(0, -0.56, 0.14)), 0.075, 0.012, 0.11), [225, 29, 72], 0.18, 14);
  }

  // Flush 1x2x1 Solid Block Legs (matching exact 2x2x1 torso width, zero thigh gap)
  const legLPitch = cfg.legLPitch ?? 0.0;
  const legRPitch = cfg.legRPitch ?? 0.0;
  const plL = rotX(sub3(q, v3(-0.17, -0.34, 0)), legLPitch);
  hit.add(sdRoundBox(sub3(plL, v3(0, -0.34, 0)), v3(0.166, 0.34, 0.168), 0.02), pal.legs, 0.28, 15);
  const plR = rotX(sub3(q, v3(0.17, -0.34, 0)), legRPitch);
  hit.add(sdRoundBox(sub3(plR, v3(0, -0.34, 0)), v3(0.166, 0.34, 0.168), 0.02), pal.legs, 0.28, 15);

  return hit;
}

// ---------- Core Raymarcher ----------
export function render3DViewport(width, height, sceneFn, camCfg = {}) {
  const buf = new Uint8Array(width * height * 4);
  const ro = camCfg.ro || v3(0, 0.35, 2.55);
  const ta = camCfg.ta || v3(0, 0.15, 0);
  const fov = camCfg.fov || 1.85;
  const bgTop = camCfg.bgTop || [15, 23, 42];
  const bgBot = camCfg.bgBot || [30, 41, 59];
  const floorY = camCfg.floorY !== undefined ? camCfg.floorY : -0.95;
  const floorCol1 = camCfg.floorCol1 || [30, 41, 59];
  const floorCol2 = camCfg.floorCol2 || [51, 65, 85];

  const fw = norm3(sub3(ta, ro));
  let rt = norm3(cross3(fw, v3(0, 1, 0)));
  let up = cross3(rt, fw);
  if (camCfg.roll) {
    const cr = Math.cos(camCfg.roll), sr = Math.sin(camCfg.roll);
    const nrt = add3(mul3(rt, cr), mul3(up, sr));
    const nup = sub3(mul3(up, cr), mul3(rt, sr));
    rt = nrt;
    up = nup;
  }

  const keyLight = norm3(camCfg.keyDir || v3(0.45, 0.78, 0.72));
  const rimLight = norm3(v3(-0.65, 0.45, -0.60));
  const rimTint = camCfg.rimTint || [56, 189, 248];

  const calcNormal = (p, d0) => {
    const e = 0.003;
    return norm3(
      v3(
        sceneFn(v3(p.x + e, p.y, p.z)).d - d0,
        sceneFn(v3(p.x, p.y + e, p.z)).d - d0,
        sceneFn(v3(p.x, p.y, p.z + e)).d - d0
      )
    );
  };

  for (let py = 0; py < height; py++) {
    const ny = 1 - (2 * (py + 0.5)) / height;
    const vg = py / height;
    for (let px = 0; px < width; px++) {
      const nx = ((2 * (px + 0.5)) / width - 1) * (width / height);
      const rd = norm3(add3(add3(mul3(rt, nx), mul3(up, ny)), mul3(fw, fov)));

      let r = mix(bgTop[0], bgBot[0], vg);
      let g = mix(bgTop[1], bgBot[1], vg);
      let b = mix(bgTop[2], bgBot[2], vg);

      // Split-screen dual background tint when requested
      if (camCfg.splitScreenTint) {
        if (px < width / 2) {
          r = mix(r, 92, 0.35);
          g = mix(g, 24, 0.35);
          b = mix(b, 68, 0.35);
        } else {
          r = mix(r, 24, 0.28);
          g = mix(g, 62, 0.28);
          b = mix(b, 96, 0.28);
        }
      }

      let t = 0.18;
      let tMax = 7.2;
      let tf = -1;
      if (floorY !== null && rd.y < -0.002) {
        tf = (floorY - ro.y) / rd.y;
        if (tf > 0 && tf < tMax) tMax = tf + 0.01;
      }

      let hit = null;
      const maxSteps = camCfg.maxSteps || 30;
      for (let step = 0; step < maxSteps; step++) {
        if (t > tMax) break;
        const pos = add3(ro, mul3(rd, t));
        const res = sceneFn(pos);
        if (res.d < 0.005) {
          hit = { pos, res, t };
          break;
        }
        t += res.d;
      }

      if (hit && (tf <= 0 || hit.t <= tf)) {
        const rough = hit.res.roughness ?? 0.32;
        if (rough <= 0.07) {
          // Emissive neon / phone screen / rune glow
          r = clamp(hit.res.color[0] * 1.08 + 16, 0, 255);
          g = clamp(hit.res.color[1] * 1.08 + 16, 0, 255);
          b = clamp(hit.res.color[2] * 1.08 + 16, 0, 255);
        } else {
          const N = calcNormal(hit.pos, hit.res.d);
          const V = mul3(rd, -1);
          const diff = Math.max(0, dot3(N, keyLight));
          const amb = 0.42 + 0.14 * (0.5 + 0.5 * N.y);
          const H = norm3(add3(keyLight, V));
          const spec = Math.pow(Math.max(0, dot3(N, H)), rough < 0.26 ? 32 : 14) * (rough < 0.26 ? 0.34 : 0.14);
          const rim = Math.pow(1 - Math.max(0, dot3(N, V)), 2.8) * Math.max(0, dot3(N, rimLight)) * 0.38;
          const base = hit.res.color;
          const lit = amb + diff * 0.64;
          r = clamp(base[0] * lit + 255 * spec + rimTint[0] * rim, 0, 255);
          g = clamp(base[1] * lit + 252 * spec + rimTint[1] * rim, 0, 255);
          b = clamp(base[2] * lit + 245 * spec + rimTint[2] * rim, 0, 255);
        }
      } else if (tf > 0 && tf < 10.0 && floorY !== null) {
        const fp = add3(ro, mul3(rd, tf));
        const checker = (Math.floor(fp.x * 2.2) + Math.floor(fp.z * 2.2)) & 1;
        const fc = checker ? floorCol1 : floorCol2;
        const fade = Math.exp(-0.07 * tf * tf);
        r = mix(r, fc[0], fade);
        g = mix(g, fc[1], fade);
        b = mix(b, fc[2], fade);
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

// ---------- Episode Specific 3D Scene Builders ----------
function buildEpisodeScene(slug, shotIdx, phase = 0.5) {
  const s = clamp(shotIdx, 0, 3);

  // 1. IRL Night-Market Selfie (Realistic Streamer + Neon Stalls + Skewer + Iced Tea)
  if (slug === "irl_night_market_selfie") {
    const bob = Math.sin(phase * Math.PI * 4) * 0.03;
    const shake = s === 2 ? Math.sin(phase * Math.PI * 10) * 0.035 : 0;
    return {
      cam: {
        ro: v3(shake, 0.36 + bob, s === 1 ? 1.85 : 2.15),
        ta: v3(0, 0.24, 0),
        fov: 1.52, // 18mm ultra-wide selfie feel
        bgTop: [24, 16, 48],
        bgBot: [68, 24, 62],
        rimTint: [254, 44, 85],
        floorY: -0.92,
        floorCol1: [32, 36, 48],
        floorCol2: [42, 46, 60]
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Neon stall signage bokeh bars in background
        if (p.z < -0.55) {
          hit.add(sdRoundBox(sub3(p, v3(-0.75, 0.65, -1.1)), v3(0.28, 0.14, 0.04), 0.02), [254, 44, 85], 0.04, 30);
          hit.add(sdRoundBox(sub3(p, v3(0.78, 0.58, -1.2)), v3(0.32, 0.12, 0.04), 0.02), [37, 244, 238], 0.04, 30);
          hit.add(sdSphere(sub3(p, v3(-0.35, 0.92, -0.95)), 0.12), [250, 204, 21], 0.05, 30);
          hit.add(sdSphere(sub3(p, v3(0.38, 0.92, -0.95)), 0.12), [249, 115, 22], 0.05, 30);
        }
        hit.merge(
          evalHumanStreamerSDF(p, {
            pos: v3(0.04, 0, 0),
            yaw: -0.1,
            armRPitch: -1.25, // Extending right arm toward selfie camera!
            armLPitch: s === 1 ? -1.1 : s === 3 ? -1.35 : -0.55,
            expression: s === 2 ? "shocked" : s === 3 ? "tears" : "grin",
            flushed: s >= 2,
            topColor: [37, 99, 235]
          })
        );
        // Chili skewer held close to lens in Shot 1 & 2
        if (s === 1 || s === 2) {
          const skPos = s === 1 ? v3(-0.04, 0.22, 1.05) : v3(-0.16, 0.16, 0.55);
          const qk = sub3(p, skPos);
          hit.add(sdCapsule(qk, v3(0, -0.22, 0), v3(0, 0.18, 0), 0.012), [214, 172, 112], 0.4, 31);
          for (let k = -1; k <= 1; k++) {
            hit.add(sdSphere(sub3(qk, v3(0, k * 0.085, 0)), 0.048), [225, 29, 72], 0.22, 31);
          }
        }
        // Oversized iced lemon tea cup in Shot 3 (index 3)
        if (s === 3) {
          const cupP = sub3(p, v3(-0.08, 0.26, 0.55));
          hit.add(sdRoundedCylinder(cupP, 0.10, 0.015, 0.15), [250, 204, 21], 0.14, 32);
          hit.add(sdCapsule(cupP, v3(0, 0.12, 0), v3(0.04, 0.26, 0.04), 0.012), [248, 250, 252], 0.2, 32);
        }
        return hit;
      }
    };
  }

  // 2. Desk Unboxing Autofocus (Boom Mic + Mystery Cube + Spring Mascot)
  if (slug === "desk_unboxing_autofocus") {
    const shake = s === 2 ? Math.sin(phase * Math.PI * 8) * 0.03 * (1 - phase) : 0;
    const popH = s === 2 ? smoothstep(0.08, 0.55, phase) * 0.48 : 0;
    return {
      cam: {
        ro: v3(0, 0.46 + shake, 2.28),
        ta: v3(0, 0.14, 0.15),
        fov: 1.92,
        bgTop: [30, 41, 59],
        bgBot: [51, 65, 85],
        rimTint: [168, 85, 247],
        floorY: null
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Desk surface
        hit.add(sdRoundBox(sub3(p, v3(0, -0.36, 0.45)), v3(1.3, 0.05, 0.55), 0.02), [226, 232, 240], 0.30, 40);
        // Locked Left Condenser Boom Mic (screen-left across all 4 shots!)
        hit.add(sdCapsule(p, v3(-0.85, -0.25, 0.65), v3(-0.36, 0.16, 0.52), 0.024), [30, 41, 59], 0.35, 41);
        hit.add(sdRoundedCylinder(sub3(p, v3(-0.34, 0.20, 0.52)), 0.055, 0.02, 0.08), [15, 23, 42], 0.45, 41);

        hit.merge(
          evalHumanStreamerSDF(p, {
            pos: v3(0, 0, s === 2 ? -0.18 * smoothstep(0.1, 0.5, phase) : 0),
            headYaw: s === 3 ? 0.26 : 0,
            armLPitch: s === 1 ? -1.18 : -0.65,
            armRPitch: s === 1 ? -1.22 : s === 3 ? -0.95 : -0.68,
            expression: s === 2 ? "shocked" : "smile",
            topColor: [214, 211, 209],
            lavalier: false
          })
        );

        // Silver Mystery Gadget Cube (held close to lens at chest level in Shot 1 with flat open palm behind it!)
        const cubePos = s === 1 ? v3(0.02, -0.02, 1.24) : v3(0.02, -0.19, 0.55);
        const qc = sub3(p, cubePos);
        hit.add(sdRoundBox(qc, v3(0.125, 0.125, 0.125), 0.022), [148, 163, 184], 0.18, 42);
        hit.add(sdRoundedCylinder(sub3(qc, v3(0, 0.13, 0)), 0.044, 0.008, 0.018), [239, 68, 68], 0.08, 42);
        if (s === 1) {
          // Influencer flat palm held behind the gadget cube to trigger continuous AF-C focus lock
          const pPalm = rotZ(sub3(p, v3(-0.11, 0.08, 1.06)), 0.18);
          hit.add(sdRoundBox(pPalm, v3(0.088, 0.125, 0.024), 0.02), [253, 220, 192], 0.32, 42);
          hit.add(sdCapsule(pPalm, v3(0.07, -0.04, 0), v3(0.13, 0.04, 0.02), 0.022), [253, 220, 192], 0.32, 42);
        }

        if (s >= 2) {
          const mascotY = s === 2 ? -0.05 + popH : -0.02;
          const pm = sub3(p, v3(0.02, mascotY, 0.55));
          const dM = sdSphere(pm, 0.105);
          if (dM < hit.d) {
            let mCol = [250, 204, 21];
            if (pm.z > 0.07 && Math.abs(Math.abs(pm.x) - 0.035) < 0.014 && Math.abs(pm.y - 0.015) < 0.016) mCol = [15, 23, 42];
            hit.add(dM, mCol, 0.22, 43);
          }
          // Spring coil beneath mascot in Shot 2
          if (s === 2) {
            hit.add(sdRoundedCylinder(sub3(p, v3(0.02, -0.04 + popH * 0.45, 0.55)), 0.032, 0.006, popH * 0.45 + 0.02), [226, 232, 240], 0.18, 43);
          }
        }
        return hit;
      }
    };
  }

  // 3. Midnight Corridor First-Person Dual-Hand POV (16mm Chest Cam)
  if (slug === "midnight_corridor_fpv_live") {
    const walkBob = Math.sin(phase * Math.PI * 4) * 0.03;
    const shake = s >= 2 ? Math.sin(phase * Math.PI * 12) * 0.035 : 0;
    const doorOpenYaw = s === 2 ? smoothstep(0.15, 0.85, phase) * 0.42 : 0;
    return {
      cam: {
        ro: v3(shake, 0.22 + walkBob, s === 0 ? 2.35 - phase * 0.35 : 2.0),
        ta: v3(s === 3 ? 0.35 : 0, 0.20, -1.0),
        fov: 1.42, // 16mm ultra-wide POV
        bgTop: [8, 12, 22],
        bgBot: [18, 24, 38],
        rimTint: [56, 189, 248],
        floorY: -0.88,
        floorCol1: [28, 24, 22],
        floorCol2: [42, 36, 30]
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Left & Right corridor walls + warm wall sconce
        hit.add(sdRoundBox(sub3(p, v3(-1.15, 0.3, -0.2)), v3(0.08, 1.3, 2.6), 0.01), [30, 41, 59], 0.48, 50);
        hit.add(sdRoundBox(sub3(p, v3(1.15, 0.3, -0.2)), v3(0.08, 1.3, 2.6), 0.01), [30, 41, 59], 0.48, 50);
        const bulbOn = !(s === 2 && Math.floor(phase * 6) % 2 === 1);
        if (s < 3 && bulbOn) {
          hit.add(sdSphere(sub3(p, v3(0, 0.96, -0.65)), 0.055), [254, 240, 138], 0.03, 50);
        }

        // End wall + Wooden Door 404 with trim & handle (or glowing green EXIT stairwell door in Shot 3)
        if (s === 3) {
          hit.add(sdRoundBox(sub3(p, v3(0.28, 0.05, -1.25)), v3(0.38, 0.72, 0.04), 0.015), [51, 65, 85], 0.35, 51);
          hit.add(sdRoundBox(sub3(p, v3(0.28, 0.92, -1.18)), v3(0.22, 0.085, 0.03), 0.01), [34, 197, 94], 0.03, 51);
        } else {
          // Outer doorframe
          hit.add(sdRoundBox(sub3(p, v3(0, 0.06, -1.28)), v3(0.41, 0.84, 0.025), 0.01), [71, 46, 28], 0.42, 51);
          const pd = rotY(sub3(p, v3(-0.34, 0.05, -1.24)), doorOpenYaw);
          const qDoor = sub3(pd, v3(0.34, 0, 0));
          hit.add(sdRoundBox(qDoor, v3(0.34, 0.78, 0.038), 0.015), [124, 76, 44], 0.38, 51);
          hit.add(sdRoundBox(sub3(qDoor, v3(0, 0.32, 0.042)), v3(0.11, 0.045, 0.01), 0.005), [250, 204, 21], 0.12, 51);
          hit.add(sdSphere(sub3(qDoor, v3(0.23, -0.04, 0.055)), 0.028), [250, 204, 21], 0.14, 51);
        }

        // First-Person Left Hand holding dark-bezel Chat Smartphone cleanly inside lower-left frame!
        const phL = rotY(sub3(p, v3(-0.22, -0.08 + walkBob * 0.5, 1.24)), 0.24);
        hit.add(sdRoundBox(phL, v3(0.078, 0.142, 0.016), 0.014), [15, 23, 42], 0.20, 52);
        const dScr = sdRoundBox(sub3(phL, v3(0, 0, 0.006)), v3(0.068, 0.126, 0.014), 0.01);
        if (dScr < hit.d) {
          const isChatRow = Math.abs(phL.x) < 0.052 && (Math.abs(phL.y + 0.02) < 0.012 || Math.abs(phL.y + 0.055) < 0.012 || Math.abs(phL.y + 0.09) < 0.012);
          hit.add(dScr, isChatRow ? [125, 211, 252] : [14, 32, 58], 0.04, 52);
        }
        hit.add(sdSphere(sub3(phL, v3(-0.072, -0.05, 0.025)), 0.042), [253, 220, 192], 0.34, 52);

        // First-Person Right Hand holding Flashlight (waves across lens in Shot 1)
        const waveX = s === 1 ? Math.sin(phase * Math.PI * 2) * 0.22 : 0.28;
        const flP = sub3(p, v3(waveX, -0.10, 1.24));
        hit.add(sdRoundedCylinder(rotX(flP, Math.PI / 2), 0.046, 0.01, 0.14), [71, 85, 105], 0.22, 53);
        hit.add(sdSphere(sub3(flP, v3(0, 0, -0.14)), 0.042), [254, 249, 195], 0.02, 53);
        hit.add(sdSphere(sub3(flP, v3(0.045, -0.04, 0.04)), 0.045), [253, 220, 192], 0.34, 53);
        return hit;
      }
    };
  }

  // 4. Late-Night Study Webcam (Glasses Host + Glowing Keyboard + Ginger Tabby Cat)
  if (slug === "late_night_study_webcam") {
    const shake = s === 2 ? Math.sin(phase * Math.PI * 8) * 0.028 * (1 - phase) : 0;
    return {
      cam: {
        ro: v3(0, 0.56 + shake, 2.35), // Monitor-top 6-degree downward webcam
        ta: v3(0, 0.10, 0.12),
        fov: 1.78,
        bgTop: [15, 23, 42],
        bgBot: [30, 27, 46],
        rimTint: [37, 244, 238],
        floorY: null
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Desk + Mechanical Keyboard with keycap grid over RGB underglow
        hit.add(sdRoundBox(sub3(p, v3(0, -0.38, 0.45)), v3(1.3, 0.05, 0.52), 0.02), [120, 82, 54], 0.40, 60);
        const pk = sub3(p, v3(0, -0.31, 0.52));
        const dKb = sdRoundBox(pk, v3(0.32, 0.024, 0.13), 0.01);
        if (dKb < hit.d) {
          let kCol = [30, 41, 59];
          if (pk.y < -0.008) kCol = [37, 244, 238];
          else if (pk.y > 0.012 && Math.abs(pk.x) < 0.28 && Math.abs(pk.z) < 0.095) {
            const gx = Math.abs(((pk.x + 1) * 18) % 1 - 0.5);
            const gz = Math.abs(((pk.z + 1) * 18) % 1 - 0.5);
            kCol = gx < 0.36 && gz < 0.36 ? [51, 65, 85] : [56, 189, 248];
          }
          hit.add(dKb, kCol, kCol[0] === 37 || kCol[0] === 56 ? 0.05 : 0.28, 61);
        }
        // Warm desk lamp on left + Solid cyan LED wall shelf behind (thick Z so zero raymarch gaps!)
        hit.add(sdCapsule(p, v3(-0.78, -0.34, 0.32), v3(-0.66, 0.24, 0.32), 0.02), [71, 85, 105], 0.3, 62);
        hit.add(sdSphere(sub3(p, v3(-0.62, 0.22, 0.34)), 0.055), [254, 243, 199], 0.04, 62);
        if (p.z < -0.5) {
          hit.add(sdRoundBox(sub3(p, v3(0.56, 0.58, -0.88)), v3(0.42, 0.032, 0.12), 0.012), [71, 85, 105], 0.38, 62);
          hit.add(sdRoundBox(sub3(p, v3(0.56, 0.62, -0.82)), v3(0.40, 0.028, 0.055), 0.014), [37, 244, 238], 0.03, 62);
        }

        hit.merge(
          evalHumanStreamerSDF(p, {
            pos: v3(-0.08, 0, 0),
            glasses: true,
            headYaw: s === 0 && phase < 0.5 ? 0.25 : 0,
            armLPitch: s === 3 ? -2.2 : -0.75,
            armRPitch: s === 1 ? -1.15 : s === 3 ? -2.2 : -0.75,
            expression: s >= 2 ? "shocked" : "smile",
            topColor: [51, 65, 85]
          })
        );

        if (s === 1) {
          hit.add(sdRoundedCylinder(sub3(p, v3(0.26, 0.04, 0.52)), 0.07, 0.012, 0.085), [248, 250, 252], 0.2, 63);
        }

        // Ginger Tabby Cat (peeks behind in Shot 1, leaps onto keyboard in Shot 2, sits staring at webcam in Shot 3)
        if (s >= 1) {
          const catPos =
            s === 1
              ? v3(0.52, -0.22, -0.15)
              : s === 2
              ? v3(mix(0.48, 0.12, smoothstep(0, 0.65, phase)), mix(-0.1, -0.16, phase) + Math.sin(phase * Math.PI) * 0.26, mix(0.0, 0.52, phase))
              : v3(0.14, -0.16, 0.52);
          const qc = sub3(p, catPos);
          hit.add(sdRoundBox(qc, v3(0.13, 0.11, 0.14), 0.07), [249, 115, 22], 0.35, 64);
          const ch = sub3(qc, v3(0, 0.14, 0.06));
          const dCatHead = sdSphere(ch, 0.105);
          if (dCatHead < hit.d) {
            let cCol = [251, 146, 60];
            if (ch.z > 0.06 && Math.abs(Math.abs(ch.x) - 0.038) < 0.018 && Math.abs(ch.y - 0.015) < 0.018) cCol = [15, 23, 42];
            else if (ch.y > 0.04 && Math.abs(ch.x) < 0.014) cCol = [194, 65, 12];
            hit.add(dCatHead, cCol, 0.32, 64);
          }
          hit.add(sdRoundBox(sub3(ch, v3(-0.065, 0.095, 0)), v3(0.028, 0.042, 0.018), 0.008), [249, 115, 22], 0.35, 64);
          hit.add(sdRoundBox(sub3(ch, v3(0.065, 0.095, 0)), v3(0.028, 0.042, 0.018), 0.008), [249, 115, 22], 0.35, 64);
        }
        return hit;
      }
    };
  }

  // 5. Wuxia Sword Flight Selfie Live (Cloud Sea + Glowing Rune Sword + Red-Crowned White Spirit Crane)
  if (slug === "wuxia_sword_flight_live") {
    const roll = s === 2 ? Math.sin(phase * Math.PI * 4) * 0.18 : 0;
    return {
      cam: {
        // Keep Shot 1 head well below top HUD safe-zone while showing the glowing sword underfoot!
        ro: v3(0.08, s === 1 ? 0.56 : 0.48, s === 1 ? 2.86 : 2.38),
        ta: v3(0, s === 1 ? -0.28 : 0.16, 0),
        roll,
        fov: 1.56,
        bgTop: [56, 189, 248],
        bgBot: [254, 243, 199],
        rimTint: [253, 224, 71],
        floorY: null
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Hovering Jade-Bronze Flying Sword underfoot with glowing gold crossguard & cyan rune blade
        const ps = sub3(p, v3(0, -0.96, 0));
        hit.add(sdRoundBox(ps, v3(0.17, 0.028, 0.92), 0.012), [45, 212, 191], 0.06, 70);
        hit.add(sdRoundBox(sub3(ps, v3(0, 0.012, -0.68)), v3(0.30, 0.035, 0.065), 0.012), [250, 204, 21], 0.16, 70);

        // Cloud puffs below
        if (p.y < -0.75) {
          hit.add(sdRoundBox(sub3(p, v3(-0.75, -1.25, -0.6)), v3(0.55, 0.14, 0.35), 0.12), [255, 255, 255], 0.45, 71);
          hit.add(sdRoundBox(sub3(p, v3(0.72, -1.18, -0.8)), v3(0.62, 0.15, 0.38), 0.12), [254, 249, 195], 0.45, 71);
        }

        hit.merge(
          evalHumanStreamerSDF(p, {
            pos: v3(0, 0, 0),
            showLegs: true,
            wuxiaBun: true,
            crookedBun: s === 3,
            armRPitch: -1.28,
            armLPitch: s === 3 ? -1.85 : -0.45,
            expression: s === 2 ? "shocked" : s === 3 ? "deadpan" : "grin",
            topColor: [186, 230, 253],
            lavalier: false
          })
        );

        // Sculpted Red-Crowned White Spirit Crane (丹顶白鹤) photobombing right shoulder in Shot 2!
        if (s === 2) {
          const cp = rotY(sub3(p, v3(mix(0.82, 0.44, phase), 0.50, -0.28)), 0.32);
          hit.add(sdRoundBox(cp, v3(0.14, 0.095, 0.20), 0.075), [255, 255, 255], 0.28, 72);
          // Graceful S-neck + white head + crimson red crown + golden beak
          hit.add(sdCapsule(cp, v3(0, 0.05, 0.14), v3(-0.04, 0.25, 0.22), 0.036), [255, 255, 255], 0.28, 72);
          hit.add(sdSphere(sub3(cp, v3(-0.04, 0.27, 0.23)), 0.048), [255, 255, 255], 0.28, 72);
          hit.add(sdSphere(sub3(cp, v3(-0.04, 0.31, 0.23)), 0.024), [239, 68, 68], 0.18, 72);
          hit.add(sdCapsule(cp, v3(-0.04, 0.26, 0.27), v3(-0.06, 0.24, 0.38), 0.016), [250, 204, 21], 0.20, 72);
          // Flapping wings with black trailing tips
          const wingAng = Math.sin(phase * Math.PI * 6) * 0.35 + 0.18;
          const pwL = rotZ(sub3(cp, v3(-0.12, 0.04, 0)), -wingAng);
          const pwR = rotZ(sub3(cp, v3(0.12, 0.04, 0)), wingAng);
          hit.add(sdRoundBox(sub3(pwL, v3(-0.18, 0, 0)), v3(0.18, 0.022, 0.12), 0.012), pwL.x < -0.26 ? [30, 41, 59] : [248, 250, 252], 0.3, 72);
          hit.add(sdRoundBox(sub3(pwR, v3(0.18, 0, 0)), v3(0.18, 0.022, 0.12), 0.012), pwR.x > 0.26 ? [30, 41, 59] : [248, 250, 252], 0.3, 72);
        }
        return hit;
      }
    };
  }

  // 6. Roblox Sky-Obby + Track-B PiP Facecam
  if (slug === "roblox_obby_rage_pip") {
    const jumpArc = s === 1 ? Math.sin(phase * Math.PI) * 0.42 : 0;
    const swing = s === 1 ? Math.sin(phase * Math.PI * 2) * 0.65 : 0;
    const fallRoll = s === 2 ? smoothstep(0.15, 0.85, phase) * 1.15 : 0;
    return {
      cam: {
        ro: v3(s === 1 ? 0.95 : -0.45, 0.52, 2.95),
        ta: v3(0, -0.05, 0),
        fov: 1.88,
        bgTop: [14, 116, 144],
        bgBot: [186, 230, 253],
        floorY: null
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Floating SmoothPlastic Sky Pads + Glowing Red Killbrick
        hit.add(sdRoundBox(sub3(p, v3(-0.55, -1.08, 0)), v3(0.48, 0.07, 0.48), 0.02), [244, 114, 182], 0.22, 80);
        hit.add(sdRoundBox(sub3(p, v3(0.55, -0.96, 0)), v3(0.48, 0.07, 0.48), 0.02), [52, 211, 153], 0.22, 80);
        if (s === 2) {
          hit.add(sdRoundBox(sub3(p, v3(0.12, -0.88, 0)), v3(0.08, 0.045, 0.46), 0.012), [255, 36, 56], 0.03, 81);
        }
        const avX = s === 0 ? -0.48 : s === 1 ? mix(-0.42, 0.22, phase) : s === 2 ? 0.14 : -0.48;
        hit.merge(
          evalRobloxAvatarSDF(p, {
            pos: v3(avX, jumpArc - (s === 2 ? phase * 0.25 : 0), 0),
            yaw: s === 0 || s === 3 ? 0.15 : 0.48,
            roll: -fallRoll,
            armLPitch: s === 0 ? -0.9 : swing,
            armRPitch: -swing,
            legLPitch: -swing,
            legRPitch: swing,
            expression: s === 2 ? "shocked" : s === 3 ? "tears" : "grin",
            theme: "obby"
          })
        );
        return hit;
      },
      pipScene: {
        cam: {
          ro: v3(s >= 2 ? Math.sin(phase * Math.PI * 8) * 0.04 : 0, 0.42, 1.92),
          ta: v3(0, 0.34, 0),
          fov: 1.85,
          bgTop: [49, 46, 129],
          bgBot: [15, 23, 42],
          rimTint: [244, 63, 94],
          floorY: null
        },
        sceneFn: (p) => {
          const hit = new SceneHit();
          hit.add(sdRoundBox(sub3(p, v3(0, -0.22, 0.35)), v3(0.8, 0.04, 0.35), 0.015), [51, 65, 85], 0.3, 82);
          const slamArm = s === 3 ? mix(-1.9, -0.85, smoothstep(0.1, 0.65, phase)) : -0.4;
          hit.merge(
            evalRobloxAvatarSDF(p, {
              pos: v3(0, 0, 0),
              waistPitch: s === 1 ? 0.16 : 0,
              armLPitch: s === 3 ? slamArm : -0.35,
              armRPitch: s === 0 ? -1.4 : s === 3 ? slamArm : -0.35,
              expression: s === 0 ? "smirk" : s === 1 ? "grin" : s === 2 ? "shocked" : "tears",
              theme: "obby",
              headset: true
            })
          );
          return hit;
        }
      }
    };
  }

  // 7. Roblox DOORS Corridor Selfie-Stick Live
  if (slug === "roblox_doors_irl_selfie") {
    const flickerRed = s === 1 && Math.floor(phase * 6) % 2 === 1;
    const shake = s === 2 ? Math.sin(phase * Math.PI * 10) * 0.04 : 0;
    return {
      cam: {
        ro: v3(shake, 0.38, s === 3 ? 1.58 : 2.18),
        ta: v3(0, 0.30, 0),
        fov: 1.55,
        bgTop: flickerRed ? [88, 18, 28] : [24, 18, 28],
        bgBot: [44, 28, 32],
        rimTint: [250, 204, 21],
        floorY: -1.02,
        floorCol1: [92, 58, 36],
        floorCol2: [76, 46, 28]
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        // Door 050 behind in corridor (or slatted closet in Shot 3)
        if (s === 3) {
          hit.add(sdRoundBox(sub3(p, v3(-0.42, 0.25, 0.68)), v3(0.18, 0.95, 0.03), 0.01), [92, 58, 36], 0.4, 85);
          hit.add(sdRoundBox(sub3(p, v3(0.42, 0.25, 0.68)), v3(0.18, 0.95, 0.03), 0.01), [92, 58, 36], 0.4, 85);
        } else if (p.z < -0.55) {
          hit.add(sdRoundBox(sub3(p, v3(0, 0.1, -1.25)), v3(0.42, 0.85, 0.05), 0.015), [112, 68, 40], 0.38, 85);
          hit.add(sdRoundBox(sub3(p, v3(0, 0.48, -1.19)), v3(0.14, 0.06, 0.015), 0.008), [250, 204, 21], 0.12, 85);
        }
        // Dark shadow figure with glowing white eyes appearing behind left shoulder in Shot 2!
        if (s === 2) {
          hit.merge(
            evalRobloxAvatarSDF(p, {
              pos: v3(-0.38, 0.08, -0.52),
              yaw: 0.15,
              theme: "shadow"
            })
          );
        }
        hit.merge(
          evalRobloxAvatarSDF(p, {
            pos: v3(0.06, 0, 0.12),
            yaw: -0.14,
            armRPitch: -1.22,
            armLPitch: s === 0 ? -0.95 : -0.25,
            selfieStick: s < 3,
            expression: s === 1 ? "deadpan" : s === 2 ? "shocked" : s === 3 ? "tears" : "smirk",
            theme: "commuter"
          })
        );
        return hit;
      }
    };
  }

  // 8. Roblox Pet Hatch 50/50 Co-Host PK Split-Screen
  const tapArm = s === 1 ? mix(-1.4, -0.75, smoothstep(0.1, 0.7, phase)) : -0.35;
  return {
    cam: {
      ro: v3(0, 0.34, 3.35),
      ta: v3(0, 0.08, 0),
      fov: 1.92,
      bgTop: [30, 27, 58],
      bgBot: [15, 23, 42],
      splitScreenTint: true,
      floorY: null
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      // Left & Right studio desks
      hit.add(sdRoundBox(sub3(p, v3(-0.62, -0.36, 0.42)), v3(0.52, 0.045, 0.36), 0.015), [244, 114, 182], 0.28, 90);
      hit.add(sdRoundBox(sub3(p, v3(0.62, -0.36, 0.42)), v3(0.52, 0.045, 0.36), 0.015), [148, 163, 184], 0.35, 90);

      // Left Host: Y2K Streamer
      hit.merge(
        evalRobloxAvatarSDF(p, {
          pos: v3(-0.62, 0, 0),
          yaw: s === 2 ? 0.48 : 0.15,
          waistPitch: s === 3 ? 1.15 : 0,
          armRPitch: s === 0 ? -1.1 : tapArm,
          expression: s === 2 ? "shocked" : s === 3 ? "dizzy" : "smirk",
          theme: "y2k"
        })
      );
      // Right Host: Classic R6 Noob
      hit.merge(
        evalRobloxAvatarSDF(p, {
          pos: v3(0.62, 0, 0),
          yaw: -0.15,
          armRPitch: s === 3 ? -1.05 : tapArm,
          colaCan: s === 3,
          expression: "smile",
          theme: "noob"
        })
      );

      // Eggs before hatch (Shots 0 & 1) vs Pebble + Blocky Mythic Dragon (Shots 2 & 3)
      if (s <= 1) {
        const glow = s === 1 ? 0.04 : 0.22;
        hit.add(sdRoundBox(sub3(p, v3(-0.56, -0.18, 0.52)), v3(0.11, 0.14, 0.11), 0.06), [250, 204, 21], glow, 91);
        hit.add(sdRoundBox(sub3(p, v3(0.56, -0.18, 0.52)), v3(0.11, 0.14, 0.11), 0.06), [226, 232, 240], glow, 91);
      } else {
        // Left: tiny dull gray pebble
        hit.add(sdRoundBox(sub3(p, v3(-0.56, -0.26, 0.52)), v3(0.06, 0.045, 0.06), 0.02), [100, 116, 139], 0.48, 92);
        // Right: Sculpted Hovering Blocky Cyan-Gold Mythic Dragon above Noob's shoulder (unobstructed smile!)
        const dy = 0.72 + Math.sin(phase * Math.PI * 2) * 0.05;
        const qd = rotY(sub3(p, v3(0.32, dy, 0.38)), -0.38);
        hit.add(sdRoundBox(qd, v3(0.11, 0.09, 0.14), 0.022), [37, 244, 238], 0.06, 93);
        const dh = sub3(qd, v3(0, 0.08, 0.15));
        const dDrgHead = sdRoundBox(dh, v3(0.085, 0.075, 0.09), 0.018);
        if (dDrgHead < hit.d) {
          let drgCol = [56, 189, 248];
          if (dh.z > 0.07 && Math.abs(Math.abs(dh.x) - 0.038) < 0.016 && Math.abs(dh.y - 0.015) < 0.018) drgCol = [15, 23, 42];
          hit.add(dDrgHead, drgCol, 0.08, 93);
        }
        // Golden blocky horns + flapping golden neon wing plates
        hit.add(sdRoundBox(sub3(dh, v3(-0.05, 0.095, -0.02)), v3(0.018, 0.042, 0.018), 0.005), [250, 204, 21], 0.05, 93);
        hit.add(sdRoundBox(sub3(dh, v3(0.05, 0.095, -0.02)), v3(0.018, 0.042, 0.018), 0.005), [250, 204, 21], 0.05, 93);
        const flap = Math.sin(phase * Math.PI * 4) * 0.28 + 0.22;
        hit.add(sdRoundBox(sub3(rotZ(sub3(qd, v3(-0.10, 0.04, 0)), -flap), v3(-0.13, 0, 0)), v3(0.13, 0.020, 0.09), 0.008), [250, 204, 21], 0.05, 93);
        hit.add(sdRoundBox(sub3(rotZ(sub3(qd, v3(0.10, 0.04, 0)), flap), v3(0.13, 0, 0)), v3(0.13, 0.020, 0.09), 0.008), [250, 204, 21], 0.05, 93);
      }
      return hit;
    }
  };
}

// ---------- Declarative Custom Spec Scene Fallback ----------
function buildCustomSpecScene(specData, shotIdx, phase = 0.5) {
  const slug = specData.slug || "";
  if (
    [
      "irl_night_market_selfie",
      "desk_unboxing_autofocus",
      "midnight_corridor_fpv_live",
      "late_night_study_webcam",
      "wuxia_sword_flight_live",
      "roblox_obby_rage_pip",
      "roblox_doors_irl_selfie",
      "roblox_pet_hatch_pk"
    ].includes(slug)
  ) {
    return buildEpisodeScene(slug, shotIdx, phase);
  }

  const isRoblox = specData.style === "roblox-blocky";
  const rig = specData.rig || "desktop-webcam";
  const shake = shotIdx === 2 ? Math.sin(phase * Math.PI * 8) * 0.03 : 0;
  const expr = shotIdx === 2 ? "shocked" : shotIdx === 3 ? "tears" : "smile";

  const baseScene = {
    cam: {
      ro: v3(shake, 0.40, rig === "handheld-selfie-irl" ? 2.05 : 2.45),
      ta: v3(0, 0.18, 0),
      fov: rig === "handheld-selfie-irl" ? 1.55 : 1.85,
      bgTop: [15, 23, 42],
      bgBot: [30, 41, 59],
      splitScreenTint: rig === "pk-cohost-split",
      floorY: -0.95
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.add(sdRoundBox(sub3(p, v3(0, -0.38, 0.45)), v3(1.2, 0.045, 0.48), 0.02), [51, 65, 85], 0.32, 95);
      if (isRoblox) {
        hit.merge(
          evalRobloxAvatarSDF(p, {
            pos: v3(0, 0, 0),
            headYaw: shotIdx === 1 ? 0.22 : 0,
            armRPitch: shotIdx === 0 ? -1.15 : -0.45,
            expression: expr,
            theme: "obby",
            headset: true
          })
        );
      } else {
        hit.merge(
          evalHumanStreamerSDF(p, {
            pos: v3(0, 0, 0),
            headYaw: shotIdx === 1 ? 0.22 : 0,
            armRPitch: rig === "handheld-selfie-irl" ? -1.25 : shotIdx === 0 ? -1.05 : -0.55,
            expression: expr
          })
        );
      }
      return hit;
    }
  };

  if (rig === "pip-facecam-rig") {
    baseScene.pipScene = {
      cam: { ro: v3(0, 0.42, 1.95), ta: v3(0, 0.34, 0), fov: 1.85, bgTop: [49, 46, 129], bgBot: [15, 23, 42], floorY: null },
      sceneFn: baseScene.sceneFn
    };
  }
  return baseScene;
}

// ---------- Timing & Synthesized Live WAV Audio ----------
export function computeEpisodeTimingPlan(specData = {}) {
  const shots = Array.isArray(specData.shots) && specData.shots.length > 0 ? specData.shots : [{}];
  const sumShotSec = shots.reduce((acc, s) => acc + (Number(s.durationSec) || 0), 0);
  const targetTotalSec = Number(specData.durationSeconds) || (sumShotSec > 0 ? sumShotSec : shots.length * 3.75);
  const fallbackSec = targetTotalSec / shots.length;
  const rawDurations = shots.map((s) => Number(s.durationSec) || fallbackSec);
  const scaleSec = targetTotalSec / (rawDurations.reduce((a, b) => a + b, 0) || targetTotalSec);
  const shotDurations = rawDurations.map((d) => Number((d * scaleSec).toFixed(3)));
  const totalDurationSec = Number(shotDurations.reduce((a, b) => a + b, 0).toFixed(3));

  const sampleFps = clamp(Number(specData.sampleFps) || 2.4, 1.6, 8);
  const shotFrameCounts = shotDurations.map((d) => Math.max(4, Math.round(d * sampleFps)));
  const totalFrames = shotFrameCounts.reduce((a, b) => a + b, 0);
  const inFps = Number((totalFrames / totalDurationSec).toFixed(4));
  return { shotDurations, totalDurationSec, shotFrameCounts, totalFrames, inFps };
}

export function buildEpisodeWavBuffer(shots = [], shotDurationsOrScalar = 3.75) {
  const sampleRate = 22050;
  const durations = Array.isArray(shotDurationsOrScalar)
    ? shotDurationsOrScalar
    : shots.map(() => Number(shotDurationsOrScalar) || 3.75);
  const totalSec = Math.max(2, durations.reduce((a, b) => a + b, 0));
  const numSamples = Math.floor(sampleRate * totalSec);
  const pcm = new Int16Array(numSamples);

  let cursorSec = 0;
  for (let s = 0; s < shots.length; s++) {
    const durSec = durations[s] || 3.75;
    const cue = (shots[s].sfxCue || (s === shots.length - 1 ? "win" : s === 0 ? "chime" : "boing")).toLowerCase();
    const startSample = Math.floor(cursorSec * sampleRate);
    const shotSamples = Math.floor(durSec * sampleRate);
    cursorSec += durSec;

    for (let i = 0; i < shotSamples && startSample + i < numSamples; i++) {
      const t = i / sampleRate;
      // Subtle live room chat-tick & synth bed
      const chatTick = (t % 0.42) < 0.03 ? Math.sin(2 * Math.PI * 1320 * t) * 0.10 : 0;
      let val = chatTick + Math.sin(2 * Math.PI * 174 * t) * Math.exp(-(t % 0.5) * 8) * 0.10;

      if (cue === "chime" && t < 0.48) {
        const f = t < 0.15 ? 659.25 : 987.77;
        val += Math.sin(2 * Math.PI * f * t) * Math.exp(-((t % 0.15) * 8)) * 0.40;
      } else if (cue === "boing" && t < 0.45) {
        const f = 280 + 440 * (t / 0.45);
        val += Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 6) * 0.42;
      } else if (cue === "clack" && t < 0.18) {
        val += (Math.sin(2 * Math.PI * 880 * t) + Math.sin(2 * Math.PI * 390 * t)) * Math.exp(-t * 24) * 0.44;
      } else if (cue === "buzz" && t < 0.55) {
        val += (Math.sin(2 * Math.PI * 145 * t) > 0 ? 0.34 : -0.34) * Math.exp(-t * 4);
      } else if (cue === "siren" && t < 1.1) {
        const f = Math.floor(t * 5) % 2 === 0 ? 720 : 540;
        val += Math.sin(2 * Math.PI * f * t) * 0.28;
      } else if (cue === "drop" && t < 0.7) {
        const f = Math.max(110, 660 - 540 * (t / 0.7));
        val += Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 3.5) * 0.42;
      } else if (cue === "win" && t < 0.85) {
        const notes = [523.25, 659.25, 783.99, 1046.5];
        const nIdx = Math.min(3, Math.floor(t / 0.16));
        val += Math.sin(2 * Math.PI * notes[nIdx] * t) * Math.exp(-((t % 0.16) * 5)) * 0.44;
      }
      pcm[startSample + i] = clamp(Math.round(val * 28000), -32767, 32767);
    }
  }

  const header = Buffer.alloc(44);
  const byteLen = pcm.length * 2;
  header.write("RIFF", 0);
  header.writeUInt32LE(36 + byteLen, 4);
  header.write("WAVE", 8);
  header.write("fmt ", 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20);
  header.writeUInt16LE(1, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(sampleRate * 2, 28);
  header.writeUInt16LE(2, 32);
  header.writeUInt16LE(16, 34);
  header.write("data", 36);
  header.writeUInt32LE(byteLen, 40);
  return Buffer.concat([header, Buffer.from(pcm.buffer)]);
}

function runHudComposerOrFallback(manifestPath, customFallbackOut = null) {
  const pyScript = path.join(ROOT, "scripts", "compose_hud.py");
  try {
    execFileSync("python3", [pyScript, manifestPath], { stdio: "inherit" });
    return true;
  } catch (err) {
    // Pure-Node fallback: copy raw keyframes so environments without python3/Pillow never fail
    if (customFallbackOut) {
      for (const [src, dst] of customFallbackOut) {
        if (fs.existsSync(src)) {
          fs.mkdirSync(path.dirname(dst), { recursive: true });
          fs.copyFileSync(src, dst);
        }
      }
    }
    return false;
  }
}

// ---------- Mode A: Custom Spec Shard Renderer ----------
function renderCustomSpecShard(specPath, rawDir, force, shardIdx, shardCount) {
  const specData = JSON.parse(fs.readFileSync(specPath, "utf8").replace(/^\uFEFF/, ""));
  const { shotFrameCounts } = computeEpisodeTimingPlan(specData);
  const prefix = (specData.slug || path.basename(specPath, path.extname(specPath)) || "episode").replace(/[^a-z0-9_-]/gi, "_");

  fs.mkdirSync(rawDir, { recursive: true });
  let taskId = 0;
  const writePng = (fname, w, h, fn) => {
    if (taskId++ % shardCount !== shardIdx) return;
    const outP = path.join(rawDir, fname);
    if (!force && fs.existsSync(outP) && fs.statSync(outP).size > 800) return;
    fs.writeFileSync(outP, encodePNG(w, h, fn()));
  };

  // 3-State Setup Anchor Views
  for (const [fname, headYaw, camRo] of [
    ["setup_0deg.png", 0.0, v3(0, 0.42, 2.25)],
    ["setup_15deg.png", 0.28, v3(0, 0.42, 2.25)],
    ["setup_side.png", 0.0, v3(1.65, 0.45, 1.65)]
  ]) {
    writePng(fname, 270, 345, () => {
      const sc = buildCustomSpecScene(specData, 0, 0.5);
      return render3DViewport(270, 345, (p) => {
        if (specData.style === "roblox-blocky") {
          return evalRobloxAvatarSDF(p, { headYaw, headset: true, theme: "obby" });
        }
        return evalHumanStreamerSDF(p, { headYaw, glasses: true });
      }, { ...sc.cam, ro: camRo, ta: v3(0, 0.25, 0), maxSteps: 26 });
    });
  }

  for (let s = 0; s < specData.shots.length; s++) {
    writePng(`${prefix}_shot_${s}.png`, 270, 480, () => {
      const sc = buildCustomSpecScene(specData, s, 0.58);
      return render3DViewport(270, 480, sc.sceneFn, sc.cam);
    });
    const probe = buildCustomSpecScene(specData, s, 0.58);
    if (probe.pipScene) {
      writePng(`${prefix}_pip_shot_${s}.png`, 135, 180, () =>
        render3DViewport(135, 180, probe.pipScene.sceneFn, { ...probe.pipScene.cam, maxSteps: 22 })
      );
    }
  }

  let frameIdx = 0;
  for (let s = 0; s < specData.shots.length; s++) {
    const count = shotFrameCounts[s];
    for (let f = 0; f < count; f++) {
      const phase = (f + 0.5) / count;
      const cur = frameIdx++;
      writePng(`${prefix}_anim_${String(cur).padStart(4, "0")}.png`, 216, 384, () => {
        const sc = buildCustomSpecScene(specData, s, phase);
        return render3DViewport(216, 384, sc.sceneFn, { ...sc.cam, maxSteps: 24 });
      });
      const probe = buildCustomSpecScene(specData, s, phase);
      if (probe.pipScene) {
        writePng(`${prefix}_pip_anim_${String(cur).padStart(4, "0")}.png`, 108, 144, () =>
          render3DViewport(108, 144, probe.pipScene.sceneFn, { ...probe.pipScene.cam, maxSteps: 20 })
        );
      }
    }
  }
}

// ---------- Mode B: Full Repository Showcase & 8 Examples Shard Renderer ----------
function renderShowcaseShard(rawDir, force, shardIdx, shardCount) {
  fs.mkdirSync(rawDir, { recursive: true });
  let taskId = 0;
  const writePng = (fname, w, h, fn) => {
    if (taskId++ % shardCount !== shardIdx) return;
    const outP = path.join(rawDir, fname);
    if (!force && fs.existsSync(outP) && fs.statSync(outP).size > 800) return;
    fs.writeFileSync(outP, encodePNG(w, h, fn()));
  };

  // 1. Setup 3-state sheet panels
  for (const [fname, headYaw, ro] of [
    ["setup_0deg.png", 0.0, v3(0, 0.44, 2.25)],
    ["setup_15deg.png", 0.28, v3(0, 0.44, 2.25)],
    ["setup_side.png", 0.0, v3(1.65, 0.48, 1.60)]
  ]) {
    writePng(fname, 270, 345, () =>
      render3DViewport(
        270,
        345,
        (p) => {
          const hit = new SceneHit();
          hit.add(sdRoundBox(sub3(p, v3(0, -0.36, 0.45)), v3(1.1, 0.045, 0.45), 0.02), [148, 163, 184], 0.3, 40);
          hit.add(sdCapsule(p, v3(-0.78, -0.25, 0.62), v3(-0.34, 0.16, 0.50), 0.024), [30, 41, 59], 0.35, 41);
          hit.add(sdRoundedCylinder(sub3(p, v3(-0.32, 0.20, 0.50)), 0.052, 0.02, 0.075), [15, 23, 42], 0.45, 41);
          hit.merge(evalHumanStreamerSDF(p, { headYaw, glasses: true, topColor: [37, 99, 235] }));
          return hit;
        },
        { ro, ta: v3(0, 0.20, 0.15), fov: 1.88, bgTop: [15, 23, 42], bgBot: [30, 41, 59], rimTint: [37, 244, 238], floorY: null }
      )
    );
  }

  // 2. Clean base frame for 5-Platform HUD Atlas + 4-Way Drift Comparison
  writePng("atlas_clean_base.png", 270, 480, () => {
    const sc = buildEpisodeScene("irl_night_market_selfie", 0, 0.55);
    return render3DViewport(270, 480, sc.sceneFn, sc.cam);
  });

  // Drift Bad 1: Detached far-away third-person cinema wide shot with letterbox bars
  writePng("drift_bad_cinema.png", 270, 480, () => {
    const sc = buildEpisodeScene("irl_night_market_selfie", 0, 0.5);
    const rgba = render3DViewport(270, 480, sc.sceneFn, {
      ...sc.cam,
      ro: v3(2.8, 1.45, 4.2),
      ta: v3(0, 0.0, 0),
      fov: 2.2
    });
    // Cinema 2.39:1 black letterbox bars
    for (let y = 0; y < 480; y++) {
      if (y < 92 || y > 388) {
        for (let x = 0; x < 270; x++) {
          const i = (y * 270 + x) * 4;
          rgba[i] = 6; rgba[i + 1] = 8; rgba[i + 2] = 12;
        }
      }
    }
    return rgba;
  });

  // Drift Bad 2: Melted / garbled burned-in AI diffusion UI artifacts
  writePng("drift_bad_gibberish.png", 270, 480, () => {
    const sc = buildEpisodeScene("irl_night_market_selfie", 2, 0.5);
    const rgba = render3DViewport(270, 480, sc.sceneFn, sc.cam);
    // Simulate warped, smeared alien glyph blobs burned into diffusion pixels
    for (let y = 320; y < 445; y++) {
      for (let x = 18; x < 215; x++) {
        const wave = Math.sin(x * 0.23 + y * 0.19) * Math.cos(y * 0.37);
        if (wave > 0.38 && ((y - 320) % 28 < 18)) {
          const i = (y * 270 + x) * 4;
          rgba[i] = 250; rgba[i + 1] = 85 + ((x * 7) % 120); rgba[i + 2] = 160;
        }
      }
    }
    return rgba;
  });

  // 3. All 8 Built-in Examples (Keyframes + Animation Frames)
  for (const tplKey of Object.keys(TEMPLATES)) {
    const plan = compileStoryboard({ template: tplKey, engine: "local3d", sampleFps: 2.0 });
    const slug = plan.slug;
    const { shotFrameCounts } = computeEpisodeTimingPlan({ ...plan, sampleFps: 2.0 });

    for (let s = 0; s < plan.shots.length; s++) {
      writePng(`${slug}_shot_${s}.png`, 270, 480, () => {
        const sc = buildEpisodeScene(slug, s, 0.58);
        return render3DViewport(270, 480, sc.sceneFn, sc.cam);
      });
      const probe = buildEpisodeScene(slug, s, 0.58);
      if (probe.pipScene) {
        writePng(`${slug}_pip_shot_${s}.png`, 135, 180, () =>
          render3DViewport(135, 180, probe.pipScene.sceneFn, { ...probe.pipScene.cam, maxSteps: 22 })
        );
      }
    }

    let fCursor = 0;
    for (let s = 0; s < plan.shots.length; s++) {
      const fCount = shotFrameCounts[s];
      for (let f = 0; f < fCount; f++) {
        const phase = (f + 0.5) / fCount;
        const idx = fCursor++;
        writePng(`${slug}_anim_${String(idx).padStart(4, "0")}.png`, 216, 384, () => {
          const sc = buildEpisodeScene(slug, s, phase);
          return render3DViewport(216, 384, sc.sceneFn, { ...sc.cam, maxSteps: 24 });
        });
        const probe = buildEpisodeScene(slug, s, phase);
        if (probe.pipScene) {
          writePng(`${slug}_pip_anim_${String(idx).padStart(4, "0")}.png`, 108, 144, () =>
            render3DViewport(108, 144, probe.pipScene.sceneFn, { ...probe.pipScene.cam, maxSteps: 20 })
          );
        }
      }
    }
  }
}

function buildShowcaseManifest(rawDir) {
  const showcaseDir = path.join(ROOT, "assets", "showcase");
  fs.mkdirSync(showcaseDir, { recursive: true });

  const heroSlugs = new Set([
    "irl_night_market_selfie",
    "wuxia_sword_flight_live",
    "roblox_obby_rage_pip",
    "roblox_pet_hatch_pk"
  ]);

  const cases = Object.keys(TEMPLATES).map((tplKey) => {
    const plan = compileStoryboard({ template: tplKey, engine: "local3d" });
    const slug = plan.slug;
    const exDir = path.join(ROOT, "examples", tplKey, "assets");
    fs.mkdirSync(exDir, { recursive: true });

    const { shotDurations, shotFrameCounts, inFps } = computeEpisodeTimingPlan({ ...plan, sampleFps: 2.0 });
    const wavPath = path.join(rawDir, `${slug}_audio.wav`);
    fs.writeFileSync(wavPath, buildEpisodeWavBuffer(plan.shots, shotDurations));

    return {
      prefix: slug,
      titleZh: plan.titleZh,
      titleEn: plan.titleEn,
      platform: plan.platform,
      rig: plan.rig,
      style: plan.style,
      host: plan.host,
      cohost: plan.cohost || "Momo",
      hudLang: plan.platform === "instagram" || plan.platform === "x" || plan.platform === "tiktok" ? "en" : "zh",
      inFps,
      wavPath,
      includeInHeroReel: heroSlugs.has(slug),
      reelLabel: `${tplKey.startsWith("roblox") ? "Roblox" : "AI Live"} · ${plan.platform.toUpperCase()}`,
      sheetZh: path.join(exDir, "storyboard_sheet.zh.png"),
      sheetEn: path.join(exDir, "storyboard_sheet.en.png"),
      sheetDefault: path.join(exDir, "storyboard_sheet.png"),
      gifPath: path.join(exDir, `${slug}.gif`),
      mp4Path: path.join(exDir, `${slug}.mp4`),
      shots: plan.shots.map((sh, idx) => {
        const num = String(idx + 1).padStart(2, "0");
        return {
          frameCount: shotFrameCounts[idx],
          labelZh: `${num} · ${sh.role}`,
          labelEn: `${num} · ${sh.role.split("/")[0].trim()}`,
          chatEn: sh.chatEn || "",
          hudMeta: sh.hudOverlay,
          savePath: path.join(exDir, `shot_${num}.png`)
        };
      })
    };
  });

  return {
    rawDir,
    turnaround: {
      titleZh: "直播间跨镜头一致性三态锚定卡 (0°主镜对视 · 15°副屏读弹幕 · 侧视机位与左置麦)",
      titleEn: "3-State Livestream Consistency Anchor Sheet (0° Lens · 15° Chat Glance · Side Rig Lock)",
      outZh: path.join(showcaseDir, "rig_setup_sheet.zh.png"),
      outEn: path.join(showcaseDir, "rig_setup_sheet.en.png"),
      outDefault: [path.join(showcaseDir, "rig_setup_sheet.png")],
      views: [
        { file: "setup_0deg.png", labelZh: "01 · 0° 主镜头眼神对视", labelEn: "01 · 0° Direct Lens Address" },
        { file: "setup_15deg.png", labelZh: "02 · 15° 偏轴扫视副屏弹幕", labelEn: "02 · 15° Off-Axis Chat Read" },
        { file: "setup_side.png", labelZh: "03 · 机位距离与左置悬臂麦锚定", labelEn: "03 · Optical Distance & Left Mic" }
      ]
    },
    platformAtlas: {
      baseFile: "atlas_clean_base.png",
      outZh: path.join(showcaseDir, "platform_hud_atlas.zh.png"),
      outEn: path.join(showcaseDir, "platform_hud_atlas.en.png"),
      outDefault: path.join(showcaseDir, "platform_hud_atlas.png"),
      items: [
        {
          platform: "douyin",
          host: "阿泽Live",
          labelZh: "抖音直播间 · 小黄车讲解卡",
          labelEn: "Douyin · Live Deal Card",
          borderColor: [254, 44, 85],
          hudMeta: buildShotHudTimeline({ hudPopup: "commerce_card", baseViewers: 21500 }, 1, 4, "douyin", "irl_night_market_selfie")
        },
        {
          platform: "kuaishou",
          host: "老铁实测",
          labelZh: "快手直播间 · 穿云箭连击x28",
          labelEn: "Kuaishou · SkyArrow Combo",
          borderColor: [255, 80, 0],
          hudMeta: buildShotHudTimeline(
            {
              hudPopup: "gift_combo",
              hudGiftZh: { sender: "榜一大哥", gift: "黄金穿云箭", combo: 28 },
              hudGiftEn: { sender: "IronBro_01", gift: "Sky Arrow", combo: 28 },
              baseViewers: 17400
            },
            2,
            4,
            "kuaishou",
            "desk_unboxing_autofocus"
          )
        },
        {
          platform: "instagram",
          host: "kaya.studio",
          labelZh: "Ins Live · 无框弹幕与提问卡",
          labelEn: "IG Live · Borderless + Q&A",
          borderColor: [225, 48, 108],
          hudMeta: buildShotHudTimeline({ hudPopup: "qa_pinned", baseViewers: 12400 }, 1, 4, "instagram", "midnight_corridor_fpv_live")
        },
        {
          platform: "x",
          host: "@dev_mika",
          labelZh: "X Live · 暗夜玻璃与六色飘心",
          labelEn: "X / Periscope · 6-Color Hearts",
          borderColor: [53, 177, 209],
          hudMeta: {
            ...buildShotHudTimeline({ hudPopup: "join_toast", baseViewers: 15800 }, 0, 4, "x", "late_night_study_webcam"),
            heartBurstIntensity: "high"
          }
        },
        {
          platform: "tiktok",
          host: "BloxyKai",
          labelZh: "TikTok Live · 玫瑰连击x99",
          labelEn: "TikTok · Galaxy Rose x99",
          borderColor: [37, 244, 238],
          hudMeta: buildShotHudTimeline(
            {
              hudPopup: "gift_combo_peak",
              hudGiftZh: { sender: "pixel_kai", gift: "Galaxy Rose", combo: 99 },
              hudGiftEn: { sender: "pixel_kai", gift: "Galaxy Rose", combo: 99 },
              baseViewers: 16200
            },
            3,
            4,
            "tiktok",
            "roblox_obby_rage_pip"
          )
        }
      ]
    },
    rigAtlas: {
      outZh: path.join(showcaseDir, "camera_rigs_atlas.zh.png"),
      outEn: path.join(showcaseDir, "camera_rigs_atlas.en.png"),
      outDefault: path.join(showcaseDir, "camera_rigs_atlas.png"),
      items: [
        {
          file: "irl_night_market_selfie_shot_0.png",
          rig: "handheld-selfie-irl",
          platform: "douyin",
          host: "Lin",
          shotIdx: 0,
          labelZh: "18mm 手持前置户外自拍",
          labelEn: "18mm Handheld IRL Selfie",
          hudMeta: buildShotHudTimeline({}, 0, 4, "douyin", "irl_night_market_selfie")
        },
        {
          file: "desk_unboxing_autofocus_shot_1.png",
          rig: "overhead-showcase-rig",
          platform: "kuaishou",
          host: "Kaya",
          shotIdx: 1,
          labelZh: "35mm 托底微距对焦 [AF-C]",
          labelEn: "35mm Palm Autofocus [AF-C]",
          hudMeta: buildShotHudTimeline({ hudPopup: "commerce_card" }, 1, 4, "kuaishou", "desk_unboxing_autofocus")
        },
        {
          file: "midnight_corridor_fpv_live_shot_0.png",
          rig: "chest-head-pov",
          platform: "instagram",
          host: "ren.urban",
          shotIdx: 0,
          labelZh: "16mm 胸挂第一人称双持",
          labelEn: "16mm Chest Dual-Hand POV",
          hudMeta: buildShotHudTimeline({}, 0, 4, "instagram", "midnight_corridor_fpv_live")
        },
        {
          file: "wuxia_sword_flight_live_shot_2.png",
          rig: "handheld-selfie-irl",
          platform: "douyin",
          host: "青云小师兄",
          shotIdx: 2,
          labelZh: "架空仙侠御剑自拍转译",
          labelEn: "Genre Plot -> Sword Selfie",
          hudMeta: buildShotHudTimeline({}, 2, 4, "douyin", "wuxia_sword_flight_live")
        },
        {
          file: "roblox_obby_rage_pip_shot_2.png",
          pipFile: "roblox_obby_rage_pip_pip_shot_2.png",
          rig: "pip-facecam-rig",
          platform: "tiktok",
          host: "BloxyKai",
          shotIdx: 2,
          labelZh: "Roblox 实况 + B轨反应小窗",
          labelEn: "Roblox Dual-Track + PiP",
          hudMeta: {
            ...buildShotHudTimeline({}, 2, 4, "tiktok", "roblox_obby_rage_pip"),
            style: "roblox-blocky",
            chatEn: "NOOOO!!"
          }
        },
        {
          file: "roblox_pet_hatch_pk_shot_2.png",
          rig: "pk-cohost-split",
          platform: "kuaishou",
          host: "Y2K_Queen",
          shotIdx: 2,
          labelZh: "Roblox 50/50 连麦 PK 分屏",
          labelEn: "Roblox 50/50 Co-Host PK",
          hudMeta: {
            ...buildShotHudTimeline({ pkScoreRatio: 0.16, hudPopup: "gift_combo" }, 2, 4, "kuaishou", "roblox_pet_hatch_pk"),
            style: "roblox-blocky"
          }
        }
      ]
    },
    drift: {
      outZh: path.join(showcaseDir, "clean_vs_hud_drift_comparison.zh.png"),
      outEn: path.join(showcaseDir, "clean_vs_hud_drift_comparison.en.png"),
      outDefault: path.join(showcaseDir, "clean_vs_hud_drift_comparison.png"),
      panels: [
        { file: "drift_bad_cinema.png", labelZh: "[X] 第三人称电影摇臂跑偏", labelEn: "[X] 3rd-Person Cinema Drift", color: [225, 29, 72] },
        { file: "drift_bad_gibberish.png", labelZh: "[X] AI直出乱码弹幕融化", labelEn: "[X] Burned-In Gibberish UI", color: [234, 88, 12] },
        { file: "atlas_clean_base.png", labelZh: "[OK] 纯净无字直播镜头底片", labelEn: "[OK] Clean Raw Camera Plate", color: [2, 132, 199] },
        { file: "atlas_clean_base.png", postHudPlatform: "douyin", labelZh: "[OK] 纯净底片 + 后置高清HUD", labelEn: "[OK] Clean Plate + Post-HUD", color: [22, 163, 74] }
      ]
    },
    heroReel: {
      gifPath: path.join(showcaseDir, "livestream_pov_reel.gif"),
      mp4Path: path.join(showcaseDir, "livestream_pov_reel.mp4")
    },
    cases
  };
}

// ---------- CLI Entry ----------
const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("render_preview.mjs");
if (isMain) {
  if (process.argv.includes("--help") || process.argv.includes("-h")) {
    console.log(`Usage:
  node scripts/render_preview.mjs --spec <episode.json> --out-dir <dir> [--platform <id>] [--workers <n>] [--force]
  node scripts/render_preview.mjs [--workers <n>] [--force]

Render 9:16 Livestream POV 3D preview videos (.mp4 + .gif), bilingual contact sheets,
3-state rig setup sheets, and multi-platform HUD overlays (douyin, kuaishou, instagram, x, tiktok, clean).`);
    process.exit(0);
  }

  const getArg = (flag) => {
    const idx = process.argv.indexOf(flag);
    return idx !== -1 && process.argv[idx + 1] ? process.argv[idx + 1] : null;
  };

  const specArg = getArg("--spec");
  const outDirArg = getArg("--out-dir");
  const platformOverride = getArg("--platform");
  const shardArg = getArg("--shard");
  const force = process.argv.includes("--force");

  if (specArg) {
    const absSpec = path.resolve(specArg);
    const specData = JSON.parse(fs.readFileSync(absSpec, "utf8").replace(/^\uFEFF/, ""));
    const outDir = outDirArg ? path.resolve(outDirArg) : path.join(path.dirname(absSpec), "assets");
    const tmpDir = getArg("--raw-dir") ? path.resolve(getArg("--raw-dir")) : path.join(outDir, ".render_tmp");

    if (shardArg) {
      const [sIdx, sTotal] = shardArg.split("/").map(Number);
      renderCustomSpecShard(absSpec, tmpDir, force, sIdx, sTotal);
      process.exit(0);
    }

    fs.mkdirSync(outDir, { recursive: true });
    fs.mkdirSync(tmpDir, { recursive: true });
    const workers = clamp(Number(getArg("--workers")) || 2, 1, 6);
    await Promise.all(
      Array.from({ length: workers }, (_, i) =>
        new Promise((resolve, reject) => {
          const args = [process.argv[1], "--spec", absSpec, "--out-dir", outDir, "--raw-dir", tmpDir, "--shard", `${i}/${workers}`];
          if (force) args.push("--force");
          const child = spawn(process.execPath, args, { stdio: "inherit" });
          child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`Shard ${i} exited ${code}`))));
        })
      )
    );

    const slug = (specData.slug || path.basename(absSpec, path.extname(absSpec))).replace(/[^a-z0-9_-]/gi, "_");
    const platformId = resolvePlatformPreset(platformOverride || specData.platform || "douyin").id;
    const { shotDurations, shotFrameCounts, inFps } = computeEpisodeTimingPlan(specData);
    const wavPath = path.join(tmpDir, `${slug}_audio.wav`);
    fs.writeFileSync(wavPath, buildEpisodeWavBuffer(specData.shots, shotDurations));

    const customManifest = {
      rawDir: tmpDir,
      turnaround: {
        titleZh: "直播间三态一致性参考卡",
        titleEn: "3-State Livestream Setup Sheet",
        outZh: path.join(outDir, "rig_setup_sheet.zh.png"),
        outEn: path.join(outDir, "rig_setup_sheet.en.png"),
        outDefault: [path.join(outDir, "rig_setup_sheet.png")],
        views: [
          { file: "setup_0deg.png", labelZh: "0° 主镜对视", labelEn: "0° Lens Address" },
          { file: "setup_15deg.png", labelZh: "15° 读弹幕", labelEn: "15° Chat Read" },
          { file: "setup_side.png", labelZh: "侧视机位锚点", labelEn: "Side Rig Lock" }
        ]
      },
      cases: [
        {
          prefix: slug,
          titleZh: specData.titleZh || slug,
          titleEn: specData.titleEn || slug,
          platform: platformId,
          rig: specData.rig || "desktop-webcam",
          style: specData.style || "realistic-irl",
          host: specData.host || "Alex",
          cohost: specData.cohost || "Momo",
          hudLang: ["instagram", "x", "tiktok"].includes(platformId) ? "en" : "zh",
          inFps,
          wavPath,
          sheetZh: path.join(outDir, "storyboard_sheet.zh.png"),
          sheetEn: path.join(outDir, "storyboard_sheet.en.png"),
          sheetDefault: path.join(outDir, "storyboard_sheet.png"),
          gifPath: path.join(outDir, `${slug}.gif`),
          mp4Path: path.join(outDir, `${slug}.mp4`),
          shots: specData.shots.map((sh, idx) => {
            const num = String(idx + 1).padStart(2, "0");
            return {
              frameCount: shotFrameCounts[idx],
              labelZh: `${num} · ${sh.role || `镜头 ${num}`}`,
              labelEn: `${num} · ${(sh.role || `Shot ${num}`).split("/")[0].trim()}`,
              chatEn: sh.chatEn || "",
              hudMeta: sh.hudOverlay || buildShotHudTimeline(sh, idx, specData.shots.length, platformId),
              savePath: path.join(outDir, `shot_${num}.png`)
            };
          })
        }
      ]
    };

    const mPath = path.join(tmpDir, "hud_manifest.json");
    fs.writeFileSync(mPath, JSON.stringify(customManifest, null, 2), "utf8");
    const fallbackCopies = specData.shots.map((_, i) => [
      path.join(tmpDir, `${slug}_shot_${i}.png`),
      path.join(outDir, `shot_${String(i + 1).padStart(2, "0")}.png`)
    ]);
    runHudComposerOrFallback(mPath, fallbackCopies);

    if (!process.argv.includes("--keep-tmp")) {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
    console.log(`Rendered custom livestream POV video (${platformId} HUD): ${path.join(outDir, `${slug}.mp4`)}`);
    process.exit(0);
  }

  // Full Showcase + 8 Flagship Examples Render
  const rawDir = getArg("--raw-dir") ? path.resolve(getArg("--raw-dir")) : path.join("/tmp", "livestream_pov_raw3d");
  if (shardArg) {
    const [sIdx, sTotal] = shardArg.split("/").map(Number);
    renderShowcaseShard(rawDir, force, sIdx, sTotal);
    process.exit(0);
  }

  fs.mkdirSync(rawDir, { recursive: true });
  const workers = clamp(Number(getArg("--workers")) || 6, 1, 8);
  await Promise.all(
    Array.from({ length: workers }, (_, i) =>
      new Promise((resolve, reject) => {
        const args = [process.argv[1], "--raw-dir", rawDir, "--shard", `${i}/${workers}`];
        if (force) args.push("--force");
        const child = spawn(process.execPath, args, { stdio: "inherit" });
        child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`Shard ${i} exited ${code}`))));
      })
    )
  );

  const manifest = buildShowcaseManifest(rawDir);
  const mPath = path.join(rawDir, "showcase_hud_manifest.json");
  fs.writeFileSync(mPath, JSON.stringify(manifest, null, 2), "utf8");
  runHudComposerOrFallback(mPath);
  if (!process.argv.includes("--keep-tmp")) {
    fs.rmSync(rawDir, { recursive: true, force: true });
  }
  console.log("Rendered all 8 Livestream POV example packages, 5-platform HUD atlas, and 4-up hero reel.");
}
