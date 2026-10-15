// ---
// name: omniailab-motion-demo-invisible-cut
// description: 参考实现——参考实现/转场/藏切点转场/InvisibleCut.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { CameraMotionBlur } from '@remotion/motion-blur';
import { FakeDashboard, Card, G } from '../../_fixtures/Fixtures';

// invisible-cut：前景遮挡隐形切——一张放大到超出画幅的卡片带重运动模糊
// 从左侧贴脸扫过，糊满屏幕的瞬间背景从 A 无痕换成 B，卡片飞出右侧时
// 观众以为还是同一镜。（invisible-cut + foreground-occlusion-swipe）
const SW_START = 40; // 卡片入场
const SW_END = 54; // 卡片出场（14f 横扫）
const CUT = 47; // 硬切点：扫掠中点，卡片完全糊满画面的那一帧

// 卡片中扫掠曲线上的水平位置（容器 left，未缩放坐标）
const xAt = (f: number) =>
  // 卡片 scale(1.6) 后半宽 1280：起点右缘 -120 / 终点左缘 2120，均完全出画；
  // 中点 f47 覆盖 -280..2280，糊满整个 1920 画幅
  interpolate(f, [SW_START, SW_END], [-2200, 2600], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.3, 0, 0.7, 1),
  });

const Scene: React.FC = () => {
  const frame = useCurrentFrame();
  const x = xAt(frame);
  // 瞬时速度（px/帧），驱动斜切与残影强度
  const v = xAt(frame + 0.5) - xAt(frame - 0.5);
  const sweeping = frame > SW_START - 2 && frame < SW_END + 3;
  // 背景被"带风"轻推：A 被拖向左，切成 B 后从右侧回稳——卖同一镜错觉
  const shove =
    frame < CUT
      ? interpolate(frame, [SW_START, CUT], [0, -40], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.in(Easing.quad),
        })
      : interpolate(frame, [CUT, CUT + 13], [40, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.cubic),
        });
  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 背景层：硬切藏在遮挡帧内 */}
      <div style={{ position: 'absolute', inset: 0, transform: `translateX(${shove}px)` }}>
        {frame < CUT ? <FakeDashboard variant="A" /> : <FakeDashboard variant="B" />}
      </div>
      {/* 手动残影：4 层拖尾（在主卡身后），保证遮挡窗口糊满全屏 */}
      {sweeping &&
        [4, 3, 2, 1].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: xAt(frame - i * 0.55),
              top: 40,
              width: 1600,
              height: 1000,
              transform: 'scale(1.6)',
              opacity: [0, 0.35, 0.22, 0.13, 0.07][i],
              filter: 'blur(14px)',
            }}
          >
            <Card w={1600} h={1000} seed={9} style={{ width: '100%', height: '100%' }} />
          </div>
        ))}
      {/* 主卡：1600x1000 放大 1.6 倍（2560x1600 超出画幅），自带 blur 加强糊感 */}
      {sweeping && (
        <div
          style={{
            position: 'absolute',
            left: x,
            top: 40,
            width: 1600,
            height: 1000,
            transform: `scale(1.6) skewX(${-v * 0.018}deg)`,
            filter: 'blur(8px)',
            boxShadow: '0 24px 80px rgba(0,0,0,0.3)',
            borderRadius: 20,
          }}
        >
          <Card w={1600} h={1000} seed={9} style={{ width: '100%', height: '100%' }} />
        </div>
      )}
    </AbsoluteFill>
  );
};

export const InvisibleCut: React.FC = () => (
  <CameraMotionBlur shutterAngle={300} samples={12}>
    <Scene />
  </CameraMotionBlur>
);
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

