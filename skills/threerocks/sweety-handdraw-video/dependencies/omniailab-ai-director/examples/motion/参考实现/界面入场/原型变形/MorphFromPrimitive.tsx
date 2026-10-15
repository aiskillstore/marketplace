// ---
// name: omniailab-motion-demo-morph-from-primitive
// description: 原型变形｜原型变形
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 原型变形｜原型变形
// 正圆呼吸一拍(anticipation) → path d 逐数值插值变形成 520×300 圆角矩形卡片轮廓
// → 卡片内部灰阶内容条淡入。全部帧驱动、确定性。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const CX = 960;
const CY = 540;
const R = 130;
const RECT_W = 520;
const RECT_H = 300;
const RECT_R = 20;

// ---- 同构 path：M + 8 段 cubic（4 直边段 + 4 圆角段），圆与圆角矩形共用锚点拓扑 ----
// 圆角矩形锚点（中心坐标系，顺时针，从右边上端点起）：
// A0(hw,-ihh) 右边上 → A1(hw,ihh) 右边下 → A2(iw,hh) 底边右 → A3(-iw,hh) 底边左
// → A4(-hw,ihh) 左边下 → A5(-hw,-ihh) 左边上 → A6(-iw,-hh) 顶边左 → A7(iw,-hh) 顶边右 → A0
const hw = RECT_W / 2; // 260
const hh = RECT_H / 2; // 150
const iw = hw - RECT_R; // 240
const ihh = hh - RECT_R; // 130
const KAPPA = 0.5522847498;

type Seg = [number, number, number, number, number, number]; // c1x c1y c2x c2y x y
type Shape = { start: [number, number]; segs: Seg[] };

const line = (from: [number, number], to: [number, number]): Seg => [
  from[0] + (to[0] - from[0]) / 3,
  from[1] + (to[1] - from[1]) / 3,
  from[0] + ((to[0] - from[0]) * 2) / 3,
  from[1] + ((to[1] - from[1]) * 2) / 3,
  to[0],
  to[1],
];
// 90° 圆角弧 from → to（弧心 c）：c1 = from + k·(to−c)，c2 = to + k·(from−c)
const corner = (
  from: [number, number],
  to: [number, number],
  c: [number, number]
): Seg => [
  from[0] + KAPPA * (to[0] - c[0]),
  from[1] + KAPPA * (to[1] - c[1]),
  to[0] + KAPPA * (from[0] - c[0]),
  to[1] + KAPPA * (from[1] - c[1]),
  to[0],
  to[1],
];

const rectAnchors: [number, number][] = [
  [hw, -ihh],
  [hw, ihh],
  [iw, hh],
  [-iw, hh],
  [-hw, ihh],
  [-hw, -ihh],
  [-iw, -hh],
  [iw, -hh],
];
const cornerCenters: [number, number][] = [
  [iw, ihh], // A1→A2 右下
  [-iw, ihh], // A3→A4 左下
  [-iw, -ihh], // A5→A6 左上
  [iw, -ihh], // A7→A0 右上
];

const rectShape: Shape = {
  start: rectAnchors[0],
  segs: [
    line(rectAnchors[0], rectAnchors[1]),
    corner(rectAnchors[1], rectAnchors[2], cornerCenters[0]),
    line(rectAnchors[2], rectAnchors[3]),
    corner(rectAnchors[3], rectAnchors[4], cornerCenters[1]),
    line(rectAnchors[4], rectAnchors[5]),
    corner(rectAnchors[5], rectAnchors[6], cornerCenters[2]),
    line(rectAnchors[6], rectAnchors[7]),
    corner(rectAnchors[7], rectAnchors[0], cornerCenters[3]),
  ],
};

// 圆：锚点取矩形锚点的同方位角，段间用精确弧公式 k = 4/3·tan(Δθ/4)
const angles = rectAnchors.map(([x, y]) => Math.atan2(y, x));
const circAnchors: [number, number][] = angles.map((a) => [
  R * Math.cos(a),
  R * Math.sin(a),
]);
const arcSeg = (i: number): Seg => {
  const a1 = angles[i];
  let a2 = angles[(i + 1) % 8];
  if (a2 <= a1) a2 += Math.PI * 2;
  const k = (4 / 3) * Math.tan((a2 - a1) / 4);
  const p1 = circAnchors[i];
  const p2 = circAnchors[(i + 1) % 8];
  return [
    p1[0] - k * R * Math.sin(a1),
    p1[1] + k * R * Math.cos(a1),
    p2[0] + k * R * Math.sin(a2 % (Math.PI * 2)),
    p2[1] - k * R * Math.cos(a2 % (Math.PI * 2)),
    p2[0],
    p2[1],
  ];
};
const circShape: Shape = {
  start: circAnchors[0],
  segs: [0, 1, 2, 3, 4, 5, 6, 7].map(arcSeg),
};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const f2 = (n: number) => n.toFixed(2);

const morphPath = (t: number): string => {
  const sx = lerp(circShape.start[0], rectShape.start[0], t);
  const sy = lerp(circShape.start[1], rectShape.start[1], t);
  let d = `M ${f2(CX + sx)} ${f2(CY + sy)}`;
  for (let i = 0; i < 8; i++) {
    const a = circShape.segs[i];
    const b = rectShape.segs[i];
    const v = a.map((n, j) => lerp(n, b[j], t));
    d += ` C ${f2(CX + v[0])} ${f2(CY + v[1])} ${f2(CX + v[2])} ${f2(
      CY + v[3]
    )} ${f2(CX + v[4])} ${f2(CY + v[5])}`;
  }
  return d + ' Z';
};

// ---- 时间轴（30fps，总 140f）----
// 0–10 静置圆 | 10–30 呼吸一拍 scale 1→1.06→1 | 30–54 变形 24f
// | 56–68 内容条淡入 12f | 68–140 真静止 72f
export const MorphFromPrimitive: React.FC = () => {
  const frame = useCurrentFrame();

  const breath = interpolate(frame, [10, 20, 30], [1, 1.12, 1], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const t = interpolate(frame, [30, 54], [0, 1], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const contentOpacity = interpolate(frame, [56, 68], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const d = morphPath(t);

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative' }}>
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{ position: 'absolute', inset: 0 }}
      >
        <g transform={`translate(${CX} ${CY}) scale(${breath}) translate(${-CX} ${-CY})`}>
          <path d={d} fill="none" stroke={G.ink} strokeWidth={3} />
        </g>
      </svg>
      {/* 卡片内容条（参考 线条沸腾 描边卡内容），变形完成后淡入 */}
      <div
        style={{
          position: 'absolute',
          left: CX - RECT_W / 2,
          top: CY - RECT_H / 2,
          width: RECT_W,
          height: RECT_H,
          boxSizing: 'border-box',
          padding: 36,
          display: 'flex',
          flexDirection: 'column',
          gap: 18,
          opacity: contentOpacity,
        }}
      >
        <div style={{ height: 26, width: '58%', background: G.bar, borderRadius: 13 }} />
        <div style={{ height: 16, width: '86%', background: G.line, borderRadius: 8 }} />
        <div style={{ height: 16, width: '72%', background: G.line, borderRadius: 8 }} />
        <div style={{ marginTop: 'auto', display: 'flex', gap: 14, alignItems: 'center' }}>
          <div style={{ width: 40, height: 40, borderRadius: 20, background: G.mid }} />
          <div style={{ height: 16, width: 120, background: G.line, borderRadius: 8 }} />
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

