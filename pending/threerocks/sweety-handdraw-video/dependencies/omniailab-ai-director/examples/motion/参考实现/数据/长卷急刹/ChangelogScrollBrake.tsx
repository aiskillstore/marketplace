// ---
// name: omniailab-motion-demo-changelog-scroll-brake
// description: changelog-scroll-brake —— Changelog 长卷急刹
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// changelog-scroll-brake —— Changelog 长卷急刹
// ~34 行灰阶条目（行高错落）从下往上高速掠过（easeOutExpo 指数减速），
// 高速段叠 blur（速度差分驱动，糊成色带），急刹精准停位后目标行抬升
// （scale 1.03 + 阴影加深）+ 高亮描边，其余行退暗。f=84 后全静止（56f）。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const CL = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// 时间轴
const SCROLL0 = 14; // 前 14f 初始静置（停在长卷顶部）
const SCROLL1 = 64; // 急刹停位帧
const LIFT0 = 68; // 目标行抬升开始
const LIFT1 = 82;

const COL_W = 1000;
const COL_X = (1920 - COL_W) / 2;
const GAP = 20;
const N = 34;
const TARGET = 28;

// 行高错落（帧确定性：全由 i 决定）
const rowH = (i: number) => 72 + ((i * 29) % 3) * 22; // 72 / 94 / 116

// 预计算每行 y
const rowY: number[] = [];
{
  let y = 0;
  for (let i = 0; i < N; i++) {
    rowY.push(y);
    y += rowH(i) + GAP;
  }
}
const TARGET_CY = rowY[TARGET] + rowH(TARGET) / 2;
const END_T = 540 - TARGET_CY; // 目标行停在画面正中
const START_T = 80; // 起始：长卷顶部略下

const scrollAt = (f: number): number =>
  interpolate(f, [SCROLL0, SCROLL1], [START_T, END_T], {
    easing: Easing.out(Easing.exp),
    ...CL,
  });

const Row: React.FC<{ i: number; frame: number }> = ({ i, frame }) => {
  const isTarget = i === TARGET;
  const h = rowH(i);
  const titleW = 30 + ((i * 37) % 45);

  // 目标行抬升 + 高亮；其余行退暗
  const t = interpolate(frame, [LIFT0, LIFT1], [0, 1], {
    easing: Easing.out(Easing.cubic),
    ...CL,
  });
  const lift = isTarget ? t : 0;
  const dim = isTarget ? 0 : t;

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: rowY[i],
        width: COL_W,
        height: h,
        background: G.card,
        border: isTarget && lift > 0 ? `3px solid rgba(47,47,47,${lift})` : `2px solid ${G.border}`,
        borderRadius: 14,
        display: 'flex',
        alignItems: 'center',
        gap: 24,
        padding: '0 30px',
        boxSizing: 'border-box',
        transform: `scale(${1 + 0.03 * lift})`,
        boxShadow:
          lift > 0
            ? `0 ${6 + 22 * lift}px ${16 + 44 * lift}px rgba(0,0,0,${0.08 + 0.28 * lift})`
            : '0 2px 8px rgba(0,0,0,0.06)',
        opacity: 1 - 0.62 * dim,
        zIndex: isTarget ? 2 : 1,
      }}
    >
      <div style={{ width: 88, height: 26, borderRadius: 13, background: isTarget ? '#4a4a48' : G.mid, flexShrink: 0 }} />
      <div style={{ height: 16, width: `${titleW}%`, background: G.bar, borderRadius: 8 }} />
      <div style={{ marginLeft: 'auto', height: 12, width: 110, background: G.line, borderRadius: 6, flexShrink: 0 }} />
    </div>
  );
};

export const ChangelogScrollBrake: React.FC = () => {
  const frame = useCurrentFrame();
  const T = scrollAt(frame);

  // 速度差分驱动模糊：v 达 60px/f 即满 6px blur
  const v = Math.abs(scrollAt(frame) - scrollAt(frame - 1));
  const blur = Math.min(v / 60, 1) * 6;

  return (
    <div style={{ width: 1920, height: 1080, background: G.bg, position: 'relative', overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          left: COL_X,
          top: 0,
          width: COL_W,
          height: 1080,
          transform: `translateY(${T}px)`,
          filter: blur > 0.15 ? `blur(${blur}px)` : undefined,
        }}
      >
        {Array.from({ length: N }).map((_, i) => (
          <Row key={i} i={i} frame={frame} />
        ))}
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

