// ---
// name: omniailab-motion-demo-portal-wipe-v2
// description: 参考实现——参考实现/转场/镜头交棒/PortalWipeV2.tsx。
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

// portal-wipe 穿窗入景·改〔批次 1 重做〕
// 批次 1 弱点：3 层 7 卡散开幅度大(0.85)+blur，穿窗后画面碎读不清。
// 本版：窗放大 bezier(0.7,0,0.3,1) 40f 先慢后快；窗内只 2 层
// （远景整页 dashboard 缩略 + 近景 2 张卡），散开系数近 0.3 / 远 0.08，
// 不加 blur；穿窗完成(f65)后所有层 8f 内缓停(f73)，之后静止 hold 77f 读清新场景。
//
// 节拍（150f @30fps）：
//   0–25   hold：旧 dashboard 建立，目标卡原位可见
//   25–65  窗放大 40f：卡放大成全屏窗，窗内新场景随之显形
//   65–73  缓停 8f：近/远两层视差余势收干（Easing.out 自然归零）
//   73–150 静止 hold：新场景完整可读
export const PortalWipeV2: React.FC = () => {
  const frame = useCurrentFrame();

  // ── 窗放大：40f，先慢后快再缓收 ──
  const t = interpolate(frame, [25, 65], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.7, 0, 0.3, 1),
  });
  const c0 = { x: 1180, y: 620, w: 480, h: 320, r: 14 };
  const x = interpolate(t, [0, 1], [c0.x, 0]);
  const y = interpolate(t, [0, 1], [c0.y, 0]);
  const w = interpolate(t, [0, 1], [c0.w, 1920]);
  const h = interpolate(t, [0, 1], [c0.h, 1080]);
  const r = interpolate(t, [0, 1], [c0.r, 0]);

  // ── 窗内视差散开：40→73f，Easing.out 保证 f65 穿窗完成后 8f 内速度归零 ──
  const spread = interpolate(frame, [40, 73], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // 窗内整体从缩略推到满幅
  const innerScale = interpolate(t, [0, 1], [0.42, 1]);

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      {/* 旧场景：dashboard A */}
      <FakeDashboard variant="A" />

      {/* 窗（放大的卡）——内藏新场景 */}
      <div
        style={{
          position: 'absolute',
          left: x,
          top: y,
          width: w,
          height: h,
          borderRadius: r,
          overflow: 'hidden',
          boxShadow: t < 1 ? '0 12px 48px rgba(0,0,0,0.22)' : 'none',
        }}
      >
        {/* 窗内 1920×1080 舞台，随穿窗从 0.42 推到 1 */}
        <div
          style={{
            position: 'absolute',
            width: 1920,
            height: 1080,
            left: '50%',
            top: '50%',
            transform: `translate(-50%, -50%) scale(${innerScale})`,
            background: '#e4e4e2',
          }}
        >
          {/* 远景层（系数 0.08，不加 blur）：新场景整页 dashboard 缩略 */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              transform: `scale(${1 + spread * 0.08})`,
              transformOrigin: '960px 540px',
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                width: 1920,
                height: 1080,
                transform: 'translate(-50%, -50%) scale(0.82)',
                transformOrigin: 'center',
                borderRadius: 20,
                overflow: 'hidden',
                border: `2px solid ${G.border}`,
                boxShadow: '0 8px 32px rgba(0,0,0,0.10)',
              }}
            >
              <FakeDashboard variant="B" />
            </div>
            <div style={{ position: 'absolute', left: 250, top: 100 }}>
              <TitleBlock text="Scene B" size={64} />
            </div>
          </div>

          {/* 近景层（系数 0.3，不加 blur）：只 2 张卡，向边缘让位 */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              transform: `scale(${1 + spread * 0.3})`,
              transformOrigin: '960px 540px',
            }}
          >
            <div style={{ position: 'absolute', left: 150, top: 660 }}>
              <Card w={380} h={250} seed={71} />
            </div>
            <div style={{ position: 'absolute', left: 1420, top: 160 }}>
              <Card w={340} h={220} seed={72} />
            </div>
          </div>
        </div>

        {/* 卡正面：放大初期渐隐，露出窗内新场景 */}
        <div style={{ position: 'absolute', inset: 0, opacity: Math.max(0, 1 - t * 2.4) }}>
          <Card w={c0.w} h={c0.h} seed={5} style={{ width: '100%', height: '100%' }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

