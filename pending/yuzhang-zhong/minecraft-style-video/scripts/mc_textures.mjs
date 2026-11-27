/**
 * mc_textures.mjs
 * Authentic 16x16 & 8x8 Vanilla Minecraft (Jappa 1.14+) pixel-art texture & sprite matrices.
 * Zero external dependencies; deterministic nearest-neighbor texel lookup.
 */

const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);

function h2(x, y, seed = 1) {
  let n = (x * 374761393 + y * 668265263 + seed * 1442695041) | 0;
  n = ((n ^ (n >> 13)) * 1274126177) | 0;
  return ((n ^ (n >> 16)) >>> 0) / 4294967295;
}

function rgbAdd(c, d) {
  return [clamp(c[0] + d, 0, 255), clamp(c[1] + d, 0, 255), clamp(c[2] + d, 0, 255)];
}

// ---------- 1. Exact 16x16 Extruded Item & Particle Sprites ----------

// Authentic 16x16 Minecraft Diamond Pickaxe (row 0 = top, row 15 = bottom)
export const PICKAXE_16 = [
  "......bbbbbb....",
  ".....bDDDDHHb...",
  "....bDDHHDDHDb..",
  "....bDbbwbDDHDb.",
  "....bb.bWwbDDDb.",
  "......bWwb.bHDb.",
  ".....bWwb..bDDb.",
  "....bWwb...bDb..",
  "...bWwb....bb...",
  "..bWwb..........",
  ".bWwb...........",
  "bWwb............",
  "bwb.............",
  ".b..............",
  "................",
  "................"
];

// Authentic 16x16 Minecraft Diamond Sword (row 0 = top-right tip, row 15 = bottom-left pommel)
export const SWORD_16 = [
  ".............bbb",
  "............bDHb",
  "...........bDHDb",
  "..........bDHDb.",
  ".........bDHDb..",
  "........bDHDb...",
  ".......bDHDb....",
  "..bb..bDHDb.....",
  ".bDDbbDHDb......",
  "..bDDDDDb.......",
  "...bbDDb........",
  "..bWwbDDb.......",
  ".bWwb.bb........",
  "bbwb............",
  "bDb.............",
  "bb.............."
];

// Authentic 16x16 Minecraft Dropped Diamond Item (diamond.png)
export const DIAMOND_ITEM_16 = [
  "................",
  ".....bbbbbb.....",
  "...bbDDHHDDbb...",
  "..bDDHHHHHHDDb..",
  ".bDDHHWWWWDDHDb.",
  ".bDHHWWDDDDDHDb.",
  "bDDHWDDDDDDDHDdb",
  "bDHWDDDDDDDDHDdb",
  "bDDHDDDDDDDDDDdb",
  "bDDDDDDDDDDDdddb",
  ".bDDDDDDDDDdddb.",
  ".bDDDDDDDDdddb..",
  "..bbDDDDddddb...",
  "...bbddddddbb...",
  ".....bbbbbb.....",
  "................"
];

// Authentic 9x9 Minecraft Red Heart Particle (heart.png)
export const HEART_SPRITE_9 = [
  ".bb...bb.",
  "bRRb.bRRb",
  "bWHRbRRRRb".slice(0, 9), // keep exact 9 cols below
];
export const HEART_16 = [
  "................",
  "................",
  "...bbb...bbb....",
  "..bRRRb.bRRRb...",
  ".bRWWWRbRRRRRb..",
  ".bRWWRRRRRRRrb..",
  ".bRRRRRRRRRRrb..",
  "..bRRRRRRRRrb...",
  "...bRRRRRRrb....",
  "....bRRRRrb.....",
  ".....bRRrb......",
  "......brb.......",
  ".......b........",
  "................",
  "................",
  "................"
];

