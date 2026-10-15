// ---
// name: omniailab-motion-demo-dataviz-landscape-open
// description: 参考实现——参考实现/开场/数据流线地景/DatavizLandscapeOpen.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

/**
 * DatavizLandscapeOpen — 暗场支流线束地景开场
 * 配方卡: 镜头卡/opening/数据流线地景.md
 *
 * 隐喻: 无数团队工作流(支流)汇成一个产品(主干)。
 * 三层景深: 近景大虚焦流过 / 中景标签清晰可读 / 远景渐隐。
 * 相机: 低速匀稳横移 + 视差 + 极缓 zoom, 收尾不急刹。
 */

const W = 1920;
const H = 1080;
const DUR = 165; // 5.5s @30fps
const WORLD_W = 4200;

// ---------- easing ----------
const outCubic = (t: number) => 1 - Math.pow(1 - t, 3);

const growth = (frame: number, start: number, dur: number) => {
  const t = Math.min(1, Math.max(0, (frame - start) / dur));
  return outCubic(t);
};

// ---------- geometry ----------
type Pt = {x: number; y: number};

// 主干: 缓和的水系曲线 (世界坐标)
const trunkY = (x: number) => 480 + 55 * Math.sin((x - 300) / 1050);
const trunkSlope = (x: number) => (55 / 1050) * Math.cos((x - 300) / 1050);

const trunkPath = () => {
  const pts: string[] = [];
  for (let x = -300; x <= WORLD_W + 100; x += 50) {
    pts.push(`${x === -300 ? 'M' : 'L'} ${x} ${trunkY(x).toFixed(1)}`);
  }
  return pts.join(' ');
};

// 三次贝塞尔求值 (用于把标签钉在线上)
const cubicAt = (p0: Pt, p1: Pt, p2: Pt, p3: Pt, t: number): Pt => {
  const u = 1 - t;
  return {
    x: u * u * u * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t * t * t * p3.x,
    y: u * u * u * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t * t * t * p3.y,
  };
};

// 支流: 起点在深处四散, 以切向汇入主干 (切线连续)
type Trib = {p0: Pt; p1: Pt; p2: Pt; p3: Pt; opacity: number; growStart: number; growDur: number};

const makeTrib = (
  start: Pt,
  mergeX: number,
  opacity: number,
  growStart: number,
  growDur: number,
): Trib => {
  const end: Pt = {x: mergeX, y: trunkY(mergeX)};
  const slope = trunkSlope(mergeX);
  const len = Math.hypot(1, slope);
  // P2 沿主干切线反向后退 => 到达时切线连续
  const p2: Pt = {x: end.x - (330 * 1) / len, y: end.y - (330 * slope) / len};
  const p1: Pt = {
    x: start.x + (end.x - start.x) * 0.35,
    y: start.y + (end.y - start.y) * 0.12,
  };
  return {p0: start, p1, p2, p3: end, opacity, growStart, growDur};
};

// 中景支流 6 条 (主角层), 错峰 4–6f
const MID_TRIBS: Trib[] = [
  makeTrib({x: -380, y: 130}, 1020, 0.62, 6, 32),
  makeTrib({x: -260, y: 880}, 1180, 0.55, 10, 32),
  makeTrib({x: -60, y: 40}, 1330, 0.7, 15, 32),
  makeTrib({x: 60, y: 960}, 1500, 0.5, 19, 32),
  makeTrib({x: 320, y: 210}, 1680, 0.6, 24, 32),
  makeTrib({x: 420, y: 790}, 1840, 0.55, 30, 32),
];

const tribPath = (t: Trib) =>
  `M ${t.p0.x} ${t.p0.y} C ${t.p1.x} ${t.p1.y}, ${t.p2.x} ${t.p2.y}, ${t.p3.x} ${t.p3.y}`;

