// 瓜尔迪（威尼斯晚期）：低地平线、银灰绿的巨大空气、细长的舢板和小到只剩几点白的人、笔触干而快、边缘松动，像被风吹散。
// 题材（新构图）：清晨的潟湖，两条细长的小船载着货横过水面，远处一座瘦塔和低矮的岛，天占四分之三。
// 原作锚定（fetch_reference.py：《威尼斯潟湖》《大运河与里亚托桥》；第三条搜索命中的是现代照片，已弃用，见 16 号「已知的坑」）：
//   天水一色的银灰绿 #9db0b0→#c9cdbd、暖云边 #e2cfa8、塔与岛赭褐 #8a7a62、船黑褐 #2e2a26、人物＝黑身＋一两点白或红、水面细长横笔。
// 管线：干净的形（天／水／岛塔）→ MEDIUM.broken（细长干笔，低饱和）→ 缓存；动态：云漂、水面逐行位移、船与撑篙人（小画布重绘）、鸟。
SCENES['42_guardi'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const HZ = 700;                                   // 低地平线：天占 65%
  let sky, land, water, built = false;
  function skyPlate() {
    const cv = P.canvas(2500, 720), g = cv.getContext('2d'), r = rng(12);
    const gr = g.createLinearGradient(0, 0, 0, 720); gr.addColorStop(0, '#8fa3a8'); gr.addColorStop(0.55, '#b4c0bb'); gr.addColorStop(1, '#d9d2b4'); g.fillStyle = gr; g.fillRect(0, 0, 2500, 720);
    for (let k = 0; k < 26; k++) { const x = r() * 2500, y = 30 + r() * 520, s = 0.6 + r() * 1.3; g.save(); g.filter = 'blur(12px)'; for (let j = 0; j < 7; j++) { const dx = (r() - .5) * 280 * s, dy = (r() - .5) * 40 * s, rx = (50 + r() * 80) * s, ry = (14 + r() * 18) * s;
      g.fillStyle = `rgba(${r() < 0.5 ? '130,146,152' : '236,222,190'},${0.28 + r() * 0.25})`; g.beginPath(); g.ellipse(x + dx, y + dy, rx, ry, (r() - .5) * 0.1, 0, TAU); g.fill(); } g.restore(); }
    return M.broken(cv, { cell: 10, len: 70, wid: 6, passes: 2, angle: (x, y) => -0.03 + Math.sin(x * 0.003 + y * 0.01) * 0.04, seed: 21, jit: 14, skip: 0.1, sat: 0.9, warm: [238, 214, 160], cool: [120, 138, 160] });
  }
  function landPlate() {
    const cv = P.canvas(), g = cv.getContext('2d');
    // 远岛（长而低）
    g.fillStyle = '#8f8a78'; g.beginPath(); g.moveTo(0, HZ); g.lineTo(0, HZ - 16); g.quadraticCurveTo(200, HZ - 30, 420, HZ - 12); g.quadraticCurveTo(520, HZ - 8, 600, HZ); g.fill();
    g.fillStyle = '#7d786a'; g.beginPath(); g.moveTo(1000, HZ); g.quadraticCurveTo(1120, HZ - 22, 1300, HZ - 14); g.lineTo(1500, HZ - 24); g.quadraticCurveTo(1780, HZ - 18, 1920, HZ - 34); g.lineTo(1920, HZ); g.fill();
    // 瘦塔（右）＋低屋＋木桩
    g.fillStyle = '#85735c'; g.fillRect(1480, HZ - 230, 70, 230); g.fillStyle = '#6b5a46'; g.fillRect(1480, HZ - 230, 18, 230); g.fillStyle = '#9a8670'; g.fillRect(1470, HZ - 246, 90, 18);
    g.fillStyle = '#4a4036'; [[1492, HZ - 190], [1518, HZ - 150], [1494, HZ - 110]].forEach(([x, y]) => g.fillRect(x, y, 14, 28));
    g.fillStyle = '#9a8670'; g.fillRect(1380, HZ - 66, 120, 66); g.fillStyle = '#7a4a3a'; g.beginPath(); g.moveTo(1370, HZ - 66); g.lineTo(1440, HZ - 100); g.lineTo(1510, HZ - 66); g.fill();
    g.fillStyle = '#3a342e'; for (let i = 0; i < 9; i++) g.fillRect(1560 + i * 34, HZ - 12 - (i % 3) * 8, 5, 24);
    // 左前景一角：渔人的木桩与网杆
    g.strokeStyle = '#2e2a26'; g.lineWidth = 7; g.beginPath(); g.moveTo(150, 960); g.lineTo(190, 740); g.stroke(); g.lineWidth = 4; g.beginPath(); g.moveTo(190, 740); g.lineTo(400, 790); g.stroke(); g.beginPath(); g.moveTo(190, 760); g.quadraticCurveTo(260, 900, 400, 800); g.stroke();
    return M.broken(cv, { cell: 7, len: 26, wid: 6, passes: 2, angle: (x, y) => y > 600 && x > 1400 ? 1.45 : 0.04, seed: 23, jit: 14, skip: 0.04, sat: 0.9 });
  }
  function waterPlate() {
    const cv = P.canvas(), g = cv.getContext('2d'), r = rng(31);
    const gr = g.createLinearGradient(0, HZ, 0, H); gr.addColorStop(0, '#b7c0b0'); gr.addColorStop(0.35, '#97a89e'); gr.addColorStop(1, '#5f7470'); g.fillStyle = gr; g.fillRect(0, HZ, W, H - HZ);
    // 天光倒影：长条银色、暖色横带，越近越宽
    for (let i = 0; i < 120; i++) { const k = Math.pow(r(), 1.4), y = HZ + 6 + k * (H - HZ - 10), w = 60 + r() * 300 * (0.3 + k), x = r() * W; g.fillStyle = `rgba(${r() < 0.55 ? '232,232,214' : '200,170,120'},${0.1 + r() * 0.2})`; g.fillRect(x, y, w, 2 + r() * 5 * (0.4 + k)); }
    // 塔与岛的倒影
    g.save(); g.translate(0, HZ * 2); g.scale(1, -1); g.globalAlpha = 0.35; g.filter = 'blur(2px)'; g.drawImage(landCanvas(), 0, 0); g.restore();
    return M.broken(cv, { cell: 9, len: 80, wid: 5, passes: 2, angle: () => 0, seed: 25, jit: 14, skip: 0.06, sat: 0.9, cool: [100, 126, 140], warm: [230, 212, 168] });
  }
  let _landRaw = null; const landCanvas = () => { if (_landRaw) return _landRaw; const cv = P.canvas(), g = cv.getContext('2d'); g.fillStyle = '#6a604e'; g.fillRect(1480, HZ - 230, 70, 230); g.fillRect(1380, HZ - 66, 120, 66); g.fillRect(0, HZ - 16, 600, 16); g.fillRect(1000, HZ - 20, 920, 20); return (_landRaw = cv); };
  function build() { sky = skyPlate(); land = landPlate(); water = waterPlate(); built = true; }
  // 细长舢板＋撑篙人：小画布（600×220）→ broken → 贴回；face 朝向
  function gondola(c, x, y, face, t, ph, scale) {
    const cv = P.scratch('guardi_gon'); if (cv.width !== 640) { cv.width = 640; cv.height = 260; } const g = cv.getContext('2d'); g.reset(); g.clearRect(0, 0, 640, 260);
    g.save(); g.translate(320, 190); g.scale(face * scale, scale); const roll = Math.sin(t * 1.3 + ph) * 0.015; g.rotate(roll);
    g.fillStyle = '#2a2622'; g.beginPath(); g.moveTo(-230, -14); g.quadraticCurveTo(-120, 12, 0, 10); g.quadraticCurveTo(130, 12, 236, -26); g.lineTo(210, -22); g.lineTo(-210, -8); g.closePath(); g.fill();                 // 船身（弯月）
    g.fillStyle = '#3a342e'; g.fillRect(-60, -46, 110, 34); g.fillStyle = '#5a2a2a'; g.fillRect(-60, -52, 110, 8);                                                                                                       // felze 小舱
    g.fillStyle = '#2a2622'; g.fillRect(-20, -20, 8, 12);
    const pole = Math.sin(t * 2.0 + ph);                                                                                                                                                                                  // 撑篙人
    g.fillStyle = '#2a2622'; g.fillRect(146, -100, 22, 84); g.beginPath(); g.arc(157, -112, 11, 0, TAU); g.fill(); g.fillStyle = '#e8e0cc'; g.fillRect(146, -94, 22, 20); g.fillStyle = '#b8402e'; g.fillRect(142, -126, 30, 8);   // 黑身＋白衫＋红帽（几点颜色）
    g.strokeStyle = '#2e2a26'; g.lineWidth = 4; g.lineCap = 'round'; g.beginPath(); g.moveTo(160, -88 - pole * 6); g.lineTo(120 + pole * 36, 56); g.stroke();                                                                       // 篙
    g.restore();
    const rep = M.broken(cv, { cell: 4, len: 13, wid: 3.2, passes: 2, angle: (xx, yy) => (yy > 150 && yy < 215) ? 0.02 : 1.2, seed: 27, jit: 12, skip: 0.02, sat: 0.95 });
    // 倒影：被拉长压暗
    c.save(); c.translate(x - 320, y - 190); c.save(); c.translate(0, 380); c.scale(1, -0.55); c.globalAlpha = 0.28; c.drawImage(rep, 0, 0); c.restore(); c.drawImage(rep, 0, 0); c.restore();
  }
  function draw(c, lt) {
    if (!built) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(sky, t * 14, 0, W, 720, 0, 0, W, 720);
    c.drawImage(land, 0, 0);
    for (let y = HZ; y < H; y += 6) { const k = (y - HZ) / (H - HZ), dx = Math.sin(t * 1.1 + y * 0.07) * (1 + k * 7) + Math.sin(t * 2.4 + y * 0.19) * 1.2 * k; c.drawImage(water, 0, y, W, 6, dx - 24, y, W + 48, 6); }
    gondola(c, lerp(1280, 760, ss(0, 6, t)), 880, -1, t, 0.0, 1.0);
    gondola(c, lerp(260, 680, ss(0, 6, t)), 820, 1, t, 2.1, 0.62);
    // 鸟：几笔
    for (let i = 0; i < 5; i++) { const u = (t * 0.06 + i * 0.19) % 1, x = lerp(-40, 1960, u), y = 220 + Math.sin(u * 9 + i) * 40 + i * 28, f = Math.sin(t * 8 + i) * 7; c.strokeStyle = 'rgba(46,42,38,.85)'; c.lineWidth = 2.6; c.lineCap = 'round'; c.beginPath(); c.moveTo(x - 12, y + f); c.quadraticCurveTo(x - 4, y - 6, x, y); c.quadraticCurveTo(x + 4, y - 6, x + 12, y + f); c.stroke(); }
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.24; c.drawImage(P.texture('canvas_guardi', '#e8e0cc', { scale: 0.006, amt: 12, grain: 7, seed: 8 }), 0, 0); c.restore();
  }
  return { draw };
})();
