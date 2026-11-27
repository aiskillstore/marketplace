#!/usr/bin/env node
/**
 * render_preview.mjs
 * Blocky R6 / Chibi Studio 3D Preview & Set Renderer (Zero External Dependencies).
 *
 * Implements canonical blocky proportions (1 stud = 0.34 world units):
 * - Torso: 2.0 x 2.0 x 1.0 studs with 0.08 stud bevel + 3D collar/hoodie/pocket/cuffs
 * - Emblem: Original trademark-free geometric triangle / star / heart / moon badges
 * - Head:  1:1 barrel-beveled cylinder (R=0.64, H=1.24 studs) with flat 2D face decals
 * - Hair:  Full-coverage scalp dome + sculpted 3D hair locks / twin pigtails / 5-point crown
 * - Limbs: Flush 0.98 x 2.0 x 0.98 stud solid rectangular arms & legs + multi-part hand props
 * - World: Smooth architectural floor shaders (zero raised circular Lego floor bumps) + multi-part 3D props.
 */

import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { execFileSync, spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

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

function sdRoundBox(p, b, r) {
  const qx = Math.abs(p.x) - b.x + r;
  const qy = Math.abs(p.y) - b.y + r;
  const qz = Math.abs(p.z) - b.z + r;
  const ox = Math.max(qx, 0);
  const oy = Math.max(qy, 0);
  const oz = Math.max(qz, 0);
  return Math.hypot(ox, oy, oz) + Math.min(Math.max(qx, qy, qz), 0) - r;
}

function sdRoundedCylinder(p, ra, rb, h) {
  const dx = Math.hypot(p.x, p.z) - ra + rb;
  const dy = Math.abs(p.y) - h + rb;
  const ox = Math.max(dx, 0);
  const oy = Math.max(dy, 0);
  return Math.min(Math.max(dx, dy), 0) + Math.hypot(ox, oy) - rb;
}

function sdSphere(p, r) {
  return len3(p) - r;
}

function sdTaperedCapsule(p, a, b, r1, r2) {
  const pa = sub3(p, a);
  const ba = sub3(b, a);
  const baba = dot3(ba, ba) || 1e-6;
  const h = clamp(dot3(pa, ba) / baba, 0, 1);
  const r = r1 + (r2 - r1) * h;
  return len3(sub3(pa, mul3(ba, h))) - r;
}

function sdLegoCClaw(p, scale = 1.0) {
  const q = mul3(p, 1 / scale);
  const qRot = rotX(q, Math.PI / 2);
  const dOuter = sdRoundedCylinder(qRot, 0.16, 0.03, 0.10);
  const dInner = sdRoundedCylinder(qRot, 0.08, 0.01, 0.18);
  const dSlot = sdRoundBox(sub3(q, v3(0, -0.12, 0)), v3(0.07, 0.12, 0.18), 0.01);
  return Math.max(dOuter, -Math.min(dInner, dSlot)) * scale;
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

// ---------- 2D Face Decal Evaluator (with 1st-Class Pupil Gaze & Asymmetrical Brows) ----------
function evalFaceDecal(u, v, expression = "smile", faceMod = {}) {
  if (Math.abs(u) > 0.44 || Math.abs(v) > 0.44) return null;

  const ink = [16, 20, 28];
  const white = [255, 255, 255];
  const mouthIn = [82, 18, 24];
  const tongue = [244, 102, 112];
  const tear = [96, 195, 255];

  const gx = clamp(Number(faceMod.gazeX) || 0, -1, 1);
  const gy = clamp(Number(faceMod.gazeY) || 0, -1, 1);
  const browMode = String(faceMod.brows || "").toLowerCase();

  const eyeSign = u >= 0 ? 1 : -1;
  const eyeCx = eyeSign * 0.125;
  const lx = u - eyeCx; // signed offset inside each eye (+lx = screen right for BOTH eyes)
  const ex = Math.abs(u) - 0.125;
  const ey = v - 0.085;

  // 1. Expressive & Asymmetrical Eyebrows
  if (browMode && browMode !== "none") {
    if (browMode === "left-up-right-down" || browMode === "asymmetrical") {
      const targetEy = u < 0 ? 0.118 - lx * 0.18 : 0.088 + lx * 0.24;
      if (Math.abs(lx) < 0.074 && Math.abs(ey - targetEy) < 0.017) return ink;
    } else if (browMode === "right-up-left-down") {
      const targetEy = u < 0 ? 0.088 - lx * 0.24 : 0.118 + lx * 0.18;
      if (Math.abs(lx) < 0.074 && Math.abs(ey - targetEy) < 0.017) return ink;
    } else if (browMode === "furrowed") {
      const by = ey - (0.095 - (0.14 - Math.abs(u)) * 0.35);
      if (Math.abs(ex) < 0.075 && Math.abs(by) < 0.018) return ink;
    } else if (browMode === "worried") {
      const by = ey - (0.105 + (0.14 - Math.abs(u)) * 0.25);
      if (Math.abs(ex) < 0.075 && Math.abs(by) < 0.017) return ink;
    } else if (browMode === "raised") {
      const arch = 0.116 - lx * lx * 1.4;
      if (Math.abs(lx) < 0.072 && Math.abs(ey - arch) < 0.016) return ink;
    } else if (browMode === "flat") {
      if (Math.abs(lx) < 0.072 && Math.abs(ey - 0.098) < 0.016) return ink;
    }
  } else if (expression === "slam" || expression === "angry") {
    const by = ey - (0.095 - (0.14 - Math.abs(u)) * 0.35);
    if (Math.abs(ex) < 0.075 && Math.abs(by) < 0.018) return ink;
  } else if (expression === "shocked" || expression === "tears") {
    const by = ey - (0.105 + (0.14 - Math.abs(u)) * 0.25);
    if (Math.abs(ex) < 0.075 && Math.abs(by) < 0.016) return ink;
  } else if (expression === "smirk") {
    const slope = u > 0 ? 0.25 : -0.1;
    const by = ey - (0.095 + ex * slope);
    if (Math.abs(ex) < 0.072 && Math.abs(by) < 0.016) return ink;
  }

  if (expression === "tears") {
    if (Math.abs(ex) < 0.036 && v < 0.03 && v > -0.34) {
      return tear;
    }
  }

  // 2. Eyes with 1st-Class Directional Pupil Tracking
  if (expression === "deadpan") {
    const slx = lx - gx * 0.022;
    const sey = ey - gy * 0.012;
    if (Math.abs(slx) < 0.068 && Math.abs(sey) < 0.018) return ink;
    // Subtle directional iris drop under the flat line when actively side-eyeing a target
    if (Math.hypot(gx, gy) > 0.18) {
      const px = lx - gx * 0.034;
      const py = ey - gy * 0.014 + 0.022;
      if (ey < sey && Math.hypot(px / 0.024, py / 0.024) < 1.0) return ink;
    }
  } else if (expression === "sleepy") {
    const slx = lx - gx * 0.020;
    if (Math.abs(slx) < 0.070 && Math.abs(ey + 0.008) < 0.016) return ink;
    const lidR = Math.hypot(slx / 0.062, (ey + 0.008) / 0.038);
    if (ey < -0.008 && lidR < 1.0 && lidR > 0.70) return ink;
  } else if (expression === "dizzy") {
    const d1 = Math.abs(ex - ey);
    const d2 = Math.abs(ex + ey);
    if (Math.abs(ex) < 0.062 && Math.abs(ey) < 0.062 && (d1 < 0.02 || d2 < 0.02)) return ink;
  } else if (expression === "shocked") {
    const rOut = Math.hypot((lx - gx * 0.006) / 0.074, (ey - gy * 0.005) / 0.084);
    if (rOut < 1.0) {
      if (rOut > 0.82) return ink;
      const px = lx - gx * 0.028;
      const py = ey - gy * 0.028;
      const rPupil = Math.hypot(px / 0.029, py / 0.033);
      if (rPupil < 1.0) return ink;
      return white;
    }
  } else {
    const elx = lx - gx * 0.026;
    const eey = ey - gy * 0.018;
    const rEye = Math.hypot(elx / 0.044, eey / 0.078);
    if (rEye < 1.0) {
      const hl = Math.hypot((elx - gx * 0.008 + 0.012) / 0.015, (eey - gy * 0.006 - 0.028) / 0.021);
      if (hl < 1.0) return white;
      return ink;
    }
  }

  const my = v + 0.115;
  if (expression === "shocked" || expression === "tears" || expression === "grin") {
    const rx = expression === "shocked" ? 0.075 : 0.125;
    const ry = 0.085;
    if (expression === "shocked") {
      const rM = Math.hypot(u / rx, my / ry);
      if (rM < 1.0) {
        if (rM > 0.78) return ink;
        if (my > 0.025) return white;
        if (my < -0.025) return tongue;
        return mouthIn;
      }
    } else {
      const inTop = my <= 0.035 && my >= -ry;
      const rArc = Math.hypot(u / rx, (my - 0.035) / (ry + 0.035));
      if (inTop && rArc < 1.0) {
        if (rArc > 0.84 || my > 0.018) return ink;
        if (my > -0.012) return white;
        if (my < -0.045 && Math.abs(u) < rx * 0.55) return tongue;
        return mouthIn;
      }
    }
  } else if (expression === "sleepy") {
    const rYawn = Math.hypot(u / 0.042, my / 0.048);
    if (rYawn < 1.0) return rYawn > 0.72 ? ink : mouthIn;
  } else if (expression === "deadpan" || expression === "dizzy") {
    if (Math.abs(u) < 0.075 && Math.abs(my) < 0.016) return ink;
  } else if (expression === "slam" || expression === "smirk") {
    const sy = my - u * 0.18 - u * u * 0.45;
    if (u > -0.10 && u < 0.12 && Math.abs(sy) < 0.018) return ink;
  } else {
    const curve = u * u * 1.65;
    if (Math.abs(u) < 0.135 && Math.abs(my - curve + 0.026) < 0.019) {
      return ink;
    }
  }

  return null;
}

function getCastPreset(theme = "theo") {
  if (theme === "noob") {
    return {
      skin: [245, 205, 48],
      top: [13, 105, 172],
      trim: [10, 85, 142],
      accent: [255, 255, 255],
      pants: [164, 189, 71],
      shoes: null,
      sleeves: "none",
      hairStyle: "bald",
      hairColor: null,
      hat: null,
      details: []
    };
  }
  if (theme === "guest") {
    return {
      skin: [242, 243, 243],
      top: [22, 26, 34],
      trim: [15, 18, 24],
      accent: [239, 68, 68],
      pants: [24, 30, 40],
      shoes: [248, 250, 252],
      sleeves: "long",
      hairStyle: "bald",
      hairColor: null,
      hat: "cap_red",
      details: ["triangle", "cuffs"]
    };
  }
  if (theme === "bacon") {
    return {
      skin: [229, 228, 223],
      top: [99, 95, 98],
      trim: [13, 105, 172],
      accent: [255, 255, 255],
      pants: [27, 42, 53],
      shoes: [241, 245, 249],
      sleeves: "long",
      hairStyle: "messy",
      hairColor: [124, 62, 28],
      hat: null,
      details: ["kangaroo", "cuffs"]
    };
  }
  if (theme === "builderman") {
    return {
      skin: [245, 205, 48],
      top: [249, 115, 22],
      trim: [194, 65, 12],
      accent: [255, 255, 255],
      pants: [30, 58, 138],
      shoes: [71, 85, 105],
      sleeves: "long",
      hairStyle: "bald",
      hairColor: null,
      hat: "hardhat_yellow",
      details: ["hood", "kangaroo", "cuffs"]
    };
  }
  if (theme === "obby") {
    return {
      skin: [245, 205, 48],
      top: [0, 162, 232],
      trim: [2, 132, 199],
      accent: [255, 255, 255],
      pants: [30, 41, 59],
      shoes: [248, 250, 252],
      sleeves: "short",
      hairStyle: "bald",
      hairColor: null,
      hat: "cap_red",
      details: ["triangle", "speed_coil"]
    };
  }
  if (theme === "y2k") {
    return {
      skin: [255, 214, 170],
      top: [244, 114, 182],
      trim: [236, 72, 153],
      accent: [255, 255, 255],
      pants: [125, 178, 248],
      shoes: [255, 255, 255],
      sleeves: "long",
      hairStyle: "pigtails",
      hairColor: [68, 36, 24],
      hat: "crown",
      details: ["hood", "kangaroo", "heart"]
    };
  }
  if (theme === "chef") {
    return {
      skin: [252, 208, 162],
      top: [255, 251, 235],
      trim: [217, 119, 6],
      accent: [251, 113, 133],
      pants: [71, 85, 105],
      shoes: [248, 250, 252],
      sleeves: "long",
      hairStyle: "bald",
      hairColor: null,
      hat: "toque_white",
      details: ["kangaroo", "cuffs"]
    };
  }
  if (theme === "base-gray") {
    return {
      skin: [203, 213, 225],
      top: [148, 163, 184],
      trim: [100, 116, 139],
      accent: [226, 232, 240],
      pants: [100, 116, 139],
      shoes: null,
      sleeves: "none",
      hairStyle: "bald",
      hairColor: null,
      hat: null,
      details: []
    };
  }
  if (theme === "police") {
    return {
      skin: [252, 208, 162],
      top: [30, 58, 138],
      trim: [23, 37, 84],
      accent: [250, 204, 21],
      pants: [23, 37, 84],
      shoes: [15, 23, 42],
      sleeves: "long",
      hairStyle: "bald",
      hairColor: null,
      hat: "cap_navy",
      details: ["cuffs", "star_gold"]
    };
  }
  if (theme === "zombie") {
    return {
      skin: [116, 166, 98],
      top: [105, 64, 40],
      trim: [78, 46, 28],
      accent: [132, 204, 22],
      pants: [51, 65, 85],
      shoes: null,
      sleeves: "none",
      hairStyle: "bald",
      hairColor: null,
      hat: null,
      details: []
    };
  }
  if (theme === "clerk") {
    return {
      skin: [252, 208, 162],
      top: [16, 185, 129],
      trim: [5, 150, 105],
      accent: [255, 255, 255],
      pants: [30, 41, 59],
      shoes: [248, 250, 252],
      sleeves: "short",
      hairStyle: "bald",
      hairColor: null,
      hat: "cap_red",
      details: ["triangle", "kangaroo"]
    };
  }
  if (theme === "commuter") {
    return {
      skin: [253, 224, 145],
      top: [244, 142, 178],
      trim: [219, 108, 148],
      accent: [255, 255, 255],
      pants: [241, 245, 249],
      shoes: [56, 189, 248],
      sleeves: "long",
      hairStyle: "messy",
      hairColor: [94, 52, 42],
      hat: null,
      details: ["hood", "kangaroo", "cuffs", "triangle"]
    };
  }
  return {
    skin: [252, 208, 162],
    top: [56, 152, 242],
    trim: [37, 122, 212],
    accent: [255, 255, 255],
    pants: [45, 55, 72],
    shoes: [248, 250, 252],
    sleeves: "long",
    hairStyle: "messy",
    hairColor: [115, 56, 26],
    hat: null,
    details: ["hood", "kangaroo", "cuffs", "moon"]
  };
}

function evalHairSDF(pHead, style, driftMode) {
  if (!style || style === "bald" || driftMode !== "none") return 1e9;
  const dBound = len3(pHead) - 0.42;
  if (dBound > 0.08) return dBound;

  // Full scalp dome that seals the crown & stops cleanly above the eyebrows
  const qCap = { x: pHead.x / 0.252, y: (pHead.y - 0.155) / 0.128, z: (pHead.z - 0.01) / 0.256 };
  let d = (len3(qCap) - 1.0) * 0.16;
  d = Math.max(d, -(pHead.y - 0.115 - pHead.z * 0.14));

  if (style === "messy") {
    const bangs = sdRoundBox(rotX(sub3(pHead, v3(0, 0.218, 0.155)), 0.18), v3(0.205, 0.042, 0.085), 0.032);
    d = Math.min(d, bangs);
    const strands = [
      [v3(-0.14, 0.23, 0.05), v3(-0.15, 0.165, 0.235), 0.066, 0.038],
      [v3(-0.04, 0.24, 0.06), v3(-0.04, 0.158, 0.245), 0.070, 0.040],
      [v3(0.06, 0.24, 0.06), v3(0.07, 0.162, 0.242), 0.068, 0.038],
      [v3(0.15, 0.22, 0.05), v3(0.16, 0.170, 0.228), 0.064, 0.036],
      [v3(-0.07, 0.23, -0.02), v3(-0.12, 0.275, -0.05), 0.065, 0.034],
      [v3(0.06, 0.23, -0.02), v3(0.11, 0.28, -0.04), 0.065, 0.034],
      [v3(-0.215, 0.15, 0.02), v3(-0.238, 0.02, 0.05), 0.054, 0.028],
      [v3(0.215, 0.15, 0.02), v3(0.238, 0.02, 0.05), 0.054, 0.028]
    ];
    for (const [a, b, r1, r2] of strands) {
      d = Math.min(d, sdTaperedCapsule(pHead, a, b, r1, r2));
    }
  } else if (style === "pigtails") {
    const bangs = sdRoundBox(rotX(sub3(pHead, v3(0, 0.218, 0.158)), 0.16), v3(0.20, 0.040, 0.082), 0.030);
    d = Math.min(d, bangs);
    const strands = [
      [v3(-0.235, 0.13, -0.02), v3(-0.36, -0.15, -0.03), 0.082, 0.046],
      [v3(0.235, 0.13, -0.02), v3(0.36, -0.15, -0.03), 0.082, 0.046]
    ];
    for (const [a, b, r1, r2] of strands) {
      d = Math.min(d, sdTaperedCapsule(pHead, a, b, r1, r2));
    }
  }
  return d;
}

function evalHandPropSDF(hit, pArmLocal, propType) {
  if (!propType) return;
  if (propType === "mug") {
    const pm = sub3(pArmLocal, v3(0, -0.46, 0.22));
    hit.add(sdRoundedCylinder(pm, 0.10, 0.018, 0.13), [239, 68, 68], 0.18, 8);
    hit.add(sdRoundedCylinder(sub3(pm, v3(0, 0.115, 0)), 0.082, 0.008, 0.022), [68, 36, 20], 0.35, 8);
    const pHandle = rotY(sub3(pm, v3(0.095, 0, 0)), Math.PI / 2);
    const dHandle = Math.max(
      sdRoundedCylinder(rotX(pHandle, Math.PI / 2), 0.068, 0.012, 0.018),
      -sdRoundedCylinder(rotX(pHandle, Math.PI / 2), 0.040, 0.008, 0.04)
    );
    hit.add(dHandle, [255, 255, 255], 0.22, 8);
  } else if (propType === "cola") {
    const pc = sub3(pArmLocal, v3(0, -0.46, 0.21));
    const dCan = sdRoundedCylinder(pc, 0.092, 0.018, 0.14);
    const col = Math.abs(pc.y) < 0.048 ? [239, 68, 68] : [146, 64, 14];
    hit.add(dCan, col, 0.16, 8);
    hit.add(sdRoundedCylinder(sub3(pc, v3(0, 0.135, 0)), 0.084, 0.008, 0.014), [226, 232, 240], 0.12, 8);
  } else if (propType === "boba") {
    const pb = sub3(pArmLocal, v3(0, -0.46, 0.22));
    hit.add(sdRoundedCylinder(pb, 0.092, 0.015, 0.125), [251, 182, 206], 0.16, 8);
    hit.add(sdSphere(sub3(pb, v3(0, 0.11, 0)), 0.09), [255, 255, 255], 0.14, 8);
    hit.add(sdRoundedCylinder(rotZ(sub3(pb, v3(0.015, 0.19, 0)), -0.18), 0.018, 0.004, 0.085), [56, 189, 248], 0.2, 8);
  } else if (propType === "flashlight") {
    // Extends forward along -Y of arm when armPitch > 0 (+1.15)
    const pf = sub3(pArmLocal, v3(0, -0.60, 0.03));
    hit.add(sdRoundedCylinder(pf, 0.054, 0.012, 0.14), [51, 65, 85], 0.28, 8);
    hit.add(sdRoundedCylinder(sub3(pf, v3(0, -0.14, 0)), 0.082, 0.014, 0.045), [30, 41, 59], 0.22, 8);
    hit.add(sdRoundedCylinder(sub3(pf, v3(0, -0.185, 0)), 0.068, 0.008, 0.012), [254, 240, 138], 0.03, 8);
  } else if (propType === "sword") {
    // Tilted -1.25 around X so +Y of sword points UP-AND-FORWARD when armPitch > 0 (+1.15..+1.35)
    const ps = rotX(sub3(pArmLocal, v3(0, -0.50, 0.05)), -1.25);
    hit.add(sdRoundedCylinder(sub3(ps, v3(0, -0.05, 0)), 0.034, 0.008, 0.09), [29, 78, 216], 0.30, 8);
    hit.add(sdSphere(sub3(ps, v3(0, -0.15, 0)), 0.044), [250, 204, 21], 0.16, 8);
    hit.add(sdRoundBox(sub3(ps, v3(0, 0.05, 0)), v3(0.145, 0.026, 0.038), 0.010), [250, 204, 21], 0.16, 8);
    hit.add(sdRoundBox(sub3(ps, v3(0, 0.40, 0)), v3(0.038, 0.34, 0.015), 0.007), [226, 232, 240], 0.10, 8);
  } else if (propType === "pencil") {
    const pp = rotZ(rotX(sub3(pArmLocal, v3(0, -0.50, 0.20)), 1.15), 0.35);
    hit.add(sdRoundedCylinder(pp, 0.024, 0.005, 0.14), [250, 204, 21], 0.28, 8);
    hit.add(sdRoundedCylinder(sub3(pp, v3(0, -0.15, 0)), 0.025, 0.006, 0.028), [244, 114, 182], 0.32, 8);
    hit.add(sdTaperedCapsule(pp, v3(0, 0.14, 0), v3(0, 0.20, 0), 0.024, 0.005), [30, 41, 59], 0.35, 8);
  } else if (propType === "kettle") {
    const pk = sub3(pArmLocal, v3(0, -0.48, 0.22));
    hit.add(sdRoundedCylinder(pk, 0.115, 0.025, 0.13), [226, 232, 240], 0.14, 8);
    hit.add(sdRoundedCylinder(sub3(pk, v3(0, 0.14, 0)), 0.085, 0.012, 0.022), [30, 41, 59], 0.25, 8);
    hit.add(sdTaperedCapsule(pk, v3(0, 0.02, 0.08), v3(0, 0.14, 0.22), 0.028, 0.016), [203, 213, 225], 0.14, 8);
  } else if (propType === "ramen_cup") {
    const pr = sub3(pArmLocal, v3(0, -0.46, 0.22));
    const dCup = sdRoundedCylinder(pr, 0.105, 0.018, 0.13);
    const col = Math.abs(pr.y) < 0.045 ? [239, 68, 68] : [255, 255, 255];
    hit.add(dCup, col, 0.22, 8);
    hit.add(sdRoundedCylinder(sub3(pr, v3(0, 0.125, 0)), 0.092, 0.008, 0.015), [250, 204, 21], 0.32, 8);
  } else if (propType === "mystery_egg") {
    const pe = sub3(pArmLocal, v3(0, -0.48, 0.24));
    const qEgg = v3(pe.x / 0.14, pe.y / 0.18, pe.z / 0.14);
    const dEgg = (len3(qEgg) - 1.0) * 0.14;
    const isStripe = Math.abs(pe.y) < 0.025 || Math.abs(pe.x) < 0.02;
    hit.add(dEgg, isStripe ? [56, 189, 248] : [248, 250, 252], isStripe ? 0.04 : 0.16, 8);
  } else if (propType === "soda_pack") {
    const ps = sub3(pArmLocal, v3(0, -0.48, 0.22));
    hit.add(sdRoundBox(ps, v3(0.14, 0.09, 0.10), 0.02), [14, 165, 233], 0.18, 8);
    hit.add(sdRoundBox(sub3(ps, v3(0, 0.095, 0)), v3(0.12, 0.018, 0.08), 0.008), [250, 204, 21], 0.20, 8);
  } else if (propType === "price_tag") {
    const pt = sub3(pArmLocal, v3(0, -0.52, 0.18));
    hit.add(sdRoundBox(pt, v3(0.09, 0.055, 0.015), 0.008), [250, 204, 21], 0.18, 8);
    hit.add(sdRoundBox(sub3(pt, v3(0, 0, 0.012)), v3(0.065, 0.016, 0.008), 0.004), [239, 68, 68], 0.20, 8);
  }
}

export function evalAvatarSDF(pWorld, cfg = {}) {
  const {
    pos = v3(0, 0, 0),
    yaw = 0,
    roll = 0,
    bodyPitch = 0,
    waistPitch = 0,
    headYaw = 0,
    headPitch = 0,
    armLPitch = -0.1,
    armRPitch = -0.15,
    legLPitch = 0,
    legRPitch = 0,
    expression = "smile",
    gazeX = 0,
    gazeY = 0,
    brows = "",
    theme = "theo",
    customPalette = null,
    noAccessories = false,
    driftMode = "none",
    hasMug = false,
    handPropL = null,
    handPropR = null,
    backProp = null,
    detachRightArm = false
  } = cfg;

  const basePal = getCastPreset(theme);
  const mergedPal = customPalette ? { ...basePal, ...customPalette } : basePal;
  const pal = noAccessories
    ? {
        ...mergedPal,
        hat: null,
        details: (mergedPal.details || []).filter((d) => d !== "speed_coil")
      }
    : mergedPal;
  const effectiveBackProp = noAccessories ? null : backProp;
  let p = sub3(pWorld, pos);
  if (roll !== 0) {
    p = add3(rotZ(sub3(p, v3(0, -0.82, 0)), -roll), v3(0, -0.82, 0));
  }
  p = rotY(p, -yaw);
  if (bodyPitch !== 0) {
    p = add3(rotX(sub3(p, v3(0, -0.78, 0)), -bodyPitch), v3(0, -0.78, 0));
  }

  const dBound = len3(p) - 2.35;
  if (dBound > 0.22) {
    return { d: dBound, color: [0, 0, 0], roughness: 0.5, id: 0 };
  }

  const hit = new SceneHit();
  const bevel = driftMode === "minecraft-voxel" ? 0.002 : 0.028;

  const pWaist = rotX(sub3(p, v3(0, -0.16, 0)), -waistPitch);
  const pUpper = add3(pWaist, v3(0, -0.16, 0));

  // 1. Torso (2.0 x 2.0 x 1.0 studs)
  const pTorso = sub3(pUpper, v3(0, 0.18, 0));
  const dTorso = sdRoundBox(pTorso, v3(0.34, 0.34, 0.17), bevel);
  if (dTorso < hit.d) {
    let col = pal.top;
    // Original trademark-free upright white geometric TRIANGLE chest badge
    if (pal.details.includes("triangle") && pTorso.z > 0.13) {
      const ty = 0.175 - pTorso.y;
      if (ty >= 0 && ty <= 0.215 && Math.abs(pTorso.x) <= ty * 0.58) {
        col = [248, 250, 252];
      }
    }
    if (pal.details.includes("star_gold") && pTorso.z > 0.13) {
      const sx = pTorso.x + 0.15;
      const sy = pTorso.y - 0.12;
      const ang = Math.atan2(sy, sx);
      const starR = 0.048 + 0.022 * Math.cos(ang * 5);
      if (Math.hypot(sx, sy) < starR) {
        col = [250, 204, 21];
      }
    }
    if (pal.details.includes("heart") && pTorso.z > 0.13) {
      const hx = pTorso.x / 0.095;
      const hy = (pTorso.y - 0.07) / 0.095;
      if (Math.hypot(hx, hy - Math.sqrt(Math.abs(hx)) * 0.55) < 0.85) {
        col = [255, 255, 255];
      }
    }
    if (pal.details.includes("moon") && pTorso.z > 0.13) {
      const d1 = Math.hypot(pTorso.x + 0.16, pTorso.y - 0.12);
      const d2 = Math.hypot(pTorso.x + 0.135, pTorso.y - 0.135);
      if (d1 < 0.068 && d2 > 0.052) {
        col = [253, 224, 71];
      }
    }
    hit.add(dTorso, col, 0.42, 2);
  }

  if (pal.details.includes("hood")) {
    const dHood = sdRoundBox(sub3(pUpper, v3(0, 0.51, -0.06)), v3(0.24, 0.065, 0.14), 0.035);
    hit.add(dHood, pal.trim, 0.45, 2);
    const dStrL = sdRoundedCylinder(sub3(pUpper, v3(-0.065, 0.39, 0.175)), 0.014, 0.005, 0.095);
    const dStrR = sdRoundedCylinder(sub3(pUpper, v3(0.065, 0.39, 0.175)), 0.014, 0.005, 0.095);
    hit.add(Math.min(dStrL, dStrR), pal.accent, 0.35, 3);
  }
  if (pal.details.includes("kangaroo")) {
    const dKanga = sdRoundBox(sub3(pUpper, v3(0, -0.02, 0.165)), v3(0.20, 0.085, 0.022), 0.015);
    hit.add(dKanga, pal.trim, 0.48, 2);
  }

  if (effectiveBackProp === "backpack_purple" || effectiveBackProp === "backpack_cyan") {
    const isCyan = effectiveBackProp === "backpack_cyan";
    const pBag = sub3(pUpper, v3(0, 0.18, -0.26));
    hit.add(sdRoundBox(pBag, v3(0.23, 0.25, 0.11), 0.035), isCyan ? [14, 165, 233] : [168, 85, 247], 0.32, 3);
    hit.add(sdRoundBox(sub3(pBag, v3(0, -0.07, -0.095)), v3(0.16, 0.11, 0.045), 0.022), isCyan ? [56, 189, 248] : [192, 132, 252], 0.28, 3);
    hit.add(sdRoundBox(sub3(pBag, v3(0, 0.26, 0)), v3(0.07, 0.03, 0.025), 0.01), [250, 204, 21], 0.2, 3);
  } else if (effectiveBackProp === "jetpack") {
    const pjL = sub3(pUpper, v3(-0.12, 0.20, -0.25));
    const pjR = sub3(pUpper, v3(0.12, 0.20, -0.25));
    hit.add(Math.min(sdRoundedCylinder(pjL, 0.085, 0.02, 0.22), sdRoundedCylinder(pjR, 0.085, 0.02, 0.22)), [241, 245, 249], 0.22, 3);
    hit.add(Math.min(sdRoundedCylinder(sub3(pjL, v3(0, -0.22, 0)), 0.055, 0.01, 0.03), sdRoundedCylinder(sub3(pjR, v3(0, -0.22, 0)), 0.055, 0.01, 0.03)), [251, 146, 60], 0.08, 3);
  }

  // 2. Neck
  hit.add(sdRoundedCylinder(sub3(pUpper, v3(0, 0.53, 0)), 0.095, 0.015, 0.045), pal.skin, 0.35, 4);

  // 3. Head
  const pHeadLocal = rotY(rotX(sub3(pUpper, v3(0, 0.75, 0)), -headPitch), -headYaw);
  const dHead =
    driftMode === "minecraft-voxel"
      ? sdRoundBox(pHeadLocal, v3(0.24, 0.24, 0.24), 0.002)
      : sdRoundedCylinder(pHeadLocal, 0.222, 0.082, 0.212);

  if (dHead < hit.d) {
    let hCol = pal.skin;
    if (driftMode === "minecraft-voxel") {
      const vx = Math.floor((pHeadLocal.x + 2) * 10);
      const vy = Math.floor((pHeadLocal.y + 2) * 10);
      const vz = Math.floor((pHeadLocal.z + 2) * 10);
      if ((vx + vy + vz) % 2 === 0) {
        hCol = [hCol[0] - 32, hCol[1] - 32, hCol[2] - 24];
      }
    }
    if (pHeadLocal.z > 0.08) {
      const u = pHeadLocal.x / 0.44;
      const v = pHeadLocal.y / 0.42;
      const decal = evalFaceDecal(u, v, expression, { gazeX, gazeY, brows });
      if (decal) hCol = decal;
    }
    hit.add(dHead, hCol, 0.28, 4);
  }

  if (driftMode === "human-fingers") {
    hit.add(sdRoundBox(sub3(pHeadLocal, v3(0, 0.0, 0.25)), v3(0.038, 0.058, 0.075), 0.02), [235, 165, 130], 0.35, 4);
  }
  if (driftMode === "lego-studs") {
    const dStud = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.255, 0)), 0.115, 0.012, 0.065);
    const dShL = sdRoundedCylinder(sub3(pUpper, v3(-0.51, 0.56, 0)), 0.075, 0.01, 0.05);
    const dShR = sdRoundedCylinder(sub3(pUpper, v3(0.51, 0.56, 0)), 0.075, 0.01, 0.05);
    hit.add(Math.min(dStud, dShL, dShR), [250, 204, 21], 0.18, 4);
  }

  if (driftMode === "none") {
    if (pal.hairColor) {
      const dHair = evalHairSDF(pHeadLocal, pal.hairStyle, driftMode);
      hit.add(dHair, pal.hairColor, 0.34, 5);
      if (pal.hairStyle === "pigtails") {
        const dTieL = sdSphere(sub3(pHeadLocal, v3(-0.23, 0.13, -0.01)), 0.048);
        const dTieR = sdSphere(sub3(pHeadLocal, v3(0.23, 0.13, -0.01)), 0.048);
        hit.add(Math.min(dTieL, dTieR), [244, 114, 182], 0.22, 5);
      }
    }
    if (pal.hat === "cap_red") {
      const dDome = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.165, 0)), 0.246, 0.075, 0.105);
      const dBrim = sdRoundBox(rotX(sub3(pHeadLocal, v3(0, 0.105, 0.20)), 0.12), v3(0.185, 0.020, 0.125), 0.012);
      hit.add(Math.min(dDome, dBrim), [225, 38, 38], 0.30, 5);
    } else if (pal.hat === "hardhat_yellow") {
      const dDome = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.17, 0)), 0.252, 0.085, 0.105);
      const dRidge = sdRoundBox(sub3(pHeadLocal, v3(0, 0.265, 0)), v3(0.036, 0.028, 0.22), 0.012);
      const dBrim = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.10, 0.03)), 0.278, 0.015, 0.018);
      hit.add(Math.min(dDome, dRidge, dBrim), [250, 204, 21], 0.20, 5);
    } else if (pal.hat === "crown") {
      const dBase = Math.max(
        sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.235, 0.01)), 0.158, 0.012, 0.035),
        -sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.245, 0.01)), 0.122, 0.008, 0.055)
      );
      let dSpikes = dBase;
      for (let k = 0; k < 5; k++) {
        const a = (k * Math.PI * 2) / 5 + Math.PI / 2;
        const bx = Math.cos(a) * 0.138;
        const bz = Math.sin(a) * 0.138 + 0.01;
        dSpikes = Math.min(dSpikes, sdTaperedCapsule(pHeadLocal, v3(bx, 0.24, bz), v3(bx * 1.06, 0.325, bz * 1.06), 0.034, 0.012));
      }
      hit.add(dSpikes, [250, 204, 21], 0.14, 5);
    } else if (pal.hat === "toque_white") {
      const dBand = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.19, 0)), 0.228, 0.02, 0.058);
      const dPuff = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.31, 0)), 0.268, 0.082, 0.115);
      hit.add(Math.min(dBand, dPuff), [255, 255, 255], 0.28, 5);
    } else if (pal.hat === "cap_navy") {
      const dDome = sdRoundedCylinder(sub3(pHeadLocal, v3(0, 0.168, 0)), 0.248, 0.068, 0.102);
      const dBrim = sdRoundBox(rotX(sub3(pHeadLocal, v3(0, 0.10, 0.20)), 0.14), v3(0.185, 0.020, 0.125), 0.012);
      const dBadge = sdSphere(sub3(pHeadLocal, v3(0, 0.18, 0.238)), 0.032);
      hit.add(dDome, [30, 58, 138], 0.32, 5);
      hit.add(dBrim, [15, 23, 42], 0.20, 5);
      hit.add(dBadge, [250, 204, 21], 0.14, 5);
    }
  }

  // 5. Left & Right Arms
  for (const side of [-1, 1]) {
    if (side === 1 && detachRightArm) continue;
    const pitch = side < 0 ? armLPitch : armRPitch;
    const pShoulder = sub3(pUpper, v3(side * 0.51, 0.38, 0));
    const pArmLocal = rotX(pShoulder, pitch);
    const pArm = sub3(pArmLocal, v3(0, -0.20, 0));

    if (pal.sleeves === "long") {
      hit.add(sdRoundBox(sub3(pArm, v3(0, 0.05, 0)), v3(0.164, 0.28, 0.164), bevel * 0.85), pal.top, 0.42, 6);
      hit.add(sdRoundBox(sub3(pArm, v3(0, -0.21, 0)), v3(0.168, 0.032, 0.168), 0.012), pal.trim, 0.45, 6);
      hit.add(sdRoundBox(sub3(pArm, v3(0, -0.28, 0)), v3(0.158, 0.065, 0.158), bevel * 0.8), pal.skin, 0.32, 7);
    } else if (pal.sleeves === "short") {
      hit.add(sdRoundBox(sub3(pArm, v3(0, 0.22, 0)), v3(0.172, 0.135, 0.172), bevel * 0.85), pal.top, 0.42, 6);
      hit.add(sdRoundBox(sub3(pArm, v3(0, -0.02, 0)), v3(0.162, 0.32, 0.162), bevel * 0.85), pal.skin, 0.32, 6);
    } else {
      hit.add(sdRoundBox(pArm, v3(0.162, 0.34, 0.162), bevel * 0.85), pal.skin, 0.32, 6);
    }

    if (pal.details.includes("speed_coil") && side === 1 && driftMode === "none") {
      for (const cy of [-0.08, -0.20, -0.32]) {
        const pCoil = sub3(pArmLocal, v3(0, cy, 0));
        const dCoil = Math.max(
          sdRoundedCylinder(pCoil, 0.195, 0.018, 0.026),
          -sdRoundedCylinder(pCoil, 0.155, 0.01, 0.05)
        );
        hit.add(dCoil, [255, 45, 65], 0.08, 8);
      }
    }

    const pHandEnd = sub3(pArmLocal, v3(0, -0.56, 0));
    if (driftMode === "human-fingers") {
      let dFingers = sdRoundBox(pHandEnd, v3(0.10, 0.06, 0.055), 0.015);
      for (let f = -2; f <= 2; f++) {
        const pf = sub3(pHandEnd, v3(f * 0.04, -0.11, 0));
        dFingers = Math.min(dFingers, sdRoundBox(pf, v3(0.014, 0.07, 0.015), 0.007));
      }
      hit.add(dFingers, [235, 165, 130], 0.35, 7);
    } else if (driftMode === "lego-studs") {
      hit.add(sdLegoCClaw(sub3(pArmLocal, v3(0, -0.60, 0)), 0.85), [250, 204, 21], 0.18, 7);
    }

    if (driftMode === "none") {
      const activeProp = side < 0 ? handPropL : handPropR || (hasMug ? "mug" : null);
      evalHandPropSDF(hit, pArmLocal, activeProp);
    }
  }

  // 6. Left & Right Legs
  for (const side of [-1, 1]) {
    const pitch = side < 0 ? legLPitch : legRPitch;
    const pHip = sub3(p, v3(side * 0.172, -0.16, 0));
    const pLegLocal = rotX(pHip, pitch);
    const pLeg = sub3(pLegLocal, v3(0, -0.34, 0));
    hit.add(sdRoundBox(pLeg, v3(0.165, 0.34, 0.168), bevel * 0.85), pal.pants, 0.45, 9);

    if (pal.shoes) {
      const pShoe = sub3(pLegLocal, v3(0, -0.63, 0.012));
      hit.add(sdRoundBox(pShoe, v3(0.172, 0.058, 0.182), 0.022), pal.shoes, 0.32, 10);
    }
  }

  return hit;
}

