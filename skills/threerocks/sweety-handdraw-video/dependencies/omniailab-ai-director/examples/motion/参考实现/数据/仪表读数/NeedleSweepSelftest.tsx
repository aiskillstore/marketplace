// ---
// name: omniailab-motion-demo-needle-sweep-selftest
// description: needle-sweep-selftest —— 满弧扫针自检
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// needle-sweep-selftest —— 满弧扫针自检
// 卡片内三个并排 270° 表盘。f12 "点火"后指针错峰 4f 依次从 0 甩满全弧
// （去程 12f ease-out），再回落到各自真实值（回程 20f：先落过头 8° 再回摆），
// 落定同帧盘下数值文字弹出。三表错峰形成波浪。f60 后真静止 80f。
// 帧确定性：纯 interpolate 分段，全部 clamp，settle 后每帧输出常数。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, TitleBlock } from '../../_fixtures/Fixtures';

const AMBER = '#b45309';
const RED = '#7c2d12';

const CARD_W = 1500;
const CARD_H = 640;
const CARD_X = (1920 - CARD_W) / 2;
const CARD_Y = 300;

const GA_W = CARD_W / 3; // 每表盘占位宽
const R = 148;
const CX = GA_W / 2;
const CY = 240;

// 表盘角 d∈[0,270] → SVG 角 a = 135 + d（0=右，顺时针，y 向下）
const polar = (a: number, r: number): [number, number] => [
  CX + r * Math.cos((a * Math.PI) / 180),
  CY + r * Math.sin((a * Math.PI) / 180),
];

const arcPath = (d0: number, d1: number, r: number): string => {
  const [x0, y0] = polar(135 + d0, r);
  const [x1, y1] = polar(135 + d1, r);
  const large = d1 - d0 > 180 ? 1 : 0;
  return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
};

// 三表：点火 f12，错峰 4f
const GAUGES = [
  { start: 12, target: 190 },
  { start: 16, target: 120 },
  { start: 20, target: 235 },
];

const needleAngle = (frame: number, s: number, target: number): number => {
  if (frame <= s) return 0;
  if (frame <= s + 12) {
    // 去程：甩满全弧，ease-out（起步猛）
    return interpolate(frame, [s, s + 12], [0, 270], {
      easing: Easing.out(Easing.cubic),
    });
  }
  if (frame <= s + 25) {
    // 回程主段：落过真实值 8°
    return interpolate(frame, [s + 12, s + 25], [270, target - 8], {
      easing: Easing.inOut(Easing.cubic),
    });
  }
  // 回摆：从过冲位弹回真实值，之后 clamp 为常数
  return interpolate(frame, [s + 25, s + 32], [target - 8, target], {
    easing: Easing.out(Easing.cubic),
    extrapolateRight: 'clamp',
  });
};

const Gauge: React.FC<{ start: number; target: number }> = ({ start, target }) => {
  const frame = useCurrentFrame();
  const d = needleAngle(frame, start, target);
  const settle = start + 32;
  const value = Math.round((target / 270) * 100);

  const popScale = interpolate(frame, [settle, settle + 4, settle + 8], [0.3, 1.18, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const popOp = interpolate(frame, [settle, settle + 3], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const [tipX, tipY] = polar(135, R - 26);
  const [tailX, tailY] = polar(315, 36);

  // 大刻度 11 根（每 27°），小刻度每 9°
  const ticks: React.ReactNode[] = [];
  for (let k = 0; k <= 30; k++) {
    const dd = k * 9;
    const major = k % 3 === 0;
    const a = 135 + dd;
    const [x0, y0] = polar(a, R - 8);
    const [x1, y1] = polar(a, major ? R - 30 : R - 19);
    ticks.push(
      <line key={k} x1={x0} y1={y0} x2={x1} y2={y1}
        stroke={dd >= 225 ? RED : G.mid} strokeWidth={major ? 4 : 2} />
    );
  }

  return (
    <div style={{ width: GA_W, height: 480, position: 'relative' }}>
      <svg width={GA_W} height={430}>
        {/* 弧形轨道 + 红区 */}
        <path d={arcPath(0, 270, R)} fill="none" stroke={G.line} strokeWidth={10} strokeLinecap="round" />
        <path d={arcPath(225, 270, R)} fill="none" stroke={RED} strokeWidth={10} strokeLinecap="round" opacity={0.85} />
        {ticks}
        {/* 指针：琥珀刚体，rotate 全量程往返 */}
        <g transform={`rotate(${d.toFixed(3)} ${CX} ${CY})`}>
          <line x1={tailX} y1={tailY} x2={tipX} y2={tipY} stroke={AMBER} strokeWidth={9} strokeLinecap="round" />
        </g>
        <circle cx={CX} cy={CY} r={15} fill={G.ink} />
        <circle cx={CX} cy={CY} r={6} fill={AMBER} />
      </svg>
      {/* 落定同帧弹出的数值 */}
      <div style={{
        position: 'absolute', left: 0, right: 0, top: 396, textAlign: 'center',
        opacity: popOp, transform: `scale(${popScale.toFixed(4)})`,
      }}>
        <span style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 62, color: G.ink }}>
          {value}
        </span>
        <span style={{ fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 700, fontSize: 30, color: G.mid, marginLeft: 8 }}>
          %
        </span>
      </div>
    </div>
  );
};

export const NeedleSweepSelftest: React.FC = () => {
  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: 110, width: '100%', textAlign: 'center' }}>
        <TitleBlock text="NEEDLE SWEEP SELF-TEST" size={72} />
      </div>
      <div style={{
        position: 'absolute', left: CARD_X, top: CARD_Y, width: CARD_W, height: CARD_H,
        background: G.card, border: `2px solid ${G.border}`, borderRadius: 14,
        boxSizing: 'border-box', boxShadow: '0 2px 8px rgba(0,0,0,0.06)', padding: 32,
      }}>
        <div style={{ height: 16, width: 320, background: G.bar, borderRadius: 8 }} />
        <div style={{ position: 'absolute', left: 0, top: 96, display: 'flex' }}>
          {GAUGES.map((g, i) => (
            <Gauge key={i} start={g.start} target={g.target} />
          ))}
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

