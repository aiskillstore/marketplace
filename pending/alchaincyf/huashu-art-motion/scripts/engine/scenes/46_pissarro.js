// 毕沙罗（印象派田园）：人是环境的一部分——人物融进树影、田垄、小路；笔触比西斯莱更短、更多向，绿色里有大量橙黄与粉的互补跳动；小路把视线带进深处。
// 题材（新构图）：集市日的乡间小路，两位挑着篮子的农妇和一个赶着小推车的人沿路走来，路两边是开着花的果树，远处一座小教堂。
// 原作锚定（风格，非原画）：天占三分之一、云小而碎；树冠＝一团团短笔的绿、黄绿、橙、粉、淡紫；地面笔触顺着地势（田垄、小路的方向）；人物只有几笔，但有重量与动势。
// 管线：干净的形（天／远景／树／地）→ MEDIUM.broken（短笔、多向）→ 缓存；动态：行人沿路（小画布→broken→贴回）、树冠风动（顶层细碎小笔漂）、云慢漂。
SCENES['46_pissarro'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  let sky, ground, trees, built = false;
  const PATH = [[250, 1100], [520, 880], [820, 700], [1080, 600], [1250, 548]];                  // 小路中线（从近到远）
  const bez = (u) => { const a = PATH, n = a.length - 1, f = u * n, i = Math.min(n - 1, Math.floor(f)), q = f - i; return [lerp(a[i][0], a[i + 1][0], q), lerp(a[i][1], a[i + 1][1], q)]; };
  const widthAt = (y) => 40 + (y - 540) * 0.55;                                                // 路在近处更宽
  function skyPlate() {
    const cv = P.canvas(2400, 560), g = cv.getContext('2d'), r = rng(4);
    const gr = g.createLinearGradient(0, 0, 0, 560); gr.addColorStop(0, '#7fa6d2'); gr.addColorStop(0.6, '#b4cadc'); gr.addColorStop(1, '#efe3c8'); g.fillStyle = gr; g.fillRect(0, 0, 2400, 560);
    for (let k = 0; k < 18; k++) { const x = r() * 2400, y = 40 + r() * 330, s = 0.5 + r() * 0.9; g.save(); g.filter = 'blur(7px)'; for (let j = 0; j < 6; j++) { const dx = (r() - .5) * 150 * s, dy = (r() - .5) * 26 * s, rx = (34 + r() * 50) * s, ry = (16 + r() * 18) * s;
      g.fillStyle = 'rgba(176,176,204,.7)'; g.beginPath(); g.ellipse(x + dx + 6, y + dy + ry * 0.5, rx, ry * 0.9, 0, 0, TAU); g.fill(); g.fillStyle = 'rgba(246,240,226,.95)'; g.beginPath(); g.ellipse(x + dx, y + dy, rx, ry, 0, 0, TAU); g.fill(); g.fillStyle = 'rgba(252,230,184,.5)'; g.beginPath(); g.ellipse(x + dx - rx * 0.2, y + dy - ry * 0.4, rx * 0.55, ry * 0.4, 0, 0, TAU); g.fill(); } g.restore(); }
    return M.broken(cv, { cell: 9, len: 34, wid: 7, passes: 2, angle: () => -0.12, seed: 8, jit: 20, skip: 0.06 });
  }
  function groundPlate() {
    const cv = P.canvas(), g = cv.getContext('2d'), r = rng(9);
    // 远景：丘陵、田野带、小教堂与农舍
    const hg = g.createLinearGradient(0, 430, 0, 560); hg.addColorStop(0, '#9fb4a8'); hg.addColorStop(1, '#8aa27a'); g.fillStyle = hg; g.beginPath(); g.moveTo(0, 520); g.quadraticCurveTo(300, 420, 640, 480); g.quadraticCurveTo(1000, 440, 1300, 470); g.quadraticCurveTo(1640, 420, 1920, 490); g.lineTo(1920, 600); g.lineTo(0, 600); g.fill();
    g.fillStyle = '#b8a890'; g.fillRect(1250, 440, 70, 80); g.fillStyle = '#c9b8a0'; g.fillRect(1320, 458, 50, 62); g.fillStyle = '#8d5a4a'; g.beginPath(); g.moveTo(1240, 440); g.lineTo(1285, 400); g.lineTo(1330, 440); g.fill(); g.beginPath(); g.moveTo(1316, 458); g.lineTo(1345, 430); g.lineTo(1376, 458); g.fill();
    g.fillStyle = '#a89a84'; g.fillRect(1280, 380, 26, 62); g.fillStyle = '#6f6a78'; g.beginPath(); g.moveTo(1274, 382); g.lineTo(1293, 346); g.lineTo(1312, 382); g.fill();
    // 田：两种绿的垄（沿地势：近处宽斜，远处窄横）
    const gg = g.createLinearGradient(0, 540, 0, H); gg.addColorStop(0, '#9bb87a'); gg.addColorStop(1, '#5f8a42'); g.fillStyle = gg; g.fillRect(0, 540, W, H - 540);
    const FP = ['#7fa05a', '#b8c070', '#5f8a42', '#d2c47a', '#8aa86a', '#9a8a5a', '#6f9a56'];
    for (let i = 0; i < 160; i++) { const k = Math.pow(r(), 1.6), y = 556 + k * 540, sc = 0.25 + k * 1.1, x = r() * W, wd = (60 + r() * 220) * sc, ht = (10 + r() * 30) * sc;
      g.fillStyle = FP[(r() * FP.length) | 0]; g.globalAlpha = 0.55; g.beginPath(); g.ellipse(x, y, wd, ht, (r() - .5) * 0.12, 0, TAU); g.fill(); }
    g.globalAlpha = 1;
    // 树影：横过小路与田的淡紫蓝软影
    [[470, 840, 240, 40], [1500, 930, 300, 50], [900, 690, 150, 22]].forEach(([x, y, rx, ry]) => { g.save(); g.filter = 'blur(10px)'; g.fillStyle = 'rgba(86,86,150,.38)'; g.beginPath(); g.ellipse(x, y, rx, ry, -0.06, 0, TAU); g.fill(); g.restore(); });
    // 小路：沿 PATH 画变宽的赭色带，路边有草，路面有车辙
    g.fillStyle = '#c9a778'; g.beginPath(); const L = [], R = [];
    for (let k = 0; k <= 40; k++) { const [x, y] = bez(k / 40), w = widthAt(y); L.push([x - w, y]); R.push([x + w, y]); } L.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); R.reverse().forEach(p => g.lineTo(p[0], p[1])); g.closePath(); g.fill();
    g.strokeStyle = 'rgba(120,86,56,.5)'; g.lineWidth = 6; for (const o of [-0.35, 0.35]) { g.beginPath(); for (let k = 0; k <= 40; k++) { const [x, y] = bez(k / 40); const px = x + o * widthAt(y); k ? g.lineTo(px, y) : g.moveTo(px, y); } g.stroke(); }
    return M.broken(cv, { cell: 9, len: 30, wid: 7, passes: 2, angle: (x, y) => y < 560 ? 0.02 : (Math.abs(x - bez(clamp((1100 - y) / 560))[0]) < widthAt(y) ? -0.75 : 0.1 + Math.sin(x * 0.01) * 0.2), seed: 11, jit: 24, skip: 0.05, warm: [255, 214, 140], cool: [130, 120, 190] });
  }
  function treesPlate() {
    const cv = P.canvas(), g = cv.getContext('2d'), r = rng(31);
    const tree = (x, y, h, kind, seed) => {
      const rr = rng(seed); g.fillStyle = '#6b5a4a'; g.beginPath(); g.moveTo(x - h * 0.03, y); g.lineTo(x - h * 0.012, y - h * 0.55); g.lineTo(x + h * 0.012, y - h * 0.55); g.lineTo(x + h * 0.035, y); g.fill();
      const pal = kind === 'bloom' ? ['#e6b4b0', '#f0d0c0', '#a8c070', '#8aa850', '#f4e4d4', '#c8a8b8'] : ['#86a850', '#b8c060', '#d6a84a', '#5f8a42', '#e0c070', '#4d6b3a'];
      for (let i = 0; i < 70; i++) { const a = rr() * TAU, d = Math.pow(rr(), 0.7) * h * 0.36, cx = x + Math.cos(a) * d * 1.2, cy = y - h * 0.66 + Math.sin(a) * d * 0.88, rx = h * (0.035 + rr() * 0.05), ry = rx * (0.7 + rr() * 0.3);
        const low = Math.sin(a) > 0.2, hi = Math.sin(a) < -0.35;                                   // 下沿阴、上沿亮
        g.fillStyle = low && rr() < 0.7 ? '#4d6b3a' : hi && rr() < 0.6 ? '#f0d878' : pal[(rr() * pal.length) | 0]; g.beginPath(); g.ellipse(cx, cy, rx, ry, rr() * 3, 0, TAU); g.fill(); }
    };
    tree(260, 900, 640, 'bloom', 1); tree(560, 760, 380, 'leaf', 2); tree(1560, 880, 620, 'leaf', 3); tree(1780, 780, 400, 'bloom', 4); tree(1040, 580, 200, 'leaf', 5);
    return M.broken(cv, { cell: 8, len: 22, wid: 7, passes: 2, angle: (x, y) => 0.9 + Math.sin(x * 0.02 + y * 0.017) * 1.1, seed: 13, jit: 34, skip: 0.04, warm: [255, 216, 150], cool: [110, 130, 190], sat: 1.12 });
  }
  function build() { sky = skyPlate(); ground = groundPlate(); trees = treesPlate(); built = true; }
  // 行人（小画布→broken→贴回）：u 沿路位置，face 朝向，basket 篮子，kind 类型
  function walker(c, u, kind, t, ph) {
    const [x, y] = bez(u), s = lerp(0.34, 1.0, (y - 560) / 540), cv = P.scratch('pis_walker'); if (cv.width !== 360) { cv.width = 360; cv.height = 420; } const g = cv.getContext('2d'); g.reset(); g.clearRect(0, 0, 360, 420);
    g.save(); g.translate(180, 380); g.scale(s * 1.6, s * 1.6); const step = Math.sin(t * 5 + ph), bob = Math.abs(step) * 3;
    g.translate(0, -bob);
    g.fillStyle = '#4a4a5a'; g.fillRect(-14, -38, 10, 38 + step * 4); g.fillRect(4, -38, 10, 38 - step * 4);                       // 腿
    const robe = kind === 'a' ? '#5a78a8' : kind === 'b' ? '#a8584a' : '#6f7f4a';
    g.fillStyle = robe; g.beginPath(); g.moveTo(-26, -40); g.quadraticCurveTo(-30, -96, -14, -128); g.lineTo(14, -128); g.quadraticCurveTo(30, -96, 28, -40); g.closePath(); g.fill();   // 衣
    g.fillStyle = '#e8d8c0'; g.beginPath(); g.moveTo(-12, -128); g.lineTo(12, -128); g.lineTo(6, -100); g.lineTo(-6, -100); g.fill();                                              // 围裙/领
    g.fillStyle = '#d8b090'; g.beginPath(); g.arc(0, -142, 12, 0, TAU); g.fill(); g.fillStyle = kind === 'c' ? '#3a3a3a' : '#efe6d4'; g.beginPath(); g.ellipse(0, -152, 14, 5, 0, 0, TAU); g.fill(); g.beginPath(); g.arc(0, -154, 8, Math.PI, 0); g.fill();   // 头与帽
    if (kind !== 'c') { g.strokeStyle = '#4a3a2a'; g.lineWidth = 4; g.beginPath(); g.moveTo(-26, -118); g.quadraticCurveTo(-48, -96, -42, -70); g.stroke(); g.fillStyle = '#b88a4a'; g.beginPath(); g.ellipse(-42, -66, 20, 12, 0, 0, TAU); g.fill(); g.fillStyle = '#d6a84a'; for (let k = 0; k < 4; k++) { g.beginPath(); g.arc(-50 + k * 8, -76, 5, 0, TAU); g.fill(); } }
    else { g.strokeStyle = '#4a3a2a'; g.lineWidth = 5; g.beginPath(); g.moveTo(14, -110); g.lineTo(80, -70); g.stroke(); g.fillStyle = '#8a6a3a'; g.fillRect(60, -64, 70, 36); g.fillStyle = '#6b8a3a'; for (let k = 0; k < 4; k++) { g.beginPath(); g.arc(70 + k * 15, -70, 9, 0, TAU); g.fill(); } g.fillStyle = '#14120f'; g.beginPath(); g.arc(78, -22, 10, 0, TAU); g.arc(120, -22, 10, 0, TAU); g.fill(); }
    g.restore();
    const rep = M.broken(cv, { cell: 5, len: 12, wid: 4.5, passes: 2, angle: (xx, yy) => (yy > 330 ? 0.4 : 1.3), seed: 15, jit: 20, skip: 0.02, sat: 1.08 });
    c.drawImage(rep, x - 180, y - 380);
  }
  function draw(c, lt) {
    if (!built) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(sky, t * 12, 0, W, 560, 0, 0, W, 560);
    c.drawImage(ground, 0, 0);
    // 远景的行人先画（小），再画树，再画近的人，保证层次
    walker(c, lerp(0.66, 0.34, ss(0, 6, t)), 'c', t, 2.0);
    c.drawImage(trees, 0, 0);
    // 树冠风动：顶层再撒一小把随风漂的叶笔
    const r = rng(77); c.save(); c.lineCap = 'round'; for (let i = 0; i < 260; i++) { const tx = [260, 560, 1560, 1780][i % 4], ty = [330, 480, 380, 460][i % 4], a = r() * TAU, d = Math.sqrt(r()) * [230, 140, 220, 150][i % 4], ph = r() * 6;
      const x = tx + Math.cos(a) * d + Math.sin(t * 1.6 + ph) * 5, y = ty + Math.sin(a) * d * 0.8 + Math.cos(t * 1.9 + ph) * 3, col = ['#e9b6b8', '#b8c060', '#f2d2c4', '#86a850', '#d6a84a'][(r() * 5) | 0]; c.strokeStyle = col; c.globalAlpha = 0.85; c.lineWidth = 6; c.beginPath(); c.moveTo(x - 8, y - 3); c.lineTo(x + 8, y + 3); c.stroke(); } c.restore();
    walker(c, lerp(0.5, 0.06, ss(0, 6, t)), 'a', t, 0.0); walker(c, lerp(0.58, 0.16, ss(0, 6, t)), 'b', t, 1.3);
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.2; c.drawImage(P.texture('canvas_pis', '#e8e0cc', { scale: 0.006, amt: 12, grain: 7, seed: 5 }), 0, 0); c.restore();
  }
  return { draw };
})();