// ---------- Smooth Architectural Floor Shaders (Zero Circular Lego Floor Studs!) ----------
function evalFloorSurface(fp, floorStyle, col1, col2, phase = 0.5) {
  if (floorStyle === "wood_planks") {
    const plankW = 0.26;
    const row = Math.floor(fp.z / plankW);
    const fz = fp.z / plankW - row;
    const stagger = (row & 1) * 0.52;
    const colIdx = Math.floor((fp.x + stagger) / 1.05);
    const fx = (fp.x + stagger) / 1.05 - colIdx;
    const isSeam = fz < 0.045 || fz > 0.955 || fx < 0.022 || fx > 0.978;
    const grain = Math.sin(fp.x * 16 + row * 2.7) * 5;
    const base = (row + colIdx) & 1 ? col1 : col2;
    const mul = isSeam ? 0.76 : 1.0;
    return [clamp((base[0] + grain) * mul, 0, 255), clamp((base[1] + grain * 0.8) * mul, 0, 255), clamp((base[2] + grain * 0.5) * mul, 0, 255)];
  }
  if (floorStyle === "checker_tile") {
    const sz = 0.42;
    const gx = Math.floor(fp.x / sz);
    const gz = Math.floor(fp.z / sz);
    const fx = fp.x / sz - gx;
    const fz = fp.z / sz - gz;
    const isGrout = fx < 0.035 || fx > 0.965 || fz < 0.035 || fz > 0.965;
    const base = (gx + gz) & 1 ? col1 : col2;
    return isGrout ? [base[0] * 0.84, base[1] * 0.84, base[2] * 0.84] : base;
  }
  if (floorStyle === "asphalt_street") {
    if (fp.z < -0.58) {
      const isCurb = fp.z > -0.68;
      if (isCurb) return [203, 213, 225];
      const seam = Math.abs((fp.x / 0.65) - Math.round(fp.x / 0.65)) < 0.025;
      return seam ? [168, 178, 192] : [214, 222, 232];
    }
    if (Math.abs(fp.z - 0.16) < 0.042 && Math.abs(((fp.x + phase * 0.4) % 0.68 + 0.68) % 0.68 - 0.34) < 0.19) {
      return [250, 204, 21];
    }
    if (Math.abs(fp.z + 0.52) < 0.028) return [241, 245, 249];
    const noise = Math.sin(fp.x * 23) * Math.cos(fp.z * 23) * 3;
    return [col1[0] + noise, col1[1] + noise, col1[2] + noise];
  }
  if (floorStyle === "hotel_carpet") {
    const ax = Math.abs(fp.x);
    if (ax > 0.82) {
      const seam = Math.abs((fp.x / 0.22) - Math.round(fp.x / 0.22)) < 0.05;
      return seam ? [68, 36, 18] : [96, 52, 26];
    }
    if (ax > 0.73) return [234, 179, 8];
    const pat = Math.abs(Math.sin(fp.x * 9) * Math.sin(fp.z * 9)) > 0.55;
    return pat ? [153, 27, 27] : [127, 29, 29];
  }
  if (floorStyle === "molten_lava") {
    const w = Math.sin(fp.x * 3.8 + phase * 6.28) + Math.cos(fp.z * 3.4 - phase * 6.28);
    if (w > 0.65) return [254, 240, 138];
    if (w > -0.25) return [249, 115, 22];
    return [220, 38, 38];
  }
  if (floorStyle === "grass_lawn") {
    const patch = Math.sin(fp.x * 2.6) * Math.cos(fp.z * 2.4) > 0;
    return patch ? col1 : col2;
  }
  if (floorStyle === "runway_gloss") {
    const ax = Math.abs(fp.x);
    if (ax > 0.88 && ax < 0.98) return [244, 114, 182];
    if (ax >= 0.98) return [30, 27, 75];
    const panel = Math.floor(fp.z / 0.65) & 1;
    return panel ? col1 : col2;
  }
  if (floorStyle === "sand_court") {
    if (fp.z > 0.44 && fp.z < 0.64) {
      const cx = Math.floor(fp.x / 0.16);
      const cz = Math.floor((fp.z - 0.44) / 0.10);
      return (cx + cz) & 1 ? [248, 250, 252] : [225, 29, 72];
    }
    if (Math.abs(Math.abs(fp.x) - 1.15) < 0.03) return [254, 249, 195];
    const ripple = Math.sin(fp.x * 5 + fp.z * 7) * 4;
    return [col1[0] + ripple, col1[1] + ripple, col1[2] + ripple];
  }
  const cellSize = floorStyle === "plaza_pavers" ? 0.48 : 0.34;
  const gx = Math.floor(fp.x / cellSize);
  const gz = Math.floor(fp.z / cellSize);
  const fx = fp.x / cellSize - gx - 0.5;
  const fz = fp.z / cellSize - gz - 0.5;
  const base = (gx + gz) & 1 ? col1 : col2;
  const isSeam = Math.abs(fx) > 0.468 || Math.abs(fz) > 0.468;
  return isSeam ? [base[0] * 0.88, base[1] * 0.88, base[2] * 0.88] : base;
}

