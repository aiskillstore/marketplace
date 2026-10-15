// ---
// name: omniailab-motion-demo-wireframe-draw-on
// description: 参考实现——参考实现/界面入场/整墙批量入场/WireframeDrawOn.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

// wireframe-draw-on〔入场退场〕：界面先以蓝图细线描画成形（stroke-dashoffset
// 分组错峰），随后一条发光竖线从左向右扫过，扫过之处线框实体化为真实灰阶界面。
// 节拍：0–20 hold 空底 → 20–82 分组描线 → 88–118 光线扫描实体化 → 118–150 hold。

// FakeDashboard variant A 的几何（1920×1080）：
// 侧栏 220 宽；顶栏 x220–1920 h72；内容区 padding36 gap28，3×2 卡片
// 卡 w524 h454，x = 256/808/1360，y = 108/590。
const CARD_W = 524;
const CARD_H = 454;
const CARD_X = [256, 808, 1360];
const CARD_Y = [108, 590];

const seedFrac = (i: number) => {
  const v = Math.sin(i * 127.3) * 43758.5453;
  return v - Math.floor(v);
};

export const WireframeDrawOn: React.FC = () => {
  const frame = useCurrentFrame();

  // 描线进度：每组 30f 画完，start 错峰
  const draw = (start: number) =>
    interpolate(frame, [start, start + 30], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.bezier(0.4, 0, 0.3, 1),
    });

  const tSide = draw(20); // 侧栏
  const tTop = draw(30); // 顶栏
  const tCards = Array.from({ length: 6 }, (_, i) => draw(40 + i * 3)); // 卡片错峰
  const tChart = draw(52); // 折线图

  // 实体化扫描：88–118 从左向右
  const scan = interpolate(frame, [88, 118], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.55, 0, 0.25, 1),
  });
  const scanX = scan * 1920;
  const lineOpacity = interpolate(frame, [86, 92, 112, 120], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 描线小工具：pathLength=1 + dashoffset 从 1 → 0
  const stroke = (t: number): React.SVGAttributes<SVGElement> => ({
    fill: 'none',
    stroke: G.mid,
    strokeWidth: 2.5,
    pathLength: 1,
    strokeDasharray: 1,
    strokeDashoffset: 1 - t,
    strokeLinecap: 'round',
    opacity: t > 0 ? 1 : 0,
  });

  // 折线图数据（seed 正弦哈希，落在卡 (1,1) 内部）
  const chartCardX = CARD_X[1];
  const chartCardY = CARD_Y[1];
  const chartPts = Array.from({ length: 8 }, (_, i) => {
    const px = chartCardX + 50 + (i * (CARD_W - 100)) / 7;
    const py = chartCardY + 130 + seedFrac(i + 3) * 230;
    return `${px},${py}`;
  }).join(' ');

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* —— 线框层（蓝图描线） —— */}
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{ position: 'absolute', inset: 0 }}
      >
        {/* 侧栏 */}
        <rect x={4} y={4} width={216} height={1072} rx={2} {...stroke(tSide)} />
        <rect x={26} y={30} width={40} height={40} rx={10} {...stroke(draw(24))} />
        {Array.from({ length: 7 }).map((_, i) => {
          const w = (216 - 44) * (0.6 + ((i * 29) % 35) / 100);
          return (
            <line
              key={`s${i}`}
              x1={26}
              y1={94 + i * 30}
              x2={26 + w}
              y2={94 + i * 30}
              {...stroke(draw(26 + i * 2))}
            />
          );
        })}

        {/* 顶栏 */}
        <line x1={220} y1={72} x2={1916} y2={72} {...stroke(tTop)} />
        <rect x={252} y={27} width={180} height={18} rx={9} {...stroke(draw(34))} />
        <rect x={1476} y={18} width={320} height={36} rx={18} {...stroke(draw(36))} />
        <circle cx={1834} cy={36} r={18} {...stroke(draw(38))} />

        {/* 3×2 卡片：轮廓 + 内部占位线 */}
        {tCards.map((t, i) => {
          const cx = CARD_X[i % 3];
          const cy = CARD_Y[Math.floor(i / 3)];
          const titleW = (CARD_W - 36) * (0.45 + (((i + 1) * 37) % 40) / 100);
          return (
            <g key={`c${i}`}>
              <rect x={cx} y={cy} width={CARD_W} height={CARD_H} rx={14} {...stroke(t)} />
              <rect x={cx + 18} y={cy + 18} width={titleW} height={16} rx={8} {...stroke(draw(46 + i * 3))} />
              <line x1={cx + 18} y1={cy + 62} x2={cx + 18 + (CARD_W - 36) * 0.82} y2={cy + 62} {...stroke(draw(49 + i * 3))} />
              <line x1={cx + 18} y1={cy + 88} x2={cx + 18 + (CARD_W - 36) * 0.62} y2={cy + 88} {...stroke(draw(51 + i * 3))} />
              <circle cx={cx + 31} cy={cy + CARD_H - 31} r={13} {...stroke(draw(53 + i * 3))} />
            </g>
          );
        })}

        {/* 折线图（画在中列下排卡内） */}
        <polyline points={chartPts} {...stroke(tChart)} strokeWidth={3} />
      </svg>

      {/* —— 实体层：clip-path inset 从左向右展开 —— */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          clipPath: `inset(0 ${(1 - scan) * 100}% 0 0)`,
        }}
      >
        <FakeDashboard variant="A" />
      </div>

      {/* —— 4px 发光扫描竖线（琥珀微光） —— */}
      <div
        style={{
          position: 'absolute',
          left: scanX - 2,
          top: 0,
          width: 4,
          height: 1080,
          background: '#ffc46b',
          opacity: lineOpacity,
          boxShadow:
            '0 0 18px 6px rgba(232, 163, 61, 0.65), 0 0 60px 18px rgba(232, 163, 61, 0.28)',
        }}
      />
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

