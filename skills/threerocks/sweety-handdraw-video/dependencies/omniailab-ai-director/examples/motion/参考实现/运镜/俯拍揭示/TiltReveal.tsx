// ---
// name: omniailab-motion-demo-tilt-reveal
// description: tilt-reveal｜俯仰揭示
// version: 2.2.1
// author: OmniAiLab
// developer: Mochiball
// agent_created: true
// 开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
// 操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
// ---

// tilt-reveal｜俯仰揭示
// 开场俯视 dashboard 顶部（rotateX 平躺、只露顶栏），~43f 机位抬头回正，
// 内容一排排涌入视野。out-cubic + 末端轻微过冲回正，落定真静止 ≥35f。
import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from 'remotion';
import { FakeDashboard, G } from '../../_fixtures/Fixtures';

const HOLD = 25; // 俯角定格
const MOVE = 43; // 主抬升
// 过冲：-55° → +2.6° → -0.9° → 0°，全部动画在 f=76 结束（145-76=69f 真静止）

export const TiltReveal: React.FC = () => {
  const f = useCurrentFrame();

  const rotX = interpolate(
    f,
    [HOLD, HOLD + MOVE, HOLD + MOVE + 4, HOLD + MOVE + 8],
    [-80, 2.6, -0.9, 0],
    { easing: Easing.out(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const p = interpolate(f, [HOLD, HOLD + MOVE], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = interpolate(p, [0, 1], [3.2, 1]);
  const ty = interpolate(p, [0, 1], [200, 0]);
  const persp = interpolate(p, [0, 1], [600, 1200]);
  const perspY = interpolate(p, [0, 1], [5, 40]);

  return (
    <AbsoluteFill style={{ background: G.bg, overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          perspective: persp,
          perspectiveOrigin: `50% ${perspY}%`,
        }}
      >
        <div
          style={{
            width: 1920,
            height: 1080,
            transformOrigin: '50% 0%', // 画面上缘
            transform: `translateY(${ty}px) scale(${scale}) rotateX(${rotX}deg)`,
          }}
        >
          <FakeDashboard variant="A" />
        </div>
      </div>
    </AbsoluteFill>
  );
};
// ---
// © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。

