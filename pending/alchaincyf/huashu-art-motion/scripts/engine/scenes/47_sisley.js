// 西斯莱（印象派风景）：天占大半、积云有暖白与淡紫灰的阴面、水面把房子拖成碎笔倒影、整幅是一笔一笔短弯笔，没有轮廓线。
// 题材（新构图）：涨水后的村口，一位摆渡人撑船载着一只木箱穿过水面，左边是半淹的客栈，右边是光秃的白杨与电线杆。
// 原作锚定（fetch_reference.py：《路维希安的雪》《马尔利港的洪水》《塞纳河上的船》）：天 #8fb0d0→#e9dcc0、云白 #f2ecde／阴 #aab0c4／暖 #f8e4b8、
//   水 #9aa89c＋倒影、屋墙赭黄 #d6bd86、屋顶石板 #6d7684、近景笔触宽而横、远处窄而碎；暖亮处偏黄粉，阴暗处偏冷紫。
// 管线：干净的形（天／水／景）→ MEDIUM.broken 各自重画成笔触（缓存）→ 动态：云慢漂、水面逐行位移＋涟漪、摆渡船与撑篙。
SCENES['47_sisley'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const WL = 540, BASE = 722;                            // 水面起点（远岸脚）与房脚吃水线
  let sky, water, scene, built = false;
  function skyPlate() {
    const cv = P.canvas(2600, 600), g = cv.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 600); gr.addColorStop(0, '#6a98c8'); gr.addColorStop(0.55, '#a8c0d8'); gr.addColorStop(1, '#ebdfc2'); g.fillStyle = gr; g.fillRect(0, 0, 2600, 600);
    const r = rng(17);
    const cloud = (x, y, s) => {
      const blobs = Array.from({ length: 9 }, () => [x + (r() - .5) * 300 * s, y + (r() - .5) * 60 * s, (50 + r() * 70) * s, (30 + r() * 36) * s]);
      g.save(); g.filter = 'blur(10px)';
      blobs.forEach(([bx, by, rx, ry]) => { g.fillStyle = 'rgba(166,170,196,.75)'; g.beginPath(); g.ellipse(bx + 8 * s, by + ry * 0.55, rx * 1.02, ry * 0.9, 0, 0, TAU); g.fill(); });                  // 阴面：淡紫灰，压在下
      blobs.forEach(([bx, by, rx, ry]) => { g.fillStyle = 'rgba(244,238,224,.95)'; g.beginPath(); g.ellipse(bx, by, rx, ry, 0, 0, TAU); g.fill(); });                                                 // 本体：暖白
      blobs.forEach(([bx, by, rx, ry]) => { g.fillStyle = 'rgba(252,232,186,.55)'; g.beginPath(); g.ellipse(bx - rx * 0.2, by - ry * 0.45, rx * 0.6, ry * 0.4, 0, 0, TAU); g.fill(); });             // 受光：暖黄
      g.restore();
    };
    [[260, 160, 1.5], [820, 110, 1.2], [1320, 190, 1.7], [1900, 120, 1.3], [2380, 210, 1.5], [620, 330, 0.9], [1560, 380, 0.8], [2100, 400, 0.9], [60, 380, 0.8]].forEach(([x, y, s]) => cloud(x, y, s));
    return M.broken(cv, { cell: 10, len: 54, wid: 10, passes: 2, angle: (x, y) => -0.06 + Math.sin(x * 0.004) * 0.05, seed: 3, jit: 18, skip: 0.06 });
  }
  function above(g) {      // 水面之上的东西：远岸、客栈、电线杆、白杨
    const r = rng(23);
    // 远岸一带：低矮房屋＋灌木，偏雾蓝灰（空气透视）
    g.fillStyle = '#9fa9a8'; g.fillRect(0, 486, W, 60);
    [[700, 470, 80, 56, '#b9a58a'], [790, 480, 60, 44, '#a99a86'], [880, 462, 100, 66, '#b7a690'], [1010, 476, 70, 50, '#a99a86'], [1120, 470, 120, 58, '#b9a58a']].forEach(([x, y, w, h, col], i) => { g.fillStyle = col; g.fillRect(x, y, w, h); g.fillStyle = '#7d7f8a'; g.beginPath(); g.moveTo(x - 6, y); g.lineTo(x + w / 2, y - 24); g.lineTo(x + w + 6, y); g.fill(); });
    g.fillStyle = '#7f8e72'; for (let i = 0; i < 40; i++) { g.beginPath(); g.ellipse(560 + r() * 1300, 520 + r() * 20, 30 + r() * 30, 16 + r() * 14, 0, 0, TAU); g.fill(); }
    // 客栈（左）：两个立面——正面赭黄、侧面阴面更暗；陡屋顶＋老虎窗；一层是浅色招牌带（不写字）
    const fx = 40, fw = 470, top = 250, sideW = 150;
    g.fillStyle = '#d8bf88'; g.fillRect(fx, top, fw, BASE - top);
    g.fillStyle = '#b8a070'; g.beginPath(); g.moveTo(fx + fw, top); g.lineTo(fx + fw + sideW, top + 40); g.lineTo(fx + fw + sideW, BASE - 6); g.lineTo(fx + fw, BASE); g.fill();
    g.fillStyle = '#6a7482'; g.beginPath(); g.moveTo(fx - 20, top + 6); g.lineTo(fx + fw * 0.45, top - 130); g.lineTo(fx + fw + sideW + 20, top + 36); g.lineTo(fx + fw + 8, top + 18); g.lineTo(fx + fw * 0.45, top - 96); g.closePath(); g.fill();
    g.fillStyle = '#4e5766'; g.beginPath(); g.moveTo(fx + fw * 0.45, top - 130); g.lineTo(fx + fw + sideW + 20, top + 36); g.lineTo(fx + fw + sideW, top + 50); g.lineTo(fx + fw * 0.45, top - 100); g.fill();
    g.fillStyle = '#6a7482'; g.fillRect(fx + 270, top - 40, 70, 62); g.fillStyle = '#4e5766'; g.beginPath(); g.moveTo(fx + 262, top - 40); g.lineTo(fx + 305, top - 76); g.lineTo(fx + 348, top - 40); g.fill(); g.fillStyle = '#3a4150'; g.fillRect(fx + 286, top - 26, 38, 40);
    [[fx + 40, top + 60], [fx + 150, top + 60], [fx + 260, top + 60], [fx + 370, top + 60]].forEach(([x, y]) => { g.fillStyle = '#7a8a86'; g.fillRect(x - 10, y, 18, 96); g.fillRect(x + 62, y, 18, 96); g.fillStyle = '#3d4348'; g.fillRect(x + 8, y + 4, 54, 90); g.fillStyle = 'rgba(210,225,235,.55)'; g.fillRect(x + 12, y + 8, 46, 36); });
    g.fillStyle = '#efe3bd'; g.fillRect(fx, top + 200, fw, 56); g.fillStyle = '#c8b27a'; g.fillRect(fx, top + 256, fw, 6);                         // 招牌带
    [[fx + 60, top + 275], [fx + 220, top + 275]].forEach(([x, y]) => { g.fillStyle = '#7a8a86'; g.fillRect(x - 8, y, 14, 150); g.fillRect(x + 58, y, 14, 150); g.fillStyle = '#31373c'; g.fillRect(x + 6, y + 4, 52, 140); });   // 一层的窗
    g.fillStyle = '#6b4d34'; g.fillRect(fx + 360, top + 290, 70, 132); g.fillStyle = '#2a2420'; g.fillRect(fx + 368, top + 300, 54, 120);          // 门（半淹）
    // 白杨：细长的光秃树，枝丫上挑
    const poplar = (x, base, hgt, seed) => { const rr = rng(seed); g.strokeStyle = '#7d7566'; g.lineCap = 'round'; g.lineWidth = 11; g.beginPath(); g.moveTo(x, base); g.lineTo(x + 6, base - hgt); g.stroke();
      for (let k = 0; k < 22; k++) { const y = base - hgt * (0.18 + rr() * 0.8), side = rr() < 0.5 ? -1 : 1, L = 60 + rr() * 110 * (1 - (base - y) / hgt * 0.6); g.lineWidth = 3 + rr() * 3; g.beginPath(); g.moveTo(x + 3, y); g.quadraticCurveTo(x + side * L * 0.4, y - L * 0.5, x + side * L * 0.55, y - L); g.stroke(); } };
    poplar(1600, BASE + 20, 560, 5); poplar(1740, BASE + 60, 500, 6); poplar(1830, BASE + 30, 430, 7);
    // 电线杆
    g.fillStyle = '#6a5d4e'; g.fillRect(1292, 160, 18, BASE - 150); g.fillRect(1250, 190, 102, 10); g.strokeStyle = '#6a5d4e'; g.lineWidth = 3; g.beginPath(); g.moveTo(1250, 194); g.quadraticCurveTo(900, 250, 600, 214); g.moveTo(1352, 194); g.quadraticCurveTo(1650, 240, 1920, 200); g.stroke();
  }
  function build() {
    sky = skyPlate();
    // 干净的景（透明底）
    const sp = P.canvas(), sg = sp.getContext('2d'); above(sg);
    // 水：底色＋倒影（景的竖向镜像，压暗压冷）＋天光碎片
    const wp = P.canvas(), wg = wp.getContext('2d'); const gr = wg.createLinearGradient(0, WL, 0, H); gr.addColorStop(0, '#c4cbc0'); gr.addColorStop(0.4, '#9fb0aa'); gr.addColorStop(1, '#788a82'); wg.fillStyle = gr; wg.fillRect(0, WL, W, H - WL);
    wg.save(); wg.beginPath(); wg.rect(0, WL, W, H - WL); wg.clip(); wg.translate(0, BASE * 2 - 2); wg.scale(1, -1); wg.globalAlpha = 0.62; wg.filter = 'blur(3px) brightness(.82) saturate(.9)'; wg.drawImage(sp, 0, 0); wg.restore();
    const r = rng(41); wg.globalAlpha = 1; for (let i = 0; i < 90; i++) { const x = r() * W, y = WL + 30 + r() * (H - WL), w = 40 + r() * 190; wg.fillStyle = `rgba(${r() < 0.6 ? '236,236,224' : '150,170,176'},${0.12 + r() * 0.2})`; wg.fillRect(x, y, w, 3 + r() * 5); }
    water = M.broken(wp, { cell: 11, len: 70, wid: 8, passes: 2, angle: () => 0, seed: 5, jit: 16, skip: 0.04, cool: [96, 120, 156], warm: [236, 222, 176] });
    scene = M.broken(sp, { cell: 8, len: 26, wid: 8, passes: 2, angle: (x, y) => x < 700 && y < 330 ? (x < 280 ? -0.5 : 0.5) : (x > 1500 ? 1.45 : (x > 1270 && x < 1330 && y < 740 ? 1.57 : (y < 520 ? 0.02 : 1.5))), seed: 9, jit: 18, skip: 0.04 });
    built = true;
  }
  function boat(c, t) {
    const u = ss(0, 6, t), X = lerp(1380, 840, u), Y = 842 + Math.sin(t * 1.5) * 3, tilt = Math.sin(t * 1.5 + 1) * 0.025, pole = Math.sin(t * 2.2) * 0.5 + 0.5;
    const cvs = P.scratch('sisley_boat'); if (cvs.width !== 520) { cvs.width = 520; cvs.height = 360; } const cg = cvs.getContext('2d'); cg.reset(); cg.clearRect(0, 0, 520, 360);
    const x = 260, y = 230, cc = c; c = cg;
    // 倒影（先画，暗、窄、被水纹打碎）
    c.save(); c.translate(x, y + 40); c.scale(1, -0.5); c.globalAlpha = 0.28; c.fillStyle = '#2d2a28'; c.beginPath(); c.moveTo(-130, 0); c.quadraticCurveTo(0, 30, 130, 0); c.lineTo(100, -36); c.lineTo(-100, -36); c.fill(); c.fillRect(-8, -150, 16, 114); c.restore();
    c.save(); c.translate(x, y); c.rotate(tilt);
    c.fillStyle = '#3a2f2a'; c.beginPath(); c.moveTo(-150, -8); c.quadraticCurveTo(-110, 34, 0, 36); c.quadraticCurveTo(110, 34, 150, -14); c.lineTo(120, -30); c.lineTo(-120, -28); c.closePath(); c.fill();
    c.fillStyle = '#6d5a42'; c.beginPath(); c.moveTo(-150, -8); c.lineTo(-120, -28); c.lineTo(120, -30); c.lineTo(150, -14); c.lineTo(110, -8); c.lineTo(-110, -4); c.closePath(); c.fill();
    c.fillStyle = '#c9b88a'; c.beginPath(); c.moveTo(26, -26); c.quadraticCurveTo(20, -88, 70, -96); c.quadraticCurveTo(122, -88, 116, -26); c.closePath(); c.fill(); c.strokeStyle = '#6b5a3a'; c.lineWidth = 4; c.beginPath(); c.moveTo(48, -92); c.quadraticCurveTo(70, -80, 94, -92); c.stroke();    // 麻袋
    // 摆渡人：深色身形，白帽，竿从右手斜入水
    c.fillStyle = '#2a3340'; c.beginPath(); c.moveTo(-52, -26); c.quadraticCurveTo(-60, -90, -46, -126); c.lineTo(-18, -126); c.quadraticCurveTo(-8, -90, -14, -26); c.fill();
    c.fillStyle = '#d9b48c'; c.beginPath(); c.arc(-32, -142, 13, 0, TAU); c.fill(); c.fillStyle = '#e8e0cc'; c.beginPath(); c.ellipse(-32, -152, 20, 7, 0, 0, TAU); c.fill();
    const px = -14 + pole * 8, ang = -0.5 - pole * 0.15; c.strokeStyle = '#4a3a2a'; c.lineWidth = 6; c.lineCap = 'round'; c.beginPath(); c.moveTo(-18, -104 - pole * 6); c.lineTo(px + Math.cos(ang) * -210 * -1, 30 + pole * 14 + 0); c.stroke();
    c.restore();
    const rep = M.broken(cvs, { cell: 7, len: 18, wid: 6, passes: 2, angle: (xx, yy) => (yy > 250 ? 0 : 1.2), seed: 12, jit: 14, skip: 0.02, base: true });
    cc.drawImage(rep, X - 260, Y - 230);
    c = cc; const x2 = X, y2 = Y;
    // 船行水纹：船尾拖出两道渐开的 V
    c.save(); c.strokeStyle = 'rgba(244,240,226,.55)'; c.lineWidth = 3; c.lineCap = 'round'; for (let k = 0; k < 3; k++) { const q = ((t * 0.5 + k / 3) % 1); c.globalAlpha = (1 - q) * 0.8; c.beginPath(); c.ellipse(x2 + 90 + q * 220, y2 + 34, 40 + q * 110, 6 + q * 14, 0, Math.PI * 0.05, Math.PI * 0.95); c.stroke(); } c.restore();
  }
  function draw(c, lt) {
    if (!built) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(sky, t * 18, 0, W, 600, 0, 0, W, 600);                                   // 云慢漂
    c.fillStyle = '#ebdfc2'; c.fillRect(0, 560, W, WL - 540 + 40);
    // 水：逐行位移，越近越大（倒影被水纹拉碎）
    for (let y = WL; y < H; y += 6) { const k = (y - WL) / (H - WL), dx = Math.sin(t * 1.3 + y * 0.09) * (1.5 + k * 9) + Math.sin(t * 2.7 + y * 0.21) * 1.5 * k; c.drawImage(water, 0, y, W, 6, dx - 24, y, W + 48, 6); }
    c.drawImage(scene, 0, 0);
    boat(c, t);
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.22; c.drawImage(P.texture('canvas_sisley', '#e8e0cc', { scale: 0.006, amt: 12, grain: 7, seed: 3 }), 0, 0); c.restore();       // 画布纹
  }
  return { draw };
})();
