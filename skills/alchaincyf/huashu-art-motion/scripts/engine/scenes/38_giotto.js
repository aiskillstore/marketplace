// 乔托（斯克罗威尼礼拜堂湿壁画）：群青天、重量感的袍、视线连接人物、斜置的建筑体块、灰泥与一天的活接缝。
// 题材（新构图，不搬名作）：码头仓库门口，两位搬运工把一只大木箱交接，第三人低头看着箱角。
// 原作锚定（scripts/analyze/fetch_reference.py 拉的公版图，色值与签名见 配方卡）：群青天 #3a5a9a→#8fa4c8、土红/赭/橄榄绿袍、
//   灰粉建筑 #c9b9ae、金边装饰带、人物视线互相咬合、衣褶大块明暗；整体粉白哑光。
// 管线：plate（干净的形：天→岩坡→建筑→人→箱）→ MEDIUM.fresco（轻糊＋石灰罩＋灰泥相乘＋针孔接缝）→ 装饰边框 → 动作。
SCENES['38_giotto'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  let plate, pg;
  const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };

  function sky(g) {
    const gr = g.createLinearGradient(0, 0, 0, 620); gr.addColorStop(0, '#2347a0'); gr.addColorStop(0.5, '#3f68b8'); gr.addColorStop(1, '#a9c0e6');
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
    // 群青是一层层罩的：大尺度斜向软斑（fbm），不是横条
    const r = rng(11);
    for (let i = 0; i < 140; i++) { const x = r() * W, y = r() * 600, rx = 90 + r() * 260, ry = 24 + r() * 70; g.save(); g.translate(x, y); g.rotate(-0.25 + (r() - .5) * 0.5); g.filter = 'blur(14px)';
      g.fillStyle = `rgba(${r() < 0.55 ? '24,52,132' : '170,190,232'},${0.06 + r() * 0.09})`; g.beginPath(); g.ellipse(0, 0, rx, ry, 0, 0, TAU); g.fill(); g.restore(); }
    g.filter = 'none';
    // 金星点（原作天幕有星）
    for (let i = 0; i < 26; i++) { const x = 60 + r() * (W - 120), y = 40 + r() * 330, s = 5 + r() * 4; g.fillStyle = 'rgba(224,190,100,.85)'; g.beginPath();
      for (let k = 0; k < 8; k++) { const a = k / 8 * TAU, rr = k % 2 ? s * 0.4 : s; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fill(); }
  }
  function rocks(g) {                    // 乔托的岩坡：斜向的大块面，亮面朝左上，暗面朝下，边缘有「梯田」台阶
    const poly = (pts, c0, c1) => { const gr = g.createLinearGradient(pts[0][0], pts[0][1], pts[2][0], pts[2][1] + 120); gr.addColorStop(0, c0); gr.addColorStop(1, c1);
      g.fillStyle = gr; g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.fill(); M.outline(g, [...pts, pts[0]], { w: [2, 3.4, 2], col: '#6e5a4a', a: 0.6 }); };
    poly([[0, 420], [340, 300], [620, 410], [700, 640], [0, 700]], '#c4b79c', '#8e8068');
    poly([[0, 560], [420, 470], [640, 620], [700, 700], [0, 760]], '#b4a487', '#7f7058');
    poly([[300, 420], [560, 330], [760, 470], [640, 620], [420, 470]], '#d1c6ac', '#a1937a');
    g.fillStyle = 'rgba(80,100,50,.55)'; [[60, 640, 120], [250, 600, 90], [470, 640, 80]].forEach(([x, y, w]) => { g.beginPath(); g.ellipse(x, y, w, 20, -0.15, 0, TAU); g.fill(); });
    g.strokeStyle = 'rgba(70,90,45,.9)'; g.lineWidth = 3;                                       // 一棵小树，几笔叶团
    g.beginPath(); g.moveTo(520, 440); g.lineTo(522, 360); g.stroke(); g.fillStyle = '#5f7a43'; [[522, 340, 34], [498, 372, 26], [548, 368, 26]].forEach(([x, y, rr]) => { g.beginPath(); g.arc(x, y, rr, 0, TAU); g.fill(); });
  }
  function building(g) {                 // 仓库：两个可见立面（正面＋斜侧），透视故意不统一（前期文艺复兴之前的「舞台盒」），带拱门和垛口
    const front = [[1040, 250], [1620, 250], [1620, 860], [1040, 860]], side = [[1620, 250], [1810, 190], [1810, 820], [1620, 860]];
    let gr = g.createLinearGradient(1040, 0, 1620, 0); gr.addColorStop(0, '#d9c9bd'); gr.addColorStop(1, '#bcab9f'); g.fillStyle = gr; g.beginPath(); front.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.fill();
    gr = g.createLinearGradient(1620, 0, 1810, 0); gr.addColorStop(0, '#9c8b82'); gr.addColorStop(1, '#7d6d66'); g.fillStyle = gr; g.beginPath(); side.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.fill();
    // 檐下装饰带：红白相间的菱格（科斯马蒂式）
    g.fillStyle = '#8c3d34'; g.fillRect(1040, 262, 580, 30); g.fillStyle = '#ead9aa'; for (let x = 1052; x < 1610; x += 36) { g.beginPath(); g.moveTo(x, 277); g.lineTo(x + 12, 266); g.lineTo(x + 24, 277); g.lineTo(x + 12, 288); g.closePath(); g.fill(); }
    // 侧面小窗
    g.fillStyle = '#4a3a30'; [[1685, 380], [1685, 560]].forEach(([x, y]) => { g.beginPath(); g.moveTo(x, y + 80); g.lineTo(x, y + 20); g.arc(x + 24, y + 20, 24, Math.PI, 0); g.lineTo(x + 48, y + 80); g.fill(); });
    // 垛口
    for (let i = 0; i < 6; i++) { const x = 1050 + i * 98; g.fillStyle = '#cdbdb0'; g.fillRect(x, 200, 62, 52); M.outline(g, [[x, 252], [x, 200], [x + 62, 200], [x + 62, 252]], { w: [2, 3, 2], col: '#6e5a4a', a: 0.6 }); }
    // 石砌水平缝（不画方格，画几道长缝，缝处有错位）
    g.strokeStyle = 'rgba(110,90,78,.28)'; g.lineWidth = 2; for (let y = 300; y < 860; y += 62) { g.beginPath(); g.moveTo(1040, y); g.lineTo(1620, y + (y % 124 ? 2 : -2)); g.stroke(); }
    // 拱门：金边环＋深洞
    const cx = 1290, top = 330, w = 250;
    g.fillStyle = '#e4d3aa'; g.beginPath(); g.moveTo(cx - w / 2 - 26, 860); g.lineTo(cx - w / 2 - 26, top + w / 2); g.arc(cx, top + w / 2, w / 2 + 26, Math.PI, 0); g.lineTo(cx + w / 2 + 26, 860); g.closePath(); g.fill();
    gr = g.createLinearGradient(0, top, 0, 860); gr.addColorStop(0, '#4a3a30'); gr.addColorStop(1, '#7a634e'); g.fillStyle = gr;
    g.beginPath(); g.moveTo(cx - w / 2, 860); g.lineTo(cx - w / 2, top + w / 2); g.arc(cx, top + w / 2, w / 2, Math.PI, 0); g.lineTo(cx + w / 2, 860); g.closePath(); g.fill();
    g.strokeStyle = '#c9a24b'; g.lineWidth = 7; g.beginPath(); g.arc(cx, top + w / 2, w / 2 + 14, Math.PI, 0); g.stroke();
    // 门洞里的暗处有几袋货
    g.fillStyle = '#6b5846'; [[cx - 70, 800, 54], [cx + 22, 810, 60]].forEach(([x, y, s]) => { g.beginPath(); g.ellipse(x, y, s, s * 0.7, 0, 0, TAU); g.fill(); });
    M.outline(g, [...front, front[0]], { w: [2.4, 3.6, 2.4], col: '#5f4a3d', a: 0.7 }); M.outline(g, [...side, side[0]], { w: [2.4, 3.6, 2.4], col: '#5f4a3d', a: 0.7 });
    // 墙脚台阶
    g.fillStyle = '#b5a592'; g.fillRect(1010, 860, 840, 26); g.fillStyle = '#9a8a78'; g.fillRect(1010, 886, 840, 16);
  }
  function ground(g) {
    const gr = g.createLinearGradient(0, 760, 0, H); gr.addColorStop(0, '#b9a56e'); gr.addColorStop(0.5, '#9a8754'); gr.addColorStop(1, '#6a5a36'); g.fillStyle = gr; g.fillRect(0, 760, W, H - 760);
    // 远处水带（码头边）：一条冷青带，岩坡脚下
    const wg = g.createLinearGradient(0, 735, 0, 790); wg.addColorStop(0, '#7f9fb4'); wg.addColorStop(1, '#5f8294'); g.fillStyle = wg; g.fillRect(0, 735, 1010, 52);
    g.strokeStyle = 'rgba(230,240,245,.5)'; g.lineWidth = 2; for (let i = 0; i < 18; i++) { const x = 40 + i * 52, y = 745 + (i % 3) * 14; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 14, y - 3, x + 30, y); g.stroke(); }
    // 土路的亮带与车辙
    g.fillStyle = 'rgba(214,194,140,.55)'; g.beginPath(); g.moveTo(0, 820); g.quadraticCurveTo(520, 780, 1010, 830); g.lineTo(1010, 930); g.quadraticCurveTo(500, 900, 0, 960); g.fill();
    const r = rng(5); for (let i = 0; i < 420; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '84,64,36' : '214,198,150'},${0.1 + r() * 0.18})`; g.fillRect(r() * W, 790 + r() * 290, 6 + r() * 44, 2 + r() * 2); }
    // 草簇与石子
    g.strokeStyle = '#4d6a36'; g.lineWidth = 2.4; for (let i = 0; i < 26; i++) { const x = r() * W, y = 960 + r() * 100; for (let k = -2; k <= 2; k++) { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + k * 5, y - 14, x + k * 9, y - 26 - r() * 8); g.stroke(); } }
    g.fillStyle = '#8c7e66'; for (let i = 0; i < 26; i++) { g.beginPath(); g.ellipse(r() * W, 900 + r() * 170, 7 + r() * 12, 4 + r() * 6, 0, 0, TAU); g.fill(); }
    // 门边的麻袋和木桶（货）
    [[1460, 905, 62], [1550, 915, 54]].forEach(([x, y, s2]) => { const sg = g.createLinearGradient(x - s2, 0, x + s2, 0); sg.addColorStop(0, '#d8c79a'); sg.addColorStop(1, '#a89468'); g.fillStyle = sg; g.beginPath(); g.moveTo(x - s2 * 0.8, y); g.quadraticCurveTo(x - s2, y - s2 * 1.1, x, y - s2 * 1.3); g.quadraticCurveTo(x + s2, y - s2 * 1.1, x + s2 * 0.8, y); g.closePath(); g.fill(); g.strokeStyle = 'rgba(90,70,48,.7)'; g.lineWidth = 3; g.stroke(); g.beginPath(); g.moveTo(x - s2 * 0.35, y - s2 * 1.1); g.quadraticCurveTo(x, y - s2 * 0.9, x + s2 * 0.35, y - s2 * 1.1); g.stroke(); });
    const bgd = g.createLinearGradient(1640, 0, 1760, 0); bgd.addColorStop(0, '#9a6a3c'); bgd.addColorStop(1, '#6e4724'); g.fillStyle = bgd; g.fillRect(1640, 790, 120, 130); g.beginPath(); g.ellipse(1700, 790, 60, 14, 0, 0, TAU); g.fill(); g.strokeStyle = '#3d3a36'; g.lineWidth = 6; [820, 880].forEach(y => { g.beginPath(); g.moveTo(1640, y); g.lineTo(1760, y); g.stroke(); });
  }
  function build() {
    plate = P.canvas(); pg = plate.getContext('2d');
    sky(pg); rocks(pg); building(pg); ground(pg);
  }
  const GROUND = M.plaster('giotto', { base: '#d8cdb6', seed: 9, seams: [[[0, 372], [380, 380], [760, 366], [1120, 378], [1500, 368], [1920, 376]], [[640, 0], [652, 190], [630, 372]]] });

  // 木箱：有体积（正面＋顶面），箱角包铁
  function crate(c, x, y, s, tilt) {
    c.save(); c.translate(x, y); c.rotate(tilt);
    const w = 150 * s, h = 110 * s, d = 28 * s;
    c.fillStyle = '#a77b49'; c.fillRect(-w / 2, -h / 2, w, h);
    c.fillStyle = '#c59a62'; c.beginPath(); c.moveTo(-w / 2, -h / 2); c.lineTo(-w / 2 + d, -h / 2 - d); c.lineTo(w / 2 + d, -h / 2 - d); c.lineTo(w / 2, -h / 2); c.fill();
    c.fillStyle = '#7d5a31'; c.beginPath(); c.moveTo(w / 2, -h / 2); c.lineTo(w / 2 + d, -h / 2 - d); c.lineTo(w / 2 + d, h / 2 - d); c.lineTo(w / 2, h / 2); c.fill();
    c.strokeStyle = 'rgba(70,45,25,.55)'; c.lineWidth = 2 * s; for (let k = 1; k < 4; k++) { c.beginPath(); c.moveTo(-w / 2, -h / 2 + k * h / 4); c.lineTo(w / 2, -h / 2 + k * h / 4); c.stroke(); }
    c.strokeStyle = '#3f3a36'; c.lineWidth = 7 * s; c.strokeRect(-w / 2 + 4, -h / 2 + 4, w - 8, h - 8);
    c.beginPath(); c.moveTo(-w / 2, -h / 2); c.lineTo(w / 2, h / 2); c.stroke();
    M.outline(c, [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2], [-w / 2, -h / 2]], { w: [2.4, 3.2, 2.4], col: '#4a2f22', a: 0.8 });
    c.restore();
  }

  function draw(c, lt, t) {
    if (!plate) build();
    const tt = clamp(lt, 0, 6);
    const hand = ease((tt - 0.6) / 3.2);                         // 箱子从左到右交接（0.6→3.8s），之后右边的人接稳、放下
    const settle = ease((tt - 3.8) / 1.4);
    const g = pg;
    // 动态的形画到 plate 副本：背景 plate 不动，人物每帧画在 live 上
    const live = P.scratch('giotto_live'), lg = live.getContext('2d'); lg.reset(); lg.drawImage(plate, 0, 0);
    // 人物：左搬运工（赭红袍＋深绿披风）、右搬运工（橄榄绿袍＋土红披风）、门边低头者（青灰袍）
    const bx = lerp(800, 890, hand), by = lerp(735, 748, hand) + Math.sin(hand * Math.PI) * -34 + settle * 38, tilt = Math.sin(hand * Math.PI) * -0.07;
    const boxTop = [bx, by];
    M.figure(lg, { hemK: 0.82, halo: true, beard: false, x: 745, y: 905, h: 480, face: 1, lean: 0.10 + 0.07 * (1 - ease(hand * 1.4)), bow: 0.4, t: tt, seed: 1, sway: 0.3,
      robe: ['#f0a98c', '#cf5f4a', '#8c3430'], mantle: ['#7da07c', '#4f7456', '#2f4f3c'], under: '#ecdcae', skin: '#e2b48a', hair: '#5b3a22',
      gaze: [bx + 30, by - 20], hands: [[bx - 74, by + 14], [bx - 74, by - 24]] });
    M.figure(lg, { hemK: 1.12, halo: true, beard: false, x: 1030, y: 915, h: 500, face: -1, lean: 0.06 + 0.1 * ss(0.2, 0.9, hand), bow: 0.5, t: tt, seed: 2, sway: 0.3,
      robe: ['#bccb8d', '#86a05c', '#4c6a3a'], mantle: ['#d28a6e', '#a8553f', '#6f3329'], under: '#efe2b8', skin: '#d9a97e', hair: '#3b2a1c',
      gaze: [bx, by - 12], hands: [[bx + 74, by + 16 + settle * 6], [bx + 74, by - 24]] });
    crate(lg, bx, by, 1, tilt);
    // 前景手要压在箱前：重画两只手
    // 第三人：站在左岩坡边，低头
    M.figure(lg, { hemK: 0.7, halo: true, x: 330, y: 885, h: 430, face: 1, lean: 0.05, bow: 0.9, t: tt, seed: 3, sway: 0.35,
      robe: ['#b8c6d0', '#8399ab', '#53677d'], under: '#e9dcb4', skin: '#dcae85', hair: '#6b4b30', gaze: [bx - 120, by + 20], hands: [[430, 720], [445, 762]] });
    // 箱子落地时扬起的一点灰
    const dust = ss(3.7, 4.0, tt) * (1 - ss(4.0, 5.4, tt));
    if (dust > 0) { lg.fillStyle = `rgba(210,190,150,${0.35 * dust})`; for (let i = 0; i < 9; i++) { const a = i / 9 * TAU; lg.beginPath(); lg.ellipse(bx + Math.cos(a) * 90 * (0.5 + dust), 868 + Math.sin(a) * 8, 22, 9, 0, 0, TAU); lg.fill(); } }
    // 一只鸟横过天（慢慢，不抢戏）
    const bt = ss(0.2, 5.8, tt), bxp = lerp(-60, 1000, bt), byp = 130 + Math.sin(bt * 9) * 14;
    lg.strokeStyle = 'rgba(240,235,220,.9)'; lg.lineWidth = 3; lg.beginPath(); lg.moveTo(bxp - 16, byp + Math.sin(tt * 11) * 6); lg.quadraticCurveTo(bxp, byp - 8, bxp + 16, byp + Math.sin(tt * 11 + 1) * 6); lg.stroke();

    M.fresco(c, live, { ground: GROUND, chalk: 0.07, soften: 0.7, plasterAlpha: 0.5, sat: 1.12 });
    // 装饰边框：深红带＋金线＋菱形 cosmati 纹（原作每幅都被这样一条带框住）
    c.save(); c.lineWidth = 1;
    c.fillStyle = '#7b2f2a'; c.fillRect(0, 0, W, 34); c.fillRect(0, H - 34, W, 34); c.fillRect(0, 0, 34, H); c.fillRect(W - 34, 0, 34, H);
    c.strokeStyle = '#d7b35c'; c.lineWidth = 3; c.strokeRect(34, 34, W - 68, H - 68);
    c.fillStyle = '#e8d6a0'; for (let x = 60; x < W - 40; x += 44) { [[x, 17], [x, H - 17]].forEach(([a, b]) => { c.beginPath(); c.moveTo(a, b - 8); c.lineTo(a + 10, b); c.lineTo(a, b + 8); c.lineTo(a - 10, b); c.fill(); }); }
    for (let y = 60; y < H - 40; y += 44) { [[17, y], [W - 17, y]].forEach(([a, b]) => { c.beginPath(); c.moveTo(a, b - 10); c.lineTo(a + 8, b); c.lineTo(a, b + 10); c.lineTo(a - 8, b); c.fill(); }); }
    c.restore();
    // 边缘剥落：灰泥外圈略亮、角上几处脱落（只在边框与天空，不碰人物）
    c.save(); c.globalCompositeOperation = 'screen'; const vg = c.createRadialGradient(W / 2, H / 2, 600, W / 2, H / 2, 1180); vg.addColorStop(0, 'rgba(255,245,225,0)'); vg.addColorStop(1, 'rgba(255,245,225,.12)'); c.fillStyle = vg; c.fillRect(0, 0, W, H); c.restore();
  }
  return { draw };
})();