export function render3DViewport(width, height, sceneFn, camCfg = {}) {
  const buf = new Uint8Array(width * height * 4);
  const ro = camCfg.ro || v3(0, 0.32, 3.15);
  const ta = camCfg.ta || v3(0, 0.08, 0);
  const fov = camCfg.fov || 1.9;
  const bgTop = camCfg.bgTop || [125, 198, 252];
  const bgBot = camCfg.bgBot || [224, 242, 254];
  const floorY = camCfg.floorY === undefined ? -0.86 : camCfg.floorY;
  const floorStyle = camCfg.floorStyle || "studio_grid";
  const floorPhase = camCfg.phase ?? 0.5;
  const floorColor1 = camCfg.floorColor1 || [154, 168, 188];
  const floorColor2 = camCfg.floorColor2 || [142, 156, 178];

  const fw = norm3(sub3(ta, ro));
  const rt = norm3(cross3(fw, v3(0, 1, 0)));
  const up = cross3(rt, fw);

  const keyLight = norm3(v3(0.58, 0.82, 0.68));
  const fillLight = norm3(v3(-0.65, 0.35, 0.55));
  const rimLight = norm3(v3(-0.55, 0.55, -0.75));

  const calcNormal = (p, centerDist) => {
    const e = 0.0025;
    const d0 = centerDist ?? sceneFn(p).d;
    const dx = sceneFn(v3(p.x + e, p.y, p.z)).d - d0;
    const dy = sceneFn(v3(p.x, p.y + e, p.z)).d - d0;
    const dz = sceneFn(v3(p.x, p.y, p.z + e)).d - d0;
    return norm3(v3(dx, dy, dz));
  };

  const calcSoftShadow = (orig, dir) => {
    const h1 = sceneFn(add3(orig, mul3(dir, 0.12))).d;
    const h2 = sceneFn(add3(orig, mul3(dir, 0.28))).d;
    return clamp(0.56 + 0.44 * Math.min(h1 * 8.0, h2 * 4.5), 0.56, 1.0);
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

      const ocx = ro.x;
      const ocy = ro.y - 0.05;
      const ocz = ro.z;
      const bSphere = ocx * rd.x + ocy * rd.y + ocz * rd.z;
      const cSphere = ocx * ocx + ocy * ocy + ocz * ocz - 4.4 * 4.4;
      const disc = bSphere * bSphere - cSphere;

      let t = disc > 0 ? Math.max(0.2, -bSphere - Math.sqrt(disc)) : 99.0;
      let tMax = disc > 0 ? Math.min(9.5, -bSphere + Math.sqrt(disc)) : 0.0;
      let tf = -1;
      if (floorY !== null && rd.y < -0.001) {
        tf = (floorY - ro.y) / rd.y;
        if (tf > 0 && tf < tMax) {
          tMax = tf + 0.01;
        }
      }

      let hit = null;
      const maxSteps = camCfg.maxSteps || 34;
      if (disc > 0 && tMax > 0.2) {
        for (let step = 0; step < maxSteps; step++) {
          if (t > tMax) break;
          const pos = add3(ro, mul3(rd, t));
          const res = sceneFn(pos);
          if (res.d < 0.0045) {
            hit = { pos, res, t };
            break;
          }
          t += res.d;
        }
      }

      if (hit && (tf <= 0 || hit.t <= tf)) {
        const rough = hit.res.roughness ?? 0.32;
        if (rough <= 0.06) {
          const base = hit.res.color;
          r = clamp(base[0] * 1.06 + 18, 0, 255);
          g = clamp(base[1] * 1.06 + 18, 0, 255);
          b = clamp(base[2] * 1.06 + 18, 0, 255);
        } else if (hit.res.id === 19 || hit.res.id === 38 || hit.res.id === 44 || hit.res.id === 63 || hit.res.id === 89 || hit.res.id === 114 || hit.res.id === 121) {
          // Flat architectural backdrop walls: fast analytical +Z normal lighting (skips 4 extra SDF evaluations per pixel!)
          const sh = calcSoftShadow(v3(hit.pos.x, hit.pos.y, hit.pos.z + 0.03), keyLight);
          const wallLit = 0.52 + 0.44 * sh;
          const base = hit.res.color;
          r = clamp(base[0] * wallLit, 0, 255);
          g = clamp(base[1] * wallLit, 0, 255);
          b = clamp(base[2] * wallLit, 0, 255);
        } else {
          const N = calcNormal(hit.pos, hit.res.d);
          const V = mul3(rd, -1);
          const sh = dot3(N, keyLight) > 0 ? calcSoftShadow(add3(hit.pos, mul3(N, 0.015)), keyLight) : 0.56;
          const keyDiff = Math.max(0, dot3(N, keyLight)) * sh;
          const fillDiff = Math.max(0, dot3(N, fillLight)) * 0.28;
          const skyAmb = 0.38 + 0.14 * (0.5 + 0.5 * N.y);
          const aoSample = sceneFn(add3(hit.pos, mul3(N, 0.065))).d / 0.065;
          const ao = clamp(0.68 + 0.32 * aoSample, 0.62, 1.0);

          const lighting = (skyAmb + keyDiff * 0.62 + fillDiff) * ao;

          const H = norm3(add3(keyLight, V));
          const specPow = rough < 0.25 ? 36 : 18;
          const specStrength = (rough < 0.25 ? 0.36 : 0.15) * sh;
          const spec = Math.pow(Math.max(0, dot3(N, H)), specPow) * specStrength;

          const fresnel = Math.pow(1 - Math.max(0, dot3(N, V)), 3.0);
          const rim = fresnel * Math.max(0, dot3(N, rimLight)) * 0.26;

          const base = hit.res.color;
          r = clamp(base[0] * lighting + 255 * spec + 245 * rim, 0, 255);
          g = clamp(base[1] * lighting + 252 * spec + 248 * rim, 0, 255);
          b = clamp(base[2] * lighting + 245 * spec + 255 * rim, 0, 255);
        }
      } else if (tf > 0 && tf < 14.0 && floorY !== null) {
        const fp = add3(ro, mul3(rd, tf));
        const tileCol = evalFloorSurface(fp, floorStyle, floorColor1, floorColor2, floorPhase);
        const floorShadow =
          floorStyle === "molten_lava"
            ? 1.0
            : Math.abs(fp.x) < 1.8 && Math.abs(fp.z) < 1.6
            ? calcSoftShadow(v3(fp.x, floorY + 0.02, fp.z), keyLight)
            : 1.0;
        const fade = Math.exp(-0.052 * tf * tf);
        r = mix(r, clamp(tileCol[0] * floorShadow, 0, 255), fade);
        g = mix(g, clamp(tileCol[1] * floorShadow, 0, 255), fade);
        b = mix(b, clamp(tileCol[2] * floorShadow, 0, 255), fade);
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

// ---------- Multi-Part Architectural & Prop Helpers (100% Lipschitz-Continuous SDF Bounds!) ----------
function addBedroomBackdrop(hit, p) {
  if (p.z - (-0.75) > hit.d) return;
  const dWall = sdRoundBox(sub3(p, v3(0, 0.35, -1.05)), v3(2.8, 1.55, 0.06), 0.01);
  if (dWall < hit.d) {
    const wCol = p.y < -0.22 ? [241, 245, 249] : [219, 234, 254];
    hit.add(dWall, wCol, 0.48, 19);
  }
  const pw = sub3(p, v3(-0.78, 0.56, -0.97));
  if (len3(pw) - 0.62 <= hit.d) {
    hit.add(sdRoundBox(pw, v3(0.38, 0.38, 0.03), 0.015), [255, 255, 255], 0.30, 19);
    const dGlass = sdRoundBox(sub3(pw, v3(0, 0, 0.014)), v3(0.32, 0.32, 0.022), 0.008);
    if (dGlass < hit.d) {
      const isMullion = Math.abs(pw.x) < 0.026 || Math.abs(pw.y) < 0.026;
      hit.add(dGlass, isMullion ? [255, 255, 255] : [125, 211, 252], isMullion ? 0.30 : 0.05, 19);
    }
  }
  const ps = sub3(p, v3(0.76, 0.62, -0.90));
  if (len3(ps) - 0.52 <= hit.d) {
    hit.add(sdRoundBox(ps, v3(0.34, 0.028, 0.11), 0.01), [180, 124, 78], 0.38, 19);
    hit.add(sdRoundBox(sub3(ps, v3(-0.16, 0.11, 0)), v3(0.038, 0.085, 0.08), 0.008), [239, 68, 68], 0.32, 19);
    hit.add(sdRoundBox(sub3(ps, v3(-0.07, 0.12, 0)), v3(0.038, 0.095, 0.08), 0.008), [59, 130, 246], 0.32, 19);
    hit.add(sdRoundBox(sub3(ps, v3(0.02, 0.10, 0)), v3(0.038, 0.075, 0.08), 0.008), [16, 185, 129], 0.32, 19);
  }
}

function addDetailedDesk(hit, p, deskY = -0.40) {
  const pd = sub3(p, v3(0, deskY, 0.42));
  if (len3(pd) - 1.65 > hit.d) return;
  hit.add(sdRoundBox(pd, v3(1.32, 0.052, 0.56), 0.02), [176, 120, 74], 0.38, 20);
  hit.add(sdRoundBox(sub3(pd, v3(0, -0.09, -0.02)), v3(1.22, 0.055, 0.48), 0.015), [146, 96, 56], 0.42, 20);
  const lx = Math.abs(pd.x) - 1.14;
  const lz = Math.abs(pd.z) - 0.42;
  hit.add(sdRoundBox(v3(lx, pd.y + 0.26, lz), v3(0.055, 0.24, 0.055), 0.012), [226, 232, 240], 0.30, 20);
  hit.add(sdRoundBox(sub3(pd, v3(0.72, -0.09, 0.47)), v3(0.14, 0.02, 0.02), 0.008), [250, 204, 21], 0.18, 20);
  const pm = sub3(pd, v3(0.86, 0.14, -0.06));
  if (len3(pm) - 0.22 <= hit.d) {
    hit.add(sdRoundedCylinder(pm, 0.085, 0.015, 0.095), [239, 68, 68], 0.18, 20);
    hit.add(sdRoundedCylinder(sub3(pm, v3(0, 0.085, 0)), 0.068, 0.006, 0.015), [68, 36, 20], 0.35, 20);
  }
}

function addTwinBellAlarmClock(hit, p, center, squash = 1.0, tilt = 0.0) {
  const q0 = sub3(p, center);
  if (len3(q0) - 0.38 > hit.d) return;
  const q = rotZ(q0, tilt);
  const qs = v3(q.x, q.y / squash, q.z);
  const qCyl = rotX(qs, Math.PI / 2);
  hit.add(sdRoundedCylinder(qCyl, 0.175, 0.026, 0.072), [225, 29, 72], 0.22, 21);
  // Note: rotX(qs, PI/2) maps +Z (toward camera) to -Y in cylinder coords!
  const dDial = sdRoundedCylinder(add3(qCyl, v3(0, 0.018, 0)), 0.138, 0.008, 0.068);
  if (dDial < hit.d) {
    let dCol = [255, 255, 255];
    if (qs.z > 0.05) {
      const r = Math.hypot(qs.x, qs.y);
      const handMin = Math.abs(qs.x) < 0.015 && qs.y > -0.01 && qs.y < 0.105;
      const handHr = Math.abs(qs.x * 0.65 - qs.y * 0.76) < 0.016 && qs.x < 0.01 && qs.y < 0.01 && r < 0.084;
      const ticks = r > 0.106 && r < 0.126 && (Math.abs(qs.x) < 0.015 || Math.abs(qs.y) < 0.015);
      if (handMin || handHr || r < 0.022 || ticks) dCol = [15, 23, 42];
    }
    hit.add(dDial, dCol, 0.18, 22);
  }
  const dBellL = sdSphere(sub3(q, v3(-0.125, 0.195 * squash, 0)), 0.058);
  const dBellR = sdSphere(sub3(q, v3(0.125, 0.195 * squash, 0)), 0.058);
  hit.add(Math.min(dBellL, dBellR), [250, 204, 21], 0.12, 23);
  hit.add(sdRoundedCylinder(sub3(q, v3(0, 0.205 * squash, 0)), 0.016, 0.005, 0.045), [226, 232, 240], 0.16, 23);
  const dFootL = sdRoundedCylinder(rotZ(sub3(q, v3(-0.10, -0.175 * squash, 0)), 0.45), 0.022, 0.006, 0.042);
  const dFootR = sdRoundedCylinder(rotZ(sub3(q, v3(0.10, -0.175 * squash, 0)), -0.45), 0.022, 0.006, 0.042);
  hit.add(Math.min(dFootL, dFootR), [226, 232, 240], 0.20, 23);
}

function addOpenLaptop(hit, p, baseCenter) {
  const q = sub3(p, baseCenter);
  if (len3(q) - 0.62 > hit.d) return;
  const dBase = sdRoundBox(q, v3(0.35, 0.020, 0.24), 0.012);
  if (dBase < hit.d) {
    let bCol = [226, 232, 240];
    if (q.y > 0.012 && Math.abs(q.x) < 0.28 && q.z > -0.16 && q.z < 0.08) {
      const kx = Math.abs(((q.x + 1) * 18) % 1 - 0.5);
      const kz = Math.abs(((q.z + 1) * 18) % 1 - 0.5);
      if (kx < 0.38 && kz < 0.38) bCol = [30, 41, 59];
    }
    hit.add(dBase, bCol, 0.22, 24);
  }
  const pScr = rotX(sub3(q, v3(0, 0.22, 0.22)), -0.22);
  const dLid = sdRoundBox(pScr, v3(0.35, 0.22, 0.016), 0.012);
  if (dLid < hit.d) {
    let sCol = [51, 65, 85];
    if (pScr.z < -0.008 && Math.abs(pScr.x) < 0.31 && Math.abs(pScr.y) < 0.18) {
      sCol = [224, 242, 254];
      if (Math.abs(pScr.x) < 0.24 && (Math.abs(pScr.y - 0.08) < 0.026 || Math.abs(pScr.y) < 0.026 || Math.abs(pScr.y + 0.08) < 0.026)) {
        sCol = [244, 63, 94];
      }
    }
    hit.add(dLid, sCol, pScr.z < -0.008 ? 0.06 : 0.25, 25);
  }
}

export function buildAlarmMeltdownScene(shotIndex, phase = 0.5) {
  const bedroomBgTop = [147, 197, 253];
  const bedroomBgBot = [241, 245, 249];
  const woodFloor1 = [198, 146, 96];
  const woodFloor2 = [182, 130, 82];

  if (shotIndex === 0) {
    const shake = Math.sin(phase * Math.PI * 8) * 0.05;
    const popY = mix(-0.16, 0.04, smoothstep(0, 0.65, phase));
    return {
      cam: {
        ro: v3(0.12 + shake * 0.25, 0.54, 2.52 - phase * 0.16),
        ta: v3(0, 0.30, 0.12),
        fov: 1.9,
        bgTop: bedroomBgTop,
        bgBot: bedroomBgBot,
        floorY: -0.86,
        floorStyle: "wood_planks",
        floorColor1: woodFloor1,
        floorColor2: woodFloor2
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        hit.merge(
          evalAvatarSDF(p, {
            pos: v3(0.18, popY, -0.10),
            yaw: -0.16,
            armLPitch: -0.85,
            armRPitch: -0.85,
            expression: "shocked",
            theme: "theo"
          })
        );
        addBedroomBackdrop(hit, p);
        addDetailedDesk(hit, p, -0.38);
        addTwinBellAlarmClock(hit, p, v3(-0.34, -0.13 + Math.abs(shake) * 1.1, 0.48), 1.0, shake * 2.0);
        return hit;
      }
    };
  }

  if (shotIndex === 1) {
    const slamT = smoothstep(0.1, 0.65, phase);
    const armAngle = mix(-2.0, -0.82, slamT);
    const squash = mix(1.0, 0.45, slamT);
    return {
      cam: {
        ro: v3(0.88, 0.46, 2.62),
        ta: v3(-0.02, 0.16, 0.15),
        fov: 1.9,
        bgTop: bedroomBgTop,
        bgBot: bedroomBgBot,
        floorY: -0.86,
        floorStyle: "wood_planks",
        floorColor1: woodFloor1,
        floorColor2: woodFloor2
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        hit.merge(
          evalAvatarSDF(p, {
            pos: v3(0.24, 0.0, -0.02),
            yaw: -0.38,
            waistPitch: slamT * 0.18,
            armRPitch: armAngle,
            armLPitch: -0.25,
            expression: "slam",
            theme: "theo"
          })
        );
        addBedroomBackdrop(hit, p);
        addDetailedDesk(hit, p, -0.42);
        addTwinBellAlarmClock(hit, p, v3(-0.24, -0.24, 0.46), squash, 0);
        return hit;
      }
    };
  }

  if (shotIndex === 2) {
    return {
      cam: {
        ro: v3(Math.sin(phase * 0.6 - 0.3) * 0.38, 0.52, 2.52),
        ta: v3(0, 0.24, 0.12),
        fov: 1.9,
        bgTop: bedroomBgTop,
        bgBot: bedroomBgBot,
        floorY: -0.86,
        floorStyle: "wood_planks",
        floorColor1: woodFloor1,
        floorColor2: woodFloor2
      },
      sceneFn: (p) => {
        const hit = new SceneHit();
        hit.merge(
          evalAvatarSDF(p, {
            pos: v3(0, -0.02, -0.10),
            yaw: 0,
            headPitch: Math.sin(phase * Math.PI * 4) * 0.04,
            armLPitch: -0.78,
            armRPitch: -0.78,
            expression: "tears",
            theme: "theo"
          })
        );
        addBedroomBackdrop(hit, p);
        addDetailedDesk(hit, p, -0.42);
        addOpenLaptop(hit, p, v3(-0.04, -0.34, 0.38));
        return hit;
      }
    };
  }

  const dropT = smoothstep(0.05, 0.55, phase);
  const bounce = phase > 0.55 ? Math.abs(Math.sin((phase - 0.55) * Math.PI * 5)) * 0.1 * (1 - phase) : 0;
  const pitch90 = mix(0.1, 1.22, dropT) - bounce;
  return {
    cam: {
      ro: v3(0.95, 1.08, 2.62),
      ta: v3(0, 0.06, 0.18),
      fov: 1.9,
      bgTop: bedroomBgTop,
      bgBot: bedroomBgBot,
      floorY: -0.86,
      floorStyle: "wood_planks",
      floorColor1: woodFloor1,
      floorColor2: woodFloor2
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(0, -0.02, -0.12),
          yaw: 0,
          waistPitch: pitch90,
          armLPitch: -0.38,
          armRPitch: -0.38,
          expression: "dizzy",
          theme: "theo"
        })
      );
      addBedroomBackdrop(hit, p);
      addDetailedDesk(hit, p, -0.42);
      addOpenLaptop(hit, p, v3(-0.04, -0.34, 0.42));
      return hit;
    }
  };
}

export function buildObbySkyScene(shotIndex, phase = 0.5) {
  const jumpArc = Math.sin(phase * Math.PI) * 0.42;
  const runSwing = Math.sin(phase * Math.PI * 2) * 0.68;
  return {
    cam: {
      ro: v3(shotIndex === 1 ? 1.25 : -0.55, 0.56 + shotIndex * 0.05, 2.95),
      ta: v3(0, 0.04, 0),
      fov: 1.88,
      bgTop: [38, 166, 242],
      bgBot: [219, 240, 255],
      floorY: null
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(mix(-0.36, 0.36, phase), jumpArc, 0),
          yaw: 0.48,
          armLPitch: runSwing,
          armRPitch: -runSwing,
          legLPitch: -runSwing,
          legRPitch: runSwing,
          expression: shotIndex === 2 ? "shocked" : "grin",
          theme: "obby",
          backProp: "jetpack"
        })
      );
      const p1 = sub3(p, v3(-0.56, -0.84, 0));
      hit.add(sdRoundBox(p1, v3(0.50, 0.075, 0.50), 0.025), [244, 114, 182], 0.22, 30);
      hit.add(sdRoundBox(sub3(p1, v3(0, -0.08, 0)), v3(0.46, 0.045, 0.46), 0.018), [248, 250, 252], 0.28, 30);

      const p2 = sub3(p, v3(0.56, -0.68, 0));
      const c2 = shotIndex === 3 ? [51, 65, 85] : [52, 211, 153];
      hit.add(sdRoundBox(p2, v3(0.52, 0.075, 0.52), 0.025), c2, 0.22, 31);
      hit.add(sdRoundBox(sub3(p2, v3(0, -0.08, 0)), v3(0.48, 0.045, 0.48), 0.018), [248, 250, 252], 0.28, 31);

      if (shotIndex >= 2) {
        const pr = sub3(p2, v3(0, 0.08, 0));
        const dRing = Math.max(sdRoundedCylinder(pr, 0.30, 0.01, 0.014), -sdRoundedCylinder(pr, 0.21, 0.008, 0.03));
        hit.add(dRing, [56, 189, 248], 0.05, 31);
        const pole = sub3(p2, v3(0.36, 0.52, -0.32));
        hit.add(sdRoundedCylinder(pole, 0.024, 0.005, 0.46), [226, 232, 240], 0.2, 31);
        hit.add(sdSphere(sub3(pole, v3(0, 0.48, 0)), 0.045), [250, 204, 21], 0.14, 31);
        const waveZ = Math.sin(phase * Math.PI * 4 + p.x * 6) * 0.03;
        hit.add(sdRoundBox(sub3(pole, v3(0.16, 0.32, waveZ)), v3(0.15, 0.10, 0.016), 0.008), [34, 197, 94], 0.25, 31);
      }

      if (shotIndex === 2) {
        hit.add(sdRoundBox(sub3(p, v3(0.06, -0.54, 0)), v3(0.075, 0.042, 0.48), 0.014), [255, 42, 62], 0.04, 32);
      }

      if (Math.min(p.z - (-0.75), p.y - (-1.10)) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(-1.25, -0.35, -1.25)), v3(0.36, 0.06, 0.36), 0.02), [250, 204, 21], 0.25, 33);
        hit.add(sdRoundBox(sub3(p, v3(1.30, 0.05, -1.35)), v3(0.36, 0.06, 0.36), 0.02), [168, 85, 247], 0.25, 33);
        const pc1 = sub3(p, v3(-0.75, -1.35, -0.65));
        hit.add(Math.min(sdRoundBox(pc1, v3(0.45, 0.12, 0.28), 0.08), sdRoundBox(sub3(pc1, v3(0.12, 0.10, 0)), v3(0.26, 0.11, 0.22), 0.07)), [255, 255, 255], 0.45, 34);
        const pc2 = sub3(p, v3(0.85, -1.42, -0.85));
        hit.add(sdRoundBox(pc2, v3(0.48, 0.12, 0.28), 0.08), [255, 255, 255], 0.45, 34);
      }
      return hit;
    }
  };
}

export function buildDuoComedyScene(shotIndex, phase = 0.5) {
  const spinY = shotIndex === 1 ? phase * Math.PI * 2 : 0.24;
  const leftX = shotIndex === 1 ? -0.48 : -0.64;
  const rightX = shotIndex === 1 ? 0.52 : 0.64;
  return {
    cam: {
      ro: v3(0, 0.30, 3.48),
      ta: v3(0, 0.06, 0),
      fov: 1.9,
      bgTop: [165, 180, 252],
      bgBot: [238, 242, 255],
      floorY: -0.86,
      floorStyle: "plaza_pavers",
      floorColor1: [226, 232, 240],
      floorColor2: [208, 218, 232]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(leftX, 0, 0.05),
          yaw: spinY,
          armLPitch: -0.32,
          armRPitch: -0.68,
          expression: shotIndex === 2 ? "shocked" : shotIndex === 3 ? "deadpan" : "smirk",
          theme: "y2k",
          handPropR: "boba",
          backProp: "backpack_purple"
        })
      );
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(rightX, 0, 0),
          yaw: -0.22,
          roll: shotIndex === 2 ? -0.24 : shotIndex === 3 ? -0.16 : 0,
          headYaw: shotIndex === 3 ? 0.20 : 0,
          armLPitch: 0,
          armRPitch: 0,
          legLPitch: 0,
          legRPitch: 0,
          expression: shotIndex === 3 ? "deadpan" : "smile",
          theme: "noob"
        })
      );
      if (p.z - (-0.60) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(0, 0.35, -1.18)), v3(2.8, 1.5, 0.06), 0.01), [254, 249, 242], 0.45, 38);
        const pAwning = rotX(sub3(p, v3(-0.35, 0.98, -0.96)), 0.38);
        const dAwn = sdRoundBox(pAwning, v3(0.95, 0.05, 0.24), 0.02);
        if (dAwn < hit.d) {
          const stripe = Math.floor((p.x + 2) / 0.18) & 1;
          hit.add(dAwn, stripe ? [244, 114, 182] : [255, 255, 255], 0.32, 38);
        }
        hit.add(sdRoundBox(sub3(p, v3(-0.35, 0.18, -1.10)), v3(0.62, 0.62, 0.03), 0.02), [186, 230, 253], 0.14, 38);
        const pt = sub3(p, v3(1.28, -0.64, -0.88));
        if (len3(pt) - 0.65 <= hit.d) {
          hit.add(sdRoundedCylinder(pt, 0.16, 0.02, 0.18), [194, 106, 62], 0.42, 39);
          hit.add(sdSphere(sub3(pt, v3(0, 0.34, 0)), 0.24), [74, 222, 128], 0.38, 39);
        }
      }
      return hit;
    }
  };
}

export function buildCozyCafeScene(shotIndex, phase = 0.5) {
  const popY = shotIndex === 0 ? mix(-0.15, 0.02, smoothstep(0, 0.65, phase)) : 0.0;
  const armWave = shotIndex === 3 ? -0.95 - Math.sin(phase * Math.PI * 4) * 0.25 : -0.72;
  return {
    cam: {
      ro: v3(shotIndex === 1 ? 0.52 : -0.32, 0.54, 2.65),
      ta: v3(0, 0.18, 0.15),
      fov: 1.9,
      bgTop: [254, 243, 199],
      bgBot: [255, 251, 235],
      floorY: -0.86,
      floorStyle: "wood_planks",
      floorColor1: [214, 178, 138],
      floorColor2: [196, 158, 118]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(0, popY, -0.12),
          yaw: shotIndex === 1 ? -0.22 : 0.12,
          armLPitch: -0.55,
          armRPitch: armWave,
          expression: shotIndex === 3 ? "grin" : "smile",
          theme: "chef"
        })
      );
      if (p.z - (-0.48) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(0, 0.35, -1.02)), v3(2.8, 1.5, 0.06), 0.01), [254, 243, 199], 0.48, 44);
        const pm = sub3(p, v3(0.68, 0.62, -0.93));
        hit.add(sdRoundBox(pm, v3(0.42, 0.28, 0.025), 0.012), [146, 96, 56], 0.38, 44);
        hit.add(sdRoundBox(sub3(pm, v3(0, 0, 0.015)), v3(0.36, 0.22, 0.015), 0.008), [30, 41, 59], 0.42, 44);
        for (const lx of [-0.68, 0.68]) {
          hit.add(sdRoundedCylinder(sub3(p, v3(lx, 1.18, -0.62)), 0.012, 0.003, 0.24), [71, 85, 105], 0.3, 44);
          hit.add(sdRoundedCylinder(sub3(p, v3(lx, 0.96, -0.62)), 0.12, 0.03, 0.055), [251, 191, 36], 0.05, 44);
        }
      }
      hit.add(sdRoundBox(sub3(p, v3(0, -0.56, 0.44)), v3(1.32, 0.26, 0.42), 0.022), [180, 124, 82], 0.38, 40);
      hit.add(sdRoundBox(sub3(p, v3(0, -0.30, 0.44)), v3(1.36, 0.035, 0.45), 0.015), [255, 251, 235], 0.22, 40);

      const pe = sub3(p, v3(-0.76, -0.09, 0.42));
      if (len3(pe) - 0.42 <= hit.d) {
        hit.add(sdRoundBox(pe, v3(0.20, 0.18, 0.18), 0.025), [110, 231, 183], 0.20, 45);
        hit.add(sdRoundBox(sub3(pe, v3(0, 0.06, 0.16)), v3(0.15, 0.05, 0.04), 0.01), [226, 232, 240], 0.12, 45);
        hit.add(sdRoundedCylinder(rotX(sub3(pe, v3(0, -0.02, 0.24)), Math.PI / 2), 0.022, 0.006, 0.08), [30, 41, 59], 0.25, 45);
      }

      const pdc = sub3(p, v3(0.76, -0.14, 0.44));
      if (len3(pdc) - 0.40 <= hit.d) {
        hit.add(sdRoundBox(pdc, v3(0.24, 0.13, 0.18), 0.018), [224, 242, 254], 0.10, 45);
        hit.add(sdRoundedCylinder(sub3(pdc, v3(0, -0.03, 0)), 0.11, 0.018, 0.055), [244, 114, 182], 0.25, 45);
      }

      hit.add(sdRoundBox(sub3(p, v3(-0.08, -0.25, 0.44)), v3(0.32, 0.018, 0.22), 0.01), [251, 207, 232], 0.22, 41);
      const pc = rotY(sub3(p, v3(-0.14, -0.19, 0.44)), 0.35);
      if (len3(pc) - 0.24 <= hit.d) {
        const dCr = Math.min(
          sdRoundBox(pc, v3(0.085, 0.048, 0.062), 0.028),
          Math.min(
            sdRoundBox(rotY(sub3(pc, v3(-0.09, -0.005, 0.035)), 0.45), v3(0.065, 0.038, 0.048), 0.022),
            sdRoundBox(rotY(sub3(pc, v3(0.09, -0.005, 0.035)), -0.45), v3(0.065, 0.038, 0.048), 0.022)
          )
        );
        hit.add(dCr, [245, 158, 11], 0.24, 42);
      }

      const cupX = shotIndex === 2 ? mix(0.10, 0.32, phase) : 0.14;
      const pl = sub3(p, v3(cupX, -0.15, 0.46));
      if (len3(pl) - 0.20 <= hit.d) {
        const dCup = sdRoundedCylinder(pl, 0.072, 0.012, 0.092);
        const cCol = Math.abs(pl.y) < 0.038 ? [180, 124, 78] : [255, 255, 255];
        hit.add(dCup, cCol, 0.20, 42);
        hit.add(sdRoundedCylinder(sub3(pl, v3(0, 0.088, 0)), 0.064, 0.006, 0.012), [245, 222, 179], 0.30, 42);
      }

      if (shotIndex === 3) {
        for (const cx of [-0.36, 0.0, 0.36]) {
          const pc2 = rotY(sub3(p, v3(cx, 1.05 + Math.sin(phase * 6 + cx) * 0.06, 0.12)), phase * 3.14);
          const dCoin = sdRoundedCylinder(rotX(pc2, Math.PI / 2), 0.095, 0.015, 0.026);
          hit.add(dCoin, [250, 204, 21], 0.10, 43);
        }
      }
      return hit;
    }
  };
}

