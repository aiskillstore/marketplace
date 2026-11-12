// 波斯细密画（赫拉特/萨法维）：没有透视收束，地面像一张竖起的挂毯；建筑被切开让人看见里面；每一寸都有纹样；金、青金石蓝、朱、孔雀绿；文字块进画。
// 题材（新构图）：庭院里的汲水轮——一位园丁摇轮，水顺渠流进八角水池，旁边两人在亭下读书；上方书页式文字块。
// 原作锚定（fetch_reference.py：赫拉特 Bustan《尤素福与祖莱哈》、花园浴女页、沙赫塔赫马斯普《列王纪》页）：
//   纸/羊皮 #d9bf88、青金石 #1f4f8f、朱 #b7372b、孔雀绿 #2a8a7a、金 #d6a93c、玫粉 #d98a7a；砖红/青瓷砖满铺几何；
//   树＝平涂树干＋点叶团＋花；人＝小、侧身、大头巾、袍上暗纹；地面一律「俯视平铺」，远处靠叠高不靠缩小。
// 管线：纸底（缓存）→ 外框金线＋蓝带 → 文字块 → 建筑切面（砖＋瓷砖满铺）→ 庭院平铺地面（草＋花点）→ 水池（八角，几何瓷砖边）
//      → 树 → 动态：汲水轮转、水沿渠流、人物动作、花瓣飘、水纹 → 极薄的纸纤维相乘。
SCENES['51_persian_miniature'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const C = { paper: '#dcc38c', lapis: '#1f4f8f', lapis2: '#2f6fb0', red: '#b7372b', teal: '#2a8a7a', gold: '#d6a93c', rose: '#d98a7a', brick: '#c0643f', cream: '#efe0b4', green: '#6f9a4a', dgreen: '#3f6e3a', ink: '#2b2118' };
  let layer;
  const poly = (pts, close = true) => { const p = new Path2D(); pts.forEach((q, i) => i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])); if (close) p.closePath(); return p; };
  const fillPoly = (g, pts, col, o = {}) => { g.fillStyle = col; g.fill(poly(pts)); if (o.line !== false) { g.strokeStyle = o.line || C.ink; g.lineWidth = o.lw || 2.4; g.stroke(poly(pts)); } };
  // 满铺几何：星/十字瓷砖，周期取模，两色交替
  function tiles(g, x, y, w, h, size, a, b, c2, seed = 1) {
    g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); g.fillStyle = a; g.fillRect(x, y, w, h);
    const r = rng(seed);
    for (let j = 0; y + j * size < y + h + size; j++) for (let i = 0; x + i * size < x + w + size; i++) {
      const cx = x + i * size + size / 2, cy = y + j * size + size / 2, k = (i + j) % 2;
      g.fillStyle = k ? b : c2; g.beginPath(); for (let q = 0; q < 8; q++) { const ang = q / 8 * TAU + Math.PI / 8, rr = q % 2 ? size * 0.2 : size * 0.38; g.lineTo(cx + Math.cos(ang) * rr, cy + Math.sin(ang) * rr); } g.closePath(); g.fill();
      g.fillStyle = k ? c2 : b; g.beginPath(); g.arc(cx, cy, size * 0.1, 0, TAU); g.fill();
    }
    g.strokeStyle = 'rgba(30,24,16,.5)'; g.lineWidth = 1.4; for (let i = 0; i <= w / size + 1; i++) { g.beginPath(); g.moveTo(x + i * size, y); g.lineTo(x + i * size, y + h); g.stroke(); } for (let j = 0; j <= h / size + 1; j++) { g.beginPath(); g.moveTo(x, y + j * size); g.lineTo(x + w, y + j * size); g.stroke(); }
    g.restore();
  }
  function border(g) {                 // 金线＋青金石蓝带＋金色细花
    g.fillStyle = C.lapis; g.fillRect(0, 0, W, H); g.fillStyle = C.gold; g.fillRect(22, 22, W - 44, H - 44); g.fillStyle = C.paper; g.fillRect(30, 30, W - 60, H - 60);
    g.fillStyle = C.lapis; g.fillRect(44, 44, W - 88, H - 88); g.fillStyle = C.gold; g.fillRect(52, 52, W - 104, H - 104); g.fillStyle = C.paper; g.fillRect(58, 58, W - 116, H - 116);
    g.fillStyle = 'rgba(214,169,60,.9)'; for (let x = 70; x < W - 70; x += 38) { [34, H - 34].forEach(y => { g.beginPath(); g.arc(x, y, 6, 0, TAU); g.fill(); }); } for (let y = 70; y < H - 70; y += 38) { [34, W - 34].forEach(x => { g.beginPath(); g.arc(x, y, 6, 0, TAU); g.fill(); }); }
  }
  function textBlock(g, x, y, w, h) {  // 书法文字块：金边朱框内一行行「连笔」——用折线笔画模拟，不写具体字
    fillPoly(g, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], '#efe3bd', { lw: 3, line: C.gold });
    const r = rng(7); g.strokeStyle = C.ink; g.lineCap = 'round'; g.lineWidth = 2.4;
    for (let row = 0; row < Math.floor(h / 34); row++) { const yy = y + 28 + row * 34; let xx = x + w - 20; g.beginPath(); g.moveTo(xx, yy); while (xx > x + 24) { const st = 8 + r() * 18; xx -= st; g.quadraticCurveTo(xx + st / 2, yy - 8 - r() * 10, xx, yy + (r() - .5) * 6); if (r() < 0.12) { g.moveTo(xx - 10, yy); xx -= 10; } } g.stroke();
      g.fillStyle = C.red; if (row % 3 === 0) { g.beginPath(); g.arc(x + w - 14, yy - 6, 4, 0, TAU); g.fill(); } }
  }
  function build() {
    layer = P.canvas(); const g = layer.getContext('2d');
    g.fillStyle = C.paper; g.fillRect(0, 0, W, H); border(g);
    // 顶部：建筑切面（被切开：里面看得到人）
    g.save(); g.beginPath(); g.rect(60, 60, W - 120, H - 120); g.clip();
    // 外墙大面：砖红＋瓷砖腰线；门楣蓝釉
    fillPoly(g, [[900, 60], [1860, 60], [1860, 520], [900, 520]], C.brick, { lw: 3 });
    for (let y = 80; y < 500; y += 26) { g.strokeStyle = 'rgba(80,30,20,.35)'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(900, y); g.lineTo(1860, y); g.stroke(); for (let x = 900 + ((y / 26) % 2) * 20; x < 1860; x += 40) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 26); g.stroke(); } }
    tiles(g, 900, 60, 960, 90, 30, C.lapis, C.cream, C.teal, 3);
    // 切开的房间：亭（拱形开口），里面有地毯、两位读书人
    const arch = new Path2D(); arch.moveTo(1040, 520); arch.lineTo(1040, 250); arch.quadraticCurveTo(1040, 170, 1260, 170); arch.quadraticCurveTo(1480, 170, 1480, 250); arch.lineTo(1480, 520); arch.closePath();
    g.fillStyle = C.gold; g.fill(arch); g.save(); g.translate(0, 0); g.scale(1, 1); g.restore();
    const inner = new Path2D(); inner.moveTo(1060, 520); inner.lineTo(1060, 256); inner.quadraticCurveTo(1060, 192, 1260, 192); inner.quadraticCurveTo(1460, 192, 1460, 256); inner.lineTo(1460, 520); inner.closePath();
    g.save(); g.clip(inner); tiles(g, 1060, 180, 400, 340, 36, '#e7d6a6', C.lapis2, C.red, 5);
    // 地毯：红地，边带，中央大八角菱形
    fillPoly(g, [[1060, 420], [1460, 420], [1460, 520], [1060, 520]], C.red, { lw: 2.4 });
    for (let x = 1076; x < 1460; x += 34) { g.fillStyle = C.gold; g.beginPath(); g.moveTo(x, 470); g.lineTo(x + 12, 456); g.lineTo(x + 24, 470); g.lineTo(x + 12, 484); g.fill(); }
    g.restore(); g.strokeStyle = C.ink; g.lineWidth = 3; g.stroke(arch);
    // 左侧塔楼＋窗；右侧小窗格
    fillPoly(g, [[1520, 150], [1840, 150], [1840, 500], [1520, 500]], C.cream, { lw: 3 }); tiles(g, 1520, 150, 320, 350, 32, C.cream, C.teal, C.lapis, 9);
    [[1560, 200], [1700, 200], [1560, 340], [1700, 340]].forEach(([x, y]) => { fillPoly(g, [[x, y + 100], [x, y + 40], [x + 20, y], [x + 60, y], [x + 80, y + 40], [x + 80, y + 100]], C.lapis, { lw: 3, line: C.gold }); });
    g.restore();
    textBlock(g, 120, 120, 640, 200); textBlock(g, 120, 340, 640, 120);
    // 下半：庭院平铺地面（竖起的挂毯）
    g.save(); g.beginPath(); g.rect(60, 520, W - 120, H - 580); g.clip();
    fillPoly(g, [[60, 520], [W - 60, 520], [W - 60, H - 60], [60, H - 60]], C.green, { line: false });
    const r = rng(11); for (let i = 0; i < 1400; i++) { const x = 70 + r() * (W - 140), y = 530 + r() * (H - 600), k = r(); g.fillStyle = k < 0.5 ? '#86b05a' : k < 0.8 ? '#4d7c3a' : (r() < 0.5 ? '#f0e6c8' : C.rose); g.beginPath(); g.ellipse(x, y, 3 + r() * 5, 2 + r() * 3, r(), 0, TAU); g.fill(); }
    // 水渠：从左上角的汲水轮底座流向八角水池，铺青瓷砖，几何边
    g.lineCap = 'butt'; g.lineJoin = 'round'; [['#2b2118', 78], [C.gold, 72], [C.teal, 58]].forEach(([col, w]) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(260, 670); g.lineTo(790, 670); g.lineTo(930, 800); g.stroke(); });
    // 八角水池：中央偏右
    const cx = 1160, cy = 790, R = 230, oct = Array.from({ length: 8 }, (_, k) => [cx + Math.cos(k / 8 * TAU + Math.PI / 8) * R * 1.08, cy + Math.sin(k / 8 * TAU + Math.PI / 8) * R * 0.74]);
    fillPoly(g, oct.map(p => [cx + (p[0] - cx) * 1.14, cy + (p[1] - cy) * 1.2]), C.gold, { lw: 3 });
    fillPoly(g, oct.map(p => [cx + (p[0] - cx) * 1.06, cy + (p[1] - cy) * 1.1]), C.lapis, { lw: 3, line: C.gold });
    fillPoly(g, oct, '#2c7e8a', { lw: 3, line: C.gold });
    // 周围铺小道：奶油色菱格
    for (let i = 0; i < 16; i++) { const x = 300 + i * 36, y = 760 + (i % 2) * 14; g.fillStyle = C.cream; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 14, y - 10); g.lineTo(x + 28, y); g.lineTo(x + 14, y + 10); g.fill(); }
    g.restore();
    // 树：左右各一，直干＋圆叶团＋花点＋果（树冠超出画面边缘上探，细密画常见）
    function tree(x, y, hgt, seed, bloom) {
      g.fillStyle = '#7a4a2a'; g.fillRect(x - 11, y - hgt, 22, hgt); g.strokeStyle = C.ink; g.lineWidth = 2.4; g.strokeRect(x - 11, y - hgt, 22, hgt);
      const rr = rng(seed); for (let k = 0; k < 9; k++) { const a = rr() * TAU, d = rr() * 70, cx2 = x + Math.cos(a) * d, cy2 = y - hgt - 30 + Math.sin(a) * d * 0.7; g.fillStyle = k % 2 ? C.dgreen : '#4f8a3f'; g.beginPath(); g.ellipse(cx2, cy2, 58, 46, 0, 0, TAU); g.fill(); g.strokeStyle = C.ink; g.lineWidth = 1.8; g.stroke(); }
      for (let k = 0; k < 40; k++) { const a = rr() * TAU, d = rr() * 100; g.fillStyle = bloom; g.beginPath(); g.arc(x + Math.cos(a) * d, y - hgt - 30 + Math.sin(a) * d * 0.6, 5, 0, TAU); g.fill(); }
    }
    tree(140, 720, 220, 31, '#f4d3d0'); tree(1790, 760, 240, 32, '#f4e6a0'); tree(700, 560, 120, 33, '#f4d3d0');
  }
  // 汲水轮：转；水斗按周期取模；水沿渠流
  function wheel(c, t) {
    const cx = 340, cy = 580, R = 120, a0 = t * 0.8;
    c.save(); c.translate(cx, cy);
    c.strokeStyle = C.ink; c.lineWidth = 3; c.fillStyle = '#9a6a3a'; c.beginPath(); c.arc(0, 0, R, 0, TAU); c.arc(0, 0, R - 14, 0, TAU, true); c.fill('evenodd'); c.stroke(); c.beginPath(); c.arc(0, 0, R - 14, 0, TAU); c.stroke();
    for (let k = 0; k < 12; k++) { const a = a0 + k / 12 * TAU; c.save(); c.rotate(a); c.fillStyle = '#7a4a2a'; c.fillRect(-4, 0, 8, R - 14); c.strokeRect(-4, 0, 8, R - 14); c.fillStyle = C.gold; c.fillRect(-14, R - 6, 28, 16); c.strokeRect(-14, R - 6, 28, 16); c.restore(); }
    c.fillStyle = C.red; c.beginPath(); c.arc(0, 0, 18, 0, TAU); c.fill(); c.stroke();
    c.restore();
  }
  function water(c, t) {
    // 渠水：沿折线 (260,670)→(790,670)→(930,800) 的金色小波，向右下流
    const seg = [[260, 670, 790, 670], [790, 670, 930, 800]], Ls = seg.map(q => Math.hypot(q[2] - q[0], q[3] - q[1])), tot = Ls[0] + Ls[1];
    for (let i = 0; i < 16; i++) { let d = ((i * tot / 16 + t * 90) % tot), k = d < Ls[0] ? 0 : 1; if (k) d -= Ls[0]; const q = seg[k], u = d / Ls[k], x = lerp(q[0], q[2], u), y = lerp(q[1], q[3], u) + ((i % 3) - 1) * 12;
      c.strokeStyle = 'rgba(244,224,160,.85)'; c.lineWidth = 2.4; c.beginPath(); c.moveTo(x - 12, y); c.quadraticCurveTo(x, y - 7, x + 12, y); c.stroke(); }
    // 水池：同心波＋金鱼
    const cx = 1160, cy = 790;
    c.save(); c.beginPath(); for (let k = 0; k < 8; k++) { const ang = k / 8 * TAU + Math.PI / 8; c.lineTo(cx + Math.cos(ang) * 230 * 1.08, cy + Math.sin(ang) * 230 * 0.74); } c.closePath(); c.clip();
    for (let i = 0; i < 6; i++) { const q = ((t * 0.35 + i / 6) % 1); c.strokeStyle = `rgba(244,230,180,${(1 - q) * 0.8})`; c.lineWidth = 2.6; c.beginPath(); c.ellipse(cx - 130 + Math.sin(i) * 40, cy - 20, 20 + q * 150, 8 + q * 50, 0, 0, TAU); c.stroke(); }
    [[0, 1.0, C.red], [2.2, -0.8, C.gold], [4.1, 0.7, C.cream]].forEach(([ph, dir, col], i) => { const a = t * 0.6 * dir + ph, x = cx + Math.cos(a) * 140, y = cy + Math.sin(a) * 70 + 10, ang = Math.atan2(Math.cos(a) * 70 * dir, -Math.sin(a) * 140 * dir);
      c.save(); c.translate(x, y); c.rotate(ang); c.fillStyle = col; c.strokeStyle = C.ink; c.lineWidth = 2; c.beginPath(); c.ellipse(0, 0, 30, 12, 0, 0, TAU); c.fill(); c.stroke(); c.beginPath(); c.moveTo(-28, 0); c.lineTo(-48, -12 + Math.sin(t * 8 + i) * 4); c.lineTo(-48, 12 + Math.sin(t * 8 + i) * 4); c.closePath(); c.fill(); c.stroke(); c.fillStyle = C.ink; c.beginPath(); c.arc(16, -3, 2.4, 0, TAU); c.fill(); c.restore(); });
    c.restore();
  }
  // 人（萨法维式）：修长，头小，高头巾＋红色冠杆，束腰长袍下摆外展，腰带垂一端，鞋尖朝前；扁平填色＋粗线描边，袍上小花散点。
  function person(c, x, y, s, face, col, turban, t, o = {}) {
    c.save(); c.translate(x, y); c.scale(s * face, s); c.lineJoin = 'round'; c.lineCap = 'round'; c.strokeStyle = C.ink; c.lineWidth = 2.6 / s;
    const bob = o.bob || 0, sw = Math.sin(t * 1.7 + (o.ph || 0)) * 3;
    // 鞋：尖头
    c.fillStyle = C.red; [[-14, 0], [16, 0]].forEach(([dx]) => { c.beginPath(); c.moveTo(dx - 9, -4); c.quadraticCurveTo(dx + 10, -10, dx + 24, -2); c.quadraticCurveTo(dx + 12, 5, dx - 9, 4); c.closePath(); c.fill(); c.stroke(); });
    // 长袍：窄肩 → 束腰 → 下摆外展，前襟交叠一道线
    c.fillStyle = col; c.beginPath(); c.moveTo(-20, -152 + bob); c.quadraticCurveTo(-26, -118, -18, -96 + bob); c.quadraticCurveTo(-34, -52, -52 + sw, -6); c.quadraticCurveTo(0, 3, 52 + sw, -6); c.quadraticCurveTo(34, -52, 18, -96 + bob); c.quadraticCurveTo(26, -118, 20, -152 + bob); c.closePath(); c.fill(); c.stroke();
    c.save(); c.clip(); c.fillStyle = 'rgba(244,224,160,.8)'; for (let k = 0; k < 24; k++) { const px = -44 + (k % 6) * 17 + (Math.floor(k / 6) % 2) * 8, py = -140 + Math.floor(k / 6) * 34; c.beginPath(); for (let q = 0; q < 5; q++) { const aa = q / 5 * TAU; c.moveTo(px, py); c.arc(px + Math.cos(aa) * 4.4, py + Math.sin(aa) * 4.4, 2.6, 0, TAU); } c.fill(); }
    c.strokeStyle = 'rgba(43,33,24,.55)'; c.lineWidth = 1.6; c.beginPath(); c.moveTo(4, -148 + bob); c.quadraticCurveTo(10, -80, 30 + sw, -6); c.stroke(); c.restore();
    c.strokeStyle = C.ink; c.lineWidth = 2.6 / s; c.strokeStyle = C.gold; c.lineWidth = 4; c.beginPath(); c.moveTo(-52 + sw, -6); c.quadraticCurveTo(0, 3, 52 + sw, -6); c.stroke(); c.strokeStyle = C.ink; c.lineWidth = 2.6 / s;
    // 腰带＋垂端
    c.fillStyle = C.gold; c.fillRect(-19, -100 + bob * 0.5, 38, 9); c.strokeRect(-19, -100 + bob * 0.5, 38, 9);
    c.fillStyle = C.cream; c.beginPath(); c.moveTo(10, -92 + bob * 0.5); c.lineTo(22, -60 + sw * 0.4); c.lineTo(10, -64 + sw * 0.4); c.closePath(); c.fill(); c.stroke();
    // 手臂：默认一只垂袖，另一只抬到胸前持物
    if (o.arm) o.arm(c, bob); else { c.strokeStyle = col; c.lineWidth = 11; c.beginPath(); c.moveTo(16, -144 + bob); c.lineTo(34, -108 + bob); c.lineTo(22, -90 + bob); c.stroke(); c.strokeStyle = C.ink; c.lineWidth = 2.6 / s; c.fillStyle = '#e8c298'; c.beginPath(); c.arc(22, -88 + bob, 5, 0, TAU); c.fill(); c.stroke(); }
    // 颈与头：小，3/4，弯眉连成一道，杏仁眼，胡须一线
    c.fillStyle = '#e8c298'; c.fillRect(-4, -160 + bob, 9, 12);
    c.beginPath(); c.ellipse(3, -172 + bob, 15, 18, 0, 0, TAU); c.fill(); c.stroke();
    c.fillStyle = C.ink; c.beginPath(); c.ellipse(10, -174 + bob, 3.8, 2.4, 0, 0, TAU); c.fill();
    c.beginPath(); c.moveTo(-1, -181 + bob); c.quadraticCurveTo(7, -186 + bob, 17, -180 + bob); c.stroke();
    c.beginPath(); c.moveTo(6, -161 + bob); c.quadraticCurveTo(13, -159 + bob, 17, -163 + bob); c.stroke();
    // 头巾：白裹布＋高耸的红冠杆（向前微倾），顶端一小簇羽
    c.fillStyle = turban; c.beginPath(); c.ellipse(1, -188 + bob, 22, 11, 0, 0, TAU); c.fill(); c.stroke();
    c.fillStyle = C.red; c.beginPath(); c.moveTo(-9, -192 + bob); c.quadraticCurveTo(-4, -226 + bob, 6 + sw * 0.3, -246 + bob); c.lineTo(12 + sw * 0.3, -244 + bob); c.quadraticCurveTo(12, -216 + bob, 14, -192 + bob); c.closePath(); c.fill(); c.stroke();
    c.strokeStyle = C.gold; c.lineWidth = 3; c.beginPath(); c.moveTo(-8, -202 + bob); c.lineTo(13, -202 + bob); c.stroke(); c.strokeStyle = C.ink; c.lineWidth = 2.6 / s;
    c.fillStyle = C.cream; c.beginPath(); c.ellipse(9 + sw * 0.3, -250 + bob, 4, 9, 0.4, 0, TAU); c.fill(); c.stroke();
    c.restore();
  }
  function draw(c, lt) {
    if (!layer) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(layer, 0, 0);
    wheel(c, t); water(c, t);
    // 园丁：站在汲水轮旁摇杆
    const crank = Math.sin(t * 0.8 * 3.0);
    person(c, 530, 706, 1.05, 1, C.lapis2, C.cream, t, { bob: Math.sin(t * 2.4) * 2, arm: (cc, bob) => { const hx = -70 - crank * 20, hy = -104 - crank * 14; cc.strokeStyle = C.ink; cc.lineWidth = 14; cc.beginPath(); cc.moveTo(14, -144 + bob); cc.lineTo(-24 - crank * 8, -118 + bob); cc.lineTo(hx, hy); cc.stroke(); cc.strokeStyle = C.lapis2; cc.lineWidth = 10; cc.beginPath(); cc.moveTo(14, -144 + bob); cc.lineTo(-24 - crank * 8, -118 + bob); cc.lineTo(hx, hy); cc.stroke(); cc.strokeStyle = C.ink; cc.lineWidth = 2.6; cc.fillStyle = '#e8c298'; cc.beginPath(); cc.arc(hx, hy, 5.5, 0, TAU); cc.fill(); cc.stroke(); } });
    // 亭下读书人（在建筑切面里）：两人对坐，一个翻页
    person(c, 1180, 520, 0.92, 1, C.red, C.cream, t, { ph: 0, bob: Math.sin(t * 1.4) * 1.5 });
    person(c, 1370, 520, 0.92, -1, C.teal, C.cream, t, { ph: 2, bob: Math.sin(t * 1.4 + 2) * 1.5 });
    // 花瓣与落叶：从树冠飘到池面
    const r = rng(3); for (let i = 0; i < 22; i++) { const ph = r() * 6, sp = 0.4 + r() * 0.4, x0 = 160 + r() * 1600, q = ((t * sp * 0.2 + ph) % 1), x = x0 + Math.sin(t * 1.4 + i) * 24 + q * 80, y = 560 + q * 480; c.fillStyle = i % 2 ? '#f4d3d0' : '#f4e6a0'; c.strokeStyle = 'rgba(43,33,24,.5)'; c.lineWidth = 1.2; c.beginPath(); c.ellipse(x, y, 7, 4, t + i, 0, TAU); c.fill(); c.stroke(); }
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.28; c.drawImage(P.texture('paper_pm', '#d6bf8a', { scale: 0.004, amt: 14, grain: 6, seed: 9 }), 0, 0); c.restore();
  }
  return { draw };
})();
