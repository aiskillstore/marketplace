// 科尔托纳（巴洛克天顶，巴贝里尼宫《神意的寓言》）：画出来的灰泥框和镀金圆章把天顶「打开」，中间是一片从中心往外发暖金光的天；云团堆成体积，人群绕着中心旋转，身体、衣带和云都漫出框外。
// 题材（新构图，不搬名作）：一个仰视的天顶——灰泥画框里的天空开口，一圈人在云上绕着光旋转，红蓝衣带随风绕过画框。
// 原作锚定（fetch_reference.py：《神意的寓言》天顶、《劫掠萨宾妇女》；第三条搜索与第一条同幅被丢弃，只有两幅不同原作）：
//   框＝象牙灰泥 #e4d8be＋镀金 #c89a3c＋深棕阴影、角上金圆章；天＝中心 #fff0c0 → #e8c07a → 边缘群青 #3a4a82；云内亮外暗；袍色猩红 #b83a3a、群青 #3a5ea8、赭 #c89a4a；对角线运动。
// 管线：形层（暗背景→画框灰泥带＋角圆章＋蛋形纹→开口天空渐变与光芒→云团）→ 人群与衣带（旋转，漫出框）→ MEDIUM.fresco（轻糊、灰泥颗粒）→ 中心光再叠一层加法光。
SCENES['44_cortona'] = (() => {
  const W = 1920, H = 1080, { clamp, lerp, rng, ss } = U, P = PAINT, M = MEDIUM, TAU = Math.PI * 2;
  const CX = 960, CY = 540, RX = 560, RY = 300;
  const ROB = { red: ['#f08a7c', '#b83a3a', '#6a1c26'], blue: ['#9ab4ea', '#3a5ea8', '#1c2f62'], ochre: ['#f2d896', '#c89a4a', '#7a5a22'], white: ['#fffaf0', '#e8dcc0', '#a89868'], green: ['#a8d0a0', '#5a8a64', '#2c4a3a'], rose: ['#f6c0c0', '#d27a86', '#8a3a4a'] };
  let plate, built = false;
  const rr = (g, x, y, w, h, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };
  function cloud(g, x, y, r, seed) {                             // 云团：一个整体的凹凸轮廓，沿朝向中心的方向打光（内亮外暗），外侧弧线勾出团块
    const rn = rng(seed), dx = CX - x, dy = CY - y, d = Math.hypot(dx, dy) || 1, ux = dx / d, uy = dy / d, cs = [];
    for (let i = 0; i < 8; i++) cs.push([x + (rn() - .5) * r * 2.0, y + (rn() - .5) * r * 0.9, r * (0.34 + rn() * 0.34)]);
    const path = new Path2D(); cs.forEach(([px, py, rad]) => { path.moveTo(px + rad, py); path.arc(px, py, rad, 0, TAU); });
    g.save(); g.clip(path);
    const gr = g.createLinearGradient(x - ux * r * 1.4, y - uy * r * 1.4, x + ux * r * 1.4, y + uy * r * 1.4); gr.addColorStop(0, '#6e6890'); gr.addColorStop(0.35, '#c3a6a2'); gr.addColorStop(0.7, '#f0cc98'); gr.addColorStop(1, '#fff3d0');
    g.fillStyle = gr; g.fillRect(x - r * 2.4, y - r * 2, r * 4.8, r * 4);
    cs.forEach(([px, py, rad]) => { g.strokeStyle = 'rgba(86,76,120,.3)'; g.lineWidth = Math.max(4, rad * 0.14); g.beginPath(); g.arc(px, py, rad * 0.92, Math.atan2(-uy, -ux) - 1.0, Math.atan2(-uy, -ux) + 1.0); g.stroke();
      g.strokeStyle = 'rgba(255,248,222,.4)'; g.lineWidth = Math.max(3, rad * 0.08); g.beginPath(); g.arc(px, py, rad * 0.9, Math.atan2(uy, ux) - 0.8, Math.atan2(uy, ux) + 0.8); g.stroke(); });
    g.restore();
  }
  function build() {
    plate = P.canvas(); const g = plate.getContext('2d'), rn = rng(4);
    g.fillStyle = '#2a1e1c'; g.fillRect(0, 0, W, H);
    // 开口天空：中心暖金 → 边缘群青，加放射光
    const ix = 190, iy = 118, iw = 1540, ih = 844, ir = 150;
    g.save(); rr(g, ix, iy, iw, ih, ir); g.clip();
    const sg = g.createRadialGradient(CX, CY - 20, 20, CX, CY, 900); sg.addColorStop(0, '#fff6d0'); sg.addColorStop(0.22, '#f4d58e'); sg.addColorStop(0.5, '#c2a0a0'); sg.addColorStop(0.8, '#5a669a'); sg.addColorStop(1, '#2c3a72'); g.fillStyle = sg; g.fillRect(0, 0, W, H);
    g.globalCompositeOperation = 'screen'; for (let i = 0; i < 28; i++) { const a = i / 28 * TAU, w = 0.04 + (i % 3) * 0.02; g.fillStyle = 'rgba(255,238,190,.09)'; g.beginPath(); g.moveTo(CX, CY); g.lineTo(CX + Math.cos(a - w) * 1100, CY + Math.sin(a - w) * 1100); g.lineTo(CX + Math.cos(a + w) * 1100, CY + Math.sin(a + w) * 1100); g.closePath(); g.fill(); } g.globalCompositeOperation = 'source-over';
    // 环绕的云团
    for (let i = 0; i < 16; i++) { const a = i / 16 * TAU + rn() * 0.2, k = 0.9 + rn() * 0.2; cloud(g, CX + Math.cos(a) * RX * k * 1.05, CY + Math.sin(a) * RY * k * 1.12, 90 + rn() * 70, 40 + i); }
    for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + 0.4; cloud(g, CX + Math.cos(a) * 250, CY + Math.sin(a) * 130, 60 + rn() * 30, 90 + i); }
    g.restore();
    // 画框：三层灰泥带，向内一层比一层亮，外层有深色阴影缝；内缘金线；蛋形纹
    const bands = [[0, '#9c8a6e'], [34, '#e4d8be'], [74, '#cbbd9c'], [112, '#f0e6cc'], [140, '#c89a3c']];
    bands.forEach(([off, col], k) => { g.fillStyle = col; rr(g, ix - 150 + off, iy - 100 + off * 0.65, iw + 300 - off * 2, ih + 200 - off * 1.3, ir + 150 - off); g.fill(); });
    g.save(); rr(g, ix, iy, iw, ih, ir); g.clip(); g.fillStyle = 'rgba(0,0,0,.12)'; g.fillRect(0, 0, W, H); g.restore();
    g.globalCompositeOperation = 'destination-over'; g.globalCompositeOperation = 'source-over';
    // 重画天空开口（帧压住了），保证「开口」在帧之上
    g.save(); rr(g, ix, iy, iw, ih, ir); g.clip(); g.drawImage(skyOnly(), 0, 0); g.restore();
    g.strokeStyle = '#c89a3c'; g.lineWidth = 12; rr(g, ix, iy, iw, ih, ir); g.stroke(); g.strokeStyle = 'rgba(60,40,20,.5)'; g.lineWidth = 4; rr(g, ix - 8, iy - 8, iw + 16, ih + 16, ir + 8); g.stroke();
    // 蛋形纹沿框走
    g.fillStyle = '#f6eed8'; for (let i = 0; i < 70; i++) { const q = i / 70, th = q * TAU, x = CX + Math.cos(th) * (iw / 2 + 52), y = CY + Math.sin(th) * (ih / 2 + 52); g.save(); g.translate(x, y); g.rotate(th + Math.PI / 2); g.beginPath(); g.ellipse(0, 0, 6, 11, 0, 0, TAU); g.fill(); g.strokeStyle = 'rgba(120,96,60,.6)'; g.lineWidth = 1.6; g.stroke(); g.restore(); }
    // 四角金圆章
    [[ix - 20, iy - 14], [ix + iw + 20, iy - 14], [ix - 20, iy + ih + 14], [ix + iw + 20, iy + ih + 14]].forEach(([x, y]) => { const gr = g.createRadialGradient(x - 14, y - 14, 4, x, y, 76); gr.addColorStop(0, '#fff0b8'); gr.addColorStop(0.5, '#d0a040'); gr.addColorStop(1, '#7a5a1c'); g.fillStyle = gr; g.beginPath(); g.arc(x, y, 76, 0, TAU); g.fill(); g.strokeStyle = '#f6eed8'; g.lineWidth = 9; g.stroke(); g.strokeStyle = 'rgba(80,50,20,.7)'; g.lineWidth = 3; g.beginPath(); g.arc(x, y, 50, 0, TAU); g.stroke(); });
    // 外缘最深的阴影，把画框「压」进天顶
    const vg = g.createRadialGradient(CX, CY, 600, CX, CY, 1150); vg.addColorStop(0, 'rgba(30,20,20,0)'); vg.addColorStop(1, 'rgba(30,20,20,.55)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);
    built = true;
  }
  let _sky = null; function skyOnly() { if (_sky) return _sky; const cv = P.canvas(), g = cv.getContext('2d'), rn = rng(4);
    const sg = g.createRadialGradient(CX, CY - 20, 20, CX, CY, 900); sg.addColorStop(0, '#fff6d0'); sg.addColorStop(0.22, '#f4d58e'); sg.addColorStop(0.5, '#c2a0a0'); sg.addColorStop(0.8, '#5a669a'); sg.addColorStop(1, '#2c3a72'); g.fillStyle = sg; g.fillRect(0, 0, W, H);
    g.globalCompositeOperation = 'screen'; for (let i = 0; i < 28; i++) { const a = i / 28 * TAU, w = 0.04 + (i % 3) * 0.02; g.fillStyle = 'rgba(255,238,190,.09)'; g.beginPath(); g.moveTo(CX, CY); g.lineTo(CX + Math.cos(a - w) * 1100, CY + Math.sin(a - w) * 1100); g.lineTo(CX + Math.cos(a + w) * 1100, CY + Math.sin(a + w) * 1100); g.closePath(); g.fill(); } g.globalCompositeOperation = 'source-over';
    for (let i = 0; i < 16; i++) { const a = i / 16 * TAU + rn() * 0.2, k = 0.9 + rn() * 0.2; cloud(g, CX + Math.cos(a) * RX * k * 1.05, CY + Math.sin(a) * RY * k * 1.12, 90 + rn() * 70, 40 + i); }
    for (let i = 0; i < 4; i++) { const a = i / 4 * TAU + 0.4; cloud(g, CX + Math.cos(a) * 250, CY + Math.sin(a) * 130, 60 + rn() * 30, 90 + i); }
    return (_sky = cv); }
  // 衣带：沿螺旋线的一条绸，宽度起伏、两面深浅不同
  function ribbon(g, t, ph, col, R0, dir) {
    const N = 60, L = [], Rr = [];
    for (let i = 0; i <= N; i++) { const q = i / N, a = ph + dir * (t * 0.35 + q * 2.4), r = lerp(0.55, 1.05, q + Math.sin(q * 6 + t) * 0.05), x = CX + Math.cos(a) * RX * r * R0, y = CY + Math.sin(a) * RY * r * R0, w = 46 * Math.sin(q * Math.PI) * (0.6 + 0.4 * Math.cos(q * 9 + t * 2));
      const nl = Math.hypot(Math.cos(a) * RY, Math.sin(a) * RX) || 1, nx = Math.cos(a) * RY / nl, ny = Math.sin(a) * RX / nl; L.push([x + nx * w, y + ny * w]); Rr.push([x - nx * w, y - ny * w]); }
    g.fillStyle = col[1]; g.beginPath(); L.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); Rr.reverse().forEach(p => g.lineTo(p[0], p[1])); g.closePath(); g.fill();
    g.strokeStyle = col[0]; g.lineWidth = 3; g.beginPath(); L.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke();
  }
  function draw(c, lt) {
    if (!built) build();
    const t = clamp(lt, 0, 6);
    const live = P.scratch('cort_live'), g = live.getContext('2d'); g.reset(); g.drawImage(plate, 0, 0);
    ribbon(g, t, 0.5, ROB.red, 0.95, 1); ribbon(g, t, 3.4, ROB.blue, 0.82, 1);
    // 人群：绕中心旋转，头朝外（徐徐翻转），手臂举向光；半数漫出画框
    const FIG = [['red', 'ochre', 0.0, 260, 1], ['blue', 'rose', 0.7, 240, -1], ['white', 'blue', 1.4, 250, 1], ['ochre', 'red', 2.1, 230, -1], ['green', 'white', 2.8, 255, 1], ['rose', 'blue', 3.5, 235, -1], ['blue', 'ochre', 4.2, 245, 1], ['red', 'green', 4.9, 240, -1], ['white', 'rose', 5.6, 250, 1]];
    FIG.forEach(([rb, mt, a0, h, face], i) => {
      const a = a0 + t * 0.22, k = 0.92 + 0.12 * Math.sin(a0 * 2.1), x = CX + Math.cos(a) * RX * k * 1.04, y = CY + Math.sin(a) * RY * k * 1.1, rot = a + Math.PI / 2 + 0.5 * Math.sin(t * 0.8 + i);
      g.save(); g.translate(x, y); g.rotate(rot + Math.PI); const sz = h * (0.78 + 0.22 * ((Math.sin(a) + 1) / 2));
      M.figure(g, { x: 0, y: sz * 0.5, h: sz, face, lean: 0.12 * Math.sin(t * 1.3 + i), bow: 0.1, t, seed: 60 + i, halo: false, robe: ROB[rb], mantle: ROB[mt], under: '#f6ecd0', skin: '#e6b48a', hair: '#5b3a22', sway: 0.9,
        gaze: [0, -sz * 0.9], hands: [[-sz * 0.34 * face, -sz * 0.34 + Math.sin(t * 2 + i) * 8], [sz * 0.3 * face, -sz * 0.18]] });
      g.restore();
    });
    // 中心：金色圆光里一位白衣者（最亮），光晕呼吸
    const br = 0.5 + 0.5 * Math.sin(t * 1.6), cg = g.createRadialGradient(CX, CY, 10, CX, CY, 220 + br * 30); cg.addColorStop(0, 'rgba(255,248,214,.95)'); cg.addColorStop(1, 'rgba(255,230,160,0)'); g.fillStyle = cg; g.beginPath(); g.arc(CX, CY, 260, 0, TAU); g.fill();
    g.save(); g.translate(CX, CY + 10); g.rotate(Math.sin(t * 0.5) * 0.1); M.figure(g, { x: 0, y: 120, h: 240, face: 1, lean: 0.04, t, seed: 99, halo: true, robe: ROB.white, mantle: ROB.ochre, under: '#fffaf0', skin: '#f0c49a', hair: '#8a5a2a', sway: 0.8, gaze: [0, -150], hands: [[-70, -26], [70, -26]] }); g.restore();
    M.fresco(c, live, { ground: M.plaster('cortona', { base: '#d8c8a8', seed: 17 }), chalk: 0.03, soften: 0.4, plasterAlpha: 0.32, sat: 1.12 });
    c.save(); c.globalCompositeOperation = 'screen'; const hg = c.createRadialGradient(CX, CY, 0, CX, CY, 520); hg.addColorStop(0, `rgba(255,236,180,${0.28 + br * 0.1})`); hg.addColorStop(1, 'rgba(255,220,150,0)'); c.fillStyle = hg; c.fillRect(0, 0, W, H); c.restore();
  }
  return { draw };
})();
