// ---
// name: omniailab-motion-demo-title-demote-to-label
// description: 标题降格为标签 —— 大标题降格为节标签
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 标题降格为标签 —— 大标题降格为节标签
// 源：perplexity-promo 16–18.5s。大标题居中显影站稳一拍，随后缩小 ~0.3x
// 平移到左上角变小节标签，内容区（灰阶骨架块）在其下方生长。
// 附加变体（framer text-selection-title）：标题登场带文本选中蓝高亮块、随后撤掉。
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';
import { G } from '../../_fixtures/Fixtures';

const FONT = 'Helvetica, Arial, sans-serif';
const SEL = 'rgba(58, 128, 236, 0.35)';

// 内容骨架块：随 t 依次生长
const Skeleton: React.FC<{ t: number }> = ({ t }) => {
  const blocks = [
    { w: 1500, h: 26 },
    { w: 1280, h: 26 },
    { w: 1420, h: 26 },
    { w: 760, h: 26 },
    { w: 1500, h: 300, card: true },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 34 }}>
      {blocks.map((b, i) => {
        const bt = interpolate(t, [i * 0.16, i * 0.16 + 0.3], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.cubic),
        });
        return (
          <div
            key={i}
            style={{
              width: b.w * (0.35 + 0.65 * bt),
              height: b.h,
              background: b.card ? G.card : G.line,
              border: b.card ? `2px solid ${G.border}` : 'none',
              borderRadius: b.card ? 16 : 13,
              opacity: bt,
              transform: `translateY(${(1 - bt) * 28}px)`,
              boxSizing: 'border-box',
            }}
          />
        );
      })}
    </div>
  );
};

// 一个完整的"显影→(可选高亮)→降格→内容生长"小节
const DemoteScene: React.FC<{
  frame: number;
  title: string;
  withSelection: boolean;
}> = ({ frame, title, withSelection }) => {
  // 时间轴（局部帧）
  const REVEAL = 0; // 0–12 显影
  const SEL_ON = 14; // 高亮扫入 14–24
  const SEL_OFF = 32; // 高亮撤掉 32–40
  const DEMOTE = withSelection ? 44 : 32; // 降格开始
  const DEMOTE_END = DEMOTE + 20;
  const GROW = DEMOTE + 12;

  // 显影：blur + 淡入
  const rev = interpolate(frame, [REVEAL, REVEAL + 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // 降格补间：scale 1 -> 0.3，中心 -> 左上
  const dem = interpolate(frame, [DEMOTE, DEMOTE_END], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const scale = interpolate(dem, [0, 1], [1, 0.3]);
  // 用 left/top 补间：起点居中（由外层 flex 定位换算），终点左上角
  const x = interpolate(dem, [0, 1], [960, 150]);
  const y = interpolate(dem, [0, 1], [480, 110]);

  // 高亮块：从左扫入盖住文字，再从左撤掉
  let selLeft = 0;
  let selWidth = 0;
  if (withSelection) {
    const on = interpolate(frame, [SEL_ON, SEL_ON + 10], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.quad),
    });
    const off = interpolate(frame, [SEL_OFF, SEL_OFF + 8], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.in(Easing.quad),
    });
    selLeft = off * 100;
    selWidth = Math.max(0, on * 100 - selLeft);
  }

  const growT = interpolate(frame, [GROW, GROW + 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ background: G.bg }}>
      {/* 内容骨架区 */}
      <div style={{ position: 'absolute', left: 150, top: 210 }}>
        <Skeleton t={growT} />
      </div>
      {/* 标题：transform-origin 左中，位置补间 */}
      <div
        style={{
          position: 'absolute',
          left: x,
          top: y,
          transform: `translate(${-(1 - dem) * 50}%, -50%) scale(${scale})`,
          transformOrigin: 'left center',
          opacity: rev,
          filter: `blur(${(1 - rev) * 12}px)`,
        }}
      >
        <div
          style={{
            position: 'relative',
            fontFamily: FONT,
            fontWeight: 800,
            fontSize: 128,
            color: G.ink,
            letterSpacing: -2,
            whiteSpace: 'nowrap',
            padding: '10px 18px',
          }}
        >
          {withSelection && selWidth > 0 && (
            <div
              style={{
                position: 'absolute',
                left: `${selLeft}%`,
                top: 8,
                width: `${selWidth}%`,
                height: 'calc(100% - 16px)',
                background: SEL,
                borderRadius: 6,
              }}
            />
          )}
          <span style={{ position: 'relative' }}>{title}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const TitleDemoteToLabel: React.FC = () => {
  const frame = useCurrentFrame();
  const SPLIT = 92; // 变体 A 时长

  if (frame < SPLIT) {
    return <DemoteScene frame={frame} title="Running Subagents" withSelection={false} />;
  }
  // 变体 B：文本选中态高亮登场
  const f = frame - SPLIT;
  // 白闪转场 3f
  const flash = interpolate(f, [0, 4], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill>
      <DemoteScene frame={f} title="Select the Answer" withSelection={true} />
      <AbsoluteFill style={{ background: '#fff', opacity: flash, pointerEvents: 'none' }} />
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

