// ---
// name: omniailab-motion-demo-color-block-step-wipe
// description: 色块阶跃吞屏 —— 纯色矩形按 steps() 离散阶跃吞屏转场
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 色块阶跃吞屏 —— 纯色矩形按 steps() 离散阶跃吞屏转场
// 源：notion-ai 1.5–3.5s（蓝块中央阶跃生长）+ 26–27s（红块右下角斜向吃屏，携带页面卡）
// 核心语法：无缓动、逐帧硬跳的块状生长，像素游戏手感。
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { G, Card } from '../../_fixtures/Fixtures';

const BLUE = '#2383e2';
const RED = '#e8503a';

// 离散阶跃：frame 越过阈值瞬间跳到新值，无插值
const stepVal = (frame: number, steps: Array<[number, number]>): number => {
  let v = steps[0][1];
  for (const [f, val] of steps) {
    if (frame >= f) v = val;
  }
  return v;
};

// 蓝底上的圆形 AI 表情徽章
const AiBadge: React.FC<{ scale: number; opacity: number }> = ({ scale, opacity }) => (
  <div
    style={{
      width: 170,
      height: 170,
      borderRadius: '50%',
      background: '#fdf6ec',
      opacity,
      transform: `scale(${scale})`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 6px 24px rgba(0,0,0,0.18)',
    }}
  >
    <svg width={110} height={110} viewBox="0 0 110 110">
      <circle cx={36} cy={44} r={8} fill={G.ink} />
      <circle cx={74} cy={44} r={8} fill={G.ink} />
      <path d="M32 70 Q55 88 78 70" stroke={G.ink} strokeWidth={7} fill="none" strokeLinecap="round" />
      <path d="M24 28 Q34 20 44 26" stroke={G.ink} strokeWidth={6} fill="none" strokeLinecap="round" />
      <path d="M66 26 Q76 20 86 28" stroke={G.ink} strokeWidth={6} fill="none" strokeLinecap="round" />
    </svg>
  </div>
);

// 变体 B 背景：极简灰阶页面（不动 Fixtures，只组合）
const GrayPage: React.FC = () => (
  <AbsoluteFill style={{ background: G.panel, padding: '90px 160px', boxSizing: 'border-box' }}>
    <div style={{ height: 40, width: 560, background: G.bar, borderRadius: 12, marginBottom: 40 }} />
    {[92, 78, 86, 60].map((w, i) => (
      <div key={i} style={{ height: 18, width: `${w}%`, background: G.line, borderRadius: 9, marginBottom: 24 }} />
    ))}
    <div style={{ display: 'flex', gap: 32, marginTop: 30 }}>
      <Card w={420} h={280} seed={2} />
      <Card w={420} h={280} seed={5} />
    </div>
  </AbsoluteFill>
);

export const ColorBlockStepWipe: React.FC = () => {
  const frame = useCurrentFrame();

  // ---------- 场景 A（0–77f）：蓝块中央阶跃生长 ----------
  if (frame < 78) {
    // [宽, 高] 逐级硬跳：小条 → 长条 → 半屏色带 → 全屏
    const w = stepVal(frame, [
      [0, 0],
      [8, 280],
      [16, 820],
      [24, 1340],
      [32, 1920],
      [44, 1920],
    ]);
    const h = stepVal(frame, [
      [0, 0],
      [8, 96],
      [16, 96],
      [24, 320],
      [32, 580],
      [44, 1080],
    ]);
    // 徽章：全屏接管后阶跃弹出（同样离散，两跳到位）
    const badgeScale = stepVal(frame, [
      [0, 0],
      [52, 0.55],
      [58, 1.12],
      [63, 1],
    ]);
    const badgeOpacity = frame >= 52 ? 1 : 0;
    return (
      <AbsoluteFill style={{ background: G.bg, alignItems: 'center', justifyContent: 'center' }}>
        <div
          style={{
            position: 'absolute',
            left: 960 - w / 2,
            top: 540 - h / 2,
            width: w,
            height: h,
            background: BLUE,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        />
        <AiBadge scale={badgeScale} opacity={badgeOpacity} />
      </AbsoluteFill>
    );
  }

  // ---------- 场景 B（78–149f）：红块从右下角斜向阶跃吃屏，携带灰阶页面卡 ----------
  // p 控制对角线推进量：p=0 无，p=200 全覆盖
  const p = stepVal(frame, [
    [78, 0],
    [84, 42],
    [96, 106],
    [108, 200],
  ]);
  // 卡片随色块逐跳前进（同样离散跳位）
  const cardPos = stepVal(frame, [
    [78, 0],
    [84, 1],
    [96, 2],
    [108, 3],
  ]);
  const cardXY: Array<[number, number]> = [
    [2100, 1180], // 画外
    [1480, 800],
    [980, 560],
    [560, 350],
  ];
  const [cx, cy] = cardXY[cardPos];
  const clip =
    p <= 0
      ? 'polygon(100% 100%, 100% 100%, 100% 100%)'
      : `polygon(${100 - p}% 100%, 100% ${100 - p}%, 100% 100%)`;

  return (
    <AbsoluteFill>
      <GrayPage />
      <AbsoluteFill style={{ background: RED, clipPath: clip }} />
      {p > 0 && (
        <div
          style={{
            position: 'absolute',
            left: cx - 210,
            top: cy - 145,
            transform: 'rotate(-4deg)',
            boxShadow: '0 18px 50px rgba(0,0,0,0.3)',
            borderRadius: 14,
          }}
        >
          <Card w={420} h={290} seed={7} />
        </div>
      )}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

