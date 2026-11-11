// 高更（综合主义／掐丝珐琅）：不写实的饱和色场、粗而不均的深群青轮廓、斜线分割画面的树干、被画框裁掉的前景人物、没有投影。
// 题材（新构图）：红色草场上，三位戴白帽的妇人（前景，裁切）看着一个男孩牵山羊横穿画面；一棵斜树把画面劈开。
// 原作锚定（fetch_reference.py：《布道后的幻象》《黄色基督》《我们从哪里来》）：朱红 #d63a1c 色场、黄赭 #e0a526 地、
//   紫褐树干 #5b2c48、白帽 #efece2＋蓝灰影 #a9b4cf、黑裙 #1b1a22、轮廓深群青 #1d2a52；没有透视收束，远近靠重叠和裁切。
// 管线：色场（缓存，顺笔向短条）→ 斜树（缓存）→ 黄地 → 动态：山羊与男孩（走）、前景妇人（风吹帽翼）、叶团摇 → 无投影，不加光效。
SCENES['48_gauguin'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const LINE = '#1d2a52';
  let layer;
  const poly = (pts, close = true) => { const p = new Path2D(); pts.forEach((q, i) => i ? p.lineTo(q[0], q[1]) : p.moveTo(q[0], q[1])); if (close) p.closePath(); return p; };
  // Catmull 式平滑闭合/开放曲线：高更什么都是圆的，不要折线
  const smooth = (pts, close = true) => { const p = new Path2D(), n = pts.length; if (close) { const m = i => [(pts[i % n][0] + pts[(i + 1) % n][0]) / 2, (pts[i % n][1] + pts[(i + 1) % n][1]) / 2]; p.moveTo(...m(n - 1)); for (let i = 0; i < n; i++) p.quadraticCurveTo(pts[i][0], pts[i][1], ...m(i)); p.closePath(); }
    else { p.moveTo(...pts[0]); for (let i = 1; i < n - 1; i++) p.quadraticCurveTo(pts[i][0], pts[i][1], (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2); p.lineTo(...pts[n - 1]); } return p; };
  const blob = (cx, cy, rx, ry, rot = 0) => { const p = new Path2D(); p.ellipse(cx, cy, rx, ry, rot, 0, TAU); return p; };
  function build() {
    layer = P.canvas(); const g = layer.getContext('2d');
    // 朱红色场：整幅铺满，笔向斜 30°，同色里有橙红/深红的条
    M.flat(g, poly([[0, 0], [W, 0], [W, H], [0, H]]), '#d63a1c', { streak: 0.5, vari: 34, lw: 0, seed: 1, n: 520 });
    // 黄赭地：右下一块大而圆的坡，波浪形上缘
    const ground = new Path2D(); ground.moveTo(520, H); ground.bezierCurveTo(700, 820, 980, 700, 1280, 730); ground.bezierCurveTo(1560, 760, 1740, 700, W, 640); ground.lineTo(W, H); ground.closePath();
    M.flat(g, ground, '#e0a526', { streak: -0.15, vari: 26, lw: 7, seed: 2, n: 300, line: LINE });
    // 紫褐小径：沿地面斜向的一条
    M.flat(g, poly([[900, 1010], [1260, 840], [1420, 860], [1060, 1060]]), '#7a3a5a', { streak: -0.45, vari: 20, lw: 5, seed: 3, n: 80, line: LINE });
    // 斜树干：从左上劈向右下，上粗下细再略弯，把画面分成两半
    const trunk = smooth([[620, -40], [830, -40], [970, 150], [1100, 330], [1300, 490], [1480, 590], [1580, 730], [1450, 760], [1350, 690], [1170, 620], [1090, 520], [930, 340], [770, 200], [670, 90]]);
    M.flat(g, trunk, '#5b2c48', { streak: 0.8, vari: 26, lw: 8, seed: 4, n: 180, line: LINE, bounds: [500, 0, 1120, 780] });
    M.flat(g, smooth([[640, -30], [760, -30], [940, 170], [1120, 360], [1300, 520], [1420, 600], [1330, 600], [1160, 480], [940, 300], [720, 120]]), '#8d4a66', { streak: 0.8, vari: 14, lw: 0, seed: 5, n: 50, bounds: [500, 0, 1100, 760] });
    // （树干上原有三个暗斑，读成笛孔，已去掉）
    // 枝：树干中段向右上分出两枝，叶团另画（动态）
    M.flat(g, smooth([[1200, 400], [1380, 250], [1560, 140], [1630, 190], [1500, 330], [1310, 480]]), '#5b2c48', { streak: -0.7, vari: 20, lw: 7, seed: 6, n: 70, line: LINE, bounds: [1200, 140, 460, 340] });
    M.flat(g, smooth([[980, 280], [1090, 150], [1190, 30], [1250, 70], [1170, 220], [1090, 340]]), '#5b2c48', { streak: -1.0, vari: 20, lw: 7, seed: 7, n: 40, line: LINE, bounds: [980, 30, 280, 300] });
  }
  function leaves(c, t) {                                         // 叶团：深绿大圆块，叠几个黄点（果），整团微摇
    [[1590, 150, 190, 120, 0.2], [1250, 70, 150, 100, -0.3], [1460, 300, 120, 80, 0.1]].forEach(([x, y, rx, ry, rot], i) => {
      const sw = Math.sin(t * 1.6 + i * 1.7) * 7, ox = x + sw, oy = y + Math.sin(t * 2.1 + i) * 3, rr = rng(70 + i), p = smooth(Array.from({ length: 11 }, (_, k) => { const a = k / 11 * TAU, j = 0.82 + rr() * 0.3; return [ox + Math.cos(a) * rx * j, oy + Math.sin(a) * ry * j]; }));
      M.flat(c, p, '#2f5a3a', { streak: 0.2, vari: 22, lw: 7, seed: 10 + i, n: 90, line: LINE, bounds: [x - rx, y - ry, rx * 2, ry * 2] });
      const r = rng(30 + i); for (let k = 0; k < 6; k++) { const a = r() * TAU, d = r() * 0.7; M.flat(c, blob(x + sw + Math.cos(a) * rx * d, y + Math.sin(a) * ry * d, 15, 13), '#f2c335', { vari: 8, lw: 3.5, seed: 40 + k, n: 6, line: LINE, bounds: [x - rx, y - ry, rx * 2, ry * 2] }); }
    });
  }
  // 戴白帽的妇人（布列塔尼）：黑裙大圆块＋肩上白披领；侧脸朝右（前额—鼻—唇—下巴一条干净的曲线）；高白帽冠立在头顶、帽翼垂在脑后随风；back=true 背对
  function woman(c, x, y, s, t, seed, bow, back) {
    const sw = Math.sin(t * 2.2 + seed) * 8 * s;
    c.save(); c.translate(x, y); c.scale(s, s);
    M.flat(c, smooth([[-170, 0], [-190, -200], [-150, -360], [-60, -430], [60, -430], [150, -340], [190, -190], [175, 0]]), '#1b1a22', { streak: 1.2, vari: 12, lw: 8, seed: seed, n: 60, line: LINE, bounds: [-190, -440, 380, 440] });
    // 白披领：肩上一圈，前襟 V 形，蓝灰影在一侧
    M.flat(c, smooth([[-120, -420], [-30, -470], [80, -462], [150, -400], [90, -350], [10, -330], [-70, -350]]), '#efece2', { streak: 0.3, vari: 8, lw: 7, seed: seed + 1, n: 16, line: LINE, bounds: [-130, -475, 290, 150] });
    M.flat(c, smooth([[-40, -352], [10, -332], [80, -352], [40, -380]]), '#a9b4cf', { vari: 6, lw: 0, seed: seed + 8, n: 6, bounds: [-40, -380, 130, 50] });
    const hy = -560 + bow * 14;
    // 帽翼（脑后垂下，随风）
    M.flat(c, smooth([[-10, hy + 30], [-70 - sw, hy + 20], [-150 - sw * 1.6, hy + 90], [-120 - sw, hy + 170], [-50, hy + 140], [-10, hy + 90]]), '#efece2', { streak: 0.5, vari: 8, lw: 7, seed: seed + 2, n: 16, line: LINE, bounds: [-160, hy + 10, 160, 170] });
    M.flat(c, smooth([[-100 - sw, hy + 110], [-60, hy + 130], [-40, hy + 100]]), '#a9b4cf', { vari: 6, lw: 0, seed: seed + 5, n: 4, bounds: [-110, hy + 90, 80, 50] });
    if (!back) {
      // 脸：侧向右，一条连续的曲线；颈接到披领
      M.flat(c, smooth([[-10, hy + 0], [52, hy - 6], [92, hy + 22], [96, hy + 56], [126, hy + 90], [100, hy + 98], [104, hy + 118], [94, hy + 134], [98, hy + 160], [60, hy + 188], [10, hy + 176], [-20, hy + 140], [-24, hy + 70]]), '#e8b078', { streak: 1.2, vari: 10, lw: 7, seed: seed + 6, n: 14, line: LINE, bounds: [-30, hy - 10, 160, 200] });
      c.strokeStyle = LINE; c.lineWidth = 5.5; c.lineCap = 'round';
      c.beginPath(); c.moveTo(56, hy + 52); c.quadraticCurveTo(76, hy + 64, 96, hy + 52); c.stroke();                                           // 闭眼
      c.beginPath(); c.moveTo(50, hy + 34); c.quadraticCurveTo(76, hy + 24, 98, hy + 34); c.stroke();                                           // 眉
      c.strokeStyle = '#8a3a30'; c.lineWidth = 6; c.beginPath(); c.moveTo(74, hy + 138); c.quadraticCurveTo(90, hy + 144, 102, hy + 134); c.stroke();     // 唇：平静
      M.flat(c, smooth([[8, hy + 90], [40, hy + 120], [30, hy + 160], [-6, hy + 120]]), '#d49a66', { vari: 6, lw: 0, seed: seed + 9, n: 4, bounds: [-6, hy + 90, 50, 70] });   // 颊下影
    }
    // 帽冠：高、圆顶、正面略宽，压在额头之上（不盖脸）
    M.flat(c, smooth([[-26, hy + 70], [-34, hy - 40], [-4, hy - 120], [58, hy - 150], [108, hy - 100], [112, hy - 20], [86, hy + 6], [20, hy + 12]]), '#efece2', { streak: 1.3, vari: 8, lw: 8, seed: seed + 4, n: 26, line: LINE, bounds: [-40, hy - 160, 160, 180] });
    M.flat(c, smooth([[-26, hy - 30], [-4, hy - 110], [20, hy - 100], [0, hy + 20]]), '#a9b4cf', { vari: 6, lw: 0, seed: seed + 3, n: 6, bounds: [-30, hy - 120, 60, 150] });
    c.restore();
  }
  // 男孩和山羊：向左走。羊在后，绳牵在男孩手里；步态用腿相位摆
  function boyGoat(c, t) {
    const u = ss(0.0, 6, t), x = lerp(1830, 1420, u), step = Math.sin(t * 7), bob = Math.abs(step) * 4, y = 808 + lerp(0, 22, u);
    c.save(); c.translate(x, y - bob); c.scale(0.58, 0.58);
    // 羊（朝左）：长躯干＋粗颈＋楔形头＋后弯角＋细腿带膝；远侧两腿先画，近侧后画；肚下蓝灰影
    const leg = (dx, ph, near) => { const sw = Math.sin(t * 7 + ph) * 26, kx = dx + sw * 0.4, fx = dx + sw; return smooth([[dx - 10, -70], [dx + 10, -70], [kx + 8, -36], [fx + 7, 6], [fx + 10, 20], [fx - 14, 20], [fx - 8, 4], [kx - 8, -34]]); };
    [[-62, 3.1, 0], [58, 0, 0]].forEach(([dx, ph], i) => M.flat(c, leg(dx, ph), '#c9c8c4', { vari: 6, lw: 6, seed: 60 + i, n: 4, line: LINE, bounds: [dx - 30, -74, 70, 110] }));
    M.flat(c, smooth([[-96, -126], [-40, -156], [50, -158], [120, -138], [134, -100], [104, -66], [30, -58], [-50, -60], [-98, -82]]), '#efece2', { streak: 0.05, vari: 10, lw: 8, seed: 66, n: 40, line: LINE, bounds: [-100, -160, 240, 100] });
    M.flat(c, smooth([[-100, -86], [-30, -62], [60, -64], [118, -86], [100, -66], [30, -58], [-50, -60]]), '#a9b4cf', { vari: 6, lw: 0, seed: 65, n: 8, bounds: [-110, -90, 240, 40] });
    [[-30, -110, 34, 22], [40, -130, 30, 20], [70, -90, 24, 16]].forEach(([x, y, rx, ry], i) => M.flat(c, blob(x, y, rx, ry, 0.3), '#6a3a2a', { vari: 8, lw: 5, seed: 80 + i, n: 6, line: LINE, bounds: [x - rx, y - ry, rx * 2, ry * 2] }));
    M.flat(c, smooth([[-96, -128], [-100, -198], [-140, -242], [-196, -236], [-224, -200], [-216, -152], [-170, -148], [-130, -110]]), '#efece2', { streak: 0.6, vari: 8, lw: 8, seed: 67, n: 22, line: LINE, bounds: [-250, -232, 160, 130] });   // 颈＋头
    M.flat(c, smooth([[-176, -232], [-150, -262], [-130, -226], [-150, -216]]), '#efece2', { vari: 4, lw: 6, seed: 68, n: 2, line: LINE });                                                       // 耳
    c.strokeStyle = LINE; c.lineWidth = 9; c.lineCap = 'round'; c.beginPath(); c.moveTo(-196, -232); c.quadraticCurveTo(-190, -290, -128, -296); c.stroke();                                          // 角（向后弯）
    c.lineWidth = 6; c.beginPath(); c.moveTo(-244, -166); c.quadraticCurveTo(-254, -134, -240, -110); c.stroke();                                                                                    // 胡须
    M.flat(c, blob(-208, -172, 22, 17, 0.2), '#c7a591', { vari: 6, lw: 5, seed: 90, n: 4, line: LINE, bounds: [-258, -186, 44, 32] });
    c.fillStyle = LINE; c.beginPath(); c.arc(-184, -208, 6.5, 0, TAU); c.fill();
    [[-34, 0, 0], [86, 3.1, 0]].forEach(([dx, ph], i) => M.flat(c, leg(dx, ph), '#efece2', { vari: 6, lw: 7, seed: 62 + i, n: 4, line: LINE, bounds: [dx - 30, -74, 70, 110] }));
    // 男孩：侧身朝左，蓝衣、黄裤、赭色头发小帽，拉绳
    const bx = -380, sw = Math.sin(t * 7) * 20;
    [0, 3.1].forEach((ph, i) => { const s2 = Math.sin(t * 7 + ph) * 22; M.flat(c, smooth([[bx - 16, -104], [bx + 18, -104], [bx + 14 + s2 * 0.5, -40], [bx + 14 + s2, 22], [bx - 20 + s2, 22], [bx - 12 + s2 * 0.5, -40]]), i ? '#1d2a52' : '#2f3f7a', { lw: 6, seed: 70 + i, n: 8, line: LINE, bounds: [bx - 30, -104, 60, 130] }); });
    M.flat(c, smooth([[bx - 46, -270], [bx + 4, -290], [bx + 48, -250], [bx + 56, -96], [bx - 54, -96]]), '#2f5f9a', { streak: 1.3, vari: 16, lw: 7, seed: 71, n: 30, line: LINE, bounds: [bx - 58, -290, 118, 200] });
    M.flat(c, smooth([[bx - 30, -330], [bx + 10, -352], [bx + 46, -320], [bx + 40, -276], [bx - 8, -262], [bx - 36, -290]]), '#e8b078', { vari: 10, lw: 6, seed: 72, n: 10, line: LINE, bounds: [bx - 40, -352, 90, 90] });
    M.flat(c, smooth([[bx - 40, -318], [bx - 8, -366], [bx + 40, -352], [bx + 52, -322], [bx + 4, -334]]), '#8a2f24', { vari: 6, lw: 6, seed: 73, n: 8, line: LINE, bounds: [bx - 44, -368, 100, 50] });   // 红帽
    c.strokeStyle = LINE; c.lineWidth = 4.5; c.beginPath(); c.moveTo(bx - 22, -312); c.quadraticCurveTo(bx - 14, -306, bx - 6, -312); c.stroke();                     // 眼
    c.strokeStyle = LINE; c.lineWidth = 6; c.beginPath(); c.moveTo(bx - 44, -230); c.quadraticCurveTo(bx - 120, -170, bx - 90, -150 + sw * 0.3); c.stroke();              // 左臂向前
    c.lineWidth = 4; c.beginPath(); c.moveTo(bx + 40, -214 + sw * 0.2); c.quadraticCurveTo(-60, -100, -186, -190); c.stroke();                                         // 绳从男孩右手到羊颈
    c.restore();
  }
  function draw(c, lt) {
    if (!layer) build();
    const t = clamp(lt, 0, 6);
    c.save(); c.translate(W, 0); c.scale(-1, 1);                                                   // 水平镜像：不复刻名作的左右布局
    c.drawImage(layer, 0, 0);
    leaves(c, t); boyGoat(c, t);
    // 前景妇人：被画框裁掉（脚在画外），两个并排朝右，一个在最左背对
    woman(c, 230, 1190 + Math.sin(t * 1.4) * 2, 1.0, t, 100, 0.2, true);
    woman(c, 560, 1250, 0.86, t, 200, 0.5, false);
    woman(c, 820, 1310, 0.72, t, 300, 0.3, false);
    c.restore();
  }
  return { draw };
})();