export function buildRunwayDropScene(shotIndex, phase = 0.5) {
  const isTransformed = shotIndex >= 2;
  const jumpY = shotIndex === 1 ? Math.sin(phase * Math.PI) * 0.45 : 0.0;
  return {
    cam: {
      ro: v3(shotIndex === 3 ? 0.58 : 0, shotIndex === 2 ? 0.10 : 0.28, 2.95),
      ta: v3(0, 0.14, 0),
      fov: 1.9,
      bgTop: isTransformed ? [126, 34, 206] : [148, 163, 184],
      bgBot: isTransformed ? [244, 114, 182] : [226, 232, 240],
      floorY: -0.86,
      floorStyle: "runway_gloss",
      floorColor1: isTransformed ? [232, 196, 255] : [186, 198, 214],
      floorColor2: isTransformed ? [216, 172, 252] : [168, 182, 200]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(0, jumpY, 0.05),
          yaw: shotIndex === 1 ? phase * Math.PI * 2 : shotIndex === 3 ? 0.32 : 0,
          headPitch: shotIndex === 0 ? 0.16 : 0,
          armLPitch: isTransformed ? -0.45 : 0,
          armRPitch: isTransformed ? -0.82 : 0,
          expression: shotIndex === 0 ? "deadpan" : shotIndex === 1 ? "shocked" : "smirk",
          theme: isTransformed ? "y2k" : "base-gray",
          handPropR: isTransformed ? "boba" : null
        })
      );
      hit.add(sdRoundedCylinder(sub3(p, v3(0, -0.80, 0.05)), 0.78, 0.025, 0.055), [30, 41, 59], 0.22, 50);
      hit.add(sdRoundedCylinder(sub3(p, v3(0, -0.74, 0.05)), 0.68, 0.022, 0.038), isTransformed ? [244, 114, 182] : [226, 232, 240], isTransformed ? 0.08 : 0.22, 50);

      if (p.z - (-0.82) <= hit.d) {
        const pa = sub3(p, v3(0, 0.25, -1.05));
        const dArch = Math.max(
          sdRoundedCylinder(rotX(pa, Math.PI / 2), 1.18, 0.03, 0.05),
          -sdRoundedCylinder(rotX(pa, Math.PI / 2), 1.02, 0.02, 0.09),
          -(pa.y + 0.85)
        );
        hit.add(dArch, isTransformed ? [56, 189, 248] : [203, 213, 225], isTransformed ? 0.04 : 0.28, 51);
        const psb = sub3(p, v3(0, 1.22, -0.92));
        if (len3(psb) - 0.68 <= hit.d) {
          hit.add(sdRoundBox(psb, v3(0.58, 0.11, 0.035), 0.02), [30, 27, 75], 0.25, 52);
          for (let i = -2; i <= 2; i++) {
            const dStar = sdSphere(sub3(psb, v3(i * 0.20, 0, 0.035)), 0.055);
            hit.add(dStar, isTransformed ? [250, 204, 21] : [100, 116, 139], isTransformed ? 0.04 : 0.35, 52);
          }
        }
      }
      return hit;
    }
  };
}

export function buildBurntPizzaScene(shotIndex, phase = 0.5) {
  const fallRoll = shotIndex === 3 ? smoothstep(0, 0.65, phase) * 1.38 : 0;
  return {
    cam: {
      ro: v3(shotIndex === 3 ? -0.28 : 0, shotIndex === 1 ? 0.45 : shotIndex === 3 ? 0.56 : 0.36, shotIndex === 1 ? 2.25 : shotIndex === 3 ? 3.45 : 2.88),
      ta: v3(shotIndex === 3 ? -0.25 : 0, shotIndex === 3 ? -0.18 : 0.16, 0.1),
      fov: 1.9,
      bgTop: shotIndex === 1 ? [51, 65, 85] : [186, 230, 253],
      bgBot: shotIndex === 1 ? [100, 116, 139] : [241, 245, 249],
      floorY: -0.86,
      floorStyle: "checker_tile",
      floorColor1: [241, 245, 249],
      floorColor2: [148, 163, 184]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      const detachArm = shotIndex === 2;
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(shotIndex === 3 ? 0.62 : 0, 0, -0.06),
          yaw: 0,
          roll: fallRoll,
          armLPitch: -0.85,
          armRPitch: -0.85,
          expression: "smile",
          theme: "chef",
          detachRightArm: detachArm
        })
      );
      if (p.z - (-0.62) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(0, 0.35, -1.08)), v3(2.8, 1.5, 0.06), 0.01), shotIndex === 1 ? [71, 85, 105] : [226, 232, 240], 0.42, 63);
        const po = sub3(p, v3(-0.78, 0.05, -0.88));
        if (len3(po) - 1.12 <= hit.d) {
          hit.add(sdRoundBox(po, v3(0.46, 0.58, 0.20), 0.025), [180, 83, 52], 0.48, 63);
          hit.add(sdRoundedCylinder(sub3(po, v3(0, 0.78, -0.02)), 0.11, 0.015, 0.25), [100, 116, 139], 0.35, 63);
          hit.add(sdRoundBox(sub3(po, v3(0, 0.02, 0.16)), v3(0.28, 0.20, 0.08), 0.03), [24, 24, 27], 0.5, 63);
          hit.add(sdRoundBox(sub3(po, v3(0, -0.08, 0.17)), v3(0.20, 0.06, 0.06), 0.02), [251, 146, 60], 0.04, 63);
        }
      }

      hit.add(sdRoundBox(sub3(p, v3(0, -0.58, 0.48)), v3(1.18, 0.26, 0.42), 0.02), [203, 213, 225], 0.34, 60);
      hit.add(sdRoundBox(sub3(p, v3(0, -0.34, 0.48)), v3(1.22, 0.035, 0.45), 0.015), [248, 250, 252], 0.22, 60);
      hit.add(sdRoundBox(sub3(p, v3(-0.72, -0.28, 0.46)), v3(0.24, 0.028, 0.24), 0.008), [217, 164, 108], 0.45, 60);

      const pp = sub3(p, v3(-0.04, -0.28, 0.46));
      hit.add(sdRoundedCylinder(pp, 0.28, 0.014, 0.018), [148, 163, 184], 0.16, 61);
      hit.add(sdRoundedCylinder(sub3(pp, v3(0, 0.028, 0)), 0.235, 0.024, 0.028), [38, 32, 28], 0.62, 62);
      hit.add(sdRoundedCylinder(sub3(pp, v3(0, 0.036, 0)), 0.185, 0.012, 0.024), [20, 18, 16], 0.68, 62);
      for (const [tx, tz] of [[-0.08, -0.05], [0.07, -0.06], [0.02, 0.08], [-0.06, 0.07]]) {
        hit.add(sdRoundedCylinder(sub3(pp, v3(tx, 0.054, tz)), 0.038, 0.006, 0.010), [68, 28, 24], 0.55, 62);
      }
      if (shotIndex !== 1) {
        for (let k = 0; k < 3; k++) {
          const sy = 0.18 + ((phase * 0.45 + k * 0.22) % 0.65);
          const sx = Math.sin(phase * 5 + k * 2) * 0.05;
          hit.add(sdRoundBox(sub3(pp, v3(sx, sy, 0)), v3(0.045, 0.045, 0.045), 0.018), [148, 163, 184], 0.52, 62);
        }
      }
      if (detachArm) {
        const pa = rotY(rotZ(sub3(p, v3(0.54, -0.20, 0.48)), 1.48), 0.35);
        hit.add(sdRoundBox(pa, v3(0.155, 0.26, 0.155), 0.022), [255, 251, 235], 0.40, 6);
        hit.add(sdRoundBox(sub3(pa, v3(0, -0.28, 0)), v3(0.15, 0.065, 0.15), 0.02), [252, 208, 162], 0.32, 7);
      }
      return hit;
    }
  };
}

export function buildTornadoTowerScene(shotIndex, phase = 0.5) {
  const sway = shotIndex === 3 ? 0 : Math.sin(phase * Math.PI * 4) * 0.07;
  const hopY = shotIndex === 2 ? Math.sin(phase * Math.PI) * 0.38 : 0;
  return {
    cam: {
      ro: v3(shotIndex === 1 ? 0.62 : -0.32, 0.48, 3.12),
      ta: v3(0, 0.08, 0),
      fov: 1.88,
      bgTop: shotIndex === 3 ? [56, 189, 248] : [51, 65, 85],
      bgBot: shotIndex === 3 ? [224, 242, 254] : [148, 163, 184],
      floorY: -1.32,
      floorStyle: "grass_lawn",
      floorColor1: [74, 222, 128],
      floorColor2: [34, 197, 94]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(sway, hopY + 0.05, 0),
          yaw: shotIndex === 0 ? -0.35 : 0.15,
          armLPitch: shotIndex === 3 ? -2.4 : -0.65,
          armRPitch: shotIndex === 0 ? -1.45 : -0.85,
          legLPitch: shotIndex === 2 ? -0.45 : 0,
          legRPitch: shotIndex === 2 ? 0.45 : 0,
          expression: shotIndex === 3 ? "grin" : shotIndex === 2 ? "tears" : "shocked",
          theme: "guest"
        })
      );
      const tx = sway * 0.5;
      const deckW = shotIndex >= 2 ? 0.42 : 0.72;
      hit.add(sdRoundBox(sub3(p, v3(tx, -0.74, 0)), v3(deckW, 0.08, 0.62), 0.022), [34, 197, 94], 0.32, 70);
      for (const sx of [-1, 1]) {
        for (const sz of [-1, 1]) {
          hit.add(sdRoundBox(sub3(p, v3(tx + sx * (deckW - 0.08), -1.06, sz * 0.48)), v3(0.065, 0.32, 0.065), 0.012), [146, 96, 56], 0.42, 70);
        }
      }
      if (shotIndex < 2) {
        hit.add(sdRoundBox(sub3(p, v3(tx, -0.44, 0.54)), v3(0.66, 0.042, 0.042), 0.012), [250, 204, 21], 0.24, 71);
        hit.add(sdRoundBox(sub3(p, v3(tx - 0.58, -0.55, 0.54)), v3(0.04, 0.14, 0.04), 0.01), [250, 204, 21], 0.24, 71);
        hit.add(sdRoundBox(sub3(p, v3(tx + 0.58, -0.55, 0.54)), v3(0.04, 0.14, 0.04), 0.01), [250, 204, 21], 0.24, 71);
      }
      if (shotIndex < 3 && p.z - (-0.42) <= hit.d) {
        for (let i = 0; i < 6; i++) {
          const ry = -0.75 + i * 0.38;
          const rad = 0.16 + i * 0.085;
          const ox = -0.98 + Math.sin(phase * Math.PI * 4 + i * 1.1) * 0.11;
          hit.add(sdRoundedCylinder(sub3(p, v3(ox, ry, -1.18)), rad, 0.055, 0.14), i & 1 ? [51, 65, 85] : [71, 85, 105], 0.55, 72);
        }
        const ang = phase * Math.PI * 4;
        const deb1 = rotZ(sub3(p, v3(-0.95 + Math.cos(ang) * 0.55, 0.45, -0.95 + Math.sin(ang) * 0.35)), ang);
        hit.add(sdRoundBox(deb1, v3(0.18, 0.04, 0.08), 0.01), [250, 204, 21], 0.3, 72);
        const deb2 = rotX(sub3(p, v3(-0.55, 0.85, -0.85)), -ang);
        hit.add(sdRoundBox(deb2, v3(0.16, 0.04, 0.12), 0.01), [34, 197, 94], 0.3, 72);
      }
      const pt = sub3(p, v3(1.22, -0.95, -0.92));
      if (len3(pt) - 0.65 <= hit.d) {
        hit.add(sdRoundedCylinder(sub3(pt, v3(0, -0.18, 0)), 0.075, 0.01, 0.20), [120, 72, 42], 0.45, 73);
        hit.add(sdTaperedCapsule(pt, v3(0, -0.02, 0), v3(0, 0.42, 0), 0.28, 0.04), [22, 163, 74], 0.4, 73);
      }
      return hit;
    }
  };
}

export function buildPoliceChaseScene(shotIndex, phase = 0.5) {
  const runSwing = Math.sin(phase * Math.PI * 4) * 0.76;
  const tripPitch = shotIndex === 2 ? smoothstep(0.1, 0.7, phase) * 1.15 : shotIndex === 3 ? 1.45 : 0;
  const sirenFlash = Math.sin(phase * Math.PI * 6) > 0;
  return {
    cam: {
      ro: v3(shotIndex === 1 ? 0.18 : 0, 0.36, 3.52),
      ta: v3(0, 0.04, 0),
      fov: 1.88,
      bgTop: sirenFlash && shotIndex < 3 ? [96, 165, 250] : [147, 197, 253],
      bgBot: [226, 232, 240],
      floorY: -0.86,
      floorStyle: "asphalt_street",
      phase,
      floorColor1: [64, 76, 94],
      floorColor2: [51, 65, 85]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(0.62, shotIndex === 3 ? -0.35 : 0, 0.14),
          yaw: shotIndex === 3 ? 0 : 0.45,
          waistPitch: tripPitch,
          armLPitch: shotIndex >= 2 ? -0.5 : runSwing,
          armRPitch: -0.95,
          legLPitch: shotIndex >= 2 ? 0 : -runSwing,
          legRPitch: shotIndex >= 2 ? 0 : runSwing,
          expression: shotIndex === 0 ? "smirk" : shotIndex === 3 ? "deadpan" : "shocked",
          theme: "noob"
        })
      );
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(-0.66, 0, -0.04),
          yaw: 0.38,
          armLPitch: shotIndex === 3 ? 0 : -runSwing,
          armRPitch: shotIndex === 3 ? -0.4 : runSwing,
          legLPitch: shotIndex === 3 ? 0 : runSwing,
          legRPitch: shotIndex === 3 ? 0 : -runSwing,
          expression: "angry",
          theme: "police"
        })
      );

      const pc = sub3(p, v3(-1.05, -0.52, -0.92));
      if (len3(pc) - 0.82 <= hit.d) {
        hit.add(sdRoundBox(pc, v3(0.56, 0.18, 0.28), 0.03), [15, 23, 42], 0.22, 82);
        hit.add(sdRoundBox(sub3(pc, v3(-0.04, 0.24, 0)), v3(0.32, 0.14, 0.25), 0.028), [248, 250, 252], 0.22, 82);
        hit.add(sdRoundBox(sub3(pc, v3(0.14, 0.23, 0)), v3(0.16, 0.10, 0.255), 0.015), [125, 211, 252], 0.10, 82);
        hit.add(sdRoundBox(sub3(pc, v3(-0.06, 0.40, 0.08)), v3(0.06, 0.035, 0.06), 0.01), [239, 68, 68], sirenFlash ? 0.03 : 0.3, 82);
        hit.add(sdRoundBox(sub3(pc, v3(-0.06, 0.40, -0.08)), v3(0.06, 0.035, 0.06), 0.01), [59, 130, 246], !sirenFlash ? 0.03 : 0.3, 82);
        for (const wx of [-0.34, 0.34]) {
          const pw = rotX(sub3(pc, v3(wx, -0.18, 0.26)), Math.PI / 2);
          hit.add(sdRoundedCylinder(pw, 0.13, 0.02, 0.05), [15, 23, 42], 0.45, 82);
        }
      }
      const ph = sub3(p, v3(1.15, 0.02, -1.25));
      if (len3(ph) - 1.05 <= hit.d) {
        hit.add(sdRoundBox(ph, v3(0.58, 0.52, 0.28), 0.02), [254, 243, 199], 0.45, 83);
        hit.add(sdRoundBox(sub3(ph, v3(0, 0.62, 0)), v3(0.64, 0.14, 0.32), 0.03), [239, 68, 68], 0.38, 83);
        hit.add(sdRoundBox(sub3(ph, v3(-0.18, 0.08, 0.27)), v3(0.16, 0.16, 0.02), 0.01), [125, 211, 252], 0.12, 83);
      }

      if (shotIndex < 3) {
        const cashY = shotIndex === 2 ? 0.58 + phase * 0.32 : 0.06;
        const pb = sub3(p, v3(0.84, cashY, 0.38));
        if (len3(pb) - 0.30 <= hit.d) {
          hit.add(sdRoundBox(pb, v3(0.145, 0.13, 0.12), 0.045), [34, 197, 94], 0.28, 80);
          hit.add(sdRoundBox(sub3(pb, v3(0, 0, 0.105)), v3(0.08, 0.04, 0.025), 0.008), [254, 240, 138], 0.22, 80);
          hit.add(sdRoundedCylinder(sub3(pb, v3(0, 0.15, 0)), 0.055, 0.012, 0.035), [22, 163, 74], 0.32, 80);
        }
      }
      if (shotIndex >= 2) {
        const phy = sub3(p, v3(0.98, -0.62, 0.28));
        if (len3(phy) - 0.38 <= hit.d) {
          hit.add(sdRoundedCylinder(phy, 0.105, 0.02, 0.21), [239, 68, 68], 0.22, 81);
          hit.add(sdSphere(sub3(phy, v3(0, 0.21, 0)), 0.098), [250, 204, 21], 0.18, 81);
          hit.add(sdRoundedCylinder(rotZ(sub3(phy, v3(0, 0.06, 0)), Math.PI / 2), 0.042, 0.008, 0.155), [250, 204, 21], 0.18, 81);
        }
      }
      if (shotIndex === 3 && Math.abs(p.z - 0.80) - 0.08 <= hit.d) {
        for (const bx of [-0.9, -0.45, 0.0, 0.45, 0.9]) {
          hit.add(sdRoundedCylinder(sub3(p, v3(bx, 0.15, 0.80)), 0.028, 0.005, 1.15), [100, 116, 139], 0.18, 84);
        }
        hit.add(sdRoundBox(sub3(p, v3(0, 0.72, 0.80)), v3(1.15, 0.032, 0.035), 0.008), [71, 85, 105], 0.2, 84);
      }
      return hit;
    }
  };
}

export function buildDoorsHallwayScene(shotIndex, phase = 0.5) {
  const flickerDark = shotIndex === 1 && Math.sin(phase * Math.PI * 6) < 0;
  const isDark = flickerDark || shotIndex >= 2;
  return {
    cam: {
      ro: v3(0.12, 0.34, 2.88),
      ta: v3(0, 0.12, 0),
      fov: 1.9,
      bgTop: isDark ? [15, 23, 42] : [58, 40, 32],
      bgBot: isDark ? [30, 41, 59] : [98, 68, 52],
      floorY: -0.86,
      floorStyle: "hotel_carpet",
      floorColor1: [120, 53, 15],
      floorColor2: [96, 42, 12]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(shotIndex === 3 ? 0.56 : -0.22, 0, 0.12),
          yaw: shotIndex === 3 ? 2.65 : -0.18,
          headYaw: shotIndex === 2 ? -0.68 : 0,
          armLPitch: -0.15,
          armRPitch: shotIndex === 3 ? 0.45 : 1.18,
          expression: shotIndex >= 1 ? "shocked" : "deadpan",
          theme: "theo",
          handPropR: shotIndex < 3 ? "flashlight" : null
        })
      );
      if (p.z - (-0.45) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(0, 0.32, -0.92)), v3(2.8, 1.5, 0.06), 0.01), isDark ? [38, 28, 26] : [78, 52, 38], 0.48, 89);
        const pd = sub3(p, v3(-0.22, 0.06, -0.78));
        if (len3(pd) - 1.12 <= hit.d) {
          hit.add(sdRoundBox(pd, v3(0.48, 0.92, 0.065), 0.018), [92, 52, 28], 0.42, 90);
          hit.add(sdRoundBox(sub3(pd, v3(0, 0, 0.025)), v3(0.40, 0.84, 0.055), 0.015), [128, 76, 44], 0.42, 90);
          hit.add(sdRoundBox(sub3(pd, v3(0, 0.62, 0.075)), v3(0.14, 0.065, 0.018), 0.01), [250, 204, 21], 0.14, 91);
          hit.add(sdSphere(sub3(pd, v3(0.30, -0.04, 0.095)), 0.046), [250, 204, 21], 0.14, 91);
        }
        const pw = sub3(p, v3(0.76, 0.08, -0.68));
        if (len3(pw) - 1.12 <= hit.d) {
          const dCloset = sdRoundBox(pw, v3(0.42, 0.94, 0.18), 0.02);
          const louver = Math.sin(pw.y * 28) > 0.35 && Math.abs(pw.x) < 0.34 && Math.abs(pw.y) < 0.72;
          hit.add(dCloset, louver ? [68, 38, 22] : [110, 66, 38], 0.44, 90);
        }
        const ps = sub3(p, v3(-0.92, 0.68, -0.82));
        hit.add(sdRoundedCylinder(ps, 0.075, 0.015, 0.09), isDark ? [71, 85, 105] : [254, 240, 138], isDark ? 0.35 : 0.04, 91);
      }
      if (shotIndex === 2) {
        const pe = sub3(p, v3(0.36, 0.56, -0.45));
        hit.add(sdSphere(pe, 0.28), [15, 23, 42], 0.65, 93);
        const dEyeL = sdSphere(sub3(pe, v3(-0.085, 0.04, 0.25)), 0.045);
        const dEyeR = sdSphere(sub3(pe, v3(0.085, 0.04, 0.25)), 0.045);
        hit.add(Math.min(dEyeL, dEyeR), [255, 255, 255], 0.02, 93);
      }
      return hit;
    }
  };
}

export function buildSwordDuelScene(shotIndex, phase = 0.5) {
  const jumpY = shotIndex === 1 ? Math.sin(phase * Math.PI) * 0.36 : 0;
  const slashPitch = shotIndex === 1 ? 1.28 + Math.sin(phase * Math.PI * 2) * 0.28 : shotIndex === 3 ? 0.95 : 1.15;
  const leftX = shotIndex === 1 ? -0.52 : -0.68;
  const rightX = shotIndex === 1 ? 0.52 : shotIndex === 2 ? 0.80 : 0.68;
  return {
    cam: {
      ro: v3(0, 0.34, 3.62),
      ta: v3(0, 0.08, 0),
      fov: 1.88,
      bgTop: [249, 115, 22],
      bgBot: [254, 215, 170],
      floorY: -1.04,
      floorStyle: "molten_lava",
      phase,
      floorColor1: [239, 68, 68],
      floorColor2: [249, 115, 22]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(leftX, jumpY, 0),
          yaw: 0.72,
          armRPitch: slashPitch,
          expression: shotIndex === 3 ? "smile" : shotIndex === 1 ? "angry" : "smirk",
          theme: "builderman",
          handPropR: shotIndex === 3 ? "cola" : "sword"
        })
      );
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(rightX, jumpY, 0),
          yaw: -0.72,
          roll: shotIndex === 2 ? -0.18 : 0,
          armLPitch: slashPitch,
          expression: shotIndex === 2 ? "shocked" : shotIndex === 3 ? "smile" : "grin",
          theme: "noob",
          handPropL: shotIndex === 3 ? "cola" : "sword"
        })
      );
      hit.add(sdRoundBox(sub3(p, v3(0, -0.82, 0)), v3(1.32, 0.12, 0.54), 0.022), [148, 163, 184], 0.36, 100);
      hit.add(sdRoundBox(sub3(p, v3(0, -0.70, -0.48)), v3(1.32, 0.05, 0.05), 0.012), [100, 116, 139], 0.38, 100);
      for (const side of [-1, 1]) {
        const pt = sub3(p, v3(side * 1.38, -0.22, -0.62));
        if (len3(pt) - 0.95 <= hit.d) {
          hit.add(sdRoundBox(pt, v3(0.28, 0.68, 0.28), 0.02), [100, 116, 139], 0.42, 100);
          hit.add(sdRoundBox(sub3(pt, v3(-0.14, 0.74, 0.14)), v3(0.08, 0.08, 0.08), 0.01), [148, 163, 184], 0.4, 100);
          hit.add(sdRoundBox(sub3(pt, v3(0.14, 0.74, 0.14)), v3(0.08, 0.08, 0.08), 0.01), [148, 163, 184], 0.4, 100);
        }
      }
      if (shotIndex === 1) {
        const ps = sub3(p, v3(0, 0.46 + jumpY, 0.22));
        const dSpark = Math.min(
          sdRoundBox(rotZ(ps, 0.78), v3(0.16, 0.028, 0.028), 0.01),
          sdRoundBox(rotZ(ps, -0.78), v3(0.16, 0.028, 0.028), 0.01)
        );
        hit.add(dSpark, [254, 240, 138], 0.02, 102);
      }
      return hit;
    }
  };
}

