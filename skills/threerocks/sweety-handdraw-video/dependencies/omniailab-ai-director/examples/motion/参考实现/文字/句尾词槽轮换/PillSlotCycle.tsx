// ---
// name: omniailab-motion-demo-pill-slot-cycle
// description: 句尾词槽轮换 —— 句中词槽轮换：固定句干 + 句尾 pill 老虎机式滚一格
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 句尾词槽轮换 —— 句中词槽轮换：固定句干 + 句尾 pill 老虎机式滚一格
// 源：notion-ai 4.5–8.5s。旧 pill 上飞淡出、新 pill 从下带运动模糊滑入，
// 连换 6 次后 pill 消失、句子落成 "One AI tool to do it all." 收束。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const FONT = 'Helvetica, Arial, sans-serif';

const PILLS = [
  { label: 'Ask a question', icon: '?' },
  { label: 'Find in Drive', icon: '▲' },
  { label: 'Find in Slack', icon: '#' },
  { label: 'Summarize', icon: '≡' },
  { label: 'Improve writing', icon: '✎' },
  { label: 'Draft an agenda', icon: '☰' },
];

const BEAT = 21; // ~0.7s @30fps
const INTRO = 12; // 句干入场
const CYCLES = PILLS.length;

const Pill: React.FC<{ label: string; icon: string; style?: React.CSSProperties }> = ({
  label,
  icon,
  style,
}) => (
  <div
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 16,
      padding: '14px 36px 14px 24px',
      borderRadius: 999,
      background: '#fff',
      border: `3px solid ${G.border}`,
      boxShadow: '0 6px 18px rgba(0,0,0,0.10)',
      fontFamily: FONT,
      fontWeight: 700,
      fontSize: 64,
      color: G.ink,
      whiteSpace: 'nowrap',
      ...style,
    }}
  >
    <span
      style={{
        width: 58,
        height: 58,
        borderRadius: 14,
        background: G.bg,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 38,
        color: G.mid,
        flexShrink: 0,
      }}
    >
      {icon}
    </span>
    {label}
  </div>
);

export const PillSlotCycle: React.FC = () => {
  const frame = useCurrentFrame();

  // 句干入场：ease-out 上浮淡入
  const stemT = interpolate(frame, [0, INTRO], [0, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const cycleStart = INTRO;
  const cycleEnd = cycleStart + CYCLES * BEAT;

  // 当前处于第几个 pill 拍
  const rel = frame - cycleStart;
  const idx = Math.min(Math.floor(rel / BEAT), CYCLES - 1);
  const beatFrame = rel - idx * BEAT;

  const SWAP = 8; // 每拍前 8f 完成换位

  // 收束段：pill 上飞消失，"do it all." 从下滑入落位
  const isFinale = frame >= cycleEnd;
  const finT = interpolate(frame, [cycleEnd, cycleEnd + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.back(1.4)),
  });

  // 槽内容渲染
  let slot: React.ReactNode = null;
  if (!isFinale && rel >= 0) {
    const incoming = PILLS[idx];
    const outgoing = idx > 0 ? PILLS[idx - 1] : null;

    // 新 pill：从下 +120px 带 blur 滑入，ease-out
    const inT = interpolate(beatFrame, [0, SWAP], [0, 1], {
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
    const inY = interpolate(inT, [0, 1], [120, 0]);
    const inBlur = interpolate(inT, [0, 0.7, 1], [14, 4, 0]);

    // 旧 pill：向上 -120px 加速飞出淡掉
    const outT = interpolate(beatFrame, [0, SWAP - 1], [0, 1], {
      extrapolateRight: 'clamp',
      easing: Easing.in(Easing.cubic),
    });
    const outY = interpolate(outT, [0, 1], [0, -130]);

    slot = (
      <div style={{ position: 'relative', display: 'inline-block' }}>
        {/* 撑起槽宽度的隐形占位（当前 pill） */}
        <Pill label={incoming.label} icon={incoming.icon} style={{ visibility: 'hidden' }} />
        {outgoing && outT < 1 && (
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              transform: `translateY(${outY}px)`,
              opacity: 1 - outT,
              filter: `blur(${outT * 10}px)`,
            }}
          >
            <Pill label={outgoing.label} icon={outgoing.icon} />
          </div>
        )}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            transform: `translateY(${inY}px)`,
            opacity: idx === 0 ? inT : Math.min(1, inT * 1.6),
            filter: `blur(${inBlur}px)`,
          }}
        >
          <Pill label={incoming.label} icon={incoming.icon} />
        </div>
      </div>
    );
  } else if (isFinale) {
    // 最后一个 pill 上飞离场（前 8f），然后 "do it all." 落位
    const lastOutT = interpolate(frame, [cycleEnd, cycleEnd + 7], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.in(Easing.cubic),
    });
    slot = (
      <div style={{ position: 'relative', display: 'inline-block' }}>
        <span
          style={{
            fontFamily: FONT,
            fontWeight: 800,
            fontSize: 96,
            color: G.ink,
            letterSpacing: -1,
            display: 'inline-block',
            opacity: finT,
            transform: `translateY(${(1 - finT) * 90}px)`,
            filter: `blur(${(1 - finT) * 8}px)`,
            whiteSpace: 'nowrap',
          }}
        >
          do it all.
        </span>
        {lastOutT < 1 && (
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: -8,
              transform: `translateY(${-130 * lastOutT}px)`,
              opacity: 1 - lastOutT,
              filter: `blur(${lastOutT * 10}px)`,
            }}
          >
            <Pill label={PILLS[CYCLES - 1].label} icon={PILLS[CYCLES - 1].icon} />
          </div>
        )}
      </div>
    );
  }

  return (
    <AbsoluteFill style={{ background: G.bg }}>
      {/* 句干固定不动：整行左端锚死，不随 pill 宽度居中重排 */}
      <div
        style={{
          position: 'absolute',
          left: 300,
          top: 540,
          transform: `translateY(calc(-50% + ${(1 - stemT) * 50}px))`,
          display: 'flex',
          alignItems: 'center',
          gap: 36,
          opacity: stemT,
        }}
      >
        <span
          style={{
            fontFamily: FONT,
            fontWeight: 800,
            fontSize: 96,
            color: G.ink,
            letterSpacing: -1,
            whiteSpace: 'nowrap',
          }}
        >
          One AI tool to
        </span>
        {slot}
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

