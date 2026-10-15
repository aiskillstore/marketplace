// ---
// name: omniailab-motion-demo-theme-sweep-toggle
// description: theme-sweep-toggle —— 深浅模式扫场
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// theme-sweep-toggle —— 深浅模式扫场
// 同一 dashboard 深浅两版叠放（深版手工映射 G 色板），上层深版用 clip-path
// polygon 15° 斜边从左上扫到右下（先快后缓），边界带 2px 亮线；
// 扫完深版整体 scale 0.995→1 "坐实"。f=70 后全静止（70f）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';

const CL = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// 浅色板 = Fixtures G；深色板手工反转映射
type Pal = {
  bg: string; panel: string; line: string; bar: string;
  mid: string; card: string; border: string; side: string; sideBar: string;
};
const LIGHT: Pal = {
  bg: '#ececea', panel: '#f7f7f6', line: '#dcdcda', bar: '#c2c2c0',
  mid: '#8f8f8d', card: '#ffffff', border: '#d8d8d6', side: '#3a3a3a', sideBar: '#5a5a58',
};
const DARK: Pal = {
  bg: '#1c1c1b', panel: '#242423', line: '#3a3a38', bar: '#6e6e6c',
  mid: '#8f8f8d', card: '#2c2c2b', border: '#454543', side: '#0f0f0e', sideBar: '#6a6a68',
};

// 带色板参数的 dashboard（结构同 Fixtures.FakeDashboard variant A）
const Dash: React.FC<{ p: Pal }> = ({ p }) => (
  <div style={{ width: 1920, height: 1080, background: p.bg, display: 'flex' }}>
    <div style={{ width: 220, background: p.side, padding: '28px 22px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ width: 40, height: 40, borderRadius: 10, background: p.sideBar }} />
      {Array.from({ length: 7 }).map((_, i) => (
        <div key={i} style={{ height: 12, width: `${60 + ((i * 29) % 35)}%`, background: p.sideBar, borderRadius: 6 }} />
      ))}
    </div>
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div style={{ height: 72, background: p.panel, borderBottom: `2px solid ${p.line}`, display: 'flex', alignItems: 'center', padding: '0 32px', gap: 20, boxSizing: 'border-box' }}>
        <div style={{ height: 18, width: 180, background: p.bar, borderRadius: 9 }} />
        <div style={{ marginLeft: 'auto', height: 36, width: 320, background: p.card, border: `2px solid ${p.line}`, borderRadius: 18, boxSizing: 'border-box' }} />
        <div style={{ width: 36, height: 36, borderRadius: 18, background: p.mid }} />
      </div>
      <div style={{ flex: 1, padding: 36, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gridAutoRows: '1fr', gap: 28, boxSizing: 'border-box' }}>
        {Array.from({ length: 6 }).map((_, i) => {
          const titleW = 45 + (((i + 1) * 37) % 40);
          const lines = 2 + ((i + 1) % 3);
          return (
            <div key={i} style={{ background: p.card, border: `2px solid ${p.border}`, borderRadius: 14, padding: 18, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ height: 16, width: `${titleW}%`, background: p.bar, borderRadius: 8 }} />
              {Array.from({ length: lines }).map((_, j) => (
                <div key={j} style={{ height: 10, width: `${88 - j * 14 - ((i + 1) % 5) * 3}%`, background: p.line, borderRadius: 5 }} />
              ))}
              <div style={{ marginTop: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
                <div style={{ width: 26, height: 26, borderRadius: 13, background: p.mid }} />
                <div style={{ height: 10, width: 64, background: p.line, borderRadius: 5 }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  </div>
);

// 时间轴
const SWEEP0 = 14; // 扫场开始（前 14f 初始静置）
const SWEEP1 = 52; // 扫场结束
const SETTLE0 = 52;
const SETTLE1 = 64; // 坐实结束 → 之后全静止

const SLANT = 1080 * Math.tan((15 * Math.PI) / 180); // ≈ 289px，15° 斜边

export const ThemeSweepToggle: React.FC = () => {
  const frame = useCurrentFrame();

  // 边界顶端 x：先快后缓（poly(3) out）；从左外扫到右外+SLANT 保证底边也扫尽
  const p = interpolate(frame, [SWEEP0, SWEEP1], [-20, 1920 + SLANT + 40], {
    easing: Easing.out(Easing.poly(3)),
    ...CL,
  });

  // 坐实：0.995 → 1
  const settle = interpolate(frame, [SETTLE0, SETTLE0 + 1, SETTLE1], [1, 0.995, 1], {
    easing: Easing.out(Easing.cubic),
    ...CL,
  });

  // 亮线透明度：扫场期间可见，扫完 6f 内淡出
  const lineOp = interpolate(frame, [SWEEP0, SWEEP0 + 4, SWEEP1 - 4, SWEEP1 + 2], [0, 1, 1, 0], CL);
  const sweeping = frame >= SWEEP0 && frame < SWEEP1 + 2;

  return (
    <div style={{ width: 1920, height: 1080, position: 'relative', overflow: 'hidden', background: LIGHT.bg }}>
      {/* 底层浅色版 */}
      <Dash p={LIGHT} />
      {/* 上层深色版，clip-path 斜切揭出 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          clipPath: `polygon(0 0, ${p}px 0, ${p - SLANT}px 1080px, 0 1080px)`,
          transform: `scale(${settle})`,
          transformOrigin: '50% 50%',
        }}
      >
        <Dash p={DARK} />
      </div>
      {/* 2px 亮线边界（条件卸载） */}
      {sweeping && (
        <div
          style={{
            position: 'absolute',
            left: p - SLANT / 2 - 2,
            top: 540 - 620,
            width: 4,
            height: 1240,
            background: '#ffffff',
            boxShadow: '0 0 18px 4px rgba(255,255,255,0.75)',
            transform: 'rotate(15deg)',
            transformOrigin: '50% 50%',
            opacity: lineOp,
          }}
        />
      )}
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