export function buildExamPanicScene(shotIndex, phase = 0.5) {
  const scribble = shotIndex === 2 ? Math.sin(phase * Math.PI * 8) * 0.24 : 0;
  const slumpPitch = shotIndex === 3 ? -0.34 : 0.08;
  return {
    cam: {
      ro: v3(shotIndex === 2 ? 0.58 : 0, 0.50, 2.65),
      ta: v3(0, 0.18, 0.12),
      fov: 1.9,
      bgTop: [219, 234, 254],
      bgBot: [254, 249, 195],
      floorY: -0.86,
      floorStyle: "checker_tile",
      floorColor1: [226, 232, 240],
      floorColor2: [208, 216, 228]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(0, -0.02, -0.08),
          yaw: scribble * 0.3,
          waistPitch: slumpPitch,
          armLPitch: shotIndex === 1 ? -2.2 : shotIndex === 3 ? 0 : -0.85,
          armRPitch: shotIndex === 1 ? -2.2 : shotIndex === 3 ? 0 : -0.85 + scribble,
          expression: shotIndex === 0 ? "smile" : shotIndex === 1 ? "shocked" : shotIndex === 2 ? "angry" : "dizzy",
          theme: "bacon",
          handPropR: shotIndex === 2 ? "pencil" : null
        })
      );
      if (p.z - (-0.75) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(0, 0.35, -0.96)), v3(2.8, 1.5, 0.06), 0.01), [254, 249, 232], 0.48, 114);
        const pcb = sub3(p, v3(-0.28, 0.52, -0.88));
        if (len3(pcb) - 0.98 <= hit.d) {
          hit.add(sdRoundBox(pcb, v3(0.84, 0.42, 0.028), 0.012), [146, 96, 56], 0.4, 114);
          const dSlate = sdRoundBox(sub3(pcb, v3(0, 0, 0.016)), v3(0.78, 0.36, 0.018), 0.008);
          if (dSlate < hit.d) {
            const chalkLine = Math.abs(pcb.x + 0.25) < 0.36 && (Math.abs(pcb.y - 0.12) < 0.012 || Math.abs(pcb.y - 0.02) < 0.012);
            hit.add(dSlate, chalkLine ? [241, 245, 249] : [20, 83, 45], 0.45, 114);
          }
        }
        const pck = sub3(p, v3(0.82, 0.78, -0.86));
        if (len3(pck) - 0.26 <= hit.d) {
          const qc = rotX(pck, Math.PI / 2);
          hit.add(sdRoundedCylinder(qc, 0.17, 0.015, 0.028), [225, 29, 72], 0.22, 112);
          const dDial = sdRoundedCylinder(add3(qc, v3(0, 0.014, 0)), 0.135, 0.008, 0.026);
          if (dDial < hit.d) {
            const hand = (Math.abs(pck.x) < 0.012 && pck.y > -0.01 && pck.y < 0.095) || (Math.abs(pck.y) < 0.012 && pck.x > -0.01 && pck.x < 0.075);
            hit.add(dDial, hand ? [15, 23, 42] : [255, 255, 255], 0.18, 113);
          }
        }
      }

      addDetailedDesk(hit, p, -0.40);
      const pbk = sub3(p, v3(-0.74, -0.29, 0.36));
      if (len3(pbk) - 0.34 <= hit.d) {
        hit.add(sdRoundBox(pbk, v3(0.18, 0.038, 0.22), 0.01), [37, 99, 235], 0.32, 115);
        hit.add(sdRoundBox(sub3(pbk, v3(0.02, 0.075, -0.01)), v3(0.17, 0.035, 0.21), 0.01), [225, 29, 72], 0.32, 115);
      }
      const pp = sub3(p, v3(0, -0.335, 0.42));
      const dPaper = sdRoundBox(pp, v3(0.28, 0.009, 0.32), 0.004);
      if (dPaper < hit.d) {
        let pCol = [255, 255, 255];
        if (pp.y > 0.004 && Math.abs(pp.x) < 0.22) {
          if (pp.z < -0.20 && pp.z > -0.25 && pp.x > 0.08) pCol = [239, 68, 68];
          else if (Math.abs(((pp.z + 1) * 18) % 1 - 0.5) < 0.16 && Math.abs(pp.z) < 0.20) pCol = [100, 116, 139];
        }
        hit.add(dPaper, pCol, 0.26, 111);
      }
      if (shotIndex !== 2) {
        const pPen = rotY(rotZ(sub3(p, v3(0.36, -0.32, 0.42)), Math.PI / 2), 0.25);
        hit.add(sdRoundedCylinder(pPen, 0.018, 0.004, 0.14), [250, 204, 21], 0.28, 115);
      }
      if (shotIndex === 1) {
        hit.add(sdRoundBox(rotZ(sub3(p, v3(-0.62, 0.72, 0.12)), 0.2), v3(0.085, 0.085, 0.085), 0.02), [250, 204, 21], 0.12, 116);
        hit.add(sdRoundBox(rotZ(sub3(p, v3(0.62, 0.76, 0.12)), -0.2), v3(0.085, 0.085, 0.085), 0.02), [250, 204, 21], 0.12, 116);
      }
      return hit;
    }
  };
}

export function buildRedLightScene(shotIndex, phase = 0.5) {
  const isRed = shotIndex === 1 || shotIndex === 2;
  const stride = isRed ? 0.64 : Math.sin(phase * Math.PI * 4) * 0.62;
  const wobble = shotIndex === 2 ? Math.sin(phase * Math.PI * 6) * 0.08 : 0;
  return {
    cam: {
      ro: v3(0, 0.36, 3.92),
      ta: v3(0, 0.06, 0),
      fov: 1.88,
      bgTop: isRed ? [244, 63, 94] : [52, 211, 153],
      bgBot: [254, 243, 199],
      floorY: -0.86,
      floorStyle: "sand_court",
      floorColor1: [234, 198, 138],
      floorColor2: [218, 180, 118]
    },
    sceneFn: (p) => {
      const hit = new SceneHit();
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(-0.78, isRed ? 0.14 : 0, 0.05),
          yaw: 0.12,
          waistPitch: shotIndex === 3 ? 0.42 : 0,
          armLPitch: -stride,
          armRPitch: stride,
          legLPitch: stride,
          legRPitch: -stride * 0.5,
          expression: isRed ? "shocked" : "grin",
          theme: "obby"
        })
      );
      hit.merge(
        evalAvatarSDF(p, {
          pos: v3(0.78, isRed ? 0.12 : 0, 0.05),
          yaw: -0.12,
          roll: wobble,
          waistPitch: shotIndex === 3 ? 0.42 : 0,
          armLPitch: stride,
          armRPitch: -stride,
          legLPitch: -stride * 0.5,
          legRPitch: stride,
          expression: isRed ? "shocked" : "grin",
          theme: "noob"
        })
      );
      if (p.z - (-0.75) <= hit.d) {
        hit.add(sdRoundBox(sub3(p, v3(0, 0.25, -1.32)), v3(2.8, 1.5, 0.06), 0.01), isRed ? [254, 205, 211] : [186, 230, 253], 0.48, 121);
        const psig = sub3(p, v3(0, 0.35, -0.95));
        if (len3(psig) - 1.25 <= hit.d) {
          hit.add(sdRoundedCylinder(sub3(psig, v3(0, -0.45, 0)), 0.042, 0.008, 0.78), [51, 65, 85], 0.3, 122);
          hit.add(sdRoundBox(sub3(psig, v3(0, 0.42, 0)), v3(0.16, 0.26, 0.11), 0.025), [15, 23, 42], 0.25, 122);
          hit.add(sdSphere(sub3(psig, v3(0, 0.53, 0.095)), 0.075), isRed ? [255, 42, 62] : [71, 24, 32], isRed ? 0.02 : 0.45, 122);
          hit.add(sdSphere(sub3(psig, v3(0, 0.31, 0.095)), 0.075), !isRed ? [34, 238, 128] : [20, 64, 42], !isRed ? 0.02 : 0.45, 122);
        }
      }
      return hit;
    }
  };
}

export function renderRawPanelSet(tmpDir, force = false, shardIdx = 0, shardCount = 1, onlyPrefixes = null, shotsOnly = false) {
  fs.mkdirSync(tmpDir, { recursive: true });
  let taskCounter = 0;
  const writePng = (name, w, h, computeFn) => {
    if (shotsOnly && !/_shot_[0-3]\.png$/.test(name)) return;
    if (onlyPrefixes && !onlyPrefixes.some((p) => name.startsWith(p + "_"))) return;
    const myTask = taskCounter++;
    if (myTask % shardCount !== shardIdx) return;
    const outPath = path.join(tmpDir, name);
    if (!force && fs.existsSync(outPath) && fs.statSync(outPath).size > 1000) return;
    const buf = computeFn();
    fs.writeFileSync(outPath, encodePNG(w, h, buf));
  };

  const studioCam = {
    ro: v3(0, 0.22, 2.75),
    ta: v3(0, 0.04, 0),
    fov: 1.95,
    bgTop: [219, 234, 254],
    bgBot: [241, 245, 249],
    floorY: -0.86,
    floorStyle: "studio_grid",
    floorColor1: [182, 194, 210],
    floorColor2: [168, 182, 198]
  };

  const turnAngles = [
    ["turn_front.png", 0.0, true],
    ["turn_3q.png", 0.68, true],
    ["turn_side.png", 1.52, true]
  ];
  for (const [fname, yaw, mug] of turnAngles) {
    writePng(fname, 420, 520, () =>
      render3DViewport(
        420,
        520,
        (p) => evalAvatarSDF(p, { yaw, hasMug: mug, theme: "theo", expression: "smile" }),
        studioCam
      )
    );
  }

  const driftModes = [
    ["drift_1_fingers.png", "human-fingers", "shocked"],
    ["drift_2_lego.png", "lego-studs", "deadpan"],
    ["drift_3_voxel.png", "minecraft-voxel", "deadpan"],
    ["drift_4_locked.png", "none", "smile"]
  ];
  for (const [fname, dMode, expr] of driftModes) {
    writePng(fname, 320, 420, () =>
      render3DViewport(
        320,
        420,
        (p) =>
          evalAvatarSDF(p, {
            yaw: 0.36,
            headPitch: dMode === "lego-studs" ? 0.14 : 0,
            armLPitch: -0.48,
            armRPitch: -0.58,
            driftMode: dMode,
            expression: expr,
            theme: "theo"
          }),
        { ...studioCam, ro: v3(0, 0.26, 2.68), ta: v3(0, 0.08, 0) }
      )
    );
  }

  const classicAvatars = [
    ["avatar_noob.png", "noob", "smile", false],
    ["avatar_guest.png", "guest", "grin", false],
    ["avatar_bacon.png", "bacon", "smile", false],
    ["avatar_builderman.png", "builderman", "smirk", false],
    ["avatar_obby.png", "obby", "grin", false],
    ["avatar_theo.png", "theo", "smile", true]
  ];
  for (const [fname, thm, expr, mug] of classicAvatars) {
    writePng(fname, 260, 340, () =>
      render3DViewport(
        260,
        340,
        (p) => evalAvatarSDF(p, { yaw: 0.32, armLPitch: -0.22, armRPitch: -0.42, theme: thm, expression: expr, hasMug: mug }),
        { ...studioCam, ro: v3(0, 0.24, 2.72), ta: v3(0, 0.05, 0) }
      )
    );
  }

  const classicFaces = [
    ["face_smile.png", "smile"],
    ["face_deadpan.png", "deadpan"],
    ["face_smirk.png", "smirk"],
    ["face_grin.png", "grin"],
    ["face_shocked.png", "shocked"],
    ["face_tears.png", "tears"],
    ["face_angry.png", "angry"],
    ["face_dizzy.png", "dizzy"]
  ];
  for (const [fname, expr] of classicFaces) {
    writePng(fname, 220, 220, () =>
      render3DViewport(
        220,
        220,
        (p) => evalAvatarSDF(p, { yaw: 0.12, theme: "noob", expression: expr }),
        { ...studioCam, ro: v3(0, 0.76, 1.28), ta: v3(0, 0.74, 0), floorY: null }
      )
    );
  }

  const suites = [
    ["alarm", buildAlarmMeltdownScene],
    ["obby", buildObbySkyScene],
    ["duo", buildDuoComedyScene],
    ["cafe", buildCozyCafeScene],
    ["runway", buildRunwayDropScene],
    ["pizza", buildBurntPizzaScene],
    ["tornado", buildTornadoTowerScene],
    ["chase", buildPoliceChaseScene],
    ["doors", buildDoorsHallwayScene],
    ["sword", buildSwordDuelScene],
    ["exam", buildExamPanicScene],
    ["redlight", buildRedLightScene]
  ];

  for (const [prefix, builder] of suites) {
    for (let s = 0; s < 4; s++) {
      writePng(`${prefix}_shot_${s}.png`, 360, 640, () => {
        const { cam, sceneFn } = builder(s, 0.55);
        return render3DViewport(360, 640, sceneFn, cam);
      });
    }
    let frameIdx = 0;
    for (let s = 0; s < 4; s++) {
      for (let f = 0; f < 6; f++) {
        const phase = (f + 0.5) / 6;
        const idx = frameIdx++;
        writePng(`${prefix}_anim_${String(idx).padStart(2, "0")}.png`, 270, 480, () => {
          const { cam, sceneFn } = builder(s, phase);
          return render3DViewport(270, 480, sceneFn, cam);
        });
      }
    }
  }
}

export function buildBoardsManifest(rawDir) {
  const showcaseDir = path.join(ROOT, "assets", "showcase");
  const alarmDir = path.join(ROOT, "examples", "monday-alarm-meltdown", "assets");
  const obbyDir = path.join(ROOT, "examples", "obby-sky-run", "assets");
  const duoDir = path.join(ROOT, "examples", "duo-bestie-contrast", "assets");
  const cafeDir = path.join(ROOT, "examples", "cozy-cafe-tycoon", "assets");
  const runwayDir = path.join(ROOT, "examples", "runway-outfit-drop", "assets");
  const pizzaDir = path.join(ROOT, "examples", "burnt-pizza-slapstick", "assets");
  const tornadoDir = path.join(ROOT, "examples", "disaster-tower-tornado", "assets");
  const chaseDir = path.join(ROOT, "examples", "brookhaven-police-chase", "assets");
  const doorsDir = path.join(ROOT, "examples", "doors-flashlight-hallway", "assets");
  const swordDir = path.join(ROOT, "examples", "crossroads-sword-duel", "assets");
  const examDir = path.join(ROOT, "examples", "classroom-exam-panic", "assets");
  const redlightDir = path.join(ROOT, "examples", "red-light-freeze", "assets");
  for (const d of [showcaseDir, alarmDir, obbyDir, duoDir, cafeDir, runwayDir, pizzaDir, tornadoDir, chaseDir, doorsDir, swordDir, examDir, redlightDir]) {
    fs.mkdirSync(d, { recursive: true });
  }

  return {
    rootDir: ROOT,
    rawDir,
    turnaround: {
      outZh: path.join(showcaseDir, "momo_turnaround_sheet.zh.png"),
      outEn: path.join(showcaseDir, "momo_turnaround_sheet.en.png"),
      outDefault: [
        path.join(showcaseDir, "momo_turnaround_sheet.png"),
        path.join(alarmDir, "momo_turnaround_sheet.png")
      ],
      views: [
        { file: "turn_front.png", labelZh: "正面 0°", labelEn: "Front 0°" },
        { file: "turn_3q.png", labelZh: "斜侧 45°", labelEn: "3/4 View 45°" },
        { file: "turn_side.png", labelZh: "侧面 90°", labelEn: "Profile 90°" }
      ]
    },
    drift: {
      outZh: path.join(showcaseDir, "drift_rescue_comparison.zh.png"),
      outEn: path.join(showcaseDir, "drift_rescue_comparison.en.png"),
      outDefault: path.join(showcaseDir, "drift_rescue_comparison.png"),
      panels: [
        { file: "drift_1_fingers.png", labelZh: "× 真人手指 / 鼻子", labelEn: "× Human Fingers / Nose", r: 225, g: 29, b: 72 },
        { file: "drift_2_lego.png", labelZh: "× 乐高圆粒 / C型爪", labelEn: "× Lego Studs / C-Claw", r: 217, g: 119, b: 6 },
        { file: "drift_3_voxel.png", labelZh: "× MC 直角像素块", labelEn: "× Voxel Cube Head", r: 124, g: 58, b: 237 },
        { file: "drift_4_locked.png", labelZh: "✓ 标准 R6 方块比例", labelEn: "✓ Blocky R6 Rig", r: 5, g: 150, b: 105 }
      ]
    },
    classicAssetSheet: {
      avatarsOutZh: path.join(showcaseDir, "classic_avatars_lineup.zh.png"),
      avatarsOutEn: path.join(showcaseDir, "classic_avatars_lineup.en.png"),
      avatarsOutDefault: path.join(showcaseDir, "classic_avatars_lineup.png"),
      facesOutZh: path.join(showcaseDir, "classic_faces_atlas.zh.png"),
      facesOutEn: path.join(showcaseDir, "classic_faces_atlas.en.png"),
      facesOutDefault: path.join(showcaseDir, "classic_faces_atlas.png"),
      avatars: [
        { file: "avatar_noob.png", labelZh: "Classic Noob · 经典新手", labelEn: "Classic Noob" },
        { file: "avatar_guest.png", labelZh: "Classic Guest · 三角标夹克", labelEn: "Classic Guest" },
        { file: "avatar_bacon.png", labelZh: "Bacon Hair · 培根头", labelEn: "Bacon Hair" },
        { file: "avatar_builderman.png", labelZh: "Builder Hat · 安全帽", labelEn: "Builder Hard Hat" },
        { file: "avatar_obby.png", labelZh: "Speedrunner · 加速弹簧", labelEn: "Obby + Speed Coil" },
        { file: "avatar_theo.png", labelZh: "Story Hero · 连帽卫衣", labelEn: "Storytime Hoodie" }
      ],
      faces: [
        { file: "face_smile.png", labelZh: "Default Smile · 默认笑脸", labelEn: "Default Smile :)" },
        { file: "face_deadpan.png", labelZh: "Chill · 死鱼眼", labelEn: "Chill -_-" },
        { file: "face_smirk.png", labelZh: "Check It · 挑眉坏笑", labelEn: "Check It Smirk" },
        { file: "face_grin.png", labelZh: "Winning Grin · 露齿笑", labelEn: "Winning Grin :D" },
        { file: "face_shocked.png", labelZh: "Shocked · 震惊大眼", labelEn: "Shocked O_O" },
        { file: "face_tears.png", labelZh: "Crying · 瀑布流泪", labelEn: "Waterfall Tears" },
        { file: "face_angry.png", labelZh: "Bloxxer · 愤怒皱眉", labelEn: "Angry Bloxxer" },
        { file: "face_dizzy.png", labelZh: "KO Dizzy · 眩晕击败", labelEn: "KO Dizzy X_X" }
      ]
    },
    cases: [
      {
        prefix: "alarm",
        sheetZh: path.join(alarmDir, "storyboard_contact_sheet.zh.png"),
        sheetEn: path.join(alarmDir, "storyboard_contact_sheet.en.png"),
        sheetDefault: path.join(alarmDir, "storyboard_contact_sheet.png"),
        gifPath: path.join(alarmDir, "monday_alarm_meltdown.gif"),
        mp4Path: path.join(alarmDir, "monday_alarm_meltdown.mp4"),
        shots: [
          {
            labelZh: "01 · 闹钟惊醒 (0–3.5s)",
            labelEn: "01 · 7:59 AM Hook (0–3.5s)",
            chatZh: "7:59?!",
            chatEn: "7:59?!",
            bubbleX: 186,
            bubbleY: 36,
            savePath: path.join(alarmDir, "shot_01_hook.png")
          },
          {
            labelZh: "02 · 拍停闹钟 (3.5–7.5s)",
            labelEn: "02 · Snooze Slam (3.5–7.5s)",
            chatZh: "再睡5分钟",
            chatEn: "5 more mins",
            bubbleX: 182,
            bubbleY: 38,
            savePath: path.join(alarmDir, "shot_02_slam.png")
          },
          {
            labelZh: "03 · 消息刷屏 (7.5–11.5s)",
            labelEn: "03 · 99+ Pings (7.5–11.5s)",
            chatZh: "99+ 未读?!",
            chatEn: "99+ pings?!",
            bubbleX: 165,
            bubbleY: 36,
            savePath: path.join(alarmDir, "shot_03_tears.png")
          },
          {
            labelZh: "04 · 扑倒键盘 (11.5–15s)",
            labelEn: "04 · Faceplant Loop (11.5–15s)",
            chatZh: "oof.",
            chatEn: "oof.",
            bubbleX: 156,
            bubbleY: 88,
            savePath: path.join(alarmDir, "shot_04_faceplant.png")
          }
        ]
      },
      {
        prefix: "obby",
        sheetZh: path.join(obbyDir, "obby_storyboard_sheet.zh.png"),
        sheetEn: path.join(obbyDir, "obby_storyboard_sheet.en.png"),
        sheetDefault: path.join(obbyDir, "obby_storyboard_sheet.png"),
        gifPath: path.join(obbyDir, "obby_sky_run.gif"),
        mp4Path: path.join(obbyDir, "obby_sky_run.mp4"),
        shots: [
          { labelZh: "01 · 加速弹簧起跳", labelEn: "01 · Speed Coil Jump", chatZh: "加速起飞!", chatEn: "Speed Coil!", bubbleX: 155, bubbleY: 36 },
          { labelZh: "02 · 连续浮台跳跃", labelEn: "02 · Rhythm Hops", chatZh: "稳住!", chatEn: "ez jumps", bubbleX: 160, bubbleY: 38 },
          { labelZh: "03 · 激光砖前急停", labelEn: "03 · Killbrick Stop", chatZh: "红砖别踩!", chatEn: "KILLBRICK!", bubbleX: 162, bubbleY: 38 },
          { labelZh: "04 · 旗帜点循环", labelEn: "04 · Checkpoint Loop", chatZh: "通关 GG!", chatEn: "GG!", bubbleX: 162, bubbleY: 36 }
        ]
      },
      {
        prefix: "duo",
        sheetZh: path.join(duoDir, "duo_storyboard_sheet.zh.png"),
        sheetEn: path.join(duoDir, "duo_storyboard_sheet.en.png"),
        sheetDefault: path.join(duoDir, "duo_storyboard_sheet.png"),
        gifPath: path.join(duoDir, "duo_bestie_contrast.gif"),
        mp4Path: path.join(duoDir, "duo_bestie_contrast.mp4"),
        shots: [
          { labelZh: "01 · 潮人闺蜜 vs 新手", labelEn: "01 · Y2K vs. Classic Noob", chatZh: "看镜头!", chatEn: "pose!", bubbleX: 98, bubbleY: 38 },
          { labelZh: "02 · 书包转身撞人", labelEn: "02 · Backpack Bump", chatZh: "哎呀!", chatEn: "oops!", bubbleX: 108, bubbleY: 38 },
          { labelZh: "03 · R6 刚体直挺侧倒", labelEn: "03 · Rigid Plank Tilt", chatZh: "oof", chatEn: "oof", bubbleX: 215, bubbleY: 56 },
          { labelZh: "04 · 同步死鱼眼盯镜", labelEn: "04 · Deadpan Stare", chatZh: "...", chatEn: "bruh...", bubbleX: 160, bubbleY: 40 }
        ]
      },
      {
        prefix: "cafe",
        sheetZh: path.join(cafeDir, "cafe_storyboard_sheet.zh.png"),
        sheetEn: path.join(cafeDir, "cafe_storyboard_sheet.en.png"),
        sheetDefault: path.join(cafeDir, "cafe_storyboard_sheet.png"),
        gifPath: path.join(cafeDir, "cozy_cafe_tycoon.gif"),
        mp4Path: path.join(cafeDir, "cozy_cafe_tycoon.mp4"),
        shots: [
          { labelZh: "01 · 甜点吧台登场", labelEn: "01 · Counter Pop-Up", chatZh: "欢迎光临!", chatEn: "Fresh croissants!", bubbleX: 160, bubbleY: 36 },
          { labelZh: "02 · 羊角包摆盘", labelEn: "02 · Croissant Snap", chatZh: "刚出炉!", chatEn: "Hot & crispy", bubbleX: 160, bubbleY: 38 },
          { labelZh: "03 · 递出热拿铁", labelEn: "03 · Latte Slide", chatZh: "您的拿铁!", chatEn: "One latte!", bubbleX: 160, bubbleY: 38 },
          { labelZh: "04 · 金币弹出循环", labelEn: "04 · +999 Coins Loop", chatZh: "+999 金币!", chatEn: "+999 Coins!", bubbleX: 160, bubbleY: 36 }
        ]
      },
      {
        prefix: "runway",
        sheetZh: path.join(runwayDir, "runway_storyboard_sheet.zh.png"),
        sheetEn: path.join(runwayDir, "runway_storyboard_sheet.en.png"),
        sheetDefault: path.join(runwayDir, "runway_storyboard_sheet.png"),
        gifPath: path.join(runwayDir, "runway_outfit_drop.gif"),
        mp4Path: path.join(runwayDir, "runway_outfit_drop.mp4"),
        shots: [
          { labelZh: "01 · 灰模初始状态", labelEn: "01 · Plain Base Avatar", chatZh: "还没穿搭...", chatEn: "0 stars...", bubbleX: 160, bubbleY: 48 },
          { labelZh: "02 · 蓄力旋转起跳", labelEn: "02 · Beat-Drop Spin", chatZh: "3, 2, 1!", chatEn: "Wait for it!", bubbleX: 160, bubbleY: 44 },
          { labelZh: "03 · 重音落地换装", labelEn: "03 · Y2K Crown Reveal", chatZh: "五星换装!", chatEn: "5 Stars!!", bubbleX: 160, bubbleY: 48 },
          { labelZh: "04 · T台定格亮相", labelEn: "04 · Runway Pose", chatZh: "全场最佳!", chatEn: "Top Model!", bubbleX: 160, bubbleY: 48 }
        ]
      },
      {
        prefix: "pizza",
        sheetZh: path.join(pizzaDir, "pizza_storyboard_sheet.zh.png"),
        sheetEn: path.join(pizzaDir, "pizza_storyboard_sheet.en.png"),
        sheetDefault: path.join(pizzaDir, "pizza_storyboard_sheet.png"),
        gifPath: path.join(pizzaDir, "burnt_pizza_slapstick.gif"),
        mp4Path: path.join(pizzaDir, "burnt_pizza_slapstick.mp4"),
        shots: [
          { labelZh: "01 · 端出焦黑披萨", labelEn: "01 · Burnt Black Pizza", chatZh: "我烤好了!", chatEn: "Dinner is ready!", bubbleX: 160, bubbleY: 38 },
          { labelZh: "02 · 顶光呆滞微笑", labelEn: "02 · Deadpan Spotlight", chatZh: ":)", chatEn: ":)", bubbleX: 160, bubbleY: 38 },
          { labelZh: "03 · 方柱手臂脱落", labelEn: "03 · Arm Detaches", chatZh: "胳膊掉了?", chatEn: "my arm...", bubbleX: 160, bubbleY: 38 },
          { labelZh: "04 · 90°刚体拍地", labelEn: "04 · 90° Statue Flop", chatZh: "oof.", chatEn: "oof.", bubbleX: 160, bubbleY: 76 }
        ]
      },
      {
        prefix: "tornado",
        sheetZh: path.join(tornadoDir, "tornado_storyboard_sheet.zh.png"),
        sheetEn: path.join(tornadoDir, "tornado_storyboard_sheet.en.png"),
        sheetDefault: path.join(tornadoDir, "tornado_storyboard_sheet.png"),
        gifPath: path.join(tornadoDir, "disaster_tower_tornado.gif"),
        mp4Path: path.join(tornadoDir, "disaster_tower_tornado.mp4"),
        shots: [
          { labelZh: "01 · 龙卷风逼近", labelEn: "01 · Tornado Spotted", chatZh: "龙卷风!!", chatEn: "TORNADO!!", bubbleX: 160, bubbleY: 36 },
          { labelZh: "02 · 抓紧护栏", labelEn: "02 · Hold the Rail", chatZh: "塔要塌了!", chatEn: "Hold on!", bubbleX: 160, bubbleY: 38 },
          { labelZh: "03 · 极限跳柱", labelEn: "03 · Last Pillar Jump", chatZh: "救命!!", chatEn: "JUMP!!", bubbleX: 160, bubbleY: 36 },
          { labelZh: "04 · 孤柱存活", labelEn: "04 · Survived!", chatZh: "成功存活!", chatEn: "Survived!", bubbleX: 160, bubbleY: 36 }
        ]
      },
      {
        prefix: "chase",
        sheetZh: path.join(chaseDir, "chase_storyboard_sheet.zh.png"),
        sheetEn: path.join(chaseDir, "chase_storyboard_sheet.en.png"),
        sheetDefault: path.join(chaseDir, "chase_storyboard_sheet.png"),
        gifPath: path.join(chaseDir, "brookhaven_police_chase.gif"),
        mp4Path: path.join(chaseDir, "brookhaven_police_chase.mp4"),
        shots: [
          { labelZh: "01 · 抱钱袋狂奔", labelEn: "01 · Bank Heist Dash", chatZh: "溜了溜了!", chatEn: "Catch me!", bubbleX: 205, bubbleY: 38 },
          { labelZh: "02 · 警车警灯追击", labelEn: "02 · Siren Pursuit", chatZh: "站住!!", chatEn: "STOP!!", bubbleX: 105, bubbleY: 38 },
          { labelZh: "03 · 消防栓绊倒", labelEn: "03 · Hydrant Trip", chatZh: "哎哟!", chatEn: "WHOA!", bubbleX: 195, bubbleY: 38 },
          { labelZh: "04 · 铁窗拿下", labelEn: "04 · Busted!", chatZh: "已老实...", chatEn: "busted...", bubbleX: 190, bubbleY: 64 }
        ]
      },
      {
        prefix: "doors",
        sheetZh: path.join(doorsDir, "doors_storyboard_sheet.zh.png"),
        sheetEn: path.join(doorsDir, "doors_storyboard_sheet.en.png"),
        sheetDefault: path.join(doorsDir, "doors_storyboard_sheet.png"),
        gifPath: path.join(doorsDir, "doors_flashlight_hallway.gif"),
        mp4Path: path.join(doorsDir, "doors_flashlight_hallway.mp4"),
        shots: [
          { labelZh: "01 · 50号门探索", labelEn: "01 · Door 050 Check", chatZh: "第50号门...", chatEn: "Door 50...", bubbleX: 138, bubbleY: 38 },
          { labelZh: "02 · 走廊闪灯", labelEn: "02 · Lights Flicker", chatZh: "灯闪了?!", chatEn: "Flicker?!", bubbleX: 138, bubbleY: 38 },
          { labelZh: "03 · 身后白眼", labelEn: "03 · Eyes Behind", chatZh: "身后有东西!", chatEn: "BEHIND ME!", bubbleX: 138, bubbleY: 38 },
          { labelZh: "04 · 极限躲木柜", labelEn: "04 · Closet Hide", chatZh: "快躲衣柜!", chatEn: "HIDE!!", bubbleX: 195, bubbleY: 38 }
        ]
      },
      {
        prefix: "sword",
        sheetZh: path.join(swordDir, "sword_storyboard_sheet.zh.png"),
        sheetEn: path.join(swordDir, "sword_storyboard_sheet.en.png"),
        sheetDefault: path.join(swordDir, "sword_storyboard_sheet.png"),
        gifPath: path.join(swordDir, "crossroads_sword_duel.gif"),
        mp4Path: path.join(swordDir, "crossroads_sword_duel.mp4"),
        shots: [
          { labelZh: "01 · 石桥拔剑", labelEn: "01 · Bridge Standoff", chatZh: "来1v1!", chatEn: "1v1 Duel!", bubbleX: 105, bubbleY: 38 },
          { labelZh: "02 · 空中拼刀火花", labelEn: "02 · Mid-Air Clash", chatZh: "当!!", chatEn: "CLANG!!", bubbleX: 160, bubbleY: 32 },
          { labelZh: "03 · 悬崖险情", labelEn: "03 · Ledge Knockback", chatZh: "要掉岩浆了!", chatEn: "WHOA!", bubbleX: 215, bubbleY: 38 },
          { labelZh: "04 · 汽水言和", labelEn: "04 · Soda Truce", chatZh: "干杯 GG!", chatEn: "GG Truce!", bubbleX: 160, bubbleY: 38 }
        ]
      },
      {
        prefix: "exam",
        sheetZh: path.join(examDir, "exam_storyboard_sheet.zh.png"),
        sheetEn: path.join(examDir, "exam_storyboard_sheet.en.png"),
        sheetDefault: path.join(examDir, "exam_storyboard_sheet.png"),
        gifPath: path.join(examDir, "classroom_exam_panic.gif"),
        mp4Path: path.join(examDir, "classroom_exam_panic.mp4"),
        shots: [
          { labelZh: "01 · 自信接卷", labelEn: "01 · Confident Start", chatZh: "稳拿满分!", chatEn: "Easy A+!", bubbleX: 160, bubbleY: 38 },
          { labelZh: "02 · 看题傻眼", labelEn: "02 · Question 1 Shock", chatZh: "这考的啥?!", chatEn: "WHAT IS THIS?!", bubbleX: 160, bubbleY: 36 },
          { labelZh: "03 · 握笔狂写", labelEn: "03 · 2x Speed Scribble", chatZh: "先写个解!", chatEn: "2 mins left!", bubbleX: 160, bubbleY: 38 },
          { labelZh: "04 · 交卷宕机", labelEn: "04 · Brain KO", chatZh: "大脑已空...", chatEn: "brain empty", bubbleX: 160, bubbleY: 42 }
        ]
      },
      {
        prefix: "redlight",
        sheetZh: path.join(redlightDir, "redlight_storyboard_sheet.zh.png"),
        sheetEn: path.join(redlightDir, "redlight_storyboard_sheet.en.png"),
        sheetDefault: path.join(redlightDir, "redlight_storyboard_sheet.png"),
        gifPath: path.join(redlightDir, "red_light_freeze.gif"),
        mp4Path: path.join(redlightDir, "red_light_freeze.mp4"),
        shots: [
          { labelZh: "01 · 绿灯冲刺", labelEn: "01 · Green Light Sprint", chatZh: "绿灯快冲!", chatEn: "Green Light!", bubbleX: 160, bubbleY: 38 },
          { labelZh: "02 · 红灯急停", labelEn: "02 · Red Light Freeze", chatZh: "别动!!", chatEn: "RED LIGHT!!", bubbleX: 160, bubbleY: 34 },
          { labelZh: "03 · 单腿摇晃", labelEn: "03 · One-Leg Wobble", chatZh: "你别晃啊!", chatEn: "don't move...", bubbleX: 195, bubbleY: 36 },
          { labelZh: "04 · 飞扑过线", labelEn: "04 · Finish Dive", chatZh: "压线过关!", chatEn: "SAFE!!", bubbleX: 160, bubbleY: 42 }
        ]
      }
    ]
  };
}

