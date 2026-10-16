// ---
// name: omniailab-motion-demo-bento-light-up
// description: 参考实现——参考实现/界面入场/整墙批量入场/BentoLightUp.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { Card, TitleBlock } from '../../_fixtures/Fixtures';

// bento-light-up：暗场里 3×2 bento 墙压暗待命，随节拍逐格点亮——
// 边框流光先描一圈（琥珀），格内内容随后提亮上浮弹出；六格全亮后整体微推收住。
// 节拍：0–20 建立(hold) → 每格间隔 12f 依次激活(描边 8f + 内容弹出 8f)
//       → ~96f 全亮 → 96–121 scale 1→1.04 缓推 → 121–150 静止收尾。

const BG = '#2a2a28';
const AMBER = '#e8b45e';
const FIRST = 20; // 首格激活帧
const GAP = 12; // 格间节拍
const CELL_W = 480;
const CELL_H = 330;
const GUT = 44;
const LEFT = (1920 - (CELL_W * 3 + GUT * 2)) / 2;
const TOP = (1080 - (CELL_H * 2 + GUT)) / 2 + 30;

const Cell: React.FC<{ i: number; frame: number }> = ({ i, frame }) => {
  const start = FIRST + i * GAP;
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = LEFT + col * (CELL_W + GUT);
  const y = TOP + row * (CELL_H + GUT);

  // ① 边框流光：pathLength=100 的 dashoffset 描边，8f 走完一圈
  const draw = interpolate(frame, [start, start + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  // 描完后流光退火：琥珀亮边 → 弱化成常亮细边
  const strokeFade = interpolate(frame, [start + 12, start + 26], [1, 0.4], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  // ② 内容提亮 + 上浮弹出：描边过半后接力，8f 弹出（back-out 带一点过冲）
  const lit = interpolate(frame, [start + 6, start + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const rise = interpolate(frame, [start + 6, start + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.3, 1.4, 0.5, 1),
  });
  const opacity = 0.18 + 0.82 * lit;
  const ty = 20 * (1 - rise);
  // seed 正弦哈希做每格微差（点亮瞬间的辉光强度略有随机感）
  const jitter = Math.abs(Math.sin(i * 127.3) * 43758.5453 % 1);
  const glow = lit * (1 - lit) * 4 * (14 + jitter * 6); // 点亮中段最亮的辉光脉冲

  return (
    <div style={{ position: 'absolute', left: x, top: y, width: CELL_W, height: CELL_H }}>
      {/* 暗态卡 + 点亮后的内容（同一张卡，靠 opacity/translateY 提亮浮出） */}
      <div
        style={{
          opacity,
          transform: `translateY(${ty}px)`,
          boxShadow: lit > 0.5 ? `0 0 ${glow}px rgba(232,180,94,${0.35 * lit * (1 - lit) * 4})` : 'none',
          borderRadius: 14,
        }}
      >
        <Card w={CELL_W} h={CELL_H} seed={i + 1} />
      </div>
      {/* 边框流光：SVG rect 描边一圈 */}
      {draw > 0 && (
        <svg
          width={CELL_W}
          height={CELL_H}
          viewBox={`0 0 ${CELL_W} ${CELL_H}`}
          style={{ position: 'absolute', left: 0, top: ty, overflow: 'visible' }}
        >
          <rect
            x={2}
            y={2}
            width={CELL_W - 4}
            height={CELL_H - 4}
            rx={14}
            fill="none"
            stroke={AMBER}
            strokeWidth={4}
            pathLength={100}
            strokeDasharray={100}
            strokeDashoffset={100 * (1 - draw)}
            opacity={strokeFade}
            style={{ filter: `drop-shadow(0 0 ${6 + jitter * 4}px ${AMBER})` }}
          />
        </svg>
      )}
    </div>
  );
};

export const BentoLightUp: React.FC = () => {
  const frame = useCurrentFrame();

  // ③ 六格全亮(~96f)后整体缓推 scale 1→1.04，25f 收住，之后真静止
  const push = interpolate(frame, [96, 121], [1, 1.04], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.33, 0, 0.2, 1),
  });

  // 标题随首格点亮微微提亮，交代场景
  const titleLit = interpolate(frame, [FIRST, FIRST + 20], [0.25, 0.75], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  return (
    <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `scale(${push})`,
          transformOrigin: '960px 540px',
        }}
      >
        <div style={{ position: 'absolute', left: LEFT, top: TOP - 110, opacity: titleLit, filter: 'invert(1)' }}>
          <TitleBlock text="Features" size={64} />
        </div>
        {Array.from({ length: 6 }).map((_, i) => (
          <Cell key={i} i={i} frame={frame} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