// 远景 4 条: 更细更暗, 向更深处的远点收拢
// (控制点形式, 供节点标记取样——卡"视差可见性": 特征点穿过画面)
type FarLine = {p0: Pt; p1: Pt; p2: Pt; p3: Pt; growStart: number; growDur: number; op: number};
const FAR_LINES: FarLine[] = [
  {p0: {x: -300, y: 260}, p1: {x: 700, y: 250}, p2: {x: 2400, y: 330}, p3: {x: 3400, y: 490}, growStart: 12, growDur: 36, op: 0.3},
  {p0: {x: -200, y: 700}, p1: {x: 800, y: 690}, p2: {x: 2500, y: 610}, p3: {x: 3450, y: 492}, growStart: 16, growDur: 36, op: 0.26},
  {p0: {x: -350, y: 400}, p1: {x: 900, y: 390}, p2: {x: 2600, y: 420}, p3: {x: 3500, y: 493}, growStart: 22, growDur: 36, op: 0.33},
  {p0: {x: -250, y: 590}, p1: {x: 850, y: 600}, p2: {x: 2650, y: 560}, p3: {x: 3520, y: 494}, growStart: 27, growDur: 36, op: 0.24},
];
const farPath = (l: FarLine) =>
  `M ${l.p0.x} ${l.p0.y} C ${l.p1.x} ${l.p1.y}, ${l.p2.x} ${l.p2.y}, ${l.p3.x} ${l.p3.y}`;
// 远景节点标记: 每条线 3 枚暗点, 随层平移穿过画面 → 视差可辨
const FAR_NODE_TS = [0.28, 0.55, 0.82];

// 近景: 大虚焦斜向流过前景 (与横移运动方向成明显角度——
// 卡"视差可见性": 平行于运动方向的线沿自身滑动不可见)
const NEAR_LINES = [
  {d: 'M 130 1270 C 480 830, 880 360, 1290 -130', growStart: 2, growDur: 40, op: 0.22, w: 9},
  {d: 'M 1480 1240 C 1830 800, 2180 330, 2540 -110', growStart: 10, growDur: 40, op: 0.18, w: 7},
];

// ---------- 标签 (中景层, 全部虚构 ID) ----------
type LabelSpec = {trib: number; t: number; id: string; appear: number; above: boolean};

// 错峰 6–10f 间隔; 最后一枚 f103, 距交棒帧 (f120) ≥15f 无新增
const LABELS: LabelSpec[] = [
  {trib: 0, t: 0.62, id: 'OKR-1024', appear: 48, above: true},
  {trib: 1, t: 0.58, id: 'TEAM-4417', appear: 56, above: false},
  {trib: 2, t: 0.66, id: 'KR-2093', appear: 66, above: true},
  {trib: 3, t: 0.6, id: 'SYNC-3308', appear: 74, above: false},
  {trib: 4, t: 0.68, id: 'OBJ-2471', appear: 84, above: true},
  {trib: 5, t: 0.64, id: 'PLAN-9124', appear: 93, above: false},
  {trib: 4, t: 0.86, id: 'GOAL-7752', appear: 103, above: true},
];

// 汇点 (偏画面一侧, 收尾亮部引导视线)
const CONV: Pt = {x: 1850, y: trunkY(1850)};