// ---------- Declarative Custom Episode 3D Video Engine (--spec <episode.json> --out-dir <dir>) ----------
function vecFromArr(arr, fallback = v3(0, 0, 0)) {
  if (!Array.isArray(arr) || arr.length < 3) return fallback;
  return v3(Number(arr[0]) || 0, Number(arr[1]) || 0, Number(arr[2]) || 0);
}

function lerpVec(a, b, t) {
  return v3(mix(a.x, b.x, t), mix(a.y, b.y, t), mix(a.z, b.z, t));
}

function mapArchetypeTo3DTheme(arch = "", explicitTheme = "") {
  if (explicitTheme) return explicitTheme;
  const map = {
    "chibi-plush": "commuter",
    "classic-noob": "noob",
    "bacon-hair": "bacon",
    "classic-guest": "guest",
    builderman: "builderman",
    "ugc-streetwear": "y2k",
    "corporate-worker": "theo",
    "cozy-chef": "chef",
    "obby-runner": "obby",
    "zombie-r6": "zombie"
  };
  return map[arch] || arch || "theo";
}

function addDeclarativeBackdrop(hit, p, backdrop = "studio", phase = 0.5) {
  if (backdrop === "bedroom") {
    addBedroomBackdrop(hit, p);
  } else if (backdrop === "subway_car") {
    // Lipschitz-exact bound covering seats out to z = -0.50 (prevents front-edge seat striping!)
    if (p.z - (-0.42) <= hit.d) {
      hit.add(sdRoundBox(sub3(p, v3(0, 0.42, -1.18)), v3(2.8, 1.48, 0.07), 0.01), [219, 228, 238], 0.44, 19);
      hit.add(sdRoundBox(sub3(p, v3(0, 0.52, -1.08)), v3(2.7, 0.04, 0.03), 0.01), [249, 115, 22], 0.25, 20);
      for (const wx of [-1.05, 0.0, 1.05]) {
        const pw = sub3(p, v3(wx, 0.88, -1.08));
        if (len3(pw) - 0.65 <= hit.d) {
          hit.add(sdRoundBox(pw, v3(0.42, 0.26, 0.035), 0.03), [71, 85, 105], 0.22, 19);
          hit.add(sdRoundBox(sub3(pw, v3(0, 0, 0.014)), v3(0.36, 0.20, 0.025), 0.02), [56, 189, 248], 0.06, 19);
        }
      }
      // Teal & slate subway seats along back wall
      hit.add(sdRoundBox(sub3(p, v3(0.62, -0.46, -0.78)), v3(0.48, 0.08, 0.26), 0.025), [13, 148, 136], 0.26, 20);
      hit.add(sdRoundBox(sub3(p, v3(0.62, -0.20, -0.98)), v3(0.48, 0.24, 0.07), 0.025), [13, 148, 136], 0.26, 20);
      hit.add(sdRoundBox(sub3(p, v3(-0.92, -0.46, -0.78)), v3(0.48, 0.08, 0.26), 0.025), [100, 116, 139], 0.34, 20);
    }
    // Overhead grab rail & 3 amber commuter straps (docked cleanly to raised 1x2x1 block hand height!)
    if (Math.max(0.98 - p.y, Math.abs(p.z - 0.04) - 0.18) <= hit.d) {
      hit.add(sdRoundBox(sub3(p, v3(0, 1.30, 0.04)), v3(2.2, 0.03, 0.03), 0.012), [203, 213, 225], 0.16, 20);
      for (const sx of [-0.72, 0.0, 0.72]) {
        const swing = sx === 0 ? Math.sin(phase * Math.PI * 2) * 0.08 : 0;
        const ps = rotZ(sub3(p, v3(sx, 1.12, 0.04)), swing);
        hit.add(sdRoundBox(sub3(ps, v3(0, 0.08, 0)), v3(0.022, 0.10, 0.022), 0.008), [148, 163, 184], 0.25, 20);
        hit.add(sdRoundBox(sub3(ps, v3(0, -0.06, 0)), v3(0.088, 0.055, 0.025), 0.018), [245, 158, 11], 0.20, 20);
      }
    }
  } else if (backdrop === "adoption_plaza" || backdrop === "plaza") {
    if (p.z - (-0.65) <= hit.d) {
      hit.add(sdRoundBox(sub3(p, v3(0, 0.38, -1.18)), v3(2.8, 1.5, 0.06), 0.01), [250, 245, 255], 0.45, 38);
      const pa = sub3(p, v3(0, 0.28, -1.04));
      const dArch = Math.max(
        sdRoundedCylinder(rotX(pa, Math.PI / 2), 1.08, 0.03, 0.05),
        -sdRoundedCylinder(rotX(pa, Math.PI / 2), 0.92, 0.02, 0.09),
        -(pa.y + 0.85)
      );
      hit.add(dArch, [56, 189, 248], 0.05, 51);
    }
    if (backdrop === "adoption_plaza") {
      // Pastel pedestal in center-front for egg/pet showcase
      hit.add(sdRoundedCylinder(sub3(p, v3(0.22, -0.68, 0.28)), 0.34, 0.025, 0.16), [233, 213, 255], 0.24, 50);
      hit.add(sdRoundedCylinder(sub3(p, v3(0.22, -0.50, 0.28)), 0.28, 0.02, 0.03), [255, 255, 255], 0.18, 50);
    }
  } else if (backdrop === "convenience_store") {
    if (p.z - (-0.55) <= hit.d) {
      hit.add(sdRoundBox(sub3(p, v3(0, 0.38, -1.08)), v3(2.8, 1.5, 0.06), 0.01), [241, 245, 249], 0.44, 44);
      // Neon 24H header stripe (green / orange / blue)
      hit.add(sdRoundBox(sub3(p, v3(0, 1.12, -0.98)), v3(2.4, 0.06, 0.04), 0.01), [16, 185, 129], 0.05, 44);
      hit.add(sdRoundBox(sub3(p, v3(0, 1.00, -0.98)), v3(2.4, 0.05, 0.04), 0.01), [249, 115, 22], 0.05, 44);
      // Stocked snack shelf on right
      const psh = sub3(p, v3(0.82, 0.22, -0.88));
      if (len3(psh) - 0.85 <= hit.d) {
        hit.add(sdRoundBox(psh, v3(0.46, 0.56, 0.12), 0.015), [203, 213, 225], 0.32, 45);
        for (const [bx, by, col] of [[-0.22, 0.28, [239, 68, 68]], [0.0, 0.28, [59, 130, 246]], [0.22, 0.28, [250, 204, 21]], [-0.18, -0.05, [16, 185, 129]], [0.14, -0.05, [244, 114, 182]]]) {
          hit.add(sdRoundBox(sub3(psh, v3(bx, by, 0.06)), v3(0.08, 0.11, 0.06), 0.012), col, 0.24, 45);
        }
      }
    }
    // Convenience store counter
    hit.add(sdRoundBox(sub3(p, v3(0, -0.58, 0.44)), v3(1.34, 0.26, 0.40), 0.02), [226, 232, 240], 0.32, 40);
    hit.add(sdRoundBox(sub3(p, v3(0, -0.32, 0.44)), v3(1.38, 0.035, 0.44), 0.015), [248, 250, 252], 0.20, 40);
  } else if (backdrop === "supermarket_aisle") {
    // Left and right supermarket shelves stocked with colorful blocky packages
    for (const side of [-1, 1]) {
      const ps = sub3(p, v3(side * 1.46, 0.12, -0.35));
      if (len3(ps) - 1.55 <= hit.d) {
        hit.add(sdRoundBox(ps, v3(0.20, 0.96, 1.02), 0.02), [226, 232, 240], 0.34, 45);
        for (const sy of [-0.36, 0.08, 0.52]) {
          const col = sy > 0.3 ? [239, 68, 68] : sy > -0.1 ? [14, 165, 233] : [250, 204, 21];
          hit.add(sdRoundBox(sub3(ps, v3(-side * 0.13, sy, 0.12)), v3(0.10, 0.12, 0.78), 0.02), col, 0.22, 45);
        }
      }
    }
  } else if (backdrop === "neon_tower") {
    // Open-front horseshoe neon tower shaft rings (clipped at p.z <= -0.18 so rings NEVER cut across the actor's face!)
    for (let i = -2; i <= 2; i++) {
      const ry = i * 0.66 - ((phase * 0.66) % 0.66);
      const pr = sub3(p, v3(0, ry, -0.42));
      if (Math.abs(pr.y) - 0.12 <= hit.d && p.z - (-0.18) <= hit.d) {
        const dShell = Math.max(sdRoundedCylinder(pr, 1.38, 0.02, 0.042), -sdRoundedCylinder(pr, 1.22, 0.01, 0.08));
        const dOpenFront = Math.max(dShell, p.z - (-0.18));
        hit.add(dOpenFront, i & 1 ? [168, 85, 247] : [56, 189, 248], 0.04, 51);
      }
    }
  }
}

