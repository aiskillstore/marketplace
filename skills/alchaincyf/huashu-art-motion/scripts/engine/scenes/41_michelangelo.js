// 米开朗基罗（红粉笔人体习作＋「未完成」）：形体是雕出来的——光从左上来，肩胛、脊沟、背阔肌像石头一样有体积；用红粉笔沿形体走向排线，暗处交叉再压一层，边缘有断续的重轮廓；画面下端不收尾，像雕像还陷在粗石里。
// 题材（新构图，不搬名作）：一张旧素描纸，一个双臂举起、背身扭转的男子习作正在被一笔笔排线画出来；右侧是同一人翻转缩小的旧习作，角落有几行不成字的注记。
// 原作锚定（fetch_reference.py：《阿特拉斯奴隶》《利比亚女先知习作》《创造亚当》）：纸 #dfc79e 偏暖米黄带霉斑、红粉笔 #9c3f26（暗处 #6e2a1a）、亮处不画（留纸）、排线以斜 50° 为主＋沿形体转向、边缘粗而断续。
// 管线：形体图（灰度，用椭圆光暗叠出肌肉）→ 由明暗＋梯度方向生成确定性排线笔画 → 缓存成一张「已画完」的红粉笔层 → 按 y 从上到下揭示，笔尖（粉笔）跟着扫。
SCENES['41_michelangelo'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const FW = 720, FH = 860;                                       // 形体图局部坐标
  let paper, big, small, built = false;
  const smooth = (pts) => { const p = new Path2D(), n = pts.length, m = i => [(pts[i % n][0] + pts[(i + 1) % n][0]) / 2, (pts[i % n][1] + pts[(i + 1) % n][1]) / 2]; p.moveTo(...m(n - 1)); for (let i = 0; i < n; i++) p.quadraticCurveTo(pts[i][0], pts[i][1], ...m(i)); p.closePath(); return p; };
  const capsule = (pts, ws) => { const L = [], R = []; pts.forEach((p, i) => { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)], d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, nx = -(b[1] - a[1]) / d, ny = (b[0] - a[0]) / d; L.push([p[0] + nx * ws[i] / 2, p[1] + ny * ws[i] / 2]); R.push([p[0] - nx * ws[i] / 2, p[1] - ny * ws[i] / 2]); }); return smooth([...L, ...R.reverse()]); };
  // ---- 形体：剪影（各部件）与明暗 ----
  const parts = () => ({
    torso: smooth([[262, 188], [196, 206], [118, 238], [100, 280], [140, 340], [176, 410], [208, 490], [226, 565], [214, 640], [188, 716], [236, 792], [305, 804], [374, 792], [424, 716], [398, 640], [386, 565], [404, 490], [438, 410], [474, 340], [516, 280], [498, 238], [418, 206], [348, 188]]),
    armL: capsule([[132, 266], [34, 128], [28, 40], [112, 8]], [128, 104, 70, 44]), armR: capsule([[486, 262], [572, 124], [570, 40], [484, 14]], [128, 104, 70, 44]),
    head: smooth([[298, 22], [346, 36], [366, 84], [358, 128], [336, 160], [300, 176], [268, 168], [250, 150], [238, 128], [226, 114], [237, 100], [240, 70], [262, 36]]),
    neck: smooth([[250, 150], [352, 150], [392, 214], [222, 214]]),
  });
  const LIGHTS = [   // x, y, rx, ry, 明度, 浓度（光从左上）
    [300, 240, 112, 62, 0.98, 0.6], [212, 330, 66, 84, 1.0, 0.8], [398, 330, 62, 84, 0.86, 0.6], [214, 420, 64, 18, 0.15, 0.8], [398, 420, 60, 18, 0.12, 0.8], [170, 300, 70, 12, 0.18, 0.7], [250, 318, 10, 70, 0.2, 0.55],
    [305, 450, 11, 235, 0.12, 0.85], [266, 535, 30, 115, 1.0, 0.65], [346, 535, 30, 115, 0.8, 0.5], [162, 420, 38, 120, 0.22, 0.7], [452, 420, 40, 120, 0.1, 0.8],
    [205, 600, 28, 74, 0.2, 0.6], [405, 600, 26, 74, 0.1, 0.6], [248, 722, 78, 70, 1.0, 0.75], [364, 722, 78, 70, 0.7, 0.6], [305, 708, 7, 76, 0.1, 0.75],
    [132, 262, 62, 64, 1.0, 0.85], [150, 330, 14, 50, 0.15, 0.7], [488, 258, 60, 64, 0.5, 0.7], [468, 330, 14, 50, 0.1, 0.7],
    [96, 180, 40, 92, 1.0, 0.7], [64, 140, 20, 60, 0.2, 0.6], [532, 170, 40, 92, 0.42, 0.65], [566, 130, 20, 60, 0.15, 0.6],
    [78, 90, 28, 52, 0.95, 0.5], [522, 96, 28, 52, 0.38, 0.55],
    [270, 100, 34, 62, 1.0, 0.65], [340, 100, 30, 70, 0.28, 0.7], [338, 116, 10, 18, 0.1, 0.8], [300, 40, 66, 32, 0.28, 0.7], [270, 52, 18, 14, 0.2, 0.6], [330, 50, 20, 14, 0.15, 0.6],
    [160, 345, 12, 70, 0.15, 0.7], [452, 345, 12, 70, 0.1, 0.7], [180, 470, 8, 38, 0.2, 0.6], [196, 500, 8, 34, 0.2, 0.6], [212, 530, 8, 30, 0.2, 0.6], [430, 470, 8, 38, 0.1, 0.7], [414, 500, 8, 34, 0.1, 0.7], [398, 530, 8, 30, 0.1, 0.7],
    [240, 655, 14, 10, 0.12, 0.8], [370, 655, 14, 10, 0.1, 0.8], [215, 290, 70, 14, 0.2, 0.6], [395, 290, 66, 14, 0.15, 0.6], [150, 215, 70, 24, 0.95, 0.5], [300, 300, 140, 24, 0.95, 0.4],
    [305, 188, 56, 28, 0.3, 0.6], [270, 176, 10, 40, 0.2, 0.6], [345, 176, 10, 40, 0.15, 0.6],
  ];
  const twist = y => 30 * Math.sin((y - 60) / 780 * Math.PI * 1.15 - 0.4) - 6;                    // 肩胛带与骨盆反向偏移：S 形扭转
  function warp(cv, bg) { const o = P.canvas(FW, FH), g = o.getContext('2d'); if (bg) { g.fillStyle = bg; g.fillRect(0, 0, FW, FH); } for (let y = 0; y < FH; y++) g.drawImage(cv, 0, y, FW, 1, twist(y), y, FW, 1); return o; }
  function formMap() {
    const cv = P.canvas(FW, FH), g = cv.getContext('2d'), pt = parts(); g.fillStyle = '#fff'; g.fillRect(0, 0, FW, FH); g.translate(60, 40);
    const body = new Path2D(); Object.values(pt).forEach(p => body.addPath(p));
    g.save(); g.clip(body); g.fillStyle = '#d4d4d4'; g.fillRect(0, 0, FW, FH);
    LIGHTS.forEach(([x, y, rx, ry, v, a]) => { g.save(); g.translate(x, y); g.scale(rx, ry); const gr = g.createRadialGradient(0, 0, 0, 0, 0, 1), c = Math.round(v * 255); gr.addColorStop(0, `rgba(${c},${c},${c},${a})`); gr.addColorStop(1, `rgba(${c},${c},${c},0)`); g.fillStyle = gr; g.beginPath(); g.arc(0, 0, 1, 0, TAU); g.fill(); g.restore(); });
    g.filter = 'blur(7px)'; g.strokeStyle = 'rgba(40,40,40,.55)'; g.lineWidth = 16; Object.values(pt).forEach(p => g.stroke(p)); g.filter = 'none';        // 边缘遮挡：体积感
    g.restore();
    const wcv = warp(cv, '#fff'), mk = P.canvas(FW, FH), mg = mk.getContext('2d'); mg.translate(60, 40); mg.fillStyle = '#000'; Object.values(pt).forEach(p => mg.fill(p));
    return { cv: wcv, pt, body, mask: warp(mk) };
  }
  // ---- 排线：明暗→笔画；亮处留纸，中调单向斜线，暗处交叉；笔向在斜 50° 与形体等高线之间混合 ----
  function hatch(f, seed) {
    const g = f.cv.getContext('2d'), d = g.getImageData(0, 0, FW, FH).data, r = rng(seed), out = [];
    const v = (x, y) => d[((clamp(y | 0, 0, FH - 1)) * FW + clamp(x | 0, 0, FW - 1)) * 4] / 255;
    for (let y = 4; y < FH - 4; y += 4.4) for (let x = 4; x < FW - 4; x += 4.4) {
      const px = x + (r() - .5) * 4, py = y + (r() - .5) * 4, val = v(px, py); if (val > 0.985) continue;
      const dk = 1 - val, gx = v(px + 3, py) - v(px - 3, py), gy = v(px, py + 3) - v(px, py - 3), cont = Math.atan2(gx, -gy), base = -0.88;
      const fade = 1 - ss(730, 840, py);                                         // 下端不收尾：越往下越淡，像还陷在石里
      let a = base + Math.sin(cont - base) * 0.18; const L = 12 + r() * 12;
      if (r() < dk * 1.55 + 0.05) out.push([px, py, a, L, 0.9 + dk * 0.9, clamp((0.18 + dk * 0.75) * fade, 0, 0.92), dk]);
      if (dk > 0.42 && r() < (dk - 0.3) * 1.5) out.push([px, py, 0.62 + (r() - .5) * 0.2, L * 0.8, 0.8 + dk * 0.7, clamp((0.15 + dk * 0.6) * fade, 0, 0.85), dk]);
    }
    return out;
  }
  function renderChalk(f, strokes, key) {
    const cv = P.canvas(FW, FH), g = cv.getContext('2d'); g.lineCap = 'round';
    strokes.forEach(([x, y, a, L, w, al, dk]) => { g.strokeStyle = dk > 0.6 ? `rgba(104,38,22,${al})` : `rgba(158,66,40,${al})`; g.lineWidth = w; g.beginPath(); g.moveTo(x - Math.cos(a) * L / 2, y - Math.sin(a) * L / 2); g.lineTo(x + Math.cos(a) * L / 2, y + Math.sin(a) * L / 2); g.stroke(); });
    // 重轮廓：取整体剪影的边界像素，按背光侧加粗、间断（粉笔在纸上拖出的颗粒线），部件之间的接缝不画
    const mg = f.mask.getContext('2d');
    const md = mg.getImageData(0, 0, FW, FH).data, al = (x, y) => md[((clamp(y | 0, 0, FH - 1)) * FW + clamp(x | 0, 0, FW - 1)) * 4 + 3] > 128, rr = rng(77);
    for (let y = 1; y < FH - 1; y++) for (let x = 1; x < FW - 1; x++) {
      if (!al(x, y) || (al(x - 1, y) && al(x + 1, y) && al(x, y - 1) && al(x, y + 1))) continue;
      const nx = (al(x - 1, y) ? 1 : 0) - (al(x + 1, y) ? 1 : 0) * -1, ny = 0;                       // 外法线粗估（见下）
      const gx = (al(x + 2, y) ? 1 : 0) - (al(x - 2, y) ? 1 : 0), gy = (al(x, y + 2) ? 1 : 0) - (al(x, y - 2) ? 1 : 0);     // 指向内部
      const shade = clamp(-(gx * 0.6 + gy * 0.8), 0, 1);                                              // 外法线朝右下＝背光
      const dash = Math.sin(x * 0.045 + y * 0.037) + Math.sin(x * 0.011 - y * 0.05) * 0.8; if (dash < -0.7 - shade * 0.7) continue;
      const fade = 1 - ss(740, 830, y); g.fillStyle = `rgba(96,34,20,${(0.5 + shade * 0.45) * fade})`; g.beginPath(); g.arc(x + (rr() - .5) * 0.8, y + (rr() - .5) * 0.8, 1.0 + shade * 1.5 + rr() * 0.5, 0, TAU); g.fill();
    }
    return cv;
  }
  function paperPlate() {
    const cv = P.canvas(), g = cv.getContext('2d'), r = rng(9);
    const bg = g.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, '#2c2218'); bg.addColorStop(1, '#17110c'); g.fillStyle = bg; g.fillRect(0, 0, W, H);
    g.strokeStyle = 'rgba(255,230,190,.035)'; g.lineWidth = 2; for (let i = 0; i < 80; i++) { const y = r() * H; g.beginPath(); g.moveTo(0, y); g.bezierCurveTo(500, y + (r() - .5) * 30, 1300, y + (r() - .5) * 30, W, y + (r() - .5) * 20); g.stroke(); }
    // 纸：不规则撕边＋投影
    const edge = []; const x0 = 120, y0 = 56, x1 = 1800, y1 = 1030;
    for (let x = x0; x <= x1; x += 40) edge.push([x, y0 + (r() - .5) * 6]); for (let y = y0; y <= y1; y += 40) edge.push([x1 + (r() - .5) * 6, y]); for (let x = x1; x >= x0; x -= 40) edge.push([x, y1 + (r() - .5) * 6]); for (let y = y1; y >= y0; y -= 40) edge.push([x0 + (r() - .5) * 6, y]);
    const sp = smooth(edge); g.save(); g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = 40; g.shadowOffsetY = 12; g.fillStyle = '#dcc397'; g.fill(sp); g.restore();
    g.save(); g.clip(sp);
    const pg = g.createRadialGradient(960, 520, 200, 960, 540, 1050); pg.addColorStop(0, 'rgba(240,220,170,.35)'); pg.addColorStop(1, 'rgba(120,80,40,.35)'); g.fillStyle = pg; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '150,100,50' : '110,80,40'},${0.03 + r() * 0.08})`; g.beginPath(); g.ellipse(x0 + r() * (x1 - x0), y0 + r() * (y1 - y0), 6 + r() * 40, 5 + r() * 30, r() * 3, 0, TAU); g.fill(); }        // 霉斑
    g.strokeStyle = 'rgba(120,90,50,.12)'; g.lineWidth = 1; for (let i = 0; i < 260; i++) { const x = x0 + r() * (x1 - x0), y = y0 + r() * (y1 - y0); g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - .5) * 34, y + (r() - .5) * 10); g.stroke(); }                 // 纸纤维
    // 注记：几行不成字的手写笔画（右下）
    g.strokeStyle = 'rgba(90,40,24,.55)'; g.lineWidth = 1.8; g.lineCap = 'round'; for (let ln = 0; ln < 4; ln++) { let x = 1240; const y = 900 + ln * 30; g.beginPath(); g.moveTo(x, y); while (x < 1640 - r() * 100) { x += 6 + r() * 12; g.quadraticCurveTo(x - 4, y - 8 - r() * 8, x, y + (r() - .5) * 3); } g.stroke(); }
    g.restore();
    return cv;
  }
  function build() {
    const f = formMap(), st = hatch(f, 5); big = renderChalk(f, st, 'big'); big._f = f;
    const sm = P.canvas(FW, FH), sg = sm.getContext('2d'); sg.drawImage(big, 0, 0); small = sm;                                  // 旧习作：同一人，翻转缩小，较淡
    paper = paperPlate(); built = true;
  }
  function draw(c, lt) {
    if (!built) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(paper, 0, 0);
    // 右侧旧习作：翻转、0.46 倍、较淡，画满
    c.save(); c.globalAlpha = 0.72; c.translate(1560, 90); c.scale(-0.46, 0.46); c.translate(-FW, 0); c.drawImage(small, 0, 0, FW, FH * 0.9, 0, 0, FW, FH * 0.9); c.restore();
    // 主习作：随笔尖从上往下被画出
    const OX = 500, OY = 110, S = 1.0, p = ss(0.25, 5.2, t), ry = p * (FH + 30);
    c.save(); c.beginPath(); c.rect(OX, OY, FW * S, ry * S); c.clip(); c.drawImage(big, OX, OY, FW * S, FH * S); c.restore();
    c.save(); c.globalAlpha = 1; const edge = c.createLinearGradient(0, OY + ry * S - 26, 0, OY + ry * S); edge.addColorStop(0, 'rgba(220,195,150,0)'); edge.addColorStop(1, 'rgba(220,195,150,.0)'); c.restore();
    if (p < 0.999) {                                       // 粉笔：笔尖在揭示线上左右扫，笔杆朝右上
      const tx = OX + FW * S * (0.5 + 0.46 * Math.sin(t * 7.3) * Math.cos(t * 1.9)), ty = OY + ry * S + Math.sin(t * 13) * 3;
      c.save(); c.translate(tx, ty); c.rotate(-0.95); c.fillStyle = '#7a3a24'; c.fillRect(0, -5, 190, 10); c.fillStyle = '#9c3f26'; c.fillRect(-16, -5, 18, 10); c.fillStyle = '#c9a56a'; c.fillRect(120, -6, 60, 12); c.restore();
      c.fillStyle = 'rgba(150,70,44,.28)'; for (let i = 0; i < 6; i++) { c.beginPath(); c.arc(tx + (Math.sin(t * 20 + i * 7) * 14), ty + 6 + ((t * 40 + i * 9) % 36), 1.3, 0, TAU); c.fill(); }   // 落下的粉屑
    }
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.18; c.drawImage(P.texture('paper_mich', '#e6d2aa', { scale: 0.006, amt: 12, grain: 8, seed: 3 }), 0, 0); c.restore();
  }
  return { draw };
})();
