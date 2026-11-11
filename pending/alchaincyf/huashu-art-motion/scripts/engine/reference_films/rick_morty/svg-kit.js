window.RM = (() => {
'use strict';
// 全局：画风常量、SVG 小工具、场景注册、确定性随机、纹理
const INK = '#222323', LW = 2.35;
const STILL = location.hash.includes('still');
const NS = 'http://www.w3.org/2000/svg';

function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// 字符串式 SVG 图元。o: {stroke, w, op, id, cls, extra}
function A(o) {
  let s = '';
  if (o.id) s += ` id="${o.id}"`;
  if (o.cls) s += ` class="${o.cls}"`;
  if (o.op != null) s += ` opacity="${o.op}"`;
  if (o.tf) s += ` transform="${o.tf}"`;
  if (o.extra) s += ' ' + o.extra;
  return s;
}
function SK(o) {
  const st = o.stroke === undefined ? INK : o.stroke;
  if (st === 'none' || st === null) return ' stroke="none"';
  return ` stroke="${st}" stroke-width="${o.w ?? LW}" stroke-linejoin="round" stroke-linecap="round"`;
}
const S = {
  poly: (pts, fill, o = {}) => `<polygon points="${pts}" fill="${fill}"${SK(o)}${A(o)}/>`,
  pl: (pts, o = {}) => `<polyline points="${pts}" fill="none"${SK(o)}${A(o)}/>`,
  path: (d, fill, o = {}) => `<path d="${d}" fill="${fill}"${SK(o)}${A(o)}/>`,
  rect: (x, y, w, h, fill, o = {}) => `<rect x="${x}" y="${y}" width="${w}" height="${h}"${o.rx ? ` rx="${o.rx}"` : ''} fill="${fill}"${SK(o)}${A(o)}/>`,
  circ: (cx, cy, r, fill, o = {}) => `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}"${SK(o)}${A(o)}/>`,
  ell: (cx, cy, rx, ry, fill, o = {}) => `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${fill}"${SK(o)}${A(o)}/>`,
  line: (x1, y1, x2, y2, o = {}) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"${SK(o)}${A(o)}/>`,
  g: (inner, o = {}) => `<g${A(o)}>${inner}</g>`,
  // 无描边填色（色块、阴影）
  fpoly: (pts, fill, o = {}) => S.poly(pts, fill, { ...o, stroke: 'none' }),
  fpath: (d, fill, o = {}) => S.path(d, fill, { ...o, stroke: 'none' }),
};

// 场景：分层。L0 建筑；L1 后墙物件；L2 按脚深度排序（家具与角色）；L3 光效与前景
const SCENE = {
  svg: null, defs: null, layers: {}, objs: [], updaters: [], t0: 0,
  init() {
    this.svg = document.getElementById('scene');
    this.svg.innerHTML = '<defs id="defs"></defs><g id="L0"></g><g id="L1"></g><g id="L2"></g><g id="L3"></g>';
    this.defs = this.svg.querySelector('#defs');
    for (const k of ['L0', 'L1', 'L2', 'L3']) this.layers[k] = this.svg.querySelector('#' + k);
  },
  def(s) { this.defs.insertAdjacentHTML('beforeend', s); },
  add(layer, s) { this.layers[layer].insertAdjacentHTML('beforeend', s); return this.layers[layer].lastElementChild; },
  // 深度物体：z = 脚／底座在地面上的 y
  addZ(id, z, s) {
    const g = document.createElementNS(NS, 'g'); g.id = id; g.dataset.z = z; g.innerHTML = s;
    this.layers.L2.appendChild(g); this.objs.push(g); return g;
  },
  sortZ() {
    const arr = [...this.layers.L2.children].sort((a, b) => (+a.dataset.z) - (+b.dataset.z));
    let ok = true; for (let i = 0; i < arr.length; i++) if (this.layers.L2.children[i] !== arr[i]) { ok = false; break; }
    if (!ok) arr.forEach(e => this.layers.L2.appendChild(e));
  },
  onUpdate(fn) { this.updaters.push(fn); },
};

// 斑驳纹理：值噪声 → 半透明 PNG，做 <pattern>。dark/light 两种。
function mottleURL(size, seed, cell, alpha, rgb) {
  const c = document.createElement('canvas'); c.width = c.height = size;
  const x = c.getContext('2d'); const img = x.createImageData(size, size);
  const r = mulberry32(seed);
  const octs = [cell, cell / 2, cell / 4].filter(v => v >= 1);
  const grids = octs.map(cs => { const n = Math.ceil(size / cs); return { cs, n, v: Array.from({ length: n * n }, r) }; });
  const sm = t => t * t * (3 - 2 * t);
  for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) {
    let v = 0, wsum = 0, wt = 1;
    for (const g of grids) {
      const gx = i / g.cs, gy = j / g.cs, x0 = Math.floor(gx), y0 = Math.floor(gy);
      const fx = sm(gx - x0), fy = sm(gy - y0);
      const at = (a, b) => g.v[((b % g.n + g.n) % g.n) * g.n + ((a % g.n + g.n) % g.n)];
      const a = at(x0, y0) * (1 - fx) + at(x0 + 1, y0) * fx, b = at(x0, y0 + 1) * (1 - fx) + at(x0 + 1, y0 + 1) * fx;
      v += (a * (1 - fy) + b * fy) * wt; wsum += wt; wt *= 0.55;
    }
    v /= wsum;
    const k = (j * size + i) * 4;
    img.data[k] = rgb[0]; img.data[k + 1] = rgb[1]; img.data[k + 2] = rgb[2];
    img.data[k + 3] = Math.max(0, Math.min(255, (v - 0.45) * 2.2 * alpha * 255));
  }
  x.putImageData(img, 0, 0); return c.toDataURL();
}
function mottlePattern(id, size, seed, cell, alpha, rgb) {
  SCENE.def(`<pattern id="${id}" patternUnits="userSpaceOnUse" width="${size}" height="${size}"><image href="${mottleURL(size, seed, cell, alpha, rgb)}" width="${size}" height="${size}"/></pattern>`);
}

const f1 = v => (Math.round(v * 10) / 10);
const P = pts => pts.map(p => f1(p[0]) + ' ' + f1(p[1]));

// Catmull-Rom → 三次贝塞尔。pts: [[x,y],...]
function smoothPath(pts, closed = true, k = 0.5) {
  const n = pts.length; if (n < 2) return '';
  const g = i => closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))];
  let d = `M${f1(pts[0][0])} ${f1(pts[0][1])}`;
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2);
    const c1 = [p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3];
    const c2 = [p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3];
    d += ` C${f1(c1[0])} ${f1(c1[1])} ${f1(c2[0])} ${f1(c2[1])} ${f1(p2[0])} ${f1(p2[1])}`;
  }
  return d + (closed ? ' Z' : '');
}
// 分段：sharp 里给出的下标处保持尖角（头发尖刺用）
function mixedPath(pts, sharp = new Set(), k = 0.5) {
  const n = pts.length; const g = i => pts[(i + n) % n];
  let d = `M${f1(pts[0][0])} ${f1(pts[0][1])}`;
  for (let i = 0; i < n; i++) {
    const p0 = g(i - 1), p1 = g(i), p2 = g(i + 1), p3 = g(i + 2);
    const k1 = sharp.has(i) ? 0 : k, k2 = sharp.has((i + 1) % n) ? 0 : k;
    const c1 = [p1[0] + (p2[0] - p0[0]) * k1 / 3, p1[1] + (p2[1] - p0[1]) * k1 / 3];
    const c2 = [p2[0] - (p3[0] - p1[0]) * k2 / 3, p2[1] - (p3[1] - p1[1]) * k2 / 3];
    d += ` C${f1(c1[0])} ${f1(c1[1])} ${f1(c2[0])} ${f1(c2[1])} ${f1(p2[0])} ${f1(p2[1])}`;
  }
  return d + ' Z';
}


return { S, INK, SCENE, mulberry32, mottlePattern, smoothPath, mixedPath, f1 };
})();
