// ---
// name: omniailab-motion-demo-cursor-dialogue-duet
// description: cursor-dialogue-duet —— figma-devmode 0:16–0:20
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// cursor-dialogue-duet —— figma-devmode 0:16–0:20
// 纯暗场上 Designer(蓝)/Developer(绿) 两枚具名光标做"对话式"双人舞：
// 相互靠近 → 绕位交换 → 名牌一亮一暗交接 → 一枚放大成巨箭头当转场。
import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';

const BLUE = '#4C8DF6';
const GREEN = '#2FBF71';
const DARK = '#101012';

const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
const easeInOutCubic = (t: number) =>
  t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const easeInCubic = (t: number) => t * t * t;

const clamp01 = (t: number) => Math.min(1, Math.max(0, t));

// 三次贝塞尔单段位移
const bez = (
  t: number,
  p0: [number, number], c1: [number, number], c2: [number, number], p3: [number, number],
): [number, number] => {
  const u = 1 - t;
  const x = u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p3[0];
  const y = u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p3[1];
  return [x, y];
};

const Cursor: React.FC<{
  x: number; y: number; scale: number; color: string; name: string;
  badgeLit: number; // 0 压暗 1 点亮
  badgeOpacity?: number;
}> = ({ x, y, scale, color, name, badgeLit, badgeOpacity = 1 }) => (
  <div style={{ position: 'absolute', left: x, top: y, transform: `scale(${scale})`, transformOrigin: '0 0' }}>
    <svg width={42} height={62} viewBox="0 0 13.5 20" style={{ display: 'block', overflow: 'visible' }}>
      <path
        d="M0.5 0.5 L0.5 17.2 L4.7 13.4 L7.3 19.5 L10 18.3 L7.4 12.3 L13 12.3 Z"
        fill={color} stroke="#ffffff" strokeWidth={1.1} strokeLinejoin="round"
      />
    </svg>
    <div style={{
      position: 'absolute', left: 34, top: 56, whiteSpace: 'nowrap',
      background: color, color: '#fff', borderRadius: 8, padding: '5px 13px',
      fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 700, fontSize: 16,
      opacity: badgeOpacity * (0.28 + 0.72 * badgeLit),
      filter: `saturate(${0.35 + 0.65 * badgeLit})`,
      boxShadow: badgeLit > 0.6 ? `0 0 ${22 * badgeLit}px ${color}` : 'none',
    }}>
      {name}
    </div>
  </div>
);

export const CursorDialogueDuet: React.FC = () => {
  const f = useCurrentFrame();
  const CX = 960; const CY = 520;
  const R = 270;

  // ---------- Designer(蓝) 轨迹 ----------
  let dx = 0; let dy = 0;
  // 入场：画外左 → 左位（弹性减速）
  {
    const t = easeOutCubic(clamp01(f / 24));
    [dx, dy] = bez(t, [-140, 260], [300, 300], [520, 620], [CX - R, CY]);
  }
  // 靠近：向 Developer 探身（26–56）
  if (f > 26) {
    const t = easeInOutCubic(clamp01((f - 26) / 30));
    const [nx, ny] = bez(t, [CX - R, CY], [CX - R + 120, CY - 150], [CX - 90, CY - 120], [CX - 120, CY - 24]);
    dx = nx; dy = ny;
  }
  // 绕位：从左侧经上方绕到右侧（60–98）
  if (f > 60) {
    const t = easeInOutCubic(clamp01((f - 60) / 38));
    const a = Math.PI + t * Math.PI; // 180° → 360°(上半弧)
    dx = CX + Math.cos(a) * (R - 40) * (1 - t * 0.15) - 0;
    dy = CY + Math.sin(a) * (R - 110);
    if (t < 0.08) { // 与靠近段衔接的小混合
      const m = t / 0.08;
      dx = (CX - 120) * (1 - m) + dx * m;
      dy = (CY - 24) * (1 - m) + dy * m;
    }
  }
  // 退场：加速甩出画面左下（104–128）
  if (f > 104) {
    const t = easeInCubic(clamp01((f - 104) / 24));
    dx = interpolate(t, [0, 1], [dx, -320]);
    dy = interpolate(t, [0, 1], [dy, 1240]);
  }

  // ---------- Developer(绿) 轨迹 ----------
  let gx = 0; let gy = 0;
  {
    const t = easeOutCubic(clamp01((f - 4) / 24));
    [gx, gy] = bez(clamp01(t), [2080, 820], [1700, 760], [1420, 420], [CX + R, CY]);
  }
  // 回应：微微后仰再前倾（30–58）
  if (f > 30) {
    const t = easeInOutCubic(clamp01((f - 30) / 28));
    const sway = Math.sin(t * Math.PI) * 70;
    gx = CX + R + sway * 0.6;
    gy = CY - Math.sin(t * Math.PI * 2) * 40;
  }
  // 绕位：从右侧经下方绕到左侧（60–98）
  if (f > 60) {
    const t = easeInOutCubic(clamp01((f - 60) / 38));
    const a = 0 + t * Math.PI; // 0° → 180°(下半弧)
    gx = CX + Math.cos(a) * (R - 40);
    gy = CY + Math.sin(a) * (R - 110);
  }
  // 终场：冲向中心并放大成巨箭头（100–140）
  const blow = easeInCubic(clamp01((f - 100) / 34));
  if (f > 100) {
    gx = interpolate(blow, [0, 1], [gx, -160]);
    gy = interpolate(blow, [0, 1], [gy, -140]);
  }
  const gScale = 2.8 + blow * 66;

  // ---------- 名牌灯光交接 ----------
  // 前半 Designer 点亮，绕位中段(f≈78)交接给 Developer
  const handoff = easeInOutCubic(clamp01((f - 70) / 14));
  const dLit = f < 24 ? easeOutCubic(clamp01(f / 24)) : 1 - handoff;
  const gLit = handoff;
  const dBadgeIn = easeOutCubic(clamp01((f - 12) / 14));
  const gBadgeIn = easeOutCubic(clamp01((f - 18) / 14));

  // 对话"脉冲"——靠近对话时轻微缩放呼吸
  const dPulse = f > 26 && f < 60 ? 1 + Math.sin((f - 26) * 0.5) * 0.05 : 1;

  return (
    <div style={{ width: 1920, height: 1080, background: DARK, position: 'relative', overflow: 'hidden' }}>
      {/* 暗场微光晕，给纯黑一点空间感 */}
      <div style={{
        position: 'absolute', inset: 0,
        background: `radial-gradient(ellipse 1100px 700px at 50% 48%, rgba(255,255,255,0.045), transparent 70%)`,
      }} />
      {f <= 132 && (
        <Cursor x={dx} y={dy} scale={2.8 * dPulse} color={BLUE} name="Designer"
          badgeLit={dLit} badgeOpacity={dBadgeIn * (f > 104 ? 1 - easeInCubic(clamp01((f - 104) / 18)) : 1)} />
      )}
      <Cursor x={gx} y={gy} scale={gScale} color={GREEN} name="Developer"
        badgeLit={gLit} badgeOpacity={gBadgeIn * (1 - clamp01((f - 102) / 12))} />
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

