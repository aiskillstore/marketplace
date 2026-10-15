// ---
// name: omniailab-motion-demo-dutch-roll-to-level
// description: 参考实现——参考实现/运镜/情绪运镜/DutchRollToLevel.tsx。
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FakeDashboard, Card, G } from '../../_fixtures/Fixtures';

// 斜角滚正（dutch-roll-to-level）：呈现痛点时整帧带 -10° 斜角悬着（叠极缓慢
// 正弦漂移防止读作静态歪图），帧 70 解决方案的一拍整帧带单次过冲滚回水平
// （-10° → +1.2° → 0），同时警示条淡出、干净卡浮现——"世界被扶正"打在节拍上。
// 帧 0–70 斜置漂移 / 70–84 滚正冲过头 / 84–94 收回 0 / 94–140 真静止。

const ROLL = 70; // 滚正起拍
const LEVEL = 94; // 完全归位帧

export const DutchRollToLevel: React.FC = () => {
  const f = useCurrentFrame();

  // —— 斜置期的缓慢漂移（帧 70 前）：±0.8° 长周期正弦 + 2px 纵漂 ——
  const driftT = Math.min(f, ROLL);
  const driftRot = Math.sin(driftT * 0.035) * 0.8;
  const driftY = Math.sin(driftT * 0.05) * 2;
  // 滚正期间漂移随进度淡出
  const driftFade = interpolate(f, [ROLL, ROLL + 6], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // —— 滚正：-10° 用 14f 冲过 0 到 +1.2°，再 10f 收回 0（单次过冲不振荡） ——
  const baseRot =
    f < ROLL
      ? -10
      : f < ROLL + 14
        ? interpolate(f, [ROLL, ROLL + 14], [-10, 1.2], {
            easing: Easing.out(Easing.cubic),
          })
        : interpolate(f, [ROLL + 14, LEVEL], [1.2, 0], {
            extrapolateRight: 'clamp',
            easing: Easing.inOut(Easing.quad),
          });

  const rot = baseRot + driftRot * driftFade;
  const y = driftY * driftFade;

  // scale 1.15（防旋转露边）→ 滚正同步收到 1.08
  const scale = interpolate(f, [ROLL, LEVEL], [1.15, 1.08], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // —— 警示条（痛点）：斜置期悬在上方，滚正一拍淡出；干净卡反向淡入 ——
  const alertOpacity = interpolate(f, [ROLL, ROLL + 12], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cleanOpacity = interpolate(f, [ROLL + 8, ROLL + 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translateY(${y}px) rotate(${rot}deg) scale(${scale})`,
          transformOrigin: '50% 50%',
        }}
      >
        <FakeDashboard variant="B" />

        {/* 痛点警示条：深色横幅压在页面上方（斜着更显歪） */}
        <div
          style={{
            position: 'absolute',
            left: 560,
            top: 120,
            width: 800,
            height: 88,
            background: G.ink,
            borderRadius: 14,
            opacity: alertOpacity * 0.92,
            display: 'flex',
            alignItems: 'center',
            gap: 18,
            padding: '0 28px',
            boxSizing: 'border-box',
            boxShadow: '0 10px 30px rgba(0,0,0,0.25)',
          }}
        >
          {/* 警示三角 */}
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: '18px solid transparent',
              borderRight: '18px solid transparent',
              borderBottom: '32px solid #f7f7f6',
            }}
          />
          <div style={{ height: 16, width: 420, background: G.mid, borderRadius: 8 }} />
        </div>

        {/* 解决方案：干净卡随滚正浮现在同一位置 */}
        <div style={{ position: 'absolute', left: 560, top: 96, opacity: cleanOpacity }}>
          <Card w={800} h={140} seed={2} style={{ boxShadow: '0 10px 30px rgba(0,0,0,0.12)' }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

