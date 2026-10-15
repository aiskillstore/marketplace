// ---
// name: omniailab-motion-demo-slow-push-in
// description: 慢推压迫（slow-push-in）——studiobinder camera movements。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 慢推压迫（slow-push-in）——studiobinder camera movements。
// 景 A（帧 0–120）：深色底 + 白色大数字 "10x"，scale 用 Easing.in(Easing.quad)
// 从 1.00 匀加速推到 1.14——前 2 秒几乎不可察，后段明显可感；同时四角径向
// 暗角 opacity 0→0.5 同步加深，构成压迫感的第二来源。
// 帧 120 无任何过渡硬切景 B：满屏亮色 FakeDashboard(A) 真静止 30f——
// 暗→亮的大反差让"切"这一拍才响。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { G, FakeDashboard } from '../../_fixtures/Fixtures';

const CUT = 120; // 硬切帧

export const SlowPushIn: React.FC = () => {
  const frame = useCurrentFrame();

  // ---- 景 B：帧 120 起，满屏亮面板，完全静止 ----
  if (frame >= CUT) {
    return <FakeDashboard variant="A" />;
  }

  // ---- 景 A：0–120f 慢推 ----
  // 匀加速推近：Easing.in(quad)——前段几乎不可察，后段可感
  const scale = interpolate(frame, [0, CUT], [1.0, 1.14], {
    easing: Easing.in(Easing.quad),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // 暗角同步加深：压迫感的第二来源
  const vignette = interpolate(frame, [0, CUT], [0, 0.5], {
    easing: Easing.in(Easing.quad),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        background: G.side,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: 'Helvetica, Arial, sans-serif',
      }}
    >
      {/* 被推近的内容层：整体 scale */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${scale})`,
          transformOrigin: '50% 50%',
        }}
      >
        <div
          style={{
            fontSize: 300,
            fontWeight: 800,
            color: '#ffffff',
            letterSpacing: -6,
            lineHeight: 1,
          }}
        >
          10x
        </div>
        <div
          style={{
            marginTop: 36,
            fontSize: 40,
            fontWeight: 500,
            color: '#b8b8b6',
            letterSpacing: 6,
          }}
        >
          FASTER THAN BASELINE
        </div>
      </div>

      {/* 暗角层：四角径向渐变，随推近同步加深 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: vignette,
          background:
            'radial-gradient(ellipse 62% 55% at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.95) 100%)',
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

