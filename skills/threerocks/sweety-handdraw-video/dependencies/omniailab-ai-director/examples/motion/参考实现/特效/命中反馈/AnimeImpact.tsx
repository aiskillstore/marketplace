// ---
// name: omniailab-motion-demo-anime-impact
// description: 参考实现——参考实现/特效/命中反馈/AnimeImpact.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, Card, TitleBlock, G } from '../../_fixtures/Fixtures';

// anime-impact 动漫打击帧〔组合〕：crash-zoom 急推撞停在目标卡上的那 3 帧，
// 整幅画面反转成黑白负片 + 手绘放射集中线 + 红青通道 ±8px 色散——
// 像素被打了一拳，第 4 帧一切撤掉恢复干净特写 + 6px 震屏衰减。
// 节拍：0–24 建立全景 hold → 24–30 急推(6f ease-in 到 2.4x) →
//       30–32 冲击帧(3f 负片/集中线/RGB split，每帧换形态) →
//       33 起恢复特写 + 震屏衰减 → ~45–120 静止读卡。

const ZOOM_START = 24;
const ZOOM_END = 30; // 撞停帧
const IMPACT_LEN = 3; // 冲击帧持续 3f（30/31/32）
const RECOVER = ZOOM_END + IMPACT_LEN; // 33：恢复干净特写

// 目标卡：盖在 3x2 网格中排第 2 格上（列 2 行 1）
const CARD = { x: 808, y: 108, w: 524, h: 454 };
const CX = CARD.x + CARD.w / 2; // 1070
const CY = CARD.y + CARD.h / 2; // 335
const SCALE_END = 2.4;

// seed 正弦哈希（禁 Math.random）
const rnd = (i: number) => {
  const s = Math.sin(i * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

// 手绘放射集中线：30 根从卡片周缘指向画框外的尖楔形，phase 换一次形态
const SpeedLines: React.FC<{ phase: number }> = ({ phase }) => {
  const cx = 960;
  const cy = 540;
  const R_OUT = 1300; // 超出画框对角(~1101)
  const polys = Array.from({ length: 30 }).map((_, i) => {
    const k = i * 13 + phase * 101;
    const ang = ((i + 0.5) / 30) * Math.PI * 2 + (rnd(k) - 0.5) * 0.22;
    const r0 = 300 + rnd(k + 1) * 220; // 内端长短随机（卡片周缘一带）
    const halfW = (7 + rnd(k + 2) * 16) / R_OUT; // 外端宽 7–23px 的楔形
    const ax = cx + Math.cos(ang) * r0;
    const ay = cy + Math.sin(ang) * r0;
    const b1x = cx + Math.cos(ang - halfW) * R_OUT;
    const b1y = cy + Math.sin(ang - halfW) * R_OUT;
    const b2x = cx + Math.cos(ang + halfW) * R_OUT;
    const b2y = cy + Math.sin(ang + halfW) * R_OUT;
    return `${ax},${ay} ${b1x},${b1y} ${b2x},${b2y}`;
  });
  return (
    <svg
      viewBox="0 0 1920 1080"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
    >
      {polys.map((pts, i) => (
        <polygon key={i} points={pts} fill={i % 4 === 0 ? '#111111' : '#f5f5f5'} />
      ))}
    </svg>
  );
};

// 目标卡叠层 + 全景底
const Scene: React.FC = () => (
  <>
    <FakeDashboard variant="A" />
    <div style={{ position: 'absolute', left: CARD.x, top: CARD.y }}>
      <Card
        w={CARD.w}
        h={CARD.h}
        seed={9}
        style={{ boxShadow: '0 10px 36px rgba(0,0,0,0.18)', border: `3px solid ${G.ink}` }}
      />
      <div style={{ position: 'absolute', left: 24, bottom: 96 }}>
        <TitleBlock text="IMPACT" size={92} />
      </div>
    </div>
  </>
);

export const AnimeImpact: React.FC = () => {
  const frame = useCurrentFrame();

  // 急推：6f ease-in 撞到 2.4x，卡心推到画面正中
  const p = interpolate(frame, [ZOOM_START, ZOOM_END], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const scale = 1 + p * (SCALE_END - 1);
  const tx = (960 - CX) * p;
  const ty = (540 - CY) * p;

  const impact = frame >= ZOOM_END && frame < RECOVER;
  const phase = impact ? frame - ZOOM_END : 0; // 每 1f 换一次集中线形态

  // 撞停后震屏：6px 起步、指数衰减，~12f 收干后真静止
  const since = frame - RECOVER;
  const env = since >= 0 ? 6 * Math.exp(-since / 2.2) : 0;
  const shakeX = env * Math.sin(since * 3.7);
  const shakeY = env * 0.7 * Math.sin(since * 5.1 + 0.9);

  const zoomStyle: React.CSSProperties = {
    position: 'absolute',
    inset: 0,
    transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
    transformOrigin: `${CX}px ${CY}px`,
  };

  return (
    <AbsoluteFill style={{ background: impact ? '#131315' : G.bg, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, transform: `translate(${shakeX}px, ${shakeY}px)` }}>
        {/* 主层：冲击帧期间整幅负片黑白 */}
        <div style={{ ...zoomStyle, filter: impact ? 'invert(1) grayscale(1)' : 'none' }}>
          <Scene />
        </div>
        {/* RGB split：红/青双层负片副本，screen 叠底、±8px 错位（随 phase 抖动） */}
        {impact && (
          <>
            <div
              style={{
                position: 'absolute',
                inset: 0,
                mixBlendMode: 'screen',
                transform: `translate(-8px, ${phase % 2 === 0 ? 4 : -4}px)`,
              }}
            >
              <div style={{ ...zoomStyle, filter: 'invert(1) grayscale(1)' }}>
                <Scene />
              </div>
              <div style={{ position: 'absolute', inset: 0, background: '#ff0033', mixBlendMode: 'multiply' }} />
            </div>
            <div
              style={{
                position: 'absolute',
                inset: 0,
                mixBlendMode: 'screen',
                transform: `translate(8px, ${phase % 2 === 0 ? -4 : 4}px)`,
              }}
            >
              <div style={{ ...zoomStyle, filter: 'invert(1) grayscale(1)' }}>
                <Scene />
              </div>
              <div style={{ position: 'absolute', inset: 0, background: '#00e5ff', mixBlendMode: 'multiply' }} />
            </div>
            {/* 手绘放射集中线：每帧换形态 */}
            <SpeedLines phase={phase} />
          </>
        )}
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