export function lookupItemSpriteColor(ch) {
  switch (ch) {
    case "b": return [18, 48, 54];    // dark teal/wood pixel border
    case "D": return [44, 214, 198];  // core diamond cyan
    case "H": return [164, 251, 242]; // diamond bright bevel
    case "W": return [236, 254, 255]; // white glint
    case "d": return [22, 138, 134];  // shaded diamond edge
    case "w": return [104, 72, 34];   // oak stick shadow
    case "R": return [235, 38, 52];   // heart red
    case "r": return [168, 20, 34];   // heart dark red
    default: return null;
  }
}
// Override 'W' inside stick zone handled via capital 'S' if needed; wait: in PICKAXE_16/SWORD_16 'W' is light oak stick!
export function lookupToolSpriteColor(ch) {
  switch (ch) {
    case "b": return [24, 38, 42];    // crisp dark pixel outline
    case "D": return [51, 224, 208];  // Mojang diamond cyan #33E0D0
    case "H": return [168, 252, 244]; // diamond highlight #A8FCF4
    case "d": return [20, 146, 140];  // diamond shadow #14928C
    case "W": return [156, 112, 54];  // oak handle highlight #9C7036
    case "w": return [108, 74, 34];   // oak handle shadow #6C4A22
    case "R": return [238, 42, 56];   // heart bright red
    case "r": return [162, 20, 32];   // heart shaded red
    default: return null;
  }
}

// ---------- 2. Authentic 16x16 Block Face Pixel Evaluators ----------
// Coordinates: ux in 0..15 (left->right), uy in 0..15 (bottom->top; row = 15 - uy from top)

// Stone (horizontal strata mottling like vanilla Jappa stone.png)
export function texStone16(ux, uy) {
  const r = h2((ux >> 1) + (uy % 3), uy, 11);
  const rFine = h2(ux, uy, 17);
  if (r < 0.22) return rgbAdd([110, 110, 114], (rFine - 0.5) * 10);
  if (r > 0.78) return rgbAdd([142, 142, 146], (rFine - 0.5) * 10);
  return rgbAdd([125, 125, 129], (rFine - 0.5) * 12);
}

// Stone Bricks (two 8px courses with staggered mortar, bright top-left bevel, dark bottom-right shadow)
export function texStoneBricks16(ux, uy) {
  const row = 15 - uy; // 0..15 top to bottom
  const inBottomCourse = row >= 8;
  const mortarX = inBottomCourse ? 8 : 0;
  if (row === 0 || row === 8 || ux === mortarX) {
    return [76, 76, 80]; // dark mortar groove
  }
  const localY = row % 8;
  const localX = (ux - mortarX + 16) % 16;
  if (localY === 1 || localX === 1) {
    return rgbAdd([154, 154, 158], (h2(ux, uy, 23) - 0.5) * 10); // top/left bevel highlight
  }
  if (localY === 7 || localX === 15) {
    return [98, 98, 103]; // bottom/right brick shadow
  }
  // Subtle crack in one brick
  if (inBottomCourse && ((ux === 3 && row === 11) || (ux === 4 && row === 12))) {
    return [88, 88, 92];
  }
  return texStone16(ux, uy);
}

// Cobblestone (distinct rounded dark-outlined pebbles for piston base & cave walls)
const COBBLE_MAP = [
  "ddddMMMMmmmmdddd",
  "dLLLmmmmLLLLmmmd",
  "dLLmmdddmLLLmmmd",
  "ddmmddMMddLLdddd",
  "mddddMLLMddmLLLm",
  "mLLLdmLLmdmLLLLm",
  "mLLmddmmddmLLmmm",
  "dmmmddddMMMMmmdd",
  "ddMMMMddMLLLdddd",
  "mLLLLLmddLLmdLLm",
  "mLLmmLmddmmdLLLm",
  "dmmddmdddddmLLmd",
  "ddddMMLLMMddmmdd",
  "dLLLmLLLLLMmddLd",
  "dLLmmmmmmLLmdLLd",
  "ddmmmmddddmmdddd"
];
export function texCobble16(ux, uy) {
  const ch = COBBLE_MAP[15 - uy][ux];
  const n = (h2(ux, uy, 31) - 0.5) * 10;
  if (ch === "d") return rgbAdd([82, 82, 86], n);
  if (ch === "L") return rgbAdd([150, 150, 154], n);
  if (ch === "M") return rgbAdd([130, 130, 134], n);
  return rgbAdd([112, 112, 116], n);
}

// Dirt & Grass Block (Jappa lush forest green top + irregular grass side overhang + warm dirt pebbles)
export function texDirt16(ux, uy) {
  const r = h2(ux, uy, 41);
  if (r < 0.14) return [104, 72, 46]; // dark root/soil speck
  if (r < 0.24) return [158, 114, 78]; // light pebble speck
  if (r > 0.88) return [124, 92, 68]; // grey-brown stone speck
  return rgbAdd([134, 96, 67], (r - 0.5) * 14);
}

