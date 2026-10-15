// ---
// name: omniailab-motion-demo-cursor-cast-ensemble
// description: cursor-cast-ensemble —— figma 0:05 (cursor-badge-cast) + miro 全片 cursor-ensemble-ambience
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// cursor-cast-ensemble —— figma 0:05 (cursor-badge-cast) + miro 全片 cursor-ensemble-ambience
// 5 枚具名彩色光标从画外飞入（弹簧减速+名牌淡入），落位后在灰阶画布上持续漂移、
// 指向、聚拢；灰阶便签当环境道具；其中一枚(Rita)在便签上实时打字补全一行文本
// （pitch collaborator-cameo 的打字戏并入）。
import React from 'react';
import { useCurrentFrame, spring, interpolate } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const mulberry32 = (a: number) => () => {
  let t = (a += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const FPS = 30;
const clamp01 = (t: number) => Math.min(1, Math.max(0, t));
const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

type Actor = {
  name: string; color: string;
  from: [number, number]; home: [number, number];
  delay: number; phase: number;
};

const ACTORS: Actor[] = [
  { name: 'Lisa', color: '#4C8DF6', from: [-160, 200], home: [430, 330], delay: 0, phase: 0.0 },
  { name: 'Lucas', color: '#2FBF71', from: [2080, 160], home: [1370, 290], delay: 5, phase: 1.7 },
  { name: 'Marta', color: '#F2994A', from: [-160, 900], home: [560, 760], delay: 9, phase: 3.1 },
  { name: 'Niko', color: '#4C8DF6', from: [2080, 950], home: [1420, 780], delay: 13, phase: 4.4 },
  { name: 'Rita', color: '#2FBF71', from: [900, -180], home: [960, 545], delay: 17, phase: 5.6 },
];

const TYPED = 'Our customers love it';

const CursorActor: React.FC<{ x: number; y: number; a: Actor; badge: number; scale?: number }> = ({
  x, y, a, badge, scale = 2.1,
}) => (
  <div style={{ position: 'absolute', left: x, top: y, transform: `scale(${scale})`, transformOrigin: '0 0', zIndex: 10 }}>
    <svg width={30} height={44} viewBox="0 0 13.5 20" style={{ display: 'block', overflow: 'visible' }}>
      <path d="M0.5 0.5 L0.5 17.2 L4.7 13.4 L7.3 19.5 L10 18.3 L7.4 12.3 L13 12.3 Z"
        fill={a.color} stroke="#ffffff" strokeWidth={1.1} strokeLinejoin="round" />
    </svg>
    <div style={{
      position: 'absolute', left: 24, top: 40, whiteSpace: 'nowrap',
      background: a.color, color: '#fff', borderRadius: 7, padding: '4px 11px',
      fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 700, fontSize: 14,
      opacity: badge, transform: `translateY(${(1 - badge) * 10}px)`,
    }}>
      {a.name}
    </div>
  </div>
);

export const CursorCastEnsemble: React.FC = () => {
  const f = useCurrentFrame();
  const rnd = mulberry32(88);
  // 便签的固定随机旋转
  const noteRots = Array.from({ length: 4 }).map(() => (rnd() - 0.5) * 8);

  // 聚拢时刻：90 帧后所有光标向中央便签聚拢
  const gatherT = easeInOut(clamp01((f - 92) / 26));
  const GATHER: [number, number][] = [
    [770, 430], [1160, 420], [800, 640], [1130, 650], [960, 545],
  ];

  // 打字进度（Rita 落位后开始，60–130 帧）
  const typedCount = Math.floor(interpolate(f, [58, 118], [0, TYPED.length], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  }));
  const caretOn = Math.floor(f / 8) % 2 === 0;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      {/* 点阵无限画布底 */}
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: `radial-gradient(${G.line} 2.4px, transparent 2.4px)`,
        backgroundSize: '46px 46px',
      }} />
      {/* 灰阶便签环境道具 */}
      {[
        { x: 250, y: 170, s: 1 }, { x: 1490, y: 140, s: 2 },
        { x: 210, y: 700, s: 3 }, { x: 1530, y: 690, s: 4 },
      ].map((n, i) => (
        <div key={i} style={{
          position: 'absolute', left: n.x, top: n.y, width: 230, height: 210,
          background: '#e6e6e2', border: `2px solid ${G.border}`, borderRadius: 6,
          boxShadow: '0 4px 14px rgba(0,0,0,0.10)', transform: `rotate(${noteRots[i]}deg)`,
          padding: 18, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 12,
        }}>
          <div style={{ height: 12, width: '70%', background: G.bar, borderRadius: 6 }} />
          <div style={{ height: 10, width: '86%', background: G.line, borderRadius: 5 }} />
          <div style={{ height: 10, width: '58%', background: G.line, borderRadius: 5 }} />
        </div>
      ))}
      {/* 中央大便签：Rita 打字的舞台 */}
      <div style={{
        position: 'absolute', left: 660, top: 420, width: 600, height: 240,
        background: '#ffffff', border: `2px solid ${G.border}`, borderRadius: 12,
        boxShadow: '0 6px 22px rgba(0,0,0,0.12)', padding: 30, boxSizing: 'border-box',
      }}>
        <div style={{ height: 14, width: 180, background: G.bar, borderRadius: 7, marginBottom: 24 }} />
        <div style={{
          fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 700, fontSize: 44,
          color: G.ink, letterSpacing: -0.5, minHeight: 56,
        }}>
          {TYPED.slice(0, typedCount)}
          <span style={{
            display: 'inline-block', width: 4, height: 44, background: '#2FBF71',
            marginLeft: 3, verticalAlign: 'middle',
            opacity: f > 50 && typedCount < TYPED.length ? (caretOn ? 1 : 0.15) : 0,
          }} />
        </div>
      </div>

      {/* 五枚光标 */}
      {ACTORS.map((a, i) => {
        const s = spring({ frame: f - a.delay, fps: FPS, config: { damping: 15, stiffness: 90, mass: 0.9 } });
        let x = interpolate(s, [0, 1], [a.from[0], a.home[0]]);
        let y = interpolate(s, [0, 1], [a.from[1], a.home[1]]);
        // 落位后持续漂移 + 偶尔"指向"性的小冲刺
        const settled = clamp01((f - a.delay - 26) / 10);
        const driftX = Math.sin(f * 0.055 + a.phase) * 46 + Math.sin(f * 0.021 + a.phase * 2) * 30;
        const driftY = Math.cos(f * 0.047 + a.phase * 1.3) * 38 + Math.cos(f * 0.017 + a.phase) * 24;
        x += driftX * settled * (1 - gatherT * 0.55);
        y += driftY * settled * (1 - gatherT * 0.55);
        // 聚拢
        x = interpolate(gatherT, [0, 1], [x, GATHER[i][0] + driftX * 0.25]);
        y = interpolate(gatherT, [0, 1], [y, GATHER[i][1] + driftY * 0.25]);
        const badge = clamp01((f - a.delay - 12) / 12);
        return <CursorActor key={a.name} x={x} y={y} a={a} badge={badge} />;
      })}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

