// 雷诺阿（印象派，人间的光）：树叶筛下的斑驳光——暖黄的亮斑、蓝紫的影；人都是一团团粉彩的色点，脸颊泛红，边缘融进周围；没有黑线，黑色衣服也是深蓝紫。
// 题材（新构图）：午后树下的露天舞场，近处一对舞者旋转，中景桌边人群说笑，光斑缓缓挪动。
// 原作锚定（风格，非原画）：亮斑 #f6e4a0／影 #6f78b8、肤色暖粉 #eab090 带红晕、衣料粉蓝白 #e8c8d0 #a8b8dc #f4f0e4、黑衣＝#2c3050、草帽黄 #e6c070、地面碎笔多向；所有边缘被光吃掉。
// 管线：静底（树冠＋地＋远景人群＋桌）→ MEDIUM.broken → 缓存；光斑层（暖亮／冷影软笔）单独 broken 缓存、两份错位叠加做摇曳；近景舞者每帧小画布重绘；中景人群每个轻微摇摆（小画布）。
SCENES['45_renoir'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  let base, crowdLayer, lightA, lightB, built = false;
  // 一个人（色点化）：x,y 脚底；s 比例。女：窄肩、收腰、钟形长裙、小头戴帽；男：深蓝紫礼服、礼帽。reach=[dx,dy] 局部坐标，指定一只手去哪（相拥舞）
  function person(g, x, y, s, o) {
    const { dress = '#e8c8d0', trim = '#f4f0e4', hat = null, skin = '#eab090', lean = 0, arms = 0, dark = false, hair = '#8a5a3a', reach = null } = o;
    g.save(); g.translate(x, y); g.scale(s, s); g.rotate(lean);
    const body = dark ? '#2c3050' : dress, lit = dark ? '#4a4f82' : trim, sh = dark ? '#1c1f38' : 'rgba(110,100,150,.45)';
    // 裙/下装：女＝钟形长裙（左亮右影），男＝直筒裤袍
    if (dark) { g.fillStyle = body; g.beginPath(); g.moveTo(-15, -72); g.lineTo(-17, -4); g.lineTo(-3, -4); g.lineTo(0, -34); g.lineTo(3, -4); g.lineTo(17, -4); g.lineTo(15, -72); g.closePath(); g.fill();
      g.fillStyle = body; g.beginPath(); g.moveTo(-15, -108); g.quadraticCurveTo(-21, -96, -17, -52); g.lineTo(17, -52); g.quadraticCurveTo(21, -96, 15, -108); g.closePath(); g.fill(); g.fillStyle = lit; g.globalAlpha = 0.5; g.fillRect(-15, -108, 6, 54); g.globalAlpha = 1;
      g.fillStyle = '#e8e0ea'; g.beginPath(); g.moveTo(-4, -108); g.lineTo(4, -108); g.lineTo(1, -80); g.closePath(); g.fill(); }
    else { const gr = g.createLinearGradient(-40, 0, 40, 0); gr.addColorStop(0, trim); gr.addColorStop(0.4, body); gr.addColorStop(1, sh); 
      g.fillStyle = gr; g.beginPath(); g.moveTo(-10, -104); g.quadraticCurveTo(-13, -84, -9, -68); g.quadraticCurveTo(-34, -34, -44, -3); g.quadraticCurveTo(0, 6, 44, -3); g.quadraticCurveTo(34, -34, 9, -68); g.quadraticCurveTo(13, -84, 10, -104); g.closePath(); g.fill();
      g.strokeStyle = sh; g.lineWidth = 3; g.globalAlpha = 0.5; [[-10, -22], [6, -20], [20, -18]].forEach(([u, v]) => { g.beginPath(); g.moveTo(u * 0.3, -66); g.quadraticCurveTo(u + 4, -36, u * 1.7 + 4, v); g.stroke(); }); g.globalAlpha = 1;
      g.fillStyle = trim; g.fillRect(-10, -72, 20, 5); g.fillStyle = '#c85a6a'; g.fillRect(-10, -70, 20, 2); }
    // 手臂：上臂下垂，前臂抬到 arms 指定高度；reach 时一只手伸向目标
    const sl = dark ? body : (dress), hx = 20 + arms * 12, hy = -70 - arms * 18;
    g.strokeStyle = sl; g.lineCap = 'round'; g.lineWidth = 8; g.beginPath(); g.moveTo(-10, -100); g.lineTo(-20 - arms * 4, -80); g.lineTo(-hx, hy);
    if (reach) { g.moveTo(10, -100); g.lineTo(22, -84); g.lineTo(reach[0], reach[1]); } else { g.moveTo(10, -100); g.lineTo(20 + arms * 4, -80); g.lineTo(hx, hy); } g.stroke();
    g.fillStyle = skin; g.beginPath(); g.arc(-hx, hy, 4.2, 0, TAU); g.arc(reach ? reach[0] : hx, reach ? reach[1] : hy, 4.2, 0, TAU); g.fill();
    // 颈、头（小）、脸颊红晕、发
    g.fillStyle = skin; g.fillRect(-3.4, -117, 6.8, 11); g.beginPath(); g.ellipse(0, -126, 9.4, 11, 0, 0, TAU); g.fill();
    g.fillStyle = 'rgba(214,90,84,.38)'; g.beginPath(); g.arc(4.5, -122, 4.4, 0, TAU); g.fill();
    g.fillStyle = hair; g.beginPath(); g.ellipse(-1.5, -130, 9.6, 8, 0, Math.PI * 0.95, Math.PI * 2.05); g.fill(); if (!dark) { g.beginPath(); g.arc(-8, -122, 5, 0, TAU); g.fill(); }
    g.fillStyle = '#3a2a30'; g.fillRect(4, -127, 1.8, 1.8); g.fillStyle = '#b05a54'; g.fillRect(3, -120, 4.2, 1.4);
    if (hat === 'straw') { g.fillStyle = '#e6c070'; g.beginPath(); g.ellipse(0, -136, 21, 5.6, 0, 0, TAU); g.fill(); g.beginPath(); g.ellipse(0, -140, 11, 8, 0, Math.PI, TAU); g.fill(); g.fillStyle = '#c85a6a'; g.fillRect(-11, -140, 22, 3.4); }
    else if (hat === 'top') { g.fillStyle = '#2c3050'; g.fillRect(-9, -153, 18, 19); g.fillRect(-14, -136, 28, 3.6); }
    g.restore();
  }
  function basePlate() {
    const cv = P.canvas(), g = cv.getContext('2d'), r = rng(5);
    // 天光漏口＋树冠：大片深绿蓝影＋暖绿
    g.fillStyle = '#9db8a0'; g.fillRect(0, 0, W, H);
    const gr = g.createLinearGradient(0, 0, 0, 460); gr.addColorStop(0, '#5f7f6a'); gr.addColorStop(1, '#a8b890'); g.fillStyle = gr; g.fillRect(0, 0, W, 460);
    for (let i = 0; i < 160; i++) { const x = r() * W, y = r() * 420, rx = 70 + r() * 150, ry = 40 + r() * 80; g.fillStyle = r() < 0.5 ? 'rgba(54,86,70,.55)' : r() < 0.7 ? 'rgba(170,196,120,.5)' : 'rgba(236,224,150,.4)'; g.beginPath(); g.ellipse(x, y, rx, ry, r(), 0, TAU); g.fill(); }
    for (let i = 0; i < 40; i++) { const x = r() * W, y = r() * 330, rx = 12 + r() * 34, ry = 8 + r() * 20; g.fillStyle = 'rgba(190,214,236,.8)'; g.beginPath(); g.ellipse(x, y, rx, ry, r(), 0, TAU); g.fill(); }                    // 叶隙里透出的天
    // 树干
    [[260, 470, 70], [1060, 450, 60], [1700, 470, 80]].forEach(([x, y, w]) => { const tg = g.createLinearGradient(x - w, 0, x + w, 0); tg.addColorStop(0, '#6f6a8a'); tg.addColorStop(0.5, '#a89a8a'); tg.addColorStop(1, '#5c5878'); g.fillStyle = tg; g.fillRect(x - w / 2, 0, w, y + 80); });
    // 地：沙土色，明暗斑
    const ggr = g.createLinearGradient(0, 470, 0, H); ggr.addColorStop(0, '#c8b890'); ggr.addColorStop(1, '#b0a07c'); g.fillStyle = ggr; g.fillRect(0, 470, W, H - 470);
    // 桌与远景人群（色点人）
    const T = (x, y, w) => { g.fillStyle = '#e8e0d0'; g.beginPath(); g.ellipse(x, y, w, w * 0.22, 0, 0, TAU); g.fill(); g.fillStyle = '#a89a8a'; g.fillRect(x - 3, y, 6, w * 0.5); };
    [[560, 640, 120], [1180, 620, 110], [1480, 700, 130], [820, 560, 90]].forEach(([x, y, w]) => T(x, y, w));
    const cv2 = P.canvas(), g2 = cv2.getContext('2d');
    const crowd = [[430, 640, 0.9, '#a8b8dc', 'straw'], [520, 676, 0.95, '#e8c8d0', null], [620, 650, 0.9, '#f4f0e4', 'straw'], [700, 662, 0.9, '#2c3050', 'top'], [1090, 640, 0.85, '#e8c8d0', 'straw'], [1190, 650, 0.88, '#a8b8dc', null], [1280, 636, 0.85, '#2c3050', 'top'],
      [1400, 720, 1.0, '#f0d6dc', 'straw'], [1500, 730, 1.02, '#2c3050', 'top'], [1590, 716, 1.0, '#a8c8dc', null], [780, 590, 0.7, '#e8c8d0', 'straw'], [880, 596, 0.7, '#a8b8dc', null], [330, 600, 0.75, '#f4f0e4', null]];
    crowd.forEach(([x, y, s, c, h], i) => person(g2, x, y, s, { dress: c, hat: h, dark: c === '#2c3050', lean: Math.sin(i * 1.7) * 0.08, arms: (i % 3) * 0.25 }));
    crowdLayer = M.broken(cv2, { cell: 4, len: 12, wid: 4.2, passes: 2, angle: (x, y) => 1.25 + Math.sin(x * 0.05) * 0.3, seed: 19, jit: 26, skip: 0.02, sat: 1.12, warm: [255, 226, 170], cool: [130, 130, 200] });
    return M.broken(cv, { cell: 7, len: 22, wid: 7, passes: 2, angle: (x, y) => y < 460 ? 0.7 + Math.sin(x * 0.01 + y * 0.013) * 0.35 : 0.08 + Math.sin(x * 0.012 + y * 0.01) * 0.3, seed: 11, jit: 30, skip: 0.04, warm: [255, 226, 160], cool: [120, 126, 196], sat: 1.12 });
  }
  function lightPlate(seed) {
    const cv = P.canvas(), g = cv.getContext('2d'), r = rng(seed); g.clearRect(0, 0, W, H);
    for (let i = 0; i < 90; i++) { const x = r() * W, y = 440 + r() * 600, rx = 26 + r() * 80, ry = 12 + r() * 30; g.fillStyle = r() < 0.62 ? 'rgba(252,232,150,.85)' : 'rgba(96,106,176,.6)'; g.beginPath(); g.ellipse(x, y, rx, ry, (r() - .5) * 0.6, 0, TAU); g.fill(); }
    return M.broken(cv, { cell: 8, len: 24, wid: 8, passes: 1, angle: () => -0.3, seed: seed + 3, jit: 24, skip: 0.1, warm: [255, 238, 170], cool: [96, 110, 190], base: false });
  }
  function build() { base = basePlate(); lightA = lightPlate(21); lightB = lightPlate(47); built = true; }
  // 近景舞者：小画布整体重绘（两人，随旋转交换位置）
  function dancers(c, t) {
    const cv = P.scratch('renoir_dance'); if (cv.width !== 760) { cv.width = 760; cv.height = 680; } const g = cv.getContext('2d'); g.reset(); g.clearRect(0, 0, 760, 680);
    const a = t * 1.6, cx = 380, cy = 660, sway = Math.sin(a) * 0.05, S2 = 2.5;
    const A = [cx + 18 + Math.sin(a) * 14, cy + Math.cos(a) * 6], B = [cx - 52 + Math.sin(a) * 6, cy - 10];            // 女在前、男在后左：圆舞里她旋出，他半步退后
    const hold = [(A[0] + B[0]) / 2 + 40, A[1] - 205];                                                              // 两人相握的手
    const loc = (p, d) => [(hold[0] - p[0]) / S2 + d[0], (hold[1] - p[1]) / S2 + d[1]];
    const pa = { dress: '#f4d4dc', trim: '#fff8ee', hat: 'straw', lean: 0.12 + sway, arms: 0.1, reach: loc(A, [0, 0]) }, pb = { dress: '#2c3050', dark: true, hat: 'top', lean: -0.06 + sway, arms: 0.1, skin: '#e2a888', hair: '#4a3a2a', reach: loc(B, [-10, 18]) };
    person(g, B[0], B[1], S2, pb); person(g, A[0], A[1], S2, pa);
    const rep = M.broken(cv, { cell: 5, len: 15, wid: 5, passes: 2, angle: (x, y) => 1.3 + Math.sin(x * 0.04) * 0.3, seed: 31, jit: 24, skip: 0.02, sat: 1.1, warm: [255, 226, 170], cool: [130, 130, 200] });
    c.drawImage(rep, 420, 340);
  }
  function draw(c, lt) {
    if (!built) build();
    const t = clamp(lt, 0, 6);
    c.drawImage(base, 0, 0);
    const q = 0.5 + 0.5 * Math.sin(t * 1.3), lights = (k) => { c.save(); c.globalAlpha = k * (0.55 * (1 - q) + 0.1); c.drawImage(lightA, Math.sin(t * 0.7) * 10, Math.cos(t * 0.6) * 6); c.globalAlpha = k * (0.55 * q + 0.1); c.drawImage(lightB, -Math.sin(t * 0.6) * 10, Math.cos(t * 0.8) * 6); c.restore(); };
    lights(1);                                  // 光斑落在地上
    c.drawImage(crowdLayer, 0, 0);              // 人站在光里
    lights(0.28);                               // 少量光斑再落到人身上：衣服上有碎光，但人不被盖没
    dancers(c, t);
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.2; c.drawImage(P.texture('canvas_renoir', '#ece2cc', { scale: 0.006, amt: 12, grain: 7, seed: 12 }), 0, 0); c.restore();
  }
  return { draw };
})();
