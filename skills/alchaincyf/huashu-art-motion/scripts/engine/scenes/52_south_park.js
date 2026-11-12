// 南方公园式数字剪纸：一切都是被剪刀剪出来的色纸——圆头、梯形身体、直边、没有曲线细节；眼睛是两个白椭圆加黑点；
// 动画是「纸片绕枢轴转、整块平移」，嘴是一个黑色半椭圆开合；背景是几块粗糙的平涂纸。
// 题材（新构图）：小镇雪地里的公交站，四个小孩缩着脖子等车，校车慢吞吞滑进来、车门啪地打开，孩子们一块一块地跳上去。
// 原作锚定（风格特征，非角色）：①纸片感——每块形状边缘有轻微的剪刀抖动，表面有纸纤维 ②眼睛贴脸、黑点在白椭圆里
//   ③身体是梯形/方块，手是单纯的圆头短棒，腿是两根黑短柱 ④色块平涂、只有一道细黑轮廓 ⑤镜头永远正对，层叠为主，不透视
// 管线：纸块（每块 P.cut 出抖动边缘）→ 纸纹相乘 → 枢轴动画。不使用任何具名角色的服装或配色组合。
SCENES['52_south_park'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, TAU = Math.PI * 2;
  const OUT = '#14120f';
  const E = { lin: x => x, io: x => { x = clamp(x); return x * x * (3 - 2 * x); } };
  // 剪纸：多边形（顶点）→ 抖动边缘，填色，细黑线。seed 固定所以确定性
  function paper(c, pts, fill, { seed = 1, lw = 3, amp = 2.4, step = 18, shade = null } = {}) {
    const p = P.cut(pts, seed, step, amp);
    c.fillStyle = fill; c.fill(p);
    if (shade) { c.save(); c.clip(p); c.fillStyle = shade; c.globalAlpha = 0.18; c.fillRect(-9999, -9999, 99999, 99999); c.restore(); c.globalAlpha = 1; }
    if (lw) { c.strokeStyle = OUT; c.lineWidth = lw; c.lineJoin = 'round'; c.stroke(p); }
    return p;
  }
  function circle(c, x, y, r, fill, seed, lw = 3) { const pts = Array.from({ length: 28 }, (_, i) => [x + Math.cos(i / 28 * TAU) * r, y + Math.sin(i / 28 * TAU) * r]); return paper(c, pts, fill, { seed, lw, amp: 1.2, step: 12 }); }
  function ell(c, x, y, rx, ry, fill, seed, lw = 3) { const pts = Array.from({ length: 24 }, (_, i) => [x + Math.cos(i / 24 * TAU) * rx, y + Math.sin(i / 24 * TAU) * ry]); return paper(c, pts, fill, { seed, lw, amp: 0.8, step: 10 }); }
  const tex = () => P.cached('sp_paper', W, H, g => {
    g.fillStyle = '#fff'; g.fillRect(0, 0, W, H); const r = rng(5);
    for (let i = 0; i < 9000; i++) { const x = r() * W, y = r() * H, a = r() * TAU, l = 3 + r() * 12; g.strokeStyle = r() < 0.5 ? 'rgba(140,130,115,.16)' : 'rgba(255,255,255,.5)'; g.lineWidth = 0.8; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
  });

  // 小孩：head 圆、眼、嘴；parka 梯形；帽子；手；腿。o: x,y(脚底) s(缩放) skin parka hat tilt(头倾) talk(0..1 嘴开) armL armR(弧度，0=下垂) hop face
  function kid(c, o) {
    const { x, y, s = 1, skin = '#f5cfa8', parka, hat, band, tilt = 0, talk = 0, armL = 0, armR = 0, hop = 0, seed = 1, lookx = 0.5 } = o;
    c.save(); c.translate(x, y - hop); c.scale(s, s);
    // 腿
    paper(c, [[-34, -52], [-10, -52], [-10, 0], [-34, 0]], '#1c1a18', { seed: seed + 1, lw: 0, amp: 1 }); paper(c, [[10, -52], [34, -52], [34, 0], [10, 0]], '#1c1a18', { seed: seed + 2, lw: 0, amp: 1 });
    // 手臂（绕肩枢轴）
    const arm = (sx, ang, k) => { c.save(); c.translate(sx, -150); c.rotate(ang); paper(c, [[-12, 0], [12, 0], [11, 84], [-11, 84]], parka, { seed: seed + 3 + k, lw: 3, amp: 1.2 }); circle(c, 0, 90, 17, '#f2ede0', seed + 5 + k, 3); c.restore(); };
    arm(-70, armL, 0); arm(70, armR, 1);
    // 身体：梯形，小孩缩着脖子
    paper(c, [[-72, -170], [72, -170], [92, -52], [-92, -52]], parka, { seed: seed + 6, lw: 3.4, amp: 1.6 });
    paper(c, [[-10, -170], [10, -170], [10, -52], [-10, -52]], 'rgba(0,0,0,.18)', { seed: seed + 7, lw: 0 });                          // 拉链缝
    // 头：绕颈枢轴倾斜
    c.save(); c.translate(0, -168); c.rotate(tilt);
    circle(c, 0, -62, 66, skin, seed + 8, 3.4);
    // 帽：半个纸球＋边带＋绒球
    paper(c, [[-66, -68], [-56, -112], [-30, -134], [0, -142], [30, -134], [56, -112], [66, -68]], hat, { seed: seed + 9, lw: 3.4, amp: 1.6 });
    paper(c, [[-68, -66], [68, -66], [68, -86], [-68, -86]], band, { seed: seed + 10, lw: 3.4, amp: 1.2 });
    circle(c, 0, -150, 18, band, seed + 11, 3);
    // 眼：两个白椭圆紧贴，黑点在里面朝向 lookx
    const ex = 15, ey = -62; ell(c, -ex, ey, 17, 21, '#fff', seed + 12, 3); ell(c, ex, ey, 17, 21, '#fff', seed + 13, 3);
    const px = (lookx - 0.5) * 12; c.fillStyle = OUT; [-ex, ex].forEach(xx => { c.beginPath(); c.arc(xx + px, ey + 2, 3.8, 0, TAU); c.fill(); });
    // 嘴：黑色半椭圆，开合
    const m = 4 + talk * 20; c.fillStyle = OUT; c.beginPath(); c.ellipse(0, -22, 14 + talk * 6, m, 0, 0, Math.PI); c.fill(); if (talk > 0.4) { c.fillStyle = '#c4412f'; c.beginPath(); c.ellipse(0, -22 + m * 0.5, 9, m * 0.4, 0, 0, Math.PI); c.fill(); }
    c.restore(); c.restore();
  }

  function draw(c, lt, t) {
    const T = clamp(lt, 0, 6), r = rng(2);
    // 天与远山：平涂纸块
    c.fillStyle = '#c9dce6'; c.fillRect(0, 0, W, H);
    paper(c, [[0, 0], [W, 0], [W, 330], [0, 330]], '#bcd3e0', { seed: 21, lw: 0, amp: 3 });
    paper(c, [[-20, 520], [260, 300], [520, 440], [860, 250], [1260, 460], [1560, 330], [1960, 520]], '#e9eef0', { seed: 22, lw: 3.4, amp: 4, step: 30 });
    paper(c, [[260, 300], [330, 360], [300, 410], [380, 400], [330, 460], [420, 460], [520, 440]], '#a9b9c6', { seed: 23, lw: 0, amp: 3 });
    paper(c, [[860, 250], [920, 330], [880, 350], [960, 380], [900, 440], [1000, 450], [1260, 460]], '#a9b9c6', { seed: 24, lw: 0, amp: 3 });
    // 松树：三角叠三层
    [[1440, 560, 1.1], [1560, 580, 0.9], [200, 560, 1.0], [320, 580, 0.8]].forEach(([x, y, s], i) => { paper(c, [[x - 8 * s, y], [x + 8 * s, y], [x + 8 * s, y + 60 * s], [x - 8 * s, y + 60 * s]], '#6b4a30', { seed: 30 + i, lw: 3 }); [[0, 70], [-26, 120], [-52, 170]].forEach(([dy, hw], k) => paper(c, [[x, y - 40 * s - dy * s * 0.2 + k * -20 * s], [x - (50 + k * 18) * s, y + 20 * s - k * 0 - (2 - k) * -20 * s + 0], [x + (50 + k * 18) * s, y + 20 * s + (2 - k) * 20 * s * 0]], '#2f5d3c', { seed: 40 + i * 3 + k, lw: 3.4, amp: 2 })); });
    // 雪地：两层白纸，前面一层带灰蓝阴影块
    paper(c, [[-20, 600], [W + 20, 600], [W + 20, H + 20], [-20, H + 20]], '#f4f7f8', { seed: 50, lw: 3.4, amp: 3, step: 40 });
    paper(c, [[-20, 840], [600, 800], [1300, 830], [W + 20, 810], [W + 20, H + 20], [-20, H + 20]], '#e6edf0', { seed: 51, lw: 0, amp: 4, step: 30 });
    // 公路（灰纸）＋黄虚线
    paper(c, [[-20, 700], [W + 20, 700], [W + 20, 800], [-20, 800]], '#6c7378', { seed: 52, lw: 3.4, amp: 2.4, step: 30 });
    for (let i = 0; i < 12; i++) paper(c, [[i * 170 + 20, 744], [i * 170 + 110, 744], [i * 170 + 110, 758], [i * 170 + 20, 758]], '#e8c13a', { seed: 60 + i, lw: 0, amp: 1.2 });
    // 站牌：灰杆＋红八角形牌（不写字，画一个 ■ 示意）
    paper(c, [[470, 520], [490, 520], [490, 840], [470, 840]], '#8c9296', { seed: 70, lw: 3.4 });
    paper(c, [[420, 400], [470, 372], [540, 372], [590, 400], [590, 468], [540, 496], [470, 496], [420, 468]], '#c8402e', { seed: 71, lw: 3.6, amp: 1.6 });
    paper(c, [[470, 420], [540, 420], [540, 450], [470, 450]], '#f6efe0', { seed: 72, lw: 0 });

    // 校车：从右滑入，停在 x≈1210，车门在 3.7 秒啪地打开；车轮不转（剪纸整块平移）
    const bx = lerp(2300, 1230, E.io(ss(0.2, 3.2, T))), by = 760;
    c.save(); c.translate(bx, by);
    paper(c, [[-420, -250], [330, -250], [350, -210], [350, 60], [-420, 60]], '#f0b92a', { seed: 80, lw: 4, amp: 2 });
    paper(c, [[-420, -250], [330, -250], [350, -210], [350, -190], [-420, -190]], '#f6cc55', { seed: 81, lw: 0 });
    for (let i = 0; i < 5; i++) paper(c, [[-380 + i * 110, -170], [-300 + i * 110, -170], [-300 + i * 110, -90], [-380 + i * 110, -90]], '#bcd3e0', { seed: 90 + i, lw: 3.4, amp: 1.2 });
    paper(c, [[-420, -20], [350, -20], [350, 0], [-420, 0]], '#14120f', { seed: 100, lw: 0 });                          // 黑杠
    const door = E.io(ss(3.6, 3.9, T)); paper(c, [[130, -190], [130 + 76 * (1 - door), -190], [130 + 76 * (1 - door), 40], [130, 40]], '#bcd3e0', { seed: 101, lw: 3.4, amp: 1 }); paper(c, [[130 + 76 * (1 - door), -190], [206, -190], [206, 40], [130 + 76 * (1 - door), 40]], '#2a2622', { seed: 102, lw: 3.4, amp: 1 });
    [-250, 200].forEach((wx, i) => { circle(c, wx, 62, 62, '#14120f', 110 + i, 0); circle(c, wx, 62, 30, '#8c9296', 112 + i, 3); });
    c.restore();

    // 四个孩子（原创配色，不借具名角色的服装组合）：站在站牌右侧等车；车停后单列依次走到车门、进门（进门＝消失在车厢里）
    const talkPhase = (k) => (Math.sin(T * 14 + k * 1.7) > 0.1 && T < 3.4 && (Math.floor(T * 1.3 + k) % 4 === k % 4)) ? 1 : 0;
    const DOOR = 1400, STARTX = [720, 860, 1000, 1140];
    const board = (k) => { const t0 = 3.9 + k * 0.5, q = clamp((T - t0) / 0.8); return { q, x: lerp(0, DOOR - STARTX[k], E.io(q)), hop: Math.abs(Math.sin(q * Math.PI * 3)) * 22 * (q > 0 && q < 1 ? 1 : 0) }; };
    [
      { parka: '#d65a7a', hat: '#4a4a52', band: '#f0d34a', seed: 200, s: 1.12 },
      { parka: '#5a78c8', hat: '#d6803a', band: '#f2ece0', seed: 300, s: 1.04 },
      { parka: '#8a8f3a', hat: '#8a3a5a', band: '#e8d9a0', seed: 400, s: 1.16 },
      { parka: '#d9d2c0', hat: '#2f6a58', band: '#3a3a3a', seed: 500, s: 1.0 },
    ].forEach((k, i) => {
      const j = board(i); if (j.q >= 1) return;                                               // 进了车厢
      const shiver = (T < 3.6) ? Math.sin(T * 30 + i) * 1.4 : 0, boarding = j.q > 0;
      kid(c, { ...k, x: STARTX[i] + j.x + shiver, y: 842 + i % 2 * 10, hop: j.hop, tilt: Math.sin(T * 1.8 + i) * 0.07 + (T > 3.4 ? -0.1 : 0), talk: talkPhase(i), armL: Math.sin(T * 6 + i) * 0.05 + (boarding ? 0.5 : 0), armR: -0.05 + Math.sin(T * 5 + i) * 0.05 + (boarding ? -0.5 : 0), lookx: T > 1 ? 0.9 : 0.4 });
    });
    // 落雪：纸圆片，12fps 一格格往下掉（剪纸的步进感）
    const st = Math.floor(T * 12) / 12; c.fillStyle = '#fff'; c.strokeStyle = 'rgba(100,110,120,.5)'; c.lineWidth = 1.4;
    for (let i = 0; i < 130; i++) { const rr = rng(i * 7 + 1), x = (rr() * W + st * 40 * (0.5 + rr() * 0.6)) % W, y = ((rr() * H) + st * (90 + rr() * 90)) % H, s = 3 + rr() * 5; c.beginPath(); c.arc(x, y, s, 0, TAU); c.fill(); c.stroke(); }
    c.save(); c.globalCompositeOperation = 'multiply'; c.globalAlpha = 0.55; c.drawImage(tex(), 0, 0); c.restore();
  }
  return { draw };
})();