function addDeclarativeProp(hit, p, prop, phase = 0.5) {
  if (prop.visible === false) return;
  if (Array.isArray(prop.visiblePhase) && prop.visiblePhase.length >= 2) {
    if (phase < Number(prop.visiblePhase[0]) || phase > Number(prop.visiblePhase[1])) return;
  }
  const s0 = prop.scale !== undefined ? Number(prop.scale) : 1.0;
  const s1 = prop.scaleTo !== undefined ? Number(prop.scaleTo) : s0;
  const scale = mix(s0, s1, smoothstep(0, 1, phase));
  if (scale <= 0.02) return;

  const p0 = vecFromArr(prop.pos, v3(0, -0.3, 0.4));
  const p1 = prop.moveTo ? vecFromArr(prop.moveTo, p0) : p0;
  const center = lerpVec(p0, p1, smoothstep(0, 1, phase));
  const q = mul3(rotY(sub3(p, center), Number(prop.yaw) || 0), 1 / scale);
  const sMul = scale;
  const t = prop.type || "box";

  if (t === "mystery_egg") {
    if ((len3(q) - 0.48) * sMul > hit.d) return;
    if (prop.state === "hatched") {
      hit.add(sdRoundedCylinder(sub3(q, v3(-0.14, -0.06, 0)), 0.16, 0.03, 0.08) * sMul, [248, 250, 252], 0.18, 52);
      hit.add(sdRoundedCylinder(sub3(q, v3(0.14, -0.06, 0)), 0.16, 0.03, 0.08) * sMul, [248, 250, 252], 0.18, 52);
    } else {
      const wobble = prop.state === "cracking" ? Math.sin(phase * Math.PI * 8) * 0.12 : 0;
      const qe = rotZ(q, wobble);
      const dEgg = (len3(v3(qe.x / 0.20, qe.y / 0.26, qe.z / 0.20)) - 1.0) * 0.20 * sMul;
      const crack = Math.abs(qe.y - Math.sin(qe.x * 18) * 0.03) < 0.022;
      hit.add(dEgg, crack ? [56, 189, 248] : [248, 250, 252], crack ? 0.03 : 0.16, 52);
    }
  } else if (t === "neon_dragon") {
    const orbitX = prop.orbit ? Math.cos(phase * Math.PI * 2) * 0.34 : 0;
    const orbitY = Math.sin(phase * Math.PI * 4) * 0.05;
    const qd = sub3(q, v3(orbitX, orbitY, 0));
    if ((len3(qd) - 0.52) * sMul > hit.d) return;
    // Blocky SmoothPlastic head & body + 2D dot eyes + cyan neon horns & flapping flat geometric wing plates
    hit.add(sdRoundBox(qd, v3(0.12, 0.10, 0.14), 0.03) * sMul, [248, 250, 252], 0.18, 53);
    const ph = sub3(qd, v3(0, 0.12, 0.10));
    const dHead = sdRoundBox(ph, v3(0.11, 0.095, 0.11), 0.028) * sMul;
    if (dHead < hit.d) {
      const isEye = ph.z > 0.08 && Math.abs(Math.abs(ph.x) - 0.045) < 0.02 && Math.abs(ph.y - 0.01) < 0.025;
      hit.add(dHead, isEye ? [15, 23, 42] : [255, 255, 255], 0.18, 53);
    }
    hit.add(sdRoundBox(sub3(ph, v3(-0.06, 0.11, -0.02)), v3(0.022, 0.045, 0.022), 0.006) * sMul, [56, 189, 248], 0.03, 53);
    hit.add(sdRoundBox(sub3(ph, v3(0.06, 0.11, -0.02)), v3(0.022, 0.045, 0.022), 0.006) * sMul, [56, 189, 248], 0.03, 53);
    const flap = Math.sin(phase * Math.PI * 6) * 0.38;
    const pwL = rotZ(sub3(qd, v3(-0.18, 0.06, -0.02)), -flap);
    const pwR = rotZ(sub3(qd, v3(0.18, 0.06, -0.02)), flap);
    hit.add(Math.min(sdRoundBox(pwL, v3(0.14, 0.018, 0.09), 0.008), sdRoundBox(pwR, v3(0.14, 0.018, 0.09), 0.008)) * sMul, [56, 189, 248], 0.04, 53);
  } else if (t === "trade_popup") {
    const count = clamp(Number(prop.count) || 1, 1, 4);
    // Framed left/right margin offsets so popup cards surround the character without covering their face!
    const offsets = [v3(-0.54, 0.32, 0.04), v3(0.54, 0.26, 0.04), v3(-0.48, -0.22, 0.06), v3(0.48, -0.26, 0.06)];
    for (let i = 0; i < count; i++) {
      const qp = sub3(q, count === 1 ? v3(0, 0, 0) : offsets[i]);
      if ((len3(qp) - 0.42) * sMul <= hit.d) {
        hit.add(sdRoundBox(qp, v3(0.25, 0.15, 0.018), 0.018) * sMul, [30, 41, 59], 0.20, 54);
        hit.add(sdRoundBox(sub3(qp, v3(-0.095, -0.055, 0.018)), v3(0.08, 0.04, 0.012), 0.01) * sMul, [34, 197, 94], 0.04, 54);
        hit.add(sdRoundBox(sub3(qp, v3(0.095, -0.055, 0.018)), v3(0.08, 0.04, 0.012), 0.01) * sMul, [244, 63, 94], 0.04, 54);
      }
    }
  } else if (t === "shopping_cart") {
    if ((len3(q) - 0.92) * sMul > hit.d) return;
    // Open wire/slatted metallic basket so seated passengers and pusher hands read clearly!
    let dCart = sdRoundBox(sub3(q, v3(0, -0.18, 0)), v3(0.36, 0.028, 0.44), 0.012); // bottom tray
    for (const sx of [-0.34, 0.34]) {
      for (const sz of [-0.42, 0.42]) {
        dCart = Math.min(dCart, sdRoundBox(sub3(q, v3(sx, 0.04, sz)), v3(0.026, 0.22, 0.026), 0.008)); // 4 corner posts
      }
      for (const ry of [-0.04, 0.10, 0.24]) {
        dCart = Math.min(dCart, sdRoundBox(sub3(q, v3(sx, ry, 0)), v3(0.022, 0.020, 0.42), 0.008)); // side rails
      }
    }
    for (const sz of [-0.42, 0.42]) {
      for (const ry of [0.06, 0.24]) {
        dCart = Math.min(dCart, sdRoundBox(sub3(q, v3(0, ry, sz)), v3(0.34, 0.022, 0.022), 0.008)); // front/back rails
      }
    }
    // Rear handle risers + bright red push-bar
    for (const sx of [-0.30, 0.30]) {
      dCart = Math.min(dCart, sdRoundBox(rotX(sub3(q, v3(sx, 0.32, -0.46)), -0.35), v3(0.022, 0.12, 0.022), 0.008));
    }
    hit.add(dCart * sMul, [203, 213, 225], 0.14, 85);
    hit.add(sdRoundBox(sub3(q, v3(0, 0.40, -0.50)), v3(0.34, 0.034, 0.034), 0.014) * sMul, [239, 68, 68], 0.18, 85);
    for (const sx of [-0.28, 0.28]) {
      for (const sz of [-0.32, 0.32]) {
        hit.add(sdRoundedCylinder(rotZ(sub3(q, v3(sx, -0.28, sz)), Math.PI / 2), 0.075, 0.015, 0.028) * sMul, [30, 41, 59], 0.4, 85);
      }
    }
  } else if (t === "ramen_cup") {
    if ((len3(q) - 0.45) * sMul > hit.d) return;
    const tipped = prop.spilled ? rotZ(q, 1.15) : q;
    const dCup = sdRoundedCylinder(tipped, 0.13, 0.02, 0.16) * sMul;
    hit.add(dCup, Math.abs(tipped.y) < 0.055 ? [239, 68, 68] : [255, 255, 255], 0.22, 86);
    hit.add(sdRoundedCylinder(sub3(tipped, v3(0, 0.15, 0)), 0.115, 0.008, 0.018) * sMul, [250, 204, 21], 0.3, 86);
    if (prop.spilled) {
      for (const nx of [-0.18, -0.06, 0.06]) {
        hit.add(sdRoundBox(sub3(q, v3(0.24 + nx * 0.4, -0.11, nx)), v3(0.14, 0.022, 0.025), 0.01) * sMul, [253, 224, 71], 0.28, 86);
      }
    }
    if (prop.tagged) {
      hit.add(sdRoundBox(sub3(q, v3(0.08, 0.04, 0.14)), v3(0.11, 0.065, 0.015), 0.008) * sMul, [250, 204, 21], 0.16, 86);
    }
  } else if (t === "laser_bar") {
    const ql = prop.spin ? rotY(q, phase * Math.PI * 2) : q;
    hit.add(sdRoundBox(ql, v3(0.92, 0.045, 0.065), 0.015) * sMul, [255, 38, 56], 0.03, 32);
    hit.add(sdRoundedCylinder(ql, 0.10, 0.02, 0.09) * sMul, [30, 41, 59], 0.25, 32);
  } else if (t === "glass_pad") {
    if (prop.broken && phase > 0.45) return;
    const flash = prop.flicker && Math.sin(phase * Math.PI * 8) > 0;
    const frame = Math.max(sdRoundBox(q, v3(0.54, 0.062, 0.54), 0.022), -sdRoundBox(q, v3(0.42, 0.09, 0.42), 0.01));
    hit.add(frame * sMul, flash ? [244, 63, 94] : [56, 189, 248], 0.06, 31);
    hit.add(sdRoundBox(q, v3(0.43, 0.032, 0.43), 0.01) * sMul, flash ? [251, 113, 133] : [186, 230, 253], 0.08, 31);
  } else if (t === "checkout_gate") {
    if ((len3(q) - 1.1) * sMul > hit.d) return;
    hit.add(sdRoundBox(sub3(q, v3(-0.62, 0, 0)), v3(0.14, 0.36, 0.32), 0.02) * sMul, [51, 65, 85], 0.3, 87);
    const swing = prop.crashed ? phase * 1.35 : 0;
    hit.add(sdRoundBox(rotY(sub3(q, v3(0, 0.12, 0)), swing), v3(0.55, 0.04, 0.04), 0.012) * sMul, [239, 68, 68], 0.18, 87);
  } else if (t === "alarm_clock") {
    addTwinBellAlarmClock(hit, p, center, prop.squash || 1.0, prop.tilt || 0);
  } else if (t === "laptop") {
    addOpenLaptop(hit, p, center);
  } else {
    // Generic platform / box / cylinder fallback so declarative "platform" or "box" props always render!
    const sz = vecFromArr(prop.size, t === "platform" ? v3(0.56, 0.07, 0.56) : v3(0.24, 0.24, 0.24));
    if ((len3(q) - (len3(sz) + 0.15)) * sMul > hit.d) return;
    const col = Array.isArray(prop.color) ? prop.color : t === "platform" ? [56, 189, 248] : [226, 232, 240];
    hit.add(sdRoundBox(q, sz, 0.024) * sMul, col, prop.roughness ?? 0.22, 94);
  }
}

function resolveActorMotion(actor = {}, phase = 0.5) {
  const pStart = vecFromArr(actor.fromPos || actor.pos, v3(0, 0, 0));
  const pEnd = vecFromArr(actor.toPos || actor.pos, pStart);
  const pos = lerpVec(pStart, pEnd, smoothstep(0, 1, phase));
  const yaw = mix(Number(actor.fromYaw ?? actor.yaw ?? 0), Number(actor.toYaw ?? actor.yaw ?? 0), phase);
  let roll = mix(Number(actor.fromRoll ?? actor.roll ?? 0), Number(actor.toRoll ?? actor.roll ?? 0), smoothstep(0, 1, phase));
  let waistPitch = Number(actor.waistPitch) || 0;
  let headYaw = Number(actor.headYaw) || 0;
  let headPitch = Number(actor.headPitch) || 0;
  let armLPitch = -0.12;
  let armRPitch = -0.15;
  let legLPitch = 0;
  let legRPitch = 0;

  const pose = actor.pose || "idle";
  const cyc = Math.sin(phase * Math.PI * 4);
  if (pose === "walk" || pose === "run" || pose === "sprint") {
    const amp = pose === "walk" ? 0.45 : 0.75;
    armLPitch = cyc * amp;
    armRPitch = -cyc * amp;
    legLPitch = -cyc * amp;
    legRPitch = cyc * amp;
  } else if (pose === "jump" || pose === "hop") {
    pos.y += Math.sin(phase * Math.PI) * 0.42;
    armLPitch = -0.85;
    armRPitch = 0.65;
    legLPitch = 0.45;
    legRPitch = -0.45;
  } else if (pose === "cheer") {
    armLPitch = 2.65;
    armRPitch = 2.65;
    pos.y += Math.abs(Math.sin(phase * Math.PI * 2)) * 0.12;
  } else if (pose === "wave" || pose === "swat") {
    armRPitch = 1.95 + Math.sin(phase * Math.PI * 6) * 0.38;
  } else if (pose === "slam") {
    const t = smoothstep(0.1, 0.7, phase);
    armRPitch = mix(2.1, 0.85, t);
    waistPitch = t * 0.22;
  } else if (pose === "pour") {
    armRPitch = 1.15 + Math.sin(phase * Math.PI) * 0.18;
    armLPitch = 0.55;
  } else if (pose === "recoil") {
    const t = smoothstep(0.05, 0.6, phase);
    waistPitch = -0.28 * t;
    armLPitch = 1.45 * t;
    armRPitch = 1.35 * t;
  } else if (pose === "sit") {
    pos.y -= 0.18;
    legLPitch = 1.48;
    legRPitch = 1.48;
    armLPitch = 0.25;
    armRPitch = 0.25;
  } else if (pose === "ride_cart") {
    pos.y += 0.12;
    legLPitch = 1.45;
    legRPitch = 1.45;
    armLPitch = 2.35;
    armRPitch = 1.15;
  } else if (pose === "push_cart") {
    armLPitch = 1.25;
    armRPitch = 1.25;
    legLPitch = -cyc * 0.62;
    legRPitch = cyc * 0.62;
  } else if (pose === "zombie_walk") {
    armLPitch = 1.48;
    armRPitch = 1.48;
    legLPitch = -cyc * 0.35;
    legRPitch = cyc * 0.35;
  } else if (pose === "hang_strap") {
    const sw = Math.sin(phase * Math.PI * 2) * 0.14;
    pos.y += 0.30;
    roll += sw;
    armRPitch = 3.12;
    armLPitch = -0.08;
  } else if (pose === "fall_rigid") {
    const t = smoothstep(0, 1, phase);
    pos.y = mix(pos.y + 0.32, pos.y - 0.38, t);
    waistPitch = -0.32 * t;
    roll += 0.42 * t;
    armLPitch = 2.15;
    armRPitch = 2.15;
  } else if (pose === "faceplant") {
    const t = smoothstep(0.05, 0.65, phase);
    return {
      pos,
      yaw,
      roll,
      bodyPitch: mix(0.28, 1.48, t),
      waistPitch: 0,
      headYaw,
      headPitch,
      armLPitch: 0.45,
      armRPitch: 0.45,
      legLPitch: 0,
      legRPitch: 0
    };
  } else if (pose === "plank_fall") {
    roll = smoothstep(0.05, 0.7, phase) * 1.48;
  } else if (pose === "one_leg_freeze") {
    pos.y += 0.12;
    armLPitch = -0.65;
    armRPitch = 0.65;
    legLPitch = 0.65;
    legRPitch = -0.35;
  } else if (pose === "head_turn") {
    headYaw = mix(0, Number(actor.targetHeadYaw ?? 0.68), smoothstep(0.1, 0.75, phase));
  } else if (pose === "sword_slash") {
    armRPitch = 1.28 + Math.sin(phase * Math.PI * 2) * 0.32;
  }

  return {
    pos,
    yaw,
    roll,
    bodyPitch: Number(actor.bodyPitch) || 0,
    waistPitch,
    headYaw,
    headPitch,
    armLPitch,
    armRPitch,
    legLPitch,
    legRPitch
  };
}

function resolveDeclarativeCamera(shot = {}, backdrop = "studio", phase = 0.5) {
  const camSpec = shot.camera && typeof shot.camera === "object" ? shot.camera : { preset: shot.cameraPreset || "medium" };
  const preset = camSpec.preset || "medium";
  let ro = v3(0, 0.36, 3.18);
  let ta = v3(0, 0.10, 0);
  let fov = Number(camSpec.fov) || 1.9;

  if (preset === "close_up") {
    ro = v3(0, 0.46, 2.32);
    ta = v3(0, 0.28, 0.08);
  } else if (preset === "push_in") {
    ro = lerpVec(v3(0, 0.42, 3.25), v3(0, 0.38, 2.52), phase);
    ta = v3(0, 0.16, 0.05);
  } else if (preset === "pull_out") {
    ro = lerpVec(v3(0, 0.38, 2.55), v3(0, 0.44, 3.48), phase);
    ta = v3(0, 0.12, 0);
  } else if (preset === "hero_low") {
    ro = v3(0.28, 0.08, 2.78);
    ta = v3(0, 0.24, 0);
  } else if (preset === "side_track") {
    ro = lerpVec(v3(-0.55, 0.38, 3.35), v3(0.55, 0.38, 3.35), phase);
    ta = v3(mix(-0.2, 0.2, phase), 0.10, 0);
  } else if (preset === "high_iso") {
    ro = v3(0.88, 1.05, 2.95);
    ta = v3(0, 0.04, 0.12);
  } else if (preset === "wide_two_shot" || preset === "wide_aisle") {
    ro = v3(0, 0.42, 3.68);
    ta = v3(0, 0.08, 0);
  } else if (preset === "fall_follow") {
    ro = v3(0.35, 0.65 - phase * 0.45, 3.35);
    ta = v3(0, -0.15 * phase, 0);
  }

  if (camSpec.ro || camSpec.fromRo) {
    const r0 = vecFromArr(camSpec.fromRo || camSpec.ro, ro);
    const r1 = vecFromArr(camSpec.toRo || camSpec.ro, r0);
    ro = lerpVec(r0, r1, phase);
  }
  if (camSpec.ta || camSpec.fromTa) {
    const t0 = vecFromArr(camSpec.fromTa || camSpec.ta, ta);
    const t1 = vecFromArr(camSpec.toTa || camSpec.ta, t0);
    ta = lerpVec(t0, t1, phase);
  }
  if (camSpec.shake) {
    const sh = Number(camSpec.shake) * Math.sin(phase * Math.PI * 10);
    ro = add3(ro, v3(sh, Math.abs(sh) * 0.5, 0));
  }

  const stageTheme = {
    subway_car: { bgTop: [71, 85, 105], bgBot: [148, 163, 184], floorY: -0.86, floorStyle: "studio_grid", floorColor1: [71, 85, 105], floorColor2: [64, 78, 98] },
    adoption_plaza: { bgTop: [192, 132, 252], bgBot: [250, 232, 255], floorY: -0.86, floorStyle: "plaza_pavers", floorColor1: [243, 232, 255], floorColor2: [233, 213, 255] },
    plaza: { bgTop: [147, 197, 253], bgBot: [241, 245, 249], floorY: -0.86, floorStyle: "plaza_pavers", floorColor1: [241, 245, 249], floorColor2: [226, 232, 240] },
    convenience_store: { bgTop: [30, 41, 59], bgBot: [71, 85, 105], floorY: -0.86, floorStyle: "checker_tile", floorColor1: [241, 245, 249], floorColor2: [203, 213, 225] },
    supermarket_aisle: { bgTop: [186, 230, 253], bgBot: [248, 250, 252], floorY: -0.86, floorStyle: "checker_tile", floorColor1: [248, 250, 252], floorColor2: [226, 232, 240] },
    neon_tower: { bgTop: [15, 23, 42], bgBot: [49, 46, 129], floorY: camSpec.floorY === undefined ? null : camSpec.floorY, floorStyle: "studio_grid", floorColor1: [51, 65, 85], floorColor2: [30, 41, 59] },
    bedroom: { bgTop: [147, 197, 253], bgBot: [241, 245, 249], floorY: -0.86, floorStyle: "wood_planks", floorColor1: [198, 146, 96], floorColor2: [182, 130, 82] },
    obby_sky: { bgTop: [38, 166, 242], bgBot: [219, 240, 255], floorY: null, floorStyle: "studio_grid", floorColor1: [241, 245, 249], floorColor2: [226, 232, 240] },
    street: { bgTop: [147, 197, 253], bgBot: [226, 232, 240], floorY: -0.86, floorStyle: "asphalt_street", floorColor1: [64, 76, 94], floorColor2: [51, 65, 85] },
    hotel_corridor: { bgTop: [24, 24, 38], bgBot: [58, 40, 32], floorY: -0.86, floorStyle: "hotel_carpet", floorColor1: [120, 53, 15], floorColor2: [96, 42, 12] },
    lava_bridge: { bgTop: [249, 115, 22], bgBot: [254, 215, 170], floorY: -1.04, floorStyle: "molten_lava", floorColor1: [239, 68, 68], floorColor2: [249, 115, 22] },
    sand_court: { bgTop: [52, 211, 153], bgBot: [254, 243, 199], floorY: -0.86, floorStyle: "sand_court", floorColor1: [234, 198, 138], floorColor2: [218, 180, 118] }
  }[backdrop] || {
    bgTop: camSpec.bgTop || [147, 197, 253],
    bgBot: camSpec.bgBot || [241, 245, 249],
    floorY: camSpec.floorY === undefined ? -0.86 : camSpec.floorY,
    floorStyle: camSpec.floorStyle || "studio_grid",
    floorColor1: camSpec.floorColor1 || [182, 194, 210],
    floorColor2: camSpec.floorColor2 || [168, 182, 198]
  };

  return {
    ro,
    ta,
    fov,
    phase,
    bgTop: camSpec.bgTop || stageTheme.bgTop,
    bgBot: camSpec.bgBot || stageTheme.bgBot,
    floorY: camSpec.floorY !== undefined ? camSpec.floorY : stageTheme.floorY,
    floorStyle: camSpec.floorStyle || stageTheme.floorStyle,
    floorColor1: camSpec.floorColor1 || stageTheme.floorColor1,
    floorColor2: camSpec.floorColor2 || stageTheme.floorColor2
  };
}

export function computeEpisodeTimingPlan(specData = {}) {
  const shots = Array.isArray(specData.shots) && specData.shots.length > 0 ? specData.shots : [{}];
  const explicitClipSec = Number(specData.clipSecPerShot) || 0;
  const sumShotSec = shots.reduce((acc, s) => acc + (Number(s.durationSec) || 0), 0);
  const targetTotalSec =
    explicitClipSec > 0
      ? shots.length * explicitClipSec
      : Number(specData.durationSeconds) || (sumShotSec > 0 ? sumShotSec : shots.length * 3.75);
  const fallbackShotSec = targetTotalSec / shots.length;
  const rawDurations = shots.map((s) => (explicitClipSec > 0 ? explicitClipSec : Number(s.durationSec) || fallbackShotSec));
  const rawSum = rawDurations.reduce((a, b) => a + b, 0) || targetTotalSec;
  const scaleSec = explicitClipSec > 0 || !specData.durationSeconds ? 1 : targetTotalSec / rawSum;
  const shotDurations = rawDurations.map((d) => Number((d * scaleSec).toFixed(3)));
  const totalDurationSec = shotDurations.reduce((a, b) => a + b, 0);

  let shotFrameCounts;
  if (specData.framesPerShot) {
    const baseFrames = clamp(Number(specData.framesPerShot), 4, 24);
    const avgSec = totalDurationSec / shots.length;
    shotFrameCounts = shotDurations.map((d) => Math.max(4, Math.round((d / avgSec) * baseFrames)));
  } else {
    const sampleFps = clamp(Number(specData.sampleFps) || (totalDurationSec > 20 ? 2.4 : 3.2), 2, 12);
    shotFrameCounts = shotDurations.map((d) => Math.max(4, Math.round(d * sampleFps)));
  }
  const totalFrames = shotFrameCounts.reduce((a, b) => a + b, 0);
  const inFps = Number((totalFrames / totalDurationSec).toFixed(4));
  return { shotDurations, totalDurationSec, shotFrameCounts, totalFrames, inFps };
}

function projectHeadToCardBubble(worldPos, cam) {
  const headAbove = v3(worldPos.x, worldPos.y + 1.10, worldPos.z);
  const fw = norm3(sub3(cam.ta, cam.ro));
  const rt = norm3(cross3(fw, v3(0, 1, 0)));
  const up = cross3(rt, fw);
  const rel = sub3(headAbove, cam.ro);
  const vz = Math.max(0.35, dot3(rel, fw));
  const fov = cam.fov || 1.9;
  const nx = (dot3(rel, rt) / vz) * fov;
  const ny = (dot3(rel, up) / vz) * fov;
  const aspect = 312 / 554;
  const bx = clamp(Math.round(6 + 312 * 0.5 * (1 + nx / aspect)), 78, 246);
  const by = clamp(Math.round(6 + 554 * 0.5 * (1 - ny) - 22), 20, 124);
  return { bubbleX: bx, bubbleY: by };
}