export function texGrassTop16(ux, uy) {
  const r = h2(ux, uy, 53);
  const blade = h2(ux * 2, uy >> 1, 59);
  if (r < 0.20) return [92, 158, 58];
  if (r > 0.78 || blade > 0.82) return [124, 192, 78];
  return rgbAdd([109, 176, 68], (r - 0.5) * 10);
}

const GRASS_SIDE_LEN = [3, 5, 4, 2, 3, 6, 4, 3, 5, 3, 2, 4, 6, 5, 3, 4];
export function texGrassSide16(ux, uy) {
  const row = 15 - uy; // 0 at top
  const len = GRASS_SIDE_LEN[ux];
  if (row < len) {
    if (row === len - 1) return [78, 138, 48]; // darker grass tip shadow
    return texGrassTop16(ux, uy);
  }
  if (row === len) {
    // 1px dirt shadow directly under grass overhang!
    const d = texDirt16(ux, uy);
    return [d[0] - 20, d[1] - 16, d[2] - 12];
  }
  return texDirt16(ux, uy);
}

// Oak Planks (4 horizontal 4px-tall boards with staggered vertical joints and wood grain)
export function texOakPlanks16(ux, uy) {
  const row = 15 - uy;
  const board = row >> 2; // 0..3
  const jointX = [7, 13, 4, 11][board];
  if (row % 4 === 3 || ux === jointX) {
    return [122, 90, 52]; // plank seam shadow
  }
  const grain = h2((ux >> 2) + board * 5, row, 67);
  if (row % 4 === 0) return rgbAdd([186, 146, 92], (grain - 0.5) * 10);
  return rgbAdd([168, 130, 78], (grain - 0.5) * 14);
}

// Authentic 16x16 Diamond Ore (stone strata + 4 multi-shaded irregular diamond clusters)
const DIAMOND_ORE_MAP = [
  "................",
  "..........bb....",
  ".........bWHb...",
  "...bb....bDDdb..",
  "..bWHb....bbb...",
  "..bDDdb.........",
  "...bbb.....bb...",
  "..........bWDdb.",
  "....bbb...bDDdb.",
  "...bWHDb...bbb..",
  "...bDDDdb.......",
  "....bddd........",
  ".........bbb....",
  "........bWHDb...",
  "........bDDdb...",
  ".........bbb...."
];
export function texDiamondOre16(ux, uy) {
  const ch = DIAMOND_ORE_MAP[15 - uy][ux];
  if (ch === ".") return { col: texStone16(ux, uy), emissive: 0, rough: 0.46 };
  if (ch === "b") return { col: [20, 98, 104], emissive: 0.05, rough: 0.25 };
  if (ch === "d") return { col: [28, 168, 164], emissive: 0.35, rough: 0.14 };
  if (ch === "D") return { col: [74, 237, 217], emissive: 0.55, rough: 0.12 };
  if (ch === "H") return { col: [174, 252, 246], emissive: 0.65, rough: 0.10 };
  return { col: [236, 254, 255], emissive: 0.75, rough: 0.08 }; // 'W'
}

// Authentic Spiderweb Mining Crack Overlay (destroy_stage_0..9)
const CRACK_PATHS = [
  [7, 7, 1], [8, 8, 1],
  [6, 6, 2], [9, 7, 2], [7, 9, 2],
  [5, 5, 3], [10, 6, 3], [6, 10, 3], [8, 5, 3],
  [4, 5, 4], [11, 5, 4], [5, 11, 4], [9, 10, 4],
  [3, 4, 5], [12, 4, 5], [4, 12, 5], [10, 11, 5], [6, 3, 5],
  [2, 3, 6], [13, 3, 6], [3, 13, 6], [11, 12, 6], [5, 2, 6], [11, 8, 6]
];
export function hasMiningCrack(ux, uy, progress) {
  if (progress <= 0.05) return false;
  const stage = Math.ceil(progress * 6);
  for (const [cx, cy, s] of CRACK_PATHS) {
    if (s <= stage && cx === ux && cy === uy) return true;
  }
  return false;
}

