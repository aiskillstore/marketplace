// 敦煌壁画（北朝：257 窟鹿王本生 · 285 窟西魏飞天）：土红地上的白色走兽和锯齿山，奶白地上的青绿风叶和长飘带飞天；
// 不是「中国风插画」——它是干燥的泥壁画：矿物色粉上墙、铅白氧化发暗、墙皮龟裂起甲、盐碱泛白，线是红褐的铁线／兰叶描。
// 题材（新构图）：上栏一位飞天托莲横空而过，风叶和散花从身边向后翻；下栏一只白鹿领着一只小鹿穿过三角形的山奔跑。
// 原作锚定（fetch_reference.py：257 窟鹿王本生、285 窟西魏飞天、428 窟北周飞天、盛唐 112 窟）：
//   土红地 #92342d／#9b4745；白鹿 #efe6d2；青绿 #3e919c／#577f7a；奶白地 #e8dcc5；赭 #b89d7d；深褐线 #3a1812；
//   山＝一排排锯齿三角、各自涂青／白／黑／绿；动物＝平涂白身＋极少内部线；飞天＝水平横飞、下身化成一条飘到身后的长裙；
//   上下两栏之间有一道多色横带；窟顶下沿垂幔三角纹；整面墙龟裂、起甲、泛盐。
// 管线：墙底（泥＋色差，缓存）→ 上栏奶白地＋下栏土红地＋多色分隔带＋顶部菱格带＋底部垂幔 → 锯齿山（缓存）
//      → 动态：鹿群奔跑、风叶后掠、飞天、散花、尘埃 → 龟裂／起甲／盐碱覆盖层（盖在画上面，裂缝穿过人和鹿）→ 泥壁颗粒相乘。
SCENES['55_dunhuang'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, TAU = Math.PI * 2;
  const C = { sky: '#e6d9bf', red: '#92342d', red2: '#7c2a24', white: '#efe6d2', teal: '#3e919c', teal2: '#1f5f6a', green: '#577f7a', ochre: '#c58a3e', ink: '#3a1812', line: '#6b2a1c', skin: '#e6cfae', flush: '#df8d74', dark: '#241512', lapis: '#35597c' };
  const TOP = 64, SPLIT = 478, GROUND = 930, BOT = 986;
  let base, over;
  const sh = (h, k) => { const q = P.hex(h); return `rgb(${Math.round(q[0] * k)},${Math.round(q[1] * k)},${Math.round(q[2] * k)})`; };
  const poly = (g, pts) => { g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); };

  // ---- 静态：墙与两栏 ----
  function band(g) {                                   // 顶部：菱格带（青／白／红／黑）
    g.fillStyle = C.dark; g.fillRect(0, 0, W, TOP);
    const cols = [C.teal, C.white, C.red, C.ochre];
    for (let i = 0, x = 0; x < W + 60; i++, x += 56) { g.fillStyle = cols[i % 4]; poly(g, [[x, TOP / 2], [x + 28, 8], [x + 56, TOP / 2], [x + 28, TOP - 8]]); g.fill(); g.strokeStyle = C.dark; g.lineWidth = 2; g.stroke(); g.fillStyle = cols[(i + 2) % 4]; g.beginPath(); g.arc(x + 28, TOP / 2, 5, 0, TAU); g.fill(); }
  }
  function divider(g) {                                // 上下栏之间的多色横带＋联珠
    const rows = [[C.dark, 8], [C.white, 14], [C.teal, 20], [C.ochre, 14], [C.white, 12], [C.dark, 8]]; let y = SPLIT;
    rows.forEach(([col, h]) => { g.fillStyle = col; g.fillRect(0, y, W, h); y += h; });
    g.fillStyle = C.white; g.strokeStyle = C.dark; g.lineWidth = 1.6; for (let x = 14; x < W; x += 28) { g.beginPath(); g.arc(x, SPLIT + 8 + 14 + 10, 5, 0, TAU); g.fill(); g.stroke(); }
  }
  function drapery(g) {                                // 底部：垂幔三角纹，每片垂一粒珠
    g.fillStyle = C.dark; g.fillRect(0, BOT, W, H - BOT);
    const cols = [C.teal, C.ochre, C.white, C.red2, C.green];
    for (let i = 0, x = -10; x < W + 80; i++, x += 84) { g.fillStyle = cols[i % 5]; poly(g, [[x, BOT], [x + 84, BOT], [x + 42, BOT + 70]]); g.fill(); g.strokeStyle = C.dark; g.lineWidth = 2.4; g.stroke();
      g.fillStyle = cols[(i + 2) % 5]; poly(g, [[x + 20, BOT], [x + 64, BOT], [x + 42, BOT + 38]]); g.fill(); g.fillStyle = C.white; g.beginPath(); g.arc(x + 42, BOT + 82, 6, 0, TAU); g.fill(); g.stroke(); }
  }
  function mountains(g) {                              // 257 窟式的山：窄高、倾斜、参差的三角碎片，一排排叠在红地上，红地大面积露出来；每片一色，一侧压暗，内部几道斜向地层线
    const r = rng(257), rows = [[790, 150, 250, [C.teal2, C.dark, C.green, C.lapis], 1.18], [905, 90, 160, [C.white, C.teal, C.ochre, C.white], 1.0]];
    rows.forEach(([bs, h0, h1, pal, step], ri) => { let x = -60 + ri * 90; while (x < W + 100) { const w = 130 + r() * 150, hh = h0 + r() * (h1 - h0), c0 = pal[Math.floor(r() * pal.length)], ap = x + w * (0.5 + (r() - .5) * 1.5);
      g.fillStyle = c0; poly(g, [[x, bs], [ap, bs - hh], [x + w, bs]]); g.fill();
      g.fillStyle = sh(c0, 0.6); poly(g, [[ap, bs - hh], [x + w, bs], [ap - (ap - x) * 0.05, bs - hh * 0.0]]); g.fill();
      g.save(); poly(g, [[x, bs], [ap, bs - hh], [x + w, bs]]); g.clip(); g.strokeStyle = 'rgba(58,24,18,.5)'; g.lineWidth = 2; for (let k = 1; k < 6; k++) { const yy = bs - hh * k / 6.4; g.beginPath(); g.moveTo(x - 10, yy + 26); g.lineTo(x + w + 10, yy - 14); g.stroke(); } g.restore();
      g.strokeStyle = C.ink; g.lineWidth = 3; g.lineJoin = 'round'; poly(g, [[x, bs], [ap, bs - hh], [x + w, bs]]); g.stroke();
      x += w * (step + r() * 0.25); } });
  }
  function ground(g) {                                 // 山脚地面：赭土＋青绿三叶草＋碎石点
    g.fillStyle = C.ochre; g.fillRect(0, GROUND, W, BOT - GROUND); g.fillStyle = C.ink; g.fillRect(0, GROUND - 3, W, 5);
    const r = rng(11); for (let i = 0; i < 70; i++) { const x = r() * W, y = GROUND + 10 + r() * (BOT - GROUND - 20); g.strokeStyle = r() < 0.6 ? C.teal2 : C.ink; g.lineWidth = 2.2; g.beginPath(); g.moveTo(x, y); g.lineTo(x - 7, y - 12); g.moveTo(x, y); g.lineTo(x + 1, y - 15); g.moveTo(x, y); g.lineTo(x + 8, y - 11); g.stroke(); }
  }
  function build() {
    base = P.canvas(); const g = base.getContext('2d');
    g.drawImage(P.texture('dh_sky', C.sky, { scale: 0.003, amt: 22, grain: 8, seed: 4 }), 0, TOP, W, SPLIT - TOP, 0, TOP, W, SPLIT - TOP);
    g.drawImage(P.texture('dh_red', C.red, { scale: 0.0034, amt: 26, grain: 9, dark: '#5a1d1a', seed: 9 }), 0, SPLIT, W, BOT - SPLIT, 0, SPLIT, W, BOT - SPLIT);
    g.save(); g.beginPath(); g.rect(0, SPLIT + 76, W, GROUND - SPLIT - 76); g.clip(); mountains(g); g.restore();
    // 红地上撒几只远处的小白兽剪影（257 窟满地走兽的感觉）
    const rs = rng(77); for (let i = 0; i < 7; i++) { const x = 120 + i * 270 + rs() * 80, y = SPLIT + 120 + rs() * 90; g.fillStyle = 'rgba(239,230,210,.92)'; g.strokeStyle = C.ink; g.lineWidth = 2; g.beginPath(); g.ellipse(x, y, 26, 11, 0, 0, TAU); g.fill(); g.stroke(); g.beginPath(); g.ellipse(x + 26, y - 14, 8, 6, 0.3, 0, TAU); g.fill(); g.stroke(); [-14, 14].forEach(dx => { g.beginPath(); g.moveTo(x + dx, y + 8); g.lineTo(x + dx - 3, y + 26); g.stroke(); }); }
    ground(g); band(g); divider(g); drapery(g);
    // 上栏底部一圈淡淡的熏黑（油灯与岁月）
    const gr = g.createLinearGradient(0, TOP, 0, SPLIT); gr.addColorStop(0, 'rgba(60,34,20,.26)'); gr.addColorStop(0.22, 'rgba(60,34,20,0)'); gr.addColorStop(1, 'rgba(60,34,20,.12)'); g.fillStyle = gr; g.fillRect(0, TOP, W, SPLIT - TOP);
    // 覆盖层：龟裂、起甲露底、盐碱
    over = P.canvas(); const o = over.getContext('2d'), r = rng(1999);
    for (let k = 0; k < 18; k++) { let x = r() * W, y = TOP + r() * (BOT - TOP), a = r() * TAU; o.strokeStyle = 'rgba(30,14,10,.5)'; o.lineWidth = 1.2 + r() * 1.2; o.lineJoin = 'round'; o.beginPath(); o.moveTo(x, y);
      const n = 10 + Math.floor(r() * 22); for (let i = 0; i < n; i++) { a += (r() - .5) * 0.9; x += Math.cos(a) * (12 + r() * 20); y += Math.sin(a) * (12 + r() * 20); o.lineTo(x, y); if (r() < 0.12) { o.stroke(); o.beginPath(); o.moveTo(x, y); a += (r() < 0.5 ? 1 : -1) * 0.9; } } o.stroke(); }
    for (let k = 0; k < 22; k++) { const cx = r() * W, cy = TOP + r() * (BOT - TOP), n = 9 + Math.floor(r() * 6), R = 6 + r() * 22; o.fillStyle = r() < 0.6 ? 'rgba(206,176,136,.34)' : 'rgba(96,60,40,.26)'; o.beginPath();
      for (let i = 0; i < n; i++) { const aa = i / n * TAU, rr = R * (0.45 + r() * 0.75); o.lineTo(cx + Math.cos(aa) * rr, cy + Math.sin(aa) * rr * 0.7); } o.closePath(); o.fill(); o.strokeStyle = 'rgba(40,20,12,.3)'; o.lineWidth = 1.4; o.stroke(); }
    for (let k = 0; k < 260; k++) { o.fillStyle = `rgba(245,238,225,${0.1 + r() * 0.3})`; o.beginPath(); o.ellipse(r() * W, TOP + r() * (BOT - TOP), 1.5 + r() * 4.5, 1 + r() * 2.5, r() * 3, 0, TAU); o.fill(); }
  }

  // ---- 动态件 ----
  const lineStroke = (c, w = 2.6) => { c.strokeStyle = C.line; c.lineWidth = w; c.lineJoin = 'round'; c.lineCap = 'round'; };
  function ribbon(c, pts, w0, w1, fill, edge = C.line, hi = null) {   // 变宽飘带：两侧沿法线展开，铁线描边
    const L = [], R = [];
    pts.forEach((p, i) => { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)], dx = b[0] - a[0], dy = b[1] - a[1], d = Math.hypot(dx, dy) || 1, nx = -dy / d, ny = dx / d, w = lerp(w0, w1, i / (pts.length - 1)) / 2; L.push([p[0] + nx * w, p[1] + ny * w]); R.push([p[0] - nx * w, p[1] - ny * w]); });
    c.beginPath(); L.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); R.reverse().forEach(p => c.lineTo(p[0], p[1])); c.closePath(); c.fillStyle = fill; c.fill(); lineStroke(c, 2.2); c.strokeStyle = edge; c.stroke();
    if (hi) { c.strokeStyle = hi; c.lineWidth = 2; c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.stroke(); }
  }
  function leaf(c, x, y, ang, len, col, col2, k) {      // 西魏「风叶」：一撮向后翻卷的逗号形青绿叶，三尖
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(1, k);
    c.beginPath(); c.moveTo(0, 0); c.bezierCurveTo(len * 0.25, -len * 0.5, len * 0.8, -len * 0.45, len, -len * 0.12); c.bezierCurveTo(len * 0.7, -len * 0.18, len * 0.5, -len * 0.1, len * 0.42, len * 0.06); c.bezierCurveTo(len * 0.3, len * 0.18, len * 0.1, len * 0.14, 0, 0); c.closePath();
    c.fillStyle = col; c.fill(); lineStroke(c, 2); c.strokeStyle = col2; c.stroke();
    c.strokeStyle = 'rgba(255,250,235,.8)'; c.lineWidth = 2.2; c.beginPath(); c.moveTo(len * 0.1, -len * 0.06); c.bezierCurveTo(len * 0.3, -len * 0.3, len * 0.6, -len * 0.3, len * 0.84, -len * 0.14); c.stroke();
    c.restore();
  }
  function bloom(c, x, y, s, rot, col) {                // 散花：四瓣白花，红心
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.fillStyle = col; lineStroke(c, 1.8 / s);
    for (let i = 0; i < 4; i++) { c.save(); c.rotate(i * TAU / 4); c.beginPath(); c.ellipse(0, -9, 5.5, 9, 0, 0, TAU); c.fill(); c.stroke(); c.restore(); }
    c.fillStyle = C.red; c.beginPath(); c.arc(0, 0, 3.2, 0, TAU); c.fill(); c.restore();
  }
  function lotus(c, x, y, s) {
    c.save(); c.translate(x, y); c.scale(s, s); lineStroke(c, 2.2 / s);
    [[-1.0, '#f1d9d0'], [1.0, '#f1d9d0'], [-0.5, '#f6e4dc'], [0.5, '#f6e4dc'], [0, '#fbeee8']].forEach(([a, col]) => { c.save(); c.rotate(a * 0.9 - 0.2); c.beginPath(); c.moveTo(0, 0); c.bezierCurveTo(-11, -14, -9, -32, 0, -40); c.bezierCurveTo(9, -32, 11, -14, 0, 0); c.fillStyle = col; c.fill(); c.stroke(); c.restore(); });
    c.fillStyle = C.ochre; c.beginPath(); c.arc(0, -4, 5, 0, TAU); c.fill(); c.restore();
  }
  // 飞天（西魏式）：水平横飞，头在前，披帛后扬，躯干与长裙是一条连贯的 S 形；脸小、眉眼细长、颊上一点红晕；红褐铁线勾边，肤色铅丹淡赭
  function apsara(c, x, y, s, flip, t, ph = 0) {
    c.save(); c.translate(x, y + Math.sin(t * 1.15 + ph) * 12); c.rotate(-0.07 + Math.sin(t * 0.9 + ph) * 0.03); c.scale(s * flip, s);
    const w = (i, k) => Math.sin(t * 2.6 - i * 0.55 + ph + k), SK = '#eab894';
    const sa = []; for (let i = 0; i <= 18; i++) sa.push([30 - i * 22, -30 - Math.sin(i * 0.22) * 34 + w(i, 0) * (3 + i * 1.5)]); ribbon(c, sa, 17, 3, C.teal, C.teal2, 'rgba(255,255,240,.75)');
    const sb = []; for (let i = 0; i <= 12; i++) sb.push([24 - i * 20, 12 + w(i, 2) * (3 + i * 1.2) + i * 5]); ribbon(c, sb, 14, 3, C.ochre, C.line);
    const sk = [[-16, 2]]; for (let i = 1; i <= 15; i++) sk.push([-16 - i * 23, 4 + Math.sin(i * 0.42 + t * 2.2 + ph) * (4 + i * 1.8) - i * 2.4]);   // 长裙：从腰接出，越飘越尖
    ribbon(c, sk, 52, 4, '#79b2a6', C.line, 'rgba(255,255,240,.5)'); c.strokeStyle = 'rgba(31,95,106,.7)'; c.lineWidth = 2; for (let k = -1; k <= 1; k += 2) { c.beginPath(); sk.slice(1, 13).forEach((p, i) => { const yy = p[1] + k * (12 - i * 0.8); i ? c.lineTo(p[0], yy) : c.moveTo(p[0], yy); }); c.stroke(); }
    c.fillStyle = 'rgba(240,226,190,.8)'; for (let i = 2; i < 12; i += 2) { c.beginPath(); c.arc(sk[i][0], sk[i][1] - 2, 3.2, 0, TAU); c.fill(); }
    ribbon(c, [[52, -28], [26, -18], [2, -6], [-22, 2]], 36, 30, SK, C.line);                                // 躯干：由肩向腰收
    c.fillStyle = C.red; ribbon(c, [[-6, -14], [-8, -2], [-12, 10]], 10, 10, C.red, C.line);               // 腰带
    c.strokeStyle = C.teal; c.lineWidth = 4; c.beginPath(); c.arc(56, -34, 16, 0.4, 2.2); c.stroke(); c.fillStyle = C.ochre; c.beginPath(); c.arc(56, -17, 4, 0, TAU); c.fill(); lineStroke(c, 1.6); c.stroke();   // 璎珞
    ribbon(c, [[40, -34], [24, -58], [0, -72]], 14, 10, SK, C.line); c.fillStyle = SK; c.beginPath(); c.arc(-6, -74, 7.5, 0, TAU); c.fill(); lineStroke(c, 2.2); c.stroke();
    ribbon(c, [[52, -28], [84, -2 + w(0, 1) * 3], [112, -20]], 15, 11, SK, C.line); c.fillStyle = SK; c.beginPath(); c.arc(116, -22, 8, 0, TAU); c.fill(); lineStroke(c, 2.2); c.stroke(); lotus(c, 120, -26, 0.95);
    const hr = []; for (let i = 0; i <= 8; i++) hr.push([62 - i * 12, -78 + i * 2.5 + w(i, 4) * (2 + i)]); ribbon(c, hr, 18, 3, C.dark, C.line);          // 发尾后扬
    c.fillStyle = SK; c.beginPath(); c.ellipse(80, -54, 20, 23, 0.12, 0, TAU); c.fill(); lineStroke(c, 2.6); c.stroke();
    c.fillStyle = C.dark; c.beginPath(); c.moveTo(60, -58); c.bezierCurveTo(60, -86, 100, -88, 100, -60); c.bezierCurveTo(92, -72, 72, -72, 60, -58); c.fill(); c.beginPath(); c.arc(70, -86, 11, 0, TAU); c.fill(); c.strokeStyle = C.line; c.stroke();
    c.fillStyle = C.ochre; [[78, -82], [86, -78], [92, -72]].forEach(([px, py]) => { c.beginPath(); c.arc(px, py, 2.8, 0, TAU); c.fill(); }); c.fillStyle = C.teal; c.beginPath(); c.arc(70, -97, 3.6, 0, TAU); c.fill();
    c.fillStyle = 'rgba(223,120,96,.8)'; c.beginPath(); c.ellipse(92, -45, 7, 5.5, 0, 0, TAU); c.fill(); c.beginPath(); c.ellipse(68, -45, 6, 5, 0, 0, TAU); c.fill();
    c.strokeStyle = C.line; c.lineWidth = 2.2; c.beginPath(); c.moveTo(80, -64); c.quadraticCurveTo(90, -69, 99, -62); c.moveTo(62, -63); c.quadraticCurveTo(68, -68, 77, -64); c.stroke();
    c.lineWidth = 2.6; c.beginPath(); c.moveTo(83, -57); c.quadraticCurveTo(91, -60, 98, -56); c.moveTo(62, -57); c.quadraticCurveTo(69, -60, 76, -57); c.stroke(); c.fillStyle = C.dark; c.beginPath(); c.arc(91, -57, 2, 0, TAU); c.arc(69, -57, 1.8, 0, TAU); c.fill();
    c.strokeStyle = C.line; c.lineWidth = 1.8; c.beginPath(); c.moveTo(82, -54); c.quadraticCurveTo(86, -46, 82, -43); c.stroke(); c.fillStyle = C.red; c.beginPath(); c.ellipse(80, -36, 4.6, 2.3, 0, 0, TAU); c.fill();
    c.restore();
  }
  // 白鹿（鹿王本生式）：侧身，身子是一整块白，只有轮廓与脊背一线赭点；奔跑用「腾空伸展—收拢」的两拍，前后腿成对错开
  function deer(c, x, y, s, t, ph, col = C.white) {
    const f = t * 5.2 + ph, g = Math.sin(f), jump = Math.max(0, Math.sin(f + 1.1)) * 20;
    c.save(); c.translate(x, y - jump * s); c.rotate(-g * 0.03); c.scale(s, s); c.lineJoin = 'round'; c.lineCap = 'round';
    const leg = (hx, hy, a, front) => {                     // a∈[-1,1]：前摆为正；前腿膝向前弯、后腿膝向后弯
      const th = a * 0.95, kn = [hx + Math.sin(th) * 52, hy + Math.cos(th) * 52], th2 = th + (front ? -1 : 1) * (0.55 + 0.45 * (1 - a * (front ? 1 : -1)) * 0.5), fo = [kn[0] + Math.sin(th2 + (front ? 0.25 : -0.1)) * 56, kn[1] + Math.cos(th2) * 56];
      ribbon(c, [[hx, hy], [kn[0], kn[1]], [fo[0], fo[1]]], 22, 8, col, C.line); c.fillStyle = C.ochre; c.beginPath(); c.ellipse(fo[0] + 3, fo[1] - 2, 8, 4.5, 0.2, 0, TAU); c.fill(); c.strokeStyle = C.line; c.lineWidth = 2; c.stroke(); };
    leg(-56, -78, -g * 0.9, false); leg(-40, -76, g * 0.9 + 0.2, false); leg(50, -80, g * 0.9, true); leg(64, -78, -g * 0.9 + 0.2, true);
    c.beginPath(); c.moveTo(-90, -92); c.bezierCurveTo(-70, -132, 30, -138, 68, -114); c.bezierCurveTo(90, -126, 100, -150, 112, -172); c.bezierCurveTo(124, -190, 150, -190, 160, -174); c.bezierCurveTo(150, -158, 130, -156, 120, -146); c.bezierCurveTo(116, -118, 100, -90, 70, -76); c.bezierCurveTo(28, -56, -30, -56, -64, -66); c.bezierCurveTo(-84, -70, -98, -82, -90, -92); c.closePath();
    c.fillStyle = col; c.fill(); lineStroke(c, 3.4); c.stroke();
    c.fillStyle = C.ochre; for (let i = 0; i < 12; i++) { const q = i / 11, px = lerp(-70, 66, q), py = lerp(-100, -114, Math.sin(q * 2.2)) - 4; c.beginPath(); c.arc(px, py + (q > 0.8 ? (q - 0.8) * 40 : 0), 3.6, 0, TAU); c.fill(); }
    c.strokeStyle = 'rgba(58,24,18,.55)'; c.lineWidth = 1.8; [[-22, -96, -8, -78], [10, -98, 22, -80], [-52, -90, -42, -74]].forEach(([a1, b1, a2, b2]) => { c.beginPath(); c.moveTo(a1, b1); c.quadraticCurveTo((a1 + a2) / 2 + 6, (b1 + b2) / 2, a2, b2); c.stroke(); });
    c.fillStyle = col; lineStroke(c, 3); c.beginPath(); c.moveTo(110, -172); c.quadraticCurveTo(100, -204, 124, -214); c.quadraticCurveTo(124, -192, 124, -172); c.closePath(); c.fill(); c.stroke(); c.fillStyle = C.teal; c.beginPath(); c.moveTo(114, -184); c.quadraticCurveTo(112, -200, 121, -206); c.quadraticCurveTo(120, -194, 120, -184); c.fill();
    c.strokeStyle = C.ochre; c.lineWidth = 5; c.beginPath(); c.moveTo(136, -186); c.quadraticCurveTo(148, -222, 176, -230); c.moveTo(152, -212); c.lineTo(150, -240); c.moveTo(160, -222); c.lineTo(184, -220); c.stroke();
    c.fillStyle = C.ink; c.beginPath(); c.arc(138, -172, 3.4, 0, TAU); c.fill(); c.strokeStyle = C.red; c.lineWidth = 1.8; c.beginPath(); c.arc(138, -172, 6, 0, TAU); c.stroke(); c.fillStyle = C.ink; c.beginPath(); c.ellipse(158, -173, 3, 2.2, 0, 0, TAU); c.fill();
    c.fillStyle = col; c.beginPath(); c.moveTo(-88, -94); c.quadraticCurveTo(-116, -108, -112, -80); c.quadraticCurveTo(-100, -86, -88, -84); c.fill(); lineStroke(c, 2.6); c.stroke();
    c.restore();
  }

  function draw(c, lt) {
    if (!base) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(base, 0, 0);
    // 上栏：风叶（远处小的在前面，带浅色；大的青绿深色）整体向后（左）翻，速度分层
    const rl = rng(285);
    for (let i = 0; i < 26; i++) {
      const sp = 70 + rl() * 120, y0 = TOP + 40 + rl() * (SPLIT - TOP - 100), ln = 60 + rl() * 80, x0 = rl() * (W + 300), k = 0.8 + rl() * 0.4, rot = (rl() - .5) * 0.7, col = rl() < 0.62 ? C.teal : rl() < 0.8 ? C.green : '#c9a23a';
      const x = ((x0 - t * sp) % (W + 300) + (W + 300)) % (W + 300) - 150, y = y0 + Math.sin(t * 1.3 + i) * 10;
      leaf(c, x, y, Math.PI + rot + Math.sin(t * 1.1 + i) * 0.1, ln, col, i % 5 === 0 ? C.line : C.teal2, k);
    }
    apsara(c, 1060, 262, 1.72, 1, t, 0);                                    // 主飞天
    apsara(c, 560, 150, 0.82, -1, t, 2.2);                                   // 远处的小飞天，反向飞
    const rb = rng(31); for (let i = 0; i < 16; i++) { const sp = 60 + rb() * 90, x = (((rb() * (W + 200)) - t * sp * 0.9) % (W + 200) + W + 200) % (W + 200) - 100, y = TOP + 30 + ((rb() * (SPLIT - TOP - 80)) + t * 28 * (0.5 + rb())) % (SPLIT - TOP - 60); bloom(c, x, y, 0.8 + rb() * 0.7, t * (0.6 + rb()) + i, C.white); }
    // 下栏：白鹿领队，小鹿稍后；前后各一个相位
    const run = (t / 6), x1 = 360 + run * 1000, x2 = 160 + run * 940;
    deer(c, x2, GROUND + 22, 0.95, t, 1.6, '#e8dcc2'); deer(c, x1, GROUND + 32, 1.5, t, 0);
    // 奔跑扬起的尘（鹿蹄后面）
    for (let i = 0; i < 12; i++) { const q = ((t * 1.6 + i / 12) % 1), px = x1 - 60 - q * 150 - i * 4, py = GROUND + 30 - q * 40 - (i % 3) * 6; c.fillStyle = `rgba(214,190,150,${(1 - q) * 0.55})`; c.beginPath(); c.arc(px, py, 6 + q * 18, 0, TAU); c.fill(); }
    // 覆盖层＋泥壁相乘
    c.drawImage(over, 0, 0);
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.42; c.drawImage(P.texture('dh_mud', '#d9c6a6', { scale: 0.006, amt: 30, grain: 14, dark: '#9a7a54', seed: 21 }), 0, 0); c.restore();
    // 漂在光里的尘
    const rd = rng(5); for (let i = 0; i < 40; i++) { const x = (rd() * W + t * (6 + rd() * 10)) % W, y = TOP + rd() * (BOT - TOP) + Math.sin(t * 0.6 + i) * 6; c.fillStyle = `rgba(255,244,214,${0.1 + rd() * 0.14})`; c.beginPath(); c.arc(x, y, 1 + rd() * 1.8, 0, TAU); c.fill(); }
  }
  return { draw };
})();
