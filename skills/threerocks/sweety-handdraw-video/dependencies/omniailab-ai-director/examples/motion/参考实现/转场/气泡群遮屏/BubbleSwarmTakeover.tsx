// ---
// name: omniailab-motion-demo-bubble-swarm-takeover
// description: 气泡群遮屏 —— loom-ai 9–12s
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 气泡群遮屏 —— loom-ai 9–12s
// 无剪切转场：珠光气泡群从画外飘入、越来越大遮满整屏，页面同时被"洗白"，
// 遮蔽峰值处藏场景切换，气泡散开后已是新场景。混入 i18n 文字胶囊变体元素。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard } from '../../_fixtures/Fixtures';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const PEAK = 75; // 遮蔽峰值帧（藏切点）
const W = 1920;
const H = 1080;
const CX = W / 2;
const CY = H / 2;

// 珠光色相微差（粉/紫/蓝/青）
const TINTS = [
  ['rgba(226,208,255,0.55)', 'rgba(255,200,235,0.45)'],
  ['rgba(190,225,255,0.55)', 'rgba(215,200,255,0.45)'],
  ['rgba(255,215,235,0.5)', 'rgba(200,235,255,0.45)'],
  ['rgba(205,240,250,0.5)', 'rgba(235,210,255,0.45)'],
];

type BubbleSpec = {
  startX: number; startY: number; targetX: number; targetY: number;
  r: number; t0: number; blur: number; tint: number;
  wobblePhase: number; wobbleAmp: number; z: number;
};

const makeBubbles = (): BubbleSpec[] => {
  const specs: BubbleSpec[] = [];
  // 34 颗常规气泡（三层景深）
  for (let i = 0; i < 34; i++) {
    const rng = mulberry32(1000 + i * 97);
    const edge = Math.floor(rng() * 4);
    const along = rng();
    let startX = 0, startY = 0;
    if (edge === 0) { startX = along * W; startY = -320; }
    if (edge === 1) { startX = W + 320; startY = along * H; }
    if (edge === 2) { startX = along * W; startY = H + 320; }
    if (edge === 3) { startX = -320; startY = along * H; }
    const layer = i % 3; // 0 远 1 中 2 近
    const r = layer === 0 ? 45 + rng() * 55 : layer === 1 ? 100 + rng() * 90 : 210 + rng() * 150;
    specs.push({
      startX, startY,
      targetX: 140 + rng() * (W - 280),
      targetY: 100 + rng() * (H - 200),
      r,
      t0: 8 + rng() * 42,
      blur: layer === 0 ? 7 : layer === 1 ? 0.5 : 9,
      tint: Math.floor(rng() * TINTS.length),
      wobblePhase: rng() * Math.PI * 2,
      wobbleAmp: 10 + rng() * 22,
      z: layer,
    });
  }
  // 6 颗巨型气泡，峰值时铺满屏（网格落点保证覆盖）
  const grid = [
    [340, 300], [960, 240], [1580, 330],
    [320, 800], [980, 860], [1600, 780],
  ];
  grid.forEach(([gx, gy], i) => {
    const rng = mulberry32(7000 + i * 131);
    const edge = i % 4;
    let startX = 0, startY = 0;
    if (edge === 0) { startX = gx; startY = -600; }
    if (edge === 1) { startX = W + 600; startY = gy; }
    if (edge === 2) { startX = gx; startY = H + 600; }
    if (edge === 3) { startX = -600; startY = gy; }
    specs.push({
      startX, startY, targetX: gx, targetY: gy,
      r: 430 + rng() * 140,
      t0: 22 + rng() * 14,
      blur: 3, tint: i % TINTS.length,
      wobblePhase: rng() * Math.PI * 2, wobbleAmp: 8,
      z: 2,
    });
  });
  return specs;
};

const BUBBLES = makeBubbles();

const CAPSULES = [
  { text: 'Hallo!', idx: 5 },
  { text: '¡Hola!', idx: 14 },
  { text: 'Ciao!', idx: 23 },
];