// Authentic 16x16 TNT Block (top & side)
const TNT_SIDE_BAND = [
  "wwwwwwwwwwwwwwww", // row 5: top edge of white label
  "wTTTTwNwNwwTTTTw", // row 6 -> adjusted to exact 16 cols below!
];
const TNT_LETTERS_5X16 = [
  "wwwwwwwwwwwwwwww",
  "wTTTwNwwNwTTTTww",
  "wwTwwNNwNwwwTwww",
  "wwTwwNwNNwwwTwww",
  "wwTwwNwwNwwwTwww"
];
export function texTntTop16(ux, uy) {
  // 4x4 grid of dynamite stick tops with central gunpowder fuse
  if (ux >= 6 && ux <= 9 && uy >= 6 && uy <= 9) {
    if ((ux === 7 || ux === 8) && (uy === 7 || uy === 8)) return [212, 212, 216]; // white-grey fuse wick
    return [36, 36, 40]; // dark gunpowder ring
  }
  const sx = ux % 4;
  const sy = uy % 4;
  if (sx === 0 || sy === 0) return [148, 28, 24];
  if (sx === 2 && sy === 2) return [242, 112, 92]; // stick center highlight
  return [214, 46, 38];
}

export function texTntSide16(ux, uy) {
  const row = 15 - uy;
  if (row === 0 || row === 15) return [138, 32, 26];
  if (row >= 5 && row <= 9) {
    const ch = TNT_LETTERS_5X16[row - 5][ux];
    if (ch !== "w") return [24, 24, 28]; // crisp black TNT pixel font
    return ux % 4 === 0 ? [224, 226, 230] : [244, 245, 247];
  }
  if (row === 4 || row === 10) return [72, 48, 38]; // dark binding strap border
  // 4 vertical dynamite sticks (4px each: dark edge, highlight, mid red, shaded red)
  const mod = ux % 4;
  if (mod === 0) return [156, 28, 22];
  if (mod === 1) return [236, 68, 52];
  if (mod === 2) return [216, 44, 34];
  return [184, 34, 26];
}

// Authentic 16x16 Crafting Table (top 3x3 grid + front/side oak cabinet with pixel saw & hammer)
export function texCraftingTop16(ux, uy) {
  const row = 15 - uy;
  if (ux === 0 || ux === 15 || row === 0 || row === 15) return [92, 58, 32]; // dark oak rim
  if (ux === 1 || ux === 14 || row === 1 || row === 14) return [184, 138, 84]; // light oak inner rim
  // 3x3 grid inside [2..13] x [2..13]
  if (ux === 2 || ux === 6 || ux === 9 || ux === 13 || row === 2 || row === 6 || row === 9 || row === 13) {
    return [78, 48, 26]; // crisp 3x3 crafting grid lines
  }
  const n = (h2(ux, row, 73) - 0.5) * 10;
  return rgbAdd([156, 108, 62], n);
}

const CRAFT_SIDE_16 = [
  "dddddddddddddddd",
  "dRRRRddRRRRddRRd", // crimson-brown cloth top overhang!
  "dRRRRddRRRRddRRd",
  "dddddddddddddddd",
  "dppppSppppHHpppd",
  "dpppSSppppHHpppd",
  "dppSSWpppwwwwppd",
  "dppSWWppppwwpppd",
  "dpppWWppppwwpppd",
  "dpppWWppppwwpppd",
  "dppppWppppwwpppd",
  "dpppppppppwwpppd",
  "ddddppppppppdddd",
  "dppppppppppppppd",
  "dppppppppppppppd",
  "dddddddddddddddd"
];
export function texCraftingSide16(ux, uy) {
  const ch = CRAFT_SIDE_16[15 - uy][ux];
  const n = (h2(ux, uy, 79) - 0.5) * 10;
  if (ch === "d") return [74, 46, 24];          // dark oak frame
  if (ch === "R") return rgbAdd([138, 52, 44], n); // red-brown workbench top cloth
  if (ch === "S") return [92, 56, 28];          // saw wooden handle
  if (ch === "W") return [204, 212, 220];       // iron saw blade
  if (ch === "H") return [182, 190, 200];       // iron hammer head
  if (ch === "w") return [108, 72, 36];         // hammer wooden handle
  return texOakPlanks16(ux, uy);                // oak plank background
}

// Authentic 16x16 Sticky Piston (12px Cobblestone base + 4px Oak Wood plunger + 8x8 Slimeball top)
export function texPistonSide16(ux, uy) {
  const row = 15 - uy;
  if (row < 4) {
    // 4px wooden plunger plate with iron corner brackets
    if ((ux <= 1 || ux >= 14) && row >= 1 && row <= 2) return [156, 162, 170];
    if (row === 3) return [96, 68, 38];
    return rgbAdd([182, 138, 82], (h2(ux, row, 83) - 0.5) * 12);
  }
  return texCobble16(ux, uy);
}

