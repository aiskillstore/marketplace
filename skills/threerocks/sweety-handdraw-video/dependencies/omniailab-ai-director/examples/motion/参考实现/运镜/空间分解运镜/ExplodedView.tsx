// ---
// name: omniailab-motion-demo-exploded-view
// description: 参考实现——参考实现/运镜/空间分解运镜/ExplodedView.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Card, G } from '../../_fixtures/Fixtures';

// exploded-view：整页 dashboard 带 3D 倾斜，咔地沿 Z 轴炸开——顶栏/侧栏/六卡
// 各自浮到不同深度悬停（近大而实、远略暗），层间透出投影；hold 一拍后
// 逆序咔哒合体，2f 震屏收口。
//
// 节拍：0–24 静止建立（已倾斜）→ 24–59 错峰炸开（每层 14f ease-out-back）
//      → 悬停 → 90–123 逆序合体（每层 12f ease-in）→ 123 震屏 → 静止到 150

const EXPLODE = 24; // 炸开起始帧
const ASSEMBLE = 90; // 合体起始帧
const STAGGER = 3; // 层间错峰
const N = 8; // 可动层数（顶栏 + 侧栏 + 6 卡）
const CLOSE = ASSEMBLE + (N - 1) * STAGGER + 12; // = 123，最后一层归位

// FakeDashboard variant A 的布局常量（绝对定位复刻）
const SIDE_W = 220;
const TOP_H = 72;
const PAD = 36;
const GAP = 28;
const CARD_W = (1920 - SIDE_W - PAD * 2 - GAP * 2) / 3; // 524
const CARD_H = (1080 - TOP_H - PAD * 2 - GAP) / 2; // 454

type Layer = {
  key: string;
  x: number;
  y: number;
  w: number;
  h: number;
  z: number; // 炸开深度 60–320
  order: number; // 错峰序
  radius: number;
  node: React.ReactNode;
};

const Sidebar: React.FC = () => (
  <div style={{ width: SIDE_W, height: 1080, background: G.side, padding: '28px 22px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 18 }}>
    <div style={{ width: 40, height: 40, borderRadius: 10, background: '#777775' }} />
    {Array.from({ length: 7 }).map((_, i) => (
      <div key={i} style={{ height: 12, width: `${60 + ((i * 29) % 35)}%`, background: G.sideBar, borderRadius: 6 }} />
    ))}
  </div>
);

const Topbar: React.FC = () => (
  <div style={{ width: 1920 - SIDE_W, height: TOP_H, background: G.panel, borderBottom: `2px solid ${G.line}`, display: 'flex', alignItems: 'center', padding: '0 32px', gap: 20, boxSizing: 'border-box' }}>
    <div style={{ height: 18, width: 180, background: G.bar, borderRadius: 9 }} />
    <div style={{ marginLeft: 'auto', height: 36, width: 320, background: '#fff', border: `2px solid ${G.line}`, borderRadius: 18, boxSizing: 'border-box' }} />
    <div style={{ width: 36, height: 36, borderRadius: 18, background: G.mid }} />
  </div>
);

// 六卡深度：错落分布在 60–320，近的自然更大（perspective 缩放）
const CARD_Z = [150, 300, 80, 230, 320, 110];

const LAYERS: Layer[] = [
  { key: 'top', x: SIDE_W, y: 0, w: 1920 - SIDE_W, h: TOP_H, z: 260, order: 0, radius: 0, node: <Topbar /> },
  { key: 'side', x: 0, y: 0, w: SIDE_W, h: 1080, z: 190, order: 1, radius: 0, node: <Sidebar /> },
  ...Array.from({ length: 6 }).map((_, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    return {
      key: `card${i}`,
      x: SIDE_W + PAD + col * (CARD_W + GAP),
      y: TOP_H + PAD + row * (CARD_H + GAP),
      w: CARD_W,
      h: CARD_H,
      z: CARD_Z[i],
      order: 2 + i,
      radius: 14,
      node: <Card w={CARD_W} h={CARD_H} seed={i + 1} />,
    };
  }),
];

export const ExplodedView: React.FC = () => {
  const frame = useCurrentFrame();

  // 每层进度：炸开 ease-out-back（带一点回弹的“咔”）× 合体逆序 ease-in
  const layerP = (order: number) => {
    const out = interpolate(
      frame,
      [EXPLODE + order * STAGGER, EXPLODE + order * STAGGER + 14],
      [0, 1],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.7)) },
    );
    const back = interpolate(
      frame,
      [ASSEMBLE + (N - 1 - order) * STAGGER, ASSEMBLE + (N - 1 - order) * STAGGER + 12],
      [0, 1],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) },
    );
    return out * (1 - back);
  };

  // 全局散开度（驱动底板变暗）
  const g =
    interpolate(frame, [EXPLODE, EXPLODE + 24], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) }) *
    (1 - interpolate(frame, [ASSEMBLE, CLOSE], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) }));

  // 合体收口：2f 震屏，指数衰减
  const since = frame - CLOSE;
  const env = since >= 0 ? 13 * Math.exp(-since / 1.3) : 0;
  const shakeX = env * Math.sin(since * 3.3);
  const shakeY = env * 0.7 * Math.sin(since * 4.7 + 1.1);

  return (
    <AbsoluteFill style={{ background: '#dedddb', overflow: 'hidden' }}>
      <AbsoluteFill style={{ perspective: 1600, transform: `translate(${shakeX}px, ${shakeY}px)` }}>
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: 1920,
            height: 1080,
            transform: 'scale(0.76) rotateX(18deg) rotateY(-12deg)',
            transformOrigin: '50% 50%',
            transformStyle: 'preserve-3d',
          }}
        >
          {/* 底板：页面背景留在 Z=0，炸开时整体压暗，衬出层间深度 */}
          <div style={{ position: 'absolute', inset: 0, background: G.bg, border: `2px solid ${G.border}`, boxSizing: 'border-box', filter: `brightness(${1 - g * 0.22})` }} />

          {/* 投到底板上的假投影：随层浮起而下移/变虚 */}
          {LAYERS.map((L) => {
            const p = Math.min(1, Math.max(0, layerP(L.order)));
            if (p <= 0.01) return null;
            return (
              <div
                key={`sh-${L.key}`}
                style={{
                  position: 'absolute',
                  left: L.x + L.z * 0.16 * p,
                  top: L.y + L.z * 0.26 * p,
                  width: L.w,
                  height: L.h,
                  borderRadius: L.radius,
                  background: 'rgba(0,0,0,0.30)',
                  filter: `blur(${8 + L.z * 0.09 * p}px)`,
                  opacity: 0.5 * p,
                  transform: 'translateZ(2px)',
                }}
              />
            );
          })}

          {/* 可动层：沿 Z 浮起，近的更大更实、远的略暗 */}
          {LAYERS.map((L) => {
            const p = layerP(L.order);
            const pc = Math.min(1, Math.max(0, p));
            const bright = 1 - (1 - L.z / 320) * 0.28 * pc; // 深度越浅（z 小=离底板近=远离镜头）越暗
            return (
              <div
                key={L.key}
                style={{
                  position: 'absolute',
                  left: L.x,
                  top: L.y,
                  width: L.w,
                  height: L.h,
                  borderRadius: L.radius,
                  transform: `translateZ(${L.z * p}px)`,
                  filter: `brightness(${bright})`,
                  boxShadow: pc > 0.02 ? `0 ${10 + L.z * 0.1 * pc}px ${16 + L.z * 0.14 * pc}px rgba(0,0,0,${0.12 + 0.1 * pc})` : 'none',
                }}
              >
                {L.node}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

