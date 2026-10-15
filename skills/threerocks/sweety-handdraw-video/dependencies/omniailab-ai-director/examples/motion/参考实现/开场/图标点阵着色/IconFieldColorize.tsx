// ---
// name: omniailab-motion-demo-icon-field-colorize
// description: 图标点阵着色 —— 灰阶图标原野错峰浮现（错峰淡入+微弹），停一拍后
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 图标点阵着色 —— 灰阶图标原野错峰浮现（错峰淡入+微弹），停一拍后
// 蓝色整场极快扫翻，随后橙/绿/红三道色波依次向下扫过，终态四色横带。
// 对标 bear-app.mp4 0–3s（密帧核实：非同帧硬翻，是极快多道波纹翻色）。
import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

// 16 个简笔图标（viewBox 0 0 24 24，纯填充），求可辨认不求精致
const SHAPES: ((c: string) => React.ReactNode)[] = [
  (c) => <path fill={c} d="M12 21s-7.5-4.7-9.6-9C.9 8.7 2.7 5 6.2 5c2 0 3.3 1 4 2.1h3.6C14.5 6 15.8 5 17.8 5c3.5 0 5.3 3.7 3.8 7-2.1 4.3-9.6 9-9.6 9z" transform="scale(0.92) translate(1,0)" />,
  (c) => <path fill={c} d="M12 2l2.7 6.3 6.8.5-5.2 4.4 1.6 6.6L12 16.2 6.1 19.8l1.6-6.6L2.5 8.8l6.8-.5z" />,
  (c) => <path fill={c} d="M13 2L4 14h6l-1 8 9-12h-6z" />,
  (c) => <circle fill={c} cx="12" cy="12" r="9" />,
  (c) => <path fill={c} d="M9 3v12.3A3.5 3.5 0 1 0 11 18V7h7v6.3A3.5 3.5 0 1 0 20 16V3z" transform="scale(0.85) translate(1.5,1.5)" />,
  (c) => <path fill={c} d="M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4V6a2 2 0 0 1 2-2z" transform="scale(0.85) translate(2,2)" />,
  (c) => <><rect fill={c} x="3" y="6" width="18" height="13" rx="2.5" /><circle fill="#fff" cx="12" cy="12.5" r="3.6" /><rect fill={c} x="8" y="3.5" width="8" height="4" rx="1.5" /></>,
  (c) => <path fill={c} d="M6.5 19a4.5 4.5 0 0 1-.4-9A6 6 0 0 1 17.8 8.7 4.2 4.2 0 0 1 17.5 19z" />,
  (c) => <path fill={c} d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z" transform="scale(0.9) translate(1.2,0.5)" />,
  (c) => <path fill={c} d="M3.5 10L12 3l8.5 7V21h-6v-6h-5v6h-6z" />,
  (c) => <><rect fill={c} x="3" y="8" width="18" height="4" rx="1" /><rect fill={c} x="5" y="12" width="14" height="9" rx="1" /><rect fill="#fff" x="10.9" y="8" width="2.2" height="13" /></>,
  (c) => <path fill={c} d="M9.4 20.6l-1 1.9 7.2-.1 4.9-8.5-2.2.1-2 3.4L13 4.5h-2.1L7.6 17.3z" transform="scale(0.9) translate(1,1)" />,
  (c) => <path fill={c} d="M20.3 6.7L9.6 17.4l-5.9-5.9 2.1-2.1 3.8 3.8 8.6-8.6z" />,
  (c) => <path fill={c} d="M21.5 15.5L14 12V5.5a2 2 0 1 0-4 0V12l-7.5 3.5v2l7.5-2v4l-2.5 2v1.5l4.5-1 4.5 1V21.5l-2.5-2v-4l7.5 2z" transform="scale(0.85) translate(1.8,1.8)" />,
  (c) => <><circle fill={c} cx="12" cy="12" r="4" /><path fill={c} d="M12 1.5l1.4 3.6h-2.8zM12 22.5l-1.4-3.6h2.8zM1.5 12l3.6-1.4v2.8zM22.5 12l-3.6 1.4v-2.8zM4.6 4.6l3.5 1.5-2 2zM19.4 19.4l-3.5-1.5 2-2zM19.4 4.6l-1.5 3.5-2-2zM4.6 19.4l1.5-3.5 2 2z" /></>,
  (c) => <path fill={c} d="M20 4C10 4 4.5 9 4 15.7 3.9 17.5 4 20 4 20s2.7-.2 4.4-.3C15 19.2 20 13.5 20 4zM6.8 17.2C10 11 15 8 15 8s-5.5 1.5-8.8 8z" />,
];

const COLS = 17, ROWS = 10, CELL = 110, ICON = 44;
const GRAYS = ['#9a9a9a', '#7c7c7c', '#b0b0b0', '#8b8b8b'];
// 四道色波：蓝覆盖全场，橙/绿/红依次覆盖更低的行带 → 终态四色横带
const WAVES = [
  { color: '#5b67e8', fromRow: 0, start: 78 },
  { color: '#e7a03c', fromRow: 3, start: 90 },
  { color: '#34a56f', fromRow: 6, start: 100 },
  { color: '#e2606b', fromRow: 9, start: 110 },
];

export const IconFieldColorize: React.FC = () => {
  const frame = useCurrentFrame();
  const rand = mulberry32(20260718);
  const icons: React.ReactNode[] = [];

  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const r1 = rand(), r2 = rand(), r3 = rand();
      // —— 错峰浮现：分 10 批，批内再抖动
      const batch = Math.floor(r1 * 10);
      const t0 = 4 + batch * 4 + r2 * 3;
      const ap = interpolate(frame, [t0, t0 + 8], [0, 1], {
        extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      });
      if (ap <= 0) continue;
      // 微弹：0.55 → 1.07 → 1
      const easeOut = 1 - Math.pow(1 - ap, 3);
      const appearScale = ap < 1 ? 0.55 + easeOut * 0.52 - Math.max(0, ap - 0.72) * 0.25 : 1;

      // —— 色波：每道波从起始行向下快扫（行 1.4 帧 + 列微倾 + 抖动）
      const gray = GRAYS[Math.floor(r2 * GRAYS.length)];
      let color = gray;
      let flipPhase = 0; // 最近一次翻色的进行度，用于 pop
      for (const w of WAVES) {
        if (r < w.fromRow) continue;
        const arrive = w.start + (r - w.fromRow) * 1.4 + c * 0.25 + r3 * 1.5;
        const p = interpolate(frame, [arrive, arrive + 3], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        });
        if (p > 0) { color = w.color; flipPhase = p; }
      }
      const flipPop = flipPhase > 0 && flipPhase < 1
        ? 1 + Math.sin(flipPhase * Math.PI) * 0.22 : 1;

      const shape = SHAPES[Math.floor(r3 * SHAPES.length) % SHAPES.length];
      const x = 48 + c * CELL + (r % 2) * 26;
      const y = 26 + r * CELL;
      icons.push(
        <div key={`${r}-${c}`} style={{
          position: 'absolute', left: x, top: y, width: ICON, height: ICON,
          opacity: ap, transform: `scale(${appearScale * flipPop})`,
        }}>
          <svg viewBox="0 0 24 24" width={ICON} height={ICON}>{shape(color)}</svg>
        </div>,
      );
    }
  }

  return <AbsoluteFill style={{ background: '#ffffff' }}>{icons}</AbsoluteFill>;
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