// ---------- component ----------
export const DatavizLandscapeOpen: React.FC = () => {
  const frame = useCurrentFrame();

  // 相机: 匀稳横移 3.2px/f (2–5 区间), 全程斜率恒定 (不急刹)
  const camX = frame * 3.2;
  // 极缓 zoom 1.0 → 1.06
  const zoom = interpolate(frame, [0, DUR - 1], [1, 1.06]);

  // 视差: 近 1.4× / 中 1× / 远 0.6×
  const farX = -camX * 0.6;
  const midX = -camX * 1.0;
  const nearX = -camX * 1.4;

  // 主干先行: f0–38 out-cubic
  const trunkGrow = growth(frame, 0, 38);

  // 流动感 (卡"流动感"行): draw-on 完成后, 虚线相位低速漂向汇点
  // 速度 1.5px/f (卡 1–2), 叠加透明度 ≤0.3; 生长完成后才淡入
  const flowOffset = -frame * 1.5; // dashoffset 递减 = 相位沿画线方向(向汇点)漂移
  const flowDash = '14 56'; // 世界像素单位
  const flowIn = (gEnd: number) =>
    interpolate(frame, [gEnd, gEnd + 20], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  // 收尾亮部 (交棒段 f120+ 缓升, 引导视线向汇点/右侧)
  const handoffGlow = interpolate(frame, [118, 160], [0, 0.4], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const layerStyle = (tx: number): React.CSSProperties => ({
    position: 'absolute',
    left: 0,
    top: 0,
    width: WORLD_W,
    height: H,
    transform: `translateX(${tx}px)`,
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#050505', overflow: 'hidden'}}>
      {/* zoom 容器: 以画面中心为原点 */}
      <AbsoluteFill style={{transform: `scale(${zoom})`, transformOrigin: '50% 50%'}}>
        {/* 底色微渐变, 避免纯黑死平 */}
        <AbsoluteFill
          style={{
            background:
              'radial-gradient(120% 90% at 62% 45%, #0b0b0d 0%, #060607 55%, #040404 100%)',
          }}
        />

        {/* ---- 远景层 (视差 0.6×) ---- */}
        <div style={layerStyle(farX)}>
          <svg width={WORLD_W} height={H} style={{position: 'absolute'}}>
            {FAR_LINES.map((l, i) => {
              const g = growth(frame, l.growStart, l.growDur);
              return (
                <g key={i}>
                  <path
                    d={farPath(l)}
                    fill="none"
                    stroke="#ffffff"
                    strokeWidth={1.3}
                    strokeLinecap="round"
                    opacity={l.op}
                    pathLength={1}
                    strokeDasharray={1}
                    strokeDashoffset={1 - g}
                  />
                  {/* 节点标记: 可见特征点穿过画面, 让 0.6× 层位移可辨 */}
                  {FAR_NODE_TS.map((t, j) => {
                    const p = cubicAt(l.p0, l.p1, l.p2, l.p3, t);
                    return (
                      <circle
                        key={j}
                        cx={p.x}
                        cy={p.y}
                        r={3}
                        fill="#ffffff"
                        opacity={t <= g ? l.op + 0.08 : 0}
                      />
                    );
                  })}
                </g>
              );
            })}
          </svg>
        </div>

        {/* ---- 中景层 (主角层, 视差 1×) ---- */}
        <div style={layerStyle(midX)}>
          <svg width={WORLD_W} height={H} style={{position: 'absolute'}}>
            {/* 微辉光垫层: 1–2px soft glow 压出"发光线"(卡坑注, Q4 单点许可内) */}
            <g style={{filter: 'blur(3px)'}}>
              <path
                d={trunkPath()}
                fill="none"
                stroke="#ffffff"
                strokeWidth={7}
                strokeLinecap="round"
                opacity={0.16}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - trunkGrow}
              />
              {MID_TRIBS.map((t, i) => (
                <path
                  key={i}
                  d={tribPath(t)}
                  fill="none"
                  stroke="#ffffff"
                  strokeWidth={5.5}
                  strokeLinecap="round"
                  opacity={t.opacity * 0.18}
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - growth(frame, t.growStart, t.growDur)}
                />
              ))}
            </g>
            {/* 主干 (唯一) */}
            <path
              d={trunkPath()}
              fill="none"
              stroke="#ffffff"
              strokeWidth={2.8}
              strokeLinecap="round"
              opacity={0.8}
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - trunkGrow}
            />
            {/* 支流, 错峰生长 */}
            {MID_TRIBS.map((t, i) => (
              <path
                key={i}
                d={tribPath(t)}
                fill="none"
                stroke="#ffffff"
                strokeWidth={2.2}
                strokeLinecap="round"
                opacity={t.opacity}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - growth(frame, t.growStart, t.growDur)}
              />
            ))}
            {/* 流动感: 虚线相位沿线漂向汇点 (1.5px/f, 叠加透明度 ≤0.3) */}
            <path
              d={trunkPath()}
              fill="none"
              stroke="#ffffff"
              strokeWidth={2.8}
              strokeLinecap="round"
              opacity={0.3 * flowIn(38)}
              strokeDasharray={flowDash}
              strokeDashoffset={flowOffset}
            />
            {MID_TRIBS.map((t, i) => (
              <path
                key={`flow-${i}`}
                d={tribPath(t)}
                fill="none"
                stroke="#ffffff"
                strokeWidth={2.2}
                strokeLinecap="round"
                opacity={0.26 * flowIn(t.growStart + t.growDur)}
                strokeDasharray={flowDash}
                strokeDashoffset={flowOffset}
              />
            ))}
          </svg>

          {/* 标签: 方块图钉 + 等宽字虚构 ID, 错峰淡入 + 沿线微漂 */}
          {LABELS.map((l) => {
            const trib = MID_TRIBS[l.trib];
            const base = cubicAt(trib.p0, trib.p1, trib.p2, trib.p3, l.t);
            const fadeIn = interpolate(frame, [l.appear, l.appear + 12], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            // 沿线微漂: 出现后沿切线方向缓移 ~6px
            const drift = interpolate(frame, [l.appear, DUR - 1], [0, 6], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            const ahead = cubicAt(trib.p0, trib.p1, trib.p2, trib.p3, Math.min(1, l.t + 0.02));
            const dx = ahead.x - base.x;
            const dy = ahead.y - base.y;
            const dl = Math.hypot(dx, dy) || 1;
            const px = base.x + (dx / dl) * drift;
            const py = base.y + (dy / dl) * drift;
            // 图钉锚在线上 (中心 = 线上取样点, 卡坑注: 钉线分离读作浮尘);
            // 文字沿垂直方向偏移, 避开线体
            const textOff = l.above ? -38 : 20;
            return (
              <React.Fragment key={l.id}>
                <div
                  style={{
                    position: 'absolute',
                    left: px - 8,
                    top: py - 8,
                    width: 16,
                    height: 16,
                    backgroundColor: '#ffffff',
                    opacity: fadeIn * 0.9,
                  }}
                />
                <span
                  style={{
                    position: 'absolute',
                    left: px + 14,
                    top: py + textOff,
                    fontFamily: 'Menlo, "SF Mono", Consolas, monospace',
                    fontSize: 22,
                    letterSpacing: 3,
                    color: '#e8e8e8',
                    whiteSpace: 'nowrap',
                    opacity: fadeIn * 0.92,
                  }}
                >
                  {l.id}
                </span>
              </React.Fragment>
            );
          })}

          {/* 交棒亮部: 汇点方向留亮, 引导视线接下一镜头 */}
          <div
            style={{
              position: 'absolute',
              left: CONV.x - 420,
              top: CONV.y - 260,
              width: 840,
              height: 520,
              background:
                'radial-gradient(50% 50% at 50% 50%, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0.12) 45%, rgba(255,255,255,0) 72%)',
              opacity: handoffGlow,
              filter: 'blur(18px)',
              pointerEvents: 'none',
            }}
          />
        </div>

        {/* ---- 近景层 (大虚焦, 视差 1.4×) ---- */}
        <div style={{...layerStyle(nearX), filter: 'blur(13px)'}}>
          <svg width={WORLD_W} height={H} style={{position: 'absolute'}}>
            {NEAR_LINES.map((l, i) => (
              <path
                key={i}
                d={l.d}
                fill="none"
                stroke="#ffffff"
                strokeWidth={l.w}
                strokeLinecap="round"
                opacity={l.op}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - growth(frame, l.growStart, l.growDur)}
              />
            ))}
          </svg>
        </div>

        {/* 轻 vignette 收住四角 */}
        <AbsoluteFill
          style={{
            background:
              'radial-gradient(115% 95% at 50% 50%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.5) 100%)',
            pointerEvents: 'none',
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