export function texPistonTopSticky16(ux, uy) {
  if (ux === 0 || ux === 15 || uy === 0 || uy === 15) return [104, 74, 42];
  // Iron corner rivets
  if ((ux <= 2 || ux >= 13) && (uy <= 2 || uy >= 13)) return [148, 154, 162];
  // 8x8 Mottled Green Slimeball in center [4..11] x [4..11]
  if (ux >= 4 && ux <= 11 && uy >= 4 && uy <= 11) {
    if ((ux === 4 || ux === 11) && (uy === 4 || uy === 11)) {
      return rgbAdd([176, 134, 78], (h2(ux, uy, 89) - 0.5) * 10); // rounded corner of slime splat
    }
    const r = h2(ux, uy, 97);
    if (r < 0.25) return [94, 172, 62];
    if (r > 0.75) return [152, 232, 112];
    return [122, 204, 84];
  }
  return rgbAdd([178, 136, 80], (h2(ux, uy, 89) - 0.5) * 12);
}

// Authentic 16x16 Redstone Lamp (Dark obsidian-iron frame + corner lattice + glowing glowstone core)
const LAMP_MAP_16 = [
  "ffffffffffffffff",
  "fbbbbbbbbbbbbbbf",
  "fbbGGGGGGGGGGbbf",
  "fbGgbWWWWWWbgGbf",
  "fbGgWWWWWWWWgGbf",
  "fbGWWWWYYWWWWGbf",
  "fbGWWWYYYYWWWGbf",
  "fbGWWYYYYYYWWGbf",
  "fbGWWYYYYYYWWGbf",
  "fbGWWWYYYYWWWGbf",
  "fbGWWWWYYWWWWGbf",
  "fbGgWWWWWWWWgGbf",
  "fbGgbWWWWWWbgGbf",
  "fbbGGGGGGGGGGbbf",
  "fbbbbbbbbbbbbbbf",
  "ffffffffffffffff"
];
export function texRedstoneLamp16(ux, uy, lit = true) {
  const ch = LAMP_MAP_16[15 - uy][ux];
  if (ch === "f") return { col: [46, 32, 24], emissive: 0, rough: 0.45 };
  if (ch === "b") return { col: [72, 48, 32], emissive: 0, rough: 0.42 };
  if (!lit) {
    if (ch === "G" || ch === "g") return { col: [104, 68, 42], emissive: 0, rough: 0.38 };
    return { col: [134, 90, 54], emissive: 0, rough: 0.36 };
  }
  if (ch === "G" || ch === "g") return { col: [217, 138, 44], emissive: 0.45, rough: 0.2 };
  if (ch === "W") return { col: [251, 198, 72], emissive: 0.78, rough: 0.14 };
  return { col: [255, 246, 182], emissive: 0.95, rough: 0.1 }; // 'Y' hot center
}

// Authentic 16x16 Diamond Block (faceted bevel border + shiny cyan center)
export function texDiamondBlock16(ux, uy) {
  if (ux === 0 || ux === 15 || uy === 0 || uy === 15) return [28, 158, 152];
  if (ux === 1 || uy === 14) return [196, 253, 248];
  if (ux === 14 || uy === 1) return [36, 186, 178];
  const diag = (ux + uy) % 6;
  if (diag === 0) return [184, 252, 246];
  if (diag === 3) return [56, 218, 206];
  return [92, 242, 228];
}

// ---------- 3. Authentic Mob Textures (Creeper, Enderman, Pink Axolotl) ----------

// Exact 8x8 Mojang Creeper Face
export const CREEPER_FACE_8 = [
  "........", // iy=7 (top)
  "........", // iy=6
  ".XX..XX.", // iy=5: 2x2 eyes
  ".XX..XX.", // iy=4: 2x2 eyes
  "...XX...", // iy=3: 2x1 nose bridge
  "..XXXX..", // iy=2: 4px upper mouth!
  "..XXXX..", // iy=1: 4px lower mouth!
  "..X..X.."  // iy=0: 1px fangs at bottom edge!
];

export function texCreeperSkin(gx, gy, gz) {
  const r = h2(gx * 3 + gz, gy, 109);
  if (r < 0.16) return [186, 224, 178]; // signature pale white-green Creeper static pixel!
  if (r < 0.36) return [124, 198, 108]; // bright lime pixel
  if (r > 0.80) return [58, 128, 52];   // deep moss pixel
  return [88, 168, 76];                 // mid Creeper green
}