const BACKDROP_LANDMARKS = {
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

function parseBodyAttitudeRad(att = "") {
  const s = String(att || "").toLowerCase();
  if (!s) return 0;
  const degMatch = s.match(/([0-9]+(?:\.[0-9]+)?)\s*(?:deg|degrees?)/);
  const deg = degMatch ? Number(degMatch[1]) : 8;
  const rad = (deg * Math.PI) / 180;
  if (s.includes("lean-forward") || s.includes("forward-lean")) return rad;
  if (s.includes("recoil") || s.includes("lean-back")) return -rad;
  return 0;
}

function resolveStageTargetMap(shot = {}, specData = {}, actorMotById = new Map(), backdrop = "studio", cam = {}, phase = 0.5) {
  const map = new Map();
  map.set("camera", cam.ro || v3(0, 0.36, 3.18));
  map.set("viewer", cam.ro || v3(0, 0.36, 3.18));

  const bMarks = BACKDROP_LANDMARKS[backdrop] || {};
  for (const [k, arr] of Object.entries(bMarks)) {
    map.set(k, vecFromArr(arr));
  }
  if (Array.isArray(specData.stageTargets)) {
    for (const st of specData.stageTargets) {
      if (st && st.id && Array.isArray(st.pos)) {
        map.set(st.id, vecFromArr(st.pos));
      }
    }
  }
  if (Array.isArray(shot.props)) {
    for (const pr of shot.props) {
      if (!pr) continue;
      const p0 = vecFromArr(pr.pos, v3(0, -0.3, 0.4));
      const p1 = pr.moveTo ? vecFromArr(pr.moveTo, p0) : p0;
      const center = lerpVec(p0, p1, smoothstep(0, 1, phase));
      if (pr.id) map.set(pr.id, center);
      if (pr.type && !map.has(pr.type)) map.set(pr.type, center);
    }
  }
  for (const [aid, mot] of actorMotById.entries()) {
    map.set(aid, v3(mot.pos.x, mot.pos.y + 0.65, mot.pos.z));
  }
  return map;
}

function applyActingAndInteractionToMotion(ac = {}, isLeadActor = false, baseMot = {}, shot = {}, targetMap = new Map(), phase = 0.5) {
  const mot = { ...baseMot, gazeX: 0, gazeY: 0, brows: ac.brows || "" };
  const perf = isLeadActor && shot.performance && typeof shot.performance === "object" ? shot.performance : null;

  if (!mot.brows && perf?.eyebrows) {
    mot.brows = perf.eyebrows;
  }
  if (perf?.bodyAttitude && ac.pose !== "faceplant" && ac.pose !== "hang_strap") {
    mot.waistPitch += parseBodyAttitudeRad(perf.bodyAttitude);
  }

  // 1. Pupil Gaze + Subtle Head Micro-Turn (cheated to camera so 2D face stays readable!)
  const gazeObj = ac.gaze && typeof ac.gaze === "object" ? ac.gaze : null;
  const targetId = gazeObj?.targetId || (typeof ac.gaze === "string" ? ac.gaze : "") || (perf?.gazeTarget || "");
  if (gazeObj && (gazeObj.horizontal !== undefined || gazeObj.vertical !== undefined)) {
    mot.gazeX = clamp(Number(gazeObj.horizontal) || 0, -1, 1);
    mot.gazeY = clamp(Number(gazeObj.vertical) || 0, -1, 1);
  } else if (targetId && targetId !== ac.castId && targetMap.has(targetId)) {
    const tgt = targetMap.get(targetId);
    const headWorld = v3(mot.pos.x, mot.pos.y + 0.75, mot.pos.z);
    const relLocal = rotY(sub3(tgt, headWorld), -mot.yaw);
    const forwardRef = Math.max(0.65, Math.abs(relLocal.z));
    mot.gazeX = clamp(relLocal.x / Math.hypot(relLocal.x, forwardRef), -0.95, 0.95);
    mot.gazeY = clamp(relLocal.y / 1.15, -0.85, 0.85);
    if (ac.pose !== "head_turn" && ac.headYaw === undefined) {
      mot.headYaw += clamp(mot.gazeX * 0.24, -0.28, 0.28);
    }
    if (ac.headPitch === undefined && ac.pose !== "faceplant") {
      mot.headPitch += clamp(-mot.gazeY * 0.14, -0.18, 0.18);
    }
  }

  // 2. Executable Hand-Prop Interaction Semantics (hold | present | tap | slam | point | drop | receive)
  const inter = ac.interaction || (shot.interaction && (!shot.interaction.actorId || shot.interaction.actorId === ac.castId) ? shot.interaction : null);
  if (inter && ac.pose !== "hang_strap" && ac.pose !== "faceplant") {
    const hand = String(inter.hand || "right").toLowerCase();
    const intent = String(inter.intent || "hold").toLowerCase();
    let targetPitch = null;
    if (intent === "point") targetPitch = 1.42;
    else if (intent === "present") targetPitch = 1.18;
    else if (intent === "hold" || intent === "receive") targetPitch = 1.06;
    else if (intent === "tap") targetPitch = mix(1.34, 0.96, smoothstep(0.15, 0.75, phase));
    else if (intent === "slam") targetPitch = mix(2.05, 0.82, smoothstep(0.10, 0.70, phase));
    else if (intent === "drop") targetPitch = mix(1.18, 0.62, smoothstep(0.20, 0.80, phase));

    if (targetPitch !== null) {
      if (hand === "left" || hand === "both") mot.armLPitch = targetPitch;
      if (hand === "right" || hand === "both") mot.armRPitch = targetPitch;
    }
  }

  return mot;
}

function resolveSignatureActingPose(castEntry = {}, idx = 0) {
  const perf = castEntry.performanceDNA || {};
  const sigGaze = String(perf.signatureGaze || "").toLowerCase();
  const sigGest = String(perf.signatureGesture || "").toLowerCase();
  const temp = String(perf.defaultTemperament || "").toLowerCase();

  const gazeDir = idx % 2 === 0 ? 0.78 : -0.65;
  const gazeX = sigGaze.includes("blank") || sigGaze.includes("calm") ? gazeDir * 0.35 : gazeDir;
  const brows =
    temp.includes("unbothered") || temp.includes("deadpan")
      ? "flat"
      : idx % 2 === 0
      ? "left-up-right-down"
      : "right-up-left-down";
  const expression =
    castEntry.defaultFace === "deadpan" || temp.includes("deadpan")
      ? "deadpan"
      : temp.includes("eager") || temp.includes("anxious") || temp.includes("panic")
      ? "shocked"
      : temp.includes("overconfident")
      ? "smirk"
      : castEntry.defaultFace || "grin";

  let armLPitch = -0.15;
  let armRPitch = 1.15;
  let waistPitch = 0.10;
  let legLPitch = 0;
  let legRPitch = 0;
  let posY = 0;

  if (sigGest.includes("sit")) {
    posY = -0.16;
    legLPitch = 1.48;
    legRPitch = 1.48;
    armLPitch = 0.22;
    armRPitch = 0.22;
    waistPitch = 0;
  } else if (sigGest.includes("both")) {
    armLPitch = 1.18;
    armRPitch = 1.18;
  } else if (sigGest.includes("lean-forward")) {
    waistPitch = 0.15;
    armRPitch = 1.32;
    legLPitch = 0.25;
    legRPitch = -0.25;
  }

  return {
    pos: v3(0, posY, 0),
    yaw: idx % 2 === 0 ? 0.24 : -0.22,
    headYaw: clamp(gazeX * 0.22, -0.24, 0.24),
    waistPitch,
    armLPitch,
    armRPitch,
    legLPitch,
    legRPitch,
    expression,
    gazeX,
    gazeY: -0.12,
    brows
  };
}

export function buildDeclarativeEpisodeBuilder(specData = {}) {
  const castList = Array.isArray(specData.cast) && specData.cast.length > 0
    ? specData.cast
    : [{ id: "hero", name: "Hero", archetype: "chibi-plush", theme3d: "theo" }];
  const castEntries = castList.map((c, idx) => {
    const id = c.id || `cast_${idx}`;
    const vis = c.visualDNA && typeof c.visualDNA === "object" ? c.visualDNA : {};
    const perf = c.performanceDNA && typeof c.performanceDNA === "object" ? c.performanceDNA : {};
    const noAcc = Boolean(vis.noAccessories ?? c.noAccessories);
    return {
      id,
      name: c.name || id,
      rig: vis.rig || c.rig || specData.rig || "r6",
      theme: mapArchetypeTo3DTheme(vis.archetype || c.archetype, vis.theme3d || c.theme3d || c.theme),
      customPalette: vis.customPalette || c.customPalette || null,
      noAccessories: noAcc,
      defaultFace: vis.face || c.face || "smile",
      defaultBackProp: noAcc ? null : vis.backProp || c.backProp || null,
      performanceDNA: perf
    };
  });
  const castMap = new Map(castEntries.map((e) => [e.id, e]));
  const primaryCast = castEntries[0];

  const buildShotScene = (shotIdx, phase = 0.5) => {
    const shot = specData.shots[clamp(shotIdx, 0, specData.shots.length - 1)] || {};
    const backdrop = shot.backdrop || specData.backdrop || "studio";
    const cam = resolveDeclarativeCamera(shot, backdrop, phase);

    // Normalize actors[] (or shorthand pose3d from custom_story_spec.json)
    let actors = Array.isArray(shot.actors) ? shot.actors : null;
    if (!actors) {
      const cArr = Array.from(castMap.entries());
      if (cArr.length >= 2) {
        actors = [
          {
            castId: cArr[0][0],
            pos: [-0.52, 0, 0.08],
            yaw: 0.25,
            pose: shot.pose3d?.primary || "idle",
            expression: shot.expressionPrimary || cArr[0][1].defaultFace
          },
          {
            castId: cArr[1][0],
            pos: [0.58, 0, -0.05],
            yaw: -0.22,
            pose: shot.pose3d?.secondary || "idle",
            expression: shot.expressionSecondary || cArr[1][1].defaultFace
          }
        ];
      } else {
        actors = [
          {
            castId: cArr[0][0],
            pos: [0, 0, 0.05],
            yaw: 0.12,
            pose: shot.pose3d?.primary || "idle",
            expression: shot.expressionPrimary || cArr[0][1].defaultFace
          }
        ];
      }
    }

    const props = Array.isArray(shot.props) ? shot.props : [];
    const blocks = Array.isArray(shot.blocks) ? shot.blocks : [];

    // Precompute actor base motions & 3D stage targets so every actor's pupil gaze & interaction resolve deterministically
    const baseMotList = actors.map((ac) => resolveActorMotion(ac, phase));
    const actorMotById = new Map();
    actors.forEach((ac, idx) => {
      if (ac.castId) actorMotById.set(ac.castId, baseMotList[idx]);
    });
    const targetMap = resolveStageTargetMap(shot, specData, actorMotById, backdrop, cam, phase);
    const resolvedActors = actors.map((ac, idx) => ({
      ac,
      mot: applyActingAndInteractionToMotion(ac, idx === 0, baseMotList[idx], shot, targetMap, phase)
    }));

    const leadMot = resolvedActors.length > 0 ? resolvedActors[0].mot : { pos: v3(0, 0, 0) };
    const autoBubble = projectHeadToCardBubble(leadMot.pos, cam);

    return {
      cam,
      autoBubble,
      sceneFn: (p) => {
        const hit = new SceneHit();
        for (const { ac, mot } of resolvedActors) {
          const castDef = castMap.get(ac.castId) || primaryCast;
          hit.merge(
            evalAvatarSDF(p, {
              ...mot,
              theme: ac.theme ? mapArchetypeTo3DTheme(ac.theme, ac.theme) : castDef.theme,
              customPalette: ac.customPalette || castDef.customPalette,
              noAccessories: ac.noAccessories !== undefined ? Boolean(ac.noAccessories) : castDef.noAccessories,
              expression: ac.expression || shot.expressionPrimary || castDef.defaultFace || "smile",
              handPropL: ac.handPropL || null,
              handPropR: ac.handPropR || null,
              backProp: ac.backProp !== undefined ? ac.backProp : castDef.defaultBackProp
            })
          );
        }
        addDeclarativeBackdrop(hit, p, backdrop, phase);
        for (const pr of props) {
          addDeclarativeProp(hit, p, pr, phase);
        }
        for (const blk of blocks) {
          const b0 = vecFromArr(blk.pos, v3(0, 0, 0));
          const b1 = blk.moveTo ? vecFromArr(blk.moveTo, b0) : b0;
          const bc = lerpVec(b0, b1, phase);
          let qb = sub3(p, bc);
          if (Array.isArray(blk.rot)) {
            if (blk.rot[1]) qb = rotY(qb, blk.rot[1]);
            if (blk.rot[0]) qb = rotX(qb, blk.rot[0]);
            if (blk.rot[2]) qb = rotZ(qb, blk.rot[2]);
          }
          const sz = vecFromArr(blk.size, v3(0.2, 0.2, 0.2));
          if (len3(qb) - (len3(sz) + 0.15) > hit.d) continue;
          const col = Array.isArray(blk.color) ? blk.color : [226, 232, 240];
          const rough = blk.roughness ?? 0.28;
          if (blk.shape === "sphere") {
            hit.add(sdSphere(qb, sz.x), col, rough, 95);
          } else if (blk.shape === "cylinder") {
            hit.add(sdRoundedCylinder(qb, sz.x, blk.bevel ?? 0.015, sz.y), col, rough, 95);
          } else {
            hit.add(sdRoundBox(qb, sz, blk.bevel ?? 0.02), col, rough, 95);
          }
        }
        return hit;
      }
    };
  };

  return { primaryCast, castEntries, buildShotScene };
}

export function buildEpisodeWavBuffer(shots = [], shotDurationsOrScalar = 2.0) {
  const sampleRate = 22050;
  const durations = Array.isArray(shotDurationsOrScalar)
    ? shotDurationsOrScalar
    : shots.map(() => Number(shotDurationsOrScalar) || 2.0);
  const totalSec = Math.max(2, durations.reduce((a, b) => a + b, 0));
  const numSamples = Math.floor(sampleRate * totalSec);
  const pcm = new Int16Array(numSamples);

  let cursorSec = 0;
  for (let s = 0; s < shots.length; s++) {
    const durSec = durations[s] || 2.0;
    const cue = (shots[s].sfxCue || (s === shots.length - 1 ? "win" : s === 0 ? "chime" : "boing")).toLowerCase();
    const startSample = Math.floor(cursorSec * sampleRate);
    const shotSamples = Math.floor(durSec * sampleRate);
    cursorSec += durSec;

    for (let i = 0; i < shotSamples && startSample + i < numSamples; i++) {
      const t = i / sampleRate;
      let val = 0;
      // Subtle upbeat background synth pulse
      const beatT = t % 0.5;
      val += Math.sin(2 * Math.PI * 165 * t) * Math.exp(-beatT * 9) * 0.12;

      if (cue === "boing" && t < 0.45) {
        const f = 260 + 420 * (t / 0.45);
        val += Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 6) * 0.45;
      } else if (cue === "chime" && t < 0.5) {
        const f = t < 0.16 ? 587.33 : 880.0;
        val += Math.sin(2 * Math.PI * f * t) * Math.exp(-((t % 0.16) * 8)) * 0.42;
      } else if (cue === "clack" && t < 0.18) {
        val += (Math.sin(2 * Math.PI * 920 * t) + Math.sin(2 * Math.PI * 410 * t)) * Math.exp(-t * 24) * 0.45;
      } else if (cue === "siren" && t < 1.4) {
        const f = Math.floor(t * 4) % 2 === 0 ? 660 : 520;
        val += Math.sin(2 * Math.PI * f * t) * 0.28;
      } else if (cue === "buzz" && t < 0.55) {
        val += (Math.sin(2 * Math.PI * 140 * t) > 0 ? 0.35 : -0.35) * Math.exp(-t * 4);
      } else if (cue === "drop" && t < 0.75) {
        const f = Math.max(110, 680 - 680 * (t / 0.75));
        val += Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 3) * 0.42;
      } else if (cue === "win" && t < 0.85) {
        const notes = [523.25, 659.25, 783.99, 1046.5];
        const nIdx = Math.min(3, Math.floor(t / 0.16));
        val += Math.sin(2 * Math.PI * notes[nIdx] * t) * Math.exp(-((t % 0.16) * 5)) * 0.44;
      } else if (t < 0.35) {
        val += Math.sin(2 * Math.PI * 640 * t) * Math.exp(-t * 10) * 0.38;
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
  header.writeUInt16LE(1, 20); // PCM
  header.writeUInt16LE(1, 22); // Mono
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(sampleRate * 2, 28);
  header.writeUInt16LE(2, 32);
  header.writeUInt16LE(16, 34);
  header.write("data", 36);
  header.writeUInt32LE(byteLen, 40);
  return Buffer.concat([header, Buffer.from(pcm.buffer)]);
}

function renderCustomSpecShard(specPath, rawDir, force, shardIdx, shardCount, outDir = "") {
  const specData = JSON.parse(fs.readFileSync(specPath, "utf8").replace(/^\uFEFF/, ""));
  const { primaryCast, castEntries, buildShotScene } = buildDeclarativeEpisodeBuilder(specData);
  const { shotFrameCounts } = computeEpisodeTimingPlan(specData);
  const prefix = (specData.slug || path.basename(specPath, path.extname(specPath)) || "episode").replace(/[^a-z0-9_-]/gi, "_");

  fs.mkdirSync(rawDir, { recursive: true });
  const avatarsDir = outDir ? path.join(outDir, "avatars") : path.join(rawDir, "avatars");
  fs.mkdirSync(avatarsDir, { recursive: true });

  let taskCounter = 0;
  const writePngTo = (targetDir, name, w, h, computeFn) => {
    const myTask = taskCounter++;
    if (myTask % shardCount !== shardIdx) return;
    const outPath = path.join(targetDir, name);
    if (!force && fs.existsSync(outPath) && fs.statSync(outPath).size > 1000) return;
    fs.writeFileSync(outPath, encodePNG(w, h, computeFn()));
  };
  const writePng = (name, w, h, computeFn) => writePngTo(rawDir, name, w, h, computeFn);

  const studioCam = {
    ro: v3(0, 0.22, 2.75),
    ta: v3(0, 0.04, 0),
    fov: 1.95,
    bgTop: [219, 234, 254],
    bgBot: [241, 245, 249],
    floorY: -0.86,
    floorStyle: "studio_grid",
    floorColor1: [182, 194, 210],
    floorColor2: [168, 182, 198]
  };

  const portraitCam = {
    ro: v3(0.08, 0.72, 1.48),
    ta: v3(0, 0.66, 0),
    fov: 2.08,
    bgTop: [224, 242, 254],
    bgBot: [248, 250, 252],
    floorY: null
  };

  // 1. Geometry Sheet views (Front 0°, 3/4 45°, Profile 90°)
  for (const [fname, yaw] of [
    ["turn_front.png", 0.0],
    ["turn_3q.png", 0.68],
    ["turn_side.png", 1.52]
  ]) {
    writePng(fname, 420, 520, () =>
      render3DViewport(
        420,
        520,
        (p) =>
          evalAvatarSDF(p, {
            yaw,
            theme: primaryCast.theme,
            customPalette: primaryCast.customPalette,
            noAccessories: primaryCast.noAccessories,
            expression: primaryCast.defaultFace || "smile",
            backProp: primaryCast.defaultBackProp
          }),
        studioCam
      )
    );
  }

  // 2. Cast Acting Sheet cells + 256x256 Avatar Crops (Identity + Signature Acting Moment)
  castEntries.forEach((ce, idx) => {
    const actPose = resolveSignatureActingPose(ce, idx);
    writePng(`cast_acting_${idx}.png`, 380, 460, () =>
      render3DViewport(
        380,
        460,
        (p) =>
          evalAvatarSDF(p, {
            ...actPose,
            theme: ce.theme,
            customPalette: ce.customPalette,
            noAccessories: ce.noAccessories,
            backProp: ce.defaultBackProp
          }),
        studioCam
      )
    );
    const safeId = String(ce.id || `cast_${idx}`).replace(/[^a-z0-9_-]/gi, "_");
    writePngTo(avatarsDir, `${safeId}_avatar.png`, 256, 256, () =>
      render3DViewport(
        256,
        256,
        (p) =>
          evalAvatarSDF(p, {
            ...actPose,
            pos: v3(0, 0, 0),
            waistPitch: 0.05,
            theme: ce.theme,
            customPalette: ce.customPalette,
            noAccessories: ce.noAccessories,
            backProp: ce.defaultBackProp
          }),
        portraitCam
      )
    );
  });

  const shotCount = specData.shots.length;
  for (let s = 0; s < shotCount; s++) {
    writePng(`${prefix}_shot_${s}.png`, 360, 640, () => {
      const { cam, sceneFn } = buildShotScene(s, 0.55);
      return render3DViewport(360, 640, sceneFn, cam);
    });
  }

  let frameIdx = 0;
  for (let s = 0; s < shotCount; s++) {
    const countForShot = shotFrameCounts[s];
    for (let f = 0; f < countForShot; f++) {
      const phase = (f + 0.5) / countForShot;
      const idx = frameIdx++;
      writePng(`${prefix}_anim_${String(idx).padStart(4, "0")}.png`, 270, 480, () => {
        const { cam, sceneFn } = buildShotScene(s, phase);
        return render3DViewport(270, 480, sceneFn, { ...cam, maxSteps: 26 });
      });
    }
  }
}

const isMain = process.argv[1] && path.resolve(process.argv[1]).endsWith("render_preview.mjs");
if (isMain) {
  if (process.argv.includes("--help") || process.argv.includes("-h")) {
    console.log(`Usage:
  node scripts/render_preview.mjs --spec <episode.json> --out-dir <dir> [--workers <n>] [--force]
  node scripts/render_preview.mjs [--raw-dir <dir>] [--force] [--only <prefixes>] [--shots-only]

Render self-contained 3D Roblox-style turnaround sheets, 9:16 storyboard sheets, GIFs, and H.264 MP4 videos with audio.`);
    process.exit(0);
  }

  const getArg = (flag) => {
    const idx = process.argv.indexOf(flag);
    return idx !== -1 && process.argv[idx + 1] ? process.argv[idx + 1] : null;
  };

  const specArg = getArg("--spec");
  const outDirArg = getArg("--out-dir");
  const force = process.argv.includes("--force");
  const shardArg = getArg("--shard");

  // Mode 1: Direct Custom Episode 3D Video Render (--spec <episode.json> --out-dir <dir>)
  if (specArg) {
    const absSpec = path.resolve(specArg);
    if (!fs.existsSync(absSpec)) {
      console.error(`ERROR: Spec file not found: ${absSpec}`);
      process.exit(1);
    }
    const specData = JSON.parse(fs.readFileSync(absSpec, "utf8").replace(/^\uFEFF/, ""));
    if (!Array.isArray(specData.shots) || specData.shots.length === 0) {
      console.error(`ERROR: Spec file must contain a non-empty shots[] array`);
      process.exit(1);
    }

    const outDir = outDirArg ? path.resolve(outDirArg) : path.join(path.dirname(absSpec), "assets");
    const tmpRoot = getArg("--raw-dir") ? path.resolve(getArg("--raw-dir")) : path.join(outDir, ".render_tmp");

    if (shardArg) {
      const [sIdx, sTotal] = shardArg.split("/").map(Number);
      renderCustomSpecShard(absSpec, tmpRoot, force, sIdx, sTotal, outDir);
      process.exit(0);
    }

    fs.mkdirSync(outDir, { recursive: true });
    fs.mkdirSync(tmpRoot, { recursive: true });
    // Default to 2 workers per custom episode so multiple concurrent sessions never hit Windows heap limits
    const workers = clamp(Number(getArg("--workers")) || 2, 1, 6);
    await Promise.all(
      Array.from({ length: workers }, (_, i) => {
        return new Promise((resolve, reject) => {
          const args = [process.argv[1], "--spec", absSpec, "--out-dir", outDir, "--raw-dir", tmpRoot, "--shard", `${i}/${workers}`];
          if (force) args.push("--force");
          const child = spawn(process.execPath, args, { stdio: "inherit" });
          child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`Custom shard ${i} exited ${code}`))));
        });
      })
    );

    const slug = (specData.slug || path.basename(absSpec, path.extname(absSpec))).replace(/[^a-z0-9_-]/gi, "_");
    const { shotDurations, shotFrameCounts, totalFrames, inFps } = computeEpisodeTimingPlan(specData);
    const { castEntries, buildShotScene } = buildDeclarativeEpisodeBuilder(specData);
    const wavPath = path.join(tmpRoot, `${slug}_audio.wav`);
    fs.writeFileSync(wavPath, buildEpisodeWavBuffer(specData.shots, shotDurations));

    const customManifest = {
      rootDir: outDir,
      rawDir: tmpRoot,
      turnaround: {
        outZh: path.join(outDir, "turnaround_sheet.zh.png"),
        outEn: path.join(outDir, "turnaround_sheet.en.png"),
        outDefault: [path.join(outDir, "turnaround_sheet.png")],
        views: [
          { file: "turn_front.png", labelZh: "正面 0°", labelEn: "Front 0°" },
          { file: "turn_3q.png", labelZh: "斜侧 45°", labelEn: "3/4 View 45°" },
          { file: "turn_side.png", labelZh: "侧面 90°", labelEn: "Profile 90°" }
        ]
      },
      castActingSheet: {
        outZh: path.join(outDir, "cast_acting_sheet.zh.png"),
        outEn: path.join(outDir, "cast_acting_sheet.en.png"),
        outDefault: path.join(outDir, "cast_acting_sheet.png"),
        panels: castEntries.map((ce, idx) => {
          const momEn = ce.performanceDNA?.actingMomentEn || ce.performanceDNA?.defaultTemperament || "Signature acting moment";
          const momZh = ce.performanceDNA?.actingMomentZh || ce.performanceDNA?.defaultTemperament || "标志性瞬间表演";
          const trunc = (t, n) => (String(t).length > n ? `${String(t).slice(0, n - 1)}…` : String(t));
          return {
            file: `cast_acting_${idx}.png`,
            titleEn: `${ce.name} (${ce.rig})`,
            titleZh: `${ce.name} (${ce.rig})`,
            momentEn: trunc(momEn, 78),
            momentZh: trunc(momZh, 38)
          };
        })
      },
      drift: { panels: [{ file: "__skip__" }] },
      cases: [
        {
          prefix: slug,
          framePadWidth: 4,
          totalFrames,
          inFps,
          wavPath,
          sheetZh: path.join(outDir, "storyboard_sheet.zh.png"),
          sheetEn: path.join(outDir, "storyboard_sheet.en.png"),
          sheetDefault: path.join(outDir, "storyboard_sheet.png"),
          gifPath: path.join(outDir, `${slug}.gif`),
          mp4Path: path.join(outDir, `${slug}.mp4`),
          shots: specData.shots.map((sh, idx) => {
            const num = String(idx + 1).padStart(2, "0");
            const { autoBubble } = buildShotScene(idx, 0.55);
            return {
              frameCount: shotFrameCounts[idx],
              labelZh: sh.labelZh || `${num} · ${sh.role || `镜头 ${num}`}`,
              labelEn: sh.labelEn || `${num} · ${(sh.role || `Shot ${num}`).split("/")[0].trim()}`,
              chatZh: sh.chatEn || "",
              chatEn: sh.chatEn || "",
              bubbleX: sh.bubbleX ?? autoBubble.bubbleX,
              bubbleY: sh.bubbleY ?? autoBubble.bubbleY,
              savePath: path.join(outDir, `shot_${num}.png`)
            };
          })
        }
      ]
    };

    const manifestPath = path.join(tmpRoot, "boards_manifest.json");
    fs.writeFileSync(manifestPath, JSON.stringify(customManifest, null, 2), "utf8");
    const ps1Path = path.join(ROOT, "scripts", "compose_boards.ps1");
    if (process.platform === "win32" && fs.existsSync(ps1Path)) {
      execFileSync("powershell", ["-ExecutionPolicy", "Bypass", "-File", ps1Path, "-ManifestPath", manifestPath], {
        stdio: "inherit"
      });
    }
    if (!process.argv.includes("--keep-tmp")) {
      fs.rmSync(tmpRoot, { recursive: true, force: true });
    }
    console.log(`Rendered custom episode video: ${path.join(outDir, `${slug}.mp4`)}`);
    process.exit(0);
  }

  // Mode 2: Built-in Repository Showcase & Examples Render
  const rawDir = getArg("--raw-dir") ? path.resolve(getArg("--raw-dir")) : path.join(ROOT, "tmp", "raw_3d");
  const onlyPrefixes = getArg("--only") ? getArg("--only").split(",") : null;
  const shotsOnly = process.argv.includes("--shots-only");

  if (shardArg) {
    const [sIdx, sTotal] = shardArg.split("/").map(Number);
    renderRawPanelSet(rawDir, force, sIdx, sTotal, onlyPrefixes, shotsOnly);
    process.exit(0);
  }

  fs.mkdirSync(rawDir, { recursive: true });
  const workers = clamp(Number(getArg("--workers")) || 6, 1, 6);
  await Promise.all(
    Array.from({ length: workers }, (_, i) => {
      return new Promise((resolve, reject) => {
        const args = [process.argv[1], "--raw-dir", rawDir, "--shard", `${i}/${workers}`];
        if (force) args.push("--force");
        if (shotsOnly) args.push("--shots-only");
        if (onlyPrefixes) args.push("--only", onlyPrefixes.join(","));
        const child = spawn(process.execPath, args, { stdio: "inherit" });
        child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`Shard ${i} exited ${code}`))));
      });
    })
  );
  console.log(`Rendered raw 3D panel set into ${rawDir} using ${workers} parallel workers`);

  if (process.platform === "win32") {
    const manifestPath = path.join(ROOT, "tmp", "boards_manifest.json");
    fs.writeFileSync(manifestPath, JSON.stringify(buildBoardsManifest(rawDir), null, 2), "utf8");
    const ps1Path = path.join(ROOT, "scripts", "compose_boards.ps1");
    if (fs.existsSync(ps1Path)) {
      execFileSync("powershell", ["-ExecutionPolicy", "Bypass", "-File", ps1Path, "-ManifestPath", manifestPath], {
        stdio: "inherit"
      });
    }
  }
}
