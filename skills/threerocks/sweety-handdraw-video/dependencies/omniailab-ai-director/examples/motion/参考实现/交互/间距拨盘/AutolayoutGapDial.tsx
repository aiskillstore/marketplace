// ---
// name: omniailab-motion-demo-autolayout-gap-dial
// description: 间距拨盘 —— framer-ai 4.5–5.5s
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 间距拨盘 —— framer-ai 4.5–5.5s
// 一排导航链接块带框选描边 + 间距标注徽章，徽章数字逐格跳动，
// 链接块被参数实时推开（flex gap 插值），标注线跟随。
// demo 放大做：间距从紧(16)拉到松(64)，再弹簧回弹归位。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const BLOCK_WIDTHS = [230, 190, 265, 210, 245];
const BLOCK_H = 100;
const ROW_Y = 540; // 行中心
const G_MIN = 12;
const G_MAX = 110;

const GROW_START = 14;
const GROW_END = 52;
const HOLD_END = 66;

export const AutolayoutGapDial: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 间距参数曲线：紧 → 松（easeInOut）→ hold → 弹簧回弹归位（带过冲）
  let gap: number;
  if (frame < HOLD_END) {
    gap = interpolate(frame, [GROW_START, GROW_END], [G_MIN, G_MAX], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.inOut(Easing.cubic),
    });
  } else {
    const s = spring({ frame: frame - HOLD_END, fps, config: { damping: 9, stiffness: 80, mass: 1.1 } });
    gap = G_MAX + (G_MIN - G_MAX) * s; // damping 9 → 过冲到 G_MIN 以下再回稳
  }
  const gapShown = Math.round(gap / 2) * 2; // 徽章逐格跳数（步进 2）

  // 布局：居中排布
  const total = BLOCK_WIDTHS.reduce((a, b) => a + b, 0) + gap * (BLOCK_WIDTHS.length - 1);
  const startX = (1920 - total) / 2;
  const xs: number[] = [];
  let acc = startX;
  for (const w of BLOCK_WIDTHS) {
    xs.push(acc);
    acc += w + gap;
  }

  // 框选描边入场
  const selIn = spring({ frame: frame - 2, fps, config: { damping: 14, stiffness: 130 } });
  const pad = 26;
  const selX = startX - pad;
  const selW = total + pad * 2;
  const selY = ROW_Y - BLOCK_H / 2 - pad;
  const selH = BLOCK_H + pad * 2;

  // 徽章在数值变动时的每格"跳一下"
  const ticking = Math.abs(gap - (frame < HOLD_END ? G_MIN : G_MIN)) > 0.5 && (frame >= GROW_START && frame < HOLD_END + 40);
  const tickPulse = ticking ? 1 + 0.10 * Math.abs(Math.sin(frame * 0.9)) : 1;

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      <AbsoluteFill
        style={{
          backgroundImage: `radial-gradient(${G.line} 3px, transparent 3px)`,
          backgroundSize: '52px 52px',
        }}
      />

      {/* 标题字块（讲清这是"参数驱动布局"） */}
      <div style={{ position: 'absolute', top: 250, width: '100%', textAlign: 'center', fontFamily: 'Helvetica, Arial, sans-serif', fontWeight: 800, fontSize: 44, color: G.mid, letterSpacing: 2 }}>
        GAP
        <span style={{ display: 'inline-block', minWidth: 130, marginLeft: 24, padding: '4px 22px', borderRadius: 12, background: G.ink, color: '#f2f2f0', fontVariantNumeric: 'tabular-nums', transform: `scale(${tickPulse})` }}>
          {gapShown}
        </span>
      </div>

      {/* 框选描边 + 8 手柄 */}
      <div
        style={{
          position: 'absolute',
          left: selX,
          top: selY,
          width: selW,
          height: selH,
          border: `3px solid ${G.ink}`,
          borderRadius: 6,
          opacity: selIn,
          boxSizing: 'border-box',
        }}
      >
        {[
          [0, 0], [0.5, 0], [1, 0],
          [0, 0.5], [1, 0.5],
          [0, 1], [0.5, 1], [1, 1],
        ].map(([hx, hy], i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${hx * 100}%`,
              top: `${hy * 100}%`,
              width: 16,
              height: 16,
              marginLeft: -8,
              marginTop: -8,
              background: '#fff',
              border: `3px solid ${G.ink}`,
              borderRadius: 3,
              boxSizing: 'border-box',
            }}
          />
        ))}
      </div>

      {/* 链接块 */}
      {BLOCK_WIDTHS.map((w, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: xs[i],
            top: ROW_Y - BLOCK_H / 2,
            width: w,
            height: BLOCK_H,
            background: G.card,
            border: `2px solid ${G.border}`,
            borderRadius: 14,
            boxShadow: '0 3px 12px rgba(0,0,0,0.07)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxSizing: 'border-box',
          }}
        >
          <div style={{ height: 16, width: w - 76, background: G.bar, borderRadius: 8 }} />
        </div>
      ))}

      {/* 间距标注：测量线 + 端刺 + 跟随徽章 */}
      {xs.slice(0, -1).map((x, i) => {
        const gx = x + BLOCK_WIDTHS[i]; // 缝隙左缘
        const cy = ROW_Y + BLOCK_H / 2 + 56;
        const badgeOp = interpolate(frame, [8, 16], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        return (
          <div key={i} style={{ position: 'absolute', left: 0, top: 0, opacity: badgeOp }}>
            {/* 竖直延长线 */}
            <div style={{ position: 'absolute', left: gx - 1.5, top: ROW_Y + BLOCK_H / 2 + 6, width: 3, height: 62, background: G.mid, opacity: 0.55 }} />
            <div style={{ position: 'absolute', left: gx + gap - 1.5, top: ROW_Y + BLOCK_H / 2 + 6, width: 3, height: 62, background: G.mid, opacity: 0.55 }} />
            {/* 水平测量线 */}
            <div style={{ position: 'absolute', left: gx, top: cy - 1.5, width: gap, height: 3, background: G.ink }} />
            {/* 徽章（跟随缝隙中心） */}
            <div
              style={{
                position: 'absolute',
                left: gx + gap / 2,
                top: cy + 18,
                transform: `translateX(-50%) scale(${tickPulse})`,
                padding: '5px 14px',
                borderRadius: 10,
                background: G.ink,
                color: '#f2f2f0',
                fontFamily: 'Helvetica, Arial, sans-serif',
                fontWeight: 700,
                fontSize: 24,
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {gapShown}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