const Bubble: React.FC<{ spec: BubbleSpec; frame: number }> = ({ spec, frame }) => {
  const pIn = interpolate(frame, [spec.t0, PEAK], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  // 峰值后向外散开（加速离场）
  const disperse = interpolate(frame, [PEAK + 2, 118], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.in(Easing.quad),
  });
  const wob = Math.sin(frame * 0.09 + spec.wobblePhase) * spec.wobbleAmp * pIn;
  let x = spec.startX + (spec.targetX - spec.startX) * pIn + wob;
  let y = spec.startY + (spec.targetY - spec.startY) * pIn + wob * 0.6;
  const dx = spec.targetX - CX, dy = spec.targetY - CY;
  const dl = Math.max(Math.hypot(dx, dy), 60);
  x += (dx / dl) * disperse * 1700;
  y += (dy / dl) * disperse * 1700;
  const scale = interpolate(frame, [spec.t0, PEAK], [0.22, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  }) * (1 - disperse * 0.35);
  const opacity =
    interpolate(frame, [spec.t0, spec.t0 + 7], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) *
    interpolate(disperse, [0.55, 1], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  if (opacity <= 0.01) return null;
  const [c1, c2] = TINTS[spec.tint];
  const d = spec.r * 2 * scale;
  return (
    <div style={{
      position: 'absolute', left: x - spec.r * scale, top: y - spec.r * scale,
      width: d, height: d, borderRadius: '50%', opacity,
      filter: `blur(${spec.blur}px)`,
      background: `radial-gradient(circle at 34% 28%, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.45) 22%, ${c1} 52%, ${c2} 76%, rgba(255,255,255,0.65) 96%)`,
      boxShadow: 'inset 0 0 40px rgba(255,255,255,0.55), 0 0 30px rgba(255,255,255,0.25)',
    }} />
  );
};

export const BubbleSwarmTakeover: React.FC = () => {
  const frame = useCurrentFrame();
  // 页面"洗白"：靠近峰值时整体亮度提升
  const whiteout = interpolate(frame, [42, 68, 82, 104], [0, 0.92, 0.92, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });
  const breathe = 1 + 0.02 * Math.sin(frame * 0.045);
  return (
    <AbsoluteFill style={{ background: '#ececea', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${breathe})` }}>
        {frame < PEAK ? <FakeDashboard variant="A" /> : <FakeDashboard variant="B" />}
      </AbsoluteFill>
      {/* 洗白层压在页面之上、气泡之下 */}
      <AbsoluteFill style={{ background: '#ffffff', opacity: whiteout }} />
      {/* 远/中层气泡 */}
      {BUBBLES.filter((b) => b.z < 2).map((b, i) => (
        <Bubble key={i} spec={b} frame={frame} />
      ))}
      {/* i18n 文字胶囊混在中层气泡里漂 */}
      {CAPSULES.map((c, i) => {
        const host = BUBBLES[c.idx];
        const pIn = interpolate(frame, [host.t0 + 4, PEAK], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
        });
        const disperse = interpolate(frame, [PEAK + 2, 116], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad),
        });
        const wob = Math.sin(frame * 0.08 + host.wobblePhase + 1.3) * 18;
        let x = host.startX + (host.targetX - host.startX) * pIn + 60 + wob;
        let y = host.startY + (host.targetY - host.startY) * pIn - host.r * 0.9;
        const dx = host.targetX - CX, dy = host.targetY - CY;
        const dl = Math.max(Math.hypot(dx, dy), 60);
        x += (dx / dl) * disperse * 1700;
        y += (dy / dl) * disperse * 1700;
        const op = pIn * interpolate(disperse, [0.5, 1], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const sc = 0.5 + 0.5 * pIn;
        return (
          <div key={i} style={{
            position: 'absolute', left: x, top: y, opacity: op,
            transform: `scale(${sc}) rotate(${wob * 0.25}deg)`,
            padding: '18px 40px', borderRadius: 60,
            background: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(235,220,255,0.9))',
            border: '2px solid rgba(255,255,255,0.9)',
            boxShadow: '0 8px 32px rgba(150,120,220,0.25)',
            fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800,
            fontSize: 46, color: '#5b4a86', whiteSpace: 'nowrap',
          }}>{c.text}</div>
        );
      })}
      {/* 前景大气泡（焦外） */}
      {BUBBLES.filter((b) => b.z === 2).map((b, i) => (
        <Bubble key={i} spec={b} frame={frame} />
      ))}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

