// ---
// name: omniailab-motion-demo-drop-blackout-slam
// description: 落拍黑场爆开（drop-blackout-slam）——EDM concert blackout 的节奏手法：
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// 落拍黑场爆开（drop-blackout-slam）——EDM concert blackout 的节奏手法：
// 帧 0–49:假面板正常"播放"(scale 呼吸 1.0↔1.02)+右下角节拍点每 12f 闪一下;
// 帧 50–61:一帧切纯黑 #0c0c0c,整整 12f 死寂,屏上完全无物(蓄力全靠这一拍静默);
// 帧 62:白色大标题 "DROP" 从 scale 1.35 撞到 1.0(5f cubic out),同帧整屏
// 10px 震屏指数衰减(τ≈2.5f,约 12f 收干),底色变 G.ink 并从中心泛出一圈
// 快速消散的亮环;帧 ~80 起全静止到 130,收尾 ≥40f 真静止。
import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

// 帧确定伪随机(硬规矩:禁 Math.random)
const h = (n: number) => {
  const s = Math.sin(n * 127.3) * 43758.5453;
  return s - Math.floor(s);
};

const BLACK_IN = 50; // 切黑帧
const SLAM = 62; // 爆入帧

export const DropBlackoutSlam: React.FC = () => {
  const f = useCurrentFrame();

  // ===== 段 1:帧 0–49 正常播放 =====
  if (f < BLACK_IN) {
    // scale 呼吸 1.0↔1.02,周期 48f
    const breathe = 1.01 + 0.01 * Math.sin((f / 48) * Math.PI * 2);
    // 节拍点:每 12f 闪一下(亮 4f 衰减)
    const beatPhase = f % 12;
    const beatOn = interpolate(beatPhase, [0, 1, 5], [0.25, 1, 0.25], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    const beatScale = interpolate(beatPhase, [0, 1, 5], [1, 1.5, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    return (
      <div style={{ width: 1920, height: 1080, background: G.bg, overflow: 'hidden', position: 'relative' }}>
        <div style={{ width: 1920, height: 1080, transform: `scale(${breathe})`, transformOrigin: '50% 50%' }}>
          <FakeDashboard variant="B" />
        </div>
        {/* 右下角节拍点 */}
        <div
          style={{
            position: 'absolute',
            right: 56,
            bottom: 48,
            width: 36,
            height: 36,
            borderRadius: 18,
            background: G.ink,
            opacity: beatOn,
            transform: `scale(${beatScale})`,
          }}
        />
      </div>
    );
  }

  // ===== 段 2:帧 50–61 纯黑死寂,屏上完全无物 =====
  if (f < SLAM) {
    return <div style={{ width: 1920, height: 1080, background: '#0c0c0c' }} />;
  }

  // ===== 段 3:帧 62 起爆入 =====
  const t = f - SLAM;

  // 标题:scale 1.35 → 1.0,5f cubic out
  const slamScale = interpolate(t, [0, 5], [1.35, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 震屏:10px 指数衰减,τ≈2.5f,~12f 收干;t≥14 强制归零保证结尾真静止
  const amp = t >= 14 ? 0 : 10 * Math.exp(-t / 2.5);
  const shakeX = amp === 0 ? 0 : (h(f * 3.7 + 1) - 0.5) * 2 * amp;
  const shakeY = amp === 0 ? 0 : (h(f * 7.1 + 2) - 0.5) * 2 * amp;

  // 亮环:从中心快速扩散并消散,~16f 走完(t≥16 后 opacity=0 且不再画)
  const ringR = interpolate(t, [0, 16], [80, 900], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ringOpacity = interpolate(t, [0, 3, 16], [0.85, 0.55, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ width: 1920, height: 1080, background: G.ink, overflow: 'hidden', position: 'relative' }}>
      <div
        style={{
          width: 1920,
          height: 1080,
          transform: `translate(${shakeX}px, ${shakeY}px)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
      >
        {/* 亮环:快速扩散消散 */}
        {t < 16 && (
          <div
            style={{
              position: 'absolute',
              left: 960 - ringR,
              top: 540 - ringR,
              width: ringR * 2,
              height: ringR * 2,
              borderRadius: '50%',
              border: '10px solid #ffffff',
              opacity: ringOpacity,
            }}
          />
        )}
        <div
          style={{
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 800,
            fontSize: 340,
            color: '#ffffff',
            letterSpacing: -6,
            transform: `scale(${slamScale})`,
            lineHeight: 1,
          }}
        >
          DROP
        </div>
      </div>
    </div>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

