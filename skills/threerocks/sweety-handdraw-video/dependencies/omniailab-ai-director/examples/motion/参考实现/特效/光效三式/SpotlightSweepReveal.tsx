// ---
// name: omniailab-motion-demo-spotlight-sweep-reveal
// description: 参考实现——参考实现/特效/光效三式/SpotlightSweepReveal.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from 'remotion';

// spotlight-sweep-reveal: 聚光灯摆动扫字
// 暗场 #2a2a28，标题两行常驻 opacity 0.07；亮版同文本用 radial-gradient mask，
// 光斑 x 按 sin 摆动扫两个来回（周期 ~55f），f110 后全字提亮定格，
// 光斑/光锥线性消散并在 f>=125 条件卸载，125–160 真静止 35f。

const BG = '#2a2a28';
const INKW = '#f5f5f3';

const CX = 960;
const CY = 540;
const AMP = 560; // 摆动幅度
const PERIOD = 55; // 单个来回帧数
const SWEEP_END = 110; // 两个来回结束
const REVEAL_END = 125; // 提亮完成，之后真静止

const textStyle: React.CSSProperties = {
  fontFamily: 'Helvetica Neue, Helvetica, Arial, sans-serif',
  fontSize: 150,
  fontWeight: 800,
  lineHeight: 1.15,
  letterSpacing: '0.04em',
  color: INKW,
  textAlign: 'center',
  whiteSpace: 'pre',
};

const TitleText: React.FC = () => (
  <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
    <div style={textStyle}>{'SPOTLIGHT\nON'}</div>
  </AbsoluteFill>
);

export const SpotlightSweepReveal: React.FC = () => {
  const f = useCurrentFrame();

  // 光斑 x：sin 摆动，两个来回后停在中心
  const sweepF = Math.min(f, SWEEP_END);
  const x = CX + AMP * Math.sin((2 * Math.PI * sweepF) / PERIOD);

  // 全字提亮（扩散感 out-cubic）
  const brighten = interpolate(f, [SWEEP_END, REVEAL_END], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  // 光斑/光锥消散（线性）
  const fadeOut = interpolate(f, [SWEEP_END, REVEAL_END], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const sweepAlive = f < REVEAL_END; // 条件卸载，保证末段真静止

  const maskGrad = `radial-gradient(circle 380px at ${x}px ${CY}px, rgba(0,0,0,1) 0%, rgba(0,0,0,0.95) 45%, rgba(0,0,0,0) 100%)`;

  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {/* 暗版文字常驻 */}
      <AbsoluteFill style={{ opacity: 0.07 }}>
        <TitleText />
      </AbsoluteFill>

      {sweepAlive && (
        <>
          {/* 光锥：从顶部收拢到光斑 */}
          <AbsoluteFill
            style={{
              opacity: fadeOut,
              clipPath: `polygon(${CX - 70}px -40px, ${CX + 70}px -40px, ${x + 420}px ${CY + 230}px, ${x - 420}px ${CY + 230}px)`,
              background:
                'linear-gradient(to bottom, rgba(245,245,243,0.16), rgba(245,245,243,0.03) 85%, rgba(245,245,243,0) 100%)',
            }}
          />
          {/* 落在暗墙上的柔光斑 */}
          <AbsoluteFill
            style={{
              opacity: fadeOut,
              background: `radial-gradient(circle 460px at ${x}px ${CY}px, rgba(245,245,243,0.22) 0%, rgba(245,245,243,0.08) 55%, rgba(245,245,243,0) 100%)`,
            }}
          />
          {/* 亮版文字，按帧移动的 radial mask */}
          <AbsoluteFill
            style={{
              opacity: fadeOut === 1 ? 1 : Math.max(fadeOut, 0),
              WebkitMaskImage: maskGrad,
              maskImage: maskGrad,
            }}
          >
            <TitleText />
          </AbsoluteFill>
        </>
      )}

      {/* 全亮定格层 */}
      <AbsoluteFill style={{ opacity: brighten }}>
        <TitleText />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

