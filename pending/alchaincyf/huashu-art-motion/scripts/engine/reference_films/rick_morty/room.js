// 第 36 种画风：Rick and Morty。
// 把 art-motion 35 种画风共用的那间屋（左窗、中桌、右边坐着端杯的少女、桌前的猫）按车库复刻量出来的画法重画一遍：
// 描边 #222323、2.35px、圆头圆角；平涂＋斑驳纹理（mtDark）；人和猫是大圆眼白＋小黑点瞳孔、眼皮可眨。
// 坐标系 = 车库 SVG（1920×1088，舞台上移 4px 显示成 1920×1080）。
window.ROOM36 = (() => {
  const { S, INK, smoothPath: sp, mixedPath: mp, f1 } = RM;
  const C = {
    wall: '#cdbf96', wallDk: '#b9aa80', trim: '#eee6cf', floor: '#9b7752', floorDk: '#87643f', plank: '#7a5a3a',
    sky: '#a7d6ea', skyLt: '#c6e5ef', hill: '#86b553', hillDk: '#6d9a40', tree: '#5f8f3a', trunk: '#7b5a3a', fence: '#f1efe4',
    table: '#a0683f', tableDk: '#83532f', rug: '#b85c4a', rugLt: '#d07a63', chair: '#5d6f8a', chairDk: '#4a5a72',
    skin: '#efc4a0', hair: '#f0cf63', hairDk: '#d8b24a', dress: '#d65a4f', dressDk: '#b9473e', shoe: '#4d4c50', mug: '#f2f0e8',
    cat: '#e99a4f', catDk: '#c4733a', catLt: '#f6e7d2', nose: '#e58f98', pot: '#c4683f', leaf: '#5a9a45', leafDk: '#467d35',
  };
  let root, girl, cat, refs = {};

  // ---------- 静态：墙、窗、地板、地毯、桌、椅、盆栽 ----------
  function backdrop() {
    let s = '';
    s += S.rect(0, 0, 1920, 800, C.wall, { stroke: 'none' }) + S.rect(0, 0, 1920, 800, 'url(#mtDark)', { stroke: 'none', op: .55 });
    // 墙裙线、踢脚线
    s += S.rect(0, 560, 1920, 14, C.trim, { w: 2.2 });
    s += S.rect(0, 574, 1920, 226, C.wallDk, { stroke: 'none' }) + S.rect(0, 574, 1920, 226, 'url(#mtDark)', { stroke: 'none', op: .5 });
    for (let x = -20; x < 1920; x += 96) s += S.line(x, 576, x, 786, { w: 1.6, stroke: '#9f915f', op: .8 });
    s += S.rect(0, 786, 1920, 22, C.trim, { w: 2.35 });
    // 地板
    s += S.rect(0, 808, 1920, 290, C.floor, { stroke: 'none' }) + S.rect(0, 808, 1920, 290, 'url(#mtDark)', { stroke: 'none', op: .6 });
    for (const y of [852, 912, 990, 1080]) s += S.line(0, y, 1920, y, { w: 2, stroke: C.plank });
    const r = RM.mulberry32(36);
    for (const [y0, y1] of [[808, 852], [852, 912], [912, 990], [990, 1080]]) { let x = -r() * 300; while (x < 1920) { x += 260 + r() * 260; s += S.line(f1(x), y0, f1(x), y1, { w: 2, stroke: C.plank }); } }
    // 窗（左）：外框、窗外的郊区（天、坡、篱笆、树）
    s += S.rect(352, 112, 456, 470, C.trim, { rx: 6 });
    s += `<clipPath id="r36win"><rect x="376" y="136" width="408" height="408"/></clipPath>`;
    let out = S.rect(376, 136, 408, 408, C.sky, { stroke: 'none' });
    out += S.ell(470, 210, 60, 18, C.skyLt, { stroke: 'none', op: .9 }) + S.ell(660, 180, 48, 14, C.skyLt, { stroke: 'none', op: .9 });
    out += S.path(sp([[360, 430], [470, 392], [600, 410], [720, 380], [800, 400], [800, 560], [360, 560]], true, .5), C.hill);
    out += S.path(sp([[360, 480], [520, 452], [680, 470], [800, 455], [800, 560], [360, 560]], true, .5), C.hillDk);
    out += S.path('M664 470 L664 400', 'none', { w: 9, stroke: C.trunk }) + S.path('M664 470 L664 400', 'none', { w: 2.35 });
    out += S.path(sp([[620, 380], [628, 342], [660, 322], [698, 336], [712, 372], [696, 402], [660, 410], [628, 402]]), C.tree);
    for (let x = 384; x < 790; x += 34) out += S.path(`M${x} 540 L${x} 494 L${x + 11} 484 L${x + 22} 494 L${x + 22} 540 Z`, C.fence, { w: 2 });
    out += S.rect(376, 506, 408, 9, C.fence, { w: 2 });
    s += `<g clip-path="url(#r36win)">${out}</g>`;
    s += S.rect(376, 136, 408, 408, 'none') + S.rect(572, 136, 16, 408, C.trim, { w: 2 }) + S.rect(376, 332, 408, 16, C.trim, { w: 2 });
    s += S.rect(334, 574, 492, 22, C.trim, { rx: 4 });
    // 墙上的画框：一扇小小的绿传送门（自己画派的签名）
    s += S.rect(1010, 190, 170, 132, '#8a6440', { rx: 3 }) + S.rect(1024, 204, 142, 104, '#2c3a2e', { w: 2 });
    s += S.ell(1095, 256, 40, 34, '#97ce4c', { w: 2.2 }) + S.ell(1095, 256, 26, 21, '#c8ec7a', { stroke: 'none' }) +
      S.path('M1095 256 m-20 0 q8 -16 22 -8 q12 8 2 20 q-10 8 -16 -2', 'none', { w: 2.2, stroke: '#4f8a2a' });
    // 地毯
    s += S.ell(1040, 948, 470, 58, C.rug) + S.ell(1040, 948, 420, 44, 'none', { w: 2, stroke: C.rugLt });
    // 桌（中）
    s += S.poly('905,668 921,668 930,915 897,915', C.tableDk) + S.poly('1112,668 1128,668 1138,915 1105,915', C.tableDk);
    s += S.poly('840,640 1210,640 1218,668 832,668', C.table) + S.rect(832, 668, 386, 14, C.tableDk);
    s += S.path('M884 640 Q900 646 916 640 M1000 640 Q1020 647 1040 640', 'none', { w: 1.8, stroke: '#7a4a2a' });
    // 桌上的盘子和饼干
    s += S.ell(990, 636, 46, 9, '#efece2', { w: 2.2 }) + S.ell(978, 630, 12, 5, '#d4a259', { w: 2 }) + S.ell(1000, 629, 12, 5, '#d4a259', { w: 2 });
    // 椅子（少女后面）
    s += S.rect(1536, 470, 34, 300, C.chair, { rx: 8 }) + S.rect(1392, 470, 34, 300, C.chair, { rx: 8 });
    s += S.rect(1392, 470, 178, 60, C.chairDk, { rx: 8 });
    // 盆栽（右角）
    s += S.path(sp([[1736, 700], [1712, 600], [1700, 520], [1726, 470], [1752, 540], [1760, 640]], true, .5), C.leaf);
    s += S.path(sp([[1760, 700], [1790, 590], [1830, 520], [1846, 556], [1812, 640], [1780, 702]], true, .5), C.leafDk);
    s += S.path(sp([[1748, 700], [1760, 600], [1774, 500], [1792, 520], [1780, 620], [1766, 702]], true, .5), C.leaf);
    s += S.poly('1712,700 1830,700 1816,790 1726,790', C.pot) + S.rect(1704, 690, 134, 20, '#d47a4f', { rx: 3 });
    return s;
  }

  // ---------- 少女：正面坐在椅子上，双手捧杯（脸、眼睛的造法照 Morty） ----------
  function girlSVG() {
    let s = '';
    // 后发：长发垂在肩后（先画，压在裙子后面）
    s += S.path(sp([[1424, 420], [1414, 500], [1418, 572], [1446, 588], [1514, 588], [1542, 572], [1546, 500], [1536, 420], [1480, 384]], true, .55), C.hairDk);
    // 椅面、腿、鞋
    s += S.rect(1384, 728, 194, 26, C.chairDk, { rx: 6 });
    s += S.path('M1423 752 L1421 890 L1451 890 L1453 752', C.skin) + S.path('M1505 752 L1508 890 L1538 890 L1535 752', C.skin);
    s += S.path(sp([[1418, 884], [1402, 896], [1404, 908], [1450, 908], [1456, 892], [1452, 882]], true, .4), C.shoe);
    s += S.path(sp([[1506, 882], [1504, 894], [1510, 908], [1556, 908], [1558, 896], [1540, 884]], true, .4), C.shoe);
    // 裙子与身体
    s += S.path(sp([[1428, 560], [1408, 640], [1392, 730], [1400, 772], [1480, 782], [1562, 772], [1570, 730], [1554, 640], [1534, 560], [1480, 548]], true, .5), C.dress);
    s += S.path('M1452 600 Q1446 680 1440 770 M1508 600 Q1514 680 1520 770', 'none', { w: 2, stroke: C.dressDk });
    s += S.path('M1460 552 Q1480 574 1500 552', 'none', { w: 2.35 });
    // 脖子
    s += S.path('M1468 528 L1468 556 Q1480 562 1492 556 L1492 528', C.skin);
    return s;
  }
  // 头（单独一组：眨眼、看人、喝水时微仰）
  function girlHeadSVG() {
    let s = '';
    // 脸（Morty 的脸型略收窄）
    s += S.path(sp([[1480, 392], [1452, 398], [1434, 414], [1426, 440], [1428, 470], [1440, 496], [1460, 514], [1480, 520], [1500, 514], [1520, 496], [1532, 470], [1534, 440], [1526, 414], [1508, 398]]), C.skin);
    // 刘海＋两侧头发
    s += S.path(mp([[1424, 452], [1420, 414], [1436, 386], [1462, 372], [1492, 370], [1520, 380], [1538, 402], [1542, 440], [1536, 462], [1526, 430], [1508, 412], [1494, 428], [1480, 414], [1462, 430], [1450, 414], [1434, 434]], new Set([9, 10, 12, 14]), .5), C.hair);
    // 眼睛（大眼白＋小黑点，眼皮可合）
    for (const [k, x] of [['L', 1462], ['R', 1500]]) {
      s += `<clipPath id="g36eye${k}"><ellipse cx="${x}" cy="452" rx="14" ry="16"/></clipPath>`;
      s += S.ell(x, 452, 14, 16, '#ebebe8', { w: 2.6 });
      s += S.circ(x, 452, 2.4, INK, { stroke: 'none', cls: 'g36pup' });
      s += `<g clip-path="url(#g36eye${k})"><rect class="g36lid" x="${x - 17}" y="433" width="34" height="0" fill="${C.skin}" stroke="${INK}" stroke-width="2.4"/></g>`;
      s += S.ell(x, 452, 14, 16, 'none', { w: 2.6 });
      s += S.path(`M${x - 13} 432 Q${x} 426 ${x + 12} 431`, 'none', { w: 2.2 });
    }
    s += S.path('M1478 470 Q1474 478 1482 480', 'none', { w: 2.2 });
    s += `<g class="g36mouth">${S.path('M1472 494 Q1481 500 1490 494', 'none', { w: 2.4 })}</g>`;
    s += S.ell(1446, 482, 7, 4, '#eaa58c', { stroke: 'none', op: .6 }) + S.ell(1516, 482, 7, 4, '#eaa58c', { stroke: 'none', op: .6 });
    return s;
  }
  // 手臂＋杯子（一组：抿一口时整体抬起）
  function girlArmsSVG() {
    let s = '';
    s += S.path(sp([[1424, 576], [1404, 630], [1418, 664], [1460, 660], [1466, 646], [1432, 640], [1440, 590]], true, .4), C.dress, { cls: 'r36sleeve' });
    s += S.path(sp([[1536, 576], [1556, 630], [1542, 664], [1500, 660], [1494, 646], [1528, 640], [1520, 590]], true, .4), C.dress, { cls: 'r36sleeve' });
    s += S.rect(1462, 612, 36, 46, C.mug, { rx: 5 }) + S.path('M1498 622 Q1514 624 1512 638 Q1510 650 1498 648', 'none', { w: 2.35 });
    s += S.path('M1462 624 L1498 624', 'none', { w: 1.8, stroke: '#b9b5a8' });
    s += S.ell(1458, 652, 11, 9, C.skin, { w: 2.2 }) + S.ell(1502, 652, 11, 9, C.skin, { w: 2.2 });
    return s;
  }

  // ---------- 猫：正面坐在地上，大眼、尾巴摆 ----------
  function catBodySVG() {
    let s = '';
    s += S.path(sp([[420, 760], [392, 800], [384, 846], [398, 880], [452, 888], [506, 880], [520, 846], [512, 800], [486, 760]], true, .55), C.cat);
    s += S.path(sp([[434, 800], [424, 840], [432, 876], [474, 876], [482, 840], [472, 800]], true, .5), C.catLt, { stroke: 'none' });
    s += S.path('M396 820 Q410 818 418 826 M392 846 Q406 844 414 852 M512 820 Q498 818 490 826 M516 846 Q502 844 494 852', 'none', { w: 2.2, stroke: C.catDk });
    // 前爪
    s += S.ell(432, 884, 18, 9, C.catLt, { w: 2.2 }) + S.ell(476, 884, 18, 9, C.catLt, { w: 2.2 });
    return s;
  }
  function catHeadSVG() {
    let s = '';
    s += S.poly('398,712 404,652 446,690', C.cat) + S.poly('508,712 502,652 460,690', C.cat);
    s += S.poly('407,700 410,668 432,690', C.nose, { stroke: 'none' }) + S.poly('499,700 496,668 474,690', C.nose, { stroke: 'none' });
    s += S.path(sp([[453, 672], [418, 680], [396, 704], [392, 736], [408, 764], [453, 776], [498, 764], [514, 736], [510, 704], [488, 680]], true, .55), C.cat);
    s += S.path('M440 676 L444 694 M453 672 L453 692 M466 676 L462 694', 'none', { w: 2.2, stroke: C.catDk });
    for (const [k, x] of [['L', 433], ['R', 473]]) {
      s += `<clipPath id="c36eye${k}"><ellipse cx="${x}" cy="720" rx="13" ry="15"/></clipPath>`;
      s += S.ell(x, 720, 13, 15, '#eef0d6', { w: 2.5 });
      s += S.circ(x, 720, 2.5, INK, { stroke: 'none', cls: 'c36pup' });
      s += `<g clip-path="url(#c36eye${k})"><rect class="c36lid" x="${x - 16}" y="703" width="32" height="0" fill="${C.cat}" stroke="${INK}" stroke-width="2.4"/></g>`;
      s += S.ell(x, 720, 13, 15, 'none', { w: 2.5 });
    }
    s += S.path('M447 742 L459 742 L453 749 Z', C.nose, { w: 2 }) + S.path('M453 749 Q448 757 441 754 M453 749 Q458 757 465 754', 'none', { w: 2.2 });
    s += S.path('M420 746 L388 740 M420 752 L390 756 M486 746 L518 740 M486 752 L516 756', 'none', { w: 1.8 });
    return s;
  }
  function tailPath(sw) {
    const k = sw;
    const pts = [[506, 870], [548, 872], [578, 852 + 6 * k], [588 + 8 * k, 820], [578 + 14 * k, 792 - 4 * k], [562 + 16 * k, 784 - 6 * k]];
    // 中心线 + 宽度 → 一条圆头尾巴
    const L = [], R = [];
    for (let i = 0; i < pts.length; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
      const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, w = 11 - i * 1.1;
      L.push([pts[i][0] - dy / l * w, pts[i][1] + dx / l * w]); R.push([pts[i][0] + dy / l * w, pts[i][1] - dx / l * w]);
    }
    return sp(L.concat(R.reverse()), true, .5);
  }

  function build() {
    root = RM.SCENE.add('L3', `<g id="room36" style="display:none"></g>`);
    root.innerHTML = backdrop() +
      `<g id="r36cat"><g id="r36tail">${S.path(tailPath(0), C.cat)}</g><g>${catBodySVG()}</g><g id="r36catHead">${catHeadSVG()}</g></g>` +
      `<g id="r36girl">${girlSVG()}<g id="r36gHead">${girlHeadSVG()}</g><g id="r36gArms">${girlArmsSVG()}</g></g>`;
    refs = {
      tail: root.querySelector('#r36tail path'), catHead: root.querySelector('#r36catHead'),
      gHead: root.querySelector('#r36gHead'), gArms: root.querySelector('#r36gArms'),
      gPup: [...root.querySelectorAll('.g36pup')], gLid: [...root.querySelectorAll('.g36lid')],
      cPup: [...root.querySelectorAll('.c36pup')], cLid: [...root.querySelectorAll('.c36lid')],
    };
  }
  const blinkAt = (t, seed) => { const per = 2.9 + seed * .7, ph = (t + seed * 1.3) % per; return ph < .16 ? (ph < .08 ? ph / .08 : (0.16 - ph) / .08) : 0; };
  // st: { look:[x,y] 少女/猫瞳孔偏移（-1..1）, catLook, sip 0..1, catJump 0..1 }
  function update(t, st = {}) {
    if (!root) return;
    refs.tail.setAttribute('d', tailPath(Math.sin(t * 2.4)));
    const gl = st.look || [0, 0], cl = st.catLook || gl;
    refs.gPup.forEach(p => p.setAttribute('transform', `translate(${f1(gl[0] * 8)} ${f1(gl[1] * 9)})`));
    refs.cPup.forEach(p => p.setAttribute('transform', `translate(${f1(cl[0] * 7)} ${f1(cl[1] * 8)})`));
    const gb = st.gBlink ?? blinkAt(t, 1), cb = st.cBlink ?? blinkAt(t, 2);
    refs.gLid.forEach(l => l.setAttribute('height', f1(38 * gb)));
    refs.cLid.forEach(l => l.setAttribute('height', f1(34 * cb)));
    const sip = st.sip || 0;
    refs.gArms.setAttribute('transform', `translate(0 ${f1(-sip * 112)})`);
    // 袖口随杯子，上臂锚点补偿组位移，肩部留在原位。
    const lift = sip * 112, sleeves = refs.gArms.querySelectorAll('.r36sleeve');
    sleeves[0].setAttribute('d', sp([[1424,576+lift],[1404,630+lift*.35],[1418,664],[1460,660],[1466,646],[1432,640],[1440,590+lift]],true,.4));
    sleeves[1].setAttribute('d', sp([[1536,576+lift],[1556,630+lift*.35],[1542,664],[1500,660],[1494,646],[1528,640],[1520,590+lift]],true,.4));
    refs.gHead.setAttribute('transform', `rotate(${f1(-sip * 4 + Math.sin(t * 1.3) * 1.2)} 1480 520)`);
    const jy = st.catJump ? -Math.sin(Math.PI * Math.min(1, st.catJump)) * 46 : 0;
    refs.catHead.setAttribute('transform', `translate(${f1(Math.sin(t * 1.1) * 2)} 0) rotate(${f1(Math.sin(t * .9) * 3)} 453 770)`);
    root.querySelector('#r36cat').setAttribute('transform', `translate(0 ${f1(jy)})`);
  }
  return { build, update, get el() { return root; } };
})();
